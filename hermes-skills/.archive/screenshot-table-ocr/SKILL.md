---
name: screenshot-table-ocr
description: "从表格截图提取数字：tesseract 单元格级 OCR + 行列求和验证。"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [OCR, Screenshot, Table, Tesseract, Data-Extraction, Validation]
    related_skills: [ocr-and-documents, chinese-enterprise-excel-editing]
---

# 表格截图数字提取（screenshot-table-ocr）

用户发来一张**表格/数字矩阵截图**（HC 缺口表、编制表、报销统计、人效表等），要的是逐格数字而不是整段文字。常见来源：聊天里 `@image:.../composer-images/...png` 拖进来的图片。

核心思路：**tesseract 单元格级 OCR → 行列求和交叉验证 → 矛盾单元格定点重识别 → 仍矛盾就问用户，绝不猜**。

## 工作流（在 720x280 HC 缺口表上验证过）

**Step 1 — 定位图片并确认尺寸**
```bash
file "<图片路径>" && sips -g pixelWidth -g pixelHeight "<图片路径>"
```

**Step 2 — 先放大再 OCR**（小截图直接识别会丢数字）
```bash
sips -z 840 2160 "<原图>" --out /tmp/hc_big.png   # -z <高> <宽>，3x 效果好
```
注意：`-z` 是纯缩放，安全。**不要用 `-s format` 重编码**（曾导致 tesseract 输出为空）。

**Step 3 — tsv 模式拿单元格坐标**（不能只出纯文本，要 x/y 重建网格）
```bash
tesseract /tmp/hc_big.png /tmp/hc_tsv -l chi_sim+eng --psm 6 tsv   # psm 6 = 均匀块，适合表格
```
解析 tsv：列 6 = x、列 7 = y、列 10 = 置信度、列 11 = 文本。按 (y, x) 排序，按 y 分组还原成行。

**Step 4 — 行列求和交叉验证（关键的数据完整性步骤）**
把每列、每行求和，和打印的"总计"行/列对比。**列合计与总计行吻合 = 单元格数值可信的强证据**；某行总计和行内求和对不上 = 红旗，需要查。

**Step 5 — 矛盾数字定点重识别**（先排除 OCR 错，再怀疑源表）
```bash
sips -c <高> <宽> --cropOffset <y> <x> "<原图>" --out /tmp/cell.png   # cropOffset 先 Y 后 X！
sips -z <放大6倍> <放大6倍> /tmp/cell.png --out /tmp/cell_big.png
tesseract /tmp/cell_big.png /tmp/cell_ocr --psm 7   # psm 7 = 单行
```
裁剪前要把 tsv 坐标**除以放大倍数**换算回原图像素。

**Step 6 — 定点重识别后仍矛盾 → 源表本身就不一致，直接问用户**
用户铁律：信息碎片化直接问，不拼凑/推演数据。真实案例：无锡行打印总计 6、行内求和 28；南京打印 72、求和 50 —— 但所有列合计都和总计 101 吻合，所以单元格可信，只把这两个总计列数字标出来让用户确认。

完整实例（含真实命令和输出）：`references/hc-gap-table-example.md`

## 多版本修订核对（同一张表用户反复改）

用户会连发多个修订版（"修改了，你看下是否正确" → "现在呢"）。规则：

- **每版都要重新 OCR 全表，不要复用上一版结果**——数字可能只在个别格变了，凭旧结果比对会漏。
- 每版独立验证：行求和 = 列求和 = 总计行，全自洽才报"正确"。
- 回复时同时给两样东西：①本版内部是否自洽；②**相比上一版改了哪些**（新增/删除的区域行、变动的数字、总计是否变化）。用户发修订版的真实意图是确认改动，不是只看总数。
- **总计没变 ≠ 没改**：区域间重分配时总和可以保持不变（2026-08-05 实例：v1→v2 修正了矛盾，v3 扩到 6 区域新增温州/惠州，总计一直 101）。

## 坑（Pitfalls）

- **sips cropOffset 参数顺序是 Y 再 X**：`--cropOffset <y> <x>`，写反会裁错区域。
- **tsv 坐标是放大后坐标**，裁剪原图前必须除以放大倍数。
- **vision_analyze 在 DeepSeek 模型上不可用**（不支持 image_url），tesseract 路径就是主方案，不要先试 vision。
- **hermes venv 的 PIL 可能坏**（`ImportError: cannot import name '_imaging'`）——缩放/裁剪一律用 `sips`，别用 PIL。
- **中文 OCR 输出噪声大**：换行错乱、中英混杂、标点乱——按坐标重建结构，不要直接信任文本流。
- **带注释的单元格要保留上下文**：如 `6 (数据开发)`，数字和括号注释是一体的。
- **数字格式按用户偏好**：不要千分位分隔符（3185 不写 3,185）。
- 检查 tesseract 中文包：`ls /opt/homebrew/share/tessdata/` 需有 `chi_sim.traineddata`（brew install tesseract-lang）。
- **深色/半透明 UI 卡片截图 tesseract 基本无效**（2026-08-05 实例）：1024×1024 岗位画像图，绿色卡片+38.9% alpha 半透明，放大/灰度/反色/二值化/alpha通道还原/颜色分类 6 种预处理全部只输出 `\` 或空。此类图（如 smardaten 平台 UI 卡片、深色主题 dashboard）文字可能是图形渲染，不是可 OCR 文本。
- **macOS Vision framework 兜底**：tesseract 失效时试 `scripts/vocr.swift`（VNRecognizeTextRequest, zh-Hans+en-US, accurate）。编译：`swiftc -O scripts/vocr.swift -o /tmp/vocr`，运行：`/tmp/vocr <图片路径>`。注意：对纯文字截图有效，图形化卡片仍可能失败。
- **OCR 连续失败 → 尽早转向源文件**：截图 OCR 试 2-3 种方案仍不行，直接请用户提供源文件（Excel/docx），不要无限试预处理。2026-08-05 实例：用户下载 Excel 后一次读取成功。这是工作流铁律，不是选项。
