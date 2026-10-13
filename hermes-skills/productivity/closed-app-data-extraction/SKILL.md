---
name: closed-app-data-extraction
description: "Export a closed desktop app's data into notes/files."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos, windows]
metadata:
  hermes:
    tags: [desktop-app, data-extraction, sandbox, obsidian, markdown, integration]
    category: productivity
    related_skills: [desktop-app-state-diagnosis, obsidian, obsidian-git-sync, ocr-and-documents]
---

# Pulling data out of a closed desktop app into notes / files

Class of problem: the user asks "can you link <app> to my notes / knowledge base?" for an app with
no public API, no export button worth using, and content that only lives inside the GUI.

**Core rule: the app's own on-disk store is almost always readable — read that first.** A local
sandbox/container copy gives full fidelity with zero credentials and zero network calls; the app's
cloud API is the fallback, and its own manual export is the last resort. Answer with real numbers,
not with a plan. If the item body you need turns out to be encrypted on disk, the *running app's own
loopback core* is the second local route (step 7) — still no cloud, still no credentials of your own.

## Procedure

1. **Identify app + bundle id** (names collide with folder names).
   ```bash
   ls /Applications | grep -iE "<keyword1>|<keyword2>|<english-name>"
   /usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "/Applications/<App>.app/Contents/Info.plist"
   ```
   Search by Chinese keyword, pinyin AND the vendor's English brand — the .app name is often not the
   name the user says out loud.
2. **Locate the real data directory.** macOS sandbox: `~/Library/Containers/<bundle-id>/Data/Library/Application Support/<dir>/`.
   For Electron apps, the helper process args name the exact `--user-data-dir` plus the logged-in user id:
   ```bash
   pgrep -fl "<App>|<vendor-binary>"   # look for --user-data-dir=..., --port, bearer, <userId>
   ```
   Prefer this over guessing: it hands you the data root, the account id and (see pitfalls) a loopback API.
3. **Inventory the store** before parsing anything: `find "$D" -maxdepth 3 | head -50`, `du -sh`, then
   read the index files (usually plaintext JSON/SQLite: `db.json`, `book_db.json`, `*.sqlite`) with Python
   and print keys + a short sample only. Index files give item ids, titles, folders and update timestamps —
   everything the exporter needs.
