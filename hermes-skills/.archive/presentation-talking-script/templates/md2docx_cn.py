#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Markdown → Word (.docx) 中文文档转换脚本（汇报话术用）
用法: python3 md2docx_cn.py input.md output.docx
- A4 页面，边距 2.2cm，微软雅黑 11pt
- 标题分级配色: H1 深蓝 #1F3B73 / H2 蓝 #2E5A9E / H3 黑
- 支持: # 标题、- 列表（含 **粗体** 前缀）、| 表格行（转文本）、--- 分隔线、> 引用
"""
import re
import sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor

def convert(src: str, out: str):
    with open(src, encoding="utf-8") as f:
        lines = f.read().split("\n")
    doc = Document()
    for section in doc.sections:
        section.page_width = Cm(21); section.page_height = Cm(29.7)
        section.left_margin = Cm(2.2); section.right_margin = Cm(2.2)
        section.top_margin = Cm(2.2); section.bottom_margin = Cm(2.2)
    style = doc.styles["Normal"]
    style.font.name = "Microsoft YaHei"; style.font.size = Pt(11)
    style._element.rPr.rFonts.set("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia", "微软雅黑")

    def set_font(run, size=11, bold=False, color=None):
        run.font.size = Pt(size); run.font.bold = bold; run.font.name = "Microsoft YaHei"
        run._element.rPr.rFonts.set("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia", "微软雅黑")
        if color: run.font.color.rgb = RGBColor(*color)

    def add_heading(text, level):
        sizes = {1: 18, 2: 15, 3: 13}
        colors = {1: (0x1F,0x3B,0x73), 2: (0x2E,0x5A,0x9E), 3: (0x33,0x33,0x33)}
        p = doc.add_paragraph()
        r = p.add_run(text); set_font(r, sizes.get(level,12), True, colors.get(level,(0,0,0)))
        p.paragraph_format.space_before = Pt(14 if level==1 else 10); p.paragraph_format.space_after = Pt(6)

    def add_para(text, size=11, bold=False, color=None, left=0.0, space_after=6):
        p = doc.add_paragraph()
        if left: p.paragraph_format.left_indent = Cm(left)
        p.paragraph_format.space_after = Pt(space_after)
        r = p.add_run(text); set_font(r, size, bold, color)
        return p

    in_code = False
    for line in lines:
        if line.startswith("```"):
            in_code = not in_code; continue
        if in_code:
            add_para(line, size=10); continue
        m = re.match(r"^(#{1,3})\s+(.*)", line)
        if m: add_heading(m.group(2), len(m.group(1))); continue
        m = re.match(r"^(\s*)[-*]\s+(.*)", line)
        if m:
            indent = len(m.group(1)); text = m.group(2)
            bm = re.match(r"^\*\*(.+?)\*\*\s*[:：]?\s*(.*)", text)
            p = doc.add_paragraph(); p.paragraph_format.left_indent = Cm(0.6 + indent*0.3)
            p.paragraph_format.space_after = Pt(3)
            if bm:
                r1 = p.add_run(bm.group(1) + "："); set_font(r1)
                if bm.group(2): set_font(p.add_run(bm.group(2)))
            else:
                set_font(p.add_run(text))
            continue
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if not all(c in ("-","---","") for c in cells):
                add_para("　".join(cells), size=10.5, space_after=3)
            continue
        if line.strip() in ("---","***"):
            p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(6); p.paragraph_format.space_after = Pt(6)
            r = p.add_run("─" * 30); set_font(r, 8, color=(0x99,0x99,0x99)); continue
        if line.strip():
            if line.strip().startswith("**") and line.strip().endswith("**"):
                add_para(line.strip().strip("**"), bold=True, space_after=4)
            else:
                add_para(line)
    doc.save(out)
    print("saved:", out)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: python3 md2docx_cn.py input.md output.docx"); sys.exit(1)
    convert(sys.argv[1], sys.argv[2])
