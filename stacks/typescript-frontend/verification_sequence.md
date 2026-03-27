## Verification Sequence

```bash
# 1. Lint
npx eslint .

# 2. Format check
npx prettier --check .

# 3. Type check — zero errors
npx tsc --noEmit

# 4. Unit + integration tests
npx vitest run

# 5. Build — ensures no build-time errors
npx vite build

# 6. E2E tests (if configured)
npx playwright test
```

IMPORTANT: Check package.json scripts FIRST (`npm run lint`, `npm run build` etc.).
Use the project's own commands as primary. Profile commands are fallbacks.
