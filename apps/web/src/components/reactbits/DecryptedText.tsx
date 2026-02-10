"use client";

import { motion, useReducedMotion } from "motion/react";
import { useCallback, useEffect, useRef, useState } from "react";

type AnimateOnMode = "hover" | "view" | "both";

type DecryptedTextProps = {
  text: string;
  speed?: number;
  maxIterations?: number;
  characters?: string;
  className?: string;
  parentClassName?: string;
  encryptedClassName?: string;
  animateOn?: AnimateOnMode;
  disabled?: boolean;
  dataTestId?: string;
};

const srOnlyStyle = {
  position: "absolute",
  width: "1px",
  height: "1px",
  padding: 0,
  margin: "-1px",
  overflow: "hidden",
  clip: "rect(0,0,0,0)",
  border: 0,
} as const;

export default function DecryptedText({
  text,
  speed = 45,
  maxIterations = 8,
  characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*()_+",
  className = "",
  parentClassName = "",
  encryptedClassName = "",
  animateOn = "hover",
  disabled = false,
  dataTestId,
}: DecryptedTextProps) {
  const prefersReducedMotion = useReducedMotion();
  const canAnimate = !disabled && !prefersReducedMotion;
  const [displayText, setDisplayText] = useState(text);
  const [isScrambling, setIsScrambling] = useState(false);
  const [hasAnimatedInView, setHasAnimatedInView] = useState(false);

  const hostRef = useRef<HTMLSpanElement | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const clearScramble = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const startScramble = useCallback(() => {
    if (!canAnimate || isScrambling || !text) {
      return;
    }

    setIsScrambling(true);
    let iteration = 0;
    const originalChars = text.split("");
    const randomChars = characters.split("");

    clearScramble();
    intervalRef.current = setInterval(() => {
      iteration += 1;
      const progress = Math.min(1, iteration / maxIterations);
      const revealCount = Math.floor(originalChars.length * progress);

      const next = originalChars
        .map((char, index) => {
          if (char === " " || index < revealCount) {
            return char;
          }
          return randomChars[Math.floor(Math.random() * randomChars.length)] ?? char;
        })
        .join("");

      setDisplayText(next);

      if (iteration >= maxIterations) {
        clearScramble();
        setDisplayText(text);
        setIsScrambling(false);
      }
    }, speed);
  }, [canAnimate, isScrambling, text, characters, maxIterations, speed, clearScramble]);

  const stopScramble = useCallback(() => {
    clearScramble();
    setDisplayText(text);
    setIsScrambling(false);
  }, [clearScramble, text]);

  useEffect(() => {
    return () => {
      clearScramble();
    };
  }, [clearScramble]);

  useEffect(() => {
    if (!canAnimate || (animateOn !== "view" && animateOn !== "both") || hasAnimatedInView) {
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting || hasAnimatedInView) {
            return;
          }

          setHasAnimatedInView(true);
          startScramble();
        });
      },
      { threshold: 0.1 },
    );

    const node = hostRef.current;
    if (node) {
      observer.observe(node);
    }

    return () => {
      if (node) {
        observer.unobserve(node);
      }
    };
  }, [animateOn, canAnimate, hasAnimatedInView, startScramble]);

  if (!canAnimate) {
    return (
      <span className={parentClassName} data-testid={dataTestId}>
        {text}
      </span>
    );
  }

  const hoverEnabled = animateOn === "hover" || animateOn === "both";
  const liveText = isScrambling ? displayText : text;
  const originalChars = text.split("");
  const liveChars = liveText.split("");
  const keyedLiveChars = (() => {
    const counts = new Map<string, number>();

    return liveChars.map((char, position) => {
      const count = counts.get(char) ?? 0;
      counts.set(char, count + 1);

      return {
        char,
        position,
        key: `${char}-${count}`,
      };
    });
  })();

  return (
    <motion.span
      ref={hostRef}
      className={parentClassName}
      style={{ display: "inline-block", whiteSpace: "pre-wrap" }}
      onMouseEnter={hoverEnabled ? startScramble : undefined}
      onMouseLeave={hoverEnabled ? stopScramble : undefined}
      data-testid={dataTestId}
    >
      <span style={srOnlyStyle}>{text}</span>
      <span aria-hidden="true">
        {keyedLiveChars.map(({ char, key, position }) => {
          const isRevealed = char === (originalChars[position] ?? char);

          return (
            <span
              key={key}
              className={isScrambling && !isRevealed ? encryptedClassName : className}
            >
              {char}
            </span>
          );
        })}
      </span>
    </motion.span>
  );
}
