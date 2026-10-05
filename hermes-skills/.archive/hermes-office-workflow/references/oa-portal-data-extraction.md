# SmarDaten OA 系统数据提取

## 待审批流程查询

查询 OA 中当前用户的待审批流程（区别于报销数据提取）。

### 导航路径

```
登录 → 首页(SuperOA智能助手)
  → 左侧导航"要我办" → 进入"要我办"工作台
  → 找到"流程"区域 → 点击右上角"更多>"按钮
  → 进入"事件流工作台"页面（URL中appid变为8864182915840980）
  → 左侧菜单选择"待我处理"
  → 显示待审批列表（表格形式）
```

### 注意事项

- **首页统计 ≠ 实际列表** — 首页顶部显示"待我审批：N"，但实际在"待我处理"标签下可能查到的条数不一致。差异原因不明，可能是不同状态/模块的汇总。
- **默认标签为空** — 进入事件流工作台后默认显示"事件列表"标签，显示"暂无数据"。需要手动点击"待我处理"标签。
- **React 渲染延迟** — 点击"要我办"后需要等待 2-3 秒让 React 渲染，否则页面显示为空白。

### 完整查询示例

参见 `references/oa-approval-query-20260528.md`（含导航细节、React渲染坑点、用户发起的进行中流程）。

## 从扫描件PDF→Word转换的用户沟通模式

当用 macOS Vision OCR + python-docx 生成 Word 文档后，用户反馈"格式和PDF里的不一致"，需要：

1. 先用 Swift 提取 OCR 结果中每个文本片段的**精确坐标**（x, y, width, height）
2. 根据坐标推断列边界（同Y范围 → 同行；同X范围 → 同列）
3. 用 `Cm()` 按坐标比例设置列宽
4. 重建表格的行列合并逻辑

详见 `ocr-and-documents` 技能的 `references/sharp-scanner-pdf-to-word.md`。

## 多页 OA 报销数据批量提取（SmarDaten 员工报销模块）

### 页面结构

| 模块 | 入口路径 | 总条数 | 总页数 | 是否增长 |
|------|---------|:------:|:------:|:--------:|
| 出差报销 | 费用报销 → 员工报销 → [出差报销]tab | 72条 | 8页 | ✅ 有增长 |
| 个人报销 | 费用报销 → 员工报销 → [个人报销]tab | 5条 | 1页 | 稳定 |
| 招待报销申请 | 差旅报销 → 招待报销 → 招待报销申请 | 26条 | 3页 | 有增长 |

**⚠️ 重要：数据量不是静态的。** 随着时间推移，出差报销等模块的记录会不断增长。之前的记录（68条/7页）现在已经变成72条/8页。抓取前不要依赖历史记录中的条数，一定要先查当前总条数。

### 列索引映射

**出差报销 & 个人报销（列索引从0开始）：**
- c[0] = 报销编码， c[1] = 出差编码(个人报销无此列)
- c[2] = 报销类型， c[3] = 申请人(部分为空)
- c[4] = 申请日期， c[5] = 业务状态
- c[6] = 经办人， c[11] = 费用合计(个人报销)
- c[12] = 费用合计(出差报销)

**招待报销申请：**
- c[0] = 报销编码， c[1] = 申请人
- c[3] = 申请日期， c[4] = 经办人
c[5] = 业务状态，c[12] = 费用合计

#### ⚠️ 业务状态过滤（用户多次纠正确认）

提取待报销数据时，需要用户确认业务状态含义，不可自行推断：

| 业务状态 | 用户确认的含义 | 算待报销？ |
|---------|--------------|:---------:|
| 出纳付款 | 到了出纳张露露，钱未付 | ✅ |
| 经办会计审批 | 在会计张琪处 | ✅ |
| 支付确认 | 到了杨志，已付款 | ❌ |
| 结束/异常结束 | 流程已终了 | ❌ |

> 用户明确纠正过：支付确认=已付（已到杨志），出纳付款=未付（还没实际打款）。如果用户说"出纳付款"有问题，记住它是不算已付的。

#### 翻页的两种方法

### 逐页提取流程

```python
# Step 1: 确认总条数和总页数
browser_console(expression="document.body.innerText.match(/共\\s*\\d+\\s*[条笔]/)")
browser_console(expression="document.querySelectorAll('.ant-pagination-item').length")

# Step 2-N: 逐页提取
# 每页先提取数据，再翻页，等2秒渲染
browser_console(expression="(function(){ ... return JSON.stringify(data); })()")
browser_console(expression="document.querySelectorAll('.ant-pagination-item').forEach(el => { if(el.textContent.trim() === '2') el.click(); }); 'ok'")
sleep 2
# 重复直到最后一页
```

### 批量翻页（一次性提取所有页，推荐）

对于分页数较多的场景（如出差报销8页），手动逐页翻页效率低。可以用 `async function` 在浏览器中一次性完成所有翻页和数据提取：

```javascript
browser_console(expression="(async function(){
  function extractData() {
    // 从当前table提取所有行
    let data = [];
    document.querySelectorAll('table tbody tr').forEach(r => {
      let c = r.querySelectorAll('td');
      if(c.length > 12 && c[0].textContent.trim()) {
        data.push({
          code: c[0].textContent.trim(),
          status: c[5].textContent.trim(),
          amount: c[12].textContent.trim()
        });
      }
    });
    return data;
  }
  
  function clickPage(n) {
    let link = document.querySelector('.ant-pagination-item-' + n + ' a');
    if(link) { link.click(); return true; }
    return false;
  }
  
  let allData = [];
  for(let p = 1; p <= totalPages; p++) {
    if(p > 1) {
      clickPage(p);
      await new Promise(r => setTimeout(r, 1500));
    }
    let pageData = extractData();
    allData.push({page: p, count: pageData.length, data: pageData});
  }
  return JSON.stringify(allData);
})()")
```

**⚠️ 已知问题：批量翻页后的数据去重**
- 某些情况下（如切换到其他tab再切回来），翻页时的table可能混入其他标签页的数据
- 翻页完成后用 `browser_console` 检查最后一页的页码，确认确实是最后一页而不只是当前可见的页码窗口
- 建议翻页完成后返回第1页验证：`document.querySelector('.ant-pagination-item-1 a').click()`

### ⚠️ 列索引陷阱：标签页间数据串扰

当你在 出差报销 tab 中提取数据时，可能需要按 `c[2]`（报销类型）过滤：

```javascript
c[2]?.innerText?.trim() === '出差报销'  // 只取出差报销行
```

因为 ant-design tab panel 在切换时可能渲染混入其他 tab 的行。**如果发现数据中有明显不属于当前标签页的类型，加上这个过滤条件。**

**员工报销 → 招待报销(旧) tab** — 此为死入口，该标签页无数据，无需尝试提取。

### 待报销 vs 已结束判断

- 业务状态 != '结束' 且 != '已完成' → 待报销
- 业务状态 == '结束' → 已结束，排除
- 待报销状态值：经办会计审批、出纳付款、直接主管审批

### SmarDaten 付款状态链（特定于杨嘉阳所在公司，2026-08 会话与用户确认）

OA 报销审批有固定流程链，不同阶段代表不同付款进度：

| 业务状态 | 经办人 | 含义 | 是否已付款 |
|---------|--------|------|:----------:|
| 经办会计审批 | 张琪 | 会计审核中，未到付款环节 | ❌ 待报销 |
| 直接主管审批 | (部门主管) | 部门审批中，未到财务 | ❌ 待报销 |
| 出纳付款 | 张露露 | 已到出纳环节，钱未付 | ❌ 待报销 |
| 支付确认 | 杨志（不出现在列表列中） | 已到杨志，钱已付 | ✅ 已付款 |

**关键规则（用户明确告知）：** "走到杨志名下的不算，是已经报过了" = 业务状态=支付确认。⚠️ 杨志**不出现**在"我发起的"列表的经办人/审批人列中（经办人只显示张露露/张琪；详情页审批记录也只有 提交→直接主管(方亮亮)→权签人(陈峥峥)→经办会计(张琪)），只能通过业务状态=支付确认识别，**不要按人名搜索**。

**对数据提取的影响：**
- "我发起的"列表中，业务状态=支付确认的处理中记录 → 已付款，不计入待报销金额
- 业务状态=出纳付款 / 经办会计审批 的处理中记录 → 算待报销
- 2026-08-03 实测：处理中 31 条 = 出纳付款 25 + 经办会计审批 4 + 支付确认 2 → 待报销 29 条

### ⚠️ 重要教训：汇总前必须实时刷新确认

**不要依赖缓存数据。** OA 数据是实时变化的（新审批、新提报、状态变更），跨时段汇总时必须：
1. **每进入一个模块，先点击"查询"按钮刷新**（`browser_click` 点击查询按钮）
2. **不要直接用前一页抓取结果做最终汇总** — 尤其是当你在多个模块间切换时
3. 用户说"没有那么多"或"数据不对"时，**立即回到 OA 重新抓取该模块的最新数据**，而不是在内存中筛选
4. 个人报销数据变化快（新提报后表项变动），每次进入该 tab 都要重新提取

**典型错误场景：** 先抓了出差报销和个人报销的数据，中间经历了 OA 超时重新登录，然后直接跳到招待报销申请，最后拿缓存的个人报销数据做汇总 → 用户指出条数不对。

**正确做法：** 在输出最终汇总前，对所有模块做一次**实时确认** — 至少检查一下是否有新条目或状态变更。

### ⚠️ Ant Design 分页器的中间省略号陷阱

当当前页码远离目标页时，`ant-pagination-item` DOM 只渲染了**当前可见的页码窗口**，中间的页被 `...` 省略号替代，**没有对应的 DOM 元素**。

**症状：** 想点击第3页，但 `document.querySelectorAll('.ant-pagination-item')` 只返回 `["1", "4", "5", "6", "7", "8"]` — 第3页不在DOM中。

**原因：** React 的 Ant Design 分页器根据当前页码动态渲染可见页码范围。当你在第7页时，它只渲染 {1, 4, 5, 6, 7, 8} 这6个DOM。中间的 {2, 3} 被一个不可点击的省略号替代。

**解决方案（三步法）：**

```javascript
// Step 1: 先看当前有哪些页码在DOM中
JSON.stringify(Array.from(document.querySelectorAll('.ant-pagination-item')).map(function(el) {
  return { text: el.textContent.trim(), active: el.classList.contains('ant-pagination-item-active') };
}))
// → 输出 e.g. [{"text":"1","active":false},{"text":"4","active":false},{"text":"5","active":false},"text":"6","active":false},{"text":"7","active":false},{"text":"8","active":true}]

// Step 2: 先点击一个可见的较远页码（如"1"），让React重新渲染出完整的页码窗口
document.querySelectorAll('.ant-pagination-item')[0].click();
await new Promise(r => setTimeout(r, 1500));

// Step 3: 现在DOM中有"1 2 3 4 5 ... 8"了，再点目标页
document.querySelectorAll('.ant-pagination-item').forEach(el => {
  if(el.textContent.trim() === '3') el.click();
});
```

**更可靠的方案：直接用蚂蚁分页器的特定类名点击**

如果用文本匹配太麻烦，可以通过 Ant Design 的分页器 `a` 标签的特定类名直接点击（类名 `ant-pagination-item-{n}`）：

```javascript
// 直接用页码数点击，不需要等DOM重新渲染
document.querySelector('.ant-pagination-item-2 a')?.click();
document.querySelector('.ant-pagination-item-3 a')?.click();
```

但这种方式的限制是当页码超出了当前渲染窗口时，该类名的 DOM 元素同样不存在。**最佳实践还是先用可见页码"1"重置窗口，然后再翻。**

**常见翻页失效场景及解决：**

| 场景 | 现象 | 原因 | 解决 |
|------|------|------|------|
| 远距离翻页 | 页码不存在DOM中 | 中间省略号 | 先点可见的远端(如"1")重置窗口 |
| 快速连续翻页 | 第二个翻页点击无效 | React还没渲染新页 | 每次翻页后 `sleep 2` |
| 标签页未切换 | 点击页码后页面不变 | 错误的tab/panel | 先确认active tab |
| 分页器在多个ant-table中 | 点到错误的table的分页器 | tab panel混渲染 | 选择正确的table容器 |

### ⚠️ 多步翻页时 pagination DOM 完全消失

在"我发起的"页面（差旅报销应用），用手动 `browser_click` 逐页点击页码，**连续点击翻页 3-4 次后**，React 可能卸载整个 `.ant-pagination` 组件。

**症状：**
- `document.querySelector('.ant-pagination')` 返回 null
- 页面内容不更新，无法再进行任何翻页交互
- 页面主体内容（表格中当前页数据）仍然显示
- 页面没有报错、没有白屏

**原因：** Ant Design 分页器在频繁的 `browser_click` + browser 无头操作下可能触发 React 卸载/重渲染 bug。这不是正常的页面行为——不同 tab 间切换再回到该 tab 时，分页器重新渲染，恢复正常。

**解决方案（按优先顺序）：**

**方案 A：一次性 async function 翻页（推荐）**
用一个 `browser_console` 调用执行完整的 `async function`，在 JS 作用域内完成所有翻页和数据提取，避免多步 browser 命令导致的 DOM 状态丢失。函数体内用 `setTimeout` + `await` 控制翻页节奏。

**方案 B：跳转到另一个 tab 再跳回来**
点击另一个标签页（如"出差申请"）后再点回"我发起的"，React 会重新渲染，分页器恢复。但这只适合恢复，如果再次手动翻页仍可能再次消失。

**方案 C：用 delegate_task 子代理（备选）**
见本文件「delegate_task 子代理的浏览器操作 → 例外」章节。

**方案 D：刷新重来**
`browser_navigate` 回登录页 → 重新登录 → 进入目标页面 → 用方案 A 一次过完成。

### 翻页时的 let/const 陷阱

`browser_console` 的每次调用是独立 eval，但 `const`/`let` 在同一页面作用域下会重复声明报错：\n- ❌ `const items = document.querySelectorAll(...)` — 第二次调用报 SyntaxError\n- ✅ `document.querySelectorAll(...).forEach(...)` — 直接操作，不用变量\n- ✅ `(function(){ ... })()` — 用 IIFE 包裹可以避免变量冲突

### 新版 OA UI：登录后进入 SuperOA 智能助手

SmarDaten OA 在 2026 年更新了 UI，登录后默认进入 **SuperOA 智能助手**（AI 对话界面），而不是传统的工作台首页。这个页面左侧有导航菜单（差旅报销、员工报销等），但点击部分菜单项可能报错（"页面出错!"）。

**快速进入报销模块的方法：**
1. 登录 OA（输入凭据 → 点击登录按钮 → 等待 SPA 加载完成）
2. 用 `browser_navigate` 直接跳转到目标报销模块的 URL
3. 系统会自动加载该模块的左侧菜单 + 表格数据

**已知可用的直接 URL：**
- 招待报销申请：`https://oa.smardaten.com/applicationview/content/view?appid=47d3ea2e-5a30-cebc-2133-665535cd8e66&type=view&menuId=3046477257476770%233`

**注意：** 不要试图通过新版 AI 助手的"要我办/我要办/要我知"菜单来导航——这些入口可能触发 qiankun 微前端子应用加载失败，导致页面空白或报错。直接导航到目标 app URL 更可靠。

### 会话超时处理

OA 页面长时间闲置后（尤其是跨浏览器 session），页面可能变成空白，所有交互失效。

**判断方法：**
- `browser_snapshot` 显示 "(empty page)" 或只有 "generic [ref=e1] clickable [onclick]"
- `browser_console` 显示窗口URL无变化，但页面内容为空

**恢复步骤：**
1. 点击空白页面上唯一的 clickable 元素（通常是登录页的"用户登录"按钮）
2. 等待出现登录表单（用户名/密码输入框）
3. 重新输入凭据
4. 点击登录按钮
5. 重新导航到目标页面

**注意：** 不要尝试重新 navigate 到目标 URL 绕过登录（会直接跳到空白页）。必须走完整的登录流程。

### 无验证码的登录 URL（特定于该 OA 实例）

某些 SmarDaten OA 登录 URL 可能**不需要图形验证码**。例如实测 `https://oa.smardaten.com/application/login/3415237453165568` 就没有验证码输入框，直接输账号密码即可登录。

**策略：** 如果登录后发现登录页有验证码，尝试用 `browser_navigate` 重新访问该 URL（页面会重新渲染加载），可能落到一个无验证码的登录实例上。注意重新 navigate 后验证码图片也会刷新（如果新实例有验证码的话），但至少给了绕过验证码的机会。

### 密码过期处理

登录时可能出现弹窗提示"密码需要更新"，说明 OA 系统要求修改密码。这不是 session 超时，而是密码策略强制更新。

**判断方法：**
- 输入正确账号密码并点击"登录"后，页面不跳转
- `browser_snapshot(full=true)` 显示弹窗 dialog，内容包含"密码需要更新"、"您的密码已过期，需要修改新密码才能登录"等文字
- 弹窗中有"修改密码"按钮

**处理步骤：**
1. 点击弹窗中的"修改密码"按钮（@e3 或类似 ref）
2. 页面切换到密码更新表单，包含三个字段：
   - 原密码（输入旧密码）
   - 新密码（输入新密码）
   - 确认密码（再次输入新密码）
3. 填写所有字段后点击"更新"按钮
4. 更新成功后页面回到登录页，用新密码重新登录
5. 将新密码**同时更新到 memory**（用 memory 工具记录新密码，因为旧密码不再有效）

**注意事项：**
- 新旧密码不能相同（OA 系统的密码历史约束）
- 新密码需要符合系统的密码复杂度要求（至少包含一个大写字母、一个小写字母，8位以上）
- **⚠️ 系统不会在输入时提前提示密码策略** — 提交"更新"按钮后，如果不符合规则，不会自动聚焦到出错字段，而是在页面正中间弹出一个 **非模态提示条**（image "close-circle" + StaticText "密码必须包含大写字母！"等）。此时输入框内容仍然保留，可以直接在原有输入上修改然后再次提交。
- 如果用户只改了字母大小写而未引入新字符，新旧密码可能被判定为"相同"，也会被拒绝
- 密码更新后必须告知用户新密码是什么，让用户也在手机/电脑上更新保存

#最新确认的列索引（2026-07 会话）：

**出差报销（员工报销 → [出差报销]tab）：**
- c[0] = 报销编码，c[1] = 出差编码
- c[2] = 报销类型（用于过滤，避免混入个人报销数据）
- c[4] = 申请日期，c[5] = 业务状态（经办会计审批/出纳付款/结束等）
- c[6] = 经办人，c[12] = 费用合计

**注意：** 出差报销 tab 中可能混入个人报销的行，提取时务必按 c[2]（报销类型）过滤：`c[2]?.innerText?.trim() === '出差报销'`

**个人报销（员工报销 → [个人报销]tab）：**
- c[0] = 报销编码，c[1] = 报销类型
- c[2] = 申请人（部分为空），c[3] = 申请日期
- c[4] = 业务状态，c[5] = 经办人
- 费用合计在 c[11]（❗与出差报销不同）
- 注意：个人报销第1列（c[0]）就是报销编码，没有出差编码列

**员工报销 → 招待报销(旧) tab** — 死入口，该标签页无数据。

---

## "我发起的"事件列表（差旅报销应用内）

### 导航路径

首页 → 我要办（左侧菜单）→ 应用列表找到"差旅报销" → 左侧菜单 → "我发起的"

此表格列出用户**历史上所有发起的出差/报销事件**（包括出差申请、招待报销、费用报销），不限于"报销"类型。

### 数据量

截至2026-07-27：**208 条记录，共 21 页**（每页 10 条）。2026-08-03 实测已增长到 **213 条 / 22 页**。数据持续增长，抓取前先确认当前总量，不要依赖历史条数。

### 列索引映射

| 索引 | 列名 | 内容示例 | 说明 |
|:----:|------|---------|------|
| c[0] | 事件类型 | "费用报销"、"出差申请"、"招待报销" | 区分事件大类 |
| c[1] | 事件名称 | "杨嘉阳 1252.20 项目 20260723516" | 格式：创建人 金额 类型/项目 编码 |
| c[2] | 摘要 | "出差至北京" | 事件摘要文本 |
| c[3] | 创建时间 | "2026-07-23 11:30" | |
| c[4] | 更新时间 | "2026-07-24 14:00" | |
| c[5] | 创建人 | "杨嘉阳" | |
| c[6] | 经办人 | "张琪" | 当前处理人 |
| c[7] | 流程状态 | "处理中" / "结束" | 整体流程是否完结 |
| c[8] | 业务状态 | "经办会计审批"、"出纳付款"、"等待主管审批"、「已结束」 | 流程中的当前位置 |

### 排序规则

⚠️ **默认创建时间升序**（第1页=最旧数据，最后页=最新数据）。这与直觉相反！
- 第1页：2024年已结束的旧记录（如出差申请、招待申请）
- 第21页：2026年最新记录（处理中的报销）
- **查待处理记录时，直接从最后一页往前翻**

### 从事件名称提取金额

事件名称 `c[1]` 包含金额信息，格式统一：`"创建人 金额 类型 编码"`
- `"杨嘉阳 1252.20 项目 20260723516"` → 金额 = 1252.20
- `"杨嘉阳 237.81 出差报销 202607024719"` → 金额 = 237.81

提取方式：
```javascript
c[1].match(/(\\d+\\.\\d{2})/)?.[1]  // 匹配金额数字
```

### 大规模自动翻页模式（window 累积器 + 分批取回 + CSV 下载）

2026-08-03 实测可用于 22 页 / 213 条的"我发起的"列表全量抓取。**不要**用 `return JSON.stringify(allData)` 一次性返回——console 输出截断（约10KB），200+条会被切掉。

**Step 1：一次性 async 循环翻页，累积到 `window.__allData`**（window 属性跨多次 browser_console 调用持久，且赋值方式避免 let/const 重复声明报错）：

```javascript
browser_console(expression="(async () => {
  window.__allData = window.__allData || [];
  const extract = () => {
    const data = [];
    document.querySelectorAll('.ant-table-tbody tr').forEach(tr => {
      const cells = tr.querySelectorAll('td');
      if (cells.length >= 10 && cells[0].textContent.trim()) {
        data.push(Array.from(cells).map(c => c.textContent.trim()));
      }
    });
    return data;
  };
  const clickNext = () => {
    const next = document.querySelector('.ant-pagination-next');
    if (!next || next.classList.contains('ant-pagination-disabled')) return false;
    next.click(); return true;
  };
  let pages = 0;
  while (clickNext()) {
    await new Promise(r => setTimeout(r, 1500));   // 等 React 渲染新页
    const d = extract();
    if (!d.length) break;                          // 防死循环：数据不再变化即停
    window.__allData = window.__allData.concat(d);
    pages++;
  }
  return 'pages: ' + pages + ' total: ' + window.__allData.length;
})()")
```

每批跑 4-6 页（约 40-60 条）比较稳妥；跑完一批再跑下一批，最后一批返回 `noMore: true` 时全部抓完。

**Step 2：分批取回**（每次 `slice` 约 70 条，避免输出截断）：
```javascript
(() => JSON.stringify(window.__allData.slice(0, 71)))()
(() => JSON.stringify(window.__allData.slice(71, 142)))()
(() => JSON.stringify(window.__allData.slice(142)))()
```

**Step 3（推荐）：直接下载 CSV 到本地，无损失分析：**
```javascript
browser_console(expression="(async () => {
  const header = ['事件类型','事件名称','摘要','创建时间','更新时间','创建人','经办人','流程状态','业务状态'];
  const rows = [header].concat(window.__allData);
  const csv = rows.map(r => r.map(c => '\"' + String(c).replace(/\"/g, '\"\"') + '\"').join(',')).join('\\n');
  const blob = new Blob(['\\ufeff' + csv], {type: 'text/csv;charset=utf-8'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'reimbursements_all.csv';
  document.body.appendChild(a); a.click(); document.body.removeChild(a);
  URL.revokeObjectURL(url);
  return 'csv downloaded, rows: ' + rows.length;
})()")
```
落地到 `~/Downloads/reimbursements_all.csv`（带 BOM，Excel 打开不乱码），用 Python csv 模块分析。

**关键细节：**
- 翻页后验证数据是否真的变了：对比**第二行**的首个非空单元格（第一行可能是空填充行，对比第一行会误判"没变化"导致提前终止）
- `window.__allData` 若中途混入脏数据，可先 `window.__allData = []` 清空重抓
- 首轮调用时若当前已在中间页，先跳回第 1 页再开抓，保证顺序完整

---

### ⚠️ delegate_task 子代理的浏览器操作

**默认情况下** `delegate_task` 子代理启动时获得**完全独立的浏览器上下文**（新的无头浏览器实例），无法继承主会话的登录 cookie、session storage 或页面状态。

这意味着：
- ❌ 主会话登录 OA → delegate_task 子代理抓取数据 = 子代理在未登录状态打开 OA，需要重新登录
- ❌ 即使子代理重新登录，它也无法看到主会话已经翻到的页面
- ✅ 正确的模式：**主会话全程操作浏览器**，用 `browser_console` 提取数据，用 `execute_code` 做统计处理

#### 例外：delegate_task 作为分页器失效的恢复方案

当主会话的 `.ant-pagination` DOM 组件因多次手动翻页而消失时，`delegate_task` 可作为一种**恢复性工作流**使用：

1. 在 context 中传入完整的登录凭据（账号、密码）和最新的验证码值
2. 子代理在独立浏览器中重新登录 OA
3. 子代理用 JS `async function` 一次性完成所有翻页和数据提取（避免多步 browser_click）
4. 子代理将提取结果返回

**⚠️ 限制：** 验证码必须在 context 中预传递（子代理无法调用 `clarify` 问用户），所以如果页面刷新后验证码变化，这种方法失效。适合验证码不需要重新输入的场景。

原因：每个子代理启动时获得**完全独立的浏览器上下文**（新的无头浏览器实例），无法继承主会话的登录 cookie、session storage 或页面状态。

这意味着：
- ❌ 主会话登录 OA → delegate_task 子代理抓取数据 = 子代理在未登录状态打开 OA，需要重新登录
- ❌ 即使子代理重新登录，它也无法看到主会话已经翻到的页面
- ✅ 正确的模式：**主会话全程操作浏览器**，用 `browser_console` 提取数据，用 `execute_code` 做统计处理

### 何时可以用 delegate_task

将 delegate_task 用于**数据处理**而非**数据采集**：

```python
# ✅ 正确：主会话完成浏览器操作，子代理做纯数据处理
browser_console(expression="...提取所有数据...")
delegate_task(
    goal="分析这些OA报销数据，按类别汇总...",
    context="原始数据: " + json_data
)

# ❌ 错误：让子代理自己去浏览器抓
delegate_task(
    goal="登录OA并提取报销数据...",
    toolsets=['browser']
)
```

用户期望的统计方式：按模块展示，含逐条明细 + 小计 + 总计。
示例输出参见本 session 的对话记录（2026-05-27 待报销金额完整汇总）。
