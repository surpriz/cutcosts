"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { BackToTop } from "@/components/layout/BackToTop";
import { OnboardingBanner } from "@/components/onboarding";
import { useAuthStore } from "@/stores/useAuthStore";
import { useAccountStore } from "@/stores/useAccountStore";
import { useScanStore } from "@/stores/useScanStore";
import { useOnboardingStore } from "@/stores/useOnboardingStore";
import { isAuthenticated } from "@/lib/auth";
import { preferencesAPI } from "@/lib/api";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { user, fetchCurrentUser } = useAuthStore();
  const { accounts } = useAccountStore();
  const { scans } = useScanStore();
  const { isCompleted, dismissed, resetOnboarding, completeOnboarding } = useOnboardingStore();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Debug log
  useEffect(() => {
    console.log("[DashboardLayout] Mounted", { user });
  }, []);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/auth/login");
      return;
    }

    if (!user) {
      fetchCurrentUser();
    }
  }, [user, fetchCurrentUser, router]);

  // Sync onboarding state with backend
  // Backend is the source of truth for onboarding status
  useEffect(() => {
    if (!user) return;

    const syncOnboardingStatus = async () => {
      try {
        const status = await preferencesAPI.getOnboardingStatus();
        console.log("[DashboardLayout] Backend onboarding status:", status);

        // Sync local state with backend
        if (!status.should_show_onboarding && !isCompleted && !dismissed) {
          // Backend says skip onboarding - update local state
          console.log("[DashboardLayout] Backend says skip onboarding, updating local state");
          completeOnboarding();
        } else if (status.should_show_onboarding && (isCompleted || dismissed)) {
          // Backend says show onboarding but local says skip - trust backend
          console.log("[DashboardLayout] Backend says show onboarding, resetting local state");
          resetOnboarding();
        }
      } catch (error) {
        console.error("[DashboardLayout] Failed to fetch onboarding status:", error);
        // Fallback to local logic if backend fails
        const isNewUser = accounts.length === 0 && scans.length === 0;
        const onboardingMarkedAsDone = isCompleted || dismissed;

        if (isNewUser && onboardingMarkedAsDone) {
          console.log("[DashboardLayout] Fallback: Detected new user with polluted state, resetting onboarding");
          resetOnboarding();
        }
      }
    };

    syncOnboardingStatus();
  }, [user, accounts.length, scans.length, isCompleted, dismissed, resetOnboarding, completeOnboarding]);

  // Close mobile menu on route change
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [children]);

  if (!isAuthenticated() || !user) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar
        isMobileMenuOpen={isMobileMenuOpen}
        onCloseMobileMenu={() => setIsMobileMenuOpen(false)}
      />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header onOpenMobileMenu={() => setIsMobileMenuOpen(true)} />
        <main className="flex-1 overflow-y-auto p-4 md:p-6">
          {/* Onboarding Banner - shown until setup is complete */}
          <div className="mb-6">
            <OnboardingBanner />
          </div>

          {children}
        </main>
      </div>
      <BackToTop />
    </div>
  );
}
