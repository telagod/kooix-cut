#!/bin/bash
# 优化后的构建脚本 - Linux

echo "=== KOOI Cut 优化构建 ==="
echo "开始优化构建..."

# 清理旧的构建文件
rm -rf build dist *.spec

# 优化后的PyInstaller构建
pyinstaller --name="KOOI-Cut" \
  --onefile \
  --windowed \
  --add-data="assets:assets" \
  --copy-metadata imageio \
  --copy-metadata moviepy \
  --copy-metadata numpy \
  \
  `# ========== 排除未使用的 Qt 模块 ==========` \
  --exclude-module PyQt6.QtWebEngine \
  --exclude-module PyQt6.QtWebEngineCore \
  --exclude-module PyQt6.QtWebEngineWidgets \
  --exclude-module PyQt6.QtTest \
  --exclude-module PyQt6.QtBluetooth \
  --exclude-module PyQt6.QtNfc \
  --exclude-module PyQt6.QtPositioning \
  --exclude-module PyQt6.QtSensors \
  --exclude-module PyQt6.Qt3D \
  --exclude-module PyQt6.QtQuick \
  --exclude-module PyQt6.QtQml \
  --exclude-module PyQt6.QtDesigner \
  --exclude-module PyQt6.QtHelp \
  --exclude-module PyQt6.QtMultimedia \
  --exclude-module PyQt6.QtMultimediaWidgets \
  --exclude-module PyQt6.QtNetwork \
  --exclude-module PyQt6.QtNetworkAuth \
  --exclude-module PyQt6.QtOpenGL \
  --exclude-module PyQt6.QtOpenGLWidgets \
  --exclude-module PyQt6.QtPdf \
  --exclude-module PyQt6.QtPdfWidgets \
  --exclude-module PyQt6.QtPrintSupport \
  --exclude-module PyQt6.QtSql \
  --exclude-module PyQt6.QtSvg \
  --exclude-module PyQt6.QtSvgWidgets \
  --exclude-module PyQt6.QtXml \
  \
  `# ========== 排除其他 Qt 绑定 ==========` \
  --exclude-module PySide2 \
  --exclude-module PySide6 \
  --exclude-module PyQt5 \
  \
  `# ========== 排除未使用的 Python 库 ==========` \
  --exclude-module matplotlib \
  --exclude-module scipy \
  --exclude-module pandas \
  --exclude-module PIL.ImageQt \
  --exclude-module tkinter \
  --exclude-module unittest \
  --exclude-module test \
  --exclude-module email \
  --exclude-module pydoc \
  --exclude-module doctest \
  --exclude-module argparse \
  \
  `# ========== 排除未使用的 OpenCV 模块 ==========` \
  --exclude-module cv2.cuda \
  --exclude-module cv2.gapi \
  --exclude-module cv2.dnn \
  --exclude-module cv2.ml \
  --exclude-module cv2.optflow \
  --exclude-module cv2.stereo \
  --exclude-module cv2.structured_light \
  --exclude-module cv2.superres \
  --exclude-module cv2.tracking \
  --exclude-module cv2.videostab \
  \
  `# ========== 排除未使用的 NumPy 测试模块 ==========` \
  --exclude-module numpy.tests \
  --exclude-module numpy.distutils \
  \
  `# ========== UPX 压缩（需要安装 upx）==========` \
  --upx-dir=/usr/bin \
  \
  `# ========== 其他优化选项 ==========` \
  --strip \
  --noupx \
  --log-level=WARN \
  \
  modern_gui.py

echo ""
echo "=== 构建完成 ==="
if [ -f "dist/KOOI-Cut" ]; then
  SIZE=$(du -h dist/KOOI-Cut | cut -f1)
  echo "✓ 生成的文件: dist/KOOI-Cut"
  echo "✓ 文件大小: $SIZE"

  # 显示详细信息
  ls -lh dist/KOOI-Cut
else
  echo "✗ 构建失败"
  exit 1
fi
