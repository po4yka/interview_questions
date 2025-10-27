---
id: 20251012-122771
title: Android Runtime Internals / Внутреннее устройство Android Runtime
aliases: ["Android Runtime Internals", "Внутреннее устройство Android Runtime"]
topic: android
subtopics: [performance-memory, processes]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-app-lag-analysis--android--medium, q-android-performance-measurement-tools--android--medium, q-android-runtime-art--android--medium]
created: 2025-10-13
updated: 2025-10-27
tags: [android/performance-memory, android/processes, difficulty/hard]
sources: []
---
# Вопрос (RU)
> Как устроено внутреннее функционирование Android Runtime (ART)?

# Question (EN)
> How does Android Runtime (ART) work internally?

## Ответ (RU)

**Android Runtime (ART)** — управляемая среда выполнения, которая абстрагирует аппаратные различия через многоуровневую архитектуру: интерпретатор для начального запуска, JIT-компилятор для горячих участков кода и AOT-компилятор для предварительной оптимизации.

**Архитектура ART:**

```text
Уровень приложения
  ↓
DEX байткод (.dex файлы)
  ↓
Компоненты ART:
  - Загрузчик классов (ClassLoader)
  - Верификатор байткода
  - Интерпретатор
  - JIT-компилятор
  - AOT-компилятор (dex2oat)
  - Сборщик мусора (GC)
  ↓
Исполнение нативного кода
```

**DEX-формат байткода:**

DEX (Dalvik Executable) использует компактный регистровый набор команд, оптимизированный для мобильных устройств. Уменьшает размер файлов по сравнению с Java-байткодом.

```kotlin
// Исходный код
class Example {
    fun add(a: Int, b: Int): Int = a + b
}

// DEX байткод
method public add(II)I
    .registers 4
    add-int v0, p1, p2    // v0 = p1 + p2
    return v0
.end method
```

**Загрузка классов:**

Классы загружаются по требованию из DEX-файлов через иерархическую систему загрузчиков (BootClassLoader → PathClassLoader). Процесс включает верификацию, связывание и инициализацию.

**Режимы выполнения:**

- **Интерпретатор** — прямое выполнение байткода (~10-100x медленнее нативного)
- **JIT-компиляция** — компиляция горячих методов во время работы
- **AOT-компиляция** — предварительная компиляция при установке

**JIT-компиляция:**

```kotlin
// Поток JIT-компиляции
Выполнение метода → Интерпретатор → Сбор профиля →
JIT-компиляция → Кеш нативного кода → Прямое выполнение

class JITExample {
    fun hotMethod() {
        // ✅ Часто вызываемый метод компилируется в нативный код
        processData()
    }
}
```

**AOT-компиляция (dex2oat):**

```kotlin
// Компиляция при установке
Установка APK → Извлечение DEX → dex2oat → OAT-файл

enum class CompilationFilter {
    QUICKEN,          // Оптимизация DEX-инструкций
    SPEED_PROFILE,    // Компиляция профилированных методов
    SPEED,            // Компиляция всего
    EVERYTHING        // Максимальная оптимизация
}
```

**Сборка мусора:**

ART использует поколенческую сборку мусора (generational GC). Большинство объектов "умирают молодыми", поэтому молодое поколение собирается чаще (~1-2ms пауза), полная сборка реже (~5-10ms).

```kotlin
// Android 10+: Поколенческая GC
class GenerationalGC {
    val youngGeneration = Region("young") // Новые объекты
    val oldGeneration = Region("old")     // Долгоживущие объекты

    fun collect() {
        collectYoungGeneration() // ✅ ~1-2ms пауза
        if (needsMajorGC()) {
            collectFullHeap()    // ~5-10ms пауза
        }
    }
}
```

**Управление памятью:**

```kotlin
class MemoryManagement {
    val imageSpace: Space       // Классы фреймворка
    val zygoteSpace: Space      // Разделяемое пространство
    val allocationSpace: Space  // Основная куча приложения
    val largeObjectSpace: Space // Объекты > 12KB

    fun allocate(size: Int): Long {
        return if (size > LARGE_OBJECT_THRESHOLD) {
            largeObjectSpace.allocate(size) // ✅ Большие объекты отдельно
        } else {
            allocationSpace.allocate(size)
        }
    }
}
```

**Типы ссылок:**

```kotlin
class ReferenceExample {
    val strong = Any()                    // Предотвращает GC
    val soft = SoftReference(Any())       // ✅ Очистка при нехватке памяти
    val weak = WeakReference(Any())       // Очистка при следующей GC
    val phantom = PhantomReference(Any(), ReferenceQueue()) // Отслеживание очистки
}
```

**Оптимизации компилятора:**

```kotlin
// Встраивание методов (inlining)
inline fun add(a: Int, b: Int) = a + b // ✅ Убирает вызов функции

// Оптимизация циклов
fun sumArray(array: IntArray): Int {
    var sum = 0
    for (i in array.indices) {
        sum += array[i] // ✅ Устранение проверки границ, развертка цикла
    }
    return sum
}

// Escape-анализ
fun test() {
    val point = Point(10, 20) // ✅ Выделение в стеке, не в куче
    val distance = point.distance()
}
```

