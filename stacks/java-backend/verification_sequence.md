## Verification Sequence — Spring Boot

```bash
# 1. Build
./mvnw clean package -DskipTests || ./gradlew build -x test

# 2. Format check
./mvnw spotless:check || ./gradlew spotlessCheck || echo "No Spotless plugin — skip format check"

# 3. Tests
./mvnw test || ./gradlew test

# 4. Static analysis (if configured)
./mvnw spotbugs:check || ./gradlew spotbugsMain || echo "No SpotBugs plugin — skip static analysis"

# 5. Application starts
(./mvnw spring-boot:run || ./gradlew bootRun) &
APP_PID=$!
sleep 10
curl -sf http://localhost:8080/actuator/health || echo "No /actuator/health endpoint — verify project-specific health URL"
kill "$APP_PID"
```

IMPORTANT: Check pom.xml / build.gradle for the project's actual build tool.
If using Gradle-only project, run `./gradlew` equivalents shown above.
