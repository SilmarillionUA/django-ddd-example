from dataclasses import dataclass
from decimal import Decimal

from lending.domain.settings import CENTS_PER_UNIT


@dataclass(frozen=True)
class LateFee:
    days_late: int
    cents: int

    @property
    def is_charged(self) -> bool:
        return self.cents > 0

    @property
    def amount(self) -> Decimal:
        return Decimal(self.cents) / CENTS_PER_UNIT
