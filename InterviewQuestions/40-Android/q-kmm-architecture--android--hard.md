---
id: android-435
title: "KMM Architecture / Архитектура KMM"
aliases: ["KMM Architecture", "Kotlin Multiplatform Mobile", "Архитектура KMM"]
topic: android
subtopics: [architecture-clean, kmp]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android, q-clean-architecture-android--android--hard, q-mvi-architecture--android--hard]
created: 2025-10-15
updated: 2025-11-11
sources: []
tags: [android, android/architecture-clean, android/kmp, difficulty/hard, kmm, kotlin, multiplatform]

date created: Saturday, November 1st 2025, 1:01:27 pm
date modified: Tuesday, November 25th 2025, 8:53:59 pm
---

# Вопрос (RU)

> Объясните архитектуру Kotlin Multiplatform Mobile (KMM) и структуру проекта. Как организовать shared код между Android и iOS? Что такое expect/actual механизмы? Как обрабатывать platform-specific реализации максимизируя переиспользование кода?

# Question (EN)

> Explain Kotlin Multiplatform Mobile (KMM) architecture and project structure. How do you organize shared code between Android and iOS? What are expect/actual mechanisms? How do you handle platform-specific implementations while maximizing code reuse?

---

## Ответ (RU)

KMM позволяет делиться бизнес-логикой, сетью и data слоями между Android и iOS, сохраняя UI platform-specific и обычно достигая порядка 60-80% переиспользования кода (в зависимости от проекта).

## Краткая Версия (RU)
- Общая бизнес-логика, сеть, кэш и доменная модель в `commonMain`.
- UI, DI-фреймворки и интеграция с платформой остаются нативными (`androidMain`, `iosMain`).
- Используйте `expect/actual` для тонких адаптеров к платформенным API.
- Стройте архитектуру вокруг Clean Architecture (Domain/Data/Presentation) и избегайте избыточного шаринга UI.

## Подробная Версия (RU)
### Требования

- Функциональные:
  - Общий слой бизнес-логики, работы с сетью и данными для Android и iOS.
  - Возможность платформенно-специфичных реализаций (логирование, хранилище, UI, системные API).
  - Четкие и устойчивые к изменениям API shared-модуля для обеих платформ.
- Нефункциональные:
  - Высокая степень переиспользования кода без ухудшения UX.
  - Простая интеграция с Android Studio/Xcode и CI.
  - Хорошая читаемость и предсказуемое поведение API для Swift.
  - Масштабируемость архитектуры для роста числа фич и команд.

### Архитектура

Высокоуровневая схема:
- `shared` модуль (KMM): домен, дата-слой, use-case, кросс-платформенные сервисы.
- `androidApp`: Android UI (Compose/Views), DI (Hilt и т.п.), навигация, интеграция с `shared`.
- `iosApp`: iOS UI (SwiftUI/UIKit), DI/композиция зависимостей на стороне iOS, интеграция с экспортируемым `shared` фреймворком.
- Тонкие `expect/actual` адаптеры для платформенных API.

### Структура Проекта

**Модули:**
```
shared/          # Общий Kotlin код
  commonMain/    # Код для всех платформ
  androidMain/   # Android-specific
  iosMain/       # iOS-specific (через iosX64Main, iosArm64Main, iosSimulatorArm64Main)
androidApp/      # Android приложение
iosApp/          # iOS Xcode проект
```

**Build Configuration (упрощенный пример, классический стиль):**
```kotlin
// shared/build.gradle.kts
kotlin {
    android()

    // iOS targets
    listOf(iosX64(), iosArm64(), iosSimulatorArm64()).forEach {
        it.binaries.framework {
            baseName = "shared"
            isStatic = true
        }
    }

    sourceSets {
        val commonMain by getting {
            dependencies {
                implementation("io.ktor:ktor-client-core")
                implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core")
            }
        }
        val androidMain by getting {
            dependencies {
                implementation("io.ktor:ktor-client-android")
            }
        }
        // Общий iOS source set, от которого зависят конкретные iOS таргеты
        val iosX64Main by getting
        val iosArm64Main by getting
        val iosSimulatorArm64Main by getting

        val iosMain by creating {
            dependsOn(commonMain)
            dependencies {
                implementation("io.ktor:ktor-client-darwin")
            }
        }

        iosX64Main.dependsOn(iosMain)
        iosArm64Main.dependsOn(iosMain)
        iosSimulatorArm64Main.dependsOn(iosMain)
    }
}
```

