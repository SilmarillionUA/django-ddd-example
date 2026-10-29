from datetime import date, timedelta

import pytest

from lending.domain.services.late_fees import LateFeeCalculator, LateFeePolicy

DUE_ON = date(2026, 3, 10)
POLICY = LateFeePolicy(cents_per_day=25, grace_days=2, max_cents=100)


def fee_after(days):
    return LateFeeCalculator(policy=POLICY).fee_for(
        due_on=DUE_ON, returned_on=DUE_ON + timedelta(days=days)
    )


@pytest.mark.unit
@pytest.mark.parametrize("days", [-3, 0, 1, 2])
def test_early_on_time_and_grace_days_are_free(days):
    assert fee_after(days).cents == 0


@pytest.mark.unit
def test_days_after_grace_are_charged():
    fee = fee_after(4)

    assert (fee.days_late, fee.cents) == (4, 50)


@pytest.mark.unit
def test_fee_stops_at_the_cap():
    assert fee_after(60).cents == POLICY.max_cents
