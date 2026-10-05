---
name: hermes-memory-management
description: Use when 用户要查看/扩容/清理记忆、把 Hermes 的 memories/skills 推 git，或要给 Hermes 接 app 的 MCP server、改 Hermes 配置。管理 Hermes 记忆、技能目录、配置与 git 同步。
version: 1.0.0
---

# Hermes 记忆管理（MEMORY.md / USER.md）

## 触发场景
- 用户问记忆容量能不能加、记忆满了、要清理记忆清单、或要推送记忆到 git
- 要了解当前记忆文件结构和占用情况
- 要把 Heremes 的 skills 目录也纳进 git / 确认哪些仓自动提交、哪些手动推
- 要改 Hermes 配置（memory 上限、mcp_servers 等）或把本地桌面应用自带的 MCP server 接进 Hermes

## 关键事实
- 记忆文件：~/.hermes/memories/MEMORY.md（工作笔记）和 USER.md（用户画像），条目以 § 分隔
- 软链：~/.hermes/memories → ~/Documents/work/jiayang/hermes-memory/。**它不是独立子仓**：在该目录里 `git rev-parse --show-toplevel` 返回 `/Users/jesseyoung/Documents/work/jiayang`，MEMORY.md / USER.md / SOUL.md / english-plan.md / holographic-facts.md 都是**主仓里被跟踪的文件**。所以「推记忆」就是在主仓 `git add` + `commit` + `push`，别 `git init` 造子仓，也别把该目录当成一个能单独 push 的仓
- 用户习惯：记忆改动后必须 commit + push（中文 commit message）
- **另一个存储容易被遗忘**：Holographic 事实库在 `~/.hermes/memory_store.db`（SQLite），被本仓库 .gitignore 排除 → 事实从没进过 git；需用「导出可读备份」的方式补上（见下文）

## 容量调整
```bash
hermes config set memory.memory_char_limit 5000   # MEMORY.md 上限（默认2200）
hermes config set memory.user_char_limit 2500     # USER.md 上限（默认1375）
```
- 当前配置：5000 / 2500（2026-08-25 调高）
- 影响：记忆每回合注入系统提示，越大 token 成本越高；几千字符可忽略，1万+ 才需警惕注意力稀释；记忆改动会打破 prompt 缓存
- 注意：memory 工具返回的 usage 可能仍按旧上限显示百分比，实际以 config.yaml 为准

## 记忆瘦身工作流（用户验证过）
1. 读两个文件：read_file MEMORY.md + USER.md
2. 分类清单（表格呈现，编号）：
   - 🔴 删除：过期（日期已过）、重复（两条内容重叠）
   - 🟡 精简：细节已存在文件/skill 里，记忆只留指针+关键摘要
   - 🟢 保留：长期有效（业务目标、用户偏好、技术配置、凭证）
3. 删前验证：被删条目若引用文件/路径/skill，先 grep skills 确认细节在别处存在（例：周计划Excel路径在 chinese-enterprise-document-writing/references/zhoujihua-resource-analysis.md）
4. 执行：用 memory 工具批量 operations（原子应用，最终字符上限统一检查）：
   - remove：old_text = 唯一子串识别整条
   - replace：old_text + content 整条替换
5. 验证：read_file 记忆文件确认行数/字符数变化
   - **容量接近上限（≥95%）时，新增信息走「就地扩写已有条目」，不要新增条目**：先在文件里把最相关那条的**全文**读出来，整条 `replace`（在末尾追加新事实），长度控制在原条附近即可（例：上限 5000、总占用 4864 时，一条 434 字符的条目扩到 ~470 仍有余量）。改完回读 + grep 新增标志串（新写入的百分比/关键结论）确认真的落盘
6. commit + push（先 git status 看工作树）

## 陷阱
- memory 工具 remove 的 old_text 必须是唯一子串；批量时新内容别撞其他条目的 old_text
- ⚠️ **replace 是「整条替换」，不是局部替换**：old_text 只负责**定位整条**，content 必须是**完整的一条新记忆**。若当成局部替换（只给被改的那一小段），该条记忆的其余内容会被**静默丢弃**——2026-09-21 实测踩过：一条 300 字的长条目被截成一句 20 字的短句。
  - 正确姿势：改前先把原条全文读出来（read_file 记忆文件），改后**立刻回读核对**（或看工具返回的 current_entries），发现被截断立即用完整内容再 replace 一次
  - 想只动一句话时：把整条旧内容原样抄进 content，只改要改的那句
