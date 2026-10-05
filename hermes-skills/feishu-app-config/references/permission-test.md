# Feishu Permission Diagnostic Script

Use this to test what a Feishu personal app can and cannot do after credential setup.

## Quick sanity check

```python
import sys
sys.path = [p for p in sys.path if 'gateway/platforms' not in p]
import lark_oapi as lark
from lark_oapi.api.docx.v1 import *

APP_ID = "<your_app_id>"
APP_SECRET = "<your_app_secret>"

client = lark.Client.builder().app_id(APP_ID).app_secret(APP_SECRET).build()

# 1. Create a document (tests docx:document:create)
req = CreateDocumentRequest.builder() \
    .request_body(CreateDocumentRequestBody.builder().title("权限测试").build()) \
    .build()
resp = client.docx.v1.document.create(req)
print(f"Create doc: success={resp.success()} code={resp.code}")
if not resp.success():
    print("Need scope: docx:document:create")
    exit()

new_id = resp.data.document.document_id
print(f"Created doc ID: {new_id}")

# 2. Add content to the new doc (tests write to self-created)
creq = CreateDocumentBlockChildrenRequest.builder() \
    .document_id(new_id).block_id(new_id) \
    .request_body(
        CreateDocumentBlockChildrenRequestBody.builder()
            .children([
                Block.builder().block_type(2)
                    .text(Text.builder()
                        .elements([TextElement.builder()
                            .text_run(TextRun.builder().content("测试内容").build())
                        .build()])
                    .build())
                .build()
            ])
            .index(-1).build()
    ).build()
cresp = client.docx.v1.document_block_children.create(creq)
print(f"Add content: success={cresp.success()} code={cresp.code}")

# 3. Read the new doc (tests docx:document)
rreq = GetDocumentRequest.builder().document_id(new_id).build()
rresp = client.docx.v1.document.get(rreq)
print(f"Read new doc: success={rresp.success()} code={rresp.code}")

# 4. Modify the new doc block (tests modify self-created)
lreq = ListDocumentBlockRequest.builder() \
    .document_id(new_id).page_size(50).document_revision_id(-1).build()
lresp = client.docx.v1.document_block.list(lreq)
if lresp.success() and lresp.data.items:
    bid = lresp.data.items[0].block_id
    preq = PatchDocumentBlockRequest.builder() \
        .document_id(new_id).block_id(bid) \
        .request_body(
            UpdateBlockRequest.builder()
                .update_text_elements(
                    UpdateTextElementsRequest.builder()
                        .elements([TextElement.builder()
                            .text_run(TextRun.builder().content("已修改测试内容").build())
                        .build()])
                        .build()
                ).build()
        ).build()
    presp = client.docx.v1.document_block.patch(preq)
    print(f"Modify self-created: success={presp.success()} code={presp.code}")

# 5. Try modifying an existing doc (tests: should fail for personal app)
# Replace with a real doc_id you cannot modify
# existing_doc = "some_doc_id"
# ...

print("\n=== Summary ===")
print("✅ Create doc     - tests docx:document:create")
print("✅ Write content  - tests write to self-created doc")
print("✅ Read doc       - tests docx:document")
print("✅ Modify self    - tests modify self-created")
print("❌ Modify other   - personal app cannot modify other-created docs (1770032)")
```

## Common failure modes

| Symptom | Likely cause |
|---------|-------------|
| `sys.path` pollution / import errors | `gateway/platforms/email.py` shadows stdlib — clean sys.path before import |
| `lark_oapi` not found | Run `pip3 install lark-oapi` |
| PATCH returns 404 | Use lark_oapi SDK instead of raw `requests.patch` |
| All write operations fail 1770032 | App only has read scopes — grant `docx:document:create` in developer console |
| Only self-created docs fail | Not possible — self-created docs always work; check other-created docs |
| Wiki operations fail 99991672 | Need `wiki:wiki` scope — not `docx:document` |
