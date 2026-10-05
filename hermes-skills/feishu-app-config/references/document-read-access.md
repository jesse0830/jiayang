# 飞书文档/表格"能不能读到"——通道决策树（2026-09 实测）

场景：用户丢来一个链接（例 `https://<tenant>.feishu.cn/docx/<DOC_ID>`）问"这个能读取到吗"，或抓取结果显示 `no content extracted`。

## 先判两件事，再选通道

1. **token 换得回来吗？**（`POST /open-apis/auth/v3/tenant_access_token/internal`）
   - 换得回 ⇒ FEISHU_APP_ID/SECRET 没问题，**不要再改 .env**。
   - 换不回 ⇒ 才是凭证问题。
2. **这份文档授权给应用了吗？** 用应用身份调 `GET /open-apis/docx/v1/documents/{doc_id}/raw_content`。
   - 返回正文 ⇒ 通路 OK（docx 用 raw_content，表格用 sheets/v2 values）。
   - 返回 `code 1770032 forBidden` ⇒ **文档没授权给应用**，跳到下面第 2 条通道。

## 通道（按"最快见效"排序）

| # | 通道 | 前提 | 说明 |
|---|---|---|---|
| 1 | 应用 API | 文档已分享给应用为「可阅读」 | docx → `raw_content`；表格 → sheets/v3 元数据 + sheets/v2 values |
| 2 | 让用户分享给应用 | 用户点几下 | 文档右上「**分享**」→ **添加协作者** → 搜应用名 → 权限选「**可阅读**」→ 确定。**一次配置长期有效**，之后同类文档都能直读；优先推荐这条 |
| 3 | 落本地再读 | 用户点几下 | 文档右上「**···**」→ 下载为 Word/PDF，存到本机任意目录后直接读文件。最稳，不依赖任何网络/权限 |
| 4 | 用户直接贴正文 | 无 | 用户只要结论时最快，30 秒 |
| 5 | 借用户已登录的浏览器 | 见下"前置条件" | 适合"只读一次、不能改文档设置"的场景，但需要先满足浏览器侧前置条件 |

**答复用户时的写法**：不要只说"读不到"，要给"卡在哪 + 你动哪一步"——用一张表列出各通道的实测结果（API 1770032 / 匿名抓取 302 跳登录 / 浏览器未就绪），然后给按快慢排序的 2-4 个可选动作，并问一句"这份文档是什么内容、你打算拿它做什么"（可能根本不需要全文）。

## 各通道实测证据（供判断，非"结论"）

- 应用 API + 未分享的文档 ⇒ `code 1770032 forBidden`（token 正常）。
- 匿名抓取文档页：`curl -m 20 <url>` ⇒ **HTTP 302、body 0 字节**，跳登录页 —— 飞书文档页不登录拿不到任何正文，不要在这条路上反复试。
- `curl https://open.feishu.cn/` ⇒ 404（属接口无参的正常返回，**不是**网络不通的判断依据）；`curl https://pypi.org/simple/` ⇒ 200 可用于确认外网可达。
- 应用身份读**表格**用 sheets 系列接口（见 SKILL.md 第 6 节 + `references/wiki-to-spreadsheet-access.md`），与 docx 是两套端点，别混。

## 浏览器通道（通道 5）的前置条件

要借用户已登录的浏览器读页面，先做**前置诊断**，别盲试：

1. 用绝对路径直接调底层 CLI（它在 uv 缓存里，不在 PATH）：`~/.cache/uv/archive-v0/*/bin/browser-harness`；支持从 stdin 喂 Python：
   ```bash
   BH=$(ls ~/.cache/uv/archive-v0/*/bin/browser-harness | head -1)
   "$BH" doctor      # 报 Chrome 是否在跑 / daemon 是否活着 / 连接状态
   "$BH" <<'PY'
   ensure_real_tab(); goto_url("<url>"); wait_for_load()
   print(js("location.href")); print(js("document.body.innerText")[:3000])
   PY
   ```
2. macOS 上第一次建立 Chrome CDP 连接会弹远程调试授权（`browser-harness mac-approve` 就是去点它），而这个动作需要**宿主 App 有「辅助功能」权限**：系统设置 → 隐私与安全性 → 辅助功能 → 允许 Hermes（或启动它的终端）。没授权时表现为 "pending Chrome connection ended before approval"。
3. 若 `drive_preview`/预览面板停在 `chrome-error://chromewebdata/`，说明浏览器侧根本没加载到目标页，此时 `action=elements` 只会返回空列表——**先修浏览器侧，再谈读页面**，不要反复 read。

**结论次序**：能改文档设置时优先走通道 2（分享给应用，一劳永逸）；不想动文档就走通道 3/4。浏览器通道留作长期能力（修好辅助功能权限后，读 OA、读任意登录墙页面都用得上）。

## 长期方案：OAuth user_access_token（未在本机配置过）

以"用户本人"身份读文档，就不需要逐个分享给应用：用户点一次授权链接，换 `user_access_token`（可 refresh，长期有效）。前提是开发者后台为该应用配置了**重定向 URL**（注意：飞书是「安全设置」里的重定向地址），并申请 docx/drive 的用户级 scope。要配就先把"开发者后台 → 安全设置 → 重定向 URL"和"申请哪些 scope"列给用户，再生成授权链接。
