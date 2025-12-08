"use client";

import { useState } from "react";
import Link from "next/link";
import { authAPI } from "@/lib/api";
import { Mail, ArrowLeft, Send, CheckCircle } from "lucide-react";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      await authAPI.forgotPassword(email);
      setIsSubmitted(true);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "An error occurred. Please try again.";
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  if (isSubmitted) {
    return (
      <div className="relative rounded-2xl bg-white p-6 md:p-10 shadow-2xl border border-gray-100 max-w-md w-full">
        <div className="absolute -top-2 -right-2 h-20 w-20 bg-gradient-to-br from-green-500 to-blue-600 rounded-2xl opacity-20 blur-2xl"></div>
        <div className="absolute -bottom-2 -left-2 h-20 w-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl opacity-20 blur-2xl"></div>

        <div className="relative z-10 text-center">
          <div className="inline-flex items-center justify-center h-14 w-14 md:h-16 md:w-16 rounded-2xl bg-gradient-to-br from-green-500 to-blue-600 shadow-lg mb-4">
            <CheckCircle className="h-7 w-7 md:h-8 md:w-8 text-white" />
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-gray-900 mb-3">
            Check Your Email
          </h1>
          <p className="text-gray-600 mb-6">
            If an account with <span className="font-semibold text-blue-600">{email}</span> exists,
            we&apos;ve sent you a password reset link.
          </p>

          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6 text-left">
            <p className="text-sm text-blue-800 font-medium mb-2">Next steps:</p>
            <ol className="text-sm text-blue-700 space-y-1 pl-4 list-decimal">
              <li>Check your email inbox</li>
              <li>Click the reset link (expires in 1 hour)</li>
              <li>Create a new password</li>
            </ol>
          </div>

          <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-3 mb-6">
            <p className="text-xs text-yellow-800">
              Don&apos;t see the email? Check your spam folder.
            </p>
          </div>

          <Link
            href="/auth/login"
            className="inline-flex items-center gap-2 text-blue-600 hover:text-purple-600 font-medium transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Login
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
            <Mail className="h-7 w-7 md:h-8 md:w-8 text-white" />
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-gray-900">
            Forgot Password?
          </h1>
          <p className="mt-2 md:mt-3 text-gray-600 text-base">
            Enter your email and we&apos;ll send you a reset link
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
              htmlFor="email"
              className="block text-sm font-semibold text-gray-700 mb-2"
            >
              Email Address
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="block w-full rounded-xl border border-gray-300 pl-11 pr-4 py-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all"
                placeholder="you@company.com"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="group w-full rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-3 font-semibold text-white shadow-lg hover:shadow-xl transition-all hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <div className="h-5 w-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                Sending...
              </>
            ) : (
              <>
                Send Reset Link
                <Send className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
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
