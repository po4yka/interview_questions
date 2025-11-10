---
id: kotlin-192
title: "Kotlin Dsl Creation / Создание DSL в Kotlin"
aliases: [Creation, Dsl, Kotlin]
topic: kotlin
subtopics: [coroutines, extensions]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-array-vs-list-kotlin--kotlin--easy]
created: 2025-10-15
updated: 2025-11-09
tags: [difficulty/hard]
---
# Вопрос (RU)
> Разработайте и реализуйте типобезопасный DSL для построения UI компонентов. Используйте контроль области видимости, extension-лямбды и `@DslMarker`.

## Ответ (RU)

**DSL (Domain-Specific Language)** в Kotlin строится на возможностях языка: лямбдах с получателем, extension-функциях, инфиксных и операторных перегрузках. Это позволяет создавать выразительные и типобезопасные API, в том числе для UI.

### Базовая структура DSL

Используем лямбды с получателем: `block: HtmlTag.() -> Unit` — это позволяет внутри блока вызывать методы `HtmlTag` без явного указания объекта.

```kotlin
@DslMarker
annotation class HtmlDsl

@HtmlDsl
class HtmlBuilder {
    private val elements = mutableListOf<String>()

    fun html(block: HtmlTag.() -> Unit): String {
        val tag = HtmlTag("html")
        tag.block()
        elements.add(tag.render())
        return elements.joinToString()
    }
}

@HtmlDsl
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

// Использование
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

### `@DslMarker` для контроля области

`@DslMarker` используется для ограничения выбора неявных получателей и предотвращения случайного обращения к внешнему builder'у из вложенного.

Типичный приём: помечаем все классы одного DSL одной и той же аннотацией. Тогда при наличии нескольких помеченных получателей внутри лямбды компилятор запрещает неявные обращения к внешнему получателю, делая вложенный DSL более безопасным.

### Полный типобезопасный UI DSL

Ниже пример DSL для UI-компонентов с `@UiDsl`, компонентами `Container`, `Button`, `Text` и функциями `button`, `text`, `column`.

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

// DSL-функции
@UiDsl
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

// Использование
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

Такой DSL:
- типобезопасен (работает с `Component` и их подтипами);
- использует лямбды с получателем для декларативного описания дерева;
- с помощью `@UiDsl` предотвращает смешивание контекстов разных уровней UI DSL.

### Продвинутый DSL: SQL Query Builder

Пример другого домена: простой и типобезопасный (на уровне конструкции выражений) SQL DSL с infix-функциями.

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

// Использование
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

Здесь `@SqlDsl` помечает классы DSL; для данного упрощённого примера он в основном демонстрационный. В реальном проекте аннотацию применяют ко всем builder'ам одного DSL, чтобы избежать коллизий с другими DSL в одной области видимости.

### Лучшие практики (RU)

1. Используйте `@DslMarker` для всех сущностей одного DSL, чтобы избежать утечки и смешивания областей:

```kotlin
@DslMarker
annotation class BuilderDsl

@BuilderDsl
class Builder { /* ... */ }
```

2. Предпочитайте лямбды с получателем (`Receiver.() -> Unit`) обычным лямбдам — это делает DSL более декларативным и типобезопасным:

```kotlin
// DO: лямбда с получателем
fun tag(name: String, block: Tag.() -> Unit)

// DON'T: обычная лямбда
fun tag(name: String, block: (Tag) -> Unit)
```

3. Стройте type-safe builders: работайте с конкретными типами компонентов, не используйте `Any` или сырые структуры, если важна корректность дерева:

```kotlin
// DO: ограничения на известные типы компонентов
fun Container.button(text: String, onClick: () -> Unit) {
    add(Button(text, onClick))
}

// DON'T: слишком общий вариант, теряется безопасность
fun Container.add(component: Any) { /* ... */ }
```

## Дополнительные вопросы (RU)

- В чем ключевые отличия подхода к DSL в Kotlin по сравнению с Java?
- В каких практических сценариях вы бы использовали такой DSL (например, описание UI, конфигурации, Gradle-подобные скрипты)?
- Какие типичные ошибки стоит избегать при проектировании DSL на Kotlin?

## Ссылки (RU)

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## Связанные вопросы (RU)

- [[q-array-vs-list-kotlin--kotlin--easy]]

# Question (EN)
> Design and implement a type-safe DSL for building UI components. Use scope control, extension lambdas, and `@DslMarker`.

## Answer (EN)

A **DSL (Domain-Specific Language)** in Kotlin is built using language features such as lambdas with receivers, extension functions, and infix/operator overloading to create expressive and type-safe APIs, e.g., for UI building.

### Basic DSL Structure

Use lambdas with receivers: `block: HtmlTag.() -> Unit` so that inside the block you can call `HtmlTag` members without qualifying the receiver.

```kotlin
@DslMarker
annotation class HtmlDsl

@HtmlDsl
class HtmlBuilder {
    private val elements = mutableListOf<String>()

    fun html(block: HtmlTag.() -> Unit): String {
        val tag = HtmlTag("html")
        tag.block()
        elements.add(tag.render())
        return elements.joinToString()
    }
}

@HtmlDsl
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

### `@DslMarker` For Scope Control

`@DslMarker` is used to limit implicit receiver resolution and to prevent accidentally calling members of an outer builder from an inner DSL scope.

If multiple receivers annotated with the same `@DslMarker` are in scope, the compiler restricts implicit access to only the closest one. This keeps nested builders type-safe and avoids mixing domains.

### Complete Type-Safe UI DSL

Example of a UI DSL with `@UiDsl`, `Container`, `Button`, `Text`, and builder functions like `button`, `text`, and `column`:

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

@UiDsl
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

This DSL is:
- type-safe (operates on `Component` and its subtypes);
- declarative via lambdas with receivers;
- using `@UiDsl` to keep nested scopes clean and avoid mixing different UI builder contexts.

### Advanced DSL: SQL Query Builder

Example in another domain with infix functions:

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

Here `@SqlDsl` marks the DSL builder types. In this simplified example it mainly illustrates the pattern; in a larger codebase it helps prevent mixing this DSL with others in the same scope.

### Best Practices

1. Use `@DslMarker`:

```kotlin
@DslMarker
annotation class BuilderDsl

@BuilderDsl
class Builder { /* ... */ }
```

Apply it consistently to all core DSL builder types to prevent leaking outer receivers.

2. Prefer extension lambdas with receivers:

```kotlin
// DO: Lambda with receiver
fun tag(name: String, block: Tag.() -> Unit)

// DON'T: Regular lambda
fun tag(name: String, block: (Tag) -> Unit)
```

Receiver lambdas make the DSL more readable and closer to natural language while staying type-safe.

3. Type-safe builders:

```kotlin
// DO: Constrained to known component types
fun Container.button(text: String, onClick: () -> Unit) {
    add(Button(text, onClick))
}

// DON'T: Too generic, loses safety
fun Container.add(component: Any) { /* ... */ }
```

Ensure your builder functions accept and produce well-defined domain types.

## Follow-ups

- What are the key differences between this and Java for building DSL-like APIs?
- When would you use this in practice (e.g. UI description, configuration, Gradle-like scripts)?
- What are common pitfalls to avoid when designing Kotlin DSLs?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## Related Questions

- [[q-array-vs-list-kotlin--kotlin--easy]]
