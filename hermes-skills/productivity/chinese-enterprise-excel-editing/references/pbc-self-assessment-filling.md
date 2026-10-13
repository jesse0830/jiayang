# 官方表单类工作簿填写（PBC 自评 / 考核表）——脚本配方

适用：用户发来一份下发回收的表单 .xlsx（干部 PBC、季度自评表、考核表），要求"帮我把自评补一下"。
**不适用**：数据分析类/合并类工作簿（见 SKILL.md 的跨表合并章节）。

## 0. 表单典型结构（写前必须实读确认，别照抄）

```
R1  表单大标题（合并区）
R2  "1.1 主业务目标    等级："        ← 汇总格，常只有标签无独立填分格
R3  "1.2 组织与人员管理 等级："
R6  表头：序号 | 关键任务/目标 | 评价标准 | 权重 | 评价结果(主管) | 自评等级 | 自评评语与举证 | ...
     ↑ 目标区 A-E                ↑ 汇总列            ↑ 自评区 F/G      ↑ 主管区 H/I
R9.. 各 KR 行（含 KR 子项 1.1/1.2 …）
Rn  "主业务目标 评价结果" / "绩效目标 整体评价结果"
Rxx 干部观六项（信念使命/责任担当/理解力/决断力/执行力/领导力）逐行 + 汇总行
Ryy 第三部分 IDP：序号 | 方向 | 目标 | 行动计划 | 个人能力提升情况总结（F:G 合并大格）
```

要点：**自评列 = F（等级）/ G（评语与举证）**，**主管列 = H/I**；汇总等级写在表头标签格（追加）；IDP 总结区是 F:G 合并格 → 只写 F。这些位置**每次都要重新实读确认**，表单版本会变。

## 1. 只读 dump（落盘成 txt 再读，不要直接读 xlsx）

```python
import openpyxl, sys
P = sys.argv[1]
wb = openpyxl.load_workbook(P, data_only=True)
for ws in wb.worksheets:
    print(f"=== SHEET {ws.title} dims={ws.dimensions} max_row={ws.max_row} max_col={ws.max_column}")
    print("MERGES:", [str(r) for r in ws.merged_cells.ranges])
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, max_col=ws.max_column):
        cells = [f"{c.coordinate}={str(c.value)[:200]}" for c in row if c.value not in (None, "")]
        if cells:
            print(f"R{row[0].row}: " + " | ".join(cells))
```

跑法：`write_file` 到 scratch（如 `~/.hermes/cache/scratch/pbc_dump.py`）→ `cd <scratch> && python3 pbc_dump.py "<表单路径>" > pbc_dump.txt 2>&1; wc -l pbc_dump.txt` → `read_file`（长输出分次读）。

横向对照：对同目录同批次其他人的同类表单再跑一遍同一个脚本，得到写法/口径参照。

## 2. 写入骨架（只写自评区）

```python
import openpyxl, shutil, datetime
from copy import copy
from openpyxl.styles import Alignment

SRC = "<表单绝对路径>"
BAK = f"pbc_backup_自评填写前_{datetime.date.today():%Y%m%d}.xlsx"
shutil.copy2(SRC, BAK)                      # ① 先备份，永远第一步
wb = openpyxl.load_workbook(SRC)            # ② 不带 data_only，保公式与格式
ws = wb["个人绩效承诺书（PBC）"]

# ③ 表头汇总格：标签后追加等级，不新建格、不插行
for addr, grade in [("F2", "B+"), ("F3", "B+")]:
    c = ws[addr]
    if c.value and "等级" not in str(c.value):
        c.value = f"{c.value}    等级：{grade}"
    elif c.value:
        c.value = f"{str(c.value).rstrip('：: ')}：{grade}"

# ④ 自评列逐格写入；合并格只写左上角（F33 = F:G 合并区起点）
for addr, text in ITEMS:                    # ITEMS = [(“F9”, “B”), (“G9”, “评语…”), …]
    c = ws[addr]
    c.value = text
    c.alignment = Alignment(wrap_text=True, vertical="top")   # 长文本必须自动换行
    ws.row_dimensions[c.row].height = max(ws.row_dimensions[c.row].height or 0, 60)

wb.save(SRC)                                # ⑤ 原地保存（提交件不改名）
print(f"backup -> {BAK}")
```

规则：**只列白名单地址**（F/G 自评区 + 表头汇总格），绝不遍历整行写；主管列 H/I 一个都不在清单里。

## 3. 改后全格 diff（唯一可信的验证）

```python
import openpyxl
A = openpyxl.load_workbook("<备份>", data_only=False)
B = openpyxl.load_workbook("<成品>", data_only=False)
changed, unexpected = [], []
SELF_COLS = {"F", "G"}
for name in A.sheetnames:
    a, b = A[name], B[name]
    for row in a.iter_rows(min_row=1, max_row=max(a.max_row, b.max_row), max_col=max(a.max_column, b.max_column)):
        for c in row:
            v1, v2 = c.value, b[c.coordinate].value
            if v1 != v2:
                changed.append(f"{name}!{c.coordinate}")
                if c.column_letter not in SELF_COLS and c.coordinate not in {"F2", "F3"}:
                    unexpected.append(f"{name}!{c.coordinate}")
print(f"changed={len(changed)}  unexpected={unexpected}")
print("\n".join(changed))
assert not unexpected, "改动越界：碰到非自评列"
```

断言通过 = 改动全部落在自评区、其余零差异。**"写成功了"不算验证**；要给出改动格数与清单，并显式说明主管列未动。

## 4. 回执模板（缺数字时）

1. 一句话结论 + 目标文件路径 + 写入时间（mtime）+ 工作表名。
2. **等级表**：区块 / 自评等级 / 依据一句话（逐行覆盖每个被评项与汇总项）。
3. **校验结论**：改动 N 处全在自评区；其余单元格与填写前逐格零差异；主管列未动。
4. **"提交前需要你补的 N 个数字"表格**：位置 / 待填项 / 对等级的影响（达 X 可升到 B+ 之类）。
5. **附带文件**：备份（回滚点）、自评全文可核对版 `_v1.0.md`。
6. **需用户拍板的格式问题**：如汇总格是标签追加式、或某区块无专用填写格 —— 给"要不要改成只填字母/不改标签文字"的选项。

## 5. 等级写法约定（自评不虚高，也不保守）

- 自评等级用 A/B/C 单字母；**顶层汇总可带 +**（B+/A）表达"达到并提供超出 B 的举证但未满 A"。
- 每个等级都要有可核实的举证（项目名/人数/条数/日期/机制名）；写不出举证的项就给 B，不硬上 A。
- 凡涉及财务口径（收入、人均产出）的等级，**只在数字确认后才上调**，否则保持 B 并标 `【待填】`。
