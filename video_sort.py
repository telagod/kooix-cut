#!/usr/bin/env python3
"""视频文件智能排序工具"""
from pathlib import Path
import re
from typing import List, Callable
from moviepy import VideoFileClip


def natural_sort_key(text: str) -> List:
    """自然排序键 - 正确处理数字

    例如: video1.mp4, video2.mp4, video10.mp4 会按数字顺序排序
    而不是 video1.mp4, video10.mp4, video2.mp4
    """
    def atoi(t):
        return int(t) if t.isdigit() else t.lower()

    return [atoi(c) for c in re.split(r'(\d+)', str(text))]


def sort_by_name(files: List[str], reverse: bool = False) -> List[str]:
    """按文件名字母顺序排序"""
    return sorted(files, reverse=reverse)


def sort_by_name_natural(files: List[str], reverse: bool = False) -> List[str]:
    """按文件名自然顺序排序（智能数字排序）"""
    return sorted(files, key=lambda x: natural_sort_key(Path(x).name), reverse=reverse)


def sort_by_creation_time(files: List[str], reverse: bool = False) -> List[str]:
    """按创建时间排序（最早的在前）"""
    return sorted(files, key=lambda x: Path(x).stat().st_ctime, reverse=reverse)


def sort_by_modification_time(files: List[str], reverse: bool = False) -> List[str]:
    """按修改时间排序（最新的在后）"""
    return sorted(files, key=lambda x: Path(x).stat().st_mtime, reverse=reverse)


def sort_by_size(files: List[str], reverse: bool = False) -> List[str]:
    """按文件大小排序（从小到大）"""
    return sorted(files, key=lambda x: Path(x).stat().st_size, reverse=reverse)


def sort_by_duration(files: List[str], reverse: bool = False) -> List[str]:
    """按视频时长排序（从短到长）

    注意: 这个方法较慢，因为需要打开每个视频文件
    """
    def get_duration(filepath: str) -> float:
        try:
            clip = VideoFileClip(filepath)
            duration = clip.duration
            clip.close()
            return duration
        except:
            return 0.0

    return sorted(files, key=get_duration, reverse=reverse)


# 排序方法注册表
SORT_METHODS = {
    'manual': {
        'name_zh': '手动排序（拖拽调整）',
        'name_en': 'Manual (Drag to reorder)',
        'func': None,  # 手动排序不需要函数
        'description_zh': '拖拽文件调整顺序，完全自定义',
        'description_en': 'Drag files to reorder, fully customizable'
    },
    'name': {
        'name_zh': '文件名（字母）',
        'name_en': 'Name (Alphabetical)',
        'func': sort_by_name,
        'description_zh': '按文件名字母顺序排序',
        'description_en': 'Sort by filename alphabetically'
    },
    'name_natural': {
        'name_zh': '文件名（智能数字）',
        'name_en': 'Name (Natural)',
        'func': sort_by_name_natural,
        'description_zh': '智能识别文件名中的数字，如 video1, video2, video10',
        'description_en': 'Smart number detection: video1, video2, video10'
    },
    'creation_time': {
        'name_zh': '创建时间',
        'name_en': 'Creation Time',
        'func': sort_by_creation_time,
        'description_zh': '按文件创建时间排序（录制时间）',
        'description_en': 'Sort by file creation time (recording time)'
    },
    'modification_time': {
        'name_zh': '修改时间',
        'name_en': 'Modification Time',
        'func': sort_by_modification_time,
        'description_zh': '按文件修改时间排序',
        'description_en': 'Sort by file modification time'
    },
    'size': {
        'name_zh': '文件大小',
        'name_en': 'File Size',
        'func': sort_by_size,
        'description_zh': '按文件大小排序（从小到大）',
        'description_en': 'Sort by file size (smallest first)'
    },
    'duration': {
        'name_zh': '视频时长',
        'name_en': 'Video Duration',
        'func': sort_by_duration,
        'description_zh': '按视频时长排序（较慢，需读取每个视频）',
        'description_en': 'Sort by video duration (slower, reads each video)'
    }
}


def sort_files(files: List[str], method: str = 'name_natural', reverse: bool = False) -> List[str]:
    """统一的排序接口

    Args:
        files: 文件路径列表
        method: 排序方法，可选值见 SORT_METHODS
        reverse: 是否反向排序

    Returns:
        排序后的文件列表
    """
    if method not in SORT_METHODS:
        raise ValueError(f"未知的排序方法: {method}，可用方法: {list(SORT_METHODS.keys())}")

    # 手动排序直接返回原列表
    if method == 'manual':
        return files

    sort_func = SORT_METHODS[method]['func']
    return sort_func(files, reverse=reverse)


def get_sort_method_name(method: str, lang: str = 'zh') -> str:
    """获取排序方法的显示名称"""
    if method not in SORT_METHODS:
        return method

    key = f'name_{lang}'
    return SORT_METHODS[method].get(key, SORT_METHODS[method]['name_zh'])


def get_sort_method_description(method: str, lang: str = 'zh') -> str:
    """获取排序方法的描述"""
    if method not in SORT_METHODS:
        return ""

    key = f'description_{lang}'
    return SORT_METHODS[method].get(key, SORT_METHODS[method]['description_zh'])
