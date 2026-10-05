---
name: github-china-access
description: "Use when GitHub clone/push times out on China networks."
version: 1.0.0
---

# GitHub Access from Restricted Networks (China)

**Trigger**: `git clone` / `git push` / `git ls-remote` to github.com hangs, times out, or crawls at KB/s. Typical on mainland China networks: channels drift: on 2026-09-21 HTTPS to github.com timed out while `api.github.com`, `codeload.github.com` and SSH (22 **and** 443) all passed — re-measure, never trust an old channel table.

Worked example (user's jiayang repo + Obsidian vault sync): see `references/jiayang-obsidian-vault-sync.md`.
Multi-device Obsidian vault sync (desktop plugin + phone GitSync app, vault-repo architecture): see skill `obsidian-git-sync`.

## Probe nuance: system proxy vs bare curl (check FIRST)

This Mac runs a Clash-style **system proxy** (`scutil --proxy` → HTTP/HTTPS at `127.0.0.1:7897`). GUI apps (browser) route through it; `curl`/`git` in a shell only honour `*_proxy` env vars, which are **unset** here. So a bare `curl https://github.com` timing out does **not** mean the host is blocked — it means the *shell bypassed the proxy the browser is using*. Before declaring anything blocked:
```bash
scutil --proxy | grep -E 'HTTPEnable|HTTPPort|HTTPSEnable|HTTPSPort'   # is a system proxy on, and where
curl -sI -m 12 https://github.com                                       # direct (no proxy)
curl -x http://127.0.0.1:7897 -sI -m 12 https://github.com              # through the proxy
```
Measured 2026-09-21 from this Mac: direct `https://github.com` **timed out**; `api.github.com` 200; `codeload.github.com` 301; `git@github.com` SSH **22 and 443 both authenticated**. Channels drift over time — re-measure per session instead of reusing an old verdict table.

Phone-side clones (GitSync etc.) have **no** such proxy, so an HTTPS remote that works fine from this Mac can hang on the phone on the same WiFi.

## Connectivity triage (fast fail, in order)

1. **API probe** (fastest signal that a path exists):
   `curl -s -m 15 https://api.github.com/repos/<owner>/<repo>`
   JSON back = api.github.com works. Use it for `"size"` (KB), `"default_branch"`, `"private"`, and `contents/<path>` for file listings.
2. **Mirror speed test**:
   `curl -sS -m 12 -o /dev/null -w "%{speed_download} B/s\n" "https://gh-proxy.com/https://github.com/<owner>/<repo>/archive/refs/heads/<branch>.zip"`
   gh-proxy.com typically gives MB/s vs ~30 KB/s direct.
3. **SSH 443 check**: `ssh -T -p 443 -o ConnectTimeout=8 git@ssh.github.com` — auth usually passes; large transfers may still be slow.

## Working recipe

1. **Clone via mirror** (fast, full history):
   `git clone "https://gh-proxy.com/https://github.com/<owner>/<repo>.git" <dir>`
2. **Point remote at SSH 443 URL for pushing**:
   `git remote set-url origin ssh://git@ssh.github.com:443/<owner>/<repo>.git`
3. **Commit and push small deltas** — only new objects cross the wire, so SSH 443 handles it fine even when full clone is slow.
4. **Verify remotely** (don't trust push output alone):
   `curl -s -m 15 "https://api.github.com/repos/<owner>/<repo>/contents/<path>"` → confirm the file/folder landed.

## Pitfalls

- **gh-proxy/codeload tarballs don't support byte-range resume** (`curl -C -` → HTTP 56). Download must finish in one shot; use generous `-m` and retry whole-file.
- **macOS has no `timeout` command.** Fail fast with `git -c http.lowSpeedLimit=1 -c http.lowSpeedTime=15 ls-remote ...` or `curl -m N`.
- **Auth paths on this machine**: SSH key `~/.ssh/id_ed25519` (GitHub user jesse0830) is the working auth; there is no git-credentials file, no credential.helper, no gh CLI, no PAT. HTTPS writes via Contents API are NOT possible without a token — SSH is the auth path.
- **Large repos**: `--depth 1` shallow clone is fine for read-only. If you must push back without force, you need full history — the mirror clone gives it fast, so prefer that over shallow.
- **Never force-push** a user's repo just to dodge downloading history — it destroys remote history.
- Large binary files in a repo (e.g. 60MB+ .pptx) make every clone slow; mention `--depth 1` to the user for read-only clones.
