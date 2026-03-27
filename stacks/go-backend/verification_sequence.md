## Go Verification Sequence

```bash
# 1. Tidy modules
go mod tidy

# 2. Format
gofmt -w .

# 3. Vet
go vet ./...

# 4. Lint
golangci-lint run ./...

# 5. Security scan
if command -v gosec >/dev/null; then gosec ./...; else echo "WARNING: gosec not found, skipping"; fi

# 6. Test with race detector
go test -race ./...

# 7. Build
go build ./...

# 8. (Optional) Vulnerability scan
if command -v govulncheck >/dev/null; then govulncheck ./...; else echo "WARNING: govulncheck not found, skipping"; fi
```

### Quick pre-commit
```bash
gofmt -w . && go vet ./... && go test -race ./...
```
