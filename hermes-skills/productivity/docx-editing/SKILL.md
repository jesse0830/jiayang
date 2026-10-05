---
name: docx-editing
description: Programmatic Word (.docx) editing with python-docx — split/merge reports, trim tables by date range, rewrite summary text while preserving formatting, regenerate charts from table data, insert images at exact positions, fill government/enterprise templates (申报书、方案) from a source document. Use for Chinese enterprise documents (运维报告、验收单、方案) that need restructuring.
---

# DOCX 程序化编辑（python-docx）

## When to use
- 拆分/合并 Word 报告（如把一份混合口径的报告拆成半年度+年度两份）
- 按日期裁剪表格行（问题趋势表、迭代表、事件表）
- 修改正文汇总数字但保留原有格式
- 用表格数据重新生成图表并插入指定位置
- 用户对 Word 排版还原度要求高（见 memory：验收单扫描件→Word 需还原排版）

## Step 1 — 先分析结构，再动手
永远先 dump 文档结构：段落（含图片/图表引用）+ 表格 + 图片位置映射。

```python
from docx import Document
from docx.oxml.ns import qn
doc = Document(path)
rId_map = {rel.rId: rel.target_ref for rel in doc.part.rels.values()}
body = doc.element.body
for child in body.iterchildren():
    if child.tag == qn('w:p'):
        blips = child.findall('.//' + qn('a:blip'))
        imgs = [rId_map.get(b.get(qn('r:embed')), '?') for b in blips]
        charts = child.findall('.//' + qn('c:chart'))  # 内嵌Excel图表
        ...
    elif child.tag == qn('w:tbl'):
        # 逐行打印首末行，确认表格内容和裁剪范围
```

关键发现（本类任务必查）：
- **图片可能嵌在表格单元格里**（服务器清单表每行一张监控截图），只在段落里找会漏。
- 页眉页脚也有图片（header/footer part 的 rels），别算进正文。
- 内嵌图表在 `word/charts/chart1.xml`，数据是缓存的（类别+数值平铺），可以读取判断口径。

## Step 2 — 拆分模式：复制源文件再改副本
不要从零重建文档（格式会全丢）。用 `shutil.copy(src, dst)` 复制两份，再分别打开修改。

## Step 3 — 改段落文本：run 合并陷阱（最大坑）
**中文+数字文本会被 Word 拆成大量小 run**（实测："2025年7月20日至..." 被拆成 19 个 run，如 '02'、'5'、'年'、'7'、'月'；标题"半年度"被拆成 '半' + '年度运维报告'）。直接对每个 run 做 `replace()` 会静默失败。

正确做法：合并成第一个 run 再整体赋值（保留第一个 run 的格式）：

```python
def merge_and_set(para, new_text):
    runs = para.runs
    if not runs:
        para.add_run(new_text); return
    runs[0].text = new_text
    for r in runs[1:]:
        r._element.getparent().remove(r._element)
```

另一个坑：用 `t.startswith(...)` 匹配段落时，原文段落可能有引导语（如"针对系统运维的各类问题，...2025年7月20日..."），必须用 `in` 判断而非 startswith。

## Step 4 — 删表格行：从后往前删
```python
del_idx = [i for i, r in enumerate(tbl.rows) if 条件(r.cells[0].text)]
for i in sorted(del_idx, reverse=True):
    tr = tbl.rows[i]._tr
    tr.getparent().remove(tr)
```
删完要同步改总计行（重新求和）。

## Step 5 — 在表格后插入图片
python-docx 的 `add_picture` 只能加到文末。用 XML 层插入：

```python
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph
new_p = OxmlElement('w:p')
tbl._tbl.addnext(new_p)
para = Paragraph(new_p, tbl._parent)
para.alignment = 1  # CENTER
para.add_run().add_picture(img_path, width=Inches(6.0))
```
注意：新图会分配新的 rId 和 media 文件名（可能复用空闲编号如 image3.png），属正常现象。

