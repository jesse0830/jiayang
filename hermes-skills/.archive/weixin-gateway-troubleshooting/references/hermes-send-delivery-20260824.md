# 多平台发送实测（2026-08-24）：hermes send CLI

微信个人通道限流（ret=-2 prepare failed）时，用 `hermes send` 走备选通道的实际案例。

## 命令

```bash
cd ~/.hermes/hermes-agent && ./venv/bin/python hermes_cli/main.py send --list
./venv/bin/python hermes_cli/main.py send --to "weixin:o9cq80xLiMZ0ptdSedyf2MjscrTk@im.wechat" "文本"
./venv/bin/python hermes_cli/main.py send --to "wecom:wo9tQCDgAApkbYg5HjV94etVjyd75yEg" "文本"
./venv/bin/python hermes_cli/main.py send --to "wecom:wo9tQCDgAApkbYg5HjV94etVjyd75yEg" "MEDIA:/abs/path/file.xlsx"
```

- 退出码：0=成功 1=后端错误 2=用法错误
- `--list` 列出全部平台目标（裸平台名=发 home channel）

## 平台差异（实测）

| 平台 | 状态 | 说明 |
|---|---|---|
| weixin | 限流 ret=-2 prepare failed | 账号级风控，本地无解，别重试 |
| wecom | ✅ 纯文本成功 | **不支持 MEDIA 附件**：报 "had only media attachments" |
| feishu | ❌ 99991672 Access denied | 应用缺 `im:message:send` scope，错误里附开通链接 |

MEDIA 附件仅支持：telegram/discord/matrix/weixin/signal/yuanbao/feishu/whatsapp/slack。

## 结论
- weixin 限流 → wecom 发文字摘要可行；附件 wecom 发不了 → 落盘桌面并告知用户路径。
- feishu 缺权限：提示用户去 open.feishu.cn/app/<appid>/auth 开通 im:message:send。
- 用户要求"发到微信"但个人微信限流时，企微（wecom）是最近的可达通道，先发企微并说明情况。
