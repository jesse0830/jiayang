# Update error signatures (seen 2026-08-05, 0.14.0 → 0.20.0)

| Signature | Meaning | Action |
|---|---|---|
| `ImportError: cannot import name 'require_readable_config_before_write' from 'hermes_cli.config'` (trailing traceback in `_kill_stale_dashboard_processes`) | Update process itself ran old code mid-update (stale sys.modules) | None — verify with fresh `./venv/bin/hermes --version` |
| `⚠ platform.feishu failed to refresh: cannot import name 'apply_subprocess_home_env' from 'hermes_constants'` | Same benign cause (stale module mix in the running process) | None; symbol exists in new hermes_constants.py (~line 932) |
| `npm error EBADENGINE ... Required: {"node":">=22.22.0","npm":"<11.10.0 || >=11.17.0"} Actual: node v24.18.0, npm 11.16.0` | npm too old for the new engines requirement | `npm install -g npm@latest` (→ 12.0.2) |
| `npm error command sh -c node install.js` + `RequestError: read ETIMEDOUT` | electron binary download blocked (CN network / GitHub) | `ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/ npm install` + persist in .npmrc |
| `CONFLICT (modify/delete): ui-tui/package-lock.json deleted in Updated upstream and modified in Stashed changes` | Upstream deleted a file you had locally modified | Do NOT restore package-lock.json (lockfile consolidated to repo root); restore only meaningful mods |
| `Your fork is not tracking the official Hermes repository.` | No upstream remote configured | `git remote add upstream https://github.com/NousResearch/hermes-agent.git` |

## Session timeline (2026-08-05)
- Pulled 11603 commits, 0.14.0 → 0.20.0; Python deps rebuilt in venv.
- Autostash `hermes-update-autostash-20260805-011331` (ref f17e645a): contained weixin.py mod + package-lock.json mod. Tree was reset to clean state; stash preserved.
- weixin.py mod restored via `git checkout stash@{0} -- gateway/platforms/weixin.py`, then `git stash drop stash@{0}`.
- npm upgraded 11.16.0 → 12.0.2 to satisfy engines.
- electron mirror added to project .npmrc; root `npm install` then succeeded (1180 packages).
- ui-tui rebuilt: `npm install && npm run build` → `built .../ui-tui/dist/entry.js` (3.5mb, 68ms).
- Update stopped 3 dashboard processes (expected; restart hermes web/dashboard if used).
- Current chat session kept running old code until user restarted hermes.
