# Audio Transcription Workflow (Whisper)

适用于把会议/汇报录音转文字，作为文档优化、反馈分析的数据采集前置步骤。

适用于 `chinese-enterprise-document-writing` 中的「Feedback-Driven Document Revision (录音反馈→文档迭代)」工作流。

**两种主要使用场景：**
1. **用户直接发录音让你总结**（"帮我把这段录音总结一下"）→ 独立任务，输出结构化会议纪要即可
2. **录音是文档优化的输入**（方总反馈录音→要改飞书文档）→ 需要做 feedback→revision gap analysis

## 转录环境准备

### 检查音频文件

```bash
ls -la "<用户提供的路径>"
ffprobe "<路径>" 2>&1 | grep -E "Duration|bitrate"
```

关键信息：
- 文件大小：判断转录所需时间（约 40KB/sec for small model on CPU）
- 时长：base model 约 3x 实时，small 约 6x 实时
- 检查 whisper 是否已安装：`which whisper` 或 `pip3 show openai-whisper`

### 安装 Whisper（如未安装）

```bash
pip3 install openai-whisper
```

⚠️ 注意：macOS Apple Silicon 上 Whisper 可能无法启用 MPS/FP16 加速（输出 `FP16 is not supported on CPU; using FP32 instead` 警告），属于正常现象。

## 场景一：用户直接发录音要求总结（独立任务）

当用户说"帮我把这段录音总结一下"或发送一个 MP3 文件时：

### 工作流

1. **检查文件**：确认文件存在、大小、时长（ffprobe）
2. **选择模型**：
   - 30分钟以内录音 → small 模型直接全量转录（前台600s可能不够，用后台模式）
   - 5分钟以内 → base模型快速预览 + small全量
3. **转录**：用 `background=true, notify_on_complete=true` 运行 Whisper small
4. **读取输出**：txt 文件最易阅读，40KB文本约1632行
5. **生成结构化会议纪要**：包含以下章节

### 会议纪要输出结构（标准模板）

保存到桌面：`/Users/jesseyoung/Desktop/YYYY-MM-DD_主题_录音总结.md`

```markdown
# [日期] [主题] 录音总结

## 概述
一句话说明会议性质（如：XX总关于YYYY的汇报会）

## 核心议题 (3-5条)
- 议题A：说明
- 议题B：说明

## 决策与结论
- 决策1：...
- 决策2：...

## 关键行动项
| 事项 | 负责人 | 时间要求 |
|------|--------|---------|
| ... | ... | ... |

## 金句（领导原话引用）
> "..."

## 关键数据（录音中提到的数字/指标）
- 数据项1: 值
- 数据项2: 值

## 我的分析/建议（如有）
- 需要关注的点
- 与现有数据的交叉验证
```

### 常见格式偏好
- 保存到桌面（`/Users/jesseyoung/Desktop/`）
- 文件名格式：`YYYY-MM-DD_主题_录音总结.md`
- 用 markdown 格式，便于复制粘贴使用
- 如果用户还提供了相关 Excel 数据，在末尾追加"数据交叉分析"章节

**两步法（推荐）：**
1. **base 模型快速预览**（前台，约 3x 时长）：
   ```bash
   whisper "<路径>" --model base --output_dir /tmp/whisper_output/ --language zh
   ```
   — 用来快速了解内容是否有效、大致主题

2. **small 模型全量转录**（后台，notify_on_complete）：
   ```bash
   whisper "<路径>" --model small --output_dir /tmp/whisper_output_small/ --language zh
   ```
   — 设置 `background=true, notify_on_complete=true`
   — 前台 timeout 600s 不够时用后台模式

### 模型选择

| 模型 | 适用场景 | macOS CPU 耗时估计 |
|------|---------|-------------------|
| `base` | 快速预览（断句错误、乱码常见） | 20min录音约10min |
| `small` | 全量转录（推荐） | 20min录音约15-20min |
| `medium` | ❌ **不推荐 macOS CPU** | 20min录音需数小时 |
| `large` | ❌ 仅 GPU 环境 | 同上 |

