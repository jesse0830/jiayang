# 飞书文档内容写入指南

创建飞书文档并批量写入 Markdown 内容的全流程。

## 场景

需要将一份结构化文档（Markdown 格式）写入飞书在线文档，供团队查阅和协作编辑。

## 前置条件

1. 飞书应用已配置 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET`（在 `~/.hermes/.env` 中）
2. 已开通以下**文档相关权限**并**发布版本**（注意：`docx:document` 权限可能不在权限列表中；实际上只需要 `drive:drive` 权限被添加即可。如果连 `drive:drive` 都未开通，仍可通过 docx/v1 创建文档+写入 blocks——文档会被创建在根目录，不受影响）：
   - `drive:drive` — 云文档读写（如不开通，docx/v1 写入仍可用，只是文件上传/导入/指定文件夹等 drive API 不可用）
3. Token 可通过 auth API 获取：`POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal`

### ⚠️ 重要：最小可行权限

如果只需**创建文档并写入内容**（不涉及文件上传、云盘操作、导入），即使飞书应用**没有** `drive:drive` 权限，以下操作仍然可行：
- ✅ `POST /docx/v1/documents` — 创建文档（自动放入根目录）
- ✅ `POST /docx/v1/documents/{id}/blocks/{id}/children` — 写入内容 blocks
- ❌ `POST /drive/v1/files/upload_all` — 需要 `drive:drive`
- ❌ `POST /drive/v1/import_task` — 需要 `drive:drive`
- ❌ 上传文件到指定 folder — 需要 `drive:drive`

所以如果用户只是需要创建在线文档写入内容，**不需要**开通 `drive:drive` 权限。如果要上传文件或从文件导入才需要。

## 完整工作流

### Step 1: 获取 tenant_access_token

```bash
FEISHU_APP_ID="cli_xxxx"
FEISHU_APP_SECRET=$(grep FEISHU_APP_SECRET ~/.hermes/.env | cut -d= -f2)

TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "{\"app_id\":\"$FEISHU_APP_ID\",\"app_secret\":\"$FEISHU_APP_SECRET\"}" | \
  python3 -c "import sys,json; print(json.load(sys.stdin).get('tenant_access_token',''))")
```

**注意：** `grep` 返回的 Secret 会被 Hermes 自动脱敏（如 `QShCGq...5zP3`），但实际值是完整的 32 位字符。如果脱敏值被截断，用 `read_file` 读取 `.env` 文件获取原始值。

### Step 2: 创建文档

```bash
DOC_ID=$(curl -s -X POST "https://open.feishu.cn/open-apis/docx/v1/documents" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"文档标题"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['document']['document_id'])")
```

### Step 3: 写入内容（批量添加 blocks）

通过 `POST /docx/v1/documents/{doc_id}/blocks/{root_block_id}/children` API 批量添加 blocks。

```python
import json, urllib.request

def add_blocks(token, doc_id, parent_id, blocks):
    """向文档的指定父block下批量添加子blocks"""
    url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{parent_id}/children?document_revision_id=-1"
    data = json.dumps({"children": blocks}).encode()
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

def text_block(content, bold=False):
    """创建文本段落 block"""
    return {
        "block_type": 2,  # Text
        "text": {
            "elements": [{
                "text_run": {
                    "content": content,
                    "text_element_style": {"bold": bold}
                }
            }],
            "style": {"align": 1}  # 1=左对齐
        }
    }

def heading_block(content, level=1):
    """创建标题 block"""
    type_map = {1: 3, 2: 4, 3: 5, 4: 6}  # heading_level -> block_type
    block_type = type_map.get(level, 3)
    key = f"heading{level}"
    return {
        "block_type": block_type,
        key: {
            "elements": [{
                "text_run": {
                    "content": content,
                    "text_element_style": {}
                }
            }]
        }
    }

def bullet_block(content):
    """创建无序列表项 block（⚠️ 批量API不支持，参考替代方案用Text模拟）"""
    return {
        "block_type": 12,  # 飞书docx API实际的Bullet编号
        "bullet": {
            "elements": [{
                "text_run": {"content": content, "text_element_style": {}}
            }]
        }
    }
