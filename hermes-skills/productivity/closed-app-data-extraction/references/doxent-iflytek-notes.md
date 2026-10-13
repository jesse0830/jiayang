# Case: 科大讯飞「读写笔记」 Doxent (macOS, com.iflytek.Doxent)

Electron app. Notebook/smart-pen notes (录音转写 + 手写页) sync into a local sandbox store that is
plaintext-readable; an exporter turns it into Markdown in the Obsidian vault.

## Identity & paths

```
/Applications/读写笔记.app                      bundle id: com.iflytek.Doxent
~/Library/Containers/com.iflytek.Doxent/Data/Library/Application Support/doxent/       <- data root
  data/<userId>/                                 userId, e.g. 261006102724545082
    db.json                                      note index: noteId, noteName, summary,
                                                 createTime/updateTime (epoch ms), dirName, dir, type, isDel, appDel
    book_db.json                                 notebook-level index
    <noteId>/res/                                per-note payloads (see table)
    <noteId>/note_json                           note body — private/encrypted, does not decode
  log/network.log, log/note.log                  show the cloud endpoints the app calls
  offline_info                                   local credentials (never print values)
```

Always wrap the path in a shell variable — `Application\ Support` escaping inside quotes breaks;
`D="$HOME/Library/Containers/com.iflytek.Doxent/Data/Library/Application Support/doxent"` then use `"$D/..."`.

## What each file yields

| File | Content | Usable |
|---|---|---|
| `db.json` | item index (title, times, notebook, type, delete flags) | yes, plaintext JSON |
| `<noteId>/res/*.txt` | recording transcript, per sentence, with timecodes | yes, plaintext JSON |
| `<noteId>/res/*.json` | OCR text of each page (handwriting + print) | yes, shape varies per file |
| `<noteId>/res/*.jpg`/`png` | page images | yes |
| `<noteId>/res/*.opus` | original audio | yes, large |
| `<noteId>/note_json` | authored/ink body | no — encrypted/private |

Extra findings: the app runs a WeChat ACP bridge (`claw/openclaw-wechat-acp/runtime-config.json`), and it
ships its own mindmap/image note types — both are just more entries in the same index.

## Cloud API (fallback route)

The app calls `http://api.iflyink.com/xbew-api` — e.g. `note/dir/getListAllByUserIdPc`,
`note/dxk/getAllNoteByPage`, `note/dxk/getNoteDetail` (visible in `log/network.log`). Calling it with the
token stored in `offline_info` returns `{"code": 401, "message": "token验证失败"}` — the on-disk token is
stale, the app holds the refreshed one in memory. Also, the running app's helper process exposes a loopback
service with a live token in its argv:

```
... App.asar/dist/core/index.js --port <port> --user <userId> bearer <token> ...
```

That loopback port is the actual route to the full note body. **Do not call it (or mint a new token from the
stored refreshToken) without the user's explicit OK** — it shares/rotates the app's login state.

## Loopback core service (the route that actually returns note bodies)

Solved and in production use. The app's core process (Electron helper) listens on 127.0.0.1 and returns
**decrypted** bodies + generated AI content for the same noteIds:

```
... App.asar/dist/core/index.js --port 46588 --user <userId> bearer <token> ...   # token: memory only
```

Request signing (reproduce from the client bundle, do not guess):

```
X-Sign = HMAC-SHA256(signSecret, METHOD + "\n" + <raw url INCLUDING query> + "\n" + timestamp + "\n" + nonce + "\n" + sha256(body))
```

The signature **must cover the query string** — signing only the path gives 401. Any later script should
`from doxent_pull import call` rather than reimplementing this.

Endpoints used: `GET /list/list` (item list) and `GET /note/getDetail?noteId=...` (one note). Loopback port
and secret come from the live process argv at call time; keep them in memory, never print or write them.

Where the bodies live inside `getDetail`'s response:

- `data.note.content.summaryContent.aiMapData[]` — the AI tabs: `tabId=2` 实时要点, `tabId=3` **纪要**,
  `tabId=5` 手写重点关注. Each tab carries `title` + `content`; an empty `content` means the app never
  generated it (report that — do not treat it as an export miss).
- `data.note.html` / `data.note.contentText` — body for `type=10` notes (app-internal 「纪要」 notes whose
  `res/` folder is empty); may be an empty shell like `<h1></h1>`.
- Raw payloads stay in `<noteId>/res/`: 纪要 = plaintext **HTML**, 逐字稿 = plaintext **JSON**.

## Exporter

`<vault>/读写笔记/_工具/doxent_export.py` — reads `data/<userId>/` read-only, writes:

```
<vault>/读写笔记/_索引.md                 index grouped by notebook, wikilinks
<vault>/读写笔记/<dirName>/<title> [<id8>].md
<vault>/读写笔记/assets/*.jpg             page images
<vault>/读写笔记/.sync-state.json         noteId -> {updated, file signatures} for incremental reruns
```

Per-note body order: frontmatter (title, source, noteId, created/updated, notebook, tags, delete state) →
`## 📋 AI 会议纪要` → `## ✍️ 文本内容/要点` → `## 🎙 录音转写` (`[mm:ss]` prefixes) → `## 🧭 该笔记的 AI 标签页`
(a per-tab has-content table: 实时要点 / 纪要 / 手写重点关注) → images/audio notes → `## 🧩 其他结构化数据`.
Deleted-in-app notes are still written but flagged in frontmatter, so nothing is lost silently.

