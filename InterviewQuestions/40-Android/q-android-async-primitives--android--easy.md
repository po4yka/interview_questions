---
id: android-143
title: Android Async Primitives / Примитивы асинхронности Android
aliases: [Android Async Primitives, Примитивы асинхронности Android]
topic: android
subtopics: [coroutines, threads-sync]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-coroutines, q-async-operations-android--android--medium, q-coroutine-builders-basics--kotlin--easy, q-how-to-start-drawing-ui-in-android--android--easy, q-viewmodel-pattern--android--easy, q-what-to-do-in-android-project-to-start-drawing-ui-on-screen--android--easy]
sources: []
created: 2025-10-15
updated: 2025-11-10
tags: [android/coroutines, android/threads-sync, difficulty/easy]

---
# Вопрос (RU)
> Какие примитивы асинхронности предоставляет Android?

---

# Question (EN)
> What are Android Async Primitives?

---

## Ответ (RU)

Android предоставляет несколько уровней примитивов для асинхронной работы:

**Современные (рекомендуемые, более высокоуровневые):**
- **[[c-coroutines|Корутины]]** — легковесная конкурентность с lifecycle-aware отменой
- **`Flow`** — реактивные потоки данных (cold streams + hot `StateFlow`/`SharedFlow`) поверх корутин
- **WorkManager** — надёжное планирование фоновых задач, переживающих смерть процесса (best effort при соблюдении ограничений)

**Базовые/Legacy (низкоуровневые или устаревшие):**
- **Thread / HandlerThread / Handler/Looper** — низкоуровневая работа с потоками и передача сообщений между ними (включая основной поток)
- **ExecutorService** — Java thread pool без интеграции с Android lifecycle
- **RxJava** — функциональное реактивное программирование (требует дисциплины управления подписками и ручной привязки к lifecycle)
- **AsyncTask** — DEPRECATED из-за проблем с lifecycle, управлением потоками, предсказуемостью очередности и частыми утечками памяти при неправильном использовании

### 1. Kotlin Coroutines (основной выбор)

```kotlin
class DataViewModel : ViewModel() {
    // ✅ Базовое использование: viewModelScope автоматически отменяется при onCleared()
    fun loadData() {
        viewModelScope.launch {
            val data = withContext(Dispatchers.IO) {
                repository.fetchData() // сеть/БД рекомендуется выполнять на IO (если вызов блокирующий)
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

    // ❌ WRONG: потенциальная блокировка Main thread
    fun loadDataWrong() {
        viewModelScope.launch { // запуск на Dispatchers.Main по умолчанию
            val data = repository.fetchData() // если метод блокирующий, он будет блокировать Main!
            _uiState.value = UiState.Success(data)
        }
    }
}
```

### 2. `Flow` (реактивные потоки)

```kotlin
// ✅ StateFlow: hot stream с последним значением + conflation
private val _users = MutableStateFlow<List<User>>(emptyList())
val users: StateFlow<List<User>> = _users.asStateFlow()

// ✅ Обработка потока с lifecycle-aware collection
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) { // коллекция при STARTED+, автоматическая отмена при STOPPED
        repository.getUsers()
            .flowOn(Dispatchers.IO) // upstream на IO
            .collect { users ->
                adapter.submitList(users) // downstream на Main
            }
    }
}

// ❌ WRONG: collect без repeatOnLifecycle (нет привязки к жизненному циклу, риск утечек/лишней работы)
lifecycleScope.launch {
    repository.getUsers().collect { /* может продолжать работу, когда UI неактивен */ }
}
```

### 3. WorkManager (фоновые Задачи С Устойчивым планированием)