```

### Step 4: 处理 Markdown 到 Blocks 的转换

关键映射关系：

| Markdown 元素 | Block Type | 说明 |
|--------------|:----------:|------|
| `# 标题` | 3 (Heading1) | 一级标题 |
| `## 标题` | 4 (Heading2) | 二级标题 |
| `### 标题` | 5 (Heading3) | 三级标题 |
| 普通段落 | 2 (Text) | 支持 `text_element_style.bold` |
| `**加粗**` | 存为元素的 `bold: true` | 需分段处理 text_run |
| `- 列表项` | 31 (Bullet) | 无序列表 |
| `---` | 22 (Divider) | 分割线 |
| `> 引用` | 17 (Quote) | 引用块 |
| `---` | 22 (Divider) | 分割线 |
| `> 引用` | 17 (Quote) | 引用块 |

### ⚠️ 关键限制：批量 API 不支持的 Block Types

**实际验证过的 block_type 允许值（来自 API 报错返回）：**
[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,999]

注意 block_type **16 不在列表中**（有些文档误称 16=Quote，实际 Quote=17）。

`POST .../children` 批量创建 API 的常见 block_types 验证结果：

| Block Type | 编号 | 批量创建支持 |
|------------|:----:|:-----------:|
|------------|:----:|:-----------:|
| Text (段落) | 2 | ✅ 支持 |
| Heading1 (一级标题) | 3 | ✅ 支持 |
| Heading2 (二级标题) | 4 | ✅ 支持 |
| Heading3 (三级标题) | 5 | ✅ 支持 |
| Heading4 (四级标题) | 6 | ✅ 支持 |
| Code (代码块) | 9 | ✅ 支持 |
| Quote (引用块) | 17 | ✅ 支持 |
| Bullet (无序列表项) | 12 | ❌ 返回 10001 |
| Ordered (有序列表项) | 13 | ❌ 返回 10001 |
| Todo (待办事项) | 18 | ❌ 返回 10001 |
| Divider (分割线) | 22 | ✅ 支持 |
| Table (表格壳) | 31 | ✅ 两步流程：先创建空表壳，再逐个填充单元格。行列积 ≤ 45（如 5×9）。详见下方"原生表格创建"小节 |

**注意 block_type 数字：** 在飞书 docx API 中，Bullet=12, Ordered=13（不是 31/32——那是其他平台的编号）。使用错误数字会导致 `invalid param` 错误。

## 原生表格创建（block_type=31）

**重要发现：** 飞书 API **支持**创建原生表格（block_type=31），之前错误地认为不支持。正确的创建方式是一个两步流程：

### 两步流程

**第一步：创建表格壳** — 通过 `POST .../children` 创建一个 block_type=31 的 table block，含空单元格。

```python
def create_table_shell(token, doc_id, parent_id, rows, cols, column_widths=None):
    """创建原生表格壳（空单元格），返回各单元格的 block_id"""
    default_width = round(800 / cols)
    widths = column_widths or [default_width] * cols
    
    table_block = {
        "block_type": 31,
        "table": {
            "property": {
                "column_size": widths,
                "column_count": cols,
                "row_count": rows
            },
            "cells": []  # 空数组——先创建壳，再填充
        }
    }
    
    url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{parent_id}/children?document_revision_id=-1"
    data = json.dumps({"children": [table_block]})
    req = urllib.request.Request(url, data=data.encode(), headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })
    resp = json.loads(urllib.request.urlopen(req).read())
    
    # 从返回中提取表格 block_id 和所有 cells
    table_block_id = resp['data']['children'][0]['block_id']
    cells = resp['data']['children'][0]['table']['cells']
    time.sleep(0.5)  # 等表格渲染
    return table_block_id, cells  # cells 是二维数组: cells[row][col] = {"block_id": "xxx", ...}
```

**第二步：填充每个单元格** — 对每个 cell，用 `POST .../children` 写入内容（Text block 或其他类型）。

