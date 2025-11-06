---
id: android-190
title: Async Operations in Android / Асинхронные операции в Android
aliases: [Async Operations in Android, Асинхронные операции в Android]
topic: android
subtopics:
  - background-execution
  - coroutines
  - threads-sync
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - c-coroutines
  - c-lifecycle
  - q-android-async-primitives--android--easy
created: 2025-10-15
updated: 2025-10-30
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

Главный поток — только для UI, остальное — в фон. Выбор зависит от задачи: корутины (по умолчанию), WorkManager (отложенные задачи), Executor/HandlerThread (легаси), RxJava (реактивность).

### Kotlin Coroutines — Выбор По Умолчанию

Структурированная конкурентность с автоматической отменой через lifecycle-scopes.

**Ключевые концепции**:
- Parent/child связь — отмена распространяется автоматически
- `withContext()` для переключения диспетчеров
- `lifecycleScope`/`viewModelScope` вместо `GlobalScope`
- `coroutineScope` (fail-fast) vs `supervisorScope` (изоляция)

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

### WorkManager — Гарантированное Выполнение

Переживает перезапуск, поддерживает constraints (сеть, батарея), цепочки задач.

**Когда использовать**:
- Deferrable задачи (синхронизация, загрузка)
- Требуется гарантия выполнения
- Нужны constraints (WiFi, зарядка)

```kotlin
class UploadWorker(ctx: Context, p: WorkerParameters):
  CoroutineWorker(ctx, p) {

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
  ).build()
```

**Важно**: Worker должен быть идемпотентным — может запуститься повторно.

### ExecutorService — Java Interop

`Thread` pools с ручным управлением, используется в легаси коде.

```kotlin
val executor = Executors.newFixedThreadPool(2)
val mainHandler = Handler(Looper.getMainLooper())

executor.execute {
  val result = computeData()
  mainHandler.post { updateUI(result) } // ✅ UI update на main
}
// ⚠️ Обязательно: executor.shutdown() в onDestroy
```

### HandlerThread — `Message` `Queue`

Один фоновый `Looper` для последовательной обработки.

```kotlin
val handlerThread = HandlerThread("bg").apply { start() }
val bgHandler = Handler(handlerThread.looper)

bgHandler.post {
  processData()
}
// Cleanup: handlerThread.quitSafely()
```

### RxJava — Reactive Streams

Используйте если проект стандартизирован на Rx, иначе корутины.

```kotlin
val disposables = CompositeDisposable()

disposables.add(
  repository.getUser()
    .subscribeOn(Schedulers.io())
    .observeOn(AndroidSchedulers.mainThread())
    .subscribe(
      { user -> render(user) }, // ✅ onNext
      { error -> showError(error) } // ✅ onError
    )
)
// В onDestroy: disposables.clear()
```

**Сравнение**

| Инструмент | Применение |
|------------|-----------|
| Coroutines | In-process задачи, UI updates, network |
| WorkManager | Deferrable work, переживает process death |
| Executor | Java interop, legacy код |
| HandlerThread | Sequential processing |
| RxJava | Reactive streams, существующая Rx база |

**Распространённые ошибки**:
- Обновление UI вне main thread
- Не отменена работа при lifecycle events
- WorkManager для точного времени (используйте AlarmManager)
- Утечка threads/executors — не вызван shutdown

---

## Answer (EN)

Main thread for UI only, offload everything else to background. Choice depends on use case: coroutines (default), WorkManager (deferrable work), Executor/HandlerThread (legacy), RxJava (reactive).

### Kotlin Coroutines — Default Choice

Structured concurrency with automatic cancellation via lifecycle-scopes.

**Key Concepts**:
- Parent/child relationship — cancellation propagates automatically
- `withContext()` for dispatcher switching
- `lifecycleScope`/`viewModelScope` instead of `GlobalScope`
- `coroutineScope` (fail-fast) vs `supervisorScope` (isolation)

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

### WorkManager — Guaranteed Execution

Survives app restarts, supports constraints (network, battery), task chaining.

**When to Use**:
- Deferrable tasks (sync, upload)
- Requires execution guarantee
- Needs constraints (WiFi, charging)

```kotlin
class UploadWorker(ctx: Context, p: WorkerParameters):
  CoroutineWorker(ctx, p) {

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
  ).build()
```

**Important**: Worker must be idempotent — may run multiple times.

### ExecutorService — Java Interop

`Thread` pools with manual management, used in legacy code.

```kotlin
val executor = Executors.newFixedThreadPool(2)
val mainHandler = Handler(Looper.getMainLooper())

executor.execute {
  val result = computeData()
  mainHandler.post { updateUI(result) } // ✅ UI update on main
}
// ⚠️ Required: executor.shutdown() in onDestroy
```

### HandlerThread — `Message` `Queue`

Single background `Looper` for sequential processing.

```kotlin
val handlerThread = HandlerThread("bg").apply { start() }
val bgHandler = Handler(handlerThread.looper)

bgHandler.post {
  processData()
}
// Cleanup: handlerThread.quitSafely()
```

### RxJava — Reactive Streams

Use if project is standardized on Rx, otherwise prefer coroutines.

```kotlin
val disposables = CompositeDisposable()

disposables.add(
  repository.getUser()
    .subscribeOn(Schedulers.io())
    .observeOn(AndroidSchedulers.mainThread())
    .subscribe(
      { user -> render(user) }, // ✅ onNext
      { error -> showError(error) } // ✅ onError
    )
)
// In onDestroy: disposables.clear()
```

**Comparison**

| Tool | When to Use |
|------|------------|
| Coroutines | In-process tasks, UI updates, network |
| WorkManager | Deferrable work, survives process death |
| Executor | Java interop, legacy code |
| HandlerThread | Sequential processing |
| RxJava | Reactive streams, existing Rx codebase |

**Common Pitfalls**:
- Updating UI off main thread
- Forgetting to cancel work on lifecycle events
- WorkManager for exact timing (use AlarmManager)
- Leaking threads/executors — missing shutdown

---

## Follow-ups

- How do you choose between WorkManager and ForegroundService for long-running tasks?
- What are the trade-offs between different Dispatcher types in coroutines?
- How do you handle cancellation propagation across multiple repository/domain layers?
- When should you use `async/await` vs `withContext` in coroutines?
- How do you test coroutine-based async code with TestDispatchers?

## References

- [[c-coroutines]]
- [[c-lifecycle]]
- [[c-structured-concurrency]]
- [Kotlin Coroutines](https://developer.android.com/kotlin/coroutines)
- [WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager)


## Related Questions

### Prerequisites (Easier)
- [[q-android-async-primitives--android--easy]]


### Related (Same Level)
- [[q-anr-application-not-responding--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]


### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]]
