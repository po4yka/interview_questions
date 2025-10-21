---
id: 20251012-122762
title: "Android Async Primitives / Примитивы асинхронности Android"
aliases: [Android Async Primitives, Примитивы асинхронности Android]
topic: android
subtopics: [coroutines, threading]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: reviewed
moc: moc-android
related: [q-coroutines-basics--kotlin--easy, q-viewmodel-pattern--android--easy, q-lifecycle-aware-components--android--medium]
created: 2025-10-15
updated: 2025-10-15
tags: [android/coroutines, android/threading, async, coroutines, threading, difficulty/easy]
---
# Question (EN)
> What async primitives are used for data processing in Android?

# Вопрос (RU)
> Какие асинхронные примитивы используют для обработки данных в Android?

---

## Answer (EN)

Android provides several async primitives: **Thread** (basic), **Handler/Looper** (message passing), **AsyncTask** (deprecated), **ExecutorService** (thread pools), **Coroutines** (modern, recommended), **RxJava** (reactive streams), and **WorkManager** (background tasks).

**Modern recommendation**: Use Kotlin Coroutines with Flow for most async operations.

**1. Kotlin Coroutines (Recommended)**
- **Lightweight concurrency** framework
- **Structured concurrency** with automatic lifecycle management
- **Readable, sequential code** that looks synchronous

```kotlin
// Basic coroutine usage
class DataViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            val data = withContext(Dispatchers.IO) {
                repository.fetchData()
            }
            _uiState.value = UiState.Success(data)
        }
    }

    // Parallel operations
    fun loadMultiple() {
        viewModelScope.launch {
            val result1 = async { fetchFromApi1() }
            val result2 = async { fetchFromApi2() }
            val combined = result1.await() + result2.await()
            _data.value = combined
        }
    }
}
```

**2. Flow (Reactive Streams)**
- **Cold flow**: Starts when collected
- **Hot flow**: Always active (StateFlow, SharedFlow)
- **Operators**: map, filter, combine, etc.

```kotlin
// Cold flow
fun getUsers(): Flow<List<User>> = flow {
    val users = api.fetchUsers()
    emit(users)
}.flowOn(Dispatchers.IO)

// Hot flow
private val _userUpdates = MutableStateFlow<User?>(null)
val userUpdates: StateFlow<User?> = _userUpdates.asStateFlow()

// Usage
lifecycleScope.launch {
    repository.getUsers().collect { users ->
        adapter.submitList(users)
    }
}
```

**3. WorkManager**
- **Guaranteed execution** that survives app restarts
- **Constraints**: WiFi, charging, low battery
- **Periodic work** and **one-time work**

```kotlin
class DataSyncWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            syncData()
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}

// Schedule work
val workRequest = PeriodicWorkRequestBuilder<DataSyncWorker>(
    repeatInterval = 15,
    repeatIntervalTimeUnit = TimeUnit.MINUTES
).build()

WorkManager.getInstance(context).enqueue(workRequest)
```

**4. Handler/Looper (Legacy)**
- **Message passing** between threads
- **Delayed execution** with postDelayed
- **Low-level** threading primitive

```kotlin
class MyActivity : AppCompatActivity() {
    private val handler = Handler(Looper.getMainLooper())

    fun performBackgroundWork() {
        Thread {
            val result = processData()
            handler.post {
                textView.text = result
            }
        }.start()
    }

    fun scheduleTask() {
        handler.postDelayed({
            updateUI()
        }, 1000)
    }
}
```

**5. ExecutorService (Legacy)**
- **Thread pool management**
- **Future** for getting results
- **Manual lifecycle** management

```kotlin
class DataProcessor {
    private val executor = Executors.newFixedThreadPool(4)

    fun processInBackground() {
        executor.execute {
            val result = heavyComputation()
            runOnUiThread {
                updateUI(result)
            }
        }
    }

    fun processWithResult(): Future<String> {
        return executor.submit<String> {
            performOperation()
        }
    }
}
```

**6. RxJava (Legacy)**
- **Reactive programming** library
- **Complex operators** for data transformation
- **Steep learning curve**

