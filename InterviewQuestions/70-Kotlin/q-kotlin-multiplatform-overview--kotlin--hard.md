---
id: 20251012-12271111141
title: "Kotlin Multiplatform - How does it work? / Kotlin Multiplatform - Как это работает?"
aliases: []

# Classification
topic: kotlin
subtopics: [kotlin-multiplatform, kmp, cross-platform, native]
question_kind: theory
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository - MEDIUM priority

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-type-aliases--kotlin--medium, q-enum-class-advanced--kotlin--medium, q-extensions-in-java--programming-languages--medium]

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [kotlin, kotlin-multiplatform, kmp, cross-platform, native, difficulty/hard]
---
# Question (EN)
> Kotlin Multiplatform - How does it work?
# Вопрос (RU)
> Kotlin Multiplatform - Как это работает?

---

## Answer (EN)

**Kotlin Multiplatform (KMP)** is a technology that allows sharing code across different platforms (Android, iOS, web, desktop, backend) while maintaining the ability to access platform-specific APIs when needed.

### Core Concept

KMP uses a **"expect/actual" mechanism** to define platform-agnostic code in common modules and platform-specific implementations.

```kotlin
// Common module (shared code)
expect class Platform() {
    val name: String
}

expect fun getPlatform(): Platform

// Android implementation (androidMain)
actual class Platform actual constructor() {
    actual val name: String = "Android ${android.os.Build.VERSION.SDK_INT}"
}

actual fun getPlatform(): Platform = Platform()

// iOS implementation (iosMain)
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
            database.getUser(id)?.let {
                Result.success(it)
            } ?: Result.failure(e)
        }
    }
}

// Shared business logic
class LoginViewModel {
    private val repository = UserRepository(/* ... */)

    suspend fun login(username: String, password: String): LoginResult {
        return repository.authenticate(username, password)
    }
}
```

**2. Platform-Specific Code**

```kotlin
// expect/actual for platform APIs
// commonMain
expect class DatabaseDriver {
    fun createDatabase(): SqlDriver
}

// androidMain
actual class DatabaseDriver {
    actual fun createDatabase(): SqlDriver {
        return AndroidSqliteDriver(
            schema = Database.Schema,
            context = ApplicationContext,
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

**1. Compilation Process**

```
Common Code (Kotlin)
        ↓

   Compiler    
   Frontend    

        ↓
   Kotlin IR (Intermediate Representation)
        ↓

                               
Android Backend        iOS/Native Backend
(JVM bytecode)         (LLVM IR → native)
                               
        ↓                       ↓
    .dex/.jar              .framework/.klib
```

**2. Platform Compilation**

- **Android**: Kotlin → JVM bytecode → DEX
- **iOS**: Kotlin → Kotlin/Native → LLVM IR → ARM64/x86_64
- **JS**: Kotlin → JavaScript
- **Native**: Kotlin → Native binary

### Project Structure

```
project/
 shared/
    commonMain/
       kotlin/
           data/
              UserRepository.kt
              models/
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

**1. Kotlin/Native for iOS**

```kotlin
// iOS bindings are generated automatically
// Can call iOS frameworks directly
import platform.UIKit.*
import platform.Foundation.*

actual fun showNativeDialog(message: String) {
    val alert = UIAlertController.alertControllerWithTitle(
        title = "Alert",
        message = message,
        preferredStyle = UIAlertControllerStyleAlert
    )

    alert.addAction(UIAlertAction.actionWithTitle(
        title = "OK",
        style = UIAlertActionStyleDefault,
        handler = null
    ))

    // Show alert
}
```

**2. Shared Libraries**

Popular KMP libraries:
- **Ktor** - Networking (HTTP client)
- **SQLDelight** - Database
- **Kotlinx.serialization** - JSON parsing
- **Kotlinx.coroutines** - Async operations
- **Kotlinx.datetime** - Date/time handling

```kotlin
// commonMain - Ktor usage
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

### Gradle Configuration

```kotlin
// shared/build.gradle.kts
kotlin {
    // Define targets
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

    // Source sets
    sourceSets {
        val commonMain by getting {
            dependencies {
                implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
                implementation("io.ktor:ktor-client-core:2.3.5")
            }
        }

        val androidMain by getting {
            dependencies {
                implementation("io.ktor:ktor-client-android:2.3.5")
            }
        }

        val iosMain by getting {
            dependencies {
                implementation("io.ktor:ktor-client-darwin:2.3.5")
            }
        }
    }
}
```

### Sharing Strategies

**1. Share Everything (except UI)**

```

   Platform-Specific UI        ← Android: Jetpack Compose
   (Android/iOS)               ← iOS: SwiftUI

   Shared Presentation         ← ViewModels, States

   Shared Business Logic       ← Use Cases, Repositories

   Shared Data Layer           ← Network, Database, Models

