---
id: 20251012-300007
title: "REST API Design Best Practices / Лучшие практики проектирования REST API"
topic: system-design
difficulty: medium
status: draft
created: 2025-10-12
tags:
  - system-design
  - rest-api
  - api-design
  - http
moc: moc-system-design
related: [q-horizontal-vertical-scaling--system-design--medium, q-sql-nosql-databases--system-design--medium, q-caching-strategies--system-design--medium]
  - q-api-versioning-strategies--system-design--medium
  - q-graphql-vs-rest--system-design--medium
  - q-api-rate-limiting--system-design--hard
subtopics:
  - rest-api
  - api-design
  - http
  - web-services
---
# Question (EN)
> What are the best practices for designing RESTful APIs? How do you structure endpoints, handle errors, and ensure API quality?

# Вопрос (RU)
> Каковы лучшие практики проектирования RESTful API? Как структурировать endpoints, обрабатывать ошибки и обеспечивать качество API?

---

## Answer (EN)

Designing a good REST API is crucial for building maintainable, scalable, and developer-friendly services. Poor API design leads to confusion, increased support burden, and difficult-to-evolve systems.



### REST Principles

**REST (Representational State Transfer)** is an architectural style based on:

1. **Resources** - Everything is a resource (users, orders, products)
2. **HTTP Methods** - Standard verbs (GET, POST, PUT, DELETE)
3. **Stateless** - Each request contains all needed information
4. **Client-Server** - Separation of concerns
5. **Cacheable** - Responses can be cached
6. **Uniform Interface** - Consistent resource identification

---

### 1. Resource Naming Conventions

### Use Nouns, Not Verbs

 **Bad:**
```
GET  /getUsers
POST /createUser
POST /updateUser/123
POST /deleteUser/123
```

 **Good:**
```
GET    /users          # Get all users
POST   /users          # Create user
GET    /users/123      # Get specific user
PUT    /users/123      # Update user
DELETE /users/123      # Delete user
```

### Use Plural Nouns

 **Bad:**
```
/user/123
/order/456
```

 **Good:**
```
/users/123
/orders/456
```

### Nested Resources for Relationships

```
GET /users/123/orders           # Get orders for user 123
GET /users/123/orders/456       # Get specific order for user
POST /users/123/orders          # Create order for user
GET /orders/456/items           # Get items in order 456
```

**Implementation:**
```kotlin
@RestController
@RequestMapping("/api/v1")
class UserController(private val userService: UserService) {

    // GET /api/v1/users
    @GetMapping("/users")
    suspend fun getAllUsers(
        @RequestParam(defaultValue = "0") page: Int,
        @RequestParam(defaultValue = "20") size: Int,
        @RequestParam(required = false) sort: String?
    ): Page<UserDto> {
        return userService.findAll(PageRequest.of(page, size, parseSort(sort)))
    }

    // GET /api/v1/users/123
    @GetMapping("/users/{id}")
    suspend fun getUser(@PathVariable id: Long): UserDto {
        return userService.findById(id) ?: throw UserNotFoundException(id)
    }

    // POST /api/v1/users
    @PostMapping("/users")
    @ResponseStatus(HttpStatus.CREATED)
    suspend fun createUser(@Valid @RequestBody request: CreateUserRequest): UserDto {
        return userService.create(request)
    }

    // PUT /api/v1/users/123
    @PutMapping("/users/{id}")
    suspend fun updateUser(
        @PathVariable id: Long,
        @Valid @RequestBody request: UpdateUserRequest
    ): UserDto {
        return userService.update(id, request)
    }

    // PATCH /api/v1/users/123
    @PatchMapping("/users/{id}")
    suspend fun partialUpdateUser(
        @PathVariable id: Long,
        @RequestBody updates: Map<String, Any>
    ): UserDto {
        return userService.partialUpdate(id, updates)
    }

    // DELETE /api/v1/users/123
    @DeleteMapping("/users/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    suspend fun deleteUser(@PathVariable id: Long) {
        userService.delete(id)
    }

    // GET /api/v1/users/123/orders
    @GetMapping("/users/{userId}/orders")
    suspend fun getUserOrders(@PathVariable userId: Long): List<OrderDto> {
        return userService.getOrders(userId)
    }
}
```

---

### 2. HTTP Methods Correctly

