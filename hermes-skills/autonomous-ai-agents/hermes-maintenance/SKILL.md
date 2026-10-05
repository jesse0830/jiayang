---
name: hermes-maintenance
description: "Maintain the local Hermes git install: run hermes update safely, recognize benign post-update crashes, recover local mods from the autostash, fix npm engines + electron mirror issues (CN network), rebuild the Web UI."
version: 1.0.0
platforms: [macos]
---

# Hermes Maintenance (local git install)

Maintaining the Hermes Agent git install on this machine — running `hermes update` without losing local changes, recognizing benign post-update crashes, fixing npm/node/electron issues (China network), rebuilding the Web UI.

## When to use
- User asks **whether the client needs upgrading**（「这个客户端需要升级吗」）→ 先跑「## 先判断要不要升级」取证，别只 `hermes --version`。
- User asks to update Hermes (`hermes update`) or reports a broken update / post-update ImportError.
- npm / Web UI build failures inside ~/.hermes/hermes-agent.
- Need to restore local modifications after an update.

## Environment facts (this machine)
- Install: ~/.hermes/hermes-agent (git install, venv at ./venv, run via ./venv/bin/hermes).
- origin = https://gitcode.com/GitHub_Trending/he/hermes-agent.git (a fork). upstream = https://github.com/NousResearch/hermes-agent.git (added 2026-08 so updates can track official releases).
- Local mods kept across updates: **ONLY `.npmrc`** (the `electron_mirror` line — upstream's `.npmrc` overwrites it every update, re-append it).
- **`gateway/platforms/weixin.py`: leave it at upstream — do NOT re-apply the old local edits.** Verified 2026-09-22 by function-level diff: the old local edits (a) added 3 markdown helpers (`_rewrite_table_block_for_weixin`, `_rewrite_headers_for_weixin`, `_split_table_row`) that were **never called from anywhere — dead code**, and (b) *reverted* newer upstream fixes (`keepalive_timeout=2` + `enable_cleanup_closed`, `asyncio.wait_for` instead of aiohttp `ClientTimeout`, shared `greedy_pack_blocks`, the #27300 voice-item STT path). They were leftovers of a botched earlier stash restore, not features. Upstream 0.21.x already ships table-aware wrapping, text debounce batching, and the `ret=-2 … the user must send the bot a message first (or re-pair)` diagnosis the old local file lacked.
- node v24.18.0, npm 12.0.2 (upgraded from 11.16.0 to satisfy engines requirements).
- Project .npmrc carries `electron_mirror=https://npmmirror.com/mirrors/electron/` (required in CN network).

## Desktop app (Electron) update flow
- The DESKTOP app can trigger its own update (root `posix.sh --desktop-pid <pid>`, then `hermes update --yes --gateway --branch main`). While that runs, a CLI `hermes update` is rejected by the anti-reentrancy lock: exit 2, "Another Hermes update is already running (PID …)". Do NOT retry — wait or investigate.
- Symptom "desktop app won't open / stuck on 'Version X — app build out of date'": the desktop app relaunched into the update-status page (serve-ui.py on a temp port) while the rebuild hangs. The usual hang: `desktop --build-only` → `npm ci` → electron@… `postinstall node install.js` downloading from GitHub (blocked in CN). Check: child chain `posix.sh → hermes update → hermes_cli.main desktop --build-only → npm ci → node install.js`, electron cache dir has no new download, 0% CPU.
- Fix: kill the whole chain (`kill -9` on install.js, npm ci, --build-only, hermes update, posix.sh — children first), then `cd ~/.hermes/hermes-agent && ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/ ./venv/bin/hermes desktop --build-only`, then `open apps/desktop/release/mac-arm64/Hermes.app`.
- A killed/interrupted update leaves the autostash NOT restored — recover via `git stash apply` (expect conflicts) or `git checkout stash@{0} -- <file>` for specific files. Merge can also silently drop upstream-added functions when local edits deleted that region: after resolving, grep the file for every call target (e.g. `_wx_secret`, `_enqueue_text_event`) and restore missing defs from `git show HEAD:<file>`. **Exception (2026-09-22): for `gateway/platforms/weixin.py` do NOT do this** — its conflicted stash restore came from obsolete local edits, so accept upstream's version and drop those hunks (see "Local mods" above).
- Verify desktop rebuild: `apps/desktop/release/mac-arm64/Hermes.app/Contents/MacOS/Hermes` has a fresh mtime; app runs (ps shows Hermes.app processes); old update-status port is released.

## 先判断要不要升级（「这个客户端需要升级吗？」）

一键取证：`bash <skill_dir>/scripts/check_update_status.sh [--fetch]`（本地只读；`--fetch` 才联网刷 ref）。要点：

1. **客户端自己已经算过一遍，先读它的结论**：`$HERMES_HOME/.update_check` 是缓存判断，形如
   `{"ts": …, "behind": 13542, "rev": null, "ver": "0.20.6"}`；界面判据在 `apps/desktop/src/app/settings/about-settings.tsx`：`updateAvailable = behind > 0 || status?.updateAvailable` —— 只要 `behind > 0` 它就会提示可更新。
   `rev: null` 的含意：它想用 **GitHub compare API** 拿精确数但失败了（github 直连不通），退回本地 `rev-list` 计数。同目录 `.update_exit_code` = 上次 update 的退出码（0 = 正常）。
2. **先验证 `behind` 是不是真的，再写进结论** —— `hermes_cli/banner.py` 注释自己就警告过 `HEAD..origin/main` 可能报「huge bogus behind」（浅克隆 / 局部 fetch 让历史断裂）：
   - `.git/shallow` 存在 → 计数不可信；
   - `git merge-base HEAD origin/main` **等于 HEAD 自身** 且 `git rev-list --count origin/main..HEAD` = 0 → 本地是远端**干净祖先、可快进**，该计数为真（本例 13542 为真）。
3. **决定性对比是版本号，不是提交数**：`git show origin/main:hermes_cli/__init__.py | grep __version__`（本例 0.20.6 → 0.21.4）**和** `git show origin/main:apps/desktop/package.json`（0.17.0 → 0.17.6）—— 两个都要比（CLI 与桌面 app 版本号是两套编号）。
4. **落后几个 release + 改动规模**（用来说服用户、估风险）：`git log --oneline HEAD..origin/main -- hermes_cli/__init__.py` 会列出 `chore(release): v0.21.x` 一列，一眼看出跨几个版本；`git diff --shortstat HEAD origin/main -- gateway|hermes_cli|apps/desktop|ui-tui` 给规模 —— **gateway 大改时 autostash 回填 `gateway/platforms/weixin.py` 极易冲突**，必须提前告知用户并准备手动恢复（见上文）。
5. **网络先分清两条通道**：`origin` 是国内 gitcode，**拉代码不需要代理**；但 GitHub compare API（精确 behind）和 electron 二进制下载需要代理/镜像（`.npmrc` 的 electron_mirror）。macOS **没有 `timeout` 命令** → 探测用 `curl --max-time N`，给 git 加超时用 `perl -e 'alarm shift; exec @ARGV' 90 git fetch …`；代理是否在听：`lsof -nP -iTCP:7897 -sTCP:LISTEN` + `scutil --proxy`。
6. **结论必须落到动作**：要升级 → 给「先打包回滚快照（git ref + 本地改动 diff）→ update → 校验版本/weixin.py/ui-tui dist → 提示重启客户端」；不需要 → 说清依据（版本号相同 / behind 为 0 或计数不可信）。

## Update procedure
1. Run `hermes update`. It: fetches from the fork, autostashes local changes, pulls, tries to restore the stash, updates Python deps, syncs bundled skills, rebuilds the Web UI.
2. Expect a possible trailing crash — see pitfalls #1 (usually benign). Don't panic at exit code 1.
3. Verify in a FRESH process: `cd ~/.hermes/hermes-agent && ./venv/bin/hermes --version` → should show the new version + "Up to date". Note: the user's CURRENT chat session still runs the old code until they restart hermes.
4. If local mods were stashed but not auto-restored: `git checkout stash@{0} -- gateway/platforms/weixin.py` (only the files you actually want), then `git stash drop stash@{0}`.
5. If the Web UI failed to build: `cd ui-tui && npm install && npm run build` — success looks like "built .../ui-tui/dist/entry.js".
6. Remind the user: restart the CLI/gateway to load the new version; the update stops dashboard processes (restart if hermes web / dashboard is used).

## Pitfalls
1. **BENIGN trailing crash.** `hermes update` can exit 1 with an ImportError (e.g. `cannot import name 'require_readable_config_before_write' from 'hermes_cli.config'`) or a lazy-backend refresh warning (`cannot import name 'apply_subprocess_home_env' from 'hermes_constants'`). Cause: the running update process imported old modules before the working tree was replaced mid-update — a stale-sys.modules mix, not a broken install. If the symbol EXISTS in the new file (grep it), the update succeeded; do NOT chase this. Verify with a fresh `hermes --version`.
2. **npm EBADENGINE** during update: engines mismatch (node >=22.22, npm <11.10 || >=11.17). Fix: `npm install -g npm@latest`.
3. **electron postinstall timeout**: `RequestError: read ETIMEDOUT` from `node install.js` (electron binary download, GitHub blocked). Fix: `ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/ npm install`. Persist: `echo "electron_mirror=https://npmmirror.com/mirrors/electron/" >> .npmrc` (project root).
4. **Conflict during stash restore**: update resets the tree to a clean state and KEEPS the stash (stash ref is printed — nothing is lost). Restore the files you care about manually (step 4), then drop the stash. Some conflicts are expected: e.g. upstream deleting ui-tui/package-lock.json (lockfile consolidated to repo root) — don't restore that one.
5. **Fork not tracking the official repo**: update may prompt to add `upstream`; say yes, or add manually so future updates can detect official releases.
6. **The update restarts the `serve` backend that hosts your own desktop chat.** A turn in flight dies mid-run (the tool result comes back as "orphan recovery: effect UNKNOWN"). So **launch the update detached** and re-verify afterwards instead of running it in the foreground: macOS has neither `timeout` nor `setsid`, and the terminal guard rejects `nohup`/`setsid`/`disown` in the command string — write a launcher script (allowed) that uses Python `subprocess.Popen(..., start_new_session=True)` and logs to a file, then poll the log in separate calls. `hermes update --plan` (read-only) first shows exactly which services will restart.
7. **`.npmrc` clobbers the electron mirror.** Upstream ships its own `.npmrc`; after an update with a conflicted stash restore, `electron_mirror` is gone (`grep -c electron_mirror .npmrc` → 0). Re-append `electron_mirror=https://npmmirror.com/mirrors/electron/` before any desktop rebuild in the CN network.
8. **Verify by importing, not by file size.** `./venv/bin/python -c` an `importlib.import_module("gateway.platforms.weixin")` plus a smoke call (e.g. `_split_text_for_weixin_delivery("a"*200, 50)`) proves the swapped module actually loads; the gateway log line `✓ weixin connected` proves the channel came back. A clean `git status` on the platform file is expected and fine.
9. **Post-update config warnings are usually not regressions.** `config migration to v45 failed and was skipped: cannot import name '_configurable_keys'` is the stale-`sys.modules` artifact (pitfall 1) — `_config_version` in config.yaml does reach 45. `platform 'teams'/'google_chat' references unknown toolset` only matters if those platforms are actually configured (check: they may simply be absent from `platforms:`).

## Verification
- `git status --short` — after a clean update this shows **only ` M .npmrc`**; a clean `weixin.py` is correct, not a lost customization.
- `./venv/bin/hermes --version` — new version; `hermes update --plan` should list every service already at the new commit.
- Platform modules load: import each touched platform module and smoke-call one public function; grep the gateway log for its `connected` line.
- ui-tui/dist/entry.js exists and is freshly built; desktop `Info.plist` version matches `apps/desktop/package.json` and the app binary mtime is fresh (`defaults read <app>/Contents/Info.plist CFBundleShortVersionString` — use an absolute path, a relative one silently returns empty).

Reference: references/update-error-signatures.md (exact error strings seen on this machine + meanings).
Script: scripts/check_update_status.sh（一键取证「要不要升级」：.update_check 缓存判断 → behind 真伪（shallow/merge-base）→ 远端版本号对比 → 落后几个 release 与改动规模 → 代理状态）。
