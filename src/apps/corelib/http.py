from django.http import HttpRequest

HTMX_REQUEST_HEADER = "HX-Request"
HTMX_REQUEST_VALUE = "true"


def is_htmx(request: HttpRequest) -> bool:
    return request.headers.get(HTMX_REQUEST_HEADER) == HTMX_REQUEST_VALUE