**总结：macOS CPU（Apple Silicon）上 small 是最佳性价比的终点。**

## 读取转录结果

转录成功后会生成 5 个文件：
- `.txt` — 纯文本（最易阅读和摘要）
- `.srt` / `.vtt` — 带时间轴的字幕
- `.tsv` — 结构化表格
- `.json` — 完整结构化数据（含每个 segment 的时序和置信度）

推荐读取 txt 文件用 `read_file`。

## 提取关键内容（结构化总结）

| 分类 | 提取要点 |
|------|---------|
| **核心议题** | 会议主要讨论什么？ |
| **决策与结论** | 谁拍板了什么？ |
| **反馈点** | 对应原文的哪些内容需要修改 |
| **关键行动项** | 谁、做什么、什么时间 |
| **金句** | 领导原话（可用于材料引用） |

## Feishu API 写入（可选，优化版文档回写）

### 获取 token
```bash
curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "{\"app_id\":\"$FEISHU_APP_ID\",\"app_secret\":\"$FEISHU_APP_SECRET\"}"
```

### 文档 block 类型（批量写入）

| Block Type | 编号 | 批量写入支持 |
|------------|:----:|:-----------:|
| Text | 2 | ✅ |
| Heading1 | 3 | ✅ |
| Heading2 | 4 | ✅ |
| Heading3 | 5 | ✅ |
| Heading4 | 6 | ✅ |
| Code | 9 | ✅ |
| Quote | 17 | ✅ |
| Bullet | 12/31 | ❌ 用 `• ` 前缀 Text 模拟 |
| Divider | 24 | ❌ 用全角横线文本模拟 |

### 覆盖写入文档策略

飞书 docx API 不支持批量删除/替换 block，有三种策略：
1. **新建文档**：创建新文档写入优化版，把链接给用户
2. **逐 block 修改**：读取原有 block 列表，更新/删除后插入
3. **通过云文档 API 批量替换**：用 PATCH 一次性替换所有子 block

### ⚠️ API 写入权限不足（错误 1770032）

即使获取 token 成功且读取 API 正常，写操作可能返回 403/1770032。

| 权限 | 支持的操作 |
|------|-----------|
| `drive:drive:readonly` | 仅 GET（读取）|
| `drive:drive` | GET + PATCH/POST/DELETE（读写）|

**诊断：** 尝试最小写操作测试权限。如果返回 403/1770032，确认是只读权限。

**修复：** 飞书开发者后台 → 权限管理 → 添加 `drive:drive` → 发布新版本。

**回退方案：** 输出优化版到本地 markdown → 用户手动复制。

## 数据交叉分析模式（录音+Excel）

当用户同时提供**录音（反馈/讨论）** 和 **结构化数据（Excel/CSV）**时，需要做交叉分析：

### 典型场景
- 领导汇报录音 + 部门收入/成本数据表
- 录音中有管理层的目标和要求（如"7200万目标"、关闭低效代表处）
- 数据表反映了实际业绩

### 分析流程

1. 先转录录音，提取关键决策、目标、反馈点
2. 读取数据文件，做多维分析（见 `chinese-enterprise-document-writing` → `references/enterprise-revenue-analysis.md`）
3. 交叉对比：
   | 录音要点 | 数据证据 | 结论 |
   |---------|---------|------|
   | 全年目标7200万 | 实际完成3,185万(44.2%) | 缺口显著 |
   | "成都低效" | 成都全年仅7,500元 | ✅ 建议关闭/合并 |
   | "12月压线回款" | 12月618万(19.4%)占全年最高 | 风险集中 |
4. 输出综合分析报告，将"听见的"和"算出的"一并呈现

### 里程碑排除分析（录音+Excel交叉验证）

当录音中的领导反馈提到"收入 ≠ 产能"、"首付款不算产能"时需要做交叉分析：

1. 从 Excel 收入明细表读取全部收入记录
2. 按里程碑字段分类
3. 排除首付款/质保款
4. 计算有效产能收入
5. 对比录音中说的目标
6. 输出复合结论
