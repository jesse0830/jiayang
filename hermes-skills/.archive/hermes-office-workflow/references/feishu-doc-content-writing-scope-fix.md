# 飞书文档内容写入：权限错误 1770032 排查

## 症状

飞书 API token 获取正常，GET 请求成功（读取文档内容），但 PATCH/POST/DELETE 操作返回 403 错误：

```json
{"code": 1770032, "msg": "forBidden", "data": {"method_id": "docx_block_update"}}
```

## 根因

飞书应用配置的权限 scope 只有 **`drive:drive:readonly`**（只读），没有 **`drive:drive`**（读写）。

这两个权限的差异：

| Scope | 用户可见文本 | 支持的操作 |
|-------|------------|-----------|
| `drive:drive` | "云文档" | 对云文档的所有内容（包括文档、电子表格等）有读、写和管理权限 |
| `drive:drive:readonly` | "云文档只读" | 仅读取云文档内容 |

**关键点：** `drive:drive:readonly` 不是 `drive:drive` 的子集——它们是两个独立的 scope。只申请 `readonly` 意味着系统只授权了 GET 请求。

## 修复步骤

1. **登录飞书开发者后台** → 应用管理 → 选择你的应用
2. **权限管理** → 找到「云文档」分类 → 勾选 `drive:drive`（不要只勾 `drive:drive:readonly`）
3. **版本管理与发布** → 创建新版本 → 输入版本号/说明 → 提交发布
   - ⚠️ 发布需要**管理员审批**（如果非管理员创建的应用）
   - 发布后通常 1-5 分钟生效
4. **重新获取 token**（旧 token 不包含新 scope 的授权时间）

## 验证修复

```python
import json, urllib.request

# 获取新 token
app_id = "cli_xxxxx"
app_secret = "xxx"

url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
data = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode()
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
resp = json.loads(urllib.request.urlopen(req).read())
token = resp["tenant_access_token"]

# 测试写操作——创建一个简单的文本 block 更新
doc_id = "your_doc_id"
block_id = "your_block_id"  # 找一个已有的文本 block
test_body = {
    "update_text_elements": {
        "elements": [{"text_run": {"content": "权限测试 - 写入成功", "text_element_style": {}}}],
        "style": {}
    }
}
req = urllib.request.Request(
    f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{block_id}",
    data=json.dumps(test_body).encode(),
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    method="PATCH"
)
try:
    resp = json.loads(urllib.request.urlopen(req).read())
    print(f"写入成功: {resp}")
except urllib.request.HTTPError as e:
    body = e.read().decode()
    print(f"仍失败: {e.code} body={body}")
```

## 注意

- **本用户（杨嘉阳）的飞书应用当前只有 `drive:drive:readonly`**
- 如果要通过 Hermes 的 API 写入飞书文档，必须先完成上述修复步骤
- 临时替代方案：浏览器打开文档手动编辑，或者输出 markdown 文件让用户粘贴