"use client";

import { useEffect, useRef, useState, useCallback } from "react";

interface UseScrollAnimationOptions {
  threshold?: number;
  rootMargin?: string;
  triggerOnce?: boolean;
}

export function useScrollAnimation<T extends HTMLElement = HTMLElement>(
  options: UseScrollAnimationOptions = {}
) {
  const { threshold = 0.1, rootMargin = "0px", triggerOnce = true } = options;
  const ref = useRef<T>(null);
  const [isInView, setIsInView] = useState(false);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    setPrefersReducedMotion(mediaQuery.matches);

    const handleChange = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches);
    };

    mediaQuery.addEventListener("change", handleChange);
    return () => mediaQuery.removeEventListener("change", handleChange);
  }, []);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    if (prefersReducedMotion) {
      setIsInView(true);
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        const entry = entries[0];
        if (entry?.isIntersecting) {
          setIsInView(true);
          if (triggerOnce) {
            observer.unobserve(element);
          }
        } else if (!triggerOnce) {
          setIsInView(false);
        }
      },
      {
        threshold,
        rootMargin,
      }
    );

    observer.observe(element);

    return () => {
      observer.disconnect();
    };
  }, [threshold, rootMargin, triggerOnce, prefersReducedMotion]);

  return { ref, isInView, prefersReducedMotion };
}

export function useScrollAnimationGroup(
  count: number,
  options: UseScrollAnimationOptions = {}
) {
  const { threshold = 0.1, rootMargin = "0px", triggerOnce = true } = options;
  const containerRef = useRef<HTMLDivElement>(null);
  const [visibleItems, setVisibleItems] = useState<boolean[]>(
    Array(count).fill(false)
  );
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    setPrefersReducedMotion(mediaQuery.matches);

    const handleChange = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches);
    };

    mediaQuery.addEventListener("change", handleChange);
    return () => mediaQuery.removeEventListener("change", handleChange);
  }, []);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    if (prefersReducedMotion) {
      setVisibleItems(Array(count).fill(true));
      return;
    }

    const children = Array.from(container.children);

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          const index = children.indexOf(entry.target as HTMLElement);
          if (index === -1) return;

          if (entry.isIntersecting) {
            setVisibleItems((prev) => {
              const next = [...prev];
              next[index] = true;
              return next;
            });
            if (triggerOnce) {
              observer.unobserve(entry.target);
            }
          } else if (!triggerOnce) {
            setVisibleItems((prev) => {
              const next = [...prev];
              next[index] = false;
              return next;
            });
          }
        });
      },
      {
        threshold,
        rootMargin,
      }
    );

    children.forEach((child) => observer.observe(child));

    return () => {
      observer.disconnect();
    };
  }, [count, threshold, rootMargin, triggerOnce, prefersReducedMotion]);

  const getStaggerDelay = useCallback((index: number, baseDelay = 100) => {
    if (prefersReducedMotion) return 0;
    return index * baseDelay;
  }, [prefersReducedMotion]);

  return { containerRef, visibleItems, getStaggerDelay, prefersReducedMotion };
}
