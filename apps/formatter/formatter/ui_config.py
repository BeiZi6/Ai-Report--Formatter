from __future__ import annotations

from formatter.config import BodyStyle, FormatConfig, HeadingStyle


def build_format_config(
    *,
    cn_font: str,
    en_font: str,
    heading_font: str,
    heading1_size_pt: int,
    heading2_size_pt: int,
    heading3_size_pt: int,
    heading4_size_pt: int,
    heading_line_spacing: float,
    heading_para_before_lines: float,
    heading_para_after_lines: float,
    body_size_pt: int,
    line_spacing: float,
    para_before_lines: float,
    para_after_lines: float,
    indent_before_chars: int,
    indent_after_chars: int,
    first_line_indent_chars: int,
    justify: bool,
    clear_background: bool,
    page_num_position: str,
) -> FormatConfig:
    body_style = BodyStyle(
        cn_font=cn_font,
        en_font=en_font,
        size_pt=body_size_pt,
        line_spacing=line_spacing,
        para_before_lines=para_before_lines,
        para_after_lines=para_after_lines,
        indent_before_chars=indent_before_chars,
        indent_after_chars=indent_after_chars,
        first_line_indent_chars=first_line_indent_chars,
        justify=justify,
    )

    heading_sizes = [heading1_size_pt, heading2_size_pt, heading3_size_pt, heading4_size_pt]
    heading_styles = {
        level: HeadingStyle(
            font=heading_font,
            size_pt=size,
            line_spacing=heading_line_spacing,
            para_before_lines=heading_para_before_lines,
            para_after_lines=heading_para_after_lines,
        )
        for level, size in zip(range(1, 5), heading_sizes)
    }

    return FormatConfig(
        body_style=body_style,
        heading_styles=heading_styles,
        clear_background=clear_background,
        page_num_position=page_num_position,
    )
