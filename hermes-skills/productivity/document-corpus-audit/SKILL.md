---
name: document-corpus-audit
description: "Audit a whole folder of docs: inventory, gaps, index."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Documents, PDF, Analysis, Inventory, Index]
    related_skills: [ocr-and-documents, chinese-enterprise-document-writing, xlsx]
---

# Document Corpus Audit

Use this when the user points at **a folder of many documents** — "这是我们的XX操作手册，帮我分析下", "分析下这堆资料", "这套文档怎么样" — and wants an analysis of the corpus. For pulling text out of a single file, use `ocr-and-documents`; this skill is about the whole set: what is in it, what is broken, what is missing, what must not be shared.

## Fixed deliverable: two files, always

1. **分析报告 md** — one-line conclusion first, then the data panorama, then findings.
2. **索引 xlsx** — one row per document, filterable, so the user can slice the corpus afterwards.

Write both to `~/Documents/work/smardaten/smardatencorp/99-软件工厂/98 hermes/` (this user's fixed output dir) and deliver with `MEDIA:` paths. Name them `<对象>_分析报告_<YYYYMMDD>.md` / `<对象>_索引_<YYYYMMDD>.xlsx`.

Report section order that works:
一句话结论 → 数据全景(总量表 + 按一级章节分布) → 来源判定 → 内容地图(按实际用法重排，非目录顺序) → 问题清单(带数字) → 能用/不能用/值钱在哪 → 后续建议(列 3-5 个可选项让用户挑一件).

Index columns: 序号/一级章节/二级/三级/文件名/页数/大小MB/外链数/导出缺失处/敏感标记/首页摘要/相对路径, with `freeze_panes='A2'` and an `auto_filter`. `scripts/corpus_audit.py` emits exactly this.

## Procedure

1. **Count before concluding.** Never reason from the attached folder tree — it is truncated and shows only a prefix. `os.walk` the real directory into `manifest.json` (rel path, size, md5) first.
2. **Extract text once, cache it.** Run `cd /tmp && python3 <skill_dir>/scripts/corpus_audit.py <ROOT> <OUT_DIR>`. It stages `manifest.json` → `text.json` (per-file pages + full text) → stats → xlsx, skipping any stage whose cache already exists. Re-parsing a 690MB / 2900-page corpus on every analysis pass is what kills these tasks: parse once, then write cheap analysis scripts against the JSON.
3. **Provenance**: count the domain that dominates the text plus footer timestamps (`20\d\d[/-]\d+/\d+ \d+:\d+`). That tells you whether the corpus is a native file set or a **print/export of an online knowledge base**, and which date it was frozen at. See `references/exported-docs-provenance.md`.
4. **Export loss**: count placeholder strings. Online-doc exports silently drop embedded cards and attachments, so a page that reads normally may have lost its entire payload.
5. **Duplicates**: group by md5 — the same document often ships in two chapters.
6. **Structure gaps**: extract the leading number from folder/file names per parent directory and diff against `range(max+1)`. This finds missing parts and junk names that the numbering alone hides.
7. **Coverage balance**: aggregate files / pages / MB / chars per top-level section. The heavy section shows where the vendor invests; the thin one is where delivery work has no ground truth — and that gap is what this user acts on.
8. **Sensitivity**: flag documents containing 报价/价格/服务条款/授权范围/商务. Name the file and the field, and state "整包禁止外发" when a corpus mixes product docs with commercial terms.
9. End with 3-5 concrete next-step options (新人上手包 / FAQ 库 / 离线全文检索 / 给上游的文档缺陷清单) and let the user pick one; the next session then starts with direction.

## Rules and pitfalls

- **Numbers, not adjectives.** Every claim carries verifiable counts (N 份 / N 页 / N 处 / N 条链接). "内容比较丰富" is worthless; "6-AppStudio 占 48%，而部署运维只有 3 份 FAQ" is the finding.
- **No thousand separators** in this user's documents or chat (write 2908, not 2,908).
- **Re-order the content map by how the audience will use it** (产品底座 / 上手路径 / 构建主体 / 生态案例 / 场景答疑), not by the vendor's chapter order. The audit exists to find what is usable, not to restate the directory tree.
- **pymupdf (`import pymupdf`, alias `fitz`) is the extractor** for text-layer PDFs; do not gate the run on `pdftotext` being installed. Wrap each file in try/except and record the error on the row — one encrypted or corrupt PDF must not abort a 170-file scan.
- **Scan in stages that each persist to JSON** and print progress every ~20 files. One long scan that dies at file 140 loses everything.
- Write scan scripts to `/tmp/<name>.py` and run `cd /tmp && python3 <name>.py`; long inline commands carrying absolute paths trip this environment's terminal guard.
- Deliver the findings the user can act on. Bundled commercial terms and offline-broken documents are the two that change how the corpus may be used.

## Supporting files

- `scripts/corpus_audit.py` — parameterized end-to-end audit (manifest → text cache → dupes/provenance/coverage/gap stats → xlsx index). Run it first; hand-write extra probes only for questions it does not answer.
- `references/exported-docs-provenance.md` — how to recognize online-knowledge-base PDF exports, and what their failure modes imply.
