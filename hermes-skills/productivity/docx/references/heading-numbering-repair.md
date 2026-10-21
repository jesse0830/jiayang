# Heading numbering repair in a large .docx

Use when a document's chapter/section numbering is "乱": chapters skip numbers, two
sections share a number, a whole chapter still carries an old chapter number, heading
depth does not match the shown number, table-cell lists restart oddly, or body text has
leftover hand-typed prefixes. Typical of long Chinese 方案/技术文档 that were assembled by
pasting blocks from earlier versions.

Rule zero: **edit the existing package, never extract text and regenerate it.** A 20 MB+
document with images, tables and headers loses its layout the moment text is rebuilt.
Work with `python-docx` on the original file, patching `pPr` and the first run's text only.

## 1. Inventory (before any edit)

```python
from docx import Document
from docx.oxml.ns import qn

d = Document(path)
for i, p in enumerate(d.paragraphs):
    pPr = p._p.pPr
    if pPr is None:
        continue
    e = pPr.find(qn("w:outlineLvl"))
    if e is None:
        continue                      # no outlineLvl => body-level paragraph
    lvl = int(e.get(qn("w:val")))    # 0-8 = heading 1-9; 9 = body level
```

- A heading is `outlineLvl` **0–8**. Word stores 9 for "正文", and pasted blocks often
  carry 9 on paragraphs whose text *looks* like a heading — always treat 9 as body.
- Chapter numbers here are **literal text inside runs** (`"4.1.2 功能说明"`), not list
  numbering fields. Renumbering = rewriting run text, and the number prefix is often split
  across the first few runs, so join `runs[:k]` before matching, then write the new prefix
  into `runs[0]` and blank the rest.
- Count and stash the inventory (`{old, new, lvl, text}` per heading) as JSON before you
  touch anything — that file is the change map, the review artifact and the redo source.

## 2. The five failure shapes to look for

| Shape | Symptom | Fix |
| --- | --- | --- |
| Chapter gap | `3` → `11` → `12`: a block kept its old chapter number | renumber the block (e.g. 11→4) and insert the missing chapter title heading |
| Duplicate number | two headings render the same `4.2` | derive the sequence from outline order, not from existing numbers |
| Depth mismatch | `4.1.2.1.1.6.1 功能说明` has `outlineLvl=5` | set `outlineLvl = segments - 1` (cap 8) so TOC indent equals the number |
| Junk prefix | body paragraph starts `4.1.2.7.9.1.1.1.1.1 每月1号…` | strip when the prefix has ≥4 dot segments |
| List restart | ①②③ lists in table cells run 160, 161, 162 | give each functional group its own `numId` so each starts at 1 |

When a chapter title is missing entirely, insert it with the **exact formatting of its
siblings** — copy the run properties (style name, size, color, font) from a neighbouring
chapter heading rather than picking a built-in style, or it will not match the template.

## 3. Two different numbering systems — do not confuse them

1. **Literal text numbers** (headings, most Chinese technical docs). Detection: regex
   `^(\d+(?:\.\d+)*)[\s、.．]` on the paragraph text. Repair = rewrite the run.
2. **Word list numbering** (`w:numPr` with `numId` + `ilvl`). Repair = edit
   `numbering.xml` or reassign `numId`.

A paragraph showing *both* is double-numbered — the classic source of `1. 1.` and
`4.1.2.1 4.1.2` artifacts. Count them: `numbering_prefix and numPr both present`.

## 4. Reading `numbering.xml`

```python
elem = d.part.numbering_part.element
# w:num -> w:abstractNumId -> w:abstractNum/w:lvl:
#   w:numFmt (decimal | bullet | ...), w:lvlText, w:start
# w:num/w:lvlOverride/w:startOverride overrides the abstract start value
```

A list only restarts at 1 if **neither** `w:start` nor `startOverride` says otherwise —
check both. Bullet levels (`numFmt=bullet`) are decorative and must be left alone; only
decimal levels need restart logic.

**A list that prints `1. 1. 1.`** is usually not a restart bug: each paragraph was given
its own `numId`, so every item renders its own "1". Detect by grouping consecutive
numbered paragraphs into a run and checking whether `numId` is uniform across the group.
Fix by pointing every paragraph of one list at a single `numId`.

## 5. Iterate in passes, verify the same way every pass

1. Back up first: `cp v1.1.docx /tmp/bak_v11.docx`.
2. One pass = one concern (chapter numbers / depth alignment / junk prefixes / table lists).
3. After every pass run the **same** audit script and diff against the previous report.

Hard gate — structure must be conserved (a numbering fix must never touch content):

```python
(len(src.paragraphs), len(src.tables), len(src.inline_shapes)) ==
(len(dst.paragraphs), len(dst.tables), len(dst.inline_shapes))
```
Paragraphs are allowed to grow only by the headings you deliberately inserted; tables and
images must be exactly equal.

Media check without opening Word:

```bash
unzip -Z1 a.docx | sort > a.txt; unzip -Z1 b.docx | sort > b.txt
comm -23 a.txt b.txt   # only in source
comm -13 a.txt b.txt   # only in output
```

`python-docx`'s rezip drops **directory entries** (`word/media/`, `_rels/`) and shrinks file
size by recompressing — that is expected, not data loss. Real files (media, embeddings,
styles, numbering) must match one for one.

## 6. Visual sanity check when there is no PDF renderer

`qlmanage -t -s 1400 -o /tmp/thumb file.docx` writes a page-1 PNG thumbnail
(macOS). Enough to confirm the package opens and the opening headings/numbering render
cleanly; inspect it with `vision_analyze`. Do not claim a full layout review from a
thumbnail — say what was checked.

## 7. Deliver

- Output as a **new version** (`v1.1`), never overwriting the source; the user's convention
  is a version number in the filename plus one in the document header.
- Ship a short `…_编号修订说明.md` next to it: a table of the original problems, what was
  changed (with counts, e.g. "11→4 共 373 条"), the resulting chapter skeleton, and the
  structural conservation numbers. This is what the user forwards to reviewers.
- If a functional chapter still carries 6–8 level numbers, offer — do not perform — a
  second pass that caps numbering at 4 levels and turns deeper items into bold unnumbered
  sub-heads.

## Pitfalls

- Judge numbering from `outlineLvl` + regex on text, **not** from Word's visible TOC; many
  of these documents have no TOC field at all, so "update the field" is not the fix.
- Never strip prefixes with a loose pattern like `^\d+[.、]` — that deletes legitimate
  `1.` / `2.1` numbering. Require ≥4 dot segments before stripping.
- Inserted headings need the sibling's `Normal` + explicit run font/size/color, not
  `Heading 1`; the template's chapter titles are usually body paragraphs with
  `outlineLvl=0` and hand-set formatting.
- Re-run the map lookup by **exact old number + level**, not by text: identical section
  titles legitimately repeat across chapters.
- Body-prefix cleanup must treat `outlineLvl >= 9` as body:
  `body = e is None or int(e.get(qn("w:val"))) >= 9`. Pasted body paragraphs carry level 9
  (not a missing `pPr`), so a check for `e is None` alone skips every junk prefix — the
  audit report comes back clean while the text is still dirty.
