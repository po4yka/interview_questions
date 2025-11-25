---
id: kotlin-057
title: "CoroutineContext Composition / Композиция CoroutineContext"
aliases: ["CoroutineContext Composition", "Композиция CoroutineContext"]
topic: kotlin
subtopics: [coroutines, flow]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
source: internal
source_note: Phase 1 Coroutines & Flow Advanced Questions
status: draft
moc: moc-kotlin
related: [c-concurrency, q-coroutine-context-detailed--kotlin--hard, q-kotlin-coroutines-introduction--kotlin--medium]
created: 2025-10-11
updated: 2025-11-11
tags: [coroutines, difficulty/hard, flow, kotlin]

date created: Sunday, October 12th 2025, 12:27:47 pm
date modified: Tuesday, November 25th 2025, 8:53:52 pm
---

# Вопрос (RU)
> Объясните как элементы `CoroutineContext` комбинируются и наследуются. Создайте пользовательский элемент `CoroutineContext` для отслеживания ID запроса в асинхронных операциях.

# Question (EN)
> Explain how `CoroutineContext` elements combine and inherit. Create a custom `CoroutineContext` element for request ID tracking across async operations.

## Ответ (RU)

`CoroutineContext` - это индексированный набор элементов, определяющий поведение корутин. Понимание композиции контекста необходимо для продвинутого использования корутин. См. также [[c-concurrency]].

### Структура CoroutineContext

`CoroutineContext` - это индексированный набор, где каждый элемент имеет уникальный ключ. Элементы комбинируются оператором `+`.

```kotlin
interface CoroutineContext {
    operator fun <E : Element> get(key: Key<E>): E?
    operator fun plus(context: CoroutineContext): CoroutineContext
    fun minusKey(key: Key<*>): CoroutineContext
    fun <R> fold(initial: R, operation: (R, Element) -> R): R

    interface Element : CoroutineContext {
        val key: Key<*>
    }

    interface Key<E : Element>
}
```

### Встроенные Элементы Контекста

```kotlin
// 1. Job - контролирует жизненный цикл
val job = Job()

// 2. Dispatcher - контролирует выполнение в потоках
val dispatcher = Dispatchers.Default

// 3. CoroutineName - имя для отладки
val name = CoroutineName("MyCoroutine")

// 4. CoroutineExceptionHandler - обработка неперехваченных исключений
val handler = CoroutineExceptionHandler { _, exception ->
    println("Перехвачено: $exception")
}

// Комбинирование элементов
val context = job + dispatcher + name + handler
```

### Правила Композиции Контекста

#### 1. Комбинирование С `+`

При комбинировании контекстов элементы с одинаковым ключом заменяют предыдущие:

```kotlin
val context1 = CoroutineName("First") + Dispatchers.IO
val context2 = CoroutineName("Second") + Dispatchers.Default

val combined = context1 + context2
// Результат: CoroutineName("Second") + Dispatchers.Default
// "Second" заменил "First", Default заменил IO
```

#### 2. Наследование Контекста

Дочерние корутины наследуют контекст родителя, но могут переопределять конкретные элементы:

```kotlin
fun main() = runBlocking(CoroutineName("Parent") + Dispatchers.Default) {
    println("Родительский контекст: $coroutineContext")

    launch(CoroutineName("Child")) {
        println("Дочерний контекст: $coroutineContext")
        // Имя переопределено, Dispatcher унаследован
    }

    launch(Dispatchers.IO) {
        println("Второй дочерний контекст: $coroutineContext")
        // Dispatcher переопределён, имя унаследовано
    }
}
```

#### 3. Иерархия Job

Важно различать композицию контекстов и поведение `Job` при создании корутины.

- Оператор `+` всегда заменяет элемент с тем же ключом (включая `Job`).
- При создании новой корутины в scope (например, `launch`/`async`) ей автоматически создаётся новый `Job`, который ссылается на `Job` родителя как на родительский, формируя иерархию отмены (это поведение определено реализацией `kotlinx.coroutines`, а не интерфейсом `CoroutineContext`).

