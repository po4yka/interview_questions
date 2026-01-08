---\
id: sysdes-003
title: "Проектирование REST API / REST API Design Best Practices"
aliases: ["REST API Design", "Проектирование REST API"]
topic: system-design
subtopics: [api-design, http, rest-api]
question_kind: system-design
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-system-design
related: [c-architecture-patterns, q-caching-strategies--system-design--medium, q-microservices-vs-monolith--system-design--hard]
created: 2025-10-12
updated: 2025-11-11
tags: [api-design, difficulty/medium, http, rest-api, system-design]
sources: ["https://en.wikipedia.org/wiki/Representational_state_transfer"]

---\
# Вопрос (RU)
> Каковы лучшие практики проектирования RESTful API? Как структурировать endpoints, обрабатывать ошибки и обеспечивать качество API?

# Question (EN)
> What are the best practices for designing RESTful APIs? How do you structure endpoints, handle errors, and ensure API quality?

---

## Ответ (RU)

### Требования

**Функциональные:**
- Поддержка CRUD-операций над ресурсами через RESTful endpoints.
- Корректное использование HTTP методов и кодов статуса.
- Стандартизированная обработка ошибок.
- Поддержка пагинации, фильтрации и сортировки коллекций.
- Версионирование API для эволюции контрактов.
- Защищенный доступ к API (аутентификация, авторизация).
- Поддержка кеширования и идемпотентности там, где необходимо.
- Документация API (например, OpenAPI/Swagger).

**Нефункциональные:**
- Масштабируемость и расширяемость API.
- Надежность и предсказуемость поведения (семантика методов, статусы).
- Хороший developer experience (понятные URL, схемы ошибок, документация).
- Производительность (кеширование, пагинация).
- Безопасность (TLS, rate limiting, валидация входных данных).

### Архитектура

- Клиент-серверная архитектура с четким разделением ответственности.
- Ресурсно-ориентированная модель: каждое бизнес-сущность как ресурс с уникальным URI.
- Использование стандартных HTTP методов и кодов как контракта взаимодействия.
- Прослойка маршрутизации/контроллеров, маппящая HTTP-запросы на доменные сервисы.
- Централизованный обработчик ошибок, возвращающий единый формат ответа.
- Интеграция с системами аутентификации/авторизации (JWT, OAuth2).
- Использование механизмов кеширования (HTTP заголовки, CDN) и rate limiting на уровне API-шлюза или прокси.

**Теория REST API:**
REST (Representational State Transfer) - архитектурный стиль для распределённых систем, основанный на ресурсах, стандартных HTTP методах и stateless коммуникации. Хороший дизайн API критичен для maintainability, scalability и developer experience.

**Принципы REST:**
1. **Resources** - всё является ресурсом (users, orders, products)
2. **HTTP Methods** - стандартные глаголы (GET, POST, PUT, DELETE)
3. **Stateless** - каждый запрос содержит всю необходимую информацию
4. **Client-Server** - разделение ответственности
5. **Cacheable** - ответы могут кешироваться
6. **Uniform Interface** - единообразная идентификация ресурсов

**1. Именование ресурсов:**

*Теория:* Используйте существительные (nouns), не глаголы (verbs). HTTP методы уже являются глаголами. Используйте множественное число для коллекций. Вложенные ресурсы для отношений.

✅ **Правильно:**
```text
GET    /users             # Получить всех пользователей
POST   /users             # Создать пользователя
GET    /users/123         # Получить конкретного пользователя
PUT    /users/123         # Обновить пользователя
DELETE /users/123         # Удалить пользователя
GET    /users/123/orders  # Заказы пользователя (вложенный ресурс)
```

❌ **Неправильно:**
```text
GET  /getUsers
POST /createUser
POST /updateUser/123
```

```kotlin
// Правильная структура endpoints
@RestController
@RequestMapping("/api/v1/users")
class UserController(private val userService: UserService) {
    @GetMapping
    fun getAll(): List<User> = userService.findAll()

    @GetMapping("/{id}")
    fun getOne(@PathVariable id: Long): User = userService.findById(id)

    @PostMapping
    fun create(@RequestBody user: User): ResponseEntity<User> {
        val created = userService.create(user)
        return ResponseEntity.status(HttpStatus.CREATED).body(created)
    }

    @PutMapping("/{id}")
    fun update(@PathVariable id: Long, @RequestBody user: User): User =
        userService.update(id, user)

    @DeleteMapping("/{id}")
    fun delete(@PathVariable id: Long): ResponseEntity<Void> {
        userService.delete(id)
        return ResponseEntity.noContent().build()
    }
}
```

