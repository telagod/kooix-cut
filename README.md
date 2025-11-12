# KOOI Cut 🎬

<div align="center">

![Version](https://img.shields.io/badge/version-0.2.5-green.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

**智能视频剪辑预处理工具**

自动合并视频 · 删除静音片段 · AI 增强检测

[功能特性](#功能特性) · [快速开始](#快速开始) · [下载](#下载)

</div>

---

## 功能特性

### 核心功能
- 🎬 **智能剪辑** - 自动识别并删除无音频和长段背景音片段
- 🚀 **并行处理** - 多线程同时处理多个视频，速度提升 2-4 倍
- ⚡ **GPU 加速** - 自动检测 NVIDIA GPU，编码速度提升 5-10 倍
- 🎯 **拖拽操作** - 直接拖拽视频文件到窗口即可开始处理
- ⚙️ **参数可调** - 静音阈值、最小时长、输出路径均可自定义

### AI 增强功能
- 🤖 **语音活动检测 (VAD)** - 使用 WebRTC VAD 精确检测真实说话
- 🎞️ **场景分割** - 基于直方图差异智能识别场景切换
- 👤 **人脸检测** - 使用 OpenCV 保留有人出镜的片段
- 🔍 **关键帧提取** - 基于运动强度识别重要画面

### 用户体验
- 🌐 **中英文界面** - 一键切换中英文（Ctrl+L）
- 📊 **实时进度** - 进度条和状态显示，处理过程一目了然
- ⌨️ **快捷键支持** - Ctrl+O 打开、Delete 删除、Ctrl+R 处理
- 🎨 **现代化界面** - 深灰色专业主题，Material Design 风格

## 快速开始

### 下载预编译版本

从 [Releases 页面](https://github.com/telagod/kooix-cut/releases/latest) 下载最新版本：

- **Windows** - [KOOI-Cut.exe](https://github.com/telagod/kooix-cut/releases/download/v0.2.5/KOOI-Cut.exe)
- **macOS** - [KOOI-Cut.dmg](https://github.com/telagod/kooix-cut/releases/download/v0.2.5/KOOI-Cut.dmg)
- **Linux** - [kooix-cut.deb](https://github.com/telagod/kooix-cut/releases/download/v0.2.5/kooix-cut_0.2.5.deb)

### 源码安装

```bash
# 克隆仓库
git clone https://github.com/telagod/kooix-cut.git
cd kooix-cut

# 安装依赖（推荐使用 uv）
uv sync

# 或使用 pip
pip install -e .

# 运行程序
uv run modern_gui.py
# 或
kooix-cut
```

### Linux DEB 安装

```bash
sudo dpkg -i kooix-cut_0.2.5.deb
sudo apt-get install -f  # 安装依赖
kooix-cut  # 运行
```

## 使用方法

1. **启动程序** - 双击运行或命令行启动
2. **添加视频** - 拖拽 `.mp4` 视频文件到窗口，或点击"选择文件"
3. **调整参数**（可选）：
   - 点击右上角"设置"按钮
   - **静音阈值** (0.001-1.0)：默认 0.01，调高删除更少，调低删除更多
   - **最小时长** (0.5-60秒)：默认 3.0秒，只保留大于此时长的片段
   - **AI 增强**：可选启用 VAD、场景分割、人脸检测
4. **开始处理** - 点击"开始处理"按钮（或按 Ctrl+R）
5. **等待完成** - 查看进度条，处理完成后会弹窗提示

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+O` | 打开文件 |
| `Delete` | 删除选中文件 |
| `Ctrl+R` | 开始处理 |
| `Ctrl+,` | 打开设置 |
| `Ctrl+L` | 切换中英文 |

## 工作原理

1. 扫描所有视频文件并按文件名排序（时间顺序）
2. 并行分析每个视频的音频，检测有效音频片段
3. 删除静音和长段背景音片段
4. 合并所有有效片段为一个视频
5. 使用 GPU（如果可用）或多线程 CPU 编码输出

## 性能优化

- **并行处理** - 最多 4 个线程同时处理视频
- **GPU 加速** - 自动检测 NVIDIA GPU 并使用 `h264_nvenc` 编码器
- **多线程编码** - 充分利用所有 CPU 核心
- **快速预设** - 使用优化的编码预设

## 技术栈

- **GUI**: PyQt6 (Material Design 风格)
- **视频处理**: MoviePy
- **音频分析**: NumPy (向量化计算)
- **AI 增强**: WebRTC VAD, OpenCV Haar Cascade
- **并行处理**: ThreadPoolExecutor
- **GPU 编码**: NVENC (自动检测)

## 依赖

- Python >= 3.10
- moviepy >= 1.0.3
- numpy >= 1.24.0
- opencv-python >= 4.8.0
- webrtcvad >= 2.0.10
- PyQt6 >= 6.6.0

## 命令行模式

如需命令行批处理，可直接使用核心模块：

```python
from kooix_cut import process_videos

process_videos(
    input_dir="./videos",
    output_file="output.mp4",
    silence_threshold=0.01,
    min_duration=3.0
)
```

## 开发路线图

### v0.3.0 - 内容增强（计划中）
- [ ] **自动字幕生成** - 集成 Whisper 语音识别
- [ ] **字幕翻译** - 多语言字幕支持
- [ ] **自动配音** - TTS 文字转语音
- [ ] **背景音乐** - 智能添加背景音乐

### v0.4.0 - 高级编辑（计划中）
- [ ] **转场效果** - 片段间自动添加转场
- [ ] **画面稳定** - 视频防抖处理
- [ ] **色彩校正** - 自动调色和滤镜
- [ ] **水印添加** - 批量添加 Logo/水印

### v0.5.0 - 智能优化（计划中）
- [ ] **内容理解** - 基于 CLIP 的语义分析
- [ ] **智能剪辑** - 根据内容自动生成精彩片段
- [ ] **多平台适配** - 自动适配不同平台尺寸
- [ ] **批量处理** - 任务队列和批量导出

## 贡献指南

欢迎提交 Issue 和 Pull Request！

### 优先级
1. **性能优化** - 更快的处理速度
2. **AI 功能** - 智能检测和分析
3. **用户体验** - 更友好的界面
4. **跨平台** - Windows/macOS/Linux 支持

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

Made with ❤️ by KOOI

**当前版本**: v0.2.5
**最后更新**: 2025-11-12
