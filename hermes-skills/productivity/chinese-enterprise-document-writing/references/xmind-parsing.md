# XMind 思维导图解析（.xmind → 结构化文本）

当用户提供 `.xmind` 文件（或说"图片的源文件是 xmind"）时，**不要 OCR 截图**——xmind 是结构化格式，直接解析比 OCR 精确得多（截图 OCR 会乱：表格/连线错位、中文乱码、漏行）。

## 触发场景
- 用户给 .xmind 文件要求"总结/提取内容"
- 用户给思维导图截图 + 说明"我有源文件 xmind，更清晰"（此时改要源文件）
- 运维工作清单、流程梳理、方案结构等思维导图类素材

## 解析方法（已验证 2026-08）

`.xmind` 本质是 **zip 压缩包**，里面是 JSON/XML 内容：

```bash
cd /tmp && mkdir xmind_x && cd xmind_x
unzip -o "$HOME/Downloads/xxx.xmind"   # 解出 content.json / content.xml / metadata.json
```

**主内容在 `content.json`**，结构：
- 顶层是 sheet 列表（`[{id, class, rootTopic, title, ...}]`）
- `rootTopic.title` = 中心主题
- 每个 topic 有 `title` + `children`（`{attached: [子topic...]}` 或列表）

递归提取：
```python
import json
d = json.load(open('content.json'))
root = d[0]['rootTopic']

def extract(node, depth=0):
    title = node.get('title', '')
    print('  ' * depth + '- ' + title)
    children = node.get('children', {})
    if isinstance(children, dict):
        for key in ('attached', 'detached', 'summary'):
            for child in children.get(key, []):
                extract(child, depth + 1)
    elif isinstance(children, list):
        for child in children:
            extract(child, depth + 1)

extract(root)
```

**注意**：
- 有些节点 title 为空（纯分支），跳过或保留层级
- 长文本节点（如工作说明、多行）在 title 里会带 `\n`，保留
- 某些 xmind 版本可能用 `content.xml` 而非 `content.json`，先看解压出什么
- 递归结果就是清晰的树状结构 → 直接整理成 markdown 文档/总结

## 对比：为什么不用 OCR
同一份内容，xmind 解析能拿到 100% 准确文本（含"安全漏洞处理""现网镜像环境复刻"等 OCR 漏掉/误解的节点），OCR 只能拼出 70-80% 且错字多。**有源文件一律解析，不用 OCR。**
