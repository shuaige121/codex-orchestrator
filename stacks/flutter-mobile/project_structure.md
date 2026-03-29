## Flutter Mobile Project Structure

```
sg_student_rent/
├── assets/
│   ├── images/              # App images, splash, placeholders
│   └── icons/               # Custom SVG icons
├── lib/
│   ├── main.dart            # App entry point, ProviderScope
│   ├── app.dart             # MaterialApp.router with theme config
│   ├── models/              # Data models (immutable)
│   │   ├── property.dart    # Property/listing model
│   │   ├── school.dart      # School model with coordinates
│   │   ├── filter.dart      # Search filter model
│   │   └── enums.dart       # PropertyType, RoomType, etc.
│   ├── providers/           # Riverpod providers
│   │   ├── property_providers.dart
│   │   ├── school_providers.dart
│   │   ├── filter_providers.dart
│   │   ├── favorites_providers.dart
│   │   ├── theme_providers.dart
│   │   └── auth_providers.dart
│   ├── router/              # go_router configuration
│   │   └── app_router.dart
│   ├── pages/               # Full-screen pages
│   │   ├── home/            # Map-based home page
│   │   │   └── home_page.dart
│   │   ├── listing/         # Property list page
│   │   │   └── listing_page.dart
│   │   ├── detail/          # Property detail page
│   │   │   └── detail_page.dart
│   │   ├── favorites/       # Saved properties
│   │   │   └── favorites_page.dart
│   │   └── profile/         # User profile / settings
│   │       └── profile_page.dart
│   ├── widgets/             # Reusable widgets
│   │   ├── property_card.dart
│   │   ├── school_chip.dart
│   │   ├── filter_sheet.dart
│   │   ├── map_marker.dart
│   │   ├── image_carousel.dart
│   │   ├── amenity_tag.dart
│   │   └── shimmer_loading.dart
│   ├── theme/               # Design system
│   │   ├── app_theme.dart   # ThemeData (light + dark)
│   │   ├── app_colors.dart  # Color constants
│   │   └── app_text_styles.dart
│   ├── services/            # API / external service layer
│   │   ├── onemap_service.dart
│   │   └── property_service.dart
│   ├── utils/               # Helpers
│   │   ├── map_utils.dart   # External map launch, distance calc
│   │   └── formatters.dart  # Price, date formatting
│   ├── data/                # Mock / seed data
│   │   ├── mock_properties.dart
│   │   └── sg_schools.dart  # Hardcoded school coordinates
│   └── l10n/                # Localization
│       ├── app_en.arb
│       ├── app_zh.arb
│       ├── app_ms.arb
│       └── app_ta.arb
├── test/                    # Unit + widget tests
├── android/
├── ios/
├── web/
├── pubspec.yaml
└── analysis_options.yaml
```

Key conventions:
- One widget per file, filename matches class name in snake_case.
- Pages are full screens, widgets are reusable components.
- Models are immutable data classes with fromJson/toJson.
- Providers are grouped by feature domain.
