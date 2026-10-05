# LLM Wiki.app (macOS): workspace, migration, verification

Concrete instance of the general procedure, for `/Applications/LLM Wiki.app`.

## 1. What it opens

```bash
/usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' "/Applications/LLM Wiki.app/Contents/Info.plist"
ls -la "$HOME/Library/Application Support/"*/llm-wiki/ 2>/dev/null
```

The workspace path is recorded in the app's project registry (state JSON under Application Support) and
mirrored in `<workspace>/.llm-wiki/project.json`. Dump the workspace tree to size up the gap:

```bash
find "<workspace>" -maxdepth 3 -name '*.md' -not -path '*/.llm-wiki/*' | sort
```

Skeleton-only — empty `purpose.md` / `schema.md`, empty `wiki/*.md`, empty `concepts/` and `entities/` —
is the "app has no content" state. The user's Obsidian vault with the real pages is typically a sibling
folder, one path segment away.

## 2. Layout the app expects

```
<workspace>/
├── purpose.md          # project goal, key questions, scope — the app reads this for context
├── schema.md           # the app's OWN layout spec; conform to it, never replace it
├── wiki/
│   ├── index.md        # nav backbone, sectioned (Entities / Concepts / Sources / Queries) + Total pages
│   ├── log.md          # append-only action log
│   ├── overview.md
│   └── concepts/ entities/ queries/ sources/
├── raw/sources/        # full-length source documents live here
└── .llm-wiki/          # app state: project.json, file-snapshot.json, chats, vector store
```

## 3. Migration pattern (copy, never move)

One Python script, vault left intact:

- vault knowledge pages (`<vault>/LLM-wiki/concepts/*.md`) → `<workspace>/wiki/concepts/`
- full-size source documents → `<workspace>/raw/sources/` (a page over the schema's line threshold is a
  source document, not a wiki page)
- rebuild `wiki/index.md` in the app's format with a real `Total pages` count
- append to `wiki/log.md` (dated entry listing the files added)
- fill `purpose.md` (was a template) and **append** a "Local Conventions" section, with a version marker, to
  `schema.md`

Write the per-file report to a file and `read_file` it back — the on-disk copy is what you quote to the user.

## 4. Verification

```bash
open -a "LLM Wiki"; sleep 8
python3 -c "
import json,os
ws=os.path.expanduser('<workspace>')
snap=json.load(open(ws+'/.llm-wiki/file-snapshot.json'))
print(snap.get('updatedAt'), len(snap.get('files',{})))"
```

`file-snapshot.json` is rewritten on each launch with every file the app can see; combined with the project
registry's `lastOpened` this proves ingestion. A `screencapture` after `open -a` may show only the desktop
(the window can be on another Space) and `osascript` window geometry needs Accessibility permission — so rely
on the state files and ask the user to confirm the window once.

## 5. Keeping app state out of git

```gitignore
<workspace>/.llm-wiki/
<workspace>/.obsidian/workspace*.json
<workspace>/.trash/
```

The workspace is itself an Obsidian vault (it has `.obsidian/`), so registering it as a second Obsidian vault
serves both apps from one copy. Two parallel copies of the same pages drift.

## 6. Integration surface

`/Applications/LLM Wiki.app/Contents/Resources/mcp-server/` is the app's own MCP server — registering it
(see the `native-mcp` skill) lets an agent query the wiki without the user browsing the GUI.
