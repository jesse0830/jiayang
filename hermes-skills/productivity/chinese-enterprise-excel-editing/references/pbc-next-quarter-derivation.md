# 承接上级 PBC 派生下一季度部门 PBC —— 配方

适用于《数睿干部 20XX年QX PBC（部门-姓名）.xlsx》这类官方表单：拿上级（部门负责人）新季度的 PBC，拆成自己部门要承诺的那一份。

## 一、输入定位与 dump

上级原件常常只落在企业微信缓存里（Mac）：

```
~/Library/Containers/com.tencent.WeWorkMac/Data/Documents/Profiles/<profile>/Caches/Files/<YYYY-MM>/<hash>/<原名>.xlsx
```

终端 `ls` 里文件名会被截断 → 用 `find "<缓存目录>" -iname '*PBC*'` 拿完整路径。**不要用截图 OCR 取数**，直接 openpyxl 读这个 xlsx。

通用 dump 脚本（两个输入各跑一次，重定向落盘后 grep / read_file）：

```python
import openpyxl
p = '<absolute path>'
wb = openpyxl.load_workbook(p, data_only=True)
print('SHEETS', wb.sheetnames)
for name in wb.sheetnames:
    ws = wb[name]
    print('== SHEET', name, ws.dimensions, 'merged', len(ws.merged_cells.ranges))
    for r in range(1, ws.max_row + 1):
        cells = []
        for c in range(1, ws.max_column + 1):
            v = ws.cell(row=r, column=c).value
            if v is not None and str(v).strip():
                cells.append('%s%d=%s' % (openpyxl.utils.get_column_letter(c), r, str(v)[:400]))
        if cells:
            print(r, ' | '.join(cells))
```

跑法（长输出必须落盘，别指望终端直接吐全量）：

```bash
cd /tmp && /usr/bin/python3 /tmp/dump_up.py > /tmp/up_dump.txt 2>&1; wc -c /tmp/up_dump.txt
```

再 `search_files` / `read_file` 在 `/tmp/up_dump.txt` 里定位"收入""权重""A 级"这类关键词所在单元格。

**每张页签都要 dump**：用户可能已经在另一页签自己写了一版，只看第一张会漏掉他的真实口径与权重（决定交付形态前先对清）。

## 二、生成骨架（copy 源 + 改格，保结构）

```python
import shutil, openpyxl
shutil.copy2(SRC, DST)
wb = openpyxl.load_workbook(DST)          # 不带 data_only，保公式与格式
ws = wb[wb.sheetnames[0]]                 # 禁止硬编码 wb["Sheet1"]

def put(ws, addr, text):
    for rng in ws.merged_cells.ranges:    # 合并区只写左上角
        if addr in rng:
            addr = rng.coord.split(':')[0]
            break
    ws[addr] = text

put(ws, 'B9', '完成年度公司整体收入 2 亿目标')
wb.save(DST)
```

要点：
- 保结构优先——不新增/删除行列、不改栏位名、不拆合并。
- 可编辑交付件**不要加工作表保护**（`ws.protection.sheet` 保持 False），不设单元格锁定。
- 待定数字写 `________` 空格（方便用户直接敲），不要写成长段占位文本；同时在回执表里列出待填项。
- 文件名带版本号（用户硬约定）：`…_v1.0.xlsx` → `…_v1.1.xlsx` → `…_v1.2_可编辑版.xlsx`，旧的都留着对比。

## 三、「拆解对照表」页签

新建一张页签（`wb.create_sheet`），列为：

| 序号 | 上级目标 | 上级权重 | 部门承接 KR | 部门权重 | 待对清口径 |

底部写一段"待对清口径"，逐条说明哪个数字为什么空着（缺 Q3 成本基线 / 场景数待与上级对 / 客户数待商务口径），避免用户回头忘了空着的原因。

## 四、映射与权重规则

- 上级每条目标都要有承接；对应的部门 KR 权重**合计 = 1.00**（1.1、1.2 两块各自合计）。
- 收入类目标用"与上级完全一致"的口径，别自己另设数字；同口径要写明（如财务终验法）。
- 上级的 A 级卓越要求里只能由本部门产出的部分（手册、自动化工具落地等）**单列一条 KR**，作为加分项。
- 组织侧要承接上级上一季度没闭环的项（工具未合入、协作机制只有初稿、待招岗位）。

## 五、校验（交付前必做）

1. 用第一节的 dump 脚本跑成品，确认：标题/周期格已改、目标格落位、F/G 等上一季度的自评列**已清空**（新季度不该带旧自评）。
2. 打印 `ws.protection.sheet`（应为 False）与各页签 `merged_cells.ranges` 数量，确认结构没被破坏。
3. 打印全部权重并断言每块合计 = 1.00。
4. 回执附：上级目标→部门 KR 映射表、权重调整说明、待填清单（位置 / 待填项 / 找谁要 / 对等级的影响）、`MEDIA:` 路径。