**2. HTTP методы:**

*Теория:* Каждый HTTP метод имеет семантику. GET - безопасный (safe) и идемпотентный. POST - не идемпотентный (обычно используется для операций, которые могут иметь побочные эффекты, например создание ресурса). PUT/DELETE - идемпотентные (повторный вызов даёт тот же наблюдаемый результат). PATCH обычно не гарантируется как идемпотентный.

| Метод | Назначение | Идемпотентный | Safe | `Request` Body | `Response` Body |
|-------|-----------|---------------|------|--------------|---------------|
| GET | Получить ресурс | Да | Да | Обычно нет | Да |
| POST | Создать ресурс / выполнить команду | Нет | Нет | Да | Да |
| PUT | Заменить ресурс | Да | Нет | Да | Да |
| PATCH | Частичное обновление | Не гарантируется | Нет | Да | Да |
| DELETE | Удалить ресурс | Да | Нет | Опционально | Опционально |

**3. HTTP коды статуса:**

*Теория:* Используйте правильные HTTP коды для передачи результата операции. Клиент должен понимать результат по коду, не парсируя body.

**Успешные (2xx):**
- `200 OK` - успешный GET, PUT, PATCH
- `201 Created` - успешный POST (с заголовком Location)
- `204 No Content` - успешный DELETE (и другие случаи без тела ответа)

**Клиентские ошибки (4xx):**
- `400 Bad Request` - невалидные данные
- `401 Unauthorized` - не аутентифицирован
- `403 Forbidden` - нет прав доступа
- `404 Not Found` - ресурс не найден
- `409 Conflict` - конфликт (например, duplicate email)
- `422 Unprocessable Entity` - валидация не прошла
- `429 Too Many Requests` - rate limit превышен

**Серверные ошибки (5xx):**
- `500 Internal Server Error` - ошибка сервера
- `503 ``Service`` Unavailable` - сервис временно недоступен

```kotlin
// Стандартизированный формат ошибок
import jakarta.servlet.http.HttpServletRequest

data class ErrorResponse(
    val status: Int,
    val error: String,
    val message: String,
    val timestamp: Instant,
    val path: String,
    val details: List<String>? = null
)

@ExceptionHandler(UserNotFoundException::class)
fun handleNotFound(ex: UserNotFoundException, request: HttpServletRequest): ResponseEntity<ErrorResponse> {
    val body = ErrorResponse(
        status = HttpStatus.NOT_FOUND.value(),
        error = HttpStatus.NOT_FOUND.reasonPhrase,
        message = ex.message ?: "User not found",
        timestamp = Instant.now(),
        path = request.requestURI
    )
    return ResponseEntity.status(HttpStatus.NOT_FOUND).body(body)
}
```

**4. Версионирование API:**

*Теория:* API эволюционирует, breaking changes неизбежны. Версионирование позволяет поддерживать старых клиентов при внедрении новых фич. Три основных подхода: URL path, query parameter, header.

**Подходы:**
- **URL path** (распространено и просто): `/api/v1/users`, `/api/v2/users`
- **Query parameter**: `/api/users?version=1`
- **Header**: `Accept: application/vnd.api.v1+json`

```kotlin
// Версионирование через URL path
@RequestMapping("/api/v1/users")
class UserControllerV1

@RequestMapping("/api/v2/users")
class UserControllerV2  // Новая версия с breaking changes
```

**5. Пагинация, фильтрация, сортировка:**

*Теория:* Большие коллекции должны поддерживать пагинацию для производительности. Фильтрация и сортировка через query parameters. Стандартизируйте формат ответа.

