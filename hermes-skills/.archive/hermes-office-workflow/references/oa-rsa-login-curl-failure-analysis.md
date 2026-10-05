# SmarDaten OA RSA加密登录 curl/requests 失败分析（2026-07-09）

## 背景

本会话尝试用 Python `requests` 库绕过浏览器直接调用 OA 登录 API。流程：

1. GET 登录页获取 cookie (XSRF-TOKEN)
2. GET `/sdata/rest/system/getPublicKey` 获取 RSA 公钥
3. 用 JSEncrypt (JavaScript) 加密密码
4. POST `/sdata/rest/system/login` 提交加密凭据 + 用户名

**结果：全部返回 401「访问接口未通过认证」**

## 核心发现：getPublicKey 本身也返回 401

最关键的发现是 **公钥获取接口也需要认证**：

```
GET /sdata/rest/system/getPublicKey
→ 401 访问接口未通过认证
```

这意味着：
- RSA 加密流程可能不是公开的 — 需要先建立 session 才能获取密钥
- 公钥可能被硬编码在前端 JS bundle 中（从 `oa_app.js` 中提取的密钥以 `MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCu` 开头，约164字符）
- 即使成功获取公钥并加密，登录 POST 仍然可能被拒绝

## 排查步骤

### 1. 确认 JS bundle 下载

```bash
# oa_app.js — 主应用 bundle（215KB），包含登录逻辑
# oa_vendor.js — 第三方库 bundle（58KB）
# jsencrypt.js — JSEncrypt 加密库（53KB），在 oa_login.html 中被加载
```

### 2. 确认登录接口

通过 JS bundle 中搜索找到的 login URL 模式：
- `getPublicKey` — 获取 RSA 公钥
- `login` — 登录提交

### 3. 尝试不同认证方式

| 尝试 | 结果 |
|------|------|
| 无任何认证头 | 401, traceId: `UCD服务` |
| Basic Auth (17705148484) | 401, traceId: `::3506::`（不同路由！） |
| Basic Auth (+test) | 401, traceId: `::3506::` |
| 带 XSRF-TOKEN cookie | 401 |
| RSA 加密密码后 POST | 401 |

Basic Auth 改变了 traceId，说明认证头确实影响了服务端路由。

### 4. Header 问题：`sdata—encrypt` 无效

OA 请求头 `sdata—encrypt` 中的连接线是**Em Dash (U+2014)**，不是 ASCII 连字符 `-`。在 Python 中：
```python
headers = {"sdata—encrypt": "true"}  # ❌ UnicodeEncodeError: em dash not valid HTTP header
```
浏览器实际发送的很可能就是普通连字符 `sdata-encrypt`。

## 结论：为什么用 requests 无法登录

### 原因 1：SPA 前端认证流程在后端无法重建

SmarDaten OA 的登录不仅是 POST 一个 url-encoded form。前端 SPA（React + qiankun）在登录过程中：
1. 在内存中维护一个 session 状态对象
2. 可能发送了额外的 HTTP 请求（如获取用户权限、租户信息）在登录之前或之后
3. 可能涉及 device fingerprint / user-agent 校验
4. 可能使用 WebSocket 或其他机制验证

所有这些都无法用 CLI curl/requests 重现。

### 原因 2：RSA 加密密钥可能已过期或被客户端拒绝

从 JS bundle 提取的公钥是一条静态字符串（`MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCu...`），约164字符。这个密钥可能：
- 是旧的/已轮换的公钥
- 仅用于演示或兼容旧版本
- 需要特定的版本头才能使用

### 原因 3：接口层面的统一认证拦截

所有 `/sdata/rest/` 开头的接口（包括 getPublicKey）都有一个统一的前置拦截器。它要求：
- 有效的 session cookie（非 XSRF-TOKEN 本身）
- 可能是基于时间戳的 token
- 或基于 IP + User-Agent 的会话绑定

### 原因 4：登录 URL 拼写错误

OA 登录页 `action="/application/login/1640627701456342"` 使用 **GET 方法**提交凭据（URL 参数 `?username=xxx&password=yyy`），而不是 POST 到 `/sdata/rest/system/login`。用 `browser_navigate` 打开该 GET URL 会直接触发登录流程（如果服务端 cookie 有效）。

## 正确的登录方式

基于以上分析，**唯一可靠的登录方式是通过浏览器**：

### 方案 A：用 browser 工具操作 SPA

1. `browser_navigate("https://oa.smardaten.com")` → 自动跳转到登录页
2. 等 React 渲染表单（`sleep 3`）
3. `browser_snapshot(full=true)` 找到输入框 ref
4. `browser_type(ref_username, "17705148484")`
5. `browser_type(ref_password, "xxx")`
6. 尝试 `browser_click(ref_login_btn)` 或 `browser_press(key="Enter")`
7. 检查登录结果（URL 变化、页面内容）
8. 成功后用 `browser_navigate` 跳转到目标模块

**已知问题：** `browser_click` 可能不触发 React 表单提交（SyntheticEvent 问题）。详见 `oa-portal-login-pitfalls.md`。

### 方案 B：浏览器手动登录 + 导出 Cookie

1. 用户在真正的浏览器中手动登录
2. 导出 Cookie（JSON 格式，带 `Domain=.smardaten.com`）
3. 在 Hermes 中用 `execute_code` 通过 Python `requests` + Cookie 直接访问目标页面
4. Cookie 有效期内可直接 GET 目标模块的 JSON 数据
5. Cookie 过期后重新导出

### 方案 C：传递已登录的 Browserbase/CDP session

如果 Hermes 使用的 browser 服务支持 session 持久化（如 Browserbase 的 session id），则：
1. 用户在一个 browser session 中手动登录
2. 将 session id 传给 Hermes
3. Hermes 通过 `browser_navigate` 在该 session 中打开目标 URL
4. 已登录状态自动继承

## 无法登录时的诊断清单

当 OA login 返回 401 时，按顺序检查：

1. **是 browser 还是 curl?** — curl/requests 大概率失败，坚持用 browser
2. **getPublicKey 是否也 401?** — 是 → 接口层全局拦截，需要完善 session
3. **Basic Auth 是否改变 traceId?** — 是 → 认证头影响路由，但不足以通过
4. **登录页是 GET method?** — `form[method=get]` → 凭据拼到 URL，不能 curl POST 模拟
5. **有无频率限制？** — 连续尝试 >3 次 → sleep 30s 再试
