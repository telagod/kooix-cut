use anyhow::{bail, Result};
use kooix_core::config::Config;
use kooix_core::video;
use std::env;

const VERSION: &str = env!("CARGO_PKG_VERSION");

fn print_help() {
    eprintln!(
        "kooix-cut {VERSION} - 视频剪辑预处理工具 - 自动合并和删除静音片段

用法: kooix-cut <输入目录> [选项]

选项:
  -o, --output <文件>       输出文件路径 (默认: output.mp4)
  -t, --threshold <值>      静音阈值 0.001-1.0 (默认: 0.01)
  -d, --min-duration <秒>   最小有效片段时长 (默认: 3.0)
  -c, --codec <编码器>      视频编码器 (默认: libx264)
  -p, --preset <预设>       编码预设 (默认: fast)
  -h, --help                显示帮助
  -V, --version             显示版本"
    );
}

fn parse_next(args: &mut impl Iterator<Item = String>, flag: &str) -> Result<String> {
    args.next()
        .ok_or_else(|| anyhow::anyhow!("{flag} 需要一个参数"))
}

fn main() -> Result<()> {
    let mut args = env::args().skip(1);
    let mut input_dir = None;
    let mut output = "output.mp4".to_string();
    let mut threshold = 0.01f64;
    let mut min_duration = 3.0f64;
    let mut codec = "libx264".to_string();
    let mut preset = "fast".to_string();

    while let Some(arg) = args.next() {
        match arg.as_str() {
            "-h" | "--help" => { print_help(); return Ok(()); }
            "-V" | "--version" => { eprintln!("kooix-cut {VERSION}"); return Ok(()); }
            "-o" | "--output" => output = parse_next(&mut args, "-o")?,
            "-t" | "--threshold" => threshold = parse_next(&mut args, "-t")?.parse()?,
            "-d" | "--min-duration" => min_duration = parse_next(&mut args, "-d")?.parse()?,
            "-c" | "--codec" => codec = parse_next(&mut args, "-c")?,
            "-p" | "--preset" => preset = parse_next(&mut args, "-p")?,
            s if s.starts_with('-') => bail!("未知选项: {s}\n使用 --help 查看帮助"),
            _ => input_dir = Some(arg),
        }
    }

    let input_dir = input_dir.ok_or_else(|| anyhow::anyhow!("缺少输入目录\n使用 --help 查看帮助"))?;

    let config = Config {
        silence_threshold: threshold,
        min_duration,
        codec,
        preset,
        output_file: output,
        ..Default::default()
    };

    video::process_videos(&input_dir, &config, |current, total, name| {
        eprint!("\r\x1b[K[{current}/{total}] 处理: {name}");
    })?;

    eprintln!("\r\x1b[K完成!");
    Ok(())
}
