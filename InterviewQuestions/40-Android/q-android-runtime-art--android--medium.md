---
id: android-297
title: Android Runtime (ART) / Android Runtime (ART)
aliases: [Android Runtime (ART), АРТ]
topic: android
subtopics:
  - performance-memory
  - processes
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - q-android-app-lag-analysis--android--medium
  - q-android-performance-measurement-tools--android--medium
created: 2025-10-15
updated: 2025-10-30
tags: [android/performance-memory, android/processes, compilation, difficulty/medium, gc, runtime]
sources: []
---

# Вопрос (RU)
> Что такое Android Runtime (ART) и чем он отличается от Dalvik?

# Question (EN)
> What is Android Runtime (ART) and how does it differ from Dalvik?

## Ответ (RU)

**Android Runtime (ART)** — среда выполнения приложений Android, отвечающая за компиляцию, запуск кода и управление памятью. ART заменил Dalvik VM и использует гибридную компиляцию для оптимального баланса производительности и размера приложения.

### Гибридная Компиляция

```kotlin
// ✅ Установка: базовый профиль → быстрая установка
class HotPath {
    fun frequentOperation() {
        // JIT профилирует "горячие" методы
        processData()
    }
}

// ❌ Редко используемый код остается интерпретированным
class ColdPath {
    fun rareOperation() { cleanup() }
}
```

Три этапа компиляции:
1. **Установка** — минимальная AOT-компиляция критических путей
2. **Выполнение** — JIT профилирование активного кода
3. **Фоновая оптимизация** — полная AOT-компиляция при зарядке и бездействии

### Улучшенная Сборка Мусора

```kotlin
// ✅ Concurrent copying GC минимизирует паузы
class MemoryExample {
    private val largeList = mutableListOf<Bitmap>()

    fun allocateMemory() {
        // GC работает параллельно с приложением
        repeat(1000) { largeList.add(createBitmap()) }
    }
}

// ❌ В Dalvik: stop-the-world паузы замораживали UI
```

### DEX Формат

```kotlin
// ✅ DEX: все классы в одном контейнере
val dexFormat = """
    Header
    StringIds → все строки
    TypeIds → все типы
    MethodIds → все методы
    ClassDefs → определения классов
"""

// ❌ Java bytecode: отдельный .class для каждого класса
```

### ART Vs Dalvik

| Характеристика | Dalvik | ART |
|----------------|--------|-----|
| Компиляция | JIT во время выполнения | Гибридная AOT + JIT |
| Запуск приложения | Медленный | Быстрый |
| Использование памяти | Меньше | Больше (скомпилированный код) |
| GC | Mark-and-sweep (паузы) | Concurrent copying (параллельная) |
| Батарея | Больше расход (постоянная JIT) | Меньше расход |

### Проверка Runtime

```kotlin
fun detectRuntime(): String {
    return System.getProperty("java.vm.name") ?: "Unknown"
    // ✅ Современные Android: "ART"
    // ❌ Android 4.4 и ниже: "Dalvik"
}

// Оптимизация под ART
@Keep // Предотвращает удаление при ProGuard/R8
class CriticalPath {
    fun criticalOperation() { /* приоритет для AOT */ }
}
```

## Answer (EN)

**Android Runtime (ART)** is the application execution environment for Android, responsible for compilation, code execution, and memory management. ART replaced Dalvik VM and uses hybrid compilation for optimal balance between performance and app size.

### Hybrid Compilation

```kotlin
// ✅ Installation: baseline profile → fast install
class HotPath {
    fun frequentOperation() {
        // JIT profiles "hot" methods
        processData()
    }
}

// ❌ Rarely used code remains interpreted
class ColdPath {
    fun rareOperation() { cleanup() }
}
```

Three compilation stages:
1. **Install** — minimal AOT compilation of critical paths
2. **Runtime** — JIT profiling of active code
3. **Background optimization** — full AOT compilation during charging and idle

### Improved Garbage Collection

```kotlin
// ✅ Concurrent copying GC minimizes pauses
class MemoryExample {
    private val largeList = mutableListOf<Bitmap>()

    fun allocateMemory() {
        // GC runs concurrently with app
        repeat(1000) { largeList.add(createBitmap()) }
    }
}

// ❌ In Dalvik: stop-the-world pauses froze UI
```

### DEX Format

```kotlin
// ✅ DEX: all classes in single container
val dexFormat = """
    Header
    StringIds → all strings
    TypeIds → all types
    MethodIds → all methods
    ClassDefs → class definitions
"""

// ❌ Java bytecode: separate .class for each class
```

### ART Vs Dalvik

| Feature | Dalvik | ART |
|---------|--------|-----|
| Compilation | JIT during runtime | Hybrid AOT + JIT |
| App startup | Slow | Fast |
| Memory usage | Less | More (compiled code) |
| GC | Mark-and-sweep (pauses) | Concurrent copying (parallel) |
| Battery | Higher drain (constant JIT) | Lower drain |

### Runtime Detection

```kotlin
fun detectRuntime(): String {
    return System.getProperty("java.vm.name") ?: "Unknown"
    // ✅ Modern Android: "ART"
    // ❌ Android 4.4 and below: "Dalvik"
}

// ART optimization
@Keep // Prevents removal during ProGuard/R8
class CriticalPath {
    fun criticalOperation() { /* priority for AOT */ }
}
```

## Follow-ups

- Как baseline profiles влияют на время установки и первый запуск приложения?
- В каких случаях AOT-компиляция может увеличить размер APK критично?
- Почему concurrent copying GC эффективнее mark-and-sweep для mobile приложений?
- Как профилировать JIT для выявления кандидатов на AOT-оптимизацию?
- Какие методы маркировать `@Keep` для предотвращения проблем с reflection после R8?

## References

- [[c-memory-management]]
- https://source.android.com/docs/core/runtime
- https://developer.android.com/topic/performance/baselineprofiles

## Related Questions

### Prerequisites
- [[q-android-app-components--android--easy]]
- [[q-android-manifest-file--android--easy]]

### Related
- [[q-android-app-lag-analysis--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]
- [[q-android-build-optimization--android--medium]]
