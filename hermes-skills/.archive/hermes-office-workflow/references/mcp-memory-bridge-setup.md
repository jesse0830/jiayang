# MCP 记忆桥搭建指南

## 架构概述

MCP 记忆桥允许多个 AI 工具（Hermes Agent、Workbuddy 等）共享同一套记忆系统。

```
┌─────────────┐     MCP (Streamable HTTP)     ┌──────────────────┐
│  Workbuddy  │ ◄─────────────────────────────► │  Hermes 记忆桥   │
│  (.mcp.json)│     tools: get_user_profile     │  (HTTP :60194)   │
│             │            search_memory         │                  │
│             │            add_to_memory         │  ┌─ USER.md  ──┐ │
│             │            get_facts             │  │ MEMORY.md   │ │
└─────────────┘                                  │  │ fact_store  │ │
                                                 │  └─────────────┘ │
                                                 └──────────────────┘
```

**核心原则：** 记忆桥是一个轻量级 HTTP 服务器，通过 MCP 协议的 Streamable HTTP transport 暴露 Hermes 记忆文件。Workbuddy 通过 `.mcp.json` 注册后，即可像调用本地工具一样查询/写入 Hermes 记忆。

## 文件结构

| 文件 | 用途 |
|------|------|
| `~/.hermes/scripts/memory_mcp_server.py` | MCP 桥服务器（Python HTTP server） |
| `~/.hermes/scripts/start_memory_bridge.sh` | 自动启动/守护脚本 |
| `~/.hermes/memories/USER.md` | 用户画像（Workbuddy 可读） |
| `~/.hermes/memories/MEMORY.md` | 工作笔记（Workbuddy 可读写） |
| `~/.hermes/memory_store.db` | 结构化 facts（SQLite） |

## 服务器实现要点

### 传输协议

使用 **MCP Streamable HTTP** 传输方式：
- 端点：`POST /mcp`
- HTTP 头：`Content-Type: application/json`
- Bearer auth（可选）
- 请求体：JSON-RPC 格式的 MCP 消息

### 暴露的工具

| 工具名 | 用途 | 参数 |
|--------|------|------|
| `get_user_profile` | 读取 USER.md（用户画像） | 无 |
| `get_memory_notes` | 读取 MEMORY.md（工作笔记） | 无 |
| `get_all_memory` | 读取 USER.md + MEMORY.md 合并 | 无 |
| `search_memory` | 搜索记忆内容 | `query` (string) |
| `add_to_memory` | 追加内容到 MEMORY.md | `content` (string), `tags` (array, optional) |
| `get_facts` | 查询结构化 facts (SQLite) | `query` (optional string) |

### 关键实现细节

1. **JSON-RPC 协议** — MCP 使用 JSON-RPC 2.0。请求体格式：
   ```json
   {
     "jsonrpc": "2.0",
     "id": 1,
     "method": "tools/call",
     "params": {
       "name": "get_user_profile",
       "arguments": {}
     }
   }
   ```

2. **初始化流程** — 客户端先发 `initialize` 请求获取服务器能力声明，再发 `tools/list` 获取工具列表：
   ```json
   // Step 1: initialize
   {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"workbuddy","version":"1.0.0"}}}
   
   // Step 1 response
   {"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"tools":{}},"serverInfo":{"name":"hermes-memory-bridge","version":"1.0.0"}}}
   
   // Step 2: tools/list
   {"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}
   ```

3. **文件读写** — 使用 Python `os.path.expanduser("~/.hermes/memories/USER.md")` 读写记忆文件。

4. **搜索实现** — 简单字符串匹配（`content.lower().find(query.lower())`），无需引入全文搜索引擎。

## Workbuddy 侧的配置

编辑 `~/.workbuddy/.mcp.json`（具体路径因安装方式可能不同）：

```json
{
  "servers": {
    "hermes-memory": {
      "transport": "http",
      "url": "http://127.0.0.1:60194/mcp",
      "timeout": 30000
    }
  }
}
```

下次启动 Workbuddy 时，它会发现 `hermes-memory` 服务并自动加载 6 个工具。

## Hermes 侧的配置

编辑 `~/.hermes/config.yaml`，在 `mcp_servers:` 下方添加：

```yaml
mcp_servers:
  # ...已有的 MCP 服务器
  memory-bridge:
    url: "http://127.0.0.1:60194/mcp"
    timeout: 30
    connect_timeout: 15
```

**注意：** 这允许 Hermes Agent 本身也调用记忆桥工具（用于跨会话给 MEMORY.md 写入条目等）。需要重启 Hermes 才能生效。

## 自动启动

### Mac 启动脚本

**`~/.hermes/scripts/start_memory_bridge.sh`**：
```bash
#!/bin/bash
# Start Hermes Memory MCP Bridge
# This script should run at login or when Workbuddy starts

PID_FILE="$HOME/.hermes/memory_bridge.pid"

# Check if already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "Memory bridge already running (PID: $OLD_PID)"
        exit 0
    fi
    rm "$PID_FILE"
fi

# Start the server
cd "$(dirname "$0")"
python3 "$HOME/.hermes/scripts/memory_mcp_server.py" &
echo $! > "$PID_FILE"
echo "Memory bridge started (PID: $!)"
```

