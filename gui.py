#!/usr/bin/env python3
"""PyQt6 GUI - 拖拽文件处理视频"""
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QListWidget, QPushButton, QProgressBar, QLabel, QDoubleSpinBox,
                             QLineEdit, QGroupBox, QGridLayout, QTabWidget, QTextEdit, QComboBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from kooix_cut import detect_audio_segments
from moviepy import VideoFileClip, concatenate_videoclips


class ProcessThread(QThread):
    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal(str)

    def __init__(self, files, output, threshold, min_duration, codec, preset,
                 window_size, smoothing, padding, enable_static, static_threshold, static_duration,
                 enable_vad, enable_scene, enable_face):
        super().__init__()
        self.files = files
        self.output = output
        self.threshold = threshold
        self.min_duration = min_duration
        self.codec = codec
        self.preset = preset
        self.window_size = window_size
        self.smoothing = int(smoothing)
        self.padding = padding
        self.enable_static = enable_static
        self.static_threshold = static_threshold
        self.static_duration = static_duration
        self.enable_vad = enable_vad
        self.enable_scene = enable_scene
        self.enable_face = enable_face

    def run(self):
        from concurrent.futures import ThreadPoolExecutor
        import os

        def process_video(i, video_file):
            from kooix_cut import detect_static_scenes
            self.progress.emit(i, len(self.files), Path(video_file).name)
            clip = VideoFileClip(video_file)

            # 选择检测方法
            if self.enable_vad:
                # AI VAD 检测
                from ai_detect import VADDetector
                vad = VADDetector()
                audio_segments = vad.detect_speech(clip, self.min_duration, self.padding)
            else:
                # 传统音频检测
                audio_segments = detect_audio_segments(
                    clip, self.threshold, self.min_duration,
                    self.window_size, self.smoothing, self.padding
                )

            # 视频静止检测（可选）
            if self.enable_static and audio_segments:
                static_segments = detect_static_scenes(
                    clip, self.static_threshold, self.static_duration
                )
                filtered = []
                for a_start, a_end in audio_segments:
                    keep = True
                    for s_start, s_end in static_segments:
                        overlap = min(a_end, s_end) - max(a_start, s_start)
                        if overlap > (a_end - a_start) * 0.8:
                            keep = False
                            break
                    if keep:
                        filtered.append((a_start, a_end))
                audio_segments = filtered

            # 场景分割（可选）
            if self.enable_scene and audio_segments:
                from ai_detect import SceneDetector
                scenes = SceneDetector.detect_scenes(clip)
                # 与音频片段求交集
                filtered = []
                for a_start, a_end in audio_segments:
                    for s_start, s_end in scenes:
                        overlap_start = max(a_start, s_start)
                        overlap_end = min(a_end, s_end)
                        if overlap_end > overlap_start:
                            filtered.append((overlap_start, overlap_end))
                audio_segments = filtered if filtered else audio_segments

            # 人脸检测（可选）
            if self.enable_face and audio_segments:
                from ai_detect import FaceDetector
                face_detector = FaceDetector()
                face_times = face_detector.detect_faces(clip)
                if face_times:
                    # 保留有人脸的片段
                    filtered = []
                    for a_start, a_end in audio_segments:
                        has_face = any(a_start <= t <= a_end for t in face_times)
                        if has_face:
                            filtered.append((a_start, a_end))
                    audio_segments = filtered if filtered else audio_segments

            result = []
            if audio_segments:
                for start, end in audio_segments:
                    result.append(clip.subclipped(start, end))
            else:
                clip.close()
            return result

        # 并行处理视频
        clips = []
        with ThreadPoolExecutor(max_workers=min(4, len(self.files))) as executor:
            futures = [executor.submit(process_video, i, f) for i, f in enumerate(self.files)]
            for future in futures:
                clips.extend(future.result())

        if clips:
            self.progress.emit(len(self.files), len(self.files), "合并中...")
            final = concatenate_videoclips(clips)

            # 编码参数
            threads = os.cpu_count() or 4

            # nvenc 使用不同的 preset
            if "nvenc" in self.codec:
                preset_map = {
                    "ultrafast": "p1", "superfast": "p2", "veryfast": "p3",
                    "faster": "p4", "fast": "p5", "medium": "p6"
                }
                preset = preset_map.get(self.preset, "p1")
            else:
                preset = self.preset

            # 尝试编码，失败则自动回退
            try:
                final.write_videofile(
                    self.output,
                    codec=self.codec,
                    audio_codec="aac",
                    preset=preset,
                    threads=threads,
                    logger=None
                )
            except Exception as e:
                if "nvenc" in self.codec and "Unknown encoder" in str(e):
                    # GPU 编码失败，回退到 CPU
                    self.progress.emit(len(self.files), len(self.files), "GPU不可用，使用CPU编码...")
                    final.write_videofile(
                        self.output,
                        codec="libx264",
                        audio_codec="aac",
                        preset=self.preset,
                        threads=threads,
                        logger=None
                    )
                else:
                    raise

            for clip in clips:
                clip.close()
            final.close()
            self.finished.emit(f"✅ 完成！输出: {self.output}")
        else:
            self.finished.emit("❌ 没有有效片段")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KOOI Cut - 视频剪辑预处理工具")
        self.setGeometry(100, 100, 800, 650)
        self.setAcceptDrops(True)

        # 深色主题样式
        self.setStyleSheet("""
            QMainWindow { background: #1e1e1e; }
            QWidget { background: #1e1e1e; color: #e0e0e0; }
            QGroupBox { font-weight: bold; border: 2px solid #3a3a3a; border-radius: 5px; margin-top: 10px; padding-top: 10px; background: #252525; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #4CAF50; }
            QPushButton { padding: 8px; font-size: 14px; border-radius: 4px; border: none; }
            QPushButton:enabled { background: #4CAF50; color: white; }
            QPushButton:hover { background: #45a049; }
            QPushButton:disabled { background: #3a3a3a; color: #666; }
            QLabel { font-size: 13px; color: #e0e0e0; }
            QListWidget { border: 1px solid #3a3a3a; border-radius: 4px; background: #252525; color: #e0e0e0; }
            QLineEdit { background: #252525; border: 1px solid #3a3a3a; border-radius: 4px; padding: 5px; color: #e0e0e0; }
            QDoubleSpinBox, QComboBox { background: #252525; border: 1px solid #3a3a3a; border-radius: 4px; padding: 5px; color: #e0e0e0; }
            QProgressBar { border: 1px solid #3a3a3a; border-radius: 4px; text-align: center; background: #252525; color: #e0e0e0; }
            QProgressBar::chunk { background: #4CAF50; }
            QTabWidget::pane { border: 1px solid #3a3a3a; border-radius: 4px; background: #252525; }
            QTabBar::tab { background: #2a2a2a; color: #e0e0e0; padding: 8px 16px; border: 1px solid #3a3a3a; }
            QTabBar::tab:selected { background: #4CAF50; color: white; }
        """)

        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QVBoxLayout(widget)

        # 拖拽区域
        drop_zone = QLabel("🎬 拖拽 .mp4 文件到此处")
        drop_zone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_zone.setStyleSheet("QLabel { font-size: 18px; padding: 30px; border: 3px dashed #4CAF50; border-radius: 8px; background: #252525; color: #4CAF50; }")
        layout.addWidget(drop_zone)

        # 文件列表
        file_group = QGroupBox("已选文件")
        file_layout = QVBoxLayout(file_group)
        self.file_list = QListWidget()
        file_layout.addWidget(self.file_list)
        layout.addWidget(file_group)

        # 标签页
        tabs = QTabWidget()

        # 基础设置
        basic_tab = QWidget()
        basic_layout = QGridLayout(basic_tab)

        basic_layout.addWidget(QLabel("静音阈值:"), 0, 0)
        self.threshold = QDoubleSpinBox()
        self.threshold.setRange(0.001, 1.0)
        self.threshold.setValue(0.01)
        self.threshold.setSingleStep(0.001)
        self.threshold.setDecimals(3)
        basic_layout.addWidget(self.threshold, 0, 1)
        basic_layout.addWidget(QLabel("音量低于此值视为静音 (默认0.01)"), 0, 2)

        basic_layout.addWidget(QLabel("最小时长(秒):"), 1, 0)
        self.min_duration = QDoubleSpinBox()
        self.min_duration.setRange(0.5, 60.0)
        self.min_duration.setValue(3.0)
        self.min_duration.setSingleStep(0.5)
        basic_layout.addWidget(self.min_duration, 1, 1)
        basic_layout.addWidget(QLabel("保留片段的最小时长 (默认3.0秒)"), 1, 2)

        basic_layout.addWidget(QLabel("分析窗口(秒):"), 2, 0)
        self.window_size = QDoubleSpinBox()
        self.window_size.setRange(0.1, 2.0)
        self.window_size.setValue(0.3)
        self.window_size.setSingleStep(0.1)
        basic_layout.addWidget(self.window_size, 2, 1)
        basic_layout.addWidget(QLabel("越小越精确，越大越快 (默认0.3秒)"), 2, 2)

        basic_layout.addWidget(QLabel("平滑强度:"), 3, 0)
        self.smoothing = QDoubleSpinBox()
        self.smoothing.setRange(1, 10)
        self.smoothing.setValue(3)
        self.smoothing.setSingleStep(1)
        self.smoothing.setDecimals(0)
        basic_layout.addWidget(self.smoothing, 3, 1)
        basic_layout.addWidget(QLabel("减少误判，越大越平滑 (默认3)"), 3, 2)

        basic_layout.addWidget(QLabel("边缘填充(秒):"), 4, 0)
        self.padding = QDoubleSpinBox()
        self.padding.setRange(0.0, 2.0)
        self.padding.setValue(0.5)
        self.padding.setSingleStep(0.1)
        basic_layout.addWidget(self.padding, 4, 1)
        basic_layout.addWidget(QLabel("避免切掉开头结尾 (默认0.5秒)"), 4, 2)

        basic_layout.addWidget(QLabel("输出文件:"), 5, 0)
        self.output_file = QLineEdit("output.mp4")
        basic_layout.addWidget(self.output_file, 5, 1, 1, 2)

        tabs.addTab(basic_tab, "基础设置")

        # 高级设置
        advanced_tab = QWidget()
        advanced_layout = QGridLayout(advanced_tab)

        advanced_layout.addWidget(QLabel("视频编码器:"), 0, 0)
        self.codec = QComboBox()
        self.codec.addItems(["libx264 (CPU)", "自动检测", "h264_nvenc (NVIDIA GPU)"])
        advanced_layout.addWidget(self.codec, 0, 1)
        advanced_layout.addWidget(QLabel("自动检测GPU或使用CPU编码"), 0, 2)

        advanced_layout.addWidget(QLabel("编码速度:"), 1, 0)
        self.preset = QComboBox()
        self.preset.addItems(["ultrafast", "superfast", "veryfast", "faster", "fast", "medium"])
        self.preset.setCurrentText("ultrafast")
        advanced_layout.addWidget(self.preset, 1, 1)
        advanced_layout.addWidget(QLabel("越快质量越低，文件越大 (推荐ultrafast)"), 1, 2)

        advanced_layout.addWidget(QLabel("静止画面检测:"), 2, 0)
        self.enable_static = QComboBox()
        self.enable_static.addItems(["禁用", "启用"])
        self.enable_static.setCurrentText("禁用")
        advanced_layout.addWidget(self.enable_static, 2, 1)
        advanced_layout.addWidget(QLabel("十字采样法，快速检测静止画面 (默认禁用)"), 2, 2)

        advanced_layout.addWidget(QLabel("画面变化阈值:"), 3, 0)
        self.static_threshold = QDoubleSpinBox()
        self.static_threshold.setRange(0.001, 0.1)
        self.static_threshold.setValue(0.02)
        self.static_threshold.setSingleStep(0.001)
        self.static_threshold.setDecimals(3)
        advanced_layout.addWidget(self.static_threshold, 3, 1)
        advanced_layout.addWidget(QLabel("越小越敏感 (默认0.02)"), 3, 2)

        advanced_layout.addWidget(QLabel("最小静止时长(秒):"), 4, 0)
        self.static_duration = QDoubleSpinBox()
        self.static_duration.setRange(1.0, 60.0)
        self.static_duration.setValue(5.0)
        self.static_duration.setSingleStep(1.0)
        advanced_layout.addWidget(self.static_duration, 4, 1)
        advanced_layout.addWidget(QLabel("删除超过此时长的静止画面 (默认5秒)"), 4, 2)

        tabs.addTab(advanced_tab, "高级设置")

        # AI 增强
        ai_tab = QWidget()
        ai_layout = QGridLayout(ai_tab)

        ai_layout.addWidget(QLabel("语音活动检测 (VAD):"), 0, 0)
        self.enable_vad = QComboBox()
        self.enable_vad.addItems(["禁用", "启用"])
        ai_layout.addWidget(self.enable_vad, 0, 1)
        ai_layout.addWidget(QLabel("AI 模型检测真实说话 (需下载模型)"), 0, 2)

        ai_layout.addWidget(QLabel("场景分割:"), 1, 0)
        self.enable_scene = QComboBox()
        self.enable_scene.addItems(["禁用", "启用"])
        ai_layout.addWidget(self.enable_scene, 1, 1)
        ai_layout.addWidget(QLabel("智能检测场景切换"), 1, 2)

        ai_layout.addWidget(QLabel("人脸检测:"), 2, 0)
        self.enable_face = QComboBox()
        self.enable_face.addItems(["禁用", "启用"])
        ai_layout.addWidget(self.enable_face, 2, 1)
        ai_layout.addWidget(QLabel("保留有人出镜的片段"), 2, 2)

        tabs.addTab(ai_tab, "AI 增强")

        layout.addWidget(tabs)

        # 进度条
        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        # 状态
        self.status = QLabel("等待文件...")
        layout.addWidget(self.status)

        # 按钮
        self.btn = QPushButton("开始处理")
        self.btn.clicked.connect(self.process)
        self.btn.setEnabled(False)
        layout.addWidget(self.btn)

        self.files = []
        self.thread = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.endswith(".mp4") and path not in self.files:
                self.files.append(path)
                self.file_list.addItem(Path(path).name)

        if self.files:
            self.files.sort()
            self.btn.setEnabled(True)
            self.status.setText(f"已添加 {len(self.files)} 个文件")

            # 自动设置输出路径
            last_file = Path(self.files[-1])
            output_name = f"cut-{last_file.name}"
            output_path = last_file.parent / output_name
            self.output_file.setText(str(output_path))

    def process(self):
        if not self.files:
            return

        self.btn.setEnabled(False)
        self.progress.setMaximum(len(self.files))

        # 获取编码器
        codec_map = {
            "libx264 (CPU)": "libx264",
            "自动检测": self._detect_gpu(),
            "h264_nvenc (NVIDIA GPU)": "h264_nvenc"
        }
        codec = codec_map[self.codec.currentText()]

        self.thread = ProcessThread(
            self.files,
            self.output_file.text(),
            self.threshold.value(),
            self.min_duration.value(),
            codec,
            self.preset.currentText(),
            self.window_size.value(),
            self.smoothing.value(),
            self.padding.value(),
            self.enable_static.currentText() == "启用",
            self.static_threshold.value(),
            self.static_duration.value(),
            self.enable_vad.currentText() == "启用",
            self.enable_scene.currentText() == "启用",
            self.enable_face.currentText() == "启用"
        )
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.process_finished)
        self.thread.start()

    def _detect_gpu(self):
        import subprocess
        try:
            # 实际测试 nvenc 是否可用
            result = subprocess.run(
                ["ffmpeg", "-f", "lavfi", "-i", "nullsrc=s=256x256:d=1", "-c:v", "h264_nvenc", "-f", "null", "-"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                return "h264_nvenc"
        except:
            pass
        return "libx264"

    def update_progress(self, current, total, name):
        self.progress.setValue(current)
        self.status.setText(f"处理中 ({current}/{total}): {name}")

    def process_finished(self, message):
        self.status.setText(message)
        self.btn.setEnabled(True)


def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
