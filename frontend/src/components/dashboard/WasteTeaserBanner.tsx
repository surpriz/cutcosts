"use client";

import { useRouter } from "next/navigation";
import { AlertTriangle, ArrowRight, Lock, TrendingDown } from "lucide-react";
import { Button } from "@/components/ui/button";

interface WasteTeaserBannerProps {
  resourceCount: number;
  monthlyCost: number;
  byType: Record<string, number>;
}

function formatResourceTypeName(type: string): string {
  return type
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

export function WasteTeaserBanner({
  resourceCount,
  monthlyCost,
  byType,
}: WasteTeaserBannerProps) {
  const router = useRouter();
  const topTypes = Object.entries(byType)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 3);

  return (
    <div className="relative overflow-hidden rounded-2xl border-2 border-orange-300 bg-gradient-to-br from-orange-50 via-amber-50 to-red-50 p-6 shadow-xl">
      {/* Decorative blobs */}
      <div className="absolute top-0 right-0 h-48 w-48 bg-orange-300 rounded-full blur-3xl opacity-20 pointer-events-none" />
      <div className="absolute bottom-0 left-0 h-32 w-32 bg-red-300 rounded-full blur-3xl opacity-20 pointer-events-none" />

      <div className="relative z-10">
        <div className="flex items-start gap-4">
          {/* Icon */}
          <div className="flex-shrink-0 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-orange-500 to-red-500 shadow-lg">
            <AlertTriangle className="h-7 w-7 text-white" />
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="text-xl font-extrabold text-gray-900">
                Waste Detected in Your Cloud
              </h3>
              <span className="inline-flex items-center gap-1 rounded-full bg-orange-100 border border-orange-300 px-3 py-1 text-xs font-bold text-orange-800">
                <Lock className="h-3 w-3" />
                Free Plan
              </span>
            </div>

            <p className="mt-1 text-gray-700 font-medium">
              Your scan found{" "}
              <span className="font-extrabold text-orange-700">
                {resourceCount} orphaned resource
                {resourceCount !== 1 ? "s" : ""}
              </span>{" "}
              costing approximately{" "}
              <span className="font-extrabold text-red-700">
                ~${monthlyCost.toFixed(0)}/month
              </span>
            </p>

            {/* Type summary */}
            {topTypes.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-2">
                {topTypes.map(([type, count]) => (
                  <span
                    key={type}
                    className="inline-flex items-center px-2.5 py-1 rounded-lg bg-white/70 border border-orange-200 text-xs font-semibold text-gray-700"
                  >
                    {count}x {formatResourceTypeName(type)}
                  </span>
                ))}
                {Object.keys(byType).length > 3 && (
                  <span className="inline-flex items-center px-2.5 py-1 rounded-lg bg-white/70 border border-orange-200 text-xs font-semibold text-gray-500">
                    +{Object.keys(byType).length - 3} more types
                  </span>
                )}
              </div>
            )}

            {/* Annual projection */}
            <div className="mt-3 flex items-center gap-1 text-sm text-gray-600">
              <TrendingDown className="h-4 w-4 text-red-500 flex-shrink-0" />
              <span>
                That&apos;s{" "}
                <strong className="text-red-700">
                  ~${(monthlyCost * 12).toFixed(0)}/year
                </strong>{" "}
                you could save — upgrade to see exactly which resources to remove
              </span>
            </div>
          </div>
        </div>

        {/* CTA row */}
        <div className="mt-5 flex flex-col sm:flex-row gap-3">
          <Button
            onClick={() => router.push("/pricing")}
            className="flex-1 sm:flex-none bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white border-0 shadow-md hover:shadow-lg transition-all"
          >
            <ArrowRight className="mr-2 h-4 w-4" />
            Unlock Full Waste Report
          </Button>
          <Button
            variant="outline"
            onClick={() => router.push("/dashboard/resources")}
            className="flex-1 sm:flex-none border-orange-300 text-orange-700 hover:bg-orange-50"
          >
            See Aggregates Only
          </Button>
        </div>
      </div>
    </div>
  );
}