(В реальных проектах используйте актуальный стиль конфигурации Multiplatform-плагина и иерархические source sets; важно правильно связать `iosMain` с конкретными таргетами.)

### Expect/Actual Механизм

**Назначение:** Абстракция platform-specific функционала.

```kotlin
// ✅ commonMain - expect declaration
expect class Platform() {
    val name: String
    val version: String
}

expect fun generateUUID(): String

// ✅ androidMain - actual implementation
actual class Platform {
    actual val name: String = "Android"
    actual val version: String = android.os.Build.VERSION.RELEASE ?: "Unknown"
}

actual fun generateUUID(): String = java.util.UUID.randomUUID().toString()

// ✅ iosMain - actual implementation
actual class Platform {
    actual val name: String = platform.UIKit.UIDevice.currentDevice.systemName
    actual val version: String = platform.UIKit.UIDevice.currentDevice.systemVersion
}

actual fun generateUUID(): String = platform.Foundation.NSUUID().UUIDString()
```

**Применение:**
- Database drivers (например, SQLDelight)
- Логирование (Logcat vs NSLog)
- Доступ к файловой системе
- Доступ к системным API, недоступным в `commonMain`

### Shared Business Logic

**Repository Pattern:**
```kotlin
// ✅ commonMain - Repository interface
interface TaskRepository {
    suspend fun getTasks(): Result<List<Task>>
    suspend fun createTask(task: Task): Result<Task>
    fun observeTasks(): Flow<List<Task>>
}

// ✅ commonMain - Implementation with offline-first strategy
class TaskRepositoryImpl(
    private val apiService: TaskApiService,
    private val database: TaskDatabase
) : TaskRepository {

    private val tasksFlow = MutableStateFlow<List<Task>>(emptyList())

    override suspend fun getTasks(): Result<List<Task>> {
        return try {
            // Fetch remote
            val remoteTasks = apiService.getTasks().map { it.toDomain() }

            // Update local cache
            remoteTasks.forEach { database.insertTask(it) }
            tasksFlow.value = remoteTasks

            Result.success(remoteTasks)
        } catch (e: Exception) {
            // ✅ Fallback to local cache on network failure
            val localTasks = database.getAllTasks()
            if (localTasks.isNotEmpty()) {
                tasksFlow.value = localTasks
                Result.success(localTasks)
            } else {
                Result.failure(e)
            }
        }
    }

    override suspend fun createTask(task: Task): Result<Task> {
        return try {
            val created = apiService.createTask(task).toDomain()
            database.insertTask(created)
            // обновляем flow (упрощенно)
            tasksFlow.value = tasksFlow.value + created
            Result.success(created)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override fun observeTasks(): Flow<List<Task>> = tasksFlow.asStateFlow()
}
```

**Use Cases:**
```kotlin
import kotlin.system.getTimeMillis

// ✅ Encapsulate business logic
class CreateTaskUseCase(private val repository: TaskRepository) {
    suspend operator fun invoke(title: String, description: String): Result<Task> {
        if (title.isBlank()) {
            return Result.failure(IllegalArgumentException("Title required"))
        }

        val task = Task(
            id = generateUUID(),
            title = title.trim(),
            description = description.trim(),
            completed = false,
            createdAt = getTimeMillis()
        )

        return repository.createTask(task)
    }
}
```

### Platform Integration

