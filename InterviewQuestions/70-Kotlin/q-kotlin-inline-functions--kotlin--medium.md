---
id: kotlin-132
title: "Kotlin Inline Functions / Inline функции в Kotlin"
aliases: ["Inline функции в Kotlin", "Kotlin Inline Functions"]

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
date created: Sunday, October 12th 2025, 2:02:58 pm
date modified: Tuesday, November 25th 2025, 8:53:50 pm
---

# Вопрос (RU)
> Что такое inline функции в Kotlin? Объясните их назначение, преимущества, модификаторы (noinline, crossinline), ограничения и приведите практические примеры с анализом производительности.

---

# Question (EN)
> What are inline functions in Kotlin? Explain their purpose, benefits, modifiers (noinline, crossinline), limitations, and provide practical examples with performance analysis.

## Ответ (RU)

Inline функции - это возможность Kotlin, которая инструктирует компилятор (на уровне Kotlin) попытаться вставить байт-код функции непосредственно в место вызова вместо генерации отдельного вызова функции, особенно для функций высшего порядка с лямбда-параметрами. Это может уменьшать накладные расходы на вызов функций и аллокации для некоторых лямбд и позволяет использовать возможности, такие как реифицированные параметры типов (см. также [[c-kotlin]]). Конкретный эффект зависит от целевой платформы и оптимизаций (включая JIT для JVM).

### Зачем Нужны Inline Функции

В Kotlin лямбда-выражения на JVM обычно компилируются в объекты (например, анонимные классы или функциональные объекты `FunctionN`), особенно если они захватывают контекст. Это может приводить к:
1. Выделению памяти в куче
2. Давлению на сборщик мусора
3. Дополнительной косвенности через накладные расходы вызова функции

При этом JVM и компилятор могут оптимизировать часть этих накладных расходов (например, через `invokedynamic` и escape-анализ), поэтому inline не гарантирует ускорения во всех сценариях, а дает компилятору дополнительные возможности.

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
        action()  // Тело лямбды может быть встроено
    }
}

// То же использование
repeat(5) {
    println("Привет")
}

// Концептуально после встраивания (упрощенно):
for (i in 0 until 5) {
    println("Привет")  // Прямой код, без отдельного объекта для некэпчеринговой лямбды
}
```

### Как Работают Inline Функции

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

При этом реальные детали зависят от backend'а (JVM/JS/Native) и оптимизаций; inlining для конкретного вызова может быть частичным или не произойти, если это нецелесообразно.

### Преимущества Inline Функций

#### 1. Снижение Накладных Расходов На Вызов Функций

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
    println("Inline: ${System.currentTimeMillis() - start1}мс (примерно)")

    result = 0
    val start2 = System.currentTimeMillis()
    repeat(iterations) {
        result += notInlined { 1 }
    }
    println("Не inline: ${System.currentTimeMillis() - start2}мс (примерно)")
}
```

Комментарий: конкретные числа зависят от JVM, JIT, оптимизаций и среды. Inline может дать выигрыш, но его следует подтверждать бенчмарками.

#### 2. Сокращение Выделения Объектов Для Лямбд

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
// processItemsInline: меньше аллокаций, особенно для некэпчеринговых лямбд (фактическое поведение зависит от оптимизаций)
```

#### 3. Реифицированные Параметры Типов

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

#### 4. Нелокальные Возвраты

В inline функциях лямбда может использовать `return` для выхода из охватывающей функции (non-local return):

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

### Полные Практические Примеры

#### Пример 1: Реализация Synchronized-блока

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

(Реальная stdlib использует внутренние API; этот пример носит учебный, концептуальный характер. В прикладном коде следует использовать стандартный `synchronized` / высокоуровневые утилиты, а не вызывать внутренние Intrinsics напрямую.)

#### Пример 2: Паттерн Use-ресурса (try-with-resources)

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

#### Пример 3: Измерение И Профилирование

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

Комментарий: `measureMemory` с ручными вызовами `System.gc()` приведен только как упрощенная демонстрация идеи и не является надежным способом измерения потребления памяти в реальных приложениях.

#### Пример 4: DSL Builders

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

#### Пример 5: Условное Выполнение (applyIf/alsoIf)

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

### Модификатор Noinline

Иногда нужно явно предотвратить встраивание конкретных параметров-лямбд и сохранить их как значения (для хранения или передачи дальше):

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

#### 1. Сохранение Лямбды Для Последующего Использования

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

#### 2. Передача Лямбды В Не-inline Функцию

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

#### 3. Композиция Функций Высшего Порядка

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

### Модификатор Crossinline

`crossinline` предотвращает нелокальные возвраты в лямбдах, которые будут вызваны в другом контексте или отложенно, где non-local return невозможен:

```kotlin
inline fun runInThread(crossinline block: () -> Unit) {
    Thread {
        block()
    }.start()
}

