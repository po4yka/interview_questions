---
id: android-035
title: Hilt Entry Points / Точки входа Hilt
aliases:
- Hilt Entry Points
- Точки входа Hilt
topic: android
subtopics:
- di-hilt
- lifecycle
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-dependency-injection
- c-hilt
created: 2025-10-11
updated: 2025-11-11
tags:
- android/di-hilt
- android/lifecycle
- dependency-injection
- difficulty/medium
- hilt
anki_cards:
- slug: android-035-0-en
  language: en
  anki_id: 1768367580655
  synced_at: '2026-01-23T16:45:05.283553'
- slug: android-035-0-ru
  language: ru
  anki_id: 1768367580680
  synced_at: '2026-01-23T16:45:05.285703'
sources:
- https://dagger.dev/hilt/entry-points.html
---
# Вопрос (RU)
> Что такое `Hilt` Entry Points и когда их использовать?

# Question (EN)
> What are `Hilt` Entry Points and when would you use them?

---

## Ответ (RU)

**Определение:**
[[c-hilt|Entry Points]] — это интерфейсы, аннотированные `@EntryPoint`, которые предоставляют доступ к зависимостям `Hilt` в местах, где автоматическая инъекция через `@AndroidEntryPoint` или конструктор невозможна. Они служат мостом между графом зависимостей и кодом, который не управляется `Hilt`.

**Когда использовать (типичные сценарии):**
- `ContentProvider` (создаются системой до `Application.onCreate()`, нельзя напрямую использовать `@AndroidEntryPoint`)
- `WorkManager` Workers (в специфичных случаях, когда вы не можете использовать `@HiltWorker` и штатный `HiltWorkerFactory`)
- Firebase Services (например, `FirebaseMessagingService`), где нельзя использовать `@AndroidEntryPoint`
- `BroadcastReceiver`, когда вы не можете или не хотите аннотировать его `@AndroidEntryPoint`
- Сторонние библиотеки и фреймворки (когда вы не контролируете конструкторы или точки создания объектов)

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

**`WorkManager` интеграция (рекомендуемый подход):**
```kotlin
// ✅ Современный подход: используем @HiltWorker и HiltWorkerFactory
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
```

**`WorkManager` и Entry Points (escape hatch):**
```kotlin
// ❗ Используйте Entry Point только если по архитектурным причинам
// вы не можете использовать @HiltWorker / HiltWorkerFactory.
@EntryPoint
@InstallIn(SingletonComponent::class)
interface WorkerEntryPoint {
    fun apiService(): ApiService
}

class CustomWorkerFactory(
    private val appContext: Context
) : WorkerFactory() {

    override fun createWorker(
        appContext: Context,
        workerClassName: String,
        workerParameters: WorkerParameters
    ): ListenableWorker? {
        return if (workerClassName == DataSyncWorker::class.qualifiedName) {
            val entryPoint = EntryPointAccessors.fromApplication(
                this.appContext,
                WorkerEntryPoint::class.java
            )
            // ✅ Ручное создание worker с зависимостью из Entry Point
            DataSyncWorker(appContext, workerParameters, entryPoint.apiService())
        } else {
            null
        }
    }
}
```

**Firebase Messaging `Service`:**
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

**`Component` scopes:**
```kotlin
// Singleton scope — живет весь жизненный цикл приложения
@EntryPoint
@InstallIn(SingletonComponent::class)
interface AppEntryPoint {
    fun database(): AppDatabase
}

// Activity scope — создается и уничтожается с Activity
// В реальном коде зависимости должны быть привязаны к ActivityComponent.
@EntryPoint
@InstallIn(ActivityComponent::class)
interface ActivityEntryPoint {
    fun navigationController(): NavigationController
}
```

**Best practices:**
- Используйте Entry Points только как "escape hatch" там, где стандартная инъекция через `@AndroidEntryPoint`, `@HiltViewModel`, `@HiltWorker` и т.п. невозможна.
- Для `WorkManager` по возможности предпочитайте `@HiltWorker` и встроенный `HiltWorkerFactory` вместо Entry Points.
- Всегда выбирайте компонент в `@InstallIn`, соответствующий тому, где объявлена нужная зависимость (Singleton, `Activity`, `Fragment` и т.д.).
- Кэшируйте полученные зависимости (например, через `lazy`), чтобы избежать лишних вызовов EntryPointAccessors.

## Answer (EN)

**Definition:**
[[c-hilt|Entry Points]] are interfaces annotated with `@EntryPoint` that provide access to `Hilt` dependencies in places where automatic injection via `@AndroidEntryPoint` or constructor injection is not possible. They act as a bridge between the dependency graph and code not managed by `Hilt`.