**Android (Compose + Hilt):**
```kotlin
@Composable
fun TaskListScreen(viewModel: TaskListViewModel = hiltViewModel()) {
    val tasks by viewModel.tasks.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()

    LazyColumn {
        items(tasks, key = { it.id }) { task ->
            TaskItem(
                task = task,
                onToggle = { viewModel.toggleTask(task.id) }
            )
        }
    }
}

// ✅ Hilt integration for Android-specific wiring of shared components
@Module
@InstallIn(SingletonComponent::class)
object SharedModule {
    @Provides
    @Singleton
    fun provideTaskRepository(
        apiService: TaskApiService,
        database: TaskDatabase
    ): TaskRepository = TaskRepositoryImpl(apiService, database)
}
```

**iOS (SwiftUI, упрощенный пример):**
```swift
// ✅ Wrapper for observing a Kotlin StateFlow/Flow (псевдокод)
class TaskListViewModelWrapper: ObservableObject {
    private let viewModel: TaskListViewModel
    @Published var tasks: [Task] = []
    @Published var isLoading: Bool = false

    init(viewModel: TaskListViewModel) {
        self.viewModel = viewModel
        observeTasks()
    }

    private func observeTasks() {
        // Здесь должен использоваться реальный bridge Flow -> Swift,
        // например, через KMP-NativeCoroutines или другой helper из проекта.
        viewModel.tasks.collectIn { [weak self] tasks in
            self?.tasks = tasks
        }
    }
}

struct TaskListView: View {
    @StateObject private var viewModel = TaskListViewModelWrapper(
        viewModel: SharedDi.shared.taskListViewModel()
    )

    var body: some View {
        List(viewModel.tasks, id: \.id) { task in
            TaskRow(task: task)
        }
    }
}
```

(Важно использовать реальный helper/bridge для `Flow` → Swift (например, `KMP-NativeCoroutines`), а приведённый `collectIn` рассматривать как иллюстрацию паттерна.)

### Dependency Injection (Koin На Shared уровне)

```kotlin
// ✅ commonMain - shared DI module (пример с Koin)
val commonModule = module {
    single { NetworkClient() }
    single<TaskRepository> { TaskRepositoryImpl(get(), get()) }
    factory { GetTasksUseCase(get()) }
    factory { CreateTaskUseCase(get()) }
    single { Logger() }
}

// androidMain
val androidModule = module {
    single { DatabaseDriverFactory(androidContext()) }
}

// iosMain
val iosModule = module {
    single { DatabaseDriverFactory() }
}

object SharedDi {
    // Инициализация Koin выполняется в platform-коде (Android/iOS)
    // с использованием multiplatform-совместимых артефактов Koin.
    // Здесь только пример доступа к зависимостям:
    fun taskListViewModel(): TaskListViewModel = getKoin().get()
}
```

Здесь Koin используется в shared коде через multiplatform-совместимые артефакты и инициализируется в платформенных entry points, а Hilt — только в Android-слое для интеграции Android-компонентов (`ViewModel`, `Activity` и т.п.). Не стоит использовать JVM-only API (например, `KoinJavaComponent`) в iOS-коде.

### Best Practices (RU)

**Code Organization:**
- Бизнес-логика в `commonMain`.
- UI слой — platform-specific.
- Минимизировать количество `expect/actual` и выносить их в тонкие адаптеры.
- Придерживаться Clean Architecture (Domain → Data → Presentation).

**Swift-Friendly APIs:**
- Избегать сложных обобщений (особенно вложенных `Result<List<T>>`) в публичном API фреймворка.
- Использовать `@Throws` для функций, которые должны мапиться на `throws` в Swift (для предсказуемого error handling).
- Экспортировать только необходимые типы во фреймворк.
- Предоставлять обертки над `Flow`/`StateFlow` для простого использования в SwiftUI/Combine.

**Performance:**
- Минимизировать количество cross-boundary вызовов между Kotlin и Swift/Objective-C.
- Кэшировать platform-specific экземпляры, когда это оправдано.
- Профилировать использование памяти и потоков на обеих платформах.
- Учитывать особенности конкуренции и memory model Kotlin/Native при работе с потоками.

### Common Pitfalls (RU)

