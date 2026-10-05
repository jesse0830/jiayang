# Recognizing exported docs and what their failure modes imply

## Signal -> verdict

| Signal in extracted text | What it means | What to tell the user |
|---|---|---|
| One domain repeated hundreds of times (`yuque.com`, `feishu.cn`, `confluence`, `notion.site`) | The corpus is a **browser print / export of an online knowledge base**, not a native document set | The files are a frozen snapshot, not the source of truth |
| Repeated footer stamp like `2026/7/9 14:36 <url>` | Exact export timestamp; two distinct stamps = two export batches | Gives the snapshot age and whether the corpus was frozen in one pass |
| `此处为语雀内容卡片，点击链接查看` and siblings | Online-embedded cards / attachments / flash blocks **did not survive the export** — the section reads normally but its payload is gone | Those pages are blank offline. Count broken occurrences per document before calling the corpus usable |
| Placeholder text clustered in a few documents | Those are the least usable files in the set, often the most needed ones (installation/ops FAQ, scenario intros are typical victims) | Flag them explicitly as needing manual rebuild |
| "相关课程" / video-link blocks | Content lives on a video platform, not in the PDF | Offline / intranet / air-gapped delivery loses it |
| 价格, 服务条款, 授权范围, 元/套 inside otherwise technical docs | Product documentation and **commercial terms were exported together** | Do not distribute the folder as a whole; name the file and the field |
| Version-log chapter present (R5C30 → R6C40 …) | The newest entry bounds the snapshot | Docs are as new as the latest version log; anything released after is undocumented |

## Standard implications to state

1. **Offline usability** — a knowledge-base export is unusable exactly where it matters most: customer sites, intranet, 信创 environments without internet access. Report the count of broken pages, not "some content may be missing".
2. **Version drift** — pair the latest version-log entry with the export date, state how far behind the docs are, and recommend confirming the current release before quoting feature behaviour to a customer.
3. **Redistribution** — check for commercial blocks before recommending the folder for training or customer use.

## Structural defects worth hunting in any vendor doc set

- Leading numbers in names form a sequence per directory: diff against `range(max+1)` to find missing parts (a `3-场景案例` absent under one module while present under its siblings) and to catch the numbering scheme itself.
- Non-numbered directories sitting inside a numbered scheme (`新建文件夹`) usually contain a real module whose name was lost on export. Open it and identify the module instead of trusting the name.
- Identical md5 across chapters means the same content was exported twice; report the redundant MB rather than listing both copies as content.
- Sections whose page/MB/char totals are tiny compared with their siblings (deployment, operations, acceptance) are where a delivery organisation has no documented ground truth — usually the finding the user acts on.
