## JavaScript Backend Project Structure
```
├── src/
│   ├── index.js                # Entry point
│   ├── app.js                  # Express/Fastify app setup
│   ├── routes/
│   │   ├── users.js
│   │   └── health.js
│   ├── middleware/
│   │   ├── auth.js
│   │   └── errorHandler.js
│   ├── services/
│   │   └── userService.js
│   ├── models/                 # Database models
│   │   └── user.js
│   ├── utils/
│   │   └── logger.js
│   └── config/
│       └── index.js            # Environment config
├── test/
│   ├── routes/
│   │   └── users.test.js
│   └── services/
│       └── userService.test.js
├── package.json
├── .eslintrc.js                # Or eslint.config.js
├── .prettierrc
├── .env.example
└── Dockerfile
```
