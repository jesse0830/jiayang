# 收入-资源交叉匹配分析（三级看板）

## 用途

将**收入明细表**（25年收入-项目.xlsx）和**周计划资源投入记录列表.xlsx**两个数据源交叉匹配，按收入金额三级分类（<30万 / 30-100万 / >=100万），计算每个等级内各角色（AE/DE/IE/数据开发）的实际投入人天和占比。

产出：一个三级看板（kanban），回答「不同金额等级的项目，各角色分别投了多少人天、占比如何？」。

## 数据源结构

### 数据源A：收入明细表

| 特征 | 说明 |
|------|------|
| 来源 | 财务系统导出，25年收入-项目.xlsx |
| 行数 | ~184 笔（逐笔入账记录） |
| 关键列 | 项目名称、客户、里程碑、收入金额 |
| 单位 | 元（需转为万） |
| 特点 | 同一项目可能有多次入账记录（首付/验收/质保分笔） |

### 数据源B：周计划资源投入表

| 特征 | 说明 |
|------|------|
| 来源 | OA周计划导出，周计划资源投入记录列表.xlsx |
| 列 | 项目名称、角色类别（AE/DE/IE/数据开发等）、各周人天数 |
| 特点 | 项目名与收入表不完全一致，需要模糊匹配 |
| 注意 | 无PM列，不包含管理层的投入 |
| 注意 | 包含"内部项目/非收入项目"（如维保、内部管理、非客户项目）——这些无对应收入，需单独归类 |

## 核心算法：三级看板生成

### Step 1：加载收入数据，按项目名聚合，三级分类

```python
import pandas as pd
import numpy as np
from collections import defaultdict

# 加载收入表
df_income = pd.read_excel('25年收入-项目.xlsx', sheet_name=0)
df_income['金额_万'] = pd.to_numeric(df_income['收入金额'], errors='coerce') / 10000

# 按项目名聚合（同一项目多笔入账合并）
project_revenue = df_income.groupby('项目名称')['金额_万'].sum().sort_values(ascending=False)

# 三级分类函数
def classify_revenue(amount):
    if amount >= 100:
        return '>=100万'
    elif amount >= 30:
        return '30-100万'
    else:
        return '<30万'

project_tier = project_revenue.apply(classify_revenue)
```

### Step 2：加载资源数据，按项目+角色汇总

```python
# 加载周计划表
df_resource = pd.read_excel('周计划资源投入记录列表.xlsx', sheet_name=0)
# 同 zhoujihua-resource-analysis.md 的清洗流程

# 找出周数列
week_cols = [c for c in df_resource.columns if c not in ('项目名称', '角色类别', '序号')]
for c in week_cols:
    df_resource[c] = pd.to_numeric(df_resource[c], errors='coerce').fillna(0)

df_resource['总人天'] = df_resource[week_cols].sum(axis=1)
```

### Step 3：项目名匹配（关键步骤）

**核心难点：** 两个Excel中的项目名不一致。收入表中的项目名偏正式/合同名，资源表中的项目名偏日常/简称。

匹配策略（按优先级从高到低）：

1. **完全匹配** — 项目名完全一致
2. **包含匹配** — 收入项目名是资源项目名的子串，或反之
3. **关键词匹配** — 提取双方项目名的关键词（如去掉"合同""项目"后缀，取共同汉字）
4. **手动映射** — 对无法自动匹配的大项目，手动建立映射表

```python
def match_projects(income_names, resource_names):
    """手动映射为主 + 自动匹配为辅"""
    manual_map = {}  # income_name -> resource_name
    
    # 完全匹配
    for iname in income_names:
        if iname in resource_names_set:
            manual_map[iname] = iname
    
    # 包含匹配
    for iname in income_names:
        if iname in manual_map:
            continue
        for rname in resource_names:
            if iname in rname or rname in iname:
                manual_map[iname] = rname
                break
    
    # 大项目（>=30万）必须逐个确认——不能用自动匹配
    # 打印未匹配项目，手动映射
    return manual_map
```

**⚠️ 关键教训：不要依赖完全自动化的模糊匹配。** 项目名称的差异无法用算法可靠解决。正确的策略是：

1. 先用完全匹配+包含匹配自动处理一部分
2. 列出未匹配的项目，特别是>=30万的项目必须逐个手动映射
3. 手动映射后验证——检查匹配后的资源投入与收入是否合理对应（如400万苍南项目→app_苍南）

### Step 4：匹配结果验证

验证指标：
- **收入覆盖率**：已匹配收入 / 总收入，应 >80%
- **大项目覆盖率**：>=100万的项目必须全部匹配
- **30-100万**：尽量匹配，少量FAQ标的不可匹配是正常的（如"在途收入"、"其它零星"）
- **<30万**：允许大量不匹配（收入项目多、合同名短，周计划表中可能是零散增补）

如果大项目（>=100万）匹配失败，需要通过`session_search`查找过往会话中的项目别名。

```python
# 检查每个大项目的匹配情况
large_unmatched = [p for p in large_projects if p not in manual_map]
if large_unmatched:
    print(f"未匹配的大项目: {large_unmatched}")
    print("需要手动补映射表")
```

### Step 5：按三级聚合资源投入

```python
# 将资源项目归到对应的收入等级
resource_tier_map = {}
for income_name, resource_name in manual_map.items():
    resource_tier_map[resource_name] = project_tier[income_name]

# 未匹配到收入的资源项目 → 归入"内部/非收入"类
resource_df['tier'] = resource_df['项目名称'].map(resource_tier_map)
resource_df['tier'] = resource_df['tier'].fillna('内部/非收入')

# 按等级 + 角色汇总
tier_role = resource_df.groupby(['tier', '角色类别'])['总人天'].sum().reset_index()

# 透视表
pivot = tier_role.pivot_table(
    index='tier', columns='角色类别', values='总人天', aggfunc='sum', fill_value=0
)

# 加上总收入
# 注意：每个等级的收入是收入表中同等级所有项目的总和，不是匹配到的项目
tier_revenue = project_tier.groupby(project_tier).apply(lambda g: project_revenue.loc[g.index].sum())

# 也统计每个等级中包含多少收入项目和资源项目
tier_income_count = project_tier.value_counts()
tier_resource_count = resource_df.groupby('tier')['项目名称'].nunique()
```

### Step 6：生成看板输出

```python
# 输出格式
tiers_order = ['>=100万', '30-100万', '<30万', '内部/非收入']
print("| 等级 | 收入项目数 | 资源项目数 | 收入(万) | AE人天 | DE人天 | IE人天 | 数据开发人天 | 合计人天 | AE% | DE% | IE% | 数据% |")
print("|------|-----------|-----------|---------|-------|-------|-------|-----------|--------|-----|-----|-----|------|")

for tier in tiers_order:
    if tier not in pivot.index and tier != '内部/非收入':
        continue
    
    rev = tier_revenue.get(tier, 0)
    income_n = tier_income_count.get(tier, 0)
    resource_n = tier_resource_count.get(tier, 0)
    
    ae = pivot.loc[tier].get('AE', 0)
    de = pivot.loc[tier].get('DE', 0)
    ie = pivot.loc[tier].get('IE', 0)
    data = pivot.loc[tier].get('数据开发', 0)
    total = ae + de + ie + data
    
    ae_pct = round(ae/total*100, 1) if total > 0 else 0
    de_pct = round(de/total*100, 1) if total > 0 else 0
    ie_pct = round(ie/total*100, 1) if total > 0 else 0
    data_pct = round(data/total*100, 1) if total > 0 else 0
    
    print(f"| {tier} | {income_n} | {resource_n} | {rev:.0f} | {round(ae)} | {round(de)} | {round(ie)} | {round(data)} | {round(total)} | {ae_pct} | {de_pct} | {ie_pct} | {data_pct} |")
```

## 典型输出示例

| 等级 | 收入项目数 | 资源项目数 | 收入(万) | AE人天 | DE人天 | IE人天 | 数据人天 | 合计 | AE% | DE% | IE% | 数据% |
|------|-----------|-----------|---------|-------|-------|-------|--------|------|-----|-----|-----|------|
| >=100万 | 7 | 9 | 1155 | 847 | 1535 | 776 | 186 | 3344 | 25.3 | 45.9 | 23.2 | 5.6 |
| 30-100万 | 21 | 17 | 1066 | 1156 | 1819 | 782 | 94 | 3851 | 30.0 | 47.2 | 20.3 | 2.4 |
| <30万 | 97 | 31 | 964 | 1681 | 4108 | 1477 | 593 | 7859 | 21.4 | 52.3 | 18.8 | 7.5 |
| 内部/非收入 | 0 | 75 | 0 | 759 | 1536 | 746 | 42 | 3083 | 24.6 | 49.8 | 24.2 | 1.4 |
| **合计** | **125** | **132** | **3185** | **4443** | **8999** | **3781** | **915** | **18137** | **24.5** | **49.6** | **20.8** | **5.0** |

## 关键洞察模式

看板出来后，逐行分析：

### >=100万（大项目）
- 通常收入占比最高（~36%），但项目数最少（~6%）——二八定律
- DE占比最高（~46%），因为大型开发需要大量代码人力
- AE占比~25%，偏高——大项目需要更多前期设计和客户对接

### 30-100万（中项目）
- 收入占比和项目数相对均衡（~33%）
- AE占比最高（~30%）——中等项目对AE的设计依赖更大
- 数据开发占比最低（~2%）——这类项目通常数据量不大

### <30万（小项目）
- 项目数量最多（~78%），但收入占比最低（~30%）
- DE占比最高（~52%）——小项目以小修小改为主
- 数据开发占比最高（~7.5%）——小项目中数据需求占比反而高
- **关键信号**：项目多而散，管理成本高（PM精力消耗大）

### 内部/非收入
- 项目数可能高达75个，投入3083人天（占全部人天的17%）
- 这部分是"不产生收入但消耗资源"的工作——维保、内部优化、非标支持
- 应主动问用户："这么多非收入项目消耗17%的产能，这些是必要的吗？还是通过提效可以压缩？"

## 人效计算（人天×收入 vs 岗位×收入）

结合三级看板，可以计算不同等级的人效：

```python
# 方式1：人天视角（不含内部项目）
total_revenue = 3185  # 万
productive_pd = 18137 - 3083  # 排除内部/非收入
efficiency = total_revenue / productive_pd
# 结果示例：0.21 万/人天（即每投1人天产生约2100元收入）

# 方式2：按角色算人效
# AE人效 = 总收入 / AE总人天（排除内部）
ae_pd_productive = 4443 - 759  # AE总人天 - 内部AE人天
ae_efficiency = 3185 / ae_pd_productive
```

## 对比：项目数视角 vs 人天视角

这个看板揭示了收入和资源之间的**结构性不匹配**：

| 等级 | 项目数占比 | 收入占比 | 人天投入占比 | 信号 |
|------|-----------|---------|------------|------|
| >=100万 | 5.6% | 36.3% | 18.4% | 大项目效率高（人天投入小于收入占比） |
| 30-100万 | 16.8% | 33.5% | 21.2% | 中等项目效率次之 |
| <30万 | 77.6% | 30.3% | 43.3% | 小项目效率低（人天投入远大于收入占比） |

**核心结论：小项目消耗44%的资源，只产生30%的收入——是人效提升的关键切入点。**

## 常见陷阱

### 陷阱1：项目名匹配率低

收入表184笔，按项目名聚合后约125个不同项目名。资源表有数百个行项。完全匹配率可能只有30-50%。**手动映射后需确认收入覆盖率 > 80%。**

### 陷阱2：资源表中的"内部项目"被误归到收入类

有些项目在资源表中名字像收入项目（如包含客户名），但实际上没有对应的收入记录。这些应该归到"内部/非收入"，强行匹配会歪曲数据。

**判断方法：** 如果一个资源项目名在所有收入项目名中找不到任何关键词匹配（含拼音缩写检查），且投入人天只出现在某1-2周（不像长期项目），很可能就是内部项目。

### 陷阱3：执行的的嵌套问题

在 `execute_code` 中执行 pandas 操作时，注意：
- `groupby.apply()` 中如果 lambda 返回布尔值，不要直接用 `&` 或 `|` 组合条件——会触发"ambiguous truth value"错误
- 用 `.loc[condition]` 替代直接布尔索引
- 翻页/多文件处理时，建议手动规划步骤，不要写一个超长脚本一次性执行

### 陷阱4：不要忽略大项目匹配失败

如果>=100万的项目匹配失败，看板会严重失真（大项目的收入-资源对应失效）。常见的解决方案：通过之前的会话（session_search）查找项目别名，或者直接问用户"XX项目在周计划里叫什么名字？"
