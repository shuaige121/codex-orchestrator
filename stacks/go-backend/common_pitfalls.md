## Go Common Pitfalls

### 1. Goroutine Leaks
```go
// BAD: ch := make(chan []byte); go func() { ch <- data }()  // blocks forever
// FIX: Buffered channel + select with ctx.Done()
```

### 2. Not Closing HTTP Response Bodies
```go
// BAD: resp, _ := http.Get(url); body, _ := io.ReadAll(resp.Body)  // leak
// FIX: defer resp.Body.Close() immediately after error check
```

### 3. Nil Interface vs Nil Pointer
```go
// An interface holding a nil pointer is NOT nil
// FIX: Return untyped nil from functions, not typed nil pointer
```

### 4. Range Variable Capture in Goroutine (Go <1.22)
```go
// BAD: for _, url := range urls { go func() { fetch(url) }() }  // all same url
// FIX: url := url  // shadow with local copy (fixed in Go 1.22+)
```

### 5. Ignoring Errors
```go
// BAD: result, _ := doSomething()
// GOOD: result, err := doSomething(); if err != nil { return fmt.Errorf(...) }
```

### 6. Nil Map Panic
```go
// BAD: var m map[string]int; m["key"] = 1  // PANIC
// FIX: m := make(map[string]int)
```

### 7. Slice Append Gotcha (Shared Backing Array)
```go
// BAD: slice1 := base[:3]; append(slice1, 99)  // mutates base!
// FIX: slice1 := base[:3:3]  // full slice expression limits capacity
```

### 8. Context Not Propagated
```go
// BAD: ctx := context.Background()  // ignores request context
// FIX: ctx := r.Context()  // carries deadlines and cancellation
```

### 9. Data Race on Shared State
```go
// BAD: concurrent map access without sync
// FIX: Use sync.Map or protect with Mutex
```

### 10. Deferred Function Argument Evaluation
```go
// BAD: defer fmt.Printf("took %v", time.Since(start))  // evaluated NOW
// FIX: defer func() { fmt.Printf("took %v", time.Since(start)) }()
```

### 11. Using panic for Control Flow
```go
// BAD: panic(err)  // not an exception mechanism
// FIX: return nil, fmt.Errorf("get user %s: %w", id, err)
```

### 12. Mixing Value and Pointer Receivers
```go
// Pick one style and be consistent for all methods on a type
```

### 13. Not Deferring Mutex Unlock
```go
// BAD: mu.Lock(); if cond { mu.Unlock(); return }; mu.Unlock()
// GOOD: mu.Lock(); defer mu.Unlock()
```
