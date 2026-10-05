---
name: oa-reimbursement-data-scraper
description: "Scrape reimbursement/pending-payment data from SmarDaten OA system — login, navigate to expense modules, paginate all pages, extract line-item data, and produce a summary table."
version: 2.2.0
---

# OA Reimbursement Data Scraper

Scrape 报销数据 (expense reimbursement data) from the SmarDaten OA system (oa.smardaten.com). Handles all three reimbursement types: 出差报销 (travel), 个人报销 (personal), 招待报销申请 (entertainment).

## When to Use

- User asks "看看OA报销数据" / "查报销金额" / "统计未结束流程一共多少钱"
- User wants totals broken down by expense module
- User asks for comparison or status check on pending reimbursements

## Prerequisites

- OA credentials in memory (phone: 17705148484)
- OA URL: `https://oa.smardaten.com`
- Login: phone-based, password known

## Navigation Path

### Option A: 从首页"我要办"区域进入（新路径，推荐）

Login → 首页 → 在首页"我要办"区域 → 找到"常用功能"中的"费用报销"卡片 → 点击进入

首页"我要办"区域的常用功能卡片位置：
- 出差申请 / 请假申请 / 补卡申请 / 加班申请 / 外出申请 / **费用报销** / OA问题反馈
- 如果"费用报销"不在常用功能里，点击"+"号添加

### Option B: 从侧边菜单进入（备选）

Login → 首页 → 点击顶部导航"要我办" → 侧边菜单切换到"我要办" → 找到"费用报销"图标点击

### Inside 费用报销:
- 左菜单"员工报销" → 3个标签页: 出差报销 / 个人报销 / 招待报销(旧)
- 左菜单"招待报销" (可展开) → 招待报销申请 / 部门额度申请

## Login

1. Navigate to `https://oa.smardaten.com`
2. Wait for page to load — click @e1 (generic wrapper) if snapshot shows "(empty page)"
3. Type phone into 账号 field
4. Type password into 密码 field
5. Click 登录 button or press Enter
6. Wait 5-8 seconds for home page to render (SuperOA智能助手 appears)
7. If page stays blank after login, retry browser_navigate to the login URL

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

## Data Extraction via JS in browser_console — Async Bulk Pagination (Recommended)

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
                // For 出差报销: also filter by c[2].textContent.trim() === '出差报销'
                // For 招待报销申请: no type column filter needed (just check code non-empty)
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

**CRITICAL: Use `(async function(){...})()` not `(function(){...})()`** — the await keyword requires async scope. The pattern `new Promise(r => setTimeout(r, 2000))` works in browser_console context.

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

1. **React virtual DOM bleed** — When switching tabs (e.g. from 出差报销 to 个人报销), the old tab's data rows persist in the DOM. This manifests as:
   - **出差报销数据出现在个人报销标签页的表格里**，列索引对不上（例如个人报销的c[0]是报销编码，c[1]是报销类型，但出差报销的行把出差编码填入c[1]位置，导致个人报销的type列显示的是出差编码而非"个人报销"）
   - **个人报销的记录在后几页重复出现**（因为同一份数据在多个分页的DOM里都存在）
   - **应对方式**：
     - 只提取 `c[1].textContent.trim() === '个人报销'` 的行作为真实个人报销记录（靠type列过滤）
     - 注意**去重**：个人报销通常只有1页真实数据，后面的翻页结果只是DOM残留
     - 出差报销用 `c[2].textContent.trim() === '出差报销'` 过滤
     - 招待报销申请没有type列，直接用 `c[0] 非空` 过滤，但也要注意分页重复

2. **Page crash on late pages** — 招待报销申请's page 3 or other late pages may cause the page body to go empty (OA micro-frontend instability). If this happens:
   - The last page may genuinely have fewer records (e.g. page 3 of 招待报销申请 may have only 7 records instead of 10)
   - If page crashes, re-navigate to home, re-login, and re-enter the module. The data from already-scraped pages is preserved in your session.

3. **Session timeout** — OA session does NOT persist across browser sessions. After ~5-10 minutes of inactivity or after a page crash, you'll be redirected to the login page. Always plan to re-login for long scraping sessions.

4. **Column indices vary by module** — Always probe first data row to find the correct amount column before bulk extraction. Use:
   ```javascript
   const c = rows[1].querySelectorAll('td');
   // Dump all columns to find amount
   ```

5. **Pagination ref IDs change** — After navigation, cached ref IDs from the snapshot are stale. Query pagination via DOM (`document.querySelector`) each time, not via cached ref IDs.

6. **DeepSeek cannot use browser_vision** — Use browser_snapshot + browser_console only for OA pages.

7. **Login retry** — If login fails (stays on login page after clicking 登录), try pressing Enter instead of clicking the button. Sometimes the click event doesn't fire.

8. **Tab switching loses context** — When clicking between 出差报销/个人报销 tabs, the page may briefly show a loading state. Always sleep 2 seconds after tab clicks before extracting data.
