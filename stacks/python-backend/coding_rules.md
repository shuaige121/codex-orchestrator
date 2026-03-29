## Python Backend Coding Rules

### Import Ordering (enforced by ruff I rules)
1. `from __future__ import annotations`
2. Standard library
3. Third-party packages
4. Local/project imports
Each group separated by a blank line. Absolute imports only.

### Naming Conventions
- snake_case: functions, methods, variables, modules, packages
- PascalCase: classes, type aliases, Protocols, exceptions
- UPPER_SNAKE_CASE: module-level constants
- _leading_underscore: internal/private
- Never shadow builtins (list, dict, str, id, type, input, hash, map, filter)

### Type Hints — Required on ALL public functions
Use modern syntax (Python 3.10+):
- `list[str]` not `List[str]`
- `dict[str, int]` not `Dict[str, int]`
- `str | None` not `Optional[str]`
- Annotate return types including `-> None`
- Use Protocol for structural typing (duck typing)

### Error Handling
- No bare except — always catch specific exceptions
- Chain exceptions: `raise ValueError("msg") from original_error`
- Use `contextlib.suppress(KeyError)` instead of try/except/pass
- Custom exception hierarchy: AppError -> ValidationError, NotFoundError, etc.
- Context managers (with statement) for resource management

### String Formatting
- f-strings only. No .format(), no %, no string concatenation in loops.
- Use `"".join(iterable)` for building strings from sequences.

### Data Structures
- dataclass or Pydantic BaseModel over raw dicts
- `@dataclass(frozen=True)` for immutable value objects
- NamedTuple over plain tuples when fields have meaning
- Enum over magic strings/numbers
- Use `__slots__` on hot-path classes

### File & Path Operations
- `pathlib.Path` over `os.path` everywhere.

### Async Rules
- Never call blocking I/O from async functions (use aiohttp, aiofiles, asyncpg)
- Always await coroutines — forgetting to await is a silent bug
- Use `asyncio.gather()` for concurrent I/O, not sequential awaits
- Don't mix sync and async — use `run_in_executor` for sync code in async

### Code Quality Hard Limits
- Max 100 lines per function, cyclomatic complexity <= 8
- Max 5 positional parameters (use dataclass for more)
- No commented-out code — delete it
- No `print()` in production — use logging module
- No `from module import *`

### Dependency Management
- Use `uv` as package manager (not pip/poetry)
- Pin exact versions in production
- Run `pip-audit` before deploying
- Justify every new dependency
