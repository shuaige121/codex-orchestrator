## TypeScript Frontend Coding Rules

### Type Safety (STRICT)
- Enable strict mode in tsconfig.json: `strict: true`, `noUncheckedIndexedAccess: true`,
  `exactOptionalPropertyTypes: true`, `verbatimModuleSyntax: true`
- NEVER use `any`. Use `unknown` and narrow with type guards.
- NEVER use `as` type assertions unless you add a `// SAFETY: ...` comment.
  Prefer the `satisfies` operator: `const cfg = { ... } satisfies Config;`
- Separate type imports: `import type { Props } from './types';`
- No `enum`. Use `as const` objects:
  ```typescript
  const Status = { Active: 'active', Inactive: 'inactive' } as const;
  type Status = (typeof Status)[keyof typeof Status];
  ```

### Immutability & Variables
- Prefer `const` over `let`. NEVER use `var`.
- ALWAYS create new objects/arrays; NEVER mutate existing ones.
- Use `readonly` for function params: `function process(items: readonly string[])`

### Naming Conventions
- camelCase for variables, functions, methods
- PascalCase for components, types, interfaces, classes
- SCREAMING_SNAKE_CASE for constants
- Boolean variables: prefix with is/has/should
- Event handlers: prefix with handle/on

### Modern Syntax
- Template literals over string concatenation
- Nullish coalescing `??` and optional chaining `?.`
- Prefer `Map`/`Set` over object literals for dynamic keys
- `Object.entries()` / `Object.fromEntries()` for object transforms

### React / Component Rules
- Functional components ONLY. No class components.
- Custom hooks must start with `use` prefix
- Never call hooks conditionally or in loops
- Props interfaces named: `ComponentNameProps`
- Co-locate component, styles, tests in same directory
- Prefer composition over prop drilling

### Code Quality Hard Limits
- Functions: max 50 lines, max 5 parameters
- Files: max 400 lines preferred, 800 hard limit
- No `console.log` in production code
- No hardcoded strings/magic numbers
- Absolute imports only (path aliases in tsconfig)

### Error Handling
- All async operations MUST have try/catch or .catch()
- UI-facing errors need user-friendly messages
- Never silently swallow errors

### Input Validation
- Validate all external data at system boundaries using Zod
- Never trust data from APIs, URL params, localStorage, or user input
