"""Paywall context dataclass for resource visibility gating."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class PaywallContext:
    """Carries the current user's paywall state for resource endpoints.

    Attributes:
        is_paid: True if user is on Pro or Enterprise plan.
        plan_name: The plan name ('free', 'pro', 'enterprise').
        paywall_cutoff_date: Scans created before this date are visible
            regardless of plan (grandfathering).
    """

    is_paid: bool
    plan_name: str
    paywall_cutoff_date: datetime
