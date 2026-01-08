---\
id: android-107
title: Android Runtime Internals / Внутреннее устройство Android Runtime
aliases: [Android Runtime Internals, Внутреннее устройство Android Runtime]
topic: android
subtopics: [performance-memory, processes, profiling]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-app-lag-analysis--android--medium, q-android-performance-measurement-tools--android--medium, q-android-runtime-art--android--medium, q-optimize-memory-usage-android--android--medium]
created: 2025-10-13
updated: 2025-11-10
tags: [android/performance-memory, android/processes, android/profiling, difficulty/hard]
sources: []
---\
# Вопрос (RU)
> Как устроено внутреннее функционирование Android Runtime (ART)?

# Question (EN)
> How does Android Runtime (ART) work internally?

---

## Ответ (RU)

**Android Runtime (ART)** — управляемая среда выполнения, объединяющая несколько режимов исполнения кода: интерпретатор для первого запуска, JIT-компилятор для горячих участков и AOT-компилятор для предварительной оптимизации при установке (на основе профилей и/или политики). Использует современный многопространственный (image/zygote/alloc/large) сборщик мусора с инкрементальными и concurrent-алгоритмами, включающими поколенческие и региональные идеи для минимизации пауз.

**Архитектура ART (упрощённо):**

```text
APK/DEX → ClassLoader → Верификатор → Интерпретатор/JIT/AOT ↔ GC → Нативный код
```

(GC работает параллельно с исполнением, а не только «после» компиляции.)

**DEX-формат:** Регистровый байткод (компактнее стекового Java-байткода):

```kotlin
// Исходный код
fun add(a: Int, b: Int): Int = a + b

// Упрощённый пример DEX байткода
method add(II)I
    .registers 3
    add-int v0, p1, p2    // ✅ Регистровая модель
    return v0
```

**Режимы выполнения:**

- **Интерпретатор** — прямое выполнение байткода без начальной задержки на компиляцию.
- **JIT** — фоновая компиляция «горячих» методов на основе профилирования (порог вызовов и эвристики зависят от версии ART, «~10k» — порядок величины, а не фиксированное значение).
- **AOT** — предкомпиляция при установке/обновлении приложения (под множество методов в соответствии с профилем и выбранным фильтром компиляции).

**Фильтры AOT-компиляции (упрощённо):**

```kotlin
enum class CompilationFilter {
    QUICKEN,         // Оптимизация и "разметка" DEX для более быстрого интерпретатора
    SPEED_PROFILE,   // ✅ Компиляция профилируемых "горячих" методов
    SPEED,           // Более агрессивная компиляция ради скорости исполнения
    EVERYTHING       // Максимум AOT-компиляции (потенциально более долгие установка/обновление)
}
// Типичное значение по умолчанию на современных устройствах: SPEED_PROFILE (конкретика зависит от OEM/версии)
```

(Набор фильтров и точное поведение могут отличаться между версиями Android; пример иллюстративный.)

**Сборка мусора и поколения (conceptually):**

ART использует несколько типов сборщиков (например, Concurrent Copying, CMS, space-based) и разделение кучи на пространства, что позволяет:
- чаще и дешевле собирать недолговечные объекты;
- реже трогать долго живущие объекты;
- выполнять значительную часть работы concurrent, снижая стоп-паузы.

```kotlin
// Молодое "пространство"/регион: новые объекты, частые быстрые сборки
// Старшие/долгоживущие области: реже собираются, сокращая полные паузы

class GCRegions {
    val youngLike = Region("young")  // Большая часть объектов умирает здесь
    val oldLike = Region("old")      // Долгоживущие данные
}
```

(Точная реализация поколенческой/региональной схемы зависит от версии ART; важно понимать идею оптимизации под "большинство объектов живут недолго".)

**Управление памятью (Heap Spaces):**

