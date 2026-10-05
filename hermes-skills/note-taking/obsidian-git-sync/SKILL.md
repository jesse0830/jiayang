---
name: obsidian-git-sync
description: "Use when 配 Obsidian 多端 git 同步或排查同步冲突。"
---

# Obsidian 多端 git 同步

把 Obsidian vault 用 git 在多台设备间同步：桌面用 obsidian-git 插件，手机用独立 git 客户端（GitSync）。核心不是 App 设置，而是**仓库架构**——架构错了会静默丢笔记。

## 何时用
- 用户要把 Obsidian 同步到手机（iPhone / Android）
- vault 现在放在某个大仓库的子目录里，想用手机打开
- 桌面 obsidian-git 插件配置、自动提交节奏、冲突处理
- 两个 git 客户端抢同一个 vault（index.lock、双向覆盖）

## 三条硬规则

**1. vault 必须是「独立仓库的根目录」，不能是大仓库的子目录。**
手机端 vault 根 = 克隆下来的仓库根。若 vault 是 `bigrepo/obsidian-vault/`，手机克隆整库后 vault 根会变成 `bigrepo`：手机上新建的笔记落在 `obsidian-vault/` **外面**，Mac 端 vault 里永远看不到——**静默丢笔记**，最难发现。同时大仓库里的无关敏感文件（GitHub 恢复码、简历、证件照）会被一起拉到手机。
拆分（保留完整提交历史，不动原仓库历史）：
```bash
cd <大仓库>
git subtree split --prefix=<vault子目录> -b vault-split          # 历史独立成新分支
# 建好空的私有仓库后（用户 30 秒在网页建，不要勾 README）
git push git@github.com:<user>/<vault仓库>.git vault-split:main
# 原仓库移除并忽略
git rm -r --cached <vault子目录> && echo "<vault子目录>/" >> .gitignore
```
拆完不用改 obsidian-git 配置：它用 isomorphic-git 的 findRoot 从 vault 目录**逐级向上找最近的 `.git`**，会自然认到 vault 自己的仓库。

**2. 同一个 repo 不能同时挂两个 git 客户端。** 手机端必须关掉插件的 git 功能：Obsidian → 设置 → Git 插件设置 → 拉到底 → 打开 **Disable on this device**。这是 obsidian-git 官方 FAQ/Troubleshooting 的明确要求（否则 index 锁 + 互相覆盖）。

**3. 手机端两条路线都可用——但必须先确认设备上装的到底是哪一个。**
「手机端 git 同步」有两个完全不同的东西，配置入口、认证方式、失败模式全不一样，**步骤不可互相套用**：

| | GitSync | obsidian-git 插件 |
|---|---|---|
| 形态 | **独立 App**（App Store） | 桌面那个插件在手机 Obsidian 里跑（`isDesktopOnly: false`） |
| 认证 | OAuth 或 **SSH 私钥导入** | **只有 HTTPS + PAT**（isomorphic-git 不支持 SSH） |
| 官方态度 | obsidian-git 官方**推荐**手机端用它 | 官方标注移动端 "highly unstable ⚠️"，但**确实能用** |
| 设置入口 | App 内 | Obsidian → 设置 → **第三方插件** → obsidian-git |

→ 用户说「我在 Obsidian 里装了 git 插件」= **插件路线**，别把 GitSync 的清单丢给他；反之亦然。
**这个错位真实发生过**（上一轮按用户话术产出 GitSync 清单，结果他手机上装的是插件，配置路径完全不同）。判断依据：能说出「在 Obsidian 里装插件」的一律按插件处理；只有提到「装了个 App / App Store 下载的」才是 GitSync。

## 桌面端（本用户现状）
- vault：`~/Documents/work/jiayang/obsidian-vault`，obsidian-git 每 5 分钟自动 commit+push（SSH 443 通道）
- `~/Documents/Obsidian Vault` 是空壳目录，勿用
- 仓库/通道细节见 `github-china-access` → `references/jiayang-obsidian-vault-sync.md`

## 桌面端：agent 维护的知识库放哪（复用同步，别另建管道）

要新建一个 agent 长期维护的 markdown 知识库（wiki / 第二大脑 / 领域笔记库），**放进 vault 里**，例如 `~/Documents/work/jiayang/obsidian-vault/LLM-wiki/`。理由：obsidian-git 的 5 分钟自动 commit+push、图谱视图、dataview、iPhone/Windows 多端全部白捡；放 vault 外就得再搭一套同步管道，还要额外处理与 Obsidian 的边界。