```python
def fill_cell(token, doc_id, cell_block_id, content, bold=False):
    """向表格单元格写入文本内容"""
    text_block = {
        "block_type": 2,
        "text": {
            "elements": [{
                "text_run": {
                    "content": content,
                    "text_element_style": {"bold": bold}
                }
            }],
            "style": {"align": 1}
        }
    }
    
    url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{cell_block_id}/children?document_revision_id=-1"
    data = json.dumps({"children": [text_block]})
    req = urllib.request.Request(url, data=data.encode(), headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())
```

### ⚠️ 已知限制

| 限制 | 具体值 | 解决方法 |
|------|--------|---------|
| 每表最大行数 | **9 行**（超过返回 1770001 invalid param） | 数据超 9 行时拆分为多个子表，每个子表 ≤9 行 |
| 行列积上限 | ≤45（如 5×9=45 ✅, 4×12=48 ❌, 6×8=48 ❌） | 宽表用 5 列×9 行，或调整列数 |
| 列宽 | 必须用 `column_size` 数组指定，单位像素 | 总宽约 800px，拆分均分或按内容比例分配 |
| 时序 | 创建表格壳后需等约 0.5-1s 再填充 | `time.sleep(0.5)` 或处理重试 |
| 多表创建 | 不要同时在一次 API 调用中创建多个表格 | 在分批循环中逐表创建，每次之间 sleep 1s |
| 列宽数值 | 未经验证的宽高比可能导致列宽不均 | 推荐：窄列 60px，中等 120px，宽列 160px+ |

### 常见问题

- **返回 1770001 invalid param** → 检查 rows 是否 ≤ 9，cols × rows ≤ 45
- **表格创建成功但内容不显示** → 检查是否填充了单元格（需对每个 cell 的 block_id 写入）
- **列宽不均匀** → 设置 `column_size` 数组（如 `[120, 120, 120, 120, 120]` 分 5 列），不设置时默认均分
- **表格单元格在填充内容前**是空白的（用户浏览器中显示为空行）—— 这是正常状态
- **表格标题行加粗**：在填充 cell 时设置 `bold=True`

### Python 批量创建示例（多表格+多行数据）

```python
import json, urllib.request, time

def create_table_with_data(token, doc_id, parent_id, headers, rows_data, col_widths=None):
    """快捷函数：创建表格并填充数据（自动处理 ≤9 行拆分）"""
    max_rows = 9
    all_rows = [headers] + rows_data
    cols = len(headers)
    
    for chunk_start in range(0, len(all_rows), max_rows):
        chunk = all_rows[chunk_start:chunk_start + max_rows]
        rows = len(chunk)
        
        # 创建表格壳
        _, cells = create_table_shell(token, doc_id, parent_id, rows, cols, col_widths)
        
        # 填充每个单元格
        for r in range(rows):
            for c in range(cols):
                cell_id = cells[r][c]['block_id']
                is_header = (chunk_start == 0 and r == 0)
                fill_cell(token, doc_id, cell_id, str(chunk[r][c]), bold=is_header)
        
        time.sleep(0.5)
```

### 与 Text 模拟表格对比

| 维度 | 原生表格 (block_type=31) | Text 模拟 (`│` + `─`) |
|------|:-----------------------:|:---------------------:|
| 视觉效果 | 标准的飞书表格样式 | 文本排版，可用但粗糙 |
| 可编辑性 | 用户可在飞书页面中点击编辑单元格 | 只读文本，无法编辑 |
| 创建复杂度 | 高（两步流程 + 限制多） | 低（一步创建） |
| 数据量限制 | 每表 ≤9 行 | 无限制 |
| 推荐场景 | 小表格（≤9行）、需要用户后续编辑的表格 | 大表格、静态展示 |

### Step 5: 分批写入

### Step 5: 分批写入

批量 API 单次可写入约 50-100 个 blocks。如果内容很多（如 100+ blocks），需要分批发送。**经验证 batch_size=40 可靠（214块全量成功，0失败）。** 如果出现失败，逐块回退写入可隔离出有问题的 block。

```python
def write_document(token, doc_id, blocks, batch_size=40):
    root_id = doc_id  # 根block就是文档本身
    for i in range(0, len(blocks), batch_size):
        batch = blocks[i:i+batch_size]
        result = add_blocks(token, doc_id, root_id, batch)
        if result.get('code') != 0:
            print(f"Batch {i//batch_size} failed: {result}")
            break
        print(f"Batch {i//batch_size} OK: {len(batch)} blocks")
```

