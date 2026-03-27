## Spring Boot Common Pitfalls

### 1. N+1 Query Problem
```java
// BAD: N additional queries for items
List<Order> orders = orderRepository.findAll();
orders.forEach(o -> o.getItems().size()); // N queries!
// GOOD: @Query("SELECT o FROM Order o LEFT JOIN FETCH o.items")
```

### 2. @Transactional Self-Invocation
```java
// BAD: this.processInternal() bypasses proxy — no transaction!
// FIX: extract to separate service bean
```

### 3. @Transactional on Private Methods
```java
// BAD: Spring AOP cannot proxy private/final methods
// GOOD: must be public and non-final
```

### 4. Swallowed Exceptions Prevent Rollback
```java
// BAD: catch(Exception) prevents Spring from seeing error — no rollback!
// GOOD: let it propagate, or re-throw after logging
```

### 5. Checked Exceptions Don't Rollback
```java
// BAD: @Transactional — checked exceptions don't roll back by default
// GOOD: @Transactional(rollbackFor = BusinessException.class)
```

### 6. Circular Dependencies
```java
// BAD: ServiceA ↔ ServiceB circular
// FIX: extract shared logic to a third service
```

### 7. Field Injection (untestable)
```java
// BAD: @Autowired private UserRepository repo;
// GOOD: constructor injection with final field
```

### 8. Derived Query Name Explosion
```java
// BAD: findByStatusAndCategoryAndPriceGreaterThan... — unreadable
// GOOD: @Query with named params for 3+ conditions
```

### 9. Missing Pagination → OOM
```java
// BAD: findAll() on million-row table
// GOOD: findAll(PageRequest.of(0, 20))
```

### 10. ddl-auto in Production
```yaml
# BAD: spring.jpa.hibernate.ddl-auto: update
# GOOD: ddl-auto: validate + Flyway migrations
```
