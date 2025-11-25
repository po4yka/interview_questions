---
id: kotlin-125
title: "Оператор flowOn и переключение контекста во Flow / flowOn operator and context switching in flows"
aliases: [flow-context-switching, flowon-operator, flowon-vs-withcontext, kotlin-flowon]
topic: kotlin
subtopics: [coroutines, flow, performance]
question_kind: theory
difficulty: hard
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-coroutines, c-flow, q-coroutine-context-elements--kotlin--hard, q-flow-operators-map-filter--kotlin--medium]
created: 2025-10-12
updated: 2025-11-11
tags: ["buffer", "context-switching", "coroutines", "difficulty/hard", "dispatchers", "flow-operators", "flow", "flowon", "kotlin", "performance"]

date created: Saturday, October 18th 2025, 3:06:32 pm
date modified: Tuesday, November 25th 2025, 8:53:51 pm
---

# Вопрос (RU)
> Что делает оператор `flowOn` в `Flow` в Kotlin? Чем он отличается от `withContext`? Объясните сохранение контекста, поведение буферизации, использование нескольких `flowOn` в цепочке и влияние на производительность с реальными примерами.

# Question (EN)
> What does the `flowOn` operator do in Kotlin `Flow`s? How does it differ from `withContext`? Explain context preservation, buffering behavior, multiple `flowOn` operators in a chain, and performance implications with real-world examples.

## Ответ (RU)

### Что Делает `flowOn`

`flowOn` запускает upstream-операторы потока в указанном контексте и создаёт асинхронную границу. Он влияет на то, где выполняются эмиссии и обработка выше него в цепочке, а не на контекст коллектора ниже него.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun demonstrateFlowOn() = runBlocking {
    flow {
        println("Эмитим на: ${Thread.currentThread().name}")
        emit(1)
        emit(2)
        emit(3)
    }
        .flowOn(Dispatchers.IO) // Переносим upstream в IO-контекст
        .collect { value ->
            println("Собираем $value на: ${Thread.currentThread().name}")
        }
}

// Возможный вывод:
// Эмитим на: DefaultDispatcher-worker-1 (IO пул)
// Собираем 1 на: main
// Собираем 2 на: main
// Собираем 3 на: main
```

Ключевой принцип: `flowOn` влияет на всё, что выше него в цепочке (upstream), и не меняет то, что ниже (downstream).

### Почему `withContext` Ограничен В `flow`

Нельзя произвольно менять контекст вокруг `emit` внутри `flow {}`. Пример ниже некорректен:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

// Это НЕ РАБОТАЕТ как ожидается
fun brokenFlow() = flow {
    withContext(Dispatchers.IO) {
        emit(1) // IllegalStateException: Flow invariant is violated
    }
}
```

Почему: холодные потоки по умолчанию контекстосохраняющие. Код внутри `flow {}` должен выполняться в контексте коллектора (если не изменён `flowOn`). Вызов `emit` из другого контекста нарушает инвариант сохранения контекста.

Правильный способ:

```kotlin
fun correctFlow() = flow {
    emit(1)
    emit(2)
}.flowOn(Dispatchers.IO) // Переносим выполнение upstream на IO
```

### Сохранение Контекста В Потоках

По умолчанию потоки сохраняют контекст:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

suspend fun demonstrateContextPreservation() {
    val f = flow {
        println("Flow builder на: ${Thread.currentThread().name}")
        emit(1)
    }

    // Собираем на Main
    withContext(Dispatchers.Main) {
        f.collect {
            println("Собрано на: ${Thread.currentThread().name}")
        }
    }
    // Оба лога на Main

    // Собираем на IO
    withContext(Dispatchers.IO) {
        f.collect {
            println("Собрано на: ${Thread.currentThread().name}")
        }
    }
    // Оба лога на IO
}
```

Без `flowOn` весь поток выполняется в контексте коллектора.

### `flowOn` Изменяет Upstream-контекст

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
        .flowOn(Dispatchers.IO) // Влияет на 1 и 2
        .map { value ->
            println("3. Map в: ${Thread.currentThread().name}")
            value.uppercase()
        }
        .collect { value ->
            println("4. Collect '$value' в: ${Thread.currentThread().name}")
        }
}

// Возможный вывод:
// 1. Emit в: DefaultDispatcher-worker-1 (IO)
// 2. Map в: DefaultDispatcher-worker-1 (IO)
// 3. Map в: main
// 4. Collect 'A' в: main
```

