---
id: kotlin-077
title: "Coroutine Profiling and Debugging / Профилирование и отладка корутин"
aliases: ["Coroutine Profiling and Debugging, Профилирование и отладка корутин"]

# Classification
topic: kotlin
subtopics: [advanced, coroutines, patterns]
question_kind: theory
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Coroutines Guide - Question 140025

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-associatewith-vs-associateby--kotlin--easy, q-kotlin-higher-order-functions--kotlin--medium, q-sam-conversions--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [coroutines, difficulty/hard, difficulty/medium, kotlin]
---
# Вопрос (RU)
> Продвинутая тема корутин Kotlin 140025

---

# Question (EN)
> Kotlin Coroutines advanced topic 140025

## Ответ (RU)

Профилирование и отладка корутин требуют специализированных инструментов и техник, поскольку корутины могут переключаться между потоками и имеют сложные потоки выполнения. Понимание эффективного профилирования и отладки критически важно для продакшн-приложений.

### Инструменты Отладки

**1. Отладчик корутин IntelliJ IDEA**

IntelliJ предоставляет встроенную поддержку отладки корутин:
- **Вкладка Coroutines**: Показывает все активные корутины с их состояниями
- **Stack traces**: Просмотр полных стеков вызовов корутин, не только потоков
- **Точки приостановки**: Видно где корутины приостановлены

```kotlin
suspend fun debugExample() {
    val data1 = async { fetchData1() }  // Breakpoint здесь
    val data2 = async { fetchData2() }  // И здесь
    println("${data1.await()} ${data2.await()}")
}
```

**2. Утилита CoroutineDebugger**

Включите режим отладки чтобы получить имена корутин в именах потоков:
```kotlin
// Добавьте VM опцию:
// -Dkotlinx.coroutines.debug

launch(Dispatchers.Default) {
    println(Thread.currentThread().name)
    // Выводит: "DefaultDispatcher-worker-1 @coroutine#1"
}
```

### Инструменты Профилирования

**1. Android Studio Profiler**

Для Android приложений используйте встроенный profiler:
- **CPU Profiler**: Отслеживание выполнения корутин по потокам
- **Memory Profiler**: Обнаружение утечек связанных с корутинами
- **Energy Profiler**: Влияние корутин на батарею

**2. JVM Profilers**

Популярные JVM профайлеры с поддержкой корутин:
- **Async Profiler**: Профайлер с низкими накладными расходами
- **YourKit**: Коммерческий профайлер с визуализацией корутин
- **JProfiler**: Показывает метрики специфичные для корутин

```kotlin
// Включить хуки профилирования
System.setProperty("kotlinx.coroutines.scheduler.core.pool.size", "4")
System.setProperty("kotlinx.coroutines.scheduler.max.pool.size", "128")
```

### Распространенные Паттерны Отладки

**Паттерн 1: Добавление отладочных имен корутинам**
```kotlin
launch(CoroutineName("UserDataLoader")) {
    // Легче идентифицировать в отладчике
    val data = loadUserData()
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
    // Если одна упадет, можно отлаживать другую
}
```

### Обнаружение Утечек Памяти

**Распространенные причины утечек**:
1. **Не отменяются корутины**:
```kotlin
class ViewModel {
    private val scope = CoroutineScope(Dispatchers.Main)

    fun loadData() {
        scope.launch {
            // Утечка если ViewModel уничтожена без вызова clear()
        }
    }

    // Исправление: Отменить scope
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

    // Исправление: Использовать lifecycle scope
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
    }
}
```

### Отладка В Продакшене

**1. Структурированное логирование**:
```kotlin
class CoroutineLogger(private val logger: Logger) : CoroutineContext.Element {
    companion object Key : CoroutineContext.Key<CoroutineLogger>

    override val key = Key

    fun log(message: String) {
        logger.info(message)
    }
}

launch(CoroutineLogger(myLogger)) {
    coroutineContext[CoroutineLogger]?.log("Operation started")
}
```

**2. Отслеживание исключений**:
```kotlin
val handler = CoroutineExceptionHandler { context, exception ->
    // Отправить в сервис отчетов о сбоях
    Crashlytics.recordException(exception)
    println("Caught in ${context[CoroutineName]}: $exception")
}

launch(handler + CoroutineName("CriticalOperation")) {
    criticalWork()
}
```

