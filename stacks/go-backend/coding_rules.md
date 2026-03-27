## Go Backend Coding Rules

### Core Principles
- **Simplicity over cleverness.** Code should be obvious and easy to read.
- **Accept interfaces, return structs.**
- **Make the zero value useful.** Design types so zero value works without init.
- **A little copying is better than a little dependency.**

### Error Handling
- Always check errors. Never `_` to discard errors unless explicitly justified.
- Wrap with context: `fmt.Errorf("operation: %w", err)`
- Use `errors.Is()` and `errors.As()` — never `==` on errors
- No `panic` in library code
- Define sentinel errors: `var ErrNotFound = errors.New("not found")`

### Context Usage
- `context.Context` as first parameter in all API/service functions
- Always `context.WithTimeout` for operations that could block
- Never store Context in a struct

### Naming Conventions
- Short names in small scope, descriptive in large scope
- No getters: `Name()` not `GetName()`
- Packages: short, lowercase, no underscores
- Interfaces: method + `er` suffix (`Reader`, `Writer`)
- Acronyms all-caps: `userID`, `httpClient`

### Interface Design
- Keep interfaces small: 1-3 methods
- Define interfaces where they are USED, not where implemented
- Compose larger interfaces from smaller ones

### Functional Options Pattern
```go
type Option func(*Server)
func WithTimeout(d time.Duration) Option { return func(s *Server) { s.timeout = d } }
func NewServer(addr string, opts ...Option) *Server { ... }
```

### Concurrency
- Share memory by communicating (channels), not by locking
- `sync.WaitGroup` for coordination, `errgroup.Group` for errors
- Buffered channels + `select` with `ctx.Done()` to prevent goroutine leaks
- `defer mu.Unlock()` immediately after `mu.Lock()`

### Code Quality
- Functions: max 50 lines, max 4 nesting levels
- No mutable package-level variables — use DI
- Preallocate slices: `make([]T, 0, len(items))`
- `strings.Builder` for string concat in loops

### Security
- Never hardcode secrets — `os.Getenv()` with validation
- `gosec ./...` for security analysis
- Parameterized SQL queries only
