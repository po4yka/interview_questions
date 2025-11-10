---
id: android-063
title: "Kotlin Context Receivers / Контекстные ресиверы Kotlin"
aliases: ["Kotlin Context Receivers", "Контекстные ресиверы Kotlin"]
topic: android
subtopics: [coroutines, di-hilt]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-kotlin, q-kotlin-dsl-builders--android--hard]
created: 2025-10-12
updated: 2025-11-10
tags: [android/coroutines, android/di-hilt, api-design, context-receivers, difficulty/hard, dsl, experimental]
sources: ["https://kotlinlang.org/docs/whatsnew15.html#context-receivers"]

---

# Вопрос (RU)
> Что такое context receivers в Kotlin и когда их использовать в Android?

# Question (EN)
> What are Kotlin context receivers and when to use them in Android?

---

## Ответ (RU)

**Краткая версия:**
`Context` receivers позволяют объявлять, какие контексты (типы) должны быть доступны для вызова функции/свойства, чтобы сделать зависимости явными на уровне типов и поддерживать несколько контекстов без проброса параметров.

**Подробная версия:**

**Концепция:**
`Context` receivers — возможность Kotlin, позволяющая объявлять контекстные зависимости для функций и свойств. Ключевое преимущество — поддержка множественных контекстов (в отличие от extension-функций с одним receiver).

(На момент Kotlin 1.6–1.8 — экспериментальная фича с флагом компилятора; в современных версиях Kotlin спецификацию и статус нужно проверять по актуальной документации проекта.)

**Основные концепции:**
- Множественные контексты (extension-функции ограничены одним receiver)
- В ранних версиях требует compiler flag `-Xcontext-receivers`
- Идеальны для DSL и cross-cutting concerns (логирование, навигация, DI)
- Могут упростить dependency injection и сделать зависимости явными на уровне типа (но не являются заменой DI-фреймворков сами по себе)

**Базовый синтаксис:**
```kotlin
// ✅ Множественные контексты для функции
context(Context, CoroutineScope)
fun launchAndShowToast(message: String) {
    launch {
        delay(1000)
        Toast.makeText(this@Context, message, Toast.LENGTH_SHORT).show()
    }
}

// ❌ Extension-функция — только один receiver,
// дополнительные зависимости приходится передавать явно
fun CoroutineScope.showToastInContext(ctx: Context, message: String) {
    launch {
        delay(1000)
        Toast.makeText(ctx, message, Toast.LENGTH_SHORT).show()
    }
}
```

**Dependency Injection паттерн (пример):**
```kotlin
interface DatabaseProvider { val database: AppDatabase }
interface NetworkProvider { val apiService: ApiService }
interface LoggerProvider { val logger: Logger }

// ✅ Фабричный метод для создания репозитория из контекста зависимостей
context(DatabaseProvider, NetworkProvider, LoggerProvider)
fun createUserRepository(): UserRepository =
    UserRepository(
        database = database,
        api = apiService,
        logger = logger
    )

class UserRepository(
    private val database: AppDatabase,
    private val api: ApiService,
    private val logger: Logger,
) {
    suspend fun getUser(userId: String): User {
        logger.log("Getting user: $userId")

        database.userDao().getUser(userId)?.let { return it }

        val user = api.getUser(userId)
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
    private val userRepository = with(deps) { createUserRepository() }
}
```

**Логирование как cross-cutting concern:**
```kotlin
interface Logger {
    fun log(message: String)
    fun error(message: String, throwable: Throwable? = null)
}

interface UserApi {
    suspend fun getUser(userId: String): User
}

context(Logger, UserApi)
suspend fun fetchUser(userId: String): User {
    log("Fetching user: $userId") // ✅ Logger и UserApi доступны из контекста

    return try {
        val user = getUser(userId)
        log("User fetched: ${user.name}")
        user
    } catch (e: Exception) {
        error("Failed to fetch user", e)
        throw e
    }
}
```

**Android-специфичные use cases (упрощённые схемы):**
```kotlin
// ✅ Навигация без явной передачи NavController
interface NavigationContext {
    fun navigate(destination: String)
}

context(NavigationContext)
fun navigateToProfile(userId: String) {
    navigate("profile/$userId")
}

// ✅ Разрешения (детали реализации запроса опущены для краткости)
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

**Short version:**
`Context` receivers let you declare which context types must be in scope to call a function/property, making dependencies explicit in the type system and supporting multiple contexts without threading parameters around.

**Detailed version:**

**Concept:**
`Context` receivers are a Kotlin language feature that allow you to declare contextual dependencies for functions and properties. The key advantage is support for multiple contexts (unlike extension functions, which have a single receiver).

(For Kotlin 1.6–1.8 they were experimental and required a compiler flag; always verify their status against the current Kotlin documentation for your project.)

**Main concepts:**
- Multiple contexts (extension functions limited to one receiver)
- In earlier versions, requires compiler flag `-Xcontext-receivers`
- Ideal for DSLs and cross-cutting concerns (logging, navigation, DI)
- Can simplify dependency injection and make dependencies explicit in the type system (but are not a full replacement for DI frameworks by themselves)

**Basic syntax:**
```kotlin
// ✅ Multiple contexts for a function
context(Context, CoroutineScope)
fun launchAndShowToast(message: String) {
    launch {
        delay(1000)
        Toast.makeText(this@Context, message, Toast.LENGTH_SHORT).show()
    }
}

