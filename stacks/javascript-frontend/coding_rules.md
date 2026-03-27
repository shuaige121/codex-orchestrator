## JavaScript Frontend Coding Rules

### Variables & Scope
- Prefer `const` over `let`. NEVER use `var`.
- ALWAYS create new objects/arrays; NEVER mutate existing ones in state.
- Destructure objects and arrays when accessing multiple properties.

### Naming Conventions
- camelCase for variables, functions, methods
- PascalCase for components and classes
- SCREAMING_SNAKE_CASE for constants
- Boolean variables: prefix with is/has/should/can
- Event handlers: prefix with handle/on

### Modern Syntax
- Template literals over string concatenation
- Nullish coalescing `??` and optional chaining `?.`
- Prefer `Map`/`Set` over object literals for dynamic keys
- `Object.entries()` / `Object.fromEntries()` for object transforms
- Arrow functions for callbacks; named functions for top-level declarations
- Use default parameters instead of `||` fallbacks

### React / Component Rules
- Functional components ONLY. No class components.
- Custom hooks must start with `use` prefix
- Never call hooks conditionally or in loops
- Co-locate component, styles, tests in same directory
- Prefer composition over prop drilling
- Memoize expensive computations with `useMemo`/`useCallback` only when needed

### Code Quality
- Functions: max 50 lines, max 5 parameters
- Files: max 400 lines preferred, 800 hard limit
- No `console.log` in production code (use a logger or remove)
- No hardcoded strings/magic numbers — use named constants
- Use relative imports within feature modules, path aliases for cross-feature

### Error Handling
- All async operations MUST have try/catch or .catch()
- UI-facing errors need user-friendly messages
- Never silently swallow errors

### JSDoc for Public APIs
- Document exported functions with `@param` and `@returns`
- Use `@typedef` for complex object shapes when JSDoc types are useful
