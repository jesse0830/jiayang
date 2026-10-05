---
name: xmind-parsing
description: "Parse .xmind files into structured text (zip+content.json)."
version: 1.0.0
created_by: agent
metadata:
  tags: [xmind, mindmap, parsing, zip, content.json]
  languages: [zh-CN, en]
---

# XMind 思维导图解析

适用于用户提供 `.xmind` 源文件要求"总结/提取内容"的场景。**优先用源文件解析，不要 OCR 图片**：xmind 导出 PNG 常因缩略图/低分辨率导致 tesseract 输出为空或乱码，而源文件是结构化 JSON，解析结果精确完整。

## 触发条件

- 用户附上 `.xmind` 文件（如"这个是刚刚图片的源文件 xmind，帮我重新总结下"）
- 用户先给思维导图截图、后又给源文件——直接要源文件解析，比 OCR 好得多

## 解析步骤

1. **解压**（xmind 本质是 zip 包）：
   ```bash
   mkdir -p /tmp/xmind_extract && cd /tmp/xmind_extract
   unzip -o "$HOME/Downloads/xxx.xmind" >/dev/null 2>&1
   find . -type f   # 可见 content.json / content.xml / metadata.json / Thumbnails/thumbnail.png
   ```

2. **读 content.json**：
   ```python
   import json
   d = json.load(open('content.json'))   # 顶层是 list，每个元素是一个 sheet
   root = d[0]['rootTopic']              # rootTopic.title = 导图根标题
   ```

3. **递归提取**（children 可能是 dict 或 list，两种都要处理）：
   ```python
   def extract(node, depth=0):
       print('  '*depth + '- ' + node.get('title', ''))
       children = node.get('children', {})
       if isinstance(children, dict):
           for key in ('attached', 'detached', 'summary'):
               for child in children.get(key, []):
                   extract(child, depth+1)
       elif isinstance(children, list):
           for child in children:
               extract(child, depth+1)
   extract(root)
   ```

4. **整理输出**：把缩进树转成带编号的分级清单（一、二、三…），叶子节点中的多行文本（如"1、xxx；2、yyy"）保留原样。

## 坑与经验

- **children 结构两种形态**：新版 xmind 用 `{"attached": [...]}`，旧版可能是裸 list。解析代码必须两者兼容，否则漏掉一半分支。
- **OCR 对比**：同内容图片 OCR（tesseract chi_sim+eng，psm 3/4/6/11/12 全试）会漏项、误解（如"安全漏洞处理"被拆散、"备份"归类错）。源文件解析后主动指出"比 OCR 版本新增了哪些点"，用户会确认。
- **解析完的结论别只给树**：转成用户可用的分级总结（模块 → 子项 → 细节），并说明和之前 OCR 版本的差异。

## 参考文件

- （暂无）后续可加 `references/xmind-structure-notes.md` 记录不同 xmind 版本 content.json 的字段差异。
