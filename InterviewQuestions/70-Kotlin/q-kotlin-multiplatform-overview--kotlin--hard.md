---\
id: kotlin-040
title: "Kotlin Multiplatform - How does it work? / Kotlin Multiplatform - Как это работает?"
aliases: ["Kotlin Multiplatform - How does it work?", "Kotlin Multiplatform - Как это работает?"]

# Classification
topic: kotlin
subtopics: [kmp, kotlin-multiplatform]
question_kind: theory
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru]
source: "https://github.com/amitshekhariitbhu/android-interview-questions"
source_note: Amit Shekhar Android Interview Questions repository - MEDIUM priority

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-kotlin, q-enum-class-advanced--kotlin--medium, q-type-aliases--kotlin--medium]

# Timestamps
created: 2025-10-06
updated: 2025-11-09

tags: [cross-platform, difficulty/hard, kmp, kotlin, kotlin-multiplatform, native]
---\
# Вопрос (RU)
> Kotlin Multiplatform - Как это работает?

---

# Question (EN)
> Kotlin Multiplatform - How does it work?

## Ответ (RU)

**Kotlin Multiplatform (KMP)** — это технология, позволяющая использовать общий код на разных платформах (Android, iOS, web, desktop, backend), сохраняя возможность доступа к платформо-специфичным API.

### Основная Концепция

KMP использует механизм **`expect` / `actual`** для определения платформо-агностического API в общих модулях и платформо-специфичных реализаций.

```kotlin
// commonMain (shared code)
expect class Platform() {
    val name: String
}

expect fun getPlatform(): Platform

// androidMain
actual class Platform actual constructor() {
    actual val name: String = "Android ${android.os.Build.VERSION.SDK_INT}"
}

actual fun getPlatform(): Platform = Platform()

// iosMain
actual class Platform actual constructor() {
    actual val name: String = UIDevice.currentDevice.systemName() + " " +
                              UIDevice.currentDevice.systemVersion
}

actual fun getPlatform(): Platform = Platform()
```

### Архитектура Слоев

**1. Общий код (shared code)**

```kotlin
// commonMain/kotlin/data/UserRepository.kt
class UserRepository(
    private val api: ApiClient,
    private val database: Database
) {
    suspend fun getUser(id: String): Result<User> {
        return try {
            val user = api.fetchUser(id)
            database.saveUser(user)
            Result.success(user)
        } catch (e: Exception) {
            database.getUser(id)?.let { cached ->
                Result.success(cached)
            } ?: Result.failure(e)
        }
    }
}
```

Общий код содержит бизнес-логику, доступ к данным и модели.

**2. Платформо-специфичный код**

```kotlin
// expect/actual для платформенных API (концептуальный пример)
// commonMain
expect class DatabaseDriver {
    fun createDatabase(): SqlDriver
}

// androidMain
actual class DatabaseDriver {
    actual fun createDatabase(): SqlDriver {
        return AndroidSqliteDriver(
            schema = Database.Schema,
            context = androidContext, // платформенный контекст передаётся из Android слоя
            name = "app.db"
        )
    }
}

// iosMain
actual class DatabaseDriver {
    actual fun createDatabase(): SqlDriver {
        return NativeSqliteDriver(
            schema = Database.Schema,
            name = "app.db"
        )
    }
}
```

### Как Это Работает Внутри

**Процесс компиляции (упрощённо):**

```text
Общий код (Kotlin)
        ↓
   Фронтенд компилятора
        ↓
Kotlin IR (промежуточное представление)
        ↓

Android backend          iOS/Native backend         JS backend
(JVM bytecode)           (LLVM IR → native)        (JS)
        ↓                        ↓                     ↓
   .class → .dex/.jar      .klib → .framework      .js
```

Общий код компилируется в таргеты конкретных платформ: JVM (Android, backend), Kotlin/Native (iOS, desktop native), JS и др.

#### Примеры Компиляции Под Платформы

