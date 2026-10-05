# SmarDaten OA 登录踩坑实录（2026-07）

## 问题诊断树

登录 OA 失败时，按此树状结构定位问题：

```
登录失败
├── 浏览器报错页面空白/404
│   └── SPA 未渲染 → 等 3-5 秒重试 snapshot
├── "用户名或密码错误"
│   ├── 确认键盘输入无误（browser_console 检查 input.value）
│   ├── 确认密码中的特殊字符（`.` `..` `@` `#`）被正确输入
│   └── 换手动登录验证凭据是否过期
├── "登录错误次数太多，请稍后重试"
│   ├── sleep(30) 等待频率限制解除
│   ├── 然后 browser_navigate(url) 重新加载干净的登录页
│   └── 一次成功登录，不要再反复试
├── 按钮点击后无反应（页面不跳转）
│   ├── React SPA 事件系统问题 — browser_click 可能不触发 onSubmit
│   ├── 尝试 browser_press(key="Enter") 提交表单
│   ├── 尝试用 JS 触发 onSubmit: form.dispatchEvent(new Event('submit'))
│   └── 或者用 React fiber 树找到真正的 onSubmit 并调用
├── 弹出"密码需要更新"弹窗
│   └── 走密码更新流程（见 oa-portal-data-extraction.md）
└── CAPTCHA 验证码错误
    ├── 数学题验证码答案错误（输入了错误的数字）
    ├── 验证码过期（页面刷新后旧验证码无效）
    └── 连续错误触发频率限制
