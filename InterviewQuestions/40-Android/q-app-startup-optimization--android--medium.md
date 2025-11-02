---
id: android-192
title: App Startup Optimization / Оптимизация запуска приложения
aliases: ["App Startup Optimization", "Оптимизация запуска приложения"]
topic: android
subtopics: [app-startup, performance-memory, performance-startup]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-app-startup, c-content-provider, c-lazy-initialization]
sources: []
created: 2025-10-15
updated: 2025-10-30
tags: [android/app-startup, android/performance-memory, android/performance-startup, difficulty/medium]
date created: Thursday, October 30th 2025, 11:43:03 am
date modified: Saturday, November 1st 2025, 5:43:37 pm
---

# Вопрос (RU)
> Как оптимизировать время запуска Android-приложения?

# Question (EN)
> How to optimize Android app startup time?

## Ответ (RU)

**Оптимизация запуска** сокращает время холодного/теплого/горячего старта через консолидацию ContentProvider, ленивую инициализацию, отложенное выполнение и измерения производительности.

### Ключевые Техники

**1. Консолидация ContentProvider**

Каждый ContentProvider добавляет 20-50ms к старту через IPC-вызовы. App Startup library объединяет инициализацию в один провайдер с разрешением зависимостей.

```kotlin
// ❌ BEFORE: Multiple providers (120ms overhead)
class AnalyticsProvider : ContentProvider() {
    override fun onCreate(): Boolean {
        Analytics.initialize(context!!)
        return true
    }
}

// ✅ AFTER: App Startup (25ms total)
class AnalyticsInitializer : Initializer<Analytics> {
    override fun create(context: Context) =
        Analytics.initialize(context)

    override fun dependencies() = emptyList()
}
```

**2. Ленивая инициализация**

Откладывает создание объектов до первого использования. Критично для опциональных фич (push-уведомления, аналитика).

```kotlin
class MyApplication : Application() {
    // ✅ Initialize on first access
    val analytics by lazy {
        AnalyticsService(this)
    }

    override fun onCreate() {
        super.onCreate()
        // ✅ Only critical services
        initCrashReporting()
    }
}
```

**3. Отложенное выполнение**

Некритичная инициализация выполняется асинхронно через WorkManager после отображения UI.

```kotlin
class DeferredInitializer : Initializer<Unit> {
    override fun create(context: Context) {
        val work = OneTimeWorkRequestBuilder<BackgroundInitWorker>()
            .setInitialDelay(5, TimeUnit.SECONDS)
            .build()

        WorkManager.getInstance(context)
            .enqueue(work)
    }
}
```

**4. Измерение производительности**

Trace API создает маркеры в Perfetto для анализа узких мест.

```kotlin
override fun onCreate() {
    Trace.beginSection("Application.onCreate")
    super.onCreate()

    Trace.beginSection("InitServices")
    initCrashReporting()
    Trace.endSection()

    Trace.endSection()
}
```

### Результаты

- Холодный старт: 1250ms → 520ms (-58%)
- ContentProviders: 8 → 1
- Оптимизации: App Startup (-175ms), lazy init (-260ms), deferred (-150ms)

### Лучшие Практики

- Измеряйте через Perfetto/systrace перед оптимизацией
- Инициализируйте только критичные сервисы в Application.onCreate()
- Избегайте синхронного I/O на главном потоке
- Тестируйте на слабых устройствах
- Цели: холодный < 500ms, теплый < 300ms, горячий < 100ms

## Answer (EN)

**Startup optimization** reduces cold/warm/hot start times through ContentProvider consolidation, lazy initialization, deferred execution, and performance measurement.

### Key Techniques

**1. ContentProvider Consolidation**

Each ContentProvider adds 20-50ms to startup via IPC calls. App Startup library consolidates initialization into single provider with dependency resolution.

```kotlin
// ❌ BEFORE: Multiple providers (120ms overhead)
class AnalyticsProvider : ContentProvider() {
    override fun onCreate(): Boolean {
        Analytics.initialize(context!!)
        return true
    }
}

// ✅ AFTER: App Startup (25ms total)
class AnalyticsInitializer : Initializer<Analytics> {
    override fun create(context: Context) =
        Analytics.initialize(context)

    override fun dependencies() = emptyList()
}
```

**2. Lazy Initialization**

Defers object creation until first access. Critical for optional features (push notifications, analytics).

```kotlin
class MyApplication : Application() {
    // ✅ Initialize on first access
    val analytics by lazy {
        AnalyticsService(this)
    }

    override fun onCreate() {
        super.onCreate()
        // ✅ Only critical services
        initCrashReporting()
    }
}
```

**3. Deferred Execution**

Non-critical initialization runs asynchronously via WorkManager after UI is shown.

```kotlin
class DeferredInitializer : Initializer<Unit> {
    override fun create(context: Context) {
        val work = OneTimeWorkRequestBuilder<BackgroundInitWorker>()
            .setInitialDelay(5, TimeUnit.SECONDS)
            .build()

        WorkManager.getInstance(context)
            .enqueue(work)
    }
}
```

**4. Performance Measurement**

Trace API creates markers in Perfetto for identifying bottlenecks.

```kotlin
override fun onCreate() {
    Trace.beginSection("Application.onCreate")
    super.onCreate()

    Trace.beginSection("InitServices")
    initCrashReporting()
    Trace.endSection()

    Trace.endSection()
}
```

### Results

- Cold start: 1250ms → 520ms (-58%)
- ContentProviders: 8 → 1
- Improvements: App Startup (-175ms), lazy init (-260ms), deferred (-150ms)

### Best Practices

- Measure with Perfetto/systrace before optimizing
- Initialize only critical services in Application.onCreate()
- Avoid synchronous I/O on main thread
- Test on low-end devices
- Targets: cold < 500ms, warm < 300ms, hot < 100ms

## Follow-ups

- How does App Startup library handle dependency graphs between initializers?
- What startup time targets are recommended for different app categories (games vs utilities)?
- How do you measure startup performance in production without instrumenting every user?
- What impact does Baseline Profile have on cold start times?
- When is it better to defer initialization vs make it lazy?

## References

**Concepts:**
- [[c-app-startup]]
- [[c-content-provider]]
- [[c-lazy-initialization]]
- [[c-application-class]]
- [[c-process-lifecycle]]

**Documentation:**
- [App Startup Library](https://developer.android.com/topic/libraries/app-startup)
- [Launch-time Performance](https://developer.android.com/topic/performance/vitals/launch-time)
- [Perfetto Tracing](https://perfetto.dev/)
- [Baseline Profiles](https://developer.android.com/topic/performance/baselineprofiles)

## Related Questions

### Prerequisites
- [[q-app-start-types-android--android--medium]]
- [[q-android-app-components--android--easy]]

### Related
- [[q-app-startup-library--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]
- [[q-baseline-profiles-android--android--medium]]

### Advanced
- [[q-android-runtime-internals--android--hard]]
- [[q-android-process-optimization--android--hard]]