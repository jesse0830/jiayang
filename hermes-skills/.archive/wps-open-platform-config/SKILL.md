---
name: wps-open-platform-config
description: "Configure WPS/金山文档 open platform OAuth app integration."
version: 1.0.0
---

# WPS 开放平台对接配置

对接 WPS/金山文档开放平台（open.wps.cn / WPS 365）——OAuth 授权、表格/文档 API 调用、凭证配置与排错。适用：用户想让我读写他的金山文档表格/文件、配置 appid/appkey、走 OAuth 授权流程。

## 触发场景
- 用户提供 WPS 开放平台 appid/appkey，要求对接（"可以和金山文档对接么"）
- 用户要求读写金山文档（表格/文档）
- OAuth 授权报错（InvalidScope / RedirectUriNotConfig / NotCompanyUser）需诊断

## 关键平台事实

### 1. 入口与开发者类型
- 开放平台：open.wps.cn（文档）＋ openapi.wps.cn（API）
- 开发者后台**仅限企业用户访问**——个人账号需先"创建新团队/企业"才能进后台
- 个人账号 + 服务商认证 = 可建"第三方个人应用"（无企业成员限制）
- 企业账号（WPS+超管）= 可建"企业自建应用"（授权时**必须**是组织成员，否则 NotCompanyUser）

### 2. OAuth 授权流程
```
1. GET https://openapi.wps.cn/oauthapi/v2/authorize
   ?response_type=code&appid=APPID&autologin=false&redirect_uri=CALLBACK&scope=SCOPES&state=STATE
2. 用户登录授权 → 重定向到 callback?code=CODE&state=STATE（code 10分钟有效，一次性）
3. GET https://openapi.wps.cn/oauthapi/v2/token?appid=&appkey=&code=CODE → access_token+refresh_token
4. POST https://openapi.wps.cn/oauthapi/v2/token/refresh?appid=&appkey=&refresh_token= → 刷新（refresh 90天）
```

### 3. scope 正确值（易错！）
| scope | 用途 |
|---|---|
| `user_info` | 获取用户信息（昵称头像） |
| `cloud_file` | 管理云文档文件（应用目录下） |
| `file_selector` | 交互方式获取用户所有文档 |
| `dbsheet.all` | 多维表格管理（用户授权可用） |

**坑**：`file`、`sheet` 等是**不存在的 scope**，会报 `InvalidScope`。个人应用读写表格用 `user_info,cloud_file,dbsheet.all`。

### 4. 错误码速查
| 错误 | 含义 | 解决 |
|---|---|---|
| `InvalidScope` | scope 拼错/不存在 | 用上表正确值 |
| `RedirectUriNotConfig` | 回调地址未配置/不一致 | 去后台安全设置配置 |
| `NotCompanyUser` | 企业自建应用，授权账号非组织成员 | 换个人应用，或把账号加入企业 |

### 5. 回调地址配置位置（易混）
- **正确**：开发者后台 → 应用 → **安全设置**（旧版叫"基本设置"）→ 授权回调地址
- **错误**：事件与回调 → 回调配置（那是消息推送/卡片交互用的，不是 OAuth 回调！）
- WPS 365 新版后台左侧菜单：基础信息/成员管理/应用能力/权限管理/事件与回调/安全设置/SSO配置等，"安全设置"才是配授权回调的地方

### 6. 本地回调接收（无公网服务器时）
起一个本地 HTTP 服务监听回调端口，授权完成后自动捕获 code：
```python
# python3 http.server 子类，do_GET 里 parse_qs 取 code，写文件 + 返回"已捕获"页面
# 监听 127.0.0.1:9999，回调地址配 http://localhost:9999/callback
```
⚠️ 注意：用远程浏览器（Browserbase）打开授权页时，授权完成后回调跳转发生在**远程浏览器环境**的 localhost，到不了用户本机——应让用户在**自己电脑的浏览器**打开授权链接，或直接从浏览器地址栏复制含 code 的回调 URL。

### 7. 表格数据读取（拿到 spreadsheet token 后）
个人应用 API 可直读表格（sheets 权限与 wiki 权限独立）：
```
元数据: GET /open-apis/sheets/v3/spreadsheets/{token}            → title/token
sheet列表: GET /open-apis/sheets/v3/spreadsheets/{token}/sheets/query → sheet_id, rows, cols
读数据: GET /open-apis/sheets/v2/spreadsheets/{token}/values/{sheet_id}!A1:Z100 → 2D数组
```
- wiki 链接（/wiki/xxx）拿不到 spreadsheet token 时：用**浏览器会话**调 `GET /space/api/wiki/v2/tree/get_node/?wiki_token=xxx`（带 cookie），响应里的 `obj_token` 就是 spreadsheet token
- 个人应用没有 wiki:wiki 权限（99991672），但拿到 obj_token 后 sheets API 可以直接读——**wiki 链接只是入口，表格本体权限够**

## 坑
- 凭证（appid/appkey）放记忆或 .env，不写进技能
- 授权必须用户本人操作（登录 WPS 账号、点同意），无法全自动
- 企业自建应用 + 个人账号 = 死路（NotCompanyUser），要么建个人应用，要么创建团队/企业

## 参考
- 2026-08-07 实例：用户 appid=AK2026... appkey 已存记忆，卡在企业自建应用 + 个人账号授权（NotCompanyUser），下一步是创建团队/企业
