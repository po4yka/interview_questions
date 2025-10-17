---
id: 20251012-400010
title: "Kotlin DSL Builders"
topic: android
difficulty: hard
status: draft
created: 2025-10-12
tags: [dsl, builders, api-design, lambdas, android/dsl, android/builders, android/api-design, android/type-safe-builders, difficulty/hard]
moc: moc-android
related:   - q-kotlin-context-receivers--kotlin--hard
  - q-jetpack-compose-basics--android--medium
  - q-gradle-kotlin-dsl-vs-groovy--android--medium
subtopics:   - kotlin
  - dsl
  - builders
  - api-design
  - type-safe-builders
---
# Kotlin DSL Builders

## English Version

### Problem Statement

Domain-Specific Languages (DSLs) in Kotlin allow creating expressive, type-safe APIs that resemble natural language. Kotlin's lambda with receiver, extension functions, and operator overloading make it ideal for building DSLs. Understanding DSL patterns is essential for creating intuitive Android APIs.

**The Question:** What are Kotlin DSLs? How do you build type-safe DSLs? What are lambda with receiver, @DslMarker, and builder patterns? What are real-world examples?

### Detailed Answer

---

### DSL FUNDAMENTALS

**Traditional API:**
```kotlin
// Traditional imperative style
val button = Button()
button.text = "Click me"
button.textColor = Color.BLUE
button.onClick = { println("Clicked") }
```

**DSL style:**
```kotlin
// Declarative DSL style
button {
    text = "Click me"
    textColor = Color.BLUE
    onClick { println("Clicked") }
}
```

**Key DSL features:**
```
 Lambda with receiver
 Extension functions
 Operator overloading
 Infix functions
 @DslMarker annotation
 Type-safe builders
```

---

### LAMBDA WITH RECEIVER

```kotlin
// Lambda with receiver - the foundation of DSLs

class HTML {
    private val content = StringBuilder()

    fun append(text: String) {
        content.append(text)
    }

    override fun toString() = content.toString()
}

// Regular lambda: (HTML) -> Unit
fun buildHtml1(builder: (HTML) -> Unit): HTML {
    val html = HTML()
    builder(html)  // Pass HTML as parameter
    return html
}

// Usage - need to reference parameter
val html1 = buildHtml1 { html ->
    html.append("<html>")
    html.append("<body>")
    html.append("</body>")
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
    append("</body>")
}
```

---

### TYPE-SAFE HTML BUILDER

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

    fun render(builder: StringBuilder, indent: String) {
        builder.append("$indent<$name")
        attributes.forEach { (name, value) ->
            builder.append(" $name=\"$value\"")
        }
        if (children.isEmpty()) {
            builder.append("/>\n")
        } else {
            builder.append(">\n")
            children.forEach { it.render(builder, "$indent  ") }
            builder.append("$indent</$name>\n")
        }
    }

    override fun toString(): String {
        val builder = StringBuilder()
        render(builder, "")
        return builder.toString()
    }
}

class TextTag(private val text: String) : Tag("") {
    override fun render(builder: StringBuilder, indent: String) {
        builder.append("$indent$text\n")
    }
}

class HTML : Tag("html") {
    fun head(init: Head.() -> Unit) = initTag(Head(), init)
    fun body(init: Body.() -> Unit) = initTag(Body(), init)
}

class Head : Tag("head") {
    fun title(init: Title.() -> Unit) = initTag(Title(), init)
}

class Title : Tag("title")

class Body : Tag("body") {
    fun h1(init: H1.() -> Unit) = initTag(H1(), init)
    fun p(init: P.() -> Unit) = initTag(P(), init)
    fun div(cssClass: String? = null, init: Div.() -> Unit): Div {
        val div = initTag(Div(), init)
        cssClass?.let { div.attribute("class", it) }
        return div
    }
    fun a(href: String, init: A.() -> Unit): A {
        val a = initTag(A(), init)
        a.attribute("href", href)
        return a
    }
}

class H1 : Tag("h1")
class P : Tag("p")
class Div : Tag("div")
class A : Tag("a")

// Build HTML
fun html(init: HTML.() -> Unit): HTML {
    val html = HTML()
    html.init()
    return html
}

