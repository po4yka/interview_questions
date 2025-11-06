---
id: kotlin-125
title: "flowOn operator and context switching in flows / flowOn оператор и переключение контекста"
aliases: [Context, Flowon, Operator, Switching]
topic: kotlin
subtopics: [coroutines, flow, performance]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-coroutines, c-flow, q-coroutine-context-elements--kotlin--hard, q-flow-operators-map-filter--kotlin--medium]
created: 2025-10-12
updated: 2025-11-06
tags: ["buffer", "context-switching", "dispatchers", "flow-operators", "flowon", "performance", difficulty/hard]
---

# flowOn Operator and Context Switching in Flows / flowOn Оператор И Переключение Контекста

## English Version

### Question
What does the `flowOn` operator do in Kotlin flows? How does it differ from `withContext`? Explain context preservation, buffering behavior, multiple flowOn operators in a chain, and performance implications with real-world examples.

### Answer

#### What flowOn Does

`flowOn` changes the **upstream** execution context of a flow. It affects where the flow's emissions are produced, not where they are collected.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun demonstrateFlowOn() = runBlocking {
    flow {
        println("Emitting on: ${Thread.currentThread().name}")
        emit(1)
        emit(2)
        emit(3)
    }
        .flowOn(Dispatchers.IO) // Change upstream context
        .collect { value ->
            println("Collecting $value on: ${Thread.currentThread().name}")
        }
}

// Output:
// Emitting on: DefaultDispatcher-worker-1 (IO pool)
// Collecting 1 on: main
// Collecting 2 on: main
// Collecting 3 on: main
```

**Key principle**: `flowOn` affects **everything above it** in the chain, not below.

#### Why withContext Doesn't Work in Flows

You **cannot** use `withContext` inside a flow builder:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

// This DOESN'T WORK as expected
fun brokenFlow() = flow {
    withContext(Dispatchers.IO) {
        emit(1) // IllegalStateException: Flow invariant is violated
    }
}
```

**Why**: Flow's `emit` function is context-preserving. It must be called from the same coroutine context where the flow was collected. Using `withContext` changes the context, violating this invariant.

**Correct way:**

```kotlin
fun correctFlow() = flow {
    // Build flow on current context
    emit(1)
    emit(2)
}.flowOn(Dispatchers.IO) // Change context of entire upstream
```

#### Context Preservation in Flows

Flows are designed to be **context-preserving**:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

suspend fun demonstrateContextPreservation() {
    val flow = flow {
        println("Flow builder on: ${Thread.currentThread().name}")
        emit(1)
    }

    // Collect on Main
    withContext(Dispatchers.Main) {
        flow.collect {
            println("Collected on: ${Thread.currentThread().name}")
        }
    }
    // Output: Both on Main (context preserved)

    // Collect on IO
    withContext(Dispatchers.IO) {
        flow.collect {
            println("Collected on: ${Thread.currentThread().name}")
        }
    }
    // Output: Both on IO (context preserved)
}
```

**Without flowOn**, the flow executes in the collector's context.

#### flowOn Changes Upstream Context

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun demonstrateUpstreamChange() = runBlocking {
    flow {
        println("1. Emit in: ${Thread.currentThread().name}")
        emit("A")
    }
        .map { value ->
            println("2. Map in: ${Thread.currentThread().name}")
            value.lowercase()
        }
        .flowOn(Dispatchers.IO) // Affects blocks 1 and 2
        .map { value ->
            println("3. Map in: ${Thread.currentThread().name}")
            value.uppercase()
        }
        .collect { value ->
            println("4. Collect '$value' in: ${Thread.currentThread().name}")
        }
}

// Output:
// 1. Emit in: DefaultDispatcher-worker-1 (IO)
// 2. Map in: DefaultDispatcher-worker-1 (IO)
// 3. Map in: main
// 4. Collect 'A' in: main
```

**Visualization:**

```
[emit] -> [map lowercase] -> flowOn(IO) -> [map uppercase] -> [collect]
   ↑           ↑                               ↑                 ↑
   IO          IO                            Main              Main
```

#### How flowOn Introduces Buffering

`flowOn` creates a **channel-based buffer** between contexts:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun demonstrateBuffering() = runBlocking {
    flow {
        repeat(5) { i ->
            println("[${System.currentTimeMillis()}] Emitting $i")
            emit(i)
            delay(100) // Fast producer
        }
    }
        .flowOn(Dispatchers.IO) // Creates buffer here
        .collect { value ->
            println("[${System.currentTimeMillis()}] Collecting $value")
            delay(500) // Slow consumer
        }
}

// Output shows producer doesn't wait for consumer
// Buffer holds values until consumer ready
```

**Default buffer size**: 64 (from `Channel.BUFFERED`)

**Custom buffer:**

```kotlin
fun customBufferFlow() = flow {
    emit(1)
}
    .buffer(10) // Explicit buffer size
    .flowOn(Dispatchers.IO)
```

#### Channel Buffer Created by flowOn

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

// flowOn internally creates something like:
fun manualFlowOnEquivalent() = flow {
    emit(1)
    emit(2)
}
    .buffer(Channel.BUFFERED) // flowOn adds this
    .let { bufferedFlow ->
        flow {
            // Collect upstream on different dispatcher
            withContext(Dispatchers.IO) {
                bufferedFlow.collect { emit(it) }
            }
        }
    }
```

**Buffer characteristics:**
- **Capacity**: Default 64 (Channel.BUFFERED)
- **Overflow**: SUSPEND (backpressure)
- **Purpose**: Decouple producer/consumer speeds

#### Multiple flowOn Operators in Chain

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun demonstrateMultipleFlowOn() = runBlocking {
    flow {
        println("Emit on: ${Thread.currentThread().name}")
        emit(1)
    }
        .map {
            println("Map1 on: ${Thread.currentThread().name}")
            it * 2
        }
        .flowOn(Dispatchers.IO) // Changes context for emit + map1
        .map {
            println("Map2 on: ${Thread.currentThread().name}")
            it + 10
        }
        .flowOn(Dispatchers.Default) // Changes context for map2
        .collect {
            println("Collect $it on: ${Thread.currentThread().name}")
        }
}

// Output:
// Emit on: DefaultDispatcher-worker-1 (IO)
// Map1 on: DefaultDispatcher-worker-1 (IO)
// Map2 on: DefaultDispatcher-worker-2 (Default)
// Collect 12 on: main
```

**Visualization:**

```
[emit] -> [map1] -> flowOn(IO) -> [map2] -> flowOn(Default) -> [collect]
   ↑        ↑                        ↑                            ↑
   IO       IO                     Default                      Main
```

**Each flowOn**:
- Affects all operators **above** it
- Creates a separate buffer
- Enables parallel pipeline processing

#### Performance Implications

**Benchmark: With vs Without flowOn**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlin.system.measureTimeMillis

suspend fun cpuIntensiveOperation(value: Int): Int {
    // Simulate heavy CPU work
    var result = value
    repeat(1_000_000) {
        result = (result * 31 + it) % 1000
    }
    return result
}

fun benchmarkFlowOn() = runBlocking {
    // Without flowOn (sequential on main)
    val withoutFlowOn = measureTimeMillis {
        flow {
            repeat(10) { emit(it) }
        }
            .map { cpuIntensiveOperation(it) }
            .collect { }
    }

    // With flowOn (parallel processing)
    val withFlowOn = measureTimeMillis {
        flow {
            repeat(10) { emit(it) }
        }
            .map { cpuIntensiveOperation(it) }
            .flowOn(Dispatchers.Default)
            .collect { }
    }

    println("Without flowOn: ${withoutFlowOn}ms")
    println("With flowOn: ${withFlowOn}ms")
    println("Speedup: ${withoutFlowOn.toDouble() / withFlowOn}x")
}

// Typical results:
// Without flowOn: 2000ms
// With flowOn: 2000ms (similar, but doesn't block collector's thread)
// Benefit: Collector's thread is free while CPU work happens
```

**Memory overhead:**

```kotlin
// Each flowOn creates a Channel buffer
val flow = flow { emit(1) }
    .flowOn(Dispatchers.IO)      // Buffer 1 (64 slots)
    .flowOn(Dispatchers.Default) // Buffer 2 (64 slots)
    .flowOn(Dispatchers.Main)    // Buffer 3 (64 slots)

// Memory: 3 * 64 * sizeof(element)
// Trade-off: Memory for concurrency
```

#### flowOn Placement in Operator Chain

**Where you place flowOn matters!**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

// Example 1: flowOn at end (affects all upstream)
fun flowOnAtEnd() = flow {
    println("Emit on: ${Thread.currentThread().name}")
    emit(1)
}
    .map {
        println("Map on: ${Thread.currentThread().name}")
        it * 2
    }
    .filter {
        println("Filter on: ${Thread.currentThread().name}")
        it > 0
    }
    .flowOn(Dispatchers.IO) // All above run on IO

// Example 2: flowOn in middle (affects only above)
fun flowOnInMiddle() = flow {
    println("Emit on: ${Thread.currentThread().name}")
    emit(1)
}
    .flowOn(Dispatchers.IO) // Only emit on IO
    .map {
        println("Map on: ${Thread.currentThread().name}")
        it * 2
    }
    .filter {
        println("Filter on: ${Thread.currentThread().name}")
        it > 0
    } // map and filter on collector's context
```

**Best practices:**

1. **Place flowOn right after expensive operations:**
```kotlin
flow { /* fetch data */ }
    .flowOn(Dispatchers.IO) // I/O on IO pool
    .map { /* parse */ }
    .flowOn(Dispatchers.Default) // Parsing on CPU pool
    .collect { /* update UI */ } // UI on Main
```

2. **Don't overuse flowOn:**
```kotlin
// Bad: Too many flowOn
flow { emit(1) }
    .flowOn(Dispatchers.IO)
    .map { it * 2 }
    .flowOn(Dispatchers.IO) // Unnecessary context switch
    .collect { }

// Good: One flowOn for related operations
flow { emit(1) }
    .map { it * 2 }
    .flowOn(Dispatchers.IO) // Both on IO
    .collect { }
```

#### Upstream Vs Downstream Context

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun demonstrateUpstreamDownstream() = runBlocking {
    println("Starting on: ${Thread.currentThread().name}")

    flow {
        println("UPSTREAM: Emit on ${Thread.currentThread().name}")
        emit(1)
    }
        .onEach {
            println("UPSTREAM: onEach on ${Thread.currentThread().name}")
        }
        .flowOn(Dispatchers.IO) // <-- Dividing line
        .onEach {
            println("DOWNSTREAM: onEach on ${Thread.currentThread().name}")
        }
        .collect {
            println("DOWNSTREAM: Collect on ${Thread.currentThread().name}")
        }
}

// Output:
// Starting on: main
// UPSTREAM: Emit on DefaultDispatcher-worker-1 (IO)
// UPSTREAM: onEach on DefaultDispatcher-worker-1 (IO)
// DOWNSTREAM: onEach on main
// DOWNSTREAM: Collect on main
```

**Rule**: Everything **above** flowOn = upstream (affected), everything **below** = downstream (not affected).

#### Real Example: Loading Data from Network and Database

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

data class User(val id: Int, val name: String)

class UserRepository {
    // Simulate network call
    private suspend fun fetchUsersFromNetwork(): List<User> {
        delay(1000)
        return listOf(User(1, "Alice"), User(2, "Bob"))
    }

    // Simulate database save
    private suspend fun saveToDatabase(user: User) {
        delay(100)
        println("Saved ${user.name} to DB")
    }

    // Flow with proper dispatcher usage
    fun syncUsers(): Flow<User> = flow {
        println("Fetching from network on: ${Thread.currentThread().name}")
        val users = fetchUsersFromNetwork()
        users.forEach { emit(it) }
    }
        .flowOn(Dispatchers.IO) // Network I/O on IO dispatcher
        .onEach { user ->
            println("Parsing $user on: ${Thread.currentThread().name}")
            // Heavy parsing could go here
        }
        .flowOn(Dispatchers.Default) // CPU work on Default
        .onEach { user ->
            println("Saving ${user.name} on: ${Thread.currentThread().name}")
            saveToDatabase(user)
        }
        .flowOn(Dispatchers.IO) // Database I/O on IO
}

suspend fun demonstrateRealWorld() {
    val repo = UserRepository()
    repo.syncUsers().collect { user ->
        println("UI update for ${user.name} on: ${Thread.currentThread().name}")
    }
}
```

**Context flow:**
```
[Network fetch] -> flowOn(IO) -> [Parsing] -> flowOn(Default) -> [DB save] -> flowOn(IO) -> [UI update]
      ↑ IO                          ↑ Default                        ↑ IO              ↑ Main
```

#### flowOn with Custom Buffer Capacity

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun customBufferWithFlowOn() = flow {
    repeat(100) { emit(it) }
}
    .buffer(10) // Small buffer
    .flowOn(Dispatchers.IO)

// vs

fun defaultBufferWithFlowOn() = flow {
    repeat(100) { emit(it) }
}
    .flowOn(Dispatchers.IO) // Buffer 64 by default
```

**When to customize buffer:**

- **Smaller buffer**: Memory-constrained, want backpressure
- **Larger buffer**: Producer much faster than consumer
- **Unbounded**: Special cases (use carefully!)

```kotlin
fun unboundedBuffer() = flow {
    repeat(1000) { emit(it) }
}
    .buffer(Channel.UNLIMITED)
    .flowOn(Dispatchers.IO)
// Warning: Can cause OOM if producer >> consumer
```

#### Common Mistakes

**1. flowOn on terminal operator**

```kotlin
// Wrong: flowOn after collect does nothing
flow { emit(1) }
    .collect { }
    .flowOn(Dispatchers.IO) // No effect! Collect is terminal

// Wrong: flowOn after toList
flow { emit(1) }
    .toList()
    .let { /* process */ }
// .flowOn here would do nothing

// Correct: flowOn before terminal operator
flow { emit(1) }
    .flowOn(Dispatchers.IO)
    .collect { }
```

**2. Unnecessary context switches**

```kotlin
// Bad: Context switch for trivial operation
flow { emit(1) }
    .map { it + 1 } // Trivial operation
    .flowOn(Dispatchers.Default) // Unnecessary overhead

// Good: Only switch for expensive operations
flow {
    // Expensive I/O
    readFromDatabase()
}
    .flowOn(Dispatchers.IO)
    .map { it + 1 } // Trivial, on collector's context
```

**3. Using withContext in flow builder**

```kotlin
// Wrong: Breaks flow invariant
flow {
    withContext(Dispatchers.IO) {
        emit(1) // IllegalStateException
    }
}

// Correct: Use flowOn
flow {
    emit(1)
}.flowOn(Dispatchers.IO)
```

#### Debugging Context Switches

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun debuggableFlow() = flow {
    println("[${Thread.currentThread().name}] Emitting")
    emit(1)
}
    .onEach { println("[${Thread.currentThread().name}] After emit") }
    .flowOn(Dispatchers.IO)
    .onEach { println("[${Thread.currentThread().name}] After flowOn") }
    .map {
        println("[${Thread.currentThread().name}] Mapping")
        it * 2
    }
    .flowOn(Dispatchers.Default)
    .onEach { println("[${Thread.currentThread().name}] After second flowOn") }

suspend fun debugFlow() {
    withContext(Dispatchers.Main) {
        debuggableFlow().collect { value ->
            println("[${Thread.currentThread().name}] Collected: $value")
        }
    }
}
```

**Output shows context at each stage:**
```
[DefaultDispatcher-worker-1] Emitting
[DefaultDispatcher-worker-1] After emit
[DefaultDispatcher-worker-2] After flowOn
[DefaultDispatcher-worker-2] Mapping
[main] After second flowOn
[main] Collected: 2
```

#### Best Practices

**1. Match dispatcher to workload**

```kotlin
// I/O operations -> Dispatchers.IO
flow {
    fetchFromNetwork()
    readFromFile()
}
    .flowOn(Dispatchers.IO)

// CPU-intensive -> Dispatchers.Default
flow {
    parseJson()
    processImage()
}
    .flowOn(Dispatchers.Default)

// UI updates -> Dispatchers.Main (or collector's context)
flow { /* ... */ }
    .collect {
        updateUI(it) // On Main
    }
```

**2. Minimize flowOn calls**

```kotlin
// Bad: Multiple flowOn for same dispatcher
flow { operationA() }
    .flowOn(Dispatchers.IO)
    .map { operationB(it) }
    .flowOn(Dispatchers.IO) // Unnecessary

// Good: Group operations
flow {
    val a = operationA()
    operationB(a)
}
    .flowOn(Dispatchers.IO)
```

**3. Place flowOn strategically**

```kotlin
// Good: flowOn right after expensive operations
flow { expensiveNetworkCall() }
    .flowOn(Dispatchers.IO) // Immediately after I/O
    .map { cheapTransform(it) } // On collector's thread
```

#### Testing Flows with flowOn

```kotlin
import kotlinx.coroutines.test.*
import kotlinx.coroutines.flow.*
import org.junit.Test
import kotlin.test.assertEquals

class FlowOnTests {
    @Test
    fun testFlowOnChangesContext() = runTest {
        val dispatcher = StandardTestDispatcher(testScheduler)

        val results = flow {
            emit(Thread.currentThread().name)
        }
            .flowOn(dispatcher)
            .toList()

        // Verify emission happened on test dispatcher
        assert(results[0].contains("Test"))
    }

    @Test
    fun testFlowOnBuffering() = runTest {
        var emitCount = 0
        var collectCount = 0

        flow {
            repeat(10) {
                emit(it)
                emitCount++
            }
        }
            .flowOn(StandardTestDispatcher(testScheduler))
            .collect {
                collectCount++
            }

        assertEquals(10, emitCount)
        assertEquals(10, collectCount)
    }
}
```

### Summary

**flowOn** changes the **upstream** execution context in flows:

- **Affects**: Everything above flowOn in the chain
- **Creates**: Channel-based buffer (default 64)
- **Use for**: I/O operations, CPU-intensive work
- **Cannot use**: `withContext` in flow builder (use flowOn instead)
- **Multiple flowOn**: Each affects operations above it, creates separate buffer
- **Placement**: Right after expensive operations
- **Avoid**: On terminal operators, for trivial operations

**Key insight**: flowOn enables pipeline parallelism - different flow stages can run on different threads concurrently.

---

## Russian Version / Русская Версия

### Вопрос
Что делает оператор `flowOn` в Kotlin потоках? Чем он отличается от `withContext`? Объясните сохранение контекста, поведение буферизации, множественные операторы flowOn в цепочке и влияние на производительность с реальными примерами.

### Ответ

#### Что Делает flowOn

`flowOn` изменяет **upstream** контекст выполнения потока. Он влияет на то, где производятся эмиссии потока, а не где они собираются.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun demonstrateFlowOn() = runBlocking {
    flow {
        println("Эмитим на: ${Thread.currentThread().name}")
        emit(1)
        emit(2)
    }
        .flowOn(Dispatchers.IO) // Изменить upstream контекст
        .collect { value ->
            println("Собираем $value на: ${Thread.currentThread().name}")
        }
}

// Вывод:
// Эмитим на: DefaultDispatcher-worker-1 (IO пул)
// Собираем 1 на: main
// Собираем 2 на: main
```

**Ключевой принцип**: `flowOn` влияет на **всё выше** его в цепочке, не ниже.

#### Почему withContext Не Работает В Потоках

Вы **не можете** использовать `withContext` внутри flow builder:

```kotlin
// Это НЕ РАБОТАЕТ как ожидается
fun brokenFlow() = flow {
    withContext(Dispatchers.IO) {
        emit(1) // IllegalStateException: Flow invariant is violated
    }
}
```

**Почему**: Функция `emit` потока сохраняет контекст. Она должна вызываться из того же контекста корутины, где поток был собран. Использование `withContext` изменяет контекст, нарушая этот инвариант.

**Правильный способ:**

```kotlin
fun correctFlow() = flow {
    emit(1)
    emit(2)
}.flowOn(Dispatchers.IO) // Изменить контекст всего upstream
```

#### Сохранение Контекста В Потоках

Потоки спроектированы так, чтобы быть **контекстосохраняющими**:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

suspend fun demonstrateContextPreservation() {
    val flow = flow {
        println("Flow builder на: ${Thread.currentThread().name}")
        emit(1)
    }

    // Собираем на Main
    withContext(Dispatchers.Main) {
        flow.collect {
            println("Собрано на: ${Thread.currentThread().name}")
        }
    }
    // Вывод: Оба на Main (контекст сохранён)

    // Собираем на IO
    withContext(Dispatchers.IO) {
        flow.collect {
            println("Собрано на: ${Thread.currentThread().name}")
        }
    }
    // Вывод: Оба на IO (контекст сохранён)
}
```

**Без flowOn**, поток выполняется в контексте коллектора.

#### flowOn Изменяет Upstream Контекст

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun demonstrateUpstreamChange() = runBlocking {
    flow {
        println("1. Emit в: ${Thread.currentThread().name}")
        emit("A")
    }
        .map { value ->
            println("2. Map в: ${Thread.currentThread().name}")
            value.lowercase()
        }
        .flowOn(Dispatchers.IO) // Влияет на блоки 1 и 2
        .map { value ->
            println("3. Map в: ${Thread.currentThread().name}")
            value.uppercase()
        }
        .collect { value ->
            println("4. Collect '$value' в: ${Thread.currentThread().name}")
        }
}

// Вывод:
// 1. Emit в: DefaultDispatcher-worker-1 (IO)
// 2. Map в: DefaultDispatcher-worker-1 (IO)
// 3. Map в: main
// 4. Collect 'A' в: main
```

**Визуализация:**

```
[emit] -> [map lowercase] -> flowOn(IO) -> [map uppercase] -> [collect]
   ↑           ↑                               ↑                 ↑
   IO          IO                            Main              Main
```

#### Как flowOn Вносит Буферизацию

`flowOn` создаёт **буфер на основе канала** между контекстами:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun demonstrateBuffering() = runBlocking {
    flow {
        repeat(5) { i ->
            println("Эмитим $i")
            emit(i)
            delay(100) // Быстрый производитель
        }
    }
        .flowOn(Dispatchers.IO) // Создаёт буфер здесь
        .collect { value ->
            println("Собираем $value")
            delay(500) // Медленный потребитель
        }
}

// Вывод показывает что производитель не ждёт потребителя
// Буфер хранит значения пока потребитель не готов
```

**Размер буфера по умолчанию**: 64 (из `Channel.BUFFERED`)

**Пользовательский буфер:**

```kotlin
fun customBufferFlow() = flow {
    emit(1)
}
    .buffer(10) // Явный размер буфера
    .flowOn(Dispatchers.IO)
```

#### Буфер Канала, Создаваемый flowOn

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

// flowOn внутри создаёт что-то вроде:
fun manualFlowOnEquivalent() = flow {
    emit(1)
    emit(2)
}
    .buffer(Channel.BUFFERED) // flowOn добавляет это
    .let { bufferedFlow ->
        flow {
            // Собираем upstream на другом диспетчере
            withContext(Dispatchers.IO) {
                bufferedFlow.collect { emit(it) }
            }
        }
    }
```

**Характеристики буфера:**
- **Ёмкость**: По умолчанию 64 (Channel.BUFFERED)
- **Переполнение**: SUSPEND (противодавление)
- **Назначение**: Разделить скорости производителя/потребителя

#### Несколько Операторов flowOn В Цепочке

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun demonstrateMultipleFlowOn() = runBlocking {
    flow {
        println("Emit на: ${Thread.currentThread().name}")
        emit(1)
    }
        .map {
            println("Map1 на: ${Thread.currentThread().name}")
            it * 2
        }
        .flowOn(Dispatchers.IO) // Изменяет контекст для emit + map1
        .map {
            println("Map2 на: ${Thread.currentThread().name}")
            it + 10
        }
        .flowOn(Dispatchers.Default) // Изменяет контекст для map2
        .collect {
            println("Collect $it на: ${Thread.currentThread().name}")
        }
}
```

**Визуализация:**

```
[emit] -> [map1] -> flowOn(IO) -> [map2] -> flowOn(Default) -> [collect]
   ↑        ↑                        ↑                            ↑
   IO       IO                     Default                      Main
```

**Каждый flowOn**:
- Влияет на все операторы **выше** него
- Создаёт отдельный буфер
- Обеспечивает параллельную обработку конвейера

#### Влияние На Производительность

**Бенчмарк: С и Без flowOn**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlin.system.measureTimeMillis

suspend fun cpuIntensiveOperation(value: Int): Int {
    // Симулируем тяжёлую CPU работу
    var result = value
    repeat(1_000_000) {
        result = (result * 31 + it) % 1000
    }
    return result
}

fun benchmarkFlowOn() = runBlocking {
    // Без flowOn (последовательно на main)
    val withoutFlowOn = measureTimeMillis {
        flow {
            repeat(10) { emit(it) }
        }
            .map { cpuIntensiveOperation(it) }
            .collect { }
    }

    // С flowOn (параллельная обработка)
    val withFlowOn = measureTimeMillis {
        flow {
            repeat(10) { emit(it) }
        }
            .map { cpuIntensiveOperation(it) }
            .flowOn(Dispatchers.Default)
            .collect { }
    }

    println("Без flowOn: ${withoutFlowOn}мс")
    println("С flowOn: ${withFlowOn}мс")
    println("Ускорение: ${withoutFlowOn.toDouble() / withFlowOn}x")
}

// Типичные результаты:
// Без flowOn: 2000мс
// С flowOn: 2000мс (похоже, но не блокирует поток коллектора)
// Преимущество: Поток коллектора свободен пока идёт CPU работа
```

**Накладные расходы памяти:**

```kotlin
// Каждый flowOn создаёт буфер Channel
val flow = flow { emit(1) }
    .flowOn(Dispatchers.IO)      // Буфер 1 (64 слота)
    .flowOn(Dispatchers.Default) // Буфер 2 (64 слота)
    .flowOn(Dispatchers.Main)    // Буфер 3 (64 слота)

// Память: 3 * 64 * sizeof(element)
// Компромисс: Память за параллелизм
```

#### Размещение flowOn В Цепочке Операторов

**Место размещения flowOn имеет значение!**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

// Пример 1: flowOn в конце (влияет на весь upstream)
fun flowOnAtEnd() = flow {
    println("Emit на: ${Thread.currentThread().name}")
    emit(1)
}
    .map {
        println("Map на: ${Thread.currentThread().name}")
        it * 2
    }
    .filter {
        println("Filter на: ${Thread.currentThread().name}")
        it > 0
    }
    .flowOn(Dispatchers.IO) // Всё выше работает на IO

// Пример 2: flowOn в середине (влияет только на то, что выше)
fun flowOnInMiddle() = flow {
    println("Emit на: ${Thread.currentThread().name}")
    emit(1)
}
    .flowOn(Dispatchers.IO) // Только emit на IO
    .map {
        println("Map на: ${Thread.currentThread().name}")
        it * 2
    }
    .filter {
        println("Filter на: ${Thread.currentThread().name}")
        it > 0
    } // map и filter на контексте коллектора
```

**Лучшие практики:**

1. **Размещайте flowOn сразу после дорогих операций:**
```kotlin
flow { /* fetch data */ }
    .flowOn(Dispatchers.IO) // I/O на IO пуле
    .map { /* parse */ }
    .flowOn(Dispatchers.Default) // Парсинг на CPU пуле
    .collect { /* update UI */ } // UI на Main
```

2. **Не злоупотребляйте flowOn:**
```kotlin
// Плохо: Слишком много flowOn
flow { emit(1) }
    .flowOn(Dispatchers.IO)
    .map { it * 2 }
    .flowOn(Dispatchers.IO) // Ненужное переключение контекста
    .collect { }

// Хорошо: Один flowOn для связанных операций
flow { emit(1) }
    .map { it * 2 }
    .flowOn(Dispatchers.IO) // Оба на IO
    .collect { }
```

#### Upstream Против Downstream Контекста

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun demonstrateUpstreamDownstream() = runBlocking {
    println("Начинаем на: ${Thread.currentThread().name}")

    flow {
        println("UPSTREAM: Emit на ${Thread.currentThread().name}")
        emit(1)
    }
        .onEach {
            println("UPSTREAM: onEach на ${Thread.currentThread().name}")
        }
        .flowOn(Dispatchers.IO) // <-- Разделяющая линия
        .onEach {
            println("DOWNSTREAM: onEach на ${Thread.currentThread().name}")
        }
        .collect {
            println("DOWNSTREAM: Collect на ${Thread.currentThread().name}")
        }
}

// Вывод:
// Начинаем на: main
// UPSTREAM: Emit на DefaultDispatcher-worker-1 (IO)
// UPSTREAM: onEach на DefaultDispatcher-worker-1 (IO)
// DOWNSTREAM: onEach на main
// DOWNSTREAM: Collect на main
```

**Правило**: Всё **выше** flowOn = upstream (затронуто), всё **ниже** = downstream (не затронуто).

#### Реальный Пример: Загрузка Данных Из Сети И Базы Данных

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

data class User(val id: Int, val name: String)

class UserRepository {
    private suspend fun fetchUsersFromNetwork(): List<User> {
        delay(1000)
        return listOf(User(1, "Алиса"), User(2, "Боб"))
    }

    private suspend fun saveToDatabase(user: User) {
        delay(100)
        println("Сохранён ${user.name} в БД")
    }

    fun syncUsers(): Flow<User> = flow {
        println("Загрузка из сети на: ${Thread.currentThread().name}")
        val users = fetchUsersFromNetwork()
        users.forEach { emit(it) }
    }
        .flowOn(Dispatchers.IO) // Сетевой I/O на IO диспетчере
        .onEach { user ->
            println("Парсинг $user на: ${Thread.currentThread().name}")
        }
        .flowOn(Dispatchers.Default) // CPU работа на Default
        .onEach { user ->
            println("Сохранение ${user.name} на: ${Thread.currentThread().name}")
            saveToDatabase(user)
        }
        .flowOn(Dispatchers.IO) // БД I/O на IO
}
```

**Поток контекста:**
```
[Загрузка из сети] -> flowOn(IO) -> [Парсинг] -> flowOn(Default) -> [Сохранение в БД] -> flowOn(IO) -> [Обновление UI]
      ↑ IO                             ↑ Default                           ↑ IO                    ↑ Main
```

#### flowOn С Пользовательской Ёмкостью Буфера

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun customBufferWithFlowOn() = flow {
    repeat(100) { emit(it) }
}
    .buffer(10) // Маленький буфер
    .flowOn(Dispatchers.IO)

// против

fun defaultBufferWithFlowOn() = flow {
    repeat(100) { emit(it) }
}
    .flowOn(Dispatchers.IO) // Буфер 64 по умолчанию
```

**Когда настраивать буфер:**

- **Меньший буфер**: Ограниченная память, нужно противодавление
- **Больший буфер**: Производитель намного быстрее потребителя
- **Неограниченный**: Особые случаи (используйте осторожно!)

```kotlin
fun unboundedBuffer() = flow {
    repeat(1000) { emit(it) }
}
    .buffer(Channel.UNLIMITED)
    .flowOn(Dispatchers.IO)
// Предупреждение: Может вызвать OOM если производитель >> потребителя
```

#### Типичные Ошибки

**1. flowOn на терминальном операторе**

```kotlin
// Неправильно: flowOn после collect ничего не делает
flow { emit(1) }
    .collect { }
    .flowOn(Dispatchers.IO) // Нет эффекта! Collect терминальный

// Правильно: flowOn перед терминальным оператором
flow { emit(1) }
    .flowOn(Dispatchers.IO)
    .collect { }
```

**2. Ненужные переключения контекста**

```kotlin
// Плохо: Переключение контекста для тривиальной операции
flow { emit(1) }
    .map { it + 1 } // Тривиальная операция
    .flowOn(Dispatchers.Default) // Ненужные накладные расходы

// Хорошо: Только переключение для дорогих операций
flow {
    readFromDatabase() // Дорогой I/O
}
    .flowOn(Dispatchers.IO)
    .map { it + 1 } // Тривиально, на контексте коллектора
```

**3. Использование withContext в flow builder**

```kotlin
// Неправильно: Нарушает инвариант потока
flow {
    withContext(Dispatchers.IO) {
        emit(1) // IllegalStateException
    }
}

// Правильно: Используйте flowOn
flow {
    emit(1)
}.flowOn(Dispatchers.IO)
```

#### Лучшие Практики

**1. Сопоставляйте диспетчер с нагрузкой**

```kotlin
// I/O операции -> Dispatchers.IO
flow {
    fetchFromNetwork()
    readFromFile()
}
    .flowOn(Dispatchers.IO)

// CPU-интенсивное -> Dispatchers.Default
flow {
    parseJson()
    processImage()
}
    .flowOn(Dispatchers.Default)
```

**2. Минимизируйте вызовы flowOn**

```kotlin
// Плохо: Несколько flowOn для одного диспетчера
flow { operationA() }
    .flowOn(Dispatchers.IO)
    .map { operationB(it) }
    .flowOn(Dispatchers.IO) // Ненужно

// Хорошо: Группируйте операции
flow {
    val a = operationA()
    operationB(a)
}
    .flowOn(Dispatchers.IO)
```

**3. Размещайте flowOn стратегически**

```kotlin
// Хорошо: flowOn сразу после дорогих операций
flow { expensiveNetworkCall() }
    .flowOn(Dispatchers.IO) // Сразу после I/O
    .map { cheapTransform(it) } // На потоке коллектора
```

#### Отладка Переключений Контекста

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun debuggableFlow() = flow {
    println("[${Thread.currentThread().name}] Эмиссия")
    emit(1)
}
    .onEach { println("[${Thread.currentThread().name}] После emit") }
    .flowOn(Dispatchers.IO)
    .onEach { println("[${Thread.currentThread().name}] После flowOn") }
    .map {
        println("[${Thread.currentThread().name}] Mapping")
        it * 2
    }
    .flowOn(Dispatchers.Default)
    .onEach { println("[${Thread.currentThread().name}] После второго flowOn") }

suspend fun debugFlow() {
    withContext(Dispatchers.Main) {
        debuggableFlow().collect { value ->
            println("[${Thread.currentThread().name}] Собрано: $value")
        }
    }
}
```

**Вывод показывает контекст на каждом этапе:**
```
[DefaultDispatcher-worker-1] Эмиссия
[DefaultDispatcher-worker-1] После emit
[DefaultDispatcher-worker-2] После flowOn
[DefaultDispatcher-worker-2] Mapping
[main] После второго flowOn
[main] Собрано: 2
```

#### Тестирование Потоков С flowOn

```kotlin
import kotlinx.coroutines.test.*
import kotlinx.coroutines.flow.*
import org.junit.Test
import kotlin.test.assertEquals

class FlowOnTests {
    @Test
    fun testFlowOnChangesContext() = runTest {
        val dispatcher = StandardTestDispatcher(testScheduler)

        val results = flow {
            emit(Thread.currentThread().name)
        }
            .flowOn(dispatcher)
            .toList()

        // Проверяем что эмиссия произошла на тестовом диспетчере
        assert(results[0].contains("Test"))
    }

    @Test
    fun testFlowOnBuffering() = runTest {
        var emitCount = 0
        var collectCount = 0

        flow {
            repeat(10) {
                emit(it)
                emitCount++
            }
        }
            .flowOn(StandardTestDispatcher(testScheduler))
            .collect {
                collectCount++
            }

        assertEquals(10, emitCount)
        assertEquals(10, collectCount)
    }
}
```

### Резюме

**flowOn** изменяет **upstream** контекст выполнения в потоках:

- **Влияет**: На всё выше flowOn в цепочке
- **Создаёт**: Буфер на основе канала (по умолчанию 64)
- **Используйте для**: I/O операций, CPU-интенсивной работы
- **Нельзя использовать**: `withContext` в flow builder (используйте flowOn вместо него)
- **Множественный flowOn**: Каждый влияет на операции выше него, создаёт отдельный буфер
- **Размещение**: Сразу после дорогих операций
- **Избегайте**: На терминальных операторах, для тривиальных операций

**Ключевое понимание**: flowOn обеспечивает параллелизм конвейера - разные стадии потока могут выполняться на разных потоках одновременно.

---

## Follow-ups

1. How does flowOn's internal buffer handle backpressure when the downstream collector is slower than upstream emissions?

2. What happens to exception propagation when flowOn is used? Does it affect how exceptions travel up the flow chain?

3. How would you implement a custom operator similar to flowOn but with different buffering strategies?

4. Explain the performance trade-offs between using multiple flowOn operators vs a single flowOn at the end of the chain.

5. How does flowOn interact with StateFlow and SharedFlow? Can you use flowOn with hot flows?

6. What are the implications of using flowOn with operators like `retry()` or `catch()`?

7. How would you design a monitoring system to track context switches in a complex flow pipeline?

## References

- [Kotlin Flow Documentation](https://kotlinlang.org/docs/flow.html)
- [flowOn API Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/flow-on.html)
- [Flow Context Preservation](https://kotlinlang.org/docs/flow.html#flow-context)
- [Roman Elizarov - Flow Dispatchers](https://medium.com/@elizarov/reactive-streams-and-kotlin-flows-bfd12772cda4)
- [Coroutines Guide - Flow](https://kotlinlang.org/docs/flow.html)

## Related Questions

### Related ("hard")
- [[q-catch-operator-flow--kotlin--medium]] - Flow
- [[q-coroutine-context-elements--kotlin--hard]] - Coroutines
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-hot-cold-flows--kotlin--medium]] - Coroutines

### Advanced (Harder)
- [[q-coroutine-context-detailed--kotlin--hard]] - Coroutines
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines

### Related (Hard)
- [[q-flow-backpressure--kotlin--hard]] - Backpressure handling
- [[q-flow-backpressure-strategies--kotlin--hard]] - Backpressure strategies
- [[q-flow-operators-deep-dive--kotlin--hard]] - Deep dive into operators
- [[q-flow-performance--kotlin--hard]] - Performance optimization
- [[q-flow-testing-advanced--kotlin--hard]] - Advanced Flow testing

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction

## Tags
#kotlin #coroutines #flowon #context-switching #dispatchers #flow #performance #buffer