```kotlin
// Пагинация и фильтрация
GET /users?page=0&size=20&sort=name,asc&status=active&role=admin

// Пример структуры ответа

data class PageResponse<T>(
    val content: List<T>,
    val page: Int,
    val size: Int,
    val totalElements: Long,
    val totalPages: Int
)

@GetMapping("/users")
fun getUsers(
    @RequestParam(defaultValue = "0") page: Int,
    @RequestParam(defaultValue = "20") size: Int,
    @RequestParam(required = false) sort: String?,
    @RequestParam(required = false) status: String?
): PageResponse<User> {
    return userService.findAll(page, size, sort, status)
}
```

**6. HATEOAS (Hypermedia):**

*Теория:* Включение ссылок на связанные ресурсы в ответ. Клиент может навигироваться по API, следуя ссылкам, не hardcoding URLs. Опционально, но улучшает discoverability API.

```kotlin
// Пример HATEOAS-совместимого ответа
{
  "id": 123,
  "name": "John Doe",
  "email": "john@example.com",
  "_links": {
    "self": { "href": "/users/123" },
    "orders": { "href": "/users/123/orders" },
    "profile": { "href": "/users/123/profile" }
  }
}
```

**7. Безопасность:**

*Теория:* API должен быть защищён. HTTPS обязателен. Authentication (кто вы) через JWT/OAuth2. Authorization (что можете) через roles/permissions. Rate limiting для защиты от abuse.

**Основные практики:**
- **HTTPS only** - всегда используйте TLS
- **Authentication** - JWT tokens, OAuth2
- **Authorization** - role-based access control (RBAC)
- **Rate limiting** - ограничение запросов (например, 100 req/min)
- **Input validation** - валидация всех входных данных
- **CORS** - правильная настройка Cross-Origin Resource Sharing

```kotlin
// Современная конфигурация безопасности (Spring Security 5.7+)
@Configuration
@EnableWebSecurity
class SecurityConfig {

    @Bean
    fun securityFilterChain(http: HttpSecurity): SecurityFilterChain {
        http
            .csrf { it.disable() }
            .authorizeHttpRequests {
                it.requestMatchers("/api/v1/public/**").permitAll()
                    .requestMatchers("/api/v1/admin/**").hasRole("ADMIN")
                    .anyRequest().authenticated()
            }
            .oauth2ResourceServer { it.jwt {} }

        return http.build()
    }
}
```

**8. Кеширование:**

*Теория:* Используйте HTTP кеширование для улучшения производительности. Заголовки `Cache-Control`, `ETag`, `Last-Modified` позволяют клиентам и CDN кешировать ответы.

```kotlin
// Cache headers
@GetMapping("/users/{id}")
fun getUser(@PathVariable id: Long): ResponseEntity<User> {
    val user = userService.findById(id)
    return ResponseEntity.ok()
        .cacheControl(CacheControl.maxAge(1, TimeUnit.HOURS))
        .eTag(user.version.toString())
        .body(user)
}
```

**9. Идемпотентность:**

*Теория:* Идемпотентные операции (GET, PUT, DELETE) можно безопасно повторять: повторный запрос не меняет результат дальше первого успешного применения. POST по умолчанию не идемпотентен. Для критичных POST операций используйте idempotency keys для предотвращения дублирования.

```kotlin
// Idempotency key для POST
@PostMapping("/payments")
fun createPayment(
    @RequestHeader("Idempotency-Key") idempotencyKey: String,
    @RequestBody payment: Payment
): Payment {
    // Проверить, не был ли уже обработан этот idempotencyKey
    return paymentService.createOrGet(idempotencyKey, payment)
}
```

**10. Документация:**

*Теория:* API без документации бесполезен. Используйте OpenAPI/Swagger для автоматической генерации документации из кода. Включайте примеры запросов/ответов, описания ошибок.

```kotlin
// OpenAPI annotations
@Operation(summary = "Get user by ID", description = "Returns a single user")
@ApiResponses(
    value = [
        ApiResponse(responseCode = "200", description = "User found"),
        ApiResponse(responseCode = "404", description = "User not found")
    ]
)
@GetMapping("/users/{id}")
fun getUser(@PathVariable id: Long): User
```

**Чеклист лучших практик:**

