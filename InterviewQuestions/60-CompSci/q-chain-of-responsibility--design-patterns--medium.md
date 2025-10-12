---
tags:
  - design-patterns
  - behavioral-patterns
  - chain-of-responsibility
  - gof-patterns
  - chain-pattern
difficulty: medium
status: draft
---

# Chain of Responsibility Pattern

# Question (EN)
> What is the Chain of Responsibility pattern? When and why should it be used?

# Вопрос (RU)
> Что такое паттерн Chain of Responsibility? Когда и зачем его использовать?

---

## Answer (EN)


**Chain of Responsibility (Цепочка обязанностей)** - это поведенческий паттерн проектирования, который позволяет передавать запросы последовательно по цепочке обработчиков. Каждый последующий обработчик решает, может ли он обработать запрос сам и стоит ли передавать запрос дальше по цепи.

### Definition


Chain of Responsibility is a design pattern in which **a request is passed sequentially through a chain of potential handlers until one of them handles the request**. Each handler in the chain has a chance to either process the request or pass it to the next handler. The client doesn't need to know which handler will actually deal with the request — it simply sends it into the chain.

This pattern decouples the client from the specific receiver that performs the action, following the Open/Closed Principle by allowing new handlers to be added without modifying existing code.

### Problems it Solves


What problems can the Chain of Responsibility design pattern solve?

1. **Coupling the sender of a request to its receiver should be avoided**
2. **It should be possible that more than one receiver can handle a request**
3. **Implementing a request directly within the class is inflexible** - Couples the class to a particular receiver

### Solution


Define a **chain of receiver objects** having the responsibility, depending on run-time conditions, to either **handle a request or forward it to the next receiver** on the chain (if any).

This enables us to send a request to a chain of receivers without having to know which one handles the request. The request gets passed along the chain until a receiver handles the request. The sender of a request is no longer coupled to a particular receiver.

## Когда использовать?

You might consider using Chain of Responsibility when:

1. **Multiple handlers for a type of request** - Which one handles it may depend on runtime conditions (e.g., UI event propagation)
2. **Avoid monolithic conditional logic** - Replace big if/else or when chains with separate handler classes
3. **Flexible chains** - Need chains that can be extended or reordered dynamically

## Пример: Request Handlers

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

**Output**:
```
FirstHandler handled Request1
SecondHandler handled Request2
DefaultHandler handled Request3
```

## Android Example: View Event Handling

```kotlin
// Touch event chain
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

## Kotlin Example: Validation Chain

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

## Android Interceptor Chain Example

```kotlin
// OkHttp-style interceptor chain
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
            // End of chain - make actual request
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

### Explanation


**Explanation**:

- **Handler interface** declares methods for handling and chaining
- **Concrete handlers** check if they can handle request, otherwise pass to next
- **Chain** is built by linking handlers together
- **Android**: View event handling, OkHttp interceptors, validation chains
- Each handler can **modify** the request or **stop** the chain

## Преимущества и недостатки

### Pros (Преимущества)


1. **Decoupling** - Sender doesn't need to know which handler processes request
2. **Flexibility** - Can add/remove/reorder handlers easily
3. **Single Responsibility** - Each handler handles one type of request
4. **Dynamic configuration** - Chain can be modified at runtime
5. **Open/Closed Principle** - New handlers without modifying existing code

### Cons (Недостатки)


1. **No guarantee of handling** - Request might not be handled at all
2. **Performance overhead** - Request passes through multiple handlers
3. **Debugging difficulty** - Hard to track request flow
4. **Runtime complexity** - Dynamic chains can be hard to manage

## Best Practices

```kotlin
// - DO: Provide a default handler at the end
class DefaultHandler : Handler {
    override var nextHandler: Handler? = null
    override fun handleRequest(request: String): Boolean {
        println("Default: No specific handler for $request")
        return true // Always handles
    }
}

// - DO: Use for UI event propagation
class ViewGroup {
    private val childHandlers = mutableListOf<ViewEventHandler>()

    fun dispatchTouchEvent(event: MotionEvent): Boolean {
        return childHandlers.any { it.onTouchEvent(event) }
    }
}

// - DO: Make chain immutable after creation
fun buildChain(): Handler {
    return FirstHandler().apply {
        nextHandler = SecondHandler().apply {
            nextHandler = DefaultHandler()
        }
    }
}

// - DO: Use functional approach in Kotlin
val validationChain = listOf<(UserData) -> Boolean>(
    { it.email.isNotBlank() },
    { it.password.length >= 8 },
    { it.age >= 18 }
)

fun validate(data: UserData) = validationChain.all { it(data) }

// - DON'T: Create circular chains
// - DON'T: Put business logic in chain construction
// - DON'T: Make handlers depend on each other
```

**English**: **Chain of Responsibility** is a behavioral pattern that passes requests through a chain of handlers until one processes it. **Problem**: Need to avoid coupling sender to specific receiver, multiple potential handlers. **Solution**: Chain handlers together, each decides to process or pass to next. **Use when**: (1) Multiple handlers for requests, (2) Avoid complex conditionals, (3) Need flexible, reconfigurable chains. **Android**: View event handling, OkHttp interceptors, validation chains. **Pros**: decoupling, flexibility, dynamic configuration. **Cons**: no guarantee of handling, performance overhead, debugging difficulty. **Examples**: Touch event propagation, HTTP interceptors, validation pipeline, logging chain.

## Links

- [Stop Hardcoding Logic: Use the Chain of Responsibility Instead](https://maxim-gorin.medium.com/stop-hardcoding-logic-use-the-chain-of-responsibility-instead-62146c9cf93a)
- [Chain-of-responsibility pattern](https://en.wikipedia.org/wiki/Chain-of-responsibility_pattern)
- [Chain of Responsibility Design Pattern in Kotlin](https://www.javaguides.net/2023/10/chain-of-responsibility-design-pattern-in-kotlin.html)
- [Chain of Responsibility Design Pattern](https://www.geeksforgeeks.org/system-design/chain-responsibility-design-pattern/)

## Further Reading

- [Chain of Responsibility](https://sourcemaking.com/design_patterns/chain_of_responsibility)
- [Chain of Responsibility](https://refactoring.guru/design-patterns/chain-of-responsibility)
- [Chain of Responsibility Software Pattern Kotlin Examples](https://softwarepatterns.com/kotlin/chain-of-responsibility-software-pattern-kotlin-example)

---
*Source: Kirchhoff Android Interview Questions*


## Ответ (RU)

### Определение


Chain of Responsibility is a design pattern in which **a request is passed sequentially through a chain of potential handlers until one of them handles the request**. Each handler in the chain has a chance to either process the request or pass it to the next handler. The client doesn't need to know which handler will actually deal with the request — it simply sends it into the chain.

This pattern decouples the client from the specific receiver that performs the action, following the Open/Closed Principle by allowing new handlers to be added without modifying existing code.

### Проблемы, которые решает


What problems can the Chain of Responsibility design pattern solve?

1. **Coupling the sender of a request to its receiver should be avoided**
2. **It should be possible that more than one receiver can handle a request**
3. **Implementing a request directly within the class is inflexible** - Couples the class to a particular receiver

### Решение


Define a **chain of receiver objects** having the responsibility, depending on run-time conditions, to either **handle a request or forward it to the next receiver** on the chain (if any).

This enables us to send a request to a chain of receivers without having to know which one handles the request. The request gets passed along the chain until a receiver handles the request. The sender of a request is no longer coupled to a particular receiver.

### Объяснение


**Explanation**:

- **Handler interface** declares methods for handling and chaining
- **Concrete handlers** check if they can handle request, otherwise pass to next
- **Chain** is built by linking handlers together
- **Android**: View event handling, OkHttp interceptors, validation chains
- Each handler can **modify** the request or **stop** the chain

### Pros (Преимущества)


1. **Decoupling** - Sender doesn't need to know which handler processes request
2. **Flexibility** - Can add/remove/reorder handlers easily
3. **Single Responsibility** - Each handler handles one type of request
4. **Dynamic configuration** - Chain can be modified at runtime
5. **Open/Closed Principle** - New handlers without modifying existing code

### Cons (Недостатки)


1. **No guarantee of handling** - Request might not be handled at all
2. **Performance overhead** - Request passes through multiple handlers
3. **Debugging difficulty** - Hard to track request flow
4. **Runtime complexity** - Dynamic chains can be hard to manage