Content classes (v1.1+): **AI 纪要** (HTML starting with `<h1>` / 含「会议纪要」) vs **实时要点** vs
**录音转写** — classifying these correctly is what stops a recording-without-minutes from looking like a
failed export. The per-tab table plus an inline `ℹ️` line makes the gap explicit and tells the user to
regenerate the minutes in the app and rerun.

Hard-won rules baked into v1.4 (each started as a review finding):

- **Empty-shell guard.** Convert html → md, then require real text
  (`re.sub(r"[#*\-|>\s]", "", md)` non-empty). Without it an empty `<h1></h1>` renders as a lone `#`, and
the note looks like it has a body it does not have. Distinguish "app note is empty" (mark `⚪ App 内该笔记为空`)
from "core returned nothing".
- **Dedupe transcripts by shape.** Two `res/*.txt` transcripts of the same meeting can differ in md5 while
  having identical segment counts (one variant with real speaker names, one with anonymous `说话人1`). Group
  by segment count, keep the richest (real names > anonymous, then longest text), and note what was dropped.
  Hash-based dedupe alone missed this and shipped a 277928-char note that should have been 152485.
- **Cross-link split notes.** The app sometimes stores a meeting's minutes as a *separate* note named
  `纪要_<meeting name>`. Don't report a missing minutes block — detect the sibling by name and emit a
  bidirectional `🔗` wikilink from both notes.
- **State file carries the version.** `.sync-state.json` stores `v: VERSION`; bumping `VERSION` forces a
  full re-export, which is how content-rule changes get applied to already-exported notes. Keyed by
  `noteId -> {updated, v, res:{basename: size}}`.

OCR normalization that matters: `note_json`-adjacent OCR JSON may hold `words` as plain strings or as
`{content: ...}` objects — handle both, else the note exports with an empty body while reporting success.

Verified state (2026-10-10): exporter **v1.5** (adds the core probe + safe skip; see Auto-sync below, **18 / 18** notes exported (12 会议纪要 + 2 MBA + 4 未分类),
index rewritten, pushed to `origin/master` by obsidian-git auto-sync. Notebook folder comes from `dirName`
frozen at first write, so a note that moves notebook leaves a stale file behind at the old path — that shows
up in `git status` as `D <old path>` + `?? <new dir>/`; that is normal, not a duplicate.

## Auto-sync (scheduled, no manual step)

Manual trigger still works: `cd <vault>/读写笔记/_工具 && PYTHONPATH= python3 doxent_export.py`.
For zero-touch, a Hermes cron job runs a gatekeeper every 30 min.

- Gatekeeper (true source, lives IN the vault so it travels with git):
  `<vault>/读写笔记/_工具/doxent_sync.py` — forces `DOXENT_REQUIRE_CORE=1`, runs the exporter with
  `PYTHONPATH=`, appends to `sync.log` (trimmed to last 400 lines), and prints NOTHING when nothing changed.
- The cron entry point must be a *relative filename* under `~/.hermes/scripts/` (absolute paths are
  rejected by cronjob_manage): `~/.hermes/scripts/doxent_autosync.py` runpy-forwards to the vault script.
  Job shape: `no_agent=true`, `script=doxent_autosync.py`, schedule `30m`, `deliver=origin`.
  no_agent + empty stdout sends nothing (watchdog pattern) → it only pings when notes were added.
- Why the guard matters: with the app closed the creds/socket probe fails and the export silently lacks
  the AI 纪要 tabs — and that degraded body is then cached as "unchanged" by `.sync-state.json` (state keys
  on noteId+updated+version), so a later healthy run may skip it. `DOXENT_REQUIRE_CORE=1` makes `main()`
  return 2 and write NOTHING. Test the guard non-destructively by stubbing `m.core_creds = lambda: (None, None, 0)`
  **and** redirecting `m.OUT` to /tmp, so even a broken guard cannot touch real notes.
- Port drift: the exporter reads the port from the core process argv (`--port <n>`) and TCP-probes
  `127.0.0.1:<port>` before trusting it, so an app restart on another port can't silently degrade output.
- Obsidian must be open for obsidian-git to push every 5 min; if it is closed the notes still land on disk
  and push on next launch. Human edits here are write-only to the vault — the app itself stays read-only.

## Downstream mining (纪要 → 素材)

The exported `.md` is section-marked, so the analysis-ready part is cheap to pull: slice
`## 📋 AI 会议纪要` → `## 🎙 录音转写` and print only that slice in one call (dumping several meetings'
bodies at once gets the output compressed to a single line, i.e. you read nothing).

Minutes record **project facts and management conclusions**, not framework vocabulary: a literal grep for
abstract terms (交付过程 / 过程痛点 / 抓过程) returns zero hits even when the material is everywhere in the
notes. Never conclude "the knowledge base has nothing" from a zero-hit grep — read the per-meeting 纪要
sections and归纳 semantically, using a known root-cause list as the cross-check anchor.

## Verification used

`head` + `wc -c` on the biggest note and a grep for a known phrase in the 基本公式 MBA note. For v1.4 the
checks were: largest note 152485 chars (八达光电, after transcript dedupe), 5 meetings carry a real AI 纪要
+ 1 standalone `纪要_…` note, 2 have only 实时要点/转写, empty notes marked `⚪`; then `git fetch` +
`git ls-tree -r origin/master -- 读写笔记` (12 会议纪要 / 2 MBA / 4 未分类) and
`git show origin/master:读写笔记/_工具/doxent_export.py | grep VERSION`. Note obsidian-git auto-commits
every 5 min, so by the time you run `git commit` the tree is often already clean and pushed — verify with
`git rev-list --count origin/master..HEAD` (0 = landed) instead of trusting your own commit.