✅ Используйте существительные, не глаголы в URL
✅ Используйте множественное число для коллекций
✅ Правильные HTTP методы и коды статуса
✅ Версионирование API (v1, v2)
✅ Пагинация для больших коллекций
✅ Стандартизированный формат ошибок
✅ HTTPS only
✅ Authentication и Authorization
✅ Rate limiting
✅ Input validation
✅ Кеширование (Cache-Control, ETag)
✅ Документация (OpenAPI/Swagger)

## Answer (EN)

### Requirements

**Functional:**
- Support CRUD operations on resources via RESTful endpoints.
- Correct usage of HTTP methods and status codes.
- Standardized error handling.
- Support pagination, filtering, and sorting for collections.
- API versioning to evolve contracts.
- Secure access to the API (authentication, authorization).
- Support caching and idempotency where appropriate.
- API documentation (e.g., OpenAPI/Swagger).

**Non-functional:**
- Scalability and extensibility of the API.
- Reliability and predictable behavior (method semantics, statuses).
- Good developer experience (clean URLs, error schema, docs).
- Performance (caching, pagination).
- Security (TLS, rate limiting, input validation).

### Architecture

- Client-server architecture with clear separation of concerns.
- Resource-oriented model: each business entity as a resource with a unique URI.
- Use of standard HTTP methods and codes as the interaction contract.
- Routing/controller layer mapping HTTP requests to domain services.
- Centralized error handler returning a unified error format.
- Integration with auth systems (JWT, OAuth2).
- Use of caching mechanisms (HTTP headers, CDN) and rate limiting at API gateway or proxy level.

**REST API Theory:**
REST (Representational State Transfer) is an architectural style for distributed systems, based on resources, standard HTTP methods, and stateless communication. Good API design is critical for maintainability, scalability, and developer experience.

**REST Principles:**
1. **Resources** - everything is a resource (users, orders, products)
2. **HTTP Methods** - standard verbs (GET, POST, PUT, DELETE)
3. **Stateless** - each request contains all necessary information
4. **Client-Server** - separation of concerns
5. **Cacheable** - responses can be cached
6. **Uniform Interface** - consistent resource identification

**1. Resource Naming:**

*Theory:* Use nouns, not verbs. HTTP methods are already verbs. Use plural for collections. Use nested resources for relationships.

✅ **Correct:**
```text
GET    /users             # Get all users
POST   /users             # Create user
GET    /users/123         # Get specific user
PUT    /users/123         # Update user
DELETE /users/123         # Delete user
GET    /users/123/orders  # User's orders (nested resource)
```

❌ **Incorrect:**
```text
GET  /getUsers
POST /createUser
POST /updateUser/123
```

```kotlin
// Correct endpoint structure
@RestController
@RequestMapping("/api/v1/users")
class UserController(private val userService: UserService) {
    @GetMapping
    fun getAll(): List<User> = userService.findAll()

    @GetMapping("/{id}")
    fun getOne(@PathVariable id: Long): User = userService.findById(id)

    @PostMapping
    fun create(@RequestBody user: User): ResponseEntity<User> {
        val created = userService.create(user)
        return ResponseEntity.status(HttpStatus.CREATED).body(created)
    }

    @PutMapping("/{id}")
    fun update(@PathVariable id: Long, @RequestBody user: User): User =
        userService.update(id, user)

    @DeleteMapping("/{id}")
    fun delete(@PathVariable id: Long): ResponseEntity<Void> {
        userService.delete(id)
        return ResponseEntity.noContent().build()
    }
}
```

**2. HTTP Methods:**

*Theory:* Each HTTP method has defined semantics. GET - safe and idempotent. POST - not idempotent (commonly used for operations that may have side effects, such as creating resources). PUT/DELETE - idempotent (repeated call results in the same observed state). PATCH is generally not guaranteed to be idempotent.

| Method | Purpose | Idempotent | Safe | `Request` Body | `Response` Body |
|--------|---------|------------|------|--------------|---------------|
| GET | Retrieve resource | Yes | Yes | Typically No | Yes |
| POST | Create resource / perform command | No | No | Yes | Yes |
| PUT | Replace resource | Yes | No | Yes | Yes |
| PATCH | Partial update | Not guaranteed | No | Yes | Yes |
| DELETE | Delete resource | Yes | No | Optional | Optional |

**3. HTTP Status Codes:**

*Theory:* Use correct HTTP codes to convey operation result. Clients should understand the outcome by the status code without parsing the body.

