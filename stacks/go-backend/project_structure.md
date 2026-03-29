## Go Backend Project Structure

```
project/
├── cmd/
│   └── myapp/
│       └── main.go               # Entry point (minimal, wires deps)
├── internal/                      # Private code (not importable)
│   ├── handler/
│   │   ├── user_handler.go
│   │   └── health.go
│   ├── service/
│   │   └── user_service.go
│   ├── repository/
│   │   └── user_repo.go
│   ├── model/
│   │   ├── user.go
│   │   └── errors.go
│   ├── middleware/
│   │   └── auth.go
│   └── config/
│       └── config.go
├── pkg/                           # Public libraries
├── migrations/
├── testdata/                      # Test fixtures, golden files
├── go.mod
├── go.sum
├── .golangci.yml
├── Makefile
└── Dockerfile
```

Layer deps: handler -> service -> repository -> model
`internal/` enforces encapsulation at the Go toolchain level.
