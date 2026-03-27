## Frontend Project Structure (React + Vite — JavaScript)

```
project-root/
├── src/
│   ├── App.jsx                    # App shell / root component
│   ├── main.jsx                   # Entry point
│   ├── components/                # Shared UI components
│   │   └── Button/
│   │       ├── Button.jsx
│   │       └── Button.test.jsx
│   ├── features/                  # Feature modules (domain-organized)
│   │   ├── auth/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   └── api.js
│   │   └── dashboard/
│   ├── hooks/                     # Shared custom hooks
│   ├── lib/                       # Utilities, constants, helpers
│   │   ├── api-client.js
│   │   └── constants.js
│   ├── assets/                    # Static assets (images, fonts)
│   └── styles/                    # Global styles, theme
├── public/                        # Static files served as-is
├── vite.config.js
├── eslint.config.js               # ESLint flat config (v9+)
├── package.json                   # "type": "module"
└── package-lock.json / pnpm-lock.yaml
```

Organize by FEATURE/DOMAIN, not by file type.
Co-locate tests with their component.
