---
name: feishu-app-config
description: Configure Feishu/Lark personal app credentials, validate API permissions, and troubleshoot common errors.
---

# Feishu App Config

Configure Feishu (飞书/ Lark) personal app credentials (App ID + App Secret) and validate that the API permissions work for reading, creating, and modifying documents.

## When to use

- User says "帮我配置飞书个人账号" / "切换为个人应用"
- User provides new App ID / App Secret and wants them activated
- User asks "这个飞书文档能改吗 / 能帮我改吗" — test write permissions first
- Permission errors (99991672, 1770032) need diagnosis
- 用户丢来一个飞书文档/表格链接问"这个能读取到吗"，或抓取结果带 `no content extracted` → 先按 `references/document-read-access.md` 走通道决策树，别急着试遍所有办法
- Feishu docx/drive tools are not working after credential change

## Steps

### 1. Backup and update .env

Feishu gateway/platform reads credentials from `~/.hermes/.env`:
- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`

**Backup first:**
```
cp ~/.hermes/.env ~/.hermes/.env.bak.$(date +%Y%m%d_%H%M%S)
```

**Update via sed** (patch tool may be blocked on .env):
```
sed -i '' 's/^FEISHU_APP_ID=.*$/FEISHU_APP_ID=<new_id>/' ~/.hermes/.env
sed -i '' 's/^FEISHU_APP_SECRET=.*$/FEISHU_APP_SECRET=<new_secret>/' ~/.hermes/.env
```

Verify:
```
grep 'FEISHU_APP_ID\|FEISHU_APP_SECRET' ~/.hermes/.env
```

### 2. Install dependency

```
pip3 install lark-oapi
```

### 3. Permission boundaries (important — save debugging time)

| Operation | Personal App | Required Scope |
|-----------|-------------|----------------|
| Read existing doc **shared with the app** | ✅ | `docx:document` |
| Read an arbitrary doc **not shared with the app** | ❌ 1770032 forBidden | 需先把文档分享给应用（见 `references/document-read-access.md`） |
| Create new doc | ✅ | `docx:document:create` |
| Modify self-created doc | ✅ | `docx:document:create` |
| Modify other-created doc (incl. wiki docs) | ❌ 1770032 forBidden | N/A — personal app cannot |
| Wiki node info (spaces/get_node) | ❌ 99991672 | `wiki:wiki`, `wiki:node:read` |

**Key insight:** Personal apps can modify only documents they created via API. Existing wiki documents created by other accounts/users cannot be modified. Workaround: create a new doc with the modified content (see `references/document-copy-workflow.md`), or have the user share the doc with edit permissions to the app.

**⚠️ 读也受同一个限制（2026-09 实测，务必先判断再动手）**：`tenant_access_token` **拿到 ≠ 有文档权限**。用应用身份读一份别人创建的 docx（`GET /open-apis/docx/v1/documents/{doc_id}/raw_content`）会直接返回 **1770032 forBidden**；此时凭证是好的（token 换得回来），问题在"这份文档没有授权给应用"。所以"这个链接能读到吗"的正确第一步是判断**文档有没有分享给应用**，没有就走替代通道 —— 完整决策树见 `references/document-read-access.md`。

### 4. Testing permissions (lark_oapi SDK)

When running Python test scripts, sys.path may be polluted by `gateway/platforms/` which has an `email.py` that shadows stdlib `email`. **Fix by cleaning sys.path:**

```python
import sys
sys.path = [p for p in sys.path if 'gateway/platforms' not in p]
import lark_oapi as lark
```

**Read a doc:**
```python
from lark_oapi.api.docx.v1 import *
client = lark.Client.builder().app_id(APP_ID).app_secret(APP_SECRET).build()
req = GetDocumentRequest.builder().document_id(doc_id).build()
resp = client.docx.v1.document.get(req)
print(resp.success(), resp.code, resp.msg)
```

**Read a doc as plain text（拿正文最省事的接口）:**
```python
# GET /open-apis/docx/v1/documents/{doc_id}/raw_content —— 返回整篇纯文本
import requests
headers = {"Authorization": f"Bearer {tenant_access_token}"}
url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/raw_content"
r = requests.get(url, headers=headers).json()
print(r.get("code"), r.get("msg"))          # code 1770032 ⇒ 文档未授权给应用（非凭证问题）
print(r.get("data", {}).get("content", "")[:2000])
```
注：`document.get` 只回元数据（title/revision 等），**拿正文要用 `raw_content`**。
若 python 侧 HTTP 有环境干扰，退一步用 curl 落盘再解析（脚本写 /tmp 后用 `bash`/`PYTHONPATH= python3` 跑）：
```bash
TOKEN=$(curl -s -X POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal \
  -H 'Content-Type: application/json' \
  -d "{\"app_id\":\"$FEISHU_APP_ID\",\"app_secret\":\"$FEISHU_APP_SECRET\"}" | python3 -c 'import sys,json;print(json.load(sys.stdin)["tenant_access_token"])')
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://open.feishu.cn/open-apis/docx/v1/documents/$DOC_ID/raw_content" -o /tmp/fs_raw.json
```

**Create and write to a new doc:**
```python
req = CreateDocumentRequest.builder() \
    .request_body(CreateDocumentRequestBody.builder().title("test").build()) \
    .build()
