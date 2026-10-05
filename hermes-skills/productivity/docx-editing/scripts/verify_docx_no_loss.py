#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重建 docx 后校验“零内容丢失”。

用法:
    PYTHONPATH= python3 verify_docx_no_loss.py <原文档.docx> <新文档.docx>

原理: 把原文档的正文段落 + 所有表格单元格按句切分（>=12 字），规范化
（去空白/箭头/框线字符）后，在新文档的全文本（段落 + 所有表格单元格）里
做子串查找。找不到的句段 = 疑似丢失。

白名单（自动不算丢失，EXPECTED）:
    - 导出后只剩 “点击图片可查看完整电子表格” 的嵌入表占位句
    - 与封面重复的原文标题行
其余任何一条都要人工确认。退出码非 0 = 有非预期缺失，不要交付。
"""
import re
import sys

from docx import Document

NOISE = re.compile(r'[\s\u3000→←↓↑│─┌┐└┘├┤┬┴┼▶►·]+')
SPLIT = re.compile(r'[。；;!?！？\n]')
MIN_LEN = 12
EXPECTED = ('点击图片可查看完整电子表格', '点击图片查看完整电子表格', '电子表格下载失败')


def norm(s):
    return NOISE.sub('', s)


def full_text(path):
    """文档全文本（段落 + 所有表格单元格，含嵌套）"""
    d = Document(path)
    parts = [p.text for p in d.paragraphs]
    for t in d.tables:
        for row in t.rows:
            for cell in row.cells:
                parts.append(cell.text)
    return norm(''.join(parts))


def fragments(path):
    """待校验句段：正文段落 + 表格单元格内容（1×1 框是重点）"""
    d = Document(path)
    texts = [p.text for p in d.paragraphs]
    for t in d.tables:
        for row in t.rows:
            for cell in row.cells:
                texts.append(cell.text)
    for txt in texts:
        for frag in SPLIT.split(txt):
            frag = frag.strip()
            if len(frag) >= MIN_LEN:
                yield frag


def main(src, dst):
    new = full_text(dst)
    checked = 0
    missing = []
    for frag in fragments(src):
        checked += 1
        key = norm(frag)
        if not key or key in new:
            continue
        missing.append(frag)
    unexpected = [m for m in missing if not any(e in m for e in EXPECTED)]
    print('source sentences checked: %d' % checked)
    print('not found: %d  (unexpected: %d)' % (len(missing), len(unexpected)))
    for m in missing:
        flag = 'X(white)' if any(e in m for e in EXPECTED) else '!! LOSS'
        print('  %s | %s' % (flag, m[:80]))
    if unexpected:
        print('\nFAIL: %d sentence(s) not found in the rebuilt docx.' % len(unexpected))
        return 1
    print('\nOK: no content lost.')
    return 0


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