```kotlin
class DataSyncWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    // ✅ Может быть повторно запущен системой после смерти процесса/перезагрузки при выполнении условий
    override suspend fun doWork(): Result = try {
        withContext(Dispatchers.IO) {
            syncData() // тяжёлая работа на IO
        }
        Result.success() // задача успешно завершена
    } catch (e: Exception) {
        if (runAttemptCount < 3) Result.retry() // можно настроить backoff policy
        else Result.failure() // после 3 попыток отказываемся
    }
}

// Планирование работы
val syncWork = PeriodicWorkRequestBuilder<DataSyncWorker>(1, TimeUnit.HOURS)
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED) // только при наличии сети
            .setRequiresBatteryNotLow(true)
            .build()
    )
    .build()

WorkManager.getInstance(context).enqueueUniquePeriodicWork(
    "DataSync",
    ExistingPeriodicWorkPolicy.KEEP, // не дублируем периодические задачи
    syncWork
)
```

**Выбор примитива:**
- **Корутины** — UI-связанные операции с коротким или контролируемым временем выполнения (API calls, DB queries, параллельные запросы)
- **`Flow`** — непрерывные/подписочные потоки данных (sensors, DB observations, WebSocket)
- **WorkManager** — критичные задачи, которые должны быть надежно запланированы и выполниться даже после закрытия app/смерти процесса (upload, sync) при соблюдении системных ограничений
- **Handler/Executor/Thread** — низкоуровневый контроль потоков и очередей, когда нужна тонкая настройка

---

## Answer (EN)

Android provides several levels of async primitives:

**Modern (recommended, higher-level):**
- **[[c-coroutines|Coroutines]]** — lightweight concurrency with lifecycle-aware cancellation
- **`Flow`** — reactive data streams (cold streams + hot `StateFlow`/`SharedFlow`) built on top of coroutines
- **WorkManager** — robust scheduling for background tasks that can survive process death (best-effort under given constraints)

**Low-level/Legacy (basic or outdated):**
- **Thread / HandlerThread / Handler/Looper** — low-level threading and message passing (including the main thread)
- **ExecutorService** — Java thread pool without built-in Android lifecycle integration
- **RxJava** — functional reactive programming (requires disciplined subscription management and manual lifecycle handling)
- **AsyncTask** — DEPRECATED due to lifecycle issues, threading behavior, ordering guarantees, and common memory leaks when misused

### 1. Kotlin Coroutines (primary choice)

```kotlin
class DataViewModel : ViewModel() {
    // ✅ Basic usage: viewModelScope auto-cancels on onCleared()
    fun loadData() {
        viewModelScope.launch {
            val data = withContext(Dispatchers.IO) {
                repository.fetchData() // network/DB should be on IO if the call is blocking
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

    // ❌ WRONG: potential Main thread blocking
    fun loadDataWrong() {
        viewModelScope.launch { // runs on Dispatchers.Main by default
            val data = repository.fetchData() // if blocking, this will block Main!
            _uiState.value = UiState.Success(data)
        }
    }
}
```

### 2. `Flow` (reactive streams)

```kotlin
// ✅ StateFlow: hot stream with latest value + conflation
private val _users = MutableStateFlow<List<User>>(emptyList())
val users: StateFlow<List<User>> = _users.asStateFlow()

// ✅ Stream processing with lifecycle-aware collection
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) { // collect when STARTED+, automatically cancelled on STOPPED
        repository.getUsers()
            .flowOn(Dispatchers.IO) // upstream on IO
            .collect { users ->
                adapter.submitList(users) // downstream on Main
            }
    }
}

// ❌ WRONG: collect without repeatOnLifecycle (no lifecycle awareness, risk of leaks/unnecessary work)
lifecycleScope.launch {
    repository.getUsers().collect { /* may keep collecting when UI is not visible */ }
}
```

### 3. WorkManager (background Work with Resilient scheduling)

```kotlin
class DataSyncWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    // ✅ Can be rescheduled by the system after process death/reboot when constraints are met
    override suspend fun doWork(): Result = try {
        withContext(Dispatchers.IO) {
            syncData() // heavy work on IO
        }
        Result.success() // task completed successfully
    } catch (e: Exception) {
        if (runAttemptCount < 3) Result.retry() // backoff policy can be configured
        else Result.failure() // give up after 3 attempts
    }
}

// Scheduling work
val syncWork = PeriodicWorkRequestBuilder<DataSyncWorker>(1, TimeUnit.HOURS)
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED) // only when network is available
            .setRequiresBatteryNotLow(true)
            .build()
    )
    .build()

WorkManager.getInstance(context).enqueueUniquePeriodicWork(
    "DataSync",
    ExistingPeriodicWorkPolicy.KEEP, // don't duplicate periodic tasks
    syncWork
)
```