## Step 6 — matplotlib 中文字体（macOS）
`/System/Library/Fonts/PingFang.ttc` 可能不存在。可用字体：`PingFang HK`、`Heiti TC`、`STHeiti`、`Songti SC`。
```python
plt.rcParams['font.sans-serif'] = ['PingFang HK', 'Heiti TC', 'STHeiti', 'Songti SC']
plt.rcParams['axes.unicode_minus'] = False
```
双轴图（柱状数量 + 折线完成率）用 `twinx()`，注意两个 y 轴范围要分开设。

## Step 7 — 验收
拆分类任务必做最终核对：
- 标题、前言汇总数字、正文关键句
- 各表行数 + 日期列内容（半年度表应只有 8 个月、事件只到截止日前）
- 图片总数与原文档对比（多出的 = 新插入的）
- 图表插入位置（在目标表格之后、下一节之前）

## 模板填充模式（申报书/方案：内容来自另一份文档）
用户给出"内容文档"+"空模板"，要求按模板章节把内容填进去。完整案例见 `references/template-filling-shenbaoshu.md`。核心流程：

1. 模板若是老 .doc，先 `textutil -convert docx` 转换（python-docx 读不了 .doc）
2. dump 模板结构：识别封面段、TOC 域段（HYPERLINK 开头，跳过）、章标题、节标题、节标题下的"填写说明"段
3. 对每个节标题：删除其下说明段 → 在标题后按序插入内容段/表格/图片
4. 插入顺序用 XML 链式 addnext：`last_el = 标题._p`，对每个新元素 `last_el.addnext(el); last_el = el`（段落用 `p._p`，表格用 `tbl._tbl`，图片先 `add_picture` 到文末再移动其段落 `_p`）
5. 标题文本处理：去掉括号注释（"单位概况及业务职责（石龙政府官网摘抄）"→"单位概况及业务职责"），用 merge_and_set 保留首 run 格式；封面同样处理

