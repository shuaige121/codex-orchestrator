## Flutter Mobile Common Pitfalls

### 1. setState in complex widgets instead of Riverpod
```dart
// BAD: setState causes full widget rebuild, state lost on navigation
class _MyState extends State<MyWidget> {
  List<Property> properties = [];
  void load() { setState(() { properties = ...; }); }
}

// GOOD: Riverpod provider, survives navigation, testable
final propertiesProvider = FutureProvider((ref) => api.fetchProperties());
// In widget: ref.watch(propertiesProvider)
```

### 2. Not disposing controllers
```dart
// BAD: Memory leak — controller lives forever
final controller = MapController();

// GOOD: Dispose in StatefulWidget.dispose()
@override
void dispose() {
  _mapController.dispose();
  _searchController.dispose();
  super.dispose();
}
```

### 3. Column with map() for long lists
```dart
// BAD: Renders ALL items at once, OOM on 500+ items
Column(children: properties.map((p) => PropertyCard(p)).toList())

// GOOD: Lazy rendering, only visible items in memory
ListView.builder(
  itemCount: properties.length,
  itemBuilder: (ctx, i) => PropertyCard(properties[i]),
)
```

### 4. Hardcoded colors ignoring theme
```dart
// BAD: Breaks dark mode
Text('Price', style: TextStyle(color: Colors.black))

// GOOD: Adapts to theme
Text('Price', style: Theme.of(context).textTheme.bodyLarge)
```

### 5. Missing const constructors
```dart
// BAD: Rebuilds every frame
return Container(padding: EdgeInsets.all(16), child: Icon(Icons.home));

// GOOD: Compile-time constant, skipped in rebuild
return const Padding(padding: EdgeInsets.all(16), child: Icon(Icons.home));
```

### 6. Using context after async gap
```dart
// BAD: Context may be invalid after await
await someAsyncOp();
Navigator.of(context).pop(); // May crash

// GOOD: Check mounted
await someAsyncOp();
if (mounted) Navigator.of(context).pop();
// Or better: use go_router with ref, no context needed
```

### 7. Blocking UI thread with heavy computation
```dart
// BAD: JSON parsing on main isolate freezes UI
final data = jsonDecode(hugeJsonString);

// GOOD: Use compute() for heavy work
final data = await compute(jsonDecode, hugeJsonString);
```

### 8. Not handling all AsyncValue states
```dart
// BAD: Only handles data, crashes on loading/error
final properties = ref.watch(propertiesProvider);
return ListView(children: properties.value!.map(...));

// GOOD: Handle all states
return properties.when(
  data: (list) => ListView.builder(...),
  loading: () => const ShimmerList(),
  error: (e, st) => ErrorWidget(e.toString()),
);
```

### 9. Platform.isIOS on web crashes
```dart
// BAD: dart:io Platform not available on web
if (Platform.isIOS) { ... }

// GOOD: Use kIsWeb first
if (kIsWeb) {
  // web logic
} else if (Platform.isIOS) {
  // iOS logic
}
```

### 10. Map markers not clustered
```dart
// BAD: 1000 individual markers, map freezes
markers: properties.map((p) => Marker(point: p.latLng, ...)).toList()

// GOOD: Use flutter_map_marker_cluster or viewport-based filtering
// Only show markers in current visible bounds, cluster when zoomed out
```

### 11. Forgetting OneMap attribution
```dart
// BAD: Violates OneMap ToS
FlutterMap(children: [TileLayer(...)])

// GOOD: Always include attribution
FlutterMap(children: [
  TileLayer(urlTemplate: '...'),
  RichAttributionWidget(attributions: [
    TextSourceAttribution('OneMap | Singapore Land Authority'),
  ]),
])
```

### 12. Relative imports
```dart
// BAD: Breaks refactoring, confusing paths
import '../../../models/property.dart';

// GOOD: Absolute package imports
import 'package:sg_student_rent/models/property.dart';
```