// Usage
val webpage = html {
    head {
        title {
            +"My Webpage"
        }
    }
    body {
        h1 {
            +"Welcome"
        }
        p {
            +"This is a paragraph with "
        }
        a(href = "https://example.com") {
            +"a link"
        }
        div(cssClass = "container") {
            p {
                +"Content in div"
            }
        }
    }
}

println(webpage)
```

---

### @DSLMARKER ANNOTATION

```kotlin
// Without @DslMarker - can call outer scope incorrectly
class TableBuilder {
    fun row(init: RowBuilder.() -> Unit) {
        RowBuilder().init()
    }
}

class RowBuilder {
    fun cell(text: String) {
        println("Cell: $text")
    }
}

// Problem: can access outer scope
fun buildTable1() {
    TableBuilder().apply {
        row {
            cell("A")
            row {  //  Can call row() here - confusing!
                cell("B")
            }
        }
    }
}

// With @DslMarker - prevents accessing outer scope
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

// Now safer
fun buildTable2() {
    SafeTableBuilder().apply {
        row {
            cell("A")
            // row {  //  Compile error - cannot access outer scope
            //     cell("B")
            // }
        }
    }
}
```

---

### ANDROID VIEW DSL

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
    var gravity = Gravity.START
    private val children = mutableListOf<ViewBuilder>()

    fun textView(init: TextViewBuilder.() -> Unit) {
        children.add(TextViewBuilder().apply(init))
    }

    fun button(init: ButtonBuilder.() -> Unit) {
        children.add(ButtonBuilder().apply(init))
    }

    fun imageView(init: ImageViewBuilder.() -> Unit) {
        children.add(ImageViewBuilder().apply(init))
    }

    override fun build(context: Context): LinearLayout {
        return LinearLayout(context).apply {
            this.orientation = this@LinearLayoutBuilder.orientation
            this.gravity = this@LinearLayoutBuilder.gravity

            children.forEach { childBuilder ->
                addView(childBuilder.build(context))
            }
        }
    }
}

@ViewDsl
class TextViewBuilder : ViewBuilder() {
    var text: String = ""
    var textSize: Float = 14f
    var textColor: Int = Color.BLACK

    override fun build(context: Context): TextView {
        return TextView(context).apply {
            this.text = this@TextViewBuilder.text
            this.textSize = this@TextViewBuilder.textSize
            setTextColor(this@TextViewBuilder.textColor)
        }
    }
}

@ViewDsl
class ButtonBuilder : ViewBuilder() {
    var text: String = ""
    var onClick: (() -> Unit)? = null

    override fun build(context: Context): Button {
        return Button(context).apply {
            this.text = this@ButtonBuilder.text
            onClick?.let { clickHandler ->
                setOnClickListener { clickHandler() }
            }
        }
    }
}

@ViewDsl
class ImageViewBuilder : ViewBuilder() {
    var imageRes: Int = 0
    var scaleType: ImageView.ScaleType = ImageView.ScaleType.CENTER

    override fun build(context: Context): ImageView {
        return ImageView(context).apply {
            if (imageRes != 0) {
                setImageResource(imageRes)
            }
            this.scaleType = this@ImageViewBuilder.scaleType
        }
    }
}

// DSL function
fun Context.verticalLayout(init: LinearLayoutBuilder.() -> Unit): LinearLayout {
    return LinearLayoutBuilder().apply(init).build(this)
}

// Usage in Activity
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val layout = verticalLayout {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER

            textView {
                text = "Welcome to my app"
                textSize = 20f
                textColor = Color.BLUE
            }

            button {
                text = "Click me"
                onClick = {
                    Toast.makeText(this@MainActivity, "Clicked!", Toast.LENGTH_SHORT).show()
                }
            }

            imageView {
                imageRes = R.drawable.logo
                scaleType = ImageView.ScaleType.FIT_CENTER
            }
        }

        setContentView(layout)
    }
}
```

---

### NAVIGATION DSL

