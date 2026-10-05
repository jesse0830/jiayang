# Best Practice Case Report — Reference Template

## Workflow Summary

1. **Accumulate materials** — user provides them incrementally. Maintain a running inventory:
   - Technical specs/requirements documents (PDF/DOCX)
   - Project plans (XLSX)
   - Implementation plans (DOCX)
   - Quotes / budget breakdowns (XLSX)
   - Any additional material the user mentions in conversation

2. **Offer a framework first** — before writing the full report, share a proposed outline. Let the user confirm the structure before filling in content.

3. **Build section by section** — the user says "一点一点完善". Write one section at a time, wait for feedback, then proceed. Do NOT write the full report in one shot unless explicitly asked.

4. **Integrate new materials as they arrive** — when the user says "先把整体材料给你", maintain a context inventory. Each new piece of material enriches existing sections.

5. **Extract structured content from binary files** — DOCX files can be read via `zipfile + xml.etree.ElementTree` in Python to extract paragraph text. This is more reliable than trying to use `read_file` on binary files. The extracted text can be scanned for key sections (headings, tables, scope descriptions, architecture diagrams).

6. **Final polish** — after all sections are drafted and confirmed, do a consistency pass: check for duplicate content, tone consistency, and quantifiable claims.

## Material Inventory Template

| # | Material Name | Type | Key Content | Status |
|---|--------------|------|-------------|--------|
| 1 | Technical Spec V10.3 | PDF | Project background, requirements, data platform section | ✅ Loaded |
| 2 | Project Plan 6-30 | XLSX | 7 objectives, 46 tasks, timeline, responsibilities | ✅ Loaded |
| 3 | Implementation Plan 2.0 | DOCX | Architecture, data governance, MDM, visualization design | ✅ Loaded |
| 4 | ... | ... | ... | ... |

## Project Context Block (populate as materials arrive)

```
客户名称: [Customer]
项目名称: [Project Name]
整体金额: [Total Amount]
我方金额: [Our Scope Amount]
我方负责: [Our Scope Description]
政策驱动: [Policy Driver, if any]
交付周期: [Delivery Timeline]
覆盖范围: [Scope — e.g., "覆盖集团及200家子公司"]
现有员工: [Headcount]
```

## Standard Chapter Template (8章结构)

Use this as the default structure for most data platform / digital transformation best practice reports. The structure is designed to tell a compelling story: problem → method → results → replicability.

```markdown
# [Project Name] — [Project Type] 最佳实践案例

## 一、项目概述

### 1.1 客户简介
Industry, scale, organizational complexity (number of subsidiaries, headcount, revenue band).

### 1.2 项目背景
What triggered the project? Policy mandate, business pain, growth pressure?
Reference specific policy documents or industry trends when available.

### 1.3 项目概况
Project amount, duration, scope coverage. Use a timeline table for milestones.

## 二、传统方案的痛点

If the project involves replacing or upgrading a traditional approach, dedicate a section to explaining what the standard industry approach looks like and why it falls short. Use the "ODS → DWD → DWS → ADS" or equivalent layered-architecture pattern for data projects.

For each layer, describe:
- What it traditionally involves
- The pain point (high manual effort, linear scaling, high maintenance)
- Why it's unsustainable at project scale

This section sets up the tension that the next section resolves.

## 三、核心方案对比

**This is the most important chapter.** Present a side-by-side comparison of the traditional approach vs. the implemented solution.

Structure by workflow step (e.g., data collection → modeling → cleaning → output):

| 维度 | 传统模式 | 本项目方案 |
|------|---------|-----------|
| Step 1 - ... | Description | Description |
| Step 2 - ... | ... | ... |

For each step, highlight:
- What's the same (to establish credibility: "we didn't skip anything")
- What's different (the core innovation)
- Why it matters (the efficiency gain)

Include a **summary efficiency table** at the end showing estimated improvement percentages per step and overall.

## 四、项目亮点与核心价值

2-3 stand-out achievements. For data platform projects, typical highlights:
- Ultra-fast delivery (e.g., "28天完成中台核心交付")
- Product-driven efficiency (e.g., "从定制开发转型为配置化交付")
- End-to-end coverage (e.g., "从采集到决策看板全链路")
- Standardized, repeatable approach

## 五、实施内容详解

Organize by major work streams:
1. **调研与方案** — departments covered, key pain points per department
2. **治理体系** — organization, standards, processes
3. **数据接入与底座** — systems integrated
4. **专题库/数仓** — topic areas built
5. **可视化大屏** — 3-tier architecture (business → management → executive)
6. **主数据管理** — phased rollout plan
7. **监管对接** — if applicable

Each section: what we did → key decisions → delivered outcome.

## 六、关键技术亮点

2-3 technical differentiators tied to the company's product capabilities (e.g., AI-assisted modeling, semantic recognition engine, algorithm library, auto-generated data processing pipelines).

## 七、客户价值

1. **直接交付物清单** — what the client received
2. **客户获得的能力** — what changed for them
3. **量化价值** — efficiency gains, cost savings, regulatory compliance improvements

## 八、经验总结与可复制性

1. **成功关键因素** — a 2×2 or 4-item table
2. **可复制经验** — which deliverables, methodologies, and standards can be reused
3. **适用客户画像** — what kind of client is a good fit for this approach
```

## Report-Specific Patterns

### For "产品对比" reports (company's product vs. traditional approach)

When the report's primary purpose is to demonstrate product superiority over a standard industry approach:

- **Chapter 2 (痛点和传统方案)** and **Chapter 3 (核心对比)** are the main chapters — they should be the longest and most detailed
- Use **comparison tables** extensively — they make the difference visible at a glance
- For each step in the workflow, explain not just *what* the product does differently, but *why* the traditional approach has that problem in the first place
- The efficiency percentage estimates should have a clear logical basis (not made-up numbers)
- Use concrete terminology from the product: algorithm library, semantic recognition, expert knowledge base, auto-generate data switch station, mapping recommendation — these make the report feel authentic and product-specific

### For "传统 vs 数据通" type reports (product-based transformation):

- The 数据采集 step often has minimal difference — be honest about this; don't exaggerate
- The biggest delta by percentage will be in 数据清洗 (算法库复用) and 交换机生成 (自动化程度最高)
- The 数据建模 step is where the **product differentiator** lies (AI-assisted + semantic rules) — spend the most writing quality here
- Include a brief explanation of key product concepts (什么是算法库, 什么是交换机, 什么是专家库, 语义识别规则的作用是什么)

## Output Format

- Default: Markdown (.md), saved to user's Desktop
- Only convert to Word (.docx) on explicit request
- If the user is on a messaging platform (WeChat/Telegram/etc.), deliver the md file path, not the full content, unless they ask to see it inline