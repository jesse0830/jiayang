#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""逐人逐月评级抽取：4~9 月行为绩效考评 xlsx -> 一个人一行的评级表。

用法:
  PYTHONPATH= /usr/bin/python3 perf_window_parse.py [年目录] [输出文件]
默认年目录: 99-软件工厂/02 绩效/2026年
默认输出:   ~/.hermes/cache/scratch/perf_window_parse.txt

设计要点（都是踩坑换来的，改脚本前先读）:
  1) 不硬编码列号：按关键字「工号/姓名/三级部门/绩效结果」各自在前 6 行里独立定位。
     4~8 月的表头是三行，姓名在第 1 行、绩效结果在第 3 行；9 月是单行表头。
     要求关键字同行出现会全部匹配失败（静默返回空）。
  2) 月份从文件名推（正则 N月），不靠文件名前缀猜；按 realpath 去重。
  3) 同月多文件：先根目录合并版，再用部门拆分表补空值；冲突只记录不静默覆盖。
  4) 一个 workbook 可能多 sheet（自评汇总无评级、5月表混在6月文件里），按「有评级行数最多」选。
  5) 错误值 #REF! 等一律按缺失处理，绝不当等级。
"""
import glob
import os
import re
import sys

import openpyxl

BASE = sys.argv[1] if len(sys.argv) > 1 else (
    "/Users/jesseyoung/Documents/work/smardaten/smardatenCorp/99-软件工厂/02 绩效/2026年"
)
OUT = sys.argv[2] if len(sys.argv) > 2 else "/Users/jesseyoung/.hermes/cache/scratch/perf_window_parse.txt"

BAD = {"#REF!", "#N/A", "#VALUE!", "#DIV/0!", "#NAME?", "#NULL!", "#NUM!"}
KEYS = ["工号", "姓名", "三级部门", "绩效结果"]
SPLIT_TAG = re.compile(r"(-DE|-IE|-All|-all|-配置开发部|配置开发部|集成验证部|技术支撑部|\(客户成功部\))$")
MONTH_RE = re.compile(r"(\d{1,2})\s*月")


def month_of(path):
    m = MONTH_RE.search(os.path.basename(path))
    return int(m.group(1)) if m else None


def find_files(base):
    """{month: [paths]}；合并版在前，拆分表在后。"""
    cands = []
    for pat in ("**/*行为绩效考评*.xlsx", "**/*考评表*.xlsx"):
        cands += glob.glob(os.path.join(base, pat), recursive=True)
    seen, out = set(), {}
    for p in sorted(cands):
        base_name = os.path.basename(p)
        if base_name.startswith("~$") or "备份" in base_name:
            continue
        rp = os.path.realpath(p)
        if rp in seen:
            continue
        seen.add(rp)
        m = month_of(p)
        if m is None:
            continue
        out.setdefault(m, []).append(p)
    for m in out:
        out[m].sort(key=lambda p: (bool(SPLIT_TAG.search(os.path.splitext(os.path.basename(p))[0])), p))
    return out


def parse_sheet(ws):
    rows = list(ws.iter_rows(values_only=True))
    col, grade_row = {}, None
    for key in KEYS:
        for i, r in enumerate(rows[:6]):
            cells = [str(c).strip() if c is not None else "" for c in r]
            if key in cells:
                col[key] = cells.index(key)
                if key == "绩效结果":
                    grade_row = i
                break
    if "姓名" not in col or "绩效结果" not in col:
        return None
    recs = []
    for r in rows[(grade_row if grade_row is not None else 0) + 1:]:
        if len(r) <= max(col["姓名"], col["绩效结果"]):
            continue
        raw_name = r[col["姓名"]]
        name = str(raw_name).strip() if raw_name is not None else ""
        if not name or name in ("姓名", "序号"):
            continue
        g = r[col["绩效结果"]]
        g = str(g).strip() if g is not None else ""
        if g in BAD:
            g = ""
        if g not in {"A", "B", "C"}:
            g = ""
        dept = ""
        if "三级部门" in col and r[col["三级部门"]] is not None:
            dept = str(r[col["三级部门"]]).strip()
        emp = ""
        if "工号" in col and r[col["工号"]] is not None:
            emp = str(r[col["工号"]]).strip()
        recs.append({"name": name, "emp": emp, "dept": dept, "grade": g})
    return recs


def load_month(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    best = None
    for ws in wb.worksheets:
        recs = parse_sheet(ws)
        if not recs:
            continue
        n = sum(1 for r in recs if r["grade"])
        if best is None or n > best[0]:
            best = (n, ws.title, recs)
    return best


def main():
    files = find_files(BASE)
    log, data = [], {}
    for m in sorted(files):
        for f in files[m]:
            res = load_month(f)
            if not res:
                log.append("M%d SKIP(表头未识别) %s" % (m, os.path.basename(f)))
                continue
            n, sheet, recs = res
            log.append("M%d OK %s sheet=%s rows=%d graded=%d" % (m, os.path.basename(f), sheet, len(recs), n))
            book = data.setdefault(m, {})
            for r in recs:
                k = r["name"]
                cur = book.get(k)
                if cur is None:
                    book[k] = dict(r)
                    continue
                if r["grade"] and not cur["grade"]:
                    cur["grade"] = r["grade"]
                    log.append("   FILL M%d %s <- %s" % (m, k, r["grade"]))
                elif r["grade"] and cur["grade"] and r["grade"] != cur["grade"]:
                    log.append("   CONFLICT M%d %s: %s vs %s (keep %s)" % (m, k, cur["grade"], r["grade"], cur["grade"]))
                for fld in ("dept", "emp"):
                    if r[fld] and not cur[fld]:
                        cur[fld] = r[fld]

    months = sorted(data)
    meta = {}
    for m in months:
        for k, v in data[m].items():
            e = meta.setdefault(k, {"dept": "", "emp": ""})
            for fld in ("dept", "emp"):
                if v[fld] and not e[fld]:
                    e[fld] = v[fld]

    rows_out = []
    for k, mt in meta.items():
        gs = [data.get(m, {}).get(k, {}).get("grade", "") for m in months]
        rows_out.append({
            "name": k, "dept": mt["dept"], "emp": mt["emp"], "g": gs,
            "A": sum(1 for g in gs if g == "A"),
            "C": sum(1 for g in gs if g == "C"),
            "valid": sum(1 for g in gs if g),
        })
    rows_out.sort(key=lambda x: (-x["A"], x["C"], x["name"]))

    hdr = "|%s|%s|%s|%s|A|C|有效月" % ("姓名", "三级部门", "工号", "|".join("%d月" % m for m in months))
    with open(OUT, "w") as fh:
        print("== PARSE LOG ==", file=fh)
        for line in log:
            print(line, file=fh)
        print("\n== 明细 %d 人 ==" % len(rows_out), file=fh)
        print(hdr, file=fh)
        for r in rows_out:
            print("|".join([r["name"], r["dept"], r["emp"]] + [g or "-" for g in r["g"]]
                           + [str(r["A"]), str(r["C"]), str(r["valid"])]), file=fh)
        print("\n== A>=3 且 C=0 ==", file=fh)
        for r in rows_out:
            if r["A"] >= 3 and r["C"] == 0:
                print("%s|%s|%s" % (r["name"], r["dept"], "/".join(g or "-" for g in r["g"])), file=fh)
        print("\n== A=2 且 C=0 ==", file=fh)
        for r in rows_out:
            if r["A"] == 2 and r["C"] == 0:
                print("%s|%s|%s" % (r["name"], r["dept"], "/".join(g or "-" for g in r["g"])), file=fh)
    print("written %s (%d 人, 月份=%s)" % (OUT, len(rows_out), months))


if __name__ == "__main__":
    main()
