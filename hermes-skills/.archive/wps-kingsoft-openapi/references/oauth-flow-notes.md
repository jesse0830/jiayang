# WPS 开放平台对接调研记录（2026-08-07）

## 现状

- 用户提供 appid=`AK20260807SZZMPB`、appkey（个人应用），已存入记忆。
- 应用名 **JesseHermes**，模式=**企业自建应用**（WPS 365 企业版），归属组织 Jesse。
- OAuth 授权走到最后一步被拒：`NotCompanyUser`（授权账号 Jesse.Young 是个人账号，非企业成员）。
- 开发者后台入口弹窗："创建新团队/企业 | 进入已加入的企业 | *开发者后台仅限企业用户访问*"。
- 下一步（用户侧）：创建免费团队/企业 → 成为企业超管 → 重新授权。

## 已验证的 API 端点

| 端点 | 方法 | 用途 |
|---|---|---|
| `https://openapi.wps.cn/oauthapi/v2/authorize` | GET | 授权页（response_type=code&appid&redirect_uri&scope&state） |
| `https://openapi.wps.cn/oauthapi/v2/token` | GET | code 换 token（appid&appkey&code） |
| `https://openapi.wps.cn/oauthapi/v2/token/refresh` | POST | 刷新 token（appid&appkey&refresh_token） |

## 错误码实测

- 用 `scope=user_info,file,sheet` → `{"result":130032,"msg":"InvalidScope"}`（file/sheet 不存在）
- 用 `scope=user_info,cloud_file,dbsheet.all` + 未配置回调 → `{"result":130031,"msg":"RedirectUriNotConfig"}`
- 正确 scope + 正确回调 → 正常进授权页 → 授权后 `NotCompanyUser`

## 回调地址位置

- 用户先在「事件与回调→回调配置」填了 localhost:9999（那是消息推送回调，报"无效的请求"）
- 正确位置：新版后台 **「安全设置」**（旧版"基本设置"）
- 配置 `http://localhost:9999/callback` 后授权链跑通

## 本地回调服务（python 单文件）

```python
import http.server, urllib.parse, json, sys
SAVE = "/tmp/wps_oauth_code.json"
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        p = urllib.parse.urlparse(self.path); q = urllib.parse.parse_qs(p.query)
        json.dump({"code": q.get("code",[None])[0], "state": q.get("state",[None])[0]}, open(SAVE,"w"))
        self.send_response(200); self.send_header("Content-Type","text/html"); self.end_headers()
        self.wfile.write(b"<h2>OK</h2>")
    def log_message(self, *a): pass
http.server.HTTPServer(("127.0.0.1", 9999), H).serve_forever()
```

## scope 完整清单（权限说明页提取）

user_info(用户信息)、vas(WPS支付)、cloud_file(管理云文档文件)、file_selector(获取云文档文件)、corp_address_book(旧版通讯录)、corp_contacts.read/write、file_edit(在线编辑,应用授权)、app_files_synerg_mgr(应用文档管理)、form_builder、dbsheet.all(多维表格管理,用户授权)、dbsheet.webhook.write(多维表格webhook)。
