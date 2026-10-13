---
name: llm-wiki-app-integration
description: "Use when 用/排障 LLM Wiki 桌面应用（MCP+HTTP 通道）。"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [LLM-Wiki, MCP, Obsidian, Knowledge-Base]
    related_skills: [llm-wiki, native-mcp, obsidian]
---

# LLM Wiki 桌面应用 × Hermes 接线

本机知识库三件套：**Hermes（写/维护）→ LLM Wiki.app（语义索引与问答）→ Obsidian（阅读/编辑）**，三者共用同一批 markdown 文件。
通用知识库方法论（页类型、写页规范、检索策略）见 bundled skill `llm-wiki`；本 skill 只管**本机 app 的接线、通道与排障**。

## 何时用

- 用户问「llm-wiki 怎么用」「怎么把资料入库 / 怎么问知识库」
- 要让 Hermes 通过 MCP 读写 wiki，或用 app 的语义检索补 grep 抓不到的相关性召回
- 排查「MCP 服务已注册，但当前会话里调不到它的工具」「wiki 搜不到刚写的内容」

## 架构与硬前提

1. **app 必须开着**。`LLM Wiki.app` 既是索引器，也是 MCP server 的宿主（子进程跑 `Contents/Resources/mcp-server/dist/src/index.js`）。app 一关，MCP 与 HTTP 通道全断，Hermes 侧一切调用失败。
2. 本地 HTTP 服务默认 `http://127.0.0.1:19828`；`allowLanAccess=false`（只本机可访问），**保持这个值**；`allowUnauthenticated=true` 是它本地可裸调的前提。
3. 项目绑定：vault 内的 `.llm-wiki/project.json` 决定哪个目录被索引；app 全局状态在 `~/Library/Application Support/com.llmwiki.app/app-state.json`（含 `apiConfig`、`mcpEnabled` 等开关）。
4. **同一批 md 只存一份**。Hermes 写页、app 索引、Obsidian 阅读共用 vault 文件，谁都不另存副本；不要为了「给 app 用」再复制一份出去。
5. Hermes 侧服务名固定为 `llm-wiki`（配置在 `~/.hermes/config.yaml` 的 `mcp_servers`）。

## 接线验证（按顺序，全部只读）

```bash
pgrep -fl "LLM Wiki"                                   # 应有 app 主进程 + mcp-server 子进程
curl -sS --max-time 5 http://127.0.0.1:19828/api/v1/health
cat "<vault>/.llm-wiki/project.json"                    # 当前绑定的项目/路径
~/.hermes/hermes-agent/venv/bin/hermes mcp list         # llm-wiki 是否 registered / enabled
~/.hermes/hermes-agent/venv/bin/hermes mcp test llm-wiki
~/.hermes/hermes-agent/venv/bin/hermes tools list       # 该服务是否 all tools enabled
```

判定：health 通 + `mcp list` registered + `tools list` enabled ⇒ **链路本身没坏**，问题多半在「当前会话有没有加载这些工具」。

## 核心坑：长驻会话的 MCP 发现是启动期快照

MCP 工具只在进程启动时发现一次，**没有热加载**。因此：**服务是在当前 gateway/会话启动之后才注册的，这个会话里就调不到它的工具**，只能重启进程。

- 判定法：`hermes mcp list` 与 `hermes tools list`（新进程视角）都正常，但**本会话自己的工具目录**（`tool_search` / `tool_describe`）里搜不到该服务任何工具 ⇒ 快照过期，不是配置写错，别去改 config。
- 修法：重启 gateway（务必用 Hermes 自带 venv 的解释器），重启后**新会话**即可直接调用。重启前先告诉用户会短暂中断连接。
- `hermes mcp tools <server>` **不存在**这个子命令，它返回的是 exit 0 的错误文案（看着像成功），别据此下结论；先 `hermes mcp --help` 拿子命令清单。

## 从 app 编译产物里挖 API / 工具名

app 的 JS 是打包产物，URL 用**模板字符串**拼接，所以 `grep '"/api/v1/...'` 抓不到任何东西（空输出 ≠ 没有端点）。改用反引号模板串提取：

```bash
cd "/Applications/LLM Wiki.app/Contents/Resources/mcp-server/dist/src" && grep -oE '`[^`]{0,60}`' api-client.js | sort -u
```

`dist/src/` 只有 4 个文件：`api-client.js`（REST 客户端，端点在这里）、`index.js`（MCP server 入口，工具注册名在这里）、`project-binding.js`、`version.js`。
端点与工具名的具体清单见 `references/local-http-api.md`。

## 探测姿势（避免空转与打断）

- 只读探测一律优先 **GET**（health / projects / files），不需要额外确认。
- 需要 POST（search / chat）时，把请求写成脚本文件再 `python3 <脚本>` 跑；**别把带 JSON 载荷的 curl 内联**——容易被命令确认拦下、打断当前轮次，白等一次。
- 别只看 `exit_code`：接管道（`| head`、`| python3 -m json.tool`）的命令失败也常表现为「空输出 / 一行输出」。用 `curl -sS` 或先把响应落盘再读，才能区分「真没数据」和「命令挂了」。

## 写库约定（Hermes 侧遵守）

- 页放 `wiki/<type>/`，type 目录：`concepts`、`entities`、`comparisons`、`queries`、`sources`、`synthesis`；入口 `wiki/index.md`，append-only 流水 `wiki/log.md`。
- 超 ~200 行的原文属于**素材**：全文放 `raw/`，wiki 只留精炼页并用 `sources:` 指回；`raw/` 只读不改。
- 目录与标签约定在 `schema.md`，**改结构先改 schema.md 并递加版本号**（本库约定：每次修改都递加 v1.x）。
- 每页 frontmatter 齐全（title / created / updated / type / tags / sources / confidence），正文至少 2 个 `[[双向链接]]`。
- 每次动作都要落 `index.md`（页数 + 日期）与 `log.md`（一条流水）。

## 排障清单

| 症状 | 原因 | 动作 |
|---|---|---|
| 本会话调不到 `llm_wiki_*` 工具 | 会话启动早于服务注册（快照过期） | 重启 gateway |
| 语义检索搜不到刚写的页 | app 没开 / 未重扫 / 项目绑错目录 | 开 app → 重扫 sources → 核对 `.llm-wiki/project.json` |
| 同一内容出现两份索引 | app 里残留旧工作区项目 | 在 app 中移除旧项目，只保留当前 vault 项目 |
| health 通但调用报错 | 工具名/参数猜错 | 用 `references/local-http-api.md` 里的真实工具名，别照 `llm_wiki_status` 之类推断名硬调 |

## 回答用户「怎么用」时的话术骨架

先给**当前真实状态表**（app 是否在跑、health、绑定项目、库内页数与空缺目录），再给**三个入口各干什么**（Obsidian 读 / app 语义问答 / Hermes 写维护），然后给**四种最常用说法**（入库、提问、lint、改 schema），最后单独列**前置条件与坑**（app 常开、需重启 gateway 生效）。用户要的是「我现在怎么用」，不是 MCP 协议科普；不要交付前先跑一堆探查却给不出状态结论。
