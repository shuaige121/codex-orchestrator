## JavaScript Backend Common Pitfalls

### 1. Callback Hell / Unhandled Promises
```javascript
// BAD: nested callbacks
fs.readFile('a', (err, data) => {
  fs.readFile('b', (err, data) => { ... });
});
// GOOD: async/await
const a = await fs.promises.readFile('a');
const b = await fs.promises.readFile('b');
```

### 2. Not Closing Resources
```javascript
// BAD: connection leak
const conn = await pool.getConnection();
const data = await conn.query('SELECT ...');
// if query throws, conn is never released!
// GOOD: try/finally
const conn = await pool.getConnection();
try {
  return await conn.query('SELECT ...');
} finally {
  conn.release();
}
```

### 3. Blocking the Event Loop
```javascript
// BAD: synchronous file I/O in request handler
app.get('/', (req, res) => {
  const data = fs.readFileSync('large.json');  // blocks ALL requests
});
// GOOD: async
app.get('/', async (req, res) => {
  const data = await fs.promises.readFile('large.json');
});
```

### 4. Missing Error Handler in Express
```javascript
// BAD: unhandled async error crashes the server
app.get('/', async (req, res) => {
  const data = await db.query();  // if this throws, 500 with no response
});
// GOOD: error middleware
app.get('/', async (req, res, next) => {
  try { ... } catch (err) { next(err); }
});
app.use((err, req, res, next) => {
  res.status(err.status || 500).json({ error: err.message });
});
```

### 5. require() Caching Side Effects
```javascript
// Module-level state is shared across all requires
let counter = 0;  // this is a singleton!
module.exports.increment = () => ++counter;
// FIX: use factory functions or classes for stateful modules
```

### 6. JSON.parse Without Try/Catch
```javascript
// BAD: crashes on invalid JSON
const data = JSON.parse(userInput);
// GOOD:
try { const data = JSON.parse(userInput); }
catch { return res.status(400).json({ error: 'Invalid JSON' }); }
```

### 7. Memory Leaks from Event Listeners
```javascript
// BAD: adds new listener on every request
app.get('/', (req, res) => {
  emitter.on('data', handler);  // never removed!
});
// GOOD: use once() or remove in cleanup
emitter.once('data', handler);
```

### 8. Not Setting Timeouts
```javascript
// BAD: fetch with no timeout hangs forever
const res = await fetch(url);
// GOOD:
const res = await fetch(url, { signal: AbortSignal.timeout(5000) });
```

### 9. process.exit() in Library Code
```javascript
// BAD: kills the entire process
if (error) process.exit(1);
// GOOD: throw and let the caller decide
if (error) throw new AppError('fatal', { cause: error });
```

### 10. Mixing ESM and CommonJS
```javascript
// BAD: require() in ESM file
import foo from './foo.js';
const bar = require('./bar');  // ERROR in ESM

// GOOD: use import for everything in ESM, or use createRequire
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
```
