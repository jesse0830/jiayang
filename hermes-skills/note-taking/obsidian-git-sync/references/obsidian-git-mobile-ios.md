# 手机端 obsidian-git 插件配置（iOS/Android，HTTPS + PAT）

适用：用户手机上装的是 **obsidian-git 插件**（不是 GitSync 独立 App）。
以下结论来自 **obsidian-git 2.39.0** 的 `main.js` 源码反查 + 官方 README，非经验推测。

⚠️ **凭证纪律**：Token 值一律 [REDACTED]，**不写入任何文档、清单、记忆文件**。本文只写「去哪儿填」。

---

## 一、三条硬限制（决定配置方式）

| 限制 | 依据 | 影响 |
|---|---|---|
| ❌ **不支持 SSH** | 官方 README: "No SSH authentication (isomorphic-git issue)" | **只能 HTTPS + Token（PAT）**；桌面那套 SSH 私钥方案在插件路线上作废 |
| ❌ **不支持 rebase** | 手机端只有 isomorphic-git | 合并策略**必须 `merge`** |
| ⚠️ **官方自称 highly unstable** | README 原文 "highly unstable ⚠️"，可能出现克隆/拉取崩溃、缓冲溢出、卡死 | 与体积相关；**几 MB 级别的库风险可控**，几十 MB 以上要提前警告用户 |

补充：插件源码里**没有任何 proxy 设置项** → 手机必须自己能连上 `github.com`。

---

## 二、配置顺序（顺序错了会白折腾）

### 第 0 步：网络自测（不过关后面全白做）
用户用手机 **Safari** 打开 `https://github.com/<user>/<repo>`：
- 能开 → 继续
- 打不开/转圈 → 插件路线走不通（无 SSH、无代理开关）。出路：① 手机装代理 App；② **Wi-Fi 里手动配 HTTP 代理指向 Mac 的 Clash**（需在 Clash 打开「允许局域网连接」，填 Mac 局域网 IP + 7897）——仅该 Wi-Fi 有效；③ 改走 GitSync（支持 SSH）。

### 第 1 步：在电脑上建 Token（别让用户在手机上操作 GitHub 后台）
GitHub → Settings → Developer settings → **Fine-grained tokens** → Generate new token：
- Expiration：1 year
- Repository access：Only select repositories → 选私有 vault 仓库
- Permissions → Repository permissions → **Contents = Read and write**（一个就够）
- 生成后**只显示一次**，当场复制

> 经典 token（Tokens classic）勾 `repo` scope 也可，粒度更粗但更省事。私有仓库必须带 Token。

### 第 2 步：手机准备 vault
- 新建**空 vault**，存 **「我的 iPhone」（本地）**
- ⚠️ **不要放 iCloud**（iCloud 与 git 双重同步会打架）
- ⚠️ 克隆前**别在本地写笔记**（克隆要求目标目录为空）
- ⚠️ **先确认这个 vault 是不是他平时写笔记的**——若里面已有笔记，克隆会把仓库文件并进来、他的笔记会变成未跟踪改动被一起提交，做法要另行商量

### 第 3 步 ⭐ 填用户名 + Token（**克隆之前**）
obsidian-git 设置 → **Authentication / commit author**：
- `Username` = GitHub 用户名
- `Password / Personal access token` = 粘贴 Token

**为什么必须提前填**：源码里克隆对话框只问 URL、目录、深度，**不问账号密码**；密码走 `onAuth` 回调取（`onAuthFailure` 时才会弹框现问）。不预填 → 克隆先失败一次。
这两项存在 Obsidian **本机 localStorage**（`localStorage.setUsername/setPassword`），**不落在 vault 里、不进 git 仓库**，凭证安全 ✅（也正因如此，两台设备各自填一次，不会互相覆盖）。

### 第 4 步：克隆 —— 4 个对话框的原文与答案
命令面板 → `Git: Clone an existing remote repo`

| # | 提示原文 | 怎么答 |
|---|---|---|
| 1 | `Enter remote URL` | `https://github.com/<user>/<repo>.git` |
| 2 | `Enter directory for clone. It needs to be empty or not existent.` | 手机端选项里有 **`Vault Root`**（等于 `.`），也可留空（`allowEmpty`）→ 克隆到 vault 根目录 |
| 3 | `Does your remote repo contain a .obsidian directory at the root?` | 仓库若跟踪了 `.obsidian` → **`YES`** |
| 4 | `To avoid conflicts, the local .obsidian directory needs to be deleted.` 按钮：`Abort clone` / `DELETE ALL YOUR LOCAL CONFIG AND PLUGINS` | 选 **`DELETE ALL YOUR LOCAL CONFIG AND PLUGINS`**（会 `rmdir` 本地 `.obsidian` 再克隆） |
| 5 | `Specify depth of clone. Leave empty for full clone.` | **留空**（小库全量克隆） |

第 3、4 步看着吓人，其实是**正常且必须**的：仓库里带着 `.obsidian`（含 obsidian-git 插件本体、主题、其他插件与设置），克隆完会重建 → 手机拿到与桌面一致的配置。
**推论（要告诉用户）**：手机上先别精心调配插件设置，会被覆盖。

> 选到子目录（非 `.`）时，插件会把 `settings.basePath` 设成该子目录；选 `Vault Root` 则不改 `basePath`。

### 第 5 步：克隆**之后**填提交身份
克隆完，**同一个设置区**才出现：
- `Author name for commit`
- `Author email for commit`