**3. Мониторинг пулов корутин**:
```kotlin
// Предоставить метрики
fun getCoroutinePoolStats(): PoolStats {
    return PoolStats(
        activeCoroutines = ...,
        queuedTasks = ...,
        completedTasks = ...
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
7. **Используйте `supervisorScope`** при отладке независимых операций

---

## Answer (EN)

Coroutine profiling and debugging require specialized tools and techniques because coroutines can jump between threads and have complex execution flows. Understanding how to profile and debug them effectively is crucial for production applications.

### Debugging Tools

**1. IntelliJ IDEA Coroutine Debugger**

IntelliJ provides built-in coroutine debugging support:
- **Coroutines tab**: Shows all active coroutines with their states
- **Stack traces**: View full coroutine call stacks, not just thread stacks
- **Suspend points**: See where coroutines are suspended

```kotlin
suspend fun debugExample() {
    val data1 = async { fetchData1() }  // Breakpoint here
    val data2 = async { fetchData2() }  // And here
    println("${data1.await()} ${data2.await()}")
}
```

**2. CoroutineDebugger utility**

Enable debug mode to get coroutine names in thread names:
```kotlin
// Add VM option:
// -Dkotlinx.coroutines.debug

launch(Dispatchers.Default) {
    println(Thread.currentThread().name)
    // Prints: "DefaultDispatcher-worker-1 @coroutine#1"
}
```

### Profiling Tools

**1. Android Studio Profiler**

For Android apps, use the built-in profiler:
- **CPU Profiler**: Track coroutine execution across threads
- **Memory Profiler**: Detect coroutine-related leaks
- **Energy Profiler**: See impact of coroutines on battery

**2. JVM Profilers**

Popular JVM profilers with coroutine support:
- **Async Profiler**: Low-overhead profiler
- **YourKit**: Commercial profiler with coroutine visualization
- **JProfiler**: Shows coroutine-specific metrics

```kotlin
// Enable profiling hooks
System.setProperty("kotlinx.coroutines.scheduler.core.pool.size", "4")
System.setProperty("kotlinx.coroutines.scheduler.max.pool.size", "128")
```

### Common Debugging Patterns

**Pattern 1: Adding debug names to coroutines**
```kotlin
launch(CoroutineName("UserDataLoader")) {
    // Easier to identify in debugger
    val data = loadUserData()
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
    // If one fails, can still debug the other
}
```

### Memory Leak Detection

**Common leak causes**:
1. **Not cancelling coroutines**:
```kotlin
class ViewModel {
    private val scope = CoroutineScope(Dispatchers.Main)

    fun loadData() {
        scope.launch {
            // Leak if ViewModel is destroyed without calling clear()
        }
    }

    // Fix: Cancel scope
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

    // Fix: Use lifecycle scope
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
    }
}
```

### Production Debugging

**1. Structured logging**:
```kotlin
class CoroutineLogger(private val logger: Logger) : CoroutineContext.Element {
    companion object Key : CoroutineContext.Key<CoroutineLogger>

    override val key = Key

    fun log(message: String) {
        logger.info(message)
    }
}

launch(CoroutineLogger(myLogger)) {
    coroutineContext[CoroutineLogger]?.log("Operation started")
}
```

**2. Exception tracking**:
```kotlin
val handler = CoroutineExceptionHandler { context, exception ->
    // Send to crash reporting service
    Crashlytics.recordException(exception)
    println("Caught in ${context[CoroutineName]}: $exception")
}

launch(handler + CoroutineName("CriticalOperation")) {
    criticalWork()
}
```

**3. Monitoring coroutine pools**:
```kotlin
// Expose metrics
fun getCoroutinePoolStats(): PoolStats {
    return PoolStats(
        activeCoroutines = ...,
        queuedTasks = ...,
        completedTasks = ...
    )
}
```

### Best Practices

1. **Always name important coroutines** for easier debugging
2. **Use structured concurrency** to avoid orphaned coroutines
3. **Profile early** to catch performance issues
4. **Enable debug mode** in development: `-Dkotlinx.coroutines.debug`
5. **Monitor for leaks** using memory profiler
6. **Add logging** at key suspend points
7. **Use `supervisorScope`** when debugging independent operations

---

## Follow-ups

1. **Follow-up question 1**
2. **Follow-up question 2**

---

## References

- [Kotlin Coroutines Documentation](https://kotlinlang.org/docs/coroutines-overview.html)

---

## Related Questions

### Related (Hard)
- [[q-coroutine-performance-optimization--kotlin--hard]] - Coroutines
- [[q-coroutine-memory-leaks--kotlin--hard]] - Coroutines
- [[q-advanced-coroutine-patterns--kotlin--hard]] - Coroutines
- [[q-select-expression-channels--kotlin--hard]] - Coroutines

### Prerequisites (Easier)
- [[q-flow-combining-zip-combine--kotlin--medium]] - Coroutines
- [[q-what-is-coroutine--kotlin--easy]] - Coroutines

### Hub
- [[q-kotlin-coroutines-introduction--kotlin--medium]] - Comprehensive coroutines introduction

