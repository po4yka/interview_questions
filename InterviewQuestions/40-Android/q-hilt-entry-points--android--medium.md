---
id: 20251012-1227151
title: "Hilt Entry Points"
topic: android
difficulty: medium
status: draft
moc: moc-android
created: 2025-10-11
tags: [dependency-injection, hilt, dagger, architecture, difficulty/medium]
related: [q-viewgroup-vs-view-differences--android--easy, q-cancel-presenter-requests--android--medium, q-how-to-create-list-like-recyclerview-in-compose--android--medium]
  - q-dagger-multibinding--di--hard
  - q-hilt-assisted-injection--di--medium
  - q-hilt-viewmodel-injection--jetpack--medium
---

# Question (EN)

> What are Hilt Entry Points and when would you use them? How do they differ from standard dependency injection?

## Answer (EN)

### Overview

**Hilt Entry Points** are interfaces annotated with `@EntryPoint` that allow you to get dependencies from Hilt in places where Hilt cannot automatically inject dependencies. They serve as a bridge between the Hilt dependency graph and code that isn't managed by Hilt.

### When Standard Injection Doesn't Work

Hilt can automatically inject dependencies into:

-   Activities (annotated with `@AndroidEntryPoint`)
-   Fragments
-   Views
-   Services
-   BroadcastReceivers
-   ViewModels

But there are cases where Hilt **cannot** inject:

1. **Content Providers** - Created before Application.onCreate()
2. **WorkManager Workers** - Instantiated by WorkManager, not Hilt
3. **Third-party libraries** - You don't control their constructors
4. **Static methods or objects** - No instance to inject into
5. **Custom lifecycle components** - Not in the standard Android lifecycle

### Basic Entry Point Example

```kotlin
// 1. Define an Entry Point interface
@EntryPoint
@InstallIn(SingletonComponent::class)
interface AnalyticsEntryPoint {
    fun analyticsTracker(): AnalyticsTracker
    fun userRepository(): UserRepository
}

// 2. Use the Entry Point in a non-Hilt class
class MyContentProvider : ContentProvider() {
    private lateinit var analyticsTracker: AnalyticsTracker
    private lateinit var userRepository: UserRepository

    override fun onCreate(): Boolean {
        // Get the application context
        val appContext = context?.applicationContext ?: throw IllegalStateException()

        // Retrieve the Entry Point
        val entryPoint = EntryPointAccessors.fromApplication(
            appContext,
            AnalyticsEntryPoint::class.java
        )

        // Get dependencies
        analyticsTracker = entryPoint.analyticsTracker()
        userRepository = entryPoint.userRepository()

        analyticsTracker.track("ContentProvider.onCreate")
        return true
    }

    override fun query(
        uri: Uri,
        projection: Array<String>?,
        selection: String?,
        selectionArgs: Array<String>?,
        sortOrder: String?
    ): Cursor? {
        val user = userRepository.getCurrentUser()
        analyticsTracker.track("ContentProvider.query", mapOf("userId" to user.id))
        // Query implementation...
        return null
    }

    // Other ContentProvider methods...
    override fun insert(uri: Uri, values: ContentValues?): Uri? = null
    override fun update(uri: Uri, values: ContentValues?, selection: String?, selectionArgs: Array<String>?): Int = 0
    override fun delete(uri: Uri, selection: String?, selectionArgs: Array<String>?): Int = 0
    override fun getType(uri: Uri): String? = null
}
```

### Entry Point Accessors

Hilt provides different accessors depending on where you need the Entry Point:

```kotlin
// 1. From Application Context
val entryPoint = EntryPointAccessors.fromApplication(
    applicationContext,
    MyEntryPoint::class.java
)

// 2. From Activity Context
val entryPoint = EntryPointAccessors.fromActivity(
    activity,
    MyEntryPoint::class.java
)

// 3. From any object that implements HasComponent
val entryPoint = EntryPointAccessors.fromActivity(
    activity,
    MyEntryPoint::class.java
)

// 4. Generic access from any component
val entryPoint = EntryPointAccessors.fromApplication<MyEntryPoint>(
    applicationContext
)
```

### Real-World Example: WorkManager Integration

Before Hilt 2.31, WorkManager was a common use case for Entry Points:

```kotlin
// Entry Point for Workers
@EntryPoint
@InstallIn(SingletonComponent::class)
interface WorkerEntryPoint {
    fun apiService(): ApiService
    fun database(): AppDatabase
    fun notificationManager(): NotificationManager
}

// Custom Worker Factory
class HiltWorkerFactory @Inject constructor(
    private val applicationContext: Context
) : WorkerFactory() {

    override fun createWorker(
        appContext: Context,
        workerClassName: String,
        workerParameters: WorkerParameters
    ): ListenableWorker? {
        return when (workerClassName) {
            DataSyncWorker::class.java.name -> {
                val entryPoint = EntryPointAccessors.fromApplication(
                    appContext,
                    WorkerEntryPoint::class.java
                )
                DataSyncWorker(
                    appContext,
                    workerParameters,
                    entryPoint.apiService(),
                    entryPoint.database()
                )
            }
            NotificationWorker::class.java.name -> {
                val entryPoint = EntryPointAccessors.fromApplication(
                    appContext,
                    WorkerEntryPoint::class.java
                )
                NotificationWorker(
                    appContext,
                    workerParameters,
                    entryPoint.notificationManager()
                )
            }
            else -> null
        }
    }
}

// Worker implementation
class DataSyncWorker(
    context: Context,
    params: WorkerParameters,
    private val apiService: ApiService,
    private val database: AppDatabase
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            val data = apiService.fetchData()
            database.dataDao().insertAll(data)
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}

// Setup in Application
@HiltAndroidApp
class MyApplication : Application(), Configuration.Provider {

    @Inject
    lateinit var workerFactory: HiltWorkerFactory

    override fun getWorkManagerConfiguration(): Configuration {
        return Configuration.Builder()
            .setWorkerFactory(workerFactory)
            .build()
    }
}
```

**Note**: Hilt 2.31+ provides `@HiltWorker` annotation for automatic Worker injection:

```kotlin
// Modern approach with Hilt 2.31+
@HiltWorker
class DataSyncWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val apiService: ApiService,
    private val database: AppDatabase
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            val data = apiService.fetchData()
            database.dataDao().insertAll(data)
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}
```

### Entry Points in Third-Party Libraries

```kotlin
// Your library code that needs dependencies
class ThirdPartyLibraryInitializer {

    fun initialize(context: Context) {
        // This is called by a third-party library
        // We don't control when or how it's called

        val entryPoint = EntryPointAccessors.fromApplication(
            context.applicationContext,
            LibraryEntryPoint::class.java
        )

        val config = LibraryConfig(
            apiKey = entryPoint.apiKeyProvider().getApiKey(),
            logger = entryPoint.logger(),
            cache = entryPoint.cacheManager()
        )

        ThirdPartyLibrary.init(config)
    }
}

@EntryPoint
@InstallIn(SingletonComponent::class)
interface LibraryEntryPoint {
    fun apiKeyProvider(): ApiKeyProvider
    fun logger(): Logger
    fun cacheManager(): CacheManager
}
```

### Entry Points for View Inflation

When inflating custom views manually (not through Hilt-aware layout inflation):

```kotlin
// Custom View that needs dependencies
class AnalyticsTrackedButton @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : AppCompatButton(context, attrs, defStyleAttr) {

    private val analyticsTracker: AnalyticsTracker

    init {
        // Get Entry Point from Activity context
        analyticsTracker = if (context is ComponentActivity) {
            val entryPoint = EntryPointAccessors.fromActivity(
                context,
                ViewEntryPoint::class.java
            )
            entryPoint.analyticsTracker()
        } else {
            // Fallback to Application context
            val entryPoint = EntryPointAccessors.fromApplication(
                context.applicationContext,
                ViewEntryPoint::class.java
            )
            entryPoint.analyticsTracker()
        }
    }

    override fun performClick(): Boolean {
        analyticsTracker.track("button_click", mapOf(
            "button_id" to id.toString(),
            "button_text" to text.toString()
        ))
        return super.performClick()
    }
}

@EntryPoint
@InstallIn(ActivityComponent::class)
interface ViewEntryPoint {
    fun analyticsTracker(): AnalyticsTracker
}
```

### Entry Points with Different Components

Entry Points can be installed in different Hilt components:

```kotlin
// Singleton scope - Lives for the entire app lifecycle
@EntryPoint
@InstallIn(SingletonComponent::class)
interface AppEntryPoint {
    fun appDatabase(): AppDatabase
    fun sharedPreferences(): SharedPreferences
}

// Activity scope - Lives for a single Activity
@EntryPoint
@InstallIn(ActivityComponent::class)
interface ActivityEntryPoint {
    fun activityTracker(): ActivityTracker
    fun navigationController(): NavigationController
}

// Activity retained scope - Survives configuration changes
@EntryPoint
@InstallIn(ActivityRetainedComponent::class)
interface ActivityRetainedEntryPoint {
    fun viewModelStore(): ViewModelStore
}

// Fragment scope - Lives for a single Fragment
@EntryPoint
@InstallIn(FragmentComponent::class)
interface FragmentEntryPoint {
    fun fragmentTracker(): FragmentTracker
}

// View scope - Lives for a single View
@EntryPoint
@InstallIn(ViewComponent::class)
interface ViewEntryPoint {
    fun viewTracker(): ViewTracker
}

// View with Fragment scope
@EntryPoint
@InstallIn(ViewWithFragmentComponent::class)
interface ViewWithFragmentEntryPoint {
    fun fragmentViewTracker(): FragmentViewTracker
}

// Service scope
@EntryPoint
@InstallIn(ServiceComponent::class)
interface ServiceEntryPoint {
    fun serviceTracker(): ServiceTracker
}
```

### Complex Example: Multi-Process Application

```kotlin
// Main process dependencies
@EntryPoint
@InstallIn(SingletonComponent::class)
interface MainProcessEntryPoint {
    fun mainRepository(): MainRepository
    fun userSession(): UserSession
}

// Background process dependencies (different Application instance)
@EntryPoint
@InstallIn(SingletonComponent::class)
interface BackgroundProcessEntryPoint {
    fun syncEngine(): SyncEngine
    fun database(): AppDatabase
}

// Content Provider running in separate process
class DataSyncProvider : ContentProvider() {

    private lateinit var syncEngine: SyncEngine
    private lateinit var database: AppDatabase

    override fun onCreate(): Boolean {
        val appContext = context?.applicationContext ?: return false

        // This provider runs in a separate process
        // It has its own Application instance with its own Hilt graph
        val entryPoint = EntryPointAccessors.fromApplication(
            appContext,
            BackgroundProcessEntryPoint::class.java
        )

        syncEngine = entryPoint.syncEngine()
        database = entryPoint.database()

        return true
    }

    override fun call(method: String, arg: String?, extras: Bundle?): Bundle? {
        return when (method) {
            "sync" -> {
                syncEngine.performSync()
                Bundle().apply { putBoolean("success", true) }
            }
            else -> null
        }
    }

    // Other ContentProvider methods...
    override fun query(uri: Uri, projection: Array<String>?, selection: String?, selectionArgs: Array<String>?, sortOrder: String?): Cursor? = null
    override fun insert(uri: Uri, values: ContentValues?): Uri? = null
    override fun update(uri: Uri, values: ContentValues?, selection: String?, selectionArgs: Array<String>?): Int = 0
    override fun delete(uri: Uri, selection: String?, selectionArgs: Array<String>?): Int = 0
    override fun getType(uri: Uri): String? = null
}

// AndroidManifest.xml
/*
<provider
    android:name=".DataSyncProvider"
    android:authorities="com.example.provider"
    android:enabled="true"
    android:exported="false"
    android:process=":sync" />
*/
```

### Production Example: Firebase Messaging

```kotlin
// Firebase Messaging Service (cannot use @AndroidEntryPoint)
class MyFirebaseMessagingService : FirebaseMessagingService() {

    private val notificationManager: NotificationManager by lazy {
        val entryPoint = EntryPointAccessors.fromApplication(
            applicationContext,
            MessagingEntryPoint::class.java
        )
        entryPoint.notificationManager()
    }

    private val userRepository: UserRepository by lazy {
        val entryPoint = EntryPointAccessors.fromApplication(
            applicationContext,
            MessagingEntryPoint::class.java
        )
        entryPoint.userRepository()
    }

    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        super.onMessageReceived(remoteMessage)

        val userId = userRepository.getCurrentUserId()

        remoteMessage.notification?.let { notification ->
            notificationManager.showNotification(
                title = notification.title ?: "New Message",
                body = notification.body ?: "",
                userId = userId
            )
        }
    }

    override fun onNewToken(token: String) {
        super.onNewToken(token)
        // Update token in repository
        userRepository.updateFcmToken(token)
    }
}

@EntryPoint
@InstallIn(SingletonComponent::class)
interface MessagingEntryPoint {
    fun notificationManager(): NotificationManager
    fun userRepository(): UserRepository
}

// Notification Manager
@Singleton
class NotificationManager @Inject constructor(
    @ApplicationContext private val context: Context,
    private val notificationChannelManager: NotificationChannelManager
) {

    private val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE)
        as android.app.NotificationManager

    fun showNotification(title: String, body: String, userId: String) {
        val channelId = notificationChannelManager.getOrCreateChannel("messages")

        val notification = NotificationCompat.Builder(context, channelId)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(title)
            .setContentText(body)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true)
            .build()

        notificationManager.notify(userId.hashCode(), notification)
    }
}
```

### Entry Points vs Standard Injection

| Aspect          | Standard Injection              | Entry Points                                    |
| --------------- | ------------------------------- | ----------------------------------------------- |
| **Syntax**      | `@Inject` annotation            | `@EntryPoint` interface + `EntryPointAccessors` |
| **Automatic**   | Yes, Hilt manages lifecycle     | No, manual retrieval required                   |
| **Type Safety** | Compile-time                    | Compile-time (interface) + Runtime (accessor)   |
| **Performance** | Faster (direct field injection) | Slightly slower (lookup + call)                 |
| **Use Case**    | Hilt-managed classes            | Non-Hilt classes, external libraries            |
| **Boilerplate** | Minimal                         | More (interface definition)                     |
| **Lifecycle**   | Tied to component scope         | Retrieved on-demand                             |

### Best Practices

1. **Prefer Standard Injection**

    ```kotlin
    //  GOOD - Use standard injection when possible
    @AndroidEntryPoint
    class MyActivity : AppCompatActivity() {
        @Inject lateinit var repository: Repository
    }

    //  AVOID - Don't use Entry Points unnecessarily
    class MyActivity : AppCompatActivity() {
        private lateinit var repository: Repository

        override fun onCreate(savedInstanceState: Bundle?) {
            super.onCreate(savedInstanceState)
            val entryPoint = EntryPointAccessors.fromActivity(this, MyEntryPoint::class.java)
            repository = entryPoint.repository() // Unnecessary!
        }
    }
    ```

2. **Minimize Entry Point Surface**

    ```kotlin
    //  GOOD - Specific, minimal interface
    @EntryPoint
    @InstallIn(SingletonComponent::class)
    interface WorkerEntryPoint {
        fun apiService(): ApiService
        fun database(): AppDatabase
    }

    //  BAD - Exposing too many dependencies
    @EntryPoint
    @InstallIn(SingletonComponent::class)
    interface GodEntryPoint {
        fun apiService(): ApiService
        fun database(): AppDatabase
        fun sharedPreferences(): SharedPreferences
        fun analytics(): Analytics
        fun logger(): Logger
        fun cache(): Cache
        // ... 20 more dependencies
    }
    ```

3. **Cache Entry Point Access**

    ```kotlin
    //  GOOD - Cache the dependency, not the accessor
    class MyContentProvider : ContentProvider() {
        private val repository: Repository by lazy {
            val entryPoint = EntryPointAccessors.fromApplication(
                context!!.applicationContext,
                MyEntryPoint::class.java
            )
            entryPoint.repository()
        }

        override fun query(...): Cursor? {
            repository.getData() // Fast, already cached
            return null
        }
    }

    //  BAD - Repeated accessor calls
    class MyContentProvider : ContentProvider() {
        override fun query(...): Cursor? {
            val entryPoint = EntryPointAccessors.fromApplication(
                context!!.applicationContext,
                MyEntryPoint::class.java
            )
            entryPoint.repository().getData() // Repeated work!
            return null
        }
    }
    ```

4. **Use Appropriate Component Scope**

    ```kotlin
    //  GOOD - SingletonComponent for app-wide dependencies
    @EntryPoint
    @InstallIn(SingletonComponent::class)
    interface AppEntryPoint {
        fun database(): AppDatabase
    }

    //  GOOD - ActivityComponent for activity-scoped dependencies
    @EntryPoint
    @InstallIn(ActivityComponent::class)
    interface ActivityEntryPoint {
        fun activityTracker(): ActivityTracker
    }

    //  BAD - Wrong scope
    @EntryPoint
    @InstallIn(ActivityComponent::class) // Activity scope!
    interface BadEntryPoint {
        fun database(): AppDatabase // Singleton dependency!
    }
    ```

5. **Error Handling**

    ```kotlin
    //  GOOD - Handle potential errors
    class MyContentProvider : ContentProvider() {
        private val repository: Repository? by lazy {
            try {
                val entryPoint = EntryPointAccessors.fromApplication(
                    context?.applicationContext ?: return@lazy null,
                    MyEntryPoint::class.java
                )
                entryPoint.repository()
            } catch (e: IllegalStateException) {
                Log.e("MyContentProvider", "Hilt not initialized", e)
                null
            }
        }

        override fun onCreate(): Boolean {
            if (repository == null) {
                Log.e("MyContentProvider", "Failed to initialize dependencies")
                return false
            }
            return true
        }
    }
    ```

### Common Pitfalls

1. **Using Entry Points in Hilt-Managed Classes**

    ```kotlin
    //  BAD - Activity already supports @Inject
    @AndroidEntryPoint
    class MyActivity : AppCompatActivity() {
        private lateinit var repository: Repository

        override fun onCreate(savedInstanceState: Bundle?) {
            super.onCreate(savedInstanceState)
            val entryPoint = EntryPointAccessors.fromActivity(this, MyEntryPoint::class.java)
            repository = entryPoint.repository() // Why?!
        }
    }

    //  GOOD - Use standard injection
    @AndroidEntryPoint
    class MyActivity : AppCompatActivity() {
        @Inject lateinit var repository: Repository
    }
    ```

2. **Incorrect Component Scope**

    ```kotlin
    //  BAD - ContentProvider needs SingletonComponent
    @EntryPoint
    @InstallIn(ActivityComponent::class) // Wrong!
    interface MyEntryPoint {
        fun repository(): Repository
    }

    class MyContentProvider : ContentProvider() {
        override fun onCreate(): Boolean {
            // This will crash - no Activity context!
            val entryPoint = EntryPointAccessors.fromApplication(
                context!!.applicationContext,
                MyEntryPoint::class.java // Expects ActivityComponent!
            )
            return true
        }
    }

    //  GOOD
    @EntryPoint
    @InstallIn(SingletonComponent::class)
    interface MyEntryPoint {
        fun repository(): Repository
    }
    ```

3. **Memory Leaks with Wrong Scope**

    ```kotlin
    //  BAD - Leaking Activity reference
    @EntryPoint
    @InstallIn(ActivityComponent::class)
    interface ActivityEntryPoint {
        fun activityTracker(): ActivityTracker
    }

    @Singleton // Singleton holding Activity-scoped dependency!
    class BackgroundService @Inject constructor(
        private val context: Context
    ) {
        private val activityTracker: ActivityTracker by lazy {
            // This will leak the Activity!
            val entryPoint = EntryPointAccessors.fromActivity(
                context as Activity, // Context might be Activity
                ActivityEntryPoint::class.java
            )
            entryPoint.activityTracker()
        }
    }

    //  GOOD - Use appropriate scope
    @EntryPoint
    @InstallIn(SingletonComponent::class)
    interface ServiceEntryPoint {
        fun serviceTracker(): ServiceTracker // Singleton-scoped
    }
    ```

### Testing Entry Points

```kotlin
// Entry Point
@EntryPoint
@InstallIn(SingletonComponent::class)
interface TestEntryPoint {
    fun repository(): Repository
    fun apiService(): ApiService
}

// Test
@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class ContentProviderTest {

    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun testContentProviderWithMocks() {
        // Get Entry Point in test
        val context = ApplicationProvider.getApplicationContext<Context>()
        val entryPoint = EntryPointAccessors.fromApplication(
            context,
            TestEntryPoint::class.java
        )

        val repository = entryPoint.repository()
        assertNotNull(repository)
    }

    // You can also provide test doubles
    @Module
    @InstallIn(SingletonComponent::class)
    object TestModule {
        @Provides
        @Singleton
        fun provideRepository(): Repository = FakeRepository()
    }
}
```

### Summary

**Hilt Entry Points** are interfaces that provide access to Hilt dependencies in classes where automatic injection isn't possible:

**When to use**:

-   Content Providers
-   WorkManager Workers (before Hilt 2.31)
-   Firebase Services
-   Third-party library initialization
-   Custom views with complex inflation
-   Multi-process components

**When NOT to use**:

-   Activities, Fragments, Services (use `@AndroidEntryPoint`)
-   ViewModels (use `@HiltViewModel`)
-   Any Hilt-managed class

**Key differences from standard injection**:

-   Manual retrieval vs automatic injection
-   Requires explicit interface definition
-   Slightly more boilerplate
-   Used as escape hatch for non-Hilt code

**Best practices**:

1. Prefer standard injection when possible
2. Keep Entry Point interfaces small and focused
3. Use appropriate component scope
4. Cache dependencies, not accessors
5. Handle initialization errors gracefully

---

# Вопрос (RU)

Что такое Hilt Entry Points и когда их использовать? Чем они отличаются от стандартной инъекции зависимостей?

## Ответ (RU)

### Обзор

**Hilt Entry Points** — это интерфейсы, помеченные аннотацией `@EntryPoint`, которые позволяют получать зависимости из Hilt в местах, где Hilt не может автоматически внедрить зависимости. Они служат мостом между графом зависимостей Hilt и кодом, который не управляется Hilt.

### Когда стандартная инъекция не работает

Hilt может автоматически внедрять зависимости в:

-   Activity (с аннотацией `@AndroidEntryPoint`)
-   Fragment
-   View
-   Service
-   BroadcastReceiver
-   ViewModel

Но есть случаи, когда Hilt **не может** выполнить инъекцию:

1. **Content Provider** — создаются до Application.onCreate()
2. **WorkManager Worker** — создаются WorkManager, а не Hilt
3. **Сторонние библиотеки** — вы не контролируете их конструкторы
4. **Статические методы или объекты** — нет экземпляра для инъекции
5. **Пользовательские компоненты жизненного цикла** — не входят в стандартный жизненный цикл Android

### Базовый пример Entry Point

```kotlin
// 1. Определяем интерфейс Entry Point
@EntryPoint
@InstallIn(SingletonComponent::class)
interface AnalyticsEntryPoint {
    fun analyticsTracker(): AnalyticsTracker
    fun userRepository(): UserRepository
}

// 2. Используем Entry Point в не-Hilt классе
class MyContentProvider : ContentProvider() {
    private lateinit var analyticsTracker: AnalyticsTracker
    private lateinit var userRepository: UserRepository

    override fun onCreate(): Boolean {
        // Получаем контекст приложения
        val appContext = context?.applicationContext ?: throw IllegalStateException()

        // Получаем Entry Point
        val entryPoint = EntryPointAccessors.fromApplication(
            appContext,
            AnalyticsEntryPoint::class.java
        )

        // Получаем зависимости
        analyticsTracker = entryPoint.analyticsTracker()
        userRepository = entryPoint.userRepository()

        analyticsTracker.track("ContentProvider.onCreate")
        return true
    }

    override fun query(
        uri: Uri,
        projection: Array<String>?,
        selection: String?,
        selectionArgs: Array<String>?,
        sortOrder: String?
    ): Cursor? {
        val user = userRepository.getCurrentUser()
        analyticsTracker.track("ContentProvider.query", mapOf("userId" to user.id))
        // Реализация query...
        return null
    }

    // Другие методы ContentProvider...
    override fun insert(uri: Uri, values: ContentValues?): Uri? = null
    override fun update(uri: Uri, values: ContentValues?, selection: String?, selectionArgs: Array<String>?): Int = 0
    override fun delete(uri: Uri, selection: String?, selectionArgs: Array<String>?): Int = 0
    override fun getType(uri: Uri): String? = null
}
```

### Entry Point Accessors

Hilt предоставляет различные способы доступа в зависимости от контекста:

```kotlin
// 1. Из контекста Application
val entryPoint = EntryPointAccessors.fromApplication(
    applicationContext,
    MyEntryPoint::class.java
)

// 2. Из контекста Activity
val entryPoint = EntryPointAccessors.fromActivity(
    activity,
    MyEntryPoint::class.java
)

// 3. Из любого объекта, реализующего HasComponent
val entryPoint = EntryPointAccessors.fromActivity(
    activity,
    MyEntryPoint::class.java
)

// 4. Обобщённый доступ из любого компонента
val entryPoint = EntryPointAccessors.fromApplication<MyEntryPoint>(
    applicationContext
)
```

### Реальный пример: интеграция с WorkManager

До Hilt 2.31 WorkManager был типичным случаем использования Entry Points:

```kotlin
// Entry Point для Worker'ов
@EntryPoint
@InstallIn(SingletonComponent::class)
interface WorkerEntryPoint {
    fun apiService(): ApiService
    fun database(): AppDatabase
    fun notificationManager(): NotificationManager
}

// Пользовательская WorkerFactory
class HiltWorkerFactory @Inject constructor(
    private val applicationContext: Context
) : WorkerFactory() {

    override fun createWorker(
        appContext: Context,
        workerClassName: String,
        workerParameters: WorkerParameters
    ): ListenableWorker? {
        return when (workerClassName) {
            DataSyncWorker::class.java.name -> {
                val entryPoint = EntryPointAccessors.fromApplication(
                    appContext,
                    WorkerEntryPoint::class.java
                )
                DataSyncWorker(
                    appContext,
                    workerParameters,
                    entryPoint.apiService(),
                    entryPoint.database()
                )
            }
            NotificationWorker::class.java.name -> {
                val entryPoint = EntryPointAccessors.fromApplication(
                    appContext,
                    WorkerEntryPoint::class.java
                )
                NotificationWorker(
                    appContext,
                    workerParameters,
                    entryPoint.notificationManager()
                )
            }
            else -> null
        }
    }
}

// Реализация Worker
class DataSyncWorker(
    context: Context,
    params: WorkerParameters,
    private val apiService: ApiService,
    private val database: AppDatabase
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            val data = apiService.fetchData()
            database.dataDao().insertAll(data)
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}

// Настройка в Application
@HiltAndroidApp
class MyApplication : Application(), Configuration.Provider {

    @Inject
    lateinit var workerFactory: HiltWorkerFactory

    override fun getWorkManagerConfiguration(): Configuration {
        return Configuration.Builder()
            .setWorkerFactory(workerFactory)
            .build()
    }
}
```

**Примечание**: начиная с Hilt 2.31+ доступна аннотация `@HiltWorker` для автоматической инъекции в Worker:

```kotlin
// Современный подход с Hilt 2.31+
@HiltWorker
class DataSyncWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val apiService: ApiService,
    private val database: AppDatabase
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            val data = apiService.fetchData()
            database.dataDao().insertAll(data)
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}
```

### Entry Points в сторонних библиотеках

```kotlin
// Код вашей библиотеки, которому нужны зависимости
class ThirdPartyLibraryInitializer {

    fun initialize(context: Context) {
        // Это вызывается сторонней библиотекой
        // Мы не контролируем, когда и как это вызывается

        val entryPoint = EntryPointAccessors.fromApplication(
            context.applicationContext,
            LibraryEntryPoint::class.java
        )

        val config = LibraryConfig(
            apiKey = entryPoint.apiKeyProvider().getApiKey(),
            logger = entryPoint.logger(),
            cache = entryPoint.cacheManager()
        )

        ThirdPartyLibrary.init(config)
    }
}

@EntryPoint
@InstallIn(SingletonComponent::class)
interface LibraryEntryPoint {
    fun apiKeyProvider(): ApiKeyProvider
    fun logger(): Logger
    fun cacheManager(): CacheManager
}
```

### Entry Points для надува View

При ручном надуве кастомных view (не через Hilt-осведомлённый layout inflation):

```kotlin
// Кастомная View, которой нужны зависимости
class AnalyticsTrackedButton @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : AppCompatButton(context, attrs, defStyleAttr) {

    private val analyticsTracker: AnalyticsTracker

    init {
        // Получаем Entry Point из контекста Activity
        analyticsTracker = if (context is ComponentActivity) {
            val entryPoint = EntryPointAccessors.fromActivity(
                context,
                ViewEntryPoint::class.java
            )
            entryPoint.analyticsTracker()
        } else {
            // Fallback на контекст Application
            val entryPoint = EntryPointAccessors.fromApplication(
                context.applicationContext,
                ViewEntryPoint::class.java
            )
            entryPoint.analyticsTracker()
        }
    }

    override fun performClick(): Boolean {
        analyticsTracker.track("button_click", mapOf(
            "button_id" to id.toString(),
            "button_text" to text.toString()
        ))
        return super.performClick()
    }
}

@EntryPoint
@InstallIn(ActivityComponent::class)
interface ViewEntryPoint {
    fun analyticsTracker(): AnalyticsTracker
}
```

### Entry Points с различными компонентами

Entry Points можно устанавливать в разные Hilt-компоненты:

```kotlin
// Singleton scope — живёт весь жизненный цикл приложения
@EntryPoint
@InstallIn(SingletonComponent::class)
interface AppEntryPoint {
    fun appDatabase(): AppDatabase
    fun sharedPreferences(): SharedPreferences
}

// Activity scope — живёт в рамках одной Activity
@EntryPoint
@InstallIn(ActivityComponent::class)
interface ActivityEntryPoint {
    fun activityTracker(): ActivityTracker
    fun navigationController(): NavigationController
}

// Activity retained scope — переживает изменения конфигурации
@EntryPoint
@InstallIn(ActivityRetainedComponent::class)
interface ActivityRetainedEntryPoint {
    fun viewModelStore(): ViewModelStore
}

// Fragment scope — живёт в рамках одного Fragment
@EntryPoint
@InstallIn(FragmentComponent::class)
interface FragmentEntryPoint {
    fun fragmentTracker(): FragmentTracker
}

// View scope — живёт в рамках одной View
@EntryPoint
@InstallIn(ViewComponent::class)
interface ViewEntryPoint {
    fun viewTracker(): ViewTracker
}

// View with Fragment scope
@EntryPoint
@InstallIn(ViewWithFragmentComponent::class)
interface ViewWithFragmentEntryPoint {
    fun fragmentViewTracker(): FragmentViewTracker
}

// Service scope
@EntryPoint
@InstallIn(ServiceComponent::class)
interface ServiceEntryPoint {
    fun serviceTracker(): ServiceTracker
}
```

### Сложный пример: многопроцессное приложение

```kotlin
// Зависимости главного процесса
@EntryPoint
@InstallIn(SingletonComponent::class)
interface MainProcessEntryPoint {
    fun mainRepository(): MainRepository
    fun userSession(): UserSession
}

// Зависимости фонового процесса (другой экземпляр Application)
@EntryPoint
@InstallIn(SingletonComponent::class)
interface BackgroundProcessEntryPoint {
    fun syncEngine(): SyncEngine
    fun database(): AppDatabase
}

// Content Provider, работающий в отдельном процессе
class DataSyncProvider : ContentProvider() {

    private lateinit var syncEngine: SyncEngine
    private lateinit var database: AppDatabase

    override fun onCreate(): Boolean {
        val appContext = context?.applicationContext ?: return false

        // Этот провайдер работает в отдельном процессе
        // У него свой экземпляр Application со своим графом Hilt
        val entryPoint = EntryPointAccessors.fromApplication(
            appContext,
            BackgroundProcessEntryPoint::class.java
        )

        syncEngine = entryPoint.syncEngine()
        database = entryPoint.database()

        return true
    }

    override fun call(method: String, arg: String?, extras: Bundle?): Bundle? {
        return when (method) {
            "sync" -> {
                syncEngine.performSync()
                Bundle().apply { putBoolean("success", true) }
            }
            else -> null
        }
    }

    // Другие методы ContentProvider...
    override fun query(uri: Uri, projection: Array<String>?, selection: String?, selectionArgs: Array<String>?, sortOrder: String?): Cursor? = null
    override fun insert(uri: Uri, values: ContentValues?): Uri? = null
    override fun update(uri: Uri, values: ContentValues?, selection: String?, selectionArgs: Array<String>?): Int = 0
    override fun delete(uri: Uri, selection: String?, selectionArgs: Array<String>?): Int = 0
    override fun getType(uri: Uri): String? = null
}
```

### Production пример: Firebase Messaging

```kotlin
// Firebase Messaging Service (нельзя использовать @AndroidEntryPoint)
class MyFirebaseMessagingService : FirebaseMessagingService() {

    private val notificationManager: NotificationManager by lazy {
        val entryPoint = EntryPointAccessors.fromApplication(
            applicationContext,
            MessagingEntryPoint::class.java
        )
        entryPoint.notificationManager()
    }

    private val userRepository: UserRepository by lazy {
        val entryPoint = EntryPointAccessors.fromApplication(
            applicationContext,
            MessagingEntryPoint::class.java
        )
        entryPoint.userRepository()
    }

    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        super.onMessageReceived(remoteMessage)

        val userId = userRepository.getCurrentUserId()

        remoteMessage.notification?.let { notification ->
            notificationManager.showNotification(
                title = notification.title ?: "New Message",
                body = notification.body ?: "",
                userId = userId
            )
        }
    }

    override fun onNewToken(token: String) {
        super.onNewToken(token)
        // Обновляем токен в репозитории
        userRepository.updateFcmToken(token)
    }
}

@EntryPoint
@InstallIn(SingletonComponent::class)
interface MessagingEntryPoint {
    fun notificationManager(): NotificationManager
    fun userRepository(): UserRepository
}

// Notification Manager
@Singleton
class NotificationManager @Inject constructor(
    @ApplicationContext private val context: Context,
    private val notificationChannelManager: NotificationChannelManager
) {

    private val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE)
        as android.app.NotificationManager

    fun showNotification(title: String, body: String, userId: String) {
        val channelId = notificationChannelManager.getOrCreateChannel("messages")

        val notification = NotificationCompat.Builder(context, channelId)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(title)
            .setContentText(body)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true)
            .build()

        notificationManager.notify(userId.hashCode(), notification)
    }
}
```

### Entry Points vs стандартная инъекция

| Аспект                 | Стандартная инъекция                | Entry Points                                    |
| ---------------------- | ----------------------------------- | ----------------------------------------------- |
| **Синтаксис**          | Аннотация `@Inject`                 | Интерфейс `@EntryPoint` + `EntryPointAccessors` |
| **Автоматичность**     | Да, Hilt управляет жизненным циклом | Нет, требуется ручное получение                 |
| **Типобезопасность**   | Compile-time                        | Compile-time (интерфейс) + Runtime (accessor)   |
| **Производительность** | Быстрее (прямая инъекция полей)     | Чуть медленнее (lookup + вызов)                 |
| **Применение**         | Hilt-управляемые классы             | Не-Hilt классы, внешние библиотеки              |
| **Boilerplate**        | Минимальный                         | Больше (определение интерфейса)                 |
| **Жизненный цикл**     | Привязан к scope компонента         | Получается по требованию                        |

### Лучшие практики

1. **Предпочитайте стандартную инъекцию**

    ```kotlin
    //  ХОРОШО — используйте стандартную инъекцию, когда возможно
    @AndroidEntryPoint
    class MyActivity : AppCompatActivity() {
        @Inject lateinit var repository: Repository
    }

    //  ИЗБЕГАЙТЕ — не используйте Entry Points без необходимости
    class MyActivity : AppCompatActivity() {
        private lateinit var repository: Repository

        override fun onCreate(savedInstanceState: Bundle?) {
            super.onCreate(savedInstanceState)
            val entryPoint = EntryPointAccessors.fromActivity(this, MyEntryPoint::class.java)
            repository = entryPoint.repository() // Ненужно!
        }
    }
    ```

2. **Минимизируйте поверхность Entry Point**

    ```kotlin
    //  ХОРОШО — конкретный, минимальный интерфейс
    @EntryPoint
    @InstallIn(SingletonComponent::class)
    interface WorkerEntryPoint {
        fun apiService(): ApiService
        fun database(): AppDatabase
    }

    //  ПЛОХО — слишком много зависимостей
    @EntryPoint
    @InstallIn(SingletonComponent::class)
    interface GodEntryPoint {
        fun apiService(): ApiService
        fun database(): AppDatabase
        fun sharedPreferences(): SharedPreferences
        fun analytics(): Analytics
        fun logger(): Logger
        fun cache(): Cache
        // ... ещё 20 зависимостей
    }
    ```

3. **Кешируйте доступ к Entry Point**

    ```kotlin
    //  ХОРОШО — кешируйте зависимость, а не accessor
    class MyContentProvider : ContentProvider() {
        private val repository: Repository by lazy {
            val entryPoint = EntryPointAccessors.fromApplication(
                context!!.applicationContext,
                MyEntryPoint::class.java
            )
            entryPoint.repository()
        }

        override fun query(...): Cursor? {
            repository.getData() // Быстро, уже в кеше
            return null
        }
    }

    //  ПЛОХО — повторные вызовы accessor
    class MyContentProvider : ContentProvider() {
        override fun query(...): Cursor? {
            val entryPoint = EntryPointAccessors.fromApplication(
                context!!.applicationContext,
                MyEntryPoint::class.java
            )
            entryPoint.repository().getData() // Повторная работа!
            return null
        }
    }
    ```

4. **Используйте подходящий scope компонента**

    ```kotlin
    //  ХОРОШО — SingletonComponent для app-wide зависимостей
    @EntryPoint
    @InstallIn(SingletonComponent::class)
    interface AppEntryPoint {
        fun database(): AppDatabase
    }

    //  ХОРОШО — ActivityComponent для activity-scoped зависимостей
    @EntryPoint
    @InstallIn(ActivityComponent::class)
    interface ActivityEntryPoint {
        fun activityTracker(): ActivityTracker
    }

    //  ПЛОХО — неправильный scope
    @EntryPoint
    @InstallIn(ActivityComponent::class) // Activity scope!
    interface BadEntryPoint {
        fun database(): AppDatabase // Singleton зависимость!
    }
    ```

5. **Обработка ошибок**

    ```kotlin
    //  ХОРОШО — обрабатывайте потенциальные ошибки
    class MyContentProvider : ContentProvider() {
        private val repository: Repository? by lazy {
            try {
                val entryPoint = EntryPointAccessors.fromApplication(
                    context?.applicationContext ?: return@lazy null,
                    MyEntryPoint::class.java
                )
                entryPoint.repository()
            } catch (e: IllegalStateException) {
                Log.e("MyContentProvider", "Hilt not initialized", e)
                null
            }
        }

        override fun onCreate(): Boolean {
            if (repository == null) {
                Log.e("MyContentProvider", "Failed to initialize dependencies")
                return false
            }
            return true
        }
    }
    ```

### Распространённые ошибки

1. **Использование Entry Points в Hilt-управляемых классах**

    ```kotlin
    //  ПЛОХО — Activity уже поддерживает @Inject
    @AndroidEntryPoint
    class MyActivity : AppCompatActivity() {
        private lateinit var repository: Repository

        override fun onCreate(savedInstanceState: Bundle?) {
            super.onCreate(savedInstanceState)
            val entryPoint = EntryPointAccessors.fromActivity(this, MyEntryPoint::class.java)
            repository = entryPoint.repository() // Зачем?!
        }
    }

    //  ХОРОШО — используйте стандартную инъекцию
    @AndroidEntryPoint
    class MyActivity : AppCompatActivity() {
        @Inject lateinit var repository: Repository
    }
    ```

2. **Неправильный scope компонента**

    ```kotlin
    //  ПЛОХО — ContentProvider нужен SingletonComponent
    @EntryPoint
    @InstallIn(ActivityComponent::class) // Неправильно!
    interface MyEntryPoint {
        fun repository(): Repository
    }

    class MyContentProvider : ContentProvider() {
        override fun onCreate(): Boolean {
            // Это упадёт — нет Activity контекста!
            val entryPoint = EntryPointAccessors.fromApplication(
                context!!.applicationContext,
                MyEntryPoint::class.java // Ожидает ActivityComponent!
            )
            return true
        }
    }

    //  ХОРОШО
    @EntryPoint
    @InstallIn(SingletonComponent::class)
    interface MyEntryPoint {
        fun repository(): Repository
    }
    ```

3. **Утечки памяти с неправильным scope**

    ```kotlin
    //  ПЛОХО — утечка ссылки на Activity
    @EntryPoint
    @InstallIn(ActivityComponent::class)
    interface ActivityEntryPoint {
        fun activityTracker(): ActivityTracker
    }

    @Singleton // Singleton держит Activity-scoped зависимость!
    class BackgroundService @Inject constructor(
        private val context: Context
    ) {
        private val activityTracker: ActivityTracker by lazy {
            // Это приведёт к утечке Activity!
            val entryPoint = EntryPointAccessors.fromActivity(
                context as Activity, // Context может быть Activity
                ActivityEntryPoint::class.java
            )
            entryPoint.activityTracker()
        }
    }

    //  ХОРОШО — используйте подходящий scope
    @EntryPoint
    @InstallIn(SingletonComponent::class)
    interface ServiceEntryPoint {
        fun serviceTracker(): ServiceTracker // Singleton-scoped
    }
    ```

### Тестирование Entry Points

```kotlin
// Entry Point
@EntryPoint
@InstallIn(SingletonComponent::class)
interface TestEntryPoint {
    fun repository(): Repository
    fun apiService(): ApiService
}

// Тест
@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class ContentProviderTest {

    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun testContentProviderWithMocks() {
        // Получаем Entry Point в тесте
        val context = ApplicationProvider.getApplicationContext<Context>()
        val entryPoint = EntryPointAccessors.fromApplication(
            context,
            TestEntryPoint::class.java
        )

        val repository = entryPoint.repository()
        assertNotNull(repository)
    }

    // Также можно предоставить тестовые дубли
    @Module
    @InstallIn(SingletonComponent::class)
    object TestModule {
        @Provides
        @Singleton
        fun provideRepository(): Repository = FakeRepository()
    }
}
```

### Резюме

**Hilt Entry Points** — это интерфейсы, предоставляющие доступ к Hilt-зависимостям в классах, где автоматическая инъекция невозможна:

**Когда использовать**:

-   Content Provider
-   WorkManager Worker (до Hilt 2.31)
-   Firebase Services
-   Инициализация сторонних библиотек
-   Кастомные view со сложным надувом
-   Многопроцессные компоненты

**Когда НЕ использовать**:

-   Activity, Fragment, Service (используйте `@AndroidEntryPoint`)
-   ViewModel (используйте `@HiltViewModel`)
-   Любой Hilt-управляемый класс

**Ключевые отличия от стандартной инъекции**:

-   Ручное получение vs автоматическая инъекция
-   Требуется явное определение интерфейса
-   Немного больше boilerplate
-   Используется как escape hatch для не-Hilt кода

**Лучшие практики**:

1. Предпочитайте стандартную инъекцию, когда возможно
2. Держите интерфейсы Entry Point небольшими и сфокусированными
3. Используйте подходящий scope компонента
4. Кешируйте зависимости, а не accessor'ы
5. Обрабатывайте ошибки инициализации корректно

## Related Questions

- [[q-viewgroup-vs-view-differences--android--easy]]
- [[q-cancel-presenter-requests--android--medium]]
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]]
