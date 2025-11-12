#!/usr/bin/env python3
"""现代化 GUI - 增强版 Material Design 风格"""
import os
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QListWidget, QPushButton, QProgressBar, QLabel, QDoubleSpinBox,
                             QLineEdit, QGroupBox, QGridLayout, QTabWidget, QComboBox, QFrame,
                             QScrollArea, QListWidgetItem, QFileDialog, QMessageBox, QToolButton)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QSize, QTimer
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor, QKeySequence, QShortcut, QAction
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


class FileListItem(QWidget):
    """增强的文件列表项"""

    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        path = Path(file_path)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # 文件名行
        name_layout = QHBoxLayout()
        name_label = QLabel(f"📹 {path.name}")
        name_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        name_layout.addWidget(name_label)
        name_layout.addStretch()
        layout.addLayout(name_layout)

        # 文件信息行
        info_layout = QHBoxLayout()

        # 文件大小
        size_mb = path.stat().st_size / 1024 / 1024
        size_label = QLabel(f"💾 {size_mb:.1f} MB")
        size_label.setStyleSheet("color: #888; font-size: 11px;")
        info_layout.addWidget(size_label)

        # 文件类型
        ext_label = QLabel(f"📄 {path.suffix.upper()}")
        ext_label.setStyleSheet("color: #888; font-size: 11px;")
        info_layout.addWidget(ext_label)

        info_layout.addStretch()
        layout.addLayout(info_layout)


class StatsCard(ModernCard):
    """统计信息卡片"""

    def __init__(self, parent=None):
        super().__init__("📊 文件统计", parent)

        grid = QGridLayout()
        grid.setSpacing(12)

        # 文件数量
        grid.addWidget(QLabel("文件数量:"), 0, 0)
        self.count_label = QLabel("0")
        self.count_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        grid.addWidget(self.count_label, 0, 1)

        # 总大小
        grid.addWidget(QLabel("总大小:"), 1, 0)
        self.size_label = QLabel("0 MB")
        self.size_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        grid.addWidget(self.size_label, 1, 1)

        # 平均大小
        grid.addWidget(QLabel("平均大小:"), 2, 0)
        self.avg_label = QLabel("0 MB")
        self.avg_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        grid.addWidget(self.avg_label, 2, 1)

        self.content_layout.addLayout(grid)

    def update_stats(self, files):
        """更新统计信息"""
        if not files:
            self.count_label.setText("0")
            self.size_label.setText("0 MB")
            self.avg_label.setText("0 MB")
            return

        count = len(files)
        total_size = sum(Path(f).stat().st_size for f in files) / 1024 / 1024
        avg_size = total_size / count if count > 0 else 0

        self.count_label.setText(str(count))
        self.size_label.setText(f"{total_size:.1f} MB")
        self.avg_label.setText(f"{avg_size:.1f} MB")


class ModernMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KOOI Cut - 智能视频剪辑工具 (增强版)")
        self.setGeometry(100, 100, 1400, 900)
        self.setAcceptDrops(True)

        # 拖拽状态
        self.drag_active = False

        # 现代化深色主题
        self.setStyleSheet("""
            QMainWindow {
                background: #1a1a1a;
            }
            QWidget {
                background: transparent;
                color: #e0e0e0;
                font-family: 'Segoe UI', 'Microsoft YaHei', 'Noto Sans CJK SC', sans-serif;
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
            QToolButton {
                background: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
            }
            QToolButton:hover {
                background: #3a3a3a;
                border: 1px solid #4CAF50;
            }
            QToolButton:pressed {
                background: #4CAF50;
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
                padding: 4px;
                margin: 4px;
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
                height: 28px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #8BC34A);
                border-radius: 8px;
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
        header_layout.setSpacing(4)
        title = QLabel("KOOI Cut")
        title.setStyleSheet("font-size: 36px; font-weight: bold; color: #4CAF50;")
        subtitle = QLabel("智能视频剪辑工具 • 增强版")
        subtitle.setStyleSheet("font-size: 14px; color: #888;")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        left_layout.addWidget(header)

        # 拖拽区域卡片
        self.drop_card = ModernCard()
        self.drop_card.setMinimumHeight(180)
        drop_layout = QVBoxLayout()
        self.drop_icon = QLabel("📁")
        self.drop_icon.setStyleSheet("font-size: 56px;")
        self.drop_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_text = QLabel("拖拽视频文件到此处\n或点击下方按钮选择文件")
        self.drop_text.setStyleSheet("font-size: 16px; color: #888;")
        self.drop_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_layout.addWidget(self.drop_icon)
        drop_layout.addWidget(self.drop_text)

        # 选择文件按钮
        select_btn = QPushButton("📂 选择文件")
        select_btn.clicked.connect(self.select_files)
        drop_layout.addWidget(select_btn)

        self.drop_card.content_layout.addLayout(drop_layout)
        left_layout.addWidget(self.drop_card)

        # 批量操作按钮
        batch_layout = QHBoxLayout()
        batch_layout.setSpacing(8)

        select_all_btn = QToolButton()
        select_all_btn.setText("✓ 全选")
        select_all_btn.setToolTip("Ctrl+A")
        select_all_btn.clicked.connect(self.select_all)
        batch_layout.addWidget(select_all_btn)

        clear_btn = QToolButton()
        clear_btn.setText("🗑️ 清空")
        clear_btn.clicked.connect(self.clear_all)
        batch_layout.addWidget(clear_btn)

        remove_btn = QToolButton()
        remove_btn.setText("✕ 删除选中")
        remove_btn.setToolTip("Delete")
        remove_btn.clicked.connect(self.remove_selected)
        batch_layout.addWidget(remove_btn)

        batch_layout.addStretch()
        left_layout.addLayout(batch_layout)

        # 文件列表卡片
        files_card = ModernCard("已选文件")
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        files_card.content_layout.addWidget(self.file_list)
        left_layout.addWidget(files_card)

        # 统计信息
        self.stats_card = StatsCard()
        left_layout.addWidget(self.stats_card)

        # 操作按钮
        btn_layout = QHBoxLayout()
        self.btn = QPushButton("🚀 开始处理")
        self.btn.setMinimumHeight(52)
        self.btn.setEnabled(False)
        self.btn.clicked.connect(self.process)
        btn_layout.addWidget(self.btn)
        left_layout.addLayout(btn_layout)

        # 进度卡片
        progress_card = ModernCard("处理进度")
        self.progress = QProgressBar()
        self.progress.setMinimumHeight(36)
        self.progress.setFormat("%p% - %v/%m")
        self.status = QLabel("等待文件...")
        self.status.setStyleSheet("color: #888; margin-top: 8px; font-size: 12px;")
        self.status.setWordWrap(True)
        progress_card.content_layout.addWidget(self.progress)
        progress_card.content_layout.addWidget(self.status)
        left_layout.addWidget(progress_card)

        main_layout.addWidget(left_panel, 2)

        # 右侧设置面板
        right_panel = self.create_settings_panel()
        main_layout.addWidget(right_panel, 1)

        self.files = []
        self.thread = None

        # 设置快捷键
        self.setup_shortcuts()

    def setup_shortcuts(self):
        """设置快捷键"""
        # Ctrl+O 打开文件
        open_shortcut = QShortcut(QKeySequence("Ctrl+O"), self)
        open_shortcut.activated.connect(self.select_files)

        # Ctrl+A 全选
        select_all_shortcut = QShortcut(QKeySequence("Ctrl+A"), self)
        select_all_shortcut.activated.connect(self.select_all)

        # Delete 删除选中
        delete_shortcut = QShortcut(QKeySequence("Delete"), self)
        delete_shortcut.activated.connect(self.remove_selected)

        # Ctrl+R 开始处理
        run_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        run_shortcut.activated.connect(self.process)

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
        self.preset.setCurrentText("fast")
        adv_grid.addWidget(self.preset, 1, 1)

        advanced_card.content_layout.addLayout(adv_grid)
        layout.addWidget(advanced_card)

        # 快捷键提示
        help_card = ModernCard("⌨️ 快捷键")
        help_layout = QVBoxLayout()
        shortcuts = [
            "Ctrl+O - 打开文件",
            "Ctrl+A - 全选",
            "Delete - 删除选中",
            "Ctrl+R - 开始处理"
        ]
        for shortcut in shortcuts:
            label = QLabel(shortcut)
            label.setStyleSheet("color: #888; font-size: 11px;")
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

                # 创建自定义列表项
                item_widget = FileListItem(file)
                item = QListWidgetItem(self.file_list)
                item.setSizeHint(item_widget.sizeHint())
                self.file_list.addItem(item)
                self.file_list.setItemWidget(item, item_widget)

        if self.files:
            self.files.sort()
            self.btn.setEnabled(True)
            self.update_stats()
            self.status.setText(f"✅ 已添加 {len(self.files)} 个文件，准备就绪")

            # 自动设置输出路径
            last_file = Path(self.files[-1])
            output_name = f"cut-{last_file.name}"
            output_path = last_file.parent / output_name
            self.output_file.setText(str(output_path))

    def update_stats(self):
        """更新统计信息"""
        self.stats_card.update_stats(self.files)

    def select_all(self):
        """全选"""
        self.file_list.selectAll()

    def clear_all(self):
        """清空所有文件"""
        if not self.files:
            return

        reply = QMessageBox.question(
            self,
            "确认清空",
            f"确定要清空所有 {len(self.files)} 个文件吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.files.clear()
            self.file_list.clear()
            self.update_stats()
            self.btn.setEnabled(False)
            self.status.setText("等待文件...")

    def remove_selected(self):
        """删除选中的文件"""
        selected = self.file_list.selectedItems()
        if not selected:
            return

        # 从后往前删除，避免索引问题
        for item in reversed(selected):
            row = self.file_list.row(item)
            if 0 <= row < len(self.files):
                self.files.pop(row)
                self.file_list.takeItem(row)

        self.update_stats()

        if not self.files:
            self.btn.setEnabled(False)
            self.status.setText("等待文件...")
        else:
            self.status.setText(f"✅ 当前有 {len(self.files)} 个文件")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            self.drag_active = True
            self.drop_card.setStyleSheet("""
                ModernCard {
                    background: #2a3a2a;
                    border: 2px dashed #4CAF50;
                    border-radius: 12px;
                }
            """)
            self.drop_text.setStyleSheet("font-size: 16px; color: #4CAF50; font-weight: bold;")
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.drag_active = False
        self.drop_card.setStyleSheet("")
        self.drop_text.setStyleSheet("font-size: 16px; color: #888;")

    def dropEvent(self, event):
        self.drag_active = False
        self.drop_card.setStyleSheet("")
        self.drop_text.setStyleSheet("font-size: 16px; color: #888;")

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
        file_name = Path(name).name
        self.status.setText(f"🎬 正在处理 ({current}/{total}): {file_name}")

    def process_finished(self, message):
        self.status.setText(message)
        self.btn.setEnabled(True)
        self.btn.setText("🚀 开始处理")

        if "完成" in message:
            QMessageBox.information(self, "完成", message)


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
