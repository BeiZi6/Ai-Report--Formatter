from formatter.latex import latex_to_omml


def test_latex_to_omml_returns_xml_string():
    omml = latex_to_omml("x^2")
    assert omml.strip().startswith("<m:oMath")


def test_latex_to_omml_supports_aligned_environment():
    latex = r"""
\begin{aligned}
f(x) &= (x+1)^2 \\
     &= x^2 + 2x + 1
\end{aligned}
"""
    omml = latex_to_omml(latex)
    assert omml.strip().startswith("<m:oMath")
    assert "begin{aligned}" not in omml
