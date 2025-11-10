---
id: kotlin-132
title: "Kotlin Inline Functions / Inline функции в Kotlin"
aliases: ["Kotlin Inline Functions", "Inline функции в Kotlin"]

# Classification
topic: kotlin
subtopics: [inline-functions, lambdas, optimization]
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
related: [c-kotlin, q-crossinline-keyword--kotlin--medium, q-inline-function-limitations--kotlin--medium, q-kotlin-higher-order-functions--kotlin--medium, q-kotlin-lambda-expressions--kotlin--medium, q-reified-type-parameters--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-11-10

tags: [difficulty/medium, inline-functions, kotlin, lambdas, optimization, performance, reified]
---
# Вопрос (RU)
> Что такое inline функции в Kotlin? Объясните их назначение, преимущества, модификаторы (noinline, crossinline), ограничения и приведите практические примеры с анализом производительности.

---

# Question (EN)
> What are inline functions in Kotlin? Explain their purpose, benefits, modifiers (noinline, crossinline), limitations, and provide practical examples with performance analysis.

## Ответ (RU)

Inline функции - это мощная возможность Kotlin, которая инструктирует компилятор вставлять байт-код функции непосредственно в место вызова вместо создания отдельного вызова функции. Это уменьшает накладные расходы на вызов функции и позволяет использовать продвинутые возможности, такие как реифицированные параметры типов (см. также [[c-kotlin]]).

### Зачем нужны inline функции

В Kotlin лямбда-выражения обычно компилируются в объекты (например, анонимные классы или функциональные объекты `FunctionN`), особенно если они захватывают контекст. Это может приводить к:
1. Выделению памяти в куче
2. Давлению на сборщик мусора
3. Дополнительной косвенности через накладные расходы вызова функции

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

// Концептуально может выглядеть так (упрощенно):
val action = object : () -> Unit {
    override fun invoke() {
        println("Привет")
    }
}
for (i in 0 until 5) {
    action()  // Объект + косвенный вызов
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

// Концептуально после встраивания:
for (i in 0 until 5) {
    println("Привет")  // Прямой код, без отдельного объекта для некэпчеринговой лямбды
}
```

### Как работают inline функции

Компилятор выполняет концептуальное «копирование-вставку» как тела функции, так и (при возможности) тел лямбд в место вызова:

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

// После встраивания (упрощенно):
val start = System.nanoTime()
println("Выполняю работу")
Thread.sleep(100)
val end = System.nanoTime()
val time = end - start
```

При этом реальные детали зависят от backend'а (JVM/JS/Native) и оптимизаций.

### Преимущества inline функций

#### 1. Снижение накладных расходов на вызов функций

```kotlin
inline fun inlined(operation: () -> Int): Int {
    return operation()
}

fun notInlined(operation: () -> Int): Int {
    return operation()
}

fun benchmark() {
    val iterations = 100_000_000

    var result = 0
    val start1 = System.currentTimeMillis()
    repeat(iterations) {
        result += inlined { 1 }
    }
    println("Inline: ${System.currentTimeMillis() - start1}мс (примерное значение)")

    result = 0
    val start2 = System.currentTimeMillis()
    repeat(iterations) {
        result += notInlined { 1 }
    }
    println("Не inline: ${System.currentTimeMillis() - start2}мс (примерное значение)")
}
```

Комментарий: конкретные числа зависят от JVM, оптимизаций и среды, пример иллюстрирует порядок разницы.

#### 2. Сокращение выделения объектов для лямбд

```kotlin
class MemoryTest {
    // Без inline - как правило, создается объект Function (особенно при захвате контекста)
    fun processItems(items: List<String>, transform: (String) -> String): List<String> {
        return items.map(transform)
    }

    // С inline - вызов transform может быть встроен, что уменьшает или устраняет аллокации для некэпчеринговых лямбд
    inline fun processItemsInline(items: List<String>, transform: (String) -> String): List<String> {
        return items.map(transform)
    }
}

// Вызов много раз:
// processItems: потенциально больше аллокаций под лямбды
// processItemsInline: меньше аллокаций, особенно для некэпчеринговых лямбд
```

#### 3. Реифицированные параметры типов

Только inline функции могут использовать `reified`, что дает доступ к информации о типе во время выполнения:

```kotlin
// Без reified - не работает
fun <T> isInstanceOf(value: Any): Boolean {
    return value is T  // Ошибка: Невозможно проверить стертый тип
}

// С inline + reified - работает
inline fun <reified T> isInstanceOf(value: Any): Boolean {
    return value is T
}

// Практический пример (в стандартной библиотеке уже есть filterIsInstance)
inline fun <reified T> List<*>.filterIsInstanceInline(): List<T> {
    return this.filter { it is T }.map { it as T }
}

val mixed: List<Any> = listOf("привет", 42, "мир", 3.14)
val strings: List<String> = mixed.filterIsInstanceInline<String>()
// Результат: ["привет", "мир"]

inline fun <reified T> Gson.fromJson(json: String): T {
    return fromJson(json, T::class.java)
}

val user: User = gson.fromJson<User>(jsonString)
```

#### 4. Нелокальные возвраты

В inline функциях лямбда может использовать `return` для выхода из охватывающей функции:

```kotlin
fun findFirstNegative(numbers: List<Int>): Int? {
    numbers.forEach { number ->  // forEach является inline
        if (number < 0) {
            return number  // Возвращаемся из findFirstNegative
        }
    }
    return null
}

val result = findFirstNegative(listOf(1, 2, -3, 4))
// Возвращает -3 и выходит из всей функции
```

### Полные практические примеры

#### Пример 1: Реализация synchronized-блока

```kotlin
inline fun <R> synchronized(lock: Any, block: () -> R): R {
    @Suppress("NON_PUBLIC_CALL_FROM_PUBLIC_INLINE")
    kotlin.jvm.internal.Intrinsics.monitorEnter(lock)
    try {
        return block()
    } finally {
        kotlin.jvm.internal.Intrinsics.monitorExit(lock)
    }
}
```

(Реальная реализация и названия методов зависят от версии stdlib/JVM, приведено концептуально.)

#### Пример 2: Паттерн use-ресурса (try-with-resources)

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

fun readFirstLine(path: String): String {
    BufferedReader(FileReader(path)).use { reader ->
        return reader.readLine()  // Нелокальный возврат работает
    }
}

fun processFile(path: String): Result<String> {
    return BufferedReader(FileReader(path)).use { reader ->
        val content = reader.readText()
        Result.success(content)
    }
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

inline fun <T> measureNanos(block: () -> T): Pair<T, Long> {
    val start = System.nanoTime()
    val result = block()
    val time = System.nanoTime() - start
    return result to time
}

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

#### Пример 4: DSL builders

```kotlin
class HTML {
    private val children = mutableListOf<String>()

    inline fun body(init: BODY.() -> Unit) {
        val body = BODY()
        body.init()
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
        children.add("<p>${init()}</p>")
    }

    override fun toString() = "<body>${children.joinToString("")}</body>"
}

fun createPage() = HTML().apply {
    body {
        h1("Welcome")
        p { "This is a paragraph" }
        p { "Another paragraph" }
    }
}.toString()
```

#### Пример 5: Условное выполнение (applyIf/alsoIf)

```kotlin
inline fun <T> T.applyIf(condition: Boolean, block: T.() -> Unit): T {
    if (condition) {
        block()
    }
    return this
}

inline fun <T> T.alsoIf(condition: Boolean, block: (T) -> Unit): T {
    if (condition) {
        block(this)
    }
    return this
}

// Использование
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

### Модификатор noinline

Иногда нужно предотвратить встраивание конкретных параметров-лямбд:

```kotlin
inline fun performOperation(
    inlinedAction: () -> Unit,
    noinline notInlinedAction: () -> Unit
) {
    inlinedAction()
    notInlinedAction()
}
```

Когда использовать `noinline`:

#### 1. Сохранение лямбды для последующего использования

```kotlin
class EventBus {
    private val listeners = mutableListOf<() -> Unit>()

    inline fun register(noinline listener: () -> Unit) {
        listeners.add(listener)  // Нужен объект для хранения
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
    GlobalScope.launch {
        delay(1000)
        onComplete(Result.success(data))
    }
}
```

#### 3. Композиция функций высшего порядка

```kotlin
inline fun <T, R> List<T>.myMap(
    noinline transform: (T) -> R
): List<R> {
    val result = mutableListOf<R>()
    forEach { item ->
        result.add(transform(item))
    }
    return result
}
```

### Модификатор crossinline

`crossinline` предотвращает нелокальные возвраты в лямбдах, которые вызываются в другом контексте:

```kotlin
inline fun runInThread(crossinline block: () -> Unit) {
    Thread {
        block()
    }.start()
}

fun test() {
    runInThread {
        println("В потоке")
        // return  // Ошибка компилятора
    }
    println("После runInThread")
}
```

Без `crossinline` встраивание в подобные контексты с потенциальным нелокальным `return` было бы некорректным, компилятор это запрещает.

**Пример**:

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
```

### Комбинирование noinline и crossinline

```kotlin
inline fun complexOperation(
    normalLambda: () -> Unit,            // Полностью inline
    noinline storedLambda: () -> Unit,   // Не inline, можно сохранить
    crossinline asyncLambda: () -> Unit  // Inline, но без нелокальных return
) {
    normalLambda()

    val stored = storedLambda
    callLater(stored)

    GlobalScope.launch {
        asyncLambda()
    }
}
```

### Ограничения и соображения

#### 1. Увеличение размера кода

Встраивание копирует код в каждое место вызова, увеличивая размер байт-кода. Встраивайте в основном маленькие функции либо функции с лямбда-параметрами.

#### 2. Нельзя делать open/abstract/override inline-методы

```kotlin
open class Base {
    // Ошибка: inline функции не могут быть open / abstract / override
    // open inline fun operation(block: () -> Unit) { block() }
}

interface Processor {
    // inline fun process(data: String): String // не допускается как abstract
}
```

Причина: inlining на этапе компиляции несовместим с динамической диспетчеризацией.

#### 3. Доступ к private-членам

Публичные inline-функции, использующие private-члены класса или файла, могут приводить к проблемам видимости на месте вызова. Компилятор либо запрещает такие случаи, либо генерирует дополнительные accessors; это нужно учитывать при проектировании API.

#### 4. Рекурсивные inline-функции

```kotlin
inline fun factorial(n: Int): Int {
    return if (n <= 1) 1 else n * factorial(n - 1)
}
```

Рекурсивные inline-функции формально допустимы, но приводят к росту байт-кода и, как правило, не дают ожидаемой оптимизации, поэтому обычно не рекомендуются.

### Анализ производительности

Примеры бенчмарков из разделов выше иллюстрируют, что inline-функции могут:
- уменьшать накладные расходы вызова функций высшего порядка;
- уменьшать количество аллокаций для некэпчеринговых лямбд;
- давать компилятору больше возможностей для оптимизаций.

Фактический выигрыш зависит от:
- целевой платформы (JVM/JS/Native);
- включенных оптимизаций;
- паттернов использования (захваты, escape-анализ и т.п.).

### Когда использовать inline функции

Используйте inline для:
- функций высшего порядка с лямбда-параметрами;
- функций с `reified` параметрами типов;
- небольших утилитарных функций и горячих участков кода;
- построения DSL;
- оберток над управлением ресурсами (`use`, `synchronized`, транзакции и т.п.).

Не используйте inline для:
- очень больших функций (рост кода);
- виртуальных (open/override/abstract) и большинства рекурсивных функций;
- случаев, где выгода от устранения лямбды минимальна;
- публичных API без учета последствий для бинарной совместимости (требуется перекомпиляция вызывающего кода).

### Лучшие практики

1. Встраивайте маленькие, часто вызываемые функции.
2. Используйте `noinline`, когда лямбду нужно сохранить или передать дальше как значение.
3. Используйте `crossinline`, когда лямбда вызывается в другом контексте (потоки, корутины) и нелокальные `return` недопустимы.
4. Используйте inline для DSL и оберток над ресурсами.
5. Будьте осторожны с публичными inline API: изменение тела требует перекомпиляции клиентов.

### Распространенные ошибки

1. Избыточное встраивание больших или редко вызываемых функций.
2. Отсутствие `noinline` при сохранении лямбды.
3. Использование `crossinline` без необходимости, когда лямбда вызывается напрямую.

### Примеры из реального мира

```kotlin
// 1. Операции над коллекциями
public inline fun <T> Iterable<T>.forEach(action: (T) -> Unit) {
    for (element in this) action(element)
}

// 2. Scope-функции
public inline fun <T, R> T.let(block: (T) -> R): R = block(this)

public inline fun <T> T.apply(block: T.() -> Unit): T {
    block()
    return this
}

// 3. Lazy-делегат
public inline fun <T> lazy(crossinline initializer: () -> T): Lazy<T> =
    SynchronizedLazyImpl(initializer)

// 4. Sequences
public inline fun <T> sequence(crossinline block: suspend SequenceScope<T>.() -> Unit): Sequence<T> =
    Sequence { iterator(block) }

// 5. Транзакции
inline fun <T> transaction(block: () -> T): T {
    beginTransaction()
    return try {
        val result = block()
        commit()
        result
    } catch (e: Exception) {
        rollback()
        throw e
    }
}

// 6. Условное логирование
inline fun logIf(condition: Boolean, message: () -> String) {
    if (condition) {
        Log.d("TAG", message())
    }
}
```

---

## Answer (EN)

Inline functions are a Kotlin feature that instructs the compiler to insert the function's bytecode directly at each call site instead of always emitting a separate call. This can reduce call overhead and enables features like reified type parameters.

### Why Inline Functions Exist

In Kotlin, lambda expressions on JVM are often compiled to objects (such as anonymous classes or `FunctionN` implementations), especially when they capture variables. This can:
1. Allocate memory on the heap
2. Add pressure to the garbage collector
3. Introduce indirection and extra call overhead

**Problem without inline**:
```kotlin
fun repeat(times: Int, action: () -> Unit) {
    for (i in 0 until times) {
        action()  // Indirect call through function object
    }
}

repeat(5) {
    println("Hello")
}

// Conceptually simplified:
val action = object : () -> Unit {
    override fun invoke() {
        println("Hello")
    }
}
for (i in 0 until 5) {
    action()  // Object + indirection
}
```

**Solution with inline**:
```kotlin
inline fun repeat(times: Int, action: () -> Unit) {
    for (i in 0 until times) {
        action()  // Lambda body may be inlined
    }
}

repeat(5) {
    println("Hello")
}

// Conceptually after inlining:
for (i in 0 until 5) {
    println("Hello")  // Direct code for non-capturing lambda
}
```

### How Inline Functions Work

The compiler conceptually "copy-pastes" the function body and, where applicable, lambda bodies into the call site:

```kotlin
inline fun measureTime(block: () -> Unit): Long {
    val start = System.nanoTime()
    block()
    val end = System.nanoTime()
    return end - start
}

val time = measureTime {
    println("Doing work")
    Thread.sleep(100)
}

// Conceptual expansion:
val start = System.nanoTime()
println("Doing work")
Thread.sleep(100)
val end = System.nanoTime()
val time = end - start
```

Actual code generation details depend on the target (JVM/JS/Native) and optimizations.

### Benefits of Inline Functions

#### 1. Reduced Function Call Overhead

```kotlin
inline fun inlined(operation: () -> Int): Int {
    return operation()
}

fun notInlined(operation: () -> Int): Int {
    return operation()
}

fun benchmark() {
    val iterations = 100_000_000

    var result = 0
    val start1 = System.currentTimeMillis()
    repeat(iterations) {
        result += inlined { 1 }
    }
    println("Inline: ${System.currentTimeMillis() - start1}ms (approx)")

    result = 0
    val start2 = System.currentTimeMillis()
    repeat(iterations) {
        result += notInlined { 1 }
    }
    println("Not inline: ${System.currentTimeMillis() - start2}ms (approx)")
}
```

Numbers are illustrative; actual performance depends on the runtime and optimizer.

#### 2. Fewer Lambda Allocations

```kotlin
class MemoryTest {
    // Without inline - typically involves a function object, especially for capturing lambdas
    fun processItems(items: List<String>, transform: (String) -> String): List<String> {
        return items.map(transform)
    }

    // With inline - transform calls may be inlined, reducing allocations for non-capturing lambdas
    inline fun processItemsInline(items: List<String>, transform: (String) -> String): List<String> {
        return items.map(transform)
    }
}

// When called many times:
// processItems: potentially more allocations for lambdas
// processItemsInline: fewer allocations, especially for non-capturing lambdas
```

#### 3. Enables Reified Type Parameters

Only inline functions can use `reified`, which allows type checks and operations with the actual type at runtime:

```kotlin
fun <T> isInstanceOf(value: Any): Boolean {
    return value is T  // Error: cannot check for erased type
}

inline fun <reified T> isInstanceOf(value: Any): Boolean {
    return value is T
}

// Note: the standard library already provides filterIsInstance
inline fun <reified T> List<*>.filterIsInstanceInline(): List<T> {
    return this.filter { it is T }.map { it as T }
}

val mixed: List<Any> = listOf("hello", 42, "world", 3.14)
val strings: List<String> = mixed.filterIsInstanceInline<String>()
// Result: ["hello", "world"]

inline fun <reified T> Gson.fromJson(json: String): T {
    return fromJson(json, T::class.java)
}

val user: User = gson.fromJson<User>(jsonString)
```

#### 4. Allows Non-Local Returns

With inline functions, lambdas can use `return` to exit the enclosing function:

```kotlin
fun findFirstNegative(numbers: List<Int>): Int? {
    numbers.forEach { number ->  // forEach is inline
        if (number < 0) {
            return number  // Returns from findFirstNegative
        }
    }
    return null
}

val result = findFirstNegative(listOf(1, 2, -3, 4))
```

### Complete Practical Examples

#### Example 1: Synchronized Block Implementation

```kotlin
inline fun <R> synchronized(lock: Any, block: () -> R): R {
    @Suppress("NON_PUBLIC_CALL_FROM_PUBLIC_INLINE")
    kotlin.jvm.internal.Intrinsics.monitorEnter(lock)
    try {
        return block()
    } finally {
        kotlin.jvm.internal.Intrinsics.monitorExit(lock)
    }
}
```

(Exact implementation details may vary across Kotlin versions.)

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

fun readFirstLine(path: String): String {
    BufferedReader(FileReader(path)).use { reader ->
        return reader.readLine()  // Non-local return works
    }
}

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
class HTML {
    private val children = mutableListOf<String>()

    inline fun body(init: BODY.() -> Unit) {
        val body = BODY()
        body.init()
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
        children.add("<p>${init()}</p>")
    }

    override fun toString() = "<body>${children.joinToString("")}</body>"
}

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

inline fun <T> T.alsoIf(condition: Boolean, block: (T) -> Unit): T {
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

### The Noinline Modifier

Sometimes you need to prevent specific lambda parameters from being inlined:

```kotlin
inline fun performOperation(
    inlinedAction: () -> Unit,
    noinline notInlinedAction: () -> Unit
) {
    inlinedAction()
    notInlinedAction()
}
```

When to use `noinline`:

#### 1. Storing Lambda for Later Use

```kotlin
class EventBus {
    private val listeners = mutableListOf<() -> Unit>()

    inline fun register(noinline listener: () -> Unit) {
        listeners.add(listener)
    }

    fun notify() {
        listeners.forEach { it() }
    }
}
```

#### 2. Passing Lambda to Non-Inline Function

```kotlin
inline fun processAsync(
    data: String,
    noinline onComplete: (Result<String>) -> Unit
) {
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
        result.add(transform(item))
    }
    return result
}
```

### The Crossinline Modifier

`crossinline` prevents non-local returns in lambdas that are called in a different context:

```kotlin
inline fun runInThread(crossinline block: () -> Unit) {
    Thread {
        block()
    }.start()
}

fun test() {
    runInThread {
        println("In thread")
        // return  // Compiler error
    }
    println("After runInThread")
}
```

Without `crossinline`, using a non-local `return` inside such a lambda would be ill-formed; the compiler enforces this.

**Example**:

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
```

### Combining Noinline and Crossinline

```kotlin
inline fun complexOperation(
    normalLambda: () -> Unit,            // Fully inlined
    noinline storedLambda: () -> Unit,  // Not inlined, can be stored
    crossinline asyncLambda: () -> Unit // Inlined but no non-local returns
) {
    normalLambda()

    val stored = storedLambda
    callLater(stored)

    GlobalScope.launch {
        asyncLambda()
    }
}
```

### Limitations and Considerations

#### 1. Code Size Increase

Inlining duplicates the function body at each call site, which can significantly increase bytecode size for large functions.

#### 2. Can't Be Virtual (open, override, abstract)

```kotlin
open class Base {
    // inline functions can't be open / abstract / override
    // open inline fun operation(block: () -> Unit) { block() }
}

interface Processor {
    // inline fun process(data: String): String // not allowed as abstract
}
```

Reason: inlining is resolved at compile time, while virtual dispatch is runtime-based.

#### 3. Access to Private Members

Public inline functions that access private members of their class or module may cause visibility issues at call sites; the compiler restricts this or generates accessors.

#### 4. Recursive Inline Functions

```kotlin
inline fun factorial(n: Int): Int {
    return if (n <= 1) 1 else n * factorial(n - 1)
}
```

Recursive inline functions are allowed but can lead to large bytecode (each call is another expansion) and are usually discouraged for performance/size reasons.

### Performance Analysis

Inline functions can:
- remove some higher-order function overhead;
- reduce allocations for non-capturing lambdas;
- enable further optimizations by the backend.

However, actual gains vary and should be measured in the real target environment. The earlier benchmark-style snippets are illustrative, not guarantees.

### When to Use Inline Functions

DO use inline for:
- higher-order functions with lambda parameters;
- functions that require reified type parameters;
- small utilities and hot paths;
- DSL builders;
- resource management wrappers (`use`, `synchronized`, transaction helpers).

DON'T use inline for:
- large, complex functions (code bloat);
- virtual (open/override/abstract) APIs;
- most recursive functions;
- cases where lambda allocation cost is negligible;
- public APIs without considering binary compatibility (changes require callers to recompile).

### Best Practices

1. Inline small, frequently-called functions.
2. Use `noinline` when you need to store or pass a lambda as a value.
3. Use `crossinline` for lambdas invoked in different contexts (threads, coroutines) where non-local returns are invalid.
4. Prefer inline for DSL builders and control-like utilities.
5. Be cautious with public inline APIs: changing them affects all call sites.

### Common Mistakes

1. Over-inlining large or rarely used functions.
2. Forgetting `noinline` when storing lambdas.
3. Using `crossinline` unnecessarily when lambda is called directly.

### Real-World Use Cases

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

// 5. Transaction management (example)
inline fun <T> transaction(block: () -> T): T {
    beginTransaction()
    return try {
        val result = block()
        commit()
        result
    } catch (e: Exception) {
        rollback()
        throw e
    }
}

// 6. Conditional logging
inline fun logIf(condition: Boolean, message: () -> String) {
    if (condition) {
        Log.d("TAG", message())
    }
}
```

---

## Дополнительные вопросы (RU)

- В чем ключевые отличия inline-функций в Kotlin от аналогичных механизмов в Java?
- В каких практических сценариях вы бы использовали inline-функции?
- Какие распространенные ошибки и подводные камни при использовании inline-функций нужно учитывать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin: Inline functions](https://kotlinlang.org/docs/inline-functions.html)
- [Kotlin Inline Functions - Official Guide (noinline)](https://kotlinlang.org/docs/inline-functions.html#noinline)
- [Производительность и inline-функции](https://kotlinlang.org/docs/inline-functions.html#inline-properties)

## References
- [Kotlin Documentation: Inline Functions](https://kotlinlang.org/docs/inline-functions.html)
- [Kotlin Inline Functions - Official Guide](https://kotlinlang.org/docs/inline-functions.html#noinline)
- [Performance: Inline Functions](https://kotlinlang.org/docs/inline-functions.html#inline-properties)

## Связанные вопросы (RU)

- [[q-kotlin-lambda-expressions--kotlin--medium]]
- [[q-kotlin-higher-order-functions--kotlin--medium]]
- [[q-reified-type-parameters--kotlin--medium]]
- [[q-crossinline-keyword--kotlin--medium]]
- [[q-inline-function-limitations--kotlin--medium]]
- [[q-inline-value-classes-performance--kotlin--medium]]

## Related Questions
- [[q-kotlin-lambda-expressions--kotlin--medium]]
- [[q-kotlin-higher-order-functions--kotlin--medium]]
- [[q-reified-type-parameters--kotlin--medium]]
- [[q-crossinline-keyword--kotlin--medium]]
- [[q-inline-function-limitations--kotlin--medium]]
- [[q-inline-value-classes-performance--kotlin--medium]]
