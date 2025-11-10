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
- c-kotlin
- c-gradle
- q-kotlin-lambda-expressions--kotlin--medium
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
- "https://kotlinlang.org/docs/type-safe-builders.html"

---

# Вопрос (RU)
> Что такое DSL строители в Kotlin и как их создавать?

# Question (EN)
> What are DSL builders in Kotlin and how to create them?

---

## Ответ (RU)

**Теория DSL строителей:**
DSL (Domain-Specific Language) строители позволяют создавать выразительные, типобезопасные API, которые напоминают декларативный язык конфигурации (как в Gradle Kotlin DSL, Jetpack Compose или HTML DSL). Они основаны на лямбдах с получателем, функциях-расширениях и (опционально) перегрузке операторов.

**Основные концепции:**
- Лямбда с получателем (`T.() -> Unit`) — основа DSL: внутри блока `this` — экземпляр `T`.
- `@DslMarker` — ограничивает видимость нескольких имплицитных получателей разных DSL-областей, предотвращая случайное обращение к «чужому» `this`.
- Функции-расширения — позволяют добавлять функции "строителя" к контекстному типу.
- Перегрузка операторов — может улучшать читаемость (например, `unaryPlus` для текста в HTML DSL).

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

class HTML {
    private val content = StringBuilder()

    fun append(text: String) {
        content.append(text)
    }
}

// Использование — чище, параметр не нужен
val html2 = buildHtml2 {
    append("<html>")  // 'this' — это HTML
    append("<body>")
}
```

**Базовый DSL строитель (упрощённый HTML DSL):**
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

class TextTag(private val text: String) : Tag("text")

class HTML : Tag("html") {
    fun head(init: Head.() -> Unit) = initTag(Head(), init)
    fun body(init: Body.() -> Unit) = initTag(Body(), init)
}

class Head : Tag("head")

class Body : Tag("body") {
    fun h1(init: H1.() -> Unit) = initTag(H1(), init)
    fun p(init: P.() -> Unit) = initTag(P(), init)
}

class H1 : Tag("h1")
class P : Tag("p")

// DSL-функция верхнего уровня
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

// Благодаря @TableDsl, когда внутри row { ... } одновременно есть получатель SafeRowBuilder
// и внешний SafeTableBuilder, Kotlin запрещает неявные обращения к "чужому" this,
// уменьшая риск ошибок при вложенных DSL-вызовах.
fun buildTable() {
    SafeTableBuilder().apply {
        row {
            cell("A")
            // Вложенный вызов row() без явной ссылки на внешний билдер будет запрещён,
            // если он создаёт конфликт имплицитных получателей.
            // row { cell("B") } // пример потенциально проблемного кода
        }
    }
}
```

**Android `View` DSL (упрощённый пример):**
```kotlin
@DslMarker
annotation class ViewDsl

@ViewDsl
abstract class ViewBuilder {
    abstract fun build(context: Context): View
}

@ViewDsl
class TextViewBuilder : ViewBuilder() {
    var text: CharSequence = ""
    var textSize: Float = 14f

    override fun build(context: Context): TextView =
        TextView(context).apply {
            this.text = this@TextViewBuilder.text
            this.textSize = this@TextViewBuilder.textSize
        }
}

@ViewDsl
class ButtonBuilder : ViewBuilder() {
    var text: CharSequence = ""
    var onClickListener: ((View) -> Unit)? = null

    override fun build(context: Context): Button =
        Button(context).apply {
            this.text = this@ButtonBuilder.text
            setOnClickListener { v -> onClickListener?.invoke(v) }
        }
}

@ViewDsl
class LinearLayoutBuilder : ViewBuilder() {
    var orientation: Int = LinearLayout.VERTICAL
    private val children = mutableListOf<ViewBuilder>()

    fun textView(init: TextViewBuilder.() -> Unit) {
        children.add(TextViewBuilder().apply(init))
    }

    fun button(init: ButtonBuilder.() -> Unit) {
        children.add(ButtonBuilder().apply(init))
    }

    override fun build(context: Context): LinearLayout =
        LinearLayout(context).apply {
            this.orientation = this@LinearLayoutBuilder.orientation
            children.forEach { child -> addView(child.build(context)) }
        }
}

// DSL-функция
fun Context.verticalLayout(init: LinearLayoutBuilder.() -> Unit): LinearLayout {
    return LinearLayoutBuilder().apply(init).build(this)
}

// Использование
val layout = context.verticalLayout {
    orientation = LinearLayout.VERTICAL
    textView {
        text = "Привет"
        textSize = 20f
    }
    button {
        text = "Нажми меня"
        onClickListener = { /* ... */ }
    }
}
```

(Этот пример иллюстрирует подход; в реальных Android-проектах чаще используют Jetpack Compose, который является DSL, основанным на аннотации `@Composable` и функциях с приемником.)

## Answer (EN)

