# 记忆瘦身实测示例（2026-08-25）

场景：用户要求查看记忆清单并清理。先给编号表格清单（🔴删除/🟡精简/🟢保留），用户用编号回复："1234 67810 都可以删除，5、9、11 帮我精简"。

## 清单示例（编号规则供复用）
1. 🔴 数盾 license 到期跟踪（2026-05-28）→ 日期已过，删除
2. 🔴 数睿职位线 → 与 USER.md 重复，删除
3. 🔴 记忆容量上限记录 → config.yaml 已有，删除
4. 🔴 USER.md 面试评语短版 → 与完整版重复，删除
5. 🟡 OA 报销条 → 精简（留教训：查完必须写金额结果 + 修正 skill 引用 smardaten-oa→hermes-office-workflow）
6. 🔴 飞书原生表格 block_type=31 → skill 已覆盖，删除
7. 🔴 软件工厂人效模型 2025 → 用户选择删除
8. 🔴 2025 周计划人天数汇总 → 路径模式已确认在 chinese-enterprise-document-writing/references/zhoujihua-resource-analysis.md，删数字留路径
9. 🟡 Obsidian 条 → 精简（去动态细节，保留 vault 路径/推送机制/简历偏好）
10. 🔴 南通驻场团队条 → 人事动态已过期，删除
11. 🟡 软件工厂花名册+绩效 → 合并为一条指针（文件路径+飞书wiki+部长TL名单）

## 执行结果
- 批量 memory 调用：11 个 operations 一次应用（memory target）+ 1 个 replace（user target）
- MEMORY.md 3021→1872 字符（49→32 行）；USER.md 1341→1268 字符（28→27 行）
- git commit cca07c7「清理过期/重复记忆，精简OA/Obsidian/花名册条目」推送成功

## 关键教训
- 删前 grep 技能库确认细节另有存档（周计划路径模式）
- 记忆里的 skill 引用会过期，精简时顺手修正
- memory 工具批量 ops 原子应用，新内容别撞 old_text
- 清单用编号呈现，用户可快速回复（"1234 67810 都可以删除"）