- 落地配方（目录骨架、hermes `.env` 接线、三层边界、验证清单、坑）：`references/vault-hosted-knowledge-base.md`
- 接线只需两个环境变量写进 `~/.hermes/.env`：`WIKI_PATH=<vault>/<知识库目录>`、`OBSIDIAN_VAULT_PATH=<vault>`。**写绝对路径，不要用 `~`**（`.env` 不做 shell 展开）；追加前先 `grep -q '^WIKI_PATH=' ~/.hermes/.env` 判重
- 三层边界别混：知识库存「知识与结论」，hermes `memories/MEMORY.md` 存「关于用户的事实」（每轮注入、有硬字数上限），`vault/smardaten/daily/` 存流水。同一结论只写一处，记忆里只放「指向知识库位置」的一句话
- ⚠️ `~/.hermes/vault/` 是 Hermes 的**加密凭据保险箱**，不是 Obsidian vault。勘察时用 `find`/glob 找 `*vault*` 会把两者混在一起——按绝对路径判断，别看名字

**动笔顺序**：勘察 vault 现有结构与插件 → 一次写完知识库文件（不需授权）→ 最后才碰 `.env` 与 `git push`。后两步是需用户确认的动作，**单独成一步问一次，不要和建目录/写文件混在同一条命令里**：被安全确认拦下的命令是**整条不执行**（不是执行一半），混写会让你误判「已完成」，也不该原样重试。

**改 `.obsidian/*.json` 前先 `pgrep -x Obsidian`**：Obsidian 运行时把配置持在内存、退出时整体覆写，手改会被静默吃掉；附件默认位置这类要在 GUI 里改（设置 → 文件与链接）。

## 手机端（GitSync）
厂商 iOS 流程、App 事实、已知启动挂起问题与排查顺序：`references/gitsync-mobile-setup.md`。
要点速记：开发者 **ViscousPotential Ltd**（商店里有 ObSync 等易混 App）、**要求 iOS 15.6+**、首次引导要**先自己建空 vault 再克隆进去并选择覆盖**、后台同步靠**快捷指令自动化**（iOS 自带定时同步会被系统随机化，可能几天不跑）。

**认证方式二选一，先做 1 分钟探路再决定**：手机上用 Safari 打开 `github.com` —— 能秒开就走 **OAuth**（App 内点一下 + 浏览器授权，全程序点按，最省事）；打不开/一直转圈就走 **SSH**（本用户家宽实测 22 与 443 均通；手机没有 Clash 代理，所以大概率是这条）。
- **SSH 最省事的路子**：Mac 上 `~/.ssh/id_ed25519` **无口令**且已注册到 GitHub → `pbcopy < ~/.ssh/id_ed25519` → 手机粘贴（同一 Apple ID 的通用剪贴板自动同步）→ 认证页选 SSH 导入私钥 → 克隆用 **SSH URL**（`git@github.com:<user>/<repo>.git`，不是 https）。GitHub 侧零改动。⚠️ 私钥进过剪贴板后，Mac 上随便复制点别的东西把它顶掉。
- 蜂窝网挡 22 端口时换 URL：`ssh://git@ssh.github.com:443/<user>/<repo>.git`
- **author 邮箱别用 GitHub 的 `noreply` 私有邮箱** → 提交会变蓝（blue commits）且**推不上去**；GitSync 的 Repository Settings 里能改。
- 官方明确：**完全空的仓库会让 obsidian-git 和 GitSync 犯难**，远端仓库先有 README 之类的文件再克隆（本用户的 vault 仓库已有 108 提交，正好避开这个坑）。
- 验证闭环：手机新建一篇笔记 → 跑一次 Sync Now → Mac 上 `git pull` 看有没有出现。

## 手机端（obsidian-git 插件，HTTPS + PAT）

用户设备上装的若是插件而非 GitSync，走这条。**完整分步、每个对话框的原文提示、源码验证结论见 `references/obsidian-git-mobile-ios.md`。**

**用户贴报错截图时先看这条**：`Can't find a valid git repository. Please create one via the given command or clone an existing repo.` → 这是插件 `checkRequirements()` 返回的 `missing-repo`，含义是**这个 vault 里还没有 `.git`，即「克隆一次都没成功」**，**不是**认证错、不是网络错、也不是插件没装好。对策 = 让他去跑 `Git: Clone an existing remote repo`，**别让他反复点 Commit-and-sync**（同步的前提是先有仓库）。其余错误码（401 / 403 / Network）怎么分诊见同一份 reference 第六节。

五个必须先知道的点：

