# 单文件交互打卡面板（check-in panel）

用于「日打卡」「打卡面板」类产物：一个 HTML 文件，双击即用，数据存在本机浏览器，用户点一下就记一笔。生成器（Python）负责把逐日数据渲染进页面。

## 页面结构

```
<div id="meta">今天 Day N / 总天数（日期 星期）</div>
<div id="stats">今日 x/y | 连续 n 天 | 累计 n/总 | 投入 x 分钟 | 状态灯</div>
<table id="tbl">
  <caption id="cap">已保存 n 天记录（本机浏览器）</caption>   <!-- 必须是 table 的第一个子元素 -->
  <thead>…</thead>
  <tbody>行 = 一天，列 = 科目/项目，单元格 = <button class="tsk" data-i="6">☐/✓</button></tbody>
</table>
<按钮：回到今天 / 今天没安排 → 看昨天>
```

- `<caption>` 放 `<thead>` 之后会被浏览器丢弃 → JS 取 `#cap` 得 null。
- 今日高亮写在 `#meta` 文案里，**不要靠给行加 class** 去做验证断言（行 class 是空的，断言会假失败）。

## 数据与存储

- 逐日数据用 JS 常量数组，日期用短键：`{d:"10-5", n:1, w:"周一", stage:"阶段1", items:[…]}`。
- `localStorage` 用带版本的命名空间 key（如 `mba-eng-checkin-v1`），值形如 `{"10-5":{s:[true,false,false], note:""}}`。
- 每个面板**各自一个 key**：科目独立面板与总面板互不影响，这也是「科目分开」的落地方式。

## 逻辑要点

- 今日判定：`curIdx = findToday()`，把 `todayKey()`（`"10-5"`，无前导零）与 `DATA[i].d` 直接比。不要用 `toISOString().slice(5,10)`（会给 `"10-05"`），否则永远匹配不上、定位到第 0 天或崩掉。
- 非今日行也能点（补打卡），但默认滚动/高亮到今日。
- **分母按当天实际安排算**：当天没排的项目该格显示「—」且不可点、不计入分母（0/3 而非 0/4）。否则用户永远打不满，连续天数永远是 0。
- 统计派生自记录：今日完成数、连续天数（从今天往前数，遇到未完成即停）、累计完成天数、投入分钟、状态灯（未开始/半卡/完成）。
- 笔记输入框 `oninput` 直接落 `localStorage`，避免「忘了点保存」。

## 验证（browser_exec，必须做）

```python
goto_url("file:///绝对路径/面板.html"); wait_for_load()
js("localStorage.clear()")
# 重新打开后再断言
js("document.querySelectorAll('#tbl tbody tr').length")      # = 天数
js("document.getElementById('cap').innerText")                # caption 生效
js("document.getElementById('stats').innerText.replace(/\\n/g,' | ')")
# 点一下第一个可选格子 → stats 里今日应 +1、连续天数=1
js("document.querySelector('.tsk[data-i=\"0\"]').click()")
js("document.getElementById('stats').innerText")
```

- 断言「打开即定位到今天」（`meta` 里出现 Day N 与今天日期），这是最容易坏的一处。
- 刷新一次确认持久化生效。
- **收尾必须 `localStorage.clear()` 并重开确认归零**，否则交付后用户看到的是测试数据（「今日 1/3」）。
- 配套的另一半产物是**可打印的 MD 台账**（表格 + 周汇总 + 里程碑），面板给「点」，台账给「打印打勾」。
