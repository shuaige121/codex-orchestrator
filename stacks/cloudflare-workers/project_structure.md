```
├── src/
│   └── index.js              # Worker entry (export default { fetch })
├── schema.sql                # D1 migration
├── wrangler.toml             # Cloudflare config (bindings, routes, vars)
├── .dev.vars                 # Local secrets (gitignored)
├── package.json
└── .gitignore
```

Key wrangler.toml fields:
- `name` = worker name
- `main` = entry file path
- `compatibility_date` = API version date
- `[[d1_databases]]` = D1 binding (binding, database_name, database_id)
- `[vars]` = non-secret env vars
- `routes` = custom domain routing
