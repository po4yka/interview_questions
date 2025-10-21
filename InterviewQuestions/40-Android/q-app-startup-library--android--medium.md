---
id: 20251006-100006
title: App Startup Library / Библиотека App Startup
aliases: [App Startup Library, Библиотека App Startup]
topic: android
subtopics: [app-startup, initialization, performance]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: reviewed
moc: moc-android
related: [q-app-start-types-android--android--medium, q-android-build-optimization--android--medium, q-android-performance-measurement-tools--android--medium]
created: 2025-10-15
updated: 2025-10-15
tags: [android/app-startup, android/initialization, android/performance, app-startup, initialization, performance, difficulty/medium]
---
# Question (EN)
> What is the Android App Startup library and how does it optimize app initialization?

# Вопрос (RU)
> Что такое библиотека Android App Startup и как она оптимизирует инициализацию приложения?

---

## Answer (EN)

**App Startup Library** centralizes component initialization through a single ContentProvider, replacing multiple SDK ContentProviders that slow cold start. Provides dependency management, lazy initialization, and controlled execution order.

**Initialization Theory:**
Each SDK ContentProvider adds 50-100ms to cold start. App Startup consolidates initialization into one provider with dependency graph resolution. Critical for apps with 5+ SDKs.

**1. Problem: Multiple ContentProviders**

```kotlin
// Before: Each SDK uses ContentProvider
class WorkManagerProvider : ContentProvider() {
    override fun onCreate(): Boolean {
        WorkManager.initialize(context!!, Configuration.Builder().build())
        return true
    }
}

class AnalyticsProvider : ContentProvider() {
    override fun onCreate(): Boolean {
        Analytics.initialize(context!!)
        return true
    }
}
// Result: 5+ ContentProviders = 250-500ms startup penalty
```

**2. Solution: Single InitializationProvider**

```kotlin
class WorkManagerInitializer : Initializer<WorkManager> {
    override fun create(context: Context): WorkManager {
        val config = Configuration.Builder().build()
        WorkManager.initialize(context, config)
        return WorkManager.getInstance(context)
    }

    override fun dependencies() = emptyList()
}

// AndroidManifest.xml
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

**3. Dependency Management**

```kotlin
class AnalyticsInitializer : Initializer<Analytics> {
    override fun create(context: Context): Analytics {
        return Analytics.Builder(context)
            .setLogger(Logger.instance) // Depends on Logger
            .build()
    }

    override fun dependencies() = listOf(LoggerInitializer::class.java)
}

class LoggerInitializer : Initializer<Logger> {
    override fun create(context: Context): Logger {
        return Logger.Builder(context).build()
    }

    override fun dependencies() = emptyList()
}
// Execution order: Logger → Analytics
```

**4. Lazy Initialization**

```kotlin
// Disable auto-init in AndroidManifest.xml
<meta-data
    android:name="com.example.LazyInitializer"
    tools:node="remove" />

// Manual initialization
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        if (userLoggedIn()) {
            AppInitializer.getInstance(this)
                .initializeComponent(AnalyticsInitializer::class.java)
        }
    }
}
```

**5. Performance Impact**

- **Before**: 5 ContentProviders = 450ms startup
- **After**: 1 InitializationProvider = 280ms startup (-38%)
- **Dependency resolution**: Automatic ordering prevents circular dependencies
- **Lazy loading**: Initialize only when needed

**6. Best Practices**

- Keep initializers lightweight (< 10ms each)
- Use dependencies for ordering, not manual delays
- Return actual component instances
- Avoid heavy I/O in initializers
- Test initialization order with dependency graph

## Ответ (RU)

**Библиотека App Startup** централизует инициализацию компонентов через один ContentProvider, заменяя множественные ContentProvider SDK, которые замедляют холодный старт. Обеспечивает управление зависимостями, ленивую инициализацию и контролируемый порядок выполнения.

**Теория инициализации:**
Каждый ContentProvider SDK добавляет 50-100мс к холодному старту. App Startup консолидирует инициализацию в один провайдер с разрешением графа зависимостей. Критично для приложений с 5+ SDK.

**1. Проблема: Множественные ContentProvider**

```kotlin
// Раньше: Каждый SDK использует ContentProvider
class WorkManagerProvider : ContentProvider() {
    override fun onCreate(): Boolean {
        WorkManager.initialize(context!!, Configuration.Builder().build())
        return true
    }
}

class AnalyticsProvider : ContentProvider() {
    override fun onCreate(): Boolean {
        Analytics.initialize(context!!)
        return true
    }
}
// Результат: 5+ ContentProvider = штраф 250-500мс на старт
```

**2. Решение: Единый InitializationProvider**

```kotlin
class WorkManagerInitializer : Initializer<WorkManager> {
    override fun create(context: Context): WorkManager {
        val config = Configuration.Builder().build()
        WorkManager.initialize(context, config)
        return WorkManager.getInstance(context)
    }

    override fun dependencies() = emptyList()
}

// AndroidManifest.xml
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

**3. Управление зависимостями**

```kotlin
class AnalyticsInitializer : Initializer<Analytics> {
    override fun create(context: Context): Analytics {
        return Analytics.Builder(context)
            .setLogger(Logger.instance) // Зависит от Logger
            .build()
    }

    override fun dependencies() = listOf(LoggerInitializer::class.java)
}

class LoggerInitializer : Initializer<Logger> {
    override fun create(context: Context): Logger {
        return Logger.Builder(context).build()
    }

    override fun dependencies() = emptyList()
}
// Порядок выполнения: Logger → Analytics
```

**4. Ленивая инициализация**

```kotlin
// Отключить авто-инициализацию в AndroidManifest.xml
<meta-data
    android:name="com.example.LazyInitializer"
    tools:node="remove" />

// Ручная инициализация
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        if (userLoggedIn()) {
            AppInitializer.getInstance(this)
                .initializeComponent(AnalyticsInitializer::class.java)
        }
    }
}
```

**5. Влияние на производительность**

- **Раньше**: 5 ContentProvider = 450мс старт
- **После**: 1 InitializationProvider = 280мс старт (-38%)
- **Разрешение зависимостей**: Автоматическое упорядочивание предотвращает циклические зависимости
- **Ленивая загрузка**: Инициализировать только при необходимости

**6. Лучшие практики**

- Держать инициализаторы легковесными (< 10мс каждый)
- Использовать зависимости для упорядочивания, не ручные задержки
- Возвращать реальные экземпляры компонентов
- Избегать тяжелого I/O в инициализаторах
- Тестировать порядок инициализации с графом зависимостей

---

## Follow-ups

- How do you measure App Startup performance impact?
- What's the difference between auto and manual initialization?
- How do you handle initialization failures?
- When should you avoid App Startup library?

## References

- [App Startup Documentation](https://developer.android.com/topic/libraries/app-startup)

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]]
- [[q-android-project-parts--android--easy]]

### Related (Same Level)
- [[q-app-start-types-android--android--medium]]
- [[q-android-build-optimization--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]]
