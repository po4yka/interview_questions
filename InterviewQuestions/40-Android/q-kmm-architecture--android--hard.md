---
id: android-435
title: "KMM Architecture / Архитектура KMM"
aliases: ["KMM Architecture", "Архитектура KMM", "Kotlin Multiplatform Mobile"]
topic: android
subtopics: [kmp, architecture-clean, di-hilt]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-clean-architecture-android--android--hard, q-mvi-architecture--android--hard, q-offline-first-architecture--android--hard]
created: 2025-10-15
updated: 2025-10-31
sources: []
tags: [android, android/kmp, android/architecture-clean, android/di-hilt, kmm, kotlin, multiplatform, difficulty/hard]
date created: Tuesday, October 28th 2025, 9:23:29 pm
date modified: Thursday, October 30th 2025, 3:11:36 pm
---

# Вопрос (RU)

> Объясните архитектуру Kotlin Multiplatform Mobile (KMM) и структуру проекта. Как организовать shared код между Android и iOS? Что такое expect/actual механизмы? Как обрабатывать platform-specific реализации максимизируя переиспользование кода?

# Question (EN)

> Explain Kotlin Multiplatform Mobile (KMM) architecture and project structure. How do you organize shared code between Android and iOS? What are expect/actual mechanisms? How do you handle platform-specific implementations while maximizing code reuse?

---

## Ответ (RU)

KMM позволяет делиться бизнес-логикой, сетью и data слоями между Android и iOS, сохраняя UI platform-specific, достигая 60-80% переиспользования кода.

### Структура Проекта

**Модули:**
```
shared/          # Общий Kotlin код
  commonMain/    # Код для всех платформ
  androidMain/   # Android-specific
  iosMain/       # iOS-specific
androidApp/      # Android приложение
iosApp/          # iOS Xcode проект
```

**Build Configuration:**
```kotlin
// shared/build.gradle.kts
kotlin {
    android()

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
        val iosMain by creating {
            dependencies {
                implementation("io.ktor:ktor-client-darwin")
            }
        }
    }
}
```

### Expect/Actual Механизм

**Назначение:** Абстракция platform-specific функционала

```kotlin
// ✅ commonMain - expect declaration
expect class Platform() {
    val name: String
    val version: String
}

expect fun generateUUID(): String

// ✅ androidMain - actual implementation
actual class Platform {
    actual val name = "Android"
    actual val version = Build.VERSION.RELEASE
}

actual fun generateUUID() = UUID.randomUUID().toString()

// ✅ iosMain - actual implementation
actual class Platform {
    actual val name = UIDevice.currentDevice.systemName
    actual val version = UIDevice.currentDevice.systemVersion
}

actual fun generateUUID() = NSUUID().UUIDString
```

**Применение:**
- Database drivers (SQLDelight)
- Logger (Logcat vs NSLog)
- File system access
- Platform-specific UI previews

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
                Result.success(localTasks)
            } else {
                Result.failure(e)
            }
        }
    }

    override fun observeTasks() = tasksFlow.asStateFlow()
}
```

**Use Cases:**
```kotlin
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
            createdAt = currentTimeMillis()
        )

        return repository.createTask(task)
    }
}
```

### Platform Integration

**Android (Compose):**
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

// ✅ Hilt integration
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

**iOS (SwiftUI):**
```swift
// ✅ Wrapper for StateFlow observation
class TaskListViewModelWrapper: ObservableObject {
    private let viewModel: TaskListViewModel
    @Published var tasks: [Task] = []
    @Published var isLoading = false

    init() {
        viewModel = KoinKt.getTaskListViewModel()
        observeTasks()
    }

    private func observeTasks() {
        // ✅ Bridge Kotlin Flow to Combine
        viewModel.tasks.watch { [weak self] tasks in
            self?.tasks = tasks?.compactMap { $0 as? Task } ?? []
        }
    }
}

struct TaskListView: View {
    @StateObject private var viewModel = TaskListViewModelWrapper()

    var body: some View {
        List(viewModel.tasks, id: \.id) { task in
            TaskRow(task: task)
        }
    }
}
```

### Dependency Injection (Koin)

```kotlin
// ✅ commonMain - shared DI
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

// ✅ iOS helper
object KoinKt {
    fun getTaskListViewModel(): TaskListViewModel {
        return KoinJavaComponent.get(TaskListViewModel::class.java)
    }
}
```

### Best Practices

**Code Organization:**
- Business logic in commonMain
- UI layer platform-specific
- Minimize expect/actual usage
- Clean Architecture (Domain → Data → Presentation)

**Swift-Friendly APIs:**
- Avoid complex generics
- Use `@Throws` annotation for iOS
- Export dependencies to framework
- Provide Flow wrappers for SwiftUI

**Performance:**
- Minimize JNI/ObjC bridge calls
- Cache platform-specific instances
- Profile memory usage on both platforms
- Use inline functions appropriately

### Common Pitfalls

❌ **Over-sharing:** Trying to share UI code leads to poor UX
❌ **Complex Generics:** iOS struggles with Kotlin generics like `Flow<Result<List<T>>>`
❌ **Missing @Throws:** iOS can't handle uncaught Kotlin exceptions
❌ **Memory Leaks:** Improper lifecycle management in shared ViewModels
❌ **Build Configuration:** Forgetting to update Podfile or export dependencies

## Answer (EN)

KMM enables sharing business logic, networking, and data layers between Android and iOS while keeping UI platform-specific, achieving 60-80% code reuse.

### Project Structure

**Modules:**
```
shared/          # Shared Kotlin code
  commonMain/    # Platform-agnostic code
  androidMain/   # Android-specific
  iosMain/       # iOS-specific