```kotlin
class MemorySpaces {
    val imageSpace: Space       // ✅ Предзагруженные и разделяемые классы фреймворка
    val zygoteSpace: Space      // Разделяемые между процессами объекты, созданные до форка zygote
    val allocationSpace: Space  // Основная куча приложения для новых объектов
    val largeObjectSpace: Space // Крупные объекты (порог порядка ~8-12KB+, обычно не перемещаются)
}
```

(Конкретный порог для LargeObjectSpace и поведение могут меняться между версиями Android.)

**Компиляторные оптимизации (упрощённые примеры):**

```kotlin
// Встраивание (inlining)
inline fun measure(block: () -> Unit) {
    val start = System.nanoTime()
    block()  // ✅ Может быть встроено на месте вызова при JIT/AOT-оптимизации
    log("Time: ${System.nanoTime() - start}")
}

// Устранение виртуализации (devirtualization)
fun test(obj: Derived) {
    obj.compute()  // ✅ Может быть превращён в прямой вызов, если рантайм знает точный тип
}

// Escape-анализ и стековое размещение
fun calculateDistance(x: Int, y: Int): Int {
    val point = Point(x, y)
    // ✅ Может быть разложен (scalar replacement) и не попадать в кучу,
    // если анализ доказывает отсутствие ухода ссылки за пределы метода
    return point.distance()
}
```

**Ключевые концепции:**
- DEX-формат: регистровый байткод, компактный и оптимизированный под ART.
- Многоуровневое выполнение: интерпретатор → JIT → AOT с профилированием.
- Продвинутый GC: многопространственная/конкурентная сборка с учётом "поколений" объектов для сокращения пауз.
- Профилирование: компиляция горячих методов и сохранение профиля между запусками.
- Оптимизации: inlining, devirtualization, escape analysis и др., применяются тогда, когда условия для них доказуемо выполняются.

## Answer (EN)

**Android Runtime (ART)** is a managed execution environment that combines multiple execution modes: an interpreter for initial runs, a JIT compiler for hot code paths, and an AOT compiler for pre-compilation at install/update time (driven by profiles and policy). It uses a modern multi-space (image/zygote/alloc/large) garbage collector with incremental and concurrent algorithms, incorporating generational/region-based ideas to minimize pause times.

**ART Architecture (simplified):**

```text
APK/DEX → ClassLoader → Verifier → Interpreter/JIT/AOT ↔ GC → Native Code
```

(GC runs alongside execution and is not limited to "after" compilation.)

**DEX Format:** Register-based bytecode (more compact than stack-based Java bytecode):

```kotlin
// Source code
fun add(a: Int, b: Int): Int = a + b

// Simplified DEX bytecode example
method add(II)I
    .registers 3
    add-int v0, p1, p2    // ✅ Register-based model
    return v0
```

**Execution Modes:**

- **Interpreter** — executes bytecode directly with no upfront compilation cost.
- **JIT** — compiles hot methods in the background based on profiling data (hotness thresholds and heuristics are version-dependent; "~10k" should be treated as an order of magnitude, not a fixed rule).
- **AOT** — compiles selected methods at install/update time according to profiles and the chosen compilation filter.

**AOT Compilation Filters (simplified view):**

```kotlin
enum class CompilationFilter {
    QUICKEN,         // Optimize/annotate DEX to speed up interpretation
    SPEED_PROFILE,   // ✅ Compile profiled hot methods
    SPEED,           // More aggressive compilation for execution speed
    EVERYTHING       // Maximum AOT compilation (potentially slower install/update)
}
// Typical default on modern devices: SPEED_PROFILE (exact behavior may vary by Android version/OEM)
```

(The actual set/semantics can differ between Android releases; this is illustrative.)

**Garbage `Collection` and Generational Behavior (conceptual):**

ART uses multiple collectors (e.g., concurrent copying, CMS, space-based) and heap spaces to:
- collect short-lived objects more frequently and cheaply;
- avoid frequently scanning long-lived objects;
- perform much of the work concurrently, reducing stop-the-world pauses.

