## Spring Boot Project Structure

```
project-root/
├── pom.xml (or build.gradle)
├── src/
│   ├── main/
│   │   ├── java/com/example/myapp/
│   │   │   ├── MyAppApplication.java
│   │   │   ├── config/
│   │   │   │   ├── SecurityConfig.java
│   │   │   │   └── WebConfig.java
│   │   │   ├── user/                   # Feature package
│   │   │   │   ├── User.java          # Entity
│   │   │   │   ├── UserRepository.java
│   │   │   │   ├── UserService.java
│   │   │   │   ├── UserController.java
│   │   │   │   ├── UserRequest.java   # DTO record
│   │   │   │   └── UserResponse.java  # DTO record
│   │   │   ├── order/                  # Another feature
│   │   │   └── common/
│   │   │       └── exception/
│   │   │           └── GlobalExceptionHandler.java
│   │   └── resources/
│   │       ├── application.yml
│   │       ├── application-dev.yml
│   │       └── db/migration/
│   │           └── V1__create_users.sql
│   └── test/
│       └── java/com/example/myapp/
│           ├── user/
│           │   ├── UserServiceTest.java
│           │   └── UserControllerTest.java
│           └── integration/
│               └── UserIntegrationTest.java
```

Organize by feature/domain. Controllers thin, logic in services.
