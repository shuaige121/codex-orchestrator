## Verification Sequence — Vue.js

```bash
# 1. Type check (Vite does NOT type-check during build)
npx vue-tsc --build

# 2. Format check
npx prettier --check "src/**/*.{vue,ts,tsx,css}"

# 3. Lint
npx eslint .

# 4. Unit tests
npx vitest run

# 5. Build
npx vite build
```

IMPORTANT: Check package.json scripts first. Use `npm run lint`,
`npm run type-check`, `npm run build` etc. if they exist.
