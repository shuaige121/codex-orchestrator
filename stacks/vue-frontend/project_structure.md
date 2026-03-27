## Vue.js Project Structure

```
project-root/
├── src/
│   ├── assets/                   # Static assets, global styles
│   ├── components/               # Shared base components
│   │   ├── BaseButton.vue
│   │   └── BaseModal.vue
│   ├── composables/              # Shared composables (useAuth, useFetch)
│   ├── layouts/                  # Layout components
│   ├── modules/                  # Feature modules (self-contained)
│   │   ├── users/
│   │   │   ├── components/
│   │   │   ├── composables/
│   │   │   ├── stores/
│   │   │   ├── views/
│   │   │   ├── types.ts
│   │   │   └── __tests__/
│   │   └── products/
│   ├── plugins/                  # Vue plugins
│   ├── router/
│   │   └── index.ts
│   ├── stores/                   # Global Pinia stores
│   ├── types/
│   ├── utils/
│   ├── App.vue
│   └── main.ts
├── vite.config.ts
├── tsconfig.json
├── eslint.config.js
├── package.json
└── vitest.config.ts
```

Components: PascalCase.vue. Composables: useCamelCase.ts.
Organize by feature/domain in `modules/`.
