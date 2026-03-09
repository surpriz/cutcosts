"use client";

import { Lock, ArrowRight, TrendingDown } from "lucide-react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";

interface PaywallOverlayProps {
  children: React.ReactNode;
  isLocked: boolean;
  resourceCount?: number;
  monthlyCost?: number;
  title?: string;
  compact?: boolean;
}

function formatCost(amount: number): string {
  if (amount >= 1000) return `$${(amount / 1000).toFixed(1)}k`;
  return `$${amount.toFixed(0)}`;
}

export function PaywallOverlay({
  children,
  isLocked,
  resourceCount,
  monthlyCost,
  title = "Upgrade to see full details",
  compact = false,
}: PaywallOverlayProps) {
  const router = useRouter();

  if (!isLocked) {
    return <>{children}</>;
  }

  return (
    <div className="relative">
      {/* Blurred content underneath */}
      <div
        className="select-none pointer-events-none blur-md opacity-70"
        aria-hidden="true"
      >
        {children}
      </div>

      {/* Upgrade CTA overlay */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div
          className={`
            flex flex-col items-center gap-3 rounded-2xl border border-orange-200
            bg-white/90 shadow-xl backdrop-blur-sm text-center
            ${compact ? "p-4 max-w-xs" : "p-8 max-w-sm"}
          `}
        >
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-orange-500 to-red-500 shadow-md">
            <Lock className="h-5 w-5 text-white" />
          </div>

          {resourceCount !== undefined && monthlyCost !== undefined && (
            <div className="rounded-xl bg-orange-50 border border-orange-200 px-4 py-2">
              <p className="text-sm font-bold text-orange-900">
                {resourceCount} wasteful resource
                {resourceCount !== 1 ? "s" : ""} detected
              </p>
              <p className="text-xs text-orange-700 mt-0.5 flex items-center justify-center gap-1">
                <TrendingDown className="h-3 w-3" />~{formatCost(monthlyCost)}
                /month in waste
              </p>
            </div>
          )}

          <div>
            <p className="font-semibold text-gray-900 text-sm">{title}</p>
            <p className="text-xs text-gray-500 mt-1">
              Upgrade to Pro to see resource IDs, names, costs, and take action
            </p>
          </div>

          <Button
            onClick={() => router.push("/pricing")}
            size={compact ? "sm" : "default"}
            className="w-full bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white border-0"
          >
            <ArrowRight className="mr-2 h-4 w-4" />
            Unlock Full Access
          </Button>
        </div>
      </div>
    </div>
  );
}
