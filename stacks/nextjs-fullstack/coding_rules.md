## Next.js App Router Coding Rules

### Server vs Client Components
- Components are Server Components BY DEFAULT — no directive needed
- Add `"use client"` ONLY when you need: useState, useEffect, event handlers, browser APIs, custom hooks
- `"use client"` declares a BOUNDARY — all imports become part of client bundle
- Keep `"use client"` as granular as possible — specific interactive components only
- Pass Server Components as `children` to Client Components to keep them server-rendered
- Props from Server to Client must be serializable (no functions, class instances)

### Data Fetching
- Fetch data in Server Components using async/await directly — NOT useEffect
- Use `Promise.all()` for parallel fetches
- Use `React.cache()` to deduplicate fetching across components
- Use `server-only` package to prevent server code from client import

### Server Actions & Mutations
- Use `"use server"` directive for mutation functions
- Client Components CANNOT define Server Functions — import from `"use server"` file
- Use `revalidatePath()` / `revalidateTag()` after mutations
- Call revalidate BEFORE redirect (redirect throws)
- Use `useActionState` hook for pending states in forms

### Route & File Conventions
- `page.tsx` — route UI (required)
- `layout.tsx` — shared wrapper (persists across navigations)
- `loading.tsx` — instant loading UI (auto Suspense)
- `error.tsx` — error boundary (must be `"use client"`)
- `not-found.tsx` — 404 UI
- `route.ts` — API route handler in `app/api/`
- `params` and `searchParams` are Promises in Next.js 15+ — must await

### TypeScript Strict Rules
- Strict mode, no `any`
- `import type` for type-only imports
- `satisfies` over `as`
- Immutable patterns — use spread, never mutate
- Functions under 50 lines, files under 800 lines
- Validate all input at boundaries using Zod

### Image & Navigation
- `next/image` for all images
- `next/link` for client-side navigation (prefetching)
- Use `router.push` only for programmatic navigation after mutations

### SEO & Metadata
- `generateMetadata` or static `metadata` export for per-page SEO
- `generateStaticParams` for static generation of dynamic routes

### Security
- Only `NEXT_PUBLIC_` env vars exposed to client
- Use `server-only` package for modules with secrets
- Validate ALL user input server-side
