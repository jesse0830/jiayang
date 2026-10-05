# Chinese OA Table Extraction Patterns

Common table structures found in Chinese OA systems (smardaten, yonyou, dingtalk enterprise, etc.) and how to extract data from them.

## Table Structure Variations

### 1. Standard HTML Table (`<table>`)

The simplest case. Rows and cells are in the DOM directly.

```javascript
// Extract all visible rows from a standard table
const rows = document.querySelectorAll('table tbody tr');
const data = Array.from(rows).map(row => {
  const cells = row.querySelectorAll('td');
  return {
    code: cells[0]?.innerText?.trim(),       // 编码
    handler: cells[1]?.innerText?.trim(),     // 经办人
    status: cells[2]?.innerText?.trim(),      // 业务状态
    amount: cells[3]?.innerText?.trim()       // 费用合计
  };
});
console.table(data);
```

Run via `browser_console(expression=...)`.

### 2. Virtual Scroll Table (Ant Design / Element UI)

Modern Chinese OA systems use component libraries with virtual scrolling. Only visible rows are in the DOM.

**Scroll to load all rows**:
```javascript
// Scroll the table body to the bottom repeatedly
const scrollContainer = document.querySelector('.ant-table-body, .el-table__body-wrapper');
let prevHeight = 0;
while (prevHeight < scrollContainer.scrollHeight) {
  prevHeight = scrollContainer.scrollHeight;
  scrollContainer.scrollTop = scrollContainer.scrollHeight;
  await new Promise(r => setTimeout(r, 500));
}
```

Then extract visible rows:
```javascript
const rows = document.querySelectorAll('.ant-table-row, .el-table__row');
// ... same extraction as above
```

### 3. Grid/DataGrid Components

Some OA systems use Ag-Grid, Kendo Grid, or custom grid components. These may have a `.ag-row` or `.k-grid-content tr` selector.

```javascript
// Ag-Grid
const rows = document.querySelectorAll('.ag-row:not(.ag-row-first)');
// Kendo
const rows = document.querySelectorAll('.k-grid-content tr');
```

## Pagination Handling

### Pattern A: Page Number List

Find pagination controls and iterate:

```javascript
// Check pagination info
const pagination = document.querySelector('.ant-pagination, .el-pagination, .pagination');
const pageInfo = pagination?.innerText;
// e.g. "共 50 条 每页 15 条 第 1/4 页"

// Click next page
function clickNextPage() {
  const nextBtn = document.querySelector('.ant-pagination-next, .el-pagination .btn-next, .pagination .next');
  if (nextBtn && !nextBtn.classList.contains('disabled')) {
    nextBtn.click();
    return true;
  }
  return false;
}
```

### Pattern B: Server-side with URL param

URL looks like: `...&page=1` or `...&pageNo=1`. Change the parameter:

```javascript
const url = new URL(window.location.href);
url.searchParams.set('page', String(pageNum));
window.location.href = url.toString();
```

### Pattern C: Post-back Form

Some older OA systems submit a form with a hidden page number field. Look for:
```html
<input type="hidden" name="page" value="1">
```

## Filtering by Business Status (业务状态)

After collecting all rows, filter out "结束" entries:

```javascript
data = data.filter(row => row.status !== '结束');
```

Common status values in OA systems:
| Status | Meaning |
|--------|---------|
| 结束 | Completed — skip |
| 审批中 | In approval — include |
| 待审批 | Pending approval — include |
| 待提交 | Draft — include |
| 已退回 | Returned — include |
| 已通过 | Approved — include |
| 已付款 | Paid — include |

## Extracting Amount (费用合计)

The "费用合计" (total expense) column often contains:
- Numeric string: `"1234.56"`
- Formatted string: `"¥1,234.56"` or `"1,234.56 元"`
- May include a link to the detail page

Clean and sum:
```javascript
function parseAmount(str) {
  if (!str) return 0;
  // Remove currency symbols, commas, and '元'
  const cleaned = str.replace(/[¥￥,，元\s]/g, '');
  return parseFloat(cleaned) || 0;
}

const total = data.reduce((sum, row) => sum + parseAmount(row.amount), 0);
```

## Final Report Format

Present as markdown:

```markdown
## 招待报销申请

| 编码 | 经办人 | 业务状态 | 费用合计 |
|------|--------|----------|----------|
| REQ-001 | 张三 | 审批中 | 1,200.00 |
| REQ-002 | 李四 | 待审批 | 800.50 |

**小计: ¥2,000.50**

## 个人报销

...

**总计: ¥X,XXX.XX**
```