```kotlin
@DslMarker
annotation class NavigationDsl

@NavigationDsl
class NavGraphBuilder(private val navController: NavController) {
    private val destinations = mutableMapOf<String, NavDestination>()

    fun screen(route: String, init: NavDestinationBuilder.() -> Unit) {
        val destination = NavDestinationBuilder(route).apply(init).build()
        destinations[route] = destination
    }

    fun build() {
        // Setup navigation graph
        destinations.forEach { (route, destination) ->
            // Add to NavController
        }
    }
}

@NavigationDsl
class NavDestinationBuilder(private val route: String) {
    var content: @Composable () -> Unit = {}
    var arguments: List<NamedNavArgument> = emptyList()
    var deepLinks: List<String> = emptyList()

    fun build(): NavDestination {
        return NavDestination(
            route = route,
            content = content,
            arguments = arguments,
            deepLinks = deepLinks
        )
    }
}

data class NavDestination(
    val route: String,
    val content: @Composable () -> Unit,
    val arguments: List<NamedNavArgument>,
    val deepLinks: List<String>
)

// DSL function
fun NavController.navigation(init: NavGraphBuilder.() -> Unit) {
    NavGraphBuilder(this).apply(init).build()
}

// Usage
@Composable
fun MyApp() {
    val navController = rememberNavController()

    navController.navigation {
        screen("home") {
            content = { HomeScreen() }
        }

        screen("profile/{userId}") {
            arguments = listOf(
                navArgument("userId") { type = NavType.StringType }
            )
            deepLinks = listOf("myapp://profile/{userId}")
            content = { ProfileScreen() }
        }

        screen("settings") {
            content = { SettingsScreen() }
        }
    }
}
```

---

### NETWORK REQUEST DSL

```kotlin
@DslMarker
annotation class RequestDsl

@RequestDsl
class RequestBuilder {
    var method: HttpMethod = HttpMethod.GET
    var url: String = ""
    private val headers = mutableMapOf<String, String>()
    private val queryParams = mutableMapOf<String, String>()
    var body: Any? = null

    fun header(name: String, value: String) {
        headers[name] = value
    }

    fun queryParam(name: String, value: String) {
        queryParams[name] = value
    }

    fun build(): HttpRequest {
        return HttpRequest(
            method = method,
            url = url,
            headers = headers,
            queryParams = queryParams,
            body = body
        )
    }
}

enum class HttpMethod { GET, POST, PUT, DELETE, PATCH }

data class HttpRequest(
    val method: HttpMethod,
    val url: String,
    val headers: Map<String, String>,
    val queryParams: Map<String, String>,
    val body: Any?
)

// DSL functions
fun request(init: RequestBuilder.() -> Unit): HttpRequest {
    return RequestBuilder().apply(init).build()
}

fun get(url: String, init: RequestBuilder.() -> Unit = {}): HttpRequest {
    return RequestBuilder().apply {
        method = HttpMethod.GET
        this.url = url
        init()
    }.build()
}

fun post(url: String, init: RequestBuilder.() -> Unit = {}): HttpRequest {
    return RequestBuilder().apply {
        method = HttpMethod.POST
        this.url = url
        init()
    }.build()
}

// Usage
val getUserRequest = get("https://api.example.com/users/123") {
    header("Authorization", "Bearer token")
    header("Accept", "application/json")
    queryParam("include", "profile")
}

val createUserRequest = post("https://api.example.com/users") {
    header("Content-Type", "application/json")
    body = mapOf(
        "name" to "John Doe",
        "email" to "john@example.com"
    )
}
```

---

### TESTING DSL

