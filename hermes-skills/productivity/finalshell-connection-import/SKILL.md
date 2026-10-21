---
name: finalshell-connection-import
description: Use when 把终端 SSH 连接记录批量导入 FinalShell。
version: 1.0.0
platforms: [macos]
metadata:
  hermes:
    tags: [finalshell, ssh, connection, import, macos]
    category: productivity
---

# FinalShell 批量导入 SSH 连接（macOS）

## 目标位置（FinalShell 4.6.5）

- 连接目录：`~/Library/FinalShell/conn/<id>_connect_config.json` —— **一条连接一个文件，文件名 = 连接 id**。FinalShell 启动时按此目录重建左侧连接树；没有别的索引文件（`sync/db_.json` 只有 task_vers/files，与连接无关，不用改）。
- 其他：`config.json`（界面/同步设置，含 `sync_config.auto_sync`）、`knownhosts.json`、`backup/`（应用自动备份）、`temp/`。
- **写文件前先确认 FinalShell 未运行**（`ps aux | grep -i [F]inalShell`）；并 `cp -R conn conn.bak-$(date +%Y%m%d-%H%M%S)` 备份。

## 连接 json 结构（照抄现网文件，少字段会不显示/报错）

```json
{"forwarding_auto_reconnect":false,"custom_size":false,"delete_time":0,"secret_key_id":"",
 "user_name":"root","remote_port_forwarding":{},"conection_type":100,"sort_time":0,
 "description":"","proxy_id":"0","authentication_type":1,"drivestoredirect":true,
 "delete_key_sequence":0,"password":"","modified_time":<ms>,"host":"1.2.3.4","accelerate":false,
 "id":"<16位小写字母数字>","height":0,"order":0,"create_time":<ms>,"port_forwarding_list":[],
 "parent_update_time":0,"rename_time":0,"backspace_key_sequence":2,"fullscreen":false,
 "port":22,"terminal_encoding":"UTF-8","parent_id":"root","exec_channel_enable":true,
 "width":0,"name":"root@1.2.3.4","access_time":0}
```

要点：
- 拼写是 `conection_type`（作者笔误），别"修正"成 connection_type。
- `conection_type:100` = 可连接主机；`parent_id:"root"` = 根节点（分组文件格式未验证，要分组让用户在界面拖）。
- **密码字段**：FinalShell 存的是 `base64(8字节前缀 + AES密文)` 形态（约 24/40 字符），**算法/密钥未逆向出来，无法生成**。所以 `password` 留空 `""`、`authentication_type:1`，用户首次连接输入一次后 FinalShell 自己保存。**不要**把明文写进 password（解不出来，界面仍空，反而误导）。

## 连接记录从哪来（本机多源）

1. **Terminal.app 历史**（主要来源）：`~/Library/Preferences/com.apple.Terminal.plist` → 各 profile 的 `PreviousCommands`（`plistlib` 递归找），正则抓 `ssh <user>@<host> [-p port]`。注意命令常写成 `ssh smard@ 10.15.110.25`（`@` 后有空格）。
2. `~/.ssh/known_hosts` / `known_hosts.old`：取第一列（`|1|...` 哈希项还原不了；明文项 `[1.2.3.4]:60005` 要连方括号端口一起解析），可补 Terminal 历史遗漏的端口。
3. `~/.hermes/state.db`（Hermes 会话库）：`file:...?mode=ro` 只读扫含 ssh 的消息。
4. 项目文档（如 `smardatenCorp/**` 的「环境信息.rtf」）：抓 `IP + 账号/密码`，供用户对照，**不要写进 chat**。

脚本模板见 `references/import_script.md`。

## 流程

1. 探测四源 → 合并成 `(user, host, port)` 去重清单。
2. 读 `conn/*.json` 建已有集合，跳过重复（同 user/host/port）。
3. 备份 conn → 逐条写新 json（name = `user@host`，非 22 端口加 `:port`）→ 打印新增/总数。
4. 校验：全部文件可 `json.load`、字段齐全、文件名 == id、**原连接 password 未被改动**。
5. `open -a FinalShell` 启动后 `diff` conn 目录清单 —— 无变化即应用接受了格式；`screencapture -x` 截图留证（首次启动窗口可能不显示，别死磕 GUI 验证）。
6. 产出导入记录 md（标版本号）存 `~/Library/FinalShell/`，聊天里给汇总。

## 坑

- 本机无 `Quartz`（系统 python3），也未必有 `computer_use` 工具 → GUI 验证靠 `screencapture` + 目录状态对比，别指望点元素。
- `~/.zsh_history` 里常常**没有** ssh 记录（Terminal 的 per-profile 历史才是），别只扫 shell history。
- `screencapture -x` 需屏幕录制权限；截到桌面壁纸（窗口没起来）不代表失败。
