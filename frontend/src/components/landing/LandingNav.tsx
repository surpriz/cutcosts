"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

export function LandingNav() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <nav
      className={`
        fixed top-0 left-0 right-0 z-50
        transition-all duration-300
        ${
          scrolled
            ? "bg-zinc-950/80 backdrop-blur-xl border-b border-zinc-800/50"
            : "bg-transparent"
        }
      `}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 md:h-20">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2">
            <span className="text-2xl font-bold text-zinc-50">
              Cut<span className="gradient-text-cyan-violet">Costs</span>
            </span>
          </Link>

          {/* Navigation Links - Hidden on mobile */}
          <div className="hidden md:flex items-center gap-8">
            <NavLink href="#features">Features</NavLink>
            <NavLink href="#how-it-works">How It Works</NavLink>
            <NavLink href="/pricing">Pricing</NavLink>
          </div>

          {/* CTAs */}
          <div className="flex items-center gap-3">
            <Link
              href="/auth/login"
              className="
                hidden sm:inline-flex
                px-4 py-2 text-sm font-medium
                text-zinc-400 hover:text-zinc-50
                transition-colors
              "
            >
              Sign In
            </Link>
            <Link
              href="/auth/register"
              className="
                inline-flex items-center gap-2
                px-4 py-2 text-sm font-semibold
                bg-cyan-500 hover:bg-cyan-400
                text-zinc-950
                rounded-lg
                transition-all duration-200
                hover:shadow-lg hover:shadow-cyan-500/25
              "
            >
              Scan for Free
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}

interface NavLinkProps {
  href: string;
  children: React.ReactNode;
}

function NavLink({ href, children }: NavLinkProps) {
  return (
    <Link
      href={href}
      className="
        text-sm font-medium
        text-zinc-400 hover:text-zinc-50
        transition-colors
      "
    >
      {children}
    </Link>
  );
}
