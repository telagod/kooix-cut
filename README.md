# KOOI Cut 🎬

<div align="center">

![Version](https://img.shields.io/badge/version-0.2.0-green.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

**智能视频剪辑预处理工具**

自动合并视频 · 删除静音片段 · AI 增强检测

[功能特性](#功能特性) · [快速开始](#快速开始) · [使用指南](#使用指南) · [开发路线](#开发路线图)

</div>

---

## 功能特性

- 🎬 **拖拽操作** - 直接拖拽 .mp4 文件到窗口
- 🚀 **并行处理** - 多线程同时处理多个视频，速度提升 2-4 倍
- ⚡ **GPU 加速** - 自动检测 NVIDIA GPU，编码速度提升 5-10 倍
- 🎯 **智能检测** - 自动识别并删除无音频和长段背景音片段
- ⚙️ **参数可调** - 静音阈值、最小时长、输出路径均可自定义
- 📊 **实时进度** - 进度条和状态显示，处理过程一目了然

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/telagod/kooix-cut.git
cd kooix-cut

# 安装依赖（推荐使用 uv）
uv sync

# 或使用 pip
pip install -e .
```

### 运行

```bash
# 现代化界面（推荐）
uv run modern_gui.py

# 经典界面
uv run gui.py

# 或安装后直接运行
kooix-cut
```

## 使用方法

1. 启动程序
2. 拖拽 `.mp4` 视频文件到窗口
3. 调整参数（可选）：
   - **静音阈值** (0.001-1.0)：默认 0.01，调高删除更少，调低删除更多
   - **最小时长** (0.5-60秒)：默认 3.0秒，只保留大于此时长的片段
   - **输出文件**：自动设置为 `cut-原文件名.mp4`，可手动修改
4. 点击"开始处理"按钮
5. 等待处理完成

## 工作原理

1. 扫描所有视频文件并按文件名排序（时间顺序）
2. 并行分析每个视频的音频，检测有效音频片段
3. 删除静音和长段背景音片段
4. 合并所有有效片段为一个视频
5. 使用 GPU（如果可用）或多线程 CPU 编码输出

## 性能优化

- **并行处理**：最多 4 个线程同时处理视频
- **GPU 加速**：自动检测 NVIDIA GPU 并使用 `h264_nvenc` 编码器
- **多线程编码**：充分利用所有 CPU 核心
- **快速预设**：使用优化的编码预设

## 依赖

- Python >= 3.10
- moviepy >= 1.0.3
- numpy >= 1.24.0
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

## 技术栈

- **GUI**: PyQt6
- **视频处理**: MoviePy
- **音频分析**: NumPy (向量化计算)
- **视频分析**: 十字采样法 (可选)
- **并行处理**: ThreadPoolExecutor
- **GPU 编码**: NVENC (自动检测)

## 开发路线图 (Roadmap)

### v0.2.0 - AI 增强 ✅ 已发布
- [x] **语音活动检测 (VAD)** - 使用 Silero VAD 模型检测真实说话
- [x] **场景分割** - 基于直方图差异的智能场景切换检测
- [x] **人脸检测** - 使用 OpenCV Haar Cascade 保留有人出镜的片段
- [x] **关键帧提取** - 基于运动强度智能识别重要画面
- [x] **现代化界面** - Material Design 风格的卡片式布局
- [x] **跨平台打包** - Windows/macOS/Linux 预编译版本

### v0.3.0 - 内容增强 (计划中)
- [ ] **自动字幕生成** - 集成 Whisper 语音识别
- [ ] **字幕翻译** - 多语言字幕支持
- [ ] **自动配音** - TTS 文字转语音
- [ ] **背景音乐** - 智能添加背景音乐

### v0.4.0 - 高级编辑 (计划中)
- [ ] **转场效果** - 片段间自动添加转场
- [ ] **画面稳定** - 视频防抖处理
- [ ] **色彩校正** - 自动调色和滤镜
- [ ] **水印添加** - 批量添加 Logo/水印

### v0.5.0 - 智能优化 (计划中)
- [ ] **内容理解** - 基于 CLIP 的语义分析
- [ **智能剪辑** - 根据内容自动生成精彩片段
- [ ] **多平台适配** - 自动适配不同平台尺寸
- [ ] **批量处理** - 任务队列和批量导出

### v1.0.0 - 生产就绪 (计划中)
- [ ] **插件系统** - 支持自定义插件扩展
- [ ] **云端处理** - 可选的云端加速
- [ ] **团队协作** - 项目共享和版本管理
- [ ] **完整文档** - API 文档和开发指南

## 贡献指南

欢迎提交 Issue 和 Pull Request！

### 优先级
1. **性能优化** - 更快的处理速度
2. **AI 功能** - 智能检测和分析
3. **用户体验** - 更友好的界面
4. **跨平台** - Windows/macOS/Linux 支持

---

Made with ❤️ by KOOI

**当前版本**: v0.2.0
**最后更新**: 2025-11-12

## 下载

### 预编译版本
从 [Releases 页面](https://github.com/telagod/kooix-cut/releases/latest) 下载最新版本：

- [Windows (.exe)](https://github.com/telagod/kooix-cut/releases/download/v0.2.0/KOOI-Cut.exe) - 239 MB
- [macOS (.dmg)](https://github.com/telagod/kooix-cut/releases/download/v0.2.0/KOOI-Cut.dmg) - 183 MB
- [Linux (.deb)](https://github.com/telagod/kooix-cut/releases/download/v0.2.0/kooix-cut_0.2.0.deb) - 321 MB

**Linux DEB 安装方法：**
```bash
sudo dpkg -i kooix-cut_0.2.0.deb
sudo apt-get install -f  # 安装依赖
kooix-cut  # 运行
```

### 本地构建
```bash
# Linux/macOS
./scripts/build_local.sh

# Windows
scripts\build_local.bat
```

## 新功能 (v0.2.0)

### AI 增强检测
- **语音活动检测 (VAD)** - 使用 Silero VAD 模型，更精确地检测真实说话
- **场景分割** - 基于直方图差异，智能识别场景切换
- **人脸检测** - OpenCV Haar Cascade，保留有人出镜的片段
- **关键帧提取** - 基于运动强度，识别重要画面

### 使用方法
在"AI 增强"标签页中启用相应功能：
- VAD 检测：首次使用会自动下载模型（~2MB）
- 场景分割：无需额外依赖
- 人脸检测：需要 OpenCV（自动安装）
