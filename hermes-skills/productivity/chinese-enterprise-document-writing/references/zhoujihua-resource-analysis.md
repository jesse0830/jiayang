# 周计划资源投入数据分析

从 SmarDaten OA 系统的周计划应用导出 Excel，分析各项目各角色实际资源投入，用于 HC 规划中的基准数据。

## 数据格式

周计划数据有两种常见格式：

### 格式A：时间轴横向展开（逐周列）

通常的周计划导出格式：
- 每周一行，项目维度，时间轴横向排列（周列）
- 表头有多行（至少2行）：第1行是大类标题（如"项目信息"、"2025年"），第2行是列名（如"项目"、"类别"、"实际投入"等）
- 典型列：项目名称、类别（AE/DE/IE/数据开发/实施/运维）、角色（通常与类别相同）、以及按周分布的投入小时数列
- 数据覆盖：通常为多个年份（如2025-2026），49-77周不等的记录

### 格式B：周计划资源投入记录列表（汇总聚合格式）

另一种常见格式，来自「周计划资源投入记录列表.xlsx」：
- **每行=一个项目在某一周的组合**，非逐列展开
- **表头结构（2行）**：
  - 第1行：父级标题（合并单元格），如"实际投入人天"跨越AE/DE/IE/数据开发/运维列
  - 第2行：子列名——`周代码 | 项目 | AE | DE | IE | 数据开发 | 运维 | 计划总投入 | 实际总投入 | 工作量偏差 | 上次统计时间`
- **列含义**：
  - `AE/DE/IE/数据开发/运维` = 各角色在本周该项目的实际投入人天数
  - `计划总投入` = 该行所有角色计划人天之和
  - `实际总投入` = 该行所有角色实际人天之合计列
  - `工作量偏差` = 计划-实际的差值
- **数据范围**：W02-W53（2025年约52周 × 多个项目 = 上千行），以周代码降序排列（最新在最前）
- **关键结构特征**：角色（AE/DE/IE/数据开发/运维）是**列（columns）**，不是行维度。每个角色的人天在同一行内
- **无PM列**：该Excel不含PM数据，只覆盖AE/DE/IE/数据开发/运维五个角色。如果需要PM数据进行HC分析，需要从其他渠道获取
- **文件路径模式**：此文件通常通过企业微信（WeWork）分享后下载，位于Mac的Caches目录下，路径模式：`/Users/jesseyoung/Library/Containers/com.tencent.WeWorkMac/Data/Documents/Profiles/*/Caches/Files/YYYY-MM/*/周计划资源投入记录列表.xlsx`

### ⚠️ 关键陷阱：Excel 数值以字符串形式存储

所有数值列（AE/DE/IE/数据开发/运维/计划总投入/实际总投入）在 openpyxl 中读取为**字符串类型**（如 `'0.00'` 而非 `0`），这是因为这些值来自 Excel 公式计算结果且启用了 `data_only=True`，而公式依赖的源数据可能不在本地。

```python
# ❌ 错误的读取方式（产生字符串）
wb = openpyxl.load_workbook(path, data_only=True)
ws = wb.active
cell_value = ws.cell(row=3, column=3).value  # 返回 '0.00' (字符串!)

# ✅ 正确的读取方式：to_num() 转换函数
def to_num(v):
    if v is None or v == '':
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        v = v.strip()
        if v == '' or v == '-':
            return 0.0
        try:
            return float(v)
        except:
            return 0.0
    return 0.0

value = to_num(ws.cell(row=3, column=3).value)  # 返回 0.0 (浮点数)
```

**pandas 用户注意**：`pd.read_excel()` 会自动转换字符串为数字，但如果遇到混合类型（如某些单元格是字符串而其他是数字），会用 `object` dtype。建议用 `pd.to_numeric(...)` 或读取后对整个 DataFrame 做类型转换。

**数据总量约束**：用户对数据完整性要求极高——必须翻完全部行（例如 208 行 21 页），不能只取前几页。

## 数据加载与清洗

```python
import pandas as pd
import openpyxl

# 读取Excel
df = pd.read_excel(path, sheet_name=0, header=None)

# 找到实际数据起始行（跳过标题行）
# 第0行通常是合并单元格标题，第1行是列名，数据从第2行开始
data_start = 2  # 或根据实际跳过

# 提取列名（第1行）
raw_cols = df.iloc[1].tolist()
df_clean = df.iloc[data_start:].copy()
df_clean.columns = raw_cols

# 过滤空行/无意义行
df_clean = df_clean.dropna(how='all')
```

## 关键清洗步骤

### 1. 跳过重复表头行
有些记录行中包含了表头（如"项目名称、类别、月份"），这是因为Excel导出时表头在分页中断后重复。需要过滤：

```python
# 过滤重复表头（行内包含"项目"、"名称"、"类别"等列名关键词）
header_keywords = ['项目', '类别', '实际投入', '每周', '序号']
mask = df_clean['项目名称'].astype(str).str.contains('项目', na=False)
df_clean = df_clean[~mask].copy()
```

### 2. 标准化列名
```python
# 重命名关键列
col_map = {}
for c in df_clean.columns:
    if '项目' in str(c):
        col_map[c] = '项目名称'
    elif '类别' in str(c):
        col_map[c] = '角色类别'
df_clean = df_clean.rename(columns=col_map)
```

