---
id: 20251012-122771
title: Android Runtime Internals / Внутреннее устройство Android Runtime
aliases: ["Android Runtime Internals", "Внутреннее устройство Android Runtime"]
topic: android
subtopics: [performance-memory, processes, profiling]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-app-lag-analysis--android--medium, q-android-performance-measurement-tools--android--medium, q-android-runtime-art--android--medium]
created: 2025-10-13
updated: 2025-10-29
tags: [android/performance-memory, android/processes, android/profiling, difficulty/hard]
sources: []
---
# Вопрос (RU)
> Как устроено внутреннее функционирование Android Runtime (ART)?

# Question (EN)
> How does Android Runtime (ART) work internally?

---

## Ответ (RU)

**Android Runtime (ART)** — управляемая среда выполнения, объединяющая три режима исполнения: интерпретатор для первого запуска, JIT-компилятор для горячих участков и AOT-компилятор для предварительной оптимизации при установке. Использует поколенческую сборку мусора для минимизации пауз.

**Компоненты ART:**

```text
APK/DEX → ClassLoader → Верификатор →
→ Интерпретатор/JIT/AOT → GC → Нативный код
```

**DEX-формат:** Регистровый байткод, компактнее Java-байткода. Использует регистры вместо стека.

```kotlin
// Исходный код
fun add(a: Int, b: Int): Int = a + b

// DEX байткод
method public add(II)I
    .registers 3
    add-int v0, p1, p2    // ✅ Регистровая модель (компактнее стековой)
    return v0
```

**Режимы выполнения:**

- **Интерпретатор** — прямое выполнение, медленно но без задержек на компиляцию
- **JIT** — компиляция горячих методов в фоне, профилирование во время работы
- **AOT** — предкомпиляция при установке (профилируемые методы или все)

```kotlin
// JIT: Профилирование → Компиляция горячих методов
class HotPathExample {
    fun processLoop(items: List<Item>) {
        items.forEach {
            calculateExpensive(it)  // ✅ Скомпилируется после ~10k вызовов
        }
    }
}
```

**Фильтры AOT-компиляции:**

```kotlin
enum class CompilationFilter {
    QUICKEN,          // ❌ Только оптимизация DEX (без нативного кода)
    SPEED_PROFILE,    // ✅ Компиляция профилируемых методов (~20-30% кода)
    SPEED,            // Полная компиляция (долгая установка)
    EVERYTHING        // Максимум оптимизаций (очень долго)
}
// По умолчанию: SPEED_PROFILE (баланс скорости/размера)
```

**Поколенческая сборка мусора:**

```kotlin
// Молодое поколение: новые объекты, частая сборка (~1-2ms)
// Старое поколение: выжившие объекты, редкая сборка (~5-10ms)

class GCRegions {
    val youngGen = Region("young")  // ✅ 95% объектов умирают здесь
    val oldGen = Region("old")      // Долгоживущие данные

    fun minorGC() {
        collectYoungGeneration()    // Быстро, параллельно
    }
}
```

**Управление памятью:**

```kotlin
// Куча разделена на регионы
class MemorySpaces {
    val imageSpace: Space       // ✅ Разделяемые классы фреймворка
    val zygoteSpace: Space      // Разделяемое между процессами
    val allocationSpace: Space  // Основная куча приложения
    val largeObjectSpace: Space // ❌ Объекты > 12KB (без перемещения)
}
```

**Типы ссылок и управление:**

```kotlin
class ReferencesExample {
    val strong = Any()                   // Блокирует GC
    val soft = SoftReference(cache)      // ✅ Кеш: очистка при нехватке памяти
    val weak = WeakReference(listener)   // ✅ Слушатели: очистка при GC
    val phantom = PhantomReference(obj, queue) // Отслеживание финализации
}
```

**Компиляторные оптимизации:**

```kotlin
// Встраивание (inlining)
inline fun measure(block: () -> Unit) {
    val start = System.nanoTime()
    block()  // ✅ Код block() встроен на месте вызова
    log("Time: ${System.nanoTime() - start}")
}

// Устранение виртуализации (devirtualization)
open class Base { open fun compute() = 1 }
class Derived : Base() { override fun compute() = 2 }

fun test(obj: Derived) {
    obj.compute()  // ✅ Прямой вызов (JIT знает точный тип)
}

// Escape-анализ: выделение в стеке
fun calculateDistance(x: Int, y: Int): Int {
    val point = Point(x, y)  // ✅ Не попадает в кучу (локальный объект)
    return point.distance()
}
```

**Ключевые концепции:**
- DEX-формат: регистровый байткод, компактный
- Многоуровневое выполнение: интерпретатор → JIT → AOT
- Поколенческая GC: молодое/старое поколение, минимальные паузы
- Профилирование: компиляция горячих методов
- Оптимизации: inlining, devirtualization, escape analysis

