## Verification Sequence — Django

```bash
# 1. Format
ruff format .

# 2. Lint
ruff check . --fix

# 3. Type check
uv run mypy .

# 4. Tests with coverage
uv run pytest --cov --cov-report=term-missing

# 5. Check migrations
uv run python manage.py makemigrations --check

# 6. Security audit (pre-deploy)
uv run python manage.py check --deploy
```