- Over-sharing: попытка шарить UI приводит к ухудшению UX и усложняет интеграцию native-паттернов.
- Complex Generics: сложные дженерики (`Flow<Result<List<T>>>`) плохо мапятся в Swift и усложняют API.
- Incorrect error mapping: отсутствие `@Throws` или понятной схемы ошибок делает обработку в Swift неудобной; непойманные исключения приводят к крэшу, как и на Android.
- Memory Leaks: неверное управление жизненным циклом shared `ViewModel`/Flows и сильные reference cycles между Kotlin и Swift.
- Build Configuration: ошибки в настройке targets, Podfile или экспорте зависимостей во фреймворк.

---

## Answer (EN)

KMM lets you share business logic, networking, and data layers between Android and iOS while keeping UI platform-specific, typically achieving around 60-80% code reuse (project-dependent).

## Short Version (EN)
- Put shared business logic, networking, caching, and domain models in `commonMain`.
- Keep UI, DI frameworks, and platform integrations native (`androidMain`, `iosMain`).
- Use `expect/actual` for thin adapters to platform APIs.
- Organize around Clean Architecture (Domain/Data/Presentation) and avoid over-sharing UI.

## Detailed Version (EN)
### Requirements

- Functional:
  - Shared business, networking, and data layers for Android and iOS.
  - Ability to plug in platform-specific implementations (logging, storage, UI, system APIs).
  - Stable, well-defined APIs of the shared module for both platforms.
- Non-functional:
  - High code reuse without compromising UX.
  - Smooth integration with Android Studio/Xcode and CI.
  - Swift-friendly, predictable public API.
  - Architecture that scales with more features and teams.

### Architecture

High-level design:
- `shared` module (KMM): domain, data, use cases, cross-platform services.
- `androidApp`: Android UI (Compose/Views), DI (Hilt etc.), navigation, integration with `shared`.
- `iosApp`: iOS UI (SwiftUI/UIKit), dependency composition on the iOS side, integration with the exported `shared` framework.
- Thin `expect/actual` adapters for platform APIs.

### Project Structure

**Modules:**
```
shared/          # Shared Kotlin code
  commonMain/    # Platform-agnostic code
  androidMain/   # Android-specific
  iosMain/       # iOS-specific (via iosX64Main, iosArm64Main, iosSimulatorArm64Main)
androidApp/      # Android application
iosApp/          # iOS Xcode project
```

**Build Configuration (simplified, classic style):**
```kotlin
// shared/build.gradle.kts
kotlin {
    android()

    // iOS targets
    listOf(iosX64(), iosArm64(), iosSimulatorArm64()).forEach {
        it.binaries.framework {
            baseName = "shared"
            isStatic = true
        }
    }

    sourceSets {
        val commonMain by getting {
            dependencies {
                implementation("io.ktor:ktor-client-core")
                implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core")
            }
        }
        val androidMain by getting {
            dependencies {
                implementation("io.ktor:ktor-client-android")
            }
        }
        // Shared iOS source set used by concrete iOS targets
        val iosX64Main by getting
        val iosArm64Main by getting
        val iosSimulatorArm64Main by getting

        val iosMain by creating {
            dependsOn(commonMain)
            dependencies {
                implementation("io.ktor:ktor-client-darwin")
            }
        }

        iosX64Main.dependsOn(iosMain)
        iosArm64Main.dependsOn(iosMain)
        iosSimulatorArm64Main.dependsOn(iosMain)
    }
}
```

(In real projects, prefer the up-to-date Multiplatform plugin style and hierarchical source sets; the key point is wiring `iosMain` correctly to the iOS targets.)

### Expect/Actual Mechanism

**Purpose:** Abstract platform-specific functionality.

```kotlin
// ✅ commonMain - expect declaration
expect class Platform() {
    val name: String
    val version: String
}

expect fun generateUUID(): String

// ✅ androidMain - actual implementation
actual class Platform {
    actual val name: String = "Android"
    actual val version: String = android.os.Build.VERSION.RELEASE ?: "Unknown"
}

actual fun generateUUID(): String = java.util.UUID.randomUUID().toString()

// ✅ iosMain - actual implementation
actual class Platform {
    actual val name: String = platform.UIKit.UIDevice.currentDevice.systemName
    actual val version: String = platform.UIKit.UIDevice.currentDevice.systemVersion
}

actual fun generateUUID(): String = platform.Foundation.NSUUID().UUIDString()
```

