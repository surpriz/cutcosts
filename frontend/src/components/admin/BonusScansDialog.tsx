"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/RadixDialog";
import { Gift, Loader2 } from "lucide-react";
import type { User } from "@/types";

interface BonusScansDialogProps {
  isOpen: boolean;
  onClose: () => void;
  user: User | null;
  onSubmit: (userId: string, bonusScans: number) => Promise<void>;
}

export function BonusScansDialog({
  isOpen,
  onClose,
  user,
  onSubmit,
}: BonusScansDialogProps) {
  const [bonusScans, setBonusScans] = useState<number>(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!user) return;

    setLoading(true);
    setError(null);

    try {
      await onSubmit(user.id, bonusScans);
      setBonusScans(5);
      onClose();
    } catch (err: unknown) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to add bonus scans";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setBonusScans(5);
    setError(null);
    onClose();
  };

  // Check if user has unlimited plan
  const isUnlimited = user?.subscription?.plan?.max_scans_per_month === null;

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Gift className="h-5 w-5 text-purple-600" />
            Add Bonus Scans
          </DialogTitle>
          <DialogDescription>
            {user ? (
              <>
                Add bonus scans for <strong>{user.email}</strong>
              </>
            ) : (
              "Select a user to add bonus scans"
            )}
          </DialogDescription>
        </DialogHeader>

        {isUnlimited ? (
          <div className="py-4">
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
              <p className="text-gray-600">
                This user has an <strong>Enterprise</strong> plan with unlimited
                scans. Bonus scans are not applicable.
              </p>
            </div>
          </div>
        ) : (
          <div className="py-4 space-y-4">
            {/* Current usage display */}
            {user?.subscription && (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                <div className="text-sm text-gray-600 mb-1">Current Usage</div>
                <div className="font-medium text-gray-900">
                  {user.subscription.scans_used_this_month} /{" "}
                  {user.subscription.plan.max_scans_per_month}
                  {user.subscription.bonus_scans_this_month > 0 && (
                    <span className="text-purple-600">
                      {" "}
                      + {user.subscription.bonus_scans_this_month} bonus
                    </span>
                  )}
                </div>
              </div>
            )}

            {/* Bonus scans input */}
            <div>
              <label
                htmlFor="bonus-scans"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Bonus Scans to Add
              </label>
              <input
                id="bonus-scans"
                type="number"
                min={1}
                max={100}
                value={bonusScans}
                onChange={(e) =>
                  setBonusScans(
                    Math.max(1, Math.min(100, parseInt(e.target.value) || 1))
                  )
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
              />
              <p className="mt-1 text-xs text-gray-500">
                Enter a value between 1 and 100
              </p>
            </div>

            {/* Error message */}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded-lg text-sm">
                {error}
              </div>
            )}
          </div>
        )}

        <DialogFooter className="gap-2 sm:gap-0">
          <button
            type="button"
            onClick={handleClose}
            className="px-4 py-2 border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 rounded-lg font-medium transition-colors"
          >
            Cancel
          </button>
          {!isUnlimited && (
            <button
              type="button"
              onClick={handleSubmit}
              disabled={loading}
              className="px-4 py-2 bg-purple-600 text-white hover:bg-purple-700 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {loading && <Loader2 className="h-4 w-4 animate-spin" />}
              Add {bonusScans} Scans
            </button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
