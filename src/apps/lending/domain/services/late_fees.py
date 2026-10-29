from dataclasses import dataclass
from datetime import date

from lending.domain.settings import (
    LATE_FEE_CENTS_PER_DAY,
    LATE_FEE_GRACE_DAYS,
    LATE_FEE_MAX_CENTS,
)
from lending.domain.types import LateFee


@dataclass(frozen=True)
class LateFeePolicy:
    cents_per_day: int = LATE_FEE_CENTS_PER_DAY
    grace_days: int = LATE_FEE_GRACE_DAYS
    max_cents: int = LATE_FEE_MAX_CENTS


class LateFeeCalculator:
    """
    How much a late return costs.

    Pure arithmetic on dates, with no database and no clock, so every
    rule can be tested with plain values. Grace days are free, the days
    after them are charged, and the total stops at the cap.
    """

    def __init__(self, *, policy: LateFeePolicy = LateFeePolicy()) -> None:
        self._policy = policy

    def fee_for(self, *, due_on: date, returned_on: date) -> LateFee:
        days_late = max((returned_on - due_on).days, 0)
        charged_days = max(days_late - self._policy.grace_days, 0)

        return LateFee(
            days_late=days_late,
            cents=min(
                charged_days * self._policy.cents_per_day,
                self._policy.max_cents,
            ),
        )