Визуализация:

```
[emit] -> [map lowercase] -> flowOn(IO) -> [map uppercase] -> [collect]
   ↑           ↑                               ↑                 ↑
   IO          IO                            Main              Main
```

### Как `flowOn` Добавляет Буферизацию

`flowOn` создаёт границу на основе канала между контекстами (это часть контрактного поведения: используется буферизированная передача значений между upstream и downstream):

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun demonstrateBuffering() = runBlocking {
    flow {
        repeat(5) { i ->
            println("[${System.currentTimeMillis()}] Эмитим $i")
            emit(i)
            delay(100) // Быстрый производитель
        }
    }
        .flowOn(Dispatchers.IO) // Граница и буфер здесь
        .collect { value ->
            println("[${System.currentTimeMillis()}] Собираем $value")
            delay(500) // Медленный потребитель
        }
}

// Вывод показывает, что producer может опережать consumer до ёмкости буфера
```

Размер буфера по умолчанию: 64 (`Channel.BUFFERED`).

Пользовательский буфер:

```kotlin
fun customBufferFlow() = flow {
    emit(1)
}
    .buffer(10) // Явный буфер до переключения контекста
    .flowOn(Dispatchers.IO)
```

### Буфер Канала, Создаваемый `flowOn` (концептуально)

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

// Концептуальное приближение поведения flowOn.
// Не используйте как реальную реализацию, это только иллюстрация разнесения контекстов через буфер.
fun manualFlowOnEquivalent() = flow {
    emit(1)
    emit(2)
}
    .buffer(Channel.BUFFERED)
    .let { bufferedFlow ->
        flow {
            withContext(Dispatchers.IO) {
                bufferedFlow.collect { emit(it) }
            }
        }
    }
```

Замечания:
- Это не точная реализация `flowOn` и не рекомендуется как паттерн; цель — показать, что:
  - есть буфер между контекстами,
  - upstream может работать на другом диспетчере,
  - downstream читает из буфера.
- Характеристики по умолчанию:
  - Ёмкость: 64 (`Channel.BUFFERED`)
  - Переполнение: `SUSPEND` (backpressure)

### Несколько Операторов `flowOn` В Цепочке

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
        .flowOn(Dispatchers.IO) // Влияет на emit + Map1
        .map {
            println("Map2 на: ${Thread.currentThread().name}")
            it + 10
        }
        .flowOn(Dispatchers.Default) // Влияет на Map2 как на свой upstream
        .collect {
            println("Collect $it на: ${Thread.currentThread().name}")
        }
}

// Возможный вывод:
// Emit на: DefaultDispatcher-worker-1 (IO)
// Map1 на: DefaultDispatcher-worker-1 (IO)
// Map2 на: DefaultDispatcher-worker-2 (Default)
// Collect 12 на: main
```

Визуализация:

```
[emit] -> [map1] -> flowOn(IO) -> [map2] -> flowOn(Default) -> [collect]
   ↑        ↑                        ↑                            ↑
   IO       IO                     Default                      Main
```

Каждый `flowOn`:
- влияет на все операторы выше него,
- создаёт собственную границу/буфер,
- позволяет различным частям конвейера выполняться на разных диспетчерах.

### Влияние На Производительность

`flowOn` в первую очередь переносит тяжёлую работу с контекста коллектора и создаёт асинхронные границы; ускорение не гарантируется само по себе.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlin.system.measureTimeMillis

suspend fun cpuIntensiveOperation(value: Int): Int {
    var result = value
    repeat(1_000_000) {
        result = (result * 31 + it) % 1000
    }
    return result
}

fun benchmarkFlowOn() = runBlocking {
    val withoutFlowOn = measureTimeMillis {
        flow {
            repeat(10) { emit(it) }
        }
            .map { cpuIntensiveOperation(it) }
            .collect { }
    }

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
}
```

Замечания:
- Для одного коллектора суммарное время часто будет схожим.
- Польза в том, что тяжёлая работа выполняется не в UI-контексте, а в фоне, улучшая отзывчивость.
- Каждый `flowOn` добавляет буфер и переключения контекста; используйте только там, где это отражает реальные границы конвейера.

Накладные расходы памяти:

```kotlin
val flow = flow { emit(1) }
    .flowOn(Dispatchers.IO)      // Буфер 1
    .flowOn(Dispatchers.Default) // Буфер 2
    .flowOn(Dispatchers.Main)    // Буфер 3
```

Каждая граница добавляет состояние буфера; это обмен памяти и планирования на развязку этапов.

### Размещение `flowOn` В Цепочке Операторов

Место размещения `flowOn` принципиально важно.

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
    .flowOn(Dispatchers.IO) // Всё выше выполняется на IO

// Пример 2: flowOn в середине
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

Лучшие практики:

1. Размещайте `flowOn` так, чтобы тяжёлая upstream-работа шла на подходящем диспетчере:

```kotlin
flow { /* сетевой или дисковый I/O */ }
    .flowOn(Dispatchers.IO)
    .map { /* тяжёлый парсинг */ }
    .flowOn(Dispatchers.Default)
    .collect { /* обновление UI */ }
```

1. Избегайте лишних `flowOn`:

```kotlin
// Слишком много переключений
flow { emit(1) }
    .flowOn(Dispatchers.IO)
    .map { it * 2 }
    .flowOn(Dispatchers.IO) // лишний
    .collect { }

// Лучше
flow { emit(1) }
    .map { it * 2 }
    .flowOn(Dispatchers.IO)
    .collect { }
```

### Upstream Против Downstream Контекста

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
        .flowOn(Dispatchers.IO) // граница
        .onEach {
            println("DOWNSTREAM: onEach на ${Thread.currentThread().name}")
        }
        .collect {
            println("DOWNSTREAM: Collect на ${Thread.currentThread().name}")
        }
}

// Возможный вывод:
// Начинаем на: main
// UPSTREAM: Emit на DefaultDispatcher-worker-1 (IO)
// UPSTREAM: onEach на DefaultDispatcher-worker-1 (IO)
// DOWNSTREAM: onEach на main
// DOWNSTREAM: Collect на main
```

Правило: всё выше `flowOn` — upstream (меняется), всё ниже — downstream (не меняется).

### Реальный Пример: Сеть И База Данных (скорректированный)

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

data class User(val id: Int, val name: String)

class UserRepository {
    private suspend fun fetchUsersFromNetwork(): List<User> {
        delay(1000)
        return listOf(User(1, "Алиса"), User(2, "Боб"))
    }

    private suspend fun parseUser(user: User): User {
        delay(10) // условный CPU-bound парсинг
        return user
    }

    private suspend fun saveToDatabase(user: User) {
        delay(100)
        println("Сохранён ${user.name} в БД")
    }

    fun syncUsers(): Flow<User> = flow {
        val users = fetchUsersFromNetwork()
        users.forEach { emit(it) }
    }
        .flowOn(Dispatchers.IO) // сеть на IO
        .map { user ->
            parseUser(user)
        }
        .flowOn(Dispatchers.Default) // парсинг на Default
        .onEach { user ->
            saveToDatabase(user)
        }
        .flowOn(Dispatchers.IO) // сохранение в БД на IO
}

suspend fun demonstrateRealWorldRu() {
    val repo = UserRepository()
    repo.syncUsers().collect { user ->
        println("Обновление UI для ${user.name} на: ${Thread.currentThread().name}")
    }
}
```

Контекстный поток (концептуально):

```
[Сеть] --IO--> [Парсинг] --Default--> [БД] --IO--> [UI]
```

Каждый `flowOn` сдвигает соответствующий upstream-фрагмент на указанный диспетчер.

### `flowOn` С Пользовательской Ёмкостью Буфера

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun customBufferWithFlowOn() = flow {
    repeat(100) { emit(it) }
}
    .buffer(10) // маленький буфер
    .flowOn(Dispatchers.IO)

fun defaultBufferWithFlowOn() = flow {
    repeat(100) { emit(it) }
}
    .flowOn(Dispatchers.IO) // буфер ~64 по умолчанию
```

Когда настраивать буфер:
- меньший: экономия памяти, более раннее противодавление;
- больший: producer сильно быстрее consumer;
- `UNLIMITED`: редкие случаи; возможен рост памяти до OOM.

```kotlin
fun unboundedBuffer() = flow {
    repeat(1000) { emit(it) }
}
    .buffer(Channel.UNLIMITED)
    .flowOn(Dispatchers.IO)
