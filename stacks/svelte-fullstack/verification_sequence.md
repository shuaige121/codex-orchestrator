## Verification Sequence — SvelteKit

```bash
# 1. Format
npx prettier --write .

# 2. Lint
npx eslint .

# 3. Svelte + TypeScript check
npx svelte-check

# 4. Unit tests
npx vitest run

# 5. Build
npx vite build

# 6. E2E tests (if configured)
npx playwright test
```

IMPORTANT: Check package.json for project's actual scripts.
Use `npm run check`, `npm run lint` etc. as primary.
