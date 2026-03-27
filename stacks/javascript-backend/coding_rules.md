## JavaScript Backend (Node.js) Coding Rules

### Core Principles
- Prefer `const` over `let`. NEVER use `var`.
- Use strict mode (`"use strict"` or ESM `"type": "module"`).
- ALL async functions MUST have proper error handling (try/catch or .catch()).
- Never swallow errors — always log or propagate.

### Module System
- Prefer ESM (`import/export`) over CommonJS (`require/module.exports`) for new projects.
- For existing CommonJS projects, stay consistent — don't mix module systems.
- Use `node:` prefix for built-in modules: `import { readFile } from 'node:fs/promises'`.

### Error Handling
- Create custom error classes extending `Error` with meaningful names.
- Use error codes, not string matching: `if (err.code === 'ENOENT')`.
- Always handle promise rejections — unhandled rejections crash Node 16+.
- In Express/Fastify: use centralized error middleware, not try/catch in every handler.

### API Design
- Validate all input at the boundary (use Joi, Zod, or Ajv).
- Return consistent error shapes: `{ error: { code, message, details } }`.
- Use proper HTTP status codes (don't return 200 for errors).
- Set appropriate timeouts on HTTP clients and database connections.

### Testing
- Check `package.json` "scripts.test" for the actual test runner (may be jest, mocha, tap, uvu, node --test, vitest, or ava).
- Use the project's own `npm test` — do NOT assume vitest or jest.
- Structure tests as: arrange, act, assert.
- Mock external services (database, HTTP), not internal modules.

### Performance
- Use `node:stream` for large data processing.
- Never block the event loop — use `setImmediate()` for CPU-heavy work or worker_threads.
- Use connection pooling for databases.
- Set `keepAlive: true` on HTTP agents.

### Security
- NEVER use `eval()`, `new Function()`, or `child_process.exec()` with user input.
- Use parameterized queries for SQL (never string concatenation).
- Sanitize all user-facing output.
- Use `helmet` middleware for HTTP headers.
- Store secrets in environment variables, not code.
