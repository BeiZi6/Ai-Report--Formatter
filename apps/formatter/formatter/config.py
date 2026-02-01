from __future__ import annotations

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


def _default_heading_styles(base: BodyStyle) -> dict[int, HeadingStyle]:
    return {
        1: HeadingStyle(
            font=base.cn_font,
            size_pt=16,
            line_spacing=base.line_spacing,
            para_before_pt=6,
            para_after_pt=6,
        ),
        2: HeadingStyle(
            font=base.cn_font,
            size_pt=14,
            line_spacing=base.line_spacing,
            para_before_pt=6,
            para_after_pt=6,
        ),
        3: HeadingStyle(
            font=base.cn_font,
            size_pt=13,
            line_spacing=base.line_spacing,
            para_before_pt=6,
            para_after_pt=6,
        ),
        4: HeadingStyle(
            font=base.cn_font,
            size_pt=12,
            line_spacing=base.line_spacing,
            para_before_pt=6,
            para_after_pt=6,
        ),
    }


@dataclass
class FormatConfig:
    body_style: BodyStyle = field(default_factory=BodyStyle)
    heading_styles: dict[int, HeadingStyle] = field(default_factory=dict)
    clear_background: bool = True
    page_num_position: str = "center"

    def __post_init__(self) -> None:
        defaults = _default_heading_styles(self.body_style)
        if not self.heading_styles:
            self.heading_styles = defaults
            return
        for level, style in defaults.items():
            self.heading_styles.setdefault(level, style)
