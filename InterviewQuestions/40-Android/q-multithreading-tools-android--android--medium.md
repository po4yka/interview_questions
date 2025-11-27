---
id: android-275
title: "Multithreading Tools Android / Инструменты многопоточности Android"
aliases: [Android Threading, Multithreading Tools Android, Инструменты многопоточности Android, Многопоточность Android]
topic: android
subtopics: [background-execution, coroutines, performance-startup]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-coroutines, q-android-async-primitives--android--easy]
created: 2024-10-15
updated: 2025-11-10
sources: ["https://developer.android.com/kotlin/coroutines", "https://developer.android.com/topic/libraries/architecture/workmanager"]
tags: [android/background-execution, android/coroutines, android/performance-startup, concurrency, difficulty/medium, rxjava, workmanager]
date created: Saturday, November 1st 2025, 1:25:23 pm
date modified: Tuesday, November 25th 2025, 8:53:58 pm
---
# Вопрос (RU)

> Какие инструменты для многопоточности в Android вы знаете?

# Question (EN)

> What tools for multithreading in Android do you know?

## Ответ (RU)

Android предоставляет несколько инструментов для многопоточности и асинхронных операций. Важно различать:
- низкоуровневые примитивы (потоки, `Handler`/`Looper`, `Executor`),
- высокоуровневые абстракции (Kotlin Coroutines, RxJava),
- планировщики фоновой работы (`WorkManager`).

### 1. Kotlin Coroutines (Рекомендуется)

**Корутина** — высокоуровневый паттерн для асинхронности и конкурентности, который работает поверх обычных потоков и диспетчеров и упрощает работу с многопоточностью.

**Ключевые преимущества:**
- **Легковесные** — тысячи корутин могут выполняться поверх ограниченного пула потоков благодаря приостановке вместо блокировки
- **Структурированная конкурентность** — иерархия задач и областей видимости, меньше утечек и «заброшенных» задач
- **Автоматическая отмена** — распространяется через иерархию корутин
- **Интеграция Jetpack** — полная поддержка в архитектурных библиотеках

**✅ Базовый пример:**

```kotlin
class MyViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState

    fun fetchData() {
        viewModelScope.launch {
            try {
                val data = withContext(Dispatchers.IO) {
                    repository.fetchData()
                }
                _uiState.value = UiState.Success(data)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e)
            }
        }
    }
}
```

**Диспетчеры:**
- `Dispatchers.Main` — UI поток
- `Dispatchers.IO` — I/O операции (сеть, БД, файлы)
- `Dispatchers.Default` — CPU-интенсивные вычисления

**✅ Структурированная конкурентность:**

```kotlin
suspend fun load(): Result {
    return coroutineScope {
        val data1 = async(Dispatchers.IO) { fetchData1() }
        val data2 = async(Dispatchers.IO) { fetchData2() }
        process(data1.await(), data2.await())
    }
}
```

**Области видимости:**
- `viewModelScope` — привязан к жизненному циклу `ViewModel`
- `lifecycleScope` — привязан к `Activity`/`Fragment`
- `GlobalScope` — уровень приложения (использовать с осторожностью)

**✅ `Flow` для потоков данных:**

```kotlin
fun fetchUpdates(): Flow<Update> = flow {
    while (true) {
        emit(api.getUpdate())
        delay(1000)
    }
}

viewModelScope.launch {
    fetchUpdates()
        .flowOn(Dispatchers.IO)
        .collect { updateUI(it) }
}
```

### 2. Базовые Android-примитивы: Thread, Handler/Looper, Executor

Для понимания многопоточности в Android важно знать основные примитивы платформы:

- `Thread` — низкоуровневое создание отдельных потоков выполнения (обычно не рекомендуется вручную для массовых задач из-за сложности и издержек).
- `Handler` + `Looper` — механизм обработки очереди сообщений/задач в конкретном потоке (например, главный поток с `Looper.getMainLooper()`), позволяет безопасно передавать работу между потоками.
- `HandlerThread` — поток с собственным `Looper` для последовательной обработки задач в фоне.
- `Executor` / `ThreadPoolExecutor` — пул потоков и очередь задач; фактически стандартная база для многопоточного выполнения, поверх которой строятся многие высокоуровневые решения.

