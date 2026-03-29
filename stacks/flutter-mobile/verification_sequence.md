## Verification Sequence — Flutter Mobile

```bash
# 1. Static analysis (lint + type check)
/snap/bin/flutter analyze

# 2. Format check
/snap/bin/dart format --set-exit-if-changed lib/

# 3. Unit & widget tests
/snap/bin/flutter test

# 4. Web build (smoke test)
/snap/bin/flutter build web
```

IMPORTANT: All commands must be run from the project root directory.
Flutter SDK is installed at `/snap/bin/flutter`, Dart at `/snap/bin/dart`.
If `flutter analyze` shows warnings but no errors, it passes.
