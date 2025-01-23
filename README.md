# TOTP Generator

一个简单的 TOTP (基于时间的一次性密码) 生成器。

## 设置

1. 创建配置文件：
   ```bash
   mkdir .keys
   cp totp_config.example.json .keys/totp_config.json
   ```

2. 编辑配置文件 `.keys/totp_config.json`，添加你的 TOTP 密钥。
   每个密钥必须是有效的 Base32 编码字符串。

   示例格式：
   ```json
   {
       "ServiceName": "YOUR_BASE32_ENCODED_SECRET"
   }
   ```

3. 运行程序：
   ```bash
   python totp_gui.py
   ```

## 获取 TOTP 密钥

当你在服务中启用两步验证时，通常会得到：
1. 二维码
2. 备用密钥（通常是 Base32 格式）

使用备用密钥（看起来像：JBSWY3DPEHPK3PXP）。

## 注意事项

- 密钥必须是有效的 Base32 编码
- 保护好你的 totp_config.json 文件
- 不要将密钥提交到版本控制系统 