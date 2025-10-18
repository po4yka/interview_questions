---
id: 20251016-174805
title: "Jit Compilation Definition / Определение JIT компиляции"
topic: kotlin
difficulty: medium
status: draft
moc: moc-kotlin
related: [q-testing-coroutine-cancellation--kotlin--medium, q-kotlin-vs-java-class-creation--programming-languages--medium, q-kotlin-reified-types--kotlin--hard]
created: 2025-10-15
tags:
  - bytecode
  - compilation
  - jit
  - just-in-time
  - jvm
  - machine-code
  - optimization
  - performance
  - programming-languages
---
# Что такое JIT?

**English**: What is JIT?

## Answer (EN)
**JIT (Just-In-Time compilation)** is a technology where **bytecode is compiled into machine code during runtime** (while the program is executing), rather than before execution.

## How It Works

### Traditional Compilation vs JIT

**Ahead-of-Time (AOT) Compilation:**

```
Source Code → Compiler → Machine Code → Execution
  (.c, .cpp)              (native)      (runs)

Example: C, C++, Rust
- Compiled before distribution
- Platform-specific binary
- Fast execution (already machine code)
```

**Interpretation:**

```
Source Code → Interpreter → Execution
  (.py, .js)              (line by line)

Example: Python (CPython), basic JavaScript
- No compilation step
- Slow execution (interpreted each time)
- Platform-independent source
```

**JIT Compilation:**

```
Source Code → Bytecode → JIT Compiler → Machine Code → Execution
  (.java)      (.class)    (runtime)      (native)      (runs)

Example: Java, Kotlin, C#, modern JavaScript
- Compiled to bytecode first (portable)
- JIT compiles hot code to machine code at runtime
- Adaptive optimization based on actual usage
```

---

## JIT Compilation Process

### Step-by-Step in JVM (Java/Kotlin)

**1. Source to Bytecode:**

```kotlin
// Source code
fun fibonacci(n: Int): Int {
    return if (n <= 1) n
    else fibonacci(n - 1) + fibonacci(n - 2)
}

// ↓ Kotlin compiler compiles to bytecode

// Bytecode (simplified)
// ILOAD 0
// ICONST_1
// IF_ICMPGT L1
// ILOAD 0
// IRETURN
// ...
```

**2. Interpretation (Initially):**

```
First few calls:
fibonacci(5) → Interpreted (slow)
fibonacci(10) → Still interpreted
```

**3. Profiling:**

```
JVM monitors:
- How often is this method called?
- What are the typical argument types?
- Which branches are taken most?
```

**4. JIT Compilation (When Hot):**

```
After many calls:
fibonacci() is "hot" → JIT compiles to native machine code

x86-64 Assembly (example):
mov eax, edi
cmp edi, 1
jle .L2
...
```

**5. Optimized Execution:**

```
Future calls:
fibonacci(20) → Runs native machine code (fast!)
```

---

## Advantages

### 1. Performance Improvement on Frequently Called Code

Code that runs frequently ("hot code") gets optimized:

```kotlin
// Hot loop - called millions of times
fun processData(data: List<Int>): Int {
    var sum = 0
    for (value in data) {  // JIT optimizes this loop
        sum += value * 2
    }
    return sum
}

// First few iterations: Interpreted (~100x slower)
// After warmup: JIT-compiled to native code (fast!)
```

**Performance boost:**
- Interpreted: ~100x slower than native
- JIT-compiled: Close to native speed

### 2. Flexible Optimization for Specific Device

JIT can optimize for the **actual hardware** running the code:

```kotlin
// JIT can use:
// - CPU-specific instructions (SSE, AVX on x86)
// - Platform-specific optimizations
// - Actual runtime data patterns

// On x86 with AVX:
JIT → Use SIMD instructions for loops

// On ARM:
JIT → Use ARM-specific instructions
```

### 3. Adaptive Optimization

JIT observes **actual runtime behavior** and optimizes accordingly:

```kotlin
interface Animal {
    fun makeSound()
}

class Dog : Animal {
    override fun makeSound() = println("Woof")
}

class Cat : Animal {
    override fun makeSound() = println("Meow")
}

fun callAnimal(animal: Animal) {
    animal.makeSound()  // Polymorphic call
}

// If callAnimal() is always called with Dog instances:
// JIT can speculate and inline Dog.makeSound() directly
// (with deoptimization fallback if Cat ever appears)
```

**Optimizations:**
- Method inlining
- Dead code elimination
- Loop unrolling
- Escape analysis
- Speculative optimization

---

## Disadvantages

### 1. Warmup Time

