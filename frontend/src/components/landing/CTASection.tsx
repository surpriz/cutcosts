"use client";

import Link from "next/link";
import { Zap, ArrowRight } from "lucide-react";
import { GradientText } from "./GradientText";
import { useScrollAnimation } from "@/hooks/useScrollAnimation";

export function CTASection() {
  const { ref, isInView } = useScrollAnimation<HTMLElement>({
    threshold: 0.2,
  });

  return (
    <section
      ref={ref}
      className="relative bg-landing-deep py-24 md:py-32 px-4 sm:px-6 lg:px-8 overflow-hidden"
    >
      {/* Background gradient */}
      <div
        className="
          absolute inset-0
          bg-gradient-to-br from-cyan-500/5 via-transparent to-violet-500/5
        "
      />

      {/* Decorative elements */}
      <div
        className="
          absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2
          w-[600px] h-[600px]
          bg-gradient-radial from-cyan-500/10 via-transparent to-transparent
          blur-3xl
          opacity-50
        "
      />

      <div className="relative max-w-4xl mx-auto text-center">
        {/* Headline */}
        <h2
          className={`
            text-display-sm md:text-display font-bold text-zinc-50 mb-6
            transition-all duration-700
            ${isInView ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"}
          `}
        >
          Ready to <GradientText>Cut Your Costs</GradientText>?
        </h2>

        {/* Subheadline */}
        <p
          className={`
            text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto mb-10
            transition-all duration-700 delay-100
            ${isInView ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"}
          `}
        >
          Join hundreds of teams saving thousands monthly by eliminating cloud
          waste. Start your free trial today.
        </p>

        {/* CTA Button */}
        <div
          className={`
            flex flex-col sm:flex-row gap-4 justify-center items-center mb-10
            transition-all duration-700 delay-200
            ${isInView ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"}
          `}
        >
          <Link
            href="/auth/register"
            className="
              group relative inline-flex items-center gap-3
              px-10 py-5 text-lg font-semibold
              bg-gradient-to-r from-cyan-500 to-cyan-400
              hover:from-cyan-400 hover:to-cyan-300
              text-zinc-950
              rounded-xl
              transition-all duration-300
              hover:shadow-2xl hover:shadow-cyan-500/30
              hover:scale-[1.02]
            "
          >
            <Zap className="h-5 w-5" />
            Start Saving Now - It&apos;s Free
            <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
          </Link>
        </div>

        {/* Trust points */}
        <div
          className={`
            flex flex-wrap justify-center gap-6 text-sm text-zinc-500
            transition-all duration-700 delay-300
            ${isInView ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"}
          `}
        >
          <span className="flex items-center gap-2">
            <CheckIcon />
            No credit card required
          </span>
          <span className="flex items-center gap-2">
            <CheckIcon />
            Setup in under 2 minutes
          </span>
          <span className="flex items-center gap-2">
            <CheckIcon />
            Cancel anytime
          </span>
        </div>
      </div>
    </section>
  );
}

function CheckIcon() {
  return (
    <svg
      className="h-4 w-4 text-emerald-400"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
    </svg>
  );
}
