#!/usr/bin/env python3
"""现代化 GUI - Material Design 风格"""
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QListWidget, QPushButton, QProgressBar, QLabel, QDoubleSpinBox,
                             QLineEdit, QGroupBox, QGridLayout, QTabWidget, QComboBox, QFrame,
                             QScrollArea, QListWidgetItem)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor
from gui import ProcessThread


class ModernCard(QFrame):
    """Material Design 卡片组件"""

    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            ModernCard {
                background: #2a2a2a;
                border-radius: 12px;
                border: 1px solid #3a3a3a;
                padding: 16px;
            }
            ModernCard:hover {
                border: 1px solid #4CAF50;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
            layout.addWidget(title_label)

        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)


class ModernMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KOOI Cut - 智能视频剪辑工具")
        self.setGeometry(100, 100, 1200, 800)
        self.setAcceptDrops(True)

        # 现代化深色主题
        self.setStyleSheet("""
            QMainWindow {
                background: #1a1a1a;
            }
            QWidget {
                background: transparent;
                color: #e0e0e0;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            }
            QLabel {
                font-size: 13px;
                color: #e0e0e0;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5CBF60, stop:1 #4CAF50);
            }
            QPushButton:pressed {
                background: #388E3C;
            }
            QPushButton:disabled {
                background: #2a2a2a;
                color: #666;
            }
            QListWidget {
                background: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                padding: 8px;
                outline: none;
            }
            QListWidget::item {
                background: #252525;
                border-radius: 6px;
                padding: 8px;
                margin: 4px;
            }
            QListWidget::item:selected {
                background: #4CAF50;
            }
            QLineEdit, QDoubleSpinBox, QComboBox {
                background: #2a2a2a;
                border: 2px solid #3a3a3a;
                border-radius: 6px;
                padding: 8px;
                color: #e0e0e0;
            }
            QLineEdit:focus, QDoubleSpinBox:focus, QComboBox:focus {
                border: 2px solid #4CAF50;
            }
            QProgressBar {
                background: #2a2a2a;
                border: none;
                border-radius: 8px;
                height: 24px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #8BC34A);
                border-radius: 8px;
            }
            QTabWidget::pane {
                background: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                padding: 16px;
            }
            QTabBar::tab {
                background: #252525;
                color: #888;
                padding: 12px 24px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background: #4CAF50;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background: #333;
                color: #e0e0e0;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)

        # 主布局
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)

        # 左侧面板
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(16)

        # Logo 和标题
        header = QWidget()
        header_layout = QVBoxLayout(header)
        title = QLabel("KOOI Cut")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #4CAF50;")
        subtitle = QLabel("智能视频剪辑工具")
        subtitle.setStyleSheet("font-size: 14px; color: #888;")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        left_layout.addWidget(header)

        # 拖拽区域卡片
        drop_card = ModernCard()
        drop_layout = QVBoxLayout()
        drop_icon = QLabel("📁")
        drop_icon.setStyleSheet("font-size: 48px;")
        drop_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_text = QLabel("拖拽视频文件到此处\n或点击选择文件")
        drop_text.setStyleSheet("font-size: 16px; color: #888;")
        drop_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_layout.addWidget(drop_icon)
        drop_layout.addWidget(drop_text)
        drop_card.content_layout.addLayout(drop_layout)
        drop_card.setMinimumHeight(200)
        left_layout.addWidget(drop_card)

        # 文件列表卡片
        files_card = ModernCard("已选文件")
        self.file_list = QListWidget()
        files_card.content_layout.addWidget(self.file_list)
        left_layout.addWidget(files_card)

        # 操作按钮
        btn_layout = QHBoxLayout()
        self.btn = QPushButton("🚀 开始处理")
        self.btn.setMinimumHeight(48)
        self.btn.setEnabled(False)
        self.btn.clicked.connect(self.process)
        btn_layout.addWidget(self.btn)
        left_layout.addLayout(btn_layout)

        # 进度卡片
        progress_card = ModernCard("处理进度")
        self.progress = QProgressBar()
        self.progress.setMinimumHeight(32)
        self.status = QLabel("等待文件...")
        self.status.setStyleSheet("color: #888; margin-top: 8px;")
        progress_card.content_layout.addWidget(self.progress)
        progress_card.content_layout.addWidget(self.status)
        left_layout.addWidget(progress_card)

        main_layout.addWidget(left_panel, 1)

        # 右侧设置面板
        right_panel = self.create_settings_panel()
        main_layout.addWidget(right_panel, 1)

        self.files = []
        self.thread = None

    def create_settings_panel(self):
        """创建设置面板"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(16)

        # 基础设置卡片
        basic_card = ModernCard("⚙️ 基础设置")
        basic_grid = QGridLayout()
        basic_grid.setSpacing(12)

        # 静音阈值
        basic_grid.addWidget(QLabel("静音阈值"), 0, 0)
        self.threshold = QDoubleSpinBox()
        self.threshold.setRange(0.001, 1.0)
        self.threshold.setValue(0.01)
        self.threshold.setSingleStep(0.001)
        self.threshold.setDecimals(3)
        basic_grid.addWidget(self.threshold, 0, 1)
        hint = QLabel("音量低于此值视为静音")
        hint.setStyleSheet("color: #666; font-size: 11px;")
        basic_grid.addWidget(hint, 0, 2)

        # 最小时长
        basic_grid.addWidget(QLabel("最小时长(秒)"), 1, 0)
        self.min_duration = QDoubleSpinBox()
        self.min_duration.setRange(0.5, 60.0)
        self.min_duration.setValue(3.0)
        basic_grid.addWidget(self.min_duration, 1, 1)

        # 输出文件
        basic_grid.addWidget(QLabel("输出文件"), 2, 0)
        self.output_file = QLineEdit("output.mp4")
        basic_grid.addWidget(self.output_file, 2, 1, 1, 2)

        basic_card.content_layout.addLayout(basic_grid)
        layout.addWidget(basic_card)

        # AI 增强卡片
        ai_card = ModernCard("🤖 AI 增强")
        ai_grid = QGridLayout()
        ai_grid.setSpacing(12)

        ai_grid.addWidget(QLabel("语音检测 (VAD)"), 0, 0)
        self.enable_vad = QComboBox()
        self.enable_vad.addItems(["禁用", "启用"])
        ai_grid.addWidget(self.enable_vad, 0, 1)

        ai_grid.addWidget(QLabel("场景分割"), 1, 0)
        self.enable_scene = QComboBox()
        self.enable_scene.addItems(["禁用", "启用"])
        ai_grid.addWidget(self.enable_scene, 1, 1)

        ai_grid.addWidget(QLabel("人脸检测"), 2, 0)
        self.enable_face = QComboBox()
        self.enable_face.addItems(["禁用", "启用"])
        ai_grid.addWidget(self.enable_face, 2, 1)

        ai_card.content_layout.addLayout(ai_grid)
        layout.addWidget(ai_card)

        # 高级设置卡片
        advanced_card = ModernCard("🔧 高级设置")
        adv_grid = QGridLayout()
        adv_grid.setSpacing(12)

        adv_grid.addWidget(QLabel("编码器"), 0, 0)
        self.codec = QComboBox()
        self.codec.addItems(["libx264 (CPU)", "自动检测", "h264_nvenc (GPU)"])
        adv_grid.addWidget(self.codec, 0, 1)

        adv_grid.addWidget(QLabel("编码速度"), 1, 0)
        self.preset = QComboBox()
        self.preset.addItems(["ultrafast", "superfast", "veryfast", "faster", "fast", "medium"])
        adv_grid.addWidget(self.preset, 1, 1)

        advanced_card.content_layout.addLayout(adv_grid)
        layout.addWidget(advanced_card)

        layout.addStretch()
        scroll.setWidget(container)
        return scroll

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.endswith(".mp4") and path not in self.files:
                self.files.append(path)
                item = QListWidgetItem(f"📹 {Path(path).name}")
                self.file_list.addItem(item)

        if self.files:
            self.files.sort()
            self.btn.setEnabled(True)
            self.status.setText(f"✅ 已添加 {len(self.files)} 个文件")

            # 自动设置输出路径
            last_file = Path(self.files[-1])
            output_name = f"cut-{last_file.name}"
            output_path = last_file.parent / output_name
            self.output_file.setText(str(output_path))

    def process(self):
        """开始处理"""
        if not self.files:
            return

        self.btn.setEnabled(False)
        self.btn.setText("⏳ 处理中...")
        self.progress.setMaximum(len(self.files))

        # 获取编码器
        codec_map = {
            "libx264 (CPU)": "libx264",
            "自动检测": self._detect_gpu(),
            "h264_nvenc (GPU)": "h264_nvenc"
        }
        codec = codec_map[self.codec.currentText()]

        self.thread = ProcessThread(
            self.files,
            self.output_file.text(),
            self.threshold.value(),
            self.min_duration.value(),
            codec,
            self.preset.currentText(),
            0.3, 3, 0.5,  # window_size, smoothing, padding
            False, 0.02, 5.0,  # static detection
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
        self.status.setText(f"🎬 处理中 ({current}/{total}): {name}")

    def process_finished(self, message):
        self.status.setText(message)
        self.btn.setEnabled(True)
        self.btn.setText("🚀 开始处理")


def main():
    app = QApplication([])

    # 设置应用字体
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = ModernMainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
