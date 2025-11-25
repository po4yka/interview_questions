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
status: draft
moc: moc-android
related: [q-android-app-components--android--easy]
created: 2024-10-15
updated: 2024-11-10
sources: []
tags: [android/app-startup, android/performance-startup, difficulty/medium, jetpack]

date created: Saturday, November 1st 2025, 1:04:12 pm
date modified: Tuesday, November 25th 2025, 8:54:02 pm
---

# Вопрос (RU)
> Зачем нужна библиотека App Startup?

# Question (EN)
> What is the purpose of the App Startup library?

---

## Ответ (RU)

**App Startup** — библиотека Jetpack для централизации инициализации компонентов. Она предоставляет единый `InitializationProvider`, который по meta-data в манифесте запускает `Initializer`-ы и уменьшает накладные расходы на инициализацию по сравнению с множественными `ContentProvider` при корректном использовании (эффект зависит от устройства и выполняемой работы).

### Проблема: Множественные `ContentProvider`

Исторически каждая библиотека могла создавать свой `ContentProvider` для auto-init, что добавляет работу в фазу запуска процесса:

```kotlin
// ❌ Проблема: каждая библиотека добавляет ContentProvider
class WorkManagerProvider : ContentProvider() {
    override fun onCreate(): Boolean {
        WorkManager.initialize(context!!, Configuration.Builder().build())
        return true  // потенциальные десятки миллисекунд к старту в зависимости от выполняемой работы
    }
}
```

**Накопительный эффект**: несколько тяжёлых `ContentProvider` подряд могут заметно увеличить время холодного старта.

### Решение: Единый Initializer

С App Startup инициализация библиотек оформляется через `Initializer`, а запуском управляет единый `InitializationProvider`.

```kotlin
// ✅ Инициализатор для WorkManager
class WorkManagerInitializer : Initializer<WorkManager> {
    override fun create(context: Context): WorkManager {
        val config = Configuration.Builder().build()
        WorkManager.initialize(context, config)
        return WorkManager.getInstance(context)
    }

    override fun dependencies() = emptyList<Class<Initializer<*>>>()
}
```

**Регистрация в AndroidManifest.xml** (в приложении или библиотеке):
```xml
<provider
    android:name="androidx.startup.InitializationProvider"
    android:authorities="${applicationId}.androidx-startup"
    android:exported="false"
    tools:node="merge">
    <meta-data
        android:name="com.example.WorkManagerInitializer"
        android:value="androidx.startup" />
</provider>
```

`InitializationProvider` при старте процесса читает meta-data и вызывает указанные `Initializer`-ы, заменяя собой множество специальных провайдеров и давая более явный контроль над порядком и стратегией инициализации.

### Управление Зависимостями

```kotlin
// ✅ Явный граф: Logger → Analytics
class AnalyticsInitializer : Initializer<Analytics> {
    override fun create(context: Context) =
        Analytics.Builder(context)
            .setLogger(
                AppInitializer.getInstance(context)
                    .initializeComponent(LoggerInitializer::class.java)
            )
            .build()

    override fun dependencies() = listOf(LoggerInitializer::class.java)
}
```

App Startup строит порядок выполнения инициализаторов с помощью топологической сортировки на основе `dependencies()`. При наличии циклической зависимости будет выброшено исключение во время инициализации (цикл не «предотвращается» автоматически, а детектируется как ошибка).

### Ленивая Инициализация

В приложении можно отключить auto-init конкретного инициализатора, прописанного в библиотеке, и запускать его вручную.

```xml
<!-- ❌ В манифесте приложения: отключаем auto-init библиотеки -->
<application
    xmlns:tools="http://schemas.android.com/tools"
    ...>

    <meta-data
        android:name="com.example.AnalyticsInitializer"
        tools:node="remove" />

</application>
```

```kotlin
// ✅ Запуск по условию
if (userLoggedIn) {
    AppInitializer.getInstance(context)
        .initializeComponent(AnalyticsInitializer::class.java)
}
```

**Результат**: вместо множества тяжёлых провайдеров и неявного порядка инициализации вы получаете единый механизм, явный граф зависимостей и возможность откладывать тяжёлую инициализацию, что в типичных сценариях улучшает время запуска.

## Answer (EN)

**App Startup** is a Jetpack library for centralizing component initialization. It provides a single `InitializationProvider` that reads manifest meta-data and runs `Initializer` implementations, reducing initialization overhead compared to multiple custom `ContentProvider`s when used correctly (the actual impact depends on device and work performed).

### Problem: Multiple ContentProviders

Historically, each library could declare its own `ContentProvider` for auto-init, adding work to process startup:

```kotlin
// ❌ Problem: each library adds a ContentProvider
class WorkManagerProvider : ContentProvider() {
    override fun onCreate(): Boolean {
        WorkManager.initialize(context!!, Configuration.Builder().build())
        return true  // can add tens of ms to startup depending on the work done
    }
}
```

**Cumulative effect**: several heavy `ContentProvider`s in sequence can noticeably increase cold start time.

### Solution: Unified Initializer

With App Startup, library initialization is expressed via `Initializer`s, and a single `InitializationProvider` orchestrates them.

```kotlin
// ✅ Initializer for WorkManager
class WorkManagerInitializer : Initializer<WorkManager> {
    override fun create(context: Context): WorkManager {
        val config = Configuration.Builder().build()
        WorkManager.initialize(context, config)
        return WorkManager.getInstance(context)
    }

    override fun dependencies() = emptyList<Class<Initializer<*>>>()
}
```

**AndroidManifest.xml registration** (in the app or library):
```xml
<provider
    android:name="androidx.startup.InitializationProvider"
    android:authorities="${applicationId}.androidx-startup"
    android:exported="false"
    tools:node="merge">
    <meta-data
        android:name="com.example.WorkManagerInitializer"
        android:value="androidx.startup" />
</provider>
```

`InitializationProvider` reads the meta-data at process start and invokes the specified `Initializer`s, replacing many custom providers and giving explicit control over order and strategy.

### Dependency Management

```kotlin
// ✅ Explicit graph: Logger → Analytics
class AnalyticsInitializer : Initializer<Analytics> {
    override fun create(context: Context) =
        Analytics.Builder(context)
            .setLogger(
                AppInitializer.getInstance(context)
                    .initializeComponent(LoggerInitializer::class.java)
            )
            .build()

    override fun dependencies() = listOf(LoggerInitializer::class.java)
}
```

App Startup computes the execution order using topological sorting based on `dependencies()`. If there is a cyclic dependency, it throws an exception during initialization (cycles are detected and reported as errors, not silently "prevented").

### Lazy Initialization

In the app manifest you can disable auto-init for a library-provided initializer and trigger it manually.

```xml
<!-- ❌ In the app manifest: disable library auto-init -->
<application
    xmlns:tools="http://schemas.android.com/tools"
    ...>

    <meta-data
        android:name="com.example.AnalyticsInitializer"
        tools:node="remove" />

</application>
```

```kotlin
// ✅ Conditional initialization
if (userLoggedIn) {
    AppInitializer.getInstance(context)
        .initializeComponent(AnalyticsInitializer::class.java)
}
```

**Impact**: instead of multiple heavy providers and implicit ordering, you get a single mechanism, an explicit dependency graph, and the ability to defer heavy initialization, which typically improves startup performance.

---

## Дополнительные Вопросы (RU)

- Как App Startup обнаруживает и обрабатывает циклические зависимости?
- В каких случаях лучше использовать `Application.onCreate()` вместо App Startup?
- Как App Startup ведет себя в многопроцессных приложениях?
- Каковы компромиссы между жадной и ленивой стратегиями инициализации?
- Как можно проверить порядок инициализации в интеграционных тестах?

## Follow-ups

- How does App Startup detect and handle circular dependencies?
- When should you use `Application.onCreate()` instead of App Startup?
- How does App Startup behave in multi-process applications?
- What are the trade-offs between eager and lazy initialization strategies?
- How can you verify initialization order in integration tests?

## Ссылки (RU)

- [[c-content-provider]] — жизненный цикл и производительность `ContentProvider`
- Официальная документация App Startup: https://developer.android.com/topic/libraries/app-startup

## References

- [[c-content-provider]] — `ContentProvider` lifecycle and performance
- [App Startup Library](https://developer.android.com/topic/libraries/app-startup)

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-android-app-components--android--easy]] — основы `ContentProvider`
- [[q-android-project-parts--android--easy]] — структура AndroidManifest

### Похожие (того Же уровня)
- [[q-app-start-types-android--android--medium]] — холодный, тёплый и горячий старт
- [[q-android-performance-measurement-tools--android--medium]] — профилирование времени запуска
- [[q-android-build-optimization--android--medium]] — оптимизации сборки

### Продвинутые (сложнее)
- [[q-android-runtime-internals--android--hard]] — внутренности инициализации приложений
- Продвинутая оптимизация старта

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] — `ContentProvider` fundamentals
- [[q-android-project-parts--android--easy]] — AndroidManifest structure

### Related (Same Level)
- [[q-app-start-types-android--android--medium]] — Cold vs warm vs hot start
- [[q-android-performance-measurement-tools--android--medium]] — Profiling startup time
- [[q-android-build-optimization--android--medium]] — Build optimizations

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]] — App initialization internals
- Advanced startup optimization
