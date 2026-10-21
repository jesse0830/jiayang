# Point Codex at DeepSeek (works where OpenAI is blocked)

Use when Codex "can't operate" in China: no OpenAI login, no API reachability.
Codex keeps its CLI + sandbox + apply-patch machinery; only the model backend moves.

## 1. Verify DeepSeek first (curl, 30s)

```bash
K=$(grep -m1 '^DEEPSEEK_API_KEY=' ~/.hermes/.env | cut -d= -f2- | tr -d '"')
curl -s https://api.deepseek.com/v1/models -H "Authorization: Bearer $K" | head -c 400
# Responses API probe (the wire protocol Codex actually uses):
curl -s -o /dev/null -w '%{http_code}\n' https://api.deepseek.com/v1/responses \
  -H "Authorization: Bearer $K" -H 'Content-Type: application/json' \
  -d '{"model":"deepseek-v4-pro","input":"hi"}'   # 200 = usable
```

## 2. config.toml

Add the model keys **at the top of the file, before the first `[section]`**
(TOML: a stray top-level key after a table lands inside that table and is ignored),
and the provider table at the end:

```toml
model = "deepseek-v4-pro"          # or deepseek-flash (cheap/fast)
model_provider = "deepseek"
model_context_window = 262144
model_reasoning_effort = "high"    # DeepSeek accepts none|low|high|max

[model_providers.deepseek]
name = "DeepSeek"
base_url = "https://api.deepseek.com/v1"
env_key = "DEEPSEEK_API_KEY"
wire_api = "responses"
request_max_retries = 4
stream_max_retries = 10
```

Back up first: `cp ~/.codex/config.toml ~/.codex/config.toml.bak-$(date +%Y%m%d)`.

## Pitfalls

- **`wire_api = "chat"` fails on Codex ≥ 0.145**: `codex_models_manager` rejects any
  provider that is not `responses`. DeepSeek *does* serve `/v1/responses`, so use
  `responses` — do not downgrade Codex to get chat-completions support.
- **`warning: Model metadata for <model> not found. Defaulting to fallback metadata`**
  is harmless: `models_cache.json` only ships OpenAI models and cannot be refreshed
  offline. Do not hand-edit it — a cache entry without `model_messages.base_instructions`
  makes the whole cache fail to parse (`failed to load models cache: missing field`),
  which is worse than the warning. A `[models.<slug>]` config table does not silence it.
- **Env var, not auth.json**: `env_key` is read from the process environment, so
  `codex login` is irrelevant. Persist it once:
  - shell: append an `export DEEPSEEK_API_KEY=$(grep ... ~/.hermes/.env)` block to `~/.zshrc`
    (single source of truth = `~/.hermes/.env`; never paste the literal key twice)
  - GUI apps (Codex/ChatGPT desktop): a `~/Library/LaunchAgents/*.plist` with `RunAtLoad`
    that runs `launchctl setenv DEEPSEEK_API_KEY "$K"`. Finder-launched apps do NOT read `~/.zshrc`.
    After editing the plist: `launchctl unload <p>; launchctl load <p>`, verify with
    `launchctl getenv DEEPSEEK_API_KEY | wc -c`, then **restart the app** — a running app
    never picks up a later `launchctl setenv`.
- **Untrusted dir**: scratch dirs need `--skip-git-repo-check` (or a `[projects."<path>"]`
  `trust_level` entry), else it exits with "Not inside a trusted directory".

## Verify end-to-end (do not stop at `--version`)

```bash
D=$(mktemp -d); cd $D; git init -q .
printf 'def add(a,b):\n    return a-b\n' > calc.py
zsh -ic "cd $D && codex exec --skip-git-repo-check --sandbox workspace-write --full-auto 'fix the bug in calc.py'"
cat calc.py   # must show a+b — proves model + tools + file writes all work
```

Starting from `zsh -ic` also proves the persisted env var works in a fresh shell.