| Method | Purpose | Idempotent | Safe | Request Body | Response Body |
|--------|---------|------------|------|--------------|---------------|
| **GET** | Retrieve resource |  Yes |  Yes |  No |  Yes |
| **POST** | Create resource |  No |  No |  Yes |  Yes |
| **PUT** | Replace resource |  Yes |  No |  Yes |  Yes |
| **PATCH** | Partial update |  No |  No |  Yes |  Yes |
| **DELETE** | Delete resource |  Yes |  No |  No |  No |

**Idempotent** = Multiple identical requests have same effect as single request

```kotlin
// POST - Not idempotent (creates new resource each time)
POST /users
{
  "name": "John",
  "email": "john@example.com"
}
Response: 201 Created
Location: /users/123

// PUT - Idempotent (same request = same result)
PUT /users/123
{
  "name": "John Updated",
  "email": "john@example.com"
}
Response: 200 OK

// PATCH - Partial update
PATCH /users/123
{
  "name": "John Updated"  // Only update name
}
Response: 200 OK

// DELETE - Idempotent (deleting already deleted = same result)
DELETE /users/123
Response: 204 No Content
```

---

### 3. Status Codes

Use appropriate HTTP status codes:

### Success (2xx)

```kotlin
@RestController
class OrderController(private val orderService: OrderService) {

    @GetMapping("/orders/{id}")
    suspend fun getOrder(@PathVariable id: Long): ResponseEntity<OrderDto> {
        val order = orderService.findById(id)
        return if (order != null) {
            ResponseEntity.ok(order)  // 200 OK
        } else {
            ResponseEntity.notFound().build()  // 404 Not Found
        }
    }

    @PostMapping("/orders")
    suspend fun createOrder(@RequestBody request: CreateOrderRequest): ResponseEntity<OrderDto> {
        val order = orderService.create(request)
        return ResponseEntity
            .status(HttpStatus.CREATED)  // 201 Created
            .header("Location", "/orders/${order.id}")
            .body(order)
    }

    @DeleteMapping("/orders/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)  // 204 No Content
    suspend fun deleteOrder(@PathVariable id: Long) {
        orderService.delete(id)
    }

    @PutMapping("/orders/{id}")
    suspend fun updateOrder(
        @PathVariable id: Long,
        @RequestBody request: UpdateOrderRequest
    ): ResponseEntity<OrderDto> {
        val order = orderService.update(id, request)
        return ResponseEntity.ok(order)  // 200 OK
    }
}
```

### Client Errors (4xx)

```kotlin
@RestControllerAdvice
class GlobalExceptionHandler {

    @ExceptionHandler(ResourceNotFoundException::class)
    fun handleNotFound(e: ResourceNotFoundException): ResponseEntity<ErrorResponse> {
        return ResponseEntity
            .status(HttpStatus.NOT_FOUND)  // 404
            .body(ErrorResponse(
                status = 404,
                error = "Not Found",
                message = e.message,
                timestamp = Instant.now()
            ))
    }

    @ExceptionHandler(MethodArgumentNotValidException::class)
    fun handleValidationError(e: MethodArgumentNotValidException): ResponseEntity<ErrorResponse> {
        val errors = e.bindingResult.fieldErrors.map {
            FieldError(it.field, it.defaultMessage ?: "Invalid value")
        }
        return ResponseEntity
            .status(HttpStatus.BAD_REQUEST)  // 400
            .body(ErrorResponse(
                status = 400,
                error = "Validation Failed",
                message = "Invalid request parameters",
                errors = errors,
                timestamp = Instant.now()
            ))
    }

    @ExceptionHandler(UnauthorizedException::class)
    fun handleUnauthorized(e: UnauthorizedException): ResponseEntity<ErrorResponse> {
        return ResponseEntity
            .status(HttpStatus.UNAUTHORIZED)  // 401
            .body(ErrorResponse(
                status = 401,
                error = "Unauthorized",
                message = "Authentication required",
                timestamp = Instant.now()
            ))
    }

    @ExceptionHandler(ForbiddenException::class)
    fun handleForbidden(e: ForbiddenException): ResponseEntity<ErrorResponse> {
        return ResponseEntity
            .status(HttpStatus.FORBIDDEN)  // 403
            .body(ErrorResponse(
                status = 403,
                error = "Forbidden",
                message = "Access denied",
                timestamp = Instant.now()
            ))
    }

    @ExceptionHandler(ConflictException::class)
    fun handleConflict(e: ConflictException): ResponseEntity<ErrorResponse> {
        return ResponseEntity
            .status(HttpStatus.CONFLICT)  // 409
            .body(ErrorResponse(
                status = 409,
                error = "Conflict",
                message = e.message,
                timestamp = Instant.now()
            ))
    }
}

data class ErrorResponse(
    val status: Int,
    val error: String,
    val message: String?,
    val errors: List<FieldError>? = null,
    val timestamp: Instant,
    val path: String? = null
)

data class FieldError(
    val field: String,
    val message: String
)
```

