---
name: presentation-talking-script
description: "生成中文汇报话术：提取pptx全文+飞书妙记，产出结构化话术并转docx。"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [PPT, 汇报, 话术, 售前, 客户汇报, docx]
    category: productivity
    related_skills: [powerpoint, docx, feishu-app-config, xmind-parsing]
---

# PPT → 汇报话术生成

用户要给客户/领导汇报技术方案时，从 PPT（.pptx）+ 历史汇报录音（飞书妙记）生成一份可照讲的**中文汇报话术**。

## 触发条件

- 用户说"帮我生成汇报话术 / 搞一套话术 / 明天汇报用"
- 用户提供方案 PPT +（可选）领导之前的汇报录音（飞书妙记 minutes 链接）
- 用户明天/近期要给客户高层汇报

## 核心工作流

### 1. 提取 PPT 全文（python-pptx）

大 PPT（30-50页）文本必须在**脚本文件**里提取（内联 `python3 -c` 含中文路径会触发 lifecycle guard 崩溃 "embedded null byte"）：

```python
# /tmp/ppt_read.py — 用脚本文件，不要内联
from pptx import Presentation
def extract_shape(shape, depth=0):
    out = []
    if shape.shape_type == 6:  # group 必须递归
        for sub in shape.shapes: out.extend(extract_shape(sub, depth+1))
    if shape.has_text_frame and shape.text_frame.text.strip():
        out.append(shape.text_frame.text.strip())
    if getattr(shape, "has_table", False) and shape.has_table:
        for row in shape.table.rows:
            out.append(" | ".join(c.text.strip().replace("\n"," ") for c in row.cells))
    return out
for i, slide in enumerate(prs.slides, 1):
    texts = []
    for shape in slide.shapes: texts.extend(extract_shape(shape))
    print(f"===== Slide {i} =====")
    for t in texts: print(t[:400])
```

运行：`PYTHONPATH= python3 /tmp/ppt_read.py`（清 PYTHONPATH 避免 venv 包污染系统 python3）。

### 2. 读飞书妙记录音（可选，强烈建议）

用户给 minutes 链接（`https://xxx.feishu.cn/minutes/{token}`）时，用**浏览器**打开（browser_navigate），页面渲染出"智能纪要"+"章节纪要"：

- 智能纪要：全文要点列表（带缩进层级，可直接用）
- 章节纪要：每段录音的标题 + AI 摘要（`00:00 章节名 + 摘要`），**这是话术骨架的金矿**
- 拿完整文本：`browser_console` 执行 `document.body.innerText.substring(N, M)` 分段取

### 3. 话术结构（标准模板）

```
# {客户}汇报话术（{版本}）
开场（1-2min，对应PPT 1-2页）— 讲三件事：为什么建/建成什么样/怎么落地
第一部分 建设背景（对应PPT 3-6页）— 痛点+目标
第二部分 建设方案（对应PPT 7-19页）— 核心架构
第三部分 核心能力（对应PPT 20-31页）— ★重点，AI能力
第四部分 商业化/落地（对应PPT 32-43页）
第五部分 价值与展望（对应PPT 44-51页）
收尾（1-2min）— 总结+下一步建议
附：精简版话术（时间紧用，每段1句）
附：汇报注意事项（口吻/客户关心点/互动技巧）
```

关键规则：
- **每段标题标注对应 PPT 页号**（"对应PPT 2-4页"）——用户电脑开 PPT 翻页用
- **完整版 + 精简版双份**——用户可能时间不够
- **售前给的话术直接嵌入**：用户转述售前原话时，润色口语化后原样保留核心论点（如"一人办"、"人的价值不降反升"），标注【售前话术 · 直接照讲】
- **客户定制**：录音是 A 客户（如城投），明天汇报 B 客户（如核电）时，框架通用但内容要替换成 B 客户场景
- 话术要口语化、可直接照念，不要书面语

### 4. 转 Word（用户 iPad 阅读）

用户偏好：**Word 给 iPad 打开照讲，电脑开 PPT 翻页**。用 python-docx 生成（中文文档比 npm docx-js 更合适）：

- 页面：A4，边距 2.2cm
- 字体：微软雅黑 11pt，标题分级配色（H1深蓝 #1F3B73 → H2蓝 #2E5A9E → H3黑）
- 加粗关键词，分隔线分节
- 脚本模板：`templates/md2docx_cn.py`（把 md 转成带格式 docx）

验证：生成后用 `read_file` 读 docx（工具自动提取文本），抽查开头/结尾段落确保内容完整。

### 5. 交付文件

默认存到用户工作目录（用户指定：`~/Documents/work/smardaten/smardatenCorp/99-软件工厂/98 hermes/`），输出 .md + .docx 两份，文件名带日期（`苍南核电汇报话术_20260812_v2.docx`）。

## 版本迭代

用户会多次给新版 PPT（"售前发了最新版"、"我调整了顺序"）：
- 新版必须**重新读取**，不能假设内容和上版一样（页数、章节都可能变：如 42页→51页，知识中心从18页提前到11页）
- 对比新旧版页序差异，在话术里更新页号对应
- 文件名加版本后缀（_v2），旧版保留作参考

## Pitfalls

- **内联 python 崩 guard**：含中文绝对路径的 `python3 -c` 会触发 lifecycle guard "embedded null byte"崩溃 → 用脚本文件 + `PYTHONPATH= python3 script.py`
- **python 环境**：`python3` 可能是系统 3.9 但被 PYTHONPATH 污染加载 venv 包 → urllib3 崩（`unsupported operand type(s) for |`）→ 加 `PYTHONPATH=` 前缀
- **PPT 文本在 group shape 里**：不递归提取会漏大量内容（shape_type == 6）
- **飞书妙记浏览器读取**：canvas 渲染拿不到文本，但章节纪要在 DOM 里（body.innerText 可读）；页面可能分页加载，用 console 分段取
- **md→docx 中文**：`python-docx` 设置中文字体必须同时设 `font.name` + `rPr.rFonts.set('w:eastAsia', ...)`，否则中文回退宋体
- **用户偏好**：话术默认给文字/markdown + Word，不主动生成 PPT；用户说"生成ppt"才做 pptx
