---
name: smardaten-agent-skill-authoring
description: 数睿SmarDaten平台agent skill模板增改，原有场景零改动+diff验证。
version: 1.0.0
---

# 数睿 SmarDaten 平台 Agent Skill 模板增改

用户（杨嘉阳，软件工厂厂长）维护数睿平台自己的 agent skill 模板（如"文稿智能审核" skill.jiangning.scenario8_document_audit）。常见需求：**在既有场景基础上新增一个场景**（如 场景E 粮食执法、场景F 专项检查通知拆解）。用户对"原有场景被改"极度敏感——历史教训：新文件内部复用 A-D 场景编号导致用户误判"4 个场景被改"。

## When to Use

- 用户上传 skill 文件（如 `skill-文稿bak.md`）说"在原有基础上增加场景X"
- 用户提到"数睿agent模板"、"场景E/F"、"新增场景"、"通知拆解"、"岗前提示"
- 需要产出 `数睿agent模板-场景X….md` 模板文件

## 铁律（用户明确要求，违反=返工）

1. **原有场景逐字保留，零改动**——新文件必须内嵌原件全文，仅追加新场景
2. 新场景追加在最后一个场景之后；若原件末尾有附录（如"审核标准速查"），插在附录**之前**
3. frontmatter 的 `description` 和路由行（"五种场景"→"六种场景"）**必须同步更新**才能让平台路由到新场景——但这是唯一允许的元信息改动，改完要明确告知用户
4. 工具名/mode 如未确认平台实际参数 → 用占位符并标注"待平台确认"

## 工作流

1. **read_file 读原件**（如 `~/Downloads/skill-文稿bak.md`）——先确认现有场景数（可能是 A-D 或 A-E，别假设），附件展示可能截断，务必读全文
2. **构造新文件**：用 write_file 直接写完整内容 = 原件逐字（含 frontmatter，description 追加新场景描述+触发词）+ 新场景段
   - 命名：`数睿agent模板-场景X<主题>.md`
   - 保存目录：`~/Documents/work/smardaten/smardatenCorp/99-软件工厂/98 hermes/`
3. **diff 验证**（关键步骤，必须做）：
   ```bash
   diff <(grep -v "^description:" 原件) <(grep -v "^description:" 新文件)
   ```
   排除 frontmatter description 行后，diff 输出应**只有**：路由行计数变化 + 新增场景段落。出现其他差异=原有内容被改动，返工
4. **read_file 回读新文件**确认完整落盘（行数/字节），重点看新场景段和附录衔接处
5. 汇报：表格列出 原件行数/新文件行数/diff 结果 + 明确列出"改了什么"（新场景+2处元信息）+"没改什么"（原有场景逐字保留）

## 新场景结构模板（对齐平台既有风格）

```
## 场景X：<主题>

用户说"<触发示例1>"/"<触发示例2>"

1. **<识别/提取>**：从 FILE[idx] 提取输入文件；调用 `jiangning_document_audit(file_path="{URL}")` → mode=<占位，待确认>
2. **<核心处理>**：分步骤描述，含结合江宁区实际的对照逻辑
3. **<输出>**：输出卡片结构（📋/⭐/⚠️ 等 emoji 分块），列清每个部分内容
4. **硬性约束**：严禁编造/仅用已知事实/区分原文与本地建议/固定输出顺序
```

参考示例见 `references/scene-f-example.md`（场景F 专项检查通知拆解与岗前提示，已落地）。

## Pitfalls

- **write_file 回显行数不可信**（多次出现"4 lines"截断假象）——写后必须 read_file 回读 + diff 验证
- **terminal guard 会拦截 heredoc python 和含绝对路径的命令**——增改文件用 write_file 直接构造完整内容，不要用 python 脚本拼接；execute_code 同样可能被拦
- **用户说"需求是1."= 后面可能还有需求 2、3**——完成当前场景后主动追问剩余需求，一次性合并
- **附件展示 ≠ 完整文件**——附件可能截断（3331 tokens 只是预览），必须 read_file 读磁盘原件
- **不要自作主张删除旧文件**——旧模板（如"场景9-模板E"作废稿）留着当素材，是否删除问用户

## 相关位置

- 基底原件：`~/Downloads/skill-文稿bak.md`（用户上传的平台实际在用 skill）
- 已产出：`~/Documents/work/smardaten/smardatenCorp/99-软件工厂/98 hermes/数睿agent模板-场景F专项检查通知拆解与岗前提示.md`（A-E 原文 + 场景F）
- 同目录还存有：场景8原文件、场景E 文件、场景9/模板E 作废稿
