#!/usr/bin/env python3
"""现代化 GUI - 专业深灰色主题（PyQt6实现）"""
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QListWidget, QPushButton, QProgressBar, QLabel, QDoubleSpinBox,
                             QLineEdit, QGridLayout, QComboBox, QFrame,
                             QListWidgetItem, QFileDialog, QMessageBox, QDialog)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QKeySequence, QShortcut
from gui import ProcessThread


# 翻译字典
TRANSLATIONS = {
    'en': {
        'app_title': 'KOOI Cut',
        'app_subtitle': 'Video Processing Tool',
        'settings': 'Settings',
        'language': 'Language',
        'drop_files': 'Drop video files here or click to select',
        'files': 'FILES',
        'start_processing': 'Start Processing',
        'processing': 'Processing...',
        'waiting': 'Waiting for files...',
        'files_selected': '{} file(s) selected',
        'processing_status': 'Processing ({}/{}): {}',
        'warning': 'Warning',
        'warning_no_files': 'Please add video files first!',
        'complete': 'Complete',
        'select_videos': 'Select Video Files',
        'video_files': 'Video Files (*.mp4 *.avi *.mov *.mkv);;All Files (*.*)',

        # Settings Dialog
        'settings_title': 'Settings',
        'basic_settings': 'BASIC SETTINGS',
        'silence_threshold': 'Silence Threshold:',
        'min_duration': 'Min Duration (s):',
        'output_file': 'Output File:',
        'ai_enhancements': 'AI ENHANCEMENTS',
        'vad': 'Voice Activity Detection:',
        'scene_detection': 'Scene Detection:',
        'face_detection': 'Face Detection:',
        'advanced_settings': 'ADVANCED SETTINGS',
        'encoder': 'Encoder:',
        'preset': 'Preset:',
        'cancel': 'Cancel',
        'apply': 'Apply',
        'disabled': 'Disabled',
        'enabled': 'Enabled',
        'auto_detect': 'Auto Detect',
    },
    'zh': {
        'app_title': 'KOOI Cut',
        'app_subtitle': '智能视频剪辑工具',
        'settings': '设置',
        'language': '语言',
        'drop_files': '拖拽视频文件到此处，或点击选择',
        'files': '文件列表',
        'start_processing': '开始处理',
        'processing': '处理中...',
        'waiting': '等待文件...',
        'files_selected': '已选择 {} 个文件',
        'processing_status': '处理中 ({}/{}): {}',
        'warning': '警告',
        'warning_no_files': '请先添加视频文件！',
        'complete': '完成',
        'select_videos': '选择视频文件',
        'video_files': '视频文件 (*.mp4 *.avi *.mov *.mkv);;所有文件 (*.*)',

        # Settings Dialog
        'settings_title': '设置',
        'basic_settings': '基础设置',
        'silence_threshold': '静音阈值:',
        'min_duration': '最小时长(秒):',
        'output_file': '输出文件:',
        'ai_enhancements': 'AI 增强',
        'vad': '语音检测 (VAD):',
        'scene_detection': '场景分割:',
        'face_detection': '人脸检测:',
        'advanced_settings': '高级设置',
        'encoder': '编码器:',
        'preset': '编码速度:',
        'cancel': '取消',
        'apply': '确定',
        'disabled': '禁用',
        'enabled': '启用',
        'auto_detect': '自动检测',
    }
}