// Предупреждение: риск неограниченного роста памяти
```

### Типичные Ошибки

1. `flowOn` после терминального оператора:

```kotlin
flow { emit(1) }
    .collect { }
    .flowOn(Dispatchers.IO) // без эффекта

flow { emit(1) }
    .flowOn(Dispatchers.IO)
    .collect { }
```

1. Лишние переключения контекста:

```kotlin
flow { emit(1) }
    .map { it + 1 }
    .flowOn(Dispatchers.Default) // накладные расходы ради мелочи

flow {
    readFromDatabase()
}
    .flowOn(Dispatchers.IO)
    .map { it + 1 }
```

1. `withContext` вокруг `emit` в `flow {}`:

```kotlin
flow {
    withContext(Dispatchers.IO) {
        emit(1) // IllegalStateException
    }
}

flow {
    emit(1)
}.flowOn(Dispatchers.IO)
```

### Отладка Переключений Контекста

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun debuggableFlow() = flow {
    println("[${Thread.currentThread().name}] Эмиссия")
    emit(1)
}
    .onEach { println("[${Thread.currentThread().name}] После emit") }
    .flowOn(Dispatchers.IO)
    .onEach { println("[${Thread.currentThread().name}] После первого flowOn") }
    .map {
        println("[${Thread.currentThread().name}] Mapping")
        it * 2
    }
    .flowOn(Dispatchers.Default)
    .onEach { println("[${Thread.currentThread().name}] После второго flowOn") }

suspend fun debugFlowRu() {
    withContext(Dispatchers.Main) {
        debuggableFlow().collect { value ->
            println("[${Thread.currentThread().name}] Собрано: $value")
        }
    }
}
```

По именам потоков видно, какие стадии выполняются на каких диспетчерах и как влияют `flowOn`-границы.

### Тестирование Потоков С `flowOn`

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

        // Демонстрационная проверка: реализация должна использовать тестовый диспетчер.
        // В реальных тестах не полагайтесь жёстко на имя потока.
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

`flowOn` управляет upstream-контекстом выполнения в потоках:

- влияет на всё выше себя в цепочке,
- вводит буферизированную границу (по умолчанию 64), обеспечивая асинхронное взаимодействие upstream/downstream,
- используйте для переноса I/O и CPU-интенсивной upstream-работы на подходящие диспетчеры,
- не используйте `withContext` вокруг `emit` внутри `flow {}`; вместо этого применяйте `flowOn`,
- несколько `flowOn`: каждый влияет на свой upstream и добавляет границу,
- размещайте `flowOn` осознанно; избегайте после терминальных операторов и для тривиальных операций.

Ключевая идея: `flowOn` даёт управляемые границы асинхронности и переключения диспетчеров между этапами холодного потока.

## Answer (EN)

### What `flowOn` Does

`flowOn` runs the upstream operators of the `Flow` on the specified context and introduces an asynchronous boundary. It controls where emissions and upstream processing are executed above it in the chain, not the collector's context below it.

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
        .flowOn(Dispatchers.IO) // Move upstream to IO context
        .collect { value ->
            println("Collecting $value on: ${Thread.currentThread().name}")
        }
}

// Possible output:
// Emitting on: DefaultDispatcher-worker-1 (IO pool)
// Collecting 1 on: main
// Collecting 2 on: main
// Collecting 3 on: main
```

Key principle: `flowOn` affects everything above it in the chain (upstream), not below (downstream).

### Why `withContext` Is Restricted in `Flow`

You cannot arbitrarily change context around `emit` inside a cold flow builder. The following is invalid:

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

Why: cold flows are context-preserving by default. Code inside `flow {}` is expected to run in the collector's context (unless changed by `flowOn`). Calling `emit` from a different context violates the context-preservation invariant.

Correct way:

```kotlin
fun correctFlow() = flow {
    emit(1)
    emit(2)
}.flowOn(Dispatchers.IO) // Run upstream in IO context
```

### Context Preservation in `Flow`

By default, flows are context-preserving:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

suspend fun demonstrateContextPreservation() {
    val f = flow {
        println("Flow builder on: ${Thread.currentThread().name}")
        emit(1)
    }

    // Collect on Main
    withContext(Dispatchers.Main) {
        f.collect {
            println("Collected on: ${Thread.currentThread().name}")
        }
    }
    // Both logs on Main

    // Collect on IO
    withContext(Dispatchers.IO) {
        f.collect {
            println("Collected on: ${Thread.currentThread().name}")
        }
    }
    // Both logs on IO
}
```

