---
---
---\
id: kotlin-240
anki_cards:
- slug: q-coroutine-delay-vs-thread-sleep-0-en
  language: en
- slug: q-coroutine-delay-vs-thread-sleep-0-ru
  language: ru
title: "delay() vs Thread.sleep(): what's the difference? / delay() против Thread.sleep()"
aliases: [delay vs Thread.sleep, delay против Thread.sleep]
topic: kotlin
difficulty: easy
original_language: en
language_tags: [en, ru]
question_kind: theory
status: draft
created: "2025-10-12"
updated: "2025-11-09"
tags: ["coroutines", "delay", "difficulty/easy", "kotlin", "suspending", "threads"]
description: "Understanding the fundamental differences between suspending delay() and blocking Thread.sleep() in Kotlin coroutines, including thread usage and performance implications"
moc: moc-kotlin
related: [c-coroutines, c-kotlin, q-coroutines-threads-android-differences--kotlin--easy]
subtopics: [coroutines, threading]
---\
# Вопрос (RU)

> В чём разница между `delay()` и `Thread.sleep()` в Kotlin-корутинах, как это влияет на блокировку потоков, производительность и когда что использовать?

# Question (EN)

> What is the difference between `delay()` and `Thread.sleep()` in Kotlin coroutines, how does it affect thread blocking, performance, and when should each be used?

## Ответ (RU)

И `delay()` , и `Thread.sleep()` приостанавливают выполнение на указанное время, но работают принципиально по-разному.

Кратко:

- `delay()` — приостанавливающая функция для корутин: не блокирует поток, поддерживает отмену, масштабируется и дружелюбна к корутинам.
- `Thread.sleep()` — блокирующий вызов: останавливает поток целиком, не кооперативен с отменой корутин, плохо масштабируется внутри корутинного кода.

Ниже приведены подробные примеры и пояснения (структура и код совпадают с английским разделом).

Также смотри [[c-kotlin]] и [[c-coroutines]] для базовых понятий.

### Описание Проблемы

И `delay()` , и `Thread.sleep()` приостанавливают выполнение на указанное время, но работают они принципиально по-разному. Одна приостанавливает корутину без блокировки потока, в то время как другая блокирует текущий поток. Каковы последствия для производительности, использования ресурсов и когда следует использовать каждую из них?

### Решение

**`delay()`** — это **приостанавливающая функция (suspending function)**, которая останавливает корутину без блокировки базового потока, позволяя работать другим корутинам. **`Thread.sleep()`** — это **блокирующая функция**, которая блокирует текущий поток, предотвращая любую другую работу на этом потоке.

#### Базовое Различие

```kotlin
import kotlinx.coroutines.*

fun basicDifference() = runBlocking {
    println("=== Thread.sleep() ===")
    println("Thread: ${Thread.currentThread().name}")

    // Thread.sleep блокирует поток
    Thread.sleep(1000)
    println("После Thread.sleep (поток был заблокирован)")

    println("\n=== delay() ===")
    println("Thread: ${Thread.currentThread().name}")

    // delay приостанавливает корутину (не блокирует поток во время ожидания)
    delay(1000)
    println("После delay (корутина была приостановлена, поток был свободен во время ожидания)")
}
```

#### Блокировка Потока Vs Приостановка

```kotlin
import kotlinx.coroutines.*
import kotlin.system.measureTimeMillis

fun demonstrateThreadBlocking() = runBlocking {
    println("=== Thread.sleep блокирует поток ===")

    val time1 = measureTimeMillis {
        // На ограниченном пуле потоков Thread.sleep уменьшает параллелизм
        val jobs = List(2) {
            launch(Dispatchers.Default) {
                println("Корутина с sleep запущена на ${Thread.currentThread().name}")
                Thread.sleep(1000) // Блокирует поток на 1 секунду
                println("Корутина с sleep завершена")
            }
        }
        jobs.forEach { it.join() }
    }
    println("Время с Thread.sleep: $time1 ms")
    // В зависимости от числа потоков они могут выполняться параллельно или конкурировать за потоки,
    // но в любом случае каждая ожидающая корутина удерживает поток всё время сна.

    println("\n=== delay приостанавливает корутину ===")

    val time2 = measureTimeMillis {
        val jobs = List(2) {
            launch(Dispatchers.Default) {
                println("Корутина с delay запущена на ${Thread.currentThread().name}")
                delay(1000) // Приостанавливает, освобождая поток
                println("Корутина с delay завершена")
            }
        }
        jobs.forEach { it.join() }
    }
    println("Время с delay: $time2 ms")
    // С delay множество корутин может ждать одновременно, не блокируя потоки.
}
```

#### Визуализация Различий

