## Backend Project Structure (Node.js + Express/Hono)

```
project-root/
├── src/
│   ├── app.ts                     # App setup, middleware
│   ├── server.ts                  # Server startup, graceful shutdown
│   ├── env.ts                     # Zod-validated environment config
│   ├── features/                  # Feature modules
│   │   ├── auth/
│   │   │   ├── auth.controller.ts
│   │   │   ├── auth.service.ts
│   │   │   ├── auth.repository.ts
│   │   │   ├── auth.schema.ts     # Zod schemas
│   │   │   ├── auth.routes.ts
│   │   │   └── auth.test.ts
│   │   └── users/
│   ├── middleware/
│   │   ├── error-handler.ts
│   │   ├── auth.ts
│   │   ├── rate-limiter.ts
│   │   └── validate.ts            # Generic Zod validation
│   ├── lib/
│   │   ├── db.ts
│   │   ├── logger.ts
│   │   └── errors.ts              # Custom error classes
│   └── types/
├── tests/integration/
├── migrations/
├── tsconfig.json
├── vitest.config.ts
├── Dockerfile
├── package.json
└── pnpm-lock.yaml
```

Organize by FEATURE, not by layer. Each feature is self-contained.
Dependencies flow inward: controller -> service -> repository.
