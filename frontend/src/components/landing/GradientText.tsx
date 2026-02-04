interface GradientTextProps {
  children: React.ReactNode;
  className?: string;
  variant?: "cyan-violet" | "emerald-cyan" | "violet-pink";
}

const gradientVariants = {
  "cyan-violet": "from-cyan-400 to-violet-400",
  "emerald-cyan": "from-emerald-400 to-cyan-400",
  "violet-pink": "from-violet-400 to-pink-400",
};

export function GradientText({
  children,
  className = "",
  variant = "cyan-violet",
}: GradientTextProps) {
  return (
    <span
      className={`bg-gradient-to-r ${gradientVariants[variant]} bg-clip-text text-transparent ${className}`}
    >
      {children}
    </span>
  );
}
