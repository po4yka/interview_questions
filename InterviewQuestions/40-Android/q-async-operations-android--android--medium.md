---
id: 20251012-122785
title: Async Operations in Android / Асинхронные операции в Android
aliases: [Async Operations in Android, Асинхронные операции в Android]
topic: android
subtopics: [background-execution, coroutines, threads-sync]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related:
  - q-android-async-primitives--android--easy
  - q-android-performance-measurement-tools--android--medium
  - q-anr-application-not-responding--android--medium
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [android/background-execution, android/coroutines, android/threads-sync, difficulty/medium]
---

# Вопрос (RU)
> Какие существуют способы выполнения асинхронных операций в Android?

---

# Question (EN)
> What are the ways to perform async operations in Android?

---

## Ответ (RU)

Основной принцип: главный поток только для UI, всю остальную работу — в фон. Выбор инструмента зависит от задачи: корутины (по умолчанию), WorkManager (отложенные задачи с гарантией выполнения), Executor/HandlerThread (легаси/интероп), RxJava (реактивность).

**Основные подходы**

### 1) Kotlin Coroutines — выбор по умолчанию

Структурированная конкурентность, lifecycle-scopes, автоматическая отмена.

**Ключевые концепции**:
- Parent/child связь: отмена и исключения распространяются автоматически
- `withContext(Dispatchers.IO)` для переключения потоков
- `lifecycleScope`/`viewModelScope` вместо `GlobalScope`
- `coroutineScope` — fail-fast, `supervisorScope` — изоляция ошибок
- Кооперативная отмена: проверяйте `isActive` в долгих циклах

```kotlin
// ✅ Правильно: lifecycle-aware scope
lifecycleScope.launch {
  val data = withContext(Dispatchers.IO) {
    repository.fetchData()
  }
  updateUI(data) // Main thread
}

// ❌ Неправильно: GlobalScope — утечка памяти
GlobalScope.launch { /* ... */ }
```

### 2) WorkManager — гарантированное выполнение

Сохраняется при перезапуске приложения, поддерживает constraints (сеть, батарея), цепочки задач.

**Ключевые концепции**:
- Используйте constraints для оптимизации батареи
- Идемпотентность обязательна — worker может запуститься несколько раз
- Unique work для предотвращения дублирования
- Не для точного времени или foreground задач

```kotlin
// ✅ Правильно: с constraints
class UploadWorker(ctx: Context, p: WorkerParameters): CoroutineWorker(ctx, p) {
  override suspend fun doWork(): Result {
    uploadFile()
    return Result.success()
  }
}

val request = OneTimeWorkRequestBuilder<UploadWorker>()
  .setConstraints(
    Constraints.Builder()
      .setRequiredNetworkType(NetworkType.CONNECTED)
      .build()
  )
  .build()
WorkManager.getInstance(context).enqueue(request)
```

### 3) ExecutorService — Java interop

Thread pools с ручным управлением жизненным циклом.

**Ключевые концепции**:
- Типы: `newFixedThreadPool`, `newCachedThreadPool`, `newSingleThreadExecutor`
- Всегда вызывайте `shutdown()` для предотвращения утечек
- Публикация результатов в main thread через Handler

```kotlin
// ✅ Правильно: с shutdown
val executor = Executors.newFixedThreadPool(2)
val mainHandler = Handler(Looper.getMainLooper())

executor.execute {
  val result = computeData()
  mainHandler.post { updateUI(result) }
}

// Не забудьте в onDestroy:
executor.shutdown()
```

### 4) HandlerThread — message queue поток

Один фоновый Looper для последовательной обработки сообщений.

**Ключевые концепции**:
- Looper + MessageQueue + Handler
- Подходит для sensor/IO pipelines где важен порядок
- `quitSafely()` для корректного завершения

```kotlin
val handlerThread = HandlerThread("bg-worker").apply { start() }
val bgHandler = Handler(handlerThread.looper)
val uiHandler = Handler(Looper.getMainLooper())

bgHandler.post {
  val result = processData()
  uiHandler.post { render(result) }
}

// Cleanup
handlerThread.quitSafely()
```

### 5) RxJava — reactive streams

Используйте если проект стандартизирован на Rx, иначе предпочитайте корутины.

**Ключевые концепции**:
- `subscribeOn` (upstream) и `observeOn` (downstream) для threading
- `CompositeDisposable` для управления lifecycle
- Cold vs hot observables, backpressure с Flowable

```kotlin
// ✅ Правильно: с lifecycle management
val disposables = CompositeDisposable()

disposables.add(
  repository.getUser()
    .subscribeOn(Schedulers.io())
    .observeOn(AndroidSchedulers.mainThread())
    .subscribe(
      { user -> render(user) },
      { error -> showError(error) }
    )
)

// В onDestroy/onCleared:
disposables.clear()
```

**Сравнение подходов**

| Инструмент | Когда использовать |
|------------|-------------------|
| Coroutines | In-process задачи, UI updates, network calls |
| WorkManager | Deferrable tasks, survives process death |
| Executor | Java interop, legacy code |
| HandlerThread | Sequential message processing |
| RxJava | Reactive streams, existing Rx codebase |