## 已完成的实践案例

- **文档ID:** `YZvYdjmZtoNkrVxDyaEcM0xXnCh` — "软件工厂氛围改善行动计划"
- **内容量:** 103 个 blocks（含标题、正文、模拟列表和表格）
- **处理时间:** 约 4 分钟（含多次调试）
- **最终效果:** 内容完整可读，表格和列表用文本方式呈现

- **文档ID:** `VdaUdF7whonNhAxvqiVcOc43nOh` — "子课题1：溱湖湿地公园游客低碳行为调研与碳迹记录表单设计"（2026-06-22）
- **内容量:** 568 个 blocks（含1-4级标题、代码块、引用块、文本段落），12批次全部成功，零失败
- **处理时间:** 约 2 分钟（含 Python 脚本编写和执行）
- **关键特性:** 全部使用 block_type 2/3/4/5/6/9/17/31（Text/Heading1-4/Code/Quote/原生表格），无列表或分割线. 对于 ≤9 行的表格数据使用原生 table (block_type=31)，超出行数的分拆为多个子表。其余 bullet/ordered/divider 用 Text block 加视觉前缀模拟
- **数据来源:** 从 69690 字节的 .md 文件逐行转换。转换逻辑：`#` → heading, `##` → heading2, `###` → heading3, `####` → heading4, ```` → code block, `>` → quote, `- ` → bullet 用 `• ` 前缀Text, `---` → 全角横线Text, 其余 → text
- **注意:** 这次是在飞书应用**缺少 `drive:drive` 权限**的情况下完成的——证明 docx/v1 文档创建和写入不需要该权限

## 插入内容到已有文档中（内容注入模式）

当需要在已有内容的文档中插入新章节（而非从零创建），使用此模式。

### 适用场景

- 已有文档包含引言→2个表格→3段正文→结语，需要在"引言之后、表格之前"插入新章节
- 需要在文档适当位置批量插入多个 blocks（H1 + 正文 + H2 + 正文...）
- 不想重建整个文档（数据量大、结构复杂时重建成本高）

### 工作流

#### 1. 读取当前文档结构，确定父 block

```python
req = ListDocumentBlockRequest.builder() \\
    .document_id(doc_id).page_size(50).document_revision_id(-1).build()
resp = client.docx.v1.document_block.list(req)
for item in resp.data.items:
    print(item.block_type, item.block_id[:20], item.children)
```

关键判断：新内容应该挂到哪个 parent 下？
- **文档根（doc_id 本身）**：新内容成为顶级块，追加到末尾
- **某个容器块**：新内容嵌套在该容器块中，出现在其子块的末尾

#### 2. 用 dict 构建 blocks（比 SDK builder 更简洁）

```python
def heading_block(content, level=1):
    type_map = {1: 3, 2: 4, 3: 5, 4: 6}
    key = f"heading{level}"
    return {
        "block_type": type_map[level],
        key: {
            "elements": [{
                "text_run": {"content": content, "text_element_style": {}}
            }]
        }
    }

def text_block(content, bold=False):
    return {
        "block_type": 2,
        "text": {
            "elements": [{
                "text_run": {"content": content, "text_element_style": {"bold": bold}}
            }],
            "style": {"align": 1}
        }
    }
```

#### 3. 批量 POST 到 parent block

```python
new_blocks = []
new_blocks.append(heading_block("一、新章节标题", level=1))
new_blocks.append(text_block("这是新的章节内容正文。"))
new_blocks.append(heading_block("1.1 子节", level=2))
new_blocks.append(text_block("子节的详细内容。可以多个段落。"))

creq = CreateDocumentBlockChildrenRequest.builder() \\
    .document_id(doc_id).block_id(parent_id) \\  # parent可以是doc_id本身或容器块ID
    .request_body(
        CreateDocumentBlockChildrenRequestBody.builder()
            .children(new_blocks)
            .index(-1)
            .build()
    ).build()
resp = client.docx.v1.document_block_children.create(creq)
```

