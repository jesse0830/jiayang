---
name: chinese-enterprise-document-writing
description: "Write formal Chinese documents — workplace action plans, survey analysis reports, meeting minutes, improvement plans, official notices, project success case summaries, AND academic research reports (调研报告/课题报告) for university course projects. Handles tone calibration (formal vs. warm vs. academic), evidence-based structure, large-file incremental generation, and common pitfalls."
version: 1.6.0
---

# Chinese Enterprise Document Writing

Write formal Chinese workplace documents for internal company use. Covers action plans, survey analysis, improvement initiatives, meeting summaries, and official notices in the context of Chinese SaaS/IT companies.

## When to Use

- User asks for a "正式文档" / "官方材料" / "行动计划" / "方案"
- **每生成或修改一份文档都必须标递增版本号（用户硬约定）**：新建从 v1.0 起，每次修订 v1.1 / v1.2 累加，文件名末尾与文档头版本行同时标；修订不换名，但版本号必须递加，否则用户分不清哪份是哪一版。
- **数字表要能自己对上加总**：可加项表在合计行下补一行「逐行相加核对」；同一批收益的两种口径（工时口径 / 环节口径）必须写明「互为印证、不可相加」；用户问「加起来是多少」时按「可见行之和 → 整表合计 → 缺哪几行/是否旧版本」三段答。详见 `references/measurement-additivity-and-reconciliation.md`
- **给已有内部方案补写／迭代某一章（用户随后分轮追加、修正措施）** → 按 `references/improvement-plan-iteration.md` 的约定做：patch 定点改＋grep 核对结构＋回复给改动后那一条的全文＋列 1~2 个待确认口径；简化类措施必须同时写审核卡点；**新写的内容默认并入既有稿件的对应条目、不新起独立文件**（融合落点与撤销独立稿的三步见该 reference）
- **需要量化指标／提效预估（"给我预估的效率指标"、"整体综合提效按超过30%"、"要么缩短周期要么降低人员投入"）** → 按 `references/quantified-efficiency-estimates.md` 做：环节权重法＋角色配比法双算法交叉验证、只引用方案内已有基线、每个分项落到缩短周期或降低人员投入、同一份工时不可双算；用户另给**真实项目工作量截图**做实测锚点时，按同文件的「实测锚点」节处理（含用户口头比例与截图数字不一致时怎么落文）
- **用户拿别人写的方案/材料说"先把格式优化下、逻辑关系比较乱，优化完我再提修改意见"** → 不是重写任务：只做排版规范＋结构理顺（**不删内容、不改观点、不改数字**），问题写成清单交用户定，技术流程走 `docx-editing` 技能的**排版重建模式**（含零内容丢失校验脚本）；交付后用户会**分轮**提内容意见（删某一节／把某章并进另一章／整篇重构成"背景、现状与问题、提升方案、落地计划"四大部分 —— 这是他认可的方案类骨架），多轮迭代的脚本约束、章号重排后的交叉引用清查、连带清理下游引用见 `docx-editing` 的 `references/iterative-restructure-and-renumbering.md`
- 激励语 / 冲刺动员 / 辛苦话（面向团队或全员的短消息）→ 见 `references/motivational-and-mobilization-messages.md`。**用户贴出自己写好的草稿说"帮我优化下"时，先读该文件末尾「优化用户自写草稿」一节**（保留原话骨架、按四条刀口改、交付群发版+精简版+干部版+改动说明表）。**先定口径再写**：目标导向版（压目标、讲结果与奖惩）还是单纯辛苦话版（只谢付出）。用户说"单纯发一段辛苦激励的话"时，机制、目标数字、会议口径、历史记忆背景一律不写；短消息直接在聊天给全文，不必落文件
- 绩效考核模型设计（DE/IE/AE/数据开发月度考核、工时审批机制）→ 见 `references/performance-assessment-model.md`（含四维权重框架、度量单元问题、任务外补偿、分档红线、简历评语润色方法）
- 客户/高管方案汇报话术（给客户高层讲方案前的逐字稿）→ 见 `references/report-speech-writing.md`（PPT+飞书妙记素材采集、七段话术骨架、完整版+精简版、Word交付格式）
- 会议纪要驱动的改进方案（提效方案/改进计划：11章骨架、配置耗时三问归因、L1/L2/L3 能力分级、**对外汇报不放内部运营数据**的内容边界、交付位置）→ 见 `references/meeting-driven-improvement-plan.md`
- XMind 思维导图文件解析（.xmind → 结构化文本，比 OCR 精确）→ 见 `references/xmind-parsing.md`（zip 解包 + content.json 递归提取）
- 培训作业（干部培训会 作业一/作业二）：要求以企业微信截图形式放在课程文件夹里，OCR 读取；A/B 题结构与用户写作风格见 `references/training-homework-assignments.md`，docx 生成脚本见 `templates/homework_docx_generator.py`
- Analyzing survey/feedback data and producing a formal response
- Writing improvement plans, team culture initiatives, or process changes
- Any document that will be shared with a team or department publicly
- User asks for a personal training reflection / 培训感想 / 心得体会 (see Document Types → Personal Reflection)
- User asks for an academic research report / 调研报告 / 课题报告 / 学术报告 (see Document Types → Academic Research Report) — these are university course projects, not enterprise documents

## Workflow

### Step 1: Understand the context and audience

Ask clarifying questions if not clear from context:
- Who is the audience? (team members, managers, cross-department, company-wide?)
- What tone is appropriate? (硬朗 vs. 温暖 vs. 中肯)
- Is this a one-time announcement or a recurring process document?

### Step 2: Collect and structure evidence

If survey data is involved:
1. Extract raw data from files (Excel/CSV/forms)
2. Categorize by department, role, or theme
3. Identify:
   - Pain points with highest frequency
   - Pain points with strongest emotion (long text responses)
   - Positive signals worth acknowledging
4. Separate root causes from symptoms

