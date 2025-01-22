#!/usr/local/bin/python3
import pyotp
import sys
import argparse
import json
from pathlib import Path
from typing import Optional, Dict
import pyperclip

def load_config() -> Dict[str, str]:
    """加载TOTP密钥配置文件"""
    # 首先尝试环境变量中的配置路径
    config_path = Path('./.keys/totp_config.json')
    if not config_path.exists():
        print(f"Config file not found at: {config_path}")
    
    try:
        with config_path.open(encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {config_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading config from {config_path}: {str(e)}")
        sys.exit(1)

def get_totp_key(type_name: str, config: Dict[str, str]) -> Optional[str]:
    """获取指定类型的TOTP密钥"""
    # 首先尝试从配置文件获取
    if type_name in config:
        return config[type_name]
    
    # 向后兼容：尝试从单独的文件读取
    key_path = Path.home() / '.keys' / f'{type_name}_totp'
    if key_path.exists():
        try:
            with open(key_path) as f:
                return f.readline().strip()
        except Exception as e:
            print(f"Error reading key file: {str(e)}")
            return None
    
    return None

def generate_totp(key: str) -> Optional[str]:
    """生成TOTP码"""
    try:
        totp = pyotp.TOTP(key)
        return totp.now()
    except Exception as e:
        print(f"Error generating TOTP: {str(e)}")
        return None

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description='Generate TOTP codes for various services',
        epilog='Example: main.py ali'
    )
    parser.add_argument(
        'type', 
        nargs='?',  # 使type参数可选
        help='Type of TOTP code to generate (e.g., ali, github)'
    )
    
    args = parser.parse_args()

    # 加载配置
    config = load_config()

    # 如果没有提供参数或使用--list，显示可用的TOTP类型
    if not args.type:
        print("Available TOTP types:")
        if config:
            for type_name in config.keys():
                print(f"- {type_name}")
        else:
            print("No TOTP types configured. Please check your configuration file.")
        return

    # 获取密钥
    key = get_totp_key(args.type, config)
    if not key:
        print(f"Error: No TOTP key found for type '{args.type}'")
        print("\nAvailable types:")
        for type_name in config.keys():
            print(f"- {type_name}")
        sys.exit(1)

    # 生成TOTP码
    code = generate_totp(key)
    if not code:
        sys.exit(1)

    # 输出结果
    print(code)
    
    # 复制到剪贴板
    pyperclip.copy(code)

if __name__ == '__main__':
    main()
