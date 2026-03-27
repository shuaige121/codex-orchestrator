## Rust Backend Project Structure

```
project/
├── src/
│   ├── main.rs                 # Entry point, server setup
│   ├── lib.rs                  # Library root, re-exports
│   ├── config.rs               # Configuration loading
│   ├── error.rs                # Domain error types (thiserror)
│   ├── handlers/               # HTTP handlers (Axum routes)
│   │   ├── mod.rs
│   │   ├── users.rs
│   │   └── health.rs
│   ├── models/                 # Data models, DTOs
│   │   └── mod.rs
│   ├── services/               # Business logic
│   │   └── mod.rs
│   ├── repositories/           # Data access (SQLx)
│   │   └── mod.rs
│   └── middleware/             # Tower middleware
│       └── mod.rs
├── tests/                      # Integration tests
├── migrations/                 # SQL migrations
├── Cargo.toml
├── Cargo.lock
├── deny.toml                   # cargo-deny config
└── Dockerfile
```

Layer dependencies: handlers -> services -> repositories -> models/error
