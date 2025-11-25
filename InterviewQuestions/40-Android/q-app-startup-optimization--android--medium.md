---
id: android-192
title: App Startup Optimization / Оптимизация запуска приложения
aliases: [App Startup Optimization, Оптимизация запуска приложения]
topic: android
subtopics:
  - app-startup
  - performance-memory
  - performance-startup
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-content-provider
  - q-app-size-optimization--android--medium
  - q-app-startup-library--android--medium
  - q-optimize-memory-usage-android--android--medium
sources: []
created: 2025-10-15
updated: 2025-11-10
tags: [android/app-startup, android/performance-memory, android/performance-startup, difficulty/medium]

date created: Saturday, November 1st 2025, 1:04:13 pm
date modified: Tuesday, November 25th 2025, 8:54:02 pm
---

# Вопрос (RU)
> Как оптимизировать время запуска Android-приложения?

# Question (EN)
> How to optimize Android app startup time?

## Ответ (RU)

**Оптимизация запуска** сокращает время холодного/теплого/горячего старта за счет снижения работы в ранних точках (`Application`.onCreate, `ContentProvider`.onCreate), консолидации `ContentProvider`, ленивой инициализации, отложенного выполнения и точных измерений производительности.

### Ключевые Техники

**1. Консолидация `ContentProvider`**

Каждый `ContentProvider` инициализируется до `Application`.onCreate и добавляет накладные расходы (создание, возможные IPC, работа в onCreate). AndroidX App Startup позволяет заменить "инициализационные" провайдеры декларативными Initializer-классами и, как правило, сократить лишние `ContentProvider` при сохранении разрешения зависимостей.

```kotlin
// ❌ BEFORE: Multiple providers doing work in onCreate
class AnalyticsProvider : ContentProvider() {
    override fun onCreate(): Boolean {
        Analytics.initialize(context!!)
        return true
    }
}

// ✅ AFTER: App Startup Initializer
class AnalyticsInitializer : Initializer<Analytics> {
    override fun create(context: Context): Analytics =
        Analytics.initialize(context)

    override fun dependencies(): List<Class<out Initializer<*>>> = emptyList()
}
```

**2. Ленивая инициализация**

Откладывает создание объектов до первого использования. Особенно полезно для опциональных фич (push-уведомления, аналитика), которые не нужны сразу при запуске.

```kotlin
class MyApplication : Application() {
    // ✅ Инициализация при первом обращении
    val analytics: AnalyticsService by lazy {
        AnalyticsService(this)
    }

    override fun onCreate() {
        super.onCreate()
        // ✅ Только критичные сервисы
        initCrashReporting()
    }
}
```

**3. Отложенное выполнение**

Некритичная инициализация выносится из горячего пути запуска и выполняется асинхронно (через WorkManager, корутины, Handler и т.п.) уже после первичного показа UI или в удобный момент жизненного цикла.

```kotlin
class DeferredInitializer : Initializer<Unit> {
    override fun create(context: Context) {
        val work = OneTimeWorkRequestBuilder<BackgroundInitWorker>()
            .setInitialDelay(5, TimeUnit.SECONDS)
            .build()

        WorkManager.getInstance(context)
            .enqueue(work)
    }

    override fun dependencies(): List<Class<out Initializer<*>>> = emptyList()
}
```

**4. Измерение производительности**

Trace API создает секции, которые можно анализировать в Perfetto / System Tracing для поиска узких мест. Важно корректно спаривать beginSection/endSection.

```kotlin
override fun onCreate() {
    Trace.beginSection("Application.onCreate")
    try {
        super.onCreate()

        Trace.beginSection("InitServices")
        initCrashReporting()
        Trace.endSection()
    } finally {
        Trace.endSection()
    }
}
```

### Результаты (пример)

Пример эффекта оптимизаций в реальном проекте (значения не универсальны):

- Холодный старт: 1250ms → 520ms (~-58%)
- ContentProviders: 8 → 1
- Основной вклад: сокращение работы в `ContentProvider`, ленивая инициализация, отложенные задачи

### Лучшие Практики

- Сначала измеряйте через Perfetto/System Tracing/Android Vitals, затем оптимизируйте
- Инициализируйте только критичные зависимости UI и навигации в `Application`.onCreate()
- Избегайте синхронного I/O и тяжёлых операций на главном потоке
- Тестируйте на слабых устройствах и реальных условиях
- Цели по времени старта подбирайте под тип приложения и устройства; для типичных утилит и контент-приложений можно ориентироваться на субсекундный холодный старт

## Answer (EN)

**Startup optimization** reduces cold/warm/hot start times by minimizing work in early entry points (`Application`.onCreate, `ContentProvider`.onCreate), consolidating ContentProviders, using lazy initialization, deferring non-critical work, and accurately measuring performance.

