#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""导出 Holographic 事实库（~/.hermes/memory_store.db）为可读 markdown，并推送到记忆 git 仓库。

背景：memory_store.db 被 hermes-memory 仓库的 .gitignore 排除，事实库因此没有任何 git 备份。
     本脚本把它导出成脱敏的可读 md 入库，是事实库唯一的外部备份。

用法：
    PYTHONPATH= python3 ~/.hermes/scripts/export_holographic_facts.py

推荐挂 cron（no_agent 纯脚本，零 token；无变化静默不投递）：
    cronjob(action='create', no_agent=True, schedule='every monday 9am',
            script='export_holographic_facts.py')

行为：无变化 → exit 0 无输出；有变化 → commit + pull --rebase + push 并打印一行摘要。

注：与原脚本同逻辑；列名改为 PRAGMA 自适应，本地库结构微调不会直接崩。
"""
import datetime
import os
import re
import sqlite3
import subprocess
import sys

DB = os.path.expanduser('~/.hermes/memory_store.db')
REPO = os.path.expanduser('~/Documents/work/jiayang/hermes-memory')
OUT_NAME = 'holographic-facts.md'
OUT = os.path.join(REPO, OUT_NAME)

CATS = {'user_pref': '用户偏好', 'project': '项目', 'tool': '工具', 'general': '通用'}

# 脱敏：①上下文关键词后面的值 ②sk- 密钥 ③appid 形态 ④长 hex
KEY_CTX = re.compile(
    r'(密码|口令|password|passwd|appkey|appsecret|appid|secret|token|api[_-]?key)'
    r'\s*[:：=]\s*([^\s，。；、)（）"]+)', re.I)
PATTERNS = [
    (re.compile(r'\bsk-[A-Za-z0-9_\-]{6,}'), '[REDACTED-KEY]'),
    (re.compile(r'\b[A-Z]{2}\d{8}[A-Z0-9]{4,}\b'), '[REDACTED-APPID]'),
    (re.compile(r'\b[0-9a-f]{16,}\b', re.I), '[REDACTED]'),
]


def redact(s):
    s = KEY_CTX.sub(lambda m: m.group(1) + '：[REDACTED]', s)
    for rx, rep in PATTERNS:
        s = rx.sub(rep, s)
    return s


def _cols(con, table):
    try:
        return [r[1] for r in con.execute('PRAGMA table_info(%s)' % table)]
    except sqlite3.Error:
        return []


def _pick(cs, *names):
    for n in names:
        if n in cs:
            return n
    return None


def collect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    try:
        fc = _cols(con, 'facts')
        c_id = _pick(fc, 'fact_id', 'id')
        c_txt = _pick(fc, 'fact', 'content', 'text', 'fact_text', 'body')
        c_cat = _pick(fc, 'category', 'cat', 'type')
        c_date = _pick(fc, 'created_at', 'created', 'timestamp')
        if not c_txt:
            raise SystemExit('facts 表里找不到内容列，请先看 PRAGMA table_info(facts)')
        sel = ', '.join(c for c in (c_id, c_txt, c_cat, c_date) if c)
        facts = con.execute('SELECT %s FROM facts' % sel).fetchall()

        entities = []
        ec = _cols(con, 'entities')
        e_id = _pick(ec, 'entity_id', 'id')
        e_nm = _pick(ec, 'name', 'entity_name')
        e_ty = _pick(ec, 'entity_type', 'type', 'kind')
        if e_nm:
            esel = ', '.join(c for c in (e_id, e_nm, e_ty) if c)
            entities = con.execute('SELECT %s FROM entities' % esel).fetchall()
        return facts, entities, (c_id, c_txt, c_cat, c_date), (e_id, e_nm, e_ty)
    finally:
        con.close()


def build_md(facts, entities, fcols, ecols):
    c_id, c_txt, c_cat, c_date = fcols
    e_id, e_nm, e_ty = ecols
    today = datetime.date.today().isoformat()

    buckets = {}
    for r in facts:
        cat = (r[c_cat] if c_cat else None) or 'general'
        buckets.setdefault(CATS.get(cat, cat), []).append(r)

    out = ['# Holographic 事实库导出', '',
           '**来源**：`~/.hermes/memory_store.db`（SQLite，被 .gitignore 排除，本文件是可读备份）',
           '**导出时间**：%s' % today,
           '**条目数**：%d' % len(facts), '',
           '> 密钥/appid/token/密码类值已脱敏为 `[REDACTED]`，完整值只在本地库。', '']

    for cat in sorted(buckets):
        out.append('## %s' % cat)
        for r in buckets[cat]:
            fid = ('**[#%s]** ' % r[c_id]) if c_id else ''
            date = (' _(%s)_' % str(r[c_date])[:10]) if c_date and r[c_date] else ''
            out.append('- %s%s%s' % (fid, redact(str(r[c_txt]).replace('\n', ' ')), date))
        out.append('')

    if entities:
        out.append('## 实体（entities）')
        for e in entities:
            name = e[e_nm]
            eid = ('#%s ' % e[e_id]) if e_id else ''
            ty = ('（%s）' % e[e_ty]) if e_ty and e[e_ty] else ''
            out.append('- %s%s%s' % (eid, redact(str(name)), ty))
        out.append('')
    return '\n'.join(out)


def main():
    if not os.path.exists(DB):
        sys.stderr.write('事实库不存在：%s\n' % DB)
        return 1
    facts, entities, fcols, ecols = collect()
    md = build_md(facts, entities, fcols, ecols)

    old = ''
    if os.path.exists(OUT):
        with open(OUT, encoding='utf-8') as f:
            old = f.read()
    # 导出时间会每天变，比较时忽略它，避免无意义提交
    def norm(s):
        return re.sub(r'\*\*导出时间\*\*：\S+', '', s)
    if norm(md) == norm(old):
        return 0  # 无变化：静默

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(md)

    def git(*args):
        return subprocess.run(['git'] + list(args), cwd=REPO,
                              capture_output=True, text=True)

    today = datetime.date.today().isoformat()
    git('add', OUT_NAME)
    git('commit', '-m', '记忆导出：Holographic 事实库可读备份 %s' % today)
    git('pull', '--rebase')
    p = git('push')
    if p.returncode != 0:
        sys.stderr.write('push 失败：%s\n' % (p.stderr or p.stdout or '')[:400])
        return 1
    print('Holographic 事实库已导出并推送：%d 条事实 + %d 个实体 → %s'
          % (len(facts), len(entities), OUT_NAME))
    return 0


if __name__ == '__main__':
    sys.exit(main())
