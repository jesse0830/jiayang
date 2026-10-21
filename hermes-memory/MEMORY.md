weixin限流ret=-2=服务端限流；gateway重启必须用venv/bin/python。
§
用户 OA 登录密码：1qw2!QW@
§
英语计划~/.hermes/english-plan.md（三阶段）。
§
OA自发起流程：首页工作台→流程→我发起的，勿去事件流工作台。
§
OA报销：流程见 skill smardaten-oa。查完写结果文件（98 hermes/OA待报销金额汇总_*.md 带版本号）+更新 skill 快照。最新 2026-10-14 = 49729.64/27 笔；出纳积压 39796.84/21 笔；出差 501.91 滞留 346 天。登录走门户根 https://oa.smardaten.com/ 用户名+密码（勿用短信码）。
§
PPT：默认给markdown素材不生成.pptx，除非明说'生成pptx文件'。
§
Holographic记忆同步：真源=jiayang仓hermes-memory/（Mac端~/.hermes/memories软链，Windows用junction）；改动后手动commit+push。memory_store.db被gitignore，用 scripts/export_holographic_facts.py 导出脱敏版（周一9:00 cron，job b5788e09ce1d）；细节见 skill hermes-memory-management。
§
H2目标7200万(月均1200万)，工厂需支撑5200万。HC规划（超总已批，2027-03前补完）：缺口101=PM14/AE53/DE(含数据开发)21/IE13。DE/IE重仓无锡、PM按地域、储备南京+无锡。PM人效10.2万→提效3倍30.6万/月；配比1:1.81:0.92:0.22。
§
飞书原生表格(block_type=31)可用：先建壳再填充，≤9行/行列积≤45，详见chinese-enterprise-document-writing skill。
§
南通驻场固定团队22人（PO类固定人头，明细见花名册文件）；运维：万守刚=负责人，申梦娇（2026-01试用），陈钰8.17入职（3年云平台）。
§
软件工厂人效模型（2025）：产能利用率AE68.4%/DE67.9%/IE69.2%/数据70.4%；DE:AE=2.03:1（DE是瓶颈），IE:DE=0.42:1；前10项目占50%产能（海外招投标+苍南占21%）；Q1爬坡→Q2稳→Q3高峰→Q4冲刺→12月骤降；理想产能DE51人×260天×68%=9000人天；H2产出+27%，利用率AE+23%/IE+20%/DE+10%。
§
合契枢=任务管理工具（周排产2026W32=8227条；模块：任务/缺陷/跟踪/分配/变更/产出/导出；字段：需求名/责任人/类型/复杂度4级/计划起止），鉴策行=PM周五提订单；排产按AE/DE/IE/数据开发，AE已划项目产品部。痛点：工时填报无审批、超8h填满致财经无法核算；方案=工时审批给PM。DE考核：bug日清前五打C，拟优化多维度。
§
98 hermes 全路径=~/Documents/work/smardaten/smardatenCorp/99-软件工厂/98 hermes（勿放Downloads）；内含 01绩效与人事/02方案与汇报/03财务与报销/04技术与工具/05招聘与面试/_归档，新文件按主题放对应目录。
§
千问已配：key在auth.json(label=qwen-dashscope，access_token=sk-ws-前缀)，base_url=dashscope.aliyuncs.com（国内站）。别名qwen/turbo/long/qwen37仅CLI /model命令生效。坑：auth add固化国际站base_url致401，须改auth.json；qwen-long在CLI消息格式不兼容（curl直连可用）；桌面app模型=会话级记忆，下拉框只有内置目录。
§
WPS开放平台 appid=AK20260807SZZMPB appkey=58b9359e5afec5ba6c6cdb7c87e51ce0（应用JesseHermes）。坑：应用=企业自建应用，个人账号授权报NotCompanyUser；开发者后台仅限企业用户→个人需先创建团队/企业。scope用user_info,cloud_file,dbsheet.all；回调地址在安全设置配（非事件与回调）。
§
terminal guard坑：命令含绝对路径/引脚本崩(null byte)；规避=脚本写/tmp+PYTHONPATH= python3跑。飞书读表：wiki链接浏览器get_node拿obj_token→个人应用sheets API可读。汇报习惯：iPad开Word讲稿+电脑开PPT翻页。
§
Obsidian vault=~/Documents/work/jiayang/obsidian-vault（独立仓库 origin=jesse0830/obsidian；obsidian-git 每5分钟自动 commit+push+pullBeforePush；git 全局身份 JesseYoung）。
§
软件工厂绩效（调薪规则=连续2个季度窗口内≥3A且无C；2026窗口=4-9月）：v1.2报告 98 hermes/软件工厂绩效分析_2026年4-9月窗口_20261001_v1.2.md/.xlsx（7页签，生成器perf_v3_report.py；源wiki=I96KwwV4niowM6k5zecc9RLNnhd）。已达标5=周婷婷/孔雨晴/刘培松/顾睿/孔令辉；临界需9月A共8=降温(季智/王佩琪/王晴)+最热(胡学生/杨军/汪靖/孙堂颖/戴忆婷)；出局18含王俊(2A1C)。坑：6月表12格#REF!（重存丢sheet）已双源恢复。解析见skill smardaten-perf-analysis
§
集控PM：决策责任=需求深度/政府验收时间与业主对清/商务接口；主导权错位（报价假设集控主导未交接）；对吴恒要求=尽快明确验收时间+书面确认验收流程与标准+主导项目。
§
工作文档传git（提效方案等）：cp到 ~/Documents/work/jiayang/Jesse/PM-documents/ 再 commit+push（jiayang仓库，远程 git@github.com:jesse0830/jiayang.git）。对外汇报方案不放内部运营数据（产能利用率/H2目标/HC缺口/人效配比），详见 chinese-enterprise-document-writing skill。
§
提效方案（2026.9 王佩琪版）：四大部分=背景/现状与问题/提升方案/落地计划，子主题名沿用原文；不含软件工厂运营数据；数字不新编（无数据写“试点期校准”）；8处丢失表格先空着、IE暂不含。成品+重建脚本在 98 hermes 与 jiayang 仓库 Jesse/PM-documents；帛飞特锚点与八达光电协作模式见该文档。
§
OA报销全量导出（含招待旧）：149笔/155492.34元/2024-03~2026-09；四来源=出差84+个人6+招待旧19+招待新40；坑=antd未激活Tab仍在DOM致虚高，须限.tabpane内抓取。详见 skill smardaten-oa/references/oa-expense-full-export.md。
§
网络通道：Mac跑Clash系统代理127.0.0.1:7897，github.com只有走代理才通（裸curl/git直连超时属预期非被墙）；探通道先scutil --proxy，复测curl -x 127.0.0.1:7897。详见 skill github-china-access。
§
iPhone端Obsidian同步=obsidian-git插件（非GitSync App）；iOS不支持SSH→只能HTTPS+PAT，克隆前先填用户名+Token；同步入口=屏幕顶部下拉。步骤见 skill obsidian-git-sync。
§
Windows Obsidian+git：Obsidian=C:\software\obsidian\Obsidian.exe；vault=克隆 ...\jiayang\obsidian-vault（origin jesse0830/obsidian，master）；repo级 core.autocrlf=false、身份 JesseYoung；git=Hermes自带 ~/AppData/Local/hermes/git（SSH key 就绪）。
§
文档版本约定（用户 2026-09-29 定）：每生成/修改一份文档都要标版本号，v1.0 起递加 v1.1/v1.2，标在文件名末尾与文档头，修订不改名换号。
§
三生态接线（2026-10-05）：内容=obsidian仓（vault兼LLM Wiki.app工作区，app须开着）；hermes经MCP stdio调其12工具（config: mcp_servers.llm-wiki）；jiayang仓=交付+hermes生态（memories/skills均软链）。详 wiki/concepts/wiki-obsidian-hermes-生态.md v1.3。
§
MBA备考：练习类进 MBA/练习/，一份卷子=一个文件（题面+末页解析，永不拆试卷版/解析版；合卷01=A卷30题+B卷24题）；入口 练习总览_v1.3、hub MBA备考总入口_v2.1；数学日更30题 + 英语日更30题（真题优先、避开近五年）规则见 skill study-material-production
§
读写笔记=讯飞Doxent：纪要自动入 vault/读写笔记（Hermes定时30m，App未运行跳过；导出器v1.5+门卫doxent_sync.py，见skill closed-app-data-extraction）。