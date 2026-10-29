from dataclasses import dataclass

from catalog.domain.exceptions import InvalidIsbn

ISBN_10_LENGTH = 10
ISBN_13_LENGTH = 13
# The last character of an ISBN-10 may be X, which stands for ten.
ISBN_10_TEN_CHECK = "X"
ISBN_SEPARATORS = ("-", " ")


@dataclass(frozen=True)
class Isbn:
    """
    A book number with dashes and spaces taken out.

    People type ISBNs in many shapes. Only the digits say which book
    it is, so two spellings of one number must compare equal. Build it
    with `from_raw`, which refuses anything that cannot be an ISBN.
    """

    value: str

    @classmethod
    def from_raw(cls, raw: str) -> "Isbn":
        cleaned = raw.strip().upper()
        for separator in ISBN_SEPARATORS:
            cleaned = cleaned.replace(separator, "")

        if not cls._is_well_formed(cleaned):
            raise InvalidIsbn(raw)

        return cls(value=cleaned)

    @staticmethod
    def _is_well_formed(cleaned: str) -> bool:
        if len(cleaned) == ISBN_13_LENGTH:
            return cleaned.isdigit()

        if len(cleaned) == ISBN_10_LENGTH:
            body, check = cleaned[:-1], cleaned[-1]
            return body.isdigit() and (
                check.isdigit() or check == ISBN_10_TEN_CHECK
            )

        return False

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class BookDetails:
    """What an outside catalogue knows about a book."""

    title: str = ""
    page_count: int | None = None