### LaunchAgent（登录自动启动）

创建 `~/Library/LaunchAgents/com.hermes.memory-bridge.plist`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.hermes.memory-bridge</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/jesseyoung/.hermes/scripts/memory_mcp_server.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>/Users/jesseyoung/.hermes/scripts</string>
</dict>
</plist>
```

加载：`launchctl load ~/Library/LaunchAgents/com.hermes.memory-bridge.plist`

## 验证方法

### 1. 健康检查
```bash
curl http://127.0.0.1:60194/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"ping"}'
```

### 2. 工具列表
```bash
curl http://127.0.0.1:60194/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
```

### 3. 读取用户画像
```bash
curl http://127.0.0.1:60194/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"get_user_profile","arguments":{}}}'
```

### 4. 搜索记忆
```bash
curl http://127.0.0.1:60194/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"search_memory","arguments":{"query":"OA密码"}}}'
```

## 注意事项

### 竞态条件
- 两个工具同时写入 MEMORY.md 可能导致冲突
- 当前设计是**单向追加**（append only），不修改已有内容，因此冲突概率低
- 如果需要双向写入，建议加文件锁

### 端口占用
- 默认端口 60194。如果冲突，修改脚本中的 `PORT` 常量和两边配置文件中的 url 端口

### 数据安全
- 桥绑定 `127.0.0.1`（仅本地访问），不暴露到外部网络
- 如果担心本地其他进程读取，可添加 Bearer token 验证

### 记忆空间限制
- Hermes 的 memory 工具有容量限制（当前 ~2,200 chars）
- MCP 桥直接读写磁盘文件，不受此限制
- 但 memory_tool.py 的 add_to_memory 操作受空间检查限制（见 fact_store 替代方案）

## 已确认的双向同步（实战验证 - 2026-07-27）

截至 2026-07-27，**add_to_memory 双向同步已通过实战验证可用**：

1. Workbuddy 调用 `add_to_memory(content="<分析结果>")` 成功将数据追加到 MEMORY.md
2. Hermes 通过 `mcp_memory_bridge_get_memory_notes()` 成功读取到 Workbuddy 写入的数据
3. 写入格式：Workbuddy 把分析结果以带标记的文本追加到 MEMORY.md 末尾，Hermes 读取时能看到完整内容

### 验证过的典型场景：跨工具数据分析交接

用户工作流「用 Workbuddy 分析 Excel 数据 → Hermes 读取分析结果 → 继续做规划」已验证可行（实际案例：2025年周计划资源投入分析 Handoff）：

**Step 1 — Workbuddy 侧**（通过 MCP 记忆桥执行）：
Workbuddy 分析数据后，调用 add_to_memory 将结构化结论写入 MEMORY.md。
Workbuddy 所用数据源路径格式：
```
~/Library/Containers/com.tencent.WeWorkMac/Data/Documents/Profiles/
  <profile_id>/Caches/Files/<hash>/<filename.xlsx>
```
这是企业微信（WeCom）的文件下载目录。每个 profile_id 不同，需要 search_files 定位。

**Step 2 — Hermes 侧**（读取 Workbuddy 写入的数据）：
```python
# 读取全部记忆
result = mcp_memory_bridge_get_memory_notes()
# 或在 Hermes 中搜索指定内容
result = mcp_memory_bridge_search_memory(keyword="鉴策行")
# 或通过系统 memory 工具
session_search(query="workbuddy 分析 投入")
```

**关键前提：**
- 记忆桥服务器（memory_mcp_server.py）必须正在运行（端口 60194）
- Workbuddy 的 `.mcp.json` 已正确配置指向该桥
- 写入是 append only，不会覆盖已有记忆

### 常见问题：为什么 Hermes 无法主动拉取 Workbuddy 的数据

当前架构中，数据流向是单向触发的：
- **Workbuddy → Hermes：** Workbuddy 主动调用 add_to_memory，写入 MEMORY.md。Hermes 被动读取
- **Hermes → Workbuddy：** Hermes 无法主动通知 Workbuddy 做任何事。Hermes 可以读取 Workbuddy 之前写进来的数据，但无法要求 Workbuddy "现在帮我分析一下"

**结论：** 桥是平等的（两边都能读写），但谁先触发数据流动是另一回事。如果数据在 Workbuddy 侧，需要 Workbuddy 主动用 add_to_memory 写过来。

### 扩展方向（以下尚未经过实战验证）

- **Workbuddy 写入 fact_store**：目前 add_to_memory 仅追加到 MEMORY.md，不写入 SQLite fact_store
- **MCP 采样**：Workbuddy 可通过 memory bridge 请求 Hermes 侧 LLM 生成记忆摘要
- **更多工具**：暴露 Hermes session_search 能力，让 Workbuddy 查询历史对话
- **自动同步**：当 Hermes 记忆更新时，自动通知 Workbuddy