**Cold start performance** is slower:

```kotlin
fun main() {
    val start = System.currentTimeMillis()

    // First 1000 iterations: SLOW (interpreted)
    repeat(1000) {
        fibonacci(20)
    }

    val warmup = System.currentTimeMillis()
    println("Warmup: ${warmup - start}ms")  // ~500ms

    // Next 1000 iterations: FAST (JIT-compiled)
    repeat(1000) {
        fibonacci(20)
    }

    val optimized = System.currentTimeMillis()
    println("Optimized: ${optimized - warmup}ms")  // ~50ms
}
```

### 2. Memory Overhead

JIT compiler itself consumes memory:

```
Application memory:     100 MB
JIT compiler overhead:  +20 MB
JIT-compiled code:      +10 MB
Total:                  130 MB
```

### 3. Unpredictable Performance

Performance varies based on warmup state:

```kotlin
// Scenario 1: Long-running server
// - Warmup once at startup
// - Consistent fast performance after

// Scenario 2: Short-lived CLI tool
// - Exits before JIT optimizations kick in
// - Always pays interpretation cost
```

---

## JIT in Different Platforms

### Java/Kotlin (HotSpot JVM)

```kotlin
// Tiered compilation (default)
// Tier 0: Interpreter
// Tier 1: C1 (client) compiler - fast compilation, basic optimizations
// Tier 2-3: Profile-guided optimization
// Tier 4: C2 (server) compiler - slow compilation, aggressive optimizations

// JVM flags
-XX:+TieredCompilation         // Enable tiered (default)
-XX:TieredStopAtLevel=1        // Stop at C1 (fast startup)
-XX:CompileThreshold=10000     // Invocations before JIT (default)
```

**Example:**

```kotlin
fun compute(x: Int) = x * x + 2 * x + 1

// Invocation count: 0-1000 → Tier 0 (Interpreted)
// Invocation count: 1000-10000 → Tier 1 (C1)
// Invocation count: 10000+ → Tier 4 (C2, fully optimized)
```

### JavaScript (V8, SpiderMonkey)

```javascript
// V8 JIT pipeline:
// 1. Ignition (interpreter)
// 2. TurboFan (optimizing compiler)

function add(a, b) {
    return a + b;
}

// First calls: Ignition interprets
// After many calls: TurboFan compiles to optimized code

// Type feedback:
add(1, 2)      // TurboFan learns: integers
add(3, 4)      // Optimizes for integer addition
add("a", "b")  // Deoptimizes! (now handling strings)
```

### C# (.NET CLR)

```csharp
// RyuJIT compiler
// - Compiles all methods on first call
// - Progressive optimization for hot methods

public int Factorial(int n) {
    return n <= 1 ? 1 : n * Factorial(n - 1);
}

// First call: JIT compiles to native code
// Hot method: Re-JIT with aggressive optimizations
```

### Android (ART)

```kotlin
// Android Runtime (ART) uses:
// - AOT compilation on app install
// - JIT compilation for new/changed code
// - Profile-guided compilation

// On install:
App → dex2oat (AOT) → native code

// During runtime:
Hot code → JIT → profile data

// On idle/charging:
Profile data → dex2oat → optimized AOT code
```

---

## JIT vs AOT Comparison

| Feature | JIT | AOT |
|---------|-----|-----|
| **Compilation time** | Runtime | Before execution |
| **Startup time** | Slower (warmup) | Faster (ready to run) |
| **Peak performance** | Excellent | Good |
| **Optimization** | Runtime profiling | Static analysis |
| **Code size** | Smaller (bytecode) | Larger (machine code) |
| **Platform** | Cross-platform | Platform-specific |
| **Memory usage** | Higher (compiler + code) | Lower |
| **Adaptability** | Adapts to usage patterns | Fixed optimization |

---

## Practical Examples

### Observing JIT in Action

```kotlin
fun benchmark(name: String, iterations: Int, block: () -> Unit) {
    val start = System.nanoTime()
    repeat(iterations) { block() }
    val duration = (System.nanoTime() - start) / 1_000_000
    println("$name: ${duration}ms")
}

fun heavyComputation(n: Int): Long {
    var result = 0L
    for (i in 0 until n) {
        result += (i * i) % 1000
    }
    return result
}

fun main() {
    // Warmup phase (interpreted/C1)
    benchmark("Warmup", 1000) {
        heavyComputation(10000)
    }
    // Output: ~500ms

    // After JIT (C2 optimized)
    benchmark("Optimized", 1000) {
        heavyComputation(10000)
    }
    // Output: ~50ms (10x faster!)
}
```

### Deoptimization Example

