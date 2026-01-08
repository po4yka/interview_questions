---\
id: kotlin-142
title: "Context Receivers / Context Receivers"
aliases: ["Context Receivers in Kotlin", "Context Receivers", "Контекстные получатели в Kotlin", "Контекстные получатели"]
topic: kotlin
subtopics: [c-kotlin, c-kotlin-features]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, c-kotlin-features, q-actor-pattern--kotlin--hard]
created: 2025-10-15
updated: 2025-11-09
tags: [advanced, context-receivers, difficulty/hard, dsl, kotlin, receivers, scope-functions]
---\
# Вопрос (RU)
> Объясните context receivers в Kotlin. Чем они отличаются от extension receivers? Приведите примеры DSL.

---

# Question (EN)
> Explain context receivers in Kotlin. How do they differ from extension receivers? Provide DSL examples.

## Ответ (RU)

**`Context` Receivers** — это (начиная с Kotlin 2.0) стабильная языковая функция, которая позволяет функциям и свойствам объявлять явные контексты и, в частности, требовать несколько типов получателей одновременно. Это позволяет строить более выразительные DSL и более чисто передавать зависимости без параметров в сигнатуре.

Ниже — подробные примеры и сравнение, параллельные EN-версии.

---

### Extension Receivers (Традиционные)

```kotlin
// Extension-функция: один получатель
fun String.shout(): String {
    return this.uppercase() + "!"
}

// Использование
"hello".shout() // "HELLO!"
```

**Ограничение:** только ОДИН тип получателя:

```kotlin
class Logger { fun log(message: String) { println(message) } }
class Config { val prefix = "[APP]" }

// Можно расширять только один тип
fun Logger.logWithPrefix(message: String, config: Config) {
    // Приходится явно передавать config параметром
    log("${config.prefix} $message")
}
```

---

### Context Receivers (Новые)

Позволяют объявлять несколько контекстных получателей:

```kotlin
class Logger { fun log(message: String) { println(message) } }
class Config(val prefix: String)

context(Logger, Config)
fun logMessage(message: String) {
    // Logger и Config доступны как неявные получатели
    log("$prefix $message")
}

// Один из стилей использования с явным предоставлением контекстов
fun useLogMessage() {
    val logger = Logger()
    val config = Config("[APP]")

    with(logger) {
        with(config) {
            logMessage("Hello")
        }
    }
}
```

Также можно использовать функции с типами `context`-функций вместо вложенных `with` — вложенные `with` выше лишь один из возможных стилей.

---

### Базовый Пример С Несколькими Контекстами

```kotlin
class Logger {
    fun log(message: String) {
        println("[LOG] $message")
    }
}

class Database {
    fun query(sql: String): List<String> {
        println("Executing query: $sql")
        return listOf("Result1", "Result2")
    }
}

// Функция с несколькими контекстами
context(Logger, Database)
fun fetchAndLog(sql: String) {
    log("Executing query: $sql")
    val results = query(sql)
    log("Found ${results.size} results")
}

// Использование
fun demoFetchAndLog() {
    val logger = Logger()
    val database = Database()

    with(logger) {
        with(database) {
            fetchAndLog("SELECT * FROM users")
        }
    }
}
```

---

### Context Receivers Vs Extension Receivers (Сравнение)

| Характеристика          | Extension Receiver            | `Context` Receiver                        |
|-------------------------|------------------------------|-----------------------------------------|
| Количество              | Ровно 1                      | 1 или более контекстов                  |
| Синтаксис               | `Type.function()`            | `context(Type1, Type2)` перед объявлением |
| Стиль вызова            | `receiver.function()`        | Любой стиль, обеспечивающий контексты (`with`, context-функции и т.п.) |
| Доступ                  | `this` или неявный получатель | Неявные получатели из объявленных контекстов |
| Зрелость фичи           | Стабильно                    | Стабильно (раньше было экспериментально) |

---

### DSL-пример: HTML Builder (упрощенный)

Ниже пример того, как context receivers помогают структурировать HTML-DSL. Код параллелен EN-версии и демонстрирует один из возможных стилей использования (не единственный идиоматический).

```kotlin
@DslMarker
annotation class HtmlDsl

@HtmlDsl
class HtmlDocument {
    private val elements = mutableListOf<Element>()

    fun render(): String = elements.joinToString("\n") { it.render() }

    fun addElement(element: Element) {
        elements.add(element)
    }
}

@HtmlDsl
class Element(private val name: String) {
    private val children = mutableListOf<Element>()
    private val attributes = mutableMapOf<String, String>()
    private var textContent: String? = null

    fun attribute(name: String, value: String) {
        attributes[name] = value
    }

    fun text(content: String) {
        textContent = content
    }

    fun addChild(element: Element) {
        children.add(element)
    }

    fun render(): String {
        val attrs = attributes.entries.joinToString(" ") { "${it.key}=\"${it.value}\"" }
        val attrsStr = if (attrs.isNotEmpty()) " $attrs" else ""
        val inner = textContent ?: children.joinToString("") { it.render() }
        return "<$name$attrsStr>$inner</$name>"
    }
}

// Функции с context receivers для построения дерева
context(HtmlDocument)
fun html(block: context(Element) () -> Unit) {
    val root = Element("html")
    with(root) { block() }
    addElement(root)
}

context(Element)
fun head(block: context(Element) () -> Unit) {
    val element = Element("head")
    with(element) { block() }
    addChild(element)
}

context(Element)
fun body(block: context(Element) () -> Unit) {
    val element = Element("body")
    with(element) { block() }
    addChild(element)
}

context(Element)
fun h1(text: String, block: (context(Element) () -> Unit)? = null) {
    val element = Element("h1")
    with(element) {
        this.text(text)
        block?.invoke()
    }
    addChild(element)
}

context(Element)
fun p(text: String) {
    val element = Element("p")
    element.text(text)
    addChild(element)
}

// Использование
fun buildPage(): String {
    val document = HtmlDocument()

    with(document) {
        html {
            head {
                // например, title/meta
            }
            body {
                h1("Welcome") {
                    attribute("class", "header")
                }
                p("This is a paragraph")
            }
        }
    }

    return document.render()
}
```

Этот пример показывает, как context receivers ограничивают использование builder-функций корректными областями видимости.

---

### DSL-пример: SQL Query Builder

Упрощенный пример с одним контекстом (`Database`), аналогичный EN-версии:

```kotlin
class Database {
    fun execute(sql: String): List<Map<String, Any?>> {
        println("Executing: $sql")
        return emptyList()
    }
}

class QueryBuilder {
    private var selectClause = "*"
    private var fromClause = ""
    private var whereClause: String? = null

    fun select(columns: String) {
        selectClause = columns
    }

    fun from(table: String) {
        fromClause = table
    }

    fun where(condition: String) {
        whereClause = condition
    }

    fun build(): String {
        val base = "SELECT $selectClause FROM $fromClause"
        val where = whereClause?.let { " WHERE $it" } ?: ""
        return base + where
    }
}

context(Database)
fun query(block: QueryBuilder.() -> Unit): List<Map<String, Any?>> {
    val builder = QueryBuilder().apply(block)
    return execute(builder.build())
}

// Использование
fun demoQuery() {
    val database = Database()

    with(database) {
        val results = query {
            select("name, email")
            from("users")
            where("age > 18")
        }
        println("Rows: ${results.size}")
    }
}
```

---

### Context Receivers Для Dependency Injection

Полный пример, зеркалирующий EN-версию:

```kotlin
data class User(val id: Int, val name: String, val email: String)

interface Logger {
    fun log(message: String)
}

interface UserRepository {
    fun findUser(id: Int): User?
}

interface EmailService {
    fun sendEmail(to: String, subject: String, body: String)
}

class ConsoleLogger : Logger {
    override fun log(message: String) {
        println("[LOG] $message")
    }
}

class InMemoryUserRepository : UserRepository {
    private val users = listOf(User(123, "Alice", "alice@example.com"))
    override fun findUser(id: Int): User? = users.find { it.id == id }
}

class SmtpEmailService : EmailService {
    override fun sendEmail(to: String, subject: String, body: String) {
        println("Sending email to $to: $subject -> $body")
    }
}

// Сервис с context receivers: все зависимости описаны как контекст
context(Logger, UserRepository, EmailService)
class UserService {
    fun sendWelcomeEmail(userId: Int) {
        log("Sending welcome email to user $userId")

        val user = findUser(userId)
        if (user != null) {
            sendEmail(
                to = user.email,
                subject = "Welcome!",
                body = "Welcome ${user.name}!"
            )
            log("Email sent successfully")
        } else {
            log("User not found: $userId")
        }
    }
}

// Использование
fun demoUserService() {
    val logger = ConsoleLogger()
    val repository = InMemoryUserRepository()
    val emailService = SmtpEmailService()

    with(logger) {
        with(repository) {
            with(emailService) {
                val userService = UserService()
                userService.sendWelcomeEmail(123)
            }
        }
    }
}
```

Этот пример показывает, как context receivers позволяют явно выразить зависимости без конструкторов/локаторов сервисов.

---

### Лучшие Практики

1. Используйте `@DslMarker` для предотвращения утечки областей видимости в сложных DSL:

```kotlin
@DslMarker
annotation class BuilderDsl

@BuilderDsl
class InnerBuilder

@BuilderDsl
class OuterBuilder {
    // Пример: функции, зависящие от контекста InnerBuilder
    context(InnerBuilder)
    fun innerSpecificOperation() {
        // ... операции, требующие InnerBuilder как контекст
    }
}
```

1. Предоставляйте удобные функции-обертки, скрывающие детали создания контекста:

```kotlin
// Хелпер, оборачивающий настройку контекста
fun buildHtml(block: context(HtmlDocument) () -> Unit): String {
    val document = HtmlDocument()
    with(document) { block() }
    return document.render()
}

// Использование становится чище
val html = buildHtml {
    html {
        body {
            h1("Hello")
        }
    }
}
```

1. Не злоупотребляйте: слишком много контекстов ухудшает читаемость. Группируйте связанные зависимости:

```kotlin
// Плохо: слишком много контекстов
context(Logger, Database, Cache, Config, Metrics, Auth, EmailService)
fun complexFunction() {
    // Сложно поддерживать и тестировать
}

// Лучше: сгруппировать в единый контекст
class Cache

class ServiceContext(
    val logger: Logger,
    val database: Database,
    val cache: Cache
)

context(ServiceContext)
fun betterFunction() {
    logger.log("...")
    // database, cache тоже доступны через контекст
}
```

`Context` receivers — мощный инструмент для создания выразительных DSL и явного описания зависимостей в Kotlin. См. также [[c-kotlin]] и [[c-kotlin-features]].

## Answer (EN)

`Context` receivers are (as of Kotlin 2.0) a stable language feature that allows functions and properties to declare explicit contexts and, in particular, require multiple receiver-like types simultaneously. This enables more expressive DSLs and cleaner dependency handling without threading parameters through every call.

---

### Extension Receivers (Traditional)

```kotlin
// Extension function: single receiver
fun String.shout(): String {
    return this.uppercase() + "!"
}

// Usage
"hello".shout() // "HELLO!"
```

**Limitation:** Only ONE receiver type allowed:

```kotlin
class Logger { fun log(message: String) { println(message) } }
class Config { val prefix = "[APP]" }

// Can only extend one type
fun Logger.logWithPrefix(message: String, config: Config) {
    // Need to pass config as parameter explicitly
    log("${config.prefix} $message")
}
```

---

### Context Receivers (New)

Enable multiple context receivers:

```kotlin
class Logger { fun log(message: String) { println(message) } }
class Config(val prefix: String)

context(Logger, Config)
fun logMessage(message: String) {
    // Both Logger and Config are available as implicit receivers
    log("$prefix $message")
}

// Usage with explicit contexts (one possible style)
fun useLogMessage() {
    val logger = Logger()
    val config = Config("[APP]")

    with(logger) {
        with(config) {
            logMessage("Hello")
        }
    }
}
```

Note: You can also use functions that take context function types instead of nesting `with` blocks; nested `with` is just one possible style.

---

### Basic Context Receiver Example

```kotlin
class Logger {
    fun log(message: String) {
        println("[LOG] $message")
    }
}

class Database {
    fun query(sql: String): List<String> {
        println("Executing query: $sql")
        return listOf("Result1", "Result2")
    }
}

// Function with multiple contexts
context(Logger, Database)
fun fetchAndLog(sql: String) {
    log("Executing query: $sql")
    val results = query(sql)
    log("Found ${results.size} results")
}

// Usage
fun demoFetchAndLog() {
    val logger = Logger()
    val database = Database()

    with(logger) {
        with(database) {
            fetchAndLog("SELECT * FROM users")
        }
    }
}
```

---

### Context Receivers Vs Extension Receivers

| Feature | Extension Receiver | `Context` Receiver |
|---------|-------------------|------------------|
| **Count** | Exactly 1 | One or more contexts |
| **Syntax** | `Type.function()` | `context(Type1, Type2)` before declaration |
| **`Call` site** | `receiver.function()` | Any style that provides required receivers (e.g. nested `with`, or context functions) |
| **Access** | `this` or implicit | Implicit receivers from declared contexts |
| **Maturity** | Stable | Stable (was experimental in earlier versions) |

---

### DSL Example: HTML Builder (Simplified)

Below is an example of how context receivers can structure an HTML DSL. It mirrors the RU version and demonstrates one possible usage style (not the only idiomatic one).

```kotlin
@DslMarker
annotation class HtmlDsl

@HtmlDsl
class HtmlDocument {
    private val elements = mutableListOf<Element>()

    fun render(): String = elements.joinToString("\n") { it.render() }

    fun addElement(element: Element) {
        elements.add(element)
    }
}

@HtmlDsl
class Element(private val name: String) {
    private val children = mutableListOf<Element>()
    private val attributes = mutableMapOf<String, String>()
    private var textContent: String? = null

    fun attribute(name: String, value: String) {
        attributes[name] = value
    }

    fun text(content: String) {
        textContent = content
    }

    fun addChild(element: Element) {
        children.add(element)
    }

    fun render(): String {
        val attrs = attributes.entries.joinToString(" ") { "${it.key}=\"${it.value}\"" }
        val attrsStr = if (attrs.isNotEmpty()) " $attrs" else ""
        val inner = textContent ?: children.joinToString("") { it.render() }
        return "<$name$attrsStr>$inner</$name>"
    }
}

// Context receiver functions for building the tree
context(HtmlDocument)
fun html(block: context(Element) () -> Unit) {
    val root = Element("html")
    with(root) { block() }
    addElement(root)
}

context(Element)
fun head(block: context(Element) () -> Unit) {
    val element = Element("head")
    with(element) { block() }
    addChild(element)
}

context(Element)
fun body(block: context(Element) () -> Unit) {
    val element = Element("body")
    with(element) { block() }
    addChild(element)
}

context(Element)
fun h1(text: String, block: (context(Element) () -> Unit)? = null) {
    val element = Element("h1")
    with(element) {
        this.text(text)
        block?.invoke()
    }
    addChild(element)
}

context(Element)
fun p(text: String) {
    val element = Element("p")
    element.text(text)
    addChild(element)
}

// Usage
fun buildPage(): String {
    val document = HtmlDocument()

    with(document) {
        html {
            head {
                // e.g., title/meta tags
            }
            body {
                h1("Welcome") {
                    attribute("class", "header")
                }
                p("This is a paragraph")
            }
        }
    }

    return document.render()
}
```

---

### DSL Example: SQL Query Builder

```kotlin
class Database {
    fun execute(sql: String): List<Map<String, Any?>> {
        println("Executing: $sql")
        return emptyList()
    }
}

class QueryBuilder {
    private var selectClause = "*"
    private var fromClause = ""
    private var whereClause: String? = null

    fun select(columns: String) {
        selectClause = columns
    }

    fun from(table: String) {
        fromClause = table
    }

    fun where(condition: String) {
        whereClause = condition
    }

    fun build(): String {
        val base = "SELECT $selectClause FROM $fromClause"
        val where = whereClause?.let { " WHERE $it" } ?: ""
        return base + where
    }
}

context(Database)
fun query(block: QueryBuilder.() -> Unit): List<Map<String, Any?>> {
    val builder = QueryBuilder().apply(block)
    return execute(builder.build())
}

// Usage
fun demoQuery() {
    val database = Database()

    with(database) {
        val results = query {
            select("name, email")
            from("users")
            where("age > 18")
        }
        println("Rows: ${results.size}")
    }
}
```

---

### Context Receivers for Dependency Injection

```kotlin
data class User(val id: Int, val name: String, val email: String)

interface Logger {
    fun log(message: String)
}

interface UserRepository {
    fun findUser(id: Int): User?
}

interface EmailService {
    fun sendEmail(to: String, subject: String, body: String)
}

class ConsoleLogger : Logger {
    override fun log(message: String) {
        println("[LOG] $message")
    }
}

class InMemoryUserRepository : UserRepository {
    private val users = listOf(User(123, "Alice", "alice@example.com"))
    override fun findUser(id: Int): User? = users.find { it.id == id }
}

class SmtpEmailService : EmailService {
    override fun sendEmail(to: String, subject: String, body: String) {
        println("Sending email to $to: $subject -> $body")
    }
}

// Service with context receivers: all dependencies are explicit contexts
context(Logger, UserRepository, EmailService)
class UserService {
    fun sendWelcomeEmail(userId: Int) {
        log("Sending welcome email to user $userId")

        val user = findUser(userId)
        if (user != null) {
            sendEmail(
                to = user.email,
                subject = "Welcome!",
                body = "Welcome ${user.name}!"
            )
            log("Email sent successfully")
        } else {
            log("User not found: $userId")
        }
    }
}

// Usage
fun demoUserService() {
    val logger = ConsoleLogger()
    val repository = InMemoryUserRepository()
    val emailService = SmtpEmailService()

    with(logger) {
        with(repository) {
            with(emailService) {
                val userService = UserService()
                userService.sendWelcomeEmail(123)
            }
        }
    }
}
```

---

### Best Practices

1. Use `@DslMarker` to prevent scope leakage in complex DSLs:

```kotlin
@DslMarker
annotation class BuilderDsl

@BuilderDsl
class InnerBuilder

@BuilderDsl
class OuterBuilder {
    // Example: functions that rely on an InnerBuilder context
    context(InnerBuilder)
    fun innerSpecificOperation() {
        // ... operations that require InnerBuilder as context
    }
}
```

1. Provide convenience functions to hide context wiring:

```kotlin
fun buildHtml(block: context(HtmlDocument) () -> Unit): String {
    val document = HtmlDocument()
    with(document) { block() }
    return document.render()
}

val html = buildHtml {
    html {
        body {
            h1("Hello")
        }
    }
}
```

1. Don't overuse: group related contexts into cohesive holders:

```kotlin
context(Logger, Database, Cache, Config, Metrics, Auth, EmailService)
fun complexFunction() {
    // Too complex and fragile
}

class Cache

class ServiceContext(
    val logger: Logger,
    val database: Database,
    val cache: Cache
)

context(ServiceContext)
fun betterFunction() {
    logger.log("...")
    // database, cache available via the context
}
```

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия context receivers от Java-подходов к передаче контекста/зависимостей?
- В каких практических сценариях вы бы применили context receivers?
- Какие типичные ошибки и подводные камни при использовании context receivers?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- Документация Kotlin по context receivers: https://kotlinlang.org/docs/context-receivers.html
- [[c-kotlin]]
- [[c-kotlin-features]]

## References

- Kotlin Documentation: https://kotlinlang.org/docs/context-receivers.html
- [[c-kotlin]]
- [[c-kotlin-features]]

## Связанные Вопросы (RU)

- [[q-actor-pattern--kotlin--hard]]

## Related Questions

- [[q-actor-pattern--kotlin--hard]]
- [[q-infix-functions--kotlin--medium]]
- [[q-coroutine-exception-handling--kotlin--medium]]
