class CatalogError(Exception):
    """Base for catalog domain errors."""

    code = "catalog_error"


class InvalidIsbn(CatalogError):
    code = "invalid_isbn"


class DuplicateIsbn(CatalogError):
    code = "duplicate_isbn"


class CopyCountOutOfRange(CatalogError):
    code = "copy_count_out_of_range"