**Распространённые ошибки**:
- Обновление UI вне main thread → используйте Main dispatcher/Handlers
- Забыли отменить работу при lifecycle events → используйте lifecycle scopes
- WorkManager для точного времени → используйте AlarmManager
- Утечка threads/executors → shutdown в onDestroy/onCleared

---

## Answer (EN)

Core principle: main thread for UI only, offload everything else to background. Tool selection depends on use case: coroutines (default), WorkManager (deferrable guaranteed work), Executor/HandlerThread (legacy/interop), RxJava (reactive).

**Main Approaches**

### 1) Kotlin Coroutines — Default Choice

Structured concurrency, lifecycle-scopes, automatic cancellation.

**Key Concepts**:
- Parent/child relationship: cancellation and exceptions propagate automatically
- `withContext(Dispatchers.IO)` for thread switching
- `lifecycleScope`/`viewModelScope` instead of `GlobalScope`
- `coroutineScope` — fail-fast, `supervisorScope` — isolate failures
- Cooperative cancellation: check `isActive` in long loops

```kotlin
// ✅ Correct: lifecycle-aware scope
lifecycleScope.launch {
  val data = withContext(Dispatchers.IO) {
    repository.fetchData()
  }
  updateUI(data) // Main thread
}

// ❌ Wrong: GlobalScope — memory leak
GlobalScope.launch { /* ... */ }
```

### 2) WorkManager — Guaranteed Execution

Persists across app restarts, supports constraints (network, battery), task chaining.

**Key Concepts**:
- Use constraints to optimize battery
- Idempotency required — worker may run multiple times
- Unique work to prevent duplication
- Not for exact timing or foreground tasks

```kotlin
// ✅ Correct: with constraints
class UploadWorker(ctx: Context, p: WorkerParameters): CoroutineWorker(ctx, p) {
  override suspend fun doWork(): Result {
    uploadFile()
    return Result.success()
  }
}

val request = OneTimeWorkRequestBuilder<UploadWorker>()
  .setConstraints(
    Constraints.Builder()
      .setRequiredNetworkType(NetworkType.CONNECTED)
      .build()
  )
  .build()
WorkManager.getInstance(context).enqueue(request)
```

### 3) ExecutorService — Java Interop

Thread pools with manual lifecycle management.

**Key Concepts**:
- Types: `newFixedThreadPool`, `newCachedThreadPool`, `newSingleThreadExecutor`
- Always call `shutdown()` to prevent leaks
- Publish results to main thread via Handler

```kotlin
// ✅ Correct: with shutdown
val executor = Executors.newFixedThreadPool(2)
val mainHandler = Handler(Looper.getMainLooper())

executor.execute {
  val result = computeData()
  mainHandler.post { updateUI(result) }
}

// Don't forget in onDestroy:
executor.shutdown()
```

### 4) HandlerThread — Message Queue Thread

Single background Looper for sequential message processing.

**Key Concepts**:
- Looper + MessageQueue + Handler
- Good for sensor/IO pipelines where order matters
- `quitSafely()` for clean shutdown

```kotlin
val handlerThread = HandlerThread("bg-worker").apply { start() }
val bgHandler = Handler(handlerThread.looper)
val uiHandler = Handler(Looper.getMainLooper())

bgHandler.post {
  val result = processData()
  uiHandler.post { render(result) }
}

// Cleanup
handlerThread.quitSafely()
```

### 5) RxJava — Reactive Streams

Use if project is standardized on Rx, otherwise prefer coroutines.

**Key Concepts**:
- `subscribeOn` (upstream) and `observeOn` (downstream) for threading
- `CompositeDisposable` for lifecycle management
- Cold vs hot observables, backpressure with Flowable

```kotlin
// ✅ Correct: with lifecycle management
val disposables = CompositeDisposable()

disposables.add(
  repository.getUser()
    .subscribeOn(Schedulers.io())
    .observeOn(AndroidSchedulers.mainThread())
    .subscribe(
      { user -> render(user) },
      { error -> showError(error) }
    )
)

// In onDestroy/onCleared:
disposables.clear()
```

**Comparison**

| Tool | When to Use |
|------|------------|
| Coroutines | In-process tasks, UI updates, network calls |
| WorkManager | Deferrable tasks, survives process death |
| Executor | Java interop, legacy code |
| HandlerThread | Sequential message processing |
| RxJava | Reactive streams, existing Rx codebase |

**Common Pitfalls**:
- Updating UI off main thread → use Main dispatcher/Handlers
- Forgetting to cancel work on lifecycle events → use lifecycle scopes
- WorkManager for exact timing → use AlarmManager
- Leaking threads/executors → shutdown in onDestroy/onCleared

---

## Follow-ups

- How do you choose between WorkManager and ForegroundService for long-running tasks?
- What are the performance implications of different Dispatcher types in coroutines?
- How do you handle cancellation propagation across multiple layers?
- When should you use `async/await` vs `withContext` in coroutines?
- How do you implement backpressure in RxJava vs Flow?

## References

- [[c-coroutines]]
- [[c-workmanager]]
- [[c-lifecycle]]
- https://developer.android.com/topic/libraries/architecture/coroutines
- https://developer.android.com/topic/libraries/architecture/workmanager

## Related Questions

### Prerequisites (Easier)
- [[q-android-async-primitives--android--easy]]

### Related (Same Level)
- [[q-anr-application-not-responding--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]]
