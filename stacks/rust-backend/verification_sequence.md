## Rust Verification Sequence

```bash
# 1. Format
cargo fmt

# 2. Lint (pedantic, treat warnings as errors)
cargo clippy --all-targets --all-features -- -D warnings

# 3. Test
cargo test

# 4. Build
cargo build

# 5. Supply chain audit
cargo deny check

# 6. (Optional) Safety check — UB detection
cargo careful test
```

### Quick pre-commit
```bash
cargo fmt && cargo clippy --all-targets --all-features -- -D warnings && cargo test
```
