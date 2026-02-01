# Docx Styles Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Write body and heading styles into exported .docx (fonts, sizes, spacing, alignment, margins, page number) using the formatter config.

**Architecture:** Extend `FormatConfig` with body and per-heading style settings. Update `docx_builder` to apply styles (`Normal`, `Heading 1–4`) and paragraph overrides (indent/justify), plus margins and footer page number.

**Tech Stack:** Python, python-docx, pytest.

---

### Task 1: Expand Config Model (Body + Heading Styles)

**Files:**
- Modify: `apps/formatter/formatter/config.py`
- Create: `tests/formatter/test_config.py`

**Step 1: Write the failing test**

```python
from formatter.config import FormatConfig


def test_default_config_has_heading_styles():
    config = FormatConfig()
    assert set(config.heading_styles.keys()) == {1, 2, 3, 4}
    assert config.heading_styles[1].font
    assert config.heading_styles[1].size_pt > config.body_style.size_pt
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/formatter/test_config.py::test_default_config_has_heading_styles -v`
Expected: FAIL (no heading_styles/body_style yet)

**Step 3: Write minimal implementation**

```python
from dataclasses import dataclass, field


@dataclass
class BodyStyle:
    cn_font: str = "SimSun"
    en_font: str = "Times New Roman"
    size_pt: int = 12
    line_spacing: float = 1.5
    para_before_pt: int = 0
    para_after_pt: int = 0
    first_line_indent: bool = True
    justify: bool = True


@dataclass
class HeadingStyle:
    font: str
    size_pt: int
    line_spacing: float
    para_before_pt: int
    para_after_pt: int


@dataclass
class FormatConfig:
    body_style: BodyStyle = field(default_factory=BodyStyle)
    heading_styles: dict[int, HeadingStyle] = field(default_factory=dict)
    clear_background: bool = True
    page_num_position: str = "center"

    def __post_init__(self):
        if not self.heading_styles:
            base = self.body_style
            self.heading_styles = {
                1: HeadingStyle(font=base.cn_font, size_pt=16, line_spacing=base.line_spacing, para_before_pt=6, para_after_pt=6),
                2: HeadingStyle(font=base.cn_font, size_pt=14, line_spacing=base.line_spacing, para_before_pt=6, para_after_pt=6),
                3: HeadingStyle(font=base.cn_font, size_pt=13, line_spacing=base.line_spacing, para_before_pt=6, para_after_pt=6),
                4: HeadingStyle(font=base.cn_font, size_pt=12, line_spacing=base.line_spacing, para_before_pt=6, para_after_pt=6),
            }
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/formatter/test_config.py::test_default_config_has_heading_styles -v`
Expected: PASS

**Step 5: Commit**

```bash
git add apps/formatter/formatter/config.py tests/formatter/test_config.py
git commit -m "feat: expand formatter config for docx styles"
```

---

### Task 2: Docx Style Application (Normal + Heading 1–4)

**Files:**
- Modify: `apps/formatter/formatter/docx_builder.py`
- Modify: `tests/formatter/test_docx_builder.py`
- Create: `tests/formatter/test_docx_styles.py`

**Step 1: Write the failing test**

```python
from docx import Document
from docx.shared import Cm, Pt
from formatter.config import FormatConfig
from formatter.docx_builder import build_docx


def test_docx_styles_and_margins_applied(tmp_path):
    config = FormatConfig()
    output = tmp_path / "out.docx"
    ast = [
        {"type": "heading", "level": 1, "text": "Title"},
        {"type": "paragraph", "text": "Hello"},
    ]
    build_docx(ast, output, config)

    doc = Document(output)
    section = doc.sections[0]
    assert int(section.top_margin) == int(Cm(2.54))
    assert int(section.left_margin) == int(Cm(3.18))

    normal = doc.styles["Normal"]
    assert normal.font.size == Pt(config.body_style.size_pt)

    h1 = doc.styles["Heading 1"]
    assert h1.font.size == Pt(config.heading_styles[1].size_pt)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/formatter/test_docx_styles.py::test_docx_styles_and_margins_applied -v`
Expected: FAIL (missing config/margins/style updates)

**Step 3: Write minimal implementation**

