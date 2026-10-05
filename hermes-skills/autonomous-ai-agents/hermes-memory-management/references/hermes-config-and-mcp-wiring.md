# Hermes 配置写入 与 本地 App 的 MCP 接线

## 改配置：一律走 `hermes config set`

- `~/.hermes/config.yaml` 对 agent 是**写保护的**：patch / write_file 会被拒（refusing to write to Hermes config file），不要硬试或绕道直接改文件。
- 用 CLI 写：
  ```bash
  hermes config set memory.memory_char_limit 5000
  hermes config set "mcp_servers.<name>.command" "/Users/jesseyoung/.local/bin/node"
  hermes config set "mcp_servers.<name>.args" '["/path/to/mcp-server/index.js"]'   # 列表/字典值按 JSON 传
  ```
- 改完回读确认：`hermes config get mcp_servers`（或读 config.yaml 对应段的行）。

## 把本地桌面应用自带的 MCP server 接进 Hermes

1. **找入口**：app 包内常自带 server，路径形如 `<App>.app/Contents/Resources/mcp-server/dist/src/index.js`。
   ```bash
   find "/Applications/<App>.app/Contents/Resources" -name index.js -path '*mcp*'
   ```
   同目录的 `api-client.js` 会暴露该 app 的本地 HTTP API 端口（LLM Wiki = 19828），可用于旁证。
2. **用 app 自带/已知可用的 node** 起服务（本机 `/Users/jesseyoung/.local/bin/node`），别假设 node 在 PATH 里。
3. **先手动握手，再落配置**：用 Hermes venv 的 python（`/Users/jesseyoung/.hermes/hermes-agent/venv/bin/python`，需要 `import mcp` 通过）跑 `mcp.ClientSession` + `StdioServerParameters` + `stdio_client`，能 `list_tools()` 出工具名才算通。
4. **写入**：`hermes config set "mcp_servers.<name>.command" ...` + `args`（JSON 数组）。
5. **验证**（这一步是汇报的依据，不通过不要说「已接通」）：
   ```bash
   hermes mcp list            # 该 server 在列
   hermes mcp test <name>     # Connected + 工具数（LLM Wiki 实测 12 个工具）
   ```
   注册名规则：`mcp_<server>_<tool>`（连字符/点会把换成下划线），在会话里直接调用。
6. **给用户写清前提**：app 必须处于运行状态，Hermes 才能拉起这个 stdio server；app 升级后 server 路径可能变，需重新核对。

## app 侧开关（"Enable MCP access" 之类）的落点

很多桌面 app 把开关只放在 UI 里，状态落在 Application Support 的 JSON。排查顺序：

1. `~/Library/Application Support/<bundle-id>/*.json`（LLM Wiki：`com.llmwiki.app/app-state.json` 的 `apiConfig`，含 `mcpEnabled`、`allowUnauthenticated`、`allowLanAccess`）
2. `~/Library/Preferences/<bundle-id>.plist` → `plutil -p`
3. `~/Library/WebKit/<bundle-id>/WebsiteData`（LocalStorage / IndexedDB）
4. app 主二进制里 grep 开关名与 UI 文案（`grep -a -o` / strings），确认键名拼写

操作规则：
- **先试 stdio 配置**：`hermes mcp test` 通了就说明不必动 UI 开关；只有连不上才回头去改 app-state.json。
- 改 app-state.json 前先备份（`cp` 到 `~/.hermes/cache/`），**只改目标键**，不要整文件重写（会抹掉 app 其它状态）。
- 重启 app 生效：`osascript -e 'quit app id "<bundle-id>"'` 然后 `open -a "<App 名>"`。
- `allowLanAccess` 保持 false（只监听 127.0.0.1），别把本地 API 暴露到局域网。
- 本地 API 存活探测：`curl -s -m 5 http://127.0.0.1:<port>/api/v1/health`；返回 401 表示开了鉴权，需要 token 或 `allowUnauthenticated`。
- 凭证（`LLM_WIKI_API_TOKEN` / `X-LLM-Wiki-Token` 之类）在输出与提交里**只出现键名与是否存在，值一律 [REDACTED]**。

## 效率陷阱

- 别用 `ls -d ~/Library/Application Support/*wiki*` 这种 glob 扫 Application Support：目录多、命中慢，实测会超时（exit 124）；直接读确定的 bundle-id 路径。
- 探测用的临时脚本、输出都放 `~/.hermes/cache/scratch/`，别污染工作目录。
