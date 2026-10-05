# Widescreen Card-Layout PPT Pattern (python-pptx)

A reusable pattern for creating 16:9 widescreen presentations with card-based layouts, colored sections, tables, and summary slides. Based on the `python-pptx-scratch.md` techniques but organized as a specific deck template.

## Template Structure (12-slide deck pattern)

| Slide | Type | Purpose |
|-------|------|---------|
| 1 | Cover | Dark background, title, subtitle, tagline |
| 2 | Table of Contents | Numbered list of sections |
| 3-4 | Info slides | Project overview tables, business content |
| 5 | Problem/Challenge | Red/Orange warning cards for issues |
| 6-7 | Methodology | Research/analysis dimensions, stakeholder tables |
| 8-9 | Solution/Action | Step-by-step cards, before/after comparison |
| 10-11 | Results+Highlights | Metrics callouts, summary cards |
| 12 | Conclusion | Key path visualization, dual success summary |

## Color Palette Setup

```python
BLUE_DARK  = RGBColor(0x1B, 0x3A, 0x5C)  # cover/cards
BLUE_MID   = RGBColor(0x2C, 0x5F, 0x8A)  # tables/headers
BLUE_LIGHT = RGBColor(0x3A, 0x7C, 0xBD)  # secondary cards
BLUE_ACCENT= RGBColor(0x5B, 0xA0, 0xD9)  # accent text/lines
ORANGE     = RGBColor(0xE8, 0x6C, 0x00)  # warning/highlight
GREEN      = RGBColor(0x27, 0xAE, 0x60)  # success
RED        = RGBColor(0xE7, 0x4C, 0x3C)  # problem
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY = RGBColor(0xF0, 0xF2, 0xF5)  # table alt rows
DARK       = RGBColor(0x2C, 0x3E, 0x50)  # body text
GRAY_TEXT  = RGBColor(0x7F, 0x8C, 0x8D)  # secondary text
```

## Reusable Helper Functions

These should be defined once at the top of your script:

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def add_bg(slide, color):
    """Set slide background to solid color."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_shape(slide, left, top, width, height, color):
    """Add a solid rectangle."""
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape

def add_rounded_shape(slide, left, top, width, height, color):
    """Add a rounded rectangle (card background)."""
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape

def add_text_box(slide, left, top, width, height, text,
                 font_size=18, color=RGBColor(0,0,0), bold=False,
                 align=PP_ALIGN.LEFT, font_name='Microsoft YaHei'):
    """Add a single-line text box."""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = color
    p.font.bold = bold
    p.font.name = font_name
    p.alignment = align
    return txBox

def add_multiline_box(slide, left, top, width, height, lines,
                      font_size=14, color=RGBColor(0,0,0)):
    """Add a multi-line text box. 'lines' is a list of strings."""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.font.size = Pt(font_size)
        p.font.color.rgb = color
        p.font.name = 'Microsoft YaHei'
        p.space_after = Pt(4)
    return txBox

def add_table(slide, left, top, width, height, rows, cols, data,
              header_color, font_size=12):
    """Add a styled table. data[0] is the header row."""
    table_shape = slide.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table
    for ri, row in enumerate(data):
        for ci, cell_text in enumerate(row):
            cell = table.cell(ri, ci)
            cell.text = str(cell_text)
            for paragraph in cell.text_frame.paragraphs:
                paragraph.font.size = Pt(font_size)
                paragraph.font.name = 'Microsoft YaHei'
                if ri == 0:
                    paragraph.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                    paragraph.font.bold = True
                    paragraph.alignment = PP_ALIGN.CENTER
                else:
                    paragraph.font.color.rgb = RGBColor(0x2C, 0x3E, 0x50)
            if ri == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = header_color
            elif ri % 2 == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(0xF0, 0xF2, 0xF5)
    return table_shape
```

## Card Layout Patterns

### 3-column Card Grid
```python
cards = [('Title1', 'desc...', COLOR1), ('Title2', 'desc...', COLOR2), ...]
for i, (title, desc, color) in enumerate(cards):
    x = 0.8 + i * 4.1
    card = add_rounded_shape(slide, Inches(x), Inches(1.3), Inches(3.8), Inches(4.0), color)
    add_text_box(slide, Inches(x + 0.2), Inches(1.5), Inches(3.4), Inches(0.4),
                 title, 18, WHITE, True, PP_ALIGN.CENTER)
    add_text_box(slide, Inches(x + 0.3), Inches(2.2), Inches(3.2), Inches(2.5),
                 desc, 12, LIGHT_TEXT_COLOR, False, PP_ALIGN.CENTER)
```

### 5-column Mini Cards
```python
for i, (icon, title, desc, color) in enumerate(cards):
    x = 0.8 + i * 2.4
    add_rounded_shape(slide, Inches(x), Inches(1.9), Inches(2.1), Inches(2.5), color)
    add_text_box(slide, Inches(x + 0.2), Inches(2.1), Inches(1.7), Inches(0.5),
                 icon, 32, WHITE, True, PP_ALIGN.CENTER)
```

### Before/After Comparison
```python
# Left column - "before"
add_rounded_shape(slide, Inches(0.8), Inches(1.8), Inches(5.5), Inches(2.0), RED_BG)
add_multiline_box(slide, Inches(1.0), Inches(2.0), Inches(5.0), ..., 'before lines')

# Right column - "after"
add_rounded_shape(slide, Inches(6.8), Inches(1.8), Inches(5.5), Inches(2.0), GREEN_BG)
add_multiline_box(slide, Inches(7.0), Inches(2.0), Inches(5.0), ..., 'after lines')
```

### Metric Callouts (large numbers)
```python
metrics = [('💰 Title', '110+', GREEN), ...]
for i, (title, value, color) in enumerate(metrics):
    x = 1.5 + i * 3.8
    add_rounded_shape(slide, Inches(x), Inches(1.3), Inches(3.2), Inches(1.8), color)
    add_text_box(slide, Inches(x + 0.2), Inches(1.5), ..., title, 14, WHITE, True, PP_ALIGN.CENTER)
    add_text_box(slide, Inches(x + 0.2), Inches(2.0), ..., value, 28, WHITE, True, PP_ALIGN.CENTER)
```

### Process Flow Path
```python
items = ['📋 Step1', '→', '🔍 Step2', '→', ...]
for i, item in enumerate(items):
    if item == '→':
        add_text_box(slide, Inches(x), ..., '→', 20, ACCENT, True, PP_ALIGN.CENTER)
    else:
        add_rounded_shape(slide, Inches(x), ..., Inches(1.0), Inches(0.7), BLUE_MID)
        add_text_box(slide, ..., item, 9, WHITE, True, PP_ALIGN.CENTER)
```

## Color Conventions for Impact

| Section | Background | Text Color | Effect |
|---------|-----------|------------|--------|
| Cover/conclusion slides | Dark blue (.1B3A5C) | White + accent | Professional, high-impact |
| Problem slides | Red/Orange cards | White + light red | Creates urgency |
| Solution slides | Blue gradient | White + light blue | Trust/competence |
| Results/metrics | Green cards | White | Positive outcome |
| Content slides | White background | Dark text | Readability |
