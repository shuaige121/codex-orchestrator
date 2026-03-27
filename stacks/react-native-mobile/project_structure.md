## React Native Expo Project Structure

```
project-root/
├── assets/                      # Images, fonts, icons
├── e2e/                         # Detox E2E tests
├── src/
│   ├── app/                     # Expo Router file-based routes
│   │   ├── _layout.tsx          # Root layout (providers)
│   │   ├── index.tsx
│   │   ├── (tabs)/
│   │   │   ├── _layout.tsx
│   │   │   └── index.tsx
│   │   └── (auth)/
│   │       ├── login.tsx
│   │       └── register.tsx
│   ├── features/                # Feature modules
│   │   ├── auth/
│   │   │   ├── login-screen.tsx
│   │   │   ├── api.ts
│   │   │   └── use-auth-store.ts
│   │   └── settings/
│   ├── components/
│   │   └── ui/                  # Design system primitives
│   ├── hooks/
│   ├── lib/
│   │   ├── api/
│   │   └── storage.ts
│   ├── stores/                  # Global Zustand stores
│   ├── types/
│   └── theme/
│       ├── colors.ts
│       └── fonts.ts
├── app.json
├── eas.json
├── tsconfig.json
├── jest.config.js
└── package.json
```

Routes in `app/` are thin — delegate to `features/`.
Platform-specific: `.ios.tsx` / `.android.tsx` / `.web.tsx`.
