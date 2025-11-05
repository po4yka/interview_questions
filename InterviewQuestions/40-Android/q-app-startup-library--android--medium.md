---
id: android-251
title: App Startup Library / Библиотека App Startup
aliases: [App Startup Library, Библиотека App Startup]
topic: android
subtopics:
  - app-startup
  - performance-startup
question_kind: android
difficulty: medium
original_language: ru
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related: []
created: 2025-10-15
updated: 2025-10-30
sources: []
tags: [android/app-startup, android/performance-startup, difficulty/medium, jetpack]
date created: Thursday, October 30th 2025, 11:43:07 am
date modified: Sunday, November 2nd 2025, 12:55:37 pm
---

# Вопрос (RU)
> Зачем нужна библиотека App Startup?

# Question (EN)
> What is the purpose of the App Startup library?

---

## Ответ (RU)

**App Startup** — библиотека Jetpack для централизации инициализации компонентов, объединяющая множественные ContentProvider'ы в один `InitializationProvider`, что сокращает холодный старт на 30-50% (~170мс при 5 SDK).

### Проблема: Множественные ContentProvider

Каждая библиотека традиционно создаёт свой ContentProvider для auto-init:

```kotlin
// ❌ Проблема: каждая библиотека добавляет ContentProvider
class WorkManagerProvider : ContentProvider() {
    override fun onCreate(): Boolean {
        WorkManager.initialize(context!!, Configuration.Builder().build())
        return true  // +50-100мс к старту
    }
}
```

**Накопительный эффект**: 5 SDK × 50-100мс = 250-500мс задержки при каждом запуске.

### Решение: Единый Initializer

```kotlin
// ✅ Один провайдер для всех компонентов
class WorkManagerInitializer : Initializer<WorkManager> {
    override fun create(context: Context): WorkManager {
        val config = Configuration.Builder().build()
        WorkManager.initialize(context, config)
        return WorkManager.getInstance(context)
    }

    override fun dependencies() = emptyList<Class<Initializer<*>>>()
}
```

**Регистрация в AndroidManifest.xml**:
```xml
<provider
    android:name="androidx.startup.InitializationProvider"
    android:authorities="${applicationId}.androidx-startup">
    <meta-data
        android:name="com.example.WorkManagerInitializer"
        android:value="androidx.startup" />
</provider>
```

### Управление Зависимостями

```kotlin
// ✅ Явный граф: Logger → Analytics
class AnalyticsInitializer : Initializer<Analytics> {
    override fun create(context: Context) =
        Analytics.Builder(context)
            .setLogger(AppInitializer.getInstance(context)
                .initializeComponent(LoggerInitializer::class.java))
            .build()

    override fun dependencies() = listOf(LoggerInitializer::class.java)
}
```

**Автоматическая топологическая сортировка** предотвращает циклические зависимости.

### Ленивая Инициализация

```kotlin
// ❌ AndroidManifest: отключить auto-init
<meta-data
    android:name="com.example.AnalyticsInitializer"
    tools:node="remove" />
```

```kotlin
// ✅ Запуск по условию
if (userLoggedIn) {
    AppInitializer.getInstance(context)
        .initializeComponent(AnalyticsInitializer::class.java)
}
```

**Результат**: 5 ContentProviders (~450мс) → 1 InitializationProvider (~280мс).

## Answer (EN)

**App Startup** is a Jetpack library for centralizing component initialization, consolidating multiple ContentProviders into a single `InitializationProvider`, reducing cold start time by 30-50% (~170ms with 5 SDKs).

### Problem: Multiple ContentProviders

Each library traditionally creates its own ContentProvider for auto-init:

```kotlin
// ❌ Problem: each library adds a ContentProvider
class WorkManagerProvider : ContentProvider() {
    override fun onCreate(): Boolean {
        WorkManager.initialize(context!!, Configuration.Builder().build())
        return true  // +50-100ms startup overhead
    }
}
```

**Cumulative effect**: 5 SDKs × 50-100ms = 250-500ms delay per launch.

### Solution: Unified Initializer

```kotlin
// ✅ Single provider for all components
class WorkManagerInitializer : Initializer<WorkManager> {
    override fun create(context: Context): WorkManager {
        val config = Configuration.Builder().build()
        WorkManager.initialize(context, config)
        return WorkManager.getInstance(context)
    }

    override fun dependencies() = emptyList<Class<Initializer<*>>>()
}
```

**AndroidManifest.xml registration**:
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
// ✅ Explicit graph: Logger → Analytics
class AnalyticsInitializer : Initializer<Analytics> {
    override fun create(context: Context) =
        Analytics.Builder(context)
            .setLogger(AppInitializer.getInstance(context)
                .initializeComponent(LoggerInitializer::class.java))
            .build()

    override fun dependencies() = listOf(LoggerInitializer::class.java)
}
```

**Automatic topological sorting** prevents circular dependencies.

### Lazy Initialization

```kotlin
// ❌ AndroidManifest: disable auto-init
<meta-data
    android:name="com.example.AnalyticsInitializer"
    tools:node="remove" />
```

```kotlin
// ✅ Conditional initialization
if (userLoggedIn) {
    AppInitializer.getInstance(context)
        .initializeComponent(AnalyticsInitializer::class.java)
}
```

**Impact**: 5 ContentProviders (~450ms) → 1 InitializationProvider (~280ms).

---

## Follow-ups

- How does App Startup detect and prevent circular dependencies?
- When should you use `Application.onCreate()` instead of App Startup?
- How does App Startup behave in multi-process applications?
- What are the trade-offs between eager and lazy initialization strategies?
- How can you verify initialization order in integration tests?

## References

- [[c-content-provider]] — ContentProvider lifecycle and performance
- [App Startup Library](https://developer.android.com/topic/libraries/app-startup)


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
 — Advanced startup optimization