- Android: Kotlin → JVM bytecode → DEX
- iOS: Kotlin → Kotlin/Native → LLVM IR → ARM64/x86_64 → framework/xcframework
- JS: Kotlin → JavaScript
- Другие native-таргеты: Kotlin → Kotlin/Native → нативные бинарники

### Структура Проекта (концептуально)

```kotlin
project/
  shared/
    commonMain/
      kotlin/
        data/
          UserRepository.kt
        domain/
          LoginUseCase.kt
        expect/
          Platform.kt
    androidMain/
      kotlin/
        actual/
          Platform.kt
    iosMain/
      kotlin/
        actual/
          Platform.kt
    build.gradle.kts
  androidApp/
    build.gradle.kts
  iosApp/
    iosApp.xcodeproj
```

### Ключевые Технологии

- Kotlin/JVM для Android и backend
- Kotlin/Native для iOS и других native-таргетов
- Kotlin/JS для web

Популярные библиотеки для KMP:
- **Ktor** — HTTP-клиент / сеть
- **SQLDelight** — работа с БД
- **kotlinx.serialization** — сериализация (JSON и др.)
- **kotlinx.coroutines** — асинхронность
- **kotlinx.datetime** — дата/время

```kotlin
// commonMain - пример использования Ktor (концептуально)
class ApiClient {
    private val client = HttpClient {
        install(ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = true
            })
        }
    }

    suspend fun fetchUser(id: String): User {
        return client.get("https://api.example.com/users/$id").body()
    }
}
```

Версии библиотек в примерах условные и могут отличаться от актуальных.

### Конфигурация Gradle (пример, Зависит От Версии Kotlin)

```kotlin
// shared/build.gradle.kts (упрощённый пример)
kotlin {
    androidTarget {
        compilations.all {
            kotlinOptions {
                jvmTarget = "1.8"
            }
        }
    }

    listOf(
        iosX64(),
        iosArm64(),
        iosSimulatorArm64()
    ).forEach {
        it.binaries.framework {
            baseName = "shared"
            isStatic = true
        }
    }

    sourceSets {
        val commonMain by getting {
            dependencies {
                implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core")
                implementation("io.ktor:ktor-client-core")
            }
        }

        val androidMain by getting {
            dependencies {
                implementation("io.ktor:ktor-client-android")
            }
        }

        val iosMain by getting {
            dependencies {
                implementation("io.ktor:ktor-client-darwin")
            }
        }
    }
}
```

### Стратегии Использования

**1. Делиться всем (кроме UI)**

```text
   Платформенный UI            ← Android: Jetpack Compose
   (Android/iOS)               ← iOS: SwiftUI

   Общий Presentation          ← ViewModel'и, состояние

   Общая бизнес-логика         ← Use Cases, Repositories

   Общий Data Layer            ← Network, Database, Models
```

**2. Делить только Data/Business Logic**

```text
   Платформенный UI
   + Presentation              ← ViewModel'и на каждую платформу

   Общая бизнес-логика         ← Use Cases

   Общий Data Layer            ← API, DB
```

### Интеграция С iOS

**Генерация iOS Framework/XCFramework:**

```bash
./gradlew :shared:assembleXCFramework
```

**Использование в Swift (концептуально)**

```swift
import shared

class ViewController: UIViewController {
    private let repository: LoginRepository = LoginRepository(/* deps */)

    func login() {
        // Конкретный способ вызова suspend-функции зависит от сгенерированных bridge-ов.
        // Здесь показан упрощённый концептуальный пример.
        repository.login(email: "user@example.com", password: "password") { result, error in
            if let result = result {
                // Обработка успеха
            }
        }
    }
}
```

Suspend-функции из общего кода при экспорте в Swift доступны через сгенерированные bridge-функции: либо как функции с completion handler, либо как async/await (в зависимости от версии Kotlin/Native и настроек interop). Приведённый пример носит концептуальный характер.

### Обработка Платформенных Различий

**1. Expect/Actual для платформенных API**

