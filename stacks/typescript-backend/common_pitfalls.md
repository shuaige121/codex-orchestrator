## TypeScript Backend Common Pitfalls

### 1. Unvalidated environment variables
```typescript
// BAD: const port = process.env.PORT; // string | undefined
// GOOD: Zod-validated env schema that crashes at startup if invalid
```

### 2. Trusting request body without validation
```typescript
// BAD: const user = await db.user.create(req.body);
// GOOD: const result = CreateUserSchema.safeParse(req.body);
```

### 3. Async errors crashing the process
```typescript
// BAD: async handler without try/catch -> unhandled rejection -> crash
// GOOD: Wrap with asyncHandler that forwards to global error middleware
```

### 4. Exposing stack traces in production
```typescript
// BAD: res.json({ error: err.message, stack: err.stack });
// GOOD: Log full error server-side, return generic message to client
```

### 5. Hardcoded secrets in source code
```typescript
// BAD: const apiKey = 'sk-proj-abc123';
// GOOD: const apiKey = env.OPENAI_API_KEY; // validated at startup
```

### 6. Not closing database connections
```typescript
// Always use try/finally with client.release(), or use connection pool auto-management
```

### 7. SQL injection via string interpolation
```typescript
// BAD: db.query(`SELECT * FROM users WHERE id = '${req.params.id}'`);
// GOOD: db.query('SELECT * FROM users WHERE id = $1', [req.params.id]);
```

### 8. No graceful shutdown
```typescript
// Handle SIGTERM: close server, drain connections, close DB pool, exit
```

### 9. Blocking the event loop
```typescript
// BAD: readFileSync in route handler
// GOOD: Use streams or async I/O for large files
```

### 10. Missing rate limiting on public endpoints
```typescript
// Especially on /login, /register, /api endpoints
```

### 11. Using console.log instead of structured logging
```typescript
// BAD: console.log('User created: ' + user.id);
// GOOD: logger.info({ userId: user.id }, 'User created');
```
