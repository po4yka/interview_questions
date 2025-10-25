---
id: 20251012-1227151
title: "Hilt Entry Points / Hilt Entry Points"
aliases: ["Hilt Entry Points"]
topic: android
subtopics: [architecture, dependency-injection]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-hilt-entry-points, q-dagger-basics--android--medium, q-hilt-basics--android--easy]
created: 2025-10-11
updated: 2025-01-25
tags: [android/architecture, android/dependency-injection, architecture, dagger, dependency-injection, difficulty/medium, hilt]
sources: [https://dagger.dev/hilt/entry-points.html]
date created: Saturday, October 25th 2025, 1:26:29 pm
date modified: Saturday, October 25th 2025, 4:43:44 pm
---

# Вопрос (RU)
> Что такое Hilt Entry Points и когда их использовать?

# Question (EN)
> What are Hilt Entry Points and when would you use them?

---

## Ответ (RU)

**Теория Entry Points:**
Hilt Entry Points - это интерфейсы с аннотацией `@EntryPoint`, которые позволяют получать зависимости из Hilt в местах, где автоматическая инъекция невозможна. Служат мостом между графом зависимостей Hilt и кодом, не управляемым Hilt.

**Основные концепции:**
- Используются когда стандартная инъекция невозможна
- Требуют ручного получения через `EntryPointAccessors`
- Предоставляют доступ к Hilt-зависимостям в не-Hilt классах
- Могут быть установлены в разные компоненты (SingletonComponent, ActivityComponent и т.д.)

**Когда стандартная инъекция не работает:**
- Content Providers (создаются до Application.onCreate())
- WorkManager Workers (создаются WorkManager, не Hilt)
- Сторонние библиотеки (не контролируете конструкторы)
- Статические методы или объекты
- Кастомные компоненты жизненного цикла

**Базовый пример:**
```kotlin
// 1. Определяем Entry Point интерфейс
@EntryPoint
@InstallIn(SingletonComponent::class)
interface AnalyticsEntryPoint {
    fun analyticsTracker(): AnalyticsTracker
    fun userRepository(): UserRepository
}

// 2. Используем в не-Hilt классе
class MyContentProvider : ContentProvider() {
    private lateinit var analyticsTracker: AnalyticsTracker
    private lateinit var userRepository: UserRepository

    override fun onCreate(): Boolean {
        val appContext = context?.applicationContext ?: throw IllegalStateException()

        // Получаем Entry Point
        val entryPoint = EntryPointAccessors.fromApplication(
            appContext,
            AnalyticsEntryPoint::class.java
        )

        // Получаем зависимости
        analyticsTracker = entryPoint.analyticsTracker()
        userRepository = entryPoint.userRepository()

        return true
    }
}
```

**Entry Point Accessors:**
```kotlin
// Из Application Context
val entryPoint = EntryPointAccessors.fromApplication(
    applicationContext,
    MyEntryPoint::class.java
)

// Из Activity Context
val entryPoint = EntryPointAccessors.fromActivity(
    activity,
    MyEntryPoint::class.java
)

// Обобщённый доступ
val entryPoint = EntryPointAccessors.fromApplication<MyEntryPoint>(
    applicationContext
)
```

**WorkManager интеграция (до Hilt 2.31):**
```kotlin
@EntryPoint
@InstallIn(SingletonComponent::class)
interface WorkerEntryPoint {
    fun apiService(): ApiService
    fun database(): AppDatabase
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
            else -> null
        }
    }
}

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

**Firebase Messaging Service:**
```kotlin
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
}

@EntryPoint
@InstallIn(SingletonComponent::class)
interface MessagingEntryPoint {
    fun notificationManager(): NotificationManager
    fun userRepository(): UserRepository
}
```

**Различные компоненты:**
```kotlin
// Singleton scope - весь жизненный цикл приложения
@EntryPoint
@InstallIn(SingletonComponent::class)
interface AppEntryPoint {
    fun appDatabase(): AppDatabase
    fun sharedPreferences(): SharedPreferences
}

// Activity scope - один Activity
@EntryPoint
@InstallIn(ActivityComponent::class)
interface ActivityEntryPoint {
    fun activityTracker(): ActivityTracker
    fun navigationController(): NavigationController
}