```kotlin
// commonMain
expect fun currentTimeMillis(): Long

// androidMain
actual fun currentTimeMillis(): Long = System.currentTimeMillis()

// iosMain
actual fun currentTimeMillis(): Long =
    (NSDate().timeIntervalSince1970 * 1000).toLong()
```

**2. Dependency Injection (концептуально)**

```kotlin
// commonMain
expect fun getPlatform(): Platform

class AppModule {
    private val platform: Platform = getPlatform()
    private val database: Database = createDatabase(platform) // платформенная реализация
    val repository: UserRepository = UserRepository(api = ApiClient(), database = database)
}
```

(Вспомогательные функции вроде `createDatabase` реализуются через expect/actual или предоставляются платформами; пример концептуальный.)

### Модель Потоков

KMP и корутины предоставляют единый API; конкретные диспетчеры реализуются для каждой платформы. В общем коде обычно используют абстракции или инъекцию нужных диспетчеров, чтобы не полагаться на платформо-специфичные детали напрямую.

```kotlin
// Общий код (концептуальный пример)
class DataRepository(
    private val api: ApiClient,
    private val backgroundDispatcher: CoroutineDispatcher
) {
    suspend fun fetchData(): Data {
        return withContext(backgroundDispatcher) {
            api.getData()
        }
    }
}
```

На iOS Kotlin/Native генерирует обёртки, чтобы suspend-функции вызывались из Swift через callbacks или async/await. Нужно уважать правила работы с потоками конкретной платформы и UI-потока.

### Управление Памятью

Kotlin/JVM использует GC; Kotlin/Native использует собственную модель памяти (в новых версиях — новый memory manager). Рекомендации для общего кода:

- Избегать лишних долгоживущих ссылок на платформенные объекты и callbacks.
- Очищать callbacks/слушатели, когда они больше не нужны, чтобы избежать утечек.

```kotlin
class ViewModel {
    private var callback: ((Result) -> Unit)? = null

    fun setCallback(cb: (Result) -> Unit) {
        callback = cb
    }

    fun cleanup() {
        callback = null
    }
}
```

### Преимущества

1. Переиспользование кода: значительная доля общей логики (часто 60–90%)
2. Типобезопасность: проверки на этапе компиляции для всех платформ
3. Производительность: близкая к нативной за счёт JVM/Native/JS таргетов
4. Постепенное внедрение: можно интегрировать KMP в существующие проекты
5. Экосистема Kotlin: использование общих библиотек

### Ограничения

1. Размер артефактов для iOS: framework/xcframework может быть больше нативного аналога
2. Кривая обучения: требуется знание Kotlin и платформ-таргетов
3. Отладка: кросс-платформенная отладка сложнее
4. Поддержка библиотек: не все библиотеки имеют KMP-версии
5. UI: обычно остаётся платформо-специфичным (если не использовать отдельные multiplatform UI-решения)

### Реальный Пример: Login Flow (концептуально)

```kotlin
// shared/commonMain
class LoginRepository(
    private val api: ApiClient,
    private val tokenStorage: TokenStorage,
    private val analytics: Analytics
) {
    suspend fun login(email: String, password: String): Result<User> {
        return try {
            analytics.logEvent("login_attempt")

            val response = api.login(LoginRequest(email, password))
            tokenStorage.saveToken(response.token)

            analytics.logEvent("login_success")
            Result.success(response.user)
        } catch (e: Exception) {
            analytics.logEvent(
                "login_failure",
                mapOf("error" to (e.message ?: "unknown"))
            )
            Result.failure(e)
        }
    }
}

// expect/actual для хранения токена (концептуально)
expect class TokenStorage {
    suspend fun saveToken(token: String)
    suspend fun getToken(): String?
}

// Android
actual class TokenStorage(private val context: Context) {
    private val dataStore = context.dataStore // предполагается предварительное определение delegate

    actual suspend fun saveToken(token: String) {
        dataStore.edit { it[TOKEN_KEY] = token }
    }

    actual suspend fun getToken(): String? {
        return dataStore.data.first()[TOKEN_KEY]
    }
}

// iOS
actual class TokenStorage {
    actual suspend fun saveToken(token: String) {
        NSUserDefaults.standardUserDefaults.setObject(token, forKey = "auth_token")
    }

    actual suspend fun getToken(): String? {
        return NSUserDefaults.standardUserDefaults.stringForKey("auth_token")
    }
}
```