Without `flowOn`, the flow executes entirely in the collector's context.

### `flowOn` Changes Upstream Context

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
        .flowOn(Dispatchers.IO) // Affects 1 and 2
        .map { value ->
            println("3. Map in: ${Thread.currentThread().name}")
            value.uppercase()
        }
        .collect { value ->
            println("4. Collect '$value' in: ${Thread.currentThread().name}")
        }
}

// Possible output:
// 1. Emit in: DefaultDispatcher-worker-1 (IO)
// 2. Map in: DefaultDispatcher-worker-1 (IO)
// 3. Map in: main
// 4. Collect 'A' in: main
```

Visualization:

```
[emit] -> [map lowercase] -> flowOn(IO) -> [map uppercase] -> [collect]
   ↑           ↑                               ↑                 ↑
   IO          IO                            Main              Main
```

### How `flowOn` Introduces Buffering

`flowOn` creates a channel-based boundary between contexts (this is part of its documented behavior: it uses buffered communication between upstream and downstream):

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
        .flowOn(Dispatchers.IO) // Boundary and buffer here
        .collect { value ->
            println("[${System.currentTimeMillis()}] Collecting $value")
            delay(500) // Slow consumer
        }
}

// Output shows producer can run ahead up to buffer capacity
```

Default buffer size: 64 (`Channel.BUFFERED`).

Custom buffer:

```kotlin
fun customBufferFlow() = flow {
    emit(1)
}
    .buffer(10) // Explicit buffer before context switch
    .flowOn(Dispatchers.IO)
```

### Channel Buffer Created by `flowOn` (Conceptual)

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

// Conceptual approximation of what flowOn does internally.
// Not an exact implementation and not recommended as a real pattern.
fun manualFlowOnEquivalent() = flow {
    emit(1)
    emit(2)
}
    .buffer(Channel.BUFFERED)
    .let { bufferedFlow ->
        flow {
            withContext(Dispatchers.IO) {
                bufferedFlow.collect { emit(it) }
            }
        }
    }
```

Notes:
- This is not the actual implementation of `flowOn`; it only illustrates that:
  - there is a buffer between contexts,
  - upstream can run on one dispatcher,
  - downstream consumes from that buffer.
- Default behavior:
  - Capacity: 64 (`Channel.BUFFERED`)
  - Overflow: `SUSPEND` (backpressure)

### Multiple `flowOn` Operators in a Chain

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
        .flowOn(Dispatchers.IO) // Affects emit + Map1
        .map {
            println("Map2 on: ${Thread.currentThread().name}")
            it + 10
        }
        .flowOn(Dispatchers.Default) // Affects Map2 as its upstream
        .collect {
            println("Collect $it on: ${Thread.currentThread().name}")
        }
}

// Possible output:
// Emit on: DefaultDispatcher-worker-1 (IO)
// Map1 on: DefaultDispatcher-worker-1 (IO)
// Map2 on: DefaultDispatcher-worker-2 (Default)
// Collect 12 on: main
```

Visualization:

```
[emit] -> [map1] -> flowOn(IO) -> [map2] -> flowOn(Default) -> [collect]
   ↑        ↑                        ↑                            ↑
   IO       IO                     Default                      Main
```

Each `flowOn`:
- affects all operators above it,
- introduces its own buffer/boundary,
- lets different pipeline segments run on different dispatchers.

### Performance Implications

`flowOn` is mainly about moving work off the collector's context and establishing asynchronous boundaries; it does not guarantee speedups by itself.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlin.system.measureTimeMillis

suspend fun cpuIntensiveOperation(value: Int): Int {
    var result = value
    repeat(1_000_000) {
        result = (result * 31 + it) % 1000
    }
    return result
}

fun benchmarkFlowOn() = runBlocking {
    val withoutFlowOn = measureTimeMillis {
        flow {
            repeat(10) { emit(it) }
        }
            .map { cpuIntensiveOperation(it) }
            .collect { }
    }

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
}
```

Notes:
- For a single collector, total wall-clock time is often similar.
- Benefit: heavy upstream work is done on a background dispatcher instead of blocking e.g. Main, improving responsiveness.
- Each `flowOn` adds buffering and context-switch overhead; use only where it models real concurrency boundaries.

Memory overhead:

```kotlin
val flow = flow { emit(1) }
    .flowOn(Dispatchers.IO)      // Buffer 1
    .flowOn(Dispatchers.Default) // Buffer 2
    .flowOn(Dispatchers.Main)    // Buffer 3