4. **Classify each per-item payload** into three buckets and stop guessing early:
   - plaintext JSON → transcripts, OCR text, annotations (the useful part);
   - binary assets → page images, audio (copy or reference, don't inline);
   - private/encrypted → hand-written or ink bodies. If one `zlib`/`head -c` attempt does not decode it,
     call it encrypted and move on; do not spend a run of calls on format archaeology.
5. **Discover the sync mechanism the vault may already have for this app before writing anything.** Look
   inside the export target folder first (`_工具/`, `_索引.md`, `.sync-state.json`): an earlier session may
   have already built an exporter for this app. Upgrade that script in place rather than starting a second
   pipeline — version it (`VERSION = "1.x"`) and bump the version so the state file forces a re-export when
   the content rules change.
6. **Write ONE exporter script**, idempotent and incremental, saved somewhere durable (vault `_工具/`, or
   the work docs folder) — not in scratch. State file (`.sync-state.json`) keyed by item id + updated-at +
   attachment signature so a rerun skips unchanged items in seconds.
7. **When the on-disk body is encrypted but the app is running, its own local core service is the read
   route** — with the user's explicit OK. Electron desktop apps usually run a loopback HTTP core
   (`--port` in the helper args) that the GUI itself calls; it returns decrypted bodies for the same items.
   Recover its contract from the packed client instead of guessing: map the client's route symbols to path
   prefixes in ONE pass, and if it signs requests, reproduce the signature from the client's own code.
   Take the port and shared secret from the live process at call time, hold them in memory only — never
   print, log or write them.
8. **Land the output as Markdown the vault already understands**: one folder per app notebook, filename
   `<title> [<id8>].md`, YAML frontmatter (title, source app + bundle id, id, created, updated, notebook,
   tags), body sections per content type (transcript with `[mm:ss]` timecodes, OCR text, embedded page
   images), assets copied into `assets/`. One auto-generated `_索引.md` grouped by notebook with wikilinks
   is what makes the dump feel like part of the vault instead of a data dump.
9. **Verify by reading the output back**, not by counting: `head -20` the largest note, `wc -c` it, and grep
   one known phrase. Then confirm the vault's own sync (obsidian-git auto-commit/push) carries it to the
   other devices.
10. **Run a quality-review pass over the export, then triage — do not just fix.** Re-read the produced files
   programmatically (per-file size, section inventory, longest/shortest note, known phrases) and list every
   anomaly. For each one decide **exporter bug** vs **the source really is like that** by querying the app
   side again. Fix only the first class; for the second, mark it inside the note (empty / not generated in
   app) and tell the user how to produce it in the GUI and re-run. Never pad a gap with invented content.
11. **Deliver one short versioned doc** (per the user's versioning convention): data path, what is covered,
   what is not, and the two upgrade routes (cloud API, manual export). Put counts and file paths in the reply.

## Pitfalls

- **Stay read-only in the container.** `ls`/`find`/`cat`/`python3`-read/`plutil -p` only; never write,
  rename or delete app data. Exports are copies — say so, so the user knows deleting them is safe.
- **A stored token being present does not mean it works.** Expect `401 token验证失败` from the app's cloud API
  even with a token string on disk: desktop apps keep the refreshed one in memory. The clean routes are the
  running app's loopback service (find `--port` / `bearer` in the helper args) and the app's own export UI.
- **Never refresh the app's token without asking.** Minting a token from a stored refreshToken can rotate the
  app's login state and force the user to re-login by SMS; propose it as an option and wait. Same for calls
  against the app's private loopback port — probe only after the user agrees.
- **State the boundary honestly.** If the hand-written/ink body is encrypted locally, report exactly what IS
  exportable (transcripts, OCR, images, audio) and offer the app's export for the rest. Do not promise
  "full text" or present the encrypted file as decodable.
- **Parse defensively.** Payload shapes vary between files of the same app (e.g. an `words` array holding
  plain strings in one file and `{content: ...}` dicts in another). Normalize types before joining, or text
  is silently dropped while the run still reports success.
- **A scripted patch to the exporter is not done until the exporter runs.** Inserting code by string
  replacement fails silently in two ways: the anchor does not match (so the new function is never defined)
  and injected code references a name that only exists under another spelling elsewhere in the file. A
  `changed` assertion afterwards proves nothing — run the script immediately, grep the inserted symbol, and
  fix any `NameError` before touching content.
- **Check exit codes without a pipe.** `python3 export.py | tail` reports the exit status of `tail`, so a
  crashed run reads as success. Run `python3 export.py > /tmp/log 2>&1; echo exit=$?` and read the log file.
- **Long stdout gets compressed to a single line in this environment.** Write dumps/logs to files and
  `read_file` them back; batch extraction into several medium calls that append to a workspace file rather
  than one giant call; print counts plus a short sample instead of everything.
- **Mine the packed client for the route table, and stop there.** The sandbox store answers item-level
  questions faster, but when bodies are encrypted the client bundle is how you learn the local service's
  routes (`<Name>Router` symbols → path prefixes). Do it in one pass — a single script that maps every
  route symbol to its prefix — instead of one probe per guessed URL; skip format archaeology into the rest
  of the archive (the same pruned output usually gets collapsed to a line, hiding the useful part).
- **Dedupe near-duplicate payloads by shape, not bytes.** The same recording can be transcribed twice (e.g.
  one variant with real speaker names, one with anonymous `说话人1`): identical sentence counts, different
  md5. A hash comparison misses it and the note ships the same transcript twice. Group candidates by
  segment count, keep the richest variant (real names > anonymous, then longest), and name what was dropped.
- **A stray shell probe can trip the approval gate** (curl/grep loops against unfamiliar endpoints). Keep
  probes minimal, single-purpose and read-only; if one is refused, stop and report — do not rephrase it.

## References

- `references/doxent-iflytek-notes.md` — 科大讯飞「读写笔记」(com.iflytek.Doxent) case: container layout,
  what each file yields, the loopback core service and its HMAC request-signing scheme, exporter version
  rules (content classes, dedupe, empty-body and cross-link handling), cloud-API findings, vault output layout.