**Use Cases:**
- Database drivers (e.g., SQLDelight)
- Logging (Logcat vs NSLog)
- File system access
- Access to system APIs unavailable in `commonMain`

### Shared Business Logic

**Repository Pattern:**
```kotlin
// ✅ commonMain - Repository interface
interface TaskRepository {
    suspend fun getTasks(): Result<List<Task>>
    suspend fun createTask(task: Task): Result<Task>
    fun observeTasks(): Flow<List<Task>>
}

// ✅ commonMain - Implementation with offline-first strategy
class TaskRepositoryImpl(
    private val apiService: TaskApiService,
    private val database: TaskDatabase
) : TaskRepository {

    private val tasksFlow = MutableStateFlow<List<Task>>(emptyList())

    override suspend fun getTasks(): Result<List<Task>> {
        return try {
            // Fetch remote
            val remoteTasks = apiService.getTasks().map { it.toDomain() }

            // Update local cache
            remoteTasks.forEach { database.insertTask(it) }
            tasksFlow.value = remoteTasks

            Result.success(remoteTasks)
        } catch (e: Exception) {
            // ✅ Fallback to local cache on network failure
            val localTasks = database.getAllTasks()
            if (localTasks.isNotEmpty()) {
                tasksFlow.value = localTasks
                Result.success(localTasks)
            } else {
                Result.failure(e)
            }
        }
    }

    override suspend fun createTask(task: Task): Result<Task> {
        return try {
            val created = apiService.createTask(task).toDomain()
            database.insertTask(created)
            // update flow (simplified)
            tasksFlow.value = tasksFlow.value + created
            Result.success(created)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override fun observeTasks(): Flow<List<Task>> = tasksFlow.asStateFlow()
}
```

**Use Cases:**
```kotlin
import kotlin.system.getTimeMillis

// ✅ Encapsulate business logic
class CreateTaskUseCase(private val repository: TaskRepository) {
    suspend operator fun invoke(title: String, description: String): Result<Task> {
        if (title.isBlank()) {
            return Result.failure(IllegalArgumentException("Title required"))
        }

        val task = Task(
            id = generateUUID(),
            title = title.trim(),
            description = description.trim(),
            completed = false,
            createdAt = getTimeMillis()
        )

        return repository.createTask(task)
    }
}
```

### Platform Integration

**Android (Compose + Hilt):**
```kotlin
@Composable
fun TaskListScreen(viewModel: TaskListViewModel = hiltViewModel()) {
    val tasks by viewModel.tasks.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()

    LazyColumn {
        items(tasks, key = { it.id }) { task ->
            TaskItem(
                task = task,
                onToggle = { viewModel.toggleTask(task.id) }
            )
        }
    }
}

// ✅ Hilt integration for Android-specific wiring of shared components
@Module
@InstallIn(SingletonComponent::class)
object SharedModule {
    @Provides
    @Singleton
    fun provideTaskRepository(
        apiService: TaskApiService,
        database: TaskDatabase
    ): TaskRepository = TaskRepositoryImpl(apiService, database)
}
```

**iOS (SwiftUI, simplified):**
```swift
// ✅ Wrapper for observing a Kotlin StateFlow/Flow (pseudo-code)
class TaskListViewModelWrapper: ObservableObject {
    private let viewModel: TaskListViewModel
    @Published var tasks: [Task] = []
    @Published var isLoading: Bool = false

    init(viewModel: TaskListViewModel) {
        self.viewModel = viewModel
        observeTasks()
    }

    private func observeTasks() {
        // Use a real Flow -> Swift bridge here, for example via KMP-NativeCoroutines
        // or another helper defined in your project.
        viewModel.tasks.collectIn { [weak self] tasks in
            self?.tasks = tasks
        }
    }
}

struct TaskListView: View {
    @StateObject private var viewModel = TaskListViewModelWrapper(
        viewModel: SharedDi.shared.taskListViewModel()
    )

    var body: some View {
        List(viewModel.tasks, id: \.id) { task in
            TaskRow(task: task)
        }
    }
}
```

