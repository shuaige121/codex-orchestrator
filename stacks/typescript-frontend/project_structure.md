## Frontend Project Structure (React + Vite)

```
project-root/
├── src/
│   ├── app/                       # App shell, providers, router
│   │   ├── App.tsx
│   │   ├── providers.tsx
│   │   └── router.tsx
│   ├── components/                # Shared UI components
│   │   └── Button/
│   │       ├── Button.tsx
│   │       ├── Button.test.tsx    # Co-located test
│   │       └── index.ts
│   ├── features/                  # Feature modules (domain-organized)
│   │   ├── auth/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── api.ts
│   │   │   └── types.ts
│   │   └── dashboard/
│   ├── hooks/                     # Shared custom hooks
│   ├── lib/                       # Utilities, constants, schemas
│   │   ├── api-client.ts
│   │   └── schemas.ts             # Shared Zod schemas
│   ├── types/
│   └── main.tsx
├── e2e/                           # Playwright E2E tests
├── vite.config.ts
├── tsconfig.json                  # strict: true
├── vitest.config.ts
├── package.json                   # "type": "module"
└── pnpm-lock.yaml
```

Organize by FEATURE/DOMAIN, not by file type.
Co-locate tests, styles, and types with their component.