### Server Errors (5xx)

```kotlin
@ExceptionHandler(Exception::class)
fun handleInternalError(e: Exception): ResponseEntity<ErrorResponse> {
    logger.error("Internal server error", e)
    return ResponseEntity
        .status(HttpStatus.INTERNAL_SERVER_ERROR)  // 500
        .body(ErrorResponse(
            status = 500,
            error = "Internal Server Error",
            message = "An unexpected error occurred",
            timestamp = Instant.now()
        ))
}

@ExceptionHandler(ServiceUnavailableException::class)
fun handleServiceUnavailable(e: ServiceUnavailableException): ResponseEntity<ErrorResponse> {
    return ResponseEntity
        .status(HttpStatus.SERVICE_UNAVAILABLE)  // 503
        .header("Retry-After", "60")
        .body(ErrorResponse(
            status = 503,
            error = "Service Unavailable",
            message = "Service temporarily unavailable",
            timestamp = Instant.now()
        ))
}
```

**Common Status Codes:**
```
200 OK              - Success (GET, PUT, PATCH)
201 Created         - Resource created (POST)
204 No Content      - Success with no body (DELETE)
400 Bad Request     - Invalid input
401 Unauthorized    - Authentication required
403 Forbidden       - No permission
404 Not Found       - Resource doesn't exist
409 Conflict        - Duplicate/conflict (e.g., email exists)
422 Unprocessable   - Validation failed
429 Too Many Requests - Rate limit exceeded
500 Internal Error  - Server error
503 Service Unavailable - Temporary outage
```

---

### 4. Filtering, Sorting, Pagination

```kotlin
// GET /products?category=electronics&minPrice=100&maxPrice=500&sort=price,desc&page=0&size=20

@GetMapping("/products")
suspend fun getProducts(
    @RequestParam(required = false) category: String?,
    @RequestParam(required = false) minPrice: BigDecimal?,
    @RequestParam(required = false) maxPrice: BigDecimal?,
    @RequestParam(required = false) search: String?,
    @RequestParam(defaultValue = "createdAt,desc") sort: String,
    @RequestParam(defaultValue = "0") page: Int,
    @RequestParam(defaultValue = "20") size: Int
): PagedResponse<ProductDto> {
    
    val filters = ProductFilters(
        category = category,
        minPrice = minPrice,
        maxPrice = maxPrice,
        search = search
    )
    
    val pageable = PageRequest.of(page, size, parseSort(sort))
    val products = productService.findAll(filters, pageable)
    
    return PagedResponse(
        data = products.content,
        page = products.number,
        size = products.size,
        totalElements = products.totalElements,
        totalPages = products.totalPages,
        hasNext = products.hasNext(),
        hasPrevious = products.hasPrevious()
    )
}

data class PagedResponse<T>(
    val data: List<T>,
    val page: Int,
    val size: Int,
    val totalElements: Long,
    val totalPages: Int,
    val hasNext: Boolean,
    val hasPrevious: Boolean
)
```

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "Laptop",
      "category": "electronics",
      "price": 999.99
    }
  ],
  "page": 0,
  "size": 20,
  "totalElements": 156,
  "totalPages": 8,
  "hasNext": true,
  "hasPrevious": false,
  "_links": {
    "self": "/products?page=0&size=20",
    "next": "/products?page=1&size=20",
    "last": "/products?page=7&size=20"
  }
}
```

---

### 5. Versioning

**Option 1: URL Versioning (Most Common)**
```kotlin
@RestController
@RequestMapping("/api/v1/users")
class UserControllerV1 { /* ... */ }

@RestController
@RequestMapping("/api/v2/users")
class UserControllerV2 { /* ... */ }
```

**Option 2: Header Versioning**
```kotlin
@GetMapping("/users", headers = ["API-Version=1"])
suspend fun getUsersV1(): List<UserDtoV1>

