---
id: kotlin-077
title: "Coroutine Profiling and Debugging / Профилирование и отладка корутин"
aliases: ["Coroutine Profiling and Debugging", "Профилирование и отладка корутин"]
topic: kotlin
subtopics: [coroutines]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Coroutines Guide - Question 140025
status: draft
moc: moc-kotlin
related: [c-coroutines, c-kotlin, q-advanced-coroutine-patterns--kotlin--hard]
created: 2025-10-12
updated: 2025-11-11
tags: [coroutines, difficulty/hard, kotlin]

date created: Saturday, October 18th 2025, 12:38:46 pm
date modified: Tuesday, November 25th 2025, 8:53:52 pm
---

# Вопрос (RU)
> Профилирование и отладка корутин в Kotlin: какие инструменты и подходы использовать для эффективной диагностики, поиска утечек и оптимизации производительности?

# Question (EN)
> `Coroutine` profiling and debugging in Kotlin: which tools and approaches should you use to effectively diagnose issues, detect leaks, and optimize performance?

## Ответ (RU)

Профилирование и отладка корутин требуют специализированных инструментов и техник, поскольку корутины могут переключаться между потоками и имеют сложные потоки выполнения. Понимание эффективного профилирования и отладки критически важно для продакшн-приложений. См. также [[c-kotlin]] и [[c-coroutines]].

### Инструменты Отладки

**1. Отладчик корутин IntelliJ IDEA**

IntelliJ предоставляет встроенную поддержку отладки корутин:
- **Вкладка `Coroutines`**: Показывает все активные корутины с их состояниями
- **`Stack` traces**: Просмотр объединённых стеков вызовов корутин, а не только потоков
- **Точки приостановки**: Видно, где корутины приостановлены

```kotlin
suspend fun debugExample() = coroutineScope {
    val data1 = async { fetchData1() }  // Breakpoint здесь
    val data2 = async { fetchData2() }  // И здесь
    println("${data1.await()} ${data2.await()}")
}
```

**2. Режим отладки kotlinx.coroutines**

Включите режим отладки, чтобы видеть идентификаторы корутин в именах потоков и расширенные трассировки:
```kotlin
// Добавьте VM опцию:
// -Dkotlinx.coroutines.debug

runBlocking {
    launch(Dispatchers.Default) {
        println(Thread.currentThread().name)
        // Например: "DefaultDispatcher-worker-1 @coroutine#1"
    }
}
```

### Инструменты Профилирования

**1. Android Studio Profiler**

Для Android-приложений используйте встроенный profiler:
- **CPU Profiler**: Отслеживание выполнения корутин через потоки (особенно полезно с включённым `kotlinx.coroutines.debug` для понимания связей)
- **Memory Profiler**: Обнаружение утечек, связанных с длительно живущими корутинами и ссылками
- **Energy Profiler**: Влияние корутин на батарею

**2. JVM Profiler'ы**

Популярные JVM-профайлеры, которые можно эффективно использовать с корутинами:
- **Async Profiler**: Низкие накладные расходы, хорошо работает с асинхронными сценариями
- **YourKit**: Коммерческий профайлер, улучшенные стек-трейсы и визуализация потоков
- **JProfiler**: Расширенные метрики потоков; в сочетании с debug-режимом корутин упрощает анализ

Важно: поддержка именно "корутин-специфичных" метрик может быть ограниченной; чаще используется комбинация обычных JVM-метрик и debug-режима корутин.

```kotlin
// Пример настройки пула планировщика корутин (не включает профилирование сам по себе)
System.setProperty("kotlinx.coroutines.scheduler.core.pool.size", "4")
System.setProperty("kotlinx.coroutines.scheduler.max.pool.size", "128")
```

### Распространенные Паттерны Отладки

**Паттерн 1: Добавление отладочных имен корутинам**
```kotlin
runBlocking {
    launch(CoroutineName("UserDataLoader")) {
        // Легче идентифицировать в отладчике
        val data = loadUserData()
    }
}
```

**Паттерн 2: Логирование жизненного цикла корутин**
```kotlin
fun CoroutineScope.launchWithLogging(
    name: String,
    block: suspend CoroutineScope.() -> Unit
): Job {
    return launch(CoroutineName(name)) {
        try {
            println("[$name] Started")
            block()
            println("[$name] Completed successfully")
        } catch (e: CancellationException) {
            println("[$name] Cancelled")
            throw e
        } catch (e: Exception) {
            println("[$name] Failed: ${e.message}")
            throw e
        }
    }
}
```

**Паттерн 3: Структурированная отладка с supervisorScope**
```kotlin
suspend fun debugMultipleOperations() = supervisorScope {
    val job1 = launch(CoroutineName("Operation1")) {
        operation1()
    }
    val job2 = launch(CoroutineName("Operation2")) {
        operation2()
    }
    // Если одна упадет, другая продолжит, что упрощает изолированную отладку
}
```

### Обнаружение Утечек Памяти

**Распространенные причины утечек**:
1. **Не отменяются корутины**:
```kotlin
// Упрощённый пример. В Android предпочтительно использовать viewModelScope.
class ViewModel {
    private val scope = CoroutineScope(Dispatchers.Main)

    fun loadData() {
        scope.launch {
            // Возможна утечка, если ViewModel уничтожена без вызова clear()
        }
    }

    // Исправление: Отменить scope (или использовать lifecycle-aware scope)
    fun clear() {
        scope.cancel()
    }
}
```

2. **Захват контекста в лямбдах**:
```kotlin
class Activity {
    fun startWork() {
        GlobalScope.launch {
            // Утечка: захвачена ссылка на Activity
            updateUI()
        }
    }

    // Исправление: использовать lifecycleScope (AndroidX lifecycle-runtime-ktx)
    fun startWorkCorrect() {
        lifecycleScope.launch {
            updateUI()
        }
    }
}
```

### Профилирование Производительности

**Измерение накладных расходов корутин**:
```kotlin
suspend fun profileCoroutines() {
    val startTime = System.currentTimeMillis()

    coroutineScope {
        repeat(10_000) {
            launch {
                // Минимальная работа
                delay(1)
            }
        }
    }

    val duration = System.currentTimeMillis() - startTime
    println("Created 10,000 coroutines in ${duration}ms")
}
```

**Поиск медленных точек приостановки**:
```kotlin
suspend fun profileSuspendPoints() {
    measureTimedValue {
        fetchData()
    }.let { (result, duration) ->
        println("fetchData took ${duration.inWholeMilliseconds}ms")
        // result можно использовать по назначению
    }
}
```

### Отладка В Продакшене

**1. Структурированное логирование**:
```kotlin
class CoroutineLogger(private val logger: Logger) : CoroutineContext.Element {
    companion object Key : CoroutineContext.Key<CoroutineLogger>

    override val key: CoroutineContext.Key<CoroutineLogger> = Key

    fun log(message: String) {
        logger.info(message)
    }
}

val coroutineLogger = CoroutineLogger(myLogger)

runBlocking {
    launch(coroutineLogger + CoroutineName("Operation")) {
        coroutineContext[CoroutineLogger]?.log("Operation started")
    }
}
```

**2. Отслеживание исключений**:
```kotlin
val handler = CoroutineExceptionHandler { context, exception ->
    // Отправить в сервис отчетов о сбоях
    Crashlytics.recordException(exception)
    println("Caught in ${context[CoroutineName]}: $exception")
}

runBlocking {
    launch(handler + CoroutineName("CriticalOperation")) {
        criticalWork()
    }
}
```

**3. Мониторинг пулов корутин**:
```kotlin
// Пример-заглушка: нет стандартного API, это иллюстрация того, что можно собирать свои метрики
fun getCoroutinePoolStats(): PoolStats {
    return PoolStats(
        activeCoroutines = /* custom metric */ 0,
        queuedTasks = /* custom metric */ 0,
        completedTasks = /* custom metric */ 0
    )
}
```

### Лучшие Практики

1. **Всегда именуйте важные корутины** для упрощения отладки
2. **Используйте структурированную конкурентность** чтобы избежать осиротевших корутин
3. **Профилируйте рано** чтобы поймать проблемы производительности
4. **Включайте режим отладки** в разработке: `-Dkotlinx.coroutines.debug`
5. **Мониторьте утечки** используя memory profiler
6. **Добавляйте логирование** в ключевых точках приостановки
7. **Используйте `supervisorScope`** при отладке и реализации независимых операций

---

## Answer (EN)

`Coroutine` profiling and debugging require specialized tools and techniques because coroutines can jump between threads and have complex execution flows. Understanding how to profile and debug them effectively is crucial for production applications. See also [[c-kotlin]] and [[c-coroutines]].

### Debugging Tools

**1. IntelliJ IDEA `Coroutine` Debugger**

IntelliJ provides built-in coroutine debugging support:
- **`Coroutines` tab**: Shows active coroutines with their states
- **`Stack` traces**: `View` combined coroutine call stacks, not just thread stacks
- **Suspend points**: See where coroutines are suspended

```kotlin
suspend fun debugExample() = coroutineScope {
    val data1 = async { fetchData1() }  // Breakpoint here
    val data2 = async { fetchData2() }  // And here
    println("${data1.await()} ${data2.await()}")
}
```

**2. kotlinx.coroutines debug mode**

Enable debug mode to include coroutine identifiers in thread names and improve traces:
```kotlin
// Add VM option:
// -Dkotlinx.coroutines.debug

runBlocking {
    launch(Dispatchers.Default) {
        println(Thread.currentThread().name)
        // Example: "DefaultDispatcher-worker-1 @coroutine#1"
    }
}
```

### Profiling Tools

**1. Android Studio Profiler**

For Android apps, use the built-in profiler:
- **CPU Profiler**: Track coroutine execution across threads (especially helpful with `kotlinx.coroutines.debug` enabled)
- **Memory Profiler**: Detect leaks caused by long-lived coroutines and references
- **Energy Profiler**: See the impact of coroutine-based work on battery

**2. JVM Profilers**

Popular JVM profilers that can be effectively used with coroutines:
- **Async Profiler**: Low-overhead profiler, works well with async workloads
- **YourKit**: Commercial profiler with improved stack trace visualization
- **JProfiler**: Advanced thread metrics; combined with coroutine debug mode helps analysis

Note: explicit, first-class "coroutine-specific" metrics may be limited; typically you combine JVM metrics with coroutine debug data.

```kotlin
// Example of configuring coroutine scheduler pool sizes (does NOT itself enable profiling)
System.setProperty("kotlinx.coroutines.scheduler.core.pool.size", "4")
System.setProperty("kotlinx.coroutines.scheduler.max.pool.size", "128")
```

### Common Debugging Patterns

**Pattern 1: Adding debug names to coroutines**
```kotlin
runBlocking {
    launch(CoroutineName("UserDataLoader")) {
        // Easier to identify in debugger
        val data = loadUserData()
    }
}
```

**Pattern 2: Logging coroutine lifecycle**
```kotlin
fun CoroutineScope.launchWithLogging(
    name: String,
    block: suspend CoroutineScope.() -> Unit
): Job {
    return launch(CoroutineName(name)) {
        try {
            println("[$name] Started")
            block()
            println("[$name] Completed successfully")
        } catch (e: CancellationException) {
            println("[$name] Cancelled")
            throw e
        } catch (e: Exception) {
            println("[$name] Failed: ${e.message}")
            throw e
        }
    }
}
```

**Pattern 3: Structured debugging with supervisorScope**
```kotlin
suspend fun debugMultipleOperations() = supervisorScope {
    val job1 = launch(CoroutineName("Operation1")) {
        operation1()
    }
    val job2 = launch(CoroutineName("Operation2")) {
        operation2()
    }
    // If one fails, the other continues, which simplifies isolated debugging
}
```

### Memory Leak Detection

**Common leak causes**:
1. **Not cancelling coroutines**:
```kotlin
// Simplified example. On Android prefer viewModelScope for lifecycle awareness.
class ViewModel {
    private val scope = CoroutineScope(Dispatchers.Main)

    fun loadData() {
        scope.launch {
            // Potential leak if ViewModel is destroyed without calling clear()
        }
    }

    // Fix: Cancel scope (or use a lifecycle-aware scope)
    fun clear() {
        scope.cancel()
    }
}
```

2. **Capturing context in lambdas**:
```kotlin
class Activity {
    fun startWork() {
        GlobalScope.launch {
            // Leak: Activity reference captured
            updateUI()
        }
    }

    // Fix: Use lifecycleScope (AndroidX lifecycle-runtime-ktx)
    fun startWorkCorrect() {
        lifecycleScope.launch {
            updateUI()
        }
    }
}
```

### Performance Profiling

**Measuring coroutine overhead**:
```kotlin
suspend fun profileCoroutines() {
    val startTime = System.currentTimeMillis()

    coroutineScope {
        repeat(10_000) {
            launch {
                // Minimal work
                delay(1)
            }
        }
    }

    val duration = System.currentTimeMillis() - startTime
    println("Created 10,000 coroutines in ${duration}ms")
}
```

**Finding slow suspend points**:
```kotlin
suspend fun profileSuspendPoints() {
    measureTimedValue {
        fetchData()
    }.let { (result, duration) ->
        println("fetchData took ${duration.inWholeMilliseconds}ms")
        // use result as needed
    }
}
```

### Production Debugging

**1. Structured logging**:
```kotlin
class CoroutineLogger(private val logger: Logger) : CoroutineContext.Element {
    companion object Key : CoroutineContext.Key<CoroutineLogger>

    override val key: CoroutineContext.Key<CoroutineLogger> = Key

    fun log(message: String) {
        logger.info(message)
    }
}

val coroutineLogger = CoroutineLogger(myLogger)

runBlocking {
    launch(coroutineLogger + CoroutineName("Operation")) {
        coroutineContext[CoroutineLogger]?.log("Operation started")
    }
}
```

**2. Exception tracking**:
```kotlin
val handler = CoroutineExceptionHandler { context, exception ->
    // Send to crash reporting service
    Crashlytics.recordException(exception)
    println("Caught in ${context[CoroutineName]}: $exception")
}

runBlocking {
    launch(handler + CoroutineName("CriticalOperation")) {
        criticalWork()
    }
}
```

**3. Monitoring coroutine pools**:
```kotlin
// Stub example: there is no standard API; illustrates collecting custom metrics
fun getCoroutinePoolStats(): PoolStats {
    return PoolStats(
        activeCoroutines = /* custom metric */ 0,
        queuedTasks = /* custom metric */ 0,
        completedTasks = /* custom metric */ 0
    )
}
```

### Best Practices

1. **Always name important coroutines** for easier debugging
2. **Use structured concurrency** to avoid orphaned coroutines
3. **Profile early** to catch performance issues
4. **Enable debug mode** in development: `-Dkotlinx.coroutines.debug`
5. **Monitor for leaks** using a memory profiler
6. **Add logging** at key suspend points
7. **Use `supervisorScope`** when debugging and implementing independent operations

---

## Дополнительные Вопросы (RU)

1. Как использовать `kotlinx.coroutines.debug` совместно с JVM-профайлерами (`Async Profiler`, `YourKit`, `JProfiler`) для анализа сложных асинхронных сценариев?
2. Какие признаки в профайлерах указывают на утечки корутин или неправильно управляемый жизненный цикл (например, в `ViewModel` или `Activity`)?
3. Как организовать структурированное логирование корутин в продакшене так, чтобы можно было трассировать запрос end-to-end?
4. Как выбирать размеры пулов потоков и диспетчеров для высоконагруженных систем с корутинами?
5. Какие подходы и метрики использовать для сравнения накладных расходов корутин и потоков в конкретном проекте?

## Follow-ups

1. How can you combine `kotlinx.coroutines.debug` with JVM profilers (`Async Profiler`, `YourKit`, `JProfiler`) to analyze complex async scenarios?
2. What profiler signals indicate coroutine leaks or mismanaged lifecycle (for example in a `ViewModel` or `Activity`)?
3. How would you design structured logging for coroutines in production to enable end-to-end tracing of requests?
4. How do you choose dispatcher and thread pool sizes for high-load systems using coroutines?
5. Which approaches and metrics would you use to compare coroutine overhead vs threads in your specific project?

---

## Ссылки (RU)

- [Kotlin `Coroutines` Documentation](https://kotlinlang.org/docs/coroutines-overview.html)

## References

- [Kotlin `Coroutines` Documentation](https://kotlinlang.org/docs/coroutines-overview.html)

---

## Связанные Вопросы (RU)

### Сложные (Hard)
- [[q-coroutine-performance-optimization--kotlin--hard]] - Коррутины
- [[q-coroutine-memory-leaks--kotlin--hard]] - Коррутины
- [[q-advanced-coroutine-patterns--kotlin--hard]] - Коррутины
- [[q-select-expression-channels--kotlin--hard]] - Коррутины

### Предварительные (Easier)
- [[q-flow-combining-zip-combine--kotlin--medium]] - Коррутины
- [[q-what-is-coroutine--kotlin--easy]] - Коррутины

### Хаб
- [[q-kotlin-coroutines-introduction--kotlin--medium]] - Введение в корутины

## Related Questions

### Related (Hard)
- [[q-coroutine-performance-optimization--kotlin--hard]] - `Coroutines`
- [[q-coroutine-memory-leaks--kotlin--hard]] - `Coroutines`
- [[q-advanced-coroutine-patterns--kotlin--hard]] - `Coroutines`
- [[q-select-expression-channels--kotlin--hard]] - `Coroutines`

### Prerequisites (Easier)
- [[q-flow-combining-zip-combine--kotlin--medium]] - `Coroutines`
- [[q-what-is-coroutine--kotlin--easy]] - `Coroutines`

### Hub
- [[q-kotlin-coroutines-introduction--kotlin--medium]] - Comprehensive coroutines introduction
