"use client";

import Link from "next/link";
import { Shield, Lock, Zap } from "lucide-react";
import { GradientText } from "./GradientText";
import { useScrollAnimation } from "@/hooks/useScrollAnimation";

export function HeroSection() {
  const { ref, isInView } = useScrollAnimation<HTMLDivElement>({
    threshold: 0.1,
  });

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-landing-deep pt-20">
      {/* Animated Mesh Gradient Background */}
      <div className="absolute inset-0 mesh-gradient-bg animate-mesh-move" />

      {/* Subtle grid overlay */}
      <div
        className="absolute inset-0 opacity-[0.02]"
        style={{
          backgroundImage: `linear-gradient(to right, #fff 1px, transparent 1px),
                           linear-gradient(to bottom, #fff 1px, transparent 1px)`,
          backgroundSize: "60px 60px",
        }}
      />

      <div
        ref={ref}
        className="relative z-10 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center"
      >
        {/* Trust Badge */}
        <div
          className={`
            inline-flex items-center gap-2 mb-8
            px-4 py-2
            bg-zinc-900/60 backdrop-blur-sm
            border border-zinc-800
            rounded-full
            transition-all duration-700
            ${isInView ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}
          `}
        >
          <span className="flex h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-sm text-zinc-400">
            Trusted by <span className="text-zinc-50 font-medium">500+</span>{" "}
            teams worldwide
          </span>
        </div>

        {/* Main Headline */}
        <h1
          className={`
            text-display font-bold text-zinc-50 mb-6
            transition-all duration-700 delay-100
            ${isInView ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}
          `}
        >
          Stop Bleeding
          <br />
          <GradientText>Cloud Cash.</GradientText>
        </h1>

        {/* Subheadline */}
        <p
          className={`
            text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto mb-10
            transition-all duration-700 delay-200
            ${isInView ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}
          `}
        >
          Detect <span className="text-zinc-50">400+ orphaned resources</span>{" "}
          across AWS, Azure & GCP automatically.
          <br className="hidden sm:block" />
          Stop paying for resources you&apos;re not using.
        </p>

        {/* CTAs */}
        <div
          className={`
            flex flex-col sm:flex-row gap-4 justify-center items-center mb-12
            transition-all duration-700 delay-300
            ${isInView ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}
          `}
        >
          <Link
            href="/auth/register"
            className="
              group relative inline-flex items-center gap-3
              px-8 py-4 text-base font-semibold
              bg-cyan-500 hover:bg-cyan-400
              text-zinc-950
              rounded-xl
              transition-all duration-200
              hover:shadow-xl hover:shadow-cyan-500/25
              hover:scale-[1.02]
            "
          >
            <Zap className="h-5 w-5" />
            Start Free Trial
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className="absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75 animate-ping" />
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-400" />
            </span>
          </Link>

          <Link
            href="/auth/login"
            className="
              inline-flex items-center gap-3
              px-8 py-4 text-base font-medium
              bg-zinc-900/50 hover:bg-zinc-800/80
              border border-zinc-800 hover:border-zinc-700
              text-zinc-50
              rounded-xl
              transition-all duration-200
              backdrop-blur-sm
            "
          >
            Sign In
          </Link>
        </div>

        {/* Trust Signals */}
        <div
          className={`
            flex flex-wrap justify-center gap-6 md:gap-10
            transition-all duration-700 delay-400
            ${isInView ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}
          `}
        >
          <TrustSignal icon={Shield} text="100% Read-Only" />
          <TrustSignal icon={Lock} text="Bank-Level Security" />
          <TrustSignal icon={Zap} text="Setup in 2 Minutes" />
        </div>
      </div>

      {/* Bottom gradient fade */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-landing-deep to-transparent" />
    </section>
  );
}

interface TrustSignalProps {
  icon: React.ComponentType<{ className?: string }>;
  text: string;
}

function TrustSignal({ icon: Icon, text }: TrustSignalProps) {
  return (
    <div className="flex items-center gap-2 text-zinc-500">
      <Icon className="h-4 w-4 text-emerald-400" />
      <span className="text-sm">{text}</span>
    </div>
  );
}
