## Python Common Pitfalls

### 1. Mutable Default Arguments
```python
# BAD:
def append_to(item, items=[]):
    items.append(item)
    return items
# append_to(1) -> [1], append_to(2) -> [1, 2] (not [2]!)

# GOOD:
def append_to(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

### 2. Late Binding Closures in Loops
```python
# BAD:
funcs = [lambda: i for i in range(5)]
[f() for f in funcs]  # -> [4, 4, 4, 4, 4]

# GOOD:
funcs = [lambda i=i: i for i in range(5)]
[f() for f in funcs]  # -> [0, 1, 2, 3, 4]
```

### 3. Comparing to None with == Instead of is
```python
# BAD: if value == None:
# GOOD: if value is None:
```

### 4. Bare except Clauses
```python
# BAD: except: pass
# Catches SystemExit, KeyboardInterrupt — hides real bugs.
# GOOD: except SpecificError as e: logger.error(...)
```

### 5. Forgetting to Await Coroutines
```python
# BAD: fetch_data()  # Returns coroutine, never executes!
# GOOD: await fetch_data()
```

### 6. Missing if __name__ == "__main__" Guard
```python
# Without it, module-level code runs on import, breaking tests.
```

### 7. Circular Imports
```python
# Fix: use TYPE_CHECKING for type-only imports
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mypackage.models import User
```

### 8. String Concatenation in Loops (O(n^2))
```python
# BAD: result += str(item)  # in loop
# GOOD: result = "".join(str(item) for item in items)
```

### 9. Shadowing Builtin Names
```python
# BAD: list = [1, 2, 3]  # list() constructor is broken!
# GOOD: user_list = [1, 2, 3]
```

### 10. N+1 Query Problem
```python
# BAD: for user in users: db.query(f"... WHERE user_id = {user.id}")
# GOOD: Use joinedload/prefetch_related or batch query with IN clause
```

### 11. SQL Injection via f-strings
```python
# BAD: cursor.execute(f"... WHERE name = '{user_input}'")
# GOOD: cursor.execute("... WHERE name = %s", (user_input,))
```

### 12. Not Using Context Managers
```python
# BAD: f = open("data.txt"); data = f.read(); f.close()
# GOOD: with open("data.txt") as f: data = f.read()
```

### 13. Large Intermediate Lists When Generator Suffices
```python
# BAD: sum([x * x for x in range(10_000_000)])  # 80MB+ in memory
# GOOD: sum(x * x for x in range(10_000_000))   # O(1) memory
```
