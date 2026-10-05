# 申报书/方案模板填充完整案例

案例：东莞市政府信息化项目申报书模板（11章50节，封面+目录域+节标题下带"填写说明"段）← 填充自《全市数字农技应用服务系统》申报书内容。交付 .docx，8 张表格 + 2 张架构图全部就位。

## 数据结构设计（内容与逻辑分离，两个文件）

`fill_content.py` — 纯数据：

```python
COVER = {"市XX局XX项目": "全市数字农技应用服务系统建设项目", "××××年××月": "2026年8月"}
# (标题匹配前缀, [内容段落], 表格 or None)
# 段落: "##"=加粗小标题, "**"=加粗正文, ""=空行, None=跳过
SECTIONS = [
    ("项目名称", ["项目名称：全市数字农技应用服务系统建设项目", "项目性质：新建"], None),
    ("云资源租赁服务", ["本项目按需租用市政务云资源..."], [("资源类型","配置规格","数量","用途说明"), ("云主机","8核16G","2台","部署应用服务")]),
    ...
]
IMAGES = {"总体架构": "/tmp/arch_total.png", "网络架构": "/tmp/arch_net.png"}
```

注意：一个模板标题对应两份内容时（如"分项投资明细"后追加说明段），用第二个占位 key（"分项投资明细2"）存内容，在填充循环里匹配到主标题时合并，占位 key 永不匹配标题。

## 填充循环骨架（含三个坑的解法）

```python
paras = doc.paragraphs
while i < len(paras):                       # 坑2：实时取长度，不要缓存 n
    p = paras[i]; t = p.text.strip()
    if not t or t.startswith('HYPERLINK') or t.startswith('TOC'): i += 1; continue
    hit = None
    for prefix, content, table in SECTIONS:
        if prefix in matched: continue
        stripped = re.sub(r'^\d+(\.\d+)*\s*', '', t)   # 去掉 "1.1 " 编号
        if is_title_match(stripped, prefix): hit = (prefix, content, table); break
    if hit is None: i += 1; continue
    prefix, content, table = hit; matched.add(prefix)
    set_para_text(p, clean_title(t), size=14, bold=True, name='黑体')   # 去括号注释+保留首run格式
    # 删说明段：从标题下一段删到下一个标题段（用 is_title_match 判停）
    j = i + 1
    while j < len(paras):
        pt = paras[j].text.strip()
        if pt and not pt.startswith('HYPERLINK') and any(
            is_title_match(re.sub(r'^\d+(\.\d+)*\s*', '', pt), p2)
            for p2, _, _ in SECTIONS if p2 not in matched):
            break
        paras[j]._p.getparent().remove(paras[j]._p); j += 1
    # 坑1：删除后重取列表，用 _p 定位，不用 index(p)
    paras = doc.paragraphs
    p_new = next(x for x in paras if x._p is p._p)
    # 插入内容（链式 addnext 保持顺序）
    last_el = p._p
    for line in content:
        np = new_para(line[2:] if line.startswith(('##','**')) else line, bold=line.startswith(('##','**')), ...)
        last_el.addnext(np._p); last_el = np._p    # lxml addnext 返回 None，必须用元素本身续链
    if table: tbl = make_table(table); last_el.addnext(tbl._tbl); last_el = tbl._tbl
    if prefix in IMAGES:
        pic_el = add_picture_para(IMAGES[prefix]); last_el.addnext(pic_el); last_el = pic_el
    paras = doc.paragraphs
    i = paras.index(next(x for x in paras if x._p is p._p)) + 1
```

## 三个坑的报错原文

1. `ValueError: <docx.text.paragraph.Paragraph object at 0x...> is not in list`
   → doc.paragraphs 每次返回新包装对象；删除段落后旧对象在新列表里 index 不到。解法：`next(x for x in paras if x._p is p._p)`。
2. `IndexError: list index out of range` 出现在 `pt = paras[j].text.strip()`
   → 主循环开头缓存的 `n = len(paras)` 在删段后过期，j 扫到旧 n 越界。解法：循环条件实时 `len(paras)`。
3. 内容行误判为标题：`is_title_match("项目名称：xxx", "项目名称")` 必须为 False。
   ```python
   def is_title_match(stripped, prefix):
       if stripped == prefix: return True
       if stripped.startswith(prefix) and len(stripped) > len(prefix):
           return stripped[len(prefix)] in ('（', '(')
       return False
   ```
   副作用：标题中间含顿号的（"应用市可复用、可共用的公共能力情况"）startswith 不满足 → 前缀用完整标题。

## 表格工具（python-docx 无默认边框，需手动）

```python
def add_table_borders(table):  # tblPr 加 w:tblBorders：top/left/bottom/right/insideH/insideV, val=single, sz=4
def shade_cell(cell, 'D9D9D9'):  # tcPr 加 w:shd val=clear fill=D9D9D9（表头灰底）
def set_col_widths(table, widths_cm):  # tblLayout fixed + 每单元格 tcW，w = int(cm*567), type=dxa
def fill_cell(cell, text, bold, size=10.5):  # cell.text='' 后 paragraph add_run
```

## 中文 run 字体（必须设 eastAsia）

```python
rFonts = run._element.get_or_add_rPr().get_or_add_rFonts()  # 或手动建 w:rFonts
rFonts.set(qn('w:ascii'), name); rFonts.set(qn('w:hAnsi'), name); rFonts.set(qn('w:eastAsia'), name)
```
只设 run.font.name 中文不生效。

## 图片插到指定位置

`doc.add_picture` 只能加文末。先建段落后 add_picture，再把该段落 `_p` 用 addnext 移到目标后：
```python
p = doc.add_paragraph(); p.alignment = 1
p.add_run().add_picture(path, width=Cm(15.2))
last_el.addnext(p._p)
```

## 验收命令（模板填充必做）

```bash
textutil -convert txt -output /tmp/check.txt "输出.docx"
grep -nE "填写要求|样例|×××|待补充|摘抄|（网上抄）" /tmp/check.txt   # 应只剩有意保留的"待补充"
python3 -c "import zipfile; print([n for n in zipfile.ZipFile('输出.docx').namelist() if n.startswith('word/media/')])"
python3 -c "from docx import Document; d=Document('输出.docx'); print(len(d.paragraphs), len(d.tables), [t.rows[0].cells[0].text for t in d.tables])"
```

## 其他要点
- 老 .doc 模板：macOS 用 `textutil -convert docx 模板.doc -output 模板.docx`（textutil 也支持 -convert txt 做验收）
- TOC 目录域（HYPERLINK 段落）保留不动，交付时提醒用户 Word 里全选 F9 刷新页码
- 数字不用千分位分隔符（用户偏好）；不确定的字段（负责人/联系方式/机构编制/文号）在文中标"（待补充）"，交付时单独列出清单
