// biome-ignore-all lint/security/noDangerouslySetInnerHtml: preview rendering requires HTML fragments generated from local backend parsing.
"use client";

import { motion } from "framer-motion";
import { type CSSProperties, useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";

import { fetchExportStats, fetchPreview, generateDocx } from "../lib/api";

type PreviewPayload = {
  summary?: {
    headings?: number;
    paragraphs?: number;
  };
  refs?: string[];
  preview_html?: string;
};

type ExportStats = {
  today: number;
  total: number;
};

type FormatConfig = {
  cn_font: string;
  en_font: string;
  heading_cn_font: string;
  heading_en_font: string;
  heading1_size_pt: number;
  heading2_size_pt: number;
  heading3_size_pt: number;
  heading4_size_pt: number;
  heading_line_spacing: number;
  heading_para_before_lines: number;
  heading_para_after_lines: number;
  body_size_pt: number;
  line_spacing: number;
  para_before_lines: number;
  para_after_lines: number;
  indent_before_chars: number;
  indent_after_chars: number;
  first_line_indent_chars: number;
  justify: boolean;
  clear_background: boolean;
  page_num_position: string;
};

const DEFAULT_CONFIG: FormatConfig = {
  cn_font: "SimSun",
  en_font: "Times New Roman",
  heading_cn_font: "SimHei",
  heading_en_font: "Times New Roman",
  heading1_size_pt: 14,
  heading2_size_pt: 14,
  heading3_size_pt: 14,
  heading4_size_pt: 14,
  heading_line_spacing: 1.25,
  heading_para_before_lines: 0.5,
  heading_para_after_lines: 0.5,
  body_size_pt: 12,
  line_spacing: 1.25,
  para_before_lines: 0,
  para_after_lines: 0,
  indent_before_chars: 0,
  indent_after_chars: 0,
  first_line_indent_chars: 2,
  justify: true,
  clear_background: true,
  page_num_position: "center",
};

const PREVIEW_PAGE_WIDTH = 794;
const PREVIEW_PAGE_HEIGHT = 1123;

const fadeUp = {
  hidden: { opacity: 0, y: 12 },
  visible: (delay = 0) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.45, ease: [0.16, 1, 0.3, 1] as const, delay },
  }),
};

