# 钉钉闪记 API 逆向记录（2026-08 验证）

## 验证结论
- **纯 API（无钉钉登录 cookie）无法读取会议内容**：所有 /r/Adaptor/* 接口返回 HTTP 200 + 登录页 HTML（"AI 听记 - 钉钉统一身份认证"），连 token 接口也被墙
- og:title 可无登录读取 → 会议标题（`curl -sL <url>` 后在 HTML 里找 `<meta property="og:title">`）

## URL 结构
- 分享链接：`https://shanji.dingtalk.com/app/transcribes/<taskId>`
- taskId 在路径最后一段，例：`76327569643432393431363930385f3130373233313638305f32`

## Host 发现过程（避免走弯路）
1. 初猜 `meeting-ai-tingji.dingtalk.com`（JS 里 baseURL 定义 `"https://" + "meeting-ai-tingji." + dingtalkDomain`）→ 根路径 200 "Welcome to MeetingAIAgent"，但 /r/Adaptor/* 全 404
2. **正确 base：`https://shanji.dingtalk.com/api`** —— 来自 JS 里 `serviceEndPoint: "https://" + main + "/api"`，cn 环境 `main` = shanji.dingtalk.com
3. 前端 JS 主文件：`https://cdn.dingtalkapps.com/alidocs/we-flashing/<ver>/index.chunk.js`（gzip；curl 后先 `mv` 加 `.gz` 再 `gunzip`）

## 关键接口
| 接口 | 用途 | body |
|---|---|---|
| /r/Adaptor/PortalMinutesI/minutesDetailV2 | 会议详情 | `[{taskId, uuid:"", bizType:"", enableScreen:true, enableCloudMeeting:true, enableMinutesDetailTab:true, skipLowClientVersionCheck:false}]` |
| /r/Adaptor/MinutesTokenI/generateDingUserIdentifierInfoToken | 拿 token | `[{scene:"aiAnswer", corpId:""}]` → token 放 header `dt-meeting-agent-token` |
| /r/Adaptor/PortalMinutesI/minutesParagraphList | 段落列表 | 未验证（同登录墙） |

## 鉴权链
- 请求拦截器自动加 `dt-meeting-agent-token` header（h = "dt-meeting-agent-token"）
- 401 时刷新 token（调 generateDingUserIdentifierInfoToken）重试
- token 存 localStorage，有效期 12h（432e5 ms）

## 尝试过的绕过（全部失败，别再试）
- body 里加 `password` / `visitPassword` 字段 → 仍返回登录页
- checkPermission / queryMinutesInfo 带密码 → 仍返回登录页
- 密码校验在前端页面层（输入密码后前端才展示内容），不是 API 参数

## 建议
- 用户侧 30 秒手动复制 >> 自动化逆向。除非拿到已登录 cookie 或用户明确要求自动化。