В современной разработке чаще используются корутины и `WorkManager`, но они концептуально опираются на эти примитивы.

### 3. WorkManager

API для планирования **отложенных и долговременных фоновых задач**, которые должны быть выполнены даже после закрытия приложения.

**Ключевые особенности:**
- **Надёжное (best-effort) выполнение** — задачи сохраняются и `WorkManager` старается выполнить их даже при убийстве приложения/перезагрузке устройства, с учётом ограничений ОС
- **Ограничения** — запуск только при выполнении условий (сеть, заряд, батарея, хранилище)
- **Обратная совместимость** — поддержка до API level 14
- **Экономия батареи** — учитывает Doze и App Standby, использует подходящие механизмы (`AlarmManager`, `JobScheduler` и др.)

**✅ Пример:**

```kotlin
class UploadWorker(context: Context, params: WorkerParameters) : Worker(context, params) {
    override fun doWork(): Result {
        uploadData()
        return Result.success()
    }
}

val uploadRequest = OneTimeWorkRequestBuilder<UploadWorker>()
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .setRequiresBatteryNotLow(true)
            .build()
    )
    .build()

WorkManager.getInstance(context).enqueue(uploadRequest)
```

**Когда использовать:**
- Задачи должны выполняться даже при закрытом приложении ("best-effort" гарантия с учётом политики ОС)
- Нужны ограничения (сеть, зарядка, батарея)
- Периодические задачи (синхронизация, бэкап)

Не подходит для низкой задержки или тесно связанных с UI операций — для них лучше корутины/`Executor`.

### 4. RxJava / RxAndroid

Reactive Extensions для JVM — композиция асинхронных программ через наблюдаемые последовательности.

**✅ Пример с переключением потоков:**

```kotlin
Observable.fromCallable { fetchDataFromNetwork() }
    .subscribeOn(Schedulers.io())
    .observeOn(AndroidSchedulers.mainThread())
    .subscribe(
        { result -> updateUI(result) },
        { error -> showError(error) }
    )
```

**Основные планировщики:**
- `Schedulers.io()` — I/O операции
- `Schedulers.computation()` — CPU-интенсивные вычисления
- `AndroidSchedulers.mainThread()` — UI поток

**Преимущества:**
- Мощные операторы для трансформации данных
- Лёгкое переключение потоков
- Подходит для сложных реактивных/событийных потоков

**❌ Недостатки:**
- Крутая кривая обучения
- Размер и сложность экосистемы
- В новых проектах постепенно заменяется Kotlin Coroutines/`Flow`

### 5. AsyncTask (❌ Устарел)

`AsyncTask` был предназначен для фоновой работы с результатом в UI, но **deprecated** и не должен использоваться.

**Почему устарел:**
- Утечки `Context`, пропущенные коллбэки, проблемы при изменении конфигурации
- Несогласованное поведение на разных версиях Android
- Поглощает исключения из `doInBackground`

**Альтернатива:** Kotlin Coroutines, `Executor`/`ThreadPoolExecutor`, `WorkManager` (для отложенных задач)

### Сравнительная Таблица

| Инструмент | Статус | Лучше всего для | Сложность |
|------------|--------|-----------------|-----------|
| **Kotlin Coroutines** | ✅ Рекомендуется | Общие async/await, современная разработка, UI + I/O | Низкая-Средняя |
| **WorkManager** | ✅ Рекомендуется | Отложенная/гарантируемая (best-effort) фоновая работа с ограничениями | Средняя |
| **RxJava** | Зрелый | Сложные реактивные потоки событий | Высокая |
| **AsyncTask** | ❌ Устарел | Ничего (используйте альтернативы) | Низкая |

### Современные Рекомендации

