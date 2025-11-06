---
id: android-035
title: "Hilt Entry Points / Точки входа Hilt"
aliases: ["Hilt Entry Points", "Точки входа Hilt"]
topic: android
subtopics: [di-hilt, lifecycle]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-dependency-injection, c-hilt]
created: 2025-10-11
updated: 2025-01-27
tags: [android/di-hilt, android/lifecycle, dependency-injection, difficulty/medium, hilt]
sources: [https://dagger.dev/hilt/entry-points.html]
---

# Вопрос (RU)
> Что такое Hilt Entry Points и когда их использовать?

# Question (EN)
> What are Hilt Entry Points and when would you use them?

---

## Ответ (RU)

**Определение:**
[[c-hilt|Entry Points]] — это интерфейсы, аннотированные `@EntryPoint`, которые предоставляют доступ к зависимостям Hilt в местах, где автоматическая инъекция невозможна. Они служат мостом между графом зависимостей и кодом, который не управляется Hilt.

**Когда использовать:**
- Content Providers (создаются до Application.onCreate())
- WorkManager Workers (инстанцируются WorkManager)
- Firebase Services (FCM, Analytics)
- Broadcast Receivers без @AndroidEntryPoint
- Сторонние библиотеки (не контролируете конструкторы)

**Базовый пример:**
```kotlin
// ✅ Определяем Entry Point интерфейс
@EntryPoint
@InstallIn(SingletonComponent::class)
interface AnalyticsEntryPoint {
    fun analyticsTracker(): AnalyticsTracker
}

// ✅ Используем в ContentProvider
class MyContentProvider : ContentProvider() {
    private lateinit var tracker: AnalyticsTracker

    override fun onCreate(): Boolean {
        val appContext = context?.applicationContext ?: return false

        // Получаем Entry Point через EntryPointAccessors
        val entryPoint = EntryPointAccessors.fromApplication(
            appContext,
            AnalyticsEntryPoint::class.java
        )
        tracker = entryPoint.analyticsTracker()

        return true
    }
}
```

**WorkManager интеграция:**
```kotlin
// ✅ Современный подход с @HiltWorker
@HiltWorker
class DataSyncWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val apiService: ApiService // ✅ Автоматическая инъекция
) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        return try {
            apiService.syncData()
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}

// ❌ Устаревший подход через Entry Point
@EntryPoint
@InstallIn(SingletonComponent::class)
interface WorkerEntryPoint {
    fun apiService(): ApiService
}

class CustomWorkerFactory : WorkerFactory() {
    override fun createWorker(/*...*/): ListenableWorker? {
        // ❌ Ручное получение зависимостей
        val entryPoint = EntryPointAccessors.fromApplication(/*...*/)
        return DataSyncWorker(entryPoint.apiService())
    }
}
```

**Firebase Messaging Service:**
```kotlin
class MyFirebaseService : FirebaseMessagingService() {

    // ✅ Ленивая инициализация через Entry Point
    private val repository: MessageRepository by lazy {
        EntryPointAccessors.fromApplication<MessagingEntryPoint>(
            applicationContext
        ).messageRepository()
    }

    override fun onMessageReceived(message: RemoteMessage) {
        repository.processMessage(message)
    }
}

@EntryPoint
@InstallIn(SingletonComponent::class)
interface MessagingEntryPoint {
    fun messageRepository(): MessageRepository
}
```

**Component scopes:**
```kotlin
// Singleton scope - живет весь жизненный цикл приложения
@EntryPoint
@InstallIn(SingletonComponent::class)
interface AppEntryPoint {
    fun database(): AppDatabase
}

// Activity scope - создается и уничтожается с Activity
@EntryPoint
@InstallIn(ActivityComponent::class)
interface ActivityEntryPoint {
    fun navigationController(): NavigationController
}
```

**Best practices:**
- Используйте Entry Points только когда стандартная инъекция невозможна
- Для WorkManager предпочитайте @HiltWorker вместо Entry Points
- Кэшируйте полученные зависимости в lazy-свойствах
- Выбирайте правильный scope компонента (Singleton, Activity, Fragment)

## Answer (EN)

**Definition:**
[[c-hilt|Entry Points]] are interfaces annotated with `@EntryPoint` that provide access to Hilt dependencies in places where automatic injection isn't possible. They bridge the dependency graph with code not managed by Hilt.

**When to use:**
- Content Providers (created before Application.onCreate())
- WorkManager Workers (instantiated by WorkManager)
- Firebase Services (FCM, Analytics)
- Broadcast Receivers without @AndroidEntryPoint
- Third-party libraries (you don't control constructors)

**Basic example:**
```kotlin
// ✅ Define Entry Point interface
@EntryPoint
@InstallIn(SingletonComponent::class)
interface AnalyticsEntryPoint {
    fun analyticsTracker(): AnalyticsTracker
}

// ✅ Use in ContentProvider
class MyContentProvider : ContentProvider() {
    private lateinit var tracker: AnalyticsTracker

    override fun onCreate(): Boolean {
        val appContext = context?.applicationContext ?: return false

        // Retrieve Entry Point via EntryPointAccessors
        val entryPoint = EntryPointAccessors.fromApplication(
            appContext,
            AnalyticsEntryPoint::class.java
        )
        tracker = entryPoint.analyticsTracker()

        return true
    }
}
```

**WorkManager integration:**
```kotlin
// ✅ Modern approach with @HiltWorker
@HiltWorker
class DataSyncWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val apiService: ApiService // ✅ Automatic injection
) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        return try {
            apiService.syncData()
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}

// ❌ Legacy approach via Entry Point
@EntryPoint
@InstallIn(SingletonComponent::class)
interface WorkerEntryPoint {
    fun apiService(): ApiService
}

class CustomWorkerFactory : WorkerFactory() {
    override fun createWorker(/*...*/): ListenableWorker? {
        // ❌ Manual dependency retrieval
        val entryPoint = EntryPointAccessors.fromApplication(/*...*/)
        return DataSyncWorker(entryPoint.apiService())
    }
}
```

**Firebase Messaging Service:**
```kotlin
class MyFirebaseService : FirebaseMessagingService() {

    // ✅ Lazy initialization via Entry Point
    private val repository: MessageRepository by lazy {
        EntryPointAccessors.fromApplication<MessagingEntryPoint>(
            applicationContext
        ).messageRepository()
    }

    override fun onMessageReceived(message: RemoteMessage) {
        repository.processMessage(message)
    }
}

@EntryPoint
@InstallIn(SingletonComponent::class)
interface MessagingEntryPoint {
    fun messageRepository(): MessageRepository
}
```

**Component scopes:**
```kotlin
// Singleton scope - lives entire app lifecycle
@EntryPoint
@InstallIn(SingletonComponent::class)
interface AppEntryPoint {
    fun database(): AppDatabase
}

// Activity scope - created and destroyed with Activity
@EntryPoint
@InstallIn(ActivityComponent::class)
interface ActivityEntryPoint {
    fun navigationController(): NavigationController
}
```

**Best practices:**
- Use Entry Points only when standard injection is impossible
- For WorkManager prefer @HiltWorker over Entry Points
- Cache retrieved dependencies in lazy properties
- Choose correct component scope (Singleton, Activity, Fragment)

---

## Follow-ups

- How do Entry Points impact app startup performance compared to standard injection?
- What testing strategy should be used for classes that rely on Entry Points?
- How to handle Entry Point initialization failures gracefully?
- When should you create a custom component instead of using Entry Points?

## References

- [[c-dependency-injection]] - Dependency injection fundamentals
- [[c-hilt]] - Hilt dependency injection framework

## Related Questions

### Prerequisites (Easier)
- Hilt basics and component hierarchy
- Android application components lifecycle
- Dependency injection patterns in Android

### Related (Same Level)
- Hilt ViewModel injection and SavedStateHandle
- Custom Hilt components and scopes
- WorkManager integration with Hilt

### Advanced (Harder)
- Assisted injection with Hilt
- Hilt multibinding and set/map binding
- Custom component lifecycles and scopes
