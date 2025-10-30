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
updated: 2025-10-29
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

### 1) Kotlin Coroutines — выбор по умолчанию

Структурированная конкурентность, lifecycle-scopes, автоматическая отмена.

**Ключевые концепции**:
- Parent/child связь — отмена распространяется автоматически
- `withContext(Dispatchers.IO)` для переключения потоков
- `lifecycleScope`/`viewModelScope` вместо `GlobalScope`
- `coroutineScope` (fail-fast) vs `supervisorScope` (изоляция)

```kotlin
// ✅ Правильно: lifecycle-aware scope
lifecycleScope.launch {
  val data = withContext(Dispatchers.IO) { repository.fetchData() }
  updateUI(data) // Main thread
}

// ❌ Неправильно: GlobalScope — утечка памяти
GlobalScope.launch { /* ... */ }
```

### 2) WorkManager — гарантированное выполнение

Переживает перезапуск, поддерживает constraints (сеть, батарея), цепочки задач.

**Ключевые концепции**:
- Идемпотентность обязательна — worker может запуститься повторно
- Unique work предотвращает дублирование
- Не для точного времени или foreground задач

```kotlin
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
```

### 3) ExecutorService — Java interop

Thread pools с ручным управлением.

```kotlin
// ✅ Правильно: с shutdown
val executor = Executors.newFixedThreadPool(2)
val mainHandler = Handler(Looper.getMainLooper())

executor.execute {
  val result = computeData()
  mainHandler.post { updateUI(result) }
}
// В onDestroy: executor.shutdown()
```

### 4) HandlerThread — message queue поток

Один фоновый Looper для последовательной обработки.

```kotlin
val handlerThread = HandlerThread("bg").apply { start() }
val bgHandler = Handler(handlerThread.looper)

bgHandler.post {
  val result = processData()
  Handler(Looper.getMainLooper()).post { render(result) }
}
// Cleanup: handlerThread.quitSafely()
```

### 5) RxJava — reactive streams

Используйте если проект стандартизирован на Rx, иначе корутины.

```kotlin
val disposables = CompositeDisposable()

disposables.add(
  repository.getUser()
    .subscribeOn(Schedulers.io())
    .observeOn(AndroidSchedulers.mainThread())
    .subscribe({ user -> render(user) }, { error -> showError(error) })
)
// В onDestroy: disposables.clear()
```

**Сравнение подходов**

| Инструмент | Применение |
|------------|-----------|
| Coroutines | In-process задачи, UI updates, network |
| WorkManager | Deferrable tasks, выживает при process death |
| Executor | Java interop, legacy |
| HandlerThread | Sequential message processing |
| RxJava | Reactive streams, существующая Rx база |

**Распространённые ошибки**:
- Обновление UI вне main thread → Main dispatcher/Handlers
- Не отменили работу при lifecycle events → lifecycle scopes
- WorkManager для точного времени → AlarmManager
- Утечка threads/executors → shutdown в onDestroy

---

## Answer (EN)

Main thread for UI only, offload everything else to background. Choice depends on use case: coroutines (default), WorkManager (deferrable work), Executor/HandlerThread (legacy), RxJava (reactive).

### 1) Kotlin Coroutines — Default Choice

Structured concurrency, lifecycle-scopes, automatic cancellation.

**Key Concepts**:
- Parent/child relationship — cancellation propagates automatically
- `withContext(Dispatchers.IO)` for thread switching
- `lifecycleScope`/`viewModelScope` instead of `GlobalScope`
- `coroutineScope` (fail-fast) vs `supervisorScope` (isolation)

```kotlin
// ✅ Correct: lifecycle-aware scope
lifecycleScope.launch {
  val data = withContext(Dispatchers.IO) { repository.fetchData() }
  updateUI(data) // Main thread
}

// ❌ Wrong: GlobalScope — memory leak
GlobalScope.launch { /* ... */ }
```

### 2) WorkManager — Guaranteed Execution

Survives app restarts, supports constraints (network, battery), task chaining.

**Key Concepts**:
- Idempotency required — worker may run multiple times
- Unique work prevents duplication
- Not for exact timing or foreground tasks

```kotlin
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
```

### 3) ExecutorService — Java Interop

Thread pools with manual management.

```kotlin
// ✅ Correct: with shutdown
val executor = Executors.newFixedThreadPool(2)
val mainHandler = Handler(Looper.getMainLooper())

executor.execute {
  val result = computeData()
  mainHandler.post { updateUI(result) }
}
// In onDestroy: executor.shutdown()
```

### 4) HandlerThread — Message Queue Thread

Single background Looper for sequential processing.

```kotlin
val handlerThread = HandlerThread("bg").apply { start() }
val bgHandler = Handler(handlerThread.looper)

bgHandler.post {
  val result = processData()
  Handler(Looper.getMainLooper()).post { render(result) }
}
// Cleanup: handlerThread.quitSafely()
```

### 5) RxJava — Reactive Streams

Use if project is standardized on Rx, otherwise prefer coroutines.

```kotlin
val disposables = CompositeDisposable()

disposables.add(
  repository.getUser()
    .subscribeOn(Schedulers.io())
    .observeOn(AndroidSchedulers.mainThread())
    .subscribe({ user -> render(user) }, { error -> showError(error) })
)
// In onDestroy: disposables.clear()
```

**Comparison**

| Tool | When to Use |
|------|------------|
| Coroutines | In-process tasks, UI updates, network |
| WorkManager | Deferrable tasks, survives process death |
| Executor | Java interop, legacy |
| HandlerThread | Sequential message processing |
| RxJava | Reactive streams, existing Rx codebase |

**Common Pitfalls**:
- Updating UI off main thread → Main dispatcher/Handlers
- Forgetting to cancel work on lifecycle events → lifecycle scopes
- WorkManager for exact timing → AlarmManager
- Leaking threads/executors → shutdown in onDestroy

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