- 凭证类（OA密码、WPS appid/appkey）留在记忆里有泄露风险，但按用户习惯保留，仅在提醒时注明。要点：这些值**已经在历史提交里**，删掉当前行 ≠ 消除风险（彻底清要 filter-repo 重写历史 + force push）；给用户的选项固定三档＝①迁到本机未跟踪文件（加 .gitignore）、MEMORY.md 只留指针 ②保持现状（私有仓库可接受）、但此后新增密钥一律不进记忆 ③迁出并重写历史。**不要擅自改动**——删掉会打断 OA 等依赖该密码的流程；用户没回话就明确写「未做任何改动」。别名侧只留 `sk-ws-前缀` 这种前缀描述不算泄露；holographic-facts.md 导出时已脱敏，扫描应命中 0
- 记忆里引用的 skill 名可能过期（例：smardaten-oa 已归档，实际是 hermes-office-workflow）——精简时顺手修正
- 用户对重复条目敏感（USER.md 曾存两条面试评语风格）——发现重复要指出

## 顺带例行：查看已配置模型
- hermes auth list 只给摘要；完整配置在 ~/.hermes/auth.json 的 credential_pool（每条含 label/auth_type/source/base_url）
- 安全查看密钥：python 脚本递归 redact（len>12 显示前6位+***），绝不直接 cat 出 key
- 当前主模型：deepseek-v4-flash（provider=deepseek）；别名 qwen→alibaba/qwen-plus（国内站 dashscope）；openai-api 仅凭据未启用
- 桌面 app 模型为会话级记忆，切换需手动或 hermes config set model.default

## 同步状态核查（先查再动手）
用户说「记忆帮我同步一下」时，通常**已经同步好了**。先查，不要造空提交：
```bash
cd ~/Documents/work/jiayang/hermes-memory
git status --short && echo === && git log -1 --oneline && echo === && git ls-remote origin master
```
- 判定：`git status` 空 + 本地 HEAD == 远程 SHA = 已同步，直接报状态即可
- 顺手查容量：MEMORY.md / USER.md 字符数与上限（`hermes config get memory.memory_char_limit`）
- 同步汇报时把「已同步」和「本轮补上的缺口」分开写，别把插件早就干完的事当成自己的工作

## 推送到 git（「把记忆以及 git 里的内容推送到 git」）
这句话是**多仓库清点 + 补缺口**任务，不是一条命令。范围固定是三处，少查一处就漏：

| 仓库 | 装什么 | 谁在提交 |
|---|---|---|
| `~/Documents/work/jiayang/hermes-memory`（= `~/.hermes/memories` 软链目标，**主仓内的目录、非独立仓**） | MEMORY.md / USER.md / SOUL.md / english-plan.md / holographic-facts.md | 记忆改动后手动 |
| `~/Documents/work/jiayang`（主仓） | `Jesse/PM-documents/` 下对外工作文档；`hermes-skills/`（= `~/.hermes/skills` 软链目标，同为**主仓内的目录、非独立仓**） | 手动 |
| `~/Documents/work/jiayang/obsidian-vault`（独立子仓） | Obsidian 笔记 | obsidian-git 每 5 分钟自动 |

步骤：
1. 逐仓取状态：`git status -sb` + `git log --oneline -1` + `git rev-parse HEAD`；不确定还有没有别的仓就先枚举：`find ~/Documents -maxdepth 5 -name .git -type d`（家目录另有 `~/.hermes/*` 与 `~/hermes-webui`）
2. 判断记忆是否真需要提交：拿仓库文件字符数与**系统提示里 live 记忆的占用数**（MEMORY x/5000、USER x/2500）对比——一致且工作树干净即已同步，直接报状态，别造空提交
   - 但「工作树干净」有两种可能：**已提交** 或 **被 .gitignore 排除**。先确认文件真被跟踪再下结论：`git ls-files hermes-memory/`（应列出 .gitignore / MEMORY.md / SOUL.md / USER.md / english-plan.md / holographic-facts.md）+ `git check-ignore -v hermes-memory/MEMORY.md`（命中＝被忽略，得先修 .gitignore 的例外规则）
3. 找本轮真正的缺口：多半是**新产出的工作文档还没进 git**（提效方案、面试评价、分析稿那类）→ 按既有约定 `cp` 到 `~/Documents/work/jiayang/Jesse/PM-documents/` 再提交，中文 commit message
4. 凭证扫描（推前必做）：对新增/待推文件 grep `sk-|appkey|appsecret|password|passwd|token|secret|AK[0-9]`；命中但只是「密钥/口令」这种清单里的通用词，要人工确认不含实际值再放行
5. 提交 + push，然后**独立回读验证**（见下）

### 验证硬规则：别信本地跟踪 ref
```bash
git rev-parse HEAD && git ls-remote origin refs/heads/master
```
两串 SHA 相同才算推成功。`git status -sb` 的 `## master...origin/master` 没 ahead/behind、或 `rev-list --left-right --count origin/HEAD...HEAD` 得 0/0，读的都是**本地缓存的 remote-tracking ref**——上游根本没收到也会显示「同步」。汇报时报「本地 HEAD = 远程 SHA」这对值。