fun test() {
    runInThread {
        println("В потоке")
        // return  // Ошибка компилятора: нелокальный return недопустим
    }
    println("После runInThread")
}
```

Без `crossinline` компилятор запрещает такие случаи с потенциальным нелокальным `return`, так как он не может корректно их сгенерировать при вызове из другого контекста.

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

### Комбинирование Noinline И Crossinline

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

### Ограничения И Соображения

#### 1. Увеличение Размера Кода

Встраивание копирует код в каждое место вызова, увеличивая размер байт-кода. Встраивайте в основном маленькие функции либо функции с лямбда-параметрами.

#### 2. Нельзя Делать open/abstract/override Inline-методы

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

#### 3. Доступ К Private-членам

Публичные inline-функции, использующие private-члены класса или файла, могут приводить к проблемам видимости на месте вызова. Компилятор либо запрещает такие случаи, либо генерирует дополнительные accessors; это нужно учитывать при проектировании API.

#### 4. Рекурсивные Inline-функции

```kotlin
inline fun factorial(n: Int): Int {
    return if (n <= 1) 1 else n * factorial(n - 1)
}
```

Рекурсивные inline-функции формально допустимы, но вызовы не будут разворачиваться бесконечно на месте вызова; компилятор обрабатывает такие случаи особо. Как правило, это не дает ожидаемой оптимизации и может ухудшить читаемость, поэтому обычно не рекомендуется.

### Анализ Производительности

Примеры бенчмарков из разделов выше иллюстрируют, что inline-функции могут:
- уменьшать накладные расходы вызова функций высшего порядка в некоторых сценариях;
- уменьшать количество аллокаций для некэпчеринговых лямбд;
- давать компилятору больше возможностей для оптимизаций.

Фактический выигрыш зависит от:
- целевой платформы (JVM/JS/Native);
- включенных оптимизаций и поведения JIT;
- паттернов использования (захваты, escape-анализ и т.п.).

Поэтому inline следует рассматривать как инструмент, требующий измерений в реальном окружении.

### Когда Использовать Inline Функции

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

### Лучшие Практики

1. Встраивайте маленькие, часто вызываемые функции.
2. Используйте `noinline`, когда лямбду нужно сохранить или передать дальше как значение.
3. Используйте `crossinline`, когда лямбда вызывается в другом контексте (потоки, корутины) и нелокальные `return` недопустимы.
4. Используйте inline для DSL и оберток над ресурсами.
5. Будьте осторожны с публичными inline API: изменение тела требует перекомпиляции клиентов.

### Распространенные Ошибки

1. Избыточное встраивание больших или редко вызываемых функций.
2. Отсутствие `noinline` при сохранении лямбды.
3. Использование `crossinline` без необходимости, когда лямбда вызывается напрямую.

### Примеры Из Реального Мира

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

Inline functions are a Kotlin feature that instruct the compiler to (where profitable and applicable) insert the function's bytecode directly at each call site instead of always emitting a separate call, especially for higher-order functions with lambda parameters. This can reduce call overhead and some lambda allocations and enables features like reified type parameters. The actual impact is platform- and optimizer-dependent.

### Why Inline Functions Exist

On the JVM, Kotlin lambda expressions are typically compiled to objects (such as anonymous classes or `FunctionN` implementations), especially when they capture variables. This can:
1. Allocate memory on the heap
2. Add pressure to the garbage collector
3. Introduce indirection and extra call overhead

At the same time, JVM and the compiler can optimize some of this (e.g., via `invokedynamic` and escape analysis), so inline is not a guaranteed win, but a tool that can unlock additional optimizations.

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

// Conceptually after inlining (simplified):
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

Actual code generation depends on the target (JVM/JS/Native) and optimizer. Inlining for a given call site can be partial or skipped based on heuristics.

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

These numbers are illustrative; real performance depends on the runtime and JIT. Inline can help, but always measure.

#### 2. Fewer Lambda Allocations

```kotlin
class MemoryTest {
    // Without inline - typically involves a function object (especially for capturing lambdas)
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
// processItemsInline: fewer allocations, especially for non-capturing lambdas (subject to optimizations)
```

#### 3. Enables Reified Type Parameters

Only inline functions can use `reified`, which allows working with the actual type at runtime:

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

With inline functions, lambdas can use `return` to exit the enclosing function (non-local return):

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

(This mirrors how stdlib does it conceptually. It relies on internal APIs and is for educational purposes; production code should use standard `synchronized`/utilities rather than calling Intrinsics directly.)

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

Note: `measureMemory` here is a simplistic illustration; explicit `System.gc()` and single-shot measurements are not reliable profiling techniques.

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

Sometimes you need to prevent specific lambda parameters from being inlined and treat them as regular function values (e.g., to store or pass them):

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

`crossinline` prevents non-local returns in lambdas that are invoked in a different or deferred context where such returns would be invalid:

```kotlin
inline fun runInThread(crossinline block: () -> Unit) {
    Thread {
        block()
    }.start()
}

fun test() {
    runInThread {
        println("In thread")
        // return  // Compiler error: non-local return is not allowed here
    }
    println("After runInThread")
}
```

Without `crossinline`, the compiler would reject using non-local `return` from lambdas passed to contexts where it cannot be implemented correctly; `crossinline` explicitly enforces this.

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
    noinline storedLambda: () -> Unit,   // Not inlined, can be stored
    crossinline asyncLambda: () -> Unit  // Inlined but no non-local returns
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

Inlining duplicates the function body at each call site, potentially increasing bytecode size. Prefer inlining small functions or those with lambda parameters.

#### 2. Can't Be Virtual (open, Override, abstract)

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

Public inline functions that access private members of their class or file can cause visibility issues at call sites; the compiler either forbids this or generates synthetic accessors. Keep this in mind for public APIs.

#### 4. Recursive Inline Functions

```kotlin
inline fun factorial(n: Int): Int {
    return if (n <= 1) 1 else n * factorial(n - 1)
}
```

Recursive inline functions are syntactically allowed, but calls are not infinitely expanded inline; the compiler handles them specially. In practice, they rarely bring benefits and may hurt bytecode size/readability, so they're usually discouraged.

### Performance Analysis

Inline functions can:
- reduce some higher-order function overhead;
- reduce allocations for certain non-capturing lambdas;
- enable further optimizations by the backend.

However, actual gains:
- depend on the target (JVM/JS/Native) and JIT;
- are sensitive to capture patterns, escape analysis, and call frequency.

Treat inline as a tool to be validated with measurements in your real workload.

### When to Use Inline Functions

DO use inline for:
- higher-order functions with lambda parameters;
- functions requiring reified type parameters;
- small utilities and hot paths;
- DSL builders;
- resource-management wrappers (`use`, `synchronized`, transaction helpers).

DON'T use inline for:
- large, complex functions (code bloat);
- virtual (open/override/abstract) APIs;
- most recursive functions;
- cases where lambda allocation cost is negligible;
- public APIs without considering binary compatibility (callers must recompile when implementation changes).

### Best Practices

1. Inline small, frequently called functions.
2. Use `noinline` when you need to store or pass a lambda as a value.
3. Use `crossinline` for lambdas invoked in different/deferred contexts (threads, coroutines) where non-local returns are not valid.
4. Prefer inline for DSL builders and control-like utilities.
5. Be cautious with public inline APIs: changes affect all call sites and require recompilation.

### Common Mistakes

1. Over-inlining large or rarely used functions.
2. Forgetting `noinline` when storing lambdas.
3. Using `crossinline` unnecessarily when the lambda is called directly.

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

## Дополнительные Вопросы (RU)

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

## Связанные Вопросы (RU)

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