**Success (2xx):**
- `200 OK` - successful GET, PUT, PATCH
- `201 Created` - successful POST (with Location header)
- `204 No Content` - successful DELETE (and other cases with no response body)

**Client Errors (4xx):**
- `400 Bad Request` - invalid data
- `401 Unauthorized` - not authenticated
- `403 Forbidden` - no access rights
- `404 Not Found` - resource not found
- `409 Conflict` - conflict (e.g., duplicate email)
- `422 Unprocessable Entity` - validation failed
- `429 Too Many Requests` - rate limit exceeded

**Server Errors (5xx):**
- `500 Internal Server Error` - server error
- `503 ``Service`` Unavailable` - service temporarily unavailable

```kotlin
// Standardized error format
import jakarta.servlet.http.HttpServletRequest

data class ErrorResponse(
    val status: Int,
    val error: String,
    val message: String,
    val timestamp: Instant,
    val path: String,
    val details: List<String>? = null
)

@ExceptionHandler(UserNotFoundException::class)
fun handleNotFound(ex: UserNotFoundException, request: HttpServletRequest): ResponseEntity<ErrorResponse> {
    val body = ErrorResponse(
        status = HttpStatus.NOT_FOUND.value(),
        error = HttpStatus.NOT_FOUND.reasonPhrase,
        message = ex.message ?: "User not found",
        timestamp = Instant.now(),
        path = request.requestURI
    )
    return ResponseEntity.status(HttpStatus.NOT_FOUND).body(body)
}
```

**4. API Versioning:**

*Theory:* APIs evolve; breaking changes are inevitable. Versioning allows supporting existing clients while introducing new features. Three main approaches: URL path, query parameter, header.

**Approaches:**
- **URL path** (common and simple): `/api/v1/users`, `/api/v2/users`
- **Query parameter**: `/api/users?version=1`
- **Header**: `Accept: application/vnd.api.v1+json`

```kotlin
// Versioning via URL path
@RequestMapping("/api/v1/users")
class UserControllerV1

@RequestMapping("/api/v2/users")
class UserControllerV2  // New version with breaking changes
```

**5. Pagination, Filtering, Sorting:**

*Theory:* Large collections should support pagination for performance. Filtering and sorting via query parameters. Standardize the response format.

```kotlin
// Pagination and filtering
GET /users?page=0&size=20&sort=name,asc&status=active&role=admin

// Example response structure

data class PageResponse<T>(
    val content: List<T>,
    val page: Int,
    val size: Int,
    val totalElements: Long,
    val totalPages: Int
)

@GetMapping("/users")
fun getUsers(
    @RequestParam(defaultValue = "0") page: Int,
    @RequestParam(defaultValue = "20") size: Int,
    @RequestParam(required = false) sort: String?,
    @RequestParam(required = false) status: String?
): PageResponse<User> {
    return userService.findAll(page, size, sort, status)
}
```

**6. HATEOAS (Hypermedia):**

*Theory:* Include links to related resources in responses. Clients can navigate the API by following links instead of hardcoding URLs. Optional, but improves API discoverability.

```kotlin
// Example HATEOAS-style response
{
  "id": 123,
  "name": "John Doe",
  "email": "john@example.com",
  "_links": {
    "self": { "href": "/users/123" },
    "orders": { "href": "/users/123/orders" },
    "profile": { "href": "/users/123/profile" }
  }
}
```

**7. Security:**

*Theory:* API must be secured. HTTPS is mandatory. Authentication (who you are) via JWT/OAuth2. Authorization (what you can do) via roles/permissions. Rate limiting to protect from abuse.

**Core Practices:**
- **HTTPS only** - always use TLS
- **Authentication** - JWT tokens, OAuth2
- **Authorization** - role-based access control (RBAC)
- **Rate limiting** - request limits (e.g., 100 req/min)
- **Input validation** - validate all input data
- **CORS** - proper Cross-Origin Resource Sharing configuration

