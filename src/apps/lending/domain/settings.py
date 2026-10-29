"""
The lending rules, in one place.

A loan runs three weeks, which covers most novels read in the evenings.
Five open loans is enough for a family card and stops one member from
emptying a shelf. Two renewals let a slow reader finish without letting
a popular book vanish for months.
"""

LOAN_PERIOD_DAYS = 21
MAX_OPEN_LOANS_PER_MEMBER = 5
MAX_RENEWALS = 2

# Members hear about a due date this many days before it.
REMINDER_DAYS_BEFORE_DUE = 2

# A book back a day or two late costs nothing. Weekends and bank
# holidays catch everyone. After that each late day counts, up to a cap,
# because a lost book is a separate conversation and not a growing fee.
LATE_FEE_CENTS_PER_DAY = 25
LATE_FEE_GRACE_DAYS = 2
LATE_FEE_MAX_CENTS = 1000
CENTS_PER_UNIT = 100

# The "my loans" page shows one screen. The cut happens in SQL.
MAX_LOANS_ON_PAGE = 100
