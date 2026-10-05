---
name: wps-kingsoft-docs-integration
description: "WPS/金山文档 OAuth 对接：授权、token、云文档与多维表格 API。"
version: 1.0.0
created_by: agent
metadata:
  tags: [wps, kingsoft, kdocs, oauth, docs, spreadsheet, dbsheet, integration]
  languages: [zh-CN, en]
---

# WPS / 金山文档开放平台对接

用户用个人版金山文档（WPS），可创建开放平台应用后通过 OAuth 让 Hermes 读写其云文档/多维表格。平台入口 **https://open.wps.cn**，API 域名 **https://openapi.wps.cn**。文档是 SPA（curl 拿不到正文，`/docs/*` 直链会 301 回首页），**必须用浏览器走导航菜单读文档**：开发文档 → 服务端开发 → 左侧菜单。

## 触发条件

- 用户要求\"和金山文档/WPS对接\"、\"把文件传到金山文档\"、\"读写我的金山表格/多维表格\"
- 用户给出 WPS 开放平台的 appid/appkey
- 需要从金山文档拉数据或推数据

## 凭证与授权模式

- **appid + appkey**（个人应用/企业自建应用均有），用户给的值直接存记忆（用户明确同意\"可以放进记忆\"）。
- OAuth 两步：**authorize 拿 code → code 换 access_token**。access_token 短效，refresh_token 90 天（刷新接口 `POST /oauthapi/v2/token/refresh`）。
- **scope 必须用平台登记值**（`https://open.wps.cn/docs/scope` 权限说明表）：
  - `user_info` 获取用户信息
  - `cloud_file` 管理云文档文件（个人应用目录下文档）
  - `file_selector` 交互方式获取用户所有文档
  - `dbsheet.all` 多维表格管理（用户授权可用，配合 dbsheet.webhook.write 订阅变更）
  - ⚠️ 别发明 scope（如 `file`、`sheet`）→ 返回 `{"result":130032,"msg":"InvalidScope"}`。

## 授权流程（本地回调）

1. **配置授权回调地址**（见下方\"回调地址在哪配\"坑）。
2. **起本地回调服务**：用 `scripts/wps_callback_server.py`（监听 127.0.0.1:9999，GET /callback 把 code/state 存到 /tmp/wps_oauth_code.json 并回显成功页）。起后先 `curl http://localhost:9999/callback?code=test&state=x` 自测。
3. **拼授权 URL**（redirect_uri 与后台配置**完全一致**）：
   `https://openapi.wps.cn/oauthapi/v2/authorize?response_type=code&appid=APPID&autologin=false&redirect_uri=<urlencoded>&scope=user_info,cloud_file,dbsheet.all&state=hermes123`
4. **浏览器打开** → 出现\"XX申请登录并使用你的WPS账号\"授权页 → 点\"确认登录\" → 点\"授权\" → 浏览器跳回 localhost:9999 显示\"✅ 授权回调已捕获\"。
5. 回调服务捕获 code 后，用 `GET https://openapi.wps.cn/oauthapi/v2/token?appid=APPID&appkey=APPKEY&code=CODE` 换 access_token（注意文档写明 appkey/token 换票必须从服务器调，别在纯前端做）。
6. 拿到 token 后即可调个人文档/多维表格 API（个人应用目录 `cloud_file`、`dbsheet.all` 多维表格）。

## 回调地址在哪配（重要坑）

- **旧版后台**：应用「基本设置」→「授权回调地址」。
- **新版 WPS 365 后台（企业自建应用）**：左侧菜单没有\"基本设置\"字样，回调地址在 **「安全设置」**（或 SSO配置）里。用户会先找\"基本设置\"找不到 → 直接指到安全设置。
- **「事件与回调」→「回调配置」不是 OAuth 回调**！那是消息推送/卡片交互用的订阅配置，填 OAuth 回调地址会报\"无效的请求\"。
- 未配置/不一致 → `{"result":130031,"msg":"RedirectUriNotConfig"}`。
- `localhost` 可能不被接受时换 `http://127.0.0.1:9999/callback` 试。

## 企业自建应用 vs 个人应用（本会话卡点）

- **企业自建应用**（WPS 365 企业版后台创建）：授权时要求**授权用户必须是该企业组织成员**。个人账号（如 Jesse.Young 个人账号）授权会失败：授权页跳 `https://openapi.wps.cn/view/person/error?code=NotCompanyUser`（\"仅企业成员可使用\"）。
- 用户用**个人版**金山文档时：应创建/切换为**第三方个人应用**（个人账号可授权，无企业成员限制），而不是企业自建应用。⚠️ 此方向已诊断、未验证完成（本会话停在 NotCompanyUser，下一步是让用户在开发者后台新建第三方个人应用或用企业账号授权）。
- 判断应用类型：登录后台看应用信息页，\"应用模式\"字段显示\"企业自建应用\"/\"第三方个人应用\"。

## 权限清单参考（从 /docs/scope 提取，用户授权类）

user_info（用户信息）、vas（WPS支付）、cloud_file（管理云文档）、file_selector（获取云文档）、dbsheet.all（多维表格）、dbsheet.webhook.write（多维表格订阅）、corp_contacts.read/write（企业通讯录）、corp_files_synerg_mgr（企业文档）、kmeeting（金山会议）、calendar.write（日程）等。企业类权限需企业授权。

## 参考文件

- `scripts/wps_callback_server.py` — 本地 OAuth 回调接收服务（127.0.0.1:9999），起后台进程 + curl 自测 + 授权后读 /tmp/wps_oauth_code.json 拿 code。
