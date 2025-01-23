import sys
from cx_Freeze import setup, Executable

# 依赖项
build_exe_options = {
    "packages": ["tkinter", "pyotp", "pyperclip"],
    "excludes": [],
    "include_files": [
        # 确保配置文件被正确复制到正确的位置
        ("totp_config.example.json", "config/totp_config.json")  # 直接作为 totp_config.json 复制
    ]
}

# 基础配置
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # 使用Windows GUI

setup(
    name="TOTP Generator",
    version="1.0",
    description="TOTP Code Generator",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "totp_gui.py", 
            base=base,
            target_name="TOTP Generator.exe",
            icon="icon.ico"  # 如果你有图标的话
        )
    ]
) 