```kotlin
fun process(value: Any): Int {
    return when (value) {
        is Int -> value * 2
        is String -> value.length
        else -> 0
    }
}

// Initially called with Ints only:
repeat(10000) { process(42) }
// JIT optimizes assuming Int input

// Suddenly called with String:
process("hello")
// JIT deoptimizes! Falls back to interpreter
// Then re-optimizes for both Int and String
```

---

## When JIT Excels

- Long-running applications (servers, desktop apps)
- Workloads with hot paths
- Applications with complex object interactions
- Cross-platform deployments

## When AOT is Better

- Short-lived CLI tools
- Embedded systems (limited resources)
- Predictable performance requirements
- Mobile apps (faster startup)

---

## Summary

**JIT (Just-In-Time) Compilation:**
- Compiles bytecode to machine code **during runtime**
- Optimizes frequently executed ("hot") code
- Adapts to actual runtime behavior

**Advantages:**
- Performance boost for hot code (near-native speed)
- Flexible optimization for specific hardware
- Adaptive optimization based on profiling
- Cross-platform (bytecode is portable)

**Disadvantages:**
- Warmup time (slow start)
- Memory overhead (compiler + compiled code)
- Unpredictable performance (depends on warmup)

**Used in:**
- Java/Kotlin (HotSpot JVM)
- JavaScript (V8, SpiderMonkey)
- C# (.NET CLR)
- Python (PyPy)
- Android (ART)

**Best for:** Long-running applications that benefit from runtime profiling and adaptive optimization.

## Ответ (RU)


JIT (Just-In-Time) компиляция компилирует код в машинный код во время выполнения, а не заранее (AOT).

### Как работает JIT

**1. Сначала интерпретация**
```
Исходный код → Bytecode → Интерпретатор
                       ↓
                  JIT Компилятор
                       ↓
                  Машинный код
```

**2. Обнаружение горячих путей**
- JIT идентифицирует часто выполняемый код ("горячие точки")
- Компилирует горячие пути в нативный машинный код
- Оптимизирует на основе профилирования во время выполнения

### JIT в Kotlin/JVM

**Bytecode в Native**
```kotlin
fun fibonacci(n: Int): Int {
    return if (n <= 1) n
    else fibonacci(n - 1) + fibonacci(n - 2)
}

// Первые вызовы: Интерпретируются
// После порога: JIT компилируется в машинный код
```

**HotSpot JVM Tiered Compilation**
```
Уровень 0: Интерпретатор
Уровень 1: C1 Компилятор (Client, быстрая компиляция)
Уровень 2-3: Профилирование
Уровень 4: C2 Компилятор (Server, агрессивная оптимизация)
```

### Преимущества
- Быстрый старт (сначала интерпретация)
- Оптимизации во время выполнения
- Адаптация к реальным паттернам использования

### Недостатки
- Нужно время прогрева
- Накладные расходы памяти
- Недетерминированная производительность

---
---

## Процесс JIT компиляции

### Пошаговый процесс в JVM (Java/Kotlin)

**1. Исходный код в байткод:**

```kotlin
// Исходный код
fun fibonacci(n: Int): Int {
    return if (n <= 1) n
    else fibonacci(n - 1) + fibonacci(n - 2)
}

// ↓ Kotlin компилятор компилирует в байткод

// Байткод (упрощенно)
// ILOAD 0
// ICONST_1
// IF_ICMPGT L1
// ILOAD 0
// IRETURN
// ...
```

**2. Интерпретация (изначально):**

```
Первые несколько вызовов:
fibonacci(5) → Интерпретируется (медленно)
fibonacci(10) → Всё ещё интерпретируется
```

**3. Профилирование:**

```
JVM отслеживает:
- Как часто вызывается этот метод?
- Какие типы аргументов обычно используются?
- Какие ветви выполняются чаще?
```

**4. JIT компиляция (когда код "горячий"):**

```
После многих вызовов:
fibonacci() становится "горячим" → JIT компилирует в нативный машинный код

x86-64 Ассемблер (пример):
mov eax, edi
cmp edi, 1
jle .L2
...
```

**5. Оптимизированное выполнение:**

```
Будущие вызовы:
fibonacci(20) → Выполняется нативный машинный код (быстро!)
```

---

## Преимущества

### 1. Улучшение производительности часто вызываемого кода

Код, который выполняется часто ("горячий код"), оптимизируется:

```kotlin
// Горячий цикл - вызывается миллионы раз
fun processData(data: List<Int>): Int {
    var sum = 0
    for (value in data) {  // JIT оптимизирует этот цикл
        sum += value * 2
    }
    return sum
}

// Первые несколько итераций: Интерпретация (~100x медленнее)
// После прогрева: JIT-компилированный в нативный код (быстро!)
```

