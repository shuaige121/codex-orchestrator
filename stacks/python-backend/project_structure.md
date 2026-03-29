## Python Backend Project Structure (src layout with uv)

```
project-name/
├── src/
│   └── project_name/           # Package (snake_case)
│       ├── __init__.py
│       ├── main.py             # Entry point / CLI
│       ├── config.py           # Settings via pydantic-settings
│       ├── api/                # HTTP layer (FastAPI routers)
│       │   ├── __init__.py
│       │   ├── routes.py
│       │   ├── deps.py         # Dependency injection
│       │   └── middleware.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── user.py         # SQLAlchemy/Pydantic models
│       │   └── schemas.py      # Request/response schemas
│       ├── services/           # Business logic
│       │   ├── __init__.py
│       │   └── user_service.py
│       ├── repositories/       # Data access (Repository pattern)
│       │   ├── __init__.py
│       │   └── user_repo.py
│       └── utils/
│           ├── __init__.py
│           └── helpers.py
├── tests/
│   ├── conftest.py             # Shared fixtures
│   ├── unit/
│   └── integration/
├── pyproject.toml              # Single config for project + all tools
├── uv.lock
└── .python-version
```

### Key Principles
- src/ layout prevents accidental imports from project root
- pyproject.toml is the single config file (ruff, pyright, pytest)
- Repository pattern separates data access from business logic
- Dependency injection via FastAPI Depends() for testability
