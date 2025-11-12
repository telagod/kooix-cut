#!/usr/bin/env python3
"""AI 增强检测模块 - VAD, 场景分割, 人脸检测, 关键帧"""
import numpy as np
try:
    import webrtcvad
    WEBRTC_AVAILABLE = True
except ImportError:
    WEBRTC_AVAILABLE = False


class VADDetector:
    """语音活动检测（使用 WebRTC VAD）"""

    def __init__(self):
        self.vad = None
        self.sample_rate = 16000
        self.frame_duration = 30  # ms (10, 20, 或 30)

    def load_model(self):
        """初始化 WebRTC VAD"""
        if not WEBRTC_AVAILABLE:
            print("WebRTC VAD 未安装，请运行: pip install webrtcvad")
            return False

        if self.vad is None:
            try:
                self.vad = webrtcvad.Vad(2)  # 模式 2 (0-3, 3最激进)
            except Exception as e:
                print(f"VAD 初始化失败: {e}")
                self.vad = None
                return False
        return True

    def detect_speech(self, clip, min_duration=1.0, padding=0.3):
        """检测语音片段

        Args:
            clip: 视频片段
            min_duration: 最小语音时长（秒）
            padding: 片段前后填充（秒）

        Returns:
            语音片段列表 [(start, end), ...]
        """
        if not clip.audio:
            return []

        if not self.load_model():
            return []  # VAD 初始化失败

        # 提取音频并重采样到 16kHz
        audio = clip.audio
        samples = audio.to_soundarray(fps=self.sample_rate)
        if len(samples.shape) > 1:
            samples = np.mean(samples, axis=1)

        # 转换为 16-bit PCM
        samples = (samples * 32767).astype(np.int16)

        # VAD 检测（逐帧处理）
        frame_length = int(self.sample_rate * self.frame_duration / 1000)
        num_frames = len(samples) // frame_length
        speech_frames = []

        for i in range(num_frames):
            start_idx = i * frame_length
            end_idx = start_idx + frame_length
            frame = samples[start_idx:end_idx].tobytes()

            try:
                is_speech = self.vad.is_speech(frame, self.sample_rate)
                speech_frames.append(is_speech)
            except Exception:
                speech_frames.append(False)

        if not speech_frames:
            return []

        # 转换为时间片段
        frame_duration_sec = self.frame_duration / 1000.0
        is_speech = np.array(speech_frames)

        # 找到变化点
        changes = np.diff(np.concatenate([[False], is_speech, [False]]).astype(int))
        starts = np.where(changes == 1)[0] * frame_duration_sec
        ends = np.where(changes == -1)[0] * frame_duration_sec

        # 过滤并添加填充
        segments = []
        for s, e in zip(starts, ends):
            if e - s >= min_duration:
                s_padded = max(0, s - padding)
                e_padded = min(clip.duration, e + padding)
                segments.append((s_padded, e_padded))

        return segments


class SceneDetector:
    """场景分割检测（基于直方图差异）"""

    @staticmethod
    def detect_scenes(clip, threshold=30.0, min_duration=2.0):
        """检测场景切换

        Args:
            clip: 视频片段
            threshold: 场景切换阈值（0-100）
            min_duration: 最小场景时长（秒）

        Returns:
            场景列表 [(start, end), ...]
        """
        duration = clip.duration
        sample_interval = 0.5  # 每0.5秒采样一次
        times = np.arange(0, duration, sample_interval)

        if len(times) < 2:
            return [(0, duration)]

        # 计算直方图
        def get_histogram(t):
            frame = clip.get_frame(t)
            # 缩小图像加速
            h, w = frame.shape[:2]
            small = frame[::4, ::4]
            hist = np.histogram(small, bins=32, range=(0, 256))[0]
            return hist / hist.sum()

        hists = [get_histogram(t) for t in times]

        # 计算相邻帧差异
        diffs = []
        for i in range(len(hists) - 1):
            diff = np.sum(np.abs(hists[i+1] - hists[i])) * 100
            diffs.append(diff)

        # 检测场景切换点
        scene_changes = [0]
        for i, diff in enumerate(diffs):
            if diff > threshold:
                scene_changes.append(times[i+1])

        scene_changes.append(duration)

        # 构建场景列表
        scenes = []
        for i in range(len(scene_changes) - 1):
            start = scene_changes[i]
            end = scene_changes[i + 1]
            if end - start >= min_duration:
                scenes.append((start, end))

        return scenes if scenes else [(0, duration)]


class FaceDetector:
    """人脸检测（使用 OpenCV Haar Cascade）"""

    def __init__(self):
        self.cascade = None

    def load_model(self):
        """加载人脸检测模型"""
        if self.cascade is None:
            try:
                import cv2
                self.cascade = cv2.CascadeClassifier(
                    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                )
            except Exception as e:
                print(f"人脸检测模型加载失败: {e}")
                self.cascade = None

    def detect_faces(self, clip, sample_interval=1.0, min_face_ratio=0.02):
        """检测有人脸的片段

        Args:
            clip: 视频片段
            sample_interval: 采样间隔（秒）
            min_face_ratio: 最小人脸占比

        Returns:
            有人脸的时间点列表
        """
        self.load_model()
        if self.cascade is None:
            return []

        import cv2
        duration = clip.duration
        times = np.arange(0, duration, sample_interval)

        face_times = []
        for t in times:
            frame = clip.get_frame(t)
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

            # 检测人脸
            faces = self.cascade.detectMultiScale(gray, 1.1, 4)

            if len(faces) > 0:
                # 计算人脸占比
                total_area = sum(w * h for (x, y, w, h) in faces)
                frame_area = frame.shape[0] * frame.shape[1]
                if total_area / frame_area >= min_face_ratio:
                    face_times.append(t)

        return face_times


class KeyframeExtractor:
    """关键帧提取（基于运动强度）"""

    @staticmethod
    def extract_keyframes(clip, num_frames=10, method='motion'):
        """提取关键帧

        Args:
            clip: 视频片段
            num_frames: 提取帧数
            method: 提取方法 ('motion', 'uniform')

        Returns:
            关键帧时间点列表
        """
        duration = clip.duration

        if method == 'uniform':
            # 均匀采样
            return list(np.linspace(0, duration, num_frames))

        # 基于运动强度
        sample_times = np.linspace(0, duration, min(100, int(duration * 2)))
        if len(sample_times) < 2:
            return [0]

        # 计算帧间差异
        diffs = []
        prev_frame = None

        for t in sample_times:
            frame = clip.get_frame(t)
            small = frame[::4, ::4]  # 缩小加速

            if prev_frame is not None:
                diff = np.mean(np.abs(small.astype(float) - prev_frame.astype(float)))
                diffs.append((t, diff))

            prev_frame = small

        if not diffs:
            return list(np.linspace(0, duration, num_frames))

        # 选择运动强度最大的帧
        diffs.sort(key=lambda x: x[1], reverse=True)
        keyframes = sorted([t for t, _ in diffs[:num_frames]])

        return keyframes
