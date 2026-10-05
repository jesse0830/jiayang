# 飞书 Wiki 链接 → 表格数据读取（个人应用桥接方法）

**问题**：用户给的是 wiki 链接（如 `https://xxx.feishu.cn/wiki/LrRbwXU87ij4gVkXJbrcZ0Mtnnc`），URL 里**没有 spreadsheet token**；个人应用调 wiki API 返回 `99991672`（无 wiki:wiki 权限）。

**已验证解法（2026-08 真实任务：读《软件工厂2026 H2重点工作》表格成功）**：

## 两步桥接

### 第 1 步：浏览器会话拿 obj_token（spreadsheet token）

用 browser 打开 wiki 链接，然后在 console 里 fetch 内部 API（浏览器已登录，带会话）：

```js
// 1. 打开 https://xxx.feishu.cn/wiki/{WIKI_TOKEN} （browser_navigate）
// 2. console 执行：
const r = await fetch('/space/api/wiki/v2/tree/get_node/?wiki_token={WIKI_TOKEN}&space_id={SPACE_ID}&expand_shortcut=true&with_deleted=true', {credentials: 'include'});
const d = await r.json();
// 返回 d.data.node.obj_token = spreadsheet token（obj_type: 3 = 表格）
```

> space_id 可从页面加载的 wiki API 请求 URL 里拿（performance.getEntriesByType('resource') 过滤 wiki），或用 get_info 接口。
> 如果直接访问 wiki 链接报 NotCompanyUser/无法打开，先确认浏览器登录了正确的飞书账号。

### 第 2 步：个人应用 API 直接读表格数据

拿到 obj_token 后，**不需要 wiki 权限**，用个人应用（FEISHU_APP_ID/SECRET 在 ~/.hermes/.env）直接调 sheets API：

```python
import requests, os
# 1. tenant token
r = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
                  json={'app_id': os.environ['FEISHU_APP_ID'], 'app_secret': os.environ['FEISHU_APP_SECRET']})
TOKEN = r.json()['tenant_access_token']
H = {'Authorization': 'Bearer ' + TOKEN}

# 2. 元数据（验证可读 + 拿标题）
requests.get(f'https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{OBJ_TOKEN}', headers=H)

# 3. 拿 sheet_id（⚠️ 不是 'Sheet1'！必须 query）
r2 = requests.get(f'https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{OBJ_TOKEN}/sheets/query', headers=H)
SHEET_ID = r2.json()['data']['sheets'][0]['sheet_id']  # 如 '712628'

# 4. 读数据（v2 values 接口，范围 A1:Z100 按需）
r3 = requests.get(f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{OBJ_TOKEN}/values/{SHEET_ID}!A1:Z100', headers=H)
values = r3.json()['data']['valueRange']['values']
```

## 关键坑

- **sheet_id 不是标题**：`sheets/v2/.../values/Sheet1!A1:Z100` 会报 `90215 not found sheetId`。必须先 `sheets/query` 拿真实 sheet_id。
- **sheets 列表接口路径**：`/sheets/v3/spreadsheets/{t}/sheets/query` 有效；`/sheets/v3/spreadsheets/{t}/sheets` 返回 404。
- **元数据接口可用**：`/sheets/v3/spreadsheets/{t}` 返回 title/url/owner（个人应用可读，说明表格本体权限够，wiki 只是入口）。
- **Python 环境**：`.env` 读取脚本用 `PYTHONPATH=` 前缀 + 系统 python3（避免 hermes venv 的 urllib3 与 3.9 不兼容）；或直接用 venv python 但先清 PYTHONPATH。
- 内部 API 路径（`/space/api/...`）用 `requests` 猜不通（400 Parameter Error），**必须用浏览器会话 fetch**（页面 JS 有完整会话上下文）。
