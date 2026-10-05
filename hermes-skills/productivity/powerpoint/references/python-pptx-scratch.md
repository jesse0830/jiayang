# Creating Presentations from Scratch with python-pptx

Use this approach when the user doesn't have Node.js/pptxgenjs or when you want to avoid the npm dependency.

## When to Use

- User requests a PPT but doesn't have pptxgenjs installed
- You're in a Python-only environment
- The deck has many slides with similar structure (tables, cards, repeated layouts)

## Setup

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
```

## Important: execute_code vs terminal for python-pptx

python-pptx depends on `lxml`, which may not work inside Hermes's `execute_code` sandbox due to import path issues. **Always write the script to a temp file and run via `terminal()` instead**.

## Modifying Existing PPTs with Slide Backup

When the user says "修改这一页，保留原来那一页做备份" (modify this slide, keep the original as backup):

1. **Duplicate slide 0 as backup** using XML deep-copy (NOT `add_slide.py`, since we work with python-pptx directly)
2. **Modify slide 0** in-place (update table cells, text boxes, etc.)
3. The backup slide will be at the end. If slide order matters, use unpack/edit/pack instead.

```python
from pptx import Presentation
from copy import deepcopy

prs = Presentation('input.pptx')

def duplicate_slide(prs, source_slide):
    layout = source_slide.slide_layout
    new_slide = prs.slides.add_slide(layout)
    for shape in list(new_slide.shapes):
        shape._element.getparent().remove(shape._element)
    spTree = source_slide.shapes._spTree
    for child in list(spTree):
        tag = child.tag
        if tag.endswith('}sp') or tag.endswith('}pic') or \
           tag.endswith('}graphicFrame') or tag.endswith('}grpSp'):
            new_slide.shapes._spTree.append(deepcopy(child))
    return new_slide

# Step 1: Backup
backup = duplicate_slide(prs, prs.slides[0])

# Step 2: Modify slide 0
slide0 = prs.slides[0]
# Update title
for shape in slide0.shapes:
    if hasattr(shape, 'text') and '原标题' in shape.text:
        shape.text = '新标题'
        break

# Update table cells
table = slide0.shapes[2].table  # adjust index
def set_cell(cell, text, font_size=9):
    p = cell.text_frame.paragraphs[0]
    p.clear()
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.name = '微软雅黑'
    cell.word_wrap = True

for r in range(rows):
    for c in range(cols):
        set_cell(table.cell(r, c), new_data[r][c])

prs.save('output.pptx')
```

## Key Patterns

### Slide background

```python
slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank layout
bg = slide.background
fill = bg.fill
fill.solid()
fill.fore_color.rgb = RGBColor(0x1B, 0x3A, 0x5C)  # dark blue
```

### Shapes (rectangles, rounded rects)

```python
shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
shape.fill.solid()
shape.fill.fore_color.rgb = color
shape.line.fill.background()  # no border
```

### Text boxes

```python
txBox = slide.shapes.add_textbox(left, top, width, height)
tf = txBox.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "Hello"
p.font.size = Pt(18)
p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
p.font.bold = True
p.font.name = 'Microsoft YaHei'
p.alignment = PP_ALIGN.CENTER
```

### Multi-line text

```python
lines = ["Line 1", "Line 2", "Line 3"]
for i, line in enumerate(lines):
    if i == 0:
        p = tf.paragraphs[0]
    else:
        p = tf.add_paragraph()
    p.text = line
    p.font.size = Pt(14)
    p.space_after = Pt(4)
```

### Tables

```python
table_shape = slide.shapes.add_table(rows, cols, left, top, width, height)
table = table_shape.table
for ri, row_data in enumerate(data):
    for ci, cell_text in enumerate(row_data):
        cell = table.cell(ri, ci)
        cell.text = str(cell_text)
        # Style header row
        if ri == 0:
            for p in cell.text_frame.paragraphs:
                p.font.color.rgb = WHITE
                p.font.bold = True
            cell.fill.solid()
            cell.fill.fore_color.rgb = HEADER_COLOR
        # Alternating row colors
        elif ri % 2 == 0:
            cell.fill.solid()
            cell.fill.fore_color.rgb = LIGHT_GRAY
```

## Common Layout Sizes

```python
# Widescreen 16:9 is default (13.333" x 7.5")
# To set explicitly:
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
```

## Important Notes

- **Do NOT reuse `Presentation()` across multiple scripts** — each script produces one file
- **Do NOT use `from hermes_tools import ...` for pptx** — install python-pptx globally with `pip install python-pptx`
- **CJK font rendering (critical!)** — setting `font.name` alone is NOT enough for Chinese text on macOS/Linux. python-pptx writes the font name into the document but the actual rendering glyph selection is governed by XML attributes. The **correct** approach:

```python
from pptx.oxml.ns import qn

def set_cn_font(run, font_name='宋体'):
    \"\"\"Set Chinese font properly — required for CJK text to render on Mac/Win.\"\"\"
    run.font.name = font_name
    rPr = run._r.get_or_add_rPr()
    rPr.set(qn('w:eaTypeface'), font_name)   # East Asian typeface
    rPr.set(qn('w:csTypeface'), font_name)   # Complex script typeface
```

Do NOT use `qn('w:eastAsia')` — that is incorrect XML. The real attribute is `w:eaTypeface`.

- **Use this helper for single-paragraph text boxes** — cleaner than `clear()` + rebuild:

```python
def set_para_text(tf, text, size, color, bold=False):
    \"\"\"Set the first paragraph of a text frame with full font control.\"\"\"
    tf.clear()
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.color.rgb = color
    run.font.bold = bold
    set_cn_font(run)
```

- **Tables are sized by the `width`/`height` parameter** — column widths auto-distribute. To control column widths, set `table.columns[0].width = Cm(3)` after creation
- **Use `slide.shapes.add_shape()` for decorative elements** — colored rectangles, dividers, card backgrounds
- **Text box padding** — text boxes have ~0.1" internal padding by default. Account for this when aligning shapes with text
- **QA via subagent** — convert to PDF/images and inspect visually. The skill's `Converting to Images` section works for any .pptx
