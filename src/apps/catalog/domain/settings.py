# One request adds a shelf's worth of copies at most. A bigger number
# is almost always a typo in the form.
MAX_COPIES_PER_BOOK_REQUEST = 20

# A barcode is the cleaned ISBN, a dash and a three-digit copy number.
BARCODE_MAX_LENGTH = 32
COPY_NUMBER_DIGITS = 3

# The search page shows one screen of books. The cut happens in SQL.
MAX_BOOKS_ON_PAGE = 50
