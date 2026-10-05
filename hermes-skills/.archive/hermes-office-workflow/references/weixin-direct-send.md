# 微信（iLink）直发消息：会话内调用路径 + 已知错误

场景：用户在 Hermes 桌面端直接说"给我微信发一条消息"，但 `send_message` 工具未加载
（tool_search 找不到）。此时可直接调用底层函数，无需依赖 gateway 长连接。

## 直发脚本（已验证可到达 iLink API）

```bash
cd ~/.hermes/hermes-agent && cat > /tmp/send_wx.py <<'EOF'
import asyncio, os, sys
sys.path.insert(0, os.path.expanduser("~/.hermes/hermes-agent"))

# 加载 ~/.hermes/.env（WEIXIN_TOKEN / WEIXIN_ACCOUNT_ID / WEIXIN_HOME_CHANNEL 等）
from pathlib import Path
env_path = Path(os.path.expanduser("~/.hermes/.env"))
for line in env_path.read_text().splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k, v)

from gateway.platforms.weixin import send_weixin_direct

async def main():
    chat_id = os.environ["WEIXIN_HOME_CHANNEL"]
    result = await send_weixin_direct(
        extra={}, token=os.environ.get("WEIXIN_TOKEN"),
        chat_id=chat_id, message="测试消息",
    )
    print(result)

asyncio.run(main())
EOF
~/.hermes/hermes-agent/venv/bin/python /tmp/send_wx.py
```

说明：
- `send_weixin_direct` 在 `~/.hermes/hermes-agent/gateway/platforms/weixin.py`（约 2071 行），签名：
  `extra, token, chat_id, message, media_files`。它绕过 long-poll 适配器，直接用原始 API。
- venv python 路径：`~/.hermes/hermes-agent/venv/bin/python`（若无则回退 python3）。
- chat_id 取 `WEIXIN_HOME_CHANNEL`（格式如 `o9cq80xL...@im.wechat`）。

## 已知错误签名（直接认，别浪费轮次）

**iLink rate limited（最常见，反复出现）**
```
[Weixin] rate limited for <id>; backing off 3.0s before retry
[Weixin] send failed to=<id>: iLink sendmessage rate limited: ret=-2 errcode=None errmsg=prepare failed
```
含义：不是 Hermes 配置问题，是 **iLink 服务端限流**（bot 账号被微信侧限制）。自动重试 4 次
仍失败。这也是每周四报销推送、晚 10:30 提醒收不到的同源原因。处理：等 10-30 分钟再试，
或检查 iLink bot 账号是否需重新授权；电脑微信收不到还有设备同步策略限制（见 memory）。

**gateway 适配器连接报错（版本不匹配）**
```
WeixinAdapter.connect() got an unexpected keyword argument 'is_reconnect'
```
来源：`gateway/run.py` 调用 `adapter.connect(is_reconnect=...)`，但
`gateway/platforms/weixin.py` 的 `connect(self)` 没接这个参数 → gateway_state.json 里
weixin 平台一直 `retrying`。这是本地 hermes-agent 代码版本与适配器签名不一致的小 bug；
不影响 send_weixin_direct 直发路径（直发不经过 connect）。修法：给 weixin.py 的
`connect` 加 `*, is_reconnect: bool = False` 参数，或等 hermes update 覆盖。

## 快速排查顺序

1. `cat ~/.hermes/gateway_state.json` → 看 platforms.weixin.state（connected / retrying / error）。
2. 确认 .env 里 WEIXIN_TOKEN / WEIXIN_ACCOUNT_ID / WEIXIN_HOME_CHANNEL 都在。
3. 用上面脚本直发一次，看错误签名再判断：rate limited = 服务端限流（等重试）；
   token missing / account missing = 配置问题。
