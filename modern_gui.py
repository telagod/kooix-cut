#!/usr/bin/env python3
"""现代化 GUI - 专业优雅的 Material Design 风格（PyQt6实现）"""
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QListWidget, QPushButton, QProgressBar, QLabel, QDoubleSpinBox,
                             QLineEdit, QGridLayout, QComboBox, QFrame,
                             QScrollArea, QListWidgetItem, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QKeySequence, QShortcut
from gui import ProcessThread


class ModernCard(QFrame):
    """统一的卡片组件"""

    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            ModernCard {
                background: #2a2a2a;
                border-radius: 8px;
                border: 1px solid #3a3a3a;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #4CAF50; border: none;")
            layout.addWidget(title_label)

        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(8)
        layout.addLayout(self.content_layout)


class ModernMainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("KOOI Cut - 智能视频剪辑工具")
        self.setGeometry(100, 100, 1000, 700)
        self.setAcceptDrops(True)

        # 统一的深色主题
        self.setStyleSheet("""
            QMainWindow {
                background: #1a1a1a;
            }
            QWidget {
                background: transparent;
                color: #e0e0e0;
                font-family: 'Segoe UI', 'Microsoft YaHei', 'Noto Sans CJK SC', sans-serif;
                font-size: 12px;
            }
            QLabel {
                color: #e0e0e0;
                border: none;
            }
            QPushButton {
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #5CBF60;
            }
            QPushButton:pressed {
                background: #45a049;
            }
            QPushButton:disabled {
                background: #2a2a2a;
                color: #666;
            }
            QListWidget {
                background: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                padding: 4px;
                outline: none;
            }
            QListWidget::item {
                background: transparent;
                padding: 6px;
                margin: 2px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background: #4CAF50;
            }
            QListWidget::item:hover:!selected {
                background: #333;
            }
            QLineEdit, QDoubleSpinBox, QComboBox {
                background: #2a2a2a;
                border: 2px solid #3a3a3a;
                border-radius: 6px;
                padding: 6px;
                color: #e0e0e0;
            }
            QLineEdit:focus, QDoubleSpinBox:focus, QComboBox:focus {
                border: 2px solid #4CAF50;
            }
            QProgressBar {
                background: #2a2a2a;
                border: none;
                border-radius: 6px;
                height: 24px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: #4CAF50;
                border-radius: 6px;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #2a2a2a;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #4CAF50;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # 主布局
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # 左侧面板
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)

        # 右侧设置面板
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 1)

        self.files = []
        self.thread = None

        # 设置快捷键
        self.setup_shortcuts()

    def setup_shortcuts(self):
        """设置快捷键"""
        QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self.select_files)
        QShortcut(QKeySequence("Delete"), self).activated.connect(self.remove_selected)
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(self.process)

    def create_left_panel(self):
        """创建左侧面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        layout.setContentsMargins(0, 0, 0, 0)

        # 标题
        title = QLabel("KOOI Cut")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #4CAF50;")
        layout.addWidget(title)

        subtitle = QLabel("智能视频剪辑工具")
        subtitle.setStyleSheet("font-size: 11px; color: #888; margin-bottom: 10px;")
        layout.addWidget(subtitle)

        # 拖拽区域卡片
        drop_card = ModernCard()
        drop_layout = QVBoxLayout()
        drop_layout.setSpacing(10)

        drop_icon = QLabel("📁")
        drop_icon.setStyleSheet("font-size: 32px; border: none;")
        drop_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_layout.addWidget(drop_icon)

        drop_text = QLabel("点击选择视频文件")
        drop_text.setStyleSheet("font-size: 12px; color: #888; border: none;")
        drop_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_layout.addWidget(drop_text)

        select_btn = QPushButton("选择文件")
        select_btn.clicked.connect(self.select_files)
        drop_layout.addWidget(select_btn)

        drop_card.content_layout.addLayout(drop_layout)
        layout.addWidget(drop_card)

        # 文件列表卡片
        files_card = ModernCard("已选文件")
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        files_card.content_layout.addWidget(self.file_list)
        layout.addWidget(files_card, 1)

        # 操作按钮
        self.btn = QPushButton("🚀 开始处理")
        self.btn.setMinimumHeight(42)
        self.btn.setEnabled(False)
        self.btn.clicked.connect(self.process)
        layout.addWidget(self.btn)

        # 进度卡片
        progress_card = ModernCard("处理进度")
        self.progress = QProgressBar()
        self.progress.setMinimumHeight(24)
        progress_card.content_layout.addWidget(self.progress)

        self.status = QLabel("等待文件...")
        self.status.setStyleSheet("color: #888; font-size: 11px; border: none;")
        progress_card.content_layout.addWidget(self.status)
        layout.addWidget(progress_card)

        return panel

    def create_right_panel(self):
        """创建右侧设置面板"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(15)
        layout.setContentsMargins(0, 0, 0, 0)

        # 基础设置卡片
        basic_card = ModernCard("⚙️ 基础设置")
        basic_grid = QGridLayout()
        basic_grid.setSpacing(10)
        basic_grid.setColumnStretch(1, 1)

        # 静音阈值
        basic_grid.addWidget(QLabel("静音阈值:"), 0, 0)
        self.threshold = QDoubleSpinBox()
        self.threshold.setRange(0.001, 1.0)
        self.threshold.setValue(0.01)
        self.threshold.setSingleStep(0.001)
        self.threshold.setDecimals(3)
        basic_grid.addWidget(self.threshold, 0, 1)

        # 最小时长
        basic_grid.addWidget(QLabel("最小时长(秒):"), 1, 0)
        self.min_duration = QDoubleSpinBox()
        self.min_duration.setRange(0.5, 60.0)
        self.min_duration.setValue(3.0)
        basic_grid.addWidget(self.min_duration, 1, 1)

        # 输出文件
        basic_grid.addWidget(QLabel("输出文件:"), 2, 0)
        self.output_file = QLineEdit("output.mp4")
        basic_grid.addWidget(self.output_file, 2, 1)

        basic_card.content_layout.addLayout(basic_grid)
        layout.addWidget(basic_card)

        # AI 增强卡片
        ai_card = ModernCard("🤖 AI 增强")
        ai_grid = QGridLayout()
        ai_grid.setSpacing(10)
        ai_grid.setColumnStretch(1, 1)

        ai_grid.addWidget(QLabel("语音检测 (VAD):"), 0, 0)
        self.enable_vad = QComboBox()
        self.enable_vad.addItems(["禁用", "启用"])
        ai_grid.addWidget(self.enable_vad, 0, 1)

        ai_grid.addWidget(QLabel("场景分割:"), 1, 0)
        self.enable_scene = QComboBox()
        self.enable_scene.addItems(["禁用", "启用"])
        ai_grid.addWidget(self.enable_scene, 1, 1)

        ai_grid.addWidget(QLabel("人脸检测:"), 2, 0)
        self.enable_face = QComboBox()
        self.enable_face.addItems(["禁用", "启用"])
        ai_grid.addWidget(self.enable_face, 2, 1)

        ai_card.content_layout.addLayout(ai_grid)
        layout.addWidget(ai_card)

        # 高级设置卡片
        advanced_card = ModernCard("🔧 高级设置")
        adv_grid = QGridLayout()
        adv_grid.setSpacing(10)
        adv_grid.setColumnStretch(1, 1)

        adv_grid.addWidget(QLabel("编码器:"), 0, 0)
        self.codec = QComboBox()
        self.codec.addItems(["libx264 (CPU)", "自动检测", "h264_nvenc (GPU)"])
        adv_grid.addWidget(self.codec, 0, 1)

        adv_grid.addWidget(QLabel("编码速度:"), 1, 0)
        self.preset = QComboBox()
        self.preset.addItems(["ultrafast", "superfast", "veryfast", "faster", "fast", "medium"])
        self.preset.setCurrentText("fast")
        adv_grid.addWidget(self.preset, 1, 1)

        advanced_card.content_layout.addLayout(adv_grid)
        layout.addWidget(advanced_card)

        # 快捷键提示
        help_card = ModernCard("⌨️ 快捷键")
        help_layout = QVBoxLayout()
        help_layout.setSpacing(4)
        shortcuts = [
            "Ctrl+O - 打开文件",
            "Delete - 删除选中",
            "Ctrl+R - 开始处理"
        ]
        for shortcut in shortcuts:
            label = QLabel(shortcut)
            label.setStyleSheet("color: #888; font-size: 11px; border: none;")
            help_layout.addWidget(label)
        help_card.content_layout.addLayout(help_layout)
        layout.addWidget(help_card)

        layout.addStretch()
        scroll.setWidget(container)
        return scroll

    def select_files(self):
        """选择文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择视频文件",
            "",
            "视频文件 (*.mp4 *.avi *.mov *.mkv);;所有文件 (*.*)"
        )
        if files:
            self.add_files(files)

    def add_files(self, files):
        """添加文件"""
        for file in files:
            if file not in self.files and Path(file).suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv']:
                self.files.append(file)
                item = QListWidgetItem(f"📹 {Path(file).name}")
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

    def remove_selected(self):
        """删除选中的文件"""
        selected = self.file_list.selectedItems()
        if not selected:
            return

        for item in reversed(selected):
            row = self.file_list.row(item)
            if 0 <= row < len(self.files):
                self.files.pop(row)
                self.file_list.takeItem(row)

        if not self.files:
            self.btn.setEnabled(False)
            self.status.setText("等待文件...")
        else:
            self.status.setText(f"✅ 当前有 {len(self.files)} 个文件")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        self.add_files(files)

    def process(self):
        """开始处理"""
        if not self.files:
            QMessageBox.warning(self, "警告", "请先添加视频文件！")
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
            0.3, 3, 0.5,
            False, 0.02, 5.0,
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
        file_name = Path(name).name
        self.status.setText(f"🎬 处理中 ({current}/{total}): {file_name}")

    def process_finished(self, message):
        self.status.setText(message)
        self.btn.setEnabled(True)
        self.btn.setText("🚀 开始处理")
        if "完成" in message:
            QMessageBox.information(self, "完成", message)


def main():
    app = QApplication([])
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    window = ModernMainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
