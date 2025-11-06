---
id: android-107
title: Android Runtime Internals / Внутреннее устройство Android Runtime
aliases: [Android Runtime Internals, Внутреннее устройство Android Runtime]
topic: android
subtopics:
  - performance-memory
  - processes
  - profiling
question_kind: android
difficulty: hard
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - q-android-app-lag-analysis--android--medium
  - q-android-performance-measurement-tools--android--medium
  - q-android-runtime-art--android--medium
created: 2025-10-13
updated: 2025-10-30
tags: [android/performance-memory, android/processes, android/profiling, difficulty/hard]
sources: []
---

# Вопрос (RU)
> Как устроено внутреннее функционирование Android Runtime (ART)?

# Question (EN)
> How does Android Runtime (ART) work internally?

---

## Ответ (RU)

**Android Runtime (ART)** — управляемая среда выполнения, объединяющая три режима исполнения кода: интерпретатор для первого запуска, JIT-компилятор для горячих участков и AOT-компилятор для предварительной оптимизации при установке. Использует поколенческую сборку мусора для минимизации пауз.

**Архитектура ART:**

```text
APK/DEX → ClassLoader → Верификатор → Интерпретатор/JIT/AOT → GC → Нативный код
```

**DEX-формат:** Регистровый байткод (компактнее стекового Java-байткода):

```kotlin
// Исходный код
fun add(a: Int, b: Int): Int = a + b

// DEX байткод
method add(II)I
    .registers 3
    add-int v0, p1, p2    // ✅ Регистровая модель
    return v0
```

**Режимы выполнения:**

- **Интерпретатор** — прямое выполнение без задержек на компиляцию
- **JIT** — фоновая компиляция горячих методов после ~10k вызовов
- **AOT** — предкомпиляция при установке (профилируемые методы или все)

**Фильтры AOT-компиляции:**

```kotlin
enum class CompilationFilter {
    QUICKEN,          // ❌ Только оптимизация DEX
    SPEED_PROFILE,    // ✅ Компиляция профилируемых методов (~20-30% кода)
    SPEED,            // Полная компиляция (долгая установка)
    EVERYTHING        // Максимум оптимизаций
}
// По умолчанию: SPEED_PROFILE
```

**Поколенческая сборка мусора:**

```kotlin
// Молодое поколение: новые объекты, частая сборка (~1-2ms)
// Старое поколение: выжившие объекты, редкая сборка (~5-10ms)

class GCRegions {
    val youngGen = Region("young")  // ✅ 95% объектов умирают здесь
    val oldGen = Region("old")      // Долгоживущие данные
}
```

**Управление памятью (Heap Spaces):**

```kotlin
class MemorySpaces {
    val imageSpace: Space       // ✅ Разделяемые классы фреймворка
    val zygoteSpace: Space      // Разделяемое между процессами
    val allocationSpace: Space  // Основная куча приложения
    val largeObjectSpace: Space // ❌ Объекты >12KB (без перемещения)
}
```

**Компиляторные оптимизации:**

```kotlin
// Встраивание (inlining)
inline fun measure(block: () -> Unit) {
    val start = System.nanoTime()
    block()  // ✅ Код встроен на месте вызова
    log("Time: ${System.nanoTime() - start}")
}

// Устранение виртуализации
fun test(obj: Derived) {
    obj.compute()  // ✅ Прямой вызов (JIT знает точный тип)
}

// Escape-анализ: выделение в стеке
fun calculateDistance(x: Int, y: Int): Int {
    val point = Point(x, y)  // ✅ Не попадает в кучу
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

**ART Architecture:**

```text
APK/DEX → ClassLoader → Verifier → Interpreter/JIT/AOT → GC → Native Code
```

**DEX Format:** Register-based bytecode (more compact than stack-based Java bytecode):

```kotlin
// Source code
fun add(a: Int, b: Int): Int = a + b

// DEX bytecode
method add(II)I
    .registers 3
    add-int v0, p1, p2    // ✅ Register-based model
    return v0
```

**Execution Modes:**

- **Interpreter** — direct execution without compilation delay
- **JIT** — background compilation of hot methods after ~10k invocations
- **AOT** — pre-compilation during install (profiled methods or all)

**AOT Compilation Filters:**

```kotlin
enum class CompilationFilter {
    QUICKEN,          // ❌ DEX optimization only
    SPEED_PROFILE,    // ✅ Compile profiled methods (~20-30% of code)
    SPEED,            // Full compilation (slow install)
    EVERYTHING        // Maximum optimizations
}
// Default: SPEED_PROFILE
```

**Generational Garbage `Collection`:**

```kotlin
// Young generation: new objects, frequent collection (~1-2ms)
// Old generation: survived objects, infrequent collection (~5-10ms)

class GCRegions {
    val youngGen = Region("young")  // ✅ 95% objects die here
    val oldGen = Region("old")      // Long-lived data
}
```

**Memory Management (Heap Spaces):**

```kotlin
class MemorySpaces {
    val imageSpace: Space       // ✅ Shared framework classes
    val zygoteSpace: Space      // Shared between processes
    val allocationSpace: Space  // Main app heap
    val largeObjectSpace: Space // ❌ Objects >12KB (no relocation)
}
```

**Compiler Optimizations:**

```kotlin
// Inlining
inline fun measure(block: () -> Unit) {
    val start = System.nanoTime()
    block()  // ✅ Code inlined at call site
    log("Time: ${System.nanoTime() - start}")
}

// Devirtualization
fun test(obj: Derived) {
    obj.compute()  // ✅ Direct call (JIT knows exact type)
}

// Escape analysis: stack allocation
fun calculateDistance(x: Int, y: Int): Int {
    val point = Point(x, y)  // ✅ Doesn't escape to heap
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

- How does ART decide which methods to compile with JIT based on profiling data?
- What are the trade-offs between SPEED_PROFILE and SPEED compilation filters?
- How does generational GC reduce pause times compared to mark-and-sweep collectors?
- What triggers promotion of objects from young to old generation?
- How does escape analysis determine if an object can be stack-allocated?

## References

- [[c-memory-management]]
- https://source.android.com/docs/core/runtime
- [Memory Management](https://developer.android.com/topic/performance/memory-overview)


## Related Questions

### Prerequisites (Easier)
- [[q-android-runtime-art--android--medium]] - ART basics and compilation modes
- [[q-android-performance-measurement-tools--android--medium]] - Profiling tools

### Related (Same Level)
- [[q-android-app-lag-analysis--android--medium]] - Performance analysis techniques

### Advanced (Harder)
- Custom classloaders and dynamic code loading optimization
- Native memory management and JNI performance tuning
