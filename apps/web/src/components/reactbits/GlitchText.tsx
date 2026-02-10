"use client";

import styles from "./GlitchText.module.css";

type GlitchTextProps = {
  children: string;
  speed?: number;
  enableShadows?: boolean;
  enableOnHover?: boolean;
  className?: string;
};

export default function GlitchText({
  children,
  speed = 1,
  enableShadows = true,
  enableOnHover = true,
  className = "",
}: GlitchTextProps) {
  const inlineStyles = {
    "--after-duration": `${speed * 3}s`,
    "--before-duration": `${speed * 2}s`,
    "--after-shadow": enableShadows ? "-4px 0 #b30000" : "none",
    "--before-shadow": enableShadows ? "4px 0 #005eb3" : "none",
  } as React.CSSProperties;

  const interactionClass = enableOnHover ? styles.enableOnHover : styles.alwaysOn;

  return (
    <span
      className={`${styles.glitch} ${interactionClass} ${className}`.trim()}
      style={inlineStyles}
      data-text={children}
    >
      {children}
    </span>
  );
}