```kotlin
val parentJob = Job()

val scope = CoroutineScope(parentJob + CoroutineName("Scope"))

scope.launch {
    // У этой корутины НОВЫЙ Job, являющийся дочерним по отношению к parentJob
    val job = coroutineContext[Job]
    // Здесь мы полагаемся на гарантии structured concurrency библиотеки:
    // job отменяется вместе с parentJob, хотя parent напрямую не доступен из API
    println(job != null) // true
}
```

### Создание Пользовательских Элементов CoroutineContext

Создадим пользовательский элемент для отслеживания ID запроса - распространенное требование в микросервисах.

#### Элемент Контекста Request ID

```kotlin
/**
 * Элемент CoroutineContext для отслеживания ID запросов.
 * Полезно для распределенной трассировки, логирования и отладки.
 */
data class RequestId(val id: String) : AbstractCoroutineContextElement(RequestId) {
    companion object Key : CoroutineContext.Key<RequestId>

    override fun toString(): String = "RequestId($id)"
}

// Вспомогательная функция для генерации ID
fun generateRequestId(): String = UUID.randomUUID().toString().take(8)

// Расширение для получения текущего request ID
val CoroutineContext.requestId: String?
    get() = this[RequestId]?.id

// Расширение для запуска с request ID
fun CoroutineScope.launchWithRequestId(
    requestId: String = generateRequestId(),
    context: CoroutineContext = EmptyCoroutineContext,
    block: suspend CoroutineScope.() -> Unit
): Job = launch(context + RequestId(requestId), block = block)
```

#### Пример Использования

```kotlin
suspend fun processRequest(userId: Int) {
    val requestId = coroutineContext.requestId ?: "unknown"
    println("[$requestId] Обработка запроса для пользователя $userId")

    delay(100)

    // Вложенные асинхронные операции наследуют request ID
    coroutineScope {
        launch {
            val nestedRequestId = coroutineContext.requestId
            println("[$nestedRequestId] Получение данных пользователя")
            delay(50)
        }

        launch {
            val nestedRequestId = coroutineContext.requestId
            println("[$nestedRequestId] Получение предпочтений")
            delay(50)
        }
    }

    println("[$requestId] Запрос завершен")
}

fun main() = runBlocking {
    // Запуск с автоматическим request ID
    launchWithRequestId {
        processRequest(123)
    }

    // Запуск с конкретным request ID
    launchWithRequestId("custom-req-456") {
        processRequest(456)
    }
}
```

### Продвинутый Пример: Мультитенантный Контекст

```kotlin
/**
 * Элемент контекста для отслеживания tenant в мультитенантных приложениях.
 */
data class TenantContext(
    val tenantId: String,
    val tenantName: String,
    val permissions: Set<String>
) : AbstractCoroutineContextElement(TenantContext) {
    companion object Key : CoroutineContext.Key<TenantContext>

    fun hasPermission(permission: String): Boolean =
        permissions.contains(permission)
}

// Расширение для получения текущего tenant
val CoroutineContext.tenant: TenantContext?
    get() = this[TenantContext]

// Проверка разрешения
suspend fun requirePermission(permission: String) {
    val tenant = coroutineContext.tenant
        ?: throw SecurityException("Нет контекста tenant")

    if (!tenant.hasPermission(permission)) {
        throw SecurityException(
            "Tenant ${tenant.tenantId} не имеет разрешения: $permission"
        )
    }
}

// Репозиторий с учетом tenant
class DocumentRepository {
    suspend fun getDocuments(): List<Document> {
        val tenant = coroutineContext.tenant
            ?: throw IllegalStateException("Нет контекста tenant")

        println("Получение документов для tenant: ${tenant.tenantId}")

        requirePermission("documents:read")

        return fetchDocumentsForTenant(tenant.tenantId)
    }

    suspend fun createDocument(doc: Document) {
        val tenant = coroutineContext.tenant
            ?: throw IllegalStateException("Нет контекста tenant")

        requirePermission("documents:write")

        println("Создание документа для tenant: ${tenant.tenantId}")
        saveDocument(tenant.tenantId, doc)
    }

    private suspend fun fetchDocumentsForTenant(tenantId: String): List<Document> {
        delay(100)
        return listOf(Document("doc1"), Document("doc2"))
    }

    private suspend fun saveDocument(tenantId: String, doc: Document) {
        delay(50)
    }
}

data class Document(val id: String)

// Использование
fun main() = runBlocking {
    val tenant1 = TenantContext(
        tenantId = "tenant-001",
        tenantName = "Acme Corp",
        permissions = setOf("documents:read", "documents:write")
    )

    val tenant2 = TenantContext(
        tenantId = "tenant-002",
        tenantName = "Example Inc",
        permissions = setOf("documents:read") // Нет права на запись
    )

    val repo = DocumentRepository()

    // Операции tenant 1
    launch(tenant1) {
        val docs = repo.getDocuments() // Работает
        println(docs)
        repo.createDocument(Document("new-doc")) // Работает
    }

    // Операции tenant 2
    launch(tenant2) {
        val docs = repo.getDocuments() // Работает
        println(docs)
        try {
            repo.createDocument(Document("new-doc")) // Бросает SecurityException
        } catch (e: SecurityException) {
            println("Ошибка: ${e.message}")
        }
    }
}
```

