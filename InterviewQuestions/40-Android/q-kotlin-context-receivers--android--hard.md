---
id: android-063
title: Kotlin Context Receivers / Контекстные ресиверы Kotlin
aliases:
- Kotlin Context Receivers
- Контекстные ресиверы Kotlin
topic: android
subtopics:
- coroutines
- di-hilt
question_kind: android
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c--android
- q-kotlin-dsl-builders--android--hard
created: 2025-10-12
updated: 2025-11-10
tags:
- android/coroutines
- android/di-hilt
- api-design
- context-receivers
- difficulty/hard
- dsl
- experimental
sources:
- https://kotlinlang.org/docs/whatsnew15.html#context-receivers
anki_cards:
- slug: android-063-0-en
  language: en
  anki_id: 1768380467128
  synced_at: '2026-01-23T16:45:05.885422'
- slug: android-063-0-ru
  language: ru
  anki_id: 1768380467152
  synced_at: '2026-01-23T16:45:05.887220'
---
# Вопрос (RU)
> Что такое context receivers в Kotlin и когда их использовать в Android?

# Question (EN)
> What are Kotlin context receivers and when to use them in Android?

---

## Ответ (RU)

**Краткая версия:**
`Context` receivers позволяют объявлять, какие контекстные типы (implicit receivers) должны быть в области видимости при вызове функции/свойства. Это делает зависимости явными на уровне типов, позволяет использовать несколько контекстов без проброса параметров и без создания дополнительных обёрток.

**Подробная версия:**

**Концепция:**
`Context` receivers — возможность Kotlin, позволяющая объявлять контекстные зависимости для функций и свойств: функция может быть вызвана только при наличии определённых implicit receivers в области видимости. Ключевое преимущество — поддержка множественных контекстов (в отличие от extension-функций с одним receiver).

(В Kotlin 1.6–1.8 фича была экспериментальной и требовала флаг компилятора; в современных версиях Kotlin (2.x) контекстные ресиверы уже стабилизированы. Всегда проверяйте актуальную документацию для вашей версии Kotlin.)

**Основные концепции:**
- Множественные контексты (extension-функции ограничены одним receiver)
- В ранних версиях требовали compiler flag `-Xcontext-receivers`
- В актуальных версиях Kotlin — стабильная часть языка (без дополнительных флагов)
- Идеальны для DSL и cross-cutting concerns (логирование, навигация, DI)
- Могут упростить dependency injection и сделать зависимости явными на уровне типа (но не являются заменой DI-фреймворков сами по себе)
- Отличаются от extension-функций тем, что добавляют требования к окружению вызова (set of implicit receivers), а не только один дополнительный receiver

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

**`Short` version:**
`Context` receivers let you declare which contextual types (implicit receivers) must be in scope to call a function/property. This makes dependencies explicit in the type system and supports multiple contexts without threading parameters around or wrapping them.

**Detailed version:**

**Concept:**
`Context` receivers are a Kotlin language feature that allow you to declare contextual dependencies for functions and properties: a function can only be called when specific implicit receivers are available in scope. The key advantage is support for multiple contexts (unlike extension functions, which have a single receiver).

(For Kotlin 1.6–1.8 they were experimental and required a compiler flag; in modern Kotlin (2.x) context receivers are stabilized. Always verify their status against the Kotlin docs for the version used in your project.)

**Main concepts:**
- Multiple contexts (extension functions are limited to one receiver)
- In earlier versions, required the `-Xcontext-receivers` compiler flag
- In current Kotlin versions, they are a stable part of the language (no extra flags)
- Ideal for DSLs and cross-cutting concerns (logging, navigation, DI)
- Can simplify dependency injection and make dependencies explicit in the type system (but are not a full DI framework replacement)
- Unlike plain extension functions, they add requirements on the call-site environment (a set of implicit receivers), not just a single extra receiver

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

## Дополнительные Вопросы (RU)

- Как context receivers влияют на бинарную совместимость при эволюции библиотеки?
- Каков накладной расход по сравнению с явной передачей параметров?
- Как эффективно тестировать код с context receivers?
- Когда стоит предпочесть extension-функции вместо context receivers?
- Как context receivers взаимодействуют с inline-функциями и `reified`-типами?

## Follow-ups (EN)

- How do context receivers affect binary compatibility when library evolves?
- What's the performance impact compared to explicit parameter passing?
- How do you test code with context receivers effectively?
- When should you prefer extension functions over context receivers?
- How do context receivers interact with inline functions and reification?

## Ссылки (RU)

- [[c--android]]
- [Kotlin `Context` Receivers (KEEP)](https://github.com/Kotlin/KEEP/blob/master/proposals/context-receivers.md)
- [Kotlin 1.6.20 Release Notes](https://kotlinlang.org/docs/whatsnew1620.html)

## References (EN)

- [[c--android]]
- [Kotlin `Context` Receivers (KEEP)](https://github.com/Kotlin/KEEP/blob/master/proposals/context-receivers.md)
- [Kotlin 1.6.20 Release Notes](https://kotlinlang.org/docs/whatsnew1620.html)

## Связанные Вопросы (RU)

### Предпосылки (Medium)
- [[q-kotlin-dsl-builders--android--hard]] - DSL builders

### Связанные (Same Level)
- [[q-kotlin-dsl-builders--android--hard]] - DSL builders

### Продвинутые (Harder)
- [[q-android-runtime-internals--android--hard]] - Внутренние оптимизации рантайма

## Related Questions (EN)

### Prerequisites (Medium)
- [[q-kotlin-dsl-builders--android--hard]] - DSL builders

### Related (Same Level)
- [[q-kotlin-dsl-builders--android--hard]] - DSL builders

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]] - Runtime internals
