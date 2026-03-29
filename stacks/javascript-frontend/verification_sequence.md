## Verification Sequence

### Step 1: Lint
```bash
npx eslint .
```
IMPORTANT: Check the project's `package.json` for the actual lint command (may be `npm run lint`).
If the project uses eslint.config.js (flat config), ESLint 9 is required.

### Step 2: Format check
```bash
npx prettier --check .
```
Skip if prettier is not configured in the project.

### Step 3: Build
```bash
npx vite build
```
Check `package.json` scripts — may be `npm run build` instead.
A successful build confirms no import errors or syntax issues.

### Step 4: Tests (if configured)
```bash
npx vitest run
```
Or `npm test` — check `package.json` for the actual test command.
Skip if no test configuration exists.

### Fallback Rule
ALWAYS check `package.json` "scripts" section FIRST. Use the project's own
`npm run lint`, `npm run build`, `npm test` commands. Only fall back to the
commands above if the project has no equivalent script.
