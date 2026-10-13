---
name: desktop-app-state-diagnosis
description: "Use when a desktop app shows empty or stale data."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos, windows]
metadata:
  hermes:
    tags: [desktop-app, troubleshooting, workspace, state-files, verification, macos]
    category: apple
    related_skills: [llm-wiki, obsidian, macos-computer-use]
---

# Desktop app shows empty / stale / unsynced data

Class of problem: a GUI app on the user's machine displays nothing, an old version, or "not synced"
content, while the agent believes the content is in place. Almost always the app is bound to a
**different folder than the one the agent wrote to**, and no amount of re-reading the content files
will reveal it.

**Core rule: ask the app which path it opens, then make that path correct — never assume, never
reinstall, never repoint the app when filling its folder would do.**

## Procedure

1. **Identify the app and version** before anything else — names collide with folders.
   ```bash
   ls /Applications | grep -i <name>
   /usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' "/Applications/<App>.app/Contents/Info.plist"
   /usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "/Applications/<App>.app/Contents/Info.plist"   # → the state-dir name
   ```
2. **Find the app's state directory** (macOS `~/Library/Application Support/<bundle-id>/`,
   Windows `%APPDATA%\<app>\`). List it and read the JSON that names its projects/recent paths —
   keys like `projectRegistry`, `lastOpened`, `recentFiles`, `workspaces`. Long listings get
   compressed/truncated in some environments: write the dump to a file and `read_file` it back.
3. **Get the path from the app's side too**: most such apps mirror their own config inside the
   workspace (e.g. `<workspace>/.appname/project.json`). If the two agree, that folder is what the UI reads.
4. **Diff it against where the content actually lives.** Names are often siblings that differ in one
   segment (`.../JesseYoung-wiki` vs `.../obsidian-vault`) — this is exactly why the user sees "empty".
   Confirm with `find <workspace> -maxdepth 3 -name '*.md' | sort`: skeleton templates and empty
   `concepts/` / `entities/` dirs mean the app was initialized but never fed.
5. **Fix by populating the folder the app reads** — copy, never move, and leave the app's own config
   untouched so the change stays reversible. Match the app's OWN expected layout: if the workspace
   contains a `schema.md` / `README` describing its directories, that file is the spec — conform to it
   (e.g. `raw/sources/` for full-length documents, `wiki/concepts/` for distilled pages) instead of
   inventing structure. If the app's nav file is empty (an `index.md` with no entries, a `Total pages: 0`),
   rebuild it in the app's own format so the UI has something to list.
6. **Relaunch so the app re-scans**, then verify from state, not from pixels (below).
7. **Record what you did in one on-disk report**, so the answer to the user can quote real numbers
   (files migrated, byte sizes, counts) rather than a description.

## Verification: state files, not screenshots

After a relaunch the app rewrites its own index/state — that is the evidence:

```bash
open -a "<App>"; sleep 8
python3 -c "
import json,os
ws=os.path.expanduser('<workspace>')
snap=json.load(open(ws+'/.<appname>/file-snapshot.json'))
print(snap.get('updatedAt'), len(snap.get('files',{})))"
```

A fresh timestamp plus every migrated file present = the app ingested the content. Look for the
app's snapshot / index / cache JSON inside its state dir and use mtime + entry count as the assertion.

Do **not** spend calls trying to force the window into view to screenshot it: `screencapture` records the
active Space only (a background app's window can be on another Space), and `osascript` / System Events
window-geometry queries need Accessibility permission granted to the terminal process. When the state
files check out, hand the final one-glance confirmation to the user explicitly — "if it still looks
empty, `Cmd+Q` and reopen" — rather than claiming a visual verification you did not perform.

## Second mechanism: client/server app — pane stale while the backend is healthy

A different mechanism with the same symptom: the desktop app is a **front-end bound to a local backend**
rather than a viewer of on-disk files. The pane renders the transcript of a **per-run runtime id**; when the
client's socket to the backend drops (app backgrounded / throttled — the close is client-side, `code=1005`),
the backend reaps that run and tells the client so. The client self-heals by resuming, which mints a new
runtime id — that the next drop orphan-reaps in turn. Healing is **capped per app run**, and once the budget
is spent the pane stays bound to the dead runtime for the rest of the process's life, repainting its cached
transcript (i.e. the messages from before the first drop).

Prompts still work, so **nothing is lost**: the composer submits over the HTTP side, the turn runs and
finishes server-side. Confirm the backend is healthy before touching anything:

- the app-side log shows the prompt accepted and the turn finishing (`status=complete`);
- the full transcript is readable in the backend's session store;
- a multi-day app uptime means the dead-runtime records and the heal latch have never been cleared.

**Fix, cheapest first — and never restart the app unasked:**
1. Switch to another session and back (or close and reopen the pane) → fresh resume + transcript refresh.
2. Quit and reopen the app → clears the warm cache, the dead-runtime records and the heal counter; on boot
   it resumes the stored session and re-pulls the transcript. Nothing is lost.
3. Prevention: start a fresh session (`/new`) when the current one has grown huge; update the app if old.

Because the pane is the broken part, also give the user another way to read the answer (CLI session view,
local dashboard URL), and ask any restart question in plain reply text.

See `references/hermes-desktop-stale-pane.md` for the concrete Hermes-desktop logs, processes and commands.

## Housekeeping

- Add the app's machine state to the parent repo's `.gitignore` (state dir, vector store / caches,
  `workspace*.json`, trash). Content markdown stays versioned; chats, indexes and snapshots do not.
- When the app's workspace is itself a valid vault/project of another app (it contains `.obsidian/`,
  `.vscode/`, etc.), offer to register it there as a second workspace so one copy of the content serves
  both — two parallel copies drift and the user will hit the same "empty" symptom again.
- Check whether the app ships an integration surface before assuming manual browsing is the only way:
  an MCP server or CLI inside `Contents/Resources/` lets an agent read the app's data directly, which is
  usually what the user actually wants when they say "link these three things together".

## Pitfalls

- **Don't re-read or re-write the content files to "fix" an empty app** — if the app reads another path,
  rewriting the same folder changes nothing. Find the path first.
- **Don't reconfigure or reinstall the app as a first move** — filling its workspace is reversible and
  survives app updates; editing its project registry can leave it pointing at a broken path.
- **Don't trust a copy/migration command's exit code** — verify with a directory listing or file count
  from the destination afterwards.
- **Don't summarize migration output from memory** — land it on disk and read it back; tool output can be
  compressed to a single line in this environment.
- **Don't state that the GUI was checked** when you only verified files. Say what proved what, and ask the
  user for the visual confirmation.
- **Don't read a stale pane as data loss.** Read the backend session store or the log's turn-finished line
  before saying anything about content — the transcript lives server-side, and telling the user their work
  is gone when it is not is the worst failure mode of this task.
- **Don't ask a question only through the GUI when the GUI is the broken thing.** A confirmation dialog or
  prompt popup can be as invisible as the frozen pane it belongs to; put the question in the reply text too.

## Reference

- `references/llm-wiki-app-workspace.md` — the concrete LLM Wiki.app (macOS) case: state file names,
  workspace layout it expects, migration and verification commands.
- `references/hermes-desktop-stale-pane.md` — the concrete client/server case: which log lines prove the
  reap loop, which process owns the socket, where the heal latch lives, and the read-only evidence set.
- Content conventions for the wiki itself (page thresholds, two-layer source pattern, frontmatter) live in
  the bundled `llm-wiki` skill; this skill is only about the app-side plumbing.
