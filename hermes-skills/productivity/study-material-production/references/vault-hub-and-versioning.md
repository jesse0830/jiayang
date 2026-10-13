# 一套材料的「主文档（hub）+ 版本号」落地配方

触发：用户说「全部放到 obsidian 里，并告诉我在 obsidian 中以哪个文档为主」、或材料升了版本号（v1.x → v1.y）。

## 1. 主文档怎么写

```markdown
---
title: X 备考总入口（主文档）
type: hub
tags: [mba, learning, reference, hub]
aliases: [X备考总入口, X主文档, 备考主文档, X从这里开始]
updated: YYYY-MM-DD
---

# X 备考总入口（主文档）

> [!important] 这份就是主文档 —— X 只看这一页

## 每天动这几份 / 要查的时候翻 / 知识库页     ← 分组导航表
## 每天怎么用（三步）                          ← 打开 → 看今天 → 打卡
## 重要日期
```

- **`aliases` 是让人找得到的关键**：文件名带 `_v1.4` 没人想记，别名让 `Cmd+O` 输入「主文档 / 总入口」即可跳到；同时 `[[X备考总入口]]`（不带版本号）也能解析到它。别名要覆盖「总入口 / 主文档 / 从这里开始」三种叫法。
- hub 是**导航**，不复制正文；资料仍各在各的文件里，否则维护两份必然走形。

## 2. 升版必做三件事

1. **全库改写引用指新版本**（用 execute_code 批量字符串替换）：`wiki/concepts/*.md`、其它资料的互链、旧 hub 内部链接。**跳过** `raw/sources/`（镜像由拷贝完成，不是改写）与 `wiki/log.md`（历史流水不能动）。
2. **挂进知识库索引**：`wiki/index.md` 末尾加一节「主文档 / 快捷入口」，一行指向新 hub（hub 常不在 wiki 目录下，索引里也得有它的位置，否则按 index 检索永远找不到）。
3. **删旧版本文件**，并把新 hub 拷进 `raw/sources/` 与 `99-软件工厂/98 hermes/`。

## 3. 让用户「三条路都能打开」

| 方式 | 做法 | 可靠性 |
|---|---|---|
| 书签栏 | `.obsidian/bookmarks.json` 预置一条 | ⚠️ Obsidian 运行时把配置持在内存、退出时整体覆写，手改会被吃掉（先 `pgrep -x Obsidian`，在跑就别写）→ 让用户点一下星标 |
| 快速切换 | 笔记 frontmatter 的 `aliases` | ✅ 属于笔记内容，随 git 走 |
| 固定路径 | 直接给 `JesseYoung/MBA/<hub>.md` | ✅ |

回执里三种都给，并说明「若书签栏没显示，给这页点个星标即可」——别把预置书签说成一定生效。

## 4. 校验命令（回执前跑一遍）

```bash
cd <vault>
ls JesseYoung/MBA/ | wc -l                       # 库内文件数
ls raw/sources/ | grep -c MBA                    # 镜像数
grep -rl "<旧版本>" --include=*.md . | grep -v "^./.git/"   # 残留引用（逐条 grep -n 看命中行再判断）
grep -o "\[\[<新hub名>" wiki/index.md            # 索引已指向新版
pgrep -x Obsidian                                # 客户端是否在跑（决定要不要碰 .obsidian/）
git log --oneline -3 && git push origin master && git status -sb
```

链接完整性校验：抽 `[[...]]` 目标 → **剥掉 `\|` 等转义反斜杠** → 与库内文件名集合比对，报 MISS 时先确认是不是转义造成的假阳性。

## 5. 回执格式

1. 首行直接给答案：**主文档 = `<绝对/库内路径>`**，再一句「为什么是它」（它是工作台，其余都是下挂资料，不用记文件名）。
2. 打开方式三种（书签 / `Cmd+O` 搜别名 / 固定路径），书签那条带上「没显示就点星标」的兜底。
3. 「库内结构」表：分组 | 文件 | 作用；外加 raw/sources 与 98 hermes 两处同步说明。
4. 「已验证」小节列真实数字（文件数、链接校验、无残留旧引用、commit SHA）。
5. 收尾给一个明天就能做的小动作 + 一段 English time。
