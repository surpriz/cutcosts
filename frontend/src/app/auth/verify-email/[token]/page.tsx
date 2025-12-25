"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { authAPI } from "@/lib/api";
import { CheckCircle, XCircle, Loader2 } from "lucide-react";
import Link from "next/link";

export default function VerifyEmailTokenPage() {
  const params = useParams();
  const router = useRouter();
  const token = params.token as string;

  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    const verifyEmail = async () => {
      try {
        const response = await authAPI.verifyEmail(token);
        setStatus("success");
        setMessage(response.message);

        // Redirect to login after 3 seconds
        setTimeout(() => {
          router.push("/auth/login");
        }, 3000);
      } catch (error: any) {
        setStatus("error");
        setMessage(error.message || "Failed to verify email");
      }
    };

    if (token) {
      verifyEmail();
    }
  }, [token, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900 px-4">
      <div className="max-w-md w-full">
        <div className="bg-gray-800 rounded-lg shadow-xl p-8 border border-gray-700">
          {/* Loading State */}
          {status === "loading" && (
            <div className="text-center">
              <div className="flex justify-center mb-6">
                <div className="w-16 h-16 bg-blue-600/20 rounded-full flex items-center justify-center">
                  <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
                </div>
              </div>
              <h1 className="text-2xl font-bold text-white mb-2">
                Verifying...
              </h1>
              <p className="text-gray-400">
                Please wait while we verify your email.
              </p>
            </div>
          )}

          {/* Success State */}
          {status === "success" && (
            <div className="text-center">
              <div className="flex justify-center mb-6">
                <div className="w-16 h-16 bg-green-600/20 rounded-full flex items-center justify-center">
                  <CheckCircle className="w-8 h-8 text-green-400" />
                </div>
              </div>
              <h1 className="text-2xl font-bold text-white mb-2">
                🎉 Email verified!
              </h1>
              <p className="text-gray-400 mb-6">
                {message}
              </p>
              <div className="bg-green-900/20 border border-green-800/30 rounded-lg p-4 mb-6">
                <p className="text-sm text-green-200">
                  ✅ Your account is now active. You will be redirected to the login page...
                </p>
              </div>
              <Link
                href="/auth/login"
                className="inline-block bg-green-600 hover:bg-green-700 text-white py-3 px-6 rounded-lg font-medium transition-colors"
              >
                Sign in now
              </Link>
            </div>
          )}

          {/* Error State */}
          {status === "error" && (
            <div className="text-center">
              <div className="flex justify-center mb-6">
                <div className="w-16 h-16 bg-red-600/20 rounded-full flex items-center justify-center">
                  <XCircle className="w-8 h-8 text-red-400" />
                </div>
              </div>
              <h1 className="text-2xl font-bold text-white mb-2">
                ❌ Verification error
              </h1>
              <p className="text-gray-400 mb-6">
                {message}
              </p>
              <div className="bg-red-900/20 border border-red-800/30 rounded-lg p-4 mb-6">
                <p className="text-sm text-red-200 mb-2">
                  <strong>Possible reasons:</strong>
                </p>
                <ul className="text-sm text-red-300 text-left pl-6 list-disc space-y-1">
                  <li>The link has expired (7 days maximum)</li>
                  <li>The link has already been used</li>
                  <li>The link is invalid</li>
                </ul>
              </div>
              <div className="space-y-3">
                <Link
                  href="/auth/register"
                  className="block w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-lg font-medium transition-colors"
                >
                  Create a new account
                </Link>
                <Link
                  href="/auth/login"
                  className="block w-full bg-gray-700 hover:bg-gray-600 text-white py-3 px-4 rounded-lg font-medium transition-colors"
                >
                  Back to login
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
