## Verification Sequence

```bash
# 1. Next.js specific lint rules
npx next lint

# 2. Format
npx prettier --write .

# 3. TypeScript strict type check
npx tsc --noEmit

# 4. Unit tests
npx vitest run

# 5. CRITICAL: Full production build
npx next build
# Catches: invalid page exports, broken dynamic routes, SSR errors,
# serialization issues, missing "use client", server/client boundary violations
```

`next build` is the most important check — it catches issues tsc alone misses.