```kotlin
// Young-like regions: new objects, frequent fast collections
// Old-like/long-lived regions: collected less frequently to reduce full pauses

class GCRegions {
    val youngLike = Region("young")  // Most objects die here
    val oldLike = Region("old")      // Long-lived data
}
```

(Exact generational/region implementation details depend on ART version; key idea: "most objects die young" is exploited.)

**Memory Management (Heap Spaces):**

```kotlin
class MemorySpaces {
    val imageSpace: Space       // ✅ Preloaded, shared framework classes
    val zygoteSpace: Space      // Objects shared across app processes, created before zygote fork
    val allocationSpace: Space  // Main app heap for regular objects
    val largeObjectSpace: Space // Large objects (threshold on the order of ~8-12KB+, typically non-moving)
}
```

(The threshold and exact behavior of LargeObjectSpace are implementation-dependent.)

**Compiler Optimizations (simplified examples):**

```kotlin
// Inlining
inline fun measure(block: () -> Unit) {
    val start = System.nanoTime()
    block()  // ✅ May be inlined at call site by JIT/AOT when profitable
    log("Time: ${System.nanoTime() - start}")
}

// Devirtualization
fun test(obj: Derived) {
    obj.compute()  // ✅ May become a direct call if runtime can prove the exact target type
}

// Escape analysis and stack allocation
fun calculateDistance(x: Int, y: Int): Int {
    val point = Point(x, y)
    // ✅ May be scalar-replaced / stack-allocated if analysis proves it does not escape
    return point.distance()
}
```

**Key Concepts:**
- DEX format: register-based, compact, optimized for ART.
- Multi-tier execution: interpreter → JIT → AOT with profile-guided decisions.
- Advanced GC: multi-space/concurrent collectors exploiting generational behavior to reduce pauses.
- Profiling: hot method detection and persisted profiles influence JIT/AOT.
- Optimizations: inlining, devirtualization, escape analysis, etc., applied when their safety and benefits are proven.

---

## Дополнительные Вопросы (RU)

- Как ART решает, какие методы компилировать JIT на основе профилирования?
- В чем компромиссы между фильтрами компиляции SPEED_PROFILE и SPEED?
- Как поколенческий/региональный GC уменьшает время пауз по сравнению с простыми mark-and-sweep сборщиками?
- Что приводит к продвижению объектов из "молодых" областей в "старые"?
- Как escape-анализ определяет, что объект можно разместить на стеке или заменить скалярными значениями?

## Follow-ups (EN)

- How does ART decide which methods to compile with JIT based on profiling data?
- What are the trade-offs between SPEED_PROFILE and SPEED compilation filters?
- How does generational/region-based GC reduce pause times compared to simple mark-and-sweep collectors?
- What triggers promotion of objects from young-like to old-like regions/spaces?
- How does escape analysis determine if an object can be stack-allocated or scalar-replaced?

## Ссылки (RU)

- https://source.android.com/docs/core/runtime
- https://developer.android.com/topic/performance/memory-overview

## References (EN)

- https://source.android.com/docs/core/runtime
- https://developer.android.com/topic/performance/memory-overview

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-android-runtime-art--android--medium]] - Основы ART и режимы компиляции
- [[q-android-performance-measurement-tools--android--medium]] - Инструменты профилирования

### Связанные (тот Же уровень)
- [[q-android-app-lag-analysis--android--medium]] - Техники анализа производительности

### Продвинутое (сложнее)
- Кастомные classloader-ы и оптимизация динамической загрузки кода
- Управление нативной памятью и оптимизация производительности JNI

## Related Questions (EN)

### Prerequisites (Easier)
- [[q-android-runtime-art--android--medium]] - ART basics and compilation modes
- [[q-android-performance-measurement-tools--android--medium]] - Profiling tools

### Related (Same Level)
- [[q-android-app-lag-analysis--android--medium]] - Performance analysis techniques

### Advanced (Harder)
- Custom classloaders and dynamic code loading optimization
- Native memory management and JNI performance tuning