```kotlin
import kotlinx.coroutines.*

fun visualizeTheorem() = runBlocking {
    println("=== Визуальная демонстрация ===")

    // С Thread.sleep: каждая корутина блокирует свой поток во время сна
    println("\nС Thread.sleep:")
    launch(Dispatchers.Default) {
        repeat(5) { i ->
            println("[$i] До sleep на ${Thread.currentThread().name}")
            Thread.sleep(500)
            println("[$i] После sleep")
        }
    }

    delay(3000) // Ждём достаточно для завершения (демонстрационный код)

    // С delay: поток свободен для другой работы, пока корутина приостановлена
    println("\n\nС delay:")
    repeat(5) {
        launch(Dispatchers.Default) {
            println("[$it] До delay на ${Thread.currentThread().name}")
            delay(500)
            println("[$it] После delay на ${Thread.currentThread().name}")
        }
    }

    // Каждая корутина всё так же ждёт ~500 мс, но не блокирует поток во время ожидания,
    // что позволяет эффективно планировать большое количество задач.
    delay(1500)
}
```

#### Влияние На Производительность

```kotlin
import kotlinx.coroutines.*
import kotlin.system.measureTimeMillis

fun performanceComparison() = runBlocking {
    println("=== Сравнение производительности ===")

    val coroutineCount = 100

    // Используя Thread.sleep: каждая ожидающая корутина удерживает поток
    val time1 = measureTimeMillis {
        val jobs = List(coroutineCount) {
            launch(Dispatchers.Default) {
                Thread.sleep(1000)
            }
        }
        jobs.forEach { it.join() }
    }
    println("$coroutineCount корутин с Thread.sleep: $time1 ms")

    // Используя delay: ожидающие корутины не блокируют потоки
    val time2 = measureTimeMillis {
        val jobs = List(coroutineCount) {
            launch(Dispatchers.Default) {
                delay(1000)
            }
        }
        jobs.forEach { it.join() }
    }
    println("$coroutineCount корутин с delay: $time2 ms")

    // При Thread.sleep масштабирование по числу корутин быстро приводит к исчерпанию или простоям пула потоков,
    // тогда как delay() масштабируется значительно лучше.
}
```

#### Истощение Пула Потоков

```kotlin
import kotlinx.coroutines.*

fun threadPoolExhaustion() {
    println("=== Истощение пула потоков ===")

    // Плохо: Использование Thread.sleep блокирует потоки и может исчерпать общий пул Dispatchers.Default
    runBlocking(Dispatchers.Default) {
        println("Доступно процессоров: ${Runtime.getRuntime().availableProcessors()}")

        val jobs = List(1000) { index ->
            launch {
                println("[$index] Запущена на ${Thread.currentThread().name}")
                Thread.sleep(5000) // Блокирует поток на 5 секунд
                println("[$index] Завершена")
            }
        }

        jobs.forEach { it.join() }
    }

    // Лучше: Использование delay не удерживает потоки во время ожидания
    runBlocking(Dispatchers.Default) {
        val jobs = List(1000) { index ->
            launch {
                println("[$index] Запущена на ${Thread.currentThread().name}")
                delay(5000) // Приостанавливает, поток может выполнять другую работу
                println("[$index] Завершена")
            }
        }

        jobs.forEach { it.join() }
    }
}
```

#### Поддержка Отмены

```kotlin
import kotlinx.coroutines.*

fun cancellationSupport() = runBlocking {
    println("=== Поддержка отмены ===")

    // Thread.sleep не кооперативен с отменой корутин:
    // он не проверяет состояние Job, а реагирует только на прерывание потока.
    val job1 = launch {
        try {
            println("Запуск Thread.sleep")
            Thread.sleep(10000)
            println("Thread.sleep завершён (это выполнится только если поток не был прерван)")
        } catch (e: InterruptedException) {
            println("Thread.sleep прерван через interruption (корутинная отмена здесь работает только потому, что прерывает поток)")
        }
    }

    delay(1000)
    job1.cancel() // Отмена пытается прервать поток, но Thread.sleep сам по себе не знает о Job
    println("Job1 отменён: ${job1.isCancelled}")
    job1.join()

    // delay кооперативен и поддерживает отмену
    val job2 = launch {
        try {
            println("Запуск delay")
            delay(10000)
            println("delay завершён (это не напечатается при отмене)")
        } catch (e: CancellationException) {
            println("delay был отменён корректно")
        }
    }

    delay(1000)
    job2.cancel()
    println("Job2 отменён: ${job2.isCancelled}")
    job2.join()
}
```

#### Примеры Использования

