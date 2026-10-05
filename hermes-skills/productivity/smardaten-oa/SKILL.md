---
name: smardaten-oa
description: "Use when 用户在 SmarDaten OA 查报销/待报销金额、做报销全量导出分析或跟审批流程。含登录、翻页、口径、落盘。"
---

# SmarDaten OA 系统操作（杨嘉阳工作账号）

数睿 OA：oa.smardaten.com。本技能沉淀 OA 常用操作的完整可执行流程（报销待付查询最常见）。**凭证不写进技能文件**：登录账号/密码从记忆条目读（"OA 登录账号" / "用户 OA 登录密码"），别让用户重复给。

## 何时用
- "帮我看下还有多少待报销金额 / 记得翻页" → 报销待付查询（主流程）
- "把所有报销数据拉出来做个分析" → **报销全量导出与分析**（四条来源合并，见下）
- 查看"我发起的"流程状态（license 申请等）
- 招待报销 / 出差报销 / 个人报销 单据跟进

## 访问方式（浏览器驱动，不是简单 HTTP）
- OA 是 JS 渲染应用壳：web_extract / read 拿不到内容；登录后 innerText / AX 树为空是常态，不代表失败。必须用真实浏览器驱动（browser_exec 等）。
- 首次需 macOS 调试授权：`browser-harness mac-approve`（该 CLI 不在 PATH，在 uv 缓存 `~/.cache/uv/archive-v0/*/bin/browser-harness`，`ls -t` 取最新）。
- 登录：goto 登录页 → `#username` / `#password` 是 React 受控输入，fill_input 提交后可能仍空 → 用**原生 value setter + 派发 input 事件**再点登录按钮（buttons 里 className 含 login 兜底匹配）。
- **整页跳转会丢会话**：每次 goto_url 后查 location.href 是否含 "login"，是则重登（有凭据，快）。
- 应用壳空白/门户菜单不渲染：别逐级点菜单，直接 goto 应用直达 URL（appid + menuId，见 references/oa-expense-query.md）。

## 报销待付查询（主流程）——两条线都要查
1. **招待报销**：独立模块（差旅报销→招待报销→招待报销申请），4 页左右。
2. **出差报销 + 个人报销**：员工报销→我发起的 总列表（事件名带类型词），2026-09 规模约 230 条 / 23 页。

**翻页铁律（用户原话"记得翻页"）**：逐页点下一页并校验 `.ant-pagination-item-active` 页码，**绝不只取第一页**。ant 筛选下拉（流程状态）点击后 popup 常不渲染、不可靠 → 放弃筛选，全量翻页抓取后本地 Python 过滤。

抓取节奏：抽 `.ant-table-tbody` 行文本 → 每页 sleep 1.5s + 校验 active 页码 → 落盘 JSON（workspace 目录）→ execute_code 本地按流程状态过滤统计。

## 统计口径（用户认可，沿用 08-24 起各期文件）
- 流程状态 = **处理中 → 待报销**（计入）
- **结束 / 异常结束 / 已撤销** → 已付款或终止（不计）
- 出差申请 ≠ 报销单（"出差申请"是申请单，勿混入）
- 金额冲突以**正式模块**为准：实例 20260723516 招待模块 1252.00 vs "我发起的"列表 1252.20 → 取 1252.00（差 0.20 是列表别名/误读）
- 抓行先打印一行全列核对列索引（如 tds[12] 才是费用合计），再批量抓，勿盲信固定位置

## 交付规则（用户强制，三步缺一不可）
1. 结果落盘 md：`~/Documents/work/smardaten/smardatenCorp/99-软件工厂/98 hermes/OA待报销金额汇总_YYYY-MM-DD.md`
2. 更新记忆摘要条目（最新合计/笔数/分类小计），供下轮做对比基准
3. 回复给总额 + 分类表 + 与上次对比 + 大额/异常单提醒（如跨年老单）

## 对比基准
读取上次结果 = 读 98 hermes/ 下最新的 `OA待报销金额汇总_*.md`（不要只信记忆），对照口径与数字。财务常在某日批量结束老单 → 对比时点明"已付清 N 笔"。

## 报销全量导出与分析（第二条产线，2026-09-17 建立）
待付查询只看"处理中"的十几笔；**全量导出要四个来源合并**：出差报销 84 + 个人报销 6 + 招待报销(旧) 19 + 招待报销申请(新) 40 = 149 笔（2024-03 ~ 2026-09）。

**铁律：招待旧模块与招待新模块是前后接续的**（旧 2024-06~2025-07，新 2025-08 起，不重叠）。用户说"包括招待报销（旧）"就是为此 —— 只看新模块会丢 19 笔 18865.00 元。

**头号陷阱：antd Tabs 未激活面板仍在 DOM。** 「员工报销」是 antd Tabs 三页签（出差报销 / 个人报销 / 招待报销(旧)），未激活 tab 的表格不销毁。全局 `querySelectorAll('tr.ant-table-row')` 会把三张表 + 累积翻页一起抓，实测行数从真实的 109 虚高到 **228**、表头重复 3 次。必须限定面板抓取与面板内翻页：
```js
const pane = document.querySelectorAll('.ant-tabs-tabpane')[tabIdx];  // 0=出差 1=个人 2=招待旧
const rows = [...pane.querySelectorAll('tr.ant-table-row')].map(r => [...r.querySelectorAll('td')].map(td => td.innerText));
pane.querySelector('.ant-pagination-next').click();                  // 翻页也要在 pane 内
```
抓后三项校验：唯一编码数 vs 行数（招待新 41 行只有 40 唯一编码，需去重）、行数 vs 分页总数、**与「我发起的」232 条交叉核对**（"我发起的"里 16 条标为"费用报销"的老单其实全落在招待旧 tab，属旧流程名称，勿重复计数）。

交付三件套：Excel 多 sheet（全量明细/类型/项目主体/状态/月度/年度/未结清）+ HTML 看板（聊天里 `::preview` 内联）+ 报告 md，均落在 `98 hermes/`。

完整列索引、分析维度、报告写作口径见 references/oa-expense-full-export.md。

## 汇总推送到企业微信 / 微信（2026-09-30 实测可用）
- 官方 CLI：`cd ~/.hermes/hermes-agent && venv/bin/python -m hermes_cli.main send --to wecom:<chat_id> --file <汇总.txt> --json`
- 查可用目标：`... send --list`。本机实测：`wecom:wo9tQCDgAApkbYg5HjV94etVjyd75yEg`=企业微信 DM，`feishu:oc_3d65...`=飞书，`weixin:o9cq80...@im.wechat`=微信
- 成功返回 `{"success": true, "message_id": "aibot_send_msg-..."}`；纯文本发送不需要运行中的网关（适配器 `_standalone_send` 临时建连）
- 企业微信 bot 只允许一条 WS 连接，CLI 临时连接理论上会踢网关；**实测无影响**（发完 `grep -h "Wecom" ~/.hermes/logs/gateway.log | tail -3` 看 ping 仍连续）。仍建议发完顺手确认一次
- 正文用纯文本（企业微信不渲染 markdown 表格），务必带上数据日期

## 参考
- references/oa-expense-query.md — 直达 URL、模块列布局、历史快照、浏览器工作区
- references/oa-expense-full-export.md — 全量导出：四来源合并、antd Tabs 面板限定抓取、分析维度、交付三件套
