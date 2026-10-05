---
name: html-single-file-bundling
description: "Use when 把 HTML 依赖内联成单文件、或把 JS 渲染去 JS 化成纯 HTML+CSS/SVG、打开即用。先静态改写，再用 file:// 空目录实测零外部加载。"
---

# HTML 单文件化 与 去 JS 化（内联依赖 / 静态渲染 → 打开即用）

用户说「把依赖和 CSS 都放进 index.html，我只要打开这个文件」时的做法。
产出必须**能在 `file://` 下、脱离原目录、单独拷到任何地方都能跑**。

同一类需求的另一面：用户说「**里面的 JS 渲染直接改成 HTML+CSS，不要出现 JS 代码**」→ 见「## 第四步（另一种需求）：去 JS 化」。两者常叠加（先内联、再去 JS）。

## 何时用
- 「把依赖/CSS 内联进一个 HTML」「我只需要打开这个文件即可」
- 要把仪表盘 / 原型 / 报表 HTML **发给别人**（微信、邮件、U 盘），对方不会起本地服务器
- 别人给的 HTML 目录里带 `assets/`、`data/`、`ref/`，想确认到底哪些是真依赖
- 「把里面的 JS 渲染改成 HTML+CSS」「不要出现 JS 代码」「图表不要用 JS 画」→ 去 JS 化（见第四步）
- 要把仪表盘发给**不允许跑脚本**的环境（内网汇报机、只读预览、邮件附件）

## 第一步：先盘点，别急着改（关键）

**不要假设「有哪些依赖」——实测经常比预想少得多。** 本用户的数据驾驶舱首页：声称有 CSS/数据/JS 三类依赖，实测**只有 1 个真外部依赖**（`assets/echarts.min.js`），CSS 早就内联在 `<style>` 里（13341 字符）、数据早就内联在 `const SCREEN_DATA = {...}`、全文 **0 处** fetch/XHR。

要查的清单：

| 类型 | 查什么 | 处理 |
|---|---|---|
| 样式 | `<link rel=stylesheet href>`、CSS 内 `@import`、`url(...)` | 内联成 `<style>`；本地 `url()` 资源转 data URI |
| 脚本 | `<script src>` | 内联成 `<script>`（本项目唯一真依赖就是它） |
| 数据 | `fetch(` / `XMLHttpRequest` / `import(...)` / `new Worker` | ⚠️ **`file://` 下会被 CORS 拦**，必须改成内联字面量或 data URI |
| 图片字体 | `<img src>`、`@font-face src`、`<iframe src>` | 本地文件转 data URI；远程字体要评估（能删则删） |
| 其它 | 注释里提到的文件名 | 可能只是注释，**不是依赖**（本项目 `data/sample-data.json` 就只出现在注释里） |

用 `scripts/inline_html.py` 一次跑完盘点 + 内联：
```bash
PYTHONPATH= python3 <skill_dir>/scripts/inline_html.py ~/Downloads/首页/index.html
```
它只做静态改写，会备份原文件、并把「仍需要联网的 CDN 依赖」单独列出来不自动下载。

## 第二步：内联本身（几个必须注意的点）

- **`</script` 必须转义**：HTML 解析器只要遇到字面 `</script` 就结束脚本块。JS 里安全写法是 `<\/script`（在字符串/正则/注释里语义完全相同）。本项目 ECharts 内 0 处，仍做防御性替换。
- **不只是 script**：`<link>` 换成 `<style>`、图片/字体换 data URI。
- **体量不要怕**：ECharts 全量 1.03 MB → 单文件 1.09 MB。桌面双击打开毫无压力，别为了体积去做 tree-shaking 或 CDN 化（CDN 恰恰破坏了「离线单文件」这个需求）。
- **先备份原文件**：`index.bak-<日期>.html`，原目录的 `assets/` 保持不动。
- **告知可清理项**：内联后 `assets/`、`data/`、`ref/` 运行时不再读取，但**不要擅自删**（改版还要用），只在结论里说明「已不再被运行时读取，可按需删除」。
- **项目自带 `change-log.md` 就补一条**：这类交付目录往往有自己的变更记录，按它原有格式追加（依赖盘点 → 动作 → 结果 → 校验等级 → 备份），比另写新文件更贴合用户习惯。

## 第三步 ⭐ 用 `file://` 空目录实测（这一步才是交付标准）

