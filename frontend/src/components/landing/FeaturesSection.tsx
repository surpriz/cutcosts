"use client";

import { Search, DollarSign, Shield, Cloud } from "lucide-react";
import { GradientText } from "./GradientText";
import { useScrollAnimation } from "@/hooks/useScrollAnimation";

interface Feature {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
  accent: "cyan" | "emerald" | "violet" | "orange";
}

const features: Feature[] = [
  {
    icon: Search,
    title: "Intelligent Detection",
    description:
      "Detect 400+ resource types across AWS, Azure & GCP with CloudWatch-powered analysis and smart heuristics.",
    accent: "cyan",
  },
  {
    icon: DollarSign,
    title: "Cost Analytics",
    description:
      'Get precise "Future waste" and "Already wasted" calculations with confidence levels for informed decisions.',
    accent: "emerald",
  },
  {
    icon: Shield,
    title: "100% Read-Only",
    description:
      "Complete peace of mind - we only read your infrastructure, never modify or delete any resources.",
    accent: "violet",
  },
  {
    icon: Cloud,
    title: "Multi-Cloud Support",
    description:
      "AWS (~50 types), Azure (~200 types), GCP (~150 types) with customizable detection rules.",
    accent: "orange",
  },
];

const accentColors = {
  cyan: {
    icon: "text-cyan-400",
    glow: "group-hover:shadow-cyan-500/20",
    border: "group-hover:border-cyan-500/30",
  },
  emerald: {
    icon: "text-emerald-400",
    glow: "group-hover:shadow-emerald-500/20",
    border: "group-hover:border-emerald-500/30",
  },
  violet: {
    icon: "text-violet-400",
    glow: "group-hover:shadow-violet-500/20",
    border: "group-hover:border-violet-500/30",
  },
  orange: {
    icon: "text-orange-400",
    glow: "group-hover:shadow-orange-500/20",
    border: "group-hover:border-orange-500/30",
  },
};

export function FeaturesSection() {
  const { ref, isInView } = useScrollAnimation<HTMLElement>({
    threshold: 0.1,
  });

  return (
    <section
      ref={ref}
      id="features"
      className="relative bg-landing-elevated py-24 md:py-32 px-4 sm:px-6 lg:px-8"
    >
      {/* Subtle gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-landing-deep via-transparent to-landing-deep opacity-50" />

      <div className="relative max-w-6xl mx-auto">
        {/* Section Header */}
        <div
          className={`
            text-center mb-16
            transition-all duration-700
            ${isInView ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"}
          `}
        >
          <h2 className="text-display-sm font-bold text-zinc-50 mb-4">
            The <GradientText>Arsenal</GradientText> for Cost Optimization
          </h2>
          <p className="text-lg text-zinc-400 max-w-2xl mx-auto">
            Everything you need to detect and eliminate cloud waste across your
            infrastructure
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {features.map((feature, index) => (
            <FeatureCard
              key={feature.title}
              feature={feature}
              index={index}
              isInView={isInView}
            />
          ))}
        </div>
      </div>
    </section>
  );
}

interface FeatureCardProps {
  feature: Feature;
  index: number;
  isInView: boolean;
}

function FeatureCard({ feature, index, isInView }: FeatureCardProps) {
  const { icon: Icon, title, description, accent } = feature;
  const colors = accentColors[accent];

  return (
    <div
      className={`
        group relative
        p-6 md:p-8
        bg-zinc-900/50 hover:bg-zinc-900/80
        border border-zinc-800 ${colors.border}
        rounded-2xl
        transition-all duration-300
        hover:shadow-xl ${colors.glow}
        ${isInView ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"}
      `}
      style={{
        transitionDelay: isInView ? `${(index + 1) * 100}ms` : "0ms",
      }}
    >
      {/* Icon */}
      <div
        className={`
          inline-flex items-center justify-center
          h-12 w-12 mb-5
          bg-zinc-800 group-hover:bg-zinc-800/80
          border border-zinc-700
          rounded-xl
          transition-colors duration-300
        `}
      >
        <Icon className={`h-6 w-6 ${colors.icon}`} />
      </div>

      {/* Content */}
      <h3 className="text-xl font-semibold text-zinc-50 mb-3">{title}</h3>
      <p className="text-zinc-400 leading-relaxed">{description}</p>
    </div>
  );
}