```

## 已知坑点

### 1. React SPA 登录按钮点击不触发表单提交

**现象：** `browser_type` 填入账号密码后，`browser_click(ref="e5")` 点击"登录"按钮，页面 URL 不跳转，没有新网络请求。

**原因：** OA 登录页是 **React Ant Design 单页应用**。`browser_click` 的底层是模拟鼠标点击事件（pointerdown/pointerup/click），但 React 的 `onFinish`/`onSubmit` 事件处理可能需要完整的 **合成事件（SyntheticEvent）** 传播链。当点击未触发 React 的事件分发时，表单不会提交。

**已尝试失败的方案：**
- `browser_click(btn)` — 无反应
- `browser_press(Enter)` — 无反应
- `form.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}))` — 返回 `false`（被阻止了）
- `fetch()` 直接 POST/OA 登录 URL — CORS 错误，不可能跨域

**部分有效的方案（不稳定）：**
- 在浏览器中注入 `window.fetch` 代理拦截登录请求 → 但 SPA 的登录流程可能不走 fetch
- 经过多次尝试后某一次突然成功（原因不明）— 可能是浏览器缓存/渲染时机问题

**建议应对策略：**
1. 先确认页面已完全渲染：`browser_snapshot(full=true)` 确保输入框和按钮都可见
2. 填入凭据后，用 `browser_console` 检查输入值确认无误
3. 尝试 `browser_click(ref)` 配合 `browser_press(key="Enter")` 的组合
4. 如果连续失败，`browser_navigate` 重新加载登录页从头开始
5. 不要连续快速尝试超过 3 次（会触发频率限制）
6. **终极方案：** 手动在浏览器中登录成功 → 导出 Cookie → 交给终端 curl 使用

### 2. 频率限制机制

**触发条件：** 连续 4-5 次登录失败（包括有效凭据但 React 事件未触发的失败，也算一次失败的登录尝试）

**错误提示：** "用户登录错误次数太多，请稍后重试"

**恢复时间：** 约 30 秒（实测）

**正确恢复流程：**
```
1. browser_navigate(url)  → 回到干净的登录页
2. sleep(30)              → 等待限时解除
3. 填入账号密码
4. 登录（尝试一次，不要反复点）
```

**不要做：**
- ❌ 在限时窗口内反复点击 — 不会成功，还会延长限时
- ❌ 刷新页面后立即重试 — 限时是服务端的，刷新不清除
- ❌ 多开浏览器窗口同时尝试 — 每个窗口独立计数

### 3. GET 方法的登录表单

OA 登录表单的 `method="get"`（不是常规的 POST），这意味着：
- 提交时凭据会拼接到 URL 上：`/application/login/1640627701456342?username=xxx&password=yyy`
- 通过 curl 直接访问该 URL 返回 404（需要 SPA 渲染，前端处理认证后才跳转）
- **curl / requests 不能直接登录 OA** — 凭据暴露在 URL 中是设计使然，但后端仍校验 session

### 4. SPA 页面是空壳

登录页的 `document.documentElement.outerHTML` 返回：
```html
<html><head></head><body></body></html>
```

所有内容由 JavaScript 动态加载（Ant Design + qiankun 微前端）。这意味着：
- 不能通过 `curl` 获取登录页内容来分析表单结构
- 必须使用完整的浏览器渲染
- 不能直接 GET 登录后的目标 URL（需要 JS session）

### 5. 页面元素 ref 稳定性

`browser_snapshot` 返回的 ref（如 `e2`、`e3`、`e5`）在同一个页面加载内是稳定的：
- `@e2` = 用户名输入框
- `@e3` = 密码输入框
- `@e5` = 登录按钮

但如果 `browser_navigate` 重新加载页面，ref 可能会重新编号。

### 6. CAPTCHA 验证码阻塞（数学题 + base64 PNG）

**现象：** 登录页有「图片验证码」，内容是数学题（如 `"2+3=?"`），用户必须输入正确答案才能登录。

**验证方式：** server-side only 验证。前端通过 `POST /api/blade-auth/oauth/captcha` 获取验证码，返回：`{code:200, data:{key: UUID, imageBase64: <base64 PNG>}}`。key 是服务端关联验证码题的 ID，imageBase64 是答案的图片表示。前端提交时同时传 `captchaKey` + `captchaCode`（用户输入的答案）。

**无 calcResult 字段：** 这个 API 的 response 中没有 calcResult（或类似明文答案字段）。验证码值仅存放在服务端 session 中。不能在客户端直接读取答案。

#### 自动识别障碍

| 方法 | 结果 | 原因 |
|------|------|------|
| Tesseract OCR (PSM 7/8/13) | ❌ 全部返回空 | 验证码有噪点/干扰线，Tesseract 无法定位文本 |
| 模型 vision 分析 | ❌ 取决于模型 | deepseek-chat 不支持 image_url 消息类型；需 vision-capable 模型 |
| PIL/Python 预处理后 OCR | ❌ 图片数据流损坏 | base64 → PNG 解码时出现 "broken data stream"（可能是传输截断） |
| 用户手动查看截图 | ✅ 可识别 | "2+3=?" — 人类一眼就能看懂，答案是 5 |

#### 验证码获取流程（完整 base64 提取）

```javascript
// Step 1: 调用验证码 API
fetch('/api/blade-auth/oauth/captcha', {method:'POST'})
  .then(r => r.json())
  .then(d => {
    window._captchaKey = d.data.key;
    window._full_b64 = d.data.imageBase64;
  });

// Step 2: 提取完整 base64（含 data:image/png;base64, 前缀）
// 使用 split(',')[1] 去掉前缀，获取纯 base64 数据
const raw = window._full_b64;  // e.g. "data:image/png;base64,iVBOR..."
const b64 = raw.split(',')[1]; // e.g. "iVBORw0KGgo..."

