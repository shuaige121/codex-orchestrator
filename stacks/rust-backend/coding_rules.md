## Rust Backend Coding Rules

### Ownership & Borrowing
- Prefer borrowing (`&T`, `&mut T`) over taking ownership unless function stores the value
- Prefer `&str` over `String` in function parameters
- Minimize `.clone()` — every clone should be justified
- Use `Cow<'_, str>` when function may or may not need to allocate

### Error Handling
- `thiserror` for library/domain errors, `anyhow` for application-level errors
- Propagate with `?` operator — never manual match just to re-wrap
- **No `.unwrap()` in production code.** Use `.expect("reason")` only in tests.
- Define domain error enums per module with `From` conversions
- Map domain errors to HTTP responses via Axum's `IntoResponse`

### Type Design
- Newtypes over primitives: `UserId(u64)` not bare `u64`
- Enums for state machines, not boolean flags
- Derive `Debug, Clone, PartialEq` by default
- `#[must_use]` on functions with important return values
- `impl Trait` for return types when concrete type is implementation detail

### Linting (Cargo.toml)
```toml
[lints.clippy]
pedantic = { level = "warn", priority = -1 }
unwrap_used = "deny"
panic = "deny"
panic_in_result_fn = "deny"
dbg_macro = "deny"
todo = "deny"
print_stdout = "deny"
print_stderr = "deny"
await_holding_lock = "deny"
```

### Naming Conventions
- `snake_case` functions/variables/modules
- `PascalCase` types/traits/enums
- `SCREAMING_SNAKE_CASE` constants/statics

### Async & Concurrency
- `tokio` as async runtime
- `Arc<Mutex<T>>` sparingly — prefer message passing with `tokio::sync::mpsc`
- `sqlx::query!` / `query_as!` for compile-time SQL verification
- All queries use parameterized placeholders, never string formatting

### Dependencies
- `cargo deny check` for advisories, licenses, bans
- Justify every new dependency