### Контекст Распределенной Трассировки

```kotlin
/**
 * Контекст для распределенной трассировки с отслеживанием parent-child span.
 */
data class TraceContext(
    val traceId: String,
    val spanId: String,
    val parentSpanId: String? = null,
    val metadata: Map<String, String> = emptyMap()
) : AbstractCoroutineContextElement(TraceContext) {
    companion object Key : CoroutineContext.Key<TraceContext>

    fun createChildSpan(): TraceContext = copy(
        spanId = generateSpanId(),
        parentSpanId = spanId
    )
}

fun generateSpanId(): String = UUID.randomUUID().toString().take(8)
fun generateTraceId(): String = UUID.randomUUID().toString()

// Расширение для доступа к текущему TraceContext
val CoroutineContext.trace: TraceContext?
    get() = this[TraceContext]

// Логирование с учетом трассировочного контекста (контекст явно передается)
fun traceLog(message: String, context: CoroutineContext) {
    val trace = context.trace
    if (trace != null) {
        println("[trace=${trace.traceId}, span=${trace.spanId}] $message")
    } else {
        println("[no-trace] $message")
    }
}

// Сервисный слой с использованием трассировки
class UserService {
    suspend fun getUser(userId: Int): User {
        traceLog("UserService.getUser вызван с userId=$userId", coroutineContext)

        // Создаем дочерний span для обращения к базе данных
        val trace = coroutineContext.trace
        val dbTrace = trace?.createChildSpan()

        return withContext(dbTrace ?: EmptyCoroutineContext) {
            traceLog("Выполнение запроса к базе данных", coroutineContext)
            delay(100)
            User(userId, "John Doe")
        }
    }
}

class OrderService(private val userService: UserService) {
    suspend fun createOrder(userId: Int, items: List<String>): Order {
        traceLog("OrderService.createOrder вызван", coroutineContext)

        // Получение пользователя наследует трассировочный контекст
        val user = userService.getUser(userId)
        traceLog("Пользователь получен: ${user.name}", coroutineContext)

        // Создаем дочерний span для создания заказа
        val trace = coroutineContext.trace
        val orderTrace = trace?.createChildSpan()

        return withContext(orderTrace ?: EmptyCoroutineContext) {
            traceLog("Создание заказа в базе данных", coroutineContext)
            delay(50)
            Order(UUID.randomUUID().toString(), userId, items)
        }
    }
}

data class User(val id: Int, val name: String)
data class Order(val id: String, val userId: Int, val items: List<String>)

// Использование
fun main() = runBlocking {
    val traceId = generateTraceId()
    val rootTrace = TraceContext(
        traceId = traceId,
        spanId = generateSpanId(),
        metadata = mapOf("endpoint" to "/api/orders")
    )

    val userService = UserService()
    val orderService = OrderService(userService)

    launch(rootTrace) {
        traceLog("Обработка HTTP-запроса", coroutineContext)

        val order = orderService.createOrder(
            userId = 123,
            items = listOf("item1", "item2")
        )

        traceLog("Заказ создан: ${order.id}", coroutineContext)
    }
}
```

