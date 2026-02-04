"use client";

import { BentoCard, BentoGrid } from "./BentoCard";
import { AnimatedCounter } from "./AnimatedCounter";
import { GradientText } from "./GradientText";
import { useScrollAnimation } from "@/hooks/useScrollAnimation";
import { Quote } from "lucide-react";

export function StatsGrid() {
  const { ref, isInView } = useScrollAnimation<HTMLElement>({
    threshold: 0.1,
  });

  return (
    <section
      ref={ref}
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
            Real <GradientText>Impact</GradientText>, Real Savings
          </h2>
          <p className="text-lg text-zinc-400 max-w-2xl mx-auto">
            Join hundreds of teams who have already optimized their cloud spend
          </p>
        </div>

        {/* Bento Grid */}
        <BentoGrid columns={3} className="max-w-5xl mx-auto">
          {/* Savings Card - Large */}
          <BentoCard
            size="md"
            className={`
              flex flex-col justify-center
              transition-all duration-700 delay-100
              ${isInView ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"}
            `}
          >
            <div className="text-sm font-medium text-zinc-500 uppercase tracking-wider mb-2">
              Total Saved
            </div>
            <div className="text-4xl md:text-5xl font-bold text-emerald-400">
              <AnimatedCounter end={2.4} decimals={1} prefix="$" suffix="M+" />
            </div>
            <div className="text-zinc-400 mt-2">By our users</div>
          </BentoCard>

          {/* Resources Card */}
          <BentoCard
            size="md"
            className={`
              flex flex-col justify-center
              transition-all duration-700 delay-200
              ${isInView ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"}
            `}
          >
            <div className="text-sm font-medium text-zinc-500 uppercase tracking-wider mb-2">
              Resources Found
            </div>
            <div className="text-4xl md:text-5xl font-bold text-cyan-400">
              <AnimatedCounter end={50000} suffix="+" />
            </div>
            <div className="text-zinc-400 mt-2">Orphaned resources detected</div>
          </BentoCard>

          {/* Uptime Card */}
          <BentoCard
            size="md"
            className={`
              flex flex-col justify-center
              transition-all duration-700 delay-300
              ${isInView ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"}
            `}
          >
            <div className="text-sm font-medium text-zinc-500 uppercase tracking-wider mb-2">
              Platform Uptime
            </div>
            <div className="text-4xl md:text-5xl font-bold text-violet-400">
              <AnimatedCounter end={99.9} decimals={1} suffix="%" />
            </div>
            <div className="text-zinc-400 mt-2">SLA guaranteed</div>
          </BentoCard>

          {/* Testimonial Card - Wide */}
          <BentoCard
            size="wide"
            glowOnHover={false}
            className={`
              md:col-span-3 bg-zinc-900/50
              transition-all duration-700 delay-400
              ${isInView ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"}
            `}
          >
            <div className="flex flex-col md:flex-row items-start md:items-center gap-6">
              <Quote className="h-10 w-10 text-cyan-400/50 flex-shrink-0" />
              <div>
                <p className="text-lg md:text-xl text-zinc-300 italic mb-4">
                  &ldquo;CutCosts found{" "}
                  <span className="text-emerald-400 font-semibold">$47K</span> in
                  cloud waste during our first scan. The ROI was immediate.&rdquo;
                </p>
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-full bg-gradient-to-br from-cyan-400 to-violet-400 flex items-center justify-center text-zinc-950 font-bold">
                    JD
                  </div>
                  <div>
                    <div className="text-zinc-50 font-medium">James Davis</div>
                    <div className="text-zinc-500 text-sm">
                      VP of Engineering, TechCorp
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </BentoCard>
        </BentoGrid>
      </div>
    </section>
  );
}
