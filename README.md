# Kooix Cut

视频剪辑预处理工具 — 自动合并视频并删除静音片段。

Rust 后端 + Tauri 2.0 GUI（液态玻璃设计）。

## 下载

前往 [Releases](https://github.com/telagod/kooix-cut/releases) 下载对应平台的安装包。

| 平台 | CLI | GUI |
|------|-----|-----|
| Linux x86_64 | `kooix-cut-linux-x86_64` | `.deb` / `.AppImage` |
| macOS ARM | `kooix-cut-macos-aarch64` | `.dmg` |
| Windows x64 | `kooix-cut-windows-x86_64.exe` | `.msi` |

## CLI 用法

```bash
kooix-cut ./videos -o output.mp4

# 自定义参数
kooix-cut ./videos -o output.mp4 -t 0.02 -d 2.0 -c libx264 -p fast
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-o` | 输出文件 | `output.mp4` |
| `-t` | 静音阈值 (0.001-1.0) | `0.01` |
| `-d` | 最小有效片段时长（秒） | `3.0` |
| `-c` | 编码器 | `libx264` |
| `-p` | 编码预设 | `fast` |

## 前置依赖

需要系统安装 [FFmpeg](https://ffmpeg.org/)：

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows (scoop)
scoop install ffmpeg
```

## 从源码构建

```bash
# CLI
cargo build --release -p kooix-cli

# GUI (需要 Node.js)
cd ui && npm install && cd ..
cargo build --release -p kooix-cut-gui
```

## 项目结构

```
├── crates/
│   ├── kooix-core/    # 核心引擎（音频检测、视频处理、排序）
│   └── kooix-cli/     # 命令行工具
├── ui/                # Tauri 2.0 GUI（液态玻璃风格）
└── legacy/            # 旧版 Python 代码（存档）
```

## License

MIT
