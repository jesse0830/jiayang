# Hermes 新增模型 Provider（如千问/DashScope）配置指南

场景：用户说"这是千问的 API，帮我配置下 / 添加下，让我能随意切换"。目标 = 把新模型加入 Hermes 并能在 deepseek 等现有模型之间切换。

## 核心流程

```bash
cd ~/.hermes/hermes-agent

# 1. 先验证 key 有效（用对端点！中国大陆 key 用国内站）
curl -s -m 20 https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions \
  -H "Authorization: Bearer <KEY>" \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen-plus","messages":[{"role":"user","content":"ping"}],"max_tokens":5}'

# 2. 用官方 auth 命令添加（不要手改 .env —— 会被审批拦截且不合规范）
./venv/bin/hermes auth add alibaba --type api-key --api-key "<KEY>" --label qwen-dashscope

# 3. 覆盖 base_url 到国内站（config.yaml 层）
./venv/bin/hermes config set providers.alibaba.base_url "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 4. 添加模型别名（桌面端模型选择器可用）
./venv/bin/hermes config set model.aliases.qwen "alibaba/qwen-plus"

# 5. 端到端验证（-Q 安静模式只看结果）
./venv/bin/hermes chat -Q -q "用一句话回复：测试成功" --provider alibaba -m qwen-plus
```

## ⚠️ 最大的坑：auth add 会把国际站 base_url 固化进凭证

- `hermes auth add alibaba` 会把 provider 插件默认的 **国际站** URL 写进 `~/.hermes/auth.json` 的凭证记录里（`base_url: https://dashscope-intl.aliyuncs.com/compatible-mode/v1`）。
- **凭证里的 base_url 优先于 config.yaml 的 `providers.alibaba.base_url`**。所以第 3 步只改 config 无效，请求还是发往国际站 → HTTP 401 "Incorrect API key provided"（虽然 curl 直连国内站明明成功）。
- 修复：直接改 `~/.hermes/auth.json` 里该凭证的 `base_url` 字段为国内站，并清掉 last_status/last_error 等字段（避免缓存旧失败状态）：
```python
import json
d = json.load(open('/Users/jesseyoung/.hermes/auth.json'))
for it in d['credential_pool']['alibaba']:
    it['base_url'] = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
    for k in ('last_status','last_status_at','last_error_code','last_error_reason','last_error_message','last_error_reset_at'):
        it[k] = None
    it['request_count'] = 0
json.dump(d, open('/Users/jesseyoung/.hermes/auth.json','w'), ensure_ascii=False, indent=2)
```

## CLI 切换模型的正确姿势

- **别名在 CLI 不生效**：`hermes chat --model qwen` 会被静默归一化回默认模型（日志见 `Normalized model 'qwen' to 'deepseek-v4-flash'`），看起来"成功"其实是跑的 deepseek！
- `--model alibaba/qwen-plus` 也不行 —— provider 不会自动切换，会报 `Provider: deepseek Model: alibaba/qwen-plus` 400。
- **必须同时指定 provider**：`hermes chat -Q -q "..." --provider alibaba -m qwen-plus`。
- 桌面端/设置里的模型选择器可以用别名 `qwen`；CLI 要用完整 `--provider X -m Y`。
- 切换模型不会影响默认模型（默认仍是 deepseek），要换默认才动 model.default。

## 其他要点

- `timeout` 命令在 macOS 不存在，别用 `timeout 90 hermes ...`，直接跑（工具自带 timeout 参数）。
- API key 一律脱敏：不写进记忆、不复述值；配置落地时用 auth add 传入或让用户重新提供。
- 验证 key 时"curl 直连成功但 Hermes 401" = 端点不对（intl vs 国内），不是 key 的问题。
