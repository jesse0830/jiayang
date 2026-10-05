# jiayang 仓库与记忆推送（用户"记忆帮我推送一下"）

## 仓库拓扑（2026-08 实测）

jiayang 仓库（`~/Documents/work/jiayang/`，remote = `git@github.com:jesse0830/jiayang.git`，
push 走 SSH 443）一个仓库同时容纳两类内容：

| 子目录 | 内容 | 说明 |
|---|---|---|
| `hermes-memory/` | MEMORY.md / USER.md / SOUL.md / english-plan.md | `~/.hermes/memories` 是软链指向它 |
| `obsidian-vault/` | Obsidian 笔记（smardaten/daily/、weekly/、software factory/ 等） | 真实 vault，`~/Documents/Obsidian Vault` 是空壳 |

## "记忆推送" = git push，不是别的

用户说"记忆先帮我推送一下"时，意图是 **push jiayang 仓库**，把 Hermes 记忆 + Obsidian
笔记同步到 GitHub 远程（家里/其他设备可拉取）。**不是** zip 打包，**不是** memory_store.db。

```bash
cd ~/Documents/work/jiayang && git push origin master
```

## 验证是否已同步

- `git status -sb` → 显示 `## master...origin/master`（无 ahead/behind）= 已同步
- `git push` 输出 `Everything up-to-date` = 远程已是最新，无需额外操作
- Obsidian 装了 obsidian-git 插件：vault 改动会自动生成 "vault backup: …" 提交，
  所以 `git status -s` 通常很干净，只需 push
- 若 hermes-memory/ 有未提交改动（少见）：`git add hermes-memory/ && git commit` 后再 push

## memory_store.db 不在 git 里

- Holographic 事实库在 `~/.hermes/memory_store.db`（+ -wal/-shm），**不进 git 仓库**
- WorkBuddy 通过 MCP 桥（端口 60194，`hermes-memory` 服务）实时读取，不走 git
- 所以"推送记忆"不覆盖事实库；用户若问事实库同步，指向 hermes-memory-configuration.md
  的 Holographic Cross-Device Sync 部分（云盘/手动拷贝/Syncthing）

## 会话内实操记录（2026-08-19）

1. `git status -s` → 空（工作树干净，obsidian-git 已自动提交）
2. `git status -sb` → `## master...origin/master`（无 ahead/behind）
3. `git push origin master` → `Everything up-to-date`
4. 验证 Obsidian 副本与源定稿：`diff 源文件 vault副本` → 一致
