#!/bin/bash
# 本地打包脚本

set -e

echo "🚀 开始构建 KOOI Cut..."

# 检查依赖
if ! command -v pyinstaller &> /dev/null; then
    echo "📦 安装 PyInstaller..."
    pip install pyinstaller
fi

# 清理旧构建
echo "🧹 清理旧构建..."
rm -rf build dist *.spec

# 构建
echo "🔨 构建应用..."
pyinstaller build.spec

echo "✅ 构建完成！"
echo "📁 输出目录: dist/"

# 显示文件大小
if [ -f "dist/KOOI-Cut" ]; then
    ls -lh dist/KOOI-Cut
elif [ -f "dist/KOOI-Cut.exe" ]; then
    ls -lh dist/KOOI-Cut.exe
elif [ -d "dist/KOOI-Cut.app" ]; then
    du -sh dist/KOOI-Cut.app
fi
