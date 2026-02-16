use anyhow::{bail, Result};
use std::path::Path;
use std::process::Command;
use tempfile::TempDir;

use crate::audio;
use crate::config::Config;
use crate::sort;

/// 扫描目录下的 mp4 文件并自然排序
fn scan_videos(dir: &str) -> Result<Vec<String>> {
    let mut files: Vec<String> = std::fs::read_dir(dir)?
        .filter_map(|e| e.ok())
        .map(|e| e.path())
        .filter(|p| {
            p.extension()
                .map(|ext| ext.to_ascii_lowercase() == "mp4")
                .unwrap_or(false)
        })
        .map(|p| p.to_string_lossy().into_owned())
        .collect();
    sort::sort_natural(&mut files);
    Ok(files)
}

/// 用 ffmpeg 切割视频片段
fn cut_segment(input: &str, start: f64, end: f64, output: &str, codec: &str, preset: &str) -> Result<()> {
    let duration = end - start;
    let status = Command::new("ffmpeg")
        .args([
            "-y",
            "-ss", &format!("{start:.3}"),
            "-i", input,
            "-t", &format!("{duration:.3}"),
            "-c:v", codec,
            "-preset", preset,
            "-c:a", "aac",
            "-avoid_negative_ts", "make_zero",
            output,
        ])
        .stderr(std::process::Stdio::null())
        .status()?;

    if !status.success() {
        bail!("ffmpeg 切割失败: {input} [{start:.1}s - {end:.1}s]");
    }
    Ok(())
}

/// 用 ffmpeg concat demuxer 合并片段
fn concat_segments(segment_files: &[String], output: &str) -> Result<()> {
    let tmp = tempfile::NamedTempFile::new()?;
    let list_content: String = segment_files
        .iter()
        .map(|f| format!("file '{}'\n", f.replace('\'', "'\\''")))
        .collect();
    std::fs::write(tmp.path(), &list_content)?;

    let status = Command::new("ffmpeg")
        .args([
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", tmp.path().to_str().unwrap(),
            "-c", "copy",
            output,
        ])
        .stderr(std::process::Stdio::null())
        .status()?;

    if !status.success() {
        bail!("ffmpeg 合并失败");
    }
    Ok(())
}

/// 处理视频：扫描 → 检测 → 切割 → 合并
/// progress_cb: (当前文件索引, 总文件数, 文件名)
pub fn process_videos<F>(input_dir: &str, config: &Config, mut progress_cb: F) -> Result<()>
where
    F: FnMut(usize, usize, &str),
{
    let files = scan_videos(input_dir)?;
    if files.is_empty() {
        bail!("未找到 mp4 文件: {input_dir}");
    }

    let total = files.len();
    let tmp_dir = TempDir::new()?;
    let mut all_segments: Vec<String> = Vec::new();
    let mut seg_idx = 0;

    for (i, file) in files.iter().enumerate() {
        let name = Path::new(file)
            .file_name()
            .unwrap_or_default()
            .to_string_lossy();
        progress_cb(i + 1, total, &name);

        let segments = audio::detect_audio_segments(
            file,
            config.silence_threshold,
            config.min_duration,
            config.window_size,
            config.smoothing,
            config.padding,
        )?;

        if segments.is_empty() {
            eprintln!("  跳过（无有效音频）: {name}");
            continue;
        }

        eprintln!("  保留 {} 个片段: {name}", segments.len());

        for (start, end) in &segments {
            let seg_path = tmp_dir
                .path()
                .join(format!("seg_{seg_idx:04}.mp4"))
                .to_string_lossy()
                .into_owned();
            cut_segment(file, *start, *end, &seg_path, &config.codec, &config.preset)?;
            all_segments.push(seg_path);
            seg_idx += 1;
        }
    }

    if all_segments.is_empty() {
        bail!("没有有效片段");
    }

    eprintln!("合并 {} 个片段...", all_segments.len());
    concat_segments(&all_segments, &config.output_file)?;
    eprintln!("完成！输出: {}", config.output_file);

    Ok(())
}
