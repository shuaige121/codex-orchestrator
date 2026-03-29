## JavaScript Frontend Common Pitfalls

### 1. Mutating state directly in React
```javascript
// BAD: items.push('c'); setItems(items); // same reference, no re-render
// GOOD: setItems(prev => [...prev, 'c']);
```

### 2. Missing dependency array in useEffect
```javascript
// BAD: useEffect(() => { fetchData(userId); }); // runs every render
// GOOD: useEffect(() => { fetchData(userId); }, [userId]);
```

### 3. Unhandled promise rejections
```javascript
// BAD: fetchData(); // no error handling
// GOOD: fetchData().catch(err => setError(err.message));
```

### 4. Stale closures in intervals/timeouts
```javascript
// BAD: setInterval(() => { setCount(count + 1); }, 1000); // stale count
// GOOD: setInterval(() => { setCount(prev => prev + 1); }, 1000);
```

### 5. == instead of ===
```javascript
// BAD: if (value == null) — matches both null and undefined
// GOOD: if (value === null) or if (value == null) only when intentional
```

### 6. Not cleaning up effects
```javascript
// BAD: useEffect(() => { window.addEventListener('resize', handler); }, []);
// GOOD: useEffect(() => { window.addEventListener('resize', handler);
//   return () => window.removeEventListener('resize', handler); }, []);
```

### 7. Barrel file circular dependencies
```javascript
// BAD: export * from './auth'; // creates circular deps
// GOOD: import directly from specific modules
```

### 8. Memory leaks from uncleared subscriptions
```javascript
// Always return cleanup function from useEffect for WebSocket, event listeners
```

### 9. Using index as key in lists
```javascript
// BAD: items.map((item, i) => <div key={i}>...</div>)
// GOOD: items.map(item => <div key={item.id}>...</div>)
```

### 10. Not handling loading/error states
```javascript
// Always handle: loading, error, empty, and success states in data fetching
```
