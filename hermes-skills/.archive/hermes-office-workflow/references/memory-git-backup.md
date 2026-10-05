# 记忆文件 git 备份（软链坑）

用户环境事实：`~/.hermes/memories` 是**软链**，指向 `~/Documents/work/jiayang/hermes-memory/`（git 仓库 `jiayang` 内，远端 github.com:jesse0830/jiayang.git）。记忆改动后要提交并推送（用户习惯）。

## 检查记忆是否在 git 里（易踩坑，曾被用户纠正）

- ❌ 只看 `cd ~/.hermes && git rev-parse` —— 根目录不是仓库，会误判"不在 git"
- ✅ 必须跟随软链：`cd ~/.hermes/memories && git rev-parse --show-toplevel`（应返回 `~/Documents/work/jiayang`）
- 确认软链：`ls -ld ~/.hermes/memories` / `readlink ~/.hermes/memories`

## 记忆推送工作流

```bash
cd ~/Documents/work/jiayang
git add hermes-memory/MEMORY.md   # 或 USER.md / SOUL.md / english-plan.md
git commit -m "更新记忆：…"
git push origin master
```

- hermes-memory/ 跟踪文件：MEMORY.md、USER.md、SOUL.md、english-plan.md、.gitignore
- memory_store.db（facts 库）**不走 git**（Holographic zip 打包同步）

## 背景

2026-08-20 会话：用户问"记忆目前是在 git 目录下么"，助手只看 `~/.hermes` 根目录误答"不在"，
用户纠正"我前几天都让你指向我创建好的一个 git 目录了啊"。随后发现 memories 是软链，
git 状态显示 MEMORY.md 有未提交改动（M），commit+push 后同步完成。