### 不在范围里的仓库（查到只报告，别推）
- `~/.hermes/hermes-agent`：Hermes 应用本体（gitcode 镜像），本地领先上游若干提交属正常；升级走 hermes-maintenance / `hermes update`，不是用户内容
- `~/hermes-webui`：上游项目克隆，无自有内容
- 任何带 `.npmrc` 这类**本机凭证相关本地改动**的仓库，盲推有泄露风险

### 汇报格式
① 已同步的（说明是自动插件或早已提交，不算本轮功劳）② 本轮补的缺口（提交号 + 本地/远程 SHA 对照）③ 没动且为什么 ④ 凭证扫描结论。

## skills 目录也入库（软链模式，与 memories 同构）
目的：整库 skill 进 git，Windows / 手机端也能看。做法是**目录搬进主仓 + 原位留软链**，不要新建独立仓。
1. 先量体积：`du -sh ~/.hermes/skills`；`.curator_backups/` 常是体积大头（实测内容 ~10M、备份 ~13M）
2. 复制（先保底，别直接 mv）：`rsync -a --exclude='.curator_backups' --exclude='.DS_Store' ~/.hermes/skills/ ~/Documents/work/jiayang/hermes-skills/`
3. 在 `hermes-skills/.gitignore` 里排除 `.curator_backups/`、`.DS_Store`、就地留的旧备份 `skills.bak-*`（机器产物 + 体积，不进 git）
4. 换软链：`mv ~/.hermes/skills ~/.hermes/skills.bak-YYYYMMDD && ln -s ~/Documents/work/jiayang/hermes-skills ~/.hermes/skills`
5. **改完立刻实测 Hermes 仍能读到 skill**：`hermes skills list`（内置 + local 都正常列出才算过）
6. 提交推送走主仓（见上一张表），确认无误后再删 `skills.bak-*`
- 陷阱：`skills.external_dirs` 是给**外置追加目录**用的，不是换主目录的开关——换位置就走软链，和 memories 保持一致；软链生效**不需要**重启进程，但 `hermes skills list` 必须实测过一次再汇报
- 顺手检查记忆的同步清单：三层（obsidian 独立子仓 / jiayang 主仓含 memories+skills / 旧工作区）要分清哪些是自动提交、哪些要手动

## Hermes 配置 与 本地 App 接线
`~/.hermes/config.yaml` 对 agent 是写保护的，改配置一律走 `hermes config set`；把本地桌面应用自带的 MCP server 接进来、以及 app 侧开关落在哪个文件——见 `references/hermes-config-and-mcp-wiring.md`。

## Holographic 事实库导出备份
事实库只有二进制 .db、又不在 git 里，换机器或库损毁就全没。做法是导出一份**可读、脱敏**的 markdown 进记忆仓库：
- 脚本：`scripts/export_holographic_facts.py`（同 `~/.hermes/scripts/export_holographic_facts.py`）
- 产物：`~/Documents/work/jiayang/hermes-memory/holographic-facts.md`——按 category 分组（用户偏好/项目/工具/通用），带条目 ID 与日期，末尾附 entities 表
- 脚本对列名自适应（`PRAGMA table_info`），库结构变动不会直接崩；**幂等**：无变化静默退出（exit 0、无输出）
- **有变化时脚本自己 commit + push**（提交信息形如「记忆导出：Holographic 事实库可读备份 <日期>」，输出「已导出并推送（N 条）」）。所以顺序是：**先跑导出脚本，再做本轮记忆/文档的提交**——脚本把主仓推干净之后，`git status` 剩下的差异才是本轮真正的缺口；它的产物不要手动再提交一次
- 推荐挂 cron，零 token 纯脚本：
  ```
  cronjob(action='create', no_agent=True, schedule='every monday 9am',
          script='export_holographic_facts.py', name='Holographic 事实库每周导出')
  ```
  相对路径解析到 `~/.hermes/scripts/`；`no_agent=True` 表示 stdout 原样投递、不跑 LLM；无输出即不发送（watchdog 式静默）
- 脱敏规则（导出前必做，否则等于把密钥新写一份进 git）：①关键词上下文（密码/appkey/appid/secret/token/api_key 后面跟的 `：`/`=` 值）②`sk-` 前缀密钥 ③`[A-Z]{2}\d{8}[A-Z0-9]{4,}` 型 appid ④长度 ≥16 的十六进制串。导出后**必须回查所有已知密钥片段在产物里搜不到**，再 push
- 自己看一遍产物：简历类事实里的手机号/邮箱默认**不**脱敏（私有仓库且简历信息本身就要），但要在汇报里主动告知用户、给他选择

## 相关文件
- `scripts/export_holographic_facts.py`：Holographic 事实库 → holographic-facts.md 导出+推送（幂等）
- references/memory-cleanup-worked-example.md：2026-08-25 实测瘦身清单示例
- references/hermes-config-and-mcp-wiring.md：config.yaml 写保护（用 `hermes config set`）、本地 app 自带 MCP server 的接线与验证、app 侧开关落点
