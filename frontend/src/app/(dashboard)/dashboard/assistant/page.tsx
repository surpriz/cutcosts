/**
 * AI Assistant page - Chat interface with FinOps AI
 * Requires Pro or Enterprise subscription
 */

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import useSubscriptionStore from "@/stores/useSubscriptionStore";
import { ChatSidebar } from "@/components/chat/ChatSidebar";
import { ChatWindow } from "@/components/chat/ChatWindow";
import { UpgradeDialog } from "@/components/subscription/UpgradeDialog";
import { ArrowLeft, Loader2 } from "lucide-react";
import Link from "next/link";

export default function AssistantPage() {
  const router = useRouter();
  const { subscription, fetchCurrentSubscription } = useSubscriptionStore();
  const [isLoading, setIsLoading] = useState(true);
  const [showUpgradeDialog, setShowUpgradeDialog] = useState(false);

  useEffect(() => {
    const checkAccess = async () => {
      await fetchCurrentSubscription();
      setIsLoading(false);
    };
    checkAccess();
  }, [fetchCurrentSubscription]);

  // Check if user has Pro/Enterprise plan
  useEffect(() => {
    if (!isLoading && subscription?.plan.name === "free") {
      setShowUpgradeDialog(true);
    }
  }, [isLoading, subscription]);

  if (isLoading) {
    return (
      <div className="flex h-[calc(100vh-4rem)] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (subscription?.plan.name === "free") {
    return (
      <UpgradeDialog
        open={showUpgradeDialog}
        onOpenChange={(open) => {
          if (!open) {
            router.push("/dashboard");
          }
        }}
        reason="ai_chat"
      />
    );
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-gray-900">
      <ChatSidebar />
      <div className="flex-1 flex flex-col">
        {/* Header with back button */}
        <div className="bg-gray-800 border-b border-gray-700 px-6 py-3 flex items-center gap-3">
          <Link
            href="/dashboard"
            className="flex items-center gap-2 text-gray-300 hover:text-white transition-colors"
          >
            <ArrowLeft className="h-5 w-5" />
            <span className="text-sm font-medium">Back to Dashboard</span>
          </Link>
          <div className="h-5 w-px bg-gray-600 mx-2" />
          <h1 className="text-lg font-semibold text-white">AI Assistant FinOps</h1>
        </div>

        {/* Chat content */}
        <div className="flex-1 overflow-hidden">
          <ChatWindow />
        </div>
      </div>
    </div>
  );
}