@GetMapping("/users", headers = ["API-Version=2"])
suspend fun getUsersV2(): List<UserDtoV2>
```

**Option 3: Accept Header**
```kotlin
@GetMapping("/users", produces = ["application/vnd.company.v1+json"])
suspend fun getUsersV1(): List<UserDtoV1>

@GetMapping("/users", produces = ["application/vnd.company.v2+json"])
suspend fun getUsersV2(): List<UserDtoV2>
```

---

### 6. Security Best Practices

```kotlin
@Configuration
@EnableWebSecurity
class SecurityConfig {

    @Bean
    fun securityFilterChain(http: HttpSecurity): SecurityFilterChain {
        http
            .csrf().disable()  // For APIs, use tokens instead
            .cors().and()
            .authorizeHttpRequests { auth ->
                auth
                    .requestMatchers("/api/v1/public/**").permitAll()
                    .requestMatchers("/api/v1/users/**").hasRole("USER")
                    .requestMatchers("/api/v1/admin/**").hasRole("ADMIN")
                    .anyRequest().authenticated()
            }
            .oauth2ResourceServer { oauth2 ->
                oauth2.jwt()  // JWT token validation
            }
        return http.build()
    }
}

// Use HTTPS only
@Configuration
class HttpsConfig {
    @Bean
    fun servletContainer(): ServletWebServerFactory {
        val tomcat = TomcatServletWebServerFactory()
        tomcat.addAdditionalTomcatConnectors(createHttpsConnector())
        return tomcat
    }
}

// Rate limiting
@RestController
class RateLimitedController {
    
    @GetMapping("/api/v1/data")
    @RateLimit(requests = 100, per = "1m")  // 100 requests per minute
    suspend fun getData(): DataResponse {
        // ...
    }
}
```

---

### 7. Documentation (OpenAPI/Swagger)

```kotlin
@Configuration
class OpenApiConfig {
    
    @Bean
    fun customOpenAPI(): OpenAPI {
        return OpenAPI()
            .info(Info()
                .title("E-commerce API")
                .version("v1.0.0")
                .description("REST API for e-commerce platform")
                .contact(Contact()
                    .name("API Support")
                    .email("support@example.com")
                )
            )
            .servers(listOf(
                Server().url("https://api.example.com").description("Production"),
                Server().url("https://staging-api.example.com").description("Staging")
            ))
    }
}

@RestController
@Tag(name = "Users", description = "User management APIs")
class UserController {

    @Operation(
        summary = "Get user by ID",
        description = "Returns a single user by their unique identifier"
    )
    @ApiResponses(value = [
        ApiResponse(responseCode = "200", description = "User found"),
        ApiResponse(responseCode = "404", description = "User not found"),
        ApiResponse(responseCode = "401", description = "Unauthorized")
    ])
    @GetMapping("/users/{id}")
    suspend fun getUser(
        @Parameter(description = "User ID", required = true)
        @PathVariable id: Long
    ): UserDto {
        return userService.findById(id) ?: throw UserNotFoundException(id)
    }
}
```

---

### 8. HATEOAS (Hypermedia)

```kotlin
data class UserDto(
    val id: Long,
    val name: String,
    val email: String,
    val _links: Map<String, Link>
)

data class Link(
    val href: String,
    val method: String = "GET"
)

@GetMapping("/users/{id}")
suspend fun getUser(@PathVariable id: Long): UserDto {
    val user = userService.findById(id) ?: throw UserNotFoundException(id)
    
    return UserDto(
        id = user.id,
        name = user.name,
        email = user.email,
        _links = mapOf(
            "self" to Link("/api/v1/users/${user.id}"),
            "orders" to Link("/api/v1/users/${user.id}/orders"),
            "update" to Link("/api/v1/users/${user.id}", "PUT"),
            "delete" to Link("/api/v1/users/${user.id}", "DELETE")
        )
    )
}
```

---

### 9. Caching Headers

```kotlin
@GetMapping("/products/{id}")
suspend fun getProduct(@PathVariable id: Long): ResponseEntity<ProductDto> {
    val product = productService.findById(id) ?: return ResponseEntity.notFound().build()
    
    return ResponseEntity.ok()
        .cacheControl(CacheControl.maxAge(1, TimeUnit.HOURS))  // Cache for 1 hour
        .eTag(product.version.toString())  // ETag for conditional requests
        .lastModified(product.updatedAt.toEpochMilli())
        .body(product)
}

