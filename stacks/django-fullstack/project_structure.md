## Django Project Structure

```
project-root/
├── pyproject.toml
├── manage.py
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   └── <app_name>/
│       ├── models.py
│       ├── views.py / viewsets.py
│       ├── urls.py
│       ├── serializers.py
│       ├── admin.py
│       ├── services/
│       ├── repositories/
│       └── tests/
│           ├── conftest.py
│           ├── test_models.py
│           └── test_views.py
├── common/
│   ├── models.py         # TimeStampedModel base
│   └── permissions.py
├── templates/
├── static/
└── tests/
    └── conftest.py
```

Business logic in `services/`, data access in `repositories/`.
Split settings into base/local/production.
