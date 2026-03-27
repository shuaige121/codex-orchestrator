## Verification Sequence — React Native Expo

```bash
# 1. Type check
npx tsc --noEmit

# 2. Lint
npx expo lint

# 3. Format check
npx prettier --check "**/*.{ts,tsx}"

# 4. Unit tests
npx jest --ci
```

IMPORTANT: Check package.json scripts for the project's actual commands.
Use `npm run lint`, `npm test` etc. as primary if they exist.
