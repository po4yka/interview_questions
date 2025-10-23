---
id: 20251012-122785
title: Async Operations in Android / Асинхронные операции в Android
aliases:
- Async Operations in Android
- Асинхронные операции в Android
topic: android
subtopics:
- threads-sync
- coroutines
- workmanager
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- q-android-async-primitives--android--easy
- q-anr-application-not-responding--android--medium
- q-android-performance-measurement-tools--android--medium
created: 2025-10-15
updated: 2025-10-20
tags:
- android/threads-sync
- android/coroutines
- android/workmanager
- concurrency
- async
- threading
- difficulty/medium
---# Вопрос (RU)
> Как запускать асинхронные операции в Android?

---

# Question (EN)
> How to run asynchronous operations in Android?

## Ответ (RU)

Выбирайте инструмент по задаче: Coroutines (по умолчанию), WorkManager (отложенная фоновая работа), Executor/HandlerThread (интероп/наследие), RxJava (реактивный подход), избегайте устаревшего AsyncTask. Threads — низкоуровневый вариант, редко нужен напрямую.

**Теория (базовые принципы)**
- Главный поток — только UI; выносите I/O/CPU работу на фон
- Структурная конкуррентность (scopes, cancellation) во избежание утечек
- Учет жизненного цикла для безопасных обновлений UI
- Отложенные задачи должны переживать смерть процесса (WorkManager)

### 1) Kotlin Coroutines — выбор по умолчанию

- Теория: Структурная конкуррентность; lifecycle scope; простая отмена; диспетчеры (Main/IO/Default).
- Ключевые моменты:
  - Родительский/дочерний подход: отмена и исключения распространяются по умолчанию
  - Используйте `coroutineScope` для быстрой отмены; `supervisorScope` для изоляции отказов
  - Переключайте потоки с `withContext(Dispatchers.IO/Default)` (CPU/I/O изоляция)
  - Предпочитайте `lifecycleScope`/`viewModelScope` вместо `GlobalScope`
  - `async/await` только когда вам действительно нужно параллелизм; иначе используйте `withContext`
  - Обрабатывайте исключения с `CoroutineExceptionHandler` на верхнем уровне
  - Сотрудничество с отменой: проверяйте отмену в длинных циклах или I/O
```kotlin
lifecycleScope.launch {
  val data = withContext(Dispatchers.IO) { repo.fetch() }
  render(data) // Main thread
}
```

### 2) ExecutorService — совместимость с Java

- Теория: Пулы потоков; ручной lifecycle/cancel; для библиотек/наследия.
- Ключевые моменты:
  - Типы пулов: `newFixedThreadPool`, `newCachedThreadPool`, `newSingleThreadExecutor`, `newScheduledThreadPool`
  - Очередь и политика отклонения влияют на задержку и backpressure
  - Предоставьте пользовательский `ThreadFactory` для установки имен и приоритетов
  - Всегда вызывайте `shutdown()`/`shutdownNow()` для избегания утечек
  - Видимость памяти: публикуйте результаты на основной поток через `Handler`/`Executor`
  - Предпочитайте корутины, если интероп требует экзекьюторов
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
- Ключевые моменты:
  - Компоненты: `Looper` + `MessageQueue` + `Handler`
  - Аффинитет потока: код в `HandlerThread` не должен касаться UI; отправляйте обратно на основной
  - Избегайте длительной блокирующей работы внутри looper; он блокирует очередь
  - Используйте для пайплайнов сенсоров/IO, где важен порядок
  - Чистый запуск с `quitSafely()` для опорожнения ожидающих сообщений
```kotlin
val ht = HandlerThread("bg").apply { start() }
val bg = Handler(ht.looper)
val ui = Handler(Looper.getMainLooper())
bg.post { val r = compute(); ui.post { render(r) } }
```

### 4) WorkManager — отложенная гарантированная работа

- Теория: Переживает перезапуски; учитывает ограничения (сеть, батарея); чейнинг и ретраи.
- Ключевые моменты:
  - Используйте ограничения (сеть, зарядка, бездействующий) и критерии отступа (линейный/экспоненциальный)
  - Уникальная работа (`enqueueUniqueWork`) для слияния дубликатов; цепочка работ с входными/выходными `Data`
  - Требуется идемпотентность: ваш работник может запуститься более одного раза
  - Используйте ForegroundService, а не WorkManager, для длительных пользовательских задач
  - Периодическая работа имеет минимальные интервальные ограничения и неточное планирование
  - Рассмотрите ускоренную работу для высокоприоритетных коротких задач
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
- Ключевые моменты:
  - Холодные vs горячие наблюдаемые; примените правильную стратегию backpressure (Flowable) для быстрых производителей
  - Многопоточность через `subscribeOn` (upstream) и `observeOn` (downstream)
  - Управление жизненным циклом с `CompositeDisposable` (dispose в `onDestroy`/`onCleared`)
  - Предпочитайте операторы отображения над побочными эффектами; сократите цепочки и сделайте их читаемыми
  - Интероп с корутинами через `kotlinx-coroutines-rx2/rx3` при миграции
```kotlin
repo.getUser()
  .subscribeOn(Schedulers.io())
  .observeOn(AndroidSchedulers.mainThread())
  .subscribe({ render(it) }, { showError(it) })
```

### 6) Потоки (Thread) — низкий уровень

- Теория: Ручное управление; нет lifecycle/cancel; используйте только при необходимости.
- Ключевые моменты:
  - Сотрудничество с `interrupt()`/`isInterrupted` для отмены
  - Синхронизация примитивов (замки, атомарные) являются источником ошибок; предпочитайте более высокие уровни API
  - Всегда переходите на основной поток для обновлений UI (`runOnUiThread`, `Handler`)
  - Риск утечек, если потоки живут дольше Activity/Fragment; обеспечьте правильное завершение
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

## Answer (EN)

Use the right tool per use case: Coroutines (default), WorkManager (deferrable background), Executor/HandlerThread (interop/legacy), RxJava (reactive), and avoid deprecated AsyncTask. Threads are low-level and rarely needed directly.

**Theory (core principles)**
- Main thread for UI only; offload I/O/CPU-bound work
- Structured concurrency (scopes, cancellation) to avoid leaks
- Lifecycle awareness for safe UI updates
- Deferrable jobs must survive process death (WorkManager)

### 1) Kotlin Coroutines — default choice

- Theory: Structured concurrency; lifecycle scopes; easy cancellation; fine-grained dispatchers (Main/IO/Default).
- Key points:
  - Parent/child relationship: cancellation and exceptions propagate by default
  - Use `coroutineScope` for fail-fast; `supervisorScope` to isolate failures
  - Switch threads with `withContext(Dispatchers.IO/Default)` (CPU/I/O confinement)
  - Prefer `lifecycleScope`/`viewModelScope` over `GlobalScope`
  - `async/await` only when you truly need parallelism; otherwise use `withContext`
  - Handle exceptions with `CoroutineExceptionHandler` at the top-level
  - Cooperative cancellation: check for cancellation in long loops or I/O
```kotlin
lifecycleScope.launch {
  val data = withContext(Dispatchers.IO) { repo.fetch() }
  render(data) // Main thread
}
```

### 2) ExecutorService — Java interop

- Theory: Thread pools; manual lifecycle/cancellation; use for libraries/legacy APIs.
- Key points:
  - Pool types: `newFixedThreadPool`, `newCachedThreadPool`, `newSingleThreadExecutor`, `newScheduledThreadPool`
  - Queueing and rejection policy impact latency and backpressure
  - Provide a custom `ThreadFactory` to set names and priorities
  - Always call `shutdown()`/`shutdownNow()` to avoid leaks
  - Memory visibility: publish results to main thread via `Handler`/`Executor`
  - Prefer coroutines unless interop requires executors
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
- Key points:
  - Components: `Looper` + `MessageQueue` + `Handler`
  - Thread affinity: code in `HandlerThread` must not touch UI; post back to main
  - Avoid long blocking work inside the looper; it stalls the queue
  - Use for sensor/IO pipelines where ordering matters
  - Clean shutdown with `quitSafely()` to drain pending messages
```kotlin
val ht = HandlerThread("bg").apply { start() }
val bg = Handler(ht.looper)
val ui = Handler(Looper.getMainLooper())
bg.post { val r = compute(); ui.post { render(r) } }
```

### 4) WorkManager — deferrable, guaranteed work

- Theory: Persists across app restarts; respects constraints (network, battery); chaining and retries.
- Key points:
  - Use constraints (network, charging, idle) and backoff criteria (linear/exponential)
  - Unique work (`enqueueUniqueWork`) to coalesce duplicates; work chaining with input/output `Data`
  - Idempotency required: your worker may run more than once
  - Use ForegroundService, not WorkManager, for user-visible long-running tasks
  - Periodic work has minimum interval limits and inexact scheduling
  - Consider expedited work for high-priority short tasks
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
- Key points:
  - Cold vs hot observables; apply correct backpressure strategy (Flowable) for fast producers
  - Threading via `subscribeOn` (upstream) and `observeOn` (downstream)
  - Manage lifecycle with `CompositeDisposable` (dispose in `onDestroy`/`onCleared`)
  - Prefer mapping operators over side-effects; keep chains short and readable
  - Interop with coroutines via `kotlinx-coroutines-rx2/rx3` when migrating
```kotlin
repo.getUser()
  .subscribeOn(Schedulers.io())
  .observeOn(AndroidSchedulers.mainThread())
  .subscribe({ render(it) }, { showError(it) })
```

### 6) Threads — low-level

- Theory: Manual thread mgmt; no lifecycle/cancellation; use only for minimal cases.
- Key points:
  - Cooperate with `interrupt()`/`isInterrupted` for cancellation
  - Synchronization primitives (locks, atomics) are error-prone; prefer higher-level APIs
  - Always hop to main thread for UI updates (`runOnUiThread`, `Handler`)
  - Risk of leaks if threads outlive Activity/Fragment; ensure proper shutdown
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

