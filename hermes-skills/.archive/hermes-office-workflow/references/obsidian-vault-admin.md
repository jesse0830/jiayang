# Obsidian 仓库（vault）管理与迁移

适用于：vault 迁移、切换 Obsidian 当前打开的仓库、判断"笔记在哪"、git 同步 vault。

## 关键坑：默认路径可能是空壳

`~/Documents/Obsidian Vault` 往往只是一个占位 vault（只有欢迎.md + .obsidian/），
真实 vault（有日报、项目笔记）通常在别处（如 `~/Documents/work/obsidian/...`）。
**迁移/备份/回答"我的笔记在哪"之前，必须验证 vault 是真实仓库**：

- 列出 vault 下所有 `.md`：`find <vault> -name "*.md"`（或用 search_files target=files pattern=*.md）
- 检查笔记的修改时间（日报应该是近几天的）
- 如果 vault 看起来是空的但用户说有笔记：全盘搜最近几天修改的 .md，
  以及搜索含 `.obsidian` 子目录的文件夹 —— 那才是真正的 vault
- 用户的真实 vault 路径已记录在 memory；拿不准先查 memory

## 迁移文件清单

**必须迁移：**

- 所有 `.md` 笔记文件（数据本体）
- `.obsidian/` 下的配置文件：`app.json`、`appearance.json`、`core-plugins.json`、`graph.json`，
  如有 `daily-notes.json` 和 `.obsidian/themes/` 一并带上

**排除（不同步）：**

- `.obsidian/workspace*.json` —— 窗口布局/打开的标签页，每台机器不同，同步会互相覆盖
- `.obsidian/cache/` —— 自动重建
- `.Trash/` —— Obsidian 回收站
- `.DS_Store`

一句话：**全部 .md + .obsidian/（去掉 workspace*.json 和 cache）+ 一个 .gitignore**

稳健的复制命令（rsync 排除法）：

```bash
rsync -av --exclude '.obsidian/workspace.json' --exclude '.obsidian/cache' \
  --exclude '.DS_Store' --exclude '.Trash' <旧vault>/ <新vault>/
```

复制后验证：数新目录下 .md 数量，抽查日报是否都在。
迁移完成后 Obsidian 需要重启（⌘Q 再打开）才能看到新仓库。

## 程序化切换当前打开的仓库（macOS）

Obsidian 的仓库列表存在 `~/Library/Application Support/obsidian/obsidian.json`
（JSON：`vaults` 映射 id → `{path, ts, open}`）。想不经 UI 直接切换：

1. **先退出 Obsidian**（它退出时会重写配置，会覆盖你的修改）：
   `osascript -e 'quit app "Obsidian"'`，等 1-2 秒，`pgrep -l -i obsidian` 确认已退出
2. 备份配置：`cp .../obsidian.json .../obsidian.json.bak`
3. 编辑 obsidian.json：`vaults` 只留目标仓库一项 —— 新随机 16 位 hex id、
   `"path": "<新vault绝对路径>"`、`"open": true`、`"ts": <当前epoch毫秒>`。
   删掉旧条目同时会把它们从仓库选择器里移除
4. 重启：`open -a Obsidian`，直接打开新仓库

删除旧 vault 目录的安全前提：**新 vault 已完整复制 且 已 push 到远程仓库**，两者都确认后才 `rm -rf`。

## 用户当前状态（2026-08）

- 真实 vault = `~/Documents/work/obsidian/JesseYoungObsidian/`（已删除）
- 新仓库 = `~/Downloads/jiayang/obsidian-vault/`，git 同步到 jiayang 仓库（push 用 SSH 443）
- `~/Documents/Obsidian Vault` 是空壳，勿用
