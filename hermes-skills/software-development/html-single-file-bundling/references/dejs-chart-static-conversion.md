# 去 JS 化：把 ECharts 渲染改成静态 HTML + SVG/CSS

2026-09-21 在用户 `~/Downloads/首页` 数据驾驶舱上跑通：1091591 → 82861 bytes，`scripts=0`、内联事件 0、`externalResources=[]`、`canvas=0`、23 个内联 `<svg>`，整页 1920x4538 与原版**分毫不差**，15 个图表平均色差 2.86/255。

## 0. 口径
- 目标：HTML 里**不出现任何 JS 代码** —— 0 个 `<script>`、0 个内联 `on*` 属性、0 个 `javascript:` 协议。
- 图表库（ECharts/Chart.js/Highcharts）也是 JS → 换成**内联 `<svg>`**（SVG 是 HTML 标签，不算 JS）或纯 CSS（`conic-gradient` 画环图）。
- 验收 = 不比原版丑、不比原版偏：结构 + 文本 + 像素三层都要过（见第 4 节）。

## 1. 方法总览（别凭截图描图）
1. **保留一份还带 JS 的原版**（本例 `index.bak-echarts-20260921.html`）；生成脚本要能从备份候选里挑源文件，因为主文件随时会被别的会话覆盖。
2. 浏览器打开原版 → 用**库自己的 API 回读几何** → 存 JSON（本例 `ref/chart-geometry.json`）。
3. 离线 Python 用几何算坐标 → 拼 `<svg>` / HTML 字符串 → 写出新 `index.html`（生成过程不写一行 JS）。
4. 三层验收 → 安装 + `change-log.md` 记录（含其他会话版本的去留与理由）。

## 2. ECharts 几何回读（browser_exec 里跑）

```js
(() => {
  const out = {};
  document.querySelectorAll('[id^=ch]').forEach(el => {
    const c = echarts.getInstanceByDom(el);
    if (!c) return;
    const s = c.getOption().series[0];
    const rec = { w: el.clientWidth, h: el.clientHeight, dpr: window.devicePixelRatio };
    if (s.type === 'pie') {
      rec.kind = 'pie';
      rec.radius = s.radius;                 // ['45%','70%'] → 乘 min(w,h)/2 得像素
      rec.center = s.center;
      rec.startAngle = s.startAngle ?? 90;   // 默认 12 点起
      rec.clockwise = s.clockwise ?? true;
      rec.data = s.data.map(d => ({
        name: d.name, value: d.value,
        color: d.itemStyle && d.itemStyle.color,
        borderWidth: (d.itemStyle && d.itemStyle.borderWidth) || 0
      }));
    } else {
      rec.kind = 'line';
      rec.grid = c.getModel().getComponent('grid').coordinateSystem.getRect(); // {x,y,width,height}
      rec.xTicks = c.getModel().getComponent('xAxis').axis.getTicksCoords()
                     .map(t => ({ v: t.tickValue, px: t.coord }));
      rec.yTicks = c.getModel().getComponent('yAxis').axis.getTicksCoords()
                     .map(t => ({ v: t.tickValue, px: t.coord }));
      rec.points = s.data.map((v, i) => ({
        i, v, px: c.convertToPixel({ seriesIndex: 0 }, [i, v])   // ⭐ 画布绝对坐标
      }));
      rec.areaStyle = s.areaStyle || null;   // 面积渐变的起止色
    }
    out[el.id] = rec;
  });
  return out;
})()
```

注意：`getOption()` 给的是**用户参数**（百分比、颜色名），像素要自己乘容器尺寸；`convertToPixel` 必须在图表渲染完成后调用；`getTicksCoords()` 的字段是 `coord`/`tickValue`。

## 3. 生成侧要点

### 环图 / 甜甜圈（一个分段一个 `<path>`）
- 角度换算：`startAngle=90` 且 `clockwise=true` → 0° 在 12 点、顺时针增加；SVG 弧用 `A` 命令。
- **`borderWidth` 还原**：可见扇区整体内缩 → `r_out - bw/2`、`r_in + bw/2`（否则环比原版粗一圈）。
- **有底色环不切 gap**：`len(data)==2 and data[1][0] > 0` → `gap = 0`，否则 12 点位置露缝。
- 中径（采样/描中心文字用）：`r_mid = r_out * (f_in + f_out) / (2 * f_out)`。
- 渐变 → `<linearGradient>`；进度环 → `<circle>` + `stroke-dasharray`。

