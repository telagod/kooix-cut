#!/usr/bin/env python3
"""生成应用图标（PNG和ICO格式）"""
import cairosvg
from PIL import Image
import io

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
print("\n所有图标文件已生成完成！")
