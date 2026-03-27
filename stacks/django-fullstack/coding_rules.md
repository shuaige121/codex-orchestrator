## Django Fullstack Coding Rules

### Models
- Inherit from a `TimeStampedModel` base providing `created_at`/`updated_at`.
- Define `__str__()` on every model.
- Use `TextChoices`/`IntegerChoices` for choice fields, never tuples of tuples.
- Set explicit `db_table`, add `indexes` for filtered/ordered fields. Define `ordering`.
- Use model-level `constraints` and `validators`. Data integrity belongs in the model.
- Use `settings.AUTH_USER_MODEL` string reference, never import User directly.

### Views & Serializers
- Use `ModelViewSet`/`ReadOnlyModelViewSet` for CRUD. Always define `queryset`, `serializer_class`, `permission_classes`.
- Override `get_queryset()` for row-level filtering (e.g., scope to current user). Never filter in individual actions.
- Never use `fields = "__all__"` in serializer Meta. Always list fields explicitly.
- Use separate read/write serializers when shapes differ.
- Use `validate_<field>()` for field-level, `validate()` for cross-field validation.
- Controllers (views) must be thin — delegate business logic to service layer.

### Queries & Performance
- Mandatory `select_related()` for ForeignKey/OneToOneField accessed in response.
- Mandatory `prefetch_related()` for reverse FK and M2M.
- Never call `.all()` without filtering or pagination in list endpoints.
- Write queries in Managers/QuerySets, not views. Create custom QuerySet methods.
- Use `bulk_create()`/`bulk_update()` for batch ops. Use `F()` and `Q()` objects.

### Project Structure
- Split settings: `base.py`, `local.py`, `production.py`. Never a single `settings.py`.
- Apps in `apps/` directory. Business logic in `services/`, data access in `repositories/`.
- One migration per logical change. Never edit migration files by hand.

### Type Hints
- All function signatures must have complete type annotations.
- Modern syntax: `list[str]` not `List[str]`, `str | None` not `Optional[str]`.
- Let `django-stubs` handle model field types.

### Security
- Never disable CSRF middleware. Use token auth for APIs.
- Never use `mark_safe()` or `|safe` on user-supplied data.
- Never use raw SQL; if necessary, always use parameterized queries.
- Production: `DEBUG=False`, `SECURE_SSL_REDIRECT=True`, `SESSION_COOKIE_SECURE=True`.

### Testing
- Use pytest + pytest-django, never `unittest.TestCase`. Use `assert`, not `self.assertEqual()`.
- Use `factory_boy` for test data. Never `Model.objects.create()` directly in tests.
- Fixtures in `conftest.py`. Use `@pytest.fixture` and `@pytest.mark.django_db`.
- Test both success and failure paths. Minimum 80% coverage on business logic.