### Паттерны Пропагации Контекста

#### Паттерн 1: Изоляция Контекста

Иногда нужно разорвать наследование части контекста (например, убрать имя или RequestId):

```kotlin
// Создание нового изолированного контекста (без дополнительных элементов родителя)
suspend fun isolatedOperation() {
    withContext(EmptyCoroutineContext) {
        // Эта корутина выполняется с "чистым" контекстом относительно пользовательских элементов:
        println(coroutineContext[CoroutineName]) // null
    }
}
```

#### Паттерн 2: Композиция Контекста

Комбинирование нескольких пользовательских контекстов:

```kotlin
// Допустим, UserId реализован аналогично RequestId

data class UserId(val id: Int) : AbstractCoroutineContextElement(UserId) {
    companion object Key : CoroutineContext.Key<UserId>
}

suspend fun handleRequest(
    tenantId: String,
    requestId: String,
    userId: Int
) {
    val context = TenantContext(tenantId, "Tenant", setOf()) +
                  RequestId(requestId) +
                  UserId(userId)

    withContext(context) {
        // Все асинхронные операции получают tenant, request и user контексты
        processData()
    }
}

suspend fun processData() {
    // Реализация опущена, использует данные из контекста
}
```

#### Паттерн 3: Перехват (Interception) Контекста

```kotlin
class LoggingContextElement(
    private val logger: Logger
) : AbstractCoroutineContextElement(LoggingContextElement) {
    companion object Key : CoroutineContext.Key<LoggingContextElement>

    fun log(message: String, context: CoroutineContext) {
        val requestId = context.requestId ?: "unknown"
        logger.info("[$requestId] $message")
    }
}

// Упрощенное логирование через контекст
suspend fun logInfo(message: String) {
    coroutineContext[LoggingContextElement]?.log(message, coroutineContext)
}
```

### Лучшие Практики

1. Делайте элементы контекста неизменяемыми:
   ```kotlin
   // Неизменяемый data class
   data class RequestId(val id: String) : AbstractCoroutineContextElement(RequestId) {
       companion object Key : CoroutineContext.Key<RequestId>
   }

   // Изменяемые свойства (пример плохой практики)
   class MutableRequestId(var id: String) : AbstractCoroutineContextElement(MutableRequestId) {
       companion object Key : CoroutineContext.Key<MutableRequestId>
   }
   ```

2. Предоставляйте `companion object Key`:
   ```kotlin
   data class MyContext(val value: String) : AbstractCoroutineContextElement(MyContext) {
       companion object Key : CoroutineContext.Key<MyContext>
   }
   ```

3. Используйте понятные имена:
   ```kotlin
   val CoroutineContext.requestId: String? // хорошо
   val CoroutineContext.id: String?       // неясно
   ```

4. Явно документируйте потокобезопасность и nullability.

5. Обрабатывайте отсутствие контекста безопасно:
   ```kotlin
   val requestId = coroutineContext.requestId ?: generateRequestId()
   ```

### Распространенные Ошибки

1. Изменение разделяемого изменяемого контекста:
   ```kotlin
   class Counter(var count: Int) : AbstractCoroutineContextElement(Counter) {
       companion object Key : CoroutineContext.Key<Counter>
   }

   // Race condition!
   launch {
       coroutineContext[Counter]?.count++ // Небезопасно
   }
   ```

2. Забытый `companion Key`:
   ```kotlin
   // Неполная реализация — нет Key
   // class MyContext(val v: String) : AbstractCoroutineContextElement(???)

   // Правильно
   class MyContext(val v: String) : AbstractCoroutineContextElement(MyContext) {
       companion object Key : CoroutineContext.Key<MyContext>
   }
   ```

3. Утечка контекста с `GlobalScope`:
   ```kotlin
   withContext(RequestId("123")) {
       GlobalScope.launch {
           println(coroutineContext.requestId) // null, контекст потерян
       }
   }

   withContext(RequestId("123")) {
       coroutineScope {
           launch {
               println(coroutineContext.requestId) // "123"
           }
       }
   }
   ```