## Answer (EN)

**Android Runtime (ART)** is a managed execution environment combining three execution modes: interpreter for initial launch, JIT compiler for hot code paths, and AOT compiler for pre-compilation during installation. Uses generational garbage collection to minimize pause times.

**ART Components:**

```text
APK/DEX → ClassLoader → Verifier →
→ Interpreter/JIT/AOT → GC → Native Code
```

**DEX Format:** Register-based bytecode, more compact than Java bytecode. Uses registers instead of stack.

```kotlin
// Source code
fun add(a: Int, b: Int): Int = a + b

// DEX bytecode
method public add(II)I
    .registers 3
    add-int v0, p1, p2    // ✅ Register-based model (more compact than stack)
    return v0
```

**Execution Modes:**

- **Interpreter** — direct execution, slow but no compilation delay
- **JIT** — background compilation of hot methods, runtime profiling
- **AOT** — pre-compilation during install (profiled methods or all)

```kotlin
// JIT: Profiling → Hot method compilation
class HotPathExample {
    fun processLoop(items: List<Item>) {
        items.forEach {
            calculateExpensive(it)  // ✅ Compiled after ~10k invocations
        }
    }
}
```

**AOT Compilation Filters:**

```kotlin
enum class CompilationFilter {
    QUICKEN,          // ❌ DEX optimization only (no native code)
    SPEED_PROFILE,    // ✅ Compile profiled methods (~20-30% of code)
    SPEED,            // Full compilation (slow install)
    EVERYTHING        // Maximum optimizations (very slow)
}
// Default: SPEED_PROFILE (balance speed/size)
```

**Generational Garbage Collection:**

```kotlin
// Young generation: new objects, frequent collection (~1-2ms)
// Old generation: survived objects, infrequent collection (~5-10ms)

class GCRegions {
    val youngGen = Region("young")  // ✅ 95% objects die here
    val oldGen = Region("old")      // Long-lived data

    fun minorGC() {
        collectYoungGeneration()    // Fast, concurrent
    }
}
```

**Memory Management:**

```kotlin
// Heap divided into regions
class MemorySpaces {
    val imageSpace: Space       // ✅ Shared framework classes
    val zygoteSpace: Space      // Shared between processes
    val allocationSpace: Space  // Main app heap
    val largeObjectSpace: Space // ❌ Objects > 12KB (no relocation)
}
```

**Reference Types and Management:**

```kotlin
class ReferencesExample {
    val strong = Any()                   // Prevents GC
    val soft = SoftReference(cache)      // ✅ Cache: cleared under memory pressure
    val weak = WeakReference(listener)   // ✅ Listeners: cleared at GC
    val phantom = PhantomReference(obj, queue) // Finalization tracking
}
```

**Compiler Optimizations:**

```kotlin
// Inlining
inline fun measure(block: () -> Unit) {
    val start = System.nanoTime()
    block()  // ✅ block() code inlined at call site
    log("Time: ${System.nanoTime() - start}")
}

// Devirtualization
open class Base { open fun compute() = 1 }
class Derived : Base() { override fun compute() = 2 }

fun test(obj: Derived) {
    obj.compute()  // ✅ Direct call (JIT knows exact type)
}

// Escape analysis: stack allocation
fun calculateDistance(x: Int, y: Int): Int {
    val point = Point(x, y)  // ✅ Doesn't escape to heap (local object)
    return point.distance()
}
```

**Key Concepts:**
- DEX format: register-based bytecode, compact
- Multi-tier execution: interpreter → JIT → AOT
- Generational GC: young/old generation, minimal pauses
- Profiling: hot method compilation
- Optimizations: inlining, devirtualization, escape analysis

---

## Follow-ups

- How does ART's JIT compiler decide which methods to optimize based on profiling data?
- What are the trade-offs between SPEED_PROFILE and SPEED compilation filters for app startup performance?
- How does generational GC reduce pause times compared to mark-and-sweep collectors?
- What is the role of escape analysis in reducing heap allocations?
- How do soft/weak references help manage memory-sensitive caches without causing OOM?

## References

- [[c-memory-management]]
- https://source.android.com/docs/core/runtime
- https://developer.android.com/topic/performance/memory-overview
- https://developer.android.com/studio/profile/jank-detection

## Related Questions

### Prerequisites (Easier)
- [[q-android-runtime-art--android--medium]] - ART basics and compilation modes
- [[q-android-performance-measurement-tools--android--medium]] - Profiling tools

### Related (Same Level)
- [[q-android-app-lag-analysis--android--medium]] - Performance analysis techniques

### Advanced (Harder)
- Custom classloaders and dynamic code loading optimization
- Native memory management and JNI performance tuning
