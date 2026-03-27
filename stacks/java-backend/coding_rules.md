## Java Spring Boot Coding Rules

### Dependency Injection
- Constructor injection ONLY. Never `@Autowired` on fields.
- Single constructor needs no `@Autowired` annotation.
- Use `@ConfigurationProperties` with records for type-safe config. Never `@Value` inline.
- Prefer `@Configuration` + `@Bean` for infrastructure beans.

### Java 21+ Features
- Use records for DTOs, value objects, and API responses.
- Use sealed interfaces for domain modeling with exhaustive pattern matching.
- Use switch expressions with pattern matching (not statements).
- Use text blocks for multi-line strings (SQL, JSON templates).
- Use `Optional` for return types, never as method parameters. Prefer `.orElseThrow()`.
- Enable virtual threads: `spring.threads.virtual.enabled=true`.

### REST API Conventions
- `ResponseEntity<>` with proper HTTP status codes (201 create, 204 delete, 400 validation).
- Global exception handling via `@RestControllerAdvice` with `ProblemDetail` (RFC 9457).
- Validate all request bodies with `@Valid`. Return 400 with field-level details.
- API versioning via URL path: `/api/v1/`.

### Data Access
- Flyway or Liquibase for schema migrations. Never `ddl-auto=update/create` in prod.
- `@Transactional` on service methods, not repositories. Keep transactions short.
- Use `@Query` for complex queries. No derived method names beyond 2 conditions.
- Use `@EntityGraph` or `JOIN FETCH` to prevent N+1 queries.
- Use `Pageable` — never load unbounded result sets.

### Architecture
- Controllers thin: HTTP concerns only, delegate to service.
- Organize by feature/domain, not purely by technical layer.
- Never expose entities in API responses — always map to DTO records.

### Logging
- SLF4J (`@Slf4j` or `LoggerFactory.getLogger()`). Never `System.out.println`.
- Include correlation IDs. Never log sensitive data.

### Security
- Never hardcode secrets. Validate at startup — fail fast.
- Hash passwords with bcrypt or argon2.
- Explicit CORS allowed origins (never `*` in prod).

### Testing
- JUnit 5 + Mockito for unit tests. `@WebMvcTest` for controllers. `@DataJpaTest` for repos.
- `@SpringBootTest` + Testcontainers for integration tests.
- Test naming: `shouldReturnUserWhenIdExists()`. Independent tests, no shared state.
- Minimum 80% coverage on business logic.
