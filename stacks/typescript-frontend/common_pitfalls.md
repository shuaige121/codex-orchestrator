## TypeScript Frontend Common Pitfalls

### 1. Using `any` to silence type errors
```typescript
// BAD: const data: any = await fetchUser(); data.nmae; // typo not caught!
// GOOD: const data: unknown = ...; const user = UserSchema.parse(data);
```

### 2. Mutating state directly in React
```typescript
// BAD: items.push('c'); setItems(items); // same reference, no re-render
// GOOD: setItems(prev => [...prev, 'c']);
```

### 3. Missing dependency array in useEffect
```typescript
// BAD: useEffect(() => { fetchData(userId); }); // runs every render
// GOOD: useEffect(() => { fetchData(userId); }, [userId]);
```

### 4. Using `as` to lie to the compiler
```typescript
// BAD: const input = document.getElementById('email') as HTMLInputElement;
// GOOD: if (input instanceof HTMLInputElement) { input.value; }
```

### 5. Unhandled promise rejections
```typescript
// All async handlers need try/catch with user-friendly error messages
```

### 6. Enum pitfalls (numeric enums allow invalid values)
```typescript
// BAD: enum Direction { Up, Down } — allows Direction = 99
// GOOD: const Direction = { Up: 'up', Down: 'down' } as const;
```

### 7. Object index access without checking
```typescript
// Enable noUncheckedIndexedAccess in tsconfig
// Or use Map: map.get('b') typed as string | undefined automatically
```

### 8. Stale closures in intervals
```typescript
// BAD: setInterval(() => { setCount(count + 1); }, 1000); // stale count
// GOOD: setInterval(() => { setCount(prev => prev + 1); }, 1000);
```

### 9. Barrel file circular dependencies
```typescript
// BAD: export * from './auth'; // creates circular deps
// GOOD: import directly from specific modules
```

### 10. Not validating API responses
```typescript
// BAD: const users: User[] = await res.json(); // blindly trust server
// GOOD: const users = z.array(UserSchema).parse(await res.json());
```

### 11. Memory leaks from uncleared subscriptions
```typescript
// Always return cleanup function from useEffect for WebSocket, event listeners
```

### 12. Spreading props defeats type checking
```typescript
// BAD: function UserCard(props: any) { return <div {...props} /> }
// GOOD: Explicitly typed props interface with destructuring
```