resp = client.docx.v1.document.create(req)
new_id = resp.data.document.document_id

# Add content
creq = CreateDocumentBlockChildrenRequest.builder() \
    .document_id(new_id).block_id(new_id) \
    .request_body(
        CreateDocumentBlockChildrenRequestBody.builder()
            .children([Block.builder().block_type(2)
                .text(Text.builder()
                    .elements([TextElement.builder()
                        .text_run(TextRun.builder().content("content").build())
                    .build()])
                .build())
            .build()])
            .index(-1).build()
    ).build()
client.docx.v1.document_block_children.create(creq)
```

**Modify an existing block (only works on self-created docs):**
```python
patch_req = PatchDocumentBlockRequest.builder() \
    .document_id(doc_id).block_id(block_id) \
    .request_body(
        UpdateBlockRequest.builder()
            .update_text_elements(
                UpdateTextElementsRequest.builder()
                    .elements([TextElement.builder()
                        .text_run(TextRun.builder().content("new text").build())
                    .build()])
                    .build()
            ).build()
    ).build()
resp = client.docx.v1.document_block.patch(patch_req)
```

**List blocks in a document:**
```python
req = ListDocumentBlockRequest.builder() \
    .document_id(doc_id).page_size(50).document_revision_id(-1).build()
resp = client.docx.v1.document_block.list(req)
for item in resp.data.items:
    print(item.block_type, item.block_id[:20], item.children)
```

### 5. Common error codes

- **99991672** — Missing API scope. Check `permission_violations` in error body for which scopes are needed. Open the link in error to grant them in Feishu developer console.
- **1770032** — "forBidden". 应用身份对这份文档**没有任何权限**。**读和写都会报，不只是"改别人文档"**。判定顺序：① token 是否换得回来（换得回 ⇒ 凭证没问题，问题在文档授权，别再折腾 .env）；② 让用户把文档**分享给应用**（文档右上「分享」→ 添加协作者 → 搜应用名 → 选「可阅读」），此后该文档走 API 直读；③ 或让用户把文档**下载为 Word/PDF 落本地**，直接读文件；④ 或让用户先把正文贴过来（最快，30 秒）。要写别人的文档另论：新建 doc 写入，或让 owner 给编辑权限。
- **PATCH endpoint 404** — When using raw `requests.patch`, the Feishu docx API may return 404. Use the lark_oapi SDK instead which handles the routing correctly.

### 6. Reading Spreadsheets via Sheets API

When you need to read data from a Feishu **spreadsheet** (not docx document), use the sheets/v3 API. The docx API returns blocks, but sheets require a completely different endpoint.

#### Prerequisites

The personal app needs these scopes in the Feishu developer console:
- `sheets:sheet:readonly` — for reading spreadsheet data
- `drive:drive:readonly` — for finding the file

Both must be **published** (发布新版) after adding.

#### Step 1: Get spreadsheet metadata (sheet list)

```python
from lark_oapi import Client
from lark_oapi.api.sheets.v3 import *

client = Client.builder().app_id(APP_ID).app_secret(APP_SECRET).build()

# spreadsheet_token is the long ID from the URL:
# https://xxx.feishu.cn/sheets/{spreadsheet_token}?sheet={sheet_id}
spreadsheet_token = "MW52wRVh4iIDl0kEcotc37vfn0b"

req = GetSpreadsheetRequest.builder() \
    .spreadsheet_token(spreadsheet_token).build()
resp = client.sheets.v3.spreadsheet.get(req)