**Ключевые концепции:**
- DEX-формат — компактный регистровый байткод
- Многоуровневое выполнение — интерпретатор → JIT → AOT
- Поколенческая GC — разделение молодых/старых объектов
- Конкурентная сборка — минимальные паузы
- Оптимизации компилятора — inlining, devirtualization, escape analysis

## Answer (EN)

**Android Runtime (ART)** is a managed execution environment that abstracts hardware differences through a multi-tier architecture: interpreter for initial execution, JIT compiler for hot code paths, and AOT compiler for pre-compiled optimization.

**ART Architecture:**

```text
Application Layer
  ↓
DEX Bytecode (.dex files)
  ↓
ART Runtime Components:
  - Class Loader
  - Bytecode Verifier
  - Interpreter
  - JIT Compiler
  - AOT Compiler (dex2oat)
  - Garbage Collector
  ↓
Native Code Execution
```

**DEX Bytecode Format:**

DEX (Dalvik Executable) uses a compact, register-based instruction set optimized for mobile devices. It reduces file size compared to Java bytecode.

```kotlin
// Source code
class Example {
    fun add(a: Int, b: Int): Int = a + b
}

// DEX bytecode
method public add(II)I
    .registers 4
    add-int v0, p1, p2    // v0 = p1 + p2
    return v0
.end method
```

**Class Loading:**

Classes are loaded on-demand from DEX files through a hierarchical classloader system (BootClassLoader → PathClassLoader). The process involves verification, linking, and initialization.

**Execution Modes:**

- **Interpreter** — direct bytecode execution (~10-100x slower than native)
- **JIT Compilation** — hot method compilation during runtime
- **AOT Compilation** — pre-compilation at install time

**JIT Compilation:**

```kotlin
// JIT compilation flow
Method Execution → Interpreter → Profile Collection →
JIT Compilation → Native Code Cache → Direct Execution

class JITExample {
    fun hotMethod() {
        // ✅ Frequently called method compiled to native code
        processData()
    }
}
```

**AOT Compilation (dex2oat):**

```kotlin
// Installation-time compilation
Install APK → Extract DEX → dex2oat → OAT file

enum class CompilationFilter {
    QUICKEN,          // Optimize DEX instructions
    SPEED_PROFILE,    // Compile profiled methods
    SPEED,            // Compile everything
    EVERYTHING        // Maximum optimization
}
```

**Garbage Collection:**

ART uses generational garbage collection. Most objects die young, so young generation is collected more frequently (~1-2ms pause), full collection less often (~5-10ms).

```kotlin
// Android 10+: Generational GC
class GenerationalGC {
    val youngGeneration = Region("young") // New objects
    val oldGeneration = Region("old")     // Long-lived objects

    fun collect() {
        collectYoungGeneration() // ✅ ~1-2ms pause
        if (needsMajorGC()) {
            collectFullHeap()    // ~5-10ms pause
        }
    }
}
```

**Memory Management:**

```kotlin
class MemoryManagement {
    val imageSpace: Space       // Framework classes
    val zygoteSpace: Space      // Shared space
    val allocationSpace: Space  // Main app heap
    val largeObjectSpace: Space // Objects > 12KB

    fun allocate(size: Int): Long {
        return if (size > LARGE_OBJECT_THRESHOLD) {
            largeObjectSpace.allocate(size) // ✅ Large objects separately
        } else {
            allocationSpace.allocate(size)
        }
    }
}
```

**Reference Types:**

```kotlin
class ReferenceExample {
    val strong = Any()                    // Prevents GC
    val soft = SoftReference(Any())       // ✅ Cleared under memory pressure
    val weak = WeakReference(Any())       // Cleared at next GC
    val phantom = PhantomReference(Any(), ReferenceQueue()) // Cleanup tracking
}
```

**Compiler Optimizations:**

```kotlin
// Method inlining
inline fun add(a: Int, b: Int) = a + b // ✅ Removes function call overhead

// Loop optimization
fun sumArray(array: IntArray): Int {
    var sum = 0
    for (i in array.indices) {
        sum += array[i] // ✅ Bounds check elimination, loop unrolling
    }
    return sum
}

// Escape analysis
fun test() {
    val point = Point(10, 20) // ✅ Stack allocation, not heap
    val distance = point.distance()
}
```

**Key Concepts:**
- DEX format — compact, register-based bytecode
- Multi-tier execution — interpreter → JIT → AOT
- Generational GC — young/old generation separation
- Concurrent collection — minimal pause times
- Compiler optimizations — inlining, devirtualization, escape analysis

## Follow-ups

- How does ART's JIT compiler determine which methods to optimize?
- What are the performance implications of different compilation filters (QUICKEN vs SPEED)?
- How does generational GC improve pause times compared to full heap collection?
- What is the trade-off between AOT and JIT compilation strategies?

## References

- [[c-memory-management]]
- https://source.android.com/docs/core/runtime
- https://developer.android.com/guide/practices/verifying-app-behavior-on-runtime

## Related Questions

### Prerequisites (Easier)
- [[q-android-runtime-art--android--medium]] - ART basics and compilation modes

### Related (Same Level)
- [[q-android-app-lag-analysis--android--medium]] - Performance analysis techniques
- [[q-android-performance-measurement-tools--android--medium]] - Profiling tools

### Advanced
- Questions about custom classloaders and dynamic code loading
- Questions about native memory management and JNI optimization