---
id: 20251012-122711
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
tags: [android/performance-memory, android/profiling, leakcanary, memory-leaks, debugging-tools, difficulty/easy]
moc: moc-android
related: [c-memory-management, q-test-doubles-dependency-injection--testing--medium, q-how-vsync-and-recomposition-events-are-related--android--hard]
sources: []
date created: Monday, October 27th 2025, 3:57:39 pm
date modified: Thursday, October 30th 2025, 3:12:27 pm
---

# Вопрос (RU)

> Какая библиотека используется для нахождения утечек памяти в Android?

# Question (EN)

> What library is used for finding memory leaks in Android?

---

## Ответ (RU)

**LeakCanary** от Square — стандартный инструмент для автоматического обнаружения утечек памяти в Android приложениях.

**Основные возможности:**

- Автоматически отслеживает утечки Activity, Fragment, ViewModel
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

- [[c-memory-profiler]] — ручной анализ через Android Studio
- Perfetto — системная трассировка с полной картиной производительности
- MAT (Eclipse Memory Analyzer) — детальный анализ heap dump

---

## Answer (EN)

**LeakCanary** by Square is the standard tool for automatically detecting memory leaks in Android applications.

**Key features:**

- Automatically tracks Activity, Fragment, ViewModel leaks
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

- [[c-memory-profiler]] — manual analysis via Android Studio
- Perfetto — system tracing with full performance picture
- MAT (Eclipse Memory Analyzer) — detailed heap dump analysis

---

## Follow-ups

- How does LeakCanary distinguish between expected retained objects and actual leaks?
- What strategies prevent common leak patterns (static Activity references, inner class listeners)?
- How do you interpret leak traces to identify the root cause in complex object graphs?

## References

- [[c-memory-management]] — Android memory management fundamentals
- [[c-garbage-collection]] — GC behavior and object lifecycle
- https://square.github.io/leakcanary/ — Official LeakCanary documentation

## Related Questions

### Prerequisites
- [[q-android-lifecycle-basics--android--easy]] — Understanding component lifecycle
- [[q-garbage-collection-basics--android--easy]] — GC fundamentals

### Related
- [[q-memory-profiler-usage--android--medium]] — Manual memory analysis tools
- [[q-common-memory-leaks--android--medium]] — Typical leak patterns

### Advanced
- [[q-heap-dump-analysis--android--hard]] — Deep heap dump investigation
