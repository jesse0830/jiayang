# 微信 (Weixin) 配置细节

来自 Hermes 文档和实际配置经验。

## 完整配置变量

以下变量在 `~/.hermes/.env` 中设置：

```env
# 账号 ID（来自 gateway setup 扫码登录）
WEIXIN_ACCOUNT_ID=your_account_id@im.bot

# 令牌（自动生成）
WEIXIN_TOKEN=your_account_id@im.bot:hex_token

# API 基础 URL
WEIXIN_BASE_URL=https://ilinkai.weixin.qq.com

# CDN 基础 URL
WEIXIN_CDN_BASE_URL=https://novac2c.cdn.weixin.qq.com/c2c

# DM 策略：open | pairing | closed
WEIXIN_DM_POLICY=open

# 是否允许所有用户
WEIXIN_ALLOW_ALL_USERS=false

# 白名单用户列表（逗号分隔）
WEIXIN_ALLOWED_USERS=

# 群聊策略：disabled | open
WEIXIN_GROUP_POLICY=disabled

# 群聊白名单
WEIXIN_GROUP_ALLOWED_USERS=

# 默认聊天频道
WEIXIN_HOME_CHANNEL=user_id@im.wechat
```

## 关键操作

### 修改后必须重启 Gateway

```bash
# 只改 .env 不行，必须重启
hermes gateway restart
```

验证是否重新连接成功：
```bash
grep -i "weixin" ~/.hermes/logs/gateway.log | tail -5
```
预期看到：`✓ weixin connected`

### DM 策略说明

| 值 | 行为 |
|----|------|
| `open` | 所有人可以私聊，自动回复 |
| `pairing` | 需要先在 Hermes 侧授权（`hermes pairing approve <user>`），未授权用户的消息会被记录为 `Unauthorized user` |
| `closed` | 不接受私聊 |

### 排查

Gateway 日志位置：`~/.hermes/logs/gateway.log`

常见日志消息：
- `[Weixin] Connected account=xxx` — 连接成功
- `[Weixin] inbound from=xxx type=dm` — 收到消息
- `Unauthorized user: xxx` — DM 策略拒绝
- `[Weixin] poll error (1/3): Server disconnected` — 网络断开，会自动重试

## 常见问题 FAQ

### iLink session 过期（errcode=-14 session timeout），QR 扫码无法修复怎么办？

这是当前已知的棘手问题。症状：

- `sendmessage` / `getupdates` / `getconfig` 全部返回 `errcode=-14 errmsg=session timeout`
- gateway 日志显示 `✓ weixin connected`，但发送仍然失败
- 即使通过 `get_bot_qrcode` 生成新二维码并扫码确认（status=confirmed），新 bot token 仍然 session timeout
- 每次扫码生成的是**全新的 bot 账号**（新 `ilink_bot_id`），这个新 bot 和用户的微信之间的消息通道可能没有完全建立

**排查和修复步骤（按顺序尝试）：**

1. **确认 gateway 状态正常：** `grep weixin ~/.hermes/logs/gateway.log | tail -5` — 应有 `✓ weixin connected`
2. **检查手机微信是否能收到** — 手机微信收不到才是真问题，Mac 收不到但手机能收到是设备同步限制
3. **在手机上给 bot 发一条消息** — 从手机微信给机器人发消息，建立双向通道后再试
4. **检查 iLink 服务是否正常：** 直接调用 API 测试：
   ```python
   url = "https://ilinkai.weixin.qq.com/ilink/bot/get_bot_qrcode?bot_type=3"
   # 成功返回 {ret:0, qrcode:"xxx"} 说明服务正常
   ```
5. **重置所有微信配置重新开始：**
   ```bash
   rm -rf ~/.hermes/weixin/
   # 清空 .env 中的 WEIXIN_TOKEN 和 WEIXIN_ACCOUNT_ID
   kill $(pgrep -f "hermes_cli.main") && hermes gateway run --replace
   # 生成全新二维码，用户扫码
   ```

**如果以上都不行：** 可能是 iLink 服务端的问题，或该 iLink 账号已被微信限制。考虑切换至 **企业微信（WeCom Callback 模式）** 作为微信的替代方案。

### 为什么已在微信上发过消息给机器人，但仍然显示 Unauthorized User？

检查 `.env` 中的两个变量：

```env
# 如果 ALLOW_ALL_USERS=false 且 ALLOWED_USERS 为空，你的所有消息都会被拒绝
WEIXIN_ALLOW_ALL_USERS=false
WEIXIN_ALLOWED_USERS=
```

**修复方法（任选其一）：**
```env
# 方案 A：允许所有用户
WEIXIN_ALLOW_ALL_USERS=true

# 方案 B：添加你的用户到白名单（用 gateway 日志中的 user_id）
WEIXIN_ALLOWED_USERS=o9cq80xLiMZ0ptdSedyf2MjscrTk@im.wechat
```

修改后必须重启 Gateway：`hermes gateway restart`

**注意：** 即使 outbound (Hermes 发送到你的微信) 在 `Unauthorized` 状态下也能成功发送！`Unauthorized` 只阻止 inbound（你发消息给 Hermes）。所以如果用户说能收到推送但不能在微信上回复 Hermes，务必检查这个配置。

### 为什么手机微信能收到消息，但电脑微信收不到？

这是 **微信客户端间的消息同步机制** 的问题，不是 Hermes 或 iLink Bot 能控制的。

iLink Bot 通过腾讯云 API 将消息投递到微信服务器（云端），微信服务器再决定推送到哪些设备。手机和电脑之间的消息同步由微信客户端自行管理：

**可能原因：**
1. **电脑微信未保持在线** — 需要扫码登录并持续在线，离线期间可能不会同步推送
2. **Bot 消息的同步优先级较低** — 微信可能对 Bot 账号的异步消息不触发多端同步
3. **网络环境差异** — 手机和电脑的网络可能不同，消息同步有延迟

**排查步骤：**
1. 确认电脑微信左上角显示绿色"已连接"状态
2. 在电脑微信上**手动切换到其他聊天再切回来**，看消息是否出现
3. 重启电脑微信
4. 手机上把消息转发到"文件传输助手"，看电脑微信能否收到——如果可以，说明是 Bot 消息的同步问题

**如果电脑端收发是刚需：** 考虑改用 **企业微信（WeCom）**，它的消息同步机制更可靠，多端同步体验更好。

### 为什么 send_message(list) 显示没有目标，但消息能发出去？

微信平台不走 channel_directory 注册，CLI 的 `send_message` 工具和 Gateway 是独立的运行时。`list` 不显示 weixin 目标不代表消息发不出去。

**正确做法：** 直接用 `send_message(target='weixin', message='...')` 即可，无需先 list。

### iLink Bot 连接不稳定（Server disconnected）

日志中出现 `[Weixin] poll error (1/3): Server disconnected` 是正常的——iLink 长轮询会因网络波动断开，Gateway 会自动重试（最多 3 次，间隔 2s + 30s backoff）。只要最终显示 `✓ weixin connected` 即表示恢复。

如果频繁断开，检查网络稳定性。

## 与微信个人号的差异

- 连接的是 iLink 机器人身份（`xxx@im.bot`），不是个人微信号本体
- 好友看到的是机器人账号，不是你的微信
- 对方给机器人发消息，机器人才回复（被动模式）
- 群聊通常不工作（iLink 侧限制）
