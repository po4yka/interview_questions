---
id: 20251012-100000
title: "Kotlin Inline Functions / Inline функции в Kotlin"
aliases: []

# Classification
topic: kotlin
subtopics: [inline-functions, performance, lambdas, reified, optimization]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Created for vault completeness

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-kotlin-lambda-expressions--kotlin--medium, q-kotlin-higher-order-functions--kotlin--medium, q-reified-type-parameters--kotlin--medium, q-crossinline-keyword--kotlin--medium, q-inline-function-limitations--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [kotlin, inline-functions, performance, lambdas, reified, optimization, difficulty/medium]
---

# Question (EN)
> What are inline functions in Kotlin? Explain their purpose, benefits, modifiers (noinline, crossinline), limitations, and provide practical examples with performance analysis.

# Вопрос (RU)
> Что такое inline функции в Kotlin? Объясните их назначение, преимущества, модификаторы (noinline, crossinline), ограничения и приведите практические примеры с анализом производительности.

---

## Answer (EN)

Inline functions are a powerful Kotlin feature that instructs the compiler to insert the function's bytecode directly at each call site instead of creating a separate function call. This eliminates function call overhead and enables advanced features like reified type parameters.

### Why Inline Functions Exist

In Kotlin, lambda expressions are typically compiled to anonymous class instances (Function0, Function1, etc.). Each lambda creates an object, which:
1. Allocates memory on the heap
2. Adds pressure to the garbage collector
3. Creates indirection through function call overhead

**Problem without inline**:
```kotlin
// Regular higher-order function
fun repeat(times: Int, action: () -> Unit) {
    for (i in 0 until times) {
        action()  // Indirect call through Function object
    }
}

// Usage
repeat(5) {
    println("Hello")
}

// Compiles to something like:
Function0 action = new Function0() {
    public void invoke() {
        System.out.println("Hello");
    }
};
for (int i = 0; i < 5; i++) {
    action.invoke();  // Object allocation + indirect call
}
```

**Solution with inline**:
```kotlin
inline fun repeat(times: Int, action: () -> Unit) {
    for (i in 0 until times) {
        action()  // Lambda body inlined directly
    }
}

// Same usage
repeat(5) {
    println("Hello")
}

// Compiles to:
for (int i = 0; i < 5; i++) {
    System.out.println("Hello");  // Direct code, no allocation!
}
```

### How Inline Functions Work

The compiler performs **copy-pasting** of both the function body and lambda bodies at the call site:

```kotlin
inline fun measureTime(block: () -> Unit): Long {
    val start = System.nanoTime()
    block()
    val end = System.nanoTime()
    return end - start
}

// Call site
val time = measureTime {
    println("Doing work")
    Thread.sleep(100)
}

// After inlining (conceptual):
val start = System.nanoTime()
println("Doing work")
Thread.sleep(100)
val end = System.nanoTime()
val time = end - start
```

### Benefits of Inline Functions

#### 1. Eliminates Function Call Overhead

```kotlin
// Performance benchmark
inline fun inlined(operation: () -> Int): Int {
    return operation()
}

fun notInlined(operation: () -> Int): Int {
    return operation()
}

fun benchmark() {
    val iterations = 100_000_000

    // With inline - ~200ms
    var result = 0
    val start1 = System.currentTimeMillis()
    repeat(iterations) {
        result += inlined { 1 }
    }
    println("Inline: ${System.currentTimeMillis() - start1}ms")

    // Without inline - ~600ms (3x slower!)
    result = 0
    val start2 = System.currentTimeMillis()
    repeat(iterations) {
        result += notInlined { 1 }
    }
    println("Not inline: ${System.currentTimeMillis() - start2}ms")
}
```

#### 2. Avoids Lambda Object Allocation

```kotlin
// Memory allocation comparison
class MemoryTest {
    // Without inline - creates Function object every call
    fun processItems(items: List<String>, transform: (String) -> String): List<String> {
        return items.map(transform)  // Function object allocated
    }

    // With inline - no allocation
    inline fun processItemsInline(items: List<String>, transform: (String) -> String): List<String> {
        return items.map(transform)  // Lambda code inlined
    }
}

// Calling 1000 times:
// processItems: Allocates 1000 Function objects → GC pressure
// processItemsInline: Zero allocations → No GC impact
```

#### 3. Enables Reified Type Parameters

Only inline functions can use `reified`, allowing access to type information at runtime:

