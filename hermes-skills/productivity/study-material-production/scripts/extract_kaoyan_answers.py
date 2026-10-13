# -*- coding: utf-8 -*-
"""从结构化考研英语真题 md 中抽取官方答案，输出 JSON（供每日练习卷「先取答案、再写卷」用）。

适用源：LIziak112/structured-kaoyan-english 的 data/<年>-<卷>/<年>-<卷>.md（`-2` = 英语二）。
该源特征：完形正文每空是 `{{n}}` 占位；答案行独立成行，形如 `> **答案**：A`；每题另带 <details> 解析与段落级译文。

用法：
    # 1) 抓源（可选）：下载 data/<year>-<paper>/<year>-<paper>.md 到 ./kaoyan_raw/
    python3 extract_kaoyan_answers.py --fetch 2016 2
    # 2) 抽答案（完形 20 + Section II Part A 各 Text 5）
    python3 extract_kaoyan_answers.py kaoyan_raw/2016-2.md
    python3 extract_kaoyan_answers.py kaoyan_raw/2015-2.md --out /tmp/key_2015.json --strict

输出结构：
    {"file": ..., "sections": {"Section I": [20 个字母], "Section II": [...], "Text 1": [5 个], ...},
     "original_question_numbers": {"Text 3": [31,32,33,34,35]}, "warnings": [...]}
说明：Section II 的扁平列表可能混入 Part B（新题型）的答案，逐篇取用一律看 `Text N` 键。
"""
import argparse
import json
import os
import re
import sys
import urllib.request

RAW = "https://raw.githubusercontent.com/LIziak112/structured-kaoyan-english/main/data/{y}-{p}/{y}-{p}.md"

# 只认「独立成行的答案行」，避免吃到解析正文里引用的字母
ANS_PATTERNS = [
    re.compile(r"^\s*>\s*\*\*答案\*\*\s*[:：]\s*\**([A-Da-d])\**\s*$"),
    re.compile(r"^\s*\*\*答案\*\*\s*[:：]\s*\**([A-Da-d])\**\s*$"),
    re.compile(r"^\s*(?:>|\*)?\s*(?:【答案】|答案)\s*[:：]\s*\**([A-Da-d])\**\s*$"),
]
HEAD_SECTION = re.compile(r"^#{1,6}\s*Section\s+([IVX]+)", re.I)
HEAD_TEXT = re.compile(r"^#{1,6}\s*(?:Text|Passage)\s*(\d+)", re.I)


def fetch(year, paper, outdir="kaoyan_raw"):
    os.makedirs(outdir, exist_ok=True)
    url = RAW.format(y=year, p=paper)
    path = os.path.join(outdir, "%s-%s.md" % (year, paper))
    with urllib.request.urlopen(url, timeout=60) as r:
        data = r.read()
    with open(path, "wb") as f:
        f.write(data)
    print("downloaded %s -> %s (%d bytes)" % (url, path, len(data)), file=sys.stderr)
    return path


def scan(lines, lo, hi):
    out = []
    for i in range(lo, hi):
        for rx in ANS_PATTERNS:
            m = rx.match(lines[i])
            if m:
                out.append((i, m.group(1).upper()))
                break
    return out


def sections(lines):
    marks = [("Section " + m.group(1), i)
             for i, l in enumerate(lines) for m in [HEAD_SECTION.match(l)] if m]
    marks.append(("EOF", len(lines)))
    return [(marks[k][0], marks[k][1], marks[k + 1][1]) for k in range(len(marks) - 1)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", help="已下载的真题 md 路径")
    ap.add_argument("--fetch", nargs=2, metavar=("YEAR", "PAPER"), help="下载 raw 源，如 --fetch 2016 2")
    ap.add_argument("--out", help="同时写入 JSON 文件")
    ap.add_argument("--strict", action="store_true", help="数量对不上就返回非 0")
    a = ap.parse_args()

    path = fetch(a.fetch[0], a.fetch[1]) if a.fetch else a.path
    if not path:
        ap.error("给一个 md 路径，或用 --fetch YEAR PAPER")
    lines = open(path, encoding="utf-8").read().split("\n")

    result = {"file": path, "sections": {}, "original_question_numbers": {}}
    problems = []
    for name, lo, hi in sections(lines):
        letters = [x[1] for x in scan(lines, lo, hi)]
        if not letters:
            continue
        result["sections"][name] = letters
        if name.upper().endswith("II"):
            tm = [((HEAD_TEXT.match(l).group(1)), i)
                  for i, l in enumerate(lines[lo:hi], lo) if HEAD_TEXT.match(l)]
            tm.append(("EOF", hi))
            for k in range(len(tm) - 1):
                t, s, e = tm[k][0], tm[k][1], tm[k + 1][1]
                tl = [x[1] for x in scan(lines, s, e)]
                key = "Text %s" % t
                result["sections"][key] = tl
                if tl:
                    first = 21 + 5 * (int(t) - 1)  # 英语二 Part A 原卷题号：Text1=21-25 …
                    result["original_question_numbers"][key] = [first + j for j in range(len(tl))]
                if len(tl) != 5:
                    problems.append("%s 抽到 %d 个答案（每篇应为 5）" % (key, len(tl)))

    if len(result["sections"].get("Section I", [])) != 20:
        problems.append("Section I 抽到 %d 个答案（完形应为 20）" % len(result["sections"].get("Section I", [])))
    result["warnings"] = problems

    text = json.dumps(result, ensure_ascii=False, indent=2)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print("wrote %s" % a.out, file=sys.stderr)
    print(text)
    if problems:
        print("PROBLEMS: " + "；".join(problems), file=sys.stderr)
        if a.strict:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
