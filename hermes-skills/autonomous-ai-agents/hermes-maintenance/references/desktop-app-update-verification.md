# Desktop app (图形化界面) update verification — 2026-08-18

Context: user runs the repo-built desktop app (not a packaged install). After `hermes update`
pulled 859 commits (0.20.1 → 0.20.3 / v2026.8.16.2), verify the FULL chain below.

## Where things live
- Desktop app source: `apps/desktop/` — NOT ui-tui/ (ui-tui = Web UI/TUI, `ui-tui/dist/entry.js`).
- User's running instance: `apps/desktop/release/mac-arm64/Hermes.app` (built from repo, not /Applications).
- Desktop web bundle: `apps/desktop/dist/` (e.g. `dist/index.html`).

## Post-update verification chain (run in order)
1. `git status -sb && git log --oneline -3` → main synced with origin/main, no "behind".
2. `./venv/bin/hermes --version` → new version (e.g. 0.20.3). CLI works = Python deps fine.
3. `stat -f "%Sm" apps/desktop/release/mac-arm64/Hermes.app` AND `stat -f "%Sm" apps/desktop/dist/index.html`
   → build timestamps should be AFTER the update ran (a fresh build proves `hermes update`
   rebuilt the desktop app automatically; it does in recent versions).
4. `hermes gateway status` → note PID/start time; recent `hermes update` auto-restarts the
   gateway with new code. If `gateway status` warns "Service definition is stale relative to
   the current Hermes install", run `hermes gateway start` to refresh the launchd plist
   (safe when gateway already running).
5. `git status --short` → only expected local mods (.npmrc, gateway/platforms/weixin.py).

## User-facing completion step
The RUNNING desktop app window is still the old instance — the user must quit and relaunch
Hermes.app to see the new build. Gateway needs no manual restart (already on new code).

## Interrupted-update recovery
If a previous update turn was interrupted (process not found, "Orphan recovery" warning):
do NOT blindly rerun `hermes update` — first run the chain above. The update may have
finished (git log shows new HEAD, version is new, Hermes.app freshly built). Only rerun if
git log still shows the old HEAD.
