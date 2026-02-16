use anyhow::{bail, Result};
use std::process::Command;

/// 检测静止画面片段，移植自 Python detect_static_scenes
/// 使用 ffmpeg 提取帧，计算帧间差异
pub fn detect_static_scenes(
    video_path: &str,
    threshold: f64,
    min_duration: f64,
    sample_interval: f64,
) -> Result<Vec<(f64, f64)>> {
    let duration = crate::audio::get_duration(video_path)?;
    let n_samples = (duration / sample_interval) as usize;
    if n_samples < 2 {
        return Ok(vec![]);
    }

    // 用 ffmpeg 按间隔提取缩略帧为 raw gray
    let width = 64;
    let height = 64;
    let output = Command::new("ffmpeg")
        .args([
            "-i", video_path,
            "-vf", &format!("fps=1/{sample_interval},scale={width}:{height},format=gray"),
            "-f", "rawvideo",
            "-pix_fmt", "gray",
            "pipe:1",
        ])
        .stderr(std::process::Stdio::null())
        .output()?;

    if !output.status.success() {
        bail!("ffmpeg 提取帧失败: {video_path}");
    }

    let frame_size = width * height;
    let frames: Vec<&[u8]> = output.stdout.chunks_exact(frame_size).collect();
    if frames.len() < 2 {
        return Ok(vec![]);
    }

    // 计算相邻帧差异
    let diffs: Vec<f64> = frames
        .windows(2)
        .map(|pair| {
            let sum: f64 = pair[0]
                .iter()
                .zip(pair[1].iter())
                .map(|(&a, &b)| (a as f64 - b as f64).abs())
                .sum();
            sum / frame_size as f64 / 255.0
        })
        .collect();

    // 检测静止段 (diff < threshold)
    let is_static: Vec<bool> = diffs.iter().map(|&d| d < threshold).collect();

    let mut segments: Vec<(f64, f64)> = Vec::new();
    let mut in_static = false;
    let mut seg_start = 0.0;

    for (i, &s) in is_static.iter().enumerate() {
        if s && !in_static {
            seg_start = i as f64 * sample_interval;
            in_static = true;
        } else if !s && in_static {
            let seg_end = (i + 1) as f64 * sample_interval;
            if seg_end - seg_start >= min_duration {
                segments.push((seg_start, seg_end.min(duration)));
            }
            in_static = false;
        }
    }
    if in_static {
        let seg_end = frames.len() as f64 * sample_interval;
        if seg_end - seg_start >= min_duration {
            segments.push((seg_start, seg_end.min(duration)));
        }
    }

    Ok(segments)
}
