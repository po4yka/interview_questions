---
id: android-363
title: "Polling Implementation / Реализация Polling"
aliases: ["Android Polling", "Polling Implementation", "Реализация Polling"]
topic: android
subtopics: [background-execution, coroutines, networking-http]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android, q-android-async-primitives--android--easy, q-android-lint-tool--android--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [android/background-execution, android/coroutines, android/networking-http, background-tasks, difficulty/medium, polling]
sources: []

---
# Вопрос (RU)

> Как реализовать polling в Android приложении? Какие подходы существуют и когда их использовать?

# Question (EN)

> How to implement polling in an Android application? What approaches exist and when to use them?

---

## Ответ (RU)

Polling — периодическая проверка данных с сервера. Выбор реализации зависит от требований: частота опроса, работа в фоне, переживание перезагрузки.

### 1. Coroutines + Flow (UI-bound)

Рекомендуемый подход для UI-зависимых задач с автоматической отменой при lifecycle.

```kotlin
// Repository
class DataRepository(private val api: ApiService) {
    fun pollData(intervalMs: Long = 5000): Flow<Result<Data>> = flow {
        while (currentCoroutineContext().isActive) {
            try {
                emit(Result.success(api.getData()))
            } catch (e: Exception) {
                emit(Result.failure(e))
            }
            delay(intervalMs)
        }
    }.flowOn(Dispatchers.IO)

    suspend fun getData(): Data = api.getData()

    // ✅ Polling с условием остановки
    fun pollUntilComplete(orderId: Int): Flow<Order> = flow {
        while (currentCoroutineContext().isActive) {
            val order = api.getOrder(orderId)
            emit(order)
            if (order.status == OrderStatus.COMPLETED) break
            delay(3000)
        }
    }.flowOn(Dispatchers.IO)
}

// ViewModel
class OrderViewModel(private val repo: DataRepository) : ViewModel() {
    val orderStatus = repo.pollUntilComplete(123)
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), null)
}
```

**Преимущества**: Простота, lifecycle-aware (привязка к scope, например `viewModelScope`), автоотмена.
**Недостатки**: Работает только пока жив соответствующий lifecycle/scope (например, `ViewModel`/экран).

### 2. WorkManager (Background)

Для гарантированного выполнения в фоне, переживает перезагрузку устройства.

```kotlin
class DataPollingWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        return try {
            val data = RetrofitClient.api.getData()
            database.dataDao().insert(data)
            // ✅ Успех, WorkManager сам применит backoff при последующих retry согласно конфигурации
            Result.success()
        } catch (e: Exception) {
            if (runAttemptCount < 3) Result.retry() else Result.failure()
        }
    }
}

// Планирование
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED)
    .setRequiresBatteryNotLow(true)
    .build()

val request = PeriodicWorkRequestBuilder<DataPollingWorker>(15, TimeUnit.MINUTES)
    .setConstraints(constraints)
    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 15, TimeUnit.MINUTES)
    .build()

WorkManager.getInstance(context)
    .enqueueUniquePeriodicWork("polling", ExistingPeriodicWorkPolicy.KEEP, request)
```

**Преимущества**: Гарантированное выполнение, переживает перезагрузку, battery-aware.
**Недостатки**: Минимальный интервал 15 минут, не подходит для real-time.

### 3. Adaptive Intervals

Оптимизация частоты опроса на основе результатов.

```kotlin
import kotlin.math.max
import kotlin.math.min

class SmartPollingManager(private val repo: DataRepository) {
    fun startAdaptivePolling(): Flow<Data> = flow {
        var interval = 5000L // Начальный интервал (локальный для этого poll)
        val minInterval = 1000L
        val maxInterval = 60000L

        while (currentCoroutineContext().isActive) {
            try {
                val data = repo.getData()
                emit(data)
                // ✅ Адаптация интервала
                interval = if (data.hasChanges) {
                    max(minInterval, interval / 2) // Чаще при изменениях
                } else {
                    min(maxInterval, interval * 2) // Реже при отсутствии
                }
            } catch (e: Exception) {
                // ❌ Не увеличивать интервал слишком агрессивно
                interval = min(maxInterval, (interval * 1.5).toLong())
            }
            delay(interval)
        }
    }.flowOn(Dispatchers.IO)
}
```

### 4. Exponential Backoff

Retry-стратегия для устойчивости к ошибкам.

```kotlin
fun pollWithBackoff(maxAttempts: Int = 5): Flow<Result<Data>> = flow {
    var attempt = 0
    var currentDelay = 1000L

    while (attempt < maxAttempts && currentCoroutineContext().isActive) {
        try {
            emit(Result.success(api.getData()))
            // Успех — можно выйти или продолжить по другой логике
            return@flow
        } catch (e: Exception) {
            emit(Result.failure(e))
            attempt++
            if (attempt >= maxAttempts) break
            currentDelay *= 2 // 1s, 2s, 4s, 8s, 16s
            delay(currentDelay)
        }
    }
}.flowOn(Dispatchers.IO)
```

### Best Practices

1. **Lifecycle-aware cancellation**: Используйте `viewModelScope` или другие scope'ы для автоотмены.
2. **Network checks**: Проверяйте доступность сети перед запросом.
3. **Battery optimization**: Избегайте частых запросов в фоне, используйте WorkManager constraints.
4. **Error handling**: Используйте exponential backoff для retry.
5. **Adaptive intervals**: Подстраивайте частоту под реальные изменения данных.

### Сравнение Подходов

| Метод | Use Case | Интервал | Lifecycle |
|-------|----------|----------|-----------|
| Coroutines + `Flow` | UI-bound | Любой | Привязан к lifecycle scope (`Activity`/`Fragment`/`ViewModel`) |
| WorkManager | Background | ≥15 минут | Переживает перезагрузку |
| Handler + Runnable | Simple tasks | Любой | Ручное управление |
| AlarmManager | Exact timing | Любой | Работает в фоне, возможен повышенный расход батареи |

---

## Answer (EN)

Polling is periodic data fetching from a server. Implementation choice depends on requirements: frequency, background execution, surviving device reboot.

### 1. Coroutines + Flow (UI-bound)

Recommended approach for UI-dependent tasks with automatic lifecycle cancellation.

```kotlin
// Repository
class DataRepository(private val api: ApiService) {
    fun pollData(intervalMs: Long = 5000): Flow<Result<Data>> = flow {
        while (currentCoroutineContext().isActive) {
            try {
                emit(Result.success(api.getData()))
            } catch (e: Exception) {
                emit(Result.failure(e))
            }
            delay(intervalMs)
        }
    }.flowOn(Dispatchers.IO)

    suspend fun getData(): Data = api.getData()

    // ✅ Polling with stop condition
    fun pollUntilComplete(orderId: Int): Flow<Order> = flow {
        while (currentCoroutineContext().isActive) {
            val order = api.getOrder(orderId)
            emit(order)
            if (order.status == OrderStatus.COMPLETED) break
            delay(3000)
        }
    }.flowOn(Dispatchers.IO)
}

// ViewModel
class OrderViewModel(private val repo: DataRepository) : ViewModel() {
    val orderStatus = repo.pollUntilComplete(123)
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), null)
}
```

**Pros**: Simple, lifecycle-aware (tied to a scope such as `viewModelScope`), auto-cancellation.
**Cons**: Only works while the corresponding lifecycle/scope (e.g., `ViewModel`/screen) is alive.

### 2. WorkManager (Background)

For guaranteed background execution that survives device reboots.

```kotlin
class DataPollingWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        return try {
            val data = RetrofitClient.api.getData()
            database.dataDao().insert(data)
            // ✅ On success; WorkManager applies configured backoff for retries
            Result.success()
        } catch (e: Exception) {
            if (runAttemptCount < 3) Result.retry() else Result.failure()
        }
    }
}

// Scheduling
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED)
    .setRequiresBatteryNotLow(true)
    .build()

val request = PeriodicWorkRequestBuilder<DataPollingWorker>(15, TimeUnit.MINUTES)
    .setConstraints(constraints)
    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 15, TimeUnit.MINUTES)
    .build()

WorkManager.getInstance(context)
    .enqueueUniquePeriodicWork("polling", ExistingPeriodicWorkPolicy.KEEP, request)
```

**Pros**: Guaranteed execution, survives reboot, battery-aware.
**Cons**: Minimum interval 15 minutes, not suitable for real-time.

### 3. Adaptive Intervals

Optimize polling frequency based on results.

```kotlin
import kotlin.math.max
import kotlin.math.min

class SmartPollingManager(private val repo: DataRepository) {
    fun startAdaptivePolling(): Flow<Data> = flow {
        var interval = 5000L // Initial interval (local to this poll)
        val minInterval = 1000L
        val maxInterval = 60000L

        while (currentCoroutineContext().isActive) {
            try {
                val data = repo.getData()
                emit(data)
                // ✅ Adapt interval
                interval = if (data.hasChanges) {
                    max(minInterval, interval / 2) // Faster on changes
                } else {
                    min(maxInterval, interval * 2) // Slower when stable
                }
            } catch (e: Exception) {
                // ❌ Don't increase interval too aggressively
                interval = min(maxInterval, (interval * 1.5).toLong())
            }
            delay(interval)
        }
    }.flowOn(Dispatchers.IO)
}
```

### 4. Exponential Backoff

Retry strategy for error resilience.

```kotlin
fun pollWithBackoff(maxAttempts: Int = 5): Flow<Result<Data>> = flow {
    var attempt = 0
    var currentDelay = 1000L

    while (attempt < maxAttempts && currentCoroutineContext().isActive) {
        try {
            emit(Result.success(api.getData()))
            // On success we can exit or switch to another strategy
            return@flow
        } catch (e: Exception) {
            emit(Result.failure(e))
            attempt++
            if (attempt >= maxAttempts) break
            currentDelay *= 2 // 1s, 2s, 4s, 8s, 16s
            delay(currentDelay)
        }
    }
}.flowOn(Dispatchers.IO)
```

### Best Practices

1. **Lifecycle-aware cancellation**: Use `viewModelScope` or other scopes for auto-cancellation.
2. **Network checks**: Verify network availability before requests.
3. **Battery optimization**: Avoid frequent background polling, use WorkManager constraints.
4. **Error handling**: Use exponential backoff for retries.
5. **Adaptive intervals**: Adjust frequency based on actual data changes.

### Comparison

| Method | Use Case | Interval | Lifecycle |
|--------|----------|----------|-----------|
| Coroutines + `Flow` | UI-bound | Any | Tied to lifecycle scope (`Activity`/`Fragment`/`ViewModel`) |
| WorkManager | Background | ≥15 min | Survives reboot |
| Handler + Runnable | Simple tasks | Any | Manual management |
| AlarmManager | Exact timing | Any | Background, possible higher battery usage |

---

## Дополнительные Вопросы (RU)

1. Как реализовать polling с fallback на WebSocket при ненадежном соединении?
2. Как оптимизировать расход батареи при фоновом polling?
3. Как обрабатывать обновление токена аутентификации во время длительного polling?
4. Каковы компромиссы между polling и Server-Sent Events (SSE)?
5. Как реализовать приоритетный polling для нескольких источников данных?

## Follow-ups

1. How to implement polling with WebSocket fallback for unreliable connections?
2. How to optimize battery consumption when polling in background?
3. How to handle authentication token refresh during long-running polling?
4. What are the trade-offs between polling and Server-Sent Events (SSE)?
5. How to implement priority-based polling for multiple data sources?

## Ссылки (RU)

- [[c-android]]

## References

- [Android Background Work Guide](https://developer.android.com/guide/background)
- [Kotlin Coroutines Best Practices](https://developer.android.com/kotlin/coroutines/coroutines-best-practices)

## Связанные Вопросы (RU)

### База (проще)

- [[q-android-async-primitives--android--easy]]

### На Том Же Уровне

- [[q-android-lint-tool--android--medium]]

## Related Questions

### Prerequisites (Easier)

- [[q-android-async-primitives--android--easy]]

### Related (Same Level)

- [[q-android-lint-tool--android--medium]]
