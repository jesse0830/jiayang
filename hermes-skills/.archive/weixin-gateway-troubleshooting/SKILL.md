---
name: weixin-gateway-troubleshooting
description: "Use when 微信/iLink 发不出消息：ret=-2 语义、清 token 实验、备选通道。"
version: 1.0.0
platforms: [macos]
metadata:
  hermes:
    tags: [weixin, ilink, gateway, troubleshooting, rate-limit]
    related_skills: [hermes-maintenance, feishu-app-config]
---

# 微信 iLink 通道排障（weixin-gateway-troubleshooting）

Hermes gateway 微信通道（iLink/ilinkai.weixin.qq.com）连不上或发不出消息时的系统化排查。用户每周四晚有报销推送 cron 走微信，通道故障有实际业务影响。

## When to use
- 用户问"微信还能发吗 / 手机收不到消息"
- gateway_state.json 里 weixin 状态不是 connected，或 connected 但发送失败
- 日志出现 `iLink sendmessage rate limited`、`ret=-2`、`prepare failed`、`WeixinAdapter.connect() got an unexpected keyword argument`
- 定时推送（如周四报销提醒）收不到

## 诊断顺序（先状态、再代码、再实验）

### Step 1 — 看通道状态
```bash
cat ~/.hermes/gateway_state.json   # 看 platforms.weixin.state
```
- `connected` = 连接层 OK，问题在发送层
- `retrying` = 连接层问题，查 connect 报错

### Step 2 — 实测发送（用已有测试脚本）
```bash
cd ~/.hermes/hermes-agent && ./venv/bin/python /tmp/send_wx.py
```
发送失败时抓关键字段：`ret`、`errcode`、`errmsg`。

### Step 3 — ret=-2 双语义区分（关键！）
iLink 返回 `ret=-2` 有两种完全不同的含义，`errmsg` 区分：

| errmsg | 含义 | 处理 |
|---|---|---|
| `unknown error` | **stale session**（会话过期，等价 errcode=-14） | 代码自动清 context_token 重试一次（`_is_stale_session_ret` 逻辑） |
| `prepare failed` | **服务端真限流**（账号级风控） | 退避重试无效，本地无解 |

weixin.py 里 `_is_stale_session_ret(ret, errcode, errmsg)` 只把 errmsg 恰为 "unknown error" 的 -2 当 stale session；`prepare failed` 不在识别范围，会走限流退避分支（3s × 重试次数）。

### Step 4 — 清 token 实验法（区分本地 vs 服务端）
```
备份 → 清空 context-tokens.json → 重发 → 恢复
```
token 文件：`~/.hermes/weixin/accounts/<account>@im.bot.context-tokens.json`
```bash
cp <token文件> <token文件>.bak && echo '{}' > <token文件>
# 重发测试；仍报 -2 prepare failed = 服务端限流，与本地 token 无关
cp <token文件>.bak <token文件>   # 记得恢复！
```
2026-08-05 实例：清空 token 后仍 `ret=-2 prepare failed` → 定性服务端账号级限流，排除本地因素。

### Step 5 — 定性结论
- **短时冷却**（分钟级）：等 10-30 分钟再试
- **账号级限流**（持续数小时+）：iLink 对 bot 账号的风控冷却按**天**算，本地配置/代码/重启都无效
- 建议用户到 iLink/微信 bot 管理后台查账号（`o9cq80xL...` 形式）是否被风控/封禁

### Step 6 — 备选通道（业务不中断）
feishu / wecom 通常同时 connected（gateway_state.json 验证），定时推送可临时切到飞书或企业微信，不要干等微信冷却。

## 已知 bug 与修复（2026-08-05）
- **is_reconnect 缺失**：`weixin.py` 的 `connect(self)` 签名缺 `*, is_reconnect: bool = False`（其他平台适配器都有），gateway 重连时必传该参数 → `TypeError: connect() got an unexpected keyword argument 'is_reconnect'`，导致通道一直 retrying。修复：加参数。**注意：hermes update 可能重置此文件**，维护见 hermes-maintenance 技能的 autostash 恢复。
- **gateway 启动必须用 venv python**：`cd ~/.hermes/hermes-agent && ./venv/bin/python hermes_cli/main.py gateway run --replace`（后台）。系统 python3 太老（不支持 `str | None` 语法）直接崩（`TypeError: unsupported operand type(s) for |`）。
- 后台进程被 SIGTERM/SIGKILL 属正常（--replace 换新进程），用 gateway_state.json 验证而不是看旧进程退出码。

## Pitfalls
- 别把 `prepare failed` 当短时限流空等——它持续数小时就是账号级风控，本地处理不了。
- 清 token 实验**必须备份并恢复**，否则 context_token 丢失会让正常会话也失效。
- 不要用系统 python3 跑 gateway（版本过老）。
- 发送前先确认通道状态，限流期间不盲目高频重试（会加重风控）。

## Verification
- gateway_state.json：weixin/feishu/wecom 均 connected
- 实际发送成功（exit 0，无 rate limited 报错）
- 微信手机端收到消息
