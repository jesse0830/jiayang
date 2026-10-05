# 飞书配对审批流程

当 Hermes 飞书 bot 配置了 `FEISHU_DM_POLICY=pairing`（即需要授权才能聊天）时，
用户首次给 bot 发消息会收到一个配对码，需要在 CLI 端 approve。

## 流程

```
用户 → 给飞书 bot 发任意消息 → bot 回复配对码（如 "98A34Q68"）
用户 → 把配对码发给当前会话 → 在当前会话中执行 pairing approve
```

## 命令

```bash
hermes pairing approve feishu <配对码>
```

示例：
```bash
hermes pairing approve feishu 98A34Q68
```

成功输出：
```
Approved! User ou_xxx on feishu can now use the bot~
  They'll be recognized automatically on their next message.
```

配对成功后，用户给飞书 bot 再发一次消息即可正常对话。

## 配对前的准备

- `.env` 中已配置 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET`
- Gateway 正在运行（`hermes gateway status` 确认）
- 飞书应用已发布并启用机器人功能
- `FEISHU_DM_POLICY=pairing`（或更宽松的 `open`）

## 验证

配对完成后，用户再在飞书给 bot 发消息，应能正常回复。
