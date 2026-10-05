# 在 Obsidian vault 里托管 agent 维护的知识库

适用：用户要在本机新建一个由 agent 长期维护的 markdown 知识库（LLM-wiki / 第二大脑 / 领域笔记库），并要求 Obsidian、知识库、hermes 三者打通。

先勘察再落地。不要凭空造目录结构，先看 vault 里已有什么、装了什么插件、笔记属性怎么约定。

## 1. 宿主位置：放进 vault，不要放 vault 外

`~/Documents/work/jiayang/obsidian-vault/<知识库名>/`

理由：白捡 obsidian-git 的自动 commit+push（本用户每 5 分钟一次）、图谱视图、dataview 查询、iPhone/Windows 多端同步。放 vault 外要另建一套同步管道，还要额外处理与 Obsidian 的边界。

（vault 的仓库架构与手机端同步通道见本 skill 主文件与 `github-china-access`。）

## 2. 目录骨架

原始素材层 + 按类型分层：

```
<知识库>/
├── SCHEMA.md        规范：领域、标签体系、收录阈值、更新政策、版本约定
├── index.md         总目录（每页一句话摘要 + 页面总数）
├── log.md           操作流水，只追加不修改
├── raw/{articles,papers,transcripts,assets}/   原始素材层，只读不改
├── entities/        实体页（人 / 组织 / 产品 / 技术）
├── concepts/        概念页
├── comparisons/     对比页
└── queries/         问答归档
```

一次 `mkdir -p` 建全，然后 `ls -la` 复核——不要在循环体里夹带占位文件，容易「以为建了其实没建」。

## 3. 知识库内部的作业纪律

- **SCHEMA.md 是「宪法」**：每次动作前先读 SCHEMA + index + log，动完往 log 追加一行 `## [YYYY-MM-DD] action | subject`。
- **标签先入表后用**：标签体系在 SCHEMA 里列全再使用，禁止随手造标签——标签一泛滥，dataview 查询就废了。
- 页面 frontmatter：`title / created / updated / type / tags / confidence`。
- 用户有「每份文档标版本号、v1.0 起递加、标在文件名末尾与文档头」的约定，知识库页面同样遵守。
- 内容页至少两条出链（链到相关页或 SCHEMA/index），否则会变成图上孤岛。

## 4. hermes 侧接线（只有一步）

往 `~/.hermes/.env` 追加：

```
WIKI_PATH=/Users/<user>/Documents/work/jiayang/obsidian-vault/<知识库名>
OBSIDIAN_VAULT_PATH=/Users/<user>/Documents/work/jiayang/obsidian-vault
```

- 写**绝对路径**：`.env` 走 dotenv 读取，不做 `~` 展开，写 `~` 会静默失效。
- 追加前先 `grep -q '^WIKI_PATH=' ~/.hermes/.env` 判重，避免多次追加出重复行。
- 这一步与 `git push` 都是**需用户确认的动作**，单独问一次。

## 5. 三层边界（最容易做错的地方）

| 层 | 位置 | 存什么 | 特性 |
|---|---|---|---|
| 知识库 | `vault/<知识库名>/` | 会被重复引用的结论、概念、对比、素材 | agent 提炼，图谱可查，多端同步 |
| hermes 记忆 | `~/.hermes/memories/MEMORY.md` | **关于用户的事实**（身份、环境、约定、当前状态） | 每轮注入，有硬字数上限，必须短 |
| 流水 | `vault/smardaten/daily/` | 当天做了什么、临时状态 | 按时间堆，不做提炼 |

规则：**同一结论只写一处**。知识库页面不复制记忆条目；记忆里只放一句「指向知识库」的定位（位置 + 用途），长内容一律外移——记忆有字数上限，塞长文会把别的条目挤掉。

⚠️ `~/.hermes/vault/` 是 Hermes 的**加密凭据保险箱**，与 Obsidian vault 完全无关，别混淆、别改动。

## 6. 落地顺序与验证

1. 勘察：vault 现有子目录、`.obsidian/` 插件清单、已有笔记风格与属性约定。
2. 写文件：SCHEMA → index → log → 首篇内容页（一般是「三层生态/入口说明」页）。
3. 接线：`.env` 两个变量（需确认）。
4. 推送：`cd <vault> && git add <知识库名> && git commit -m '...' && git push`（需确认；obsidian-git 5 分钟内也会自动做掉）。
5. 验证：`git ls-remote origin` 看服务端真值（绕开本地缓存）；Obsidian 图谱视图里 index ↔ 页面 ↔ SCHEMA 能连成边；dataview 按 `type` 或 `tags` 能筛出页面。

## 7. 坑

- **被安全确认拦下的命令整条不执行**（不是执行一半）：所以「建目录/写文件」与「改 `.env`/push」必须分成两条命令，混写会让你误判状态；被拦后不要原样重试，把需授权的那一步拆出来单独征求同意，或给用户可粘贴的命令让他自己跑。
- **改 `.obsidian/*.json` 前先 `pgrep -x Obsidian`**：Obsidian 运行时把配置持在内存、退出时整体覆写，手改会被静默吃掉。附件默认位置这类要在 GUI 里改（设置 → 文件与链接）。
- 附件目录可以指向 `<知识库>/raw/assets/`，让抓下来的图片自动归档，不要散落在 vault 根。
- 勘察时找 vault 别只按名字匹配——`~/.hermes/vault/` 会撞上，按绝对路径判断。