**三个必踩的坑（本模式特有）：**
- **`doc.paragraphs` 每次返回新的包装对象**：删除/插入段落后再 `list.index(p)` 会 `ValueError`（对象不在列表）。重新获取列表后必须用底层元素定位：`next(x for x in paras if x._p is p._p)`，绝不用 index(p)。
- **`len(paras)` 缓存过期**：删段后列表变短，循环条件必须实时取 `while i < len(paras)`，不要缓存 n=len(paras) 用旧值。
- **标题匹配要严格**：内容行"项目名称：xxx"不能误判为标题"项目名称"。规则：前缀后只能是结尾或 （/(；但标题中间含顿号时（"应用市可复用、可共用的公共能力情况"）startswith 会失败，必须把完整标题当前缀。

表格与格式要点：
- add_table 建在文末再移动；手动加边框（tblBorders 六边 single sz=4）、表头灰底（w:shd fill=D9D9D9）、固定列宽（tblLayout fixed + 每单元格 tcW，dxa = cm×567）
- 中文 run 字体必须同时设 rFonts 的 ascii/hAnsi/eastAsia，否则宋体/黑体不生效；正文宋体小四 12pt、1.5 倍行距、首行缩进 2 字符（first_line_indent = Pt(24)）
- 目录是 TOC 域，填完保留，交付时提醒用户全选 F9 刷新页码

验收（模板填充必做）：
- `textutil -convert txt` 输出后 grep 模板残留标记：填写要求/样例/×××/待补充/摘抄
- zipfile 检查 `word/media/` 图片数是否符合预期
- 抽查表格数 + 每表表头；抽查各节标题出现次数（正文+TOC 各应出现）

## 排版重建模式（原排版靠表格拼 → 规范重排，零内容丢失）
用户话术："格式帮我优化下，逻辑关系有点混乱，优化完我再提修改意见"。
**铁律：只做排版规范 + 结构理顺，不删内容、不改观点、不改数字**（内容判断留给用户）。
完整案例（含诊断计数、四种还原规则、三个坑的定位过程、交付结构）见 `references/rebuild-messy-layout-docx.md`。

**第一步永远是诊断并先报结论**（不要直接开写）：
```python
print('paragraphs:', len(d.paragraphs), '| tables:', len(d.tables))
boxes = [t for t in d.tables if len(t.rows) == 1 and len(t.columns) == 1]
print('1x1 boxes:', len(boxes))   # 占比高 = 强调框/流程图都是表格拼的
```
`len(tables)` 很大但绝大多数是 1×1 单格表，就是这类文档的病根。

**层级判定必须用 `w:outlineLvl`，不能靠正则**：`^[一二三四五六七八九十]、` 会把"节"误判成"章"
（实测误判 18 章 → 改用大纲级别得正确 10 章）。没编号的章另建显式映射表兜底。

**1×1 框四种还原**：①上一段以 `：` 结尾 → 合并成一句完整的话、框内加粗 ②独立强调框 → 左侧竖线引用块
③含 `→` 的流程框 → 单行 `A → B → C` ④含 `┌┐└┘├┤┬┴┼│` → **保留原结构**的等宽流程段（分叉图是最有价值的内容，逐行 run、Consolas＋中文等宽）。真数据表原样保留。

三个静默毁内容的坑：
- **单元格文本里的 `\n` 不能 replace 成空格** —— 会把 ASCII 图形抹平成一串乱码，导致 `FORK` 判定永不命中。用 `.strip()` 原样保留。
- **`run._element.rPr.rFonts` 可能是 None** → 用 `get_or_add_rPr().get_or_add_rFonts()`，中文等宽另设 `w:eastAsia`。
- **不要用 dump 出来的文本判断"原句被截断"** —— dump 常按行截断，会产生"前者决"这类假截断；**报给用户前必须在真实 docx 文本里 grep 复核**（本次为此撤回了 3 条不存在的问题）。

校验与交付：
- 内容零丢失：跑 `scripts/verify_docx_no_loss.py 原文档.docx 新文档.docx`（句级子串比对，退出码非 0 不得交付）。
- 排版：本机常无 LibreOffice，WPS headless 转 PDF 会挂住 → **不要把"渲染不出来"当成"格式不对"**，改用回读断言（`templates/assert_layout.py`：样式/字体/对齐/缩进/表格数/图形段行数与字体）。
- 交付两份：**优化版 docx**（封面＋TOC 域＋页码＋"文档结构导览"页；提醒用户 Ctrl+A→F9 更新域）＋**优化说明与问题清单 md**。清单按六类组织：内容缺失（逐处列位置）／数字口径不一致／逻辑结构／覆盖缺口（对照上级要求的角色清单）／占位章节／术语统一。每类明确区分"我改了什么"与"留给你定"。

## 多轮迭代：用户提内容意见后的删改与结构重排
排版重建交付后，用户会**分轮**提内容级意见（删某一节、把某章并进另一章、整篇重构为"背景／现状与问题／提升方案／落地计划"四大部分）。完整案例与逐处坑见 `references/iterative-restructure-and-renumbering.md`。

- **"一字不删"只在用户点名处解除**：第一轮的铁律继续有效，除用户明确要求删／并／改的那几处，其余一律不动。
- **不自创名称**：章节降级成子主题时，子主题名**沿用原章名或用户消息里的原话**（本次自创了两个名字 —— "…与效率问题""业务复杂度与能力依赖模型"，最后全部改回原文）。层级变了不等于要改名。
- **rebuild 脚本永远从源文档重建**，不是在上一版输出上增量改。因此替换用的 `old_string` 必须取自**原文文本**；拿新编号／新措辞去替换原文里不存在的串会**静默无改动**（本次犯过一次，白跑一轮）。
- **结构映射做成表**：`(原一级标题前缀, 目标部分, 子主题标题)` 表 + 在 `(kind, value)` 中间产物上做一遍后置映射，别把 if 塞进渲染逻辑。多一层子主题是常态：现状部分合并后 31 个节，直接连号会变成 2.1～2.31，汇报时没法定位。
- **改章号后必须全文扫交叉引用**：`第X章`、`x.y`、`x.y.z` 全部会指错人（本次 6 处，如"后面第四、第五章可以进一步建立"→"后面 2.2、2.3"）。改完再扫一遍，确认零残留旧章号。
- **删目标／指标／章节后清查下游引用**：本次删"目标三：设计方案复用率达到 50%"后，试点方案里"验证复用率 50% 的目标"和验收标准里"48 小时、30%、50% 及质量指标"都还挂着这个口径，不连带清理就自相矛盾。能改的改成不带该口径的表述，判断不了的列进问题清单交用户定。
- **零内容丢失校验要 norm 掉编号层**：句首挂上新编号（`2.3.4`、`（1）`）会让句级比对全部 miss；`norm()` 去空白＋去行首编号后再比。比"通过"更重要的是**逐条解释残余的"找不到"** —— 本次 13 条全部是用户要求删除／替换的内容，说不清的那条才是真丢内容。注意自创标题名也会污染校验结果（改名的那句标题被标为 missing），这是"不要自创名称"的又一个理由。
- **汇报格式**：ASCII 结构树（部分 → 子主题 → 节，右侧标原章号，用户一眼看出旧章去哪了）＋ 两张表格（引用修正／连带清理，列"位置｜原文｜改后"）＋ 一句话校验结论带数字（"614 句逐句核对，13 处找不到，全部是你要求删除或替换的"）。新发现的问题单独列，沿用"我改了什么 / 留给你定"的区分。

- **数字口径类笔误：全文审、先问、后改**。多轮改稿后必做一遍「以下N类／N个／N 个原则」式断言的全文审计，逐条数紧随其后实际列出的条目。
  - **扫描窗口必须覆盖整节**：只看节的前几段会漏掉后半段的条目 —— 本次 DE 侧先只数到 4 条，扩窗后才是 6 条（实测与原判断不符时，回去看全节，不要就着窗口下结论）。
  - 实测两处真笔误：「以下五类」实列 6 条 → 改「六类」；「围绕三个原则」实列 4 条 → 改「四个原则」。改前一律写进问题清单问用户，用户批准（本次回「可以改」）后再动，**绝不擅自改数字口径**。
  - 与断言对应的表在原文就缺失（属已列的 8 处内容缺失之一）时标「无法核对」，不要默认成笔误。
  - 审计结论要给全量判断并点名一致的项：「全文只有这 2 处是真笔误，AE 侧『以下三类』实列 3 条一致」。
- **改成三段号（x.y.z）后，遗留的指代问题在交付时单列**（全部进「留给你定」，不动正文）：①「本章核心结论」这类相对指代在多轮合并后指代不清（本次 4 处）→ 建议改「2.3 核心结论：人员能力与任务匹配」式绝对编号 ②各子主题结论节有无不一 → 建议补齐、把该部分问题收敛成一句话 ③正文条目序号「一、二、三」与一级标题格式撞车 → 建议改「（1）（2）（3）」。
- 审计用的核对方式与本次全部发现见 `references/claim-count-and-crossref-audit.md`。

## 拆分报告类文档的口径要点
- 前言汇总数字（问题总数/完成数/迭代次数/功能点数）必须重新核算，不能只裁表格
- 存量数据（园区数、设备分布、业务单据等不分年月的总量）按用户决定保留原样或裁剪，动手前先问用户口径
- 原文档内部数据矛盾（正文数字 vs 表格数字不一致）要指出，并说明你采用了哪个口径

## 支持文件
- `references/nsiot-report-split.md` — NSIoT 运维报告拆分完整案例（结构、坑、代码片段）
- `references/template-filling-shenbaoshu.md` — 申报书/方案模板填充完整案例（数据结构和填充循环骨架、三个坑的报错原文、表格/图片/验收代码）
- `references/rebuild-messy-layout-docx.md` — 排版重建完整案例（1×1 框四种还原规则、outlineLvl 判层级、假截断误判、问题清单六分类模板）
- `references/iterative-restructure-and-renumbering.md` — 多轮迭代完整案例（结构映射表、原章名不自创、章号重排后 6 处交叉引用清查、删目标后连带清理下游引用、norm 掉编号层的零丢失校验、汇报模板）
- `scripts/verify_docx_no_loss.py` — 重建后"零内容丢失"句级校验器（必跑，退出码非 0 不得交付）
- `templates/assert_layout.py` — 交付前排版断言模板（无 LibreOffice/WPS 渲染时的回读校验）