#### 4. 验证

```python
check_req = ListDocumentBlockRequest.builder() \\
    .document_id(doc_id).page_size(50).document_revision_id(-1).build()
check_resp = client.docx.v1.document_block.list(check_req)
print(f"Root blocks: {len(check_resp.data.items)}")
```

### 重要：`?index=N` 不可靠

| 方案 | 可靠？ | 最佳使用场景 |
|------|:-----:|-------------|
| `POST .../children?index=N` | ❌ 不可靠 — 始终追加到末尾 | 避免使用 |
| 追加到根 block（doc_id） | ✅ 可靠 | 新增顶级章节 |
| 追加到容器 block | ✅ 可靠 | 在已有章节内插入内容 |
| 重建整个文档 | ✅ 但代价高 | 大规模重构 |

**核心原则：** `POST .../children` 追加到指定 parent 的末尾。通过选择合适的 parent 控制内容位置，而非通过 `?index` 参数。

## 排查

| 现象 | 原因 | 解决 |
|------|------|------|
| `code: 10001` | 使用了不支持的 block type | 用 Text block 替代，或用支持的 block types（2,3,4,5,6,9,17） |
| `code: 0` 但文档无内容 | 没指定 `document_revision_id` | 添加参数 `?document_revision_id=-1` |
| API 返回 99991672 | 权限未发布 | 去飞书开发者后台发布版本 |
| token 获取失败 | Secret 被截断 | 用 `read_file` 读取 `.env` |
| `invalid param` 且 block_type 在 10-20 范围 | 使用了错误的 block_type 编号（如 Bullet=31 应为 12） | 确认正确的 block_type 编号（见上方表格） |
| 文档创建成功但返回 `code: 0` + 异常数据 | block 的 key 名与 block_type 不匹配 | 确保 block 的 key 名与 block_type 对应（如 block_type=9 的 key 是 "code"，block_type=17 的 key 是 "quote"，block_type=4 的 key 是 "heading2"） |
| 文档内容混乱（测试块残留） | 测试过程中创建了重复内容 | 直接删除旧文档不安全（DELETE 可能返回 404），推荐创建新文档重新写入，不要尝试清理旧文档 |

## 文档结构调试：Block 分析（手动修复指南）

当飞书 API 的 `batch_delete` 返回 404、`?index=N` 无法控制插入位置、或文档内容顺序错乱时，**不要反复尝试自动化方案**。正确的做法是：读取文档所有 block → 生成可读的结构映射图 → 指导用户在飞书 UI 中手动拖拽修复。

### 适用场景

- 文档内容顺序错乱（测试表格、文字块位置不对）
- `batch_delete` 返回 404 无法通过 API 删除
- `POST .../children?index=N` 不生效，块被追加到末尾
- 不想重建整个文档（数据量大，重建成本高）

### 工作流

#### 1. 读取所有 blocks

用 Feishu API 递归读取文档的 block 树。根 block 就是文档本身（doc_id）。

```python
def get_all_blocks(token, doc_id, page_size=500):
    """递归获取文档的所有 blocks"""
    all_blocks = []
    
    def fetch_children(block_id, depth=0):
        url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{block_id}/children?page_size={page_size}&document_revision_id=-1"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        try:
            resp = json.loads(urllib.request.urlopen(req).read())
        except Exception:
            return
        items = resp.get("data", {}).get("items", [])
        for item in items:
            item["_depth"] = depth
            all_blocks.append(item)
            if item.get("children"):
                fetch_children(item["block_id"], depth + 1)
    
    fetch_children(doc_id)
    return all_blocks
```

#### 2. 构建可读的 Block 映射表

对每个 block，提取关键信息并按顺序列出：

