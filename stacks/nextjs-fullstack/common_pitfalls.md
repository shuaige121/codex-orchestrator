## Next.js Common Pitfalls

### 1. Using hooks in Server Components
```typescript
// WRONG: export default function Page() { const [x, setX] = useState(0); }
// FIX: Add "use client" or move state to a child Client Component
```

### 2. Importing client-only libraries in Server Components
```typescript
// WRONG: import confetti from 'canvas-confetti'; // in Server Component
// FIX: Create a "use client" wrapper component
```

### 3. Not awaiting params in Next.js 15+
```typescript
// WRONG: function Page({ params }: { params: { id: string } })
// CORRECT:
export default async function Page({
  params,
}: { params: Promise<{ id: string }> }) {
  const { id } = await params;
}
```

### 4. searchParams is also a Promise in Next.js 15+
```typescript
// Must: const { q } = await searchParams;
```

### 5. Using `window` or `document` without guards
```typescript
// WRONG: const width = window.innerWidth; // crashes during SSR
// FIX: Use "use client" + useEffect to access browser APIs
```

### 6. Leaking secrets from Server to Client Components
```typescript
// WRONG: <ClientComponent apiKey={process.env.API_SECRET} />
// FIX: Only pass data, keep secrets on server. Use `server-only` package.
```

### 7. Not using Suspense boundaries for streaming
```typescript
// WRONG: Slow async component blocks entire page
// FIX: Wrap slow parts in <Suspense fallback={<Skeleton />}>
```

### 8. Sequential fetching when parallel is possible
```typescript
// WRONG: const a = await getA(); const b = await getB(); // serial
// FIX: const [a, b] = await Promise.all([getA(), getB()]); // parallel
```

### 9. Using router.push instead of <Link>
```typescript
// <Link> prefetches on viewport enter — better UX
// Use router.push only for programmatic navigation after mutations
```

### 10. Incorrect revalidation — redirect before revalidate
```typescript
// WRONG: redirect('/posts'); revalidatePath('/posts'); // never reached
// FIX: revalidatePath('/posts'); redirect('/posts'); // revalidate first
```

### 11. Non-serializable props to Client Components
```typescript
// Functions and class instances can't cross the server/client boundary
// Use Server Actions (serialized as reference) instead
```

### 12. Forgetting generateStaticParams for static dynamic routes
```typescript
// Without it, dynamic routes generate at runtime only
export async function generateStaticParams() {
  const posts = await getPosts();
  return posts.map((post) => ({ slug: post.slug }));
}
```