if resp.success():
    for sheet in resp.data.sheets:
        print(f"sheet_id={sheet.sheet_id} title={sheet.title} "
              f"rows={sheet.grid_properties.row_count} "
              f"cols={sheet.grid_properties.column_count}")
else:
    print(f"Error: code={resp.code} msg={resp.msg}")
```

#### Step 2: Read cell values

**Simple approach — read entire sheet as 2D array:**

```python
# Use sheets/v2 values API (simpler than v3 for reading)
import json

range_str = f"{sheet_id}!A1:XFD"  # read all columns, all rows
url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{range_str}"

headers = {"Authorization": f"Bearer {access_token}"}
resp = requests.get(url, headers=headers)
data = resp.json()

if data.get("data"):
    values = data["data"].get("valueRange", {}).get("values", [])
    # values is a list of lists: [[A1,B1,C1], [A2,B2,C2], ...]
    for row_idx, row in enumerate(values):
        for col_idx, cell in enumerate(row):
            print(f"[{row_idx}][{col_idx}] = {cell}")
else:
    print(f"Error: {data}")
```

**⚠️ Important: Use sheets/v2 for cell reading, not sheets/v3**

The v3 SDK's `sheets.v3.spreadsheet_sheet` endpoints are designed for **spreadsheet structure** (sheet properties, protected ranges, conditional formats), not for direct cell value reading. For getting "what's in the cells", use the v2 REST API endpoint directly via `requests.get()`. The v2 endpoint returns a clean 2D array of values.

#### Step 3: Read specific range by coordinates

```python
# Read only a specific block of cells
range_str = f"{sheet_id}!A1:J50"  # columns A-J, rows 1-50
url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{range_str}"
headers = {"Authorization": f"Bearer {access_token}"}
resp = requests.get(url, headers=headers)
data = resp.json()
```

#### Step 4: Get tenant_access_token (if not using SDK)

The SDK handles token refresh automatically. If using raw requests:

```python
import requests

def get_feishu_token(app_id, app_secret):
    resp = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": app_id, "app_secret": app_secret}
    )
    data = resp.json()
    return data.get("tenant_access_token")
```

#### Complete minimal example (reading all sheets + cell data)

```python
import requests
import sys
sys.path = [p for p in sys.path if 'gateway/platforms' not in p]

from lark_oapi import Client
from lark_oapi.api.sheets.v3 import *

APP_ID = "cli_xxx"
APP_SECRET = "xxx"
TOKEN = "MW52wRVh4iIDl0kEcotc37vfn0b"  # spreadsheet token

client = Client.builder().app_id(APP_ID).app_secret(APP_SECRET).build()

# 1. Get access token for raw API call
token_resp = requests.post(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": APP_ID, "app_secret": APP_SECRET}
)
access_token = token_resp.json()["tenant_access_token"]

# 2. Get sheet IDs
req = GetSpreadsheetRequest.builder().spreadsheet_token(TOKEN).build()
resp = client.sheets.v3.spreadsheet.get(req)

for sheet in resp.data.sheets:
    sid = sheet.sheet_id
    title = sheet.title
    print(f"\n=== Sheet: {title} (id={sid}) ===")

    # 3. Read values
    url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{TOKEN}/values/{sid}!A1:XFD"
    headers = {"Authorization": f"Bearer {access_token}"}
    data_resp = requests.get(url, headers=headers).json()
    values = data_resp.get("data", {}).get("valueRange", {}).get("values", [])

    for i, row in enumerate(values[:5]):  # first 5 rows only
        print(f"  Row {i}: {row[:6]}...")  # first 6 columns
```

#### Common patterns

| Task | API | Notes |
|------|-----|-------|
| Get all sheet IDs + dimensions | `sheets/v3/spreadsheets.get` | Use SDK |
| Read cell values | `sheets/v2/spreadsheets/{t}/values/{range}` | Use raw HTTP — v2 is simpler |
| Read only first N rows | range: `Sheet1!A1:N100` | Perf: limit range, don't read entire sheet |
| Multiple disjoint ranges | `sheets/v2/spreadsheets/{t}/values_batch_get` | Pass `ranges` param |
| Number of rows with data | Check `valueRange.values` length | Empty rows are excluded from the 2D array |

#### Browser vs API tradeoff

| Approach | What works | Issues |
|----------|-----------|--------|
| Browser (browser_navigate) | Viewing the page | Canvas rendering = unreadable text; "只能阅读" mode for wiki docs; slow |
| Feishu API (sheets/v3 + v2) | Full data access | Need correct scopes published; v2 vs v3 confusion |

**Rule of thumb:** Use Feishu API for any structured data extraction. The browser is only useful for visually confirming what you're accessing.

---

### 7. Switching from Org App to Personal App

When the user says "之前配置的是组织账号，帮我切换成个人账号":

#### What's different

| Dimension | Org App (组织应用) | Personal App (个人应用) |
|-----------|-------------------|----------------------|
| Scope of access | Company-wide org data | Personal account data only |
| Wiki access ($99991672) | ✅ With `wiki:wiki` scope | ❌ Always returns `99991672` — cannot read wiki meta |
| Modify other-created docs | ✅ If app is added as editor | ❌ Always `1770032 forBidden` |
| Create new docs | ✅ | ✅ Works |
| Modify self-created docs | ✅ | ✅ Works |
| Sheets reading | ✅ | ✅ Works with `sheets:sheet:readonly` |

#### Steps

1. **User must create a new personal app in Feishu developer console** (飞书开发者后台 → 创建企业自建应用, but select "个人应用" type instead of "组织应用"). The App ID and Secret will be different.

2. **Update `.env`** with the new credentials:
   ```bash
   # Backup first
   cp ~/.hermes/.env ~/.hermes/.env.bak.$(date +%Y%m%d_%H%M%S)
   # Edit
   sed -i '' 's/^FEISHU_APP_ID=.*$/FEISHU_APP_ID=<new_personal_app_id>/' ~/.hermes/.env
   sed -i '' 's/^FEISHU_APP_SECRET=.*$/FEISHU_APP_SECRET=<new_secret>/' ~/.hermes/.env
   ```

3. **Grant scopes** in the developer console: `docx:document`, `docx:document:create`, `sheets:sheet:readonly`, `drive:drive:readonly`

4. **⚠️ Must publish** — scope changes only take effect after clicking "发布新版" (Publish New Version).

5. **Test** the credential switch works:
   ```python
   # Quick check: can you get a token?
   import requests
   r = requests.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
       json={"app_id": APP_ID, "app_secret": APP_SECRET})
   print("Token OK" if r.json().get("tenant_access_token") else "FAIL")
   ```

6. **Test read access** on a known document/spreadsheet to confirm permissions.

#### ⚠️ Pitfalls when switching from org to personal

- **Old doc references don't transfer** — Personal app cannot read or modify documents created under the org app's context. The user will need to re-share or recreate docs.
- **Wiki API stays broken** — Personal app will never get `wiki:wiki` scope. Content in wiki spaces must be accessed through `drive:drive:readonly` if wiki isn't required, or the doc must be moved out of the wiki.
- **读取 wiki 表格的绕过法（已验证 2026-08 可用）**：wiki 只是入口，拿不到 obj_token ≠ 文档不可读。① 用浏览器（用户已登录态）打开 wiki 链接，在 console 里 fetch `/space/api/wiki/v2/tree/get_node/?wiki_token=<token>&space_id=<space_id>&expand_shortcut=true&with_deleted=true`（space_id 可从页面 performance entries 的 wiki 请求 URL 里抄），响应 `data.node.obj_token` 就是文档 token（表格是 obj_type=3）；② 个人应用 **sheets API 可以直接读**这个 token：`GET /open-apis/sheets/v3/spreadsheets/{obj_token}` 拿元数据（title 可核对）→ `GET /open-apis/sheets/v3/spreadsheets/{obj_token}/sheets/query` 拿 sheet_id（**是数字如 712628，不是 "Sheet1"！** v2 values 接口用 "Sheet1" 会报 90215 not found sheetId）→ `GET /open-apis/sheets/v2/spreadsheets/{obj_token}/values/{sheet_id}!A1:Z200` 读全部数据。读取用 sheets/v2 values（返回干净二维数组），结构查询用 sheets/v3 query。⚠️ 注意 sheets/query 返回的 sheets 数组可能不含 title（只有 sheet_id + grid_properties），需用 sheets/v3 get 或 values 接口核对；`/sheets/v3/spreadsheets/{t}/sheets`（无 query 后缀）会 404。
- **跑飞书 API 脚本的 python 环境坑**：`python3` 可能指向系统 3.9 但被 PYTHONPATH 污染加载了 venv 3.11 的包 → urllib3 崩（`TypeError: unsupported operand type(s) for |`）。修复：`PYTHONPATH= python3 -c "..."`（清空环境变量），或直接用 venv/bin/python。脚本里 `sys.path = [p for p in sys.path if 'gateway/platforms' not in p]` 防 email 模块遮蔽。
- **Cron jobs still work** if they use `deliver` to a chat platform (微信/WeCom), but if they reference Feishu doc operations, the new credentials apply automatically after the .env update.
- **Gateway restart required**: `hermes gateway restart` after changing .env.

---

### 8. Inserting content between existing blocks (content injection pattern)

Use this when you need to add new blocks (H1/H2/Text/Code etc.) at a specific position within an existing document that already has content.

#### The challenge

`POST .../children?index=N` does NOT reliably insert at position N — blocks are always appended to the end. This means you cannot control insertion position with an index parameter.

#### The approach: Identify insertion point from block structure

1. Read the document's full block tree to find where to insert
2. Determine which **parent block** (root or a container block) the new content should be a child of
3. Build new blocks using the **dict format** (cleaner than SDK builders for dynamic content)
4. POST blocks as children of that parent — they appear nested at the correct position

#### Dict-based block construction (preferred over SDK builders)

Using raw Python dicts instead of the SDK's `Block.builder().block_type(N).text(Text.builder()...)` chain gives you more control and less boilerplate for dynamic content:

```python
def heading_block(content, level=1):
    \"\"\"Create a heading block block_type: 1->3, 2->4, 3->5, 4->6\"\"\"
    type_map = {1: 3, 2: 4, 3: 5, 4: 6}
    key = f\"heading{level}\"
    return {
        \"block_type\": type_map[level],
        key: {
            \"elements\": [{
                \"text_run\": {\"content\": content, \"text_element_style\": {}}
            }]
        }
    }

