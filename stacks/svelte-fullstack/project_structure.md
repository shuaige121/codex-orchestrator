## SvelteKit Project Structure

```
project-root/
├── src/
│   ├── routes/
│   │   ├── +page.svelte          # Home page
│   │   ├── +page.server.ts       # Server load/actions
│   │   ├── +layout.svelte        # Root layout
│   │   ├── +error.svelte         # Error page
│   │   ├── api/
│   │   │   └── [resource]/
│   │   │       └── +server.ts    # REST endpoints
│   │   └── [feature]/
│   │       ├── +page.svelte
│   │       └── +page.server.ts
│   ├── lib/
│   │   ├── components/           # PascalCase.svelte
│   │   ├── server/               # Server-only ($lib/server)
│   │   │   ├── db.ts
│   │   │   └── auth.ts
│   │   ├── utils/
│   │   ├── types/
│   │   └── state/                # .svelte.ts reactive modules
│   ├── params/                   # Route param matchers
│   ├── app.html
│   ├── app.d.ts                  # App-level types
│   ├── hooks.server.ts           # Server hooks
│   └── hooks.client.ts
├── static/
├── tests/                        # Playwright E2E
├── svelte.config.js
├── vite.config.ts
├── tsconfig.json
├── eslint.config.js
└── .prettierrc
```

Route files: `+page.svelte`, `+page.server.ts`, `+layout.svelte`.
Server-only: `$lib/server/` or `.server.ts` extension.
Reactive modules: `.svelte.ts` extension.
