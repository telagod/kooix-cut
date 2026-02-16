#!/usr/bin/env python3
"""视频剪辑预处理工具 - 自动合并和删除静音片段"""
from pathlib import Path
from moviepy import VideoFileClip, concatenate_videoclips
import numpy as np
from video_sort import sort_files


def detect_static_scenes(clip, threshold=0.02, min_duration=5.0, sample_interval=1.0):
    """快速检测静止画面（十字采样法）

    Args:
        clip: 视频片段
        threshold: 变化阈值（0-1），越小越敏感
        min_duration: 最小静止时长（秒）
        sample_interval: 采样间隔（秒）

    Returns:
        静止片段的时间区间列表 [(start, end), ...]
    """
    duration = clip.duration
    h, w = clip.size[1], clip.size[0]

    # 十字采样位置（中心横竖条带）
    h_center = h // 2
    w_center = w // 2
    strip_width = max(2, min(h, w) // 20)  # 条带宽度约5%

    times = np.arange(0, duration, sample_interval)
    if len(times) < 2:
        return []

    # 提取十字条带
    def get_cross_sample(t):
        frame = clip.get_frame(t)
        # 横条
        h_strip = frame[h_center - strip_width:h_center + strip_width, :]
        # 竖条
        v_strip = frame[:, w_center - strip_width:w_center + strip_width]
        return np.concatenate([h_strip.flatten(), v_strip.flatten()])

    # 批量采样
    samples = [get_cross_sample(t) for t in times]

    # 计算相邻帧差异
    diffs = []
    for i in range(len(samples) - 1):
        diff = np.mean(np.abs(samples[i+1].astype(float) - samples[i].astype(float))) / 255.0
        diffs.append(diff)

    # 检测静止段
    is_static = np.array(diffs) < threshold
    changes = np.diff(np.concatenate([[False], is_static, [False]]).astype(int))
    starts = np.where(changes == 1)[0]
    ends = np.where(changes == -1)[0]

    # 转换为时间并过滤
    static_segments = []
    for s, e in zip(starts, ends):
        start_time = times[s]
        end_time = times[min(e + 1, len(times) - 1)]
        if end_time - start_time >= min_duration:
            static_segments.append((start_time, end_time))

    return static_segments


def detect_audio_segments(clip, silence_threshold=0.01, min_duration=3.0,
                         window_size=0.3, smoothing=3, padding=0.5):
    """智能检测有效音频片段（高性能+高质量）

    Args:
        clip: 视频片段
        silence_threshold: 静音阈值（RMS）
        min_duration: 最小有效片段时长（秒）
        window_size: 分析窗口大小（秒），越小越精确但越慢
        smoothing: 平滑窗口（帧数），减少误判
        padding: 片段前后填充时间（秒），避免切掉开头结尾

    Returns:
        有效片段的时间区间列表 [(start, end), ...]
    """
    if not clip.audio:
        return []

    audio = clip.audio
    fps = audio.fps
    duration = clip.duration

    # 智能采样率（避免MoviePy在低采样率下的bug）
    # MoviePy在16kHz及以下会导致音频数据损坏
    target_fps = min(fps, 22050)  # 使用至少22050Hz
    samples = audio.to_soundarray(fps=target_fps)
    if len(samples.shape) > 1:
        samples = np.mean(samples, axis=1)

    # 向量化计算音量（RMS + 峰值混合）
    win_samples = int(target_fps * window_size)
    n_windows = len(samples) // win_samples

    trimmed = samples[:n_windows * win_samples].reshape(n_windows, win_samples)

    # RMS（平均能量）
    rms = np.sqrt(np.mean(trimmed ** 2, axis=1))

    # 峰值（捕捉瞬时音量）
    peaks = np.max(np.abs(trimmed), axis=1)

    # 混合指标（70% RMS + 30% 峰值）
    volumes = 0.7 * rms + 0.3 * peaks

    # 平滑处理（移动平均，减少抖动）
    if smoothing > 1:
        kernel = np.ones(smoothing) / smoothing
        volumes = np.convolve(volumes, kernel, mode='same')

    # 改进的阈值检测：使用相对差异而非自适应提升
    # 计算音量的动态范围
    volume_min = np.percentile(volumes, 5)  # 排除极端安静的片段
    volume_max = np.percentile(volumes, 95)  # 排除极端响亮的片段
    volume_range = volume_max - volume_min

    # 如果音量范围很小（整体音量变化不大），使用用户设置的阈值
    # 否则使用动态阈值：最小音量 + 范围的一定比例
    if volume_range < silence_threshold * 2:
        # 音量变化很小，直接用用户阈值
        adaptive_threshold = silence_threshold
    else:
        # 音量变化大，用最小音量 + 30% 范围作为阈值
        # 这样能更好地区分"说话"和"静音/背景音"
        dynamic_threshold = volume_min + volume_range * 0.3
        # 但不能低于用户设置的阈值
        adaptive_threshold = max(silence_threshold, dynamic_threshold)

    # 检测有效段
    is_active = volumes > adaptive_threshold

    # 找到变化点
    changes = np.diff(np.concatenate([[False], is_active, [False]]).astype(int))
    starts = np.where(changes == 1)[0] * window_size
    ends = np.where(changes == -1)[0] * window_size

    # 过滤并添加填充
    segments = []
    for s, e in zip(starts, ends):
        if e - s >= min_duration:
            # 添加前后填充，避免切掉音频
            s_padded = max(0, s - padding)
            e_padded = min(duration, e + padding)
            segments.append((s_padded, e_padded))

    # 合并相邻片段（间隔小于1秒）
    if len(segments) > 1:
        merged = [segments[0]]
        for s, e in segments[1:]:
            if s - merged[-1][1] < 1.0:
                merged[-1] = (merged[-1][0], e)
            else:
                merged.append((s, e))
        segments = merged

    return segments


def process_videos(input_dir, output_file, silence_threshold=0.01, min_duration=3.0):
    """处理视频文件

    Args:
        input_dir: 输入目录
        output_file: 输出文件路径
        silence_threshold: 静音阈值
        min_duration: 最小有效片段时长
    """
    input_path = Path(input_dir)
    video_files = list(input_path.glob("*.mp4"))

    # 使用智能数字排序
    video_files = [str(f) for f in video_files]
    video_files = sort_files(video_files, method='name_natural')
    video_files = [Path(f) for f in video_files]

    if not video_files:
        print("未找到视频文件")
        return

    print(f"找到 {len(video_files)} 个视频文件")

    clips = []
    for video_file in video_files:
        print(f"处理: {video_file.name}")
        clip = VideoFileClip(str(video_file))

        segments = detect_audio_segments(clip, silence_threshold, min_duration)

        if not segments:
            print(f"  跳过（无有效音频）")
            clip.close()
            continue

        print(f"  保留 {len(segments)} 个片段")
        for start, end in segments:
            clips.append(clip.subclipped(start, end))

    if not clips:
        print("没有有效片段")
        return

    print(f"\n合并 {len(clips)} 个片段...")
    final = concatenate_videoclips(clips)
    final.write_videofile(output_file, codec="libx264", audio_codec="aac")

    for clip in clips:
        clip.close()
    final.close()

    print(f"\n完成！输出: {output_file}")


def main():
    from sys import argv

    if len(argv) < 2:
        print("用法: kooix-cut <输入目录> [输出文件] [静音阈值] [最小时长]")
        print("示例: kooix-cut ./videos output.mp4 0.01 3.0")
        return

    input_dir = argv[1]
    output_file = argv[2] if len(argv) > 2 else "output.mp4"
    silence_threshold = float(argv[3]) if len(argv) > 3 else 0.01
    min_duration = float(argv[4]) if len(argv) > 4 else 3.0

    process_videos(input_dir, output_file, silence_threshold, min_duration)


if __name__ == "__main__":
    main()
