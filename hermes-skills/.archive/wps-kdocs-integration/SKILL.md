---
name: wps-kdocs-integration
description: "对接WPS/金山文档开放平台：OAuth授权、个人文档与多维表格API。"
version: 1.0.0
metadata:
  tags: [wps, kdocs, 金山文档, oauth, api, integration, chinese]
  languages: [zh-CN, en]
---

# WPS / 金山文档开放平台对接

连接 Hermes 与 WPS/金山文档（open.wps.cn）：把本地 xlsx 传到金山文档、读写多维表格、按用户指令操作云文档。个人版应用即可用（用户 SmarDaten 场景）。

## 凭证与状态（2026-08-07 更新）

- appid=`AK20260807SZZMPB`，appkey 见 memory（WPS_APPKEY 条目）。应用名 **JesseHermes**，类型 = **企业自建应用**（用户后台是 WPS 365 新版，左侧菜单：基础信息/成员管理/应用能力/权限管理/事件与回调/安全设置/SSO配置…）。
- **⚠️ 当前卡点**：个人账号授权报 `NotCompanyUser`（企业自建应用要求授权用户是企业成员）；**开发者后台仅限企业用户访问**（个人账号进后台提示"创建新团队/企业"或"进入已加入的企业"）。个人用户需先创建团队/企业才能继续。解决方向：a) 创建"第三方个人应用"（若后台支持切换应用类型）b) 创建/加入企业组织后用企业账号授权。
- 用户明确同意 appid/appkey 存入 memory，非高敏感。

## OAuth 授权流程（一次性，用户参与）

1. **scope 必须用合法值**：`user_info,cloud_file,dbsheet.all`（逗号分隔）。用 `file`/`sheet` 等非法值会报 `InvalidScope`（result 130032）。
2. **回调地址配置位置 = WPS 365 新版后台「安全设置」页**（不是「事件与回调」里的"回调配置"——那是消息推送用的；新版后台没有"基本设置"这个词）。填 `http://localhost:9999/callback` 或 `http://127.0.0.1:9999/callback`。没配会报 `RedirectUriNotConfig`（result 130031）。
3. 授权 URL（redirect_uri/scope 需 URL 编码）：
   `https://openapi.wps.cn/oauthapi/v2/authorize?response_type=code&appid=APPID&autologin=false&redirect_uri=http%3A%2F%2Flocalhost%3A9999%2Fcallback&scope=user_info%2Ccloud_file%2Cdbsheet.all&state=xxx`
4. 用户浏览器同意授权 → 重定向回 redirect_uri 带 `?code=CODE&state=STATE`（code 仅一次有效、10 分钟过期）。
5. 换 token：`[GET] https://openapi.wps.cn/oauthapi/v2/token?appid=APPID&appkey=APPKEY&code=CODE` → `token.access_token/refresh_token/openid`。
6. 刷新：`[POST] https://openapi.wps.cn/oauthapi/v2/token/refresh?appid=APPID&appkey=APPKEY&refresh_token=REFRESH`。refresh_token 90 天，刷新后旧的失效。

## scope 权限速查（用户授权类，个人版可用）

| scope | 用途 |
|---|---|
| `user_info` | 获取用户昵称/头像 |
| `cloud_file` | 管理应用目录下的云文档文件 |
| `file_selector` | 交互式获取用户所有文档 |
| `dbsheet.all` | 多维表格 CRUD（数据表/记录/视图） |
| `dbsheet.webhook.write` | 多维表格变更 webhook 订阅 |

企业版才有的（个人版申请不到）：corp_*、admin_*、audit_log、kmeeting、calendar.write、enterprise_email.* 等。

## API 域与文档站

- 开放平台文档站：open.wps.cn（SPA，**curl 拿不到内容**——`We're sorry but open doesn't work properly...`；必须浏览器导航，且 `/docs/xxx` 直链会重定向回首页，只能从导航菜单点击进入。权限清单在 `https://open.wps.cn/docs/scope`，但同样要浏览器打开）
- API 域：`openapi.wps.cn`（oauthapi、个人文档、多维表格接口都在这）

## 坑

- **⚠️ 远程浏览器 localhost 陷阱**：Hermes 的 browser 工具是远程浏览器（Browserbase），它的 localhost ≠ 用户电脑的 localhost！在远程浏览器里完成 OAuth 授权后，code 回调会打到远程容器，用户本机收不到。**正确做法：把授权 URL 给用户，让用户在本地浏览器打开完成授权**，用户本机的 9999 服务才能收到 code。
- **本地回调接收服务**（无公网服务器方案）：本机起 http server 监听 9999 端口，do_GET 解析 query 的 `code`/`state` 写到 `/tmp/wps_oauth_code.json`，返回"✅ 已捕获"HTML 页。起服务后先 `curl "http://localhost:9999/callback?code=test"` 自测。脚本模式：`python3 /tmp/wps_callback_server.py`（后台运行）。
- **WPS 文档站是纯 JS SPA**：curl/grep 抓不到正文，别浪费时间；用 browser_navigate + 菜单点击，或 console 里 `document.querySelectorAll('a')` 找真实 href（如 `/docs/scope`）。
- 授权页文案"仅企业成员可使用"= 账号类型不匹配（个人账号 + 企业自建应用 → NotCompanyUser），不是 scope 问题。
- 测试接口别瞎猜路径：`/oauthapi/v2/userinfo` 不存在（404），从文档里抄。
- 个人版应用**没有**企业文档/团队/通讯录能力，只有个人文档 + 多维表格 + user_info。
- 文件/表格 API 的具体端点（上传、读表、写记录）需要时再查文档站对应菜单（个人文档 → 个人文档接口；多维表格管理 → 接口列表）。
