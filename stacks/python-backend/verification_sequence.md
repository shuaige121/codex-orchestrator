## Verification Sequence — Run after EVERY code change

### Step 1: Lint + Auto-fix
```bash
ruff check --fix .
```
Runs 900+ lint rules. If it fails: read the error codes, fix manually what --fix can't auto-fix.
(ruff is pre-installed via `uv tool install ruff` during setup.)

### Step 2: Format
```bash
ruff format .
```
If it changes files, that's expected — re-stage before committing.

### Step 3: Type Check
```bash
pyright .
```
If it fails: add type annotations, fix type mismatches.
Never use `# type: ignore` without a specific error code and justification.

### Step 4: Test
```bash
uv run pytest -xvs
```
-x = stop on first failure. If it fails: fix the failing test. Do NOT skip or delete tests.
For coverage: `uv run pytest --cov=src --cov-report=term-missing` (target 80%+).

### Quick Pre-commit
```bash
ruff check --fix . && ruff format . && uv run pytest -x
```
