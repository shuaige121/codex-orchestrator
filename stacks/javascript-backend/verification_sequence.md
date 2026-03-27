## JavaScript Backend Verification Sequence

```bash
# 1. Check project's own scripts FIRST
cat package.json | grep -A 20 '"scripts"'

# 2. Lint
npm run lint || npx eslint .

# 3. Format check
npx prettier --check . || echo "No prettier config — skip format check"

# 4. Tests (use project's test runner)
npm test

# 5. Start check (verify the app can boot)
timeout 10 node index.js || timeout 10 node src/index.js || echo "No standard entry point"
```

IMPORTANT: Always check `package.json` "scripts" section FIRST.
The project may use jest, mocha, tap, uvu, node:test, or other runners.
Use `npm test` — do NOT hardcode a specific test framework.
