# WeCom Callback（企业微信自建应用）完整配置指南

从零配置 Hermes 与企业微信的双向聊天连接。

## 概述

WeCom 支持两种连接模式：

| 模式 | 配置变量 | 方向 | 场景 |
|------|---------|------|------|
| Bot 模式 | `WECOM_BOT_ID`, `WECOM_SECRET` | 仅发送 | cron 推送通知 |
| Callback 自建应用 | `WECOM_CALLBACK_*` | 双向收发 | 日常聊天交互 |

本文档只针对 **Callback 自建应用模式**。

## 前置条件

- 企业微信管理员权限（能访问管理后台）
- Hermes 网关机器**必须有公网可达的 HTTPS 地址**（本地 Mac 需要内网穿透）

## 完整配置变量

以下全部写入 `~/.hermes/.env`：

```env
# 企业微信 Corp ID（管理后台 → 我的企业 → 企业信息底部）
WECOM_CALLBACK_CORP_ID=wwxxxxxxxxxxxxx

# 自建应用的 Secret（应用详情页）
WECOM_CALLBACK_CORP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx

# 自建应用的 AgentId
WECOM_CALLBACK_AGENT_ID=1000002

# 回调 Token（配置接收消息时自己设的）
WECOM_CALLBACK_TOKEN=your_custom_token

# 回调 EncodingAESKey（配置接收消息时生成的）
WECOM_CALLBACK_ENCODING_AES_KEY=xxxxxxxxxxxxxxxxxxxxx

# HTTP 回调服务器端口（默认 8645）
WECOM_CALLBACK_PORT=8645

# 白名单（可选，逗号分隔用户 ID，留空则允许所有人）
# WECOM_CALLBACK_ALLOWED_USERS=
```

> **注意：** 配置后必须重启 Gateway：`hermes gateway restart`

## 操作步骤

### 第1步：创建企业微信自建应用

1. 登录 [企业微信管理后台](https://work.weixin.qq.com/wework_admin/frame#apps)
2. 应用管理 → 自建 → 创建应用
3. 填写：
   - 应用 Logo（可以随便上传一张）
   - 应用名称（如"智能助手"）
   - 可见范围（选择自己或相关部门）
4. 创建成功后进入应用详情页，记录：
   - **AgentId**（页面顶部）
   - **Secret**（点"查看"复制）→ 对应 `WECOM_CALLBACK_CORP_SECRET`
5. 获取 **Corp ID**：我的企业 → 企业信息 → 底部"企业ID" → 对应 `WECOM_CALLBACK_CORP_ID`

### 第2步：解决回调 URL 公网访问

Hermes 网关默认监听 `localhost:8645` 接收回调。企业微信需要一个公网 HTTPS 地址来访问它。

#### 方案 A：ngrok（推荐，免费）

```bash
# 安装 ngrok
brew install ngrok                 # macOS 方式一
# 或直接下载
curl -sL https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-darwin-amd64.zip -o /tmp/ngrok.zip
unzip -o /tmp/ngrok.zip -d /usr/local/bin/
chmod +x /usr/local/bin/ngrok

# 配置 Authtoken（需要先注册 https://dashboard.ngrok.com 免费账号）
ngrok config add-authtoken YOUR_AUTHTOKEN

# 启动隧道（终端 1）
ngrok http 8645

# 输出示例：
# Forwarding https://xxxx-xxx.ngrok-free.app → http://localhost:8645
# 复制这个 HTTPS URL
```

#### 方案 B：Cloudflare Tunnel（备用）

```bash
brew install cloudflared
cloudflared tunnel --url http://localhost:8645
```

### 第3步：配置企业微信回调

1. 在自建应用详情页 → **接收消息** → **设置接收消息**
2. 填写：
   - **URL:** `https://你的ngrok地址.ngrok-free.app/webhooks/wecom`
     - 注意路径是 `/webhooks/wecom`（固定）
   - **Token:** 自己设一个，如 `hermes123` → 对应 `WECOM_CALLBACK_TOKEN`
   - **EncodingAESKey:** 点"随机获取"按钮 → 对应 `WECOM_CALLBACK_ENCODING_AES_KEY`
3. 点击保存
   - 如果提示"URL 验证失败"，说明 ngrok 还未启动或 Hermes 网关未运行

### 第4步：配置 Hermes

交互式向导：
```bash
hermes gateway setup
# 选择 "WeCom Callback (Self-Built App)" → 输入 Corp ID, Secret, AgentId, Token, AES Key, Port
```

或直接编辑 `~/.hermes/.env` 手动写入上述变量。

### 第5步：重启网关

```bash
hermes gateway restart
```

验证连接：
```bash
grep "wecom" ~/.hermes/logs/gateway.log | tail -5
```
预期看到 `✓ wecom_callback connected` 类似输出。

### 第6步：测试

在企业微信中打开自建应用，发送一条消息给机器人。确认 gateway 日志能收到：
```bash
grep "wecom" ~/.hermes/logs/gateway.log | tail -10
```

## 故障排查

### 回调 URL 验证失败

**表现：** 企业微信后台点保存时提示"URL 验证失败"

**排查：**
1. 确认 ngrok/隧道正在运行：`curl https://你的地址.ngrok-free.app/webhooks/wecom` 返回非空
2. 确认 Hermes 网关已启动：`hermes gateway status`
3. 确认端口匹配：ngrok 的端口和 `WECOM_CALLBACK_PORT` 一致
4. 路径必须是 `/webhooks/wecom`（固定值）

### 消息发送成功但收不到

**表现：** 能从 Hermes 发消息到企业微信，但用户在企业微信中发消息给机器人，Hermes 不回应

**排查：**
1. 检查 gateway 日志是否收到消息：`grep wecom ~/.hermes/logs/gateway.log | tail -10`
   - 如果没有任何日志 → 回调 URL 配置有问题，企业微信的通知没有到达 Hermes
   - 如果有 `inbound from=xxx` → Hermes 收到了但可能处理异常
2. 检查 `WECOM_CALLBACK_ALLOWED_USERS` 是否设置了白名单且未包含当前用户
3. 检查 gateway 是否有报错：`grep -i error ~/.hermes/logs/gateway.log | grep wecom`

## ngrok 管理提示

- **免费版限制：** ngrok 免费的域名每次重启会变，每次都需要更新企业微信回调 URL
- **推荐做法：** 用 `--domain` 参数固定域名（需要付费版）或每次重启后更新回调 URL
- **长期方案：** 如果稳定使用，建议用云服务器或 Cloudflare Tunnel（可固定域名）

## 参考文件

主技能 `hermes-office-workflow` 中还有：
- `references/weixin-config-details.md` — 微信 iLink Bot 配置
- `references/wecom-message-history.md` — 企业微信消息历史限制
