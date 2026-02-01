# AI 报告排版助手

Streamlit 小工具：将 Markdown 转成 Word 报告，并支持基础结构化预览。

## 运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r apps/formatter/requirements.txt
streamlit run apps/formatter/app.py
```

## 在线部署 (Render)

1. Render 新建 Web Service → 连接 GitHub 仓库
2. Build Command / Start Command 按 render.yaml
3. 等待部署完成获得默认域名

## 绑定阿里云域名

1. Render 添加 Custom Domain
2. 阿里云 DNS 增加 CNAME 指向 Render 给的目标域名
3. 等待生效，HTTPS 自动配置

## 说明

- 当前导出支持标题与段落的基础映射。
- 引用和 LaTeX 转换已提供基础能力。
