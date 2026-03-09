"use client";

import { Suspense, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { setAuthTokens } from "@/lib/api";
import { useAuthStore } from "@/stores/useAuthStore";
import { useOnboardingRedirect } from "@/hooks/useOnboardingRedirect";

function OAuthCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const fetchCurrentUser = useAuthStore((state) => state.fetchCurrentUser);
  const { redirectIfNeeded } = useOnboardingRedirect();

  useEffect(() => {
    const accessToken = searchParams.get("access_token");
    const refreshToken = searchParams.get("refresh_token");
    const error = searchParams.get("error");

    if (error === "use_password") {
      router.replace(
        "/auth/login?error=" +
          encodeURIComponent(
            "This email is already registered with a password. Please sign in with your password."
          )
      );
      return;
    }

    if (error === "account_inactive") {
      router.replace(
        "/auth/login?error=" +
          encodeURIComponent("Your account has been deactivated.")
      );
      return;
    }

    if (error || !accessToken || !refreshToken) {
      router.replace(
        "/auth/login?error=" +
          encodeURIComponent(
            "Google sign-in failed. Please try again."
          )
      );
      return;
    }

    // Store tokens
    setAuthTokens({
      access_token: accessToken,
      refresh_token: refreshToken,
      token_type: "bearer",
    });

    // Remove tokens from URL for security
    window.history.replaceState({}, "", "/auth/oauth-callback");

    // Hydrate user in store, then redirect
    fetchCurrentUser().then(() => {
      redirectIfNeeded();
    });
  }, [searchParams, router, fetchCurrentUser, redirectIfNeeded]);

  return (
    <div className="flex min-h-[400px] items-center justify-center">
      <div className="text-center">
        <div className="h-10 w-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-gray-600 text-lg">Completing sign-in...</p>
      </div>
    </div>
  );
}

export default function OAuthCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-[400px] items-center justify-center">
          <div className="h-10 w-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
        </div>
      }
    >
      <OAuthCallbackContent />
    </Suspense>
  );
}
