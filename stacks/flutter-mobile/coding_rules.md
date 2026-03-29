## Flutter Mobile Coding Rules

### Dart Language
- Use Dart 3.x features: records, patterns, sealed classes, class modifiers.
- `final` by default. Only use `var` when mutation is required. Never use `dynamic` unless interfacing with JSON.
- Prefer `const` constructors everywhere possible. Mark widgets `const` when all parameters are compile-time constants.
- Use trailing commas for better formatting and diffs.
- Absolute imports only: `package:sg_student_rent/...`. Never relative imports.

### Widget Architecture
- Functional decomposition: extract widgets into separate classes when they exceed ~80 lines or are reused.
- Widget file structure: (1) imports, (2) class definition, (3) build method, (4) helper methods, (5) private sub-widgets.
- Prefer `StatelessWidget` unless local ephemeral state is needed (animations, TextEditingController).
- Check existing widgets before creating new ones. Reuse design system components.
- Never hardcode colors, spacing, or text styles — use theme system (`Theme.of(context)`).

### State Management — Riverpod
- Use `flutter_riverpod` for all shared state.
- Provider types:
  - `Provider` for computed/derived values
  - `StateProvider` for simple mutable state
  - `NotifierProvider` / `AsyncNotifierProvider` for complex state with logic
  - `FutureProvider` for one-shot async data
  - `StreamProvider` for real-time data
- One provider file per feature domain: `property_providers.dart`, `auth_providers.dart`.
- Always use `ref.watch()` in build methods, `ref.read()` in callbacks.

### Routing — go_router
- Define all routes in a single `lib/router/app_router.dart`.
- Use `ShellRoute` for bottom navigation with persistent tab state.
- Type-safe route parameters with extension methods.
- Use `GoRoute` path constants to avoid hardcoded strings.

### Map — flutter_map + OneMap
- Use OneMap tile URLs: `https://www.onemap.gov.sg/maps/tiles/{style}/{z}/{x}/{y}.png`
- Supported styles: `Default`, `Default_HD`, `Grey`, `Night` (dark mode).
- Center on Singapore: `LatLng(1.3521, 103.8198)`, zoom 11-18.
- Always include OneMap attribution as required by ToS.
- Dispose `MapController` in `dispose()` to prevent memory leaks.
- Use marker clustering for large datasets.

### Networking & Data
- Use `http` package for REST API calls.
- All API calls go through a service layer in `lib/services/`.
- Model classes use `fromJson` / `toJson` factory constructors.
- Use `freezed` or manual immutable classes for data models.

### Theming
- Support dark and light mode, following system setting.
- Define all colors in `lib/theme/app_colors.dart` as `MaterialColor` / `Color` constants.
- Use `ThemeData.dark()` and `ThemeData.light()` as bases, override with custom values.
- Text styles in `lib/theme/app_text_styles.dart`.
- Use `google_fonts` for typography.

### i18n
- Use `flutter_localizations` + ARB files for localization.
- Support 4 locales: zh (Chinese), en (English), ms (Malay), ta (Tamil).
- All user-facing strings must use `AppLocalizations.of(context)!.key`.
- Never hardcode user-visible strings in widget code.

### Performance
- Use `ListView.builder` / `SliverList` for long lists — never `Column` with `map()`.
- Cache network images with `cached_network_image`.
- Use `const` widgets to avoid unnecessary rebuilds.
- Lazy-load map markers based on visible viewport.
- Use `AutomaticKeepAliveClientMixin` for tab pages to preserve state.

### Platform-Specific
- Use `Platform.isIOS` / `Platform.isAndroid` for platform checks (not available on web).
- Use `kIsWeb` for web platform detection.
- External map navigation: Apple Maps URL on iOS, Google Maps URL on Android/Web.
- Use `url_launcher` for all external URL/app launches.

### Security
- Never hardcode API keys or secrets in source code.
- Use environment variables or `--dart-define` for configuration.
- Store auth tokens with `flutter_secure_storage` (not `shared_preferences`).
- Sanitize all user input before display or API submission.

### Error Handling
- Wrap async operations in try/catch. Never swallow errors silently.
- Use `AsyncValue` from Riverpod for loading/error/data states.
- Show user-friendly error messages in the UI, log details to console in debug mode.
