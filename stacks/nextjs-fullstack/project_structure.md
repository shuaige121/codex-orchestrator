## Next.js Fullstack Project Structure

```
app/
├── (marketing)/              # Route group — public pages
│   ├── page.tsx
│   └── layout.tsx
├── (app)/                    # Route group — authenticated
│   ├── dashboard/
│   │   ├── page.tsx
│   │   ├── loading.tsx
│   │   └── error.tsx
│   └── layout.tsx            # App layout (auth check, sidebar)
├── api/
│   └── webhooks/route.ts
├── layout.tsx                # Root layout
├── globals.css
├── not-found.tsx
└── loading.tsx
actions/
├── auth.ts                   # Server Actions
└── posts.ts
components/
├── ui/                       # Shared primitives
└── features/                 # Feature-specific components
lib/
├── db.ts
├── auth.ts
├── utils.ts
└── validations.ts            # Shared Zod schemas
types/
└── index.ts
middleware.ts                 # Auth middleware, redirects
next.config.ts
tailwind.config.ts
```
