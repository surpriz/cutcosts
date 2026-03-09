"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Check, Loader2, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import useSubscriptionStore from "@/stores/useSubscriptionStore";
import { useAuthStore } from "@/stores/useAuthStore";

export default function PricingPage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const {
    plans,
    currentSubscription,
    isLoadingPlans,
    isCreatingCheckout,
    fetchPlans,
    fetchCurrentSubscription,
    createCheckoutSession,
  } = useSubscriptionStore();

  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);

  useEffect(() => {
    fetchPlans();
    if (user) {
      fetchCurrentSubscription();
    }
  }, [user]);

  const handleSubscribe = async (planName: string) => {
    if (!user) {
      router.push("/auth/login?redirect=/pricing");
      return;
    }

    if (planName === "free") {
      router.push("/dashboard");
      return;
    }

    setSelectedPlan(planName);

    try {
      await createCheckoutSession(
        planName as "pro" | "enterprise",
        `${window.location.origin}/payment/success`,
        `${window.location.origin}/pricing`
      );
    } catch (error) {
      setSelectedPlan(null);
    }
  };

  const isCurrentPlan = (planName: string) => {
    return currentSubscription?.plan.name === planName;
  };

  const getPlanFeatures = (plan: (typeof plans)[number]) => {
    const features: string[] = [];

    // All plans get unlimited scans
    features.push("Unlimited scans");

    // Cloud accounts
    if (plan.max_cloud_accounts === null) {
      features.push("Unlimited cloud accounts");
    } else {
      features.push(`Up to ${plan.max_cloud_accounts} cloud account${plan.max_cloud_accounts > 1 ? "s" : ""}`);
    }

    if (plan.name === "free") {
      // Free-specific features
      features.push("Waste summary & aggregates");
      features.push("Resource count by type");
      features.push("Total savings potential");
    } else {
      // Paid features
      features.push("Full resource details (IDs, names, costs)");
      features.push("Take action on wasteful resources");
      features.push("Cost Intelligence dashboard");
    }

    // Plan-specific features
    if (plan.has_ai_chat) features.push("AI Chat Assistant");
    if (plan.has_impact_tracking) features.push("Environmental Impact Tracking");
    if (plan.has_email_notifications) features.push("Email notifications");
    if (plan.has_api_access) features.push("API Access");
    if (plan.has_priority_support) features.push("Priority Support");

    return features;
  };

  const getPlanBadge = (planName: string) => {
    if (planName === "enterprise") {
      return (
        <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-gradient-to-r from-purple-600 to-blue-600 text-white px-4 py-1 rounded-full text-sm font-semibold flex items-center gap-1">
          <Sparkles className="h-3 w-3" />
          Most Popular
        </div>
      );
    }
    return null;
  };

  if (isLoadingPlans) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white py-12 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Scan Free. Pay Only for Value.
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            All scans are unlimited and free. If we don&apos;t find waste, you never pay.
            Upgrade only to unlock detailed resource insights and take action.
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {plans
            .sort((a, b) => Number(a.price_monthly) - Number(b.price_monthly))
            .map((plan) => {
              const isCurrent = isCurrentPlan(plan.name);
              const isPopular = plan.name === "pro";
              const isLoading = isCreatingCheckout && selectedPlan === plan.name;

              return (
                <Card
                  key={plan.id}
                  className={`relative ${
                    isPopular
                      ? "border-2 border-blue-600 shadow-xl scale-105"
                      : "border border-gray-200"
                  }`}
                >
                  {getPlanBadge(plan.name)}

                  <CardHeader>
                    <CardTitle className="text-2xl">{plan.display_name}</CardTitle>
                    <CardDescription>{plan.description}</CardDescription>
                  </CardHeader>

                  <CardContent className="space-y-6">
                    {/* Price */}
                    <div className="flex items-baseline gap-2">
                      <span className="text-4xl font-bold">
                        €{Number(plan.price_monthly).toFixed(0)}
                      </span>
                      <span className="text-gray-500">/month</span>
                    </div>

                    {/* Features */}
                    <ul className="space-y-3">
                      {getPlanFeatures(plan).map((feature, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <Check className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                          <span className="text-sm text-gray-700">{feature}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>

                  <CardFooter>
                    {isCurrent ? (
                      <Button className="w-full" variant="outline" disabled>
                        Current Plan
                      </Button>
                    ) : (
                      <Button
                        className={`w-full ${
                          isPopular
                            ? "bg-blue-600 hover:bg-blue-700"
                            : ""
                        }`}
                        onClick={() => handleSubscribe(plan.name)}
                        disabled={isLoading}
                      >
                        {isLoading ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Processing...
                          </>
                        ) : plan.name === "free" ? (
                          "Get Started"
                        ) : (
                          "Subscribe"
                        )}
                      </Button>
                    )}
                  </CardFooter>
                </Card>
              );
            })}
        </div>

        {/* FAQ Section */}
        <div className="mt-20 max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold text-center mb-8">
            Frequently Asked Questions
          </h2>
          <div className="space-y-6">
            <div>
              <h3 className="font-semibold mb-2">Are scans really free and unlimited?</h3>
              <p className="text-gray-600">
                Yes. You can scan your cloud accounts as often as you want at no cost.
                If no waste is detected, you never pay anything.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">What do I see on the free plan?</h3>
              <p className="text-gray-600">
                You see aggregated results: total number of wasteful resources, savings
                potential by type, and total monthly cost. Individual resource details
                (names, IDs, exact costs) require a paid plan.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">Can I change my plan later?</h3>
              <p className="text-gray-600">
                Yes, you can upgrade or downgrade your plan at any time. Changes
                will be prorated automatically.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">What payment methods do you accept?</h3>
              <p className="text-gray-600">
                We accept all major credit cards (Visa, Mastercard, American
                Express) via Stripe secure payment processing.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">Can I cancel anytime?</h3>
              <p className="text-gray-600">
                Yes, you can cancel your subscription at any time. You&apos;ll
                continue to have access until the end of your billing period.
              </p>
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="mt-16 text-center">
          <p className="text-gray-600 mb-4">
            Need help choosing the right plan?
          </p>
          <Button variant="outline" onClick={() => router.push("/dashboard")}>
            Go to Dashboard
          </Button>
        </div>
      </div>
    </div>
  );
}
