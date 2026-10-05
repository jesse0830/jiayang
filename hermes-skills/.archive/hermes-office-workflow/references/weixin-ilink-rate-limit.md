# 微信 iLink 限流 vs 会话过期：判别与处理（2026-08-05 实战）

## 场景

Hermes 微信通道（iLink）发送消息报：
```
[Weixin] rate limited for o9cq80xL; backing off 3.0s before retry
[Weixin] send failed to=o9cq80xL: iLink sendmessage rate limited: ret=-2 errcode=None errmsg=prepare failed
```
持续数小时，退避重试全部失败。

## 核心判别：errmsg 决定含义

`ret=-2` 有两种完全不同的含义，**看 errmsg 区分**：

| errmsg | 含义 | 处理 |
|--------|------|------|
| `unknown error` | **会话过期**信号（与 errcode=-14 同义），`_is_stale_session_ret()` 会识别 | 清 context_token 重试（代码在 `gateway/platforms/weixin.py` 中自动处理：`SESSION_EXPIRED_ERRCODE = -14`，`_is_stale_session_ret` 判定 `ret=-2 && errmsg=="unknown error"`） |
| `prepare failed` | **iLink 服务端账号级限流**，本地无法解除 | 等冷却（按天），不要高频重试；检查 iLink/微信 bot 后台该账号是否被风控 |

## 判别实验：token 问题 vs 服务端限流

1. **备份** context token 文件：
   ```
   cp ~/.hermes/weixin/accounts/<account>@im.bot.context-tokens.json{,.bak}
   ```
2. **清空**（写成 `{}`）
3. **重发**：
   - 仍报 `-2 prepare failed` → **服务端限流实锤** → **恢复备份**
     ```
     cp ...context-tokens.json.bak ...context-tokens.json
     ```
   - 发送成功 → 是本地 token 失效，保持清空即可

## 关键要点

- **`connected` ≠ 能发送**：gateway_state.json 显示 weixin connected 不代表 sendmessage 不被限流。发送前必须实测。
- **账号级限流冷却是按天的**：实测 2026-08-05 下午开始限流，次日恢复。
- **周期性推送会静默失败**：每周报销/学习提醒等 cron 在限流期间发不出去，需提前确认通道或临时切飞书/企微。
- 检查状态：`cat ~/.hermes/gateway_state.json`（platforms.weixin.state）。
- 实测发送脚本：`cd ~/.hermes/hermes-agent && ./venv/bin/python /tmp/send_wx.py`（或走 `send_weixin_direct`）。

## 定时提醒发微信（cron deliver 模式）

把 cron 消息直接投递到用户手机微信：
```
cronjob action=create schedule="2026-08-06T14:45:00" name="xx提醒" \
  deliver="weixin:<chat_id>" prompt="发送微信提醒：...内容简洁中文，失败重试一次"
```
- `deliver` 用 `weixin:<chat_id>`，chat_id 形如 `o9cq80xLiMZ0ptdSedyf2MjscrTk@im.wechat`（从 gateway_state.json 或发送成功返回 `chat_id` 字段拿）
- 一次性提醒用 ISO 时间戳 + 默认 once
- `enabled_toolsets` 可精简为 `["web"]`（纯发消息不需要其他工具）
- 创建后返回 `job_id`，可用 `cronjob action=list` 核对 `next_run_at`
