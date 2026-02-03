import type { Metadata } from "next";
import { Press_Start_2P, Space_Mono } from "next/font/google";
import "./globals.css";

const display = Press_Start_2P({
  variable: "--font-display",
  subsets: ["latin"],
  weight: "400",
});

const ui = Space_Mono({
  variable: "--font-ui",
  subsets: ["latin"],
  weight: ["400", "700"],
});

export const metadata: Metadata = {
  title: "AI 报告排版助手",
  description: "把 Markdown 转换为专业 Word 文档的排版助手。",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body className={`${display.variable} ${ui.variable}`}>
        {children}
      </body>
    </html>
  );
}