4. Отсутствие обработки отсутствующего контекста:
   ```kotlin
   // Падает, если RequestId нет
   // val requestId = coroutineContext[RequestId]!!.id

   // Безопасно
   val requestId = coroutineContext.requestId ?: generateRequestId()
   ```

**Краткое содержание**: `CoroutineContext` - это индексированный набор элементов, комбинируемых оператором `+`. Дочерние корутины наследуют родительский контекст, но могут переопределять элементы. Оператор `+` всегда заменяет элемент с тем же ключом; при создании корутины в scope ей создаётся новый `Job`, являющийся дочерним по отношению к родительскому (как определено реализацией библиотеки), что формирует иерархию отмены. Пользовательские элементы обычно расширяют `AbstractCoroutineContextElement` и должны предоставлять `companion Key`. Типичные применения: отслеживание запросов, мультитенантная изоляция, распределенная трассировка. Элементы должны быть неизменяемыми, иметь понятные имена и аккуратно обрабатывать отсутствие значений.

---

## Answer (EN)

`CoroutineContext` is an indexed set of elements that defines the behavior of coroutines. Understanding context composition is essential for advanced coroutine usage.

### CoroutineContext Structure

A `CoroutineContext` is an indexed set where each element has a unique key. Elements can be combined using the `+` operator.

```kotlin
interface CoroutineContext {
    operator fun <E : Element> get(key: Key<E>): E?
    operator fun plus(context: CoroutineContext): CoroutineContext
    fun minusKey(key: Key<*>): CoroutineContext
    fun <R> fold(initial: R, operation: (R, Element) -> R): R

    interface Element : CoroutineContext {
        val key: Key<*>
    }

    interface Key<E : Element>
}
```

### Built-in Context Elements

```kotlin
// 1. Job - controls lifecycle
val job = Job()

// 2. Dispatcher - controls thread execution
val dispatcher = Dispatchers.Default

// 3. CoroutineName - debugging name
val name = CoroutineName("MyCoroutine")

// 4. CoroutineExceptionHandler - handles uncaught exceptions
val handler = CoroutineExceptionHandler { _, exception ->
    println("Caught: $exception")
}

// Combine elements
val context = job + dispatcher + name + handler
```

### Context Composition Rules

#### 1. Combining Contexts with `+`

When combining contexts, elements with the same key replace earlier ones:

```kotlin
val context1 = CoroutineName("First") + Dispatchers.IO
val context2 = CoroutineName("Second") + Dispatchers.Default

val combined = context1 + context2
// Result: CoroutineName("Second") + Dispatchers.Default
// "Second" replaced "First", Default replaced IO
```

#### 2. Context Inheritance

Child coroutines inherit context from their parent, but can override specific elements:

```kotlin
fun main() = runBlocking(CoroutineName("Parent") + Dispatchers.Default) {
    println("Parent context: $coroutineContext")

    launch(CoroutineName("Child")) {
        println("Child context: $coroutineContext")
        // Name overridden, Dispatcher inherited
    }

    launch(Dispatchers.IO) {
        println("Child2 context: $coroutineContext")
        // Dispatcher overridden, Name inherited
    }
}
```

#### 3. Job Hierarchy

It's important to distinguish between context combination and how `Job`s behave when launching coroutines:

- The `+` operator always replaces an element with the same key (including `Job`).
- When you launch a new coroutine in a scope, it gets a NEW `Job` whose parent is the `Job` from the scope's context, forming a structured concurrency hierarchy (this is defined by the `kotlinx.coroutines` implementation, not by the `CoroutineContext` interface itself).

```kotlin
val parentJob = Job()
val scope = CoroutineScope(parentJob + CoroutineName("Scope"))

scope.launch {
    // This coroutine gets a new Job that is a child of parentJob
    val job = coroutineContext[Job]
    // We rely on structured concurrency guarantees: this job is cancelled with parentJob
    println(job != null) // true
}
```

### Creating Custom CoroutineContext Elements

Let's create a custom context element for request ID tracking - a common requirement in microservices and distributed systems.

#### Request ID Context Element

