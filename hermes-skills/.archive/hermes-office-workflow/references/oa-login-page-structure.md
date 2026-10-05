# OA 登录页结构实测（2026-08-09 更新）

补充/修正 `oa-login-captcha.md` 中"验证码图片 = data:image img"的旧假设。
本文件记录最新实测的登录页结构，未来会话以本文件为准。

## 页面类型

- `https://oa.smardaten.com/application/login/1640627701456342` 是 **antd (Ant
  Design) SPA**，整个 HTML 约 4MB。
- `browser_navigate` 后 **不要立即 query DOM**：渲染早期
  `document.body.innerHTML` / `querySelectorAll` 可能返回空（`about:blank`、
  bodyLen 0），页面还在加载。先 `browser_snapshot` 确认登录表单出现再操作。
- 表单是常规 DOM（无 shadow DOM、无 iframe）：`document.querySelectorAll('input')`
  可找到账号/密码框。

## 两个登录方式 tab（重要）

- 登录页有 tab 切换：**`密码登录`（默认 active）** / **`验证码登录`**。
- 表单里的 span 文本可确认当前 tab：`class="active"` 的那个就是当前方式。
- **密码登录 tab 下 DOM 里可能没有任何 `<img>` / `<canvas>`**（2026-08-09 实测）：
  验证码图片此时未渲染。旧经验"验证码 = `src` 以 `data:image` 开头的 img"只在
  验证码已渲染时成立。

## 若取不到验证码图（querySelectorAll('img') 为空）

1. 先确认当前 tab：是否停在"密码登录"？考虑切到"验证码登录"tab 再看。
2. 或先点一次登录触发失败——验证码常在失败后自动刷新/出现，再取图。
3. 不要死等 data:image img；不要反复刷新页面（每次重载 ~4MB，很慢）。

## 表单元素

- 账号：`#username`（placeholder=请输入登录账号）
- 密码：`#password`（placeholder=请输入登录密码）
- 均为 class=ant-input；也可用 browser_snapshot 的 ref 定位（ref 每次会话会变）。
- 登录按钮：页面 button "登录"。

## 与 oa-login-captcha.md 的关系

`references/oa-login-captcha.md` 的 base64 分块 hash 修复、OCR 多引擎投票、
重试纪律仍然有效；仅"登录页"一节中的验证码 img 假设需要按本文件修正。
