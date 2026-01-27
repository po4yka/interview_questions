---
id: dp-012
title: Chain Of Responsibility / Цепочка обязанностей
aliases:
- Chain Of Responsibility
- Цепочка обязанностей
topic: cs
subtopics:
- design-patterns
- behavioral
- chain-of-responsibility
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-cs
related:
- c-architecture-patterns
- c-dao-pattern
- q-abstract-factory-pattern--cs--medium
created: 2025-10-15
updated: 2025-11-11
tags:
- behavioral
- chain-of-responsibility
- design-patterns
- difficulty/medium
anki_cards:
- slug: dp-012-0-en
  language: en
  anki_id: 1768454033689
  synced_at: '2026-01-25T13:01:16.916234'
- slug: dp-012-0-ru
  language: ru
  anki_id: 1768454033713
  synced_at: '2026-01-25T13:01:16.917561'
---
# Вопрос (RU)
> Что такое паттерн Chain of Responsibility? Когда и зачем его использовать?

# Question (EN)
> What is the Chain of Responsibility pattern? When and why should it be used?

---

## Ответ (RU)

Chain of Responsibility (Цепочка обязанностей) — это поведенческий паттерн проектирования, в котором запрос последовательно передается через цепочку потенциальных обработчиков, пока один из них не обработает запрос или цепочка не закончится. Каждый обработчик в цепочке имеет возможность либо обработать запрос, либо передать его следующему обработчику. Клиенту не нужно знать, какой обработчик фактически обработает запрос — он просто отправляет его в цепочку.

Этот паттерн отделяет клиента от конкретного получателя, выполняющего действие, следуя принципу открытости/закрытости и позволяя добавлять новые обработчики без изменения существующего кода.

### Определение

Chain of Responsibility — это паттерн, в котором запрос последовательно проходит через цепочку обработчиков, и каждый обработчик решает, может ли он обработать запрос (и остановить цепочку) или передать его дальше. Как правило, клиент взаимодействует только с начальным звеном цепочки.

### Проблемы, Которые Решает

1. Необходимо избежать жесткой связи отправителя запроса с конкретным получателем.
2. Должно быть несколько потенциальных обработчиков, при этом конкретный выбирается во время выполнения.
3. Логика обработки не должна быть "зашита" в один монолитный класс с огромным количеством if/else/when.

### Решение

Определяется цепочка объектов-обработчиков. Каждый обработчик:
- знает о следующем обработчике;
- либо обрабатывает запрос, либо перенаправляет его дальше по цепочке;
- клиенту не нужно знать, кто именно обработает запрос.

В классической формулировке GoF обычно только один обработчик обрабатывает запрос и может остановить дальнейшее распространение. Вариации допускают, что несколько обработчиков могут обработать один и тот же запрос.

### Когда Использовать?

Используйте Chain of Responsibility, когда:

1. Есть несколько возможных обработчиков запроса, и выбор конкретного должен решаться во время выполнения.
2. Нужно заменить громоздкие условные конструкции (if/else/when) более гибкой структурой.
3. Требуется возможность динамически расширять, переупорядочивать или конфигурировать цепочку обработчиков без изменения клиентского кода.

### Пример: Обработчики Запросов (Kotlin)

```kotlin
// Интерфейс обработчика
interface Handler {
    var nextHandler: Handler?
    fun handleRequest(request: String): Boolean
}

// Конкретные обработчики
class FirstHandler : Handler {
    override var nextHandler: Handler? = null

    override fun handleRequest(request: String): Boolean {
        if (request == "Request1") {
            println("FirstHandler handled $request")
            return true
        }
        return nextHandler?.handleRequest(request) ?: false
    }
}

class SecondHandler : Handler {
    override var nextHandler: Handler? = null

    override fun handleRequest(request: String): Boolean {
        if (request == "Request2") {
            println("SecondHandler handled $request")
            return true
        }
        return nextHandler?.handleRequest(request) ?: false
    }
}

class DefaultHandler : Handler {
    override var nextHandler: Handler? = null

    override fun handleRequest(request: String): Boolean {
        println("DefaultHandler handled $request")
        return true
    }
}

// Построение цепочки
fun main() {
    val firstHandler = FirstHandler()
    val secondHandler = SecondHandler()
    val defaultHandler = DefaultHandler()

    firstHandler.nextHandler = secondHandler
    secondHandler.nextHandler = defaultHandler

    listOf("Request1", "Request2", "Request3").forEach {
        if (!firstHandler.handleRequest(it)) {
            println("$it was not handled")
        }
    }
}
```

Результат:

- `Request1` обрабатывается `FirstHandler`.
- `Request2` обрабатывается `SecondHandler`.
- `Request3` обрабатывается `DefaultHandler` как обработчиком по умолчанию.

### Android-пример: Обработка Событий `View` (концептуально)

```kotlin
// Концептуальная цепочка обработки touch-событий (упрощенная)
sealed class TouchEvent {
    data class Click(val x: Int, val y: Int) : TouchEvent()
    data class LongPress(val x: Int, val y: Int) : TouchEvent()
    data class Swipe(val direction: String) : TouchEvent()
}

interface TouchHandler {
    var nextHandler: TouchHandler?
    fun handle(event: TouchEvent): Boolean
}

class ClickHandler : TouchHandler {
    override var nextHandler: TouchHandler? = null

    override fun handle(event: TouchEvent): Boolean {
        return when (event) {
            is TouchEvent.Click -> {
                println("Click handled at (${event.x}, ${event.y})")
                true
            }
            else -> nextHandler?.handle(event) ?: false
        }
    }
}

class LongPressHandler : TouchHandler {
    override var nextHandler: TouchHandler? = null

    override fun handle(event: TouchEvent): Boolean {
        return when (event) {
            is TouchEvent.LongPress -> {
                println("Long press handled at (${event.x}, ${event.y})")
                true
            }
            else -> nextHandler?.handle(event) ?: false
        }
    }
}

class SwipeHandler : TouchHandler {
    override var nextHandler: TouchHandler? = null

    override fun handle(event: TouchEvent): Boolean {
        return when (event) {
            is TouchEvent.Swipe -> {
                println("Swipe ${event.direction} handled")
                true
            }
            else -> nextHandler?.handle(event) ?: false
        }
    }
}

class GestureDetector {
    private val chain: TouchHandler

    init {
        val clickHandler = ClickHandler()
        val longPressHandler = LongPressHandler()
        val swipeHandler = SwipeHandler()

        clickHandler.nextHandler = longPressHandler
        longPressHandler.nextHandler = swipeHandler

        chain = clickHandler
    }

    fun processEvent(event: TouchEvent) {
        if (!chain.handle(event)) {
            println("Event not handled: $event")
        }
    }
}
```

Здесь событие проходит по цепочке обработчиков: каждый пытается обработать его и при необходимости передает дальше.

### Kotlin-пример: Цепочка Валидации

```kotlin
// Интерфейс обработчика валидации
interface ValidationHandler {
    var next: ValidationHandler?

    fun validate(data: UserData): ValidationResult {
        val result = doValidate(data)
        return if (result is ValidationResult.Valid && next != null) {
            next!!.validate(data)
        } else {
            result
        }
    }

    fun doValidate(data: UserData): ValidationResult
}

sealed class ValidationResult {
    object Valid : ValidationResult()
    data class Invalid(val message: String) : ValidationResult()
}

data class UserData(
    val email: String,
    val password: String,
    val age: Int
)

// Конкретные валидаторы
class EmailValidator : ValidationHandler {
    override var next: ValidationHandler? = null

    override fun doValidate(data: UserData): ValidationResult {
        return if (data.email.contains("@")) {
            ValidationResult.Valid
        } else {
            ValidationResult.Invalid("Invalid email format")
        }
    }
}

class PasswordValidator : ValidationHandler {
    override var next: ValidationHandler? = null

    override fun doValidate(data: UserData): ValidationResult {
        return if (data.password.length >= 8) {
            ValidationResult.Valid
        } else {
            ValidationResult.Invalid("Password must be at least 8 characters")
        }
    }
}

class AgeValidator : ValidationHandler {
    override var next: ValidationHandler? = null

    override fun doValidate(data: UserData): ValidationResult {
        return if (data.age >= 18) {
            ValidationResult.Valid
        } else {
            ValidationResult.Invalid("Must be 18 or older")
        }
    }
}

// Построение цепочки
fun createValidationChain(): ValidationHandler {
    val emailValidator = EmailValidator()
    val passwordValidator = PasswordValidator()
    val ageValidator = AgeValidator()

    emailValidator.next = passwordValidator
    passwordValidator.next = ageValidator

    return emailValidator
}

// Использование
fun main() {
    val validator = createValidationChain()

    val userData = UserData("user@example.com", "pass123", 20)
    when (val result = validator.validate(userData)) {
        is ValidationResult.Valid -> println("Validation passed")
        is ValidationResult.Invalid -> println("Validation failed: ${result.message}")
    }
}
```

Цепочка валидаторов поочередно проверяет данные; при первой ошибке валидация останавливается.

### Пример: Цепочка Интерсепторов (OkHttp-подобная, упрощенно)

```kotlin
// Упрощенная цепочка интерсепторов в стиле OkHttp
interface Interceptor {
    fun intercept(chain: Chain): Response
}

interface Chain {
    fun request(): Request
    fun proceed(request: Request): Response
}

class RealInterceptorChain(
    private val interceptors: List<Interceptor>,
    private val index: Int,
    private val request: Request
) : Chain {

    override fun request() = request

    override fun proceed(request: Request): Response {
        if (index >= interceptors.size) {
            // Конец цепочки — реальный запрос (упрощено)
            return makeRealRequest(request)
        }

        val next = RealInterceptorChain(interceptors, index + 1, request)
        val interceptor = interceptors[index]
        return interceptor.intercept(next)
    }

    private fun makeRealRequest(request: Request): Response {
        return Response(200, "Success")
    }
}

// Конкретные интерсепторы
class LoggingInterceptor : Interceptor {
    override fun intercept(chain: Chain): Response {
        val request = chain.request()
        println("Request: ${request.url}")
        val response = chain.proceed(request)
        println("Response: ${response.code}")
        return response
    }
}

class AuthInterceptor(private val token: String) : Interceptor {
    override fun intercept(chain: Chain): Response {
        val originalRequest = chain.request()
        val authorizedRequest = originalRequest.copy(
            headers = originalRequest.headers + ("Authorization" to "Bearer $token")
        )
        return chain.proceed(authorizedRequest)
    }
}

class CacheInterceptor : Interceptor {
    private val cache = mutableMapOf<String, Response>()

    override fun intercept(chain: Chain): Response {
        val request = chain.request()
        cache[request.url]?.let {
            println("Returning cached response")
            return it
        }

        val response = chain.proceed(request)
        cache[request.url] = response
        return response
    }
}

data class Request(val url: String, val headers: Map<String, String> = emptyMap())
data class Response(val code: Int, val body: String)
```

Этот пример иллюстрирует цепочку перехватчиков, где каждый может модифицировать запрос/ответ или передать дальше.

### Лучшие Практики

```kotlin
// РЕКОМЕНДУЕТСЯ: использовать обработчик по умолчанию в конце цепочки, когда это уместно
class DefaultHandler : Handler {
    override var nextHandler: Handler? = null
    override fun handleRequest(request: String): Boolean {
        println("Default: No specific handler for $request")
        return true
    }
}

// РЕКОМЕНДУЕТСЯ: сделать цепочку неизменяемой после создания, когда это возможно
fun buildChain(): Handler {
    return FirstHandler().apply {
        nextHandler = SecondHandler().apply {
            nextHandler = DefaultHandler()
        }
    }
}

// РЕКОМЕНДУЕТСЯ: при простой логике использовать функциональный подход,
// сохраняя идею последовательной проверки
val validationChain = listOf<(UserData) -> Boolean>(
    { it.email.isNotBlank() },
    { it.password.length >= 8 },
    { it.age >= 18 }
)

fun validate(data: UserData) = validationChain.all { it(data) }

// НЕ РЕКОМЕНДУЕТСЯ: создавать циклические цепочки
// НЕ РЕКОМЕНДУЕТСЯ: класть тяжелую бизнес-логику в конструирование цепочки
// НЕ РЕКОМЕНДУЕТСЯ: делать обработчики сильно связанными друг с другом
```

Кратко: Chain of Responsibility позволяет передавать запрос по цепочке обработчиков до тех пор, пока один из них его не обработает или цепочка не закончится, что уменьшает связность и повышает гибкость архитектуры. Паттерн полезен для обработки событий, валидации, логирования, интерсепторов и других последовательных конвейеров.

---

## Answer (EN)

Chain of Responsibility is a behavioral design pattern that allows passing requests along a chain of handlers. Each handler decides whether it can handle the request and whether to pass it further along the chain.

### Definition

Chain of Responsibility is a design pattern in which a request is passed sequentially through a chain of potential handlers until one of them handles the request (or the chain ends). Each handler in the chain has a chance to either process the request or pass it to the next handler. The client doesn't need to know which handler will actually deal with the request — it simply sends it into the chain.

This pattern decouples the client from the specific receiver that performs the action, following the Open/Closed Principle by allowing new handlers to be added without modifying existing code.

### Problems it Solves

1. Coupling the sender of a request to its receiver should be avoided.
2. It should be possible to have multiple potential receivers for a request, with the actual receiver determined at runtime.
3. Implementing request handling logic directly in the sender class is inflexible — it tightly couples the class to concrete receivers and complex conditional logic.

### Solution

Define a chain of receiver objects that, depending on run-time conditions, either handle a request or forward it to the next receiver in the chain (if any).

This enables us to send a request to a chain of receivers without having to know which one handles the request. The request gets passed along the chain until a receiver handles the request or the chain is exhausted. The sender of a request is no longer coupled to a particular receiver.

Note: In the classic GoF formulation, typically at most one handler processes a given request (and may stop propagation). Variations may allow multiple handlers to act on the same request.

### When to Use?

You might consider using Chain of Responsibility when:

1. Multiple handlers for a type of request – which one handles it is decided at runtime (e.g., conceptual UI event propagation).
2. You want to avoid monolithic conditional logic – replace big if/else or when chains with separate handler classes.
3. You need flexible chains that can be extended, composed, or reordered dynamically.

### Example: Request Handlers

```kotlin
// Step 1: Handler Interface
interface Handler {
    var nextHandler: Handler?
    fun handleRequest(request: String): Boolean
}

// Step 2: Concrete Handlers
class FirstHandler : Handler {
    override var nextHandler: Handler? = null

    override fun handleRequest(request: String): Boolean {
        if (request == "Request1") {
            println("FirstHandler handled $request")
            return true
        }
        return nextHandler?.handleRequest(request) ?: false
    }
}

class SecondHandler : Handler {
    override var nextHandler: Handler? = null

    override fun handleRequest(request: String): Boolean {
        if (request == "Request2") {
            println("SecondHandler handled $request")
            return true
        }
        return nextHandler?.handleRequest(request) ?: false
    }
}

class DefaultHandler : Handler {
    override var nextHandler: Handler? = null

    override fun handleRequest(request: String): Boolean {
        println("DefaultHandler handled $request")
        return true
    }
}

// Step 3: Building the chain
fun main() {
    val firstHandler = FirstHandler()
    val secondHandler = SecondHandler()
    val defaultHandler = DefaultHandler()

    firstHandler.nextHandler = secondHandler
    secondHandler.nextHandler = defaultHandler

    listOf("Request1", "Request2", "Request3").forEach {
        if (!firstHandler.handleRequest(it)) {
            println("$it was not handled")
        }
    }
}
```

Output:

FirstHandler handled Request1
SecondHandler handled Request2
DefaultHandler handled Request3

### Android Example: `View` Event Handling (Conceptual)

```kotlin
// Conceptual touch event chain (simplified, not full Android implementation)
sealed class TouchEvent {
    data class Click(val x: Int, val y: Int) : TouchEvent()
    data class LongPress(val x: Int, val y: Int) : TouchEvent()
    data class Swipe(val direction: String) : TouchEvent()
}

interface TouchHandler {
    var nextHandler: TouchHandler?
    fun handle(event: TouchEvent): Boolean
}

class ClickHandler : TouchHandler {
    override var nextHandler: TouchHandler? = null

    override fun handle(event: TouchEvent): Boolean {
        return when (event) {
            is TouchEvent.Click -> {
                println("Click handled at (${event.x}, ${event.y})")
                true
            }
            else -> nextHandler?.handle(event) ?: false
        }
    }
}

class LongPressHandler : TouchHandler {
    override var nextHandler: TouchHandler? = null

    override fun handle(event: TouchEvent): Boolean {
        return when (event) {
            is TouchEvent.LongPress -> {
                println("Long press handled at (${event.x}, ${event.y})")
                true
            }
            else -> nextHandler?.handle(event) ?: false
        }
    }
}

class SwipeHandler : TouchHandler {
    override var nextHandler: TouchHandler? = null

    override fun handle(event: TouchEvent): Boolean {
        return when (event) {
            is TouchEvent.Swipe -> {
                println("Swipe ${event.direction} handled")
                true
            }
            else -> nextHandler?.handle(event) ?: false
        }
    }
}

// Usage
class GestureDetector {
    private val chain: TouchHandler

    init {
        val clickHandler = ClickHandler()
        val longPressHandler = LongPressHandler()
        val swipeHandler = SwipeHandler()

        clickHandler.nextHandler = longPressHandler
        longPressHandler.nextHandler = swipeHandler

        chain = clickHandler
    }

    fun processEvent(event: TouchEvent) {
        if (!chain.handle(event)) {
            println("Event not handled: $event")
        }
    }
}
```

Note: This example is conceptual and demonstrates the pattern; real Android input handling also involves framework-defined propagation rules.

### Kotlin Example: Validation Chain

```kotlin
// Validation handler interface
interface ValidationHandler {
    var next: ValidationHandler?

    fun validate(data: UserData): ValidationResult {
        val result = doValidate(data)
        return if (result is ValidationResult.Valid && next != null) {
            next!!.validate(data)
        } else {
            result
        }
    }

    fun doValidate(data: UserData): ValidationResult
}

sealed class ValidationResult {
    object Valid : ValidationResult()
    data class Invalid(val message: String) : ValidationResult()
}

data class UserData(
    val email: String,
    val password: String,
    val age: Int
)

// Concrete validators
class EmailValidator : ValidationHandler {
    override var next: ValidationHandler? = null

    override fun doValidate(data: UserData): ValidationResult {
        return if (data.email.contains("@")) {
            ValidationResult.Valid
        } else {
            ValidationResult.Invalid("Invalid email format")
        }
    }
}

class PasswordValidator : ValidationHandler {
    override var next: ValidationHandler? = null

    override fun doValidate(data: UserData): ValidationResult {
        return if (data.password.length >= 8) {
            ValidationResult.Valid
        } else {
            ValidationResult.Invalid("Password must be at least 8 characters")
        }
    }
}

class AgeValidator : ValidationHandler {
    override var next: ValidationHandler? = null

    override fun doValidate(data: UserData): ValidationResult {
        return if (data.age >= 18) {
            ValidationResult.Valid
        } else {
            ValidationResult.Invalid("Must be 18 or older")
        }
    }
}

// Building the chain
fun createValidationChain(): ValidationHandler {
    val emailValidator = EmailValidator()
    val passwordValidator = PasswordValidator()
    val ageValidator = AgeValidator()

    emailValidator.next = passwordValidator
    passwordValidator.next = ageValidator

    return emailValidator
}

// Usage
fun main() {
    val validator = createValidationChain()

    val userData = UserData("user@example.com", "pass123", 20)
    when (val result = validator.validate(userData)) {
        is ValidationResult.Valid -> println("Validation passed")
        is ValidationResult.Invalid -> println("Validation failed: ${result.message}")
    }
}
```

### Android Interceptor Chain Example (Simplified)

```kotlin
// OkHttp-style interceptor chain (simplified proof-of-concept)
interface Interceptor {
    fun intercept(chain: Chain): Response
}

interface Chain {
    fun request(): Request
    fun proceed(request: Request): Response
}

class RealInterceptorChain(
    private val interceptors: List<Interceptor>,
    private val index: Int,
    private val request: Request
) : Chain {

    override fun request() = request

    override fun proceed(request: Request): Response {
        if (index >= interceptors.size) {
            // End of chain - make actual request (simplified)
            return makeRealRequest(request)
        }

        val next = RealInterceptorChain(interceptors, index + 1, request)
        val interceptor = interceptors[index]
        return interceptor.intercept(next)
    }

    private fun makeRealRequest(request: Request): Response {
        // Simulate network call
        return Response(200, "Success")
    }
}

// Concrete interceptors
class LoggingInterceptor : Interceptor {
    override fun intercept(chain: Chain): Response {
        val request = chain.request()
        println("Request: ${request.url}")
        val response = chain.proceed(request)
        println("Response: ${response.code}")
        return response
    }
}

class AuthInterceptor(private val token: String) : Interceptor {
    override fun intercept(chain: Chain): Response {
        val originalRequest = chain.request()
        val authorizedRequest = originalRequest.copy(
            headers = originalRequest.headers + ("Authorization" to "Bearer $token")
        )
        return chain.proceed(authorizedRequest)
    }
}

class CacheInterceptor : Interceptor {
    private val cache = mutableMapOf<String, Response>()

    override fun intercept(chain: Chain): Response {
        val request = chain.request()
        cache[request.url]?.let {
            println("Returning cached response")
            return it
        }

        val response = chain.proceed(request)
        cache[request.url] = response
        return response
    }
}

data class Request(val url: String, val headers: Map<String, String> = emptyMap())
data class Response(val code: Int, val body: String)
```

### Best Practices

```kotlin
// DO: Provide a default handler at the end when appropriate
class DefaultHandler : Handler {
    override var nextHandler: Handler? = null
    override fun handleRequest(request: String): Boolean {
        println("Default: No specific handler for $request")
        return true
    }
}

// DO: Make chain immutable after creation when possible
fun buildChain(): Handler {
    return FirstHandler().apply {
        nextHandler = SecondHandler().apply {
            nextHandler = DefaultHandler()
        }
    }
}

// DO: Use functional approach in Kotlin as an alternative when suitable
val validationChain = listOf<(UserData) -> Boolean>(
    { it.email.isNotBlank() },
    { it.password.length >= 8 },
    { it.age >= 18 }
)

fun validate(data: UserData) = validationChain.all { it(data) }

// DON'T: Create circular chains
// DON'T: Put heavy business logic in chain construction
// DON'T: Make handlers depend tightly on each other
```

Summary: Chain of Responsibility is a behavioral pattern that passes requests through a chain of handlers until one processes it (or the chain ends). It reduces coupling between sender and receiver, replaces complex conditionals with composable handlers, and is useful for event handling, validation pipelines, logging, and interceptor chains.

---

## Related Questions

- [[q-adapter-pattern--cs--medium]]
- [[q-abstract-factory-pattern--cs--medium]]

## Follow-ups

- How would you implement error handling or fallback strategies in a chain if multiple handlers can act on the same request?
- How does Chain of Responsibility compare to the Decorator and Middleware patterns conceptually?
- In what cases might Chain of Responsibility harm readability or performance, and how would you mitigate that?

## References

- [[c-architecture-patterns]]
- https://maxim-gorin.medium.com/stop-hardcoding-logic-use-the-chain-of-responsibility-instead-62146c9cf93a
- https://en.wikipedia.org/wiki/Chain-of-responsibility_pattern
- https://www.javaguides.net/2023/10/chain-of-responsibility-design-pattern-in-kotlin.html
- https://www.geeksforgeeks.org/system-design/chain-responsibility-design-pattern/
- https://sourcemaking.com/design_patterns/chain-of-responsibility
- https://refactoring.guru/design-patterns/chain-of-responsibility
- https://softwarepatterns.com/kotlin/chain-of-responsibility-software-pattern-kotlin-example
