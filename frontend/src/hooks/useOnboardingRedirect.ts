/**
 * Hook for automatic onboarding redirection after login/registration
 */

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useOnboardingStore } from "@/stores/useOnboardingStore";
import { preferencesAPI } from "@/lib/api";

/**
 * Auto-redirect to onboarding if not completed
 *
 * Usage: Call this hook after successful login/registration
 *
 * @example
 * ```tsx
 * function LoginPage() {
 *   const { redirectIfNeeded, isChecking } = useOnboardingRedirect();
 *
 *   const handleLogin = async () => {
 *     await login();
 *     await redirectIfNeeded(); // Will redirect if onboarding not done
 *   };
 * }
 * ```
 */
export function useOnboardingRedirect() {
  const router = useRouter();
  const { isCompleted, dismissed, completeOnboarding } = useOnboardingStore();
  const [isChecking, setIsChecking] = useState(false);

  const redirectIfNeeded = useCallback(async () => {
    setIsChecking(true);

    try {
      // Fetch fresh status from backend
      const status = await preferencesAPI.getOnboardingStatus();

      console.log("[useOnboardingRedirect] Backend status:", status);

      // Sync local store with backend state
      if (!status.should_show_onboarding && !isCompleted && !dismissed) {
        completeOnboarding();
      }

      if (!status.should_show_onboarding) {
        console.log("[useOnboardingRedirect] Redirecting to /dashboard (backend says skip)");
        router.push("/dashboard");
      } else {
        console.log("[useOnboardingRedirect] Redirecting to /onboarding (backend says show)");
        router.push("/onboarding");
      }
    } catch (error) {
      console.error("[useOnboardingRedirect] Backend check failed, using localStorage:", error);

      // Fallback to localStorage state if backend fails
      if (isCompleted || dismissed) {
        console.log("[useOnboardingRedirect] Fallback: Redirecting to /dashboard");
        router.push("/dashboard");
      } else {
        console.log("[useOnboardingRedirect] Fallback: Redirecting to /onboarding");
        router.push("/onboarding");
      }
    } finally {
      setIsChecking(false);
    }
  }, [router, isCompleted, dismissed, completeOnboarding]);

  return { redirectIfNeeded, isChecking };
}

/**
 * Auto-redirect hook with useEffect (automatic version)
 *
 * Automatically redirects when component mounts.
 * Use this in protected routes after login.
 *
 * @example
 * ```tsx
 * function DashboardRedirect() {
 *   useAutoOnboardingRedirect();
 *   return <div>Redirecting...</div>;
 * }
 * ```
 */
export function useAutoOnboardingRedirect() {
  const { redirectIfNeeded } = useOnboardingRedirect();

  useEffect(() => {
    redirectIfNeeded();
  }, [redirectIfNeeded]);
}
