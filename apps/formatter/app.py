from __future__ import annotations

import tempfile

import streamlit as st

from formatter.app_logic import build_preview_payload
from formatter.config import FormatConfig
from formatter.docx_builder import build_docx
from formatter.ui_config import build_format_config


def _apply_theme() -> None:
    st.set_page_config(page_title="AI 报告排版助手", layout="wide")
    st.markdown(
        """
        <style>
        .stApp { background: #f2f7ff; }
        .block-container { padding-top: 2rem; }
        h1, h2, h3, h4, h5, h6 { color: #0b2a4a; }
        .stTextArea textarea { background: #ffffff; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _sidebar_config() -> FormatConfig:
    st.sidebar.header("样式设置")
    cn_font = st.sidebar.text_input("中文字体", value="SimSun")
    en_font = st.sidebar.text_input("英文字体", value="Times New Roman")
    heading_font = st.sidebar.text_input("标题字体", value="SimHei")
    heading1_size = st.sidebar.number_input("标题字号 H1 (pt)", min_value=8, max_value=48, value=14)
    heading2_size = st.sidebar.number_input("标题字号 H2 (pt)", min_value=8, max_value=48, value=14)
    heading3_size = st.sidebar.number_input("标题字号 H3 (pt)", min_value=8, max_value=48, value=14)
    heading4_size = st.sidebar.number_input("标题字号 H4 (pt)", min_value=8, max_value=48, value=14)
    heading_line_spacing = st.sidebar.selectbox(
        "标题行距", [1.0, 1.25, 1.5, 1.75, 2.0], index=1
    )
    heading_para_before = st.sidebar.number_input(
        "标题段前 (行)", min_value=0.0, max_value=10.0, value=0.5, step=0.1
    )
    heading_para_after = st.sidebar.number_input(
        "标题段后 (行)", min_value=0.0, max_value=10.0, value=0.5, step=0.1
    )
    body_size = st.sidebar.number_input("正文字号 (pt)", min_value=8, max_value=32, value=12)
    line_spacing = st.sidebar.selectbox("正文行距", [1.0, 1.25, 1.5, 1.75, 2.0], index=1)
    para_before = st.sidebar.number_input(
        "正文段前 (行)", min_value=0.0, max_value=10.0, value=0.0, step=0.1
    )
    para_after = st.sidebar.number_input(
        "正文段后 (行)", min_value=0.0, max_value=10.0, value=0.0, step=0.1
    )
    indent_before = st.sidebar.number_input(
        "文本之前 (字符)", min_value=0, max_value=10, value=0, step=1
    )
    indent_after = st.sidebar.number_input(
        "文本之后 (字符)", min_value=0, max_value=10, value=0, step=1
    )
    first_line = st.sidebar.number_input(
        "首行缩进 (字符)", min_value=0, max_value=10, value=2, step=1
    )
    justify = st.sidebar.checkbox("两端对齐", value=True)
    clear_bg = st.sidebar.checkbox("清除背景色", value=True)
    page_num_pos = st.sidebar.selectbox("页码位置", ["center", "right"], index=0)

    return build_format_config(
        cn_font=cn_font,
        en_font=en_font,
        heading_font=heading_font,
        heading1_size_pt=int(heading1_size),
        heading2_size_pt=int(heading2_size),
        heading3_size_pt=int(heading3_size),
        heading4_size_pt=int(heading4_size),
        heading_line_spacing=float(heading_line_spacing),
        heading_para_before_lines=float(heading_para_before),
        heading_para_after_lines=float(heading_para_after),
        body_size_pt=body_size,
        line_spacing=float(line_spacing),
        para_before_lines=float(para_before),
        para_after_lines=float(para_after),
        indent_before_chars=int(indent_before),
        indent_after_chars=int(indent_after),
        first_line_indent_chars=int(first_line),
        justify=justify,
        clear_background=clear_bg,
        page_num_position=page_num_pos,
    )


def main() -> None:
    _apply_theme()
    st.title("AI 报告排版助手")
    st.caption("Markdown → Word，适配课题报告排版")

    config = _sidebar_config()

    col_input, col_preview = st.columns(2, gap="large")
    with col_input:
        st.subheader("输入区")
        if st.button("插入示例 Markdown"):
            st.session_state["input_text"] = (
                "# 示例标题\n\n"
                "这是一个示例段落，用于展示 Markdown 转换效果。\n\n"
                "## 二级标题\n\n"
                "- 列表项一\n"
                "- 列表项二\n"
            )
        text = st.text_area("粘贴 Markdown 内容", height=400, key="input_text")
        if not text.strip():
            st.warning("请先输入 Markdown 内容")

    with col_preview:
        st.subheader("结构化预览")
        payload = build_preview_payload(text or "")
        st.write("块数量：", payload["summary"])
        st.write("引用：", payload["refs"])
        st.write("样式参数：", config)

    if st.button("生成并下载 Word 文档", disabled=not text.strip()):
        try:
            with tempfile.NamedTemporaryFile(suffix=".docx") as tmp:
                build_docx(payload["ast"], tmp.name, config=config)
                tmp.seek(0)
                st.download_button(
                    label="下载 Word",
                    data=tmp.read(),
                    file_name="ai-report.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
        except Exception as exc:
            st.error(f"生成失败：{exc}")


if __name__ == "__main__":
    main()