```

**2. Share Only Data/Business Logic**

```

   Platform-Specific UI      
   + Presentation              ← ViewModels are native

   Shared Business Logic       ← Use Cases

   Shared Data Layer           ← API, DB

```

### iOS Integration

**1. Generate iOS Framework**

```bash
./gradlew :shared:assembleXCFramework
```

**2. Use in Swift**

```swift
import shared

class ViewController: UIViewController {
    private let viewModel = LoginViewModel()

    func login() {
        viewModel.login(
            username: "user@example.com",
            password: "password"
        ) { result, error in
            if let result = result {
                // Handle success
            }
        }
    }
}
```

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

**2. Dependency Injection**

```kotlin
// Common interface
interface Platform {
    val name: String
    val type: PlatformType
}

// Android implementation
class AndroidPlatform : Platform {
    override val name = "Android"
    override val type = PlatformType.ANDROID
}

// DI setup (common)
class AppModule {
    val platform: Platform = getPlatform()
    val database: Database = createDatabase(platform)
    val repository: UserRepository = UserRepository(database)
}
```

### Threading Model

**Coroutines work differently on iOS**:

```kotlin
// Common code
class DataRepository {
    suspend fun fetchData(): Data {
        return withContext(Dispatchers.IO) {
            api.getData()
        }
    }
}

// iOS: Suspend functions are exposed as async callbacks
// Swift:
repository.fetchData { data, error in
    // Handle result
}

// Or with async/await (Swift 5.5+):
let data = try await repository.fetchData()
```

### Memory Management

**iOS uses ARC, need to be careful with retain cycles**:

```kotlin
// Common - avoid capturing strong references
class ViewModel {
    private var callback: ((Result) -> Unit)? = null

    fun setCallback(cb: (Result) -> Unit) {
        callback = cb
    }

    fun cleanup() {
        callback = null  // Important for iOS to avoid leaks
    }
}
```

### Advantages

1. **Code Reuse**: Share 60-90% of code
2. **Type Safety**: Compile-time checking across platforms
3. **Performance**: Native performance on all platforms
4. **Gradual Adoption**: Can adopt incrementally
5. **Kotlin Ecosystem**: Use Kotlin libraries everywhere

### Limitations

1. **iOS Framework Size**: Can be larger than native
2. **Learning Curve**: Need to understand both platforms
3. **Debugging**: More complex cross-platform debugging
4. **Library Support**: Not all libraries support KMP yet
5. **UI Sharing**: Still need platform-specific UI

### Real-World Example: Login Flow

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
            analytics.logEvent("login_failure", mapOf("error" to e.message))
            Result.failure(e)
        }
    }
}

// expect/actual for token storage
expect class TokenStorage {
    suspend fun saveToken(token: String)
    suspend fun getToken(): String?
}

// Android
actual class TokenStorage(private val context: Context) {
    private val dataStore = context.dataStore

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

**English Summary**: Kotlin Multiplatform enables code sharing across platforms using expect/actual mechanism. Common code compiles to platform-specific targets (JVM for Android, Native for iOS). Share business logic, data layer, models while keeping UI platform-specific. Uses Kotlin/Native for iOS (generates frameworks), Kotlin/JVM for Android. Popular libraries: Ktor, SQLDelight, kotlinx.serialization. Code reuse: 60-90%. Supports gradual adoption and maintains native performance.

## Ответ (RU)

**Kotlin Multiplatform (KMP)** — это технология, позволяющая использовать общий код на разных платформах (Android, iOS, web, desktop, backend), сохраняя возможность доступа к платформо-специфичным API.

### Основная концепция

KMP использует **механизм "expect/actual"** для определения платформо-агностического кода в общих модулях и платформо-специфичных реализаций.

### Архитектура слоев

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
            database.getUser(id)?.let {
                Result.success(it)
            } ?: Result.failure(e)
        }
    }
}
```

**2. Платформо-специфичный код**

