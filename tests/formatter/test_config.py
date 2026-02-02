from formatter.config import FormatConfig, HeadingStyle


def test_default_config_has_heading_styles():
    config = FormatConfig()
    assert set(config.heading_styles.keys()) == {1, 2, 3, 4}
    assert config.heading_styles[1].font
    assert config.heading_styles[1].size_pt > config.body_style.size_pt


def test_heading_styles_can_be_overridden_and_filled():
    config = FormatConfig(
        heading_styles={
            1: HeadingStyle(
                font="Arial",
                size_pt=20,
                line_spacing=1.0,
                para_before_lines=0.0,
                para_after_lines=0.0,
            )
        }
    )
    assert set(config.heading_styles.keys()) == {1, 2, 3, 4}
    assert config.heading_styles[1].font == "Arial"
    assert config.heading_styles[2].font