```

Each boundary adds buffer state; this trades memory and scheduling overhead for decoupling.

### `flowOn` Placement in Operator Chain

Placement of `flowOn` is critical.

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
    .flowOn(Dispatchers.IO) // All upstream on IO

// Example 2: flowOn in middle
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

Best practices:

1. Place `flowOn` so heavy upstream work runs on appropriate dispatchers:

```kotlin
flow { /* network or disk I/O */ }
    .flowOn(Dispatchers.IO)
    .map { /* CPU-heavy parsing */ }
    .flowOn(Dispatchers.Default)
    .collect { /* UI update */ }
```

1. Avoid redundant `flowOn`:

```kotlin
// Too many switches
flow { emit(1) }
    .flowOn(Dispatchers.IO)
    .map { it * 2 }
    .flowOn(Dispatchers.IO) // redundant
    .collect { }

// Better
flow { emit(1) }
    .map { it * 2 }
    .flowOn(Dispatchers.IO)
    .collect { }
```

### Upstream Vs Downstream Context

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
        .flowOn(Dispatchers.IO) // boundary
        .onEach {
            println("DOWNSTREAM: onEach on ${Thread.currentThread().name}")
        }
        .collect {
            println("DOWNSTREAM: Collect on ${Thread.currentThread().name}")
        }
}

// Possible output:
// Starting on: main
// UPSTREAM: Emit on DefaultDispatcher-worker-1 (IO)
// UPSTREAM: onEach on DefaultDispatcher-worker-1 (IO)
// DOWNSTREAM: onEach on main
// DOWNSTREAM: Collect on main
```

Rule: everything above `flowOn` = upstream (affected), below = downstream (unchanged).

### Real Example: Network and Database (Corrected)

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

data class User(val id: Int, val name: String)

class UserRepository {
    private suspend fun fetchUsersFromNetwork(): List<User> {
        delay(1000)
        return listOf(User(1, "Alice"), User(2, "Bob"))
    }

    private suspend fun parseUser(user: User): User {
        // simulate CPU-bound parsing
        delay(10)
        return user
    }

    private suspend fun saveToDatabase(user: User) {
        delay(100)
        println("Saved ${user.name} to DB")
    }

    fun syncUsers(): Flow<User> = flow {
        val users = fetchUsersFromNetwork()
        users.forEach { emit(it) }
    }
        .flowOn(Dispatchers.IO) // network on IO
        .map { user ->
            parseUser(user)
        }
        .flowOn(Dispatchers.Default) // parsing on Default
        .onEach { user ->
            saveToDatabase(user)
        }
        .flowOn(Dispatchers.IO) // DB I/O on IO
}

suspend fun demonstrateRealWorld() {
    val repo = UserRepository()
    repo.syncUsers().collect { user ->
        println("UI update for ${user.name} on: ${Thread.currentThread().name}")
    }
}
```

`Context` flow (conceptual):

```
[Network fetch] --IO--> [Parsing] --Default--> [DB save] --IO--> [UI update]
```

Each `flowOn` shifts its upstream segment to the specified dispatcher.

### `flowOn` With Custom Buffer Capacity

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun customBufferWithFlowOn() = flow {
    repeat(100) { emit(it) }
}
    .buffer(10) // Small buffer
    .flowOn(Dispatchers.IO)

fun defaultBufferWithFlowOn() = flow {
    repeat(100) { emit(it) }
}
    .flowOn(Dispatchers.IO) // Default buffer size (~64)
```

When to customize buffer:
- Smaller: conserve memory, stronger backpressure.
- Larger: producer much faster than consumer.
- `UNLIMITED`: rare; may cause OOM.

```kotlin
fun unboundedBuffer() = flow {
    repeat(1000) { emit(it) }
}
    .buffer(Channel.UNLIMITED)
    .flowOn(Dispatchers.IO)
// Warning: risk of unbounded memory growth
```

### Common Mistakes

1. `flowOn` after terminal operator:

```kotlin
flow { emit(1) }
    .collect { }
    .flowOn(Dispatchers.IO) // no effect

flow { emit(1) }
    .flowOn(Dispatchers.IO)
    .collect { }
```

1. Excessive context switching:

```kotlin
flow { emit(1) }
    .map { it + 1 }
    .flowOn(Dispatchers.Default) // overhead for trivial work

flow {
    readFromDatabase()
}
    .flowOn(Dispatchers.IO)
    .map { it + 1 }
```

1. `withContext` around `emit` inside `flow {}`:

```kotlin
flow {
    withContext(Dispatchers.IO) {
        emit(1) // IllegalStateException
    }
}

flow {
    emit(1)
}.flowOn(Dispatchers.IO)
```

### Debugging Context Switches

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun debuggableFlow() = flow {
    println("[${Thread.currentThread().name}] Emitting")
    emit(1)
}
    .onEach { println("[${Thread.currentThread().name}] After emit") }
    .flowOn(Dispatchers.IO)
    .onEach { println("[${Thread.currentThread().name}] After first flowOn") }
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

By checking thread names, you can see which stages run on which dispatcher and how `flowOn` boundaries affect them.

### Testing Flows with `flowOn`

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

        // Demonstrative assertion: implementation should use the test dispatcher.
        // In real tests, avoid hard depending on thread name.
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

`flowOn` controls the upstream execution context in flows:

- affects everything above it in the chain,
- introduces a buffered boundary (default 64) enabling asynchronous interaction between upstream and downstream,
- use it to move I/O and CPU-heavy upstream work to appropriate dispatchers,
- do not use `withContext` around `emit` inside `flow {}`; prefer `flowOn`,
- multiple `flowOn` calls: each affects its upstream segment and adds a boundary,
- place `flowOn` thoughtfully; avoid using it after terminal operators or for trivial work.

Key idea: `flowOn` provides controlled async boundaries and dispatcher shifts between stages of a cold flow pipeline.

---

## Дополнительные Вопросы

1. Как внутренний буфер `flowOn` обрабатывает backpressure, когда downstream-коллектор медленнее upstream-эмиссий?
2. Как `flowOn` влияет на распространение исключений? Меняется ли путь, по которому исключения идут вверх по цепочке?
3. Как бы вы реализовали пользовательский оператор, похожий на `flowOn`, но с иными стратегиями буферизации?
4. Объясните компромиссы производительности между использованием нескольких `flowOn` и одного `flowOn` в конце цепочки.
5. Как `flowOn` взаимодействует с `StateFlow` и `SharedFlow`? Можно ли применять `flowOn` к горячим потокам?
6. Каковы последствия использования `flowOn` совместно с операторами `retry()` или `catch()`?
7. Как бы вы спроектировали систему мониторинга для отслеживания переключений контекста в сложном конвейере `Flow`?

## Follow-ups

1. How does `flowOn`'s internal buffer handle backpressure when the downstream collector is slower than upstream emissions?
2. What happens to exception propagation when `flowOn` is used? Does it affect how exceptions travel up the flow chain?
3. How would you implement a custom operator similar to `flowOn` but with different buffering strategies?
4. Explain the performance trade-offs between using multiple `flowOn` operators vs a single `flowOn` at the end of the chain.
5. How does `flowOn` interact with `StateFlow` and `SharedFlow`? Can you use `flowOn` with hot flows?
6. What are the implications of using `flowOn` with operators like `retry()` or `catch()`?
7. How would you design a monitoring system to track context switches in a complex flow pipeline?

## References

- [Kotlin `Flow` Documentation](https://kotlinlang.org/docs/flow.html)
- [flowOn API Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/flow-on.html)
- [`Flow` `Context` Preservation](https://kotlinlang.org/docs/flow.html#flow-context)
- [Roman Elizarov - Reactive Streams and Kotlin `Flows`](https://medium.com/@elizarov/reactive-streams-and-kotlin-flows-bfd12772cda4)
- [Coroutines Guide - `Flow`](https://kotlinlang.org/docs/flow.html)
- [[c-flow]]

## Related Questions

### Related ("hard")
- [[q-catch-operator-flow--kotlin--medium]] - `Flow`
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
- [[q-flow-testing-advanced--kotlin--hard]] - Advanced `Flow` testing

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive `Flow` introduction

## Tags

#kotlin #coroutines #flowon #context-switching #dispatchers #flow #performance #buffer