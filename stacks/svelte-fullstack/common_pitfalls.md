## SvelteKit Common Pitfalls

### 1. Browser APIs during SSR
```typescript
// BAD: window.innerWidth crashes on server
// GOOD: defer to onMount or $effect
import { onMount } from 'svelte';
let width = $state(0);
onMount(() => { width = window.innerWidth; });
```

### 2. Hydration mismatch
```svelte
<!-- BAD: different on server vs client -->
<p>{Date.now()}</p>
<!-- GOOD: pass from server load or defer to client -->
```

### 3. $effect where $derived suffices
// $effect is for side effects. $derived is for computed values.
// Using $effect to set state creates unnecessary re-render cycles.

### 4. Returning too much data from server load
```typescript
// BAD: return entire DB record
// GOOD: pick only needed fields
```

### 5. Dynamic Tailwind classes
```svelte
<!-- BAD: purged by scanner -->
<div class="bg-{color}-500">
<!-- GOOD: complete class names -->
<div class={color === 'blue' ? 'bg-blue-500' : 'bg-red-500'}>
```

### 6. $effect doesn't track async reads
```typescript
$effect(() => {
  setTimeout(() => { console.log(count); }, 1000); // NOT tracked
});
```

### 7. Mutating objects without $state in classes
```typescript
// BAD: mutations won't trigger reactivity
class Store { items: string[] = []; }
// GOOD:
class Store { items = $state<string[]>([]); }
```

### 8. Vite plugin order with Tailwind
// Tailwind Vite plugin MUST come BEFORE SvelteKit plugin in vite.config.ts

### 9. CSS imports in app.html instead of +layout.svelte
// CSS belongs in +layout.svelte for proper cascading

### 10. Using on:click directive (Svelte 4) instead of onclick property
// WRONG: on:click={handler}  CORRECT: onclick={handler}

### 11. Module-level state shared across users on server
```typescript
// BAD: let user = $state(null); // shared across ALL requests!
// GOOD: use context API or return from load function
```

### 12. Touch events passive by default in Svelte 5
// ontouchstart/ontouchmove are passive — preventDefault() won't work.
// Use Svelte actions for non-passive touch handlers.
