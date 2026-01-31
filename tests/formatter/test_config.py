from formatter.config import FormatConfig


def test_default_config_has_heading_styles():
    config = FormatConfig()
    assert set(config.heading_styles.keys()) == {1, 2, 3, 4}
    assert config.heading_styles[1].font
    assert config.heading_styles[1].size_pt > config.body_style.size_pt
