# 打包说明

## 开发环境打包

1. 安装打包依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 运行打包命令：
   ```bash
   python setup.py build
   ```

3. 打包后的文件在 `build/exe.win-amd64-3.10/` 目录下

## 使用说明

1. 复制配置文件示例：
   ```
   build/exe.win-amd64-3.10/config/totp_config.example.json
   ```
   重命名为：
   ```
   build/exe.win-amd64-3.10/config/totp_config.json
   ```

2. 编辑 `totp_config.json` 添加你的 TOTP 密钥

3. 运行 `TOTP Generator.exe` 