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
updated: 2025-11-10
tags: [android/performance-memory, android/profiling, debugging-tools, difficulty/easy, leakcanary, memory-leaks]
moc: moc-android
related: [c-garbage-collection, c-memory-management]
sources: []

date created: Saturday, November 1st 2025, 1:25:02 pm
date modified: Tuesday, November 25th 2025, 8:53:59 pm
---

# Вопрос (RU)

> Какая библиотека используется для нахождения утечек памяти в Android?

# Question (EN)

> What library is used for finding memory leaks in Android?

---

## Ответ (RU)

**LeakCanary** от Square — де-факто стандартный и широко используемый инструмент для автоматического обнаружения утечек памяти в Android-приложениях во время разработки.

**Основные возможности:**

- Автоматически отслеживает утечки `Activity`, `Fragment`, `ViewModel` и других Android-компонентов
- Работает "из коробки" с минимальной конфигурацией
- Визуализирует цепочки удержания объектов (retention path)
- Обычно подключается только в debug-сборках и не влияет на production при использовании `debugImplementation`

**Подключение:**

```kotlin
// build.gradle (app)
dependencies {
    debugImplementation("com.squareup.leakcanary:leakcanary-android")  // ✅ Только debug-сборки по умолчанию
}
```

**Принцип работы (упрощённо):**

LeakCanary регистрирует lifecycle callbacks и отслеживает объекты после того, как их жизненный цикл завершён (например, `Activity` после `onDestroy`). Если объект остаётся в памяти дольше заданного времени ожидания и не собирается GC, LeakCanary инициирует heap dump и выполняет его анализ, чтобы построить цепочку удержания.

```kotlin
// Упрощённый пример того, как объект может быть передан в LeakCanary
AppWatcher.objectWatcher.watch(
    activity,
    "Activity#onDestroy() called"
)
```

(В реальном проекте LeakCanary делает это автоматически; вручную вы обычно не переопределяете колбэки для базовых компонентов.)

**Пример утечки:**

```kotlin
class MainActivity : AppCompatActivity() {

    companion object {
        var activity: Activity? = null  // ❌ Статическая ссылка удерживает Activity
    }

    init {
        activity = this  // ❌ Activity не будет собрана GC
    }
}
```

**Отслеживание кастомных объектов (пример):**

`AppWatcher.objectWatcher.watch(...)` следует вызывать в тот момент, когда объект ДОЛЖЕН стать освобождаемым. Например, для собственных listener-объектов или менеджеров, которые вы вручную "отвязываете":

```kotlin
class MyLeakProneManager {
    fun clear() {
        // ... отписки и очистка ссылок ...
        AppWatcher.objectWatcher.watch(
            watchedObject = this,
            description = "MyLeakProneManager should be cleared now"
        )
    }
}
```

**Альтернативы / смежные инструменты:**

- Профилировщик памяти Android Studio (Memory Profiler) — ручной анализ памяти
- Perfetto — системная трассировка и анализ производительности, включая память
- MAT (Eclipse Memory Analyzer) — детальный анализ heap dump

---

## Answer (EN)

**LeakCanary** by Square is the de facto standard and widely used library for automatically detecting memory leaks in Android apps during development.

**Key features:**

- Automatically tracks leaks for `Activity`, `Fragment`, `ViewModel`, and other Android components
- Works out of the box with minimal configuration
- Visualizes object retention chains (retention paths)
- Typically added only to debug builds via `debugImplementation`, so it does not affect production in that setup

**Setup:**

```kotlin
// build.gradle (app)
dependencies {
    debugImplementation("com.squareup.leakcanary:leakcanary-android")  // ✅ Debug-only by default
}
```

**How it works (simplified):**

LeakCanary registers lifecycle callbacks and watches objects after their lifecycle is finished (e.g., an `Activity` after `onDestroy`). If an object remains in memory longer than the configured wait time and is not collected by GC, LeakCanary triggers a heap dump and analyzes it to build the retention path.

```kotlin
// Simplified example of passing an object to LeakCanary
AppWatcher.objectWatcher.watch(
    activity,
    "Activity#onDestroy() called"
)
```

(In real usage, LeakCanary handles this automatically; you usually don't override lifecycle callbacks for core components just for LeakCanary.)

**Leak example:**

```kotlin
class MainActivity : AppCompatActivity() {

    companion object {
        var activity: Activity? = null  // ❌ Static reference holds onto Activity
    }

    init {
        activity = this  // ❌ Activity won't be GC'd
    }
}
```

**Watch custom objects (example):**

You should call `AppWatcher.objectWatcher.watch(...)` at the moment when the object is expected to become unreachable. For example, for your own managers or listeners that you explicitly clear:

```kotlin
class MyLeakProneManager {
    fun clear() {
        // ... unsubscribe and clear references ...
        AppWatcher.objectWatcher.watch(
            watchedObject = this,
            description = "MyLeakProneManager should be cleared now"
        )
    }
}
```

**Alternatives / related tools:**

- Android Studio Memory Profiler — manual memory analysis
- Perfetto — system tracing and performance analysis, including memory
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