```python
from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

from formatter.config import FormatConfig


def _set_style_fonts(style, ascii_font: str, east_asia_font: str | None = None):
    style.font.name = ascii_font
    rfonts = style.element.rPr.rFonts
    rfonts.set(qn("w:ascii"), ascii_font)
    rfonts.set(qn("w:hAnsi"), ascii_font)
    if east_asia_font:
        rfonts.set(qn("w:eastAsia"), east_asia_font)


def _apply_style_paragraph(style, size_pt, line_spacing, before_pt, after_pt, align=None):
    style.font.size = Pt(size_pt)
    pf = style.paragraph_format
    pf.space_before = Pt(before_pt)
    pf.space_after = Pt(after_pt)
    pf.line_spacing = line_spacing
    if align is not None:
        pf.alignment = align


def _add_page_number(section, position):
    footer = section.footer
    paragraph = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    run = paragraph.add_run()
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    run._r.append(fld)


def build_docx(ast: list[dict], output_path, config: FormatConfig | None = None) -> None:
    config = config or FormatConfig()
    doc = Document()

    section = doc.sections[0]
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(3.18)
    section.right_margin = Cm(3.18)

    try:
        _add_page_number(section, config.page_num_position)
    except Exception:
        pass

    try:
        normal = doc.styles["Normal"]
        _set_style_fonts(normal, config.body_style.en_font, config.body_style.cn_font)
        _apply_style_paragraph(
            normal,
            config.body_style.size_pt,
            config.body_style.line_spacing,
            config.body_style.para_before_pt,
            config.body_style.para_after_pt,
            WD_PARAGRAPH_ALIGNMENT.JUSTIFY if config.body_style.justify else None,
        )

        for level, hstyle in config.heading_styles.items():
            h = doc.styles[f"Heading {level}"]
            _set_style_fonts(h, hstyle.font, hstyle.font)
            _apply_style_paragraph(h, hstyle.size_pt, hstyle.line_spacing, hstyle.para_before_pt, hstyle.para_after_pt)
    except Exception:
        pass

    for node in ast:
        if node.get("type") == "heading":
            doc.add_heading(node.get("text", ""), level=node.get("level", 1))
        elif node.get("type") == "paragraph":
            p = doc.add_paragraph(node.get("text", ""))
            if config.body_style.justify:
                p.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
            if config.body_style.first_line_indent:
                p.paragraph_format.first_line_indent = Pt(config.body_style.size_pt * 2)

    doc.save(output_path)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/formatter/test_docx_styles.py::test_docx_styles_and_margins_applied -v`
Expected: PASS

**Step 5: Commit**

```bash
git add apps/formatter/formatter/docx_builder.py tests/formatter/test_docx_builder.py tests/formatter/test_docx_styles.py
git commit -m "feat: apply docx styles and margins"
```

---

### Task 3: Page Number Field Presence (XML Check)

**Files:**
- Create: `tests/formatter/test_docx_footer.py`

**Step 1: Write the failing test**

```python
from formatter.config import FormatConfig
from formatter.docx_builder import build_docx
from docx import Document


def test_footer_contains_page_field(tmp_path):
    output = tmp_path / "out.docx"
    build_docx([{"type": "paragraph", "text": "Hello"}], output, FormatConfig())
    doc = Document(output)
    footer_xml = doc.sections[0].footer._element.xml
    assert "PAGE" in footer_xml
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/formatter/test_docx_footer.py::test_footer_contains_page_field -v`
Expected: FAIL (field missing or not inserted)

**Step 3: Write minimal implementation**

If failing, adjust `_add_page_number` or fallback behavior in `build_docx`.

**Step 4: Run test to verify it passes**

Run: `pytest tests/formatter/test_docx_footer.py::test_footer_contains_page_field -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/formatter/test_docx_footer.py apps/formatter/formatter/docx_builder.py
git commit -m "test: verify footer page number field"
```

---

### Task 4: UI Pass-Through for New Config

**Files:**
- Modify: `apps/formatter/app.py`

**Step 1: Write the failing test**

```python
from formatter.config import FormatConfig, HeadingStyle


def test_heading_styles_can_be_overridden():
    config = FormatConfig(heading_styles={1: HeadingStyle(font="Arial", size_pt=20, line_spacing=1.0, para_before_pt=0, para_after_pt=0)})
    assert config.heading_styles[1].font == "Arial"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/formatter/test_config.py::test_heading_styles_can_be_overridden -v`
Expected: FAIL (override not respected)

**Step 3: Write minimal implementation**

Ensure `FormatConfig.__post_init__` preserves provided `heading_styles` and fills missing levels (2–4) with defaults.

**Step 4: Run test to verify it passes**

Run: `pytest tests/formatter/test_config.py::test_heading_styles_can_be_overridden -v`
Expected: PASS

**Step 5: Commit**

```bash
git add apps/formatter/formatter/config.py tests/formatter/test_config.py
git commit -m "feat: support per-heading overrides"
```

---

### Task 5: Final Test Run

**Step 1: Run tests**

Run: `pytest -v`
Expected: PASS

**Step 2: Commit (if needed)**

```bash
git add -A
git commit -m "test: green test suite"
```