### 平滑折线
- Catmull-Rom → 三次贝塞尔控制点；面积 = 同路径闭合 + `<linearGradient>` 填充。
- 网格线/刻度用回读的 tick 像素位；**轴标签 x 用数据点自身 x**；轴标签基线 = `y0 + gh + 17.5`（比 16 低 1.5px 才和 ECharts 对齐）。
- 数据标注框（本例「接入总量 87.23」）= 圆角 `<rect>` + `<text>`，位置从原版回读。

### 坑①（最容易漏）
`axis.dataToCoord(v)` 返回**网格相对**坐标（0..gridW），`chart.convertToPixel()` 返回**画布绝对**坐标（gridX..gridX+gridW）。混用 → 轴标签整体偏移 `grid.x`（本例 44px：红蓝双影 + 最左标签被裁）。数据点走 `convertToPixel`，标签就跟着数据点 x。

### 原样搬过来的静态 DOM
KPI 卡、图例、TOP5 四表、更新时间、环形中心数字 —— 数值必须与页内数据源（本例 `SCREEN_DATA`）逐一对照，改完不能少项。模板渲染（`innerHTML +=`）的内容要改成**直接在 HTML 里展开**。

## 4. 三层验收

| 层 | 做法 | 本例实测 |
|---|---|---|
| 结构 | `document.scripts.length`、内联事件数、`performance.getEntriesByType('resource')`、`<svg>`/`<canvas>`/卡片/表行计数、`scrollWidth/scrollHeight` | scripts 0 / 事件 0 / 资源 `[]` / svg 23 / canvas 0 / KPI 8 / 行 25 / 1920x4538（原版同） |
| 文本 | 抓 12 组 DOM 文本（KPI/图例/4 表/时间）逐条比对 | 全部一致 |
| 像素 | 逐图表 `clip` 截图 + `scripts/chart_pixel_compare.py` | 平均色差 2.86/255；环图 IoU 0.87~1.00；显著差异 ≤5.22% |

- **dpr=2**：截图坐标全部 ×2，否则裁图偏半张图。
- **环图必须做沿圆角度采样**（`chart_pixel_compare.py --ring`）：自动识别墨迹中心/半径 → 逐角度取色 → 打印分段起止角。本例「费单层次」期望 0/189.6/324.6/343.9°，实测 0/190/324/344° ✅ —— 这是唯一能证明「分段没画反、颜色顺序没串」的证据，肉眼看截图看不出来。
- ⚠️ **别只信二值「非白」掩膜 IoU**：淡渐变填充两版只差 1~2 个 RGB 值（(248,250,253) vs (250,251,254)），卡在阈值上会把整条带算成差异（假阳性；本例 `chGrowth` IoU 0.653 就是这个原因，逐列颜色剖面查证后证伪）。判据换成**强墨迹掩膜（通道差 >60）+ 平均色差**。
- 裁图取样坐标算偏时，症状是「每个采样点都完全相同」——那不是真的相同，是**采到图外/白底**了。改成先在图内自动识别墨迹范围再采样。

## 5. 交付说明模板（必写「交互降级」）
- 交互降级清单：搜索框只剩外观不再过滤；全屏按钮不响应（改用浏览器 F11 / ⌃⌘F）；导航/分段按钮静态高亮；tooltip/hover、drill-down、自动刷新失效。
- 备份清单（含别人做的版本）：`index.bak-原版` / `index.bak-内联版` / `index.bak-<其他方案>`，说明各自体积与去留理由。
- 可复现资产：生成脚本 + `ref/chart-geometry.json`（改数据重跑即可）+ 新的整页参考渲染图 `ref/render_noscript_full.png`。
- `change-log.md` 补条目：需求 → 前置过程（其他会话版本被取代的实测理由）→ 改造动作 → 体积变化 → 校验等级（结构/文本/像素实测数字）→ 交互降级 → 参考渲染图。
