# Sharp Scanner PDF → Word Conversion

## Source: OCR-and-documents skill

### Scenario
A Sharp scanner produced a single-page PDF at 200 DPI, grayscale JPEG image embedded in a PDF-1.4 wrapper. The goal was to reproduce it as a .docx with identical table structure.

### File characteristics
```
%PDF-1.4 Sharp Scanned ImagePDF
/Type /Page /MediaBox [0 0 595 841]  → A4
/XObject << /Img1 >>  /Filter /DCTDecode  → JPEG embedded
/Width 1653 /Height 2338 /ColorSpace /DeviceGray  → 200 DPI grayscale
```

### Workflow (exact steps)
1. **Identify** — Check PDF header (`PDF-1.4 Sharp Scanned ImagePDF`), look for `/Image` / `/XObject` in raw content
2. **Extract JPEG** — Find `\xff\xd8\xff\xe0` (SOI) and `\xff\xd9` (EOI) markers in binary
3. **OCR via swift** — Use `VNRecognizeTextRequest` with `.accurate` level and `zh-Hans,en` recognition languages
4. **Verify rotation** — OCR output was garbled at 90°/180°/270°, correct at 0°. Try all 4 rotations via `sips -r 0/90/180/270`
5. **Regenerate** — Build .docx with `python-docx`, matching: title, info table (甲方/乙方/合同), delivery checklist table

### Coordinate-based Layout Detection (for precise table reconstruction)

When the user says the layout doesn't match, use Swift to extract **exact pixel coordinates** for each text fragment:

```swift
// Extract bounding boxes from VNRecognizedTextObservation
for obs in observations {
    let box = obs.boundingBox  // normalized 0-1
    let text = obs.topCandidates(1).first?.string ?? ""
    let x = box.origin.x * imgW
    let y = (1 - box.origin.y - box.height) * imgH  // convert to top-left coords
    let w = box.width * imgW
    let h = box.height * imgH
    print("x,y,w,h,text")
}
```

This reveals:
- **Column boundaries**: items with overlapping X ranges belong to the same column
- **Row grouping**: items with similar Y positions are on the same row
- **Merged cells**: single text spanning multiple column X-ranges
- **Label/value adjacency**: "甲方名称 | 数盾信息科技股份有限公司" appear at same Y, adjacent X

Example output from a real 验收单 at 1653×2338px:
```
224,112,336,55|smardaten           ← logo
200,316,122,41|甲方名称            ← label column
441,316,356,41|数盾信息科技股份有限公司  ← value column
899,316,122,41|授权代表            ← right-side label
1239,316,95,41|林泰清             ← right-side value
543,761,353,38|福州北斗资源综合监管平台  ← table cell (row 1, col 2)
```

Use these coordinates to set column widths proportionally in python-docx (`Cm()` values) and determine whether cells should be merged.

### python-docx tips for scanned document reproduction

```python
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml.ns import qn

doc = Document()

# Chinese font setup
style = doc.styles['Normal']
font = style.font
font.name = '宋体'
font.size = Pt(10.5)
style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

# Helper function
def set_cell(cell, text, bold=False, align=WD_ALIGN_PARAGRAPH.CENTER, size=Pt(10.5)):
    cell.text = ''
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.0
    run = p.add_run(text)
    run.font.size = size
    run.font.name = '宋体'
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    if bold:
        run.bold = True

# Column width matching coordinate proportions
col_widths = [Cm(3.0), Cm(7.0), Cm(2.5), Cm(2.5)]
for i, w in enumerate(col_widths):
    for cell in table.columns[i].cells:
        cell.width = w

# Merge cells for labels spanning full width
table.cell(2,0).merge(table.cell(2,3))

# Vertical centering
for row in table.rows:
    for cell in row.cells:
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER

doc.save('output.docx')
```

### Grayscale-to-RGB conversion (critical for OCR quality)

Sharp scanner grayscale PDFs embed JPEG as `DeviceGray` color space. Apple Vision OCR accuracy is noticeably worse on pure grayscale images than on sRGB-converted versions. **Always convert to sRGB before OCR:**

```bash
# Convert grayscale PNG/JPEG to sRGB
sips -m "/System/Library/ColorSync/Profiles/sRGB Profile.icc" input_gray.png --out output_rgb.png
```

The `sips -m` flag applies color matching. Without this, text recognition misses characters and misreads numbers, especially at low resolution or for small Chinese text.

### Identifying Sharp scanner PDFs

Sharp copiers write a distinctive PDF header. Check for this string to confirm the source:

```bash
head -c 100 file.pdf | grep -o "Sharp Scanned ImagePDF"
# Output: Sharp Scanned ImagePDF
```

The header also contains `/Filter /DCTDecode` (JPEG) and `/ColorSpace /DeviceGray` for grayscale scans.

### Layout pitfalls
- **Table headers**: In the scan, "交付成果清单" is a merged row in the info table, NOT a standalone heading. Don't add extra paragraph breaks between sections — match the scan's spacing.
- **Font sizes**: Logo (smardaten) ~14pt, main title (项目验收单) ~22pt bold, table content ~10-11pt
- **Color**: The scan is grayscale, so no color info is available. Use default black for text, blue (#005AB5) for the logo for consistency with company branding.
- **Multi-page**: This technique works per-page. For multi-page scans, extract and OCR each page's JPEG separately, then merge DOCX sections.

### Limitations
- Apple Vision OCR accuracy on Sharp scanner grayscale scans is ~85-95% (depends on scan quality)
- Swift script does not detect reading order within table cells (assumes top-to-bottom, left-to-right)
- For complex layouts (nested tables, forms), marker-pdf is preferred when installable
- Coordinate extraction requires writing a custom Swift script — there's no prebuilt tool for it
