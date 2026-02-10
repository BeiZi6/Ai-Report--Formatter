from formatter.ui_config import build_format_config


def test_build_format_config_overrides_heading_sizes():
    config = build_format_config(
        cn_font="SimSun",
        en_font="Times New Roman",
        heading_cn_font="SimHei",
        heading_en_font="Times New Roman",
        heading1_size_pt=18,
        heading2_size_pt=16,
        heading3_size_pt=15,
        heading4_size_pt=14,
        heading_line_spacing=1.5,
        heading_para_before_lines=0.0,
        heading_para_after_lines=0.0,
        body_size_pt=12,
        line_spacing=1.5,
        para_before_lines=0.0,
        para_after_lines=0.0,
        indent_before_chars=0,
        indent_after_chars=0,
        first_line_indent_chars=2,
        justify=True,
        clear_background=True,
        page_num_position="center",
        figure_max_width_cm=12.0,
        figure_align="right",
    )

    assert config.body_style.cn_font == "SimSun"
    assert config.body_style.en_font == "Times New Roman"
    assert config.body_style.size_pt == 12
    assert config.heading_styles[1].cn_font == "SimHei"
    assert config.heading_styles[1].en_font == "Times New Roman"
    assert config.heading_styles[1].size_pt == 18
    assert config.heading_styles[2].size_pt == 16
    assert config.heading_styles[3].size_pt == 15
    assert config.heading_styles[4].size_pt == 14
    assert config.figure_style.max_width_cm == 12.0
    assert config.figure_style.align == "right"


def test_build_format_config_supports_paragraph_spacing_and_indents():
    config = build_format_config(
        cn_font="SimSun",
        en_font="Times New Roman",
        heading_cn_font="SimHei",
        heading_en_font="Times New Roman",
        heading1_size_pt=14,
        heading2_size_pt=14,
        heading3_size_pt=14,
        heading4_size_pt=14,
        heading_line_spacing=1.25,
        heading_para_before_lines=0.5,
        heading_para_after_lines=0.5,
        body_size_pt=12,
        line_spacing=1.25,
        para_before_lines=0.0,
        para_after_lines=0.0,
        indent_before_chars=0,
        indent_after_chars=0,
        first_line_indent_chars=2,
        justify=True,
        clear_background=True,
        page_num_position="center",
        figure_max_width_cm=14.0,
        figure_align="center",
    )

    assert config.body_style.line_spacing == 1.25
    assert config.body_style.para_before_lines == 0.0
    assert config.body_style.para_after_lines == 0.0
    assert config.body_style.indent_before_chars == 0
    assert config.body_style.indent_after_chars == 0
    assert config.body_style.first_line_indent_chars == 2
    assert config.heading_styles[1].size_pt == 14
    assert config.heading_styles[1].line_spacing == 1.25
    assert config.heading_styles[1].para_before_lines == 0.5
    assert config.heading_styles[1].para_after_lines == 0.5
    assert config.figure_style.max_width_cm == 14.0
    assert config.figure_style.align == "center"
