---
name: wps-kingsoft-openapi
description: "WPS/金山文档开放平台对接：OAuth 授权、个人/企业应用差异、表格读写。"
version: 1.0.0
created_by: agent
metadata:
  tags: [wps, kingsoft, kdocs, oauth, spreadsheet, openapi]
  languages: [zh-CN]
---

# WPS/金山文档开放平台对接

适用于用户要求"和金山文档对接/把文件同步到金山文档/从金山文档拉数据"等场景。官方平台：open.wps.cn（文档 SPA，curl 拿不到内容，需浏览器）。

## 关键事实

- **开发者类型**：个人账号可注册"第三方个人应用"；WPS+ 企业超管可建"企业自建应用"（JesseHermes 案例：个人账号在 WPS 365 里创建的应用是**企业自建应用**，授权时要求用户是企业成员）。
- **开发者后台仅限企业用户访问**：个人账号进入 open.wps.cn 开发者后台会看到"创建新团队/企业"或"进入已加入的企业"两个入口；个人用户需**自己创建免费团队**才能成为企业超管。
- **应用信息**：appid（如 `AK20260807SZZMPB`）、appkey 在应用"基础信息"页；用户已授权，凭证存于记忆/凭据库。

## OAuth 授权流程

1. **构造授权链接**：
   `https://openapi.wps.cn/oauthapi/v2/authorize?response_type=code&appid=<APPID>&autologin=false&redirect_uri=<URLENCODED>&scope=<URLENCODED>&state=<任意>`
2. 浏览器打开 → 用户登录 WPS 账号 → 同意授权 → 重定向到 redirect_uri 带 `code`
3. **换 token**：`GET https://openapi.wps.cn/oauthapi/v2/token?appid=<APPID>&appkey=<APPKEY>&code=<code>` → 返回 `token.access_token` + `refresh_token`（90 天）+ `openid`
4. **刷新 token**：`POST https://openapi.wps.cn/oauthapi/v2/token/refresh?appid=...&appkey=...&refresh_token=...`

## scope 值（必须用准确值，否则 InvalidScope）

| scope | 含义 |
|---|---|
| `user_info` | 获取用户信息（头像/昵称） |
| `cloud_file` | 管理云文档文件（应用目录下） |
| `file_selector` | 获取云文档文件（交互方式） |
| `dbsheet.all` | 多维表格管理 |
| `file_edit` | 文档在线编辑（应用授权） |

> ⚠️ 不存在的 scope（如 `file`、`sheet`）会返回 `130032 InvalidScope`。

## 常见错误码

| 错误 | 含义 | 解决 |
|---|---|---|
| `130031 RedirectUriNotConfig` | 回调地址未配置 | 在开发者后台配置授权回调地址 |
| `130032 InvalidScope` | scope 值不对 | 用上表准确 scope |
| `NotCompanyUser` | 应用是企业自建应用但授权账号非企业成员 | 创建免费团队/企业，或用企业成员账号授权 |

## 回调地址配置位置（重要）

- **旧版后台**：应用"基本设置"页 → 授权回调地址
- **新版 WPS 365 后台（企业版）**：左侧菜单 **「安全设置」**（旧版"基本设置"被拆分，**不是**"事件与回调"里的回调配置——那是消息推送用的）
- 本地接收：`python3 -c` 起一个 HTTP 服务监听 9999 端口捕获 code（`http.server` + `BaseHTTPRequestHandler`），回调 URL 填 `http://localhost:9999/callback`

## 表格读写（个人文档 API）

- 读取/写入需先拿 access_token，请求头 `Authorization: Bearer <token>`
- 个人文档接口前缀：`https://openapi.wps.cn/...`（具体路径以官网文档为准，文档是 SPA 需浏览器逐级点击导航进入）
- 多维表格接口独立于普通表格

## 坑与经验

- **SPA 文档抓取**：open.wps.cn 文档是 Vue SPA，curl 只见 `<div id=app>`，需浏览器 navigate 后从导航菜单逐级点击（快速入门 → 服务端开发 → 权限说明），或从页面 console 里 `document.querySelectorAll('a')` 提取真实 href（如 `/docs/scope`）。
- **个人版对接前提**：注册开发者应用 + 服务商认证（可能需审核数天）；个人应用用不了企业文档/团队管理，但个人文档、多维表格够用。
- **本地回调**：OAuth code 只回跳到 redirect_uri；本地开发用 localhost 端口 + 自建 HTTP 服务最方便。
- **未完成事项（2026-08）**：JesseHermes 应用（企业自建应用）授权遇 NotCompanyUser，用户需创建免费团队后重试；创建团队若要求企业资质认证（营业执照）则需换思路。

## 参考文件

- `references/oauth-flow-notes.md` — 本次对接的完整调研记录（授权链、scope 表、错误码、后台导航路径）。