**DSL Builders Theory:**
DSL (Domain-Specific Language) builders help create expressive, type-safe APIs that look like a declarative configuration language (similar to Gradle Kotlin DSL, Jetpack Compose, or HTML DSL). They are built on lambdas with receiver, extension functions, and optionally operator overloading.

**Main concepts:**
- Lambda with receiver (`T.() -> Unit`) — the core: inside the block, `this` is an instance of `T`.
- `@DslMarker` — restricts visibility when multiple implicit receivers from different DSL scopes are in play, preventing accidental calls on the wrong `this`.
- Extension functions — provide builder-style functions on the context type.
- Operator overloading — can improve readability (for example, `unaryPlus` for text in HTML DSL).

**Lambda with receiver:**
```kotlin
// Regular lambda: (HTML) -> Unit
fun buildHtml1(builder: (HTML) -> Unit): HTML {
    val html = HTML()
    builder(html)  // Pass HTML as argument
    return html
}

// Lambda with receiver: HTML.() -> Unit
fun buildHtml2(builder: HTML.() -> Unit): HTML {
    val html = HTML()
    html.builder()  // HTML becomes 'this' inside lambda
    return html
}

class HTML {
    private val content = StringBuilder()

    fun append(text: String) {
        content.append(text)
    }
}

// Usage — cleaner, no parameter needed
val html2 = buildHtml2 {
    append("<html>")  // 'this' is HTML
    append("<body>")
}
```

**Basic DSL builder (simplified HTML DSL):**
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

class TextTag(private val text: String) : Tag("text")

class HTML : Tag("html") {
    fun head(init: Head.() -> Unit) = initTag(Head(), init)
    fun body(init: Body.() -> Unit) = initTag(Body(), init)
}

class Head : Tag("head")

class Body : Tag("body") {
    fun h1(init: H1.() -> Unit) = initTag(H1(), init)
    fun p(init: P.() -> Unit) = initTag(P(), init)
}

class H1 : Tag("h1")
class P : Tag("p")

// Top-level DSL function
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

// With @TableDsl, when inside row { ... } there are both SafeRowBuilder and outer SafeTableBuilder
// as potential receivers, Kotlin restricts implicit member resolution to avoid calling the wrong receiver.
fun buildTable() {
    SafeTableBuilder().apply {
        row {
            cell("A")
            // Nested row() without qualifying the outer receiver would be disallowed
            // if it causes conflicting implicit receivers.
            // row { cell("B") } // example of potentially problematic code
        }
    }
}
```

**Android `View` DSL (simplified example):**
```kotlin
@DslMarker
annotation class ViewDsl

@ViewDsl
abstract class ViewBuilder {
    abstract fun build(context: Context): View
}

@ViewDsl
class TextViewBuilder : ViewBuilder() {
    var text: CharSequence = ""
    var textSize: Float = 14f

    override fun build(context: Context): TextView =
        TextView(context).apply {
            this.text = this@TextViewBuilder.text
            this.textSize = this@TextViewBuilder.textSize
        }
}

@ViewDsl
class ButtonBuilder : ViewBuilder() {
    var text: CharSequence = ""
    var onClickListener: ((View) -> Unit)? = null

    override fun build(context: Context): Button =
        Button(context).apply {
            this.text = this@ButtonBuilder.text
            setOnClickListener { v -> onClickListener?.invoke(v) }
        }
}

@ViewDsl
class LinearLayoutBuilder : ViewBuilder() {
    var orientation: Int = LinearLayout.VERTICAL
    private val children = mutableListOf<ViewBuilder>()

    fun textView(init: TextViewBuilder.() -> Unit) {
        children.add(TextViewBuilder().apply(init))
    }

    fun button(init: ButtonBuilder.() -> Unit) {
        children.add(ButtonBuilder().apply(init))
    }

    override fun build(context: Context): LinearLayout =
        LinearLayout(context).apply {
            this.orientation = this@LinearLayoutBuilder.orientation
            children.forEach { child -> addView(child.build(context)) }
        }
}

// DSL function
fun Context.verticalLayout(init: LinearLayoutBuilder.() -> Unit): LinearLayout {
    return LinearLayoutBuilder().apply(init).build(this)
}

// Usage
val layout = context.verticalLayout {
    orientation = LinearLayout.VERTICAL
    textView {
        text = "Hello"
        textSize = 20f
    }
    button {
        text = "Click me"
        onClickListener = { /* ... */ }
    }
}
```

(This example is illustrative; in modern Android, Jetpack Compose itself is a Kotlin-based UI DSL built with composable functions.)

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

- [[c-kotlin]]
- [[c-gradle]]

### Related (Same Level)
- [[q-kotlin-lambda-expressions--kotlin--medium]] - Lambda receivers

### Advanced (Harder)
- [[q-kotlin-context-receivers--android--hard]] - `Context` receivers
