use anyhow::Result;
use clap::Parser;
use indicatif::{ProgressBar, ProgressStyle};
use kooix_core::config::Config;
use kooix_core::video;

#[derive(Parser)]
#[command(name = "kooix-cut", version, about = "视频剪辑预处理工具 - 自动合并和删除静音片段")]
struct Cli {
    /// 输入目录（包含 mp4 文件）
    input_dir: String,

    /// 输出文件路径
    #[arg(short, long, default_value = "output.mp4")]
    output: String,

    /// 静音阈值 (0.001-1.0)
    #[arg(short = 't', long, default_value_t = 0.01)]
    threshold: f64,

    /// 最小有效片段时长（秒）
    #[arg(short = 'd', long, default_value_t = 3.0)]
    min_duration: f64,

    /// 视频编码器
    #[arg(short, long, default_value = "libx264")]
    codec: String,

    /// 编码预设
    #[arg(short, long, default_value = "fast")]
    preset: String,
}

fn main() -> Result<()> {
    let cli = Cli::parse();

    let config = Config {
        silence_threshold: cli.threshold,
        min_duration: cli.min_duration,
        codec: cli.codec,
        preset: cli.preset,
        output_file: cli.output,
        ..Default::default()
    };

    let pb = ProgressBar::new(0);
    pb.set_style(
        ProgressStyle::default_bar()
            .template("{msg} [{bar:40}] {pos}/{len}")?
            .progress_chars("█▓░"),
    );

    video::process_videos(&cli.input_dir, &config, |current, total, name| {
        pb.set_length(total as u64);
        pb.set_position(current as u64);
        pb.set_message(format!("处理: {name}"));
    })?;

    pb.finish_with_message("完成!");
    Ok(())
}