class SettingsDialog(QDialog):
    """设置对话框"""

    def __init__(self, parent=None, lang='en'):
        super().__init__(parent)
        self.lang = lang
        self.setModal(True)
        self.resize(480, 520)

        # 深灰色主题
        self.setStyleSheet("""
            QDialog {
                background: #0d0d0d;
            }
            QWidget {
                background: transparent;
                color: #cccccc;
                font-family: 'Segoe UI', 'Microsoft YaHei', 'Noto Sans CJK SC', sans-serif;
                font-size: 12px;
            }
            QLabel {
                color: #cccccc;
            }
            QLabel#sectionTitle {
                color: #888888;
                font-size: 10px;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 1px;
                padding: 8px 0px 4px 0px;
            }
            QLabel#separator {
                background: #1a1a1a;
            }
            QPushButton {
                background: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #5CBF60;
            }
            QPushButton:pressed {
                background: #45a049;
            }
            QPushButton#cancelButton {
                background: #2a2a2a;
            }
            QPushButton#cancelButton:hover {
                background: #333333;
            }
            QLineEdit, QDoubleSpinBox, QComboBox {
                background: #1a1a1a;
                border: 1px solid #2a2a2a;
                padding: 6px 8px;
                color: #cccccc;
            }
            QLineEdit:focus, QDoubleSpinBox:focus, QComboBox:focus {
                border: 1px solid #4CAF50;
                background: #242424;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
        """)

        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 16, 20, 16)

        # 基础设置
        self.basic_title = QLabel()
        self.basic_title.setObjectName("sectionTitle")
        layout.addWidget(self.basic_title)

        basic_grid = QGridLayout()
        basic_grid.setSpacing(10)
        basic_grid.setColumnStretch(1, 1)
        basic_grid.setContentsMargins(0, 0, 0, 0)

        self.threshold_label = QLabel()
        basic_grid.addWidget(self.threshold_label, 0, 0)
        self.threshold = QDoubleSpinBox()
        self.threshold.setRange(0.001, 1.0)
        self.threshold.setValue(0.01)
        self.threshold.setSingleStep(0.001)
        self.threshold.setDecimals(3)
        basic_grid.addWidget(self.threshold, 0, 1)

        self.duration_label = QLabel()
        basic_grid.addWidget(self.duration_label, 1, 0)
        self.min_duration = QDoubleSpinBox()
        self.min_duration.setRange(0.5, 60.0)
        self.min_duration.setValue(3.0)
        basic_grid.addWidget(self.min_duration, 1, 1)

        self.output_label = QLabel()
        basic_grid.addWidget(self.output_label, 2, 0)
        self.output_file = QLineEdit("output.mp4")
        basic_grid.addWidget(self.output_file, 2, 1)

        layout.addLayout(basic_grid)

        # 分割线
        sep1 = QLabel()
        sep1.setObjectName("separator")
        sep1.setFixedHeight(1)
        layout.addWidget(sep1)

        # AI 增强
        self.ai_title = QLabel()
        self.ai_title.setObjectName("sectionTitle")
        layout.addWidget(self.ai_title)

        ai_grid = QGridLayout()
        ai_grid.setSpacing(10)
        ai_grid.setColumnStretch(1, 1)
        ai_grid.setContentsMargins(0, 0, 0, 0)

        self.vad_label = QLabel()
        ai_grid.addWidget(self.vad_label, 0, 0)
        self.enable_vad = QComboBox()
        ai_grid.addWidget(self.enable_vad, 0, 1)

        self.scene_label = QLabel()
        ai_grid.addWidget(self.scene_label, 1, 0)
        self.enable_scene = QComboBox()
        ai_grid.addWidget(self.enable_scene, 1, 1)

        self.face_label = QLabel()
        ai_grid.addWidget(self.face_label, 2, 0)
        self.enable_face = QComboBox()
        ai_grid.addWidget(self.enable_face, 2, 1)

        layout.addLayout(ai_grid)

        # 分割线
        sep2 = QLabel()
        sep2.setObjectName("separator")
        sep2.setFixedHeight(1)
        layout.addWidget(sep2)

        # 高级设置
        self.adv_title = QLabel()
        self.adv_title.setObjectName("sectionTitle")
        layout.addWidget(self.adv_title)

        adv_grid = QGridLayout()
        adv_grid.setSpacing(10)
        adv_grid.setColumnStretch(1, 1)
        adv_grid.setContentsMargins(0, 0, 0, 0)

        self.encoder_label = QLabel()
        adv_grid.addWidget(self.encoder_label, 0, 0)
        self.codec = QComboBox()
        adv_grid.addWidget(self.codec, 0, 1)

        self.preset_label = QLabel()
        adv_grid.addWidget(self.preset_label, 1, 0)
        self.preset = QComboBox()
        self.preset.addItems(["ultrafast", "superfast", "veryfast", "faster", "fast", "medium"])
        self.preset.setCurrentText("fast")
        adv_grid.addWidget(self.preset, 1, 1)

        layout.addLayout(adv_grid)

        layout.addStretch()

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self.cancel_btn = QPushButton()
        self.cancel_btn.setObjectName("cancelButton")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        self.ok_btn = QPushButton()
        self.ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.ok_btn)

        layout.addLayout(btn_layout)

        self.update_language(self.lang)

    def update_language(self, lang):
        """更新语言"""
        self.lang = lang
        t = TRANSLATIONS[lang]

        self.setWindowTitle(t['settings_title'])
        self.basic_title.setText(t['basic_settings'])
        self.threshold_label.setText(t['silence_threshold'])
        self.duration_label.setText(t['min_duration'])
        self.output_label.setText(t['output_file'])

        self.ai_title.setText(t['ai_enhancements'])
        self.vad_label.setText(t['vad'])
        self.scene_label.setText(t['scene_detection'])
        self.face_label.setText(t['face_detection'])

        self.adv_title.setText(t['advanced_settings'])
        self.encoder_label.setText(t['encoder'])
        self.preset_label.setText(t['preset'])

        self.cancel_btn.setText(t['cancel'])
        self.ok_btn.setText(t['apply'])

        # 更新下拉框选项
        self.enable_vad.clear()
        self.enable_vad.addItems([t['disabled'], t['enabled']])

        self.enable_scene.clear()
        self.enable_scene.addItems([t['disabled'], t['enabled']])

        self.enable_face.clear()
        self.enable_face.addItems([t['disabled'], t['enabled']])

        self.codec.clear()
        if lang == 'zh':
            self.codec.addItems(["libx264 (CPU)", t['auto_detect'], "h264_nvenc (GPU)"])
        else:
            self.codec.addItems(["libx264 (CPU)", t['auto_detect'], "h264_nvenc (GPU)"])

    def get_config(self):
        """获取配置"""
        t = TRANSLATIONS[self.lang]
        return {
            'threshold': self.threshold.value(),
            'min_duration': self.min_duration.value(),
            'output_file': self.output_file.text(),
            'enable_vad': self.enable_vad.currentText() == t['enabled'],
            'enable_scene': self.enable_scene.currentText() == t['enabled'],
            'enable_face': self.enable_face.currentText() == t['enabled'],
            'codec': self.codec.currentText(),
            'preset': self.preset.currentText(),
        }

    def set_output_file(self, path):
        """设置输出文件路径"""
        self.output_file.setText(path)


class ModernMainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.lang = 'zh'  # 默认中文
        self.setGeometry(100, 100, 720, 640)
        self.setAcceptDrops(True)

        # 深灰色主题
        self.setStyleSheet("""
            QMainWindow {
                background: #0d0d0d;
            }
            QWidget {
                background: transparent;
                color: #cccccc;
                font-family: 'Segoe UI', 'Microsoft YaHei', 'Noto Sans CJK SC', sans-serif;
                font-size: 12px;
            }
            QLabel {
                color: #cccccc;
            }
            QLabel#sectionTitle {
                color: #888888;
                font-size: 10px;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 1px;
                padding: 4px 0px;
            }
            QLabel#separator {
                background: #1a1a1a;
            }
            QPushButton {
                background: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #5CBF60;
            }
            QPushButton:pressed {
                background: #45a049;
            }
            QPushButton:disabled {
                background: #1a1a1a;
                color: #555555;
            }
            QPushButton#settingsButton, QPushButton#langButton {
                background: transparent;
                border: 1px solid #2a2a2a;
                color: #cccccc;
                padding: 6px 12px;
                font-size: 11px;
            }
            QPushButton#settingsButton:hover, QPushButton#langButton:hover {
                background: #1a1a1a;
                border: 1px solid #333333;
            }
            QPushButton#selectButton {
                background: transparent;
                border: 2px dashed #2a2a2a;
                color: #666666;
                padding: 30px;
                font-size: 12px;
            }
            QPushButton#selectButton:hover {
                border: 2px dashed #4CAF50;
                color: #4CAF50;
                background: #0f0f0f;
            }
            QListWidget {
                background: #0d0d0d;
                border: none;
                border-top: 1px solid #1a1a1a;
                border-bottom: 1px solid #1a1a1a;
                padding: 4px 0px;
                outline: none;
            }
            QListWidget::item {
                background: transparent;
                padding: 8px 4px;
                border-bottom: 1px solid #151515;
            }
            QListWidget::item:selected {
                background: #1a1a1a;
                color: #4CAF50;
            }
            QListWidget::item:hover:!selected {
                background: #111111;
            }
            QProgressBar {
                background: #1a1a1a;
                border: none;
                height: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: #4CAF50;
            }
        """)

        # 主布局
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        # 标题区域
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)

        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)

        self.title = QLabel()
        self.title.setStyleSheet("font-size: 24px; font-weight: 600; color: #4CAF50; letter-spacing: 1px;")
        title_layout.addWidget(self.title)

        self.subtitle = QLabel()
        self.subtitle.setStyleSheet("font-size: 11px; color: #666666; font-weight: 400;")
        title_layout.addWidget(self.subtitle)

        header_layout.addWidget(title_container)
        header_layout.addStretch()

        # 语言切换按钮
        self.lang_btn = QPushButton()
        self.lang_btn.setObjectName("langButton")
        self.lang_btn.clicked.connect(self.toggle_language)
        header_layout.addWidget(self.lang_btn)

        # 设置按钮
        self.settings_btn = QPushButton()
        self.settings_btn.setObjectName("settingsButton")
        self.settings_btn.clicked.connect(self.open_settings)
        header_layout.addWidget(self.settings_btn)

        main_layout.addWidget(header)

        # 分割线
        sep1 = QLabel()
        sep1.setObjectName("separator")
        sep1.setFixedHeight(1)
        main_layout.addWidget(sep1)

        # 拖拽选择区域
        self.select_btn = QPushButton()
        self.select_btn.setObjectName("selectButton")
        self.select_btn.clicked.connect(self.select_files)
        self.select_btn.setMinimumHeight(120)
        main_layout.addWidget(self.select_btn)

        # 文件列表标题
        self.list_title = QLabel()
        self.list_title.setObjectName("sectionTitle")
        main_layout.addWidget(self.list_title)

        # 文件列表
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        main_layout.addWidget(self.file_list, 1)

        # 开始按钮
        self.btn = QPushButton()
        self.btn.setMinimumHeight(40)
        self.btn.setEnabled(False)
        self.btn.clicked.connect(self.process)
        main_layout.addWidget(self.btn)

        # 进度条
        self.progress = QProgressBar()
        self.progress.setMinimumHeight(3)
        self.progress.setMaximumHeight(3)
        self.progress.setTextVisible(False)
        main_layout.addWidget(self.progress)

        # 状态
        self.status = QLabel()
        self.status.setStyleSheet("color: #666666; font-size: 11px; padding: 4px 0px;")
        main_layout.addWidget(self.status)

        self.files = []
        self.thread = None
        self.settings_dialog = SettingsDialog(self, self.lang)

        # 设置快捷键
        self.setup_shortcuts()

        # 更新语言
        self.update_language(self.lang)

    def setup_shortcuts(self):
        """设置快捷键"""
        QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self.select_files)
        QShortcut(QKeySequence("Delete"), self).activated.connect(self.remove_selected)
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(self.process)
        QShortcut(QKeySequence("Ctrl+,"), self).activated.connect(self.open_settings)
        QShortcut(QKeySequence("Ctrl+L"), self).activated.connect(self.toggle_language)

    def toggle_language(self):
        """切换语言"""
        self.lang = 'zh' if self.lang == 'en' else 'en'
        self.update_language(self.lang)
        self.settings_dialog.update_language(self.lang)

    def update_language(self, lang):
        """更新界面语言"""
        t = TRANSLATIONS[lang]

        self.setWindowTitle(t['app_title'])
        self.title.setText(t['app_title'])
        self.subtitle.setText(t['app_subtitle'])
        self.lang_btn.setText('EN' if lang == 'zh' else '中文')
        self.settings_btn.setText(t['settings'])
        self.select_btn.setText(t['drop_files'])
        self.list_title.setText(t['files'])

        # 更新按钮文本
        if self.btn.isEnabled():
            self.btn.setText(t['start_processing'])
        else:
            if self.thread and self.thread.isRunning():
                self.btn.setText(t['processing'])
            else:
                self.btn.setText(t['start_processing'])

        # 更新状态文本
        if not self.files:
            self.status.setText(t['waiting'])
        else:
            self.status.setText(t['files_selected'].format(len(self.files)))

    def open_settings(self):
        """打开设置对话框"""
        if self.files:
            last_file = Path(self.files[-1])
            output_name = f"cut-{last_file.name}"
            output_path = last_file.parent / output_name
            self.settings_dialog.set_output_file(str(output_path))

        self.settings_dialog.exec()

    def select_files(self):
        """选择文件"""
        t = TRANSLATIONS[self.lang]
        files, _ = QFileDialog.getOpenFileNames(
            self,
            t['select_videos'],
            "",
            t['video_files']
        )
        if files:
            self.add_files(files)

    def add_files(self, files):
        """添加文件"""
        t = TRANSLATIONS[self.lang]
        for file in files:
            if file not in self.files and Path(file).suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv']:
                self.files.append(file)
                item = QListWidgetItem(Path(file).name)
                self.file_list.addItem(item)

        if self.files:
            self.files.sort()
            self.btn.setEnabled(True)
            self.btn.setText(t['start_processing'])
            self.status.setText(t['files_selected'].format(len(self.files)))

            # 自动设置输出路径
            last_file = Path(self.files[-1])
            output_name = f"cut-{last_file.name}"
            output_path = last_file.parent / output_name
            self.settings_dialog.set_output_file(str(output_path))

    def remove_selected(self):
        """删除选中的文件"""
        t = TRANSLATIONS[self.lang]
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
            self.status.setText(t['waiting'])
        else:
            self.status.setText(t['files_selected'].format(len(self.files)))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        self.add_files(files)

    def process(self):
        """开始处理"""
        t = TRANSLATIONS[self.lang]
        if not self.files:
            QMessageBox.warning(self, t['warning'], t['warning_no_files'])
            return

        config = self.settings_dialog.get_config()

        self.btn.setEnabled(False)
        self.btn.setText(t['processing'])
        self.progress.setMaximum(len(self.files))

        # 获取编码器
        codec_map = {
            "libx264 (CPU)": "libx264",
            "Auto Detect": self._detect_gpu(),
            "h264_nvenc (GPU)": "h264_nvenc",
            "自动检测": self._detect_gpu(),
        }
        codec = codec_map.get(config['codec'], "libx264")

        self.thread = ProcessThread(
            self.files,
            config['output_file'],
            config['threshold'],
            config['min_duration'],
            codec,
            config['preset'],
            0.3, 3, 0.5,
            False, 0.02, 5.0,
            config['enable_vad'],
            config['enable_scene'],
            config['enable_face']
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
        t = TRANSLATIONS[self.lang]
        self.progress.setValue(current)
        file_name = Path(name).name
        self.status.setText(t['processing_status'].format(current, total, file_name))

    def process_finished(self, message):
        t = TRANSLATIONS[self.lang]
        self.status.setText(message)
        self.btn.setEnabled(True)
        self.btn.setText(t['start_processing'])
        if "完成" in message or "成功" in message.lower() or "complete" in message.lower():
            QMessageBox.information(self, t['complete'], message)


def main():
    app = QApplication([])
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    window = ModernMainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