// Fragment scope - один Fragment
@EntryPoint
@InstallIn(FragmentComponent::class)
interface FragmentEntryPoint {
    fun fragmentTracker(): FragmentTracker
}
```

## Answer (EN)

**Entry Points Theory:**
Hilt Entry Points are interfaces annotated with `@EntryPoint` that allow you to get dependencies from Hilt in places where automatic injection isn't possible. They serve as a bridge between the Hilt dependency graph and code that isn't managed by Hilt.

**Main concepts:**
- Used when standard injection doesn't work
- Require manual retrieval through `EntryPointAccessors`
- Provide access to Hilt dependencies in non-Hilt classes
- Can be installed in different components (SingletonComponent, ActivityComponent, etc.)

**When standard injection doesn't work:**
- Content Providers (created before Application.onCreate())
- WorkManager Workers (instantiated by WorkManager, not Hilt)
- Third-party libraries (you don't control constructors)
- Static methods or objects
- Custom lifecycle components

**Basic example:**
```kotlin
// 1. Define Entry Point interface
@EntryPoint
@InstallIn(SingletonComponent::class)
interface AnalyticsEntryPoint {
    fun analyticsTracker(): AnalyticsTracker
    fun userRepository(): UserRepository
}

// 2. Use in non-Hilt class
class MyContentProvider : ContentProvider() {
    private lateinit var analyticsTracker: AnalyticsTracker
    private lateinit var userRepository: UserRepository

    override fun onCreate(): Boolean {
        val appContext = context?.applicationContext ?: throw IllegalStateException()

        // Retrieve Entry Point
        val entryPoint = EntryPointAccessors.fromApplication(
            appContext,
            AnalyticsEntryPoint::class.java
        )

        // Get dependencies
        analyticsTracker = entryPoint.analyticsTracker()
        userRepository = entryPoint.userRepository()

        return true
    }
}
```

**Entry Point Accessors:**
```kotlin
// From Application Context
val entryPoint = EntryPointAccessors.fromApplication(
    applicationContext,
    MyEntryPoint::class.java
)

// From Activity Context
val entryPoint = EntryPointAccessors.fromActivity(
    activity,
    MyEntryPoint::class.java
)

// Generic access
val entryPoint = EntryPointAccessors.fromApplication<MyEntryPoint>(
    applicationContext
)
```

**WorkManager integration (before Hilt 2.31):**
```kotlin
@EntryPoint
@InstallIn(SingletonComponent::class)
interface WorkerEntryPoint {
    fun apiService(): ApiService
    fun database(): AppDatabase
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
            else -> null
        }
    }
}

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

**Firebase Messaging Service:**
```kotlin
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
}

@EntryPoint
@InstallIn(SingletonComponent::class)
interface MessagingEntryPoint {
    fun notificationManager(): NotificationManager
    fun userRepository(): UserRepository
}
```

**Different components:**
```kotlin
// Singleton scope - entire app lifecycle
@EntryPoint
@InstallIn(SingletonComponent::class)
interface AppEntryPoint {
    fun appDatabase(): AppDatabase
    fun sharedPreferences(): SharedPreferences
}

// Activity scope - single Activity
@EntryPoint
@InstallIn(ActivityComponent::class)
interface ActivityEntryPoint {
    fun activityTracker(): ActivityTracker
    fun navigationController(): NavigationController
}

// Fragment scope - single Fragment
@EntryPoint
@InstallIn(FragmentComponent::class)
interface FragmentEntryPoint {
    fun fragmentTracker(): FragmentTracker
}
```

---

## Follow-ups

- How do Entry Points affect performance compared to standard injection?
- What are the testing strategies for Entry Points?
- When should you avoid using Entry Points?

## Related Questions

### Prerequisites (Easier)
- [[q-hilt-basics--android--easy]] - Hilt basics
- [[q-android-app-components--android--easy]] - App components

### Related (Same Level)
- [[q-dagger-basics--android--medium]] - Dagger basics
- [[q-hilt-viewmodel-injection--android--medium]] - ViewModel injection
- [[q-dependency-injection-patterns--android--medium]] - DI patterns

### Advanced (Harder)
- [[q-dagger-multibinding--android--hard]] - Multibinding
- [[q-hilt-assisted-injection--android--hard]] - Assisted injection