```kotlin
// Modern security configuration (Spring Security 5.7+)
@Configuration
@EnableWebSecurity
class SecurityConfig {

    @Bean
    fun securityFilterChain(http: HttpSecurity): SecurityFilterChain {
        http
            .csrf { it.disable() }
            .authorizeHttpRequests {
                it.requestMatchers("/api/v1/public/**").permitAll()
                    .requestMatchers("/api/v1/admin/**").hasRole("ADMIN")
                    .anyRequest().authenticated()
            }
            .oauth2ResourceServer { it.jwt {} }

        return http.build()
    }
}
```

**8. Caching:**

*Theory:* Use HTTP caching to improve performance. `Cache-Control`, `ETag`, and `Last-Modified` headers enable clients and CDNs to cache responses.

```kotlin
// Cache headers
@GetMapping("/users/{id}")
fun getUser(@PathVariable id: Long): ResponseEntity<User> {
    val user = userService.findById(id)
    return ResponseEntity.ok()
        .cacheControl(CacheControl.maxAge(1, TimeUnit.HOURS))
        .eTag(user.version.toString())
        .body(user)
}
```

**9. Idempotency:**

*Theory:* Idempotent operations (GET, PUT, DELETE) can be safely retried: subsequent identical requests do not change the state beyond the first successful one. POST is not idempotent by default. For critical POST operations, use idempotency keys to prevent duplicates.

```kotlin
// Idempotency key for POST
@PostMapping("/payments")
fun createPayment(
    @RequestHeader("Idempotency-Key") idempotencyKey: String,
    @RequestBody payment: Payment
): Payment {
    // Check if this idempotencyKey has already been processed
    return paymentService.createOrGet(idempotencyKey, payment)
}
```

**10. Documentation:**

*Theory:* An API without documentation is useless. Use OpenAPI/Swagger for automatic documentation generation from code. Include request/response examples and error descriptions.

```kotlin
// OpenAPI annotations
@Operation(summary = "Get user by ID", description = "Returns a single user")
@ApiResponses(
    value = [
        ApiResponse(responseCode = "200", description = "User found"),
        ApiResponse(responseCode = "404", description = "User not found")
    ]
)
@GetMapping("/users/{id}")
fun getUser(@PathVariable id: Long): User
```

**Best Practices Checklist:**

✅ Use nouns, not verbs in URLs
✅ Use plural for collections
✅ Correct HTTP methods and status codes
✅ API versioning (v1, v2)
✅ Pagination for large collections
✅ Standardized error format
✅ HTTPS only
✅ Authentication and Authorization
✅ Rate limiting
✅ Input validation
✅ Caching (Cache-Control, ETag)
✅ Documentation (OpenAPI/Swagger)

---

## Follow-ups

- How do you implement API rate limiting?
- What is the difference between PUT and PATCH?
- How do you handle API deprecation?

## References

- [[c-architecture-patterns]]
- "https://en.wikipedia.org/wiki/Representational_state_transfer"

## Related Questions

### Prerequisites (Easier)
- [[q-caching-strategies--system-design--medium]] - Caching patterns
- [[q-horizontal-vertical-scaling--system-design--medium]] - Scaling strategies

### Related (Same Level)
- [[q-load-balancing-strategies--system-design--medium]] - Load balancing
- [[q-message-queues-event-driven--system-design--medium]] - Async communication

### Advanced (Harder)
- [[q-microservices-vs-monolith--system-design--hard]] - Architecture patterns
- [[q-cap-theorem-distributed-systems--system-design--hard]] - Distributed systems theory

## Дополнительные Вопросы (RU)

- Как реализовать rate limiting в API?
- В чем разница между PUT и PATCH?
- Как правильно организовать процесс деприкации и удаления старых версий API?

## Связанные Вопросы (RU)

### Предварительные (проще)
- [[q-caching-strategies--system-design--medium]] - Паттерны кеширования
- [[q-horizontal-vertical-scaling--system-design--medium]] - Стратегии масштабирования

### Связанные (средний уровень)
- [[q-load-balancing-strategies--system-design--medium]] - Балансировка нагрузки
- [[q-message-queues-event-driven--system-design--medium]] - Асинхронное взаимодействие

### Продвинутые (сложнее)
- [[q-microservices-vs-monolith--system-design--hard]] - Архитектурные подходы
- [[q-cap-theorem-distributed-systems--system-design--hard]] - Теория распределенных систем

## Ссылки (RU)