function StatusPill({ label }: { label: string }) {
  return (
    <div className="status-pill" aria-live="polite">
      <span className="dot-pulse" aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
}

type WaveRibbonProps = {
  status: string;
  onGenerate: () => void;
  disabled: boolean;
};

function WaveRibbon({ status, onGenerate, disabled }: WaveRibbonProps) {
  return (
    <div className="wave-wrap" aria-hidden={false}>
      <motion.div
        className="wave-track"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
      >
        <motion.div
          className="wave-line"
          animate={{ translateY: [0, -8, 0, 10, 0] }}
          transition={{ repeat: Infinity, duration: 14, ease: "easeInOut" }}
        />
        <motion.div
          className="wave-glow"
          animate={{ translateX: ["-10%", "110%"] }}
          transition={{ repeat: Infinity, duration: 6, ease: "linear" }}
        />
      </motion.div>

      <div className="wave-content">
        <div className="wave-meta">
          <span className="label">DEV · Monochrome</span>
          <span className="wave-status">{status}</span>
        </div>
        <div className="wave-verse" aria-hidden="true">
          <span className="verse-text">我失骄杨君失柳,杨柳轻飏直上重霄九</span>
        </div>
        <div className="wave-actions">
          <button
            type="button"
            className="primary-btn strong"
            onClick={onGenerate}
            disabled={disabled}
            aria-disabled={disabled}
          >
            {disabled ? "待输入" : "生成 Word"}
          </button>
        </div>
      </div>
    </div>
  );
}

type MeasurePage = {
  content: HTMLDivElement;
};

const createMeasurePage = (host: HTMLDivElement): MeasurePage => {
  const page = document.createElement("div");
  page.className = "preview-page-measure";

  const content = document.createElement("div");
  content.className = "preview-page-content";

  page.appendChild(content);
  host.appendChild(page);

  return { content };
};

export default function Home() {
  const [markdown, setMarkdown] = useState("");
  const [preview, setPreview] = useState<PreviewPayload | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exportStats, setExportStats] = useState<ExportStats | null>(null);
  const [config, setConfig] = useState<FormatConfig>(DEFAULT_CONFIG);
  const [previewPages, setPreviewPages] = useState<string[]>([]);
  const [previewScale, setPreviewScale] = useState(1);
  const [hasDesktopLogExport, setHasDesktopLogExport] = useState(false);
  const [logExportMessage, setLogExportMessage] = useState<string | null>(null);
  const previewMeasureRef = useRef<HTMLDivElement | null>(null);
  const previewViewportRef = useRef<HTMLDivElement | null>(null);
  const fontSizeOptions = [
    { label: "小四 (12pt)", value: 12 },
    { label: "四号 (14pt)", value: 14 },
    { label: "小三 (16pt)", value: 16 },
    { label: "三号 (18pt)", value: 18 },
    { label: "二号 (22pt)", value: 22 },
  ];
  const lineSpacingOptions = [1, 1.25, 1.5, 1.75, 2];

  const isEmpty = markdown.trim().length === 0;

  const refreshExportStats = useCallback(async () => {
    try {
      const data = await fetchExportStats();
      setExportStats(data);
    } catch {
      setExportStats(null);
    }
  }, []);

  useEffect(() => {
    refreshExportStats();
  }, [refreshExportStats]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    setHasDesktopLogExport(typeof window.desktop?.exportLogs === "function");
  }, []);

  useEffect(() => {
    if (isEmpty) {
      setPreview(null);
      setError(null);
      return;
    }

    const controller = new AbortController();
    const handle = window.setTimeout(async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await fetchPreview(markdown, controller.signal);
        setPreview(data);
      } catch (err) {
        if (err instanceof DOMException && err.name === "AbortError") {
          return;
        }
        setError("预览失败，请检查接口连接");
      } finally {
        setIsLoading(false);
      }
    }, 350);

    return () => {
      window.clearTimeout(handle);
      controller.abort();
    };
  }, [markdown, isEmpty]);

  useEffect(() => {
    const viewport = previewViewportRef.current;
    if (!viewport) {
      return;
    }

    const updateScale = () => {
      const styles = window.getComputedStyle(viewport);
      const paddingX =
        Number.parseFloat(styles.paddingLeft) + Number.parseFloat(styles.paddingRight);
      const availableWidth = viewport.clientWidth - paddingX;
      if (!availableWidth || Number.isNaN(availableWidth)) {
        return;
      }
      const nextScale = Math.min(1, availableWidth / PREVIEW_PAGE_WIDTH);
      setPreviewScale((prev) => (Math.abs(prev - nextScale) < 0.01 ? prev : nextScale));
    };

    updateScale();
    const observer = new ResizeObserver(updateScale);
    observer.observe(viewport);

    return () => {
      observer.disconnect();
    };
  }, []);

  useLayoutEffect(() => {
    if (!preview?.preview_html) {
      setPreviewPages([]);
      return;
    }

    const host = previewMeasureRef.current;
    if (!host) {
      return;
    }

    host.innerHTML = "";
    const parser = new DOMParser();
    const doc = parser.parseFromString(preview.preview_html, "text/html");
    const nodes = Array.from(doc.body.children);

    if (nodes.length === 0) {
      setPreviewPages([preview.preview_html]);
      return;
    }

    const pages: string[] = [];
    let currentPage = createMeasurePage(host);

    for (const node of nodes) {
      currentPage.content.appendChild(node);
      if (
        currentPage.content.scrollHeight > PREVIEW_PAGE_HEIGHT + 1 &&
        currentPage.content.childElementCount > 1
      ) {
        currentPage.content.removeChild(node);
        pages.push(currentPage.content.innerHTML);
        currentPage = createMeasurePage(host);
        currentPage.content.appendChild(node);
      }
    }

    if (currentPage.content.childElementCount > 0) {
      pages.push(currentPage.content.innerHTML);
    }

    setPreviewPages(pages);
  }, [preview?.preview_html]);

  const headingCount = preview?.summary?.headings ?? 0;
  const paragraphCount = preview?.summary?.paragraphs ?? 0;
  const refCount = preview?.refs?.length ?? 0;
  const estimatedPages = useMemo(() => {
    if (!paragraphCount) return 0;
    return Math.max(1, Math.ceil(paragraphCount / 6));
  }, [paragraphCount]);

  const statusLabel = useMemo(() => {
    if (isGenerating) return "正在导出";
    if (isLoading) return "分析中…";
    if (error) return "预览失败";
    if (isEmpty) return "等待输入";
    return "已更新";
  }, [error, isEmpty, isGenerating, isLoading]);

  const handleGenerate = async () => {
    if (isEmpty || isGenerating) return;
    setIsGenerating(true);
    setError(null);
    try {
      const blob = await generateDocx(markdown, config);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "ai-report.docx";
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      setError("导出失败，请稍后重试");
    } finally {
      setIsGenerating(false);
      refreshExportStats();
    }
  };

  const handleExportLogs = async () => {
    if (typeof window === "undefined" || !window.desktop?.exportLogs) {
      setLogExportMessage("当前环境不支持日志导出");
      return;
    }

    try {
      const result = await window.desktop.exportLogs();
      if (result.ok) {
        setLogExportMessage(
          result.filePath ? `日志已导出：${result.filePath}` : "日志已成功导出",
        );
        return;
      }

      if (result.cancelled) {
        setLogExportMessage("已取消日志导出");
        return;
      }

      setLogExportMessage(result.error ? `日志导出失败：${result.error}` : "日志导出失败");
    } catch {
      setLogExportMessage("日志导出失败");
    }
  };

  return (
    <div className="page">
      <a className="skip-link" href="#main-content">
        跳到主要内容
      </a>
      <div className="scanline-band" aria-hidden="true" />

      <WaveRibbon status={statusLabel} onGenerate={handleGenerate} disabled={isEmpty || isGenerating} />

      <motion.header
        className="hero"
        variants={fadeUp}
        initial="hidden"
        animate="visible"
        custom={0}
      >
        <div className="hero-badge">FastAPI · Next.js · Word</div>
        <h1 className="hero-title">AI 报告排版助手</h1>
        <p className="hero-subtitle">
          把 Markdown 变成干净、专业、可交付的 Word 文档。左侧编辑，右侧即时预览摘要。
        </p>
        <div className="hero-meta">
          <span>两栏工作台</span>
          <span className="dot" aria-hidden="true">
            •
          </span>
          <span>可配置字体与版式</span>
          <span className="dot" aria-hidden="true">
            •
          </span>
          <span>一键导出</span>
        </div>
      </motion.header>

      <motion.main
        id="main-content"
        className="workspace"
        variants={fadeUp}
        initial="hidden"
        animate="visible"
        custom={0.1}
      >
        <motion.section className="panel" variants={fadeUp} custom={0.2}>
          <div className="panel-header">
            <div>
              <p className="panel-kicker">输入与配置</p>
              <h2 className="panel-title">Markdown 工作区</h2>
            </div>
            <StatusPill label={statusLabel} />
          </div>

          <div className="field">
            <label htmlFor="markdown">Markdown 输入</label>
            <textarea
              id="markdown"
              name="markdown"
              placeholder="# 报告标题\n\n从这里开始写内容..."
              rows={12}
              value={markdown}
              onChange={(event) => setMarkdown(event.target.value)}
            />
            <p className="hint">支持标题、列表、行内代码与引用标记 [1]</p>
          </div>

          <div className="settings-stack">
            <div className="setting-card">
              <div className="setting-card-head">
                <div>
                  <p className="panel-kicker">标题设置</p>
                  <h3>Title 样式</h3>
                </div>
                <span className="chip">中文/英文分开</span>
              </div>
              <div className="setting-grid">
                <div className="field compact">
                  <label htmlFor="heading-font-cn">中文字体</label>
                  <select
                    id="heading-font-cn"
                    name="heading-font-cn"
                    value={config.heading_cn_font}
                    onChange={(event) =>
                      setConfig((prev) => ({
                        ...prev,
                        heading_cn_font: event.target.value,
                      }))
                    }
                  >
                    <option value="SimHei">黑体 SimHei</option>
                    <option value="SimSun">宋体 SimSun</option>
                    <option value="FangSong">仿宋 FangSong</option>
                  </select>
                </div>
                <div className="field compact">
                  <label htmlFor="heading-font-en">英文字体</label>
                  <select
                    id="heading-font-en"
                    name="heading-font-en"
                    value={config.heading_en_font}
                    onChange={(event) =>
                      setConfig((prev) => ({
                        ...prev,
                        heading_en_font: event.target.value,
                      }))
                    }
                  >
                    <option value="Times New Roman">Times New Roman</option>
                    <option value="Arial">Arial</option>
                    <option value="Calibri">Calibri</option>
                  </select>
                </div>
                <div className="field compact">
                  <label htmlFor="heading1-size">H1 字号</label>
                  <select
                    id="heading1-size"
                    name="heading1-size"
                    value={String(config.heading1_size_pt)}
                    onChange={(event) =>
                      setConfig((prev) => ({
                        ...prev,
                        heading1_size_pt: Number.parseInt(event.target.value, 10),
                      }))
                    }
                  >
                    {fontSizeOptions.map((option) => (
                      <option key={`h1-${option.value}`} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="field compact">
                  <label htmlFor="heading2-size">H2 字号</label>
                  <select
                    id="heading2-size"
                    name="heading2-size"
                    value={String(config.heading2_size_pt)}
                    onChange={(event) =>
                      setConfig((prev) => ({
                        ...prev,
                        heading2_size_pt: Number.parseInt(event.target.value, 10),
                      }))
                    }
                  >
                    {fontSizeOptions.map((option) => (
                      <option key={`h2-${option.value}`} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="field compact">
                  <label htmlFor="heading3-size">H3 字号</label>
                  <select
                    id="heading3-size"
                    name="heading3-size"
                    value={String(config.heading3_size_pt)}
                    onChange={(event) =>
                      setConfig((prev) => ({
                        ...prev,
                        heading3_size_pt: Number.parseInt(event.target.value, 10),
                      }))
                    }
                  >
                    {fontSizeOptions.map((option) => (
                      <option key={`h3-${option.value}`} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="field compact">
                  <label htmlFor="heading4-size">H4 字号</label>
                  <select
                    id="heading4-size"
                    name="heading4-size"
                    value={String(config.heading4_size_pt)}
                    onChange={(event) =>
                      setConfig((prev) => ({
                        ...prev,
                        heading4_size_pt: Number.parseInt(event.target.value, 10),
                      }))
                    }
                  >
                    {fontSizeOptions.map((option) => (
                      <option key={`h4-${option.value}`} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="field compact">
                  <label htmlFor="heading-line-spacing">标题行距</label>
                  <select
                    id="heading-line-spacing"
                    name="heading-line-spacing"
                    value={String(config.heading_line_spacing)}
                    onChange={(event) =>
                      setConfig((prev) => ({
                        ...prev,
                        heading_line_spacing: Number.parseFloat(event.target.value),
                      }))
                    }
                  >
                    {lineSpacingOptions.map((value) => (
                      <option key={`heading-spacing-${value}`} value={value}>
                        {value}
                      </option>
                    ))}
                  </select>
                  <p className="hint">倍行距</p>
                </div>
                <div className="field compact">
                  <label htmlFor="heading-para-before">标题段前</label>
                  <input
                    id="heading-para-before"
                    name="heading-para-before"
                    type="number"
                    min={0}
                    step={0.1}
                    value={config.heading_para_before_lines}
                    onChange={(event) => {
                      const nextValue = event.target.valueAsNumber;
                      setConfig((prev) => ({
                        ...prev,
                        heading_para_before_lines: Number.isNaN(nextValue) ? 0 : nextValue,
                      }));
                    }}
                  />
                  <p className="hint">单位：行</p>
                </div>
                <div className="field compact">
                  <label htmlFor="heading-para-after">标题段后</label>
                  <input
                    id="heading-para-after"
                    name="heading-para-after"
                    type="number"
                    min={0}
                    step={0.1}
                    value={config.heading_para_after_lines}
                    onChange={(event) => {
                      const nextValue = event.target.valueAsNumber;
                      setConfig((prev) => ({
                        ...prev,
                        heading_para_after_lines: Number.isNaN(nextValue) ? 0 : nextValue,
                      }));
                    }}
                  />
                  <p className="hint">单位：行</p>
                </div>
              </div>
            </div>

            <div className="setting-card">
              <div className="setting-card-head">
                <div>
                  <p className="panel-kicker">正文设置</p>
                  <h3>Body 样式</h3>
                </div>
                <span className="chip">中文/英文分开</span>
              </div>
              <div className="setting-grid">
                <div className="field compact">
                  <label htmlFor="font-cn">中文字体</label>
                  <select
                    id="font-cn"
                    name="font-cn"
                    value={config.cn_font}
                    onChange={(event) =>
                      setConfig((prev) => ({ ...prev, cn_font: event.target.value }))
                    }
                  >
                    <option value="SimSun">宋体 SimSun</option>
                    <option value="SimHei">黑体 SimHei</option>
                    <option value="FangSong">仿宋 FangSong</option>
                  </select>
                </div>
                <div className="field compact">
                  <label htmlFor="font-en">英文字体</label>
                  <select
                    id="font-en"
                    name="font-en"
                    value={config.en_font}
                    onChange={(event) =>
                      setConfig((prev) => ({ ...prev, en_font: event.target.value }))
                    }
                  >
                    <option value="Times New Roman">Times New Roman</option>
                    <option value="Arial">Arial</option>
                    <option value="Calibri">Calibri</option>
                  </select>
                </div>
                <div className="field compact">
                  <label htmlFor="body-size">正文字号</label>
                  <select
                    id="body-size"
                    name="body-size"
                    value={String(config.body_size_pt)}
                    onChange={(event) =>
                      setConfig((prev) => ({
                        ...prev,
                        body_size_pt: Number.parseInt(event.target.value, 10),
                      }))
                    }
                  >
                    {fontSizeOptions.map((option) => (
                      <option key={`body-${option.value}`} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="field compact">
                  <label htmlFor="line-spacing">正文行距</label>
                  <select
                    id="line-spacing"
                    name="line-spacing"
                    value={String(config.line_spacing)}
                    onChange={(event) =>
                      setConfig((prev) => ({
                        ...prev,
                        line_spacing: Number.parseFloat(event.target.value),
                      }))
                    }
                  >
                    {lineSpacingOptions.map((value) => (
                      <option key={`body-spacing-${value}`} value={value}>
                        {value}
                      </option>
                    ))}
                  </select>
                  <p className="hint">倍行距</p>
                </div>
                <div className="field compact">
                  <label htmlFor="para-before">正文段前</label>
                  <input
                    id="para-before"
                    name="para-before"
                    type="number"
                    min={0}
                    step={0.1}
                    value={config.para_before_lines}
                    onChange={(event) => {
                      const nextValue = event.target.valueAsNumber;
                      setConfig((prev) => ({
                        ...prev,
                        para_before_lines: Number.isNaN(nextValue) ? 0 : nextValue,
                      }));
                    }}
                  />
                  <p className="hint">单位：行</p>
                </div>
                <div className="field compact">
                  <label htmlFor="para-after">正文段后</label>
                  <input
                    id="para-after"
                    name="para-after"
                    type="number"
                    min={0}
                    step={0.1}
                    value={config.para_after_lines}
                    onChange={(event) => {
                      const nextValue = event.target.valueAsNumber;
                      setConfig((prev) => ({
                        ...prev,
                        para_after_lines: Number.isNaN(nextValue) ? 0 : nextValue,
                      }));
                    }}
                  />
                  <p className="hint">单位：行</p>
                </div>
                <div className="field compact">
                  <label htmlFor="indent-before">左缩进</label>
                  <input
                    id="indent-before"
                    name="indent-before"
                    data-testid="left-indent"
                    type="number"
                    min={0}
                    step={1}
                    value={config.indent_before_chars}
                    onChange={(event) => {
                      const nextValue = event.target.valueAsNumber;
                      setConfig((prev) => ({
                        ...prev,
                        indent_before_chars: Number.isNaN(nextValue) ? 0 : nextValue,
                      }));
                    }}
                  />
                  <p className="hint">单位：字符</p>
                </div>
                <div className="field compact">
                  <label htmlFor="indent-after">右缩进</label>
                  <input
                    id="indent-after"
                    name="indent-after"
                    data-testid="right-indent"
                    type="number"
                    min={0}
                    step={1}
                    value={config.indent_after_chars}
                    onChange={(event) => {
                      const nextValue = event.target.valueAsNumber;
                      setConfig((prev) => ({
                        ...prev,
                        indent_after_chars: Number.isNaN(nextValue) ? 0 : nextValue,
                      }));
                    }}
                  />
                  <p className="hint">单位：字符</p>
                </div>
                <div className="field compact">
                  <label htmlFor="indent-first-line">首行缩进</label>
                  <input
                    id="indent-first-line"
                    name="indent-first-line"
                    data-testid="first-line-indent"
                    type="number"
                    min={0}
                    step={1}
                    value={config.first_line_indent_chars}
                    onChange={(event) => {
                      const nextValue = event.target.valueAsNumber;
                      setConfig((prev) => ({
                        ...prev,
                        first_line_indent_chars: Number.isNaN(nextValue) ? 0 : nextValue,
                      }));
                    }}
                  />
                  <p className="hint">单位：字符</p>
                </div>
              </div>
            </div>
          </div>

          <div className="action-row">
            <button
              className="ghost-btn"
              type="button"
              onClick={() => setMarkdown("")}
            >
              清空内容
            </button>
            <button
              className="primary-btn"
              type="button"
              onClick={handleGenerate}
                disabled={isEmpty || isGenerating}
                aria-disabled={isEmpty || isGenerating}
                data-testid="btn-generate"
              >
                {isGenerating ? "生成中…" : "生成 Word"}
              </button>
            </div>

          {error ? <p className="error-text">{error}</p> : null}
        </motion.section>

        <motion.section className="panel preview-panel" variants={fadeUp} custom={0.3}>
          <div className="panel-header">
            <div>
              <p className="panel-kicker">预览摘要</p>
              <h2 className="panel-title">结构概览</h2>
            </div>
            <div className="meta-chip">
              今日已导出 {exportStats?.today ?? "—"} 次
            </div>
          </div>

          <div className="stats-grid">
            <div className="stat-card">
              <span className="stat-label">标题数</span>
              <strong className="stat-value">{headingCount}</strong>
            </div>
            <div className="stat-card">
              <span className="stat-label">引用标记</span>
              <strong className="stat-value">{refCount}</strong>
            </div>
            <div className="stat-card">
              <span className="stat-label">预计页数</span>
              <strong className="stat-value">{estimatedPages}</strong>
            </div>
          </div>

          <div className="preview-card">
            <div className="preview-header">
              <h3>排版预览</h3>
              <span className="preview-badge">样式：学术简洁</span>
            </div>
            <div className="preview-body">
              {isEmpty ? (
                <p>等待输入 Markdown 后显示结构摘要。</p>
              ) : (
                <>
                  <p>已识别 {paragraphCount} 个段落与 {headingCount} 个标题。</p>
                  <ul>
                    <li>最新引用：{preview?.refs?.[0] ?? "无"}</li>
                    <li>分页建议：约 {estimatedPages} 页</li>
                    <li>正文字体：{config.cn_font} / {config.en_font}</li>
                    <li>标题字体：{config.heading_cn_font} / {config.heading_en_font}</li>
                  </ul>
                  {preview?.preview_html ? (
                    <>
                      <div
                        className="preview-html preview-pages"
                        ref={previewViewportRef}
                        style={{ "--preview-scale": previewScale } as CSSProperties}
                      >
                        {(previewPages.length ? previewPages : [preview.preview_html]).map(
                          (pageHtml) => (
                            <div className="preview-page-shell" key={pageHtml}>
                              <div className="preview-page">
                                <div
                                  className="preview-page-content"
                                  dangerouslySetInnerHTML={{ __html: pageHtml }}
                                />
                              </div>
                            </div>
                          ),
                        )}
                      </div>
                      <div
                        className="preview-measure"
                        ref={previewMeasureRef}
                        aria-hidden="true"
                        style={
                          {
                            "--preview-page-width": `${PREVIEW_PAGE_WIDTH}px`,
                            "--preview-page-height": `${PREVIEW_PAGE_HEIGHT}px`,
                            "--preview-page-padding": "72px",
                          } as CSSProperties
                        }
                      />
                    </>
                  ) : null}
                </>
              )}
            </div>
          </div>

            <div className="note-box">
              <h4>导出提示</h4>
              <p>点击“生成 Word”后会自动下载 docx 文件，并保持当前样式。</p>
              <p>
                表格单元格默认居中，块级公式自动按 (1) 样式编号并右侧对齐，无需在 Word 里手动刷新域。
              </p>
              <div className="action-row">
                <button
                  className="ghost-btn"
                  type="button"
                  onClick={handleExportLogs}
                  disabled={!hasDesktopLogExport}
                  data-testid="btn-export-logs"
                >
                  导出运行日志
                </button>
              </div>
              {logExportMessage ? <p className="hint">{logExportMessage}</p> : null}
            </div>
        </motion.section>
      </motion.main>

      <footer className="page-footer">
        <p>
          说明：如系统未安装中文黑体字体（如 SimHei/黑体），标题字体可能被自动替换。
        </p>
      </footer>
    </div>
  );
}
