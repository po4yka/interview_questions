---
id: android-063
title: "Kotlin Context Receivers / Kotlin Context Receivers"
aliases: ["Kotlin Context Receivers", "Kotlin Context Receivers"]
topic: android
subtopics: [coroutines, di-hilt]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-kotlin-dsl-builders--android--hard, q-coroutines-basics--kotlin--medium]
created: 2025-10-12
updated: 2025-10-28
tags: [android/coroutines, android/di-hilt, api-design, context-receivers, difficulty/hard, dsl, experimental]
sources: [https://kotlinlang.org/docs/whatsnew15.html#context-receivers]
date created: Tuesday, October 28th 2025, 9:23:51 pm
date modified: Thursday, October 30th 2025, 3:11:54 pm
---

# Вопрос (RU)
> Что такое context receivers в Kotlin и когда их использовать в Android?

# Question (EN)
> What are Kotlin context receivers and when to use them in Android?

---

## Ответ (RU)

**Концепция:**
Context receivers — экспериментальная возможность Kotlin, позволяющая объявлять контекстные зависимости для функций. Ключевое преимущество — поддержка множественных контекстов (в отличие от extension-функций).

**Основные концепции:**
- Множественные контексты (extension-функции ограничены одним receiver)
- Требует compiler flag `-Xcontext-receivers`
- Идеальны для DSL и cross-cutting concerns (логирование, навигация, DI)
- Упрощают dependency injection без фреймворков

**Базовый синтаксис:**
```kotlin
// ✅ Множественные контексты
context(Context, CoroutineScope)
fun launchAndShowToast(message: String) {
    launch {
        delay(1000)
        Toast.makeText(this@Context, message, Toast.LENGTH_SHORT).show()
    }
}

// ❌ Extension-функция — только один receiver
fun CoroutineScope.showToastInContext(ctx: Context, message: String) {
    launch { /* Громоздко, передаём Context явно */ }
}
```

**Dependency Injection паттерн:**
```kotlin
interface DatabaseProvider { val database: AppDatabase }
interface NetworkProvider { val apiService: ApiService }
interface LoggerProvider { val logger: Logger }

// ✅ Repository получает зависимости через context
context(DatabaseProvider, NetworkProvider, LoggerProvider)
class UserRepository {
    suspend fun getUser(userId: String): User {
        logger.log("Getting user: $userId")

        database.userDao().getUser(userId)?.let { return it }

        val user = apiService.getUser(userId)
        database.userDao().insert(user)
        return user
    }
}

// Использование
class AppDependencies : DatabaseProvider, NetworkProvider, LoggerProvider {
    override val database = Room.databaseBuilder(/*...*/).build()
    override val apiService = Retrofit.Builder().build().create(/*...*/)
    override val logger = AndroidLogger()
}

class MyViewModel(private val deps: AppDependencies) : ViewModel() {
    private val userRepository = with(deps) { UserRepository() }
}
```

**Логирование как cross-cutting concern:**
```kotlin
interface Logger {
    fun log(message: String)
    fun error(message: String, throwable: Throwable? = null)
}

context(Logger)
suspend fun fetchUser(userId: String): User {
    log("Fetching user: $userId") // ✅ Не передаём logger явно

    return try {
        val user = apiService.getUser(userId)
        log("User fetched: ${user.name}")
        user
    } catch (e: Exception) {
        error("Failed to fetch user", e) // ✅ Доступно из контекста
        throw e
    }
}
```

**Android-специфичные use cases:**
```kotlin
// ✅ Навигация без передачи NavController
interface NavigationContext {
    fun navigate(destination: String)
}

context(NavigationContext)
fun navigateToProfile(userId: String) {
    navigate("profile/$userId")
}

// ✅ Разрешения
interface PermissionContext {
    fun hasPermission(permission: String): Boolean
    fun requestPermission(permission: String)
}

context(PermissionContext, Context)
fun openCamera() {
    if (hasPermission(Manifest.permission.CAMERA)) {
        val intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
        this@Context.startActivity(intent)
    } else {
        requestPermission(Manifest.permission.CAMERA)
    }
}
```

## Answer (EN)

**Concept:**
Context receivers are an experimental Kotlin feature that allows declaring context dependencies for functions. Key advantage — support for multiple contexts (unlike extension functions).

**Main concepts:**
- Multiple contexts (extension functions limited to one receiver)
- Requires compiler flag `-Xcontext-receivers`
- Ideal for DSLs and cross-cutting concerns (logging, navigation, DI)
- Simplify dependency injection without frameworks

**Basic syntax:**
```kotlin
// ✅ Multiple contexts
context(Context, CoroutineScope)
fun launchAndShowToast(message: String) {
    launch {
        delay(1000)
        Toast.makeText(this@Context, message, Toast.LENGTH_SHORT).show()
    }
}

// ❌ Extension function — only one receiver
fun CoroutineScope.showToastInContext(ctx: Context, message: String) {
    launch { /* Verbose, pass Context explicitly */ }
}
```

**Dependency Injection pattern:**
```kotlin
interface DatabaseProvider { val database: AppDatabase }
interface NetworkProvider { val apiService: ApiService }
interface LoggerProvider { val logger: Logger }

// ✅ Repository receives dependencies via context
context(DatabaseProvider, NetworkProvider, LoggerProvider)
class UserRepository {
    suspend fun getUser(userId: String): User {
        logger.log("Getting user: $userId")

        database.userDao().getUser(userId)?.let { return it }

        val user = apiService.getUser(userId)
        database.userDao().insert(user)
        return user
    }
}

// Usage
class AppDependencies : DatabaseProvider, NetworkProvider, LoggerProvider {
    override val database = Room.databaseBuilder(/*...*/).build()
    override val apiService = Retrofit.Builder().build().create(/*...*/)
    override val logger = AndroidLogger()
}

class MyViewModel(private val deps: AppDependencies) : ViewModel() {
    private val userRepository = with(deps) { UserRepository() }
}
```

**Logging as cross-cutting concern:**
```kotlin
interface Logger {
    fun log(message: String)
    fun error(message: String, throwable: Throwable? = null)
}

context(Logger)
suspend fun fetchUser(userId: String): User {
    log("Fetching user: $userId") // ✅ Don't pass logger explicitly

    return try {
        val user = apiService.getUser(userId)
        log("User fetched: ${user.name}")
        user
    } catch (e: Exception) {
        error("Failed to fetch user", e) // ✅ Available from context
        throw e
    }
}
```

**Android-specific use cases:**
```kotlin
// ✅ Navigation without passing NavController
interface NavigationContext {
    fun navigate(destination: String)
}

context(NavigationContext)
fun navigateToProfile(userId: String) {
    navigate("profile/$userId")
}

// ✅ Permissions
interface PermissionContext {
    fun hasPermission(permission: String): Boolean
    fun requestPermission(permission: String)
}

context(PermissionContext, Context)
fun openCamera() {
    if (hasPermission(Manifest.permission.CAMERA)) {
        val intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
        this@Context.startActivity(intent)
    } else {
        requestPermission(Manifest.permission.CAMERA)
    }
}
```

---

## Follow-ups

- How do context receivers affect binary compatibility when library evolves?
- What's the performance impact compared to explicit parameter passing?
- How do you test code with context receivers effectively?
- When should you prefer extension functions over context receivers?
- How do context receivers interact with inline functions and reification?

## References

- [[c-dependency-injection]] - Dependency injection patterns
- [[c-kotlin-dsl]] - DSL builders in Kotlin
- [Kotlin Context Receivers (KEEP)](https://github.com/Kotlin/KEEP/blob/master/proposals/context-receivers.md)
- [Kotlin 1.6.20 Release Notes](https://kotlinlang.org/docs/whatsnew1620.html)

## Related Questions

### Prerequisites (Easier)
- [[q-kotlin-extension-functions--kotlin--medium]] - Extension functions basics
- [[q-dependency-injection-basics--android--medium]] - DI fundamentals

### Related (Same Level)
- [[q-kotlin-dsl-builders--android--hard]] - DSL builders
- [[q-hilt-dependency-injection--android--hard]] - Hilt DI framework
- [[q-kotlin-scope-functions--kotlin--medium]] - Scope functions (with, apply, etc.)

### Advanced (Harder)
- [[q-kotlin-compiler-plugins--kotlin--hard]] - Compiler plugins
- [[q-advanced-coroutines-patterns--android--hard]] - Advanced coroutines patterns