```kotlin
// expect/actual для платформенных API
// commonMain
expect class DatabaseDriver {
    fun createDatabase(): SqlDriver
}

// androidMain
actual class DatabaseDriver {
    actual fun createDatabase(): SqlDriver {
        return AndroidSqliteDriver(
            schema = Database.Schema,
            context = ApplicationContext,
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

### Как это работает внутри

**Процесс компиляции:**

```
Общий код (Kotlin)
        ↓
   Компилятор
        ↓
Kotlin IR (Промежуточное представление)
        ↓

                               
Android Backend        iOS/Native Backend
(JVM bytecode)         (LLVM IR → native)
                               
        ↓                       ↓
    .dex/.jar              .framework/.klib
```

### Ключевые технологии

**Популярные KMP библиотеки:**
- **Ktor** - Сеть (HTTP клиент)
- **SQLDelight** - База данных
- **Kotlinx.serialization** - Парсинг JSON
- **Kotlinx.coroutines** - Асинхронные операции
- **Kotlinx.datetime** - Работа с датой/временем

### Конфигурация Gradle

```kotlin
// shared/build.gradle.kts
kotlin {
    androidTarget()

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
                implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
                implementation("io.ktor:ktor-client-core:2.3.5")
            }
        }

        val androidMain by getting {
            dependencies {
                implementation("io.ktor:ktor-client-android:2.3.5")
            }
        }

        val iosMain by getting {
            dependencies {
                implementation("io.ktor:ktor-client-darwin:2.3.5")
            }
        }
    }
}
```

### Стратегии использования

**Делиться всем (кроме UI):**

```

   Платформенный UI            ← Android: Jetpack Compose
   (Android/iOS)               ← iOS: SwiftUI

   Общий Presentation          ← ViewModels, States

   Общая бизнес-логика         ← Use Cases, Repositories

   Общий Data Layer            ← Network, Database, Models

```

### Интеграция с iOS

**Генерация iOS Framework:**

```bash
./gradlew :shared:assembleXCFramework
```

**Использование в Swift:**

```swift
import shared

class ViewController: UIViewController {
    private let viewModel = LoginViewModel()

    func login() {
        viewModel.login(
            username: "user@example.com",
            password: "password"
        ) { result, error in
            if let result = result {
                // Обработка успеха
            }
        }
    }
}
```

### Модель потоков

**Корутины работают по-разному на iOS:**

```kotlin
// Общий код
class DataRepository {
    suspend fun fetchData(): Data {
        return withContext(Dispatchers.IO) {
            api.getData()
        }
    }
}

// iOS: Suspend функции экспонируются как async callbacks
// Swift:
repository.fetchData { data, error in
    // Обработка результата
}

// Или с async/await (Swift 5.5+):
let data = try await repository.fetchData()
```

### Преимущества

1. **Переиспользование кода**: Разделяйте 60-90% кода
2. **Типобезопасность**: Проверка на этапе компиляции
3. **Производительность**: Нативная производительность на всех платформах
4. **Постепенное внедрение**: Можно внедрять инкрементально
5. **Экосистема Kotlin**: Используйте библиотеки Kotlin везде

### Ограничения

1. **Размер iOS Framework**: Может быть больше нативного
2. **Кривая обучения**: Нужно понимать обе платформы
3. **Отладка**: Более сложная кросс-платформенная отладка
4. **Поддержка библиотек**: Не все библиотеки поддерживают KMP
5. **Разделение UI**: Всё ещё нужен платформо-специфичный UI

**Краткое содержание**: Kotlin Multiplatform позволяет разделять код между платформами используя механизм expect/actual. Общий код компилируется в платформо-специфичные таргеты (JVM для Android, Native для iOS). Делитесь бизнес-логикой, data layer, моделями, сохраняя UI платформо-специфичным. Использует Kotlin/Native для iOS, Kotlin/JVM для Android. Популярные библиотеки: Ktor, SQLDelight, kotlinx.serialization. Переиспользование кода: 60-90%. Поддерживает постепенное внедрение и нативную производительность.

---

## References
- [Kotlin Multiplatform Documentation](https://kotlinlang.org/docs/multiplatform.html)
- [Kotlin Multiplatform Mobile](https://kotlinlang.org/lp/mobile/)
- [KMP Samples](https://github.com/JetBrains/compose-multiplatform)

## Related Questions
- [[q-expect-actual-kotlin--kotlin--medium]]
- [[q-kotlin-native--kotlin--hard]]
