---
name: new-view
description: Add a class-based view, its URL and template that call a use case through the DI container. Use for new pages.
---

# Create a view

Create a view with the name the user gives in the app's `infrastructure/views.py`.

## Rules

- Class-based views. `LoginRequiredMixin` for member pages.
- Views read the request, call a use case from the container, and render. No queries and no business rules in the view.
- Pass the clock in: `today=timezone.localdate()`.
- Query parameter names are module constants, passed to the template through the context.
- A page and its HTMX fragment share one mixin that builds the context, so both read the request the same way.
- Map domain errors to messages in one dict keyed by error class. Catch only those classes.
- Templates live in `infrastructure/templates/{app}/`, fragments in `partials/` with a leading underscore.

```python
class MyLoansMixin(LoginRequiredMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["my_loans"] = my_loans_report(request=self.request)
        return context


class MyLoansView(MyLoansMixin, TemplateView):
    template_name = "lending/my_loans.html"


class MyLoansTableView(MyLoansMixin, TemplateView):
    http_method_names = ["get"]
    template_name = "lending/partials/_loan_table.html"
```

## URL

```python
path("table/", MyLoansTableView.as_view(), name="my_loans_table"),
```

## After creating

- Add tests in `infrastructure/tests/test_views.py`.
- `make format`