```kotlin
// Without reified - doesn't work
fun <T> isInstanceOf(value: Any): Boolean {
    return value is T  //  Error: Cannot check for erased type
}

// With inline + reified - works!
inline fun <reified T> isInstanceOf(value: Any): Boolean {
    return value is T  //  Type check works!
}

// Practical examples
inline fun <reified T> List<*>.filterIsInstance(): List<T> {
    return this.filter { it is T }.map { it as T }
}

val mixed: List<Any> = listOf("hello", 42, "world", 3.14)
val strings: List<String> = mixed.filterIsInstance<String>()
// Result: ["hello", "world"]

inline fun <reified T> Gson.fromJson(json: String): T {
    return fromJson(json, T::class.java)
}

val user: User = gson.fromJson<User>(jsonString)
```

#### 4. Allows Non-Local Returns

In inline functions, lambda can use `return` to exit the enclosing function:

```kotlin
// Non-local return example
fun findFirstNegative(numbers: List<Int>): Int? {
    numbers.forEach { number ->  // forEach is inline
        if (number < 0) {
            return number  // Returns from findFirstNegative, not lambda
        }
    }
    return null
}

val result = findFirstNegative(listOf(1, 2, -3, 4))
// Returns -3 and exits the entire function

// Without inline, this wouldn't compile:
fun findFirstNegativeCustom(numbers: List<Int>): Int? {
    myForEach(numbers) { number ->  // myForEach is NOT inline
        if (number < 0) {
            return number  //  Error: 'return' not allowed here
        }
    }
    return null
}
```

### Complete Practical Examples

#### Example 1: Synchronized Block Implementation

```kotlin
// Standard library implementation
inline fun <R> synchronized(lock: Any, block: () -> R): R {
    @Suppress("NON_PUBLIC_CALL_FROM_PUBLIC_INLINE")
    kotlin.jvm.internal.Intrinsics.monitor.enter(lock)
    try {
        return block()
    } finally {
        kotlin.jvm.internal.Intrinsics.monitor.exit(lock)
    }
}

// Usage
class Counter {
    private val lock = Any()
    private var count = 0

    fun increment() {
        synchronized(lock) {
            count++
        }
    }

    fun get(): Int = synchronized(lock) { count }
}

// Inlines to:
fun increment() {
    kotlin.jvm.internal.Intrinsics.monitor.enter(lock)
    try {
        count++
    } finally {
        kotlin.jvm.internal.Intrinsics.monitor.exit(lock)
    }
}
```

#### Example 2: Use-Resource Pattern (try-with-resources)

```kotlin
inline fun <T : Closeable, R> T.use(block: (T) -> R): R {
    var exception: Throwable? = null
    try {
        return block(this)
    } catch (e: Throwable) {
        exception = e
        throw e
    } finally {
        when {
            exception == null -> close()
            else -> try {
                close()
            } catch (closeException: Throwable) {
                exception.addSuppressed(closeException)
            }
        }
    }
}

// Usage
fun readFirstLine(path: String): String {
    BufferedReader(FileReader(path)).use { reader ->
        return reader.readLine()  // Non-local return works!
    }
    // File automatically closed
}

// Alternative with explicit return
fun processFile(path: String): Result<String> {
    return BufferedReader(FileReader(path)).use { reader ->
        val content = reader.readText()
        Result.success(content)
    }
}
```

#### Example 3: Measurement and Profiling

```kotlin
inline fun <T> measureTimeMillis(block: () -> T): Pair<T, Long> {
    val start = System.currentTimeMillis()
    val result = block()
    val time = System.currentTimeMillis() - start
    return result to time
}

inline fun <T> measureNanos(block: () -> T): Pair<T, Long> {
    val start = System.nanoTime()
    val result = block()
    val time = System.nanoTime() - start
    return result to time
}

// Usage
fun complexOperation(): List<Int> {
    val (result, timeMs) = measureTimeMillis {
        (1..1000000).filter { it % 2 == 0 }.map { it * it }
    }
    println("Operation took ${timeMs}ms")
    return result
}

// Memory profiling
inline fun <T> measureMemory(block: () -> T): Pair<T, Long> {
    System.gc()
    val runtime = Runtime.getRuntime()
    val before = runtime.totalMemory() - runtime.freeMemory()
    val result = block()
    System.gc()
    val after = runtime.totalMemory() - runtime.freeMemory()
    return result to (after - before)
}
```

#### Example 4: DSL Builders

```kotlin
// HTML DSL with inline
class HTML {
    private val children = mutableListOf<String>()

    inline fun body(init: BODY.() -> Unit) {
        val body = BODY()
        body.init()  // Lambda inlined
        children.add(body.toString())
    }

    override fun toString() = "<html>${children.joinToString("")}</html>"
}

class BODY {
    private val children = mutableListOf<String>()

    inline fun h1(text: String) {
        children.add("<h1>$text</h1>")
    }

    inline fun p(init: () -> String) {
        children.add("<p>${init()}</p>")  // Lambda inlined
    }

    override fun toString() = "<body>${children.joinToString("")}</body>"
}

// Usage - very clean syntax thanks to inlining
fun createPage() = HTML().apply {
    body {
        h1("Welcome")
        p { "This is a paragraph" }
        p { "Another paragraph" }
    }
}.toString()
```

#### Example 5: Conditional Execution

```kotlin
inline fun <T> T.applyIf(condition: Boolean, block: T.() -> Unit): T {
    if (condition) {
        block()
    }
    return this
}

inline fun <T> T.also If(condition: Boolean, block: (T) -> Unit): T {
    if (condition) {
        block(this)
    }
    return this
}

// Usage
val user = User("John", 25)
    .applyIf(isDebugMode) {
        println("Debug: Created user $this")
    }
    .applyIf(age < 18) {
        isMinor = true
    }

val list = mutableListOf(1, 2, 3)
    .alsoIf(shouldLog) { println("List contents: $it") }
    .alsoIf(shouldSort) { it.sort() }
```

### The noinline Modifier

Sometimes you need to prevent specific lambda parameters from being inlined:

```kotlin
inline fun performOperation(
    inlinedAction: () -> Unit,
    noinline notInlinedAction: () -> Unit
) {
    inlinedAction()  //  Inlined at call site
    notInlinedAction()  //  Not inlined, treated as regular lambda
}
```

**When to use noinline**:

#### 1. Storing Lambda for Later Use

```kotlin
class EventBus {
    private val listeners = mutableListOf<() -> Unit>()

    // Can't inline because we store the lambda
    inline fun register(noinline listener: () -> Unit) {
        listeners.add(listener)  // Need actual Function object to store
    }

    fun notify() {
        listeners.forEach { it() }
    }
}

// Usage
val bus = EventBus()
bus.register { println("Event fired!") }
bus.notify()
```

#### 2. Passing Lambda to Non-Inline Function

```kotlin
inline fun processAsync(
    data: String,
    noinline onComplete: (Result<String>) -> Unit
) {
    // Can't inline because coroutine launch needs Function object
    GlobalScope.launch {
        delay(1000)
        onComplete(Result.success(data))
    }
}
```

#### 3. Higher-Order Function Composition

```kotlin
inline fun <T, R> List<T>.myMap(
    noinline transform: (T) -> R
): List<R> {
    val result = mutableListOf<R>()
    forEach { item ->
        // Need Function object to pass to another function
        result.add(transform(item))
    }
    return result
}
```

### The crossinline Modifier

`crossinline` prevents non-local returns in lambdas that are called in a different context:

```kotlin
inline fun runInThread(crossinline block: () -> Unit) {
    Thread {
        block()  // Called in different context (new thread)
    }.start()
}

fun test() {
    runInThread {
        println("In thread")
        // return  //  Compiler error: 'return' not allowed here
    }
    println("After runInThread")  // Always executes
}
```

**Without crossinline**, this would be dangerous:

```kotlin
// Dangerous version without crossinline
inline fun runInThreadDangerous(block: () -> Unit) {
    Thread {
        block()  // If block contains 'return', what should it return from?
    }.start()
}

fun test() {
    runInThreadDangerous {
        return  // Return from test()? From lambda? From thread? Unclear!
    }
}
```

**Complete example**:

```kotlin
class TaskExecutor {
    inline fun executeAsync(crossinline task: () -> Unit) {
        Thread {
            try {
                task()
            } catch (e: Exception) {
                println("Task failed: ${e.message}")
            }
        }.start()
    }

    inline fun executeWithCallback(
        crossinline task: () -> String,
        crossinline onResult: (String) -> Unit
    ) {
        Thread {
            val result = task()
            onResult(result)
        }.start()
    }
}

// Usage
val executor = TaskExecutor()

fun processData() {
    executor.executeAsync {
        println("Processing in background")
        // return  // Not allowed - crossinline prevents this
    }

    executor.executeWithCallback(
        task = {
            "Data processed"
            // return "result"  // Not allowed
        },
        onResult = { result ->
            println("Got result: $result")
        }
    )
}
```

### Combining noinline and crossinline

```kotlin
inline fun complexOperation(
    normalLambda: () -> Unit,                    // Fully inlined
    noinline storedLambda: () -> Unit,          // Not inlined, can be stored
    crossinline asyncLambda: () -> Unit         // Inlined but no non-local returns
) {
    // Normal lambda - fully inlined
    normalLambda()

    // Noinline lambda - can store it
    val stored = storedLambda
    callLater(stored)

    // Crossinline lambda - inlined but restricted returns
    GlobalScope.launch {
        asyncLambda()
    }
}
```

### Limitations and Considerations

#### 1. Code Size Increase

Inlining copies code to every call site, increasing bytecode size:

```kotlin
inline fun largeFunction(block: () -> Unit) {
    // 100 lines of code
    println("Starting operation")
    println("Step 1")
    // ... many lines ...
    block()
    // ... many more lines ...
    println("Operation complete")
}

// Called 50 times in your code
// → 50 copies of largeFunction's body in bytecode
// → Significantly larger APK/JAR
```

**Guideline**: Only inline small functions (typically 1-3 lines) or functions with lambda parameters.

#### 2. Can't Be Virtual (open, override, abstract)

```kotlin
open class Base {
    //  Error: inline functions can't be open
    open inline fun operation(block: () -> Unit) {
        block()
    }
}

interface Processor {
    //  Error: inline functions can't be abstract
    inline fun process(data: String): String
}
```

**Reason**: Inlining happens at compile time, but virtual dispatch is runtime.

#### 3. Can't Access Private Members of Call Site

```kotlin
class MyClass {
    private val secret = "hidden"

    inline fun accessSecret() {
        println(secret)  //  Error when inlined at external call site
    }
}
```

#### 4. Recursive Inline Functions

```kotlin
//  Warning: Recursive inline function may cause stack overflow
inline fun factorial(n: Int): Int {
    return if (n <= 1) 1 else n * factorial(n - 1)
}
// Each recursive call inlines the entire function → exponential code growth
```

### Performance Analysis

#### Benchmark: Higher-Order Function Overhead

```kotlin
fun benchmarkInlinePerformance() {
    val iterations = 10_000_000

    // Test 1: Direct code
    var result = 0
    var start = System.nanoTime()
    repeat(iterations) {
        result += 1
    }
    val directTime = System.nanoTime() - start
    println("Direct: ${directTime / 1_000_000}ms")

    // Test 2: Inline function
    result = 0
    start = System.nanoTime()
    inline fun inlineAdd(n: Int, operation: (Int) -> Int): Int {
        return operation(n)
    }
    repeat(iterations) {
        result = inlineAdd(result) { it + 1 }
    }
    val inlineTime = System.nanoTime() - start
    println("Inline: ${inlineTime / 1_000_000}ms")

    // Test 3: Regular function
    result = 0
    start = System.nanoTime()
    fun regularAdd(n: Int, operation: (Int) -> Int): Int {
        return operation(n)
    }
    repeat(iterations) {
        result = regularAdd(result) { it + 1 }
    }
    val regularTime = System.nanoTime() - start
    println("Regular: ${regularTime / 1_000_000}ms")

    // Results on typical hardware:
    // Direct:  ~10ms   (baseline)
    // Inline:  ~12ms   (20% overhead from inlining complexity)
    // Regular: ~150ms  (15x slower due to lambda allocation)
}
```

#### Memory Allocation Benchmark

```kotlin
fun benchmarkMemoryAllocation() {
    val iterations = 1_000_000

    // Force garbage collection
    System.gc()
    Thread.sleep(100)

    val runtime = Runtime.getRuntime()
    val beforeInline = runtime.totalMemory() - runtime.freeMemory()

    // Test with inline
    var result = 0
    inline fun inlineOperation(block: () -> Int): Int = block()
    repeat(iterations) {
        result += inlineOperation { 1 }
    }

    System.gc()
    Thread.sleep(100)
    val afterInline = runtime.totalMemory() - runtime.freeMemory()
    val inlineMemory = afterInline - beforeInline

    // Test without inline
    System.gc()
    Thread.sleep(100)
    val beforeRegular = runtime.totalMemory() - runtime.freeMemory()

    result = 0
    fun regularOperation(block: () -> Int): Int = block()
    repeat(iterations) {
        result += regularOperation { 1 }
    }

    System.gc()
    Thread.sleep(100)
    val afterRegular = runtime.totalMemory() - runtime.freeMemory()
    val regularMemory = afterRegular - beforeRegular

    println("Inline memory: ${inlineMemory / 1024}KB")
    println("Regular memory: ${regularMemory / 1024}KB")
    // Inline: ~0KB (no allocations)
    // Regular: ~40MB (Function object per call)
}
```

### When to Use Inline Functions

 **DO use inline for**:
- Higher-order functions with lambda parameters
- Functions that need reified type parameters
- Small utility functions (1-3 lines)
- Performance-critical hot paths
- DSL builders
- Resource management (use, synchronized)

 **DON'T use inline for**:
