import tkinter as tk
from tkinter import ttk, messagebox
import json
from pathlib import Path
import pyotp
import pyperclip
from typing import Dict
from datetime import datetime
import os
import sys

class TOTPGenerator:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("TOTP Generator")
        self.window.geometry("500x600")
        self.window.configure(bg='#f0f0f0')
        
        # 存储所有的TOTP条目
        self.totp_entries: Dict[str, Dict] = {}
        
        self.setup_ui()
        self.load_config()
        self.update_codes()
        self.center_window()
    
    def center_window(self):
        """将窗口居中显示"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        """设置UI界面"""
        style = ttk.Style()
        
        # 配置主题颜色
        self.colors = {
            'primary': '#3e5cf5',  # Google Blue
            'bg': '#f0f0f0',       # 背景色
            'white': '#ffffff',      # 白色
            'button': '#3e5cf5',    # 新增：按钮颜色
            'button_text': '#000'  # 新增：按钮文本颜色
        }
        
        # 配置样式
        style.configure('Custom.TFrame', background=self.colors['white'])
        style.configure('Header.TLabel', 
                       font=('Segoe UI', 16, 'bold'),
                       padding=10,
                       background=self.colors['white'])
        # 复制按钮样式
        style.configure('Round.TButton',
                        padding=(5, 2),
                        relief="flat",
                        background=self.colors['button'],
                        foreground=self.colors['button_text'])
        
        
        # 创建主框架
        main_frame = ttk.Frame(self.window, padding="20", style='Custom.TFrame')
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text="Authentication Codes",
            style='Header.TLabel'
        )
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # 创建滚动容器
        container = ttk.Frame(main_frame)
        container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        canvas = tk.Canvas(container, bg=self.colors['white'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas, style='Custom.TFrame')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=440)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 绑定鼠标滚轮
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # 配置权重
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        
        # 进度条区域
        self.setup_progress_area(main_frame)
    
    def setup_progress_area(self, parent):
        """设置进度条区域"""
        progress_frame = ttk.Frame(parent, style='Custom.TFrame')
        progress_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=20)
        
        style = ttk.Style()
        style.configure("Horizontal.TProgressbar",
                       troughcolor=self.colors['bg'],
                       background=self.colors['primary'])
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            orient="horizontal",
            length=300,
            mode="determinate",
            style="Horizontal.TProgressbar"
        )
        self.progress_bar.grid(row=0, column=0, padx=(0, 10))
        
        self.time_label = ttk.Label(
            progress_frame,
            text="30s",
            font=('Segoe UI', 10),
            background=self.colors['white']
        )
        self.time_label.grid(row=0, column=1)
    
    def create_totp_entry(self, name: str, key: str) -> None:
        """创建单个TOTP条目"""
        frame = ttk.Frame(self.scrollable_frame, style='Custom.TFrame')
        frame.pack(fill=tk.X, pady=5, padx=5)
        
        # 配置列的权重和最小宽度
        frame.grid_columnconfigure(0, weight=1, minsize=80)  # 服务名称列
        frame.grid_columnconfigure(1, weight=1, minsize=100)  # TOTP码列
        frame.grid_columnconfigure(2, weight=0, minsize=80)   # 按钮列
        
        # 服务名称 (左对齐)
        name_label = ttk.Label(
            frame, 
            text=name, 
            font=('Segoe UI', 11, 'bold'),
            background=self.colors['white']
        )
        name_label.grid(row=0, column=0, sticky=tk.W, padx=10)
        
        # TOTP码 (居中对齐)
        code_label = ttk.Label(
            frame, 
            text="------", 
            font=('Consolas', 14),
            foreground=self.colors['primary'],
            background=self.colors['white'],
            width=6  # 固定宽度为6个字符
        )
        code_label.grid(row=0, column=1, sticky=tk.EW, padx=(0, 10))
        
        # 复制按钮 (右对齐)
        copy_button = ttk.Button(
            frame,
            text="复制",
            command=lambda: self.copy_code(name),
            style='Round.TButton',
            width=8
        )
        copy_button.grid(row=0, column=2, sticky=tk.E, padx=5)


        try:
            totp = pyotp.TOTP(key)
            totp.now()
            self.totp_entries[name] = {
                'key': key,
                'code_label': code_label,
                'totp': totp
            }
        except Exception as e:
            code_label.configure(text="Invalid Key")
            copy_button.configure(state="disabled")
            messagebox.showerror(
                "Error",
                f"Invalid TOTP key for {name}: {str(e)}"
    )

    def get_config_path(self) -> Path:
        """获取配置文件路径"""
        if getattr(sys, 'frozen', False):
            # 打包后的配置文件路径
            base_path = Path(sys.executable).parent
            config_path = base_path / 'config' / 'totp_config.json'
            
            # 如果配置文件不存在，尝试从示例文件复制
            if not config_path.exists():
                example_path = base_path / 'config' / 'totp_config.example.json'
                if example_path.exists():
                    import shutil
                    shutil.copy2(example_path, config_path)
                    messagebox.showinfo(
                        "配置文件已创建",
                        f"已从示例文件创建配置文件：\n{config_path}\n请编辑此文件添加你的TOTP密钥。"
                    )
            
            return config_path
        else:
            # 开发环境的配置文件路径
            return Path('./.keys/totp_config.json')

    def load_config(self) -> None:
        """加载TOTP配置"""
        config_path = self.get_config_path()
        try:
            if not config_path.exists():
                messagebox.showerror(
                    "Error",
                    f"配置文件未找到：{config_path}\n"
                    "请确保配置文件存在并包含有效的TOTP密钥。\n\n"
                    "配置文件格式示例：\n"
                    '{\n    "服务名称": "BASE32编码的密钥",\n    "示例": "JBSWY3DPEHPK3PXP"\n}'
                )
                return
            
            with config_path.open(encoding='utf-8') as f:
                config = json.load(f)
                
            if not config:
                messagebox.showwarning(
                    "Warning",
                    "配置文件是空的，请添加TOTP密钥。"
                )
                return
            
            # 清除现有条目
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            
            # 创建新条目
            for name, key in config.items():
                self.create_totp_entry(name, key)
                
        except json.JSONDecodeError:
            messagebox.showerror(
                "Error", 
                f"配置文件格式错误：{config_path}\n"
                "请确保是有效的JSON格式。"
            )
        except Exception as e:
            messagebox.showerror(
                "Error", 
                f"加载配置文件失败：{str(e)}"
            )
    
    def copy_code(self, name: str) -> None:
        """复制TOTP码到剪贴板"""
        code = self.totp_entries[name]['code_label']['text']
        pyperclip.copy(code)
        
        # 显示复制成功提示
        self.show_copy_feedback(name)
    
    def show_copy_feedback(self, name: str) -> None:
        """显示复制成功的反馈"""
        original_text = self.totp_entries[name]['code_label']['text']
        self.totp_entries[name]['code_label'].configure(text="Copied!")
        
        # 1秒后恢复原始文本
        self.window.after(1000, lambda: self.totp_entries[name]['code_label'].configure(text=original_text))
    
    def update_codes(self) -> None:
        """更新所有TOTP码"""
        current_time = datetime.now().timestamp()
        time_step = 30
        
        # 计算进度
        progress = ((time_step - (int(current_time) % time_step)) / time_step) * 100
        self.progress_bar['value'] = progress
        self.time_label['text'] = f"{int(time_step - (int(current_time) % time_step))}s"
        
        # 更新TOTP码
        for entry in self.totp_entries.values():
            new_code = entry['totp'].now()
            entry['code_label']['text'] = new_code
        
        # 每秒更新一次
        self.window.after(1000, self.update_codes)
    
    def run(self):
        """运行应用程序"""
        self.window.mainloop()

if __name__ == "__main__":
    app = TOTPGenerator()
    app.run() 