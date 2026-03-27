## React Native + Expo Coding Rules

### TypeScript
- Strict mode everywhere. Never use `any`; prefer `unknown` with type guards.
- `const` by default, `let` only when mutation required. Never `var`.
- Prefer ESM imports and avoid `require()` unless a library only supports it.
- Prefer avoiding barrel `index.ts` exports in hot paths (can hurt Fast Refresh in large trees).
- Absolute path aliases: `@/` mapped to `./src`.
- Define explicit TypeScript interfaces for all component props.

### Components
- Functional components only. Use function declarations for better stack traces.
- Component file structure: (1) Props interface, (2) function, (3) hooks at top,
  (4) early returns, (5) JSX, (6) StyleSheet.create() at bottom.
- Check existing components before creating new ones. Reuse design system primitives.
- Never hardcode colors or spacing — import from theme system.

### Navigation
- Use Expo Router for file-based routing. Route files should be thin wrappers.
- Use route groups `(tabs)`, `(auth)` to organize hierarchies.
- Type-safe navigation with Expo Router's typed routes.

### State Management
- Zustand for client state, TanStack Query for server state. Prefer clear ownership; if both are used together, document boundaries.
- One Zustand store per feature. Persist with `zustand/middleware` + `react-native-mmkv`.
- TanStack Query: `staleTime: 5min`, structured query keys `['users', userId]`.

### Performance
- `FlashList` from `@shopify/flash-list` instead of FlatList for long lists.
  Always provide `estimatedItemSize` and stable `keyExtractor`.
- Prefer `react-native-reanimated` for animations (UI thread); JS-driven `Animated` is acceptable for simple non-critical transitions.
- `expo-image` instead of React Native's `Image`. Use `.webp` format.
- `StyleSheet.create()` — never inline styles (creates new objects every render).

### Platform-Specific
- `Platform.select()` for small differences. File extensions (.ios.tsx/.android.tsx) for large ones.
- `SafeAreaView` from `react-native-safe-area-context`, never from `react-native`.
- Always test on both iOS and Android.

### Security
- `expo-secure-store` for tokens/credentials (encrypted).
- `react-native-mmkv` for non-sensitive persistent state.
- Never hardcode API keys — use `expo-constants` + EAS Secrets.
- Strip `console.log` from production with `babel-plugin-transform-remove-console`.

### Error Handling
- Wrap app in `Sentry.ErrorBoundary` with fallback UI.
- All async event handlers need try/catch. Log to Sentry with context.