**Прирост производительности:**
- Интерпретируемый: ~100x медленнее чем нативный
- JIT-компилированный: Близко к нативной скорости

### 2. Гибкая оптимизация под конкретное устройство

JIT может оптимизировать под **реальное железо**, на котором выполняется код:

```kotlin
// JIT может использовать:
// - CPU-специфичные инструкции (SSE, AVX на x86)
// - Платформо-специфичные оптимизации
// - Реальные паттерны данных во время выполнения

// На x86 с AVX:
JIT → Использует SIMD инструкции для циклов

// На ARM:
JIT → Использует ARM-специфичные инструкции
```

### 3. Адаптивная оптимизация

JIT наблюдает за **реальным поведением во время выполнения** и оптимизирует соответственно:

```kotlin
interface Animal {
    fun makeSound()
}

class Dog : Animal {
    override fun makeSound() = println("Woof")
}

class Cat : Animal {
    override fun makeSound() = println("Meow")
}

fun callAnimal(animal: Animal) {
    animal.makeSound()  // Полиморфный вызов
}

// Если callAnimal() всегда вызывается с экземплярами Dog:
// JIT может спекулятивно встроить Dog.makeSound() напрямую
// (с откатом деоптимизации, если появится Cat)
```

**Оптимизации:**
- Встраивание методов (inlining)
- Удаление мертвого кода
- Разворачивание циклов
- Анализ escape
- Спекулятивная оптимизация

---

## Недостатки

### 1. Время прогрева

**Производительность холодного старта** медленнее:

```kotlin
fun main() {
    val start = System.currentTimeMillis()

    // Первые 1000 итераций: МЕДЛЕННО (интерпретируются)
    repeat(1000) {
        fibonacci(20)
    }

    val warmup = System.currentTimeMillis()
    println("Прогрев: ${warmup - start}ms")  // ~500ms

    // Следующие 1000 итераций: БЫСТРО (JIT-компилированные)
    repeat(1000) {
        fibonacci(20)
    }

    val optimized = System.currentTimeMillis()
    println("Оптимизировано: ${optimized - warmup}ms")  // ~50ms
}
```

### 2. Накладные расходы по памяти

Сам JIT компилятор потребляет память:

```
Память приложения:     100 МБ
Накладные расходы JIT:  +20 МБ
JIT-компилированный код: +10 МБ
Всего:                  130 МБ
```

### 3. Непредсказуемая производительность

Производительность варьируется в зависимости от состояния прогрева:

```kotlin
// Сценарий 1: Долгоработающий сервер
// - Прогревается один раз при запуске
// - Стабильная быстрая производительность после

// Сценарий 2: Короткоживущий CLI инструмент
// - Завершается до того, как включатся JIT оптимизации
// - Всегда платит за интерпретацию
```

---

## JIT на разных платформах

### Java/Kotlin (HotSpot JVM)

```kotlin
// Многоуровневая компиляция (по умолчанию)
// Уровень 0: Интерпретатор
// Уровень 1: C1 (клиентский) компилятор - быстрая компиляция, базовые оптимизации
// Уровни 2-3: Оптимизация на основе профиля
// Уровень 4: C2 (серверный) компилятор - медленная компиляция, агрессивные оптимизации

// Флаги JVM
-XX:+TieredCompilation         // Включить многоуровневую (по умолчанию)
-XX:TieredStopAtLevel=1        // Остановиться на C1 (быстрый запуск)
-XX:CompileThreshold=10000     // Вызовов до JIT (по умолчанию)
```

**Пример:**

```kotlin
fun compute(x: Int) = x * x + 2 * x + 1

// Количество вызовов: 0-1000 → Уровень 0 (Интерпретируется)
// Количество вызовов: 1000-10000 → Уровень 1 (C1)
// Количество вызовов: 10000+ → Уровень 4 (C2, полностью оптимизировано)
```

### JavaScript (V8, SpiderMonkey)

```javascript
// Пайплайн JIT в V8:
// 1. Ignition (интерпретатор)
// 2. TurboFan (оптимизирующий компилятор)

function add(a, b) {
    return a + b;
}

// Первые вызовы: Ignition интерпретирует
// После многих вызовов: TurboFan компилирует в оптимизированный код

// Обратная связь по типам:
add(1, 2)      // TurboFan узнаёт: целые числа
add(3, 4)      // Оптимизирует для сложения целых
add("a", "b")  // Деоптимизирует! (теперь обрабатывает строки)
```