### Key Techniques

**1. `ContentProvider` Consolidation**

Each `ContentProvider` is initialized before `Application`.onCreate and adds overhead (instantiation, possible IPC, work in onCreate). The AndroidX App Startup library lets you replace "initializer" providers with Initializer classes and often reduce the number of ContentProviders while preserving dependency resolution.

```kotlin
// ❌ BEFORE: Multiple providers doing work in onCreate
class AnalyticsProvider : ContentProvider() {
    override fun onCreate(): Boolean {
        Analytics.initialize(context!!)
        return true
    }
}

// ✅ AFTER: App Startup Initializer
class AnalyticsInitializer : Initializer<Analytics> {
    override fun create(context: Context): Analytics =
        Analytics.initialize(context)

    override fun dependencies(): List<Class<out Initializer<*>>> = emptyList()
}
```

**2. Lazy Initialization**

Defers object creation until first access. Especially useful for optional features (push notifications, analytics) that are not needed during initial launch.

```kotlin
class MyApplication : Application() {
    // ✅ Initialize on first access
    val analytics: AnalyticsService by lazy {
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

Moves non-critical work off the hot startup path and runs it asynchronously (via WorkManager, coroutines, Handler, etc.) after the initial UI is presented or at an appropriate lifecycle point.

```kotlin
class DeferredInitializer : Initializer<Unit> {
    override fun create(context: Context) {
        val work = OneTimeWorkRequestBuilder<BackgroundInitWorker>()
            .setInitialDelay(5, TimeUnit.SECONDS)
            .build()

        WorkManager.getInstance(context)
            .enqueue(work)
    }

    override fun dependencies(): List<Class<out Initializer<*>>> = emptyList()
}
```

**4. Performance Measurement**

The Trace API creates sections that can be inspected in Perfetto / System Tracing to identify bottlenecks. Ensure beginSection/endSection calls are properly paired.

```kotlin
override fun onCreate() {
    Trace.beginSection("Application.onCreate")
    try {
        super.onCreate()

        Trace.beginSection("InitServices")
        initCrashReporting()
        Trace.endSection()
    } finally {
        Trace.endSection()
    }
}
```

### Results (example)

An example of optimization impact in a real project (values are not universal):

- Cold start: 1250ms → 520ms (~-58%)
- ContentProviders: 8 → 1
- Main contributors: reduced work in ContentProviders, lazy initialization, deferred tasks

### Best Practices

- Measure with Perfetto/System Tracing/Android Vitals before optimizing
- Initialize only critical UI and navigation dependencies in `Application`.onCreate()
- Avoid synchronous I/O and heavy operations on the main thread
- Test on low-end devices and realistic conditions
- `Set` startup time targets based on app category and device profile; for typical utility/content apps, aim for sub-second cold start where feasible

## Дополнительные Вопросы (RU)

- Как библиотека App Startup обрабатывает граф зависимостей между инициализаторами?
- Какие целевые значения времени старта рекомендуются для разных категорий приложений (игры vs утилиты)?
- Как измерять производительность запуска в продакшене, не инструментируя каждого пользователя?
- Какое влияние Baseline Profile оказывает на время холодного старта?
- В каких случаях лучше отложить инициализацию, а в каких сделать ее ленивой?

## Follow-ups

- How does App Startup library handle dependency graphs between initializers?
- What startup time targets are recommended for different app categories (games vs utilities)?
- How do you measure startup performance in production without instrumenting every user?
- What impact does Baseline Profile have on cold start times?
- When is it better to defer initialization vs make it lazy?

## Ссылки (RU)

**Концепции:**
- [[c-content-provider]]

**Документация:**
- [App Startup Library](https://developer.android.com/topic/libraries/app-startup)
- [Launch-time Performance](https://developer.android.com/topic/performance/vitals/launch-time)
- [Perfetto Tracing](https://perfetto.dev/)
- [Baseline Profiles](https://developer.android.com/topic/performance/baselineprofiles)

## References

**Concepts:**
- [[c-content-provider]]

**Documentation:**
- [App Startup Library](https://developer.android.com/topic/libraries/app-startup)
- [Launch-time Performance](https://developer.android.com/topic/performance/vitals/launch-time)
- [Perfetto Tracing](https://perfetto.dev/)
- [Baseline Profiles](https://developer.android.com/topic/performance/baselineprofiles)

## Связанные Вопросы (RU)

### Предпосылки
- [[q-app-start-types-android--android--medium]]
- [[q-android-app-components--android--easy]]

### Похожие
- [[q-app-startup-library--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]
- [[q-baseline-profiles-android--android--medium]]

### Продвинутые
- [[q-android-runtime-internals--android--hard]]

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
