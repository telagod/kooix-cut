@echo off
REM Windows 本地打包脚本

echo 🚀 开始构建 KOOI Cut...

REM 检查依赖
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 📦 安装 PyInstaller...
    pip install pyinstaller
)

REM 清理旧构建
echo 🧹 清理旧构建...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec

REM 构建
echo 🔨 构建应用...
pyinstaller build.spec

echo ✅ 构建完成！
echo 📁 输出目录: dist\

REM 显示文件
if exist dist\KOOI-Cut.exe (
    dir dist\KOOI-Cut.exe
)

pause