「改完了」不等于「能跑」。**把单文件复制到一个空目录再打开**，周围什么都没有，跑不起来就露馅。最强证据是浏览器自己汇报的**资源加载列表为空**。

```python
# browser_exec：注意先注入错误捕获再导航，才能抓到加载期报错
new_tab("about:blank"); wait_for_load()
cdp('Page.enable'); cdp('Runtime.enable')
cdp('Page.addScriptToEvaluateOnNewDocument', source="""
  window.__errs = [];
  window.addEventListener('error', e => window.__errs.push(String(e.message || e)), true);
  window.addEventListener('unhandledrejection', e => window.__errs.push('unhandledrejection: ' + e.reason));
""")
goto_url("file:///tmp/single_test/index.html"); wait_for_load()
print(js("""(() => ({
  url: location.href,
  errors: window.__errs,
  externalResources: performance.getEntriesByType('resource').map(r => r.name),
  canvases: document.querySelectorAll('canvas').length,
  libVersion: (typeof echarts !== 'undefined') ? echarts.version : null,
  pageWidth: document.documentElement.scrollWidth,
  pageHeight: document.documentElement.scrollHeight
}))()"""))
```

判定标准（照抄给用户，别只说「应该能开」）：

| 字段 | 期望 | 含义 |
|---|---|---|
| `externalResources` | **`[]`** | ⭐ 关键证据：除这个 HTML 外没再请求任何东西 = 真单文件 |
| `errors` | `[]` | 无加载期/运行期报错 |
| `libVersion` / 框架对象 | 有值 | 内联的库真的解析并执行了 |
| `canvases` / 渲染节点数 | 与升级前一致 | **图表/动态内容真的画出来了**（只检查加载成功会漏掉渲染崩溃） |
| `pageWidth` | 与设计宽度一致（如 1920） | 没塌版 |

再补一张全页截图做视觉确认（`cdp('Page.captureScreenshot', captureBeyondViewport=True)`），和用户原有的参考渲染图对一眼。
**建议同时 md5 比对**「交付文件」与「实测副本」，证明测的就是交付物。

## 第四步（另一种需求）：去 JS 化 —— 图表渲染改成静态 HTML+CSS/SVG

口径（按用户原话执行，别自己放宽）：**一个 `<script>` 都不留、不留内联 `on*` 事件、不留 `javascript:` 协议**。图表库（ECharts / Chart.js / Highcharts）本身也是 JS → 必须换成**内联 `<svg>`**（SVG 是 HTML 标签）或纯 CSS（环图可用 `conic-gradient`）。完整配方与代码：`references/dejs-chart-static-conversion.md`。

**核心原则：不要凭截图描图，要从活的库实例回读真实几何。** 先保留一份**还带 JS 的原版**用浏览器打开，把几何抄出来（ECharts：`getOption()` 拿 series 内外径/center/startAngle/配色/`borderWidth`、`xAxis.axis.getTicksCoords()` 拿刻度像素位、`convertToPixel()` 拿数据点像素坐标、`grid.coordinateSystem.getRect()` 拿网格矩形）→ 存 JSON → **离线 Python 算坐标生成 `<svg>`**（生成过程不写任何 JS）。这样折线每个点、环图每个分界角都落在原版同一像素上，而不是「看着差不多」。

### 三个必踩的坐标/绘制坑
1. **`axis.dataToCoord()` 是网格相对坐标（0..gridW），`convertToPixel()` 是画布绝对坐标（gridX..gridX+gridW）** —— 混用会让轴标签整体偏移一个 `grid.x`（本例 44px；症状是横轴标签红蓝双影、最左标签被裁）。定位轴标签要用**数据点自身 x**。
2. **饼图 `itemStyle.borderWidth` 会让可见扇区整体内缩**（本例 2px → 内外径各缩 1px）：要还原就得 `r_out - bw/2` / `r_in + bw/2`，否则环比原版粗一圈。
3. **有底色环的仪表环不要切分段间隙**：给「底色环 + 前景弧」型图加 gap，会在 12 点位置露一条浅色缝（本例 750/250 环露 2° 缝）。判据：`len(data)==2 && data[1][0] > 0` → `gap = 0`。

### 静态化后的验收（三层，缺一层就会被看出问题）
| 层 | 做什么 | 判据 |
|---|---|---|
| 结构 | 数 `<script>` / 内联事件 / `externalResources` / `<svg>` / `<canvas>` / KPI 卡 / 表行 / 整页宽高 | `scripts=0`、事件 0、资源 `[]`、`canvas=0`、宽高与原版**完全相同** |
| 文本 | 抓 12 组 DOM 文本（KPI/图例/表格/时间）逐条比对 | 逐条完全一致 |
| 像素 | 逐图表 `clip` 截图两版对比（平均色差 / 强墨迹差异占比 / 墨迹 IoU） | 平均色差 ≤3/255、显著差异 ≤5%；环图另做**沿圆角度采样**验证分段方向与分界角 |

- 截图是 **dpr=2**，所有像素坐标 ×2。
- ⚠️ **别只信二值「非白」掩膜的 IoU**：淡渐变填充处两版只差 1~2 个 RGB 值（(248,250,253) vs (250,251,254)），正好卡在阈值上，整条带会被算成差异 → 假阳性（本例 `chGrowth` IoU 0.653 就是这么来的）。改用**强墨迹掩膜（通道差 >60）+ 平均色差**判定。
- 环图中径公式：`r_mid = r_out * (f_in + f_out) / (2 * f_out)`（漏掉 `/f_out` 就采到环空心，采样全是白）。
- 现成脚本：`scripts/chart_pixel_compare.py`（配对裁图逐图算指标；`--ring` 模式做环形角度扫描）。

### 交付说明必须写清「交互降级」
去 JS 必然掉交互，不写清就是坑：搜索框只留外观不再过滤、全屏按钮不响应（改用浏览器 F11 / ⌃⌘F）、导航/分段按钮只是静态高亮；同类页面常见还有 tooltip/hover、drill-down、自动刷新。

## 坑

1. **`file://` 下 `fetch`/XHR 读本地 JSON 一定失败**（CORS/协议限制）——遇到 `data/*.json` 被运行时读取的页面，唯一正解是把数据内联成 JS 字面量，不是让用户「起个 http 服务」。
2. **别把「代码里有 url( 字样」当外部依赖**：内联后仍可能剩几处（在库源码内部，如图片 base64、SVG 片段），以 `externalResources` 实测为准。
3. **升级没做回归**：只看「库加载成功」不够，必须数图表/canvas/卡片数并与原版一致。
4. **改动记录别丢**：单文件化会让目录里一半文件变成死文件，下一轮接手的人不知道，务必落 `change-log.md` 或交付说明。
5. **目标文件可能已被另一个会话/窗口改过**（本用户会同时开多个会话做同一件事）：动手前先 `ls -la` 看时间戳和 `index.bak-*`；发现来历不明的新版本/新备份时，**先 `cp -p` 备份对方那版 → 在同一环境实测两版对比 → 最后才安装自己那版**，绝不静默覆盖。本例另一会话的 `conic-gradient` 版环图半径与分段整体偏移、整页高度 4527 与原版 4538 差 11px → 结论「保留文件但不采用」。
6. **先入为主的误判要当场收回**：曾疑心对方版本改了标题（多了 🐴 emoji），终验时查明 emoji 本来就在原版里 → 在汇报里明确更正，别让悬着的怀疑留在结论里。
7. **生成脚本要从备份候选里挑源文件**：改版途中主 `index.html` 会被别的会话覆盖（本例就被换成 80137 bytes 的版本），生成器要按优先级尝试 `index.bak-*` 候选源，而不是硬编码 `index.html`。
8. **汇报里的 SVG/节点数要用 DOM 计数，别用 `grep -c`**：`grep -c '<svg'` 是按**行**计数会少报（本例 16 vs 实际 23），最终数字一律以浏览器 `document.querySelectorAll('svg').length` 为准。

## 支持文件
- `scripts/inline_html.py` — 盘点 + 内联 + 备份 + 残留外部依赖报告（单文件 CLI，可直接跑）
- `scripts/chart_pixel_compare.py` — 两版图表裁图逐图像素等价比对（平均色差 / 强墨迹差异占比 / 墨迹 IoU；`--ring` 做环形角度扫描，验证分段方向）
- `references/dejs-chart-static-conversion.md` — 去 JS 化完整配方：ECharts 几何回读代码、环图/平滑折线 SVG 生成要点、三层验收与实测数字、交付说明模板
