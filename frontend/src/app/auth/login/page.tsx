"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { useAuthStore } from "@/stores/useAuthStore";
import { authAPI } from "@/lib/api";
import { useOnboardingRedirect } from "@/hooks/useOnboardingRedirect";
import { LogIn, Mail, Lock, ArrowRight } from "lucide-react";

function LoginContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const login = useAuthStore((state) => state.login);
  const isLoading = useAuthStore((state) => state.isLoading);
  const storeError = useAuthStore((state) => state.error);
  const clearError = useAuthStore((state) => state.clearError);
  const { redirectIfNeeded } = useOnboardingRedirect();

  const [urlError, setUrlError] = useState<string | null>(null);
  const [lastLoginMethod, setLastLoginMethod] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    username: "",
    password: "",
    remember_me: false,
  });

  // Read last login method and error from URL query params
  useEffect(() => {
    setLastLoginMethod(localStorage.getItem("last_login_method"));

    const errorParam = searchParams.get("error");
    if (errorParam) {
      setUrlError(decodeURIComponent(errorParam));
      window.history.replaceState({}, "", "/auth/login");
    }
  }, [searchParams]);

  const error = storeError || urlError;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setUrlError(null);

    try {
      await login(formData);
      localStorage.setItem("last_login_method", "email");
      await redirectIfNeeded();
    } catch (err) {
      console.error("Login error:", err);
    }
  };

  return (
    <div className="relative rounded-2xl bg-white p-6 md:p-10 shadow-2xl border border-gray-100 max-w-md w-full">
      {/* Decorative gradient */}
      <div className="absolute -top-2 -right-2 h-20 w-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl opacity-20 blur-2xl"></div>
      <div className="absolute -bottom-2 -left-2 h-20 w-20 bg-gradient-to-br from-green-500 to-blue-600 rounded-2xl opacity-20 blur-2xl"></div>

      <div className="relative z-10">
        <div className="mb-6 md:mb-8 text-center">
          <div className="inline-flex items-center justify-center h-14 w-14 md:h-16 md:w-16 rounded-2xl bg-gradient-to-br from-blue-600 to-purple-600 shadow-lg mb-3 md:mb-4">
            <LogIn className="h-7 w-7 md:h-8 md:w-8 text-white" />
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            CutCosts
          </h1>
          <p className="mt-2 md:mt-3 text-gray-600 text-base md:text-lg">Welcome back! Sign in to continue</p>
        </div>

        {error && (
          <div className="mb-6 rounded-xl bg-red-50 border border-red-200 p-4 text-sm text-red-700">
            <div className="flex items-start gap-2 mb-2">
              <span className="text-lg">⚠️</span>
              <span>{error}</span>
            </div>
            {error.toLowerCase().includes("email not verified") && (
              <div className="mt-3 pl-7">
                <Link
                  href={`/auth/verify-email-sent?email=${encodeURIComponent(formData.username)}`}
                  className="inline-block text-blue-600 hover:text-blue-700 font-medium underline"
                >
                  Resend verification email →
                </Link>
              </div>
            )}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label
              htmlFor="username"
              className="block text-sm font-semibold text-gray-700 mb-2"
            >
              Email Address
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                id="username"
                type="email"
                required
                value={formData.username}
                onChange={(e) =>
                  setFormData({ ...formData, username: e.target.value })
                }
                className="block w-full rounded-xl border border-gray-300 pl-11 pr-4 py-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all"
                placeholder="you@company.com"
              />
            </div>
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-semibold text-gray-700 mb-2"
            >
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                id="password"
                type="password"
                required
                value={formData.password}
                onChange={(e) =>
                  setFormData({ ...formData, password: e.target.value })
                }
                className="block w-full rounded-xl border border-gray-300 pl-11 pr-4 py-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all"
                placeholder="••••••••"
              />
            </div>
            <div className="flex justify-end mt-1">
              <Link
                href="/auth/forgot-password"
                className="text-sm text-blue-600 hover:text-purple-600 transition-colors"
              >
                Forgot password?
              </Link>
            </div>
          </div>

          <div className="flex items-center">
            <input
              id="remember_me"
              type="checkbox"
              checked={formData.remember_me}
              onChange={(e) =>
                setFormData({ ...formData, remember_me: e.target.checked })
              }
              className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-2 focus:ring-blue-500/20 transition-all cursor-pointer"
            />
            <label
              htmlFor="remember_me"
              className="ml-2 text-sm text-gray-600 cursor-pointer select-none"
            >
              Remember me for 30 days
            </label>
          </div>

          <div className="relative">
            <button
              type="submit"
              disabled={isLoading}
              className="group w-full rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-3 font-semibold text-white shadow-lg hover:shadow-xl transition-all hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <div className="h-5 w-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  Signing in...
                </>
              ) : (
                <>
                  Sign in to Dashboard
                  <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
            {lastLoginMethod === "email" && (
              <span className="absolute -top-2 -right-2 bg-blue-600 text-white text-[10px] font-bold px-2 py-0.5 rounded-full shadow-sm">
                Last used
              </span>
            )}
          </div>
        </form>

        {/* OAuth divider */}
        <div className="mt-6">
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="bg-white px-4 text-gray-500">Or continue with</span>
            </div>
          </div>
          <div className="relative mt-4">
            <button
              type="button"
              onClick={() => authAPI.googleLogin()}
              className="w-full flex items-center justify-center gap-3 rounded-xl border border-gray-300 bg-white px-6 py-3 font-semibold text-gray-700 shadow-sm hover:bg-gray-50 hover:shadow transition-all"
            >
              <svg className="h-5 w-5" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              Continue with Google
            </button>
            {lastLoginMethod === "google" && (
              <span className="absolute -top-2 -right-2 bg-blue-600 text-white text-[10px] font-bold px-2 py-0.5 rounded-full shadow-sm">
                Last used
              </span>
            )}
          </div>
        </div>

        <div className="mt-8 text-center">
          <p className="text-gray-600">
            Don&apos;t have an account?{" "}
            <Link
              href="/auth/register"
              className="font-semibold text-blue-600 hover:text-purple-600 transition-colors"
            >
              Create one now →
            </Link>
          </p>
        </div>

        <div className="mt-6 pt-6 border-t border-gray-200">
          <Link
            href="/"
            className="flex items-center justify-center gap-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
          >
            ← Back to home
          </Link>
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <div className="relative rounded-2xl bg-white p-6 md:p-10 shadow-2xl border border-gray-100 max-w-md w-full">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="h-10 w-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
          </div>
        </div>
      }
    >
      <LoginContent />
    </Suspense>
  );
}