Common categories for Chinese tech company employee feedback:
- 薪酬福利 (can't control → mark as "需向上反馈")
- 流程效率 (可以推动)
- 职责边界 (可以推动)
- 成长发展 (可以推动)
- 团队氛围 (可以推动)

### Step 3: Structure the document

Use this proven structure for action plans:

```
# 标题

**发文单位：XXX**
**发布日期：XXXX年X月**
**适用对象：XXX**

---

## 一、背景与目的

坦诚承认问题（引用反馈中的原话增加可信度）。说明为什么要做这件事。

## 二、行动计划

每条措施包含：
- 具体措施（可执行的动作）
- 责任人（谁负责）
- 时间要求（何时完成）
- 每节以"目标：..."开头

### 措施一：XXXX
### 措施二：XXXX
...

## 三、推进时间表

表格形式：时间节点 | 事项 | 交付物

## 四、预期效果

## 五、结语

署名
日期
```

### Step 4: Tone calibration rules

- **正式版（用户说"更正式一些"）：** 使用"现制定"、"经梳理"、"特制定"等书面语，添加发文单位、适用对象、发布日期、责任人表格
- **温和版（用户没要求正式）：** 使用"我看了"、"我觉得"、"我们一起"等第一人称口语化表达
- **核心原则：** 不做不承诺。如果某个问题超出了作者权限，明确写"需向上反馈"而不是回避

### Step 5: Write the final document

- Use tables for action items (序号 | 具体措施 | 责任人 | 时间要求)
- Use **bold** for key principles and commitments
- Include a 结语 section that acknowledges the team's real feelings
- Sign with the author's name/title and date

### Skeleton + Drip-Feed Generation (骨架+逐点投喂)

When the user provides data **one piece at a time** (e.g. "PM 26人", then later "AE 25人", then "收入7200万") and wants the document updated immediately after each data point:

1. **Create the skeleton first**: Write a complete markdown structure with all planned sections and `（待投喂）` placeholder markers where data is missing.
2. **Write to file immediately** — don't wait for all data to arrive before starting.
3. **Patch in place for each data point**: Use `patch` with `old_string` targeting the corresponding placeholder. Replace only the relevant subsection — don't rewrite the whole file.
4. **Keep the scaffolding**: Leave unfilled sections with their markers so the overall structure remains visible.
5. **Calculation cascades**: When a data point affects cross-referenced numbers (e.g. "提效30%-50%" changes the HC gap calculation), update both the data section AND the dependent calculation section in the same pass if possible.
6. **Table-first for ratio/rules data**: If the data is a set of ratios (1:1:3:1:1) or headcount breakdowns, put it directly into a comparison table rather than narrating it in prose first.

**Contrast with Incremental Generation (below):**
- Incremental: user gives high-level task → agent writes a full chapter section → user reviews → agent appends next chapter. Best for 8000+ word narrative documents.
- Skeleton+Drip-Feed: user gives one data point → agent fills one subsection → user gives next point → agent fills next subsection. Best for data-dense planning documents.

**Common document types for this pattern:**
- HC/Headcount planning reports
- Budget allocation documents
- Project resource estimates
- Org chart planning documents

#### Project Plan Image → HC Gap Analysis Pipeline

Sometimes the user provides a project plan as an **image (screenshot/photo)** rather than as written data. The workflow:

1. **Install OCR tool** (first time only): `brew install tesseract && brew install tesseract-lang` (for Chinese language support)
2. **OCR the image**: `tesseract <image_path> stdout -l chi_sim+eng 2>/dev/null`
3. **Extract project names + amounts**: Parse the OCR output (it's messy — expect line breaks in wrong places, mixed Chinese/English, table structure lost). Manually organize into a clean project list.
4. **Categorize by business source** (PO制/项目制) and by customer (e.g. 中远川崎 vs 通州高新集团)
5. **Sum up total amount**: Cross-verify with user's stated revenue target (e.g. OCR result ~1,020万 vs user's 1,000万 — close enough)
6. **Flag uncertain items**: Items marked as "商机阶段" or similar should be noted as low-probability and excluded from hard calculation
7. **Feed into HC gap calculation**: Use the verified project total as the `项目总盘子` input

**Known OCR quirks with tesseract + Chinese:**
- Numbers may be concatenated (e.g. "90万" as "90万" fine, but "830万" might render as "8 3 0万")
- Table borders cause noise characters
- Handwritten annotations are unreliable
- Best practice: OCR once, manually verify each project+amount against any visual context in the image

For HC planning or delivery-model documents, consider generating an **architecture diagram** (HTML/SVG) as a visual companion alongside the markdown document. This is especially useful when:

- The document describes **business source → delivery mode → location** mapping (e.g. 客户经营部/城市运营部 → 3种/区域化交付模式 → 具体城市)
- The structure has a clear **top-down hierarchy** (渠道 → 模式 → 城市 → 人员策略)
- The output will be presented to company leadership (who prefer visual overviews)

Use the `architecture-diagram` skill to generate a dark-themed HTML diagram. The diagram should mirror the document structure but present it visually. Save it in the same directory as the markdown document (e.g. `99-软件工厂/业务来源交付模式图.html`).

Typical elements per node:
- Node name (项目/渠道名称)
- Delivery strategy (交付策略: 本地招聘 / 集中交付 / 现有人力)
- HC status (满编 / 缺N人 / 待定)
- City annotation (南通 / 南京+宿迁 / 成都 etc.)

The diagram serves as a navigation aid — the document is the source of truth.

### ⚠️ Revenue Classification: 首付款/质保款 — 包含/排除 取决于用户当前口径

**核心原则：这个口径是动态的，每次做 人效 计算时必须先跟用户确认。** 用户在不同阶段有不同的口径要求，不要默认用上次的结论。

**历史演变（以该用户为例）：**
- 阶段A（方总指出后）：首付款/质保款 **剔除**，理由是"不用人力投入"
- 阶段B（2026年7月会话后）：首付款/质保款 **包含**，直接拿总收入算

**正确工作流：**
1. 先说「去年的分析口径是[剔除/包含]首付质保，现在这次怎么算？」
2. 等用户明确回答后再执行
3. **不要自己假设** — 两种口径都有道理，用户的需求在变

如果用户说**包含**：
```
人效 = 全年总收入（含首付质保） ÷ 全年总投入人天
```

如果用户说**剔除**（旧口径，供参考）：
| Category | 排除原因 | 示例里程碑 |
|----------|---------|-----------|
| ❌ 首付款/预付款 | 无人力投入，签约即收 | `首付款`, 备注含"首付"/"预付" |
| ❌ 质保款/维保款 | 低人力投入，验收后收 | `质保款`, `质保款1`, 备注含"质保" |

排除方法：逐笔入账检查 里程碑列 + 备注列，确认后执行排除计算。

### ⚠️ User Preference: No Budget/Salary Estimates in Planning Docs

This user does NOT want salary/budget estimates in headcount planning documents. Do NOT include sections like "招聘预算参考", "新增薪酬估算", "招聘成本测算" or any table with salary ranges. When the user sees one, they will say "不需要招聘预算估算" — remove it immediately. The planning document should focus on: role counts, ratios, efficiency targets, revenue data, and phased ramp-up plans. Money/payroll estimates are out of scope.

### Business Source → Delivery Mode Mapping

Many HC planning documents involve a **two-channel business source** model:

| 渠道 | 交付模式 | 人员策略 |
|:---|:--------|:--------|
| 客户经营部 | 模式1: 合同驻场 | 本地招聘 |
| 客户经营部 | 模式2: 普通合同 | 南京+宿迁集中交付 |
| 客户经营部 | 模式3: PO项目 | 南通+苍南本地交付 |
| 城市运营部 | 区域化现场团队 | 各地现有人力+本地招聘 |

Common patterns:
- **驻场项目** (一年起步) → 必须本地招聘，无法远程
- **普通合同** (无需驻场) → 总部基地（南京/宿迁）集中交付最优
- **PO项目** → 可复用已有区域团队（南通/苍南）
- **区域化项目** (成都城投/南通通州/无锡数据中台) → 现场团队为主，总部仅承担指导角色

When building the HC gap analysis after the user provides the delivery mode, cross-reference each region's projects against its current HC by role to identify specific gaps.

## Headcount Planning Report (人员HC规划报告)

For documents planning personnel headcount for a department/team for a coming period.

### Chapter Structure — Business Source + Revenue in Chapter 1

**Critical structural decision:** The **业务来源（business source channels）** and **收入来源/收入地域分解（revenue sources by region）** both belong in **Chapter 1 (规划背景)**, NOT as standalone chapters. This is because:

1. 规划背景 should answer: "Why do we need this many people?" → because X revenue is expected from Y business channels in Z regions.
2. 业务来源 (who brings the money — 客户经营部 vs 城市运营部) and 收入来源 (where the money is — 南通/成都/南京) are the **upstream context** for all subsequent HC calculations.
3. Keeping them in separate chapters (e.g. Chapter 5 or 6) breaks the logical flow: the audience reads through revenue data (Ch2-3), efficiency tools (Ch4), and only then learns where the work comes from.

**Implementation pattern for restructuring:**

When a user says "把5.1放第一章里" (or similar), this means:
- Move **业务来源** (business source channels, originally separate chapter 5.1) → integrate into Chapter 1 as subsections (1.1, 1.2)
- Move **收入来源/收入地域分解** (revenue sources by region, originally separate section 6.1.x) → also into Chapter 1
- Delete the now-empty source chapter (old Chapter 5)
- Renumber all subsequent chapters (old Ch6 → 5, with internal sections 6.x → 5.x)
- Update all cross-references (tables of contents, internal "见6.1节" links, etc.)

**Execution order (critical):**
1. FIRST: Expand the target chapter (patch new sections into Chapter 1)
2. SECOND: Delete the now-empty source chapter header (patch replace with "" or next chapter's header)
3. THIRD: Renumber all downstream chapters — use `replace_all` for `### 6.` → `### 5.`
4. FOURTH: Run a SEPARATE `replace_all` for `#### 6.` → `#### 5.` (sub-subsection level, not caught by the `###` pattern)
5. FIFTH: Search for any literal references in running text (e.g. "第6章", "6.1节中") and update them
6. SIXTH: Read the first 50-75 lines of the restructured document to verify the target chapter looks correct

**Typical structure** (adapt to user's input order):

```
# [Team] [Period] HC规划

## 1. 规划背景
### 1.1 业务来源（客户经营部 + 城市运营部）
- Channel A: 客户经营部 (3 delivery modes: 合同驻场/普通合同/PO项目)
- Channel B: 城市运营部 (regional projects: 成都城投/南通通州/无锡数据中台)
- With tables showing each channel's project portfolio and delivery strategy
### 1.2 收入来源与地域分解
- Revenue targets by region/city (e.g. 南通530万/月, 成都1,000万)
- Total target (e.g. 半年7,200万元)
- Explanation: how revenue maps to the channels in 1.1
### 1.3 （optional）组织现状
- Current headcount and org structure

## 2. [Previous Year] 全年收入与人效
- Organization chart with headcount by role
- Revenue total + per-capita output

## 3. [Next Period] 收入计划
- Monthly/revenue targets
- Target vs previous period comparison
- Implied productivity gap

## 4. 基于人效工具的人员配比优化
- List each efficiency tool (4+3模式, AE结对, 交付中心, etc.)
- For each: how it works, expected % improvement
- Combined impact table (baseline → with tooling → remaining gap)

## 5. 区域布局HC预估
- Per region/city: current headcount by role, with names
- Notes on external/delegated headcount
- Projected HC gap vs target ratio (e.g. 苍南项目 1:1:3:1:1)
```

**Key patterns:**
- **Role ratio reference** (e.g. PM:AE:DE:IE:数据 = 1:1:3:1:1) is a critical benchmark — place it in section 4 as the "target ratio" to compare each region's actual ratio against.
- **Deduplicate headcount**: A person may appear in multiple project rows. Use unique person count, not project-assignment count.
- **Distinguish "local HC" (base in that city) from "delegated HC" (based elsewhere but project-located)** with a footnote.
- **HC gap calculation**: `target capacity = target revenue / per-capita output` → `current capacity × efficiency multiplier = gap`. Keep this explicit in a table.
- **Data implementation (数据实施/数据开发) bottleneck**: This role (the user's 数据角色) is the hardest to recruit across all regions. Always flag it as a key risk when the gap shows 数据实施 shortage. In the SmarDaten context, 数据实施 is a separate role from DE, with different skillset.
- **Aggregate table recalibration**: When updating one region's data (e.g., Nantong 24→21 core), recalculate ALL totals: 现状总计, 目标总计, 需增补总计, and the narrative description text that references percentages. These are all interdependent — patch them as a single atomic update.
- **⚠️ 人天折合人数 ≠ 在岗人数** — 这是最容易翻车的概念混淆。人天折合数是理论满负荷值（总人天÷22天），在岗人数是实际花名册数。产能利用率≈65%，所以折合数≈在岗数×65%。**永远用实际在岗人数做HC基准，别用折合数。**
- **⚠️ 不要猜输入系数** — 当你在做HC演算时，如果缺少某个参数（如首付款投入系数、提效比例、月均工作天数），不要自己编一个数（如"按30%折算"）。直接展示干净的计算框架，标注"待用户输入"，让用户自己填。不然用户会说"算了，我给你重新理一下"。

**Full analytical methodology** with step-by-step calculations, role breakdowns, multi-scenario analysis, and common pitfalls: see [references/hc-gap-analysis-methodology.md](references/hc-gap-analysis-methodology.md).

**Revenue decomposition: 三分类模式 (PO类驻场 + 已生产完待拿 + 项目交付).** Beyond the 首付款/质保款 exclusion for historical benchmarks, target revenue must be split into three buckets with different HC calculation formulas. See [references/hc-gap-analysis-methodology.md](references/hc-gap-analysis-methodology.md) → 三分类收入分解模式.

**Resource allocation baseline: 周计划系统 Excel.** Beyond revenue data, HC planning needs a baseline of actual personnel allocation by role (who actually does what work). This comes from the SmarDaten 周计划 Weekly Plan system export. See [references/zhoujihua-resource-analysis.md](references/zhoujihua-resource-analysis.md) for the full analysis pattern: data cleaning (skip duplicate header rows), numeric conversion, role ratio computation. Key output: AE:DE:IE:数据开发 ≈ 25:50:21:5 baseline ratio for the company.

**Revenue data source: Excel 订收回计划表 or 收入明细表.** The HC planning revenue input often comes from a structured Excel file. Two common formats:

**Revenue × Resource cross-matching kanban (收入-资源交叉匹配看板):** When the user wants to see how resource person-days (AE/DE/IE/数据开发) map to revenue tiers (<30万 / 30-100万 / >=100万), use the cross-matching workflow in `references/revenue-resource-cross-matching.md`. This combines income data and weekly-plan resource data via project name matching (manual mapping for large projects, fuzzy match for small ones), then produces a tiered kanban showing role-by-role投入 per tier — useful for efficiency analysis and highlighting structural imbalances (e.g. small projects consuming 44% of resources but generating only 30% of revenue).

**Format A — 收入明细表** (本次会话新增): 逐笔收入登记表，184笔×11列，含里程碑/客户/部门/责任人等维度。适用于多维分析：
- 详见 [references/enterprise-revenue-analysis.md](references/enterprise-revenue-analysis.md) — 8维分析标准模板 + Python实现要点
- 用于: 总量汇总、月度趋势、部门排行、大客户集中度、里程碑质量、单笔区间分布
- 交叉分析: 可结合录音反馈（方总目标等）做"听见的×算出的"验证

**Format B — 订收回计划表** (原格式): 时间轴横向排列，双周粒度，含合并单元格。 Key recognition patterns:
- **Column structure**: 时间轴横向排列（7月下 / 8月上 / 8月下等双周粒度），第1行合并单元格作为季度/月头，第2行列标识（订货/收入/回款）在列中重复出现
- **Row structure**: 第3行起每个项目一行，项目名可能在合并单元格中，商机金额列在第1个数据列
- **Deterministic vs Pipeline**: The user may give a full sheet (含所有商机) first, then a "Sheet1" version (仅确定性计划). The two can differ by 5x (e.g. 2,549万 vs 530万). Always clarify which version you're looking at before doing HC calculations.
- **Extraction**: Use Python + openpyxl (`data_only=True`). Handle merged cells via `ws.merged_cells.ranges`. Parse per-row the 收入 column, aggregate by month.
- **Document delivery**: When the analysis flips from "缺人" to "不缺人" based on which version you use, present both scenarios (确定性计划 + 全量商机推演) so the decision-maker has a complete picture.

See [references/hc-gap-analysis-methodology.md](references/hc-gap-analysis-methodology.md) → 「收入数据来源：Excel订收回计划表」 for complete extraction code, example data, and the deterministic-vs-pipeline analysis workflow.

## Project-Tier-Based PM Demand Model (基于项目分级的PM需求模型)

This is a **complementary methodology** to the revenue-based HC calculation. While the revenue model answers "how many TOTAL people", the project-tier model answers "how many PMs specifically" — because PM bandwidth is gated by **project count**, not revenue.

### Core Logic

PM demand is driven by **how many distinct projects** a PM can manage simultaneously, not by revenue proportionality. A 20万 project consumes nearly the same PM energy as a 400万 project (communication overhead, stakeholder management, milestone tracking).

### The 苍南 Benchmark

Use a known reference project to calibrate PM-to-project mapping:

```
苍南项目: 400万合同, 1年周期, 3-4个PM全职驻场
→ 400万 ÷ 3.5人 ≈ 114万/PM/年 (PM承载率)
```

### Three-Tier Classification

Classify all projects by total contract value (not annualized, not per-payment):

| Tier | Range | PM Model | Rationale |
|:-----|:------|:---------|:----------|
| Large | >=100万 | 1+ dedicated PM per project | Revenue justifies full-time PM; similar to 苍南 structure |
| Medium | 30-100万 | 1 PM covers 2-3 projects | Moderate complexity; PM can dual-track |
| Small | <30万 | Multiple projects per PM (e.g. 4-6) | Each project still consumes PM energy proportional to number of projects, not revenue |

### Key Insight: The Project Count Bottleneck

When analyzing a portfolio, **count projects, not just revenue**:

```
Example from 2025 data (125 projects, 3185万 total):
  >=100万:   7 projects (5.6%)   -> 1155万 (36.3%)  -> 7-14 PMs needed
  30-100万: 21 projects (16.8%)  -> 1066万 (33.5%)  -> 7-10 PMs needed
  <30万:    97 projects (77.6%)  -> 964万 (30.3%)   -> 20-32 PMs needed (bottleneck!)
```

**The <30万 tier is the consistent bottleneck**: ~78% of projects by count but only 30% of revenue. Even though these are "small" projects monetarily, each still requires a PM to manage scope, schedule, communication, and delivery.

### Workflow

1. **Get the project revenue breakdown** (Excel with per-project amounts)
2. **Classify every project** by total contract value into the three tiers
3. **Assign PM load per tier**: large->dedicated, medium->shared 2-3, small->shared 4-6
4. **Calculate total PM demand**: sum(projects_per_tier / PMs_per_tier)
5. **Cross-validate with revenue-based HC model**: The PM count from this model should be <= total PMs from the revenue model multiplied by the PM role ratio

### When to Use

- The user explicitly asks "how many PMs do we need" (not just "how many people")
- The project count is high and project sizes vary widely
- The user mentions "苍南" or "驻场" as a benchmark
- Small projects dominate the portfolio by count (>50%)

### PM x Project Mapping Details

See [references/pm-demand-project-tier-model.md](references/pm-demand-project-tier-model.md) for full methodology, Python analysis code, and calibration formulas.

## General Generation Patterns

### Incremental Generation (分批生成)

When the requested document is very large (8000+ words / 15+ pages / multiple chapters):

- **Preferred flow**: Do NOT block-write the entire file in memory first. Write the first portion (e.g. abstract + first chapter) to a `.md` file, confirm with user, then use `patch` to append subsequent chapters.
- **Why**: Large documents exceed single-write token limits and waste time if the user wants to correct direction mid-way.
- **User explicitly prefers**: "先写一部分，再逐渐补充" — write partial, then gradually add.
- **Output format**: Use `.md` by default for large documents. Word generation (`.docx`) is slow and complex — only convert to Word when user explicitly requests it.

### Large File Writing Strategy

When writing files exceeding ~10,000 characters:

1. Write the first major section (abstract + chapter 1) via `write_file` to create the file
2. Use `patch` with `old_string` anchored to the last sentence to append new content
   - Set `old_string` to the last few sentences of the current content (unique string)
   - Set `new_string` to the old content + all new content, ensuring the transition is seamless
3. Repeat for each subsequent chapter
4. Final verification: use `wc -c` + word count check to ensure target length is met

### Feedback-Driven Document Revision (录音反馈→文档迭代)

When the user has a recording (MP3) of leadership feedback on an existing document, use the **audio transcription workflow** to convert speech to text, then integrate findings here.

**Two usage patterns:**
- **Pattern A — 用户直接要求总结录音**（"帮我把这段录音总结一下"）：按照 `references/audio-transcription-workflow.md` → 场景一的模板输出结构化会议纪要，保存到桌面。
- **Pattern B — 录音是已有文档的反馈/迭代输入**（方总反馈→改规划文档）：按以下工作流执行。

**Workflow:**

1. Transcribe the feedback recording via the Whisper transcription workflow (see [references/audio-transcription-workflow.md](references/audio-transcription-workflow.md))
2. Extract structured feedback points from transcript
3. Read the existing document (Feishu API or markdown file)
4. Identify gaps between feedback and current document
5. Produce a gap table: `# | 反馈要求 | 当前状态 | 优化方向`
6. Restructure the document following MECE/金字塔原则

**Common gap types found in leadership feedback (方总 style):**
| 差距类型 | 说明 | 优化方式 |
|----------|------|---------|
| 缺职责定位开篇 | 材料上来就写数据，没写"为什么做""我的角色" | 新增第一章：职责定位与使命 |
| 缺人效模型 | 只写了人员配比，没写配比的依据/基准 | 新增人效模型章节（按城市/类型设三档基准） |
| 缺量化验收标准 | 每条策略没有对应可量化的成果指标 | 新增量化成果总表 |
| 结构不是金字塔 | 平铺直叙，不是目标→策略→成果递进 | 重排为金字塔结构 |
| 维度有交叉 | 各维度之间不MECE，内容重叠 | 清理维度，确保独立穷尽 |
| 缺落地路径 | 只写了目标，没写分阶段怎么干 | 新增分Phase落地路径（Phase 1-3） |
| 缺与协作方的关系变革 | 只写了自己怎么做，没写怎么跟其他人配合 | 新增协作模式变革章节 |

**Output structure** (金字塔原则):
```
1. 职责定位与使命
2. 规划背景与目标
3. 现状数据与基准
4. 核心策略（每条可量化）
5. AI场景落地
6. 各地布局
7. 人才梯队
8. 量化成果总表
```

See `references/feedback-revision-checklist.md` for a template gap analysis checklist.

## Document Types with Specific Preferences

### Best Practice Case Report (最佳实践案例报告)

See [references/best-practice-case-report.md](references/best-practice-case-report.md) for the full template and workflow. This is a distinct genre with its own structure.

### Internal Process Innovation Report (内部流程创新报告)

See [references/internal-process-innovation-report.md](references/internal-process-innovation-report.md) for the full template and workflow. Use this for reports that aggregate multiple AI/tool-enabled workflow innovations across the delivery lifecycle (e.g., "交付中心最佳实践报告"). Covers multiple independent scenarios (3-5), each with validation data, problem analysis, SOP, and efficiency comparison — plus cross-scenario synthesis and phased promotion plans. Distinct from single-project best practice reports.

**Key structure** (8 chapters): 项目概述 → 传统方案痛点 → **核心方案对比**（最重要的章节） → 项目亮点 → 实施内容详解 → 技术亮点 → 客户价值 → 经验总结与可复制性。

**When the report's primary purpose is product superiority demonstration** (e.g., data通 vs 传统模式), Chapter 2 (痛点) and Chapter 3 (核心对比) are the longest and most detailed. Use comparison tables extensively for each workflow step. The reference file has specific guidance for this pattern.

**DOCX extraction pattern**: Use Python zipfile + ElementTree to extract paragraph text from DOCX files (read_file cannot handle binary formats). Quick one-liner:\n```python\nfrom docx import Document\ndoc = Document(path)\nfor i, p in enumerate(doc.paragraphs):\n    print(f"[{i}] [{p.style.name}] {p.text}")\n```\nThis has been reliable for getting 12万字+ implementation document content.\n\n**Report regeneration pattern**: When the user edits the .docx source (adds a new chapter, modifies data), do NOT patch the markdown — **rewrite the entire file**. The report has tightly coupled cross-references (概览表, 汇总表, 经验总结 that reference each scenario) that are prone to drift under partial patches. Full rewrite ensures consistency.

### Personal Reflection / Training Sentiment Documents (感想/心得)

For documents where the user wants to express personal take-aways from a training, meeting, or event (培训感想、心得体会):

**Tone**: First-person, grounded in real experience. Not a formal announcement — the "I" is the author.

**Key pattern: Start from the user's current understanding, then show the cognitive shift.**

The user in this project has a management career arc spanning 10+ years: 研发 → 项目经理 → 管项目经理 → 软件工厂负责人. Effective reflections use this progression as an anchor.

**Structure template** (flexible, adapt to user's input):

```
## Opening — 背景铺垫 (optional)

Briefly set the context: when and what training/event happened. If the user has a specific career arc or prior understanding, mention it here to establish the "before" state. This is where the user's own words (e.g. "我对管理的理解就是把人管好，把结果拿到") give the essay authenticity.

## Body — 认知冲击和转变

Organize around 3-5 key points from the training content that resonated most with the user. For each point:

1. **The new concept** — what the training said (quote the core phrase, e.g. "管理者是'给我上'，干部是'跟我上'")
2. **The contrast** — connect it to the user's prior understanding or behavior ("我以前觉得...但培训让我看到...")
3. **The take-away** — what the user will do differently as a result

Let the user's experience drive the selection: not every slide needs commentary. Pick what hit home for this person.

## Closing — 总结和表态

A brief summary of how the user's understanding has evolved, and a forward-looking commitment.

```

**User corrections/iterations to expect and handle:**
- The user will progressively reveal more personal context. Each reveal is a chance to deepen the reflection, not a correction of the previous draft. Expect 5-10 rounds of iterative refinement. Write a new draft each round rather than patching the old one — the user wants to see the whole essay re-assembled with the new insight integrated.
- The user's prior understanding statement (e.g. "我对管理的理解就是把人管好，把结果拿到") should be kept as a narrative anchor throughout the essay, not just in the opening. Revisit it in each section to maintain a cohesive "before → after" arc.
- When the user reveals specific career transitions (三级部门→二级部门, 研发→项目经理→管项目经理→工厂), integrate them chronologically to build narrative arc. The career timeline becomes the backbone of the essay.
- The essay should feel genuine and specific to this person, not generic. Avoid HR/Slogan language.
- **Key cognitive shift framework for THIS user**: old model = 三要素 (目标→执行→结果) → new model = 四个一 (理念一致→目标一致→行动一致→标准一致). Keep this contrast alive throughout the entire essay.
- **The "明确期望比提升能力更重要" insight** is the user's single most impactful take-away. Position it as the solution to the "标准一致" problem and connect it to the user's self-flaw (自己上): "自己上" happens because expectations were unclear.
- **The "你就是公司" insight** is the user's second key cognitive shift: from "带团队拿结果的人" to understanding that 干部团队是公司经营的核心力量. Give it its own section in the essay, after the "四个一" framework.
- **When the user demands "结构乱了/分个层级":** the essay likely needs restructuring. The preferred structure is chronological by cognitive evolution: 背景介绍 → 旧认知 → 新认知(逐条展开) → 自我反思(结合个人习惯) → 结合当前岗位 → 总结. Use numbered h1/h2 headings.
- **Avoid duplicate content across sections.** If two paragraphs say the same thing about standard-alignment, merge them. The user will catch and complain about redundancy.
- **User role correction pattern**: The user may initially describe their role one way (e.g. "现在要更多做决策"), then correct to a more precise description (e.g. "我是二级部门负责人，核心是抓执行，在执行中做战术决策"). When this happens, rewrite the entire essay with the corrected framing — don't just patch the one sentence. The role definition is the spine of the essay.
- **User's self-flaw pattern**: The user consistently reveals a personal management flaw as a narrative device (e.g. "不行就自己上"). This becomes a recurring thread that ties the essay together. Keep it as a through-line: show how each training insight connects to and addresses this flaw.
- **Default output format**: .md file on Desktop. Only convert to .docx when user explicitly asks for Word format.

**Avoid in personal reflections:**
- Tables with 责任人/时间要求 (those are for action plans, not sentiment essays)
- Formal document headers (发文单位、适用对象)
- Third-person objective tone — this is "I think / I feel / I learned"
- Overly long or exhaustive coverage of every training slide; pick the impactful moments

### Training Homework (培训作业/干部培训作业)

For the recurring 干部培训会 series (2026年: 第一期→第二期→第三期…). Each session assigns homework with a fixed format. Distinct from 培训感想: it answers a specific assignment question, must be Word format with a strict file name, and is submitted by a deadline.

**Assignment format (observed, 第三期):**
- Usually 2 questions (A/B), student picks ONE — but user may ask for both, which is fine
- Word format required, file name: `作业N+姓名+题目.docx` (e.g. `作业一+杨嘉阳+沟通冲突案例复盘与团队激发实践.docx`)
- Submit by deadline (e.g. 8月9日18:00)

**第四期 (2026-09，管理高尔夫课程) 观察**: 作业通知截图可能标为「第N期(主题)作业」（如「第5期(选对人、用好人)作业」），但文件仍归档在 `第四期/` 目录。本期要求：文件名需含「部门 姓名」，9月15日前提交，中途群发一次提醒（不单点），**提交时主送主管、抄送李争辉**。题目二选一：①关键人员招聘的人才画像与面试考察方式 ②下属绩效考核的一致性、可信性问题诊断 + 作为考评主管从认识/意愿态度/能力三方面的改进。命名示例：`作业二+软件工厂 杨嘉阳+绩效考核的一致性与可信性反思与改进.docx`。
- **Diagnostic-type answers (诊断类题，如 ②) 的写法**: 用本部门真实绩效数据做证据（如 4-7月 A/C 人次、同部门 A 的核心分是否雷同、同一人跨月评级波动、C 的判定依据是否只有一句话），但**脱敏不点名**（用「有一位配置开发的同事」）。结构：现状判断（分条列问题，每条一个数据事实）→ 根因（要落到"我自己角色失位"这类主管自身问题）→ 认识上改进 → 意愿态度上改进 → 能力上改进 → 可落地动作（带月份/时限）→ 小结（呼应课程主题）。
- Save path: `/Users/jesseyoung/Documents/work/smardaten/smardatenCorp/07-综合管理/03-干部培训会2026/第三期/` (numbered per 期)

**Content formula that works for this user:**
- **A类题 (案例复盘)**: a real management scenario from the user's actual work (软件工厂交付、跨部门冲突、客户现场), anonymized (脱敏, no real names). Structure: 案例背景 → 用本次培训理论回看问题(2-4条, 每条"理论名词 + 我的错在哪") → 如果重来一次怎么做(分步骤, 每步"动作 + 话术示例"). Use the training's actual framework names (ICON模型, 立场vs利益, 定额心智, 情绪降级阶梯, 有效承诺三工具, 目标设置理论, 自我决定理论SDT, 工作嵌入Links/Sacrifice/Fit…).
- **B类题 (结合公司政策激发团队)**: 现状判断(引用真实数据: 人效模型、产能瓶颈、驻场团队) → 公司现行政策与理论工具的对应表(PBC→目标设置理论, IDP→胜任感, 职级双通道→职业承诺, 授权→自主性, 驻场关怀→工作嵌入) → 3个具体落地动作(每个动作带量化/可执行细节) → 小结.
- **风格**: first-person reflective, 真诚自我反思 (user's established style from 第一期作业), anchor to the 软件工厂厂长 role. No invented names/projects — anonymize or ask.
- **Style reference**: 第一期作业 `杨嘉阳+培训后的个人思考+20260530干部训战营第一期作业.docx` in the 第一期 folder — read it first when a new homework arrives to match voice.

**Deliverable**: generate .docx directly with python-docx (NOT markdown — homework explicitly requires Word). Font pattern: 宋体 body + 黑体 headings (not 微软雅黑 — see Markdown → Word section). ~3500字 is a good length for A+B both.

### Evaluation/Promotion Opinion Documents (评审意见)

For documents like promotion evaluation summaries (晋升答辩评审意见):
- **Do NOT use section headings** — the user explicitly corrected: "不需要用大标题，直接一段话就行"
- Format as a single coherent paragraph, not structured sections
- Start with "下面对XXX的评审意见如下："
- Present all evaluation dimensions inline (comma-separated or semicolon-separated)
- End with a clear conclusion/recommendation sentence
- Keep the same evidence-based structure internally, but remove visible headings

Example structure for a promotion opinion:
```
下面对 [name] [from_level] 晋升 [to_level] 的评审意见如下：
[Name]本次答辩表现突出，汇报内容紧扣晋升核心要求，围绕"[维度1]、[维度2]、[维度3]"展开...
在[维度1]方面，[具体数据+评价]...
在[维度2]方面，[具体数据+评价]...
在[维度3]方面，[具体数据+评价]...
综合来看，[name]在[所有维度]均达到[目标级别]标准，部分维度超出预期，建议予以晋升通过。
```

### Academic Research Report (学术调研报告/课题报告)

For university/college course projects where the user needs a long-form Chinese academic research report (调研报告/课题报告). These are NOT enterprise documents — they follow academic conventions.

**Target audience**: University professor grading the report. Tone is formal-academic, not enterprise-corporate.

**Key differences from enterprise documents:**
- Uses academic chapter numbering: 一、绪论 → 二、调查方案 → 三、数据处理 → 四、数据分析 → 五、系统/工具设计 → 六、结论建议
- Includes 摘要 (abstract) and 关键词 (keywords) at the top
- Requires 参考文献 (references) with proper citation format
- Includes 附录 (appendix) with questionnaires, interview outlines, survey instruments
- Uses first-person "本研究" (this study) not "我司" / "我们"
- Tables use formal academic table captions (表4-1, 表4-2 etc.)

**Standard chapter structure for a survey-based research report:**

```
## 摘要
Brief abstract summarizing research background, methods, findings, and significance.
**关键词**：3-5 keywords separated by semicolons.

## 一、绪论
### （一）调查背景
### （二）研究目的与意义
### （三）文献综述（国内外研究现状）
### （四）研究思路与框架
### （五）研究特色与创新点

## 二、调查方案设计与实施
### （一）调查内容及目的
### （二）调查范围与对象
### （三）调查方式与方法
### （四）抽样方案设计
### （五）问卷及访谈提纲设计
### （六）调研方案实施（含进度表、人员分工）
### （七）质量控制与评估

## 三、数据处理与检验
### （一）预调查数据处理（信效度检验）
### （二）正式调查数据处理
### （三）数据清洗与标准化

## 四、数据分析
### （一）描述性统计分析（样本画像+变量描述）
### （二）Logit回归分析（影响因素分析）
### （三）对应分析（群体差异分析）
### （四）K-means聚类分析（群体画像划分）
### （五）模糊综合评价（碳足迹评价）
### （六）结构方程模型（路径分析/中介效应检验）

## 五、系统/工具设计（调研成果转化）
### （一）设计目标与原则
### （二）整体框架设计
### （三）各模块详细设计
### （四）功能设计（数据输入、存储、报告生成）

## 六、结论与建议
### （一）主要研究结论（分条列出）
### （二）面向[对象]的管理建议
### （三）面向[对象]的行为建议
### （四）研究不足与展望

## 参考文献
（20篇左右，中英文混合，按正式学术引用格式）

## 附录
### 附录一：调查问卷（完整版）
### 附录二：访谈提纲
### 附录三：实地勘察记录表
```

**Content generation rules for academic reports:**
- **Sample size**: Use plausible numbers (~385-420 for questionnaire-based studies). Reference the 10-20x rule for SEM sample size requirements.
- **Statistical rigor**: Include KMO test, Bartlett's test, Cronbach's α values (0.7+ acceptable, 0.8+ good), factor loadings (0.5+), model fit indices (χ²/df < 3, GFI/CFI > 0.9, RMSEA < 0.08).
- **Balance**: Cover both descriptive and inferential analysis. Don't just describe — explain what the numbers mean.
- **Tables**: Use markdown pipe tables with clear headers and footnotes (注: *p<0.05, **p<0.01, ***p<0.001).
- **Carbon footprint / environmental data**: Reference realistic emission factors (kg CO₂/km for transport, kg CO₂/meal for food).
- **Cluster naming**: Give each cluster a descriptive name (e.g., 低碳先锋型, 认知-行为差距型, 随大流型, 低碳漠然型) with plausible percentages.
- **SEM paths**: Report standardized path coefficients, C.R. values, p-values, and direct/indirect/total effect decomposition.

**Length requirement**: The user specified "全文不少于8000字" (minimum 8000 Chinese characters). Use write_file + patch incremental strategy to hit this target. Check with `grep -o '[一-龥]' file.md | wc -l` for Chinese character count.

**Common pitfalls:**
- Don't use 我司/我们 (enterprise tone) — use 本研究/研究团队
- Don't include 责任人/时间要求 tables (those are action plan format)
- Don't skip 预调查/信效度检验 — it's a required section for academic rigor
- Don't forget 附录 with the complete questionnaire and interview outline
- Don't use overly simplistic methods (only descriptive stats) — need regression, clustering, SEM etc. for a full report

**Appendix generation rules:**

When the user asks for the appendix files to be generated as separate `.md` files:

See full appendix generation details at [references/carbon-footprint-form-design.md](references/carbon-footprint-form-design.md) for carbon footprint form design (碳排放因子值表、零代码平台字段配置清单、自动计算逻辑、游客碳迹报告模板)。

**附录1：游客方调查问卷**
- 5-6 个部分：基本信息(人口学)→低碳认知(李克特量表)→低碳态度/意愿(李克特量表)→低碳行为表现(选择题)→碳迹记录意愿(李克特量表)→开放建议
- 基本信息：性别/年龄/学历/职业/收入/客源地/同行人数（7题）
- 量表建议 6-7 题/维度，1-5 级李克特
- 行为表现用情景选择题，不编造数据
- 标题格式：`# 附录1：XXX调查问卷`，问卷开头有称呼问候语和匿名说明
- 额外提示：用户可能还要求生成**景区管理方调查问卷**——但要求文件里提到的"景区管理方调查问卷"实际指的是"景区管理方深度访谈提纲"（半结构化访谈）。确认用户意图后再生成，不要擅自决定。

**附录2：景区管理方深度访谈提纲**
- 5-6 个维度：景区低碳管理现状→低碳设施投入与运营→游客低碳行为观察→数字化/碳迹管理→困难与未来规划
- 每个维度 3-4 个问题，共 15-20 个问题
- 每个问题带追问提示（如：请从交通/垃圾/节能/宣传分别介绍）
- 开放题收尾（"您有什么补充？"）
- 包含访谈元信息（对象/时间/地点/时长/记录方式）
- 标题格式：`# 附录2：XXX深度访谈提纲`

**附录3：深度访谈提纲/实地勘察记录表**
- 如果大纲要求的是"实地勘察记录表"：用表格形式，左侧勘察项目，中间勘察内容说明，右侧填写区
- 表格包含：新能源接驳车/分类垃圾桶/低碳宣传牌/节能标识/生态植被/景区照明/游客步道/餐饮服务/住宿设施
- 底部有勘察日期/人员/天气/游客流量填写栏

**NOTE on appending order:** User may request the files one at a time ("先生成第一个问卷" / "再帮我生成访谈提纲"). Generate as separate `.md` files on Desktop, not one combined file. File naming: `附录1_XXX.md`, `附录2_XXX.md`.

### Best Practice Case Report (最佳实践案例报告)

For documents showcasing a successful project delivery as a "最佳实践案例" — typically used for internal knowledge sharing, customer success stories, or to demonstrate capability for future bids.

**Tone**: Professional but not overly academic. Evidence-driven, data-backed. Should read like a proven methodology rather than a boast. It's about "what we did and why it worked", not "how great we are".

**Key input pattern for this user**: The user provides materials incrementally — first a technical spec/requirements doc, then a project plan, then an implementation plan. Each new piece of material should be integrated into a growing body of project context. The report is assembled section by section as materials arrive.

**When the user says "先把整体材料给你" or "一点一点完善"**: Accept partial materials, build context incrementally, and offer a framework for review. Do NOT jump to write the full report until the user explicitly says to start. Maintain a running material inventory.

**Structure template** (adapt to project specifics):

```
# [Project Name] — 数据中台项目建设最佳实践案例

**客户：** [Customer Name]
**项目类型：** [Project Type]
**交付周期：** [Duration]
**项目金额：** [Amount]

## 一、项目概述

### 1.1 客户简介
Brief description of the customer — industry, scale, organizational complexity.

### 1.2 项目背景与挑战
What was the situation before? Key pain points (data silos, manual processes, regulatory pressure).
Reference policy drivers where applicable (e.g., government mandates, industry regulations).

### 1.3 承担范围
What was our scope vs. the overall project? Use a clear scope table if the project is part of a larger program.

## 二、项目亮点与核心价值

2-3 bullet points that make this project special. For this user's typical projects:
- Ultra-fast delivery (e.g., "3周完成270万数据中台交付")
- End-to-end coverage (e.g., "从数据采集到决策看板全链路")
- Standardized, repeatable methodology

## 三、快速交付方法论

3.1 分阶段推进（用甘特图或时间线展示）
3.2 标准化产品能力支撑
3.3 客户协同机制

## 四、实施内容

Organize by major work streams, not chronological order. For data platforms:
4.1 需求与方案
4.2 数据治理标准
4.3 数据接入与底座
4.4 主数据管理
4.5 数仓与专题库
4.6 可视化与决策看板
4.7 信创适配与交付

Each section: what we did → what was delivered → key decisions or trade-offs.

## 五、关键技术亮点

2-3 technical differentiators. Reference the company's product capabilities.

## 六、客户价值

6.1 直接交付物清单
6.2 客户获得的能力
6.3 量化价值（如果可获得）

## 七、经验总结与可复制性

What made this project work? What would we do the same or differently next time?
How can this approach be reused for similar projects?

```

**Tone calibration rules for best practice reports:**
- **默认（用户没特别要求）：** 事实陈述为主，避免夸大。用 "实现了"、"达成了"、"支撑了" 等中性动词
- **更完整的版本：** 增加业务背景的细节、引入客户原话或引用、补充具体数据（如接入系统数量、治理指标数等）
- **避免：** 过多的形容词堆砌（"行业领先"、"业界首创"等）、空洞的承诺式语言、缺少数据支撑的论断

**Common pitfalls:**
- 只写了"做了什么"，没写"为什么这么做"和"不这么做会怎样" — 最佳实践的关键在于方法论，不光是成果
- 缺少量化数据 — 尽量用数字说话
- 把客户项目的商业目标混同为自己的技术目标 — 要区分"客户想要什么"和"我们怎么做到的"


### PBC (绩效承诺书) IDP 补充

See [references/pbc-idp-adaptation.md](references/pbc-idp-adaptation.md) for handling the enterprise PBC Excel template — reading the 3-part structure (绩效目标/核心价值观/IDP), designing IDP content by referencing peers' IDP from screenshots (OCR → adaptation), the iterative refinement pattern (角色定位驱动法: each round tightens fit to user's role), and the validated dual-dimension IDP framework for 软件工厂厂长 (对内管团队 + 对外接客户).

### Offer Comparison / Job Change Analysis Documents (Offer对比分析)

For documents where the user is comparing their current company vs. a new offer and needs decision support:

**Structure:**
1. **基本信息对比表** — 岗位、薪资、公积金、股票、报销、汇报关系、公司阶段
2. **2年经济账** — 计算真实收入差（含公积金差额、股票解锁、报销资金占用）
3. **现公司优劣势分析** — 客观列出好处，以及现金流/合规等致命问题
4. **新公司优劣势分析** — 客观列出风险，以及上市公司/新建分部/核心配股等利好信号
5. **关键诊断问题** — 问用户核心问题："如果2年后现公司还是这样，你会留吗？"
6. **最终建议** — 提供分析框架和判断依据，让用户自己做决定

**Key analytical signals for Offer comparison:**
- **公积金缴纳合规性** → 上市公司通常按时，民企可能拖欠——直接影响房贷和现金流
- **报销周期** → 一年多才一次是现金流紧张的信号，管理岗招待费垫付压力大
- **股票配发条件** → 全员配股 vs 核心岗位才配，含金量完全不同
- **新建分部 vs 成熟团队** → 早期核心成员上升空间大但累，成熟团队稳定但天花板有限
- **业务方向匹配度** → 政府/AI项目 vs 用户TOB交付经验，直接平移转型风险低

See the full analysis framework at: [references/interview-company-analysis.md](references/interview-company-analysis.md) → Offer对比分析

The supplementary standalone template is also available at [references/offer-comparison-analysis.md](references/offer-comparison-analysis.md) for quick structured comparison tables.

### Project Success Case Summary (项目成功/客户成功案例总结)

For documents that profile successful project deliveries as reusable case studies — used for internal knowledge sharing, customer success stories, or bid capability demos.

See the full template, narrative structure, and trust-rebuilding strategies at [references/project-case-summary-writing.md](references/project-case-summary-writing.md).

## Templates

### Email/Shareable Link Delivery

Save the document as a markdown file on Desktop, then deliver via available channels (WeChat, Feishu, Enterprise WeChat).

### Training Reflection Template

For long-form personal reflections (培训感想/心得体会) with iterative refinement: see [references/training-reflection-template.md](references/training-reflection-template.md). Covers the 10+ round iteration pattern, preferred structure, and this user's specific style.

### Markdown → Other Platforms

The markdown version is the source of truth. Convert to Feishu/WeCom document as needed using platform APIs.

### Markdown → Feishu 文档：
1. 参考 `hermes-office-workflow` 技能下的 `references/feishu-doc-content-writing.md`
2. 核心流程：获取 token → 创建空白文档 → 逐行解析 markdown 转为飞书 blocks → 按 50个/批次 批量写入
3. block type 映射：`#`→heading1(3), `##`→heading2(4), `###`→heading3(5), `####`→heading4(6), `````→code(9), `>`→quote(17)
4. ~~不支持列表/表格/分割线的批量写入~~ → **原生表格 (block_type=31) 已支持！** 需两步流程：先创建表格壳（含空单元格），再逐个填充单元格内容。列表/分割线仍需 Text block 模拟。
   - 原生表格 API 限制：一次最多 9 行，行列积不超过 45（如 5x9=45 可行，6x8=48 不可行）
   - 详见 `hermes-office-workflow` 技能 `references/feishu-doc-content-writing.md` → 原生表格创建
5. **重要：不要用 delegate_task 子代理去执行**——token 和 doc_id 无法传回
6. **⚠️ `?index=N` 参数不可靠**：`POST .../children?index=N` 并不会在该位置插入，而是追加到文档末尾。实测确认。如需控制插入位置，可以：
   - 方案A：用 POST 一次传入所有 children（不需 index 参数），保持顺序
   - 方案B：先写入正确顺序在末尾，再手动在飞书 UI 中拖拽（推荐，5秒操作）
   - 方案C：从头重建整个文档，将全部内容按正确 block 顺序一次提交
   - ⚠️ `batch_delete` 端点在当前 API 版本中返回 404，不要依赖删除操作来调整位置
7. 验证：打开飞书文档 URL（格式：`https://bytedance.feishu.cn/docx/{doc_id}`）人工确认

### Feishu 文档 → Markdown 导出

当用户需要将飞书文档内容导出为本地 Markdown 文件时（如「把飞书文档内容给我存到桌面md」），使用此流程：

**完整工作流：**

1. **获取 tenant_access_token** — 同 Markdown→Feishu 流程

2. **读取文档全部 blocks** — 通过飞书 API 递归获取 block 树：
   - 根 block 就是文档本身（doc_id 同时也是 block_id）
   - 用 `GET /docx/v1/documents/{doc_id}/blocks/{block_id}/children?page_size=500` 递归获取所有子 blocks
   - 每个 block 包含 block_type、对应的内容字段（text/heading1/code/table 等）

3. **Block Type → Markdown 映射表**：

| block_type | 含义 | Markdown 输出 |
|:----------:|------|:-------------:|
| 1 | Page（文档根） | 忽略，递归子节点 |
| 2 | Text 段落 | 直接输出文本 |
| 3 | Heading1 | `# 内容` |
| 4 | Heading2 | `## 内容` |
| 5 | Heading3 | `### 内容` |
| 6 | Heading4 | `#### 内容` |
| 9 | Code 代码块 | ````language\n内容\n```` |
| 12 | Bullet 无序列表 | `- 内容` |
| 13 | Ordered 有序列表 | `1. 内容` |
| 17 | Quote 引用块 | `> 内容` |
| 22 | Divider 分割线 | `---` |
| 31 | Table 表格 | 读取 cells 结构转为 markdown 管道表 |

4. **处理嵌套结构**：blocks 的 children 列表保持飞书中的顺序。在递归遍历时，用 depth 跟踪层级，保持正确的父子关系。Bullet 列表可以嵌套——用 depth 缩进控制。

5. **表格（block_type=31）特殊处理**：读取 cells 数组，取每个单元格第一个 children 的 text_run content，按行列拼成 markdown 管道表（第一行为表头，第二行为 `|---|` 分隔行，后续为数据行）。

6. **提取元素内容 key 映射**：每个 block 的内容字段名与 block_type 对应（如 block_type=3→heading1, 4→heading2, 12→bullet, 17→quote）。遍历每个元素的 elements 数组拼接文本。

7. **写入本地文件**：将生成的 markdown 保存到用户桌面，文件名为 `原飞书文档标题.md`

**注意事项：**
- 飞书 API 每页最多 500 个 blocks（`page_size=500`），不需要翻页
- 如果文档很大（200+ blocks），建议分块递归读取，每块之间 `time.sleep(0.1)` 避免限速
- 最终输出文件路径：`/Users/jesseyoung/Desktop/<标题>.md`（或用户指定的路径）
- 此流程**不需要** `drive:drive` 权限，仅需 `docx:document:readonly` 权限
- 代码块（block_type=9）可能包含 `language` 字段，用于指定代码语言

**与反向流程对比：**

| 方向 | API 调用 | 关键差异 |
|------|---------|---------|
| Markdown → Feishu（写入） | `POST .../children` 批量创建 blocks | 需处理 block_type 限制、分批写入、表格限制 |
| Feishu → Markdown（导出） | `GET .../children` 递归读取 blocks | 需处理递归遍历、元素内容拼接、表格转管道表 |

### Markdown → Word (.docx)

When the user asks for a Word document after finalizing the markdown:

1. Install `python-docx` if not present: `python3 -m pip install python-docx`
2. Write a standalone `.py` script that builds the docx from scratch using python-docx. Do NOT read the markdown and parse it — write the content directly in the Python script for full control over formatting.
3. Key formatting for Chinese enterprise documents:
   - Font: 微软雅黑 throughout (set via `run.font.name` + `run._element.rPr.rFonts.set(qn('w:eastAsia'), name)`)
   - **Alternative for formal/作业 documents (validated)**: 宋体 body + 黑体 headings is the standard official-Chinese-document pairing. Helper pattern:
     ```python
     def set_cn_font(run, name='宋体', size=12, bold=False):
         run.font.name = 'Times New Roman'  # ASCII glyphs
         run.font.size = Pt(size); run.font.bold = bold
         run._element.rPr.rFonts.set(qn('w:eastAsia'), name)
     # title: 黑体16 bold centered; h1: 黑体14 bold; h2: 宋体12 bold; body: 宋体12, first_line_indent Pt(24), 1.5 line spacing
     ```
     Also set the Normal style default (font.name + `style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')`) so plain runs inherit it.
   - Page margins: top/bottom 2.54cm, left/right 3.17cm
   - Title: 22pt bold centered
   - h1: 16pt bold
   - h2: 14pt bold
   - Body: 12pt, 1.5 line spacing, first-line indent 0.74cm
   - Tables: 'Light Grid Accent 1' style, rightmost column bold for emphasis
4. Save to Desktop: `/Users/jesseyoung/Desktop/<filename>.docx`

## User Preferences

- This user prefers no emotional reassurance or sentimentality in documents. Stick to factual, evidence-based content.
- The user values "说到做到，不做不承诺" — don't include promises that can't be kept.
- Documents should be immediately actionable, not motivational.
- **Number formatting: NEVER use thousands separators (千分位分隔符)**. Write `3185` not `3,185`, `7200万` not `7,200万`. This applies to all numbers in all documents — tables, text, calculations, and narrative descriptions. The user explicitly corrected this. This is a hard rule, not a style suggestion.
- **Ratio display format**: When showing role ratios (AE:DE:IE:数据开发), use this two-line format:
  ```
  原始比值（以AE=1为基准）：1 : 2.03 : 0.85 : 0.21
  简化整比（比例对齐）：         5 : 10  : 4   : 1
  ```
  First give the raw ratio (AE=1 as baseline), then the simplified integer ratio. Format: `AE:DE:IE:数据开发 = 1:2.03:0.85:0.21`. Always include both lines — the user uses both for different purposes.
- **File output directory**: All generated files go to `/Users/jesseyoung/Documents/work/smardaten/smardatenCorp/99-软件工厂/98 hermes/`, NOT `~/.hermes/`. Do not save documents under the `.hermes` directory.
