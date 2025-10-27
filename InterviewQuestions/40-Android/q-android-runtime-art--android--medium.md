---
id: 20251012-122770
title: Android Runtime (ART) / Android Runtime (ART)
aliases: ["Android Runtime (ART)", "Android Runtime (ART)", "ART", "АРТ"]
topic: android
subtopics: [performance-memory, processes]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related:
  - q-android-app-lag-analysis--android--medium
  - q-android-build-optimization--android--medium
  - q-android-performance-measurement-tools--android--medium
created: 2025-10-15
updated: 2025-10-27
tags: [android/performance-memory, android/processes, difficulty/medium]
sources: []
---
# Вопрос (RU)
> Что такое Android Runtime (ART)?

# Question (EN)
> What is Android Runtime (ART)?

## Ответ (RU)

**Android Runtime (ART)** — среда выполнения приложений Android, ответственная за запуск кода, управление памятью и взаимодействие с ОС. ART заменил Dalvik VM начиная с Android 5.0 и использует **AOT (Ahead-of-Time) компиляцию** для повышения производительности. См. также [[c-memory-management]].

**Ключевые особенности ART:**

1. **Гибридная компиляция (Android 7.0+)**
   - Установка: базовая AOT-компиляция (быстро)
   - Первые запуски: JIT-компиляция "горячих" путей кода
   - Фоновая оптимизация: полная AOT-компиляция

2. **Улучшенная сборка мусора**
   - Concurrent copying GC с heap compaction
   - Минимальные паузы приложения
   - Эффективное использование памяти

3. **DEX формат**
   - Оптимизирован для мобильных устройств
   - Меньший размер по сравнению с Java bytecode
   - Все классы в одном DEX-файле

**ART vs Dalvik:**
- **Dalvik**: JIT-компиляция во время выполнения, простая GC
- **ART**: AOT + JIT, продвинутая GC, быстрее запуск/выполнение, больше размер приложения

**Пример проверки runtime:**

```kotlin
fun checkRuntime() {
    val runtime = System.getProperty("java.vm.name")
    Log.d("Runtime", "VM: $runtime") // ✅ "ART" на современных устройствах
}
```

**Оптимизация производительности:**

```kotlin
class PerformanceExample {
    fun hotMethod() {
        // ✅ Часто вызывается → компилируется в оптимизированный нативный код
        processData()
    }

    fun coldMethod() {
        // ❌ Редкие вызовы → может оставаться интерпретированным
        cleanup()
    }
}
```

## Answer (EN)

**Android Runtime (ART)** is the execution environment for Android applications, responsible for running code, managing memory, and interacting with the OS. ART replaced Dalvik VM starting from Android 5.0 and uses **AOT (Ahead-of-Time) compilation** for improved performance. See also [[c-memory-management]].

**Key ART Features:**

1. **Hybrid Compilation (Android 7.0+)**
   - Install: Basic AOT compilation (fast)
   - First runs: JIT compilation of "hot" code paths
   - Background optimization: Full AOT compilation

2. **Improved Garbage Collection**
   - Concurrent copying GC with heap compaction
   - Minimal application pause times
   - Efficient memory utilization

3. **DEX Format**
   - Optimized for mobile devices
   - Smaller size compared to Java bytecode
   - All classes packaged in single DEX file

**ART vs Dalvik:**
- **Dalvik**: JIT compilation during runtime, simple GC
- **ART**: AOT + JIT, advanced GC, faster startup/execution, larger app size

**Runtime detection example:**

```kotlin
fun checkRuntime() {
    val runtime = System.getProperty("java.vm.name")
    Log.d("Runtime", "VM: $runtime") // ✅ "ART" on modern devices
}
```

**Performance optimization:**

```kotlin
class PerformanceExample {
    fun hotMethod() {
        // ✅ Frequently called → compiled to optimized native code
        processData()
    }

    fun coldMethod() {
        // ❌ Rarely called → may remain interpreted
        cleanup()
    }
}
```

## Follow-ups

- How does ART's concurrent copying GC reduce pause times?
- What triggers full AOT compilation in background optimization?
- How does profile-guided compilation improve performance in Android 7.0+?
- What are the trade-offs between app install time and runtime performance?

## References

- https://developer.android.com/guide/practices/verifying-app-behavior-on-runtime
- https://source.android.com/docs/core/runtime

## Related Questions

### Prerequisites
- [[q-android-app-components--android--easy]] - Understanding app lifecycle and components
- [[q-android-manifest-file--android--easy]] - App configuration basics

### Related
- [[q-android-app-lag-analysis--android--medium]] - Analyzing performance bottlenecks
- [[q-android-performance-measurement-tools--android--medium]] - Profiling and measuring performance
- [[q-android-build-optimization--android--medium]] - Optimizing build and compilation

### Advanced
- Memory management strategies in ART
- DEX optimization techniques
- Runtime performance profiling