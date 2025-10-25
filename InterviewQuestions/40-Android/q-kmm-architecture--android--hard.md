---
id: 20251012-12271118
title: "Kmm Architecture / Архитектура KMM"
topic: android
difficulty: hard
status: draft
moc: moc-android
related: [q-which-class-to-use-for-rendering-view-in-background-thread--android--hard, q-app-size-optimization--performance--medium, q-how-mutablestate-notifies--android--medium]
created: 2025-10-15
tags: [Kotlin, KMM, Multiplatform, Architecture, difficulty/hard]
---
# Kotlin Multiplatform Mobile (KMM) Architecture

# Question (EN)
> 
Explain Kotlin Multiplatform Mobile (KMM) architecture and project structure. How do you organize shared code between Android and iOS? What are expect/actual mechanisms? How do you handle platform-specific implementations while maximizing code reuse?

## Answer (EN)
Kotlin Multiplatform Mobile (KMM) enables sharing business logic, networking, and data layers between Android and iOS while keeping UI platform-specific, achieving significant code reuse without compromising native experience.

#### KMM Project Structure

**1. Multi-Module Setup**
```kotlin
// settings.gradle.kts (root)
rootProject.name = "TaskFlowKMM"

include(":androidApp")
include(":shared")
include(":iosApp") // Xcode project reference

// shared/build.gradle.kts
plugins {
    kotlin("multiplatform")
    kotlin("native.cocoapods")
    id("com.android.library")
    kotlin("plugin.serialization")
}

kotlin {
    android {
        compilations.all {
            kotlinOptions {
                jvmTarget = "17"
            }
        }
    }

    listOf(
        iosX64(),
        iosArm64(),
        iosSimulatorArm64()
    ).forEach { iosTarget ->
        iosTarget.binaries.framework {
            baseName = "shared"
            isStatic = true

            // Export dependencies to iOS
            export("io.ktor:ktor-client-core:2.3.7")
            export("org.jetbrains.kotlinx:kotlinx-datetime:0.5.0")
        }
    }

    cocoapods {
        summary = "Shared business logic for TaskFlow"
        homepage = "https://taskflow.app"
        version = "1.0"
        ios.deploymentTarget = "14.0"
        framework {
            baseName = "shared"
            isStatic = true
        }
    }

    sourceSets {
        val commonMain by getting {
            dependencies {
                // Networking
                implementation("io.ktor:ktor-client-core:2.3.7")
                implementation("io.ktor:ktor-client-content-negotiation:2.3.7")
                implementation("io.ktor:ktor-serialization-kotlinx-json:2.3.7")

                // Serialization
                implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.2")

                // DateTime
                implementation("org.jetbrains.kotlinx:kotlinx-datetime:0.5.0")

                // Coroutines
                implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")

                // Logging
                implementation("co.touchlab:kermit:2.0.2")

                // Dependency Injection
                implementation("io.insert-koin:koin-core:3.5.3")
            }
        }

        val commonTest by getting {
            dependencies {
                implementation(kotlin("test"))
                implementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")
            }
        }

        val androidMain by getting {
            dependencies {
                implementation("io.ktor:ktor-client-android:2.3.7")
                implementation("androidx.startup:startup-runtime:1.1.1")
                implementation("androidx.lifecycle:lifecycle-viewmodel-ktx:2.7.0")
            }
        }

        val iosX64Main by getting
        val iosArm64Main by getting
        val iosSimulatorArm64Main by getting

        val iosMain by creating {
            dependsOn(commonMain)
            iosX64Main.dependsOn(this)
            iosArm64Main.dependsOn(this)
            iosSimulatorArm64Main.dependsOn(this)

            dependencies {
                implementation("io.ktor:ktor-client-darwin:2.3.7")
            }
        }
    }
}

android {
    namespace = "com.taskflow.shared"
    compileSdk = 34

    defaultConfig {
        minSdk = 24
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
```

**2. Directory Structure**
```
project/
 androidApp/              # Android-specific app
    src/main/
       kotlin/
          com/taskflow/android/
              MainActivity.kt
              ui/
              di/
       res/
    build.gradle.kts
 iosApp/                  # iOS Xcode project
    iosApp/
       ContentView.swift
       TaskListView.swift
       ViewModel/
    iosApp.xcodeproj
 shared/                  # Shared Kotlin code
     src/
        commonMain/kotlin/
           com/taskflow/shared/
               domain/
                  model/
                  repository/
                  usecase/
               data/
                  remote/
                  local/
                  repository/
               Platform.kt
               di/
        commonTest/kotlin/
        androidMain/kotlin/
           com/taskflow/shared/
               PlatformAndroid.kt
               database/
        iosMain/kotlin/
            com/taskflow/shared/
                PlatformIOS.kt
                database/
     build.gradle.kts
```

#### Expect/Actual Mechanism

**1. Platform Abstraction**
```kotlin
// commonMain/Platform.kt - expect declaration
expect class Platform() {
    val name: String
    val version: String
    val deviceModel: String
}

expect fun generateUUID(): String

expect fun currentTimeMillis(): Long

expect class Logger() {
    fun debug(tag: String, message: String)
    fun error(tag: String, message: String, throwable: Throwable?)
}

// androidMain/PlatformAndroid.kt - actual implementation
actual class Platform {
    actual val name: String = "Android"
    actual val version: String = Build.VERSION.RELEASE
    actual val deviceModel: String = "${Build.MANUFACTURER} ${Build.MODEL}"
}

actual fun generateUUID(): String = UUID.randomUUID().toString()

actual fun currentTimeMillis(): Long = System.currentTimeMillis()

actual class Logger {
    actual fun debug(tag: String, message: String) {
        Log.d(tag, message)
    }

    actual fun error(tag: String, message: String, throwable: Throwable?) {
        Log.e(tag, message, throwable)
    }
}

// iosMain/PlatformIOS.kt - actual implementation
import platform.UIKit.UIDevice
import platform.Foundation.NSUUID

actual class Platform {
    actual val name: String = UIDevice.currentDevice.systemName
    actual val version: String = UIDevice.currentDevice.systemVersion
    actual val deviceModel: String = UIDevice.currentDevice.model
}

actual fun generateUUID(): String = NSUUID().UUIDString

actual fun currentTimeMillis(): Long =
    platform.Foundation.NSDate().timeIntervalSince1970.toLong() * 1000

actual class Logger {
    actual fun debug(tag: String, message: String) {
        NSLog("[$tag] $message")
    }

    actual fun error(tag: String, message: String, throwable: Throwable?) {
        NSLog("[$tag] ERROR: $message ${throwable?.message ?: ""}")
    }
}
```

**2. Database Abstraction**
```kotlin
// commonMain - Database interface
interface TaskDatabase {
    suspend fun getAllTasks(): List<Task>
    suspend fun getTaskById(id: String): Task?
    suspend fun insertTask(task: Task)
    suspend fun updateTask(task: Task)
    suspend fun deleteTask(id: String)
    suspend fun searchTasks(query: String): List<Task>
}

// commonMain - expect declaration
expect class DatabaseDriverFactory {
    fun createDriver(): SqlDriver
}

// androidMain - Android implementation with SQLDelight
actual class DatabaseDriverFactory(private val context: Context) {
    actual fun createDriver(): SqlDriver {
        return AndroidSqliteDriver(
            schema = TaskFlowDatabase.Schema,
            context = context,
            name = "taskflow.db"
        )
    }
}

// iosMain - iOS implementation with SQLDelight
actual class DatabaseDriverFactory {
    actual fun createDriver(): SqlDriver {
        return NativeSqliteDriver(
            schema = TaskFlowDatabase.Schema,
            name = "taskflow.db"
        )
    }
}

// commonMain - Database implementation
class TaskDatabaseImpl(driverFactory: DatabaseDriverFactory) : TaskDatabase {
    private val database = TaskFlowDatabase(driverFactory.createDriver())
    private val queries = database.taskQueries

    override suspend fun getAllTasks(): List<Task> = withContext(Dispatchers.Default) {
        queries.selectAll().executeAsList().map { it.toDomain() }
    }

    override suspend fun getTaskById(id: String): Task? = withContext(Dispatchers.Default) {
        queries.selectById(id).executeAsOneOrNull()?.toDomain()
    }

    override suspend fun insertTask(task: Task) = withContext(Dispatchers.Default) {
        queries.insert(
            id = task.id,
            title = task.title,
            description = task.description,
            completed = task.completed.toLong(),
            createdAt = task.createdAt,
            updatedAt = task.updatedAt
        )
    }

    override suspend fun updateTask(task: Task) = withContext(Dispatchers.Default) {
        queries.update(
            title = task.title,
            description = task.description,
            completed = task.completed.toLong(),
            updatedAt = task.updatedAt,
            id = task.id
        )
    }

    override suspend fun deleteTask(id: String) = withContext(Dispatchers.Default) {
        queries.deleteById(id)
    }

    override suspend fun searchTasks(query: String): List<Task> = withContext(Dispatchers.Default) {
        queries.search("%$query%").executeAsList().map { it.toDomain() }
    }
}
```

**3. Network Client Abstraction**
```kotlin
// commonMain - HTTP Client configuration
class NetworkClient {
    val httpClient = HttpClient {
        install(ContentNegotiation) {
            json(Json {
                prettyPrint = true
                isLenient = true
                ignoreUnknownKeys = true
            })
        }

        install(Logging) {
            logger = object : io.ktor.client.plugins.logging.Logger {
                override fun log(message: String) {
                    Logger().debug("HTTP", message)
                }
            }
            level = LogLevel.INFO
        }

        defaultRequest {
            url("https://api.taskflow.app/")
            contentType(ContentType.Application.Json)
        }

        // Platform-specific engine configured automatically
        // Android: uses OkHttp
        // iOS: uses NSURLSession
    }
}

// commonMain - API Service
class TaskApiService(private val client: NetworkClient) {
    suspend fun getTasks(): List<TaskDto> {
        return client.httpClient.get("tasks").body()
    }

    suspend fun createTask(task: CreateTaskRequest): TaskDto {
        return client.httpClient.post("tasks") {
            setBody(task)
        }.body()
    }

    suspend fun updateTask(id: String, task: UpdateTaskRequest): TaskDto {
        return client.httpClient.put("tasks/$id") {
            setBody(task)
        }.body()
    }

    suspend fun deleteTask(id: String) {
        client.httpClient.delete("tasks/$id")
    }
}
```

#### Shared Business Logic

**1. Repository Pattern**
```kotlin
// commonMain/domain/repository/TaskRepository.kt
interface TaskRepository {
    suspend fun getTasks(forceRefresh: Boolean = false): Result<List<Task>>
    suspend fun getTaskById(id: String): Result<Task>
    suspend fun createTask(task: Task): Result<Task>
    suspend fun updateTask(task: Task): Result<Task>
    suspend fun deleteTask(id: String): Result<Unit>
    fun observeTasks(): Flow<List<Task>>
}

// commonMain/data/repository/TaskRepositoryImpl.kt
class TaskRepositoryImpl(
    private val apiService: TaskApiService,
    private val database: TaskDatabase,
    private val logger: Logger
) : TaskRepository {

    private val tasksFlow = MutableStateFlow<List<Task>>(emptyList())

    init {
        // Initialize with local data
        CoroutineScope(Dispatchers.Default).launch {
            val localTasks = database.getAllTasks()
            tasksFlow.value = localTasks
        }
    }

    override suspend fun getTasks(forceRefresh: Boolean): Result<List<Task>> {
        return try {
            if (forceRefresh) {
                // Fetch from network
                val remoteTasks = apiService.getTasks().map { it.toDomain() }

                // Update local database
                remoteTasks.forEach { database.insertTask(it) }

                // Update flow
                tasksFlow.value = remoteTasks

                Result.success(remoteTasks)
            } else {
                // Return local data
                val localTasks = database.getAllTasks()
                tasksFlow.value = localTasks
                Result.success(localTasks)
            }
        } catch (e: Exception) {
            logger.error("TaskRepository", "Failed to get tasks", e)

            // Fallback to local data
            val localTasks = database.getAllTasks()
            if (localTasks.isNotEmpty()) {
                Result.success(localTasks)
            } else {
                Result.failure(e)
            }
        }
    }

    override suspend fun getTaskById(id: String): Result<Task> {
        return try {
            // Try local first
            val localTask = database.getTaskById(id)
            if (localTask != null) {
                return Result.success(localTask)
            }

            // Fetch from network if not found locally
            val remoteTask = apiService.getTask(id).toDomain()
            database.insertTask(remoteTask)

            Result.success(remoteTask)
        } catch (e: Exception) {
            logger.error("TaskRepository", "Failed to get task", e)
            Result.failure(e)
        }
    }

    override suspend fun createTask(task: Task): Result<Task> {
        return try {
            val createdTask = apiService.createTask(task.toCreateRequest()).toDomain()
            database.insertTask(createdTask)

            // Update flow
            val updatedList = tasksFlow.value + createdTask
            tasksFlow.value = updatedList

            Result.success(createdTask)
        } catch (e: Exception) {
            logger.error("TaskRepository", "Failed to create task", e)
            Result.failure(e)
        }
    }

    override suspend fun updateTask(task: Task): Result<Task> {
        return try {
            val updatedTask = apiService.updateTask(task.id, task.toUpdateRequest()).toDomain()
            database.updateTask(updatedTask)

            // Update flow
            val updatedList = tasksFlow.value.map {
                if (it.id == updatedTask.id) updatedTask else it
            }
            tasksFlow.value = updatedList

            Result.success(updatedTask)
        } catch (e: Exception) {
            logger.error("TaskRepository", "Failed to update task", e)
            Result.failure(e)
        }
    }

    override suspend fun deleteTask(id: String): Result<Unit> {
        return try {
            apiService.deleteTask(id)
            database.deleteTask(id)

            // Update flow
            val updatedList = tasksFlow.value.filter { it.id != id }
            tasksFlow.value = updatedList

            Result.success(Unit)
        } catch (e: Exception) {
            logger.error("TaskRepository", "Failed to delete task", e)
            Result.failure(e)
        }
    }

    override fun observeTasks(): Flow<List<Task>> = tasksFlow.asStateFlow()
}
```

**2. Use Cases**
```kotlin
// commonMain/domain/usecase/GetTasksUseCase.kt
class GetTasksUseCase(
    private val repository: TaskRepository
) {
    suspend operator fun invoke(forceRefresh: Boolean = false): Result<List<Task>> {
        return repository.getTasks(forceRefresh)
    }
}

// commonMain/domain/usecase/CreateTaskUseCase.kt
class CreateTaskUseCase(
    private val repository: TaskRepository
) {
    suspend operator fun invoke(title: String, description: String): Result<Task> {
        if (title.isBlank()) {
            return Result.failure(IllegalArgumentException("Title cannot be empty"))
        }

        val task = Task(
            id = generateUUID(),
            title = title.trim(),
            description = description.trim(),
            completed = false,
            createdAt = currentTimeMillis(),
            updatedAt = currentTimeMillis()
        )

        return repository.createTask(task)
    }
}

// commonMain/domain/usecase/ToggleTaskCompletionUseCase.kt
class ToggleTaskCompletionUseCase(
    private val repository: TaskRepository
) {
    suspend operator fun invoke(taskId: String): Result<Task> {
        val taskResult = repository.getTaskById(taskId)

        return taskResult.mapCatching { task ->
            val updatedTask = task.copy(
                completed = !task.completed,
                updatedAt = currentTimeMillis()
            )

            repository.updateTask(updatedTask).getOrThrow()
        }
    }
}
```

**3. Shared ViewModel (for iOS)**
```kotlin
// commonMain - Shared ViewModel for iOS
class TaskListViewModel(
    private val getTasksUseCase: GetTasksUseCase,
    private val createTaskUseCase: CreateTaskUseCase,
    private val toggleTaskUseCase: ToggleTaskCompletionUseCase,
    private val deleteTaskUseCase: DeleteTaskUseCase,
    private val repository: TaskRepository
) {
    private val viewModelScope = CoroutineScope(Dispatchers.Main + SupervisorJob())

    private val _tasks = MutableStateFlow<List<Task>>(emptyList())
    val tasks: StateFlow<List<Task>> = _tasks.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()

    init {
        loadTasks()
        observeTasks()
    }

    private fun observeTasks() {
        viewModelScope.launch {
            repository.observeTasks().collect { tasks ->
                _tasks.value = tasks
            }
        }
    }

    fun loadTasks(forceRefresh: Boolean = false) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null

            getTasksUseCase(forceRefresh)
                .onSuccess { tasks ->
                    _tasks.value = tasks
                }
                .onFailure { exception ->
                    _error.value = exception.message ?: "Unknown error"
                }

            _isLoading.value = false
        }
    }

    fun createTask(title: String, description: String) {
        viewModelScope.launch {
            createTaskUseCase(title, description)
                .onFailure { exception ->
                    _error.value = exception.message
                }
        }
    }

    fun toggleTaskCompletion(taskId: String) {
        viewModelScope.launch {
            toggleTaskUseCase(taskId)
                .onFailure { exception ->
                    _error.value = exception.message
                }
        }
    }

    fun deleteTask(taskId: String) {
        viewModelScope.launch {
            deleteTaskUseCase(taskId)
                .onFailure { exception ->
                    _error.value = exception.message
                }
        }
    }

    fun clearError() {
        _error.value = null
    }

    // iOS compatibility - convert StateFlow to observable
    fun observeTasksAsFlow(): Flow<List<Task>> = tasks

    // Clean up when done
    fun onCleared() {
        viewModelScope.cancel()
    }
}
```

#### Platform Integration

**1. Android Integration**
```kotlin
// androidApp - Compose UI
@Composable
fun TaskListScreen(
    viewModel: TaskListViewModel = hiltViewModel()
) {
    val tasks by viewModel.tasks.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val error by viewModel.error.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(title = { Text("Tasks") })
        },
        floatingActionButton = {
            FloatingActionButton(onClick = { /* Show create dialog */ }) {
                Icon(Icons.Default.Add, "Add task")
            }
        }
    ) { padding ->
        Box(modifier = Modifier.padding(padding)) {
            when {
                isLoading -> {
                    CircularProgressIndicator(
                        modifier = Modifier.align(Alignment.Center)
                    )
                }
                error != null -> {
                    ErrorView(
                        message = error!!,
                        onRetry = { viewModel.loadTasks(forceRefresh = true) }
                    )
                }
                tasks.isEmpty() -> {
                    EmptyView()
                }
                else -> {
                    LazyColumn {
                        items(tasks, key = { it.id }) { task ->
                            TaskItem(
                                task = task,
                                onToggle = { viewModel.toggleTaskCompletion(task.id) },
                                onDelete = { viewModel.deleteTask(task.id) }
                            )
                        }
                    }
                }
            }
        }
    }
}

// Android Hilt Module
@Module
@InstallIn(SingletonComponent::class)
object SharedModule {
    @Provides
    @Singleton
    fun provideDatabaseDriverFactory(
        @ApplicationContext context: Context
    ): DatabaseDriverFactory {
        return DatabaseDriverFactory(context)
    }

    @Provides
    @Singleton
    fun provideTaskDatabase(
        driverFactory: DatabaseDriverFactory
    ): TaskDatabase {
        return TaskDatabaseImpl(driverFactory)
    }

    @Provides
    @Singleton
    fun provideTaskRepository(
        apiService: TaskApiService,
        database: TaskDatabase,
        logger: Logger
    ): TaskRepository {
        return TaskRepositoryImpl(apiService, database, logger)
    }
}
```

**2. iOS Integration (SwiftUI)**
```swift
// iosApp - SwiftUI View
import SwiftUI
import shared

struct TaskListView: View {
    @StateObject private var viewModel: TaskListViewModelWrapper

    init() {
        _viewModel = StateObject(wrappedValue: TaskListViewModelWrapper())
    }

    var body: some View {
        NavigationView {
            ZStack {
                if viewModel.isLoading {
                    ProgressView()
                } else if let error = viewModel.error {
                    ErrorView(message: error) {
                        viewModel.loadTasks(forceRefresh: true)
                    }
                } else if viewModel.tasks.isEmpty {
                    EmptyView()
                } else {
                    List {
                        ForEach(viewModel.tasks, id: \.id) { task in
                            TaskRow(task: task) {
                                viewModel.toggleTaskCompletion(taskId: task.id)
                            } onDelete: {
                                viewModel.deleteTask(taskId: task.id)
                            }
                        }
                    }
                }
            }
            .navigationTitle("Tasks")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { /* Show create sheet */ }) {
                        Image(systemName: "plus")
                    }
                }
            }
        }
    }
}

// iosApp - ViewModel Wrapper for SwiftUI compatibility
class TaskListViewModelWrapper: ObservableObject {
    private let viewModel: TaskListViewModel

    @Published var tasks: [Task] = []
    @Published var isLoading: Bool = false
    @Published var error: String? = nil

    init() {
        // Get shared ViewModel from DI
        viewModel = KoinKt.getTaskListViewModel()

        // Observe StateFlows
        observeTasks()
        observeLoading()
        observeError()
    }

    private func observeTasks() {
        viewModel.tasks.watch { [weak self] tasks in
            self?.tasks = tasks?.compactMap { $0 as? Task } ?? []
        }
    }

    private func observeLoading() {
        viewModel.isLoading.watch { [weak self] loading in
            self?.isLoading = loading?.boolValue ?? false
        }
    }

    private func observeError() {
        viewModel.error.watch { [weak self] error in
            self?.error = error as? String
        }
    }

    func loadTasks(forceRefresh: Bool = false) {
        viewModel.loadTasks(forceRefresh: forceRefresh)
    }

    func toggleTaskCompletion(taskId: String) {
        viewModel.toggleTaskCompletion(taskId: taskId)
    }

    func deleteTask(taskId: String) {
        viewModel.deleteTask(taskId: taskId)
    }

    deinit {
        viewModel.onCleared()
    }
}

// Helper extension for StateFlow observation in Swift
extension Kotlinx_coroutines_coreStateFlow {
    func watch(block: @escaping (Any?) -> Void) {
        let cancellable = self.collect(collector: FlowCollector(block: block))
        // Store cancellable if needed
    }
}

class FlowCollector: Kotlinx_coroutines_coreFlowCollector {
    private let block: (Any?) -> Void

    init(block: @escaping (Any?) -> Void) {
        self.block = block
    }

    func emit(value: Any?) async throws {
        await MainActor.run {
            block(value)
        }
    }
}
```

#### Dependency Injection

**1. Koin Setup**
```kotlin
// commonMain/di/CommonModule.kt
val commonModule = module {
    // Network
    single { NetworkClient() }
    single { TaskApiService(get()) }

    // Database
    single<TaskDatabase> { TaskDatabaseImpl(get()) }

    // Repository
    single<TaskRepository> { TaskRepositoryImpl(get(), get(), get()) }

    // Use Cases
    factory { GetTasksUseCase(get()) }
    factory { CreateTaskUseCase(get()) }
    factory { ToggleTaskCompletionUseCase(get()) }
    factory { DeleteTaskUseCase(get()) }

    // ViewModel
    factory {
        TaskListViewModel(
            getTasksUseCase = get(),
            createTaskUseCase = get(),
            toggleTaskUseCase = get(),
            deleteTaskUseCase = get(),
            repository = get()
        )
    }

    // Platform
    single { Logger() }
}

// androidMain/di/AndroidModule.kt
val androidModule = module {
    single { DatabaseDriverFactory(androidContext()) }
}

// iosMain/di/IOSModule.kt
val iosModule = module {
    single { DatabaseDriverFactory() }
}

// Initialize Koin
fun initKoin(appDeclaration: KoinAppDeclaration = {}) = startKoin {
    appDeclaration()
    modules(commonModule)
}

// Android initialization
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        initKoin {
            androidContext(this@MyApplication)
            modules(androidModule)
        }
    }
}

// iOS initialization
fun initKoinIOS() = initKoin {
    modules(iosModule)
}

// Helper for iOS to get ViewModels
object KoinKt {
    fun getTaskListViewModel(): TaskListViewModel {
        return KoinJavaComponent.get(TaskListViewModel::class.java)
    }
}
```

#### Best Practices

1. **Code Organization**:
   - Keep business logic in commonMain
   - UI layer platform-specific
   - Use expect/actual only when necessary
   - Minimize platform-specific code

2. **Architecture**:
   - Clean Architecture (Domain, Data, Presentation)
   - Repository pattern for data access
   - Use cases for business logic
   - Dependency Injection (Koin)

3. **State Management**:
   - Use StateFlow for reactive state
   - Provide Flow wrappers for iOS
   - Keep ViewModels in shared code
   - Handle lifecycle properly

4. **Platform Integration**:
   - Provide Swift-friendly APIs
   - Use typealias for complex generics
   - Export necessary dependencies to iOS
   - Test on both platforms

5. **Performance**:
   - Minimize expect/actual overhead
   - Use inline functions when appropriate
   - Cache platform-specific instances
   - Profile memory usage on both platforms

#### Common Pitfalls

1. **Over-sharing**: Trying to share UI code leads to poor UX
2. **Complex Generics**: iOS struggles with Kotlin generics
3. **Missing @Throws**: iOS can't handle Kotlin exceptions properly
4. **Memory Leaks**: Improper lifecycle management in shared ViewModels
5. **Platform Assumptions**: Assuming Android APIs work on iOS
6. **Build Configuration**: Forgetting to update Podfile

### Summary

KMM enables significant code reuse while maintaining native UX:
- **Shared Layer**: Business logic, networking, data, repositories
- **Platform Layer**: UI, platform-specific APIs, lifecycle
- **Expect/Actual**: Platform abstractions for database, logging, UUID
- **Architecture**: Clean Architecture with Repository pattern
- **Integration**: Hilt/Dagger on Android, Koin everywhere, SwiftUI on iOS

Key considerations: appropriate boundaries, Swift-friendly APIs, proper lifecycle management, and platform-specific optimizations where needed.

---

# Вопрос (RU)
> 
Объясните архитектуру Kotlin Multiplatform Mobile (KMM) и структуру проекта. Как организовать shared код между Android и iOS? Что такое expect/actual механизмы? Как обрабатывать platform-specific реализации максимизируя переиспользование кода?

## Ответ (RU)
Kotlin Multiplatform Mobile (KMM) позволяет делиться бизнес-логикой, сетью и data слоями между Android и iOS, сохраняя UI platform-specific, достигая значительного переиспользования кода без ущерба нативному опыту.

#### Структура проекта

**Модули**:
- `shared/` - общий Kotlin код
- `androidApp/` - Android приложение
- `iosApp/` - iOS приложение (Xcode)

**Source Sets**:
- `commonMain` - код для всех платформ
- `androidMain` - Android-specific код
- `iosMain` - iOS-specific код
- `commonTest` - общие тесты

#### Expect/Actual

**Назначение**: Абстракция platform-specific функционала

**Примеры**:
- Database driver (SQLDelight)
- Logger (Logcat vs NSLog)
- UUID generation
- Current timestamp
- File system access

**Механизм**:
```kotlin
// commonMain - expect
expect fun generateUUID(): String

// androidMain - actual
actual fun generateUUID() = UUID.randomUUID().toString()

// iosMain - actual
actual fun generateUUID() = NSUUID().UUIDString
```

#### Shared код

**Что делить**:
-  Domain models
-  Repository interfaces & implementations
-  Use cases
-  Network layer (Ktor)
-  Database (SQLDelight)
-  Business logic
-  ViewModels (для iOS)

**Что НЕ делить**:
-  UI компоненты
-  Platform lifecycle
-  Navigation
-  Permissions handling

#### Интеграция

**Android**:
- Compose UI
- Hilt/Dagger для DI
- Lifecycle-aware ViewModels
- Coroutines Flow

**iOS**:
- SwiftUI
- Combine framework
- ObservableObject wrapper
- Async/await bridge

#### Dependency Injection

**Koin** - общий DI для обеих платформ:
- commonModule - shared dependencies
- androidModule - Android-specific
- iosModule - iOS-specific

#### Best Practices

1. **Границы**:
   - Четкое разделение shared/platform
   - Минимизировать expect/actual
   - UI всегда platform-specific

2. **API Design**:
   - Swift-friendly интерфейсы
   - Избегать сложных generics
   - @Throws для iOS
   - Простые типы в public API

3. **Архитектура**:
   - Clean Architecture
   - Repository pattern
   - Use cases для бизнес-логики
   - StateFlow для reactive state

4. **Производительность**:
   - Минимизировать JNI calls (iOS)
   - Кэшировать platform instances
   - Профилировать обе платформы
   - Оптимизировать memory usage

### Резюме

KMM позволяет значительное переиспользование кода:
- **Shared**: Бизнес-логика, сеть, данные, репозитории (60-80% кода)
- **Platform**: UI, lifecycle, permissions (20-40% кода)
- **Expect/Actual**: Platform abstractions
- **Architecture**: Clean Architecture + Repository pattern
- **Integration**: Нативные UI frameworks, shared ViewModels

Ключевые моменты: правильные границы, Swift-friendly APIs, lifecycle management, platform-specific оптимизации.


---

## Related Questions

### Hub
- [[q-clean-architecture-android--android--hard]] - Clean Architecture principles

### Related (Hard)
- [[q-mvi-architecture--android--hard]] - MVI architecture pattern
- [[q-mvi-handle-one-time-events--android--hard]] - MVI one-time event handling
- [[q-offline-first-architecture--android--hard]] - Offline-first architecture