- Large functions (increases code size)
- Virtual functions (open, override, abstract)
- Recursive functions
- Functions where lambda allocation is negligible
- Public API functions (can't change signature later)

### Best Practices

1. **Inline small, frequently-called functions**:
```kotlin
//  Good
inline fun <T> T.applyIf(condition: Boolean, block: T.() -> Unit): T {
    if (condition) block()
    return this
}

//  Bad - too large to inline
inline fun processLargeData(data: List<String>, transform: (String) -> String): List<String> {
    val result = mutableListOf<String>()
    // 50+ lines of processing logic
    return result
}
```

2. **Use noinline when lambda needs to be stored**:
```kotlin
inline fun registerCallback(noinline callback: () -> Unit) {
    callbacks.add(callback)  // Storing requires actual object
}
```

3. **Use crossinline for async contexts**:
```kotlin
inline fun launchAsync(crossinline block: () -> Unit) {
    GlobalScope.launch { block() }  // Different execution context
}
```

4. **Prefer inline for DSL builders**:
```kotlin
inline fun buildString(builderAction: StringBuilder.() -> Unit): String {
    return StringBuilder().apply(builderAction).toString()
}
```

5. **Be cautious with public API**:
```kotlin
// Public API - consider future changes
inline fun publicUtility(action: () -> Unit) {
    // Changing implementation affects all call sites
    action()
}
```

### Common Mistakes

#### 1. Over-inlining

```kotlin
//  Bad - large function, rarely called
inline fun generateReport(data: List<Data>, formatter: (Data) -> String): String {
    // 200 lines of complex logic
    // ...
}

//  Good - small, frequently called
inline fun <T> Iterable<T>.sumByLong(selector: (T) -> Long): Long {
    var sum = 0L
    for (element in this) {
        sum += selector(element)
    }
    return sum
}
```

#### 2. Forgetting noinline

```kotlin
//  Doesn't compile
inline fun registerHandler(handler: () -> Unit) {
    handlers.add(handler)  // Error: can't store inlined lambda
}

//  Correct
inline fun registerHandler(noinline handler: () -> Unit) {
    handlers.add(handler)
}
```

#### 3. Unnecessary crossinline

```kotlin
//  Unnecessary - lambda not used in different context
inline fun simpleOperation(crossinline block: () -> Unit) {
    block()  // Called directly, crossinline not needed
}

//  Correct
inline fun simpleOperation(block: () -> Unit) {
    block()
}
```

### Real-World Use Cases

#### Standard Library Examples

```kotlin
// 1. Collection operations
public inline fun <T> Iterable<T>.forEach(action: (T) -> Unit) {
    for (element in this) action(element)
}

// 2. Scope functions
public inline fun <T, R> T.let(block: (T) -> R): R = block(this)
public inline fun <T> T.apply(block: T.() -> Unit): T {
    block()
    return this
}

// 3. Lazy delegation
public inline fun <T> lazy(crossinline initializer: () -> T): Lazy<T> =
    SynchronizedLazyImpl(initializer)

// 4. Sequences
public inline fun <T> sequence(crossinline block: suspend SequenceScope<T>.() -> Unit): Sequence<T> =
    Sequence { iterator(block) }
```

#### Custom Utility Examples

```kotlin
// Transaction management
inline fun <T> transaction(block: () -> T): T {
    beginTransaction()
    try {
        val result = block()
        commit()
        return result
    } catch (e: Exception) {
        rollback()
        throw e
    }
}

// Conditional logging
inline fun logIf(condition: Boolean, message: () -> String) {
    if (condition) {
        Log.d("TAG", message())  // message() only called if condition true
    }
}

// Retry with exponential backoff
inline fun <T> retry(
    times: Int = 3,
    initialDelay: Long = 100,
    factor: Double = 2.0,
    block: () -> T
): T {
    var currentDelay = initialDelay
    repeat(times - 1) { attempt ->
        try {
            return block()
        } catch (e: Exception) {
            Thread.sleep(currentDelay)
            currentDelay = (currentDelay * factor).toLong()
        }
    }
    return block()  // Last attempt throws if fails
}
```

---

## Ответ (RU)

Inline функции - это мощная возможность Kotlin, которая инструктирует компилятор вставлять байт-код функции непосредственно в место вызова вместо создания отдельного вызова функции. Это устраняет накладные расходы на вызов функции и позволяет использовать продвинутые возможности, такие как реифицированные параметры типов.

### Зачем нужны Inline функции

В Kotlin лямбда-выражения обычно компилируются в экземпляры анонимных классов (Function0, Function1 и т.д.). Каждая лямбда создает объект, который:
1. Выделяет память в куче
2. Создает давление на сборщик мусора
3. Добавляет косвенность через накладные расходы вызова функции

**Проблема без inline**:
```kotlin
// Обычная функция высшего порядка
fun repeat(times: Int, action: () -> Unit) {
    for (i in 0 until times) {
        action()  // Косвенный вызов через объект Function
    }
}

// Использование
repeat(5) {
    println("Привет")
}

// Компилируется примерно в:
Function0 action = new Function0() {
    public void invoke() {
        System.out.println("Привет");
    }
};
for (int i = 0; i < 5; i++) {
    action.invoke();  // Выделение объекта + косвенный вызов
}
```

**Решение с inline**:
```kotlin
inline fun repeat(times: Int, action: () -> Unit) {
    for (i in 0 until times) {
        action()  // Тело лямбды встраивается напрямую
    }
}

// То же использование
repeat(5) {
    println("Привет")
}

// Компилируется в:
for (int i = 0; i < 5; i++) {
    System.out.println("Привет");  // Прямой код, без выделения памяти!
}
```

### Как работают Inline функции

Компилятор выполняет **копирование-вставку** как тела функции, так и тел лямбд в место вызова:

```kotlin
inline fun measureTime(block: () -> Unit): Long {
    val start = System.nanoTime()
    block()
    val end = System.nanoTime()
    return end - start
}

// Место вызова
val time = measureTime {
    println("Выполняю работу")
    Thread.sleep(100)
}

// После встраивания (концептуально):
val start = System.nanoTime()
println("Выполняю работу")
Thread.sleep(100)
val end = System.nanoTime()
val time = end - start
```

### Преимущества Inline функций

#### 1. Устраняет накладные расходы на вызов функций

```kotlin
// Бенчмарк производительности
inline fun inlined(operation: () -> Int): Int {
    return operation()
}

fun notInlined(operation: () -> Int): Int {
    return operation()
}

fun benchmark() {
    val iterations = 100_000_000

    // С inline - ~200мс
    var result = 0
    val start1 = System.currentTimeMillis()
    repeat(iterations) {
        result += inlined { 1 }
    }
    println("Inline: ${System.currentTimeMillis() - start1}мс")

    // Без inline - ~600мс (в 3 раза медленнее!)
    result = 0
    val start2 = System.currentTimeMillis()
    repeat(iterations) {
        result += notInlined { 1 }
    }
    println("Не inline: ${System.currentTimeMillis() - start2}мс")
}
```

#### 2. Избегает выделения объектов для лямбд

```kotlin
// Сравнение выделения памяти
class MemoryTest {
    // Без inline - создает объект Function при каждом вызове
    fun processItems(items: List<String>, transform: (String) -> String): List<String> {
        return items.map(transform)  // Выделяется объект Function
    }

    // С inline - нет выделения
    inline fun processItemsInline(items: List<String>, transform: (String) -> String): List<String> {
        return items.map(transform)  // Код лямбды встраивается
    }
}

// Вызов 1000 раз:
// processItems: Выделяет 1000 объектов Function → давление на GC
// processItemsInline: Ноль выделений → Нет влияния на GC
```

#### 3. Позволяет использовать реифицированные параметры типов

Только inline функции могут использовать `reified`, что дает доступ к информации о типе во время выполнения:

```kotlin
// Без reified - не работает
fun <T> isInstanceOf(value: Any): Boolean {
    return value is T  //  Ошибка: Невозможно проверить стертый тип
}

// С inline + reified - работает!
inline fun <reified T> isInstanceOf(value: Any): Boolean {
    return value is T  //  Проверка типа работает!
}

// Практические примеры
inline fun <reified T> List<*>.filterIsInstance(): List<T> {
    return this.filter { it is T }.map { it as T }
}

val mixed: List<Any> = listOf("привет", 42, "мир", 3.14)
val strings: List<String> = mixed.filterIsInstance<String>()
// Результат: ["привет", "мир"]

inline fun <reified T> Gson.fromJson(json: String): T {
    return fromJson(json, T::class.java)
}

val user: User = gson.fromJson<User>(jsonString)
```

#### 4. Разрешает нелокальные возвраты

В inline функциях лямбда может использовать `return` для выхода из охватывающей функции:

```kotlin
// Пример нелокального возврата
fun findFirstNegative(numbers: List<Int>): Int? {
    numbers.forEach { number ->  // forEach является inline
        if (number < 0) {
            return number  // Возвращается из findFirstNegative, не из лямбды
        }
    }
    return null
}

val result = findFirstNegative(listOf(1, 2, -3, 4))
// Возвращает -3 и выходит из всей функции
```

### Полные практические примеры

#### Пример 1: Реализация синхронизированного блока

```kotlin
// Реализация из стандартной библиотеки
inline fun <R> synchronized(lock: Any, block: () -> R): R {
    @Suppress("NON_PUBLIC_CALL_FROM_PUBLIC_INLINE")
    kotlin.jvm.internal.Intrinsics.monitor.enter(lock)
    try {
        return block()
    } finally {
        kotlin.jvm.internal.Intrinsics.monitor.exit(lock)
    }
}

// Использование
class Counter {
    private val lock = Any()
    private var count = 0

    fun increment() {
        synchronized(lock) {
            count++
        }
    }

    fun get(): Int = synchronized(lock) { count }
}
```

#### Пример 2: Паттерн Use-Resource (try-with-resources)

```kotlin
inline fun <T : Closeable, R> T.use(block: (T) -> R): R {
    var exception: Throwable? = null
    try {
        return block(this)
    } catch (e: Throwable) {
        exception = e
        throw e
    } finally {
        when {
            exception == null -> close()
            else -> try {
                close()
            } catch (closeException: Throwable) {
                exception.addSuppressed(closeException)
            }
        }
    }
}

// Использование
fun readFirstLine(path: String): String {
    BufferedReader(FileReader(path)).use { reader ->
        return reader.readLine()  // Нелокальный возврат работает!
    }
    // Файл автоматически закрыт
}
```

#### Пример 3: Измерение и профилирование

```kotlin
inline fun <T> measureTimeMillis(block: () -> T): Pair<T, Long> {
    val start = System.currentTimeMillis()
    val result = block()
    val time = System.currentTimeMillis() - start
    return result to time
}

// Использование
fun complexOperation(): List<Int> {
    val (result, timeMs) = measureTimeMillis {
        (1..1000000).filter { it % 2 == 0 }.map { it * it }
    }
    println("Операция заняла ${timeMs}мс")
    return result
}

// Профилирование памяти
inline fun <T> measureMemory(block: () -> T): Pair<T, Long> {
    System.gc()
    val runtime = Runtime.getRuntime()
    val before = runtime.totalMemory() - runtime.freeMemory()
    val result = block()
    System.gc()
    val after = runtime.totalMemory() - runtime.freeMemory()
    return result to (after - before)
}
```

### Модификатор noinline

Иногда нужно предотвратить встраивание конкретных параметров-лямбд:

```kotlin
inline fun performOperation(
    inlinedAction: () -> Unit,
    noinline notInlinedAction: () -> Unit
) {
    inlinedAction()  //  Встраивается в место вызова
    notInlinedAction()  //  Не встраивается, обрабатывается как обычная лямбда
}
```

**Когда использовать noinline**:

#### 1. Сохранение лямбды для последующего использования

```kotlin
class EventBus {
    private val listeners = mutableListOf<() -> Unit>()

    // Не можем встроить, потому что сохраняем лямбду
    inline fun register(noinline listener: () -> Unit) {
        listeners.add(listener)  // Нужен реальный объект Function для сохранения
    }

    fun notify() {
        listeners.forEach { it() }
    }
}
```

#### 2. Передача лямбды в не-inline функцию

```kotlin
inline fun processAsync(
    data: String,
    noinline onComplete: (Result<String>) -> Unit
) {
    // Не можем встроить, потому что launch корутины нужен объект Function
    GlobalScope.launch {
        delay(1000)
        onComplete(Result.success(data))
    }
}
```

### Модификатор crossinline

`crossinline` предотвращает нелокальные возвраты в лямбдах, которые вызываются в другом контексте:

```kotlin
inline fun runInThread(crossinline block: () -> Unit) {
    Thread {
        block()  // Вызывается в другом контексте (новый поток)
    }.start()
}

fun test() {
    runInThread {
        println("В потоке")
        // return  //  Ошибка компилятора: 'return' здесь не разрешен
    }
    println("После runInThread")  // Всегда выполняется
}
```

### Ограничения и соображения

#### 1. Увеличение размера кода

Встраивание копирует код в каждое место вызова, увеличивая размер байт-кода:

```kotlin
inline fun largeFunction(block: () -> Unit) {
    // 100 строк кода
    println("Начало операции")
    println("Шаг 1")
    // ... много строк ...
    block()
    // ... еще много строк ...
    println("Операция завершена")
}

// Вызывается 50 раз в вашем коде
// → 50 копий тела largeFunction в байт-коде
// → Значительно больший APK/JAR
```

**Рекомендация**: Встраивайте только маленькие функции (обычно 1-3 строки) или функции с параметрами-лямбдами.

#### 2. Не может быть виртуальной (open, override, abstract)

```kotlin
open class Base {
    //  Ошибка: inline функции не могут быть open
    open inline fun operation(block: () -> Unit) {
        block()
    }
}
```

**Причина**: Встраивание происходит во время компиляции, но виртуальная диспетчеризация - во время выполнения.

### Анализ производительности

#### Бенчмарк: Накладные расходы функций высшего порядка

```kotlin
fun benchmarkInlinePerformance() {
    val iterations = 10_000_000

    // Тест 1: Прямой код
    var result = 0
    var start = System.nanoTime()
    repeat(iterations) {
        result += 1
    }
    val directTime = System.nanoTime() - start
    println("Прямой: ${directTime / 1_000_000}мс")

    // Тест 2: Inline функция
    result = 0
    start = System.nanoTime()
    inline fun inlineAdd(n: Int, operation: (Int) -> Int): Int {
        return operation(n)
    }
    repeat(iterations) {
        result = inlineAdd(result) { it + 1 }
    }
    val inlineTime = System.nanoTime() - start
    println("Inline: ${inlineTime / 1_000_000}мс")

    // Тест 3: Обычная функция
    result = 0
    start = System.nanoTime()
    fun regularAdd(n: Int, operation: (Int) -> Int): Int {
        return operation(n)
    }
    repeat(iterations) {
        result = regularAdd(result) { it + 1 }
    }
    val regularTime = System.nanoTime() - start
    println("Обычная: ${regularTime / 1_000_000}мс")

    // Результаты на типичном железе:
    // Прямой:  ~10мс   (базовый уровень)
    // Inline:  ~12мс   (20% накладных расходов от сложности встраивания)
    // Обычная: ~150мс  (в 15 раз медленнее из-за выделения лямбд)
}
```

### Когда использовать Inline функции

 **ИСПОЛЬЗУЙТЕ inline для**:
- Функций высшего порядка с параметрами-лямбдами
- Функций, нуждающихся в реифицированных параметрах типов
- Маленьких утилитарных функций (1-3 строки)
- Критичных по производительности горячих путей
- DSL построителей
- Управления ресурсами (use, synchronized)

 **НЕ используйте inline для**:
- Больших функций (увеличивает размер кода)
- Виртуальных функций (open, override, abstract)
- Рекурсивных функций
- Функций, где выделение лямбды незначительно
- Функций публичного API (нельзя изменить сигнатуру позже)

### Лучшие практики

1. **Встраивайте маленькие, часто вызываемые функции**
2. **Используйте noinline когда лямбду нужно сохранить**
3. **Используйте crossinline для асинхронных контекстов**
4. **Предпочитайте inline для DSL построителей**
5. **Будьте осторожны с публичным API**

### Распространенные ошибки

#### 1. Избыточное встраивание

```kotlin
//  Плохо - большая функция, редко вызывается
inline fun generateReport(data: List<Data>, formatter: (Data) -> String): String {
    // 200 строк сложной логики
}

//  Хорошо - маленькая, часто вызывается
inline fun <T> Iterable<T>.sumByLong(selector: (T) -> Long): Long {
    var sum = 0L
    for (element in this) {
        sum += selector(element)
    }
    return sum
}
```

#### 2. Забытый noinline

```kotlin
//  Не компилируется
inline fun registerHandler(handler: () -> Unit) {
    handlers.add(handler)  // Ошибка: нельзя сохранить встроенную лямбду
}

//  Правильно
inline fun registerHandler(noinline handler: () -> Unit) {
    handlers.add(handler)
}
```

#### 3. Ненужный crossinline

```kotlin
//  Ненужный - лямбда не используется в другом контексте
inline fun simpleOperation(crossinline block: () -> Unit) {
    block()  // Вызывается напрямую, crossinline не нужен
}

//  Правильно
inline fun simpleOperation(block: () -> Unit) {
    block()
}
```

### Примеры из реального мира

#### Примеры из стандартной библиотеки

```kotlin
// 1. Операции с коллекциями
public inline fun <T> Iterable<T>.forEach(action: (T) -> Unit) {
    for (element in this) action(element)
}

// 2. Функции области видимости
public inline fun <T, R> T.let(block: (T) -> R): R = block(this)
public inline fun <T> T.apply(block: T.() -> Unit): T {
    block()
    return this
}

// 3. Ленивая делегация
public inline fun <T> lazy(crossinline initializer: () -> T): Lazy<T> =
    SynchronizedLazyImpl(initializer)

// 4. Последовательности
public inline fun <T> sequence(crossinline block: suspend SequenceScope<T>.() -> Unit): Sequence<T> =
    Sequence { iterator(block) }
```

---

## Related Questions
- [[q-kotlin-lambda-expressions--kotlin--medium]]
- [[q-kotlin-higher-order-functions--kotlin--medium]]
- [[q-reified-type-parameters--kotlin--medium]]
- [[q-crossinline-keyword--kotlin--medium]]
- [[q-inline-function-limitations--kotlin--medium]]
- [[q-inline-value-classes-performance--kotlin--medium]]

## References
- [Kotlin Documentation: Inline Functions](https://kotlinlang.org/docs/inline-functions.html)
- [Kotlin Inline Functions - Official Guide](https://kotlinlang.org/docs/inline-functions.html#noinline)
- [Performance: Inline Functions](https://kotlinlang.org/docs/inline-functions.html#inline-properties)