// Step 3: 纯 base64 写入文件（约 5300-5500 字节）
// 注意：如果 base64 从浏览器到 Python 被截断，解码的 PNG 会损坏
```

**⚠️ base64 传输截断问题：** 当 base64 字符串从 browser_console 传到 Python 时可能被截断或编码错误。如果 PIL 报 "broken data stream"，原始 base64 可能不完整。建议用 `write_file` 直接保存完整 base64 字符串，然后用 Python 解码。

#### 如果模型不支持 vision 分析的替代方案

1. **用户手动查看截图** — 用 screenshot 保存到文件，让用户肉眼查看并告知验证码内容
2. **切换到带 vision 的模型** — 选择支持图片分析的 provider/model（如 Claude Sonnet、Gemini）
3. **绕过方案（仅限测试）** — 如果只是为了测试登录流程，可以在开发环境关闭验证码

#### 验证码过期处理

每次页面刷新/重导航都会生成新的验证码（新的 key + 新图片）。一个验证码值只在当前登录 session 中有效。如果 `browser_navigate` 重新加载了登录页，之前从截图中识别的答案就失效了，必须重新获取并识别。

**⚠️ 特别陷阱：点击验证码图片本身也会触发页面变空 + 验证码更新**
- 点击验证码图片（无头浏览器中）会触发 SPA 重渲染 → 页面变空 → 必须重新 navigate → 新的验证码
- **最佳实践：不要在填好账号密码后去点验证码图片。** 直接截屏问用户，拿到答案后一次性完成所有输入和提交。

#### 频率限制与验证码的关系

- 即使验证码正确，连续 4-5 次登录失败也会触发频率限制
- 错误的验证码返回 `{code:500, msg:"图片验证码错误"}`，也算一次失败尝试
- 正确流程：获取验证码 → 填入答案 → 提交 → 如果失败，等待 30 秒后再试

### 7. 页面状态活性陷阱：点击任意交互元素后页面变空

**现象：** 在登录页状态下，点击以下任意元素后，`browser_snapshot()` 返回 `"(empty page)"`：
- 点击验证码图片（@e6）刷新验证码
- 点击登录按钮（无论成功还是失败，表单校验失败时）
- 点击其他交互式元素（如眼睛图标切换密码可见性、close-circle 错误提示条）

**原因：** OA 的 React SPA 在交互事件触发后可能触发完整的组件树重渲染。在重渲染期间，accessibility tree 为空，所有之前定位的 ref ID（@e2/@e3/@e5 等）立即失效。这不是普通的重绘——它是 DOM 树级的卸载→重建。

**恢复流程（必须完整执行，不要跳过任何步骤）：**
```python
# ❌ 错误：尝试点击空白页上的元素
browser_click(ref="@e1")  # 可能触发登录页弹窗但ref已失效

