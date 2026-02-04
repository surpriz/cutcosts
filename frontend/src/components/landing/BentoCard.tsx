"use client";

import { ReactNode } from "react";

interface BentoCardProps {
  children: ReactNode;
  className?: string;
  size?: "sm" | "md" | "lg" | "wide" | "tall";
  glowOnHover?: boolean;
}

const sizeClasses = {
  sm: "col-span-1 row-span-1",
  md: "col-span-1 row-span-1 md:col-span-1",
  lg: "col-span-1 row-span-1 md:col-span-2 md:row-span-2",
  wide: "col-span-1 md:col-span-2 row-span-1",
  tall: "col-span-1 row-span-1 md:row-span-2",
};

export function BentoCard({
  children,
  className = "",
  size = "md",
  glowOnHover = true,
}: BentoCardProps) {
  return (
    <div
      className={`
        relative overflow-hidden rounded-2xl
        bg-zinc-900 border border-zinc-800
        p-6 md:p-8
        transition-all duration-300
        ${glowOnHover ? "glow-hover hover:border-zinc-700 hover:bg-zinc-900/80" : ""}
        ${sizeClasses[size]}
        ${className}
      `}
    >
      {children}
    </div>
  );
}

interface BentoGridProps {
  children: ReactNode;
  className?: string;
  columns?: 2 | 3 | 4;
}

export function BentoGrid({
  children,
  className = "",
  columns = 3,
}: BentoGridProps) {
  const columnClasses = {
    2: "md:grid-cols-2",
    3: "md:grid-cols-3",
    4: "md:grid-cols-4",
  };

  return (
    <div
      className={`
        grid grid-cols-1 gap-4 md:gap-6
        ${columnClasses[columns]}
        ${className}
      `}
    >
      {children}
    </div>
  );
}
