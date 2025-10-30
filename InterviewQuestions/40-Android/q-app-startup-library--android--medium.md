---
id: 20251006-100006
title: App Startup Library / Библиотека App Startup
aliases: ["App Startup Library", "Библиотека App Startup"]
topic: android
subtopics: [app-startup, performance-startup]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-app-start-types-android--android--medium, q-android-performance-measurement-tools--android--medium, q-android-build-optimization--android--medium]
created: 2025-10-15
updated: 2025-10-29
sources: []
tags: [android/app-startup, android/performance-startup, jetpack, difficulty/medium]
---
# Вопрос (RU)
> Зачем нужна библиотека App Startup?

# Question (EN)
> What is the purpose of the App Startup library?

## Ответ (RU)

**App Startup** — библиотека Jetpack, которая объединяет инициализацию компонентов в один `InitializationProvider` вместо множественных ContentProvider'ов, ускоряя холодный старт на 30-50%.

### Проблема

Каждый SDK традиционно создаёт свой ContentProvider, замедляя запуск на 50-100мс:

```kotlin
// ❌ Проблема: каждая библиотека добавляет ContentProvider
class WorkManagerProvider : ContentProvider() {
    override fun onCreate(): Boolean {
        // +50-100мс к старту
        WorkManager.initialize(context!!, Configuration.Builder().build())
        return true
    }
}
```

5 SDK = 250-500мс задержки при каждом холодном старте.

### Решение: Initializer

Один `InitializationProvider` для всех компонентов:

```kotlin
// ✅ Решение: один провайдер, явные зависимости
class WorkManagerInitializer : Initializer<WorkManager> {
    override fun create(context: Context): WorkManager {
        val config = Configuration.Builder().build()
        WorkManager.initialize(context, config)
        return WorkManager.getInstance(context)
    }

    override fun dependencies() = emptyList<Class<Initializer<*>>>()
}
```

AndroidManifest.xml:
```xml
<provider
    android:name="androidx.startup.InitializationProvider"
    android:authorities="${applicationId}.androidx-startup">
    <meta-data
        android:name="com.example.WorkManagerInitializer"
        android:value="androidx.startup" />
</provider>
```

### Управление зависимостями

```kotlin
// ✅ Автоматический порядок: Logger → Analytics
class AnalyticsInitializer : Initializer<Analytics> {
    override fun create(context: Context) =
        Analytics.Builder(context)
            .setLogger(AppInitializer.getInstance(context)
                .initializeComponent(LoggerInitializer::class.java))
            .build()

    override fun dependencies() = listOf(LoggerInitializer::class.java)
}
```

### Ленивая инициализация

```kotlin
// AndroidManifest: отключаем автозапуск
<meta-data
    android:name="com.example.AnalyticsInitializer"
    tools:node="remove" />
```

```kotlin
// ✅ Запуск по требованию
if (userLoggedIn) {
    AppInitializer.getInstance(context)
        .initializeComponent(AnalyticsInitializer::class.java)
}
```

**Эффект**: 5 ContentProviders (~450мс) → 1 InitializationProvider (~280мс).

## Answer (EN)

**App Startup** is a Jetpack library that consolidates component initialization into a single `InitializationProvider` instead of multiple ContentProviders, reducing cold start time by 30-50%.

### Problem

Each SDK traditionally creates its own ContentProvider, adding 50-100ms overhead:

```kotlin
// ❌ Problem: each library adds a ContentProvider
class WorkManagerProvider : ContentProvider() {
    override fun onCreate(): Boolean {
        // +50-100ms to startup
        WorkManager.initialize(context!!, Configuration.Builder().build())
        return true
    }
}
```

5 SDKs = 250-500ms delay on every cold start.

### Solution: Initializer

One `InitializationProvider` for all components:

```kotlin
// ✅ Solution: single provider, explicit dependencies
class WorkManagerInitializer : Initializer<WorkManager> {
    override fun create(context: Context): WorkManager {
        val config = Configuration.Builder().build()
        WorkManager.initialize(context, config)
        return WorkManager.getInstance(context)
    }

    override fun dependencies() = emptyList<Class<Initializer<*>>>()
}
```

AndroidManifest.xml:
```xml
<provider
    android:name="androidx.startup.InitializationProvider"
    android:authorities="${applicationId}.androidx-startup">
    <meta-data
        android:name="com.example.WorkManagerInitializer"
        android:value="androidx.startup" />
</provider>
```

### Dependency Management

```kotlin
// ✅ Automatic ordering: Logger → Analytics
class AnalyticsInitializer : Initializer<Analytics> {
    override fun create(context: Context) =
        Analytics.Builder(context)
            .setLogger(AppInitializer.getInstance(context)
                .initializeComponent(LoggerInitializer::class.java))
            .build()

    override fun dependencies() = listOf(LoggerInitializer::class.java)
}
```

### Lazy Initialization

```kotlin
// AndroidManifest: disable auto-start
<meta-data
    android:name="com.example.AnalyticsInitializer"
    tools:node="remove" />
```

```kotlin
// ✅ On-demand initialization
if (userLoggedIn) {
    AppInitializer.getInstance(context)
        .initializeComponent(AnalyticsInitializer::class.java)
}
```

**Impact**: 5 ContentProviders (~450ms) → 1 InitializationProvider (~280ms).

## Follow-ups

- How does App Startup detect and prevent circular dependencies?
- When should you use `Application.onCreate()` instead of App Startup?
- How does App Startup behave in multi-process applications?
- What are the trade-offs between eager and lazy initialization strategies?
- How can you verify initialization order in integration tests?

## References

- [[q-app-start-types-android--android--medium]] — Cold/warm/hot start mechanics
- [[c-content-provider]] — ContentProvider lifecycle
- https://developer.android.com/topic/libraries/app-startup

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] — ContentProvider fundamentals
- [[q-android-project-parts--android--easy]] — AndroidManifest structure

### Related (Same Level)
- [[q-app-start-types-android--android--medium]] — Cold vs warm vs hot start
- [[q-android-performance-measurement-tools--android--medium]] — Profiling startup time
- [[q-android-build-optimization--android--medium]] — Build optimizations

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]] — App initialization internals
- [[q-android-startup-best-practices--android--hard]] — Advanced startup optimization