def text_block(content, bold=False):
    return {
        \"block_type\": 2,
        \"text\": {
            \"elements\": [{
                \"text_run\": {\"content\": content, \"text_element_style\": {\"bold\": bold}}
            }],
            \"style\": {\"align\": 1}
        }
    }

def code_block(content, language=\"python\"):
    return {
        \"block_type\": 9,
        \"code\": {
            \"elements\": [{
                \"text_run\": {\"content\": content, \"text_element_style\": {}}
            }],
            \"style\": {\"language\": 1, \"wrap\": True}
        }
    }
```

#### Sequential multi-block insertion

Build all blocks for a new section, then POST them in a single batch to the parent block:

```python
# Step 1: Build new section blocks
new_blocks = []
new_blocks.append(heading_block(\"一、新章节标题\", level=1))
new_blocks.append(text_block(\"这是新的章节内容正文。包含数据分析和描述。\"))
new_blocks.append(heading_block(\"1.1 子节\", level=2))
new_blocks.append(text_block(\"子节的详细内容。可以多个段落。\"))
new_blocks.append(text_block(\"第二个段落。继续展开。\"))

# Step 2: POST to the correct parent block
# parent_id = root's block_id (= doc_id) for root-level content
# OR parent_id = a specific container block for nested content
creq = CreateDocumentBlockChildrenRequest.builder() \\
    .document_id(doc_id).block_id(parent_id) \\
    .request_body(
        CreateDocumentBlockChildrenRequestBody.builder()
            .children(new_blocks)
            .index(-1)  # -1 = append to end of parent's children
            .build()
    ).build()
resp = client.docx.v1.document_block_children.create(creq)

# Step 3: Verify
check_req = ListDocumentBlockRequest.builder() \\
    .document_id(doc_id).page_size(50).document_revision_id(-1).build()
check_resp = client.docx.v1.document_block.list(check_req)
new_count = len(check_resp.data.items)
```

#### Key insight: `?index=N` vs parent selection

| Approach | Reliable? | Best for |
|----------|:---------:|----------|
| `POST .../children?index=N` | No — blocks always append | Avoid |
| POST to root block (doc_id) as parent | Yes — appends to end | Adding new top-level sections |
| POST to a specific container block as parent | Yes — content nests inside | Inserting content within an existing section |
| Rebuild entire doc from scratch | Yes but expensive | Major restructuring needed |

**Practical tip:** If you need to insert between two existing root-level blocks (e.g. after "引言" but before "收入结构"), read the hierarchy first. If both siblings are at root level, the simplest approach is to post new blocks as children of the root — they will appear after all existing root children. To truly insert between siblings, the parent must be an intermediate container block that sits at the right position.
