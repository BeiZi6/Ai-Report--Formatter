# DOCX Formatting Enhancements Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add Word-style block equation numbering, improve list layout with multilevel numbering/bullets, and default tables to three-line style.

**Architecture:** Keep the existing Markdown AST and rendering pipeline intact. Extend `formatter/docx_builder.py` to add equation-number fields, explicit list indentation/numbering rules, and three-line table borders using OXML. Tests inspect generated docx XML for alignment, numbering fields, and borders.

**Tech Stack:** Python, python-docx, pytest, OXML manipulation.

---

### Task 1: Block equation numbering for math blocks

**Files:**
- Modify: `apps/formatter/formatter/docx_builder.py`
- Test: `tests/formatter/test_docx_builder.py`

**Step 1: Write the failing test**

Add to `tests/formatter/test_docx_builder.py`:

```python
from docx import Document


def test_math_block_adds_equation_number(tmp_path):
    ast = [{"type": "math_block", "latex": "x"}]
    output = tmp_path / "out.docx"
    build_docx(ast, output, FormatConfig())

    doc = Document(output)
    paragraph = doc.paragraphs[0]
    xml = paragraph._p.xml
    assert "SEQ Equation" in xml
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/formatter/test_docx_builder.py::test_math_block_adds_equation_number -v`
Expected: FAIL (no SEQ field yet).

**Step 3: Write minimal implementation**

Update `apps/formatter/formatter/docx_builder.py`:

```python
from docx.shared import Inches


def _add_equation_number(paragraph) -> None:
    # Right-aligned tab stop for equation number
    p_pr = paragraph._p.get_or_add_pPr()
    tabs = OxmlElement("w:tabs")
    tab = OxmlElement("w:tab")
    tab.set(qn("w:val"), "right")
    tab.set(qn("w:pos"), "9350")
    tabs.append(tab)
    p_pr.append(tabs)

    paragraph.add_run("\t(")
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "SEQ Equation")
    paragraph._p.append(fld)
    paragraph.add_run(")")
```

Then in the `math_block` branch of `build_docx`, after `_add_math_run(...)`, call `_add_equation_number(paragraph)`.

**Step 4: Run test to verify it passes**

Run: `pytest tests/formatter/test_docx_builder.py::test_math_block_adds_equation_number -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/formatter/formatter/docx_builder.py tests/formatter/test_docx_builder.py
git commit -m "feat: add equation numbering for math blocks"
```

---

### Task 2: Improve ordered/unordered list layout and numbering

**Files:**
- Modify: `apps/formatter/formatter/docx_builder.py`
- Test: `tests/formatter/test_docx_styles.py`

**Step 1: Write the failing test**

Add to `tests/formatter/test_docx_styles.py`:

```python
from docx import Document
from docx.shared import Pt


def test_list_indents_and_numbering_levels(tmp_path):
    ast = [
        {
            "type": "list",
            "ordered": True,
            "level": 1,
            "start": 1,
            "items": [
                [{"type": "paragraph", "text": "第一项"}],
                [
                    {
                        "type": "list",
                        "ordered": True,
                        "level": 2,
                        "start": 1,
                        "items": [[{"type": "paragraph", "text": "子项"}]],
                    }
                ],
            ],
        }
    ]
    output = tmp_path / "out.docx"
    build_docx(ast, output, FormatConfig())

    doc = Document(output)
    first = doc.paragraphs[0]
    nested = doc.paragraphs[1]
    assert first.paragraph_format.left_indent == Pt(18)
    assert nested.paragraph_format.left_indent == Pt(36)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/formatter/test_docx_styles.py::test_list_indents_and_numbering_levels -v`
Expected: FAIL (no custom indents applied).

**Step 3: Write minimal implementation**

Update `apps/formatter/formatter/docx_builder.py`:

```python
LIST_INDENT_PT = 18


def _apply_list_indents(paragraph, level: int) -> None:
    paragraph.paragraph_format.left_indent = Pt(LIST_INDENT_PT * level)
    paragraph.paragraph_format.first_line_indent = Pt(-LIST_INDENT_PT / 2)
```

Call `_apply_list_indents(...)` inside `_add_list` for each list paragraph using `node.get("level", 1)`.

**Step 4: Run test to verify it passes**

Run: `pytest tests/formatter/test_docx_styles.py::test_list_indents_and_numbering_levels -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/formatter/formatter/docx_builder.py tests/formatter/test_docx_styles.py
git commit -m "feat: improve list indent layout"
```

---

### Task 3: Default tables to three-line style

**Files:**
- Modify: `apps/formatter/formatter/docx_builder.py`
- Test: `tests/formatter/test_docx_builder.py`

**Step 1: Write the failing test**

Add to `tests/formatter/test_docx_builder.py`:

```python
from docx import Document


def test_table_uses_three_line_style(tmp_path):
    ast = [
        {
            "type": "table",
            "align": ["left"],
            "header": [{"text": "列1"}],
            "rows": [[{"text": "A"}]],
        }
    ]
    output = tmp_path / "out.docx"
    build_docx(ast, output, FormatConfig())

    doc = Document(output)
    tbl_xml = doc.tables[0]._tbl.xml
    assert "w:tblBorders" in tbl_xml
    assert "insideV" not in tbl_xml
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/formatter/test_docx_builder.py::test_table_uses_three_line_style -v`
Expected: FAIL (grid borders still present).

**Step 3: Write minimal implementation**

Update `_add_table` in `apps/formatter/formatter/docx_builder.py` to replace the table borders with:
- `top` line
- `bottom` line
- `insideH` = none
- `insideV` = none
- header row bottom border

```python
from docx.oxml import OxmlElement


def _apply_three_line_table(table) -> None:
    tbl_pr = table._tbl.get_or_add_tblPr()
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "bottom"):
        elem = OxmlElement(f"w:{edge}")
        elem.set(qn("w:val"), "single")
        elem.set(qn("w:sz"), "8")
        elem.set(qn("w:color"), "000000")
        borders.append(elem)
    for edge in ("left", "right", "insideH", "insideV"):
        elem = OxmlElement(f"w:{edge}")
        elem.set(qn("w:val"), "nil")
        borders.append(elem)
    tbl_pr.append(borders)
```

Call `_apply_three_line_table(table)` after table creation, and apply a bottom border to the header row cells.

**Step 4: Run test to verify it passes**

Run: `pytest tests/formatter/test_docx_builder.py::test_table_uses_three_line_style -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/formatter/formatter/docx_builder.py tests/formatter/test_docx_builder.py
git commit -m "feat: apply three-line table style"
```