### C# (.NET CLR)

```csharp
// RyuJIT компилятор
// - Компилирует все методы при первом вызове
// - Прогрессивная оптимизация для горячих методов

public int Factorial(int n) {
    return n <= 1 ? 1 : n * Factorial(n - 1);
}

// Первый вызов: JIT компилирует в нативный код
// Горячий метод: Повторная JIT с агрессивными оптимизациями
```

### Android (ART)

```kotlin
// Android Runtime (ART) использует:
// - AOT компиляцию при установке приложения
// - JIT компиляцию для нового/измененного кода
// - Компиляцию на основе профиля

// При установке:
Приложение → dex2oat (AOT) → нативный код

// Во время выполнения:
Горячий код → JIT → данные профиля

// В режиме простоя/зарядки:
Данные профиля → dex2oat → оптимизированный AOT код
```

---

## Сравнение JIT vs AOT

| Характеристика | JIT | AOT |
|----------------|-----|-----|
| **Время компиляции** | Во время выполнения | До выполнения |
| **Время запуска** | Медленнее (прогрев) | Быстрее (готов к работе) |
| **Пиковая производительность** | Отличная | Хорошая |
| **Оптимизация** | Профилирование во время выполнения | Статический анализ |
| **Размер кода** | Меньше (байткод) | Больше (машинный код) |
| **Платформа** | Кросс-платформенный | Платформо-специфичный |
| **Использование памяти** | Выше (компилятор + код) | Ниже |
| **Адаптивность** | Адаптируется к паттернам использования | Фиксированная оптимизация |

---

## Практические примеры

### Наблюдение за JIT в действии

```kotlin
fun benchmark(name: String, iterations: Int, block: () -> Unit) {
    val start = System.nanoTime()
    repeat(iterations) { block() }
    val duration = (System.nanoTime() - start) / 1_000_000
    println("$name: ${duration}ms")
}

fun heavyComputation(n: Int): Long {
    var result = 0L
    for (i in 0 until n) {
        result += (i * i) % 1000
    }
    return result
}

fun main() {
    // Фаза прогрева (интерпретация/C1)
    benchmark("Прогрев", 1000) {
        heavyComputation(10000)
    }
    // Вывод: ~500ms

    // После JIT (оптимизировано C2)
    benchmark("Оптимизировано", 1000) {
        heavyComputation(10000)
    }
    // Вывод: ~50ms (в 10 раз быстрее!)
}
```

### Пример деоптимизации

```kotlin
fun process(value: Any): Int {
    return when (value) {
        is Int -> value * 2
        is String -> value.length
        else -> 0
    }
}

// Изначально вызывается только с Int:
repeat(10000) { process(42) }
// JIT оптимизирует предполагая Int на входе

// Внезапно вызывается с String:
process("hello")
// JIT деоптимизирует! Возвращается к интерпретатору
// Затем повторно оптимизирует для Int и String
```

---

## Когда JIT превосходит

- Долгоработающие приложения (серверы, десктопные приложения)
- Рабочие нагрузки с горячими путями
- Приложения со сложными объектными взаимодействиями
- Кросс-платформенные развертывания

## Когда AOT лучше

- Короткоживущие CLI инструменты
- Встраиваемые системы (ограниченные ресурсы)
- Требования к предсказуемой производительности
- Мобильные приложения (быстрый запуск)

---

## Резюме

**JIT (Just-In-Time) компиляция:**
- Компилирует байткод в машинный код **во время выполнения**
- Оптимизирует часто выполняемый ("горячий") код
- Адаптируется к реальному поведению во время выполнения

**Преимущества:**
- Прирост производительности для горячего кода (близко к нативной скорости)
- Гибкая оптимизация под конкретное железо
- Адаптивная оптимизация на основе профилирования
- Кросс-платформенность (байткод портируемый)

**Недостатки:**
- Время прогрева (медленный старт)
- Накладные расходы по памяти (компилятор + скомпилированный код)
- Непредсказуемая производительность (зависит от прогрева)

**Используется в:**
- Java/Kotlin (HotSpot JVM)
- JavaScript (V8, SpiderMonkey)
- C# (.NET CLR)
- Python (PyPy)
- Android (ART)

**Лучше всего для:** Долгоработающих приложений, которые выигрывают от профилирования во время выполнения и адаптивной оптимизации.

## Related Questions

- [[q-testing-coroutine-cancellation--kotlin--medium]]
- [[q-kotlin-vs-java-class-creation--programming-languages--medium]]
- [[q-kotlin-reified-types--kotlin--hard]]
