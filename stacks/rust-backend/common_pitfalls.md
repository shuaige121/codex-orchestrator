## Rust Common Pitfalls

### 1. Use After Move
```rust
let name = String::from("Alice");
let greeting = consume(name);  // name is moved here
// println!("{name}");  // ERROR: value used after move
// FIX: Pass &name (borrow), or name.clone() if ownership transfer is needed
```

### 2. Lifetime Issues in Closures
```rust
// BAD: fn make_greeting(name: &str) -> impl Fn() -> String
// FIX: Take String ownership: fn make_greeting(name: String) -> impl Fn() -> String
```

### 3. Deadlock with Mutex
```rust
// BAD: let lock1 = data.lock(); let lock2 = data.lock(); // DEADLOCK
// FIX: Drop first lock before acquiring second (use scoping blocks)
```

### 4. .clone() Overuse
```rust
// BAD: fn process(items: Vec<String>) { for item in items.clone() { ... } }
// FIX: fn process(items: &[String]) { for item in items { ... } }
```

### 5. String vs &str Confusion
```rust
// BAD: fn greet(name: String)  — forces caller to allocate
// FIX: fn greet(name: &str)    — accepts both &String and &str
```

### 6. Wildcard Match Hides New Variants
```rust
// BAD: _ => {}  // silently ignores new variants
// FIX: Explicit match — compiler warns when new variant added
```

### 7. Blocking in Async Context
```rust
// BAD: std::fs::read_to_string(path)?  // blocks executor thread
// FIX: tokio::fs::read_to_string(path).await?
```

### 8. Unbounded Channels
```rust
// BAD: unbounded_channel() — can OOM
// FIX: channel(1024) — bounded with backpressure
```

### 9. Rc Not Send (can't use across threads)
```rust
// BAD: Rc<T> in tokio::spawn — ERROR: not Send
// FIX: Use Arc<T> for shared ownership across threads
```

### 10. Forgetting await on Futures
```rust
// BAD: fetch_data();   // returns Future, nothing happens
// FIX: fetch_data().await;
```

### 11. Panic in Production Code
```rust
// BAD: CONFIG.get(key).unwrap()
// FIX: CONFIG.get(key).ok_or(ConfigError::MissingKey(...))?
```

### 12. Mutating Collection While Iterating
```rust
// Borrow checker prevents this — collect first, then mutate
```