```kotlin
import kotlinx.coroutines.*

// Пример 1: Операции в корутинах — предпочтительнее delay
suspend fun periodicTask() {
    while (true) {
        performTask()
        delay(1000) // Приостанавливает, не блокирует
    }
}

// Пример 2: Тестирование с задержками (демонстрационный; в реальных тестах лучше избегать реального ожидания)
suspend fun testWithDelay() {
    val result = loadData()
    delay(100) // Даём время асинхронным операциям (или используем структурную конкуррентность)
    verify(result)
}

// Пример 3: Механизм повторных попыток
suspend fun retryWithDelay(times: Int, delayTime: Long, block: suspend () -> Unit) {
    repeat(times) { attempt ->
        try {
            block()
            return
        } catch (e: Exception) {
            if (attempt < times - 1) {
                delay(delayTime) // Ждём перед повторной попыткой
            }
        }
    }
}

// Пример 4: Throttling (ограничение частоты)
suspend fun throttledOperation(intervalMs: Long) {
    var lastExecutionTime = 0L

    fun canExecute(): Boolean {
        val currentTime = System.currentTimeMillis()
        return currentTime - lastExecutionTime >= intervalMs
    }

    if (!canExecute()) {
        val waitTime = intervalMs - (System.currentTimeMillis() - lastExecutionTime)
        delay(waitTime) // Используйте delay, не Thread.sleep
    }

    lastExecutionTime = System.currentTimeMillis()
    // Выполняем операцию
}

// ИЗБЕГАЙТЕ: Thread.sleep в корутинах, если ожидаете неблокирующее поведение
suspend fun badExample() {
    Thread.sleep(1000) // Как правило, лучше избегать этого в корутинах
}

// Хорошо: Используйте delay вместо этого
suspend fun goodExample() {
    delay(1000)
}

suspend fun performTask() {
    delay(100)
}

suspend fun loadData(): String {
    delay(100)
    return "data"
}

fun verify(result: String) {
    println("Проверено: $result")
}
```

#### Когда Thread.sleep Может Быть Допустим

```kotlin
import kotlinx.coroutines.*

fun whenThreadSleepIsOk() {
    // 1. Код вне корутин
    fun blockingFunction() {
        Thread.sleep(1000) // OK, если не в контексте корутины
    }

    // 2. Простые блокирующие утилиты для тестов (хотя есть лучшие альтернативы)
    fun simpleBlockingTest() {
        Thread.sleep(100)
        // Лучше использовать runBlocking + delay для корутинного кода
    }

    // 3. Главный поток в простых скриптах без корутин
    fun oldStyleMain() {
        println("Start")
        Thread.sleep(1000)
        println("End")
    }

    // Лучшая альтернатива для асинхронного/приостанавливающего кода
    suspend fun modernMain() {
        println("Start")
        delay(1000)
        println("End")
    }
}
```

#### Реальные Примеры

```kotlin
import kotlinx.coroutines.*

// Пример 1: Ограничение частоты API-запросов
class ApiClient {
    private var lastRequestTime = 0L
    private val minRequestInterval = 1000L // 1 секунда

    suspend fun makeRequest(url: String): String {
        val now = System.currentTimeMillis()
        val timeSinceLastRequest = now - lastRequestTime

        if (timeSinceLastRequest < minRequestInterval) {
            // Используйте delay, не Thread.sleep
            delay(minRequestInterval - timeSinceLastRequest)
        }

        lastRequestTime = System.currentTimeMillis()
        return performRequest(url)
    }

    private suspend fun performRequest(url: String): String {
        delay(500) // Имитация сетевого запроса
        return "Response from $url"
    }
}

// Пример 2: Механизм опроса (polling)
class DataPoller {
    suspend fun pollForData(intervalMs: Long = 5000) {
        while (true) {
            try {
                val data = fetchData()
                processData(data)
                delay(intervalMs) // Используйте delay для опроса
            } catch (e: CancellationException) {
                println("Опрос отменён")
                throw e
            } catch (e: Exception) {
                println("Ошибка: ${e.message}, повторная попытка...")
                delay(intervalMs)
            }
        }
    }

    private suspend fun fetchData(): String {
        delay(200)
        return "data"
    }

    private fun processData(data: String) {
        println("Обработано: $data")
    }
}

// Пример 3: Реализация timeout
suspend fun <T> withCustomTimeout(timeMs: Long, block: suspend () -> T): T {
    return withTimeout(timeMs) {
        block()
    }
}

// Пример 4: Отложенное выполнение
class TaskScheduler {
    private val scope = CoroutineScope(Dispatchers.Default)

    fun scheduleTask(delayMs: Long, task: suspend () -> Unit): Job {
        return scope.launch {
            delay(delayMs) // Используйте delay для планирования
            task()
        }
    }

    fun cancel() {
        scope.cancel()
    }
}

fun demonstrateRealWorld() = runBlocking {
    // Ограничение частоты API
    val client = ApiClient()
    repeat(5) { index ->
        launch {
            val response = client.makeRequest("https://api.example.com/$index")
            println(response)
        }
    }

    delay(6000)

    // Опрос
    val poller = DataPoller()
    val pollingJob = launch {
        poller.pollForData(1000)
    }

    delay(5000)
    pollingJob.cancel()

    // Запланированные задачи
    val scheduler = TaskScheduler()
    scheduler.scheduleTask(2000) {
        println("Запланированная задача выполнена")
    }

    delay(3000)
    scheduler.cancel()
}
```

#### Соображения По Тестированию

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.Test
import kotlin.test.assertEquals

class DelayVsSleepTest {
    // delay можно контролировать в тестах с помощью виртуального времени
    @Test
    fun testWithDelay() = runTest {
        var executed = false

        launch {
            delay(5000) // Виртуальное время
            executed = true
        }

        advanceTimeBy(5000) // Перемотка времени вперёд
        assertEquals(true, executed)
    }

    // Thread.sleep не управляется TestCoroutineScheduler и блокирует реальный поток;
    // такой код приведён как анти-пример и в реальных тестах использоваться не должен.
    @Test
    fun testWithSleep() = runTest {
        var executed = false

        launch {
            Thread.sleep(5000) // Реальное время! Блокирует поток и может "подвесить" тест
            executed = true
        }

        // Нельзя перемотать Thread.sleep виртуальным временем;
        // использование delay(5000) здесь лишь сдвигает виртуальное время и не завершит sleep быстрее.
        delay(5000)
        assertEquals(true, executed)
    }

    // delay намного лучше для тестирования
    @Test
    fun testDelayAdvantage() = runTest {
        val startTime = currentTime

        delay(10000) // 10 секунд в виртуальном времени
        advanceUntilIdle()

        val elapsedTime = currentTime - startTime
        // Тест выполняется мгновенно по реальному времени, моделируя длинные задержки
        println("Прошло виртуального времени: $elapsedTime ms")
    }
}
```

#### Распространённые Ошибки

```kotlin
import kotlinx.coroutines.*

fun commonMistakes() = runBlocking {
    // Ошибка 1: Использование Thread.sleep в корутине при ожидании неблокирующего поведения
    launch {
        // ПЛОХО: Блокирует поток
        Thread.sleep(1000)
    }

    // Правильно
    launch {
        // ХОРОШО: Приостанавливает корутину
        delay(1000)
    }

    // Ошибка 2: Использование Thread.sleep с withContext на диспетчере корутин
    withContext(Dispatchers.IO) {
        // ПЛОХО: Блокирует IO-поток
        Thread.sleep(1000)
    }

    // Правильно
    withContext(Dispatchers.IO) {
        // ХОРОШО: Приостанавливает, освобождая IO-поток для другой работы
        delay(1000)
    }

    // Ошибка 3: Смешивание блокирующего и приостанавливающего подходов без необходимости
    // (ниже функции показаны как иллюстрация; в реальном коде определяйте их на верхнем уровне и не используйте Thread.sleep без нужды)
    suspend fun mixedApproach() {
        delay(1000)
        Thread.sleep(1000) // ПЛОХО: Блокирует после приостановки без причины
        delay(1000)
    }

    // Правильно
    suspend fun consistentApproach() {
        delay(1000)
        delay(1000)
        delay(1000)
    }

    // Ошибка 4: Использование Thread.sleep для timeout в корутинах
    launch {
        // ПЛОХО
        Thread.sleep(5000)
        cancel() // Ручной timeout
    }

    // ХОРОШО: Используйте withTimeout для корректного timeout в корутинах
    withTimeout(5000) {
        // Автоматическая отмена
    }
}
```

### Краткая Справка

```kotlin
//  Используйте delay() когда:
// - Внутри корутин
// - Нужна поддержка отмены
// - Хотите избежать блокировки потоков
// - Пишете тесты (можно использовать виртуальное время)
// - Нужно эффективное использование ресурсов

suspend fun goodExample1() {
    delay(1000)
}

//  Избегайте Thread.sleep когда:
// - Внутри корутин (если только намеренно не вызываете блокирующий код на отдельном пуле)
// - Нужна отмена
// - Важна производительность и масштабируемость
// - Пишете тестируемый асинхронный код
// - Ограниченный пул потоков

suspend fun badExample1() {
    Thread.sleep(1000) // Как правило, не делайте так
}

//  Thread.sleep может быть OK когда:
// - Не в контексте корутины
// - Простые блокирующие скрипты/утилиты
// - Легаси/блокирующий код (предпочтительно оборачивать в Dispatchers.IO или рефакторить)

fun legacyCode() {
    Thread.sleep(1000) // OK, если не в корутине
}
```

### Лучшие Практики

1. Предпочитайте `delay()` в корутинах для временного ожидания; избегайте `Thread.sleep()` на диспетчерах корутин.
2. Используйте `delay()` для любого временного ожидания в приостанавливающих функциях.
3. Применяйте `Thread.sleep()` только в блокирующем коде вне корутин или при осознанном использовании блокирующих API на подходящих потоках.
4. Тестируйте корутинный код с `delay()` и тестовыми утилитами (`runTest`, виртуальное время) для быстрых и детерминированных тестов.
5. В долгоработающих циклах с `delay()` проверяйте `isActive` (или обрабатывайте `CancellationException`), чтобы корректно реагировать на отмену.

### Сводка По Производительности

| Аспект | delay() | `Thread`.sleep() |
|--------|---------|----------------|
| Использование потока | Приостанавливает, освобождает поток | Блокирует поток |
| Возможность отмены | Да (кооперативно) | Нет (некооперативно, только через interrupt потока) |
| Поддержка тестирования | Возможна перемотка с виртуальным временем | Реальное ожидание, не зависит от виртуального времени |
| Эффективность ресурсов | Да | Нет (удерживает потоки во время сна) |
| Совместимость с корутинами | Да | Нет |
| Производительность | Высокая масштабируемость в корутинах | Плохая масштабируемость в корутинах |

---

## Answer (EN)

Both `delay()` and `Thread.sleep()` pause execution for a specified time, but they work fundamentally differently.

In short:

- `delay()` is a suspending function for coroutines: it does not block the thread, supports cancellation, scales well, and is coroutine-friendly.
- `Thread.sleep()` is a blocking call: it blocks the entire thread, is not cooperative with coroutine cancellation, and scales poorly when used inside coroutine-based code.

Below are detailed examples and explanations.

See also [[c-kotlin]] and [[c-coroutines]] for the core concepts.

### Problem Statement

Both `delay()` and `Thread.sleep()` pause execution for a specified time, but they work fundamentally differently. One suspends a coroutine without blocking the thread, while the other blocks the underlying thread. What are the implications for performance, resource usage, and when should each be used?

### Solution

**`delay()`** is a **suspending function** that pauses a coroutine without blocking the underlying thread, allowing other coroutines to run. **`Thread.sleep()`** is a **blocking function** that blocks the current thread, preventing any other work on that thread.

#### Basic Difference

```kotlin
import kotlinx.coroutines.*

fun basicDifference() = runBlocking {
    println("=== Thread.sleep() ===")
    println("Thread: ${Thread.currentThread().name}")

    // Thread.sleep blocks the thread
    Thread.sleep(1000)
    println("After Thread.sleep (thread was blocked)")

    println("\n=== delay() ===")
    println("Thread: ${Thread.currentThread().name}")

    // delay suspends the coroutine (does not block thread while waiting)
    delay(1000)
    println("After delay (coroutine was suspended, thread was free while waiting)")
}
```

#### Thread Blocking Vs Suspending

```kotlin
import kotlinx.coroutines.*
import kotlin.system.measureTimeMillis

fun demonstrateThreadBlocking() = runBlocking {
    println("=== Thread.sleep blocks thread ===")

    val time1 = measureTimeMillis {
        // On a limited thread pool, blocking with Thread.sleep() reduces parallelism
        val jobs = List(2) {
            launch(Dispatchers.Default) {
                println("Coroutine with sleep started on ${Thread.currentThread().name}")
                Thread.sleep(1000) // Blocks the thread for 1s
                println("Coroutine with sleep finished")
            }
        }
        jobs.forEach { it.join() }
    }
    println("Time with Thread.sleep: $time1 ms")
    // Depending on available threads, they may run in parallel or contend for threads,
    // but in all cases each blocked coroutine occupies a thread for the full duration.

    println("\n=== delay suspends coroutine ===")

    val time2 = measureTimeMillis {
        val jobs = List(2) {
            launch(Dispatchers.Default) {
                println("Coroutine with delay started on ${Thread.currentThread().name}")
                delay(1000) // Suspends, freeing the thread while waiting
                println("Coroutine with delay finished")
            }
        }
        jobs.forEach { it.join() }
    }
    println("Time with delay: $time2 ms")
    // With delay, many coroutines can wait concurrently without blocking threads.
}
```

#### Visualizing the Difference

```kotlin
import kotlinx.coroutines.*

fun visualizeTheorem() = runBlocking {
    println("=== Visual Demonstration ===")

    // With Thread.sleep: each coroutine blocks its thread while sleeping
    println("\nWith Thread.sleep:")
    launch(Dispatchers.Default) {
        repeat(5) { i ->
            println("[$i] Before sleep on ${Thread.currentThread().name}")
            Thread.sleep(500)
            println("[$i] After sleep")
        }
    }

    delay(3000) // Wait long enough for completion (demo code)

    // With delay: thread is free for other work while coroutine is suspended
    println("\n\nWith delay:")
    repeat(5) {
        launch(Dispatchers.Default) {
            println("[$it] Before delay on ${Thread.currentThread().name}")
            delay(500)
            println("[$it] After delay on ${Thread.currentThread().name}")
        }
    }

    // Each coroutine still waits ~500ms, but they don't block threads while waiting,
    // so many of them can be scheduled efficiently.
    delay(1500)
}
```

#### Performance Impact

```kotlin
import kotlinx.coroutines.*
import kotlin.system.measureTimeMillis

fun performanceComparison() = runBlocking {
    println("=== Performance Comparison ===")

    val coroutineCount = 100

    // Using Thread.sleep: Each waiting coroutine occupies a thread
    val time1 = measureTimeMillis {
        val jobs = List(coroutineCount) {
            launch(Dispatchers.Default) {
                Thread.sleep(1000)
            }
        }
        jobs.forEach { it.join() }
    }
    println("$coroutineCount coroutines with Thread.sleep: $time1 ms")

    // Using delay: Waiting coroutines do not block threads
    val time2 = measureTimeMillis {
        val jobs = List(coroutineCount) {
            launch(Dispatchers.Default) {
                delay(1000)
            }
        }
        jobs.forEach { it.join() }
    }
    println("$coroutineCount coroutines with delay: $time2 ms")

    // With Thread.sleep, scaling to many coroutines quickly exhausts or stalls the thread pool,
    // while delay() scales efficiently by suspending without blocking threads.
}
```

#### Thread Pool Exhaustion

```kotlin
import kotlinx.coroutines.*

fun threadPoolExhaustion() {
    println("=== Thread Pool Exhaustion ===")

    // Bad: Using Thread.sleep blocks threads and can exhaust shared Dispatchers.Default threads
    runBlocking(Dispatchers.Default) {
        println("Available processors: ${Runtime.getRuntime().availableProcessors()}")

        val jobs = List(1000) { index ->
            launch {
                println("[$index] Started on ${Thread.currentThread().name}")
                Thread.sleep(5000) // Blocks thread for 5 seconds
                println("[$index] Finished")
            }
        }

        jobs.forEach { it.join() }
    }

    // Better: Using delay doesn't hold threads while waiting
    runBlocking(Dispatchers.Default) {
        val jobs = List(1000) { index ->
            launch {
                println("[$index] Started on ${Thread.currentThread().name}")
                delay(5000) // Suspends; thread can do other work
                println("[$index] Finished")
            }
        }

        jobs.forEach { it.join() }
    }
}
```

#### Cancellation Support

```kotlin
import kotlinx.coroutines.*

fun cancellationSupport() = runBlocking {
    println("=== Cancellation Support ===")

    // Thread.sleep is non-cooperative with coroutine cancellation:
    // it does not observe Job state, only reacts to thread interruption.
    val job1 = launch {
        try {
            println("Starting Thread.sleep")
            Thread.sleep(10000)
            println("Thread.sleep completed (this prints only if the thread was not interrupted)")
        } catch (e: InterruptedException) {
            println("Thread.sleep interrupted via thread interruption (cancellation only works here because it interrupts the thread)")
        }
    }

    delay(1000)
    job1.cancel() // Cancellation attempts to interrupt the thread, but Thread.sleep itself is unaware of the Job
    println("Job1 cancelled: ${job1.isCancelled}")
    job1.join()

    // delay is cooperative and cancellable
    val job2 = launch {
        try {
            println("Starting delay")
            delay(10000)
            println("delay completed (this won't print if cancelled)")
        } catch (e: CancellationException) {
            println("delay was cancelled properly")
        }
    }

    delay(1000)
    job2.cancel()
    println("Job2 cancelled: ${job2.isCancelled}")
    job2.join()
}
```

#### Use Cases

```kotlin
import kotlinx.coroutines.*

// Use Case 1: Coroutine operations - prefer delay
suspend fun periodicTask() {
    while (true) {
        performTask()
        delay(1000) // Suspends, doesn't block
    }
}

// Use Case 2: Testing with delays (demo; avoid real-time sleeps in proper tests)
suspend fun testWithDelay() {
    val result = loadData()
    delay(100) // Give time for async operations (or use structured concurrency)
    verify(result)
}

// Use Case 3: Retry mechanism
suspend fun retryWithDelay(times: Int, delayTime: Long, block: suspend () -> Unit) {
    repeat(times) { attempt ->
        try {
            block()
            return
        } catch (e: Exception) {
            if (attempt < times - 1) {
                delay(delayTime) // Wait before retry
            }
        }
    }
}

// Use Case 4: Throttling
suspend fun throttledOperation(intervalMs: Long) {
    var lastExecutionTime = 0L

    fun canExecute(): Boolean {
        val currentTime = System.currentTimeMillis()
        return currentTime - lastExecutionTime >= intervalMs
    }

    if (!canExecute()) {
        val waitTime = intervalMs - (System.currentTimeMillis() - lastExecutionTime)
        delay(waitTime) // Use delay, not Thread.sleep
    }

    lastExecutionTime = System.currentTimeMillis()
    // Perform operation
}

// AVOID: Thread.sleep in coroutines when you expect non-blocking behavior
suspend fun badExample() {
    Thread.sleep(1000) // Generally avoid this in coroutines
}

// Good: Use delay instead
suspend fun goodExample() {
    delay(1000)
}

suspend fun performTask() {
    delay(100)
}

suspend fun loadData(): String {
    delay(100)
    return "data"
}

fun verify(result: String) {
    println("Verified: $result")
}
```

#### When Thread.sleep Might Be Acceptable

```kotlin
import kotlinx.coroutines.*

fun whenThreadSleepIsOk() {
    // 1. Non-coroutine blocking code
    fun blockingFunction() {
        Thread.sleep(1000) // OK if not in coroutine context
    }

    // 2. Simple blocking test utilities (though better async alternatives exist)
    fun simpleBlockingTest() {
        Thread.sleep(100)
        // Better to use runBlocking + delay for coroutine code
    }

    // 3. Main thread in simple scripts without coroutines
    fun oldStyleMain() {
        println("Start")
        Thread.sleep(1000)
        println("End")
    }

    // Better alternative for suspending/async code
    suspend fun modernMain() {
        println("Start")
        delay(1000)
        println("End")
    }
}
```

#### Real-World Examples

```kotlin
import kotlinx.coroutines.*

// Example 1: API rate limiting
class ApiClient {
    private var lastRequestTime = 0L
    private val minRequestInterval = 1000L // 1 second

    suspend fun makeRequest(url: String): String {
        val now = System.currentTimeMillis()
        val timeSinceLastRequest = now - lastRequestTime

        if (timeSinceLastRequest < minRequestInterval) {
            // Use delay, not Thread.sleep
            delay(minRequestInterval - timeSinceLastRequest)
        }

        lastRequestTime = System.currentTimeMillis()
        return performRequest(url)
    }

    private suspend fun performRequest(url: String): String {
        delay(500) // Simulate network request
        return "Response from $url"
    }
}

// Example 2: Polling mechanism
class DataPoller {
    suspend fun pollForData(intervalMs: Long = 5000) {
        while (true) {
            try {
                val data = fetchData()
                processData(data)
                delay(intervalMs) // Use delay for polling
            } catch (e: CancellationException) {
                println("Polling cancelled")
                throw e
            } catch (e: Exception) {
                println("Error: ${e.message}, retrying...")
                delay(intervalMs)
            }
        }
    }

    private suspend fun fetchData(): String {
        delay(200)
        return "data"
    }

    private fun processData(data: String) {
        println("Processed: $data")
    }
}

// Example 3: Timeout implementation
suspend fun <T> withCustomTimeout(timeMs: Long, block: suspend () -> T): T {
    return withTimeout(timeMs) {
        block()
    }
}

// Example 4: Delayed execution
class TaskScheduler {
    private val scope = CoroutineScope(Dispatchers.Default)

    fun scheduleTask(delayMs: Long, task: suspend () -> Unit): Job {
        return scope.launch {
            delay(delayMs) // Use delay for scheduling
            task()
        }
    }

    fun cancel() {
        scope.cancel()
    }
}

fun demonstrateRealWorld() = runBlocking {
    // API rate limiting
    val client = ApiClient()
    repeat(5) { index ->
        launch {
            val response = client.makeRequest("https://api.example.com/$index")
            println(response)
        }
    }

    delay(6000)

    // Polling
    val poller = DataPoller()
    val pollingJob = launch {
        poller.pollForData(1000)
    }

    delay(5000)
    pollingJob.cancel()

    // Scheduled tasks
    val scheduler = TaskScheduler()
    scheduler.scheduleTask(2000) {
        println("Scheduled task executed")
    }

    delay(3000)
    scheduler.cancel()
}
```

#### Testing Considerations

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.Test
import kotlin.test.assertEquals

class DelayVsSleepTest {
    // delay can be controlled in tests via virtual time
    @Test
    fun testWithDelay() = runTest {
        var executed = false

        launch {
            delay(5000) // Virtual time
            executed = true
        }

        advanceTimeBy(5000) // Fast-forward time
        assertEquals(true, executed)
    }

    // Thread.sleep is NOT controlled by TestCoroutineScheduler and blocks the real thread;
    // this example is an ANTI-PATTERN and should not be used in real tests.
    @Test
    fun testWithSleep() = runTest {
        var executed = false

        launch {
            Thread.sleep(5000) // Real time! Blocks thread and may hang the test
            executed = true
        }

        // Cannot fast-forward Thread.sleep with virtual time;
        // using delay(5000) here only advances virtual time and will not complete the sleep sooner.
        delay(5000)
        assertEquals(true, executed)
    }

    // delay is much better for testing
    @Test
    fun testDelayAdvantage() = runTest {
        val startTime = currentTime

        delay(10000) // 10 seconds in virtual time
        advanceUntilIdle()

        val elapsedTime = currentTime - startTime
        // Test runs instantly in real time, while simulating long delays
        println("Elapsed virtual time: $elapsedTime ms")
    }
}
```

#### Common Mistakes

```kotlin
import kotlinx.coroutines.*

fun commonMistakes() = runBlocking {
    // Mistake 1: Using Thread.sleep in coroutine expecting non-blocking behavior
    launch {
        // BAD: Blocks the thread
        Thread.sleep(1000)
    }

    // Correct
    launch {
        // GOOD: Suspends the coroutine
        delay(1000)
    }

    // Mistake 2: Using Thread.sleep with withContext on coroutine dispatcher
    withContext(Dispatchers.IO) {
        // BAD: Blocks IO thread
        Thread.sleep(1000)
    }

    // Correct
    withContext(Dispatchers.IO) {
        // GOOD: Suspends, frees IO thread for other work
        delay(1000)
    }

    // Mistake 3: Mixing blocking and suspending without intent
    // (functions below are illustrative; define them at top level in real code)
    suspend fun mixedApproach() {
        delay(1000)
        Thread.sleep(1000) // BAD: Blocks after suspending, unnecessary
        delay(1000)
    }

    // Correct
    suspend fun consistentApproach() {
        delay(1000)
        delay(1000)
        delay(1000)
    }

    // Mistake 4: Using Thread.sleep for timeout logic in coroutines
    launch {
        // BAD
        Thread.sleep(5000)
        cancel() // Manual timeout
    }

    // GOOD: Use withTimeout for coroutine-friendly timeout
    withTimeout(5000) {
        // Automatic cancellation
    }
}
```

### Quick Reference

```kotlin
//  Use delay() when:
// - Inside coroutines
// - Need cancellation support
// - Want to avoid blocking threads
// - Writing tests (can be fast-forwarded with virtual time)
// - Need efficient resource usage

suspend fun goodExample1() {
    delay(1000)
}

//  Avoid Thread.sleep when:
// - Inside coroutines (unless intentionally calling blocking code on a dedicated dispatcher)
// - Need cancellation
// - Care about performance and scalability
// - Writing testable async code
// - Running on a limited thread pool

suspend fun badExample1() {
    Thread.sleep(1000) // Generally avoid this in coroutines
}

//  Thread.sleep might be OK when:
// - Not in coroutine context
// - Simple blocking scripts/tools
// - Legacy/blocking code paths (prefer wrapping in Dispatchers.IO or refactoring)

fun legacyCode() {
    Thread.sleep(1000) // OK if not in coroutine
}
```

### Best Practices

1. Prefer `delay()` in coroutines for time-based waiting; avoid `Thread.sleep()` on coroutine dispatchers.
2. Use `delay()` for any time-based waiting in suspending functions.
3. Use `Thread.sleep()` only in non-coroutine blocking code or when deliberately working with blocking APIs on appropriate threads.
4. Test coroutine code with `delay()` and test utilities (`runTest`, virtual time) for fast, deterministic tests.
5. In long-running loops that use `delay()`, check `isActive` (or handle `CancellationException`) to remain responsive to cancellation.

### Performance Summary

| Aspect | delay() | `Thread`.sleep() |
|--------|---------|----------------|
| `Thread` Usage | Suspends, frees thread | Blocks thread |
| Cancellable | Yes (cooperative) | No (non-cooperative, only via thread interrupt) |
| Test Support | Fast-forward possible with virtual time | Real-time/blocking, not virtual-time aware |
| Resource Efficient | Yes | No (wastes threads while sleeping) |
| `Coroutine`-friendly | Yes | No |
| Performance | High scalability in coroutine code | Poor scalability in coroutine code |

---

## Follow-ups

1. Can you use `delay()` outside of a coroutine context, and what happens if you try?
2. What happens if you call `Thread.sleep()` on the Main dispatcher in Android?
3. How does `delay()` work internally (e.g., timers, event loop, scheduling)?
4. Can `delay(0)` be useful, and what does it effectively do?
5. What is the relationship between `delay()` and `yield()` in terms of scheduling and fairness?
6. How can you detect and refactor inappropriate uses of `Thread.sleep()` in coroutine-based code?
7. Is there any scenario where using `Thread.sleep()` within a `Dispatchers.IO`-backed coroutine is acceptable?
8. How does `delay()` behave for very long delays (hours or days), and what are the practical considerations?

## References

- [Kotlin Coroutines Guide - Cancellation and Timeouts](https://kotlinlang.org/docs/cancellation-and-timeouts.html)
- [delay - kotlinx.coroutines API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/delay.html)
- [Roman Elizarov - Blocking threads, suspending coroutines](https://medium.com/@elizarov/blocking-threads-suspending-coroutines-d33e11bf4761)
- [Android Developers - Coroutines Best Practices](https://developer.android.com/kotlin/coroutines/coroutines-best-practices)

## Related Questions

- [[q-what-is-coroutine--kotlin--easy]]
- [[q-coroutine-builders-basics--kotlin--easy]]
- [[q-coroutine-scope-basics--kotlin--easy]]
- [[q-coroutines-threads-android-differences--kotlin--easy]]
- [[q-suspend-functions-basics--kotlin--easy]]
- [[q-coroutine-dispatchers--kotlin--medium]]
- [[q-coroutinescope-vs-coroutinecontext--kotlin--medium]]
- [[q-coroutine-profiling--kotlin--hard]]
- [[q-coroutine-performance-optimization--kotlin--hard]]
- [[q-coroutine-memory-leaks--kotlin--hard]]
- [[q-suspending-vs-blocking--kotlin--medium]]
- [[q-coroutine-virtual-time--kotlin--medium]]
- [[q-coroutine-context-explained--kotlin--medium]]
- [[q-coroutine-cancellation-cooperation--kotlin--medium]]
- [[q-kotlin-coroutines-introduction--kotlin--medium]]
