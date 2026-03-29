## SvelteKit Fullstack Coding Rules

### Svelte 5 Runes (Reactivity)
- `$state` for reactive variables. Prefer not to use bare `let` for reactive state in new Svelte 5 code.
- `$derived` for computed values. Prefer not to use `$:` reactive declarations in new code; keep them only for legacy compatibility.
- `$effect` for side effects. Prefer not to use `$:` with side effects in new code. Return cleanup function if needed.
- `$props()` for component props. Prefer not to use `export let` except in legacy Svelte 4 compatibility paths.
- `$bindable()` only when two-way binding is explicitly needed.
- Snippets `{@render children?.()}` instead of slots `<slot />`.
- Prefer property event handlers `onclick={handler}`; keep `on:click={handler}` only when maintaining legacy components.

### Data Loading
- Always return data from load functions; never set global state in them.
- `+page.server.ts` for sensitive data (cookies, DB, private env).
- `+page.ts` for shared logic (runs on both server and client).
- Use SvelteKit's enhanced `fetch` from load params, not global `fetch`.

### Form Actions
- Define actions in `+page.server.ts`. Use `fail()` for validation errors.
- Always add `use:enhance` to forms for progressive enhancement.

### Server-Side & Security
- Server-only code in `$lib/server/` or `.server.ts` files. SvelteKit errors at build if imported client-side.
- `$env/static/private` for secrets, `$env/static/public` (PUBLIC_ prefix) for public values.
- Use `hooks.server.ts` for cross-cutting concerns (auth, logging). Use `sequence()`.
- `event.locals` for per-request state. Never module-level variables for user data.

### State Management
- Never use global/module-level state for user-specific data on server (shared across ALL users!).
- Export reactive state via classes or getter/setter, not bare `$state` exports.
- Use `$derived` in components for values computed from props (not one-time assignment).
- Use Svelte context API (`setContext`/`getContext`) for component tree state.

### TypeScript
- Always `lang="ts"` in script tags.
- Type load functions via `./$types` module (`PageLoad`, `PageData`).
- Customize error shape via `App.Error` in `src/app.d.ts`.

### Code Quality
- Components: PascalCase filenames (`Button.svelte`).
- Functional, declarative style. Minimal `$effect` — prefer `$derived` when possible.
- CSS in `<style>` blocks (scoped by default) or Tailwind utility classes.
- `+page.svelte` files should be concise — extract logic to `$lib` components.
