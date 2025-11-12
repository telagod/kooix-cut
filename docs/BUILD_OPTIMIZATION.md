# 构建包体积优化分析

## 当前状态（v0.2.4）

- **Windows**: 95MB
- **macOS**: 93MB
- **Linux DEB**: 181MB
- **Linux AppImage**: 183MB

## 体积占比分析

```
PyQt6 + Qt6 Runtime  →  60 MB  (54.5%)  ████████████████████████████
OpenCV (cv2)         →  15 MB  (13.6%)  ███████
NumPy                →  12 MB  (10.9%)  █████
Python Runtime       →  10 MB  ( 9.1%)  ████
imageio + ffmpeg     →   5 MB  ( 4.5%)  ██
Other Dependencies   →   4 MB  ( 3.6%)  ██
MoviePy              →   3 MB  ( 2.7%)  █
webrtcvad            →   1 MB  ( 0.9%)  ▌
```

## 优化策略

### 1. PyQt6 优化（最大收益）

**当前问题**：PyQt6 占据 54.5% 的体积

**已实施的优化**：
- ✅ 排除 WebEngine 模块（最大的模块之一）
- ✅ 排除 Test、Bluetooth、NFC 等不常用模块
- ✅ 排除 Quick、Qml 模块

**进一步优化**：
```bash
--exclude-module PyQt6.QtMultimedia      # 多媒体播放（不需要）
--exclude-module PyQt6.QtMultimediaWidgets
--exclude-module PyQt6.QtNetwork         # 网络功能（不需要）
--exclude-module PyQt6.QtOpenGL          # OpenGL（不需要）
--exclude-module PyQt6.QtPrintSupport    # 打印支持（不需要）
--exclude-module PyQt6.QtSql             # SQL数据库（不需要）
--exclude-module PyQt6.QtSvg             # SVG支持（不需要）
--exclude-module PyQt6.QtXml             # XML解析（不需要）
```

**预期减少**：8-12 MB

### 2. OpenCV 优化（第二大收益）

**当前问题**：OpenCV 包含很多不需要的模块

**优化方案**：
```bash
--exclude-module cv2.cuda                # CUDA支持（GPU相关，不需要）
--exclude-module cv2.dnn                 # 深度学习模块（不需要）
--exclude-module cv2.ml                  # 机器学习（不需要）
--exclude-module cv2.optflow             # 光流算法（不需要）
--exclude-module cv2.stereo              # 立体视觉（不需要）
--exclude-module cv2.tracking            # 目标跟踪（不需要）
--exclude-module cv2.videostab           # 视频稳定（不需要）
```

**预期减少**：3-5 MB

### 3. NumPy 优化

**优化方案**：
```bash
--exclude-module numpy.tests             # 测试模块
--exclude-module numpy.distutils         # 构建工具
```

**预期减少**：1-2 MB

### 4. Python 标准库优化

**优化方案**：
```bash
--exclude-module tkinter                 # Tkinter GUI（已用PyQt6）
--exclude-module unittest                # 单元测试
--exclude-module test                    # 测试模块
--exclude-module email                   # 邮件处理
--exclude-module pydoc                   # 文档工具
--exclude-module doctest                 # 文档测试
```

**预期减少**：2-3 MB

### 5. 使用 UPX 压缩

UPX（Ultimate Packer for eXecutables）可以压缩可执行文件

**注意**：
- macOS 可能有签名问题
- 启动时间可能略微增加（需要解压）

**预期减少**：20-30%

### 6. 替代方案（更激进）

如果需要更小的体积，可以考虑：

#### 6.1 使用 opencv-python-headless
```bash
# 替换 opencv-python → opencv-python-headless
pip uninstall opencv-python
pip install opencv-python-headless
```
**减少**：~5 MB（移除GUI相关依赖）

#### 6.2 考虑使用 PySide6
PySide6 在某些平台可能比 PyQt6 略小

#### 6.3 静态链接优化
使用 `--noupx` 或 UPX 的不同压缩级别

## 优化后预期体积

### 保守估算（应用所有优化）
- **Windows**: 95MB → **70-75 MB** (-20~-25 MB, -21~-26%)
- **macOS**: 93MB → **68-73 MB** (-20~-25 MB, -21~-26%)
- **Linux**: 181MB → **145-155 MB** (-26~-36 MB, -14~-20%)

### 激进估算（包括 UPX + opencv-headless）
- **Windows**: 95MB → **50-55 MB** (-40~-45 MB, -42~-47%)
- **macOS**: 93MB → **48-53 MB** (-40~-45 MB, -43~-48%)
- **Linux**: 181MB → **110-120 MB** (-61~-71 MB, -34~-39%)

## 实施建议

### 阶段1：低风险优化（推荐立即实施）
1. 添加更多 PyQt6 模块排除
2. 添加 OpenCV 模块排除
3. 添加 NumPy 测试模块排除
4. 添加 Python 标准库模块排除

**预期减少**: 15-20 MB
**风险**: 低
**工作量**: 小

### 阶段2：中等风险优化
1. 启用 UPX 压缩（Windows/Linux）
2. 使用 `--strip` 移除调试符号

**预期减少**: 20-30%
**风险**: 中（macOS可能有问题）
**工作量**: 中

### 阶段3：高风险优化（需要测试）
1. 替换为 opencv-python-headless
2. 评估是否可以移除某些依赖

**预期减少**: 额外 5-10 MB
**风险**: 高（需要充分测试）
**工作量**: 大

## 监控和验证

### 构建后验证清单
- [ ] 程序能正常启动
- [ ] GUI 界面正常显示
- [ ] 文件选择功能正常
- [ ] 视频处理功能正常
- [ ] AI 增强功能正常（VAD、场景分割、人脸检测）
- [ ] 设置对话框正常
- [ ] 中英文切换正常
- [ ] 进度显示正常

### 测试脚本
```bash
# 运行优化构建
./scripts/build_optimized.sh

# 测试生成的程序
./dist/KOOI-Cut

# 比较大小
du -h dist/KOOI-Cut
```

## 持续优化

### 长期策略
1. **依赖审计**：定期review依赖项，移除不必要的依赖
2. **按需加载**：考虑将某些功能改为动态加载
3. **分离可选功能**：将 AI 功能作为可选插件
4. **使用更轻量的GUI框架**：评估 DearPyGui 等替代方案

### 监控工具
- PyInstaller 的 `--log-level=DEBUG` 查看包含的所有模块
- `pyinstaller-versionfile` 分析版本依赖
- `pipdeptree` 查看依赖树

## 结论

通过实施**阶段1+阶段2**的优化，可以在保持所有功能的前提下，将体积减少 **25-35%**（约 25-35 MB），达到：

- **Windows**: ~65-70 MB
- **macOS**: ~63-68 MB
- **Linux**: ~120-140 MB

这是一个很好的平衡点，既能显著减小体积，又不会引入太多风险。
