---
name: hermes-llm-provider-config
description: "Use when user gives an LLM API key to configure in Hermes."
version: 1.0.0
created_by: agent
metadata:
  tags: [hermes, provider, api-key, qwen, dashscope, config]
  languages: [zh-CN, en]
---

# Hermes LLM Provider / API Key 配置

用户给出一个 LLM 的 API key（如"这个是千问的api，帮我配置下"）时的标准流程。
凭据一律入 `~/.hermes/.env`，**永不**写入 config.yaml、memory、摘要或对话复述。

## 触发条件

- 用户粘贴 API key 并要求"配置下"
- 用户问某个 provider 怎么接入 Hermes（千问 / DeepSeek / GLM / Kimi 等）
- 需要添加可切换的模型（不改默认模型，除非用户明确要求）

## 标准流程

1. **确认 provider 插件存在**：`ls ~/.hermes/hermes-agent/plugins/model-providers/`
   - 千问/通义 = `alibaba`（env var `DASHSCOPE_API_KEY`）
   - DeepSeek = `deepseek`（`DEEPSEEK_API_KEY`）
   - 每个插件的 `.py` 里有 env var 名、默认 base_url、aliases — 先读它
2. **先用 curl 验证 key 有效性**（最小请求，别直接配完再测）：
   ```bash
   curl -s -m 30 https://<base_url>/chat/completions \
     -H "Authorization: Bearer <KEY>" -H "Content-Type: application/json" \
     -d '{"model":"qwen-plus","messages":[{"role":"user","content":"ping"}],"max_tokens":10}'
   ```
   返回 `choices[].message.content` = key 有效。**同时确认 key 属于哪个站点**：测国内 `dashscope.aliyuncs.com` 和/或国际 `dashscope-intl.aliyuncs.com`，哪个 200 就用哪个（key 与站点绑定，国际站 key 打国内站会 401）。
3. **key 入凭证池（首选官方命令）**：
   ```bash
   hermes auth add <provider> --type api-key --api-key <KEY> --label <label>
   # 例：hermes auth add alibaba --type api-key --api-key sk-xxx --label qwen-dashscope
   ```
   存到 `~/.hermes/auth.json` 的 `credential_pool`。⚠ 见 Pitfall：auth add 会把**插件默认 base_url 固化进凭证**且凭证优先于 config.yaml。
   .env 备选（老方法）：`printf '\nDASHSCOPE_API_KEY=<KEY>\n' >> ~/.hermes/.env` — 会触发终端审批，先说明方案拿确认。
4. **base_url 与 key 区域匹配**（本用户踩过的坑，见 Pitfalls）：
   - `hermes config set providers.<name>.base_url <url>` 覆盖 config 层；
   - **若用了 auth add**，还必须改 auth.json 里该凭证的 base_url（凭证优先于 config！）：
     ```bash
     python3 -c "
     import json
     p = '$HOME/.hermes/auth.json'
     d = json.load(open(p))
     for c in d['credential_pool']['alibaba']:
         c['base_url'] = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
         for k in ['last_status','last_status_at','last_error_code','last_error_reason','last_error_message','last_error_reset_at']:
             c[k] = None
         c['request_count'] = 0
     json.dump(d, open(p,'w'), ensure_ascii=False, indent=2)
     "
     ```
5. **加模型别名**方便切换：`hermes config set model.aliases.<name> <provider>/<model>`
   例：`hermes config set model.aliases.qwen alibaba/qwen-plus`
6. **端到端验证**：`hermes chat -Q -q "回复ok" --provider <provider> -m <model>`
   ⚠ CLI 的 `--model <alias>` **别名不解析**（会把别名当模型名扔给当前默认 provider，报 400）— 必须 `--provider <provider> -m <model>` 完整格式。
7. **默认模型不动**：只增加"可用"，不替换当前默认（用户当前默认 deepseek-v4-flash）。切换默认见下节。

## Pitfalls

- **alibaba 插件默认走国际站** `dashscope-intl.aliyuncs.com/compatible-mode/v1`；
  **国内百炼 key 必须用国内站** `https://dashscope.aliyuncs.com/compatible-mode/v1`。
  `sk-ws-` 前缀 = 国内百炼新版工作空间 key。配完 base_url 必须再 curl 验证一次。
- **`hermes auth add` 会固化插件默认 base_url 进 auth.json 凭证**（`dashscope-intl`），
  且**凭证里的 base_url 优先于 config.yaml** — 只改 config 不改 auth.json 照样 401
  （错误特征：`HTTP 401: Incorrect API key provided`，但 curl 直连 key 有效）。
  修法：改 auth.json 里该凭证的 base_url（见标准流程第 4 步脚本）。
- **CLI 别名不解析**：`hermes chat --model qwen` 会把 `qwen` 当模型名丢给当前默认
  provider（报 `HTTP 400: The supported API model names are ...`），或静默 normalized
  成默认模型。必须 `--provider alibaba -m qwen-plus`。
- **切换默认模型后当前会话不变**：会话在启动时固定模型；改 config 只影响新会话。
- **桌面 app 有会话级模型记忆**：开新窗口、重启 app、重启 gateway 都**不会**改变
  已开会话的模型（用户实测：新窗口 + 重启 app 后仍显示旧模型）。唯一生效方式：
  在 app 模型选择器/下拉里**手动切换**（立即生效，runtime metadata 同步更新）；
  或开一个明确指定模型的新会话。CLI/gateway 侧才靠 config.yaml 默认值。
- **重启 gateway**：`hermes gateway restart`（排空 in-flight runs 最长 180s，
  launchd 自动拉起新 PID，微信/飞书/企微重连）。仅影响之后的会话，当前会话模型不变。
- 不要用 `hermes model` 交互选择器代替手动配置 — 它是交互式 TUI（方向键+回车），
  运行中会一直挂着等输入，且改的是默认模型。
- 不要 hand-edit config.yaml — 一律 `hermes config set`（缩进错误会崩 live gateway）。
- key 值任何片段不保留在 memory/摘要；用户重发 key 时按 REDACTED 处理，仅用于写入 .env / auth add。

## 切换默认模型

用户明确要求"切换到 X 模型"时（区别于只添加）：

```bash
hermes config set model.default <model>       # 例：qwen-plus
hermes config set model.provider <provider>   # 例：alibaba
hermes config set model.base_url <url>        # 例：https://dashscope.aliyuncs.com/compatible-mode/v1
```

- 每步 set 会警告"enabled unpinned cron job has stored model/provider_snapshot values that
  differ" — 一次性 cron 可忽略；长期 cron 用 `cronjob action=update job_id=... provider=... model=...` 钉住。
- 改完 `hermes chat -Q -q "测试"` 验证。
- **告诉用户当前会话仍是旧模型**，新会话/重启 gateway 才生效；桌面端可尝试模型下拉热切换。

## 验证

- 配置后用同一 curl 探针走配置后的 base_url 再打一次，确认 200 + 正常回复。
- `hermes config get model.aliases` 确认别名已生效。
- `hermes auth list` / `python3 -c "import json; d=json.load(open('$HOME/.hermes/auth.json')); [print(p, c.get('base_url')) for p,cs in d['credential_pool'].items() for c in cs]"` — 确认凭证 base_url 已是目标站点。
- 端到端：`hermes chat -Q -q "回复ok" --provider <provider> -m <model>`。
