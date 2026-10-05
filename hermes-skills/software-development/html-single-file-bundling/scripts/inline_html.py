#!/usr/bin/env python3
"""把 HTML 的外部依赖内联，产出可双击打开的单文件版本。

用法:
    PYTHONPATH= python3 inline_html.py <index.html> [--out OUT] [--no-backup]

做四件事:
  1. 盘点外部依赖: <script src> / <link href> / CSS @import / url() / fetch-XHR 目标 / <img src>
  2. 本地文件就地内联: JS -> <script>(转义 </script), CSS -> <style>, 媒体 -> data URI
  3. 单独列出「仍需要联网」的依赖(CDN 等), 不自动下载, 由你决定
  4. 备份原文件为 <name>.bak-YYYYMMDD.html

⚠️ 只做静态改写。正确性必须用浏览器在 file:// 空目录实测确认(见 SKILL.md 第三步)。
"""
import argparse
import base64
import datetime
import mimetypes
import pathlib
import re
import sys

LINK_RE = re.compile(r'<link\b[^>]*rel=["\']?stylesheet["\']?[^>]*>', re.I)
HREF_RE = re.compile(r'href=["\']([^"\']+)["\']', re.I)
SCRIPT_SRC_RE = re.compile(r'<script\b[^>]*\bsrc=["\']([^"\']+)["\'][^>]*>\s*</script\s*>', re.I)
IMG_SRC_RE = re.compile(r'(<(?:img|source)\b[^>]*?\bsrc=["\'])([^"\']+)(["\'])')
CSS_IMPORT_RE = re.compile(r'@import\s+(?:url\()?["\']([^"\')]+)["\']\)?\s*;')
CSS_URL_RE = re.compile(r'url\(\s*["\']?([^"\')]+)["\']?\s*\)')
FETCH_RE = re.compile(r'\b(?:fetch\(|XMLHttpRequest|new\s+Worker\(|import\s*\()')

SKIP_PREFIX = ('http://', 'https://', '//', 'data:', 'blob:', 'mailto:', '#', 'javascript:')


def is_local(ref: str) -> bool:
    return not ref.strip().lower().startswith(SKIP_PREFIX)


def data_uri(path: pathlib.Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
    return 'data:%s;base64,%s' % (mime, base64.b64encode(path.read_bytes()).decode())


def local_path(root: pathlib.Path, ref: str):
    p = (root / ref.split('?')[0].split('#')[0]).resolve()
    return p if p.is_file() else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('html')
    ap.add_argument('--out')
    ap.add_argument('--no-backup', action='store_true')
    args = ap.parse_args()

    src = pathlib.Path(args.html).expanduser().resolve()
    root = src.parent
    html = src.read_text(encoding='utf-8')
    before = len(html)
    report, remote, missing = [], [], []

    # ---- 1) <link rel=stylesheet> -> <style> ----
    def repl_link(m):
        tag = m.group(0)
        hm = HREF_RE.search(tag)
        if not hm:
            return tag
        ref = hm.group(1)
        if not is_local(ref):
            remote.append(ref)
            return tag
        p = local_path(root, ref)
        if not p:
            missing.append(ref)
            return tag
        css = p.read_text(encoding='utf-8', errors='ignore')
        n_url = len(CSS_URL_RE.findall(css))
        report.append('CSS 内联: %s (%d chars, 内部 url() %d 处)' % (ref, len(css), n_url))
        return '<style>\n%s\n</style>' % css

    html = LINK_RE.sub(repl_link, html)

    # ---- 2) <script src> -> 内联 ----
    def repl_script(m):
        ref = m.group(1)
        if not is_local(ref):
            remote.append(ref)
            return m.group(0)
        p = local_path(root, ref)
        if not p:
            missing.append(ref)
            return m.group(0)
        code = p.read_text(encoding='utf-8', errors='ignore')
        escaped = code.count('</script')
        code = code.replace('</script', '<\\/script')
        report.append('JS 内联: %s (%d chars, 转义 </script %d 处)' % (ref, len(code), escaped))
        return '<script>\n%s\n</script>' % code

    html = SCRIPT_SRC_RE.sub(repl_script, html)

    # ---- 3) CSS 内本地 url() -> data URI ----
    def repl_url(m):
        ref = m.group(1)
        if not is_local(ref):
            remote.append(ref)
            return m.group(0)
        p = local_path(root, ref)
        if not p:
            missing.append(ref)
            return m.group(0)
        report.append('CSS url() -> data URI: %s (%d bytes)' % (ref, p.stat().st_size))
        return 'url("%s")' % data_uri(p)

    html = CSS_URL_RE.sub(repl_url, html)

    # ---- 4) <img src> 本地图片 -> data URI ----
    def repl_img(m):
        ref = m.group(2)
        if not is_local(ref):
            remote.append(ref)
            return m.group(0)
        p = local_path(root, ref)
        if not p:
            missing.append(ref)
            return m.group(0)
        report.append('图片 -> data URI: %s (%d bytes)' % (ref, p.stat().st_size))
        return m.group(1) + data_uri(p) + m.group(3)

    html = IMG_SRC_RE.sub(repl_img, html)

    # ---- 5) 写盘（先备份） ----
    out = pathlib.Path(args.out).expanduser() if args.out else src
    if out == src and not args.no_backup:
        bak = src.with_name(src.stem + '.bak-' + datetime.date.today().strftime('%Y%m%d') + src.suffix)
        bak.write_text(src.read_text(encoding='utf-8'), encoding='utf-8')
        print('备份: %s (%d bytes)' % (bak.name, bak.stat().st_size))
    out.write_text(html, encoding='utf-8')

    # ---- 6) 报告 ----
    print('\n=== 内联明细 ===')
    print('\n'.join('  - ' + r for r in report) or '  (无本地依赖可内联)')
    print('\n=== 体积 ===')
    print('  %d -> %d chars  (%s -> %s bytes)' % (before, len(html), src.stat().st_size, out.stat().st_size))

    residual = re.findall(r'<script\b[^>]*\bsrc=', html, re.I) + LINK_RE.findall(html)
    print('\n=== 残留检查 ===')
    print('  外部 <script src> / <link rel=stylesheet>: %d 处' % len(residual))
    if FETCH_RE.search(html):
        print('  ⚠️ 代码里仍有 fetch/XHR/import() —— file:// 下运行时会失败，必须改成内联字面量')
    if remote:
        print('  ⚠️ 仍需联网: ' + ', '.join(sorted(set(remote))[:10]))
    if missing:
        print('  ⚠️ 文件缺失(路径错?): ' + ', '.join(sorted(set(missing))[:10]))
    print('\n下一步: 复制到空目录，用 file:// 打开实测（见 SKILL.md 第三步）')
    print('判定标准: externalResources == [] 且 errors == [] 且渲染节点数与升级前一致')
    return 0


if __name__ == '__main__':
    sys.exit(main())
