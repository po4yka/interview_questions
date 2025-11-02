---
id: kotlin-142
title: "Context Receivers / Context Receivers"
aliases: [Context Receivers, Context Receivers]
topic: kotlin
subtopics: [type-system, advanced-features]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en]
status: draft
moc: moc-kotlin
related: [q-infix-functions--kotlin--medium, q-kotlin-conversion-functions--programming-languages--medium, q-coroutine-exception-handling--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags:
  - kotlin
  - context-receivers
  - dsl
  - advanced
  - receivers
  - scope-functions
  - difficulty/hard
---
# Context Receivers in Kotlin

# Question (EN)
> Explain context receivers in Kotlin. How do they differ from extension receivers? Provide DSL examples.

# Вопрос (RU)
> Объясните context receivers в Kotlin. Чем они отличаются от extension receivers? Приведите примеры DSL.

---

## Answer (EN)

**Context Receivers** are an experimental Kotlin feature that allows functions and properties to require multiple receiver types simultaneously, enabling more expressive DSLs and cleaner dependency injection.

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
//  Cannot have multiple receivers traditionally
class Logger { fun log(message: String) { println(message) } }
class Config { val prefix = "[APP]" }

// Can only extend one type
fun Logger.logWithPrefix(message: String, config: Config) {
    // Need to pass config as parameter
    log("${config.prefix} $message")
}
```

---

### Context Receivers (New)

Enable multiple receiver types:

```kotlin
context(Logger, Config)
fun logMessage(message: String) {
    // Both Logger and Config available as receivers
    log("$prefix $message")
}

// Usage
with(Logger()) {
    with(Config()) {
        logMessage("Hello") // Both contexts available
    }
}
```

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
fun main() {
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

### Context Receivers vs Extension Receivers

| Feature | Extension Receiver | Context Receiver |
|---------|-------------------|------------------|
| **Count** | Exactly 1 | Multiple |
| **Syntax** | `Type.function()` | `context(Type1, Type2)` |
| **Call site** | `receiver.function()` | `with(receiver1) { with(receiver2) { } }` |
| **Access** | `this` or implicit | Implicit |
| **Maturity** | Stable | Experimental |

---

### DSL Example: HTML Builder

**Without context receivers:**

```kotlin
class HtmlBuilder {
    private val content = StringBuilder()

    fun html(block: HtmlTag.() -> Unit): String {
        val tag = HtmlTag("html")
        tag.block()
        return tag.render()
    }
}

class HtmlTag(private val name: String) {
    private val children = mutableListOf<HtmlTag>()
    private val attributes = mutableMapOf<String, String>()

    fun tag(name: String, block: HtmlTag.() -> Unit) {
        val child = HtmlTag(name)
        child.block()
        children.add(child)
    }

    fun attribute(name: String, value: String) {
        attributes[name] = value
    }

    fun text(content: String) {
        children.add(HtmlTag("text").apply {
            this.content = content
        })
    }
}

// Usage - nested contexts awkward
fun buildPage() {
    HtmlBuilder().html {
        tag("head") {
            tag("title") {
                text("My Page")
            }
        }
        tag("body") {
            tag("h1") {
                attribute("class", "header")
                text("Welcome")
            }
        }
    }
}
```

**With context receivers:**

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

    fun render(): String {
        val attrs = attributes.entries.joinToString(" ") { "${it.key}=\"${it.value}\"" }
        val attrsStr = if (attrs.isNotEmpty()) " $attrs" else ""
        val childrenStr = children.joinToString("") { it.render() }
        val content = textContent ?: childrenStr

        return "<$name$attrsStr>$content</$name>"
    }

    fun addChild(element: Element) {
        children.add(element)
    }
}

// Context receiver functions
context(HtmlDocument)
fun html(block: context(Element) () -> Unit) {
    val element = Element("html")
    block(element)
    addElement(element)
}

context(Element)
fun head(block: context(Element) () -> Unit) {
    val element = Element("head")
    block(element)
    addChild(element)
}

context(Element)
fun body(block: context(Element) () -> Unit) {
    val element = Element("body")
    block(element)
    addChild(element)
}

context(Element)
fun h1(text: String, block: (context(Element) () -> Unit)? = null) {
    val element = Element("h1")
    element.text(text)
    block?.invoke(element)
    addChild(element)
}

context(Element)
fun p(text: String) {
    val element = Element("p")
    element.text(text)
    addChild(element)
}

// Usage - cleaner!
fun buildPage(): String {
    val document = HtmlDocument()

    with(document) {
        html {
            head {
                // title, meta, etc.
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
    fun execute(sql: String): List<Map<String, Any>> {
        println("Executing: $sql")
        return emptyList()
    }
}

class QueryBuilder {
    private var selectClause = ""
    private var fromClause = ""
    private var whereClause = ""

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
        return "SELECT $selectClause FROM $fromClause WHERE $whereClause"
    }
}

context(Database)
fun query(block: QueryBuilder.() -> Unit): List<Map<String, Any>> {
    val builder = QueryBuilder()
    builder.block()
    return execute(builder.build())
}

// Usage
fun main() {
    val database = Database()

    with(database) {
        val results = query {
            select("name, email")
            from("users")
            where("age > 18")
        }
    }
}
```

---

### Context Receivers for Dependency Injection

```kotlin
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

// Service with context receivers
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
fun main() {
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

**1. Use @DslMarker to prevent scope leakage:**

```kotlin
@DslMarker
annotation class BuilderDsl

@BuilderDsl
class OuterBuilder {
    context(InnerBuilder)
    fun inner(block: context(InnerBuilder) () -> Unit) {
        // ...
    }
}
```

**2. Provide convenience functions:**

```kotlin
//  DO: Provide helper
fun buildHtml(block: context(HtmlDocument) () -> Unit): String {
    val document = HtmlDocument()
    block(document)
    return document.render()
}

// Usage is cleaner
val html = buildHtml {
    html {
        body {
            h1("Hello")
        }
    }
}
```

**3. Don't overuse:**

```kotlin
//  DON'T: Too many contexts
context(Logger, Database, Cache, Config, Metrics, Auth, EmailService)
fun complexFunction() {
    // Too complex!
}

//  DO: Group related contexts
class ServiceContext(
    val logger: Logger,
    val database: Database,
    val cache: Cache
)

context(ServiceContext)
fun betterFunction() {
    logger.log("...")
}
```

---

## Ответ (RU)

**Context Receivers** — это экспериментальная функция Kotlin, которая позволяет функциям и свойствам требовать несколько типов получателей одновременно, обеспечивая более выразительные DSL и более чистое внедрение зависимостей.

### Extension Receivers (Традиционные)

Позволяют только ОДИН тип получателя. Ограничение в выразительности для сложных случаев.

### Context Receivers (Новые)

Позволяют несколько типов получателей одновременно, используя синтаксис `context(Type1, Type2)`.

### Сравнение

Extension receivers: ровно 1, стабильны.
Context receivers: множество, экспериментальны.

### Примеры DSL

HTML builder, SQL query builder, dependency injection - все становятся чище с context receivers.

### Лучшие практики

1. Используйте @DslMarker для предотвращения утечки области видимости
2. Предоставляйте convenience функции
3. Не злоупотребляйте - слишком много контекстов усложняет код

Context receivers - мощный инструмент для создания выразительных DSL в Kotlin.

## Related Questions

- [[q-infix-functions--kotlin--medium]]
- [[q-kotlin-conversion-functions--programming-languages--medium]]
- [[q-coroutine-exception-handling--kotlin--medium]]