// Client sends: If-None-Match: "v123"
// Server responds: 304 Not Modified (if ETag matches)
```

---

### 10. Bulk Operations

```kotlin
// Batch create
@PostMapping("/users/batch")
suspend fun createUsers(@RequestBody users: List<CreateUserRequest>): BatchResponse<UserDto> {
    val results = users.map { request ->
        try {
            val user = userService.create(request)
            BatchResult.Success(user)
        } catch (e: Exception) {
            BatchResult.Failure(request.email, e.message)
        }
    }
    
    return BatchResponse(
        successful = results.filterIsInstance<BatchResult.Success<UserDto>>().map { it.data },
        failed = results.filterIsInstance<BatchResult.Failure>()
    )
}

data class BatchResponse<T>(
    val successful: List<T>,
    val failed: List<BatchResult.Failure>
)

sealed class BatchResult<T> {
    data class Success<T>(val data: T) : BatchResult<T>()
    data class Failure<T>(val identifier: String, val error: String?) : BatchResult<T>()
}
```

---

### Key Takeaways

1. **Use nouns for resources**, not verbs
2. **Plural nouns** for collections (/users, /orders)
3. **HTTP methods correctly** - GET (read), POST (create), PUT (replace), PATCH (update), DELETE
4. **Appropriate status codes** - 2xx success, 4xx client error, 5xx server error
5. **Version your APIs** - /api/v1/, /api/v2/
6. **Pagination** for large collections
7. **Filter and sort** with query parameters
8. **Consistent error responses** with proper structure
9. **Document with OpenAPI/Swagger**
10. **Security** - HTTPS, authentication, rate limiting

---

## Ответ (RU)

Проектирование хорошего REST API критически важно для построения поддерживаемых, масштабируемых и удобных для разработчиков сервисов.



### Принципы REST

**REST (Representational State Transfer)** - архитектурный стиль, основанный на:

1. **Ресурсы** - Всё является ресурсом (пользователи, заказы, продукты)
2. **HTTP методы** - Стандартные глаголы (GET, POST, PUT, DELETE)
3. **Stateless** - Каждый запрос содержит всю необходимую информацию
4. **Client-Server** - Разделение ответственности
5. **Cacheable** - Ответы могут кешироваться
6. **Uniform Interface** - Единообразная идентификация ресурсов

### 1. Соглашения об именовании ресурсов

### Используйте существительные, не глаголы

 **Плохо:**
```
GET  /getUsers
POST /createUser
```

 **Хорошо:**
```
GET    /users          # Получить всех пользователей
POST   /users          # Создать пользователя
GET    /users/123      # Получить конкретного пользователя
PUT    /users/123      # Обновить пользователя
DELETE /users/123      # Удалить пользователя
```

### Ключевые выводы

1. **Используйте существительные для ресурсов**, не глаголы
2. **Множественное число** для коллекций (/users, /orders)
3. **HTTP методы правильно** - GET (читать), POST (создать), PUT (заменить), PATCH (обновить), DELETE
4. **Подходящие коды статусов** - 2xx успех, 4xx ошибка клиента, 5xx ошибка сервера
5. **Версионирование API** - /api/v1/, /api/v2/
6. **Пагинация** для больших коллекций
7. **Фильтрация и сортировка** через query параметры
8. **Единообразные ответы об ошибках**
9. **Документация с OpenAPI/Swagger**
10. **Безопасность** - HTTPS, аутентификация, rate limiting

## Follow-ups

1. What is the difference between PUT and PATCH methods?
2. How do you implement API versioning strategies?
3. What is HATEOAS and should you use it?
4. How do you handle file uploads in REST APIs?
5. What are idempotency keys and when to use them?
6. How do you implement rate limiting for APIs?
7. What is the difference between authentication and authorization?
8. How do you handle long-running operations in REST APIs?
9. What are the best practices for API error handling?
10. How do you implement API pagination (offset vs cursor-based)?

---

## Related Questions

### Android Implementation
- [[q-when-can-the-system-restart-a-service--android--medium]] - Networking
- [[q-graphql-vs-rest--networking--easy]] - Networking
- [[q-api-file-upload-server--android--medium]] - Networking
- [[q-splash-screen-api-android12--android--medium]] - Networking
- [[q-data-encryption-at-rest--security--medium]] - Networking
- [[q-privacy-sandbox-topics-api--privacy--medium]] - Networking

### Kotlin Language Features
- [[q-retrofit-coroutines-best-practices--kotlin--medium]] - Networking