(Use an actual `Flow` → Swift bridge instead of the non-standard `collectIn`; the snippet shows the pattern, not a concrete library API.)

### Dependency Injection (Koin in Shared, Hilt on Android)

```kotlin
// ✅ commonMain - shared DI module (Koin example)
val commonModule = module {
    single { NetworkClient() }
    single<TaskRepository> { TaskRepositoryImpl(get(), get()) }
    factory { GetTasksUseCase(get()) }
    factory { CreateTaskUseCase(get()) }
    single { Logger() }
}

// androidMain
val androidModule = module {
    single { DatabaseDriverFactory(androidContext()) }
}

// iosMain
val iosModule = module {
    single { DatabaseDriverFactory() }
}

object SharedDi {
    // Koin is initialized from platform code (Android/iOS)
    // using its multiplatform-compatible artifacts.
    // This is an example of exposing dependencies:
    fun taskListViewModel(): TaskListViewModel = getKoin().get()
}
```

Koin (or a similar library) is used in shared code via multiplatform-compatible artifacts and initialized from platform entry points, while Hilt remains an Android-only DI framework. JVM-only APIs (e.g., `KoinJavaComponent`) must not be used in iOS code.

### Best Practices (EN)

**Code Organization:**
- Put business logic in `commonMain`.
- Keep UI layers platform-specific.
- Minimize `expect/actual` usage and isolate platform details behind small adapters.
- Follow Clean Architecture (Domain → Data → Presentation).

**Swift-Friendly APIs:**
- Avoid overly complex generics (especially nested `Result<List<T>>`) in the exported framework API.
- Use `@Throws` for functions that should map to `throws` in Swift for predictable error handling.
- Export only the necessary types to the iOS framework.
- Provide adapters/wrappers over `Flow`/`StateFlow` to integrate cleanly with SwiftUI/Combine.

**Performance:**
- Minimize cross-boundary calls between Kotlin and Swift/Objective-C.
- Cache platform-specific instances when it makes sense.
- Profile memory and threading behavior on both platforms.
- Be mindful of Kotlin/Native concurrency and memory model.

### Common Pitfalls (EN)

- Over-sharing: trying to share UI code hurts UX and complicates native integration.
- Complex Generics: complicated generics (`Flow<Result<List<T>>>`) do not map nicely to Swift and make APIs harder to use.
- Incorrect error mapping: missing `@Throws`/clear error contracts leads to awkward Swift error handling; uncaught exceptions crash just like on Android.
- Memory Leaks: incorrect lifecycle handling of shared ViewModels/Flows and strong reference cycles across the Kotlin ↔ Swift boundary.
- Build Configuration: misconfigured targets, Podfile, or framework exports causing integration issues.

---

## Follow-ups (RU)

- Как вы обрабатываете отмену корутин в shared ViewModel, к которой обращается iOS?
- Какие стратегии вы используете для отладки shared-кода на iOS-устройствах?
- Как вы эффективно тестируете платформенно-специфичные реализации (`expect/actual`)?
- Каковы последствия для памяти при удержании ссылок на Kotlin-объекты из Swift?
- Как вы версионируете и поставляете shared-фреймворк для использования на iOS?

## Follow-ups (EN)

- How do you handle coroutine cancellation in shared ViewModels accessed from iOS?
- What strategies exist for debugging shared code on iOS devices?
- How do you test platform-specific implementations (expect/actual) effectively?
- What are the memory implications of keeping references to Kotlin objects from Swift?
- How do you version and publish the shared framework for iOS consumption?

## References (RU)

- [[c-android]]

## References (EN)

- [[c-android]]

## Related Questions

### Prerequisites (Medium)
- [[q-clean-architecture-android--android--hard]] - Clean Architecture on Android

### Related (Hard)
- [[q-mvi-architecture--android--hard]] - MVI architecture pattern