```kotlin
fun loadData(): Observable<List<Item>> {
    return Observable.create { emitter ->
        try {
            val data = api.fetchData()
            emitter.onNext(data)
            emitter.onComplete()
        } catch (e: Exception) {
            emitter.onError(e)
        }
    }
    .subscribeOn(Schedulers.io())
    .observeOn(AndroidSchedulers.mainThread())
}
```

**7. AsyncTask (Deprecated)**
- **Deprecated since API 30**
- **Memory leaks** with Activity/Fragment references
- **No cancellation** mechanism
- **Don't use** in new code

**Comparison:**

| Primitive | Difficulty | Lifecycle Aware | Cancellation | Modern | Use Case |
|-----------|------------|-----------------|--------------|--------|----------|
| **Coroutines** | Low | Yes | Yes | Yes | General async operations |
| **Flow** | Medium | Yes | Yes | Yes | Reactive streams |
| **WorkManager** | Low | Yes | Yes | Yes | Guaranteed background work |
| **Handler** | Medium | No | Manual | Yes | Message passing |
| **ExecutorService** | Medium | No | Manual | Yes | Thread pool management |
| **RxJava** | High | No | Yes | Yes | Complex reactive streams |
| **AsyncTask** | Low | No | No | No | Deprecated |

**Best Practices:**
- **Use Coroutines** for most async operations
- **Use Flow** for reactive data streams
- **Use WorkManager** for guaranteed background work
- **Avoid AsyncTask** - use Coroutines instead
- **Use Handler** only for specific message passing needs

## Ответ (RU)

Android предоставляет несколько асинхронных примитивов: **Thread** (базовый), **Handler/Looper** (передача сообщений), **AsyncTask** (устарел), **ExecutorService** (пулы потоков), **Coroutines** (современный, рекомендуется), **RxJava** (реактивные потоки) и **WorkManager** (фоновые задачи).

**Современная рекомендация**: Используйте Kotlin Coroutines с Flow для большинства асинхронных операций.

**1. Kotlin Coroutines (Рекомендуется)**
- **Легковесный framework** для конкурентности
- **Структурированная конкурентность** с автоматическим управлением жизненным циклом
- **Читаемый, последовательный код**, который выглядит синхронным

```kotlin
// Базовое использование корутин
class DataViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            val data = withContext(Dispatchers.IO) {
                repository.fetchData()
            }
            _uiState.value = UiState.Success(data)
        }
    }

    // Параллельные операции
    fun loadMultiple() {
        viewModelScope.launch {
            val result1 = async { fetchFromApi1() }
            val result2 = async { fetchFromApi2() }
            val combined = result1.await() + result2.await()
            _data.value = combined
        }
    }
}
```

**2. Flow (Реактивные потоки)**
- **Cold flow**: Начинает работу при подписке
- **Hot flow**: Всегда активен (StateFlow, SharedFlow)
- **Операторы**: map, filter, combine и др.

```kotlin
// Cold flow
fun getUsers(): Flow<List<User>> = flow {
    val users = api.fetchUsers()
    emit(users)
}.flowOn(Dispatchers.IO)

// Hot flow
private val _userUpdates = MutableStateFlow<User?>(null)
val userUpdates: StateFlow<User?> = _userUpdates.asStateFlow()

// Использование
lifecycleScope.launch {
    repository.getUsers().collect { users ->
        adapter.submitList(users)
    }
}
```

**3. WorkManager**
- **Гарантированное выполнение**, которое переживает перезапуск приложения
- **Ограничения**: WiFi, зарядка, низкий заряд батареи
- **Периодическая работа** и **одноразовая работа**

```kotlin
class DataSyncWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            syncData()
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}

// Планирование работы
val workRequest = PeriodicWorkRequestBuilder<DataSyncWorker>(
    repeatInterval = 15,
    repeatIntervalTimeUnit = TimeUnit.MINUTES
).build()

WorkManager.getInstance(context).enqueue(workRequest)
```

**4. Handler/Looper (Устаревший)**
- **Передача сообщений** между потоками
- **Отложенное выполнение** с postDelayed
- **Низкоуровневый** примитив потоков

