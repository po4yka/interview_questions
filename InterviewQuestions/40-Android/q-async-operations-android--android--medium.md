---
id: 20251012-122785
title: Async Operations in Android / Асинхронные операции в Android
aliases: [Async Operations in Android, Асинхронные операции в Android]
topic: android
subtopics: [threads-sync, coroutines, workmanager]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-async-primitives--android--easy, q-anr-application-not-responding--android--medium, q-android-performance-measurement-tools--android--medium]
created: 2025-10-15
updated: 2025-10-20
tags: [android/threads-sync, android/coroutines, android/workmanager, concurrency, async, threading, difficulty/medium]
---

# Question (EN)
> How to run asynchronous operations in Android?

# Вопрос (RU)
> Как запускать асинхронные операции в Android?

---

## Answer (EN)

Use the right tool per use case: Coroutines (default), WorkManager (deferrable background), Executor/HandlerThread (interop/legacy), RxJava (reactive), and avoid deprecated AsyncTask. Threads are low-level and rarely needed directly.

**Theory (core principles)**
- Main thread for UI only; offload I/O/CPU-bound work
- Structured concurrency (scopes, cancellation) to avoid leaks
- Lifecycle awareness for safe UI updates
- Deferrable jobs must survive process death (WorkManager)

### 1) Kotlin Coroutines — default choice

- Theory: Structured concurrency; lifecycle scopes; easy cancellation; fine-grained dispatchers (Main/IO/Default).
```kotlin
lifecycleScope.launch {
  val data = withContext(Dispatchers.IO) { repo.fetch() }
  render(data) // Main thread
}
```

### 2) ExecutorService — Java interop

- Theory: Thread pools; manual lifecycle/cancellation; use for libraries/legacy APIs.
```kotlin
val executor = Executors.newFixedThreadPool(2)
val main = Handler(Looper.getMainLooper())
executor.execute {
  val result = doWork()
  main.post { render(result) }
}
```

### 3) HandlerThread — message queue thread

- Theory: Single background Looper + Handler; good for sequential tasks and message-based processing.
```kotlin
val ht = HandlerThread("bg").apply { start() }
val bg = Handler(ht.looper)
val ui = Handler(Looper.getMainLooper())
bg.post { val r = compute(); ui.post { render(r) } }
```

### 4) WorkManager — deferrable, guaranteed work

- Theory: Persists across app restarts; respects constraints (network, battery); chaining and retries.
```kotlin
class UploadWorker(ctx: Context, p: WorkerParameters): CoroutineWorker(ctx,p){
  override suspend fun doWork() = Result.success()
}
val req = OneTimeWorkRequestBuilder<UploadWorker>()
  .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build())
  .build()
WorkManager.getInstance(context).enqueue(req)
```

### 5) RxJava — reactive streams

- Theory: Pull/push streams with schedulers; prefer coroutines unless project standardizes on Rx.
```kotlin
repo.getUser()
  .subscribeOn(Schedulers.io())
  .observeOn(AndroidSchedulers.mainThread())
  .subscribe({ render(it) }, { showError(it) })
```

### 6) Threads — low-level

- Theory: Manual thread mgmt; no lifecycle/cancellation; use only for minimal cases.
```kotlin
Thread { val r = compute(); runOnUiThread { render(r) } }.start()
```

**Comparisons**
- Coroutines vs Rx: coroutines integrate with Kotlin/Jetpack; Rx offers powerful operators but higher complexity
- WorkManager vs coroutines: WorkManager for deferrable, guaranteed jobs; coroutines for in-process tasks
- Executor/HandlerThread vs coroutines: use for interop or message-queue pattern; otherwise coroutines

**Common pitfalls**
- Updating UI off main thread → use Main dispatcher/Handlers
- Forgetting to cancel work on lifecycle end → use lifecycleScope/viewModelScope
- Using WorkManager for exact timing/foreground tasks → use ForegroundService/AlarmManager
- Leaking threads/executors → shutdown in onDestroy/onCleared

**Testing**
- Coroutines: TestDispatcher/TestScope, Turbine for Flow
- WorkManager: WorkManagerTestInitHelper, set test configuration
- Executors/HandlerThread: use Robolectric/LooperMode or instrumentation

---

## Ответ (RU)

Выбирайте инструмент по задаче: Coroutines (по умолчанию), WorkManager (отложенная фоновая работа), Executor/HandlerThread (интероп/наследие), RxJava (реактивный подход), избегайте устаревшего AsyncTask. Threads — низкоуровневый вариант, редко нужен напрямую.

**Теория (базовые принципы)**
- Главный поток — только UI; выносите I/O/CPU работу на фон
- Структурная конкуррентность (scopes, cancellation) во избежание утечек
- Учет жизненного цикла для безопасных обновлений UI
- Отложенные задачи должны переживать смерть процесса (WorkManager)

### 1) Kotlin Coroutines — выбор по умолчанию

- Теория: Структурная конкуррентность; lifecycle scope; простая отмена; диспетчеры (Main/IO/Default).
```kotlin
lifecycleScope.launch {
  val data = withContext(Dispatchers.IO) { repo.fetch() }
  render(data) // Main thread
}
```

### 2) ExecutorService — совместимость с Java

- Теория: Пулы потоков; ручной lifecycle/cancel; для библиотек/наследия.
```kotlin
val executor = Executors.newFixedThreadPool(2)
val main = Handler(Looper.getMainLooper())
executor.execute {
  val result = doWork()
  main.post { render(result) }
}
```

### 3) HandlerThread — поток с очередью сообщений

- Теория: Фоновый Looper + Handler; подходит для последовательных задач и message-based обработки.
```kotlin
val ht = HandlerThread("bg").apply { start() }
val bg = Handler(ht.looper)
val ui = Handler(Looper.getMainLooper())
bg.post { val r = compute(); ui.post { render(r) } }
```

### 4) WorkManager — отложенная гарантированная работа

- Теория: Переживает перезапуски; учитывает ограничения (сеть, батарея); чейнинг и ретраи.
```kotlin
class UploadWorker(ctx: Context, p: WorkerParameters): CoroutineWorker(ctx,p){
  override suspend fun doWork() = Result.success()
}
val req = OneTimeWorkRequestBuilder<UploadWorker>()
  .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build())
  .build()
WorkManager.getInstance(context).enqueue(req)
```

### 5) RxJava — реактивные потоки

- Теория: Потоки с планировщиками; выбирайте, если проект стандартизирован на Rx; иначе корутины проще.
```kotlin
repo.getUser()
  .subscribeOn(Schedulers.io())
  .observeOn(AndroidSchedulers.mainThread())
  .subscribe({ render(it) }, { showError(it) })
```

### 6) Потоки (Thread) — низкий уровень

- Теория: Ручное управление; нет lifecycle/cancel; используйте только при необходимости.
```kotlin
Thread { val r = compute(); runOnUiThread { render(r) } }.start()
```

**Сравнения**
- Coroutines vs Rx: корутины — интеграция с Kotlin/Jetpack; Rx — мощные операторы, выше сложность
- WorkManager vs корутины: WorkManager — гарантированные отложенные задачи; корутины — в рамках процесса
- Executor/HandlerThread vs корутины: интероп/очереди сообщений; иначе — корутины

**Типичные ошибки**
- Обновление UI не на главном потоке → Main dispatcher/Handler
- Нет отмены при завершении lifecycle → lifecycleScope/viewModelScope
- WorkManager для точного времени/foreground → ForegroundService/AlarmManager
- Утечки потоков/экзекьюторов → shutdown в onDestroy/onCleared

**Тестирование**
- Корутины: TestDispatcher/TestScope, Turbine для Flow
- WorkManager: WorkManagerTestInitHelper, тестовые конфигурации
- Executors/HandlerThread: Robolectric/LooperMode или инструментальные

---

## Follow-ups

- How do you choose between WorkManager and ForegroundService?
- When to use RemoteMediator with Paging in async pipelines?
- Strategies for cancellation propagation across layers?

## References

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
