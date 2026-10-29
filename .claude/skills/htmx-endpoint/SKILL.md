---
name: htmx-endpoint
description: Add an HTMX fragment endpoint or POST action that returns a partial template. Use for search-as-you-type, inline actions and partial page updates.
---

# Create an HTMX endpoint

Add an HTMX interaction to the page or feature the user names.

## Rules

- Detect HTMX with `corelib.http.is_htmx(request)`.
- A POST action answers HTMX with the fresh fragment and a plain form post with a redirect. See `LoanActionView` in `lending/infrastructure/views.py`.
- A fragment returned after an action renders its own messages. The full page already shows them in the layout, so pass a flag (`show_messages`) only from the action response.
- CSRF comes from `hx-headers` on `<body>` in `base.html`.
- Fragments live in `templates/{app}/partials/_name.html` and never extend a layout.

## Trigger

```html
<button class="btn btn-sm btn-outline-primary"
        hx-post="{% url 'lending:return_loan' loan_id=row.loan_id %}"
        hx-target="#loan-table">
  <i class="fas fa-fw fa-rotate-left"></i> {% translate "Return" %}
</button>
```

- `hx-trigger="input changed delay:300ms"` for search boxes.
- `fa-fw` on every Font Awesome icon.
- `js-` prefixed classes for JavaScript hooks, never styled.

## After creating

- Test with `HTTP_HX_REQUEST="true"` in the test client.
- `make format`
