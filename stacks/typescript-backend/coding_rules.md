## TypeScript Backend Coding Rules

### Type Safety (STRICT)
- Strict mode + `noUncheckedIndexedAccess` + `exactOptionalPropertyTypes`
- NEVER use `any`. Use `unknown` and narrow.
- `import type` for type-only imports. No `enum` — use `as const`.

### ESM & Runtime
- Node 22 LTS. ESM only (`"type": "module"`).
- Use `node:` prefix for builtins: `import { readFile } from 'node:fs/promises';`

### Environment Variables — Validate at startup
```typescript
import { z } from 'zod';
const EnvSchema = z.object({
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
  NODE_ENV: z.enum(['development', 'staging', 'production']).default('development'),
});
export const env = EnvSchema.parse(process.env);
```
NEVER hardcode secrets. NEVER access process.env directly in business logic.

### Request/Response Validation (Zod)
- Validate ALL incoming data at the boundary with `safeParse` (not `parse`).
- Standardized API response envelope:
```typescript
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: { message: string; code: string };
  meta?: { total: number; page: number; limit: number };
}
```

### Async/Await & Error Handling
- ALWAYS use async/await. Never mix with raw .then() chains.
- Every async route handler must catch errors (use wrapper):
```typescript
const asyncHandler = (fn: RequestHandler) => (req, res, next) =>
  Promise.resolve(fn(req, res, next)).catch(next);
```
- Global error handler MUST exist. Never expose stack traces in production.

### Repository Pattern
```typescript
interface UserRepository {
  findAll(filters?: UserFilters): Promise<User[]>;
  findById(id: string): Promise<User | null>;
  create(data: CreateUserDto): Promise<User>;
}
```
Business logic depends on the interface, not concrete implementation.

### Naming Conventions
- camelCase for variables, functions
- PascalCase for types, interfaces, classes
- SCREAMING_SNAKE_CASE for constants
- Files: kebab-case: `user-service.ts`, `auth.controller.ts`

### Security
- Parameterized queries only — never string concat SQL
- Rate limiting on all public endpoints
- Helmet middleware for HTTP security headers
- CORS configured explicitly (never `origin: '*'` in production)

### Code Quality
- Functions: max 100 lines, max 5 params, complexity <= 8
- Files: max 400 lines preferred, 800 hard limit
- No `console.log` — use structured logger (pino, winston)
- Absolute imports only (path aliases)
