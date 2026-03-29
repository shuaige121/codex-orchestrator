1. `npx wrangler deploy --dry-run --outdir=dist` — build must succeed
2. `npx eslint src/` — zero errors
3. Check `wrangler.toml` has valid `name`, `main`, `compatibility_date`
4. Check no Node.js imports (`require()`, `import fs`, `import path`)
5. Check all D1 queries use parameterized `?` (no string concatenation for SQL)
6. Check `export default { fetch }` exists in entry file