**为什么之后才有**：源码里这两项被 `if (gitReady)` 门控——没有仓库时根本不渲染。
**为什么要填**：iOS 没有系统 git，写不进全局配置；插件把它们写进**该仓库的 `.git/config`**（`user.name` / `user.email`），所以 `.git/` 不进仓库内容，不会和桌面端互相覆盖 ✅
**填什么**：`<用户名>` 与 **与仓库历史提交一致的作者邮箱**（例如 `<GitHub用户名>@users.noreply.github.com`）。
⚠️ 别用 GitHub 的数字前缀 noreply 私有邮箱——官方 FAQ 提到会导致提交推不上去（蓝提交）。

### 第 6 步：验证闭环
1. 命令面板 → `Git: Commit-and-sync`
2. 改一篇笔记 → 再跑一次
3. 去 GitHub 网页看提交列表：新提交在、作者正确 ✅
4. 反向：桌面端改点东西等自动推送 → 手机 `Git: Pull` 能看到 ✅

---

## 三、设置共享（最容易忽略的一条）

若 `.obsidian/plugins/obsidian-git/data.json` **被 git 跟踪**，两端共用同一份设置：

| 项 | 值 |
|---|---|
| 自动提交 / 自动拉取间隔 | 5 分钟 |
| Push on backup | 开 |
| Pull on startup | 开 |
| **Pull before push** | **开**（多端关键，防 non-fast-forward 失败） |
| Merge strategy | **`merge`**（手机不支持 rebase，必须） |

→ **改一边 = 改两边**，要让用户知道。好处：手机克隆完自动继承桌面配置，几乎不用手填。

---

## 四、手机端特有坑

1. **自动同步只在 Obsidian 前台跑**：iOS 会挂起后台 App，定时器切出即停。靠 **Pull on startup**（开着）兜底 → 习惯是「打开 Obsidian → 等它拉完 → 写笔记 → 走之前跑一次 Commit-and-sync」。
2. **一个仓库同时只让一个客户端动**：两端都开着自动同步 + 改同一个文件 = 冲突。要么错开，要么至少别改同一篇笔记。
3. **克隆完 `.obsidian` 是仓库那套**（见第 4 步），别指望保留手机上原有插件配置。

---

## 五、技术：怎么从 `main.js` 反查插件的真实行为

手机端配置的坑（克隆要不要密码、身份字段何时出现、目录能不能留空）在上面全都有确定答案，来源是直接读插件打包后的 JS。方法：

```bash
# 1) 标签/设置项名（看 UI 文案）
grep -o -E '"[^"]{0,45}(Author|Username|token|depth)[^"]{0,45}"' main.js | sort -u

# 2) 函数名与调用点，先定位再读上下文
grep -o -E 'cloneNewRepo|onAuth[A-Za-z]*|setPassword|gitReady' main.js | sort | uniq -c
```

**坑：BSD grep 的 `-E` 不支持大重复次数** —— `grep -o -E '.{0,900}pattern.{0,1200}'` 会直接报 `invalid repetition count(s)` 并**什么都不输出**（看着像"没匹配到"，实际是报错）。要看大段上下文就换 Python：

```python
import re, pathlib
s = pathlib.Path("main.js").read_text(errors="ignore")
for m in re.finditer(r"cloneNewRepo", s):
    print(s[max(0, m.start()-900): m.end()+1200])
```

⚠️ 打包后的 JS 是压缩/混淆的（局部变量 `i/n/s/f`、可选链 `?.`），读的时候**只信字符串字面量与调用结构**，不要猜变量含义；`git_gitManager instanceof <Cls>` 这类分支用来区分「桌面原生 git 实现」与「手机 isomorphic-git 实现」。

---

## 六、失败信号 → 病因对照表（用户贴报错时先查这里）

用户在手机上能看到的**只有 Notice 弹窗文案**。把文案反查回源码里的错误码，就能一次定性，不必让用户来回试。

| 用户看到的文案 | 源码错误码 | 真实病因 | 下一步 |
|---|---|---|---|
| `Can't find a valid git repository. Please create one via the given command or clone an existing repo.` | `missing-repo` | **vault 里没有 `.git` = 克隆从未成功**（用户常误以为是「同步失败」） | 跑 **`Git: Clone an existing remote repo`**（第 4 步），不是跑同步 |
| `Authentication failed` / 401 类 | `auth-failed` | Token 错/过期，或 **Contents 权限没给** | 重发 Fine-grained Token：Contents = Read and write |
| `not found` / 403 类 | `remote-not-found` | Token 的仓库范围没包含这个私有库，或仓库名/用户名拼错 | 核对 `Only select repositories` 与 URL |
| `Failed to fetch` / timeout | network | 手机连不上 `github.com`（无 SSH、无代理开关） | 先 Safari 自测；见 SKILL.md「中国网络前提」 |

⚠️ **第一次克隆完成后跑 Commit-and-sync 提示 "no changes" 属正常**（克隆不产生本地改动），别把这条当失败——见 SKILL.md 的「验证同步真的发生了」。

### 反查手法（把任意 Notice 文案定位回错误码）
```bash
# 全库搜文案片段 → 找到 case "<错误码>" 那一行
PYTHONPATH= python3 - <<'PY'
import re, pathlib
s = pathlib.Path("main.js").read_text(errors="ignore")
for m in re.finditer(r"Can't find a valid git repository", s):
    print(s[max(0, m.start()-500): m.end()+200])
PY
```
本会话实测：该文案在全库**只有一处**，位于 `case "missing-repo": new Notice(...)`，返回点由 `checkRequirements()` 在 vault 内找不到 `.git` 时触发 —— 由此定性「不是认证/网络问题」，避免了一轮无效排查。
