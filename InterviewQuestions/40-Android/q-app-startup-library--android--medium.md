---
id: 20251006-100006
title: App Startup Library / Библиотека App Startup
aliases: ["App Startup Library", "Библиотека App Startup"]
topic: android
subtopics: [app-startup, performance-memory]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-build-optimization--android--medium, q-android-performance-measurement-tools--android--medium, q-app-start-types-android--android--medium]
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [android/app-startup, android/performance-memory, difficulty/medium]
---
# Вопрос (RU)
> Что такое Библиотека App Startup?

# Question (EN)
> What is App Startup Library?

## Ответ (RU)

**App Startup Library** — библиотека Jetpack для централизованной инициализации компонентов через единый ContentProvider. Решает проблему множественных ContentProvider'ов от SDK, которые замедляют холодный старт приложения на 50-100мс каждый.

**Ключевая идея**: объединить все инициализаторы в один `InitializationProvider` с автоматическим разрешением зависимостей.

**1. Проблема: Множественные ContentProvider'ы**

```kotlin
// ❌ До: каждый SDK создаёт свой ContentProvider
class WorkManagerProvider : ContentProvider() {
    override fun onCreate(): Boolean {
        // +50-100ms к старту приложения
        WorkManager.initialize(context!!, Configuration.Builder().build())
        return true
    }
}
// Результат: 5 SDK = 250-500мс задержки
```

**2. Решение: Единый Initializer**

```kotlin
// ✅ После: один ContentProvider для всех SDK
class WorkManagerInitializer : Initializer<WorkManager> {
    override fun create(context: Context): WorkManager {
        WorkManager.initialize(context, Configuration.Builder().build())
        return WorkManager.getInstance(context)
    }
    override fun dependencies() = emptyList()
}
```

AndroidManifest.xml:
```xml
<provider
    android:name="androidx.startup.InitializationProvider"
    android:authorities="${applicationId}.androidx-startup">
    <meta-data android:name="com.example.WorkManagerInitializer"
               android:value="androidx.startup" />
</provider>
```

**3. Управление зависимостями**

```kotlin
// ✅ Автоматический порядок инициализации
class AnalyticsInitializer : Initializer<Analytics> {
    override fun create(context: Context) =
        Analytics.Builder(context)
            .setLogger(Logger.instance) // требует LoggerInitializer
            .build()

    override fun dependencies() = listOf(LoggerInitializer::class.java)
}
// Порядок выполнения: Logger → Analytics (автоматически)
```

**4. Отложенная инициализация**

```kotlin
// AndroidManifest: отключить автозапуск
<meta-data android:name="com.example.AnalyticsInitializer"
           tools:node="remove" />

// ✅ Ручная инициализация при необходимости
if (userLoggedIn()) {
    AppInitializer.getInstance(this)
        .initializeComponent(AnalyticsInitializer::class.java)
}
```

**Производительность**:
- До: 5 ContentProviders = ~450мс
- После: 1 InitializationProvider = ~280мс (-38%)

## Answer (EN)

**App Startup Library** is a Jetpack library that centralizes component initialization through a single ContentProvider. It solves the problem of multiple SDK ContentProviders that each add 50-100ms to cold start time.

**Core Concept**: Consolidate all initializers into one `InitializationProvider` with automatic dependency resolution.

**1. Problem: Multiple ContentProviders**

```kotlin
// ❌ Before: Each SDK creates its own ContentProvider
class WorkManagerProvider : ContentProvider() {
    override fun onCreate(): Boolean {
        // +50-100ms to app startup
        WorkManager.initialize(context!!, Configuration.Builder().build())
        return true
    }
}
// Result: 5 SDKs = 250-500ms delay
```

**2. Solution: Single Initializer**

```kotlin
// ✅ After: One ContentProvider for all SDKs
class WorkManagerInitializer : Initializer<WorkManager> {
    override fun create(context: Context): WorkManager {
        WorkManager.initialize(context, Configuration.Builder().build())
        return WorkManager.getInstance(context)
    }
    override fun dependencies() = emptyList()
}
```

AndroidManifest.xml:
```xml
<provider
    android:name="androidx.startup.InitializationProvider"
    android:authorities="${applicationId}.androidx-startup">
    <meta-data android:name="com.example.WorkManagerInitializer"
               android:value="androidx.startup" />
</provider>
```

**3. Dependency Management**

```kotlin
// ✅ Automatic initialization ordering
class AnalyticsInitializer : Initializer<Analytics> {
    override fun create(context: Context) =
        Analytics.Builder(context)
            .setLogger(Logger.instance) // requires LoggerInitializer
            .build()

    override fun dependencies() = listOf(LoggerInitializer::class.java)
}
// Execution order: Logger → Analytics (automatic)
```

**4. Lazy Initialization**

```kotlin
// AndroidManifest: disable auto-start
<meta-data android:name="com.example.AnalyticsInitializer"
           tools:node="remove" />

// ✅ Manual initialization when needed
if (userLoggedIn()) {
    AppInitializer.getInstance(this)
        .initializeComponent(AnalyticsInitializer::class.java)
}
```

**Performance**:
- Before: 5 ContentProviders = ~450ms
- After: 1 InitializationProvider = ~280ms (-38%)

## Follow-ups

- How do you detect circular dependencies in initializers?
- When should you avoid App Startup and use manual initialization in `Application.onCreate()`?
- How does App Startup interact with process lifecycle in multi-process apps?
- What are the trade-offs between automatic and lazy initialization?
- How do you test initialization order without launching the full app?

## References

- [App Startup Documentation](https://developer.android.com/topic/libraries/app-startup)
- [[c-content-provider]]

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] — Understanding ContentProvider basics
- [[q-android-project-parts--android--easy]] — AndroidManifest configuration

### Related (Same Level)
- [[q-app-start-types-android--android--medium]] — Cold vs warm vs hot start
- [[q-android-build-optimization--android--medium]] — Build-time optimizations
- [[q-android-performance-measurement-tools--android--medium]] — Profiling startup time

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]] — Deep dive into app initialization