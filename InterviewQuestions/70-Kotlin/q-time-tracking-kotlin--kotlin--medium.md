---
anki_cards:
- slug: q-time-tracking-kotlin--kotlin--medium-0-en
  language: en
  anki_id: 1769173397962
  synced_at: '2026-01-23T17:03:51.065846'
- slug: q-time-tracking-kotlin--kotlin--medium-0-ru
  language: ru
  anki_id: 1769173397983
  synced_at: '2026-01-23T17:03:51.072026'
---
# Вопрос (RU)
> Объясните пакет kotlin.time. Как измерять время и работать с длительностями в Kotlin?

# Question (EN)
> Explain the kotlin.time package. How do you measure time and work with durations in Kotlin?

## Ответ (RU)

**Стабильно с Kotlin 2.3**

Пакет `kotlin.time` предоставляет мультиплатформенный API для работы со временем: измерение длительности операций, работа с временными интервалами и отметками времени.

---

### Класс Duration

```kotlin
import kotlin.time.Duration
import kotlin.time.Duration.Companion.seconds
import kotlin.time.Duration.Companion.milliseconds
import kotlin.time.Duration.Companion.minutes

// Создание Duration
val fiveSeconds = 5.seconds
val twoMinutes = 2.minutes
val halfSecond = 500.milliseconds

// Арифметика
val total = fiveSeconds + twoMinutes  // 2m 5s
val doubled = fiveSeconds * 2         // 10s
val half = fiveSeconds / 2            // 2.5s

// Сравнение
println(fiveSeconds > twoMinutes)  // false
println(fiveSeconds < 10.seconds)  // true
```

---

### Измерение времени

```kotlin
import kotlin.time.measureTime
import kotlin.time.measureTimedValue

// measureTime - возвращает только Duration
val elapsed = measureTime {
    // операция
    Thread.sleep(100)
}
println("Took: $elapsed")  // Took: 100.123456ms

// measureTimedValue - возвращает результат и Duration
val (result, duration) = measureTimedValue {
    // операция с результатом
    computeExpensiveValue()
}
println("Result: $result, took: $duration")
```

---

### TimeSource и TimeMark

```kotlin
import kotlin.time.TimeSource

// Получение источника времени
val timeSource = TimeSource.Monotonic

// Создание временной отметки
val start = timeSource.markNow()

// Выполнение операции
performWork()

// Измерение прошедшего времени
val elapsed = start.elapsedNow()
println("Elapsed: $elapsed")

// Проверка истечения времени
val deadline = start + 5.seconds
println("Expired: ${deadline.hasPassedNow()}")
```

---

### Практические примеры

**Таймаут операций:**

```kotlin
import kotlin.time.TimeSource
import kotlin.time.Duration.Companion.seconds

suspend fun fetchWithTimeout(timeout: Duration): Result {
    val deadline = TimeSource.Monotonic.markNow() + timeout

    while (!deadline.hasPassedNow()) {
        val result = tryFetch()
        if (result != null) return result
        delay(100.milliseconds)
    }

    throw TimeoutException("Operation timed out after $timeout")
}

// Использование
val result = fetchWithTimeout(5.seconds)
```

**Профилирование:**

```kotlin
class Profiler {
    private val measurements = mutableMapOf<String, Duration>()

    inline fun <T> measure(name: String, block: () -> T): T {
        val (result, duration) = measureTimedValue(block)
        measurements[name] = (measurements[name] ?: Duration.ZERO) + duration
        return result
    }

    fun report() {
        measurements.forEach { (name, total) ->
            println("$name: $total")
        }
    }
}

// Использование
val profiler = Profiler()
profiler.measure("database") { queryDatabase() }
profiler.measure("api") { callApi() }
profiler.report()
```

**Rate limiting:**

```kotlin
class RateLimiter(
    private val maxRequests: Int,
    private val window: Duration
) {
    private val requests = mutableListOf<TimeMark>()
    private val timeSource = TimeSource.Monotonic

    fun tryAcquire(): Boolean {
        val now = timeSource.markNow()

        // Удаляем устаревшие записи
        requests.removeAll { (now - it) > window }

        if (requests.size >= maxRequests) {
            return false
        }

        requests.add(now)
        return true
    }
}

// Использование: максимум 10 запросов в секунду
val limiter = RateLimiter(10, 1.seconds)
if (limiter.tryAcquire()) {
    processRequest()
}
```

---

### Форматирование Duration

```kotlin
val duration = 3661.seconds  // 1 час, 1 минута, 1 секунда

// Стандартный вывод
println(duration)  // 1h 1m 1s

// В конкретных единицах
println(duration.inWholeHours)        // 1
println(duration.inWholeMinutes)      // 61
println(duration.inWholeSeconds)      // 3661
println(duration.inWholeMilliseconds) // 3661000

// Десятичные значения
println(duration.inSeconds)  // 3661.0 (deprecated в пользу toDouble)
println(duration.toDouble(DurationUnit.HOURS))  // 1.0169...
```

---

### Компоненты Duration

```kotlin
val duration = 90.minutes + 30.seconds

// Разбиение на компоненты
duration.toComponents { hours, minutes, seconds, nanoseconds ->
    println("$hours h $minutes m $seconds s")
    // 1 h 30 m 30 s
}

// Упрощенная версия
duration.toComponents { minutes, seconds, nanoseconds ->
    println("$minutes min $seconds sec")
}
```

---

### Специальные значения

```kotlin
// Бесконечность
val infinite = Duration.INFINITE
println(infinite.isInfinite())  // true

// Ноль
val zero = Duration.ZERO
println(zero.isPositive())  // false

// Проверки
println(5.seconds.isPositive())  // true
println((-5).seconds.isNegative())  // true
println(Duration.ZERO.isFinite())  // true
```

---

### Мультиплатформенность

```kotlin
// TimeSource работает на всех платформах
expect val platformTimeSource: TimeSource

// JVM
actual val platformTimeSource: TimeSource = TimeSource.Monotonic

// Native/JS
actual val platformTimeSource: TimeSource = TimeSource.Monotonic
```

---

## Answer (EN)

**Stable since Kotlin 2.3**

The `kotlin.time` package provides a multiplatform API for working with time: measuring operation durations, working with time intervals, and time marks.

---

### Duration Class

```kotlin
import kotlin.time.Duration
import kotlin.time.Duration.Companion.seconds
import kotlin.time.Duration.Companion.milliseconds
import kotlin.time.Duration.Companion.minutes

// Creating Duration
val fiveSeconds = 5.seconds
val twoMinutes = 2.minutes
val halfSecond = 500.milliseconds

// Arithmetic
val total = fiveSeconds + twoMinutes  // 2m 5s
val doubled = fiveSeconds * 2         // 10s
val half = fiveSeconds / 2            // 2.5s

// Comparison
println(fiveSeconds > twoMinutes)  // false
println(fiveSeconds < 10.seconds)  // true
```

---

### Measuring Time

```kotlin
import kotlin.time.measureTime
import kotlin.time.measureTimedValue

// measureTime - returns only Duration
val elapsed = measureTime {
    // operation
    Thread.sleep(100)
}
println("Took: $elapsed")  // Took: 100.123456ms

// measureTimedValue - returns result and Duration
val (result, duration) = measureTimedValue {
    // operation with result
    computeExpensiveValue()
}
println("Result: $result, took: $duration")
```

---

### TimeSource and TimeMark

```kotlin
import kotlin.time.TimeSource

// Get time source
val timeSource = TimeSource.Monotonic

// Create time mark
val start = timeSource.markNow()

// Perform operation
performWork()

// Measure elapsed time
val elapsed = start.elapsedNow()
println("Elapsed: $elapsed")

// Check if time has passed
val deadline = start + 5.seconds
println("Expired: ${deadline.hasPassedNow()}")
```

---

### Practical Examples

**Operation Timeout:**

```kotlin
import kotlin.time.TimeSource
import kotlin.time.Duration.Companion.seconds

suspend fun fetchWithTimeout(timeout: Duration): Result {
    val deadline = TimeSource.Monotonic.markNow() + timeout

    while (!deadline.hasPassedNow()) {
        val result = tryFetch()
        if (result != null) return result
        delay(100.milliseconds)
    }

    throw TimeoutException("Operation timed out after $timeout")
}

// Usage
val result = fetchWithTimeout(5.seconds)
```

**Profiling:**

```kotlin
class Profiler {
    private val measurements = mutableMapOf<String, Duration>()

    inline fun <T> measure(name: String, block: () -> T): T {
        val (result, duration) = measureTimedValue(block)
        measurements[name] = (measurements[name] ?: Duration.ZERO) + duration
        return result
    }

    fun report() {
        measurements.forEach { (name, total) ->
            println("$name: $total")
        }
    }
}

// Usage
val profiler = Profiler()
profiler.measure("database") { queryDatabase() }
profiler.measure("api") { callApi() }
profiler.report()
```

**Rate Limiting:**

```kotlin
class RateLimiter(
    private val maxRequests: Int,
    private val window: Duration
) {
    private val requests = mutableListOf<TimeMark>()
    private val timeSource = TimeSource.Monotonic

    fun tryAcquire(): Boolean {
        val now = timeSource.markNow()

        // Remove expired entries
        requests.removeAll { (now - it) > window }

        if (requests.size >= maxRequests) {
            return false
        }

        requests.add(now)
        return true
    }
}

// Usage: max 10 requests per second
val limiter = RateLimiter(10, 1.seconds)
if (limiter.tryAcquire()) {
    processRequest()
}
```

---

### Formatting Duration

```kotlin
val duration = 3661.seconds  // 1 hour, 1 minute, 1 second

// Standard output
println(duration)  // 1h 1m 1s

// In specific units
println(duration.inWholeHours)        // 1
println(duration.inWholeMinutes)      // 61
println(duration.inWholeSeconds)      // 3661
println(duration.inWholeMilliseconds) // 3661000

// Decimal values
println(duration.inSeconds)  // 3661.0 (deprecated for toDouble)
println(duration.toDouble(DurationUnit.HOURS))  // 1.0169...
```

---

### Duration Components

```kotlin
val duration = 90.minutes + 30.seconds

// Breaking into components
duration.toComponents { hours, minutes, seconds, nanoseconds ->
    println("$hours h $minutes m $seconds s")
    // 1 h 30 m 30 s
}

// Simplified version
duration.toComponents { minutes, seconds, nanoseconds ->
    println("$minutes min $seconds sec")
}
```

---

### Special Values

```kotlin
// Infinity
val infinite = Duration.INFINITE
println(infinite.isInfinite())  // true

// Zero
val zero = Duration.ZERO
println(zero.isPositive())  // false

// Checks
println(5.seconds.isPositive())  // true
println((-5).seconds.isNegative())  // true
println(Duration.ZERO.isFinite())  // true
```

---

### Multiplatform Support

```kotlin
// TimeSource works on all platforms
expect val platformTimeSource: TimeSource

// JVM
actual val platformTimeSource: TimeSource = TimeSource.Monotonic

// Native/JS
actual val platformTimeSource: TimeSource = TimeSource.Monotonic
```

---

## Follow-ups

- What is the difference between Monotonic and System time sources?
- How does Duration handle overflow for very large values?
- Can you serialize Duration values?

## Related Questions

- [[q-coroutine-virtual-time--kotlin--medium]]
- [[q-performance-profiling-kotlin--kotlin--medium]]

## References

- https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.time/
- https://kotlinlang.org/docs/time-measurement.html
