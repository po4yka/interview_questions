---
id: android-075
title: "Leakcanary Library / Библиотека LeakCanary"
aliases: ["Leakcanary Library", "Библиотека LeakCanary"]
topic: android
subtopics: [performance-memory, profiling]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
created: 2025-10-13
updated: 2025-01-27
tags: [android/performance-memory, android/profiling, debugging-tools, difficulty/easy, leakcanary, memory-leaks]
moc: moc-android
related: [c-memory-management]
sources: []

---

# Вопрос (RU)

> Какая библиотека используется для нахождения утечек памяти в Android?

# Question (EN)

> What library is used for finding memory leaks in Android?

---

## Ответ (RU)

**LeakCanary** от Square — стандартный инструмент для автоматического обнаружения утечек памяти в Android приложениях.

**Основные возможности:**

- Автоматически отслеживает утечки `Activity`, `Fragment`, `ViewModel`
- Работает "из коробки" без конфигурации
- Визуализирует цепочки удержания объектов
- Не влияет на production (только debug-сборки)

**Подключение:**

```kotlin
// build.gradle (app)
dependencies {
    debugImplementation("com.squareup.leakcanary:leakcanary-android")  // ✅ Only debug builds
}
```

**Принцип работы:**

LeakCanary регистрирует lifecycle callbacks и отслеживает объекты после их уничтожения. Если объект не собран GC через 5 секунд — выполняется heap dump и анализ.

```kotlin
// LeakCanary автоматически следит за Activity
override fun onActivityDestroyed(activity: Activity) {
    AppWatcher.objectWatcher.watch(
        activity,
        "Activity#onDestroy() called"
    )
}
```

**Пример утечки:**

```kotlin
companion object {
    var activity: Activity? = null  // ❌ Static reference — leak!
}

class MainActivity : AppCompatActivity() {
    init {
        activity = this  // ❌ Activity won't be GC'd
    }
}
```

**Отслеживание кастомных объектов:**

```kotlin
class MyViewModel : ViewModel() {
    init {
        AppWatcher.objectWatcher.watch(
            watchedObject = this,
            description = "ViewModel cleared"
        )
    }
}
```

**Альтернативы:**

-  — ручной анализ через Android Studio
- Perfetto — системная трассировка с полной картиной производительности
- MAT (Eclipse Memory Analyzer) — детальный анализ heap dump

---

## Answer (EN)

**LeakCanary** by Square is the standard tool for automatically detecting memory leaks in Android applications.

**Key features:**

- Automatically tracks `Activity`, `Fragment`, `ViewModel` leaks
- Zero configuration — works out of the box
- Visualizes object retention chains
- No production impact (debug builds only)

**Setup:**

```kotlin
// build.gradle (app)
dependencies {
    debugImplementation("com.squareup.leakcanary:leakcanary-android")  // ✅ Only debug builds
}
```

**How it works:**

LeakCanary registers lifecycle callbacks and watches objects after destruction. If an object isn't collected by GC after 5 seconds — heap dump is performed and analyzed.

```kotlin
// LeakCanary automatically watches Activity
override fun onActivityDestroyed(activity: Activity) {
    AppWatcher.objectWatcher.watch(
        activity,
        "Activity#onDestroy() called"
    )
}
```

**Leak example:**

```kotlin
companion object {
    var activity: Activity? = null  // ❌ Static reference — leak!
}

class MainActivity : AppCompatActivity() {
    init {
        activity = this  // ❌ Activity won't be GC'd
    }
}
```

**Watch custom objects:**

```kotlin
class MyViewModel : ViewModel() {
    init {
        AppWatcher.objectWatcher.watch(
            watchedObject = this,
            description = "ViewModel cleared"
        )
    }
}
```

**Alternatives:**

-  — manual analysis via Android Studio
- Perfetto — system tracing with full performance picture
- MAT (Eclipse Memory Analyzer) — detailed heap dump analysis

---

## Follow-ups

- How does LeakCanary distinguish between expected retained objects and actual leaks?
- What strategies prevent common leak patterns (static `Activity` references, inner class listeners)?
- How do you interpret leak traces to identify the root cause in complex object graphs?

## References

- [[c-memory-management]] — Android memory management fundamentals
- [[c-garbage-collection]] — GC behavior and object lifecycle
- https://square.github.io/leakcanary/ — Official LeakCanary documentation

## Related Questions

### Prerequisites
- [[q-memory-leaks-definition--android--easy]] - Understanding memory leaks basics
- [[q-what-is-the-main-application-execution-thread--android--easy]] - Main thread and memory management
- [[q-android-async-primitives--android--easy]] - Basic async tools in Android

### Related (Same Level)
- [[q-android-performance-measurement-tools--android--medium]] - Tools for performance profiling
- [[q-memory-leak-detection--android--medium]] - Memory leak detection strategies
- [[q-optimize-memory-usage-android--android--medium]] - Memory optimization techniques

### Advanced (Harder)
- [[q-leakcanary-detection-mechanism--android--medium]] - How LeakCanary detects leaks
- [[q-leakcanary-heap-dump-analysis--android--medium]] - Analyzing heap dumps in detail
- [[q-memory-leak-vs-oom-android--android--medium]] - Memory leaks vs OOM errors