Для новой разработки Android:
1. **Kotlin Coroutines** — для асинхронных операций, сетевых вызовов, доступа к БД, работы с UI
2. **WorkManager** — для отложенных фоновых задач с учётом ограничений и best-effort гарантий выполнения
3. **RxJava** — только при существующей Rx-кодовой базе или специфических реактивных требованиях
4. **Базовые примитивы (`Executor`, `HandlerThread`)** — когда нужен точный контроль над потоками/очередями
5. **❌ `AsyncTask`** — не использовать (устарел)

## Answer (EN)

Android provides several tools for multithreading and asynchronous operations. It is important to distinguish:
- low-level primitives (threads, `Handler`/`Looper`, `Executor`),
- high-level abstractions (Kotlin Coroutines, RxJava),
- background work schedulers (`WorkManager`).

### 1. Kotlin Coroutines (Recommended)

A **coroutine** is a high-level pattern for asynchrony and concurrency that runs on top of regular threads/dispatchers and simplifies working with multithreading.

**Key Benefits:**
- **Lightweight** — thousands of coroutines can be multiplexed over a limited thread pool via suspension instead of blocking
- **Structured concurrency** — scoped hierarchies of tasks, fewer leaks and "forgotten" jobs
- **Built-in cancellation** — automatically propagates through the coroutine hierarchy
- **Jetpack integration** — first-class support across architecture libraries

**✅ Basic Example:**

```kotlin
class MyViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState

    fun fetchData() {
        viewModelScope.launch {
            try {
                val data = withContext(Dispatchers.IO) {
                    repository.fetchData()
                }
                _uiState.value = UiState.Success(data)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e)
            }
        }
    }
}
```

**Dispatchers:**
- `Dispatchers.Main` — UI thread
- `Dispatchers.IO` — I/O operations (network, database, files)
- `Dispatchers.Default` — CPU-intensive work

**✅ Structured Concurrency:**

```kotlin
suspend fun load(): Result {
    return coroutineScope {
        val data1 = async(Dispatchers.IO) { fetchData1() }
        val data2 = async(Dispatchers.IO) { fetchData2() }
        process(data1.await(), data2.await())
    }
}
```

**Coroutine scopes:**
- `viewModelScope` — tied to `ViewModel` lifecycle
- `lifecycleScope` — tied to `Activity`/`Fragment` lifecycle
- `GlobalScope` — application-level scope (use carefully)

**✅ `Flow` for streams:**

```kotlin
fun fetchUpdates(): Flow<Update> = flow {
    while (true) {
        emit(api.getUpdate())
        delay(1000)
    }
}

viewModelScope.launch {
    fetchUpdates()
        .flowOn(Dispatchers.IO)
        .collect { updateUI(it) }
}
```

### 2. Core Android Primitives: Thread, Handler/Looper, Executor

To reason about multithreading on Android, you should know the platform primitives:

- `Thread` — low-level creation of separate execution threads (usually not preferred for large-scale use due to overhead and lifecycle complexity).
- `Handler` + `Looper` — message/queue processing in a specific thread (e.g., main thread via `Looper.getMainLooper()`), used to post work safely across threads.
- `HandlerThread` — a background thread with its own `Looper` for sequential background processing.
- `Executor` / `ThreadPoolExecutor` — thread pools and task queues; the standard base for parallel execution that many higher-level tools build upon.

Modern apps typically favor coroutines and `WorkManager`, but these abstractions conceptually rely on these primitives.

### 3. WorkManager

API for scheduling **deferrable and long-running background tasks** that should be executed even if the app exits.

**Key Features:**
- **Reliable (best-effort) execution** — work is persisted and `WorkManager` attempts to run it even after app kill/device reboot, subject to OS policies and constraints
- **Constraint-based** — run only when conditions are met (network, charging, battery, storage)
- **Backward compatibility** — supports back to API level 14
- **Battery-conscious** — respects Doze/App Standby and uses appropriate system facilities (e.g., `JobScheduler`, `AlarmManager`)

**✅ Example:**

```kotlin
class UploadWorker(context: Context, params: WorkerParameters) : Worker(context, params) {
    override fun doWork(): Result {
        uploadData()
        return Result.success()
    }
}

val uploadRequest = OneTimeWorkRequestBuilder<UploadWorker>()
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .setRequiresBatteryNotLow(true)
            .build()
    )
    .build()

WorkManager.getInstance(context).enqueue(uploadRequest)
```

**When to Use:**
- Tasks should run even if the app is closed (with best-effort guarantees under OS constraints)
- You need constraints (network, charging, battery)
- Periodic tasks (sync, backup)

Not suitable for low-latency or tightly UI-coupled operations — use coroutines/`Executor` instead.

### 4. RxJava / RxAndroid

Reactive Extensions for the JVM — composing asynchronous programs via observable sequences.

**✅ Thread Switching Example:**

```kotlin
Observable.fromCallable { fetchDataFromNetwork() }
    .subscribeOn(Schedulers.io())
    .observeOn(AndroidSchedulers.mainThread())
    .subscribe(
        { result -> updateUI(result) },
        { error -> showError(error) }
    )
```

**Common Schedulers:**
- `Schedulers.io()` — I/O operations
- `Schedulers.computation()` — CPU-intensive computations
- `AndroidSchedulers.mainThread()` — Android UI thread

**Advantages:**
- Powerful operators for data transformation and composition
- Easy thread switching
- Great for complex reactive/event-based flows

**❌ Disadvantages:**
- Steep learning curve
- Larger ecosystem and complexity
- In modern greenfield projects often replaced by Kotlin Coroutines/`Flow`

### 5. AsyncTask (❌ Deprecated)

`AsyncTask` was designed for simple background work with UI callbacks but is **deprecated** and should not be used.

**Why Deprecated:**
- `Context` leaks, missed callbacks, configuration change issues
- Inconsistent behavior across Android versions
- Swallows exceptions from `doInBackground`

**Alternatives:** Kotlin Coroutines, `Executor`/`ThreadPoolExecutor`, `WorkManager` (for deferrable work)

### Comparison Summary

| Tool | Status | Best For | Complexity |
|------|--------|----------|------------|
| **Kotlin Coroutines** | ✅ Recommended | General async/await, modern Android (UI + I/O) | Low-Medium |
| **WorkManager** | ✅ Recommended | Deferrable/background work with constraints; best-effort guaranteed | Medium |
| **RxJava** | Mature | Complex reactive event streams | High |
| **AsyncTask** | ❌ Deprecated | Nothing (use alternatives) | Low |

### Modern Recommendations

For new Android development:
1. **Kotlin Coroutines** — for async operations, network calls, DB access, and coordinating with UI
2. **WorkManager** — for deferrable background tasks with constraints and persisted/best-effort execution
3. **RxJava** — only if you have an existing Rx-based codebase or strong reactive requirements
4. **Core primitives (`Executor`, `HandlerThread`)** — when you need fine-grained control over threads/queues
5. **❌ `AsyncTask`** — never use (deprecated)

## Дополнительные Вопросы (RU)

- Как структурированная конкурентность в корутинах помогает избежать утечек памяти?
- Когда стоит выбрать `WorkManager` вместо фонового `Service`?
- В чем различия между `flowOn()` и `withContext()` в корутинах?
- Как обрабатывать backpressure в RxJava по сравнению с `Flow`?
- Что происходит с запущенными корутинами при очистке `ViewModel`?

## Follow-ups

- How does structured concurrency prevent memory leaks in coroutines?
- When should you choose `WorkManager` over a background `Service`?
- What are the differences between `flowOn()` and `withContext()` in coroutines?
- How do you handle backpressure in RxJava vs `Flow`?
- What happens to running coroutines when a `ViewModel` is cleared?

## References

- [[c-coroutines]]
- [[c-flow]]
- [Kotlin Coroutines on Android](https://developer.android.com/kotlin/coroutines)
- [WorkManager Guide](https://developer.android.com/topic/libraries/architecture/workmanager)

## Related Questions

### Prerequisites (Easier)
- [[q-android-async-primitives--android--easy]] - Basic async primitives in Android

### Related (Same Level)
- [[q-android-runtime-internals--android--hard]] - ART internals