**Choosing the right primitive:**
- **Coroutines** — UI-bound operations with short or controlled execution time (API calls, DB queries, parallel calls)
- **`Flow`** — continuous/subscribed data streams (sensors, DB observations, WebSocket)
- **WorkManager** — critical tasks that must be reliably scheduled and run even after app closure/process death (upload, sync) under system constraints
- **Handler/Executor/Thread** — low-level control of threads and queues when fine-grained behavior is needed

---

## Дополнительные Вопросы (RU)

- Как `viewModelScope` обеспечивает автоматическую отмену при очистке `ViewModel`?
- В чем разница между `StateFlow` и `SharedFlow` с точки зрения буферизации и `replay`?
- В каких случаях вы предпочтете `ExecutorService` вместо корутин, несмотря на рекомендации?
- Как WorkManager сохраняет и переназначает задачи при смерти процесса и перезагрузке устройства?
- Каковы последствия для памяти при использовании `Handler` с долгоживущими ссылками на `Activity`?
- Почему `AsyncTask` устарел и какие конкретные проблемы у него были с lifecycle и потоками?
- Как диспетчеры корутин отображаются на модель потоков Android (Main, IO, Default)?

## Follow-ups

- How does `viewModelScope` ensure automatic cancellation when `ViewModel` is cleared?
- What's the difference between `StateFlow` and `SharedFlow` in terms of buffering and replay?
- When would you prefer `ExecutorService` over coroutines despite the recommendation?
- How does WorkManager persist and reschedule work across process death and device reboot?
- What are the memory implications of using Handler with long-lived `Activity` references?
- Why is `AsyncTask` deprecated and what specific issues did it have with lifecycle management and threading?
- How do coroutine dispatchers map to Android's threading model (Main, IO, Default)?

## Ссылки (RU)

- [[c-coroutines]] — основы корутин
- Руководство по корутинам Kotlin на Android: https://developer.android.com/kotlin/coroutines
- Документация по `Flow`: https://kotlinlang.org/docs/flow.html
- Руководство по WorkManager: https://developer.android.com/topic/libraries/architecture/workmanager
- Обзор фоновых задач: https://developer.android.com/develop/background-work/background-tasks

## References

- [[c-coroutines]] — Coroutines fundamentals
- [Kotlin Coroutines on Android](https://developer.android.com/kotlin/coroutines)
- [Kotlin `Flow` Documentation](https://kotlinlang.org/docs/flow.html)
- [WorkManager Guide](https://developer.android.com/topic/libraries/architecture/workmanager)
- [Background Tasks Overview](https://developer.android.com/develop/background-work/background-tasks)

## Связанные Вопросы (RU)

### Предусловия
- [[q-coroutine-builders-basics--kotlin--easy]] — основы корутин
- [[q-viewmodel-pattern--android--easy]] — паттерн `ViewModel`

### Связанные
- [[q-flow-operators--kotlin--medium]] — операторы `Flow`
- [[q-what-is-workmanager--android--medium]] — основы WorkManager

### Продвинутые
- [[q-advanced-coroutine-patterns--kotlin--hard]] — продвинутые паттерны корутин
- [[q-workmanager-execution-guarantee--android--medium]] — гарантии выполнения WorkManager

## Related Questions

### Prerequisites
- [[q-coroutine-builders-basics--kotlin--easy]] — Coroutines fundamentals
- [[q-viewmodel-pattern--android--easy]] — `ViewModel` pattern

### Related
- [[q-flow-operators--kotlin--medium]] — `Flow` operators
- [[q-what-is-workmanager--android--medium]] — WorkManager basics

### Advanced
- [[q-advanced-coroutine-patterns--kotlin--hard]] — Advanced coroutines
- [[q-workmanager-execution-guarantee--android--medium]] — WorkManager guarantees
