# Feishu Document Copy Workflow

Copy a wiki/document content when the app can only read existing docs but cannot modify them (1770032 forBidden).
Strategy: create a new doc → read original block structure → rebuild block-by-block via raw API.

## When to use

- User wants you to "copy a wiki document to your own account" so you can edit it
- Personal app gets 1770032 forBidden when trying to modify someone else's document
- User says "直接复制一下创建个副本" — avoid overcomplicating this

## Key constraints

| Constraint | Detail |
|-----------|--------|
| Personal app write scope | Only docs created by the app itself (via API) |
| Table rows | Max **9 rows** per table. Split larger tables: 11→9+2 |
| Row × Col | Must be ≤ 45 |
| Divider (type 43) | Cannot be created via raw API (`invalid param`) — use `"─────"` TEXT block instead |
| Images (type 27) | Cannot be recreated via raw API — skip them |
| Embed (type 33) | Cannot be recreated — skip them |

## Block type mapping

| Original type | Raw API block_type | Key name |
|--------------|-------------------|----------|
| text | 2 | `text` |
| heading1 | 3 | `heading1` |
| heading2 | 4 | `heading2` |
| heading3 | 5 | `heading3` |
| bullet | 12 | `bullet` |
| ordered | 13 | `ordered` |
| table | 31 | `table` (with `property`) |
| divider | 43 | ❌ unsupported |
| image | 27 | ❌ unsupported |
| embed | 33 | ❌ unsupported |

## Workflow steps

### Step 1: Read original doc's block structure

Use `/open-apis/docx/v1/documents/{doc_token}/blocks` with full pagination.

The response has `parent_id` for each block. Build a `parent_children` dict to reconstruct hierarchy:

```python
parent_children = {}
for b in orig_blocks:
    pid = b.get("parent_id", "")
    bid = b.get("block_id", "")
    if pid not in parent_children:
        parent_children[pid] = []
    parent_children[pid].append(b)
```

Root blocks = `parent_children[doc_token]` (blocks whose parent is the doc itself).

### Step 2: Create new empty document

Use lark_oapi SDK:

```python
import lark_oapi as lark
from lark_oapi.api.docx.v1 import *
client = lark.Client.builder().app_id(APP_ID).app_secret(APP_SECRET).build()
req = CreateDocumentRequest.builder() \
    .request_body(CreateDocumentRequestBody.builder().title("title").build()).build()
resp = client.docx.v1.document.create(req)
new_id = resp.data.document.document_id
```

### Step 3: Rebuild blocks via raw API (NOT SDK)

The raw REST API at `/open-apis/docx/v1/documents/{doc_id}/blocks/{parent_id}/children`
is more reliable than the SDK for block creation, especially for tables.

**Batch creation** (3 per batch with 350ms delay):

```python
BASE = "https://open.feishu.cn/open-apis/docx/v1/documents"

def add_blocks(doc_id, parent_id, blocks_list):
    created = []
    for i in range(0, len(blocks_list), 3):
        batch = blocks_list[i:i+3]
        url = f"{BASE}/{doc_id}/blocks/{parent_id}/children"
        data = {"children": batch, "index": -1}
        r2 = requests.post(url, headers=headers, json=data)
        rd = r2.json()
        if rd.get("code") == 0:
            items = rd.get("data", {}).get("children", [])
            created.extend([it.get("block_id", "") for it in items])
        time.sleep(0.35)
    return created
```

### Step 4: Build each block type

**Text (type 2):**
```python
{"block_type": 2, "text": {"elements": [{"text_run": {"content": "content"}}]}}
```

**Heading (type 3-5):**
```python
{"block_type": 3, "heading1": {"elements": [{"text_run": {"content": "title"}}]}}
# type 4 → "heading2", type 5 → "heading3"
```

**Bullet (type 12):**
```python
{"block_type": 12, "bullet": {"elements": [{"text_run": {"content": "item"}}]}}
```

**Divider (type 43):** Unsupported. Use a text block instead:
```python
{"block_type": 2, "text": {"elements": [{"text_run": {"content": "─────"}}]}}
```

**Table (type 31):**
```python
{
    "block_type": 31,
    "table": {
        "property": {
            "row_size": rows,       # ≤ 9
            "column_size": cols,    # row*col ≤ 45
            "column_width": [100, 100, 100]  # one value per column
        }
    }
}
```

After creating a table, fill cells by getting the newly created cell blocks:

```python
r2 = requests.get(f"{BASE}/{doc_id}/blocks?page_size=200", headers=headers)
items = r2.json()["data"]["items"]
new_cells = [x for x in items if x["parent_id"] == table_id and x["block_type"] == 32]
for ci, old_cell in enumerate(cell_blocks):
    if ci >= len(new_cells): break
    cell_text = get_cell_text(old_cell["block_id"])
    if cell_text:
        curl = f"{BASE}/{doc_id}/blocks/{new_cells[ci]['block_id']}/children"
        cdata = {"children": [{"block_type": 2, "text": {"elements": [{"text_run": {"content": cell_text}}]}}], "index": -1}
        requests.post(curl, headers=headers, json=cdata)
        time.sleep(0.25)
```

### Step 5: Handle table row limits

If a table has > 9 rows, split it:

1. Read original table data: `cell_blocks = parent_children[table_id]`
2. `rows = len(cell_blocks) // cols`
3. `chunk1 = cell_blocks[:9*cols]`, `chunk2 = cell_blocks[9*cols:]`
4. Create two tables: one with 9 rows, one with remaining rows
5. Fill both tables with their respective cell data

### Step 6: Pagination for reading

When reading blocks, the API pages at 200 items:

```python
all_items = []
pt = None
while True:
    url = f"{BASE}/{doc_id}/blocks?page_size=200&document_revision_id=-1"
    if pt: url += f"&page_token={pt}"
    r2 = requests.get(url, headers=headers)
    rd = r2.json()
    all_items.extend(rd["data"]["items"])
    if rd["data"].get("has_more"):
        pt = rd["data"]["page_token"]
    else:
        break
```

## Common pitfalls

- **sys.path pollution**: `gateway/platforms/` has `email.py` that shadows stdlib. Fix:
  ```python
  import sys
  sys.path = [p for p in sys.path if 'gateway/platforms' not in p]
  ```
- **Table creation fails with `invalid param`**: Usually means rows > 9 or row*col > 45
- **Big tables silently fail**: The `add_blocks` function returns empty `created` list on failure — check for this
- **Old documents persist after creating new copies**: Clean them up via Drive API or tell the user
- **Variable name bugs in scripts**: When copying a script pattern, ensure variables like `new_id` / `new_doc_id` are consistently named