```kotlin
class MyActivity : AppCompatActivity() {
    private val handler = Handler(Looper.getMainLooper())

    fun performBackgroundWork() {
        Thread {
            val result = processData()
            handler.post {
                textView.text = result
            }
        }.start()
    }

    fun scheduleTask() {
        handler.postDelayed({
            updateUI()
        }, 1000)
    }
}
```

**5. ExecutorService (Устаревший)**
- **Управление пулом потоков**
- **Future** для получения результатов
- **Ручное управление** жизненным циклом

```kotlin
class DataProcessor {
    private val executor = Executors.newFixedThreadPool(4)

    fun processInBackground() {
        executor.execute {
            val result = heavyComputation()
            runOnUiThread {
                updateUI(result)
            }
        }
    }

    fun processWithResult(): Future<String> {
        return executor.submit<String> {
            performOperation()
        }
    }
}
```

**6. RxJava (Устаревший)**
- **Реактивная библиотека** программирования
- **Сложные операторы** для трансформации данных
- **Крутая кривая** обучения

```kotlin
fun loadData(): Observable<List<Item>> {
    return Observable.create { emitter ->
        try {
            val data = api.fetchData()
            emitter.onNext(data)
            emitter.onComplete()
        } catch (e: Exception) {
            emitter.onError(e)
        }
    }
    .subscribeOn(Schedulers.io())
    .observeOn(AndroidSchedulers.mainThread())
}
```

**7. AsyncTask (Устарел)**
- **Устарел с API 30**
- **Утечки памяти** при ссылках на Activity/Fragment
- **Нет механизма** отмены
- **Не используйте** в новом коде

**Сравнение:**

| Примитив | Сложность | Осведомленность о жизненном цикле | Отмена | Современный | Случай использования |
|----------|-----------|-----------------------------------|--------|-------------|---------------------|
| **Coroutines** | Низкая | Да | Да | Да | Общие асинхронные операции |
| **Flow** | Средняя | Да | Да | Да | Реактивные потоки |
| **WorkManager** | Низкая | Да | Да | Да | Гарантированная фоновая работа |
| **Handler** | Средняя | Нет | Вручную | Да | Передача сообщений |
| **ExecutorService** | Средняя | Нет | Вручную | Да | Управление пулом потоков |
| **RxJava** | Высокая | Нет | Да | Да | Сложные реактивные потоки |
| **AsyncTask** | Низкая | Нет | Нет | Нет | Устарел |

**Лучшие практики:**
- **Используйте Coroutines** для большинства асинхронных операций
- **Используйте Flow** для реактивных потоков данных
- **Используйте WorkManager** для гарантированной фоновой работы
- **Избегайте AsyncTask** - используйте Coroutines вместо этого
- **Используйте Handler** только для специфических нужд передачи сообщений

---

## Follow-ups

- How do you choose between Coroutines and RxJava for a new project?
- What are the key differences between StateFlow and SharedFlow?
- How do you handle cancellation in long-running coroutines?
- What are the benefits of using WorkManager over other background task solutions?
- How do you debug async operations in Android?

## References

- [Kotlin Coroutines](https://kotlinlang.org/docs/coroutines-overview.html)
- [Flow Documentation](https://kotlinlang.org/docs/flow.html)
- [WorkManager Guide](https://developer.android.com/topic/libraries/architecture/workmanager)
- [Android Threading](https://developer.android.com/guide/components/processes-and-threads)

## Related Questions

### Prerequisites (Easier)
- [[q-coroutines-basics--kotlin--easy]] - Coroutines fundamentals
- [[q-viewmodel-pattern--android--easy]] - ViewModel pattern

### Related (Medium)
- [[q-lifecycle-aware-components--android--medium]] - Lifecycle management
- [[q-flow-operators--kotlin--medium]] - Flow operators
- [[q-what-is-workmanager--android--medium]] - WorkManager basics

### Advanced (Harder)
- [[q-advanced-coroutine-patterns--kotlin--hard]] - Advanced coroutines
- [[q-workmanager-execution-guarantee--android--medium]] - WorkManager guarantees