**Краткое содержание**: Kotlin Multiplatform позволяет разделять код между платформами с помощью механизма `expect` / `actual`. Общий код компилируется в платформо-специфичные таргеты (JVM для Android, Native для iOS, JS и др.). Обычно делят бизнес-логику, слой данных и модели, а UI оставляют нативным. Примеры конфигурации Gradle и interop носят концептуальный характер и зависят от версии Kotlin и настроек проекта.

---

## Answer (EN)

**Kotlin Multiplatform (KMP)** is a technology that allows sharing code across different platforms (Android, iOS, web, desktop, backend) while still calling platform-specific APIs when needed.

### Core Concept

KMP uses the **`expect` / `actual` mechanism** to define platform-agnostic APIs in common modules and provide platform-specific implementations.

```kotlin
// commonMain (shared code)
expect class Platform() {
    val name: String
}

expect fun getPlatform(): Platform

// androidMain
actual class Platform actual constructor() {
    actual val name: String = "Android ${android.os.Build.VERSION.SDK_INT}"
}

actual fun getPlatform(): Platform = Platform()

// iosMain
actual class Platform actual constructor() {
    actual val name: String = UIDevice.currentDevice.systemName() + " " +
                              UIDevice.currentDevice.systemVersion
}

actual fun getPlatform(): Platform = Platform()
```

### Architecture Layers

**1. Common Code (shared across all platforms)**

```kotlin
// commonMain/kotlin/data/UserRepository.kt
class UserRepository(
    private val api: ApiClient,
    private val database: Database
) {
    suspend fun getUser(id: String): Result<User> {
        return try {
            val user = api.fetchUser(id)
            database.saveUser(user)
            Result.success(user)
        } catch (e: Exception) {
            database.getUser(id)?.let { cached ->
                Result.success(cached)
            } ?: Result.failure(e)
        }
    }
}
```

Shared code holds business logic, data access, and models.

**2. Platform-Specific Code**

```kotlin
// expect/actual for platform APIs (conceptual example)
// commonMain
expect class DatabaseDriver {
    fun createDatabase(): SqlDriver
}

// androidMain
actual class DatabaseDriver {
    actual fun createDatabase(): SqlDriver {
        return AndroidSqliteDriver(
            schema = Database.Schema,
            context = androidContext, // provided from Android layer
            name = "app.db"
        )
    }
}

// iosMain
actual class DatabaseDriver {
    actual fun createDatabase(): SqlDriver {
        return NativeSqliteDriver(
            schema = Database.Schema,
            name = "app.db"
        )
    }
}
```

### How It Works Internally

**1. Compilation Process (simplified)**

```text
Common Code (Kotlin)
        ↓
   Compiler Frontend
        ↓
   Kotlin IR (Intermediate Representation)
        ↓

Android backend          iOS/Native backend         JS backend
(JVM bytecode)           (LLVM IR → native)        (JS)
        ↓                        ↓                     ↓
   .class → .dex/.jar      .klib → .framework      .js
```

Common code is compiled to concrete platform targets: JVM (Android, server), Native (iOS, desktop), JS, etc.

**2. Platform Compilation Examples**

- Android: Kotlin → JVM bytecode → DEX
- iOS: Kotlin → Kotlin/Native → LLVM IR → ARM64/x86_64 → framework/xcframework
- JS: Kotlin → JavaScript
- Other Native targets: Kotlin → Kotlin/Native → native binaries

### Project Structure (Conceptual)

```kotlin
project/
  shared/
    commonMain/
      kotlin/
        data/
          UserRepository.kt
        domain/
          LoginUseCase.kt
        expect/
          Platform.kt
    androidMain/
      kotlin/
        actual/
          Platform.kt
    iosMain/
      kotlin/
        actual/
          Platform.kt
    build.gradle.kts
  androidApp/
    build.gradle.kts
  iosApp/
    iosApp.xcodeproj
```