androidApp/      # Android application
iosApp/          # iOS Xcode project
```

**Build Configuration:**
```kotlin
// shared/build.gradle.kts
kotlin {
    android()

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
        val iosMain by creating {
            dependencies {
                implementation("io.ktor:ktor-client-darwin")
            }
        }
    }
}
```

### Expect/Actual Mechanism

**Purpose:** Platform-specific abstraction

```kotlin
// ✅ commonMain - expect declaration
expect class Platform() {
    val name: String
    val version: String
}

expect fun generateUUID(): String

// ✅ androidMain - actual implementation
actual class Platform {
    actual val name = "Android"
    actual val version = Build.VERSION.RELEASE
}

actual fun generateUUID() = UUID.randomUUID().toString()

// ✅ iosMain - actual implementation
actual class Platform {
    actual val name = UIDevice.currentDevice.systemName
    actual val version = UIDevice.currentDevice.systemVersion
}

actual fun generateUUID() = NSUUID().UUIDString
```

**Use Cases:**
- Database drivers (SQLDelight)
- Logger (Logcat vs NSLog)
- File system access
- Platform-specific UI previews

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
                Result.success(localTasks)
            } else {
                Result.failure(e)
            }
        }
    }

    override fun observeTasks() = tasksFlow.asStateFlow()
}
```

**Use Cases:**
```kotlin
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
            createdAt = currentTimeMillis()
        )

        return repository.createTask(task)
    }
}
```

### Platform Integration

**Android (Compose):**
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

// ✅ Hilt integration
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

**iOS (SwiftUI):**
```swift
// ✅ Wrapper for StateFlow observation
class TaskListViewModelWrapper: ObservableObject {
    private let viewModel: TaskListViewModel
    @Published var tasks: [Task] = []
    @Published var isLoading = false

    init() {
        viewModel = KoinKt.getTaskListViewModel()
        observeTasks()
    }

    private func observeTasks() {
        // ✅ Bridge Kotlin Flow to Combine
        viewModel.tasks.watch { [weak self] tasks in
            self?.tasks = tasks?.compactMap { $0 as? Task } ?? []
        }
    }
}

struct TaskListView: View {
    @StateObject private var viewModel = TaskListViewModelWrapper()

    var body: some View {
        List(viewModel.tasks, id: \.id) { task in
            TaskRow(task: task)
        }
    }
}
```

### Dependency Injection (Koin)

```kotlin
// ✅ commonMain - shared DI
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

// ✅ iOS helper
object KoinKt {
    fun getTaskListViewModel(): TaskListViewModel {
        return KoinJavaComponent.get(TaskListViewModel::class.java)
    }
}
```

### Best Practices

**Code Organization:**
- Business logic in commonMain
- UI layer platform-specific
- Minimize expect/actual usage
- Clean Architecture (Domain → Data → Presentation)

**Swift-Friendly APIs:**
- Avoid complex generics
- Use `@Throws` annotation for iOS
- Export dependencies to framework
- Provide Flow wrappers for SwiftUI

**Performance:**
- Minimize JNI/ObjC bridge calls
- Cache platform-specific instances
- Profile memory usage on both platforms
- Use inline functions appropriately

### Common Pitfalls

❌ **Over-sharing:** Trying to share UI code leads to poor UX
❌ **Complex Generics:** iOS struggles with Kotlin generics like `Flow<Result<List<T>>>`
❌ **Missing @Throws:** iOS can't handle uncaught Kotlin exceptions
❌ **Memory Leaks:** Improper lifecycle management in shared ViewModels
❌ **Build Configuration:** Forgetting to update Podfile or export dependencies

---

## Follow-ups

- How do you handle coroutine cancellation in shared ViewModels accessed from iOS?
- What strategies exist for debugging shared code on iOS devices?
- How do you test platform-specific implementations (expect/actual) effectively?
- What are the memory implications of keeping references to Kotlin objects from Swift?
- How do you version and publish the shared framework for iOS consumption?

## References

- [[c-clean-architecture]] - Clean Architecture principles
- [[c-repository-pattern]] - Repository pattern implementation
- [[c-dependency-injection]] - Dependency injection patterns

## Related Questions

### Prerequisites (Medium)
- [[q-clean-architecture-android--android--hard]] - Clean Architecture on Android
- [[q-repository-pattern--android--medium]] - Repository pattern basics

### Related (Hard)
- [[q-mvi-architecture--android--hard]] - MVI architecture pattern
- [[q-offline-first-architecture--android--hard]] - Offline-first architecture strategies

### Advanced (Hard)
- [[q-modularization-strategies--android--hard]] - Multi-module architecture patterns
- [[q-gradle-dependency-management--android--hard]] - Complex build configuration
