# Chinese Academic Literature Search (中文文献检索)

When the user asks to search for papers on a topic, always ask: "你要英文论文还是中文论文？" before proceeding. They may want one, the other, or both.

## Accessible Chinese Academic Database (2026)

**掌桥科研 (zhangqiaokeyan.com)** — the most reliable Chinese paper source accessible via Hermes browser tools.

### Why this works

Most Chinese academic databases block automated access:
| Site | Status | Issue |
|------|--------|-------|
| 知网 (cnki.net) | ❌ Blocked | Captcha → 403 on search results |
| 万方数据 (wanfangdata.com.cn) | ❌ Blocked | Requires login |
| 百度学术 (xueshu.baidu.com) | ❌ Blocked | Baidu captcha |
| Google Scholar | ❌ Timeout | Bot detection |
| 维普 (cqvip.com) | ❌ Blocked | 412 Precondition Failed |
| AMiner | ❌ Blocked | Requires login (empty results) |
| **掌桥科研 (zhangqiaokeyan.com)** | **✅ Works** | Loads via browser tools, extractable via console |

### Access Pattern

1. `browser_navigate(url="https://www.zhangqiaokeyan.com/search/all.html?text=<URL_ENCODED_QUERY>")`
   - Example: `text=%E7%A2%B3%E8%B6%B3%E8%BF%B9` (碳足迹)
   - **NOTE**: Direct URL with query param may show 404. Use search box instead.

2. If direct URL fails with "页面不存在", use the on-page search box:
   - `browser_type(ref=e3, text="搜索词")` — where e3 = the search textbox
   - `browser_click(ref=e4)` — click "搜索" button
   - Wait for JS to load results (the page shows "加载中..." then populates)

3. Extract results via `browser_console(expression="document.body.innerText")`:
   - Results are rendered via JS into the DOM
   - The full page text contains papers in numbered list format: `N.[期刊]Title\n   Author(s)\n   摘要: ...`
   - Year filter, discipline filter, and pagination are visible in the sidebar

4. Pagination: click page number links via DOM query:
   ```javascript
   var btn = document.querySelector('[class*="page"]') || 
             Array.from(document.querySelectorAll('a, button, span'))
               .find(el => el.textContent.trim() === '2');
   btn.click();
   ```

### Key Data on 掌桥科研

- Sidebar shows: total results count, yearly distribution, discipline breakdown, database coverage (SCI, EI, CA, CSTPCD)
- Each result: title, authors, journal, year, issue, abstract (150-300 chars), keywords
- Results are sorted by relevance or publication date (switchable)
- Per-page: 20, 30, or 50 results
- Covers: 中文期刊 + 中文会议 + 中文学位 + 外文期刊 + 标准 + 专利

### Example: Carbon Footprint (碳足迹) 中文文献

```
Total results: ~10,878
Year distribution: 2026(158) | 2025(527) | 2024(1,026) | 2023(1,034)
Disciplines: 环境科学(166) | 工业经济(147) | 化学工业(142) | 农业(116)
Coverage: CA(2,278) | SCI(1,997) | EI(1,587) | CSTPCD(560)
```

### Limitations

- Cannot download PDFs (paywalled by individual papers)
- Only text extraction of titles + abstracts via DOM
- Pagination requires manual JS clicks (no clean API endpoint)
- 掌桥科研 requires no login for search, but some result details may prompt login