```kotlin
@DslMarker
annotation class TestDsl

@TestDsl
class TestSuiteBuilder(private val name: String) {
    private val tests = mutableListOf<TestCase>()

    fun test(name: String, body: suspend TestContext.() -> Unit) {
        tests.add(TestCase(name, body))
    }

    suspend fun run() {
        println("Running test suite: $name")
        tests.forEach { testCase ->
            val context = TestContext()
            try {
                testCase.body(context)
                println(" ${testCase.name}")
            } catch (e: AssertionError) {
                println(" ${testCase.name}: ${e.message}")
            }
        }
    }
}

@TestDsl
class TestContext {
    fun <T> assertThat(actual: T): Assertion<T> {
        return Assertion(actual)
    }

    infix fun <T> T.shouldBe(expected: T) {
        if (this != expected) {
            throw AssertionError("Expected $expected but got $this")
        }
    }

    infix fun <T> T.shouldNotBe(expected: T) {
        if (this == expected) {
            throw AssertionError("Expected not $expected but got $this")
        }
    }
}

class Assertion<T>(private val actual: T) {
    infix fun isEqualTo(expected: T) {
        if (actual != expected) {
            throw AssertionError("Expected $expected but got $actual")
        }
    }

    infix fun isNotEqualTo(expected: T) {
        if (actual == expected) {
            throw AssertionError("Expected not $expected but got $actual")
        }
    }
}

data class TestCase(
    val name: String,
    val body: suspend TestContext.() -> Unit
)

// DSL function
suspend fun testSuite(name: String, init: TestSuiteBuilder.() -> Unit) {
    TestSuiteBuilder(name).apply(init).run()
}

// Usage
suspend fun runTests() {
    testSuite("User Repository Tests") {
        test("should fetch user by id") {
            val user = userRepository.getUser("123")
            user.name shouldBe "John Doe"
            user.email shouldBe "john@example.com"
        }

        test("should throw exception for invalid id") {
            assertThat(repository.getUser("invalid")).isEqualTo(null)
        }

        test("should update user") {
            val updated = repository.updateUser(user.copy(name = "Jane Doe"))
            updated.name shouldBe "Jane Doe"
        }
    }
}
```

---

### COMPOSE-STYLE BUILDER

```kotlin
@DslMarker
annotation class UiDsl

@UiDsl
interface ComponentScope {
    fun add(component: Component)
}

sealed class Component

data class Text(val text: String, val size: Int) : Component()
data class Button(val text: String, val onClick: () -> Unit) : Component()
data class Container(
    val children: List<Component>,
    val padding: Int
) : Component()

class ContainerScope : ComponentScope {
    private val children = mutableListOf<Component>()

    override fun add(component: Component) {
        children.add(component)
    }

    fun build(): List<Component> = children
}

// DSL functions
@UiDsl
fun ComponentScope.text(text: String, size: Int = 14) {
    add(Text(text, size))
}

@UiDsl
fun ComponentScope.button(text: String, onClick: () -> Unit) {
    add(Button(text, onClick))
}

@UiDsl
fun ComponentScope.container(
    padding: Int = 16,
    content: ComponentScope.() -> Unit
) {
    val scope = ContainerScope()
    scope.content()
    add(Container(scope.build(), padding))
}

fun ui(content: ComponentScope.() -> Unit): List<Component> {
    val scope = ContainerScope()
    scope.content()
    return scope.build()
}

// Usage
val screen = ui {
    text("Welcome to DSL", size = 20)

    button("Click me") {
        println("Button clicked!")
    }

    container(padding = 24) {
        text("Nested content")
        button("Nested button") {
            println("Nested clicked")
        }
    }
}
```

---

### BEST PRACTICES

```kotlin
//  Use @DslMarker to prevent scope leakage
@DslMarker
annotation class MyDsl

//  Use lambda with receiver for builder APIs
fun myBuilder(init: MyBuilder.() -> Unit) {
    MyBuilder().init()
}

//  Use operator overloading judiciously
class HtmlBuilder {
    operator fun String.unaryPlus() {  // +text
        append(this)
    }
}

//  Make DSL type-safe
class TypeSafeBuilder {
    fun validOption(value: String) { /* only valid values */ }
}

//  Don't overuse operator overloading
// Bad: confusing
class BadBuilder {
    operator fun String.minus(other: String) { }  // text1 - text2 ???
}

//  Provide good defaults
fun layout(
    orientation: Orientation = Orientation.VERTICAL,
    init: LayoutBuilder.() -> Unit
) { }

//  Document DSL usage
/**
 * Creates a layout with the given configuration.
 * Example:
 * ```kotlin
 * layout {
 *     text("Hello")
 *     button("Click") { }
 * }
 * ```
 */
fun layout(init: LayoutBuilder.() -> Unit) { }
```

---

### KEY TAKEAWAYS

1. **DSLs** create expressive, type-safe APIs
2. **Lambda with receiver** (T.() -> Unit) is the foundation
3. **@DslMarker** prevents accessing outer scope
4. **Extension functions** add builder methods
5. **Operator overloading** makes DSL more natural
6. **Type-safe builders** prevent invalid configurations
7. **Compose** is a perfect example of Kotlin DSL
8. **Gradle Kotlin DSL** uses these patterns
9. **Keep DSLs simple** - don't overcomplicate
10. **Document usage** with examples

---

### Подробный ответ

---

### ОСНОВЫ DSL

**Традиционный API:**
```kotlin
// Традиционный императивный стиль
val button = Button()
button.text = "Нажми меня"
button.textColor = Color.BLUE
button.onClick = { println("Нажато") }
```

**Стиль DSL:**
```kotlin
// Декларативный стиль DSL
button {
    text = "Нажми меня"
    textColor = Color.BLUE
    onClick { println("Нажато") }
}
```

**Ключевые особенности DSL:**
```
 Лямбда с получателем (lambda with receiver)
 Функции-расширения (extension functions)
 Перегрузка операторов (operator overloading)
 Инфиксные функции (infix functions)
 Аннотация @DslMarker
 Типобезопасные строители (type-safe builders)
```

---

### ЛЯМБДА С ПОЛУЧАТЕЛЕМ

```kotlin
// Лямбда с получателем - основа DSL

class HTML {
    private val content = StringBuilder()

    fun append(text: String) {
        content.append(text)
    }

    override fun toString() = content.toString()
}

// Обычная лямбда: (HTML) -> Unit
fun buildHtml1(builder: (HTML) -> Unit): HTML {
    val html = HTML()
    builder(html)  // Передаем HTML как параметр
    return html
}

// Использование - нужно ссылаться на параметр
val html1 = buildHtml1 { html ->
    html.append("<html>")
    html.append("<body>")
    html.append("</body>")
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
    append("</body>")
}
```

---

### ТИПОБЕЗОПАСНЫЙ HTML СТРОИТЕЛЬ

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

    fun render(builder: StringBuilder, indent: String) {
        builder.append("$indent<$name")
        attributes.forEach { (name, value) ->
            builder.append(" $name=\"$value\"")
        }
        if (children.isEmpty()) {
            builder.append("/>\n")
        } else {
            builder.append(">\n")
            children.forEach { it.render(builder, "$indent  ") }
            builder.append("$indent</$name>\n")
        }
    }

    override fun toString(): String {
        val builder = StringBuilder()
        render(builder, "")
        return builder.toString()
    }
}

class TextTag(private val text: String) : Tag("") {
    override fun render(builder: StringBuilder, indent: String) {
        builder.append("$indent$text\n")
    }
}

class HTML : Tag("html") {
    fun head(init: Head.() -> Unit) = initTag(Head(), init)
    fun body(init: Body.() -> Unit) = initTag(Body(), init)
}

class Head : Tag("head") {
    fun title(init: Title.() -> Unit) = initTag(Title(), init)
}

class Title : Tag("title")

class Body : Tag("body") {
    fun h1(init: H1.() -> Unit) = initTag(H1(), init)
    fun p(init: P.() -> Unit) = initTag(P(), init)
    fun div(cssClass: String? = null, init: Div.() -> Unit): Div {
        val div = initTag(Div(), init)
        cssClass?.let { div.attribute("class", it) }
        return div
    }
    fun a(href: String, init: A.() -> Unit): A {
        val a = initTag(A(), init)
        a.attribute("href", href)
        return a
    }
}

class H1 : Tag("h1")
class P : Tag("p")
class Div : Tag("div")
class A : Tag("a")

// Сборка HTML
fun html(init: HTML.() -> Unit): HTML {
    val html = HTML()
    html.init()
    return html
}

// Использование
val webpage = html {
    head {
        title {
            +"Моя веб-страница"
        }
    }
    body {
        h1 {
            +"Добро пожаловать"
        }
        p {
            +"Это параграф с "
        }
        a(href = "https://example.com") {
            +"ссылкой"
        }
        div(cssClass = "container") {
            p {
                +"Содержимое в div"
            }
        }
    }
}

println(webpage)
```

---

### АННОТАЦИЯ @DSLMARKER

```kotlin
// Без @DslMarker - можно некорректно вызвать внешний scope
class TableBuilder {
    fun row(init: RowBuilder.() -> Unit) {
        RowBuilder().init()
    }
}

class RowBuilder {
    fun cell(text: String) {
        println("Ячейка: $text")
    }
}

// Проблема: можно получить доступ к внешнему scope
fun buildTable1() {
    TableBuilder().apply {
        row {
            cell("A")
            row {  // Можно вызвать row() здесь - это сбивает с толку!
                cell("B")
            }
        }
    }
}

// С @DslMarker - предотвращает доступ к внешнему scope
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

// Теперь безопаснее
fun buildTable2() {
    SafeTableBuilder().apply {
        row {
            cell("A")
            // row {  // Ошибка компиляции - нельзя получить доступ к внешнему scope
            //     cell("B")
            // }
        }
    }
}
```

---

### ANDROID VIEW DSL

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
    var gravity = Gravity.START
    private val children = mutableListOf<ViewBuilder>()

    fun textView(init: TextViewBuilder.() -> Unit) {
        children.add(TextViewBuilder().apply(init))
    }

    fun button(init: ButtonBuilder.() -> Unit) {
        children.add(ButtonBuilder().apply(init))
    }

    fun imageView(init: ImageViewBuilder.() -> Unit) {
        children.add(ImageViewBuilder().apply(init))
    }

    override fun build(context: Context): LinearLayout {
        return LinearLayout(context).apply {
            this.orientation = this@LinearLayoutBuilder.orientation
            this.gravity = this@LinearLayoutBuilder.gravity

            children.forEach { childBuilder ->
                addView(childBuilder.build(context))
            }
        }
    }
}

@ViewDsl
class TextViewBuilder : ViewBuilder() {
    var text: String = ""
    var textSize: Float = 14f
    var textColor: Int = Color.BLACK

    override fun build(context: Context): TextView {
        return TextView(context).apply {
            this.text = this@TextViewBuilder.text
            this.textSize = this@TextViewBuilder.textSize
            setTextColor(this@TextViewBuilder.textColor)
        }
    }
}

@ViewDsl
class ButtonBuilder : ViewBuilder() {
    var text: String = ""
    var onClick: (() -> Unit)? = null

    override fun build(context: Context): Button {
        return Button(context).apply {
            this.text = this@ButtonBuilder.text
            onClick?.let { clickHandler ->
                setOnClickListener { clickHandler() }
            }
        }
    }
}

@ViewDsl
class ImageViewBuilder : ViewBuilder() {
    var imageRes: Int = 0
    var scaleType: ImageView.ScaleType = ImageView.ScaleType.CENTER

    override fun build(context: Context): ImageView {
        return ImageView(context).apply {
            if (imageRes != 0) {
                setImageResource(imageRes)
            }
            this.scaleType = this@ImageViewBuilder.scaleType
        }
    }
}

// DSL функция
fun Context.verticalLayout(init: LinearLayoutBuilder.() -> Unit): LinearLayout {
    return LinearLayoutBuilder().apply(init).build(this)
}

// Использование в Activity
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val layout = verticalLayout {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER

            textView {
                text = "Добро пожаловать в мое приложение"
                textSize = 20f
                textColor = Color.BLUE
            }

            button {
                text = "Нажми меня"
                onClick = {
                    Toast.makeText(this@MainActivity, "Нажато!", Toast.LENGTH_SHORT).show()
                }
            }

            imageView {
                imageRes = R.drawable.logo
                scaleType = ImageView.ScaleType.FIT_CENTER
            }
        }

        setContentView(layout)
    }
}
```

---

### NAVIGATION DSL

```kotlin
@DslMarker
annotation class NavigationDsl

@NavigationDsl
class NavGraphBuilder(private val navController: NavController) {
    private val destinations = mutableMapOf<String, NavDestination>()

    fun screen(route: String, init: NavDestinationBuilder.() -> Unit) {
        val destination = NavDestinationBuilder(route).apply(init).build()
        destinations[route] = destination
    }

    fun build() {
        // Настройка графа навигации
        destinations.forEach { (route, destination) ->
            // Добавить в NavController
        }
    }
}

@NavigationDsl
class NavDestinationBuilder(private val route: String) {
    var content: @Composable () -> Unit = {}
    var arguments: List<NamedNavArgument> = emptyList()
    var deepLinks: List<String> = emptyList()

    fun build(): NavDestination {
        return NavDestination(
            route = route,
            content = content,
            arguments = arguments,
            deepLinks = deepLinks
        )
    }
}

data class NavDestination(
    val route: String,
    val content: @Composable () -> Unit,
    val arguments: List<NamedNavArgument>,
    val deepLinks: List<String>
)

// DSL функция
fun NavController.navigation(init: NavGraphBuilder.() -> Unit) {
    NavGraphBuilder(this).apply(init).build()
}

// Использование
@Composable
fun MyApp() {
    val navController = rememberNavController()

    navController.navigation {
        screen("home") {
            content = { HomeScreen() }
        }

        screen("profile/{userId}") {
            arguments = listOf(
                navArgument("userId") { type = NavType.StringType }
            )
            deepLinks = listOf("myapp://profile/{userId}")
            content = { ProfileScreen() }
        }

        screen("settings") {
            content = { SettingsScreen() }
        }
    }
}
```

---

### NETWORK REQUEST DSL

```kotlin
@DslMarker
annotation class RequestDsl

@RequestDsl
class RequestBuilder {
    var method: HttpMethod = HttpMethod.GET
    var url: String = ""
    private val headers = mutableMapOf<String, String>()
    private val queryParams = mutableMapOf<String, String>()
    var body: Any? = null

    fun header(name: String, value: String) {
        headers[name] = value
    }

    fun queryParam(name: String, value: String) {
        queryParams[name] = value
    }

    fun build(): HttpRequest {
        return HttpRequest(
            method = method,
            url = url,
            headers = headers,
            queryParams = queryParams,
            body = body
        )
    }
}

enum class HttpMethod { GET, POST, PUT, DELETE, PATCH }

data class HttpRequest(
    val method: HttpMethod,
    val url: String,
    val headers: Map<String, String>,
    val queryParams: Map<String, String>,
    val body: Any?
)

// DSL функции
fun request(init: RequestBuilder.() -> Unit): HttpRequest {
    return RequestBuilder().apply(init).build()
}

fun get(url: String, init: RequestBuilder.() -> Unit = {}): HttpRequest {
    return RequestBuilder().apply {
        method = HttpMethod.GET
        this.url = url
        init()
    }.build()
}

fun post(url: String, init: RequestBuilder.() -> Unit = {}): HttpRequest {
    return RequestBuilder().apply {
        method = HttpMethod.POST
        this.url = url
        init()
    }.build()
}

// Использование
val getUserRequest = get("https://api.example.com/users/123") {
    header("Authorization", "Bearer token")
    header("Accept", "application/json")
    queryParam("include", "profile")
}

val createUserRequest = post("https://api.example.com/users") {
    header("Content-Type", "application/json")
    body = mapOf(
        "name" to "John Doe",
        "email" to "john@example.com"
    )
}
```

---

### TESTING DSL

```kotlin
@DslMarker
annotation class TestDsl

@TestDsl
class TestSuiteBuilder(private val name: String) {
    private val tests = mutableListOf<TestCase>()

    fun test(name: String, body: suspend TestContext.() -> Unit) {
        tests.add(TestCase(name, body))
    }

    suspend fun run() {
        println("Запуск набора тестов: $name")
        tests.forEach { testCase ->
            val context = TestContext()
            try {
                testCase.body(context)
                println(" ${testCase.name}")
            } catch (e: AssertionError) {
                println(" ${testCase.name}: ${e.message}")
            }
        }
    }
}

@TestDsl
class TestContext {
    fun <T> assertThat(actual: T): Assertion<T> {
        return Assertion(actual)
    }

    infix fun <T> T.shouldBe(expected: T) {
        if (this != expected) {
            throw AssertionError("Ожидалось $expected, но получено $this")
        }
    }

    infix fun <T> T.shouldNotBe(expected: T) {
        if (this == expected) {
            throw AssertionError("Ожидалось не $expected, но получено $this")
        }
    }
}

class Assertion<T>(private val actual: T) {
    infix fun isEqualTo(expected: T) {
        if (actual != expected) {
            throw AssertionError("Ожидалось $expected, но получено $actual")
        }
    }

    infix fun isNotEqualTo(expected: T) {
        if (actual == expected) {
            throw AssertionError("Ожидалось не $expected, но получено $actual")
        }
    }
}

data class TestCase(
    val name: String,
    val body: suspend TestContext.() -> Unit
)

// DSL функция
suspend fun testSuite(name: String, init: TestSuiteBuilder.() -> Unit) {
    TestSuiteBuilder(name).apply(init).run()
}

// Использование
suspend fun runTests() {
    testSuite("Тесты репозитория пользователей") {
        test("должен получать пользователя по id") {
            val user = userRepository.getUser("123")
            user.name shouldBe "John Doe"
            user.email shouldBe "john@example.com"
        }

        test("должен выбрасывать исключение для неверного id") {
            assertThat(repository.getUser("invalid")).isEqualTo(null)
        }

        test("должен обновлять пользователя") {
            val updated = repository.updateUser(user.copy(name = "Jane Doe"))
            updated.name shouldBe "Jane Doe"
        }
    }
}
```

