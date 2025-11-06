---
id: android-143
title: Android Async Primitives / Примитивы асинхронности Android
aliases: [Android Async Primitives, Примитивы асинхронности Android]
topic: android
subtopics:
  - coroutines
  - threads-sync
question_kind: android
difficulty: easy
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - q-coroutine-builders-basics--kotlin--easy
  - q-viewmodel-pattern--android--easy
sources: []
created: 2025-10-15
updated: 2025-10-29
tags: [android/coroutines, android/threads-sync, difficulty/easy]
---

# Вопрос (RU)
> Какие примитивы асинхронности предоставляет Android?

---

# Question (EN)
> What are Android Async Primitives?

---

## Ответ (RU)

Android предоставляет несколько примитивов для асинхронной работы:

**Современные (рекомендуемые):**
- **[[c-coroutines|Корутины]]** — легковесная конкурентность с lifecycle-aware отменой
- **Flow** — реактивные потоки данных (cold streams + hot StateFlow/SharedFlow)
- **[[c-workmanager|WorkManager]]** — гарантированное выполнение задач, переживающих смерть процесса

**Legacy (устаревшие):**
- **Handler/Looper** — низкоуровневая передача сообщений между потоками
- **ExecutorService** — Java thread pool без интеграции с Android lifecycle
- **RxJava** — функциональное реактивное программирование (требует дисциплины управления подписками)
- **AsyncTask** — DEPRECATED, утечки памяти при rotation

### 1. Kotlin Coroutines (основной выбор)

```kotlin
class DataViewModel : ViewModel() {
    // ✅ Базовое использование: viewModelScope автоматически отменяется при onCleared()
    fun loadData() {
        viewModelScope.launch {
            val data = withContext(Dispatchers.IO) {
                repository.fetchData() // сеть/БД всегда на IO
            }
            _uiState.value = UiState.Success(data) // обновление UI на Main
        }
    }

    // ✅ Параллельные операции: async для конкурентного выполнения
    fun loadMultiple() {
        viewModelScope.launch {
            val result1 = async(Dispatchers.IO) { fetchFromApi1() }
            val result2 = async(Dispatchers.IO) { fetchFromApi2() }
            _data.value = result1.await() + result2.await() // ждём оба результата
        }
    }

    // ❌ WRONG: blocking Main thread
    fun loadDataWrong() {
        viewModelScope.launch { // launch без withContext
            val data = repository.fetchData() // блокирует Main!
            _uiState.value = UiState.Success(data)
        }
    }
}
```

### 2. Flow (реактивные потоки)

```kotlin
// ✅ StateFlow: hot stream с последним значением + conflation
private val _users = MutableStateFlow<List<User>>(emptyList())
val users: StateFlow<List<User>> = _users.asStateFlow()

// ✅ Обработка потока с lifecycle-aware collection
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) { // останавливается при STOPPED
        repository.getUsers()
            .flowOn(Dispatchers.IO) // upstream на IO
            .collect { users ->
                adapter.submitList(users) // downstream на Main
            }
    }
}

// ❌ WRONG: collect без repeatOnLifecycle
lifecycleScope.launch {
    repository.getUsers().collect { /* утечка при background */ }
}
```

### 3. WorkManager (гарантированная Фоновая работа)

```kotlin
class DataSyncWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    // ✅ Переживает смерть процесса, перезагрузку устройства
    override suspend fun doWork(): Result = try {
        withContext(Dispatchers.IO) {
            syncData() // тяжёлая работа на IO
        }
        Result.success() // задача завершена, больше не будет перезапущена
    } catch (e: Exception) {
        if (runAttemptCount < 3) Result.retry() // exponential backoff
        else Result.failure() // после 3 попыток отказываемся
    }
}

// Планирование работы
val syncWork = PeriodicWorkRequestBuilder<DataSyncWorker>(1, TimeUnit.HOURS)
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED) // только при сети
            .setRequiresBatteryNotLow(true)
            .build()
    )
    .build()

WorkManager.getInstance(context).enqueueUniquePeriodicWork(
    "DataSync",
    ExistingPeriodicWorkPolicy.KEEP, // не дублируем задачи
    syncWork
)
```

**Выбор примитива:**
- **Корутины** — UI-связанные операции с коротким временем выполнения (API calls, DB queries)
- **Flow** — непрерывные потоки данных (sensors, DB observations, WebSocket)
- **WorkManager** — критичные задачи, которые должны выполниться даже после закрытия app (upload, sync)

---

## Answer (EN)

Android provides several async primitives:

**Modern (recommended):**
- **[[c-coroutines|Coroutines]]** — lightweight concurrency with lifecycle-aware cancellation
- **Flow** — reactive data streams (cold streams + hot StateFlow/SharedFlow)
- **[[c-workmanager|WorkManager]]** — guaranteed task execution surviving process death

**Legacy (outdated):**
- **Handler/Looper** — low-level message passing between threads
- **ExecutorService** — Java thread pool without Android lifecycle integration
- **RxJava** — functional reactive programming (requires disciplined subscription management)
- **AsyncTask** — DEPRECATED, memory leaks on rotation

### 1. Kotlin Coroutines (primary choice)

```kotlin
class DataViewModel : ViewModel() {
    // ✅ Basic usage: viewModelScope auto-cancels on onCleared()
    fun loadData() {
        viewModelScope.launch {
            val data = withContext(Dispatchers.IO) {
                repository.fetchData() // network/DB always on IO
            }
            _uiState.value = UiState.Success(data) // UI update on Main
        }
    }

    // ✅ Parallel operations: async for concurrent execution
    fun loadMultiple() {
        viewModelScope.launch {
            val result1 = async(Dispatchers.IO) { fetchFromApi1() }
            val result2 = async(Dispatchers.IO) { fetchFromApi2() }
            _data.value = result1.await() + result2.await() // wait for both
        }
    }

    // ❌ WRONG: blocking Main thread
    fun loadDataWrong() {
        viewModelScope.launch { // launch without withContext
            val data = repository.fetchData() // blocks Main!
            _uiState.value = UiState.Success(data)
        }
    }
}
```

### 2. Flow (reactive streams)

```kotlin
// ✅ StateFlow: hot stream with latest value + conflation
private val _users = MutableStateFlow<List<User>>(emptyList())
val users: StateFlow<List<User>> = _users.asStateFlow()

// ✅ Stream processing with lifecycle-aware collection
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) { // stops on STOPPED
        repository.getUsers()
            .flowOn(Dispatchers.IO) // upstream on IO
            .collect { users ->
                adapter.submitList(users) // downstream on Main
            }
    }
}

// ❌ WRONG: collect without repeatOnLifecycle
lifecycleScope.launch {
    repository.getUsers().collect { /* leaks on background */ }
}
```

### 3. WorkManager (guaranteed Background work)

```kotlin
class DataSyncWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    // ✅ Survives process death, device reboot
    override suspend fun doWork(): Result = try {
        withContext(Dispatchers.IO) {
            syncData() // heavy work on IO
        }
        Result.success() // task complete, won't restart
    } catch (e: Exception) {
        if (runAttemptCount < 3) Result.retry() // exponential backoff
        else Result.failure() // give up after 3 attempts
    }
}

// Scheduling work
val syncWork = PeriodicWorkRequestBuilder<DataSyncWorker>(1, TimeUnit.HOURS)
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED) // only with network
            .setRequiresBatteryNotLow(true)
            .build()
    )
    .build()

WorkManager.getInstance(context).enqueueUniquePeriodicWork(
    "DataSync",
    ExistingPeriodicWorkPolicy.KEEP, // don't duplicate tasks
    syncWork
)
```

**Choosing the right primitive:**
- **Coroutines** — UI-bound operations with short execution time (API calls, DB queries)
- **Flow** — continuous data streams (sensors, DB observations, WebSocket)
- **WorkManager** — critical tasks that must complete even after app closes (upload, sync)

---

## Follow-ups

- How does `viewModelScope` ensure automatic cancellation when ViewModel is cleared?
- What's the difference between `StateFlow` and `SharedFlow` in terms of buffering and replay?
- When would you prefer `ExecutorService` over coroutines despite the recommendation?
- How does WorkManager guarantee task execution across process death?
- What are the memory implications of using Handler with long-lived Activity references?
- Why is `AsyncTask` deprecated and what specific issues did it have with lifecycle management?
- How do coroutine dispatchers map to Android's threading model (Main, IO, Default)?

## References

- [[c-coroutines]] — Coroutines fundamentals
- [[c-workmanager]] — WorkManager architecture
- [Kotlin Coroutines on Android](https://developer.android.com/kotlin/coroutines)
- [Kotlin Flow Documentation](https://kotlinlang.org/docs/flow.html)
- [WorkManager Guide](https://developer.android.com/topic/libraries/architecture/workmanager)
- [Background Tasks Overview](https://developer.android.com/develop/background-work/background-tasks)

## Related Questions

### Prerequisites
- [[q-coroutine-builders-basics--kotlin--easy]] — Coroutines fundamentals
- [[q-viewmodel-pattern--android--easy]] — ViewModel pattern

### Related
- [[q-flow-operators--kotlin--medium]] — Flow operators
- [[q-what-is-workmanager--android--medium]] — WorkManager basics

### Advanced
- [[q-advanced-coroutine-patterns--kotlin--hard]] — Advanced coroutines
- [[q-workmanager-execution-guarantee--android--medium]] — WorkManager guarantees