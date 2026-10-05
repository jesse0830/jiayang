# OA Reimbursement Data Scraper — Full Reference

Absorbed from standalone `oa-reimbursement-data-scraper` skill (v2.2.0). Handles all three reimbursement types from the SmarDaten OA system: 出差报销 (travel), 个人报销 (personal), 招待报销申请 (entertainment).

## Navigation Path

### Option A: 从首页"我要办"区域进入（推荐）

Login → 首页 → 在首页"我要办"区域 → 找到"常用功能"中的"费用报销"卡片 → 点击进入

首页"我要办"区域的常用功能卡片位置：
- 出差申请 / 请假申请 / 补卡申请 / 加班申请 / 外出申请 / **费用报销** / OA问题反馈
- 如果"费用报销"不在常用功能里，点击"+"号添加

### Option B: 从侧边菜单进入（备选）

Login → 首页 → 点击顶部导航"要我办" → 侧边菜单切换到"我要办" → 找到"费用报销"图标点击

### Inside 费用报销:
- **员工报销（含出差报销、个人报销、招待报销(旧)标签页）**：
  - 出差报销、个人报销的数据都在这里，通过标签页切换
  - 招待报销(旧)标签页只是一个提示入口，不展示招待报销申请数据
- **招待报销 → 招待报销申请**（在左侧菜单栏中，是独立的页面，不是标签页）
  - 从这里进入招待报销申请列表，有自己的查询条件、表格列和分页
  - 注意：招待报销申请的数据不在"员工报销"里的任一标签页中，必须从左侧菜单进入
- **招待报销 → 部门额度申请**（同样是独立页面）

## Column Index Mapping (verified 2026-05)

### 出差报销 tab
| Field | Index |
|-------|:-----:|
| 报销编码 | c[0] |
| 出差编码 | c[1] |
| 报销类型 | c[2] — filter: "出差报销" |
| 申请人 | c[3] |
| 申请日期 | c[4] |
| 业务状态 | c[5] |
| 经办人 | c[6] |
| 金额(费用合计) | c[12] |

### 个人报销 tab
| Field | Index |
|-------|:-----:|
| 报销编码 | c[0] |
| 报销类型 | c[1] |
| 申请人 | c[2] |
| 申请日期 | c[3] |
| 业务状态 | c[4] |
| 金额 | c[11] |

### 招待报销申请 tab
| Field | Index |
|-------|:-----:|
| 报销编码 | c[0] |
| 申请人 | c[1] |
| 承担部门 | c[2] |
| 申请日期 | c[3] |
| 经办人 | c[4] |
| 业务状态 | c[5] |
| 报销额度 | c[11] |
| 费用合计(金额) | c[12] |

## Data Extraction via JS — Async Bulk Pagination (Recommended)

Use an async IIFE to extract all pages in one call. This avoids page-crash issues from sequential manual navigation:

```javascript
(async function(){
    const results = [];
    const pag = document.querySelector('.ant-pagination');
    const items = pag ? pag.querySelectorAll('.ant-pagination-item') : [];
    const totalPages = items.length;
    
    for(let p = 1; p <= totalPages; p++){
        // Click page
        const pis = document.querySelectorAll('.ant-pagination-item');
        for(let el of pis){
            if(el.textContent.trim() === String(p)){
                el.click();
                break;
            }
        }
        // Wait for React re-render
        await new Promise(r => setTimeout(r, 2000));
        
        // Extract data from this page
        const rows = document.querySelectorAll('.ant-table-tbody tr');
        const pageData = [];
        rows.forEach(r => {
            const c = r.querySelectorAll('td');
            if(c.length > 12 && c[0].textContent.trim() !== '') {
                pageData.push({
                    code: c[0].textContent.trim(),
                    status: c[STATUS_IDX].textContent.trim(),
                    amount: c[AMOUNT_IDX].textContent.trim()
                });
            }
        });
        results.push({page: p, records: pageData});
    }
    return JSON.stringify(results);
})()
```

**CRITICAL: Use `(async function(){...})()` not `(function(){...})()`** — the await keyword requires async scope.

## Pagination

### Step 1: Check total pages (quick check)
```javascript
(function(){
    const pag = document.querySelector('.ant-pagination');
    if(!pag) return 'no pagination';
    const items = pag.querySelectorAll('.ant-pagination-item');
    return JSON.stringify(Array.from(items).map(x => x.textContent.trim()));
})()
```

### Known page counts (typical):
- 出差报销: ~7 pages
- 个人报销: 1 page
- 招待报销申请: 3 pages (~26 records)

## Status Filtering

Include in "未结束" (pending) sum:
- `直接主管审批`
- `经办会计审批`
- `出纳付款` (finance has not yet paid)

Exclude (already completed):
- `结束`
- `已完成` / `完成`

**注意**："出纳付款"状态的记录可能有几个月前的老数据——这种情况说明钱一直没打出去，可能是财务积压或审批链卡住。汇报时可以做时间分层提示。

## Pitfalls

1. **React virtual DOM bleed** — When switching tabs, the old tab's data rows persist in the DOM. This manifests as:
   - 出差报销数据出现在个人报销标签页的表格里，列索引对不上
   - 个人报销的记录在后几页重复出现
   - **应对方式**：
     - 只提取 `c[1].textContent.trim() === '个人报销'` 的行作为真实个人报销记录（靠type列过滤）
     - 注意**去重**：个人报销通常只有1页真实数据，后面的翻页结果只是DOM残留
     - 出差报销用 `c[2].textContent.trim() === '出差报销'` 过滤
     - 招待报销申请没有type列，直接用 `c[0] 非空` 过滤，但也要注意分页重复

2. **Page crash on late pages** — Late pages (e.g. page 3 of 招待报销申请) may cause the page body to go empty (OA micro-frontend instability). If this happens:
   - The last page may genuinely have fewer records
   - Re-navigate to home, re-login, and re-enter the module. Already-scraped data is preserved in your session.

3. **Session timeout** — OA session does NOT persist across browser sessions. After ~5-10 minutes of inactivity or page crash, you'll be redirected to login. Always plan to re-login for long scraping sessions.

4. **Column indices vary by module** — Always probe first data row to find the correct amount column before bulk extraction.

5. **Pagination ref IDs change** — After navigation, cached ref IDs from the snapshot are stale. Query pagination via DOM each time.

6. **DeepSeek cannot use browser_vision** — Use browser_snapshot + browser_console only for OA pages.

7. **Login retry** — If login fails (stays on login page), try pressing Enter instead of clicking the button.

8. **Tab switching loses context** — Always sleep 2 seconds after tab clicks before extracting data.

## Querying Personal Reimbursement Records ("我发起的" Module)

When the user asks "我个人的报销还有多少没报", use the **"我发起的"** menu item (not the 员工报销 tab) to find records initiated by the user.

### Navigation Path

费用报销页面 → 左侧菜单点击 **"我发起的"** → 列表显示该用户发起的全部流程记录

### Column Layout (我发起的)

The "我发起的" page has a **different table structure** from 员工报销:

| Field | Description |
|-------|-------------|
| c[0] | 事件类型（如"招待报销"、"费用报销"） |
| c[1] | 事件名称（格式：`杨嘉阳 金额 类型 编码`，如`杨嘉阳 478.80 出差报销 202605304501`） |
| c[2] | 摘要（项目名称等信息） |
| c[3] | 创建时间 |
| c[4] | 更新时间 |
| c[5] | 创建人 |
| c[6] | 经办人 |
| c[7] | 流程状态（"处理中" / "结束"） |
| c[8] | 业务状态（"直接主管审批" / "经办会计审批" / "出纳付款" / "结束"） |

**Parse the event name (c[1]):** The format is `姓名 金额 类型 编码`. E.g., `杨嘉阳 478.80 出差报销 202605304501`. Split by space to extract the amount.

### Pitfall: "我发起的" Pagination (Jump-Style)

The "我发起的" pagination on SmarDaten OA uses **jump-style** pagination (not sequential). After clicking page 1, the page items show `1, 16, 17, 18, 19, 20` instead of sequential page numbers like `1, 2, 3, 4, 5`. This means:

- Pages 2-15 are hidden behind the "..." jump
- The `.ant-pagination-item` elements only show the current range
- Sequential `for` loop traversal via JS will fail because page 2 doesn't exist in the DOM
- Use the `.ant-pagination-next` button to navigate forward, or manually click specific page numbers
- **The `async` loop pattern (click every page in a `for` loop) does NOT work for this page** — it will try to click page 2 which doesn't exist in the DOM. Use `.ant-pagination-next` instead.
- **Use delegate_task** with browser toolset and max_iterations=100+ to let a sub-agent navigate page by page, extracting each page with a browser_console snippet before clicking next. This typically covers 10-12 pages per run.
- **Parsing the event name (c[1]):** format is `杨嘉阳 1280.00 项目 20260608365`. Amount is the 2nd space-separated token. Use `.split(' ')`.

### Determining What's User's Personal Reimbursement

The 出差报销 (travel expense) table **does not have an "申请人" (applicant) column** in the 员工报销 view. To determine which records are the user's:

1. Use **"我发起的"** module — this only shows records initiated by the logged-in user
2. Parse the event name (c[1]) to extract the amount and type
3. Cross-reference with the 员工报销 data (by 报销编码) to verify amounts

### Typical Personal Pending Breakdown

For a software factory manager (杨嘉阳) at SmarDaten, the personal pending typically spans:
- **招待报销** (entertainment): mixed states — 直接主管审批, 经办会计审批, 出纳付款
- **个人报销** (personal): 2 records totaling ~¥9,000 in 出纳付款
- **出差报销** (travel): 1+ records in 出纳付款

## Session Data Example

A June 2026 snapshot of actual expense data (see `references/oa-reimbursement-snapshot-202606.md` for full breakdown):

- 出差报销 pending: ¥12,521.98 (21 records, all "出纳付款")
- 个人报销 pending: ¥9,179.12 (2 records, both "出纳付款")  
- 招待报销 pending: ¥18,032.97 (21 records, mixed 经办会计审批 and 出纳付款)
- Total pending: **¥39,734.07** (44 records)

**Note:** This is a one-time session snapshot — always re-scrape for current data rather than relying on these numbers.

## Additional Session-Specific Pitfalls

See `references/oa-reimbursement-scraper-pitfalls.md` for details on:
- React DOM bleed between tabs causing shifted columns and phantom records
- Async pagination loop overshooting actual page count (7 pages → 8 iterations)
- 招待报销申请 entry point is via left sidebar menu, not "员工报销" tab panel