```kotlin
/**
 * CoroutineContext element for tracking request IDs across async operations.
 * Useful for distributed tracing, logging, and debugging.
 */
data class RequestId(val id: String) : AbstractCoroutineContextElement(RequestId) {
    companion object Key : CoroutineContext.Key<RequestId>

    override fun toString(): String = "RequestId($id)"
}

// Helper function to generate request IDs
fun generateRequestId(): String = UUID.randomUUID().toString().take(8)

// Extension to get current request ID
val CoroutineContext.requestId: String?
    get() = this[RequestId]?.id

// Extension to launch with request ID
fun CoroutineScope.launchWithRequestId(
    requestId: String = generateRequestId(),
    context: CoroutineContext = EmptyCoroutineContext,
    block: suspend CoroutineScope.() -> Unit
): Job = launch(context + RequestId(requestId), block = block)
```

#### Usage Example

```kotlin
suspend fun processRequest(userId: Int) {
    val requestId = coroutineContext.requestId ?: "unknown"
    println("[$requestId] Processing request for user $userId")

    // Simulate async operations
    delay(100)

    // Nested async operations inherit request ID
    coroutineScope {
        launch {
            val nestedRequestId = coroutineContext.requestId
            println("[$nestedRequestId] Fetching user data")
            delay(50)
        }

        launch {
            val nestedRequestId = coroutineContext.requestId
            println("[$nestedRequestId] Fetching user preferences")
            delay(50)
        }
    }

    println("[$requestId] Request completed")
}

fun main() = runBlocking {
    // Launch with automatic request ID
    launchWithRequestId {
        processRequest(123)
    }

    // Launch with specific request ID
    launchWithRequestId("custom-req-456") {
        processRequest(456)
    }
}
```

### Advanced: Multi-Tenant Context

A more complex example for multi-tenant applications:

```kotlin
/**
 * Context element for tracking tenant in multi-tenant applications.
 */
data class TenantContext(
    val tenantId: String,
    val tenantName: String,
    val permissions: Set<String>
) : AbstractCoroutineContextElement(TenantContext) {
    companion object Key : CoroutineContext.Key<TenantContext>

    fun hasPermission(permission: String): Boolean =
        permissions.contains(permission)

    override fun toString(): String =
        "TenantContext(tenantId=$tenantId, tenantName=$tenantName)"
}

// Extension to get current tenant
val CoroutineContext.tenant: TenantContext?
    get() = this[TenantContext]

// Extension to check permission
suspend fun requirePermission(permission: String) {
    val tenant = coroutineContext.tenant
        ?: throw SecurityException("No tenant context")

    if (!tenant.hasPermission(permission)) {
        throw SecurityException(
            "Tenant ${tenant.tenantId} lacks permission: $permission"
        )
    }
}

// Repository that respects tenant context
class DocumentRepository {
    suspend fun getDocuments(): List<Document> {
        val tenant = coroutineContext.tenant
            ?: throw IllegalStateException("No tenant context")

        println("Fetching documents for tenant: ${tenant.tenantId}")

        // Verify permission
        requirePermission("documents:read")

        // Fetch tenant-specific documents
        return fetchDocumentsForTenant(tenant.tenantId)
    }

    suspend fun createDocument(doc: Document) {
        val tenant = coroutineContext.tenant
            ?: throw IllegalStateException("No tenant context")

        requirePermission("documents:write")

        println("Creating document for tenant: ${tenant.tenantId}")
        saveDocument(tenant.tenantId, doc)
    }

    private suspend fun fetchDocumentsForTenant(tenantId: String): List<Document> {
        delay(100) // Simulate DB query
        return listOf(Document("doc1"), Document("doc2"))
    }

    private suspend fun saveDocument(tenantId: String, doc: Document) {
        delay(50)
    }
}

data class Document(val id: String)

// Usage
fun main() = runBlocking {
    val tenant1 = TenantContext(
        tenantId = "tenant-001",
        tenantName = "Acme Corp",
        permissions = setOf("documents:read", "documents:write")
    )

    val tenant2 = TenantContext(
        tenantId = "tenant-002",
        tenantName = "Example Inc",
        permissions = setOf("documents:read") // No write permission
    )

    val repo = DocumentRepository()

    // Tenant 1 operations
    launch(tenant1) {
        val docs = repo.getDocuments() // Works
        repo.createDocument(Document("new-doc")) // Works
    }

    // Tenant 2 operations
    launch(tenant2) {
        val docs = repo.getDocuments() // Works
        try {
            repo.createDocument(Document("new-doc")) // Fails
        } catch (e: SecurityException) {
            println("Error: ${e.message}")
        }
    }
}
```