### 3. 过滤无效数据
```python
# 只保留有实际投入的记录
# 找出所有周数据列（非元数据列）
week_cols = [c for c in df_clean.columns if c not in ('项目名称', '角色类别', '序号', '项目编码')]

# 转数值并过滤
for c in week_cols:
    df_clean[c] = pd.to_numeric(df_clean[c], errors='coerce')

# 过滤全部NaN的行
df_clean = df_clean.dropna(subset=week_cols, how='all')

# 只保留实际投入>0的行
df_clean = df_clean[(df_clean[week_cols] > 0).any(axis=1)]
```

## 核心分析计算

### 按角色汇总总人天

```python
# 假设周列是"人天"单位（1人天=1人工作1天）
df_clean['总人天'] = df_clean[week_cols].sum(axis=1)

# 按角色类别汇总
role_summary = df_clean.groupby('角色类别')['总人天'].sum().sort_values(ascending=False)

# 计算比例
total = role_summary.sum()
role_pct = (role_summary / total * 100).round(1)
```

### 按项目+角色汇总

```python
# 按项目和角色双重分组
project_role = df_clean.groupby(['项目名称', '角色类别'])['总人天'].sum().reset_index()

# 每个项目中角色的比例
project_totals = project_role.groupby('项目名称')['总人天'].sum().reset_index()
project_role = project_role.merge(project_totals, on='项目名称', suffixes=('', '_total'))
project_role['占比'] = (project_role['总人天'] / project_role['总人天_total'] * 100).round(1)
```

### 格式B专用：按角色列分组汇总

对于"周计划资源投入记录列表"（格式B），角色是列而不是行，汇总方式不同：

```python
# 角色列名映射（只取实际投入人天列）
role_cols = {
    'AE': 3, 'DE': 4, 'IE': 5,
    '数据开发': 6, '运维': 7
}
# 列索引号取决于实际文件结构（1-based: 1=周代码, 2=项目, 3=AE, 4=DE, ...）

# 按角色列单独求和
role_totals = {}
for role, col_idx in role_cols.items():
    total = sum(to_num(ws.cell(row=r, column=col_idx).value) for r in range(data_start, max_row + 1))
    role_totals[role] = round(total, 0)  # 取整

# 输出：AE=4443, DE=8999, IE=3781, 数据开发=915, 运维=268
# 不含PM！该Excel无PM数据
```

## 典型输出

角色配比基准表（Excel提取数据，不含PM）：

| 角色 | 总人天 | 占比 |
|------|--------|------|
| AE | 4443 | 24.5% |
| DE | 8999 | 49.6% |
| IE | 3781 | 20.8% |
| 数据开发 | 915 | 5.0% |

**典型配比（Excel提取 2025年基准）：AE:DE:IE:数据开发 = 1:2.03:0.85:0.21**

### 比值展示格式（用户偏好）

用户习惯的配比展示方式（不用千分位，显示比例关系）：

```
原始比值（以AE=1为基准）：1 : 2.03 : 0.85 : 0.21
简化整比（比例对齐）：         5 : 10  : 4   : 1
```

**展示规则：**
- 数字用纯数字，不用千分位（4443 不用 4,443）
- 先给原始比值（以AE=1），再给简化整比
- 比值格式：`AE:DE:IE:数据开发 = 1:2.03:0.85:0.21`
- ⚠️ 当多个来源数据不一致时（如Excel提取 vs 用户口头给出的数字），**以用户最新给出的数字为准**，不要执着于自己的提取结果

### ⚠️ Excel提取 vs 用户提供数字的差异

| 角色 | Excel提取值 | 用户提供值（2026年7月会话） |
|------|-------------|--------------------------|
| AE | 4443 | 4426 |
| DE | 8999 | 9302 |
| IE | 3781 | 3787 |
| 数据开发 | 915 | 928 |
| 合计 | 18137 | 18443 |

差异原因推测：用户提供的数字可能来自不同的统计口径（如包含/排除某些项目类型）。**当用户给出新数字时，以用户为准**。

### 2025年完整基准数据（Excel提取，验证过的）

| 维度 | 数值 |
|------|------|
| 实际执行总人天 | 18065（AE 4443 + DE 8999 + IE 3781 + 数据开发 915 + 运维 268） |
| 计划总投入人天 | 19859（不含PM） |
| 覆盖周期 | W02-W53（2025年全年，52周数据） |
| 实际产能利用率 | AE ~68%、DE ~68%、IE ~69% |
| 项目数 | ~125个项目 |

## 说明

- 人天数据来自周计划系统，是实际填报的资源投入，比 HR 系统数据更准确反映一线人员配置
- 这个基准可用于对比各区域/项目的真实配比 vs 理想配比
- 注意：周计划数据可能不包括管理层/非产出型角色；如果是全员周报则包含全部
- 如果数据跨多年，建议按年分别计算，观察配比变化趋势
- **格式B的数据天然不含PM**（Excel中没有PM列），用于HC分析时需另取PM数据
- **WeWork 文件路径**：从企业微信分享下载的Excel文件存放在Caches目录，路径含Profiles/随机串/Caches/Files/日期，每次分享下载的文件名可能带随机后缀，建议用 `search_files` 按文件名查找后确认路径
