---
name: ocr-and-documents
description: "Extract text from PDFs/scans (pymupdf, marker-pdf)."
version: 2.4.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [PDF, Documents, Research, Arxiv, Text-Extraction, OCR]
    related_skills: [powerpoint]
---

# PDF & Document Extraction

For DOCX: use `python-docx` (parses actual document structure, far better than OCR).
For PPTX: see the `powerpoint` skill (uses `python-pptx` with full slide/notes support).
This skill covers **PDFs and scanned documents**.

## Step 1: Remote URL Available?

If the document has a URL, **always try `web_extract` first**:

```
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])
web_extract(urls=["https://example.com/report.pdf"])
```

This handles PDF-to-markdown conversion via Firecrawl with no local dependencies.

Only use local extraction when: the file is local, web_extract fails, or you need batch processing.

## Step 2: Choose Local Extractor

| Feature | pymupdf (~25MB) | marker-pdf (~3-5GB) |
|---------|-----------------|---------------------|
| **Text-based PDF** | ✅ | ✅ |
| **Scanned PDF (OCR)** | ❌ | ✅ (90+ languages) |
| **Tables** | ✅ (basic) | ✅ (high accuracy) |
| **Equations / LaTeX** | ❌ | ✅ |
| **Code blocks** | ❌ | ✅ |
| **Forms** | ❌ | ✅ |
| **Headers/footers removal** | ❌ | ✅ |
| **Reading order detection** | ❌ | ✅ |
| **Images extraction** | ✅ (embedded) | ✅ (with context) |
| **Images → text (OCR)** | ❌ | ✅ |
| **EPUB** | ✅ | ✅ |
| **Markdown output** | ✅ (via pymupdf4llm) | ✅ (native, higher quality) |
| **Install size** | ~25MB | ~3-5GB (PyTorch + models) |
| **Speed** | Instant | ~1-14s/page (CPU), ~0.2s/page (GPU) |

**Decision**: Use pymupdf unless you need OCR, equations, forms, or complex layout analysis.

If the user needs marker capabilities but the system lacks ~5GB free disk:
> "This document needs OCR/advanced extraction (marker-pdf), which requires ~5GB for PyTorch and models. Your system has [X]GB free. Options: free up space, provide a URL so I can use web_extract, or I can try pymupdf which works for text-based PDFs but not scanned documents or equations."

---

## Scanned PDF / Image-based PDF (macOS-native, zero install)

When pip install is unavailable or times out, macOS has **built-in OCR** via the Vision framework — no dependencies, works offline.

**Step 1: Identify scanned PDF**
```bash
# Check if it's image-based or text-based
python3 -c "
with open('file.pdf', 'rb') as f:
    c = f.read()
    print('Has text:', any(op in c for op in [b'Tj', b'TJ']))
    print('Has image:', b'/Image' in c or b'/XObject' in c)
"
```

**Step 2: Extract embedded JPEG** (if image-based)
```bash
python3 -c "
import re
with open('file.pdf', 'rb') as f:
    c = f.read()
start = c.find(b'\\xff\\xd8\\xff\\xe0')
end = c.find(b'\\xff\\xd9', start) + 2
with open('/tmp/page.jpg', 'wb') as f:
    f.write(c[start:end])
print('Extracted JPEG')
"
```
For multi-page PDFs, extract each page's image separately (scan for multiple JPEG markers).

**Step 3: OCR with Apple Vision** (multi-page PDFs directly supported)

```bash
swift scripts/extract_macos_vision_ocr.swift file.pdf
swift scripts/extract_macos_vision_ocr.swift file.pdf --lang zh-Hans,en
swift scripts/extract_macos_vision_ocr.swift image.jpg --lang en
```

The script handles both single images and PDFs. It:
- Renders each PDF page at native resolution
- Runs `VNRecognizeTextRequest` with `.accurate` level
- Supports Chinese + English recognition (`zh-Hans`, `en`)
- Sorts text top-to-bottom, left-to-right
- Works entirely offline — no pip install needed

**Image rotation**: If the scan is rotated, use `sips` (macOS built-in) before OCR:
```bash
sips -r 90 input.jpg --out rotated.jpg
```

**Image format conversion**:
```bash
sips -s format png input.jpg --out output.png
sips -m "/System/Library/ColorSync/Profiles/sRGB Profile.icc" gray_input.png --out rgb_output.png
```

**Step 4: Generate Word document** from OCR output
```bash
pip install python-docx
```
Use `python-docx` to create a DOCX with tables, headers, formatting matching the scan structure.

**Layout verification**: After generating the DOCX, ALWAYS ask the user to verify the layout. If they say it doesn't match, use the coordinate-based layout detection technique in `references/sharp-scanner-pdf-to-word.md` → Coordinate-based Layout Detection to extract exact pixel positions from the source image, enabling precise column widths and cell merges in python-docx.

> ⚠️ **Pitfall**: DeepSeek model does NOT support vision/image_url — `vision_analyze` fails with "unknown variant `image_url`, expected `text`". Use macOS Vision OCR as the fallback.

### Chinese screenshots (PNG) — tesseract path

For WeChat/WeCom/screenshot PNGs (not PDFs), tesseract with the Chinese pack is the fastest fallback when vision is unavailable:

```bash
# Install once: brew install tesseract && brew install tesseract-lang  (adds chi_sim)
tesseract "/path/to/screenshot.png" /tmp/out -l chi_sim --psm 3 2>/dev/null
cat /tmp/out.txt
```

- **OCR the ORIGINAL file directly.** Observed: a sips-re-encoded PNG (`sips -Z 2000 -s format png`) produced EMPTY tesseract output, while the same command on the original 2180x1216 PNG worked fine. Don't re-encode unless you must shrink; if you do, re-verify output is non-empty.
- `--psm 3` (auto page segmentation) was the working mode for single-screen screenshots.
- Output is noisy for Chinese: expect wrong line breaks, mixed CN/EN, garbled punctuation. Manually reconstruct the structure after OCR (see `chinese-enterprise-document-writing` → Project Plan Image pipeline for the same workflow on tables).
- If tesseract is missing and pip installs are unavailable, use the macOS Vision swift script above instead (`--lang zh-Hans,en`).

> ⚠️ **Layout fidelity**: After OCR-to-DOCX conversion, ALWAYS verify the generated document's layout with the user before calling it done. Users care about table structure, cell alignment, merged cells, font sizing, and visual spacing — not just text accuracy. The coordinate-based layout approach (see `references/sharp-scanner-pdf-to-word.md`) helps but is still an approximation. Proactively ask: "这个格式和PDF里的布局一致吗？哪里需要调整？"
>
> **Pro tip**: When the user says layout doesn't match, use Swift to extract **exact pixel coordinates** of each text fragment from the source image (see `references/sharp-scanner-pdf-to-word.md` → Coordinate-based Layout Detection). This reveals column boundaries, row grouping, and merged cells — enabling precise `Cm()` width ratios and cell merges in python-docx.

---

## pymupdf (lightweight)

```bash
pip install pymupdf pymupdf4llm
```

**Via helper script**:
```bash
python scripts/extract_pymupdf.py document.pdf              # Plain text
python scripts/extract_pymupdf.py document.pdf --markdown    # Markdown
python scripts/extract_pymupdf.py document.pdf --tables      # Tables
python scripts/extract_pymupdf.py document.pdf --images out/ # Extract images
python scripts/extract_pymupdf.py document.pdf --metadata    # Title, author, pages
python scripts/extract_pymupdf.py document.pdf --pages 0-4   # Specific pages
```

**Inline**:
```bash
python3 -c "
import pymupdf
doc = pymupdf.open('document.pdf')
for page in doc:
    print(page.get_text())
"
```

---

## marker-pdf (high-quality OCR)

```bash
# Check disk space first
python scripts/extract_marker.py --check

pip install marker-pdf
```

**Via helper script**:
```bash
python scripts/extract_marker.py document.pdf                # Markdown
python scripts/extract_marker.py document.pdf --json         # JSON with metadata
python scripts/extract_marker.py document.pdf --output_dir out/  # Save images
python scripts/extract_marker.py scanned.pdf                 # Scanned PDF (OCR)
python scripts/extract_marker.py document.pdf --use_llm      # LLM-boosted accuracy
```

**CLI** (installed with marker-pdf):
```bash
marker_single document.pdf --output_dir ./output
marker /path/to/folder --workers 4    # Batch
```

---

## Arxiv Papers

```
# Abstract only (fast)
web_extract(urls=["https://arxiv.org/abs/2402.03300"])

# Full paper
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])

# Search
web_search(query="arxiv GRPO reinforcement learning 2026")
```

## Split, Merge & Search

pymupdf handles these natively — use `execute_code` or inline Python:

```python
# Split: extract pages 1-5 to a new PDF
import pymupdf
doc = pymupdf.open("report.pdf")
new = pymupdf.open()
for i in range(5):
    new.insert_pdf(doc, from_page=i, to_page=i)
new.save("pages_1-5.pdf")
```

```python
# Merge multiple PDFs
import pymupdf
result = pymupdf.open()
for path in ["a.pdf", "b.pdf", "c.pdf"]:
    result.insert_pdf(pymupdf.open(path))
result.save("merged.pdf")
```

```python
# Search for text across all pages
import pymupdf
doc = pymupdf.open("report.pdf")
for i, page in enumerate(doc):
    results = page.search_for("revenue")
    if results:
        print(f"Page {i+1}: {len(results)} match(es)")
        print(page.get_text("text"))
```

No extra dependencies needed — pymupdf covers split, merge, search, and text extraction in one package.

---

## Notes

- `web_extract` is always first choice for URLs
- pymupdf is the safe default — instant, no models, works everywhere
- marker-pdf is for OCR, scanned docs, equations, complex layouts — install only when needed
- Both helper scripts accept `--help` for full usage
- marker-pdf downloads ~2.5GB of models to `~/.cache/huggingface/` on first use
- For Word docs: `pip install python-docx` (better than OCR — parses actual structure)
- For PowerPoint (.pptx): see the `powerpoint` skill (uses python-pptx)
- For **old .ppt (PowerPoint 97-2003 binary format)**: see `references/legacy-ppt-extraction.md` — these are OLE2 compound documents, not Open XML, and cannot be parsed by python-pptx
