# 领导口述反馈 → PPT优化更新流程

在国产企业环境中，典型的PPT修改流程：领导听完汇报后口述反馈（录音），转文字后需要分析并更新PPT。

## 典型场景

> 用户（部门经理）向一级部门负责人汇报PPT → 领导提出优化建议（录音）→ 用户把录音转成文字发给你 → 需要分析建议并更新PPT

## 工作流程

### Step 1: 提取原PPT和录音文字的内容

```bash
# 提取PPT内容
python3 -c "
from pptx import Presentation
prs = Presentation('文件.pptx')
for i, slide in enumerate(prs.slides):
    print(f'===== Slide {i+1} =====')
    for shape in slide.shapes:
        if hasattr(shape, 'text') and shape.text.strip():
            print(f'  {shape.text[:500]}')
        if shape.has_table:
            table = shape.table
            for r, row in enumerate(table.rows):
                cells = [cell.text for cell in row.cells]
                print(f'  Table Row{r}: {\" | \".join(cells)}')
"

# 提取录音文字（docx）
python3 -c "
import docx
doc = docx.Document('发言人1.docx')
for p in doc.paragraphs:
    print(p.text)
"
```

### Step 2: 分析领导的优化方向

常见分析维度：
- **MECE原则**：领导是否指出职责/模块之间有交叉重叠
- **目标清晰度**：是否缺少"做这些事最终要达到什么目标"
- **职责vs活动混淆**：是否把岗位职责和当前正在做的事混为一谈了
- **术语是否准确**：如"复合型人才"是否太宽泛，需要更具体

### Step 3: 重构内容框架

常见模式：领导会给出一个从上往下的逻辑链。

例如方总给出的框架：
```
目标：完成XX收入目标（按时生产交付）
    ↓
Step 1：拆解计划 → 人效模型 → 动态前瞻 → 看板+复盘
    ↓
Step 2：统一工具平台 → 找效率瓶颈 → 组织优化 → 持续提效
    ↓
Step 3：沉淀全局知识 → 融入自动化 → 提效+客户价值（新增维度）
    ↓
Step 4：培养能沉淀/吸收/用好知识的人才 → 干部后备
```

### Step 4: 更新PPT

1. 先备份原版：`cp 原文件.pptx 原文件_原版.pptx`
2. 用python-pptx XML deep-copy方式复制原slide做备份（详见 `python-pptx-scratch.md` 的"Modifying Existing PPTs with Slide Backup"章节）
3. 修改原slide的表格内容、标题等
4. 在PPT的注/说明区域标注"优化版基于XX领导评审建议调整，原版保留在后续页面"

## 注意事项

- 领导的口述逻辑往往比PPT更体系化，需要"翻译"成PPT的结构化语言
- 录音中可能有跳跃、重复，需要提炼主线，去芜存菁
- 保持原PPT的格式风格（表格结构、字号、颜色）不变，只改内容
- 如果领导提到了AI辅助方法（如"把原始截图+逻辑输入AI，让AI整理"），应在最终总结中告知用户这个捷径
