---
tags:
  - kotlin
  - dsl
  - type-safety
  - scope-functions
  - dsl-marker
  - builders
difficulty: hard
status: draft
---

# Creating Type-Safe DSLs in Kotlin

# Question (EN)
> Design and implement a type-safe DSL for building UI components. Use scope control, extension lambdas, and @DslMarker.

# Вопрос (RU)
> Разработайте и реализуйте типобезопасный DSL для построения UI компонентов. Используйте контроль области видимости, extension лямбды и @DslMarker.

---

## Answer (EN)

A **DSL (Domain-Specific Language)** in Kotlin uses language features like lambdas with receivers, extension functions, and operator overloading to create expressive, type-safe APIs.

---

### Basic DSL Structure

```kotlin
class HtmlBuilder {
    private val elements = mutableListOf<String>()

    fun html(block: HtmlTag.() -> Unit): String {
        val tag = HtmlTag("html")
        tag.block()
        elements.add(tag.render())
        return elements.joinToString()
    }
}

class HtmlTag(private val name: String) {
    private val children = mutableListOf<String>()
    private val attributes = mutableMapOf<String, String>()

    fun tag(name: String, block: HtmlTag.() -> Unit) {
        val child = HtmlTag(name)
        child.block()
        children.add(child.render())
    }

    fun attribute(key: String, value: String) {
        attributes[key] = value
    }

    fun text(content: String) {
        children.add(content)
    }

    fun render(): String {
        val attrs = attributes.entries.joinToString(" ") { "${it.key}=\"${it.value}\"" }
        val attrsStr = if (attrs.isNotEmpty()) " $attrs" else ""
        return "<$name$attrsStr>${children.joinToString()}</$name>"
    }
}

// Usage
fun buildPage() = HtmlBuilder().html {
    tag("head") {
        tag("title") {
            text("My Page")
        }
    }
    tag("body") {
        tag("h1") {
            attribute("class", "header")
            text("Welcome!")
        }
    }
}
```

---

### @DslMarker for Scope Control

Prevents implicit receiver scope leakage:

```kotlin
@DslMarker
annotation class HtmlDsl

@HtmlDsl
class HtmlBuilder { /* ... */ }

@HtmlDsl
class HtmlTag { /* ... */ }

// Now this is an error:
html {
    tag("div") {
        tag("p") {
            // ❌ Cannot access outer html scope directly
            // Prevents: html { }
        }
    }
}
```

---

### Complete Type-Safe UI DSL

```kotlin
@DslMarker
annotation class UiDsl

@UiDsl
abstract class Component {
    abstract fun render(): String
}

@UiDsl
class Container : Component() {
    private val children = mutableListOf<Component>()

    fun add(component: Component) {
        children.add(component)
    }

    override fun render(): String {
        return children.joinToString("\n") { it.render() }
    }
}

@UiDsl
class Button(
    private val text: String,
    private val onClick: () -> Unit
) : Component() {
    override fun render() = "<button>$text</button>"
}

@UiDsl
class Text(private val content: String) : Component() {
    override fun render() = "<p>$content</p>"
}

// DSL Functions
fun ui(block: Container.() -> Unit): Container {
    val container = Container()
    container.block()
    return container
}

fun Container.button(text: String, onClick: () -> Unit) {
    add(Button(text, onClick))
}

fun Container.text(content: String) {
    add(Text(content))
}

fun Container.column(block: Container.() -> Unit) {
    val container = Container()
    container.block()
    add(container)
}

// Usage
val page = ui {
    text("Welcome!")

    column {
        button("Click Me") {
            println("Clicked!")
        }

        button("Cancel") {
            println("Cancelled")
        }
    }
}
```

---

### Advanced DSL: SQL Query Builder

```kotlin
@DslMarker
annotation class SqlDsl

@SqlDsl
class Query {
    private var selectClause = ""
    private var fromClause = ""
    private var whereClause = ""
    private var orderClause = ""

    fun select(columns: String) {
        selectClause = columns
    }

    fun from(table: String) {
        fromClause = table
    }

    fun where(block: WhereBuilder.() -> String) {
        val builder = WhereBuilder()
        whereClause = builder.block()
    }

    fun orderBy(column: String) {
        orderClause = column
    }

    fun build(): String {
        return buildString {
            append("SELECT $selectClause")
            append(" FROM $fromClause")
            if (whereClause.isNotEmpty()) append(" WHERE $whereClause")
            if (orderClause.isNotEmpty()) append(" ORDER BY $orderClause")
        }
    }
}

@SqlDsl
class WhereBuilder {
    infix fun String.eq(value: Any): String = "$this = '$value'"
    infix fun String.gt(value: Any): String = "$this > $value"
    infix fun String.lt(value: Any): String = "$this < $value"
    infix fun String.and(other: String): String = "$this AND $other"
    infix fun String.or(other: String): String = "$this OR $other"
}

fun query(block: Query.() -> Unit): String {
    val query = Query()
    query.block()
    return query.build()
}

// Usage
val sql = query {
    select("name, email, age")
    from("users")
    where {
        ("age" gt 18) and ("status" eq "active")
    }
    orderBy("name")
}
// SELECT name, email, age FROM users WHERE age > 18 AND status = 'active' ORDER BY name
```

---

### Best Practices

**1. Use @DslMarker:**

```kotlin
@DslMarker
annotation class BuilderDsl

@BuilderDsl
class Builder { /* ... */ }
```

**2. Extension lambdas with receivers:**

```kotlin
// ✅ DO: Lambda with receiver
fun tag(name: String, block: Tag.() -> Unit)

// ❌ DON'T: Regular lambda
fun tag(name: String, block: (Tag) -> Unit)
```

**3. Type-safe builders:**

```kotlin
// ✅ DO: Type constraints
fun Container.button(text: String, onClick: () -> Unit) {
    add(Button(text, onClick))
}

// ❌ DON'T: Accept any type
fun Container.add(component: Any)
```

---

## Ответ (RU)

**DSL (Domain-Specific Language)** в Kotlin использует возможности языка, такие как лямбды с получателями, extension функции и перегрузку операторов для создания выразительных, типобезопасных API.

### Базовая структура DSL

Использует лямбды с получателями: `block: HtmlTag.() -> Unit`.

### @DslMarker для контроля области

Предотвращает утечку области видимости неявных получателей.

### Полный типобезопасный UI DSL

Включает Container, Component, и функции построения как `button`, `text`, `column`.

### Продвинутый DSL: SQL Query Builder

Использует infix функции для SQL операторов: `"age" gt 18`.

### Лучшие практики

1. Используйте @DslMarker
2. Extension лямбды с получателями
3. Типобезопасные builders

DSL в Kotlin обеспечивают выразительные, типобезопасные API для специфических доменов.