**When to use (typical scenarios):**
- ContentProviders (created by the system before `Application.onCreate()`, cannot directly use `@AndroidEntryPoint`)
- `WorkManager` Workers (in specific cases where you cannot use `@HiltWorker` and the standard `HiltWorkerFactory`)
- Firebase Services (e.g., `FirebaseMessagingService`) where `@AndroidEntryPoint` cannot be applied
- BroadcastReceivers when you cannot or do not want to annotate them with `@AndroidEntryPoint`
- Third-party libraries/frameworks (when you don't control constructors or creation points)

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

**`WorkManager` integration (recommended):**
```kotlin
// ✅ Modern approach: use @HiltWorker and HiltWorkerFactory
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
```

**`WorkManager` and Entry Points (escape hatch):**
```kotlin
// ❗ Use Entry Points only if, for architectural reasons,
// you cannot use @HiltWorker / HiltWorkerFactory.
@EntryPoint
@InstallIn(SingletonComponent::class)
interface WorkerEntryPoint {
    fun apiService(): ApiService
}

class CustomWorkerFactory(
    private val appContext: Context
) : WorkerFactory() {

    override fun createWorker(
        appContext: Context,
        workerClassName: String,
        workerParameters: WorkerParameters
    ): ListenableWorker? {
        return if (workerClassName == DataSyncWorker::class.qualifiedName) {
            val entryPoint = EntryPointAccessors.fromApplication(
                this.appContext,
                WorkerEntryPoint::class.java
            )
            // ✅ Manually create worker with dependency from Entry Point
            DataSyncWorker(appContext, workerParameters, entryPoint.apiService())
        } else {
            null
        }
    }
}
```

**Firebase Messaging `Service`:**
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

**`Component` scopes:**
```kotlin
// Singleton scope - lives for the entire app lifecycle
@EntryPoint
@InstallIn(SingletonComponent::class)
interface AppEntryPoint {
    fun database(): AppDatabase
}

// Activity scope - created and destroyed with Activity
// In real usage the dependencies must actually be bound in ActivityComponent.
@EntryPoint
@InstallIn(ActivityComponent::class)
interface ActivityEntryPoint {
    fun navigationController(): NavigationController
}
```

**Best practices:**
- Treat Entry Points as an escape hatch: use them only where standard injection (`@AndroidEntryPoint`, `@HiltViewModel`, `@HiltWorker`, etc.) cannot be applied.
- For `WorkManager`, prefer `@HiltWorker` and the built-in `HiltWorkerFactory` over Entry Points whenever possible.
- Always choose the `@InstallIn` component that matches where the dependency is bound (Singleton, `Activity`, `Fragment`, etc.).
- Cache retrieved dependencies (e.g., using `lazy`) to avoid repeated EntryPointAccessors calls.

---

## Дополнительные Вопросы (RU)

- Как точки входа влияют на производительность запуска приложения по сравнению со стандартной инъекцией?
- Какую стратегию тестирования использовать для классов, зависящих от Entry Points?
- Как корректно обрабатывать ошибки инициализации Entry Point?
- В каких случаях стоит создать собственный компонент вместо использования Entry Points?

## Follow-ups

- How do Entry Points impact app startup performance compared to standard injection?
- What testing strategy should be used for classes that rely on Entry Points?
- How to handle Entry Point initialization failures gracefully?
- When should you create a custom component instead of using Entry Points?

## Ссылки (RU)

- [[c-dependency-injection]] - Основы dependency injection
- [[c-hilt]] - Фреймворк dependency injection `Hilt`

## References

- [[c-dependency-injection]] - Dependency injection fundamentals
- [[c-hilt]] - `Hilt` dependency injection framework

## Связанные Вопросы (RU)

### База (проще)
- Основы `Hilt` и иерархии компонентов
- Жизненный цикл компонентов Android-приложения
- Паттерны dependency injection в Android

### На Том Же Уровне
- Инъекция `ViewModel` в `Hilt` и `SavedStateHandle`
- Кастомные компоненты и скоупы в `Hilt`
- Интеграция `WorkManager` с `Hilt`

### Продвинутое (сложнее)
- Assisted-инъекция в `Hilt`
- `Hilt` multibinding и set/map binding
- Кастомные жизненные циклы и скоупы компонентов

## Related Questions

### Prerequisites (Easier)
- `Hilt` basics and component hierarchy
- Android application components lifecycle
- Dependency injection patterns in Android

### Related (Same Level)
- `Hilt` `ViewModel` injection and SavedStateHandle
- Custom `Hilt` components and scopes
- `WorkManager` integration with `Hilt`

### Advanced (Harder)
- Assisted injection with `Hilt`
- `Hilt` multibinding and set/map binding
- Custom component lifecycles and scopes
