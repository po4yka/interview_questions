---
id: android-061
title: Kotlin DSL Builders / Kotlin DSL строители
aliases:
- Kotlin DSL Builders
- Kotlin DSL строители
topic: android
subtopics:
- coroutines
- ui-compose
question_kind: android
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-kotlin-lambda-receivers--kotlin--medium
created: 2025-10-12
updated: 2025-10-31
tags:
- android/coroutines
- android/ui-compose
- api-design
- builders
- difficulty/hard
- dsl
- lambdas
sources:
- https://kotlinlang.org/docs/type-safe-builders.html

---

# Вопрос (RU)
> Что такое DSL строители в Kotlin и как их создавать?

# Question (EN)
> What are DSL builders in Kotlin and how to create them?

---

## Ответ (RU)

**Теория DSL строителей:**
DSL (Domain-Specific Language) строители позволяют создавать выразительные, типобезопасные API, которые напоминают естественный язык. Основаны на лямбдах с получателем, функциях-расширениях и перегрузке операторов.

**Основные концепции:**
- Лямбда с получателем (`T.() -> Unit`) - основа DSL
- `@DslMarker` - предотвращает доступ к внешнему scope
- Функции-расширения для добавления методов строителя
- Перегрузка операторов для естественного синтаксиса

**Лямбда с получателем:**
```kotlin
// Обычная лямбда: (HTML) -> Unit
fun buildHtml1(builder: (HTML) -> Unit): HTML {
    val html = HTML()
    builder(html)  // Передаем HTML как параметр
    return html
}

// Лямбда с получателем: HTML.() -> Unit
fun buildHtml2(builder: HTML.() -> Unit): HTML {
    val html = HTML()
    html.builder()  // HTML становится 'this' внутри лямбды
    return html
}

// Использование - чище, параметр не нужен
val html2 = buildHtml2 {
    append("<html>")  // 'this' - это HTML
    append("<body>")
}
```

**Базовый DSL строитель:**
```kotlin
@DslMarker
annotation class HtmlTagMarker

@HtmlTagMarker
abstract class Tag(val name: String) {
    private val children = mutableListOf<Tag>()
    private val attributes = mutableMapOf<String, String>()

    protected fun <T : Tag> initTag(tag: T, init: T.() -> Unit): T {
        tag.init()
        children.add(tag)
        return tag
    }

    operator fun String.unaryPlus() {
        children.add(TextTag(this))
    }

    fun attribute(name: String, value: String) {
        attributes[name] = value
    }
}

class HTML : Tag("html") {
    fun head(init: Head.() -> Unit) = initTag(Head(), init)
    fun body(init: Body.() -> Unit) = initTag(Body(), init)
}

class Body : Tag("body") {
    fun h1(init: H1.() -> Unit) = initTag(H1(), init)
    fun p(init: P.() -> Unit) = initTag(P(), init)
}

// DSL функция
fun html(init: HTML.() -> Unit): HTML {
    val html = HTML()
    html.init()
    return html
}

// Использование
val webpage = html {
    head { /* ... */ }
    body {
        h1 { +"Заголовок" }
        p { +"Параграф" }
    }
}
```

**@DslMarker для безопасности:**
```kotlin
@DslMarker
annotation class TableDsl

@TableDsl
class SafeTableBuilder {
    fun row(init: SafeRowBuilder.() -> Unit) {
        SafeRowBuilder().init()
    }
}

@TableDsl
class SafeRowBuilder {
    fun cell(text: String) {
        println("Ячейка: $text")
    }
}

// Теперь безопаснее - нельзя получить доступ к внешнему scope
fun buildTable() {
    SafeTableBuilder().apply {
        row {
            cell("A")
            // row { // Ошибка компиляции - нельзя получить доступ к внешнему scope
            //     cell("B")
            // }
        }
    }
}
```

**Android `View` DSL:**
```kotlin
@DslMarker
annotation class ViewDsl

@ViewDsl
abstract class ViewBuilder {
    abstract fun build(context: Context): View
}

@ViewDsl
class LinearLayoutBuilder : ViewBuilder() {
    var orientation = LinearLayout.VERTICAL
    private val children = mutableListOf<ViewBuilder>()

    fun textView(init: TextViewBuilder.() -> Unit) {
        children.add(TextViewBuilder().apply(init))
    }

    fun button(init: ButtonBuilder.() -> Unit) {
        children.add(ButtonBuilder().apply(init))
    }

    override fun build(context: Context): LinearLayout {
        return LinearLayout(context).apply {
            this.orientation = this@LinearLayoutBuilder.orientation
            children.forEach { addView(it.build(context)) }
        }
    }
}

// DSL функция
fun Context.verticalLayout(init: LinearLayoutBuilder.() -> Unit): LinearLayout {
    return LinearLayoutBuilder().apply(init).build(this)
}

// Использование
val layout = verticalLayout {
    orientation = LinearLayout.VERTICAL
    textView {
        text = "Привет"
        textSize = 20f
    }
    button {
        text = "Нажми меня"
        onClick = { /* ... */ }
    }
}
```