### Advanced: Correlation Context for Distributed Tracing

```kotlin
/**
 * Context for distributed tracing with parent-child span tracking.
 */
data class TraceContext(
    val traceId: String,
    val spanId: String,
    val parentSpanId: String? = null,
    val metadata: Map<String, String> = emptyMap()
) : AbstractCoroutineContextElement(TraceContext) {
    companion object Key : CoroutineContext.Key<TraceContext>

    fun createChildSpan(): TraceContext = copy(
        spanId = generateSpanId(),
        parentSpanId = spanId
    )

    override fun toString(): String =
        "TraceContext(trace=$traceId, span=$spanId, parent=$parentSpanId)"
}

fun generateSpanId(): String = UUID.randomUUID().toString().take(8)
fun generateTraceId(): String = UUID.randomUUID().toString()

// Extension to get current trace
val CoroutineContext.trace: TraceContext?
    get() = this[TraceContext]

// Logging with trace context (context is passed explicitly)
fun traceLog(message: String, context: CoroutineContext) {
    val trace = context.trace
    if (trace != null) {
        println("[trace=${trace.traceId}, span=${trace.spanId}] $message")
    } else {
        println("[no-trace] $message")
    }
}

// Service layer with tracing
class UserService {
    suspend fun getUser(userId: Int): User {
        traceLog("UserService.getUser called with userId=$userId", coroutineContext)

        // Create child span for database call
        val trace = coroutineContext.trace
        val dbTrace = trace?.createChildSpan()

        return withContext(dbTrace ?: EmptyCoroutineContext) {
            traceLog("Querying database", coroutineContext)
            delay(100)
            User(userId, "John Doe")
        }
    }
}

class OrderService(private val userService: UserService) {
    suspend fun createOrder(userId: Int, items: List<String>): Order {
        traceLog("OrderService.createOrder called", coroutineContext)

        // User lookup inherits trace context automatically
        val user = userService.getUser(userId)
        traceLog("User retrieved: ${user.name}", coroutineContext)

        // Create child span for order creation
        val trace = coroutineContext.trace
        val orderTrace = trace?.createChildSpan()

        return withContext(orderTrace ?: EmptyCoroutineContext) {
            traceLog("Creating order in database", coroutineContext)
            delay(50)
            Order(UUID.randomUUID().toString(), userId, items)
        }
    }
}

data class User(val id: Int, val name: String)
data class Order(val id: String, val userId: Int, val items: List<String>)

// Usage
fun main() = runBlocking {
    val traceId = generateTraceId()
    val rootTrace = TraceContext(
        traceId = traceId,
        spanId = generateSpanId(),
        metadata = mapOf("endpoint" to "/api/orders")
    )

    val userService = UserService()
    val orderService = OrderService(userService)

    launch(rootTrace) {
        traceLog("Handling HTTP request", coroutineContext)

        val order = orderService.createOrder(
            userId = 123,
            items = listOf("item1", "item2")
        )

        traceLog("Order created: ${order.id}", coroutineContext)
    }
}
```

### Context Propagation Patterns

#### Pattern 1: Context Isolation

Sometimes you want to break inheritance of custom elements (e.g., remove name or RequestId):

```kotlin
// Create new isolated context (without parent's additional elements)
suspend fun isolatedOperation() {
    withContext(EmptyCoroutineContext) {
        // This coroutine runs with a "clean" context relative to custom elements
        println(coroutineContext[CoroutineName]) // null
    }
}
```

#### Pattern 2: Context Composition

Combine multiple custom contexts:

```kotlin
// Assume UserId is implemented similar to RequestId

data class UserId(val id: Int) : AbstractCoroutineContextElement(UserId) {
    companion object Key : CoroutineContext.Key<UserId>
}

suspend fun handleRequest(
    tenantId: String,
    requestId: String,
    userId: Int
) {
    val context = TenantContext(tenantId, "Tenant", setOf()) +
                  RequestId(requestId) +
                  UserId(userId)

    withContext(context) {
        // All async operations have tenant, request, and user context
        processData()
    }
}

suspend fun processData() {
    // Implementation omitted, uses data from context
}
```

