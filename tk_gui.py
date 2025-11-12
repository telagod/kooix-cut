#!/usr/bin/env python3
"""Tkinter GUI - 轻量级界面（仅使用Python标准库）"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
from kooix_cut import process_videos


class ProcessThread(threading.Thread):
    """视频处理线程"""

    def __init__(self, files, output_file, config, callback):
        super().__init__(daemon=True)
        self.files = files
        self.output_file = output_file
        self.config = config
        self.callback = callback
        self.progress = 0
        self.status = ""

    def run(self):
        """执行处理"""
        try:
            def progress_callback(progress, status):
                self.progress = progress
                self.status = status
                self.callback(progress, status, False)

            # 提取配置
            input_dir = Path(self.files[0]).parent

            process_videos(
                input_dir=str(input_dir),
                output_file=self.output_file,
                silence_threshold=self.config.get('threshold', 0.01),
                min_duration=self.config.get('min_duration', 3.0),
                preset=self.config.get('preset', 'fast'),
                progress_callback=progress_callback,
                # AI 增强参数
                use_vad=self.config.get('use_vad', False),
                use_scene_detect=self.config.get('use_scene', False),
                use_face_detect=self.config.get('use_face', False),
                # 视频检测参数
                detect_video_static=self.config.get('detect_video', False),
                static_threshold=self.config.get('video_threshold', 0.02),
                min_static_duration=self.config.get('min_static', 5.0),
            )

            self.callback(100, "✅ 处理完成！", True)
        except Exception as e:
            self.callback(0, f"❌ 错误: {str(e)}", True)


class ModernApp:
    def __init__(self, root):
        self.root = root
        self.root.title("KOOI Cut - 智能视频剪辑工具")
        self.root.geometry("1000x700")

        # 深色主题配置
        self.colors = {
            'bg': '#1a1a1a',
            'fg': '#e0e0e0',
            'card_bg': '#2a2a2a',
            'border': '#3a3a3a',
            'accent': '#4CAF50',
            'accent_dark': '#45a049',
            'hint': '#888888',
            'disabled': '#666666',
        }

        # 配置样式
        self.setup_style()

        # 主容器
        main_frame = tk.Frame(root, bg=self.colors['bg'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # 创建左右布局
        left_frame = self.create_left_panel(main_frame)
        left_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10))

        right_frame = self.create_right_panel(main_frame)
        right_frame.grid(row=0, column=1, sticky='nsew', padx=(10, 0))

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # 数据
        self.files = []
        self.thread = None

    def setup_style(self):
        """配置 ttk 样式"""
        style = ttk.Style()
        style.theme_use('clam')

        # 通用样式
        style.configure('.', background=self.colors['bg'], foreground=self.colors['fg'])

        # Frame 样式
        style.configure('Card.TFrame', background=self.colors['card_bg'],
                       relief='solid', borderwidth=1)

        # Label 样式
        style.configure('TLabel', background=self.colors['bg'],
                       foreground=self.colors['fg'])
        style.configure('Title.TLabel', font=('Arial', 24, 'bold'),
                       foreground=self.colors['accent'])
        style.configure('Subtitle.TLabel', font=('Arial', 11),
                       foreground=self.colors['hint'])
        style.configure('Hint.TLabel', font=('Arial', 9),
                       foreground=self.colors['hint'])

        # Button 样式
        style.configure('Accent.TButton', font=('Arial', 11, 'bold'),
                       background=self.colors['accent'],
                       foreground='white', padding=12)
        style.map('Accent.TButton',
                 background=[('active', self.colors['accent_dark']),
                            ('disabled', self.colors['disabled'])])

        # Entry 样式
        style.configure('TEntry', fieldbackground=self.colors['card_bg'],
                       foreground=self.colors['fg'], borderwidth=2)

        # Spinbox 样式
        style.configure('TSpinbox', fieldbackground=self.colors['card_bg'],
                       foreground=self.colors['fg'], borderwidth=2)

        # Listbox 样式
        style.configure('TListbox', background=self.colors['card_bg'],
                       foreground=self.colors['fg'], borderwidth=1)

        # Progressbar 样式
        style.configure('TProgressbar',
                       background=self.colors['accent'],
                       troughcolor=self.colors['card_bg'],
                       borderwidth=0, thickness=24)

    def create_card(self, parent, title=None):
        """创建卡片组件"""
        card = ttk.Frame(parent, style='Card.TFrame', padding=16)

        if title:
            title_label = ttk.Label(card, text=title,
                                   font=('Arial', 13, 'bold'),
                                   foreground=self.colors['accent'])
            title_label.pack(anchor='w', pady=(0, 10))

        content_frame = tk.Frame(card, bg=self.colors['card_bg'])
        content_frame.pack(fill='both', expand=True)

        return card, content_frame

    def create_left_panel(self, parent):
        """创建左侧面板"""
        frame = tk.Frame(parent, bg=self.colors['bg'])

        # 标题
        header = tk.Frame(frame, bg=self.colors['bg'])
        header.pack(fill='x', pady=(0, 20))

        title = ttk.Label(header, text="KOOI Cut", style='Title.TLabel')
        title.pack(anchor='w')

        subtitle = ttk.Label(header, text="智能视频剪辑工具", style='Subtitle.TLabel')
        subtitle.pack(anchor='w')

        # 拖拽区域
        drop_card, drop_content = self.create_card(frame)
        drop_card.pack(fill='x', pady=(0, 15))

        drop_icon = ttk.Label(drop_content, text="📁", font=('Arial', 36))
        drop_icon.pack(pady=10)

        drop_text = ttk.Label(drop_content, text="点击选择视频文件",
                             font=('Arial', 12), foreground=self.colors['hint'])
        drop_text.pack()

        # 选择按钮
        select_btn = ttk.Button(drop_content, text="选择文件",
                               command=self.select_files)
        select_btn.pack(pady=15)

        # 文件列表
        files_card, files_content = self.create_card(frame, "已选文件")
        files_card.pack(fill='both', expand=True, pady=(0, 15))

        # 创建 Listbox
        list_frame = tk.Frame(files_content, bg=self.colors['card_bg'])
        list_frame.pack(fill='both', expand=True)

        scrollbar = tk.Scrollbar(list_frame, bg=self.colors['card_bg'])
        scrollbar.pack(side='right', fill='y')

        self.file_list = tk.Listbox(list_frame,
                                    bg=self.colors['card_bg'],
                                    fg=self.colors['fg'],
                                    selectbackground=self.colors['accent'],
                                    selectforeground='white',
                                    borderwidth=0,
                                    highlightthickness=0,
                                    yscrollcommand=scrollbar.set)
        self.file_list.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.file_list.yview)

        # 开始按钮
        self.btn = ttk.Button(frame, text="🚀 开始处理",
                             style='Accent.TButton',
                             command=self.process, state='disabled')
        self.btn.pack(fill='x', pady=(0, 15))

        # 进度卡片
        progress_card, progress_content = self.create_card(frame, "处理进度")
        progress_card.pack(fill='x')

        self.progress = ttk.Progressbar(progress_content, mode='determinate',
                                       style='TProgressbar')
        self.progress.pack(fill='x', pady=(0, 10))

        self.status = ttk.Label(progress_content, text="等待文件...",
                               style='Hint.TLabel')
        self.status.pack(anchor='w')

        return frame

    def create_right_panel(self, parent):
        """创建右侧设置面板"""
        frame = tk.Frame(parent, bg=self.colors['bg'])

        # 创建 Canvas 用于滚动
        canvas = tk.Canvas(frame, bg=self.colors['bg'],
                          highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient='vertical',
                                command=canvas.yview,
                                bg=self.colors['bg'])
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 基础设置
        basic_card, basic_content = self.create_card(scrollable_frame, "⚙️ 基础设置")
        basic_card.pack(fill='x', pady=(0, 15))

        # 静音阈值
        self.create_setting(basic_content, "静音阈值", 0.001, 1.0, 0.01, 0.001,
                           "音量低于此值视为静音", 'threshold')

        # 最小时长
        self.create_setting(basic_content, "最小时长(秒)", 0.5, 60.0, 3.0, 0.5,
                           "保留片段的最小时长", 'min_duration')

        # 编码预设
        preset_frame = tk.Frame(basic_content, bg=self.colors['card_bg'])
        preset_frame.pack(fill='x', pady=8)

        tk.Label(preset_frame, text="编码预设", bg=self.colors['card_bg'],
                fg=self.colors['fg']).pack(side='left', padx=(0, 10))

        self.preset_var = tk.StringVar(value='fast')
        preset_combo = ttk.Combobox(preset_frame, textvariable=self.preset_var,
                                   values=['ultrafast', 'superfast', 'veryfast',
                                          'fast', 'medium'],
                                   state='readonly', width=15)
        preset_combo.pack(side='left')

        # 输出文件
        output_frame = tk.Frame(basic_content, bg=self.colors['card_bg'])
        output_frame.pack(fill='x', pady=8)

        tk.Label(output_frame, text="输出文件", bg=self.colors['card_bg'],
                fg=self.colors['fg']).pack(anchor='w', pady=(0, 5))

        self.output_var = tk.StringVar(value='output.mp4')
        output_entry = ttk.Entry(output_frame, textvariable=self.output_var)
        output_entry.pack(fill='x')

        # AI 增强设置
        ai_card, ai_content = self.create_card(scrollable_frame, "🤖 AI 增强")
        ai_card.pack(fill='x', pady=(0, 15))

        self.use_vad_var = tk.BooleanVar(value=False)
        self.create_checkbox(ai_content, "语音活动检测 (VAD)",
                            self.use_vad_var, "使用 WebRTC VAD 检测真实说话")

        self.use_scene_var = tk.BooleanVar(value=False)
        self.create_checkbox(ai_content, "场景分割检测",
                            self.use_scene_var, "基于直方图差异检测场景变化")

        self.use_face_var = tk.BooleanVar(value=False)
        self.create_checkbox(ai_content, "人脸检测",
                            self.use_face_var, "保留有人出镜的片段")

        # 视频检测设置
        video_card, video_content = self.create_card(scrollable_frame, "🎬 视频检测")
        video_card.pack(fill='x')

        self.detect_video_var = tk.BooleanVar(value=False)
        self.create_checkbox(video_content, "静态画面检测",
                            self.detect_video_var, "删除长时间静止的画面")

        self.create_setting(video_content, "静止阈值", 0.01, 0.1, 0.02, 0.01,
                           "画面变化低于此值视为静止", 'video_threshold')

        self.create_setting(video_content, "最小静止时长(秒)", 1.0, 30.0, 5.0, 1.0,
                           "删除静止片段的最小时长", 'min_static')

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return frame

    def create_setting(self, parent, label, min_val, max_val, default, step, hint, key):
        """创建数值设置项"""
        frame = tk.Frame(parent, bg=self.colors['card_bg'])
        frame.pack(fill='x', pady=8)

        tk.Label(frame, text=label, bg=self.colors['card_bg'],
                fg=self.colors['fg']).grid(row=0, column=0, sticky='w', padx=(0, 10))

        var = tk.DoubleVar(value=default)
        spinbox = tk.Spinbox(frame, from_=min_val, to=max_val, increment=step,
                            textvariable=var, width=10,
                            bg=self.colors['card_bg'], fg=self.colors['fg'],
                            buttonbackground=self.colors['border'])
        spinbox.grid(row=0, column=1, sticky='w')

        hint_label = tk.Label(frame, text=hint, bg=self.colors['card_bg'],
                             fg=self.colors['hint'], font=('Arial', 9))
        hint_label.grid(row=1, column=0, columnspan=2, sticky='w', pady=(2, 0))

        # 保存变量引用
        setattr(self, f'{key}_var', var)

    def create_checkbox(self, parent, label, variable, hint):
        """创建复选框设置项"""
        frame = tk.Frame(parent, bg=self.colors['card_bg'])
        frame.pack(fill='x', pady=8)

        cb = tk.Checkbutton(frame, text=label, variable=variable,
                           bg=self.colors['card_bg'], fg=self.colors['fg'],
                           selectcolor=self.colors['card_bg'],
                           activebackground=self.colors['card_bg'],
                           activeforeground=self.colors['accent'])
        cb.pack(anchor='w')

        hint_label = tk.Label(frame, text=hint, bg=self.colors['card_bg'],
                             fg=self.colors['hint'], font=('Arial', 9))
        hint_label.pack(anchor='w', padx=(20, 0))

    def select_files(self):
        """选择文件"""
        files = filedialog.askopenfilenames(
            title="选择视频文件",
            filetypes=[("视频文件", "*.mp4 *.avi *.mov *.mkv"), ("所有文件", "*.*")]
        )
        if files:
            self.add_files(files)

    def add_files(self, files):
        """添加文件到列表"""
        for file in files:
            file_path = Path(file)
            if file_path.suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv']:
                if str(file_path) not in self.files:
                    self.files.append(str(file_path))
                    self.file_list.insert('end', file_path.name)

        self.btn['state'] = 'normal' if self.files else 'disabled'
        self.status.config(text=f"已选择 {len(self.files)} 个文件")

    def process(self):
        """开始处理"""
        if not self.files:
            return

        # 禁用按钮
        self.btn['state'] = 'disabled'
        self.progress['value'] = 0
        self.status.config(text="正在处理...")

        # 收集配置
        config = {
            'threshold': self.threshold_var.get(),
            'min_duration': self.min_duration_var.get(),
            'preset': self.preset_var.get(),
            'use_vad': self.use_vad_var.get(),
            'use_scene': self.use_scene_var.get(),
            'use_face': self.use_face_var.get(),
            'detect_video': self.detect_video_var.get(),
            'video_threshold': self.video_threshold_var.get(),
            'min_static': self.min_static_var.get(),
        }

        # 启动线程
        self.thread = ProcessThread(
            self.files,
            self.output_var.get(),
            config,
            self.on_progress
        )
        self.thread.start()

    def on_progress(self, progress, status, done):
        """进度回调"""
        self.root.after(0, lambda: self._update_progress(progress, status, done))

    def _update_progress(self, progress, status, done):
        """更新进度（在主线程）"""
        self.progress['value'] = progress
        self.status.config(text=status)

        if done:
            self.btn['state'] = 'normal'
            if "完成" in status:
                messagebox.showinfo("完成", status)
            elif "错误" in status:
                messagebox.showerror("错误", status)


def main():
    """主函数"""
    root = tk.Tk()
    app = ModernApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