## Answer (EN)

**DSL Builders Theory:**
DSL (Domain-Specific Language) builders allow creating expressive, type-safe APIs that resemble natural language. Based on lambda with receiver, extension functions, and operator overloading.

**Main concepts:**
- Lambda with receiver (`T.() -> Unit`) - foundation of DSL
- `@DslMarker` - prevents accessing outer scope
- Extension functions for adding builder methods
- Operator overloading for natural syntax

**Lambda with receiver:**
```kotlin
// Regular lambda: (HTML) -> Unit
fun buildHtml1(builder: (HTML) -> Unit): HTML {
    val html = HTML()
    builder(html)  // Pass HTML as parameter
    return html
}

// Lambda with receiver: HTML.() -> Unit
fun buildHtml2(builder: HTML.() -> Unit): HTML {
    val html = HTML()
    html.builder()  // HTML becomes 'this' inside lambda
    return html
}

// Usage - cleaner, no parameter needed
val html2 = buildHtml2 {
    append("<html>")  // 'this' is HTML
    append("<body>")
}
```

**Basic DSL builder:**
```kotlin
@DslMarker
annotation class HtmlTagMarker

@HtmlTagMarker
abstract class Tag(val name: String) {
    private val children = mutableListOf<Tag>()
    private val attributes = mutableMapOf<String, String>()

    protected fun <T : Tag> initTag(tag: T, init: T.() -> Unit): T {
        tag.init()
        children.add(tag)
        return tag
    }

    operator fun String.unaryPlus() {
        children.add(TextTag(this))
    }

    fun attribute(name: String, value: String) {
        attributes[name] = value
    }
}

class HTML : Tag("html") {
    fun head(init: Head.() -> Unit) = initTag(Head(), init)
    fun body(init: Body.() -> Unit) = initTag(Body(), init)
}

class Body : Tag("body") {
    fun h1(init: H1.() -> Unit) = initTag(H1(), init)
    fun p(init: P.() -> Unit) = initTag(P(), init)
}

// DSL function
fun html(init: HTML.() -> Unit): HTML {
    val html = HTML()
    html.init()
    return html
}

// Usage
val webpage = html {
    head { /* ... */ }
    body {
        h1 { +"Title" }
        p { +"Paragraph" }
    }
}
```

**@DslMarker for safety:**
```kotlin
@DslMarker
annotation class TableDsl

@TableDsl
class SafeTableBuilder {
    fun row(init: SafeRowBuilder.() -> Unit) {
        SafeRowBuilder().init()
    }
}

@TableDsl
class SafeRowBuilder {
    fun cell(text: String) {
        println("Cell: $text")
    }
}

// Now safer - cannot access outer scope
fun buildTable() {
    SafeTableBuilder().apply {
        row {
            cell("A")
            // row { // Compile error - cannot access outer scope
            //     cell("B")
            // }
        }
    }
}
```

**Android `View` DSL:**
```kotlin
@DslMarker
annotation class ViewDsl

@ViewDsl
abstract class ViewBuilder {
    abstract fun build(context: Context): View
}

@ViewDsl
class LinearLayoutBuilder : ViewBuilder() {
    var orientation = LinearLayout.VERTICAL
    private val children = mutableListOf<ViewBuilder>()

    fun textView(init: TextViewBuilder.() -> Unit) {
        children.add(TextViewBuilder().apply(init))
    }

    fun button(init: ButtonBuilder.() -> Unit) {
        children.add(ButtonBuilder().apply(init))
    }

    override fun build(context: Context): LinearLayout {
        return LinearLayout(context).apply {
            this.orientation = this@LinearLayoutBuilder.orientation
            children.forEach { addView(it.build(context)) }
        }
    }
}

// DSL function
fun Context.verticalLayout(init: LinearLayoutBuilder.() -> Unit): LinearLayout {
    return LinearLayoutBuilder().apply(init).build(this)
}

// Usage
val layout = verticalLayout {
    orientation = LinearLayout.VERTICAL
    textView {
        text = "Hello"
        textSize = 20f
    }
    button {
        text = "Click me"
        onClick = { /* ... */ }
    }
}
```

---

## Follow-ups

- How do you make DSLs discoverable in IDE?
- What's the performance impact of DSL builders?
- How do you version DSL APIs?


## References

- [Android Documentation](https://developer.android.com/docs)
- [Jetpack Compose](https://developer.android.com/develop/ui/compose)


## Related Questions

### Prerequisites / Concepts

- 


### Related (Same Level)
- [[q-kotlin-lambda-expressions--kotlin--medium]] - Lambda receivers

### Advanced (Harder)
- [[q-kotlin-context-receivers--android--hard]] - `Context` receivers