---

### COMPOSE-STYLE BUILDER

```kotlin
@DslMarker
annotation class UiDsl

@UiDsl
interface ComponentScope {
    fun add(component: Component)
}

sealed class Component

data class Text(val text: String, val size: Int) : Component()
data class Button(val text: String, val onClick: () -> Unit) : Component()
data class Container(
    val children: List<Component>,
    val padding: Int
) : Component()

class ContainerScope : ComponentScope {
    private val children = mutableListOf<Component>()

    override fun add(component: Component) {
        children.add(component)
    }

    fun build(): List<Component> = children
}

// DSL функции
@UiDsl
fun ComponentScope.text(text: String, size: Int = 14) {
    add(Text(text, size))
}

@UiDsl
fun ComponentScope.button(text: String, onClick: () -> Unit) {
    add(Button(text, onClick))
}

@UiDsl
fun ComponentScope.container(
    padding: Int = 16,
    content: ComponentScope.() -> Unit
) {
    val scope = ContainerScope()
    scope.content()
    add(Container(scope.build(), padding))
}

fun ui(content: ComponentScope.() -> Unit): List<Component> {
    val scope = ContainerScope()
    scope.content()
    return scope.build()
}

// Использование
val screen = ui {
    text("Добро пожаловать в DSL", size = 20)

    button("Нажми меня") {
        println("Кнопка нажата!")
    }

    container(padding = 24) {
        text("Вложенный контент")
        button("Вложенная кнопка") {
            println("Вложенная кнопка нажата")
        }
    }
}
```

---

### ЛУЧШИЕ ПРАКТИКИ

```kotlin
//  Используйте @DslMarker для предотвращения утечки scope
@DslMarker
annotation class MyDsl

//  Используйте лямбду с получателем для API строителей
fun myBuilder(init: MyBuilder.() -> Unit) {
    MyBuilder().init()
}

//  Используйте перегрузку операторов с умом
class HtmlBuilder {
    operator fun String.unaryPlus() {  // +text
        append(this)
    }
}

//  Делайте DSL типобезопасным
class TypeSafeBuilder {
    fun validOption(value: String) { /* только валидные значения */ }
}

//  Не злоупотребляйте перегрузкой операторов
// Плохо: сбивает с толку
class BadBuilder {
    operator fun String.minus(other: String) { }  // text1 - text2 ???
}

//  Предоставляйте хорошие значения по умолчанию
fun layout(
    orientation: Orientation = Orientation.VERTICAL,
    init: LayoutBuilder.() -> Unit
) { }

//  Документируйте использование DSL
/**
 * Создает макет с заданной конфигурацией.
 * Пример:
 * ```kotlin
 * layout {
 *     text("Привет")
 *     button("Нажми") { }
 * }
 * ```
 */
fun layout(init: LayoutBuilder.() -> Unit) { }
```

## Follow-ups

1. How do you make DSLs discoverable in IDE?
2. What's the performance impact of DSL builders?
3. How do you version DSL APIs?
4. What's the difference between DSL and fluent API?
5. How do you test DSL implementations?
6. What are the limitations of Kotlin DSLs?
7. How do you handle DSL error messages?
8. What is the relationship between DSLs and Compose compiler?
9. How do you create reusable DSL components?
10. What are anti-patterns in DSL design?

---

## Related Questions

### Prerequisites (Easier)
- [[q-dagger-build-time-optimization--android--medium]] - Build, Ui
- [[q-build-optimization-gradle--gradle--medium]] - Build, Ui
- [[q-android-build-optimization--android--medium]] - Build, Ui
