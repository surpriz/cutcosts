"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { authAPI } from "@/lib/api";
import { Lock, ArrowLeft, KeyRound, CheckCircle, Eye, EyeOff } from "lucide-react";

export default function ResetPasswordPage() {
  const params = useParams();
  const router = useRouter();
  const token = params.token as string;

  const [formData, setFormData] = useState({
    newPassword: "",
    confirmPassword: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState("");

  const validateForm = (): string | null => {
    if (formData.newPassword.length < 8) {
      return "Password must be at least 8 characters long";
    }
    if (formData.newPassword !== formData.confirmPassword) {
      return "Passwords do not match";
    }
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsLoading(true);

    try {
      await authAPI.resetPassword(token, formData.newPassword);
      setIsSuccess(true);
      setTimeout(() => {
        router.push("/auth/login");
      }, 3000);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Failed to reset password. The link may be invalid or expired.";
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  if (isSuccess) {
    return (
      <div className="relative rounded-2xl bg-white p-6 md:p-10 shadow-2xl border border-gray-100 max-w-md w-full">
        <div className="absolute -top-2 -right-2 h-20 w-20 bg-gradient-to-br from-green-500 to-blue-600 rounded-2xl opacity-20 blur-2xl"></div>
        <div className="absolute -bottom-2 -left-2 h-20 w-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl opacity-20 blur-2xl"></div>

        <div className="relative z-10 text-center">
          <div className="inline-flex items-center justify-center h-14 w-14 md:h-16 md:w-16 rounded-2xl bg-gradient-to-br from-green-500 to-blue-600 shadow-lg mb-4">
            <CheckCircle className="h-7 w-7 md:h-8 md:w-8 text-white" />
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-gray-900 mb-3">
            Password Reset!
          </h1>
          <p className="text-gray-600 mb-6">
            Your password has been successfully reset.
          </p>

          <div className="bg-green-50 border border-green-200 rounded-xl p-4 mb-6">
            <p className="text-sm text-green-800">
              Redirecting to login page in a moment...
            </p>
          </div>

          <Link
            href="/auth/login"
            className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all hover:scale-[1.02]"
          >
            Sign in now
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="relative rounded-2xl bg-white p-6 md:p-10 shadow-2xl border border-gray-100 max-w-md w-full">
      <div className="absolute -top-2 -right-2 h-20 w-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl opacity-20 blur-2xl"></div>
      <div className="absolute -bottom-2 -left-2 h-20 w-20 bg-gradient-to-br from-green-500 to-blue-600 rounded-2xl opacity-20 blur-2xl"></div>

      <div className="relative z-10">
        <div className="mb-6 md:mb-8 text-center">
          <div className="inline-flex items-center justify-center h-14 w-14 md:h-16 md:w-16 rounded-2xl bg-gradient-to-br from-blue-600 to-purple-600 shadow-lg mb-3 md:mb-4">
            <KeyRound className="h-7 w-7 md:h-8 md:w-8 text-white" />
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-gray-900">
            Reset Your Password
          </h1>
          <p className="mt-2 md:mt-3 text-gray-600 text-base">
            Enter your new password below
          </p>
        </div>

        {error && (
          <div className="mb-6 rounded-xl bg-red-50 border border-red-200 p-4 text-sm text-red-700">
            <div className="flex items-start gap-2">
              <span className="text-lg">&#9888;&#65039;</span>
              <span>{error}</span>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label
              htmlFor="newPassword"
              className="block text-sm font-semibold text-gray-700 mb-2"
            >
              New Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                id="newPassword"
                type={showPassword ? "text" : "password"}
                required
                minLength={8}
                value={formData.newPassword}
                onChange={(e) =>
                  setFormData({ ...formData, newPassword: e.target.value })
                }
                className="block w-full rounded-xl border border-gray-300 pl-11 pr-11 py-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all"
                placeholder="Minimum 8 characters"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                {showPassword ? (
                  <EyeOff className="h-5 w-5" />
                ) : (
                  <Eye className="h-5 w-5" />
                )}
              </button>
            </div>
          </div>

          <div>
            <label
              htmlFor="confirmPassword"
              className="block text-sm font-semibold text-gray-700 mb-2"
            >
              Confirm New Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                id="confirmPassword"
                type={showConfirmPassword ? "text" : "password"}
                required
                minLength={8}
                value={formData.confirmPassword}
                onChange={(e) =>
                  setFormData({ ...formData, confirmPassword: e.target.value })
                }
                className="block w-full rounded-xl border border-gray-300 pl-11 pr-11 py-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all"
                placeholder="Re-enter your password"
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                {showConfirmPassword ? (
                  <EyeOff className="h-5 w-5" />
                ) : (
                  <Eye className="h-5 w-5" />
                )}
              </button>
            </div>
            {formData.confirmPassword && formData.newPassword !== formData.confirmPassword && (
              <p className="mt-1 text-sm text-red-600">Passwords do not match</p>
            )}
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-xl p-3">
            <p className="text-xs text-blue-800">
              Password must be at least 8 characters long.
            </p>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="group w-full rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-3 font-semibold text-white shadow-lg hover:shadow-xl transition-all hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <div className="h-5 w-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                Resetting...
              </>
            ) : (
              <>
                Reset Password
                <KeyRound className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </>
            )}
          </button>
        </form>

        <div className="mt-8 text-center">
          <Link
            href="/auth/login"
            className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Login
          </Link>
        </div>
      </div>
    </div>
  );
}
