---
id: sysdes-003
title: "REST API Design Best Practices / Лучшие практики проектирования REST API"
aliases: ["REST API Design", "Проектирование REST API"]
topic: system-design
subtopics: [api-design, http, rest-api, web-services]
question_kind: system-design
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-system-design
related: [c-rest-api, q-caching-strategies--system-design--medium, q-microservices-vs-monolith--system-design--hard]
created: 2025-10-12
updated: 2025-01-25
tags: [api-design, difficulty/medium, http, rest-api, system-design]
sources: [https://en.wikipedia.org/wiki/Representational_state_transfer]
date created: Sunday, October 12th 2025, 8:38:24 pm
date modified: Saturday, November 1st 2025, 5:43:37 pm
---

# Вопрос (RU)
> Каковы лучшие практики проектирования RESTful API? Как структурировать endpoints, обрабатывать ошибки и обеспечивать качество API?

# Question (EN)
> What are the best practices for designing RESTful APIs? How do you structure endpoints, handle errors, and ensure API quality?

---

## Ответ (RU)

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
```
GET    /users          # Получить всех пользователей
POST   /users          # Создать пользователя
GET    /users/123      # Получить конкретного пользователя
PUT    /users/123      # Обновить пользователя
DELETE /users/123      # Удалить пользователя
GET    /users/123/orders  # Заказы пользователя (вложенный ресурс)
```

❌ **Неправильно:**
```
GET  /getUsers
POST /createUser
POST /updateUser/123
```

```kotlin
// Правильная структура endpoints
@RestController
@RequestMapping("/api/v1/users")
class UserController(private val userService: UserService) {
    @GetMapping fun getAll() = userService.findAll()
    @GetMapping("/{id}") fun getOne(@PathVariable id: Long) = userService.findById(id)
    @PostMapping fun create(@RequestBody user: User) = userService.create(user)
    @PutMapping("/{id}") fun update(@PathVariable id: Long, @RequestBody user: User) = userService.update(id, user)
    @DeleteMapping("/{id}") fun delete(@PathVariable id: Long) = userService.delete(id)
}
```

**2. HTTP методы:**

*Теория:* Каждый HTTP метод имеет семантику. GET - безопасный (safe) и идемпотентный. POST - не идемпотентный (создаёт новый ресурс каждый раз). PUT/DELETE - идемпотентные (повторный вызов даёт тот же результат).

| Метод | Назначение | Идемпотентный | Safe | Request Body | Response Body |
|-------|-----------|---------------|------|--------------|---------------|
| GET | Получить ресурс | Да | Да | Нет | Да |
| POST | Создать ресурс | Нет | Нет | Да | Да |
| PUT | Заменить ресурс | Да | Нет | Да | Да |
| PATCH | Частичное обновление | Нет | Нет | Да | Да |
| DELETE | Удалить ресурс | Да | Нет | Нет | Нет |

**3. HTTP коды статуса:**

*Теория:* Используйте правильные HTTP коды для передачи результата операции. Клиент должен понимать результат по коду, не парсируя body.

**Успешные (2xx):**
- `200 OK` - успешный GET, PUT, PATCH
- `201 Created` - успешный POST (с заголовком Location)
- `204 No Content` - успешный DELETE

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
- `503 Service Unavailable` - сервис временно недоступен

```kotlin
// Стандартизированный формат ошибок
data class ErrorResponse(
    val status: Int,
    val error: String,
    val message: String,
    val timestamp: Instant,
    val path: String,
    val details: List<String>? = null
)

@ExceptionHandler(UserNotFoundException::class)
fun handleNotFound(ex: UserNotFoundException): ResponseEntity<ErrorResponse> {
    return ResponseEntity.status(404).body(
        ErrorResponse(
            status = 404,
            error = "Not Found",
            message = ex.message ?: "User not found",
            timestamp = Instant.now(),
            path = request.requestURI
        )
    )
}
```

**4. Версионирование API:**

*Теория:* API эволюционирует, breaking changes неизбежны. Версионирование позволяет поддерживать старых клиентов при внедрении новых фич. Три основных подхода: URL path, query parameter, header.

**Подходы:**
- **URL path** (рекомендуется): `/api/v1/users`, `/api/v2/users`
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

*Теория:* Включение ссылок на связанные ресурсы в ответ. Клиент может навигироваться по API, следуя ссылкам, не hardcoding URLs. Опционально, но улучшает discoverable API.

```kotlin
// HATEOAS response
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
// JWT Authentication
@Configuration
class SecurityConfig : WebSecurityConfigurerAdapter() {
    override fun configure(http: HttpSecurity) {
        http
            .csrf().disable()
            .authorizeRequests()
            .antMatchers("/api/v1/public/**").permitAll()
            .antMatchers("/api/v1/admin/**").hasRole("ADMIN")
            .anyRequest().authenticated()
            .and()
            .oauth2ResourceServer().jwt()
    }
}
```

**8. Кеширование:**

*Теория:* Используйте HTTP кеширование для улучшения производительности. `Cache-Control`, `ETag`, `Last-Modified` headers позволяют клиентам и CDN кешировать ответы.

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

*Теория:* Идемпотентные операции (GET, PUT, DELETE) можно безопасно повторять. POST не идемпотентен. Для критичных POST операций используйте idempotency keys для предотвращения дублирования.

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
    ApiResponse(responseCode = "200", description = "User found"),
    ApiResponse(responseCode = "404", description = "User not found")
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

**REST API Theory:**
REST (Representational State Transfer) - architectural style for distributed systems, based on resources, standard HTTP methods, and stateless communication. Good API design is critical for maintainability, scalability, and developer experience.

**REST Principles:**
1. **Resources** - everything is a resource (users, orders, products)
2. **HTTP Methods** - standard verbs (GET, POST, PUT, DELETE)
3. **Stateless** - each request contains all necessary information
4. **Client-Server** - separation of concerns
5. **Cacheable** - responses can be cached
6. **Uniform Interface** - consistent resource identification

**1. Resource Naming:**

*Theory:* Use nouns, not verbs. HTTP methods are already verbs. Use plural for collections. Nested resources for relationships.

✅ **Correct:**
```
GET    /users          # Get all users
POST   /users          # Create user
GET    /users/123      # Get specific user
PUT    /users/123      # Update user
DELETE /users/123      # Delete user
GET    /users/123/orders  # User's orders (nested resource)
```

❌ **Incorrect:**
```
GET  /getUsers
POST /createUser
POST /updateUser/123
```

```kotlin
// Correct endpoint structure
@RestController
@RequestMapping("/api/v1/users")
class UserController(private val userService: UserService) {
    @GetMapping fun getAll() = userService.findAll()
    @GetMapping("/{id}") fun getOne(@PathVariable id: Long) = userService.findById(id)
    @PostMapping fun create(@RequestBody user: User) = userService.create(user)
    @PutMapping("/{id}") fun update(@PathVariable id: Long, @RequestBody user: User) = userService.update(id, user)
    @DeleteMapping("/{id}") fun delete(@PathVariable id: Long) = userService.delete(id)
}
```

**2. HTTP Methods:**

*Theory:* Each HTTP method has semantics. GET - safe and idempotent. POST - not idempotent (creates new resource each time). PUT/DELETE - idempotent (repeated call gives same result).

| Method | Purpose | Idempotent | Safe | Request Body | Response Body |
|--------|---------|------------|------|--------------|---------------|
| GET | Retrieve resource | Yes | Yes | No | Yes |
| POST | Create resource | No | No | Yes | Yes |
| PUT | Replace resource | Yes | No | Yes | Yes |
| PATCH | Partial update | No | No | Yes | Yes |
| DELETE | Delete resource | Yes | No | No | No |

**3. HTTP Status Codes:**

*Theory:* Use correct HTTP codes to convey operation result. Client should understand result by code, not parsing body.

**Success (2xx):**
- `200 OK` - successful GET, PUT, PATCH
- `201 Created` - successful POST (with Location header)
- `204 No Content` - successful DELETE

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
- `503 Service Unavailable` - service temporarily unavailable

```kotlin
// Standardized error format
data class ErrorResponse(
    val status: Int,
    val error: String,
    val message: String,
    val timestamp: Instant,
    val path: String,
    val details: List<String>? = null
)

@ExceptionHandler(UserNotFoundException::class)
fun handleNotFound(ex: UserNotFoundException): ResponseEntity<ErrorResponse> {
    return ResponseEntity.status(404).body(
        ErrorResponse(
            status = 404,
            error = "Not Found",
            message = ex.message ?: "User not found",
            timestamp = Instant.now(),
            path = request.requestURI
        )
    )
}
```

**4. API Versioning:**

*Theory:* API evolves, breaking changes inevitable. Versioning allows supporting old clients while introducing new features. Three main approaches: URL path, query parameter, header.

**Approaches:**
- **URL path** (recommended): `/api/v1/users`, `/api/v2/users`
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

*Theory:* Large collections should support pagination for performance. Filtering and sorting via query parameters. Standardize response format.

```kotlin
// Pagination and filtering
GET /users?page=0&size=20&sort=name,asc&status=active&role=admin

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

*Theory:* Including links to related resources in response. Client can navigate API by following links, not hardcoding URLs. Optional, but improves discoverable API.

```kotlin
// HATEOAS response
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

*Theory:* API must be secured. HTTPS mandatory. Authentication (who you are) via JWT/OAuth2. Authorization (what you can do) via roles/permissions. Rate limiting to protect from abuse.

**Core Practices:**
- **HTTPS only** - always use TLS
- **Authentication** - JWT tokens, OAuth2
- **Authorization** - role-based access control (RBAC)
- **Rate limiting** - request limits (e.g., 100 req/min)
- **Input validation** - validate all input data
- **CORS** - proper Cross-Origin Resource Sharing configuration

```kotlin
// JWT Authentication
@Configuration
class SecurityConfig : WebSecurityConfigurerAdapter() {
    override fun configure(http: HttpSecurity) {
        http
            .csrf().disable()
            .authorizeRequests()
            .antMatchers("/api/v1/public/**").permitAll()
            .antMatchers("/api/v1/admin/**").hasRole("ADMIN")
            .anyRequest().authenticated()
            .and()
            .oauth2ResourceServer().jwt()
    }
}
```

**8. Caching:**

*Theory:* Use HTTP caching to improve performance. `Cache-Control`, `ETag`, `Last-Modified` headers allow clients and CDN to cache responses.

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

*Theory:* Idempotent operations (GET, PUT, DELETE) can be safely repeated. POST not idempotent. For critical POST operations use idempotency keys to prevent duplication.

```kotlin
// Idempotency key for POST
@PostMapping("/payments")
fun createPayment(
    @RequestHeader("Idempotency-Key") idempotencyKey: String,
    @RequestBody payment: Payment
): Payment {
    // Check if this idempotencyKey was already processed
    return paymentService.createOrGet(idempotencyKey, payment)
}
```

**10. Documentation:**

*Theory:* API without documentation is useless. Use OpenAPI/Swagger for automatic documentation generation from code. Include request/response examples, error descriptions.

```kotlin
// OpenAPI annotations
@Operation(summary = "Get user by ID", description = "Returns a single user")
@ApiResponses(
    ApiResponse(responseCode = "200", description = "User found"),
    ApiResponse(responseCode = "404", description = "User not found")
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
