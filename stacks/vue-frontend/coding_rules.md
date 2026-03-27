## Vue.js Frontend Coding Rules

### SFC Conventions
- Always use `<script setup lang="ts">`. Avoid Options API in new code.
- Block order: `<script>`, `<template>`, `<style>`. Enforce via `vue/block-order`.
- One component per file. Multi-word component names (no `Profile`, use `UserProfile`).
- PascalCase in SFC templates (`<UserProfile />`), kebab-case in DOM templates.
- Self-close components without content: `<MyComponent />`.

### Reactivity
- Prefer `ref()` over `reactive()` for most cases. `ref()` works with primitives, has clearer `.value`.
- `shallowRef()` for large non-reactive data (API responses, configs).
- `markRaw()` for external library objects (Chart instances, WebSocket, Three.js).
- Never reassign a `reactive()` object — mutate properties instead.
- Use `toRefs()` when destructuring reactive objects to preserve reactivity.

### State Management
- Pinia for global state, composables for local/reusable logic.
- `storeToRefs()` when destructuring Pinia stores (preserves reactivity).
  Actions can be destructured directly.
- Define stores with `defineStore('name', () => { ... })` (setup syntax).

### TypeScript
- Type-based `defineProps<{ title: string; count?: number }>()`.
- Tuple syntax for `defineEmits<{ change: [id: number] }>()`.
- Type template refs: `useTemplateRef<HTMLInputElement>('el')` (Vue 3.5+).
- Use `InjectionKey` for typed provide/inject.

### Template Rules
- Never `v-if` and `v-for` on the same element. Pre-filter with `computed`.
- Always `:key` with `v-for` — use stable unique IDs, not array indices.
- Keep template expressions simple — move logic to `computed`.
- Avoid `v-html` unless sanitized. Use directive shorthands (`:`, `@`, `#`).

### Composables
- Prefix with `use` (file and function). Return named ref objects, not plain values.
- Accept refs/getters/plain values — use `toValue()` to unwrap.
- Clean up side effects in `onUnmounted`/`onScopeDispose`.
- One responsibility per composable.
- Call composables synchronously in setup — never after `await`.

### Performance
- Avoid `deep: true` on watchers unless necessary. Watch specific computed properties.
- Lazy-load routes with `defineAsyncComponent()` and dynamic `import()`.
- Split complex computed properties into smaller, independently cached ones.

### Code Quality
- `const` by default, `let` only when needed. Never `var`.
- Functions: max 50 lines. Files: max 400 lines preferred.
- No `console.log` in production. No hardcoded strings/magic numbers.
