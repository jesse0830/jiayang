# GitSync 手机端（iOS）上手流程与排障

GitSync = ViscousPot 的**独立手机 git 客户端 App**（Flutter），**不是 Obsidian 插件**。
iOS 上原生 git 跑不了，obsidian-git 插件官方因此推荐手机端改用它。

## App 事实（2026-09 核对）
- App Store：`https://apps.apple.com/us/app/gitsync/id6744980427`，开发者显示为 **ViscousPotential Ltd**（商店里有 **ObSync** 等同类易混 App，先核对开发者名）
- 系统要求 **iOS 15.6+**（低于此版本装了也起不来）
- 支持 GitHub / GitLab / Gitea / Codeberg / 任意 HTTP(S) git 远程 + SSH
- 报 bug：App 右上灰色齿轮 → **Report a Bug**（可用 GitHub OAuth 或 PAT 登录）；邮件 `bugs.viscouspotential@gmail.com`（作者更新较勤，附机型 + iOS 版本 + 现象）

## 官方文档（GitHub wiki 信息不足，走厂商站点）
- 全设备教程（含 iOS 段）：`https://viscouspotenti.al/posts/gitsync-all-devices-tutorial`
- wiki：`https://gitsync.viscouspotenti.al/wiki/`（`/wiki/faq`、`/wiki/guides/`、`/wiki/authentication-methods`、`/wiki/troubleshooting`）
- 仓库：`https://github.com/ViscousPot/GitSync`

## 认证方式（官方 wiki，2026-09-21 实读核实）
GitSync 原生支持两条路，**先探路再选**：手机 Safari 打开 `github.com`，能秒开走 OAuth，打不开走 SSH。

| 方式 | 机制 | 前提 |
|---|---|---|
| **OAuth** | App 内点 OAuth → 浏览器登录授权 → 仓库列表里直接选 | 手机必须能访问 `github.com`（HTTPS）；国内裸网大概率不行 |
| **SSH** | ED25519 密钥对；GitSync **能生成新密钥，也能导入/导出私钥** | `github.com:22` 或 `ssh.github.com:443` 可达 |

**SSH 导入现有私钥（推荐，最省事）**：Mac 上 `~/.ssh/id_ed25519` 实测**无口令**且已注册 GitHub →
```bash
pbcopy < ~/.ssh/id_ed25519          # Mac 上复制（不要 cat 到屏幕、不要贴进聊天）
```
手机直接粘贴（同一 Apple ID 的**通用剪贴板**自动同步；若没同步就用 AirDrop 把文件传到「文件」App 再导入）。
克隆 URL 必须用 SSH 形式：`git@github.com:<user>/<repo>.git`。
⚠️ 粘贴完在 Mac 上随便复制点别的东西，把剪贴板里的私钥顶掉；手机本身保持锁屏密码。

**SSH 自生成密钥（更规范）**：GitSync 生成 → 复制公钥 →
- 只给一个仓库：`https://github.com/<user>/<repo>/settings/keys` → Add deploy key → **勾 Allow write access**（不勾=只读，推不上去）
- 整个账号：`https://github.com/settings/keys` → New SSH key

**22 端口被蜂窝网挡时**（GitHub 官方 443 通道，本用户家宽实测可认证）：
```
ssh://git@ssh.github.com:443/<user>/<repo>.git
```

## iOS 上手流程（厂商教程步骤，约 10 分钟）
1. Obsidian iOS 先建一个**空 vault**：Create a vault → 位置 On this device > Obsidian → 内容留空（克隆时会被覆盖）
2. GitSync 引导：Let's Go → 选 **Sync mode**（新手）/ Client mode（熟 git，暴露更多选项）→ 跳过 premium → **允许通知** → 「almost there」跳过
3. **认证**：按上面二选一做（OAuth 或 SSH）→ 填 **Author details**：username = GitHub 用户名，email = **公开邮箱**（⚠️ 别用 `xxxx+用户名@users.noreply.github.com`）
4. **克隆**：选仓库 → 目录选第 1 步那个空 vault 文件夹 → 提示覆盖时选**覆盖**
5. **关掉手机端 obsidian-git**：Obsidian → 设置 → Git 插件设置 → 拉到底 → **Disable on this device**
6. 后台同步用**快捷指令自动化**：Shortcuts → 自动化 → Open App → 选 Obsidian → 关闭「运行前询问」→ 动作选 GitSync **Sync Now**（打开/关闭各设一条可选）。iOS 自带定时同步被系统随机化，可能几天不跑（官方原话）
7. **验证闭环**：手机新建一篇笔记 → 跑一次 Sync Now → Mac 上 `git pull` 看有没有出现

## 官方写明的坑
| 坑 | 后果 / 规避 |
|---|---|
| **同一仓库被两个客户端动** | `index is locked` + 互相覆盖；桌面 obsidian-git、手机 GitSync，分开就对 |
| **author 用 GitHub 私有 noreply 邮箱** | 提交变蓝（blue commits）且**推不上去** → 换成公开邮箱 |
| **完全空的远端仓库** | 官方说会让 obsidian-git 和 GitSync 犯难 → 先有 README/初始提交再克隆 |
| **vault 是大仓库的子目录** | 手机 vault 根 ≠ 仓库根 → 新笔记静默落在 vault 外（见 SKILL.md 硬规则 1） |

## 排障
- **卡住的加载指示器：长按可重置**（官方 Troubleshooting 原文 long-press to reset stuck loading indicator）
- **卡在启动/欢迎页、永远进不到主界面**：issue **#1151**（iPadOS 报告，open，作者未修）——症状与「卡欢迎页」吻合
- App 本身一旦能开，握手失败的典型原因是手机端网络通道连不到远程（见 SKILL.md「中国网络前提」）

## 2026-09-21 个案（状态：服务端已就绪，等用户回报手机端）
现象：iPhone 装 Obsidian + GitSync，GitSync 一打开就卡在欢迎页。
已确认：App 选型正确（GitSync 是移动端官方推荐做法）；Mac 侧仓库与 SSH 通道正常；**Mac 私钥无口令且已授权**，手机端导私钥即可用。
服务器侧已完成（不再需要用户手工建仓库）：父仓库 jiayang 压缩 + `git subtree split` 出的独立 vault 仓库已建并推送 = **`jesse0830/obsidian`**（私有，108 提交 / 53 文件 / .git 2.1M），本地与远程 HEAD 一致；父仓库已 `git rm --cached` 该子目录并写进 `.gitignore`。
现有假设（**均未验证**）：
1. App 自身启动挂起 bug（issue #1151 同症状）
2. 手机没有代理，HTTPS 连不到 github.com，初始化网络请求一直等（→ 正好该走 SSH 方案）
决定性诊断：**开飞行模式 + 关 WiFi 再开 App** —— 断网反而能进主界面 = 网络请求卡住；照样卡 = App 自身 bug（彻底重装 → 仍失败则报 bug）。
已交付清单文件：`99-软件工厂/98 hermes/iPhone端Obsidian同步设置清单_20260921.md`。
⚠️ 在用户回报结果之前，不要把上述假设写成结论或「已修复」。
