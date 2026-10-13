# LLM Wiki.app 本地通道速查

每条标可信度：`[实测]` = 本机实跑过；`[读码]` = 从 app 打包 JS 读出、尚未在本机实跑——首次用某条前先跑一遍探测脚本验证，验证通过就把标注改成 `[实测]`。

## 基础

- Base URL：`http://127.0.0.1:19828`（默认端口，app 设置里可改）`[读码]`
- 本机裸调可用：`allowUnauthenticated=true`；`allowLanAccess=false`（只监听本机）`[实测]`

## 端点

| 方法 | 路径 | 说明 | 可信度 |
|---|---|---|---|
| GET | `/api/v1/health` | 存活与开关状态（ok / mcpEnabled / allowUnauthenticated / allowLanAccess） | [实测] |
| GET | `/api/v1/projects` | 已注册项目列表（id / name / path）；项目 id 可传 `current` 表示当前绑定项目 | [读码] |
| GET | `/api/v1/projects/{id}/files` | 项目内被索引的文件树 | [读码] |
| GET | `/api/v1/files/content` | 取页正文 | [读码] |
| POST | `/api/v1/projects/{id}/search` | 语义检索，body：`{"query": "...", "topK": 5, "includeContent": false}` | [读码] |
| POST | `/api/v1/chat` | 带召回来源的问答（SSE 流式） | [读码] |
| GET | `/api/v1/reviews` | 待复核/存疑项 | [读码] |
| GET | `/api/v1/graph` | 页级知识图谱 | [读码] |
| POST | `/api/v1/pages/embed` | 对单页重建向量 | [读码] |
| POST | `/api/v1/pages/write` | 写入/更新页并重索引 | [读码] |
| POST | `/api/v1/sources/rescan` | 重扫素材源、增量入库 | [读码] |

若某条返回 404：**不要猜新路径**，按 SKILL.md 里的反引号模板串 grep 法，从
`/Applications/LLM Wiki.app/Contents/Resources/mcp-server/dist/src/api-client.js` 重取（app 升级会改路径）。

## MCP 工具名（Hermes 侧 `llm-wiki` 服务）

`llm_wiki_status`、`projects`、`set_project`、`files`、`read_file`、`search`、`chat`、`graph`、`reviews`、`rescan_sources`、`embed_page`、`write_page`。

- 调用前用 `tool_describe` 确认真实名字（前缀/大小写随版本变）；**不要按 `llm_wiki_status` 这类推断名硬调**，`tool_describe` 会直接回 not_found。
- 会话里搜不到这些名字 ⇒ 见 SKILL.md「核心坑：启动期快照」。

## 只读探测脚本模板

写成文件再跑，别内联 curl（避免命令确认打断本轮）：

```python
# /tmp/wiki_probe.py
import json, urllib.request
BASE = "http://127.0.0.1:19828/api/v1"

def get(path):
    with urllib.request.urlopen(BASE + path, timeout=8) as r:
        return json.loads(r.read().decode())

def post(path, payload):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

if __name__ == "__main__":
    print("health:", get("/health"))
    print("projects:", get("/projects"))
    # print("search:", post("/projects/current/search", {"query": "关键词", "topK": 5}))
```