```python
def analyze_structure(blocks, doc_id, token):
    TYPE_NAMES = {
        2: "text", 3: "h1", 4: "h2", 5: "h3", 6: "h4",
        9: "code", 12: "bullet", 13: "ordered", 17: "quote",
        22: "divider", 31: "table"
    }
    for idx, b in enumerate(blocks):
        bt = b["block_type"]
        type_name = TYPE_NAMES.get(bt, f"type{bt}")
        preview = ""
        if bt == 31:  # table
            prop = b.get("table", {}).get("property", {})
            rows = prop.get("row_count", 0)
            cols = prop.get("column_count", 0)
            cells = b.get("table", {}).get("cells", [])
            is_empty = all(
                not cell[0].get("children", [])
                for row in cells for cell in row
            )
            preview = f"({rows}x{cols}){' ⛔️ 空' if is_empty else ' ✅ 有数据'}"
        elif bt in (2, 12, 13, 17):
            elements = (b.get("text") or b.get("bullet") or b.get("ordered") or b.get("quote", {})).get("elements", [])
            preview = " | " + "".join(
                e.get("text_run", {}).get("content", "")
                for e in elements
            )[:60]
        elif bt in (3, 4, 5, 6):
            elements = (b.get("heading1") or b.get("heading2") or b.get("heading3") or b.get("heading4", {})).get("elements", [])
            preview = " | " + "".join(
                e.get("text_run", {}).get("content", "")
                for e in elements
            )[:60]
        print(f"[{idx:3d}] {type_name:12s} {preview}")
```

#### 3. 标注：判断哪些 block 需要修复

在打印结果后，人工标注每类的处理方式：

| 标注 | 含义 | 处理 |
|------|------|------|
| `✅ 保留` | 内容和位置正确 | 不动 |
| `⛔️【空表-删掉】` | 测试残留，无数据的表格 | 用户在 UI 中选中 → Delete |
| `→ 需移前` | 文字块位置错 | 拖到正确位置 |
| `→ 需移后` | 文字块或子弹位置错 | 拖到正确位置 |

#### 4. 呈现给用户

示例输出格式：

```
=== 第 1.6 ~ 1.7 节区域 ===
[35] 表(8x5)    | ✅ 其他表(有数据)
[36] text       | ✓ 即使维持去年有效月均217万...
[37] h3         | ✓ 1.7 基于2025周计划...
[38] text       | ✓ 以下是基于2025年...
[43] 表(6x3)    | ✅ 总配比表
[44] 表(3x3)    | ⛔️【空测试表-删掉！】
[45] 表(4x5)    | ✅ 苍南表
[47] 表(3x3)    | ⛔️【空测试表-删掉！】
[48] text       | → 苍南标杆项目配比...【应移到43之后】
[49-51] bullets | → 三条差距分析【应移到52,53之后】
[52] text       | ✓ 上表可见...
```

#### 5. 给用户的操作说明

用最简洁的语言说明要干什么：

```
你要做的操作（飞书里，总共15秒）：
1. 删两个空表 — 选中→Delete
2. 拖一行文字 — 拖「苍南标杆项目配比」到总配比表后面
3. 拖三条子弹 — 拖差距分析子弹到「差距分析：」后面
```

### ⚠️ 为什么不重建文档

旧文档里还有大量有数据的表格（收入图表、里程碑分类、场景对比等），用 API 重建需要逐个填几百个单元格，不仅慢还容易丢数据。手动拖拽调整后内容完好无损。

### 关键原则

1. **先分析，再修复** — 不要直接重建。先读结构，判断是否可以用手动拖拽修复。
2. **标注清晰** — ✅⛔️→ 让用户一眼看懂。
3. **给出具体操作步骤** — 不要说"内容顺序有问题"，要说"删第44和第47号表格，把第48号文字拖到43之后"。
4. **解释为什么不自动修** — 简要说明 API 限制（batch_delete 404, ?index=N不可靠）。
5. **文档链接附在末尾** — 用户点开即可操作。

## 注意事项

- **不要用 delegate_task 的子代理执行**——子代理在沙箱中运行时，获取的 token 和创建的文档 ID 不会自动传回主会话。建议在主会话中直接通过 `terminal` 执行 Python 脚本。
- **token 有效期 2 小时**——长时间写入需要刷新
- **文档创建后立即写入**——不需要等同步，API 是同步的
- **不支持富文本中混合加粗/正常文本**——飞书 text_run 的 `bold` 是 per-element 的。如果一段文字中既有加粗又有正常文本，需要拆分成多个 `text_run` elements。
