# ✂️ Kooix Cut

智能视频剪辑预处理工具 — 自动合并视频并删除静音片段。

Rust 引擎 + Tauri 2.0 液态玻璃 GUI，跨平台单文件分发。

## 下载

前往 [Releases](https://github.com/telagod/kooix-cut/releases) 下载：

| 平台 | CLI | GUI |
|------|-----|-----|
| Linux x86_64 | `kooix-cut-linux-x86_64` | `.deb` / `.AppImage` |
| macOS ARM | `kooix-cut-macos-aarch64` | `.dmg` |
| Windows x64 | `kooix-cut-windows-x86_64.exe` | `.msi` |

## 功能

- 🔇 自动检测并删除静音片段（自适应阈值）
- 🎞️ 多视频自动合并（智能自然排序）
- 🖼️ 静止画面检测
- 🖥️ 液态玻璃风格 GUI（深色/浅色自动切换）
- ⌨️ CLI 命令行工具
- 📦 单文件分发，无需安装运行时

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

## 从源码构建

```bash
# CLI
cargo build --release -p kooix-cli

# GUI（需要 Node.js）
cd ui && npm install && cd ..
cargo build --release -p kooix-cut-gui
```

## 项目结构

```
├── crates/
│   ├── kooix-core/    # 核心引擎（音频检测、视频处理、排序）
│   └── kooix-cli/     # 命令行工具
└── ui/                # Tauri 2.0 GUI（液态玻璃风格）
```

## Roadmap

- [x] Rust 核心引擎（音频检测、视频切割合并）
- [x] CLI 命令行工具
- [x] Tauri 2.0 液态玻璃 GUI
- [x] 全平台 CI/CD（Linux / macOS / Windows）
- [x] 静止画面检测
- [x] 响应式设计（桌面 / 平板 / 手机）
- [ ] Tauri 移动端（Android / iOS）
- [ ] WebRTC VAD 语音活动检测
- [ ] 场景分割检测
- [ ] GPU 编码自动检测（NVENC / VideoToolbox）
- [ ] 拖拽文件到 GUI 窗口
- [ ] 批量处理队列
- [ ] Tauri 自动更新
- [ ] 多语言界面（中/英）

## License

MIT
