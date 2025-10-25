---
id: 20251012-400009
title: "Kotlin Context Receivers / Kotlin Context Receivers"
aliases: ["Kotlin Context Receivers"]
topic: android
subtopics: [advanced-features, kotlin]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-context-receivers, q-kotlin-basics--kotlin--easy, q-kotlin-dsl-builders--android--hard]
created: 2025-10-12
updated: 2025-01-25
tags: [android/advanced-features, android/kotlin, api-design, context-receivers, difficulty/hard, dsl, experimental]
sources: [https://kotlinlang.org/docs/whatsnew15.html#context-receivers]
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Saturday, October 25th 2025, 4:07:48 pm
---

# Вопрос (RU)
> Что такое context receivers в Kotlin и когда их использовать в Android?

# Question (EN)
> What are Kotlin context receivers and when to use them in Android?

---

## Ответ (RU)

**Теория Context Receivers:**
Context receivers - экспериментальная возможность Kotlin, позволяющая объявлять контекстные зависимости для функций. Предоставляют более чистую альтернативу extension функциям с receivers, обеспечивая более выразительные DSL и паттерны dependency injection.

**Основные концепции:**
- Множественные контексты возможны (в отличие от extension функций)
- Экспериментальная возможность - требует compiler flag `-Xcontext-receivers`
- Лучше подходят для DSL и cross-cutting concerns
- Упрощают dependency injection без фреймворков

**Базовый синтаксис:**
```kotlin
// Включение в build.gradle
compilerOptions {
    freeCompilerArgs.add("-Xcontext-receivers")
}

// Традиционная extension функция
fun Context.showToast(message: String) {
    Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
}

// С context receiver
context(Context)
fun showToast(message: String) {
    Toast.makeText(this@Context, message, Toast.LENGTH_SHORT).show()
}

// Использование (одинаково для обоих)
fun Activity.someMethod() {
    showToast("Hello")
}
```

**Множественные контексты:**
```kotlin
// Множественные контексты
context(Context, CoroutineScope)
fun launchAndShowToast(message: String) {
    launch {
        delay(1000)
        Toast.makeText(this@Context, message, Toast.LENGTH_SHORT).show()
    }
}

// С тремя контекстами
context(Context, LifecycleOwner, CoroutineScope)
fun observeAndShowData() {
    launch {
        // Можем использовать Context
        val resources = this@Context.resources

        // Можем использовать LifecycleOwner
        lifecycle.addObserver(object : DefaultLifecycleObserver {
            override fun onResume(owner: LifecycleOwner) {
                // Обработка resume
            }
        })

        // Можем использовать CoroutineScope
        delay(1000)
    }
}
```

**Логирование с Context Receivers:**
```kotlin
interface Logger {
    fun log(message: String)
    fun error(message: String, throwable: Throwable? = null)
}

// Функции, требующие логирования
context(Logger)
fun processData(data: String) {
    log("Processing data: $data")

    try {
        // Обработка
        log("Data processed successfully")
    } catch (e: Exception) {
        error("Failed to process data", e)
    }
}

context(Logger)
suspend fun fetchUser(userId: String): User {
    log("Fetching user: $userId")

    return try {
        val user = apiService.getUser(userId)
        log("User fetched: ${user.name}")
        user
    } catch (e: Exception) {
        error("Failed to fetch user", e)
        throw e
    }
}

// Использование
class UserRepository(private val logger: Logger) {
    suspend fun loadUser(userId: String): User {
        with(logger) {
            return fetchUser(userId)
        }
    }
}
```

**Dependency Injection паттерн:**
```kotlin
interface DatabaseProvider {
    val database: AppDatabase
}

interface NetworkProvider {
    val apiService: ApiService
}

interface LoggerProvider {
    val logger: Logger
}

// Repository с context receivers
context(DatabaseProvider, NetworkProvider, LoggerProvider)
class UserRepository {
    suspend fun getUser(userId: String): User {
        logger.log("Getting user: $userId")

        // Сначала проверяем локальную БД
        database.userDao().getUser(userId)?.let {
            logger.log("User found in database")
            return it
        }

        // Загружаем из сети
        logger.log("Fetching from network")
        val user = apiService.getUser(userId)

        // Сохраняем в БД
        database.userDao().insert(user)

        return user
    }
}

// Провайдеры на уровне приложения
class AppDependencies : DatabaseProvider, NetworkProvider, LoggerProvider {
    override val database: AppDatabase by lazy {
        Room.databaseBuilder(context, AppDatabase::class.java, "app.db").build()
    }

    override val apiService: ApiService by lazy {
        Retrofit.Builder()
            .baseUrl("https://api.example.com")
            .build()
            .create(ApiService::class.java)
    }

    override val logger: Logger = AndroidLogger()
}

// Использование
class MyViewModel(private val deps: AppDependencies) : ViewModel() {
    private val userRepository = with(deps) {
        UserRepository()
    }
}
```

**DSL Builders:**
```kotlin
interface HtmlContext {
    fun tag(name: String, content: HtmlContext.() -> Unit)
    fun text(content: String)
}

context(HtmlContext)
fun head(content: HtmlContext.() -> Unit) {
    tag("head", content)
}

context(HtmlContext)
fun body(content: HtmlContext.() -> Unit) {
    tag("body", content)
}

context(HtmlContext)
fun title(text: String) {
    tag("title") {
        text(text)
    }
}

context(HtmlContext)
fun h1(text: String) {
    tag("h1") {
        text(text)
    }
}

// Использование
val htmlContent = html {
    head {
        title("My Page")
    }
    body {
        h1("Welcome")
        p("This is a paragraph")
    }
}
```

**Android-специфичные use cases:**
```kotlin
// Доступ к ресурсам
interface ResourceContext {
    val context: Context
    val resources: Resources
}

context(ResourceContext)
fun getString(@StringRes resId: Int): String {
    return resources.getString(resId)
}

context(ResourceContext)
fun getColor(@ColorRes resId: Int): Int {
    return resources.getColor(resId, null)
}

// Навигация
interface NavigationContext {
    fun navigate(destination: String)
    fun navigateBack()
    fun navigateUp()
}

context(NavigationContext)
fun navigateToProfile(userId: String) {
    navigate("profile/$userId")
}

context(NavigationContext)
fun navigateToSettings() {
    navigate("settings")
}

// Разрешения
interface PermissionContext {
    fun hasPermission(permission: String): Boolean
    fun requestPermission(permission: String)
}

context(PermissionContext)
fun checkCameraPermission(): Boolean {
    return hasPermission(Manifest.permission.CAMERA)
}

context(PermissionContext, Context)
fun openCamera() {
    if (checkCameraPermission()) {
        val intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
        this@Context.startActivity(intent)
    } else {
        requestPermission(Manifest.permission.CAMERA)
    }
}
```

## Answer (EN)

**Context Receivers Theory:**
Context receivers are an experimental Kotlin feature that allows declaring context dependencies for functions. They provide a cleaner alternative to extension functions with receivers, enabling more expressive DSLs and dependency injection patterns.

**Main concepts:**
- Multiple contexts possible (unlike extension functions)
- Experimental feature - requires compiler flag `-Xcontext-receivers`
- Better suited for DSLs and cross-cutting concerns
- Simplify dependency injection without frameworks

**Basic syntax:**
```kotlin
// Enable in build.gradle
compilerOptions {
    freeCompilerArgs.add("-Xcontext-receivers")
}

// Traditional extension function
fun Context.showToast(message: String) {
    Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
}

// With context receiver
context(Context)
fun showToast(message: String) {
    Toast.makeText(this@Context, message, Toast.LENGTH_SHORT).show()
}

// Usage (same for both)
fun Activity.someMethod() {
    showToast("Hello")
}
```

**Multiple contexts:**
```kotlin
// Multiple contexts
context(Context, CoroutineScope)
fun launchAndShowToast(message: String) {
    launch {
        delay(1000)
        Toast.makeText(this@Context, message, Toast.LENGTH_SHORT).show()
    }
}

// With three contexts
context(Context, LifecycleOwner, CoroutineScope)
fun observeAndShowData() {
    launch {
        // Can use Context
        val resources = this@Context.resources

        // Can use LifecycleOwner
        lifecycle.addObserver(object : DefaultLifecycleObserver {
            override fun onResume(owner: LifecycleOwner) {
                // Handle resume
            }
        })

        // Can use CoroutineScope
        delay(1000)
    }
}
```

**Logging with Context Receivers:**
```kotlin
interface Logger {
    fun log(message: String)
    fun error(message: String, throwable: Throwable? = null)
}

// Functions that require logging
context(Logger)
fun processData(data: String) {
    log("Processing data: $data")

    try {
        // Process
        log("Data processed successfully")
    } catch (e: Exception) {
        error("Failed to process data", e)
    }
}

context(Logger)
suspend fun fetchUser(userId: String): User {
    log("Fetching user: $userId")

    return try {
        val user = apiService.getUser(userId)
        log("User fetched: ${user.name}")
        user
    } catch (e: Exception) {
        error("Failed to fetch user", e)
        throw e
    }
}

// Usage
class UserRepository(private val logger: Logger) {
    suspend fun loadUser(userId: String): User {
        with(logger) {
            return fetchUser(userId)
        }
    }
}
```

**Dependency Injection pattern:**
```kotlin
interface DatabaseProvider {
    val database: AppDatabase
}

interface NetworkProvider {
    val apiService: ApiService
}

interface LoggerProvider {
    val logger: Logger
}

// Repository with context receivers
context(DatabaseProvider, NetworkProvider, LoggerProvider)
class UserRepository {
    suspend fun getUser(userId: String): User {
        logger.log("Getting user: $userId")

        // Try local database first
        database.userDao().getUser(userId)?.let {
            logger.log("User found in database")
            return it
        }

        // Fetch from network
        logger.log("Fetching from network")
        val user = apiService.getUser(userId)

        // Save to database
        database.userDao().insert(user)

        return user
    }
}

// Application-level providers
class AppDependencies : DatabaseProvider, NetworkProvider, LoggerProvider {
    override val database: AppDatabase by lazy {
        Room.databaseBuilder(context, AppDatabase::class.java, "app.db").build()
    }

    override val apiService: ApiService by lazy {
        Retrofit.Builder()
            .baseUrl("https://api.example.com")
            .build()
            .create(ApiService::class.java)
    }

    override val logger: Logger = AndroidLogger()
}

// Usage
class MyViewModel(private val deps: AppDependencies) : ViewModel() {
    private val userRepository = with(deps) {
        UserRepository()
    }
}
```

**DSL Builders:**
```kotlin
interface HtmlContext {
    fun tag(name: String, content: HtmlContext.() -> Unit)
    fun text(content: String)
}

context(HtmlContext)
fun head(content: HtmlContext.() -> Unit) {
    tag("head", content)
}

context(HtmlContext)
fun body(content: HtmlContext.() -> Unit) {
    tag("body", content)
}

context(HtmlContext)
fun title(text: String) {
    tag("title") {
        text(text)
    }
}

context(HtmlContext)
fun h1(text: String) {
    tag("h1") {
        text(text)
    }
}

// Usage
val htmlContent = html {
    head {
        title("My Page")
    }
    body {
        h1("Welcome")
        p("This is a paragraph")
    }
}
```

**Android-specific use cases:**
```kotlin
// Resource access
interface ResourceContext {
    val context: Context
    val resources: Resources
}

context(ResourceContext)
fun getString(@StringRes resId: Int): String {
    return resources.getString(resId)
}

context(ResourceContext)
fun getColor(@ColorRes resId: Int): Int {
    return resources.getColor(resId, null)
}

// Navigation
interface NavigationContext {
    fun navigate(destination: String)
    fun navigateBack()
    fun navigateUp()
}

context(NavigationContext)
fun navigateToProfile(userId: String) {
    navigate("profile/$userId")
}

context(NavigationContext)
fun navigateToSettings() {
    navigate("settings")
}

// Permissions
interface PermissionContext {
    fun hasPermission(permission: String): Boolean
    fun requestPermission(permission: String)
}

context(PermissionContext)
fun checkCameraPermission(): Boolean {
    return hasPermission(Manifest.permission.CAMERA)
}

context(PermissionContext, Context)
fun openCamera() {
    if (checkCameraPermission()) {
        val intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
        this@Context.startActivity(intent)
    } else {
        requestPermission(Manifest.permission.CAMERA)
    }
}
```

---

## Follow-ups

- How do context receivers affect binary compatibility?
- What's the performance impact of context receivers?
- How do you test code with context receivers?

## Related Questions

### Prerequisites (Easier)
- [[q-kotlin-basics--kotlin--easy]] - Kotlin basics
- [[q-android-app-components--android--easy]] - App components

### Related (Same Level)
- [[q-kotlin-dsl-builders--android--hard]] - DSL builders
- [[q-kotlin-extension-functions--kotlin--medium]] - Extension functions
- [[q-kotlin-lambda-receivers--kotlin--medium]] - Lambda receivers

### Advanced (Harder)
- [[q-kotlin-multiplatform--kotlin--hard]] - Multiplatform
- [[q-kotlin-coroutines-advanced--kotlin--hard]] - Advanced coroutines