#### Pattern 3: Context Interception

```kotlin
class LoggingContextElement(
    private val logger: Logger
) : AbstractCoroutineContextElement(LoggingContextElement) {
    companion object Key : CoroutineContext.Key<LoggingContextElement>

    fun log(message: String, context: CoroutineContext) {
        val requestId = context.requestId ?: "unknown"
        logger.info("[$requestId] $message")
    }
}

// Extension for easy logging
suspend fun logInfo(message: String) {
    coroutineContext[LoggingContextElement]?.log(message, coroutineContext)
}
```

### Best Practices

1. Make context elements immutable:
   ```kotlin
   // Immutable data class
   data class RequestId(val id: String) : AbstractCoroutineContextElement(RequestId) {
       companion object Key : CoroutineContext.Key<RequestId>
   }

   // Mutable properties (avoid)
   class MutableRequestId(var id: String) : AbstractCoroutineContextElement(MutableRequestId) {
       companion object Key : CoroutineContext.Key<MutableRequestId>
   }
   ```

2. Provide a `companion object Key`:
   ```kotlin
   data class MyContext(val value: String) : AbstractCoroutineContextElement(MyContext) {
       companion object Key : CoroutineContext.Key<MyContext> // Required
   }
   ```

3. Use meaningful names:
   ```kotlin
   val CoroutineContext.requestId: String? // clear
   val CoroutineContext.id: String?       // unclear
   ```

4. Document thread safety and nullability.

5. Handle missing context gracefully:
   ```kotlin
   val requestId = coroutineContext.requestId ?: generateRequestId()
   ```

### Common Pitfalls

1. Modifying shared mutable context:
   ```kotlin
   class Counter(var count: Int) : AbstractCoroutineContextElement(Counter) {
       companion object Key : CoroutineContext.Key<Counter>
   }

   // Race condition!
   launch {
       coroutineContext[Counter]?.count++ // Unsafe
   }
   ```

2. Forgetting `Key` companion object:
   ```kotlin
   // Incomplete - missing Key
   // class MyContext : AbstractCoroutineContextElement(???)

   // Correct
   class MyContext : AbstractCoroutineContextElement(MyContext) {
       companion object Key : CoroutineContext.Key<MyContext>
   }
   ```

3. `Context` leaks with `GlobalScope`:
   ```kotlin
   // Context lost when using GlobalScope
   withContext(RequestId("123")) {
       GlobalScope.launch {
           // RequestId is lost here!
           println(coroutineContext.requestId) // null
       }
   }

   // Use coroutineScope to preserve context
   withContext(RequestId("123")) {
       coroutineScope {
           launch {
               println(coroutineContext.requestId) // "123"
           }
       }
   }
   ```

4. Not handling missing context gracefully:
   ```kotlin
   // Unsafe
   // val requestId = coroutineContext[RequestId]!!.id

   // Safe
   val requestId = coroutineContext.requestId ?: generateRequestId()
   ```

**English Summary**: `CoroutineContext` is an indexed set of elements that combine using the `+` operator. Child coroutines inherit parent context but can override specific elements. The `+` operator always replaces elements with the same key; when launching coroutines within a scope, a new child `Job` is created by the library to maintain structured concurrency. Custom context elements typically extend `AbstractCoroutineContextElement` and must provide a companion `Key`. Common uses include request tracking, multi-tenant isolation, and distributed tracing. `Context` elements should be immutable, well-named, thread-safe, and handle missing values gracefully.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- ["Coroutine" context and dispatchers - Kotlin]("https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html")
- [CoroutineContext - API Reference]("https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-coroutine-context/")
- [Custom CoroutineContext elements]("https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx-coroutines-core/kotlinx.coroutines/-abstract-coroutine-context-element/")

## Related Questions
- [[q-coroutine-context-detailed--kotlin--hard]]
- [[q-kotlin-coroutines-introduction--kotlin--medium]]