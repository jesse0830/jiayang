# jiayang 仓库 + Obsidian vault 同步（用户专属实例）

Worked example of `github-china-access` workflow. 首次推送 2026-08-17（commit 556f8d3）；vault 已改为桌面 obsidian-git 自动同步（见下）。

## 远程仓库（user: jesse0830）

- URL: `github.com/jesse0830/jiayang` — 默认分支 `master`，仓库约 114MB
- 根目录原有内容（未动）：`BEC/`、`Jesse/`、`lyy/`、`神木煤矿项目/`、`数字三农协同平台应用分享会.pptx`（61MB）、`github-recovery-codes.txt`、`readme.txt`
- ⚠️ `github-recovery-codes.txt` 是 GitHub 恢复码 — 若仓库公开应尽快删除/转私密
- ⚠️ 仓库里有敏感文件（恢复码、`Jesse/resume/` 简历证件照）→ **不要把整个仓库克隆到手机当 vault**，见 skill `obsidian-git-sync`
- 仓库大（61MB pptx），clone 慢 — 读场景建议 `--depth 1`

## Obsidian vault（2026-09 更新）

- **现行路径：`~/Documents/work/jiayang/obsidian-vault`**（仓库内子目录，Obsidian 打开它作为 vault 根）
- 同步方式：**obsidian-git 插件每 5 分钟自动 commit+push**（走 SSH 443），无需手动命令
- `~/Documents/Obsidian Vault`（`/Users/jesseyoung/Documents/Obsidian Vault`）**是空壳目录，勿用** — 早期记录里的「vault 路径」已失效
- 无 `OBSIDIAN_VAULT_PATH` 环境变量；`.env` 未配置
- 结构: `.obsidian/`（app.json / appearance.json / core-plugins.json / graph.json / workspace.json）+ 笔记 .md

## obsidian-vault/.gitignore（已验证生效）

```gitignore
# 窗口布局：每台机器不同，同步会互相覆盖
.obsidian/workspace*.json
# 缓存
.obsidian/cache
# Obsidian 回收站
.Trash/
# macOS 系统文件
.DS_Store
```

`.obsidian/` 其余文件（app/appearance/core-plugins/graph）保留 — 插件/主题/快捷键跨端同步。

## 手动兜底同步命令（自动同步失灵时）

```bash
cd ~/Documents/work/jiayang && git add obsidian-vault/ && git commit -m "更新笔记" && git push origin master
```

其它设备克隆：`git clone ssh://git@ssh.github.com:443/jesse0830/jiayang.git`，然后 Obsidian 打开 `obsidian-vault/`。
⚠️ 手机端不能用这个仓库当 vault（子目录嵌套 + 敏感文件），必须先拆独立仓库 → skill `obsidian-git-sync`。

## 通道探测记录

**2026-08-17**：HTTPS clone/ls-remote 直连超时；SSH 22 超时；SSH 443 认证秒过但大传输慢（>10 分钟未完成 114MB）；`api.github.com` 可通；`gh-proxy.com` 镜像 clone ~3MB/s（直连 30KB/s，快 80 倍）；gh-proxy tarball 不支持断点续传（HTTP 56）；本地无 git-credentials / credential.helper / gh CLI / PAT — push 只能走 SSH。

**2026-09-21 复测（通道已变化，务必现测现用）**：`https://github.com` **直连超时**（000/12s）；`api.github.com` 200；`codeload.github.com` 301；`git@github.com` SSH **22 与 443 均认证成功**（22 不再是死路）。关键：本机跑着 Clash **系统代理 127.0.0.1:7897**，浏览器走它所以 github.com 看着正常，而裸 curl/git **不走** 系统代理 → 直连超时属预期。判定通道前先 `scutil --proxy`，必要时用 `curl -x http://127.0.0.1:7897` 复测。
