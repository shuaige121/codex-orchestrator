## Vue.js Common Pitfalls

### 1. Losing reactivity by destructuring reactive()
```typescript
// BAD: x and y are plain numbers, NOT reactive
const state = reactive({ x: 0, y: 0 })
const { x, y } = state  // reactivity lost!
// GOOD: const { x, y } = toRefs(state) or just use ref()
```

### 2. Destructuring Pinia store without storeToRefs()
```typescript
// BAD: count is plain number
const { count } = store
// GOOD: const { count } = storeToRefs(store)
```

### 3. Mutating props directly
```vue
// BAD: props.items.push('new') — vue/no-mutating-props
// GOOD: emit('update', [...props.items, 'new'])
```

### 4. Reassigning a reactive() object
```typescript
// BAD: state = reactive({ count: 1 }) — breaks reactivity
// GOOD: state.count = 1 or use ref() with .value reassignment
```

### 5. Forgetting .value on refs in script
```typescript
// BAD: if (count === 0) — comparing Ref object
// GOOD: if (count.value === 0) — in templates .value is auto-unwrapped
```

### 6. v-if and v-for on same element
```vue
<!-- BAD: confusing precedence -->
<li v-for="user in users" v-if="user.active" :key="user.id">
<!-- GOOD: pre-filter with computed -->
```

### 7. Accessing template ref before mount
```typescript
// BAD: el.value is null during setup
// GOOD: access in onMounted(() => { el.value?.focus() })
```

### 8. Deep watching large objects
```typescript
// BAD: watch(hugeObj, cb, { deep: true }) — performance drain
// GOOD: watch specific computed property
```

### 9. Async operations breaking composable context
```typescript
// BAD: composables called after await lose component instance
// GOOD: call all composables synchronously BEFORE any await
```

### 10. Array index as :key
```vue
<!-- BAD: :key="index" causes incorrect DOM reuse -->
<!-- GOOD: :key="item.id" -->
```

### 11. Using reactive() generic argument
```typescript
// BAD: const book = reactive<Book>({...}) — type mismatch due to unwrapping
// GOOD: const book: Book = reactive({...})
```

### 12. Not handling null for conditional template refs
```vue
<!-- v-if makes ref null when hidden — always use ?. -->
```
