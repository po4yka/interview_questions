---
id: 20251012-122770
title: Android Runtime (ART) / Android Runtime (ART)
aliases: ["Android Runtime (ART)", "АРТ"]
topic: android
subtopics: [processes, performance-memory]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-app-lag-analysis--android--medium, q-android-performance-measurement-tools--android--medium, q-android-build-optimization--android--medium]
created: 2025-10-15
updated: 2025-10-29
tags: [android/processes, android/performance-memory, runtime, compilation, gc, difficulty/medium]
sources: []
---
# Вопрос (RU)
> Что такое Android Runtime (ART) и чем он отличается от Dalvik?

# Question (EN)
> What is Android Runtime (ART) and how does it differ from Dalvik?

## Ответ (RU)

**Android Runtime (ART)** — среда выполнения приложений Android, отвечающая за компиляцию, запуск кода и управление памятью. ART заменил Dalvik VM и использует гибридную компиляцию для оптимального баланса производительности и размера приложения.

### Гибридная компиляция

```kotlin
// ✅ Установка: базовый профиль → быстрая установка
// При первых запусках приложения:
class HotPath {
    fun frequentOperation() {
        // Профилируется JIT → выявляются "горячие" методы
        processData()
    }
}

// ❌ Редко используемый код остается интерпретированным
class ColdPath {
    fun rareOperation() {
        cleanup()
    }
}
```

Три этапа компиляции:
1. **Установка** — минимальная AOT-компиляция критических путей
2. **Выполнение** — JIT профилирование активного кода
3. **Фоновая оптимизация** — полная AOT-компиляция при зарядке и бездействии

### Улучшенная сборка мусора

```kotlin
// ✅ Concurrent copying GC минимизирует паузы
class MemoryExample {
    private val largeList = mutableListOf<Bitmap>()

    fun allocateMemory() {
        // GC работает параллельно с приложением
        // Heap compaction устраняет фрагментацию
        repeat(1000) {
            largeList.add(createBitmap())
        }
    }
}

// ❌ В Dalvik: stop-the-world паузы замораживали UI
```

### DEX формат

```kotlin
// ✅ DEX: все классы в одном контейнере
// dex/classes.dex: compact bytecode для Android
val dexFormat = """
    Header
    StringIds → все строки
    TypeIds → все типы
    MethodIds → все методы
    ClassDefs → определения классов
"""

// ❌ Java bytecode: отдельный .class для каждого класса
// Больше overhead, медленнее загрузка
```

### ART vs Dalvik

| Характеристика | Dalvik | ART |
|----------------|--------|-----|
| Компиляция | JIT во время выполнения | Гибридная AOT + JIT |
| Запуск приложения | Медленный | Быстрый |
| Использование памяти | Меньше | Больше (скомпилированный код) |
| GC | Mark-and-sweep (паузы) | Concurrent copying (параллельная) |
| Батарея | Больше расход (постоянная JIT) | Меньше расход |

### Проверка runtime в коде

```kotlin
fun detectRuntime(): String {
    return System.getProperty("java.vm.name") ?: "Unknown"
    // ✅ Современные Android: "ART"
    // ❌ Android 4.4 и ниже: "Dalvik"
}

// Оптимизация под ART
@Keep // Предотвращает удаление при ProGuard/R8
class CriticalPath {
    // Часто вызываемые методы → приоритет для AOT
    fun criticalOperation() { /* ... */ }
}
```

## Answer (EN)

**Android Runtime (ART)** is the application execution environment for Android, responsible for compilation, code execution, and memory management. ART replaced Dalvik VM and uses hybrid compilation for optimal balance between performance and app size.

### Hybrid Compilation

```kotlin
// ✅ Installation: baseline profile → fast install
// During first app launches:
class HotPath {
    fun frequentOperation() {
        // Profiled by JIT → identifies "hot" methods
        processData()
    }
}

// ❌ Rarely used code remains interpreted
class ColdPath {
    fun rareOperation() {
        cleanup()
    }
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
        // Heap compaction eliminates fragmentation
        repeat(1000) {
            largeList.add(createBitmap())
        }
    }
}

// ❌ In Dalvik: stop-the-world pauses froze UI
```

### DEX Format

```kotlin
// ✅ DEX: all classes in single container
// dex/classes.dex: compact bytecode for Android
val dexFormat = """
    Header
    StringIds → all strings
    TypeIds → all types
    MethodIds → all methods
    ClassDefs → class definitions
"""

// ❌ Java bytecode: separate .class for each class
// More overhead, slower loading
```

### ART vs Dalvik

| Feature | Dalvik | ART |
|---------|--------|-----|
| Compilation | JIT during runtime | Hybrid AOT + JIT |
| App startup | Slow | Fast |
| Memory usage | Less | More (compiled code) |
| GC | Mark-and-sweep (pauses) | Concurrent copying (parallel) |
| Battery | Higher drain (constant JIT) | Lower drain |

### Runtime detection in code

```kotlin
fun detectRuntime(): String {
    return System.getProperty("java.vm.name") ?: "Unknown"
    // ✅ Modern Android: "ART"
    // ❌ Android 4.4 and below: "Dalvik"
}

// ART optimization
@Keep // Prevents removal during ProGuard/R8
class CriticalPath {
    // Frequently called methods → priority for AOT
    fun criticalOperation() { /* ... */ }
}
```

## Follow-ups

- Как профилирование JIT влияет на производительность в первых запусках?
- Почему concurrent copying GC эффективнее mark-and-sweep для Android?
- Как baseline profiles оптимизируют установку приложений?
- В каких сценариях DEX-формат предпочтительнее стандартного Java bytecode?
- Какие стратегии минимизации размера APK при AOT-компиляции?

## References

- [[c-memory-management]]
- [[c-android-build-process]]
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

### Advanced
- [[q-android-memory-leaks--android--hard]]
- [[q-r8-proguard-optimization--android--hard]]