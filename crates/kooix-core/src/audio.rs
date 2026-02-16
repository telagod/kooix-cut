use anyhow::{bail, Result};
use std::process::Command;

/// 用 ffmpeg 提取音频为 raw PCM f32le mono 22050Hz，返回采样数据
fn extract_audio_pcm(video_path: &str) -> Result<Vec<f32>> {
    let output = Command::new("ffmpeg")
        .args([
            "-i", video_path,
            "-vn",
            "-ac", "1",
            "-ar", "22050",
            "-f", "f32le",
            "-acodec", "pcm_f32le",
            "pipe:1",
        ])
        .stderr(std::process::Stdio::null())
        .output()?;

    if !output.status.success() {
        bail!("ffmpeg 提取音频失败: {}", video_path);
    }

    let samples: Vec<f32> = output
        .stdout
        .chunks_exact(4)
        .map(|b| f32::from_le_bytes([b[0], b[1], b[2], b[3]]))
        .collect();

    Ok(samples)
}

/// 获取视频时长（秒）
pub fn get_duration(video_path: &str) -> Result<f64> {
    let output = Command::new("ffprobe")
        .args([
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path,
        ])
        .output()?;

    let s = String::from_utf8_lossy(&output.stdout);
    s.trim().parse::<f64>().map_err(|e| anyhow::anyhow!("解析时长失败: {e}"))
}

/// 计算百分位数
fn percentile(data: &[f64], p: f64) -> f64 {
    if data.is_empty() {
        return 0.0;
    }
    let mut sorted = data.to_vec();
    sorted.sort_by(|a, b| a.partial_cmp(b).unwrap());
    let idx = (p / 100.0 * (sorted.len() - 1) as f64).round() as usize;
    sorted[idx.min(sorted.len() - 1)]
}

/// 检测有效音频片段，移植自 Python detect_audio_segments
pub fn detect_audio_segments(
    video_path: &str,
    silence_threshold: f64,
    min_duration: f64,
    window_size: f64,
    smoothing: usize,
    padding: f64,
) -> Result<Vec<(f64, f64)>> {
    let samples = extract_audio_pcm(video_path)?;
    if samples.is_empty() {
        return Ok(vec![]);
    }

    let duration = get_duration(video_path)?;
    let fps: usize = 22050;
    let win_samples = (fps as f64 * window_size) as usize;
    if win_samples == 0 {
        return Ok(vec![]);
    }
    let n_windows = samples.len() / win_samples;
    if n_windows == 0 {
        return Ok(vec![]);
    }

    // 计算每个窗口的 RMS 和峰值
    let mut volumes: Vec<f64> = Vec::with_capacity(n_windows);
    for i in 0..n_windows {
        let window = &samples[i * win_samples..(i + 1) * win_samples];
        let rms = (window.iter().map(|&s| (s as f64).powi(2)).sum::<f64>() / win_samples as f64).sqrt();
        let peak = window.iter().map(|&s| (s as f64).abs()).fold(0.0f64, f64::max);
        volumes.push(0.7 * rms + 0.3 * peak);
    }

    // 平滑处理（移动平均）
    if smoothing > 1 {
        let mut smoothed = vec![0.0; volumes.len()];
        for i in 0..volumes.len() {
            let start = i.saturating_sub(smoothing / 2);
            let end = (i + smoothing / 2 + 1).min(volumes.len());
            smoothed[i] = volumes[start..end].iter().sum::<f64>() / (end - start) as f64;
        }
        volumes = smoothed;
    }

    // 自适应阈值
    let vol_min = percentile(&volumes, 5.0);
    let vol_max = percentile(&volumes, 95.0);
    let vol_range = vol_max - vol_min;

    let adaptive_threshold = if vol_range < silence_threshold * 2.0 {
        silence_threshold
    } else {
        (vol_min + vol_range * 0.3).max(silence_threshold)
    };

    // 检测有效段
    let is_active: Vec<bool> = volumes.iter().map(|&v| v > adaptive_threshold).collect();

    // 找变化点
    let mut segments: Vec<(f64, f64)> = Vec::new();
    let mut in_segment = false;
    let mut seg_start = 0.0;

    for (i, &active) in is_active.iter().enumerate() {
        if active && !in_segment {
            seg_start = i as f64 * window_size;
            in_segment = true;
        } else if !active && in_segment {
            let seg_end = i as f64 * window_size;
            if seg_end - seg_start >= min_duration {
                let s = (seg_start - padding).max(0.0);
                let e = (seg_end + padding).min(duration);
                segments.push((s, e));
            }
            in_segment = false;
        }
    }
    // 处理末尾
    if in_segment {
        let seg_end = n_windows as f64 * window_size;
        if seg_end - seg_start >= min_duration {
            let s = (seg_start - padding).max(0.0);
            let e = (seg_end + padding).min(duration);
            segments.push((s, e));
        }
    }

    // 合并间隔 < 1s 的相邻片段
    if segments.len() > 1 {
        let mut merged = vec![segments[0]];
        for &(s, e) in &segments[1..] {
            let last = merged.last_mut().unwrap();
            if s - last.1 < 1.0 {
                last.1 = e;
            } else {
                merged.push((s, e));
            }
        }
        segments = merged;
    }

    Ok(segments)
}