# ✅ 正确：完整重建
browser_navigate(LOGIN_URL)      # 1. 重新加载登录页
browser_snapshot(full=True)       # 2. 获取新 ref
browser_type(acct_ref, account)   # 3. 重新填账号
browser_type(pwd_ref, password)   # 4. 重新填密码
# ⚠️ 验证码已经变了！必须重新问用户
browser_type(captcha_ref, code)   # 5. 填新的验证码
browser_click(login_btn_ref)      # 6. 登录
```

**三级 ref 失效范围速查：**

| 触发操作 | 失效范围 | 恢复行动 |
|---------|---------|---------|
| `browser_snapshot()` 重新获取 | ref 稳定 | 无需行动 |
| `browser_navigate(URL)` 重新加载页面 | ref 重新编号 | 重新 snapshot + refill |
| **点击任意交互元素导致页面变空** | **全部 ref 丢失** | **必须完整重建（含新验证码）** |

**经验教训：始终把登录页视为"一次性渲染"**
- 一旦开始填账号密码，尽量避免在该页面做任何其他交互（如点验证码刷新）
- 如果点验证码后还是看不清，接受这个损失：不点验证码刷新，直接截图当前验证码问用户
- 如果在登录前需要其他操作，先拿到验证码答案一次性填完提交

### 8. 验证码重新读取是合法的

**当前规则：**「当用户提供验证码后，如果在输入过程中页面刷新导致验证码变化，不要再次问用户要验证码」

**修正规则：** 区分两种情况：

| 情况 | 验证码是否变化 | 操作 |
|------|:------------:|------|
| 页面未刷新，只是输入输入框 | ❌ 不变 | 无需再问 |
| 页面因交互事件重新渲染（空白 → navigate 恢复） | ✅ 必然变化 | **必须重新问用户** |

**如何判断：** 如果在账号密码已经填好时页面变空，然后你 `browser_navigate` 重新加载了登录页——这就是一个**新的验证码**。旧的验证码值已与服务端 session 中的 key 解除绑定，填入旧值必定失败。需要重新截图给用户看。

### 9. 「点验证码刷新 → 页面变空」恶性循环

**典型错误流程：**
1. 填写账号密码 ✓
2. 想看验证码 → 用 `browser_click(@e6)` 点击验证码图片
3. 页面变空 → `browser_snapshot` 不显示任何元素
4. `browser_navigate` 重新加载登录页
5. 重新填账号密码 → 验证码已经是新的了 → 需要用户重新告诉
6. 用户发现两次提供了验证码 → 产生挫败感

**正确流程：**
1. 登录页截图 → 直接问用户验证码（不要点验证码图片）
2. 等用户提供验证码
3. 一次性填完：账号 → 密码 → 验证码 → 点击登录
4. 一次操作，不要中途做任何额外交互

## 方法局限性总结

| 方法 | 适用 | 不适用 |
|------|------|--------|
| `browser_navigate` + `browser_type` + `browser_click` | 大部分登录页 | React SPA 不稳定 |
| `browser_press(Enter)` | 有 form submit 绑定 | 没有绑定 Enter 的页面 |
| JS dispatchEvent | 已知事件名 | 复杂合成事件 |
| curl/fetch 直接登录 | 标准 POST 登录 | SPA + CORS + session 绑定 |
| **CAPTCHA 识别** | 支持 vision 的模型 + Tesseract 可识别的验证码 | 干扰复杂的数学题验证码 |
| 用户肉眼识别 | ✅ 始终可用 | 需人工参与，cron 无法自动化 |

## 用户体验行为准则：CAPTCHA 验证码

⚠️ **优先问用户，不要尝试自动破解再失败。** 用户修正过这个行为模式：

当页面出现 base64 数学验证码时，正确的处理顺序：
1. **先问用户**：用 `browser_console` 下载验证码图片到本地文件，然后通过终端输出路径让用户肉眼识别并提供答案
2. 不要先尝试 Tesseract OCR、PIL 预处理、vision 模型等方法——经多次验证它们全都会失败
3. 不要先尝试"有没有可能不用验证码"的替代方案（如切换 URL、绕过 login）——这些方案已确认不可行
4. 拿到用户提供的答案后，配合 `captchaKey` 一起提交登录

**一次性流程（获取验证码 → 问用户 → 填答案 → 登录）：**
```javascript
// 1. 获取验证码
const resp = await fetch('/api/blade-auth/oauth/captcha', {method:'POST'});
const data = await resp.json();
window._captchaKey = data.data.key;

// 2. 将图片保存到文件供用户查看
// 纯 base64 写入文件（去掉 data:image/png;base64, 前缀）
const b64 = data.data.imageBase64.split(',')[1];
// 保存为 /tmp/captcha.png
```

配置项：
- 用 `write_file` 将纯 base64 写为文件
- 然后用 `terminal` 调用 `base64 -d` 解码为 PNG
- 或者直接通过 `vision_analyze` 展示（如果当前模型支持 vision）
- 如果不支持，把文件路径告诉用户：`"登录页有验证码图片，在 /tmp/captcha.png，麻烦你帮我看看是什么数？"`

## 登录成功后

参考 `oa-portal-data-extraction.md` 中的：
- 会话超时恢复（空白页处理方法）
- 密码过期弹窗处理
- 快速导航到目标模块（直接 URL 跳转）

## 对比：其他系统的登录

| 系统 | SPA? | browser_click 有效? | curl 绕过? | CAPTCHA? |
|------|------|--------------------|------------|----------|
| SmarDaten OA | ✅ React SPA | ❌ 不稳定 | ❌ 404 | ✅ 数学题 base64 PNG |
| 典型 Spring/JSP 登录页 | ❌ | ✅ | 可能有 | 不一定 |
| 典型 Vue SPA | ✅ | 通常有效 | ❌ | 不一定 |

SmarDaten OA 的 React 事件处理方式在这个问题上似乎是特例 — 其他 SPA 登录页通常能用 `browser_click` 正常提交。