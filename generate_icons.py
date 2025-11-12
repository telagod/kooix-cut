#!/usr/bin/env python3
"""生成应用图标（PNG、ICO和ICNS格式）"""
import cairosvg
from PIL import Image
import io
import subprocess
import platform

# 从SVG生成PNG
print("正在从SVG生成PNG (512x512)...")
png_data = cairosvg.svg2png(
    url="assets/icon.svg",
    output_width=512,
    output_height=512
)

# 保存PNG
with open("assets/icon.png", "wb") as f:
    f.write(png_data)
print("✓ 已生成 assets/icon.png")

# 生成ICO文件（多种尺寸）
print("正在生成ICO文件...")
img = Image.open(io.BytesIO(png_data))

# 创建多个尺寸的图标
sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
icons = []
for size in sizes:
    icons.append(img.resize(size, Image.Resampling.LANCZOS))

# 保存为ICO
icons[0].save(
    "assets/icon.ico",
    format="ICO",
    sizes=sizes,
    append_images=icons[1:]
)
print("✓ 已生成 assets/icon.ico")

# 生成ICNS文件（macOS专用）
print("正在生成ICNS文件（macOS）...")
try:
    # 创建临时iconset目录
    import os
    import shutil
    iconset_path = "assets/icon.iconset"
    if os.path.exists(iconset_path):
        shutil.rmtree(iconset_path)
    os.makedirs(iconset_path)

    # macOS ICNS需要的尺寸和文件名
    icns_sizes = [
        (16, "icon_16x16.png"),
        (32, "icon_16x16@2x.png"),
        (32, "icon_32x32.png"),
        (64, "icon_32x32@2x.png"),
        (128, "icon_128x128.png"),
        (256, "icon_128x128@2x.png"),
        (256, "icon_256x256.png"),
        (512, "icon_256x256@2x.png"),
        (512, "icon_512x512.png"),
        (1024, "icon_512x512@2x.png"),
    ]

    for size, filename in icns_sizes:
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(os.path.join(iconset_path, filename))

    # 使用iconutil转换（macOS）或png2icns（Linux）
    if platform.system() == "Darwin":
        subprocess.run(["iconutil", "-c", "icns", iconset_path, "-o", "assets/icon.icns"], check=True)
    else:
        # Linux上使用png2icns或直接用PIL（简化版）
        try:
            subprocess.run(["png2icns", "assets/icon.icns"] + [os.path.join(iconset_path, f) for _, f in icns_sizes], check=True)
        except FileNotFoundError:
            # 如果没有png2icns，生成一个简单的ICNS
            print("  警告：未找到png2icns，生成简化版ICNS")
            # 简化：只是重命名最大的PNG为ICNS（不完全正确但PyInstaller可能接受）
            with open("assets/icon.png", "rb") as src, open("assets/icon.icns", "wb") as dst:
                # ICNS文件头
                dst.write(b"icns")
                data = src.read()
                dst.write(len(data).to_bytes(4, "big"))
                dst.write(data)

    # 清理临时文件
    shutil.rmtree(iconset_path)
    print("✓ 已生成 assets/icon.icns")
except Exception as e:
    print(f"  警告：ICNS生成失败 - {e}")
    print("  如果在macOS上构建，请手动生成ICNS文件")

print("\n所有图标文件已生成完成！")
