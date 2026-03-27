## React Native Common Pitfalls

### 1. ScrollView for long lists
```typescript
// BAD: renders ALL items, destroys memory
<ScrollView>{items.map(i => <Item key={i.id} />)}</ScrollView>
// GOOD: FlashList virtualizes, recycles views
<FlashList data={items} renderItem={...} estimatedItemSize={80} />
```

### 2. JS-thread animations cause jank
```typescript
// BAD: Animated.timing with useNativeDriver: false
// GOOD: react-native-reanimated (runs on UI thread)
```

### 3. Inline styles cause re-renders
```typescript
// BAD: <View style={{ flex: 1, padding: 16 }}>
// GOOD: const styles = StyleSheet.create({...}); <View style={styles.container}>
```

### 4. Index as key in lists
```typescript
// BAD: keyExtractor={(_, i) => i.toString()}
// GOOD: keyExtractor={item => item.id}
```

### 5. Barrel imports kill bundle size
```typescript
// BAD: import { Button, Card } from '@/components';
// GOOD: import { Button } from '@/components/ui/button';
```

### 6. API data in Zustand instead of TanStack Query
```typescript
// BAD: manual loading/error state in store
// GOOD: useQuery({ queryKey, queryFn }) — automatic cache, retry, refresh
```

### 7. SafeAreaView from wrong package
```typescript
// BAD: import { SafeAreaView } from 'react-native';
// GOOD: import { SafeAreaView } from 'react-native-safe-area-context';
```

### 8. Secrets in source code
```typescript
// BAD: const API_KEY = 'sk-abc123';
// GOOD: Constants.expoConfig?.extra?.apiKey via EAS Secrets
```

### 9. console.log in production
// Causes memory leaks. Use babel-plugin-transform-remove-console.

### 10. Missing getItemLayout for fixed-height lists
// FlatList must measure each item dynamically without it — use FlashList instead.