1. **认证只有 HTTPS + Token**（isomorphic-git 硬限制，无 SSH），且插件**没有任何代理设置项** → 手机必须自己能连上 `github.com`。先让用户用 Safari 探一次，不通就得先解决网络（手机代理 / Wi-Fi 指向 Mac 的 Clash / 改走 GitSync 的 SSH）。
2. **克隆对话框只问 URL、目录、克隆深度，根本不问账号密码** → **用户名与 Token 必须在克隆之前**在插件设置里填好，否则克隆会先失败一次再弹框问（密码存在 Obsidian 本机 localStorage，**不进 git 仓库**，安全）。
3. 克隆到 vault 根目录时会被问 **「远端仓库根目录有 .obsidian 吗」** → 答 `YES` 后要求确认删除本地 `.obsidian`（按钮 `DELETE ALL YOUR LOCAL CONFIG AND PLUGINS`）——这是**正常且必须**的：仓库里带着 `.obsidian`（含插件本体），克隆完会重建，所以手机上先别费劲调配插件设置，会被覆盖。
4. **提交身份（Author name / email）在克隆前不显示**（源码里有 `gitReady` 门控），克隆完才出现在同一个设置区；填的是该仓库 `.git/config` 的 `user.name` / `user.email`（iOS 没有系统 git，写不进全局配置）。
5. **若 `.obsidian/plugins/obsidian-git/data.json` 被跟踪，两端设置共享 → 改一边 = 改两边**。好处是手机克隆完自动继承桌面的自动提交/拉取节奏、`pullBeforePush`、`merge` 策略，基本不用手填。

### 手机端在哪点同步（UI 入口——配好后用户必问这个）

手机 Obsidian 的 UI 和桌面**不是一套**，按桌面习惯找按钮一定找不到：

- **命令面板 = 手指从屏幕最顶端往下拉**（官方 Quick Action，默认值就是 Command palette），不是某个按钮/菜单项。拉出来搜 `sync` → **`Git: Commit-and-sync`**。
- **手机没有 ribbon**（官方原文 "The mobile app has no Ribbon."）→ 插件往 ribbon 加的那个 Git 图标（`git-pull-request`）收在**导航栏最右边的 `☰`（Open menu）**里。
- **导航栏只在「不在编辑笔记」时出现** → 让用户先收起键盘/退出编辑。
- ⭐ **推荐做法**：设置 → **Mobile** → **Manage toolbar options** → 拉到底 **Add global command** → 输入 `Git: Commit-and-sync` → 编辑笔记时底部工具栏就多一个同步按钮，一次设置长期省事。

原文引用、Quick Action 被改坏时的修法（设置 → Options → Toolbar → Configure mobile Quick Action）、以及**怎么从官方文档源码仓库取权威说明**（站点正文异步渲染抓不到，规则分支是 `master` 不是 `main`）见 `references/mobile-obsidian-ui-and-docs.md`。

### 验证同步真的发生了（从 Mac 回读，不信手机上弹出的提示）

```bash
cd <vault> && git ls-remote origin            # 服务端真值，绕开本地缓存
git fetch origin --quiet
git log -3 --format='%h | %an | %ad | %s' --date=format:'%m-%d %H:%M'
```
- 本地 HEAD != origin/master → 远程有新提交，看 `%an` + 时间就能判断来自哪台设备（本用户两端同一身份 `JesseYoung`）。
- **手机第一次跑 Commit-and-sync 提示 "no changes" 是正常的**：克隆本身不产生本地改动。让用户随便改一篇笔记再跑一次，才有提交可验证——别把这句提示当成配置失败。

## 中国网络前提（决定成败）
手机端克隆通常走 HTTPS → `https://github.com` 在国内直连超时；Mac 上能打开是因为挂着代理，**手机没有这个代理就会一直转圈**。三条通道按省事程度排序：
1. **换国内托管（Gitee 码云）**：HTTPS + PAT，免代理，最稳最省事（⚠️ 需要用户有 Gitee 账号并建空私有仓库）
2. **手机装代理**（Shadowrocket / Stash + 现有订阅）：保持全在 GitHub
3. **SSH 认证**：`git@github.com` 的 22 / 443 端口在该用户家宽可通，GitSync 支持**导入现有 ED25519 私钥**（`~/.ssh/id_ed25519` 无口令，导入即用、GitHub 侧零改动）；克隆 URL 用 `git@github.com:<user>/<repo>.git`，22 被挡时换 `ssh://git@ssh.github.com:443/<user>/<repo>.git`
通道探测怎么做见 `github-china-access`。

## 支持文件
- `references/vault-hosted-knowledge-base.md` — 把 agent 维护的知识库（LLM-wiki 等）托管进 vault 的落地配方：目录骨架、SCHEMA/index/log 纪律、hermes `.env` 接线、三层边界表、验证清单、坑
- `references/gitsync-mobile-setup.md` — GitSync iOS 上手流程、官方认证方式（OAuth vs SSH 私钥导入）、蓝提交/空仓库等坑、卡启动页问题的现有证据与待验证假设
- `references/obsidian-git-mobile-ios.md` — **obsidian-git 插件**手机端完整配置：iOS 硬限制、克隆 4 个对话框的原文与答案、认证/身份填写顺序、Token 权限、设置对照表、如何从 `main.js` 反查插件真实行为
- `references/mobile-obsidian-ui-and-docs.md` — **配好之后**手机端在哪点同步（命令面板=屏幕顶部下拉、无 ribbon、☰ 菜单、工具栏加全局命令）、官方帮助文档怎么取（`obsidianmd/obsidian-help`，分支 `master`）、从 Mac 回读远程验证同步的脚本