// ❌ Extension function — only one receiver,
// extra dependencies must be passed explicitly
fun CoroutineScope.showToastInContext(ctx: Context, message: String) {
    launch {
        delay(1000)
        Toast.makeText(ctx, message, Toast.LENGTH_SHORT).show()
    }
}
```

**Dependency Injection pattern (example):**
```kotlin
interface DatabaseProvider { val database: AppDatabase }
interface NetworkProvider { val apiService: ApiService }
interface LoggerProvider { val logger: Logger }

// ✅ Factory-style function that creates a repository from context dependencies
context(DatabaseProvider, NetworkProvider, LoggerProvider)
fun createUserRepository(): UserRepository =
    UserRepository(
        database = database,
        api = apiService,
        logger = logger
    )

class UserRepository(
    private val database: AppDatabase,
    private val api: ApiService,
    private val logger: Logger,
) {
    suspend fun getUser(userId: String): User {
        logger.log("Getting user: $userId")

        database.userDao().getUser(userId)?.let { return it }

        val user = api.getUser(userId)
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
    private val userRepository = with(deps) { createUserRepository() }
}
```

**Logging as cross-cutting concern:**
```kotlin
interface Logger {
    fun log(message: String)
    fun error(message: String, throwable: Throwable? = null)
}

interface UserApi {
    suspend fun getUser(userId: String): User
}

context(Logger, UserApi)
suspend fun fetchUser(userId: String): User {
    log("Fetching user: $userId") // ✅ Logger and UserApi are available from context

    return try {
        val user = getUser(userId)
        log("User fetched: ${user.name}")
        user
    } catch (e: Exception) {
        error("Failed to fetch user", e)
        throw e
    }
}
```

**Android-specific use cases (simplified):**
```kotlin
// ✅ Navigation without explicitly passing NavController
interface NavigationContext {
    fun navigate(destination: String)
}

context(NavigationContext)
fun navigateToProfile(userId: String) {
    navigate("profile/$userId")
}

// ✅ Permissions (request implementation details omitted for brevity)
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

## Дополнительные вопросы / Follow-ups (RU/EN)

- Как context receivers влияют на бинарную совместимость при эволюции библиотеки? / How do context receivers affect binary compatibility when library evolves?
- Каков накладной расход по сравнению с явной передачей параметров? / What's the performance impact compared to explicit parameter passing?
- Как эффективно тестировать код с context receivers? / How do you test code with context receivers effectively?
- Когда стоит предпочесть extension-функции вместо context receivers? / When should you prefer extension functions over context receivers?
- Как context receivers взаимодействуют с inline-функциями и `reified`-типами? / How do context receivers interact with inline functions and reification?

## Ссылки / References (RU/EN)

- [[c-dependency-injection]]
- [Kotlin `Context` Receivers (KEEP)](https://github.com/Kotlin/KEEP/blob/master/proposals/context-receivers.md)
- [Kotlin 1.6.20 Release Notes](https://kotlinlang.org/docs/whatsnew1620.html)

## Связанные вопросы / Related Questions (RU/EN)

### Предпосылки / Prerequisites (Medium)
- [[q-kotlin-value-classes--android--medium]] - Value classes для типобезопасности / Value classes for type safety
- [[q-koin-vs-hilt-comparison--android--medium]] - Паттерны dependency injection / Dependency injection patterns
- [[q-repository-pattern--android--medium]] - Базовые принципы Repository pattern / Repository pattern basics

### Связанные / Related (Same Level)
- [[q-kotlin-dsl-builders--android--hard]] - DSL builders
- [[q-dagger-custom-scopes--android--hard]] - Кастомные DI-скоупы / Custom DI scopes
- [[q-koin-resolution-internals--android--hard]] - Механика разрешения зависимостей / DI resolution mechanics

### Продвинутые / Advanced (Harder)
- [[q-compose-compiler-plugin--android--hard]] - Механика compiler plugin / Compiler plugin mechanics
- [[q-android-runtime-internals--android--hard]] - Внутренние оптимизации рантайма / Runtime optimizations
- [[q-kotlin-dsl-builders--android--hard]] - Продвинутые DSL-паттерны / Advanced DSL patterns
