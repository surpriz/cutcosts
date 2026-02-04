"use client";

import { GradientText } from "./GradientText";
import { useScrollAnimation } from "@/hooks/useScrollAnimation";
import { CloudCog, ScanLine, ListChecks } from "lucide-react";

interface Step {
  number: string;
  title: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
}

const steps: Step[] = [
  {
    number: "01",
    title: "Connect Your Cloud Accounts",
    description:
      "Add AWS, Azure or GCP credentials with read-only permissions. We never modify or delete anything.",
    icon: CloudCog,
  },
  {
    number: "02",
    title: "Run Intelligent Scan",
    description:
      "CloudWatch-powered scanner analyzes 400+ resource types to identify orphaned resources with precision.",
    icon: ScanLine,
  },
  {
    number: "03",
    title: "Review & Take Action",
    description:
      'Get confidence-rated detections with "Future waste" and "Already wasted" cost calculations.',
    icon: ListChecks,
  },
];

export function HowItWorks() {
  const { ref, isInView } = useScrollAnimation<HTMLElement>({
    threshold: 0.1,
  });

  return (
    <section
      ref={ref}
      id="how-it-works"
      className="relative bg-landing-deep py-24 md:py-32 px-4 sm:px-6 lg:px-8"
    >
      <div className="max-w-6xl mx-auto">
        {/* Section Header */}
        <div
          className={`
            text-center mb-16
            transition-all duration-700
            ${isInView ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"}
          `}
        >
          <h2 className="text-display-sm font-bold text-zinc-50 mb-4">
            Start Saving in <GradientText>3 Steps</GradientText>
          </h2>
          <p className="text-lg text-zinc-400 max-w-2xl mx-auto">
            Get up and running in minutes, not hours
          </p>
        </div>

        {/* Steps */}
        <div className="relative">
          {/* Connecting Line - Desktop only */}
          <div className="hidden md:block absolute top-24 left-[16.67%] right-[16.67%] h-px">
            <svg
              className="w-full h-8 overflow-visible"
              preserveAspectRatio="none"
            >
              <line
                x1="0%"
                y1="50%"
                x2="100%"
                y2="50%"
                stroke="url(#lineGradient)"
                strokeWidth="2"
                strokeDasharray="8 4"
                className={`
                  transition-all duration-1000
                  ${isInView ? "opacity-100" : "opacity-0"}
                `}
              />
              <defs>
                <linearGradient
                  id="lineGradient"
                  x1="0%"
                  y1="0%"
                  x2="100%"
                  y2="0%"
                >
                  <stop offset="0%" stopColor="#22D3EE" stopOpacity="0.3" />
                  <stop offset="50%" stopColor="#A78BFA" stopOpacity="0.5" />
                  <stop offset="100%" stopColor="#22D3EE" stopOpacity="0.3" />
                </linearGradient>
              </defs>
            </svg>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-12">
            {steps.map((step, index) => (
              <StepCard
                key={step.number}
                step={step}
                index={index}
                isInView={isInView}
              />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

interface StepCardProps {
  step: Step;
  index: number;
  isInView: boolean;
}

function StepCard({ step, index, isInView }: StepCardProps) {
  const { number, title, description, icon: Icon } = step;

  return (
    <div
      className={`
        relative text-center
        transition-all duration-700
        ${isInView ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"}
      `}
      style={{
        transitionDelay: isInView ? `${(index + 1) * 150}ms` : "0ms",
      }}
    >
      {/* Number Badge */}
      <div className="flex justify-center mb-6">
        <div
          className="
            relative
            flex items-center justify-center
            h-16 w-16
            bg-zinc-900
            border border-zinc-800
            rounded-2xl
            group
          "
        >
          {/* Glow effect on hover */}
          <div
            className="
              absolute inset-0
              rounded-2xl
              bg-gradient-to-br from-cyan-500/20 to-violet-500/20
              opacity-0 group-hover:opacity-100
              transition-opacity duration-300
            "
          />
          <Icon className="h-7 w-7 text-cyan-400 relative z-10" />
          {/* Step number badge */}
          <div
            className="
              absolute -top-2 -right-2
              h-6 w-8
              bg-zinc-950
              border border-zinc-800
              rounded-md
              flex items-center justify-center
            "
          >
            <span className="text-xs font-mono font-bold text-zinc-400">
              {number}
            </span>
          </div>
        </div>
      </div>

      {/* Content */}
      <h3 className="text-xl font-semibold text-zinc-50 mb-3">{title}</h3>
      <p className="text-zinc-400 leading-relaxed max-w-xs mx-auto">
        {description}
      </p>
    </div>
  );
}