### Key Technologies

- Kotlin/JVM for Android and backend
- Kotlin/Native for iOS and other native targets
- Kotlin/JS for web

Popular KMP libraries:
- **Ktor** — Networking (HTTP client)
- **SQLDelight** — `Database`
- **kotlinx.serialization** — Serialization / JSON
- **kotlinx.coroutines** — Async operations
- **kotlinx.datetime** — Date/time

```kotlin
// commonMain - Ktor usage (conceptual)
class ApiClient {
    private val client = HttpClient {
        install(ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = true
            })
        }
    }

    suspend fun fetchUser(id: String): User {
        return client.get("https://api.example.com/users/$id").body()
    }
}
```

(Dependency versions are intentionally omitted; use current stable versions.)

### Gradle Configuration (Example, version-dependent)

```kotlin
// shared/build.gradle.kts (simplified example)
kotlin {
    androidTarget {
        compilations.all {
            kotlinOptions {
                jvmTarget = "1.8"
            }
        }
    }

    listOf(
        iosX64(),
        iosArm64(),
        iosSimulatorArm64()
    ).forEach {
        it.binaries.framework {
            baseName = "shared"
            isStatic = true
        }
    }

    sourceSets {
        val commonMain by getting {
            dependencies {
                implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core")
                implementation("io.ktor:ktor-client-core")
            }
        }

        val androidMain by getting {
            dependencies {
                implementation("io.ktor:ktor-client-android")
            }
        }

        val iosMain by getting {
            dependencies {
                implementation("io.ktor:ktor-client-darwin")
            }
        }
    }
}
```

### Sharing Strategies

**1. Share Everything (except UI)**

```text
   Platform-Specific UI        ← Android: Jetpack Compose
   (Android/iOS)               ← iOS: SwiftUI

   Shared Presentation         ← ViewModels, state

   Shared Business Logic       ← Use Cases, Repositories

   Shared Data Layer           ← Network, Database, Models
```

**2. Share Only Data/Business Logic**

```text
   Platform-Specific UI
   + Presentation              ← ViewModels are per-platform

   Shared Business Logic       ← Use Cases

   Shared Data Layer           ← API, DB
```

### iOS Integration

**1. Generate iOS Framework/XCFramework**

```bash
./gradlew :shared:assembleXCFramework
```

**2. Use in Swift (conceptual)**

```swift
import shared

class ViewController: UIViewController {
    private let repository: LoginRepository = LoginRepository(/* deps */)

    func login() {
        // The exact way to call the suspend function depends on generated bridges.
        // This is a simplified conceptual example.
        repository.login(email: "user@example.com", password: "password") { result, error in
            if let result = result {
                // Handle success
            }
        }
    }
}
```

Suspend functions from Kotlin are exposed to Swift via generated bridge functions as completion-based APIs or async/await functions, depending on Kotlin/Native version and interop configuration. The example above is conceptual.

### Handling Platform Differences

**1. Expect/Actual for Platform APIs**

```kotlin
// Common
expect fun currentTimeMillis(): Long

// Android
actual fun currentTimeMillis(): Long = System.currentTimeMillis()

// iOS
actual fun currentTimeMillis(): Long =
    (NSDate().timeIntervalSince1970 * 1000).toLong()
```

**2. Dependency Injection (conceptual)**

```kotlin
// Common
expect fun getPlatform(): Platform

class AppModule {
    private val platform: Platform = getPlatform()
    private val database: Database = createDatabase(platform) // platform-specific implementation
    val repository: UserRepository = UserRepository(api = ApiClient(), database = database)
}
```

(Helper functions like `createDatabase` are implemented via expect/actual or provided per platform; conceptual example.)

### Threading Model

KMP coroutines provide a unified API; concrete dispatchers are implemented per platform. In shared code you typically inject or abstract dispatchers instead of relying directly on platform-specific ones.

```kotlin
// Common code (conceptual example)
class DataRepository(
    private val api: ApiClient,
    private val backgroundDispatcher: CoroutineDispatcher
) {
    suspend fun fetchData(): Data {
        return withContext(backgroundDispatcher) {
            api.getData()
        }
    }
}
```

On iOS, Kotlin/Native generates appropriate bridge functions so that suspend functions can be called from Swift via callbacks or async/await. You must respect each platform's threading and UI-thread rules.

### Memory Management

Kotlin/JVM uses GC; Kotlin/Native (including iOS) has its own memory management (with a new memory manager in recent versions). General guidelines for shared code:

- Avoid unnecessary long-lived references to platform objects or callbacks.
- Clear callbacks/listeners when they are no longer needed to prevent leaks.

```kotlin
class ViewModel {
    private var callback: ((Result) -> Unit)? = null

    fun setCallback(cb: (Result) -> Unit) {
        callback = cb
    }

    fun cleanup() {
        callback = null
    }
}
```

### Advantages

1. Code Reuse: significant shared logic (often 60–90%)
2. Type Safety: compile-time checks across platforms
3. Performance: close-to-native performance via JVM/Native/JS backends
4. Gradual Adoption: can be integrated incrementally into existing apps
5. Kotlin Ecosystem: reuse Kotlin libraries across platforms

### Limitations

1. iOS Framework Size: framework/xcframework may be larger than a purely native implementation
2. Learning Curve: requires understanding Kotlin and multiple platform targets
3. Debugging: cross-platform debugging can be more complex
4. Library Support: not all libraries are KMP-ready
5. UI Sharing: UI is typically platform-specific (unless using separate multiplatform UI solutions)

### Real-World Example: Login Flow (Conceptual)

```kotlin
// shared/commonMain
class LoginRepository(
    private val api: ApiClient,
    private val tokenStorage: TokenStorage,
    private val analytics: Analytics
) {
    suspend fun login(email: String, password: String): Result<User> {
        return try {
            analytics.logEvent("login_attempt")

            val response = api.login(LoginRequest(email, password))
            tokenStorage.saveToken(response.token)

            analytics.logEvent("login_success")
            Result.success(response.user)
        } catch (e: Exception) {
            analytics.logEvent(
                "login_failure",
                mapOf("error" to (e.message ?: "unknown"))
            )
            Result.failure(e)
        }
    }
}

// expect/actual for token storage (conceptual)
expect class TokenStorage {
    suspend fun saveToken(token: String)
    suspend fun getToken(): String?
}

// Android
actual class TokenStorage(private val context: Context) {
    private val dataStore = context.dataStore // assumes delegated property is defined elsewhere

    actual suspend fun saveToken(token: String) {
        dataStore.edit { it[TOKEN_KEY] = token }
    }

    actual suspend fun getToken(): String? {
        return dataStore.data.first()[TOKEN_KEY]
    }
}

// iOS
actual class TokenStorage {
    actual suspend fun saveToken(token: String) {
        NSUserDefaults.standardUserDefaults.setObject(token, forKey: "auth_token")
    }

    actual suspend fun getToken(): String? {
        return NSUserDefaults.standardUserDefaults.stringForKey("auth_token")
    }
}
```

**English Summary**: Kotlin Multiplatform enables sharing code across platforms using the `expect` / `actual` mechanism. Common code compiles to platform-specific targets (JVM for Android, Native for iOS, JS, etc.). You typically share business logic, data layer, and models while keeping UI platform-specific. The Gradle and interop examples are conceptual and depend on Kotlin version and project configuration.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [Kotlin Multiplatform Documentation](https://kotlinlang.org/docs/multiplatform.html)
- [Kotlin Multiplatform Mobile](https://kotlinlang.org/lp/mobile/)
- [KMP Samples](https://github.com/JetBrains/compose-multiplatform)

## Related Questions
- [[q-expect-actual-kotlin--kotlin--medium]]
- [[q-kotlin-native--kotlin--hard]]
- [[c-kotlin]]
