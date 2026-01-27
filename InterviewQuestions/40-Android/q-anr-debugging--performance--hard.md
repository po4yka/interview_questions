---
id: android-751
title: ANR Debugging and Prevention / Отладка и Предотвращение ANR
aliases:
- ANR
- Application Not Responding
- Отладка ANR
topic: android
subtopics:
- performance
- debugging
- threading
question_kind: theory
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-strict-mode--performance--medium
- q-profiler-tools--performance--medium
created: 2026-01-23
updated: 2026-01-23
tags:
- android/performance
- android/debugging
- difficulty/hard
- anr
- threading
anki_cards:
- slug: android-751-0-en
  language: en
- slug: android-751-0-ru
  language: ru
---
# Вопрос (RU)

> Что такое ANR? Каковы причины и как предотвращать и отлаживать ANR?

# Question (EN)

> What is ANR? What are the causes and how do you prevent and debug ANR?

---

## Ответ (RU)

**ANR (Application Not Responding)** -- это диалог, который система показывает пользователю, когда приложение не отвечает на пользовательский ввод в течение определённого времени.

### Краткий Ответ

- **Input ANR**: Main thread заблокирован >5 секунд при обработке ввода
- **Broadcast ANR**: BroadcastReceiver не завершился за 10 секунд
- **Service ANR**: Service не завершился за 20 секунд (foreground) или 200 секунд (background)
- **Причины**: длительные операции в main thread, deadlock, бесконечные циклы

### Подробный Ответ

### Типы ANR и Таймауты

```
Тип                          Таймаут
------------------------------------------
Input dispatch               5 секунд
BroadcastReceiver           10 секунд
Service (foreground)        20 секунд
Service (background)       200 секунд
ContentProvider             10 секунд
```

### Основные Причины ANR

```kotlin
// 1. Длительные операции в Main Thread
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)

    // ПЛОХО -- блокирует main thread
    val data = database.loadAllData() // 10 секунд
    val response = httpClient.get(url) // Сетевой запрос
    val result = heavyComputation()    // CPU-интенсивно
}

// 2. Deadlock
class DeadlockExample {
    private val lock1 = Any()
    private val lock2 = Any()

    fun method1() {
        synchronized(lock1) {
            Thread.sleep(100)
            synchronized(lock2) { /* ... */ }
        }
    }

    fun method2() {
        synchronized(lock2) {
            Thread.sleep(100)
            synchronized(lock1) { /* ... */ } // Deadlock!
        }
    }
}

// 3. Бесконечный цикл
fun processData() {
    while (hasMoreData) {
        // Забыли обновить hasMoreData
        processItem()
    }
}
```

### Анализ ANR Trace

При ANR система создаёт trace файл: `/data/anr/traces.txt`

```
"main" prio=5 tid=1 Blocked
  | group="main" sCount=1 dsCount=0 flags=1 obj=0x73c1e000 self=0x7f8a6c8000
  | sysTid=12345 nice=-10 cgrp=default sched=0/0 handle=0x7f8b6c9530
  | state=S schedstat=( 12345678 123456 100 ) utm=100 stm=50 core=2 HZ=100
  | stack=0x7ff8e9e000-0x7ff8ea0000 stackSize=8192KB
  | held mutexes=
  at com.example.app.MainActivity.loadData(MainActivity.kt:45)
  - waiting to lock <0x0abc1234> (a java.lang.Object) held by thread 15
  at com.example.app.MainActivity.onCreate(MainActivity.kt:20)
  at android.app.Activity.performCreate(Activity.java:8000)
```

**Ключевая информация:**
- `tid=1` -- Thread ID (1 = main thread)
- `Blocked` -- состояние потока
- `waiting to lock` -- ждёт lock, который держит другой поток
- Stack trace показывает где поток заблокирован

### Инструменты Отладки

#### 1. Android Studio Profiler

```kotlin
// Запись CPU trace во время ANR
Debug.startMethodTracing("anr_trace")
// ... код, который может вызвать ANR
Debug.stopMethodTracing()
// Файл: /sdcard/Android/data/<package>/files/anr_trace.trace
```

#### 2. Perfetto / Systrace

```bash
# Запись system trace
adb shell perfetto \
  -c - --txt \
  -o /data/misc/perfetto-traces/trace \
<<EOF
buffers: {
    size_kb: 63488
    fill_policy: DISCARD
}
data_sources: {
    config {
        name: "linux.ftrace"
        ftrace_config {
            ftrace_events: "sched/sched_switch"
            ftrace_events: "power/suspend_resume"
            atrace_categories: "am"
            atrace_categories: "wm"
            atrace_apps: "com.example.app"
        }
    }
}
duration_ms: 10000
EOF

# Получить trace
adb pull /data/misc/perfetto-traces/trace
```

#### 3. Play Console ANR Reports

```kotlin
// Программное получение ANR информации
class AnrWatchdog(
    private val timeout: Long = 5000L
) : Thread("ANR-Watchdog") {

    private val mainHandler = Handler(Looper.getMainLooper())
    @Volatile private var tick = 0L
    @Volatile private var reported = false

    override fun run() {
        while (!isInterrupted) {
            tick = 0L
            reported = false

            mainHandler.post { tick = System.currentTimeMillis() }

            sleep(timeout)

            if (tick == 0L && !reported) {
                reported = true
                val stackTrace = Looper.getMainLooper().thread.stackTrace
                Log.e("ANR", "Main thread blocked:\n${stackTrace.joinToString("\n")}")
                // Отправить в crash reporting
            }
        }
    }
}
```

### Исправление ANR

#### 1. Перенос в Фоновый Поток

```kotlin
// ПЛОХО
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val users = database.getAllUsers() // Блокирует!
    }
}

// ХОРОШО -- Coroutines
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            val users = withContext(Dispatchers.IO) {
                database.getAllUsers()
            }
            updateUI(users)
        }
    }
}
```

#### 2. BroadcastReceiver с WorkManager

```kotlin
// ПЛОХО -- длительная работа в onReceive
class MyReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // Таймаут 10 секунд!
        processLargeData() // 30 секунд
    }
}

// ХОРОШО -- делегируем в WorkManager
class MyReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val data = intent.extras?.let { Data.Builder().putAll(it).build() }

        val workRequest = OneTimeWorkRequestBuilder<ProcessDataWorker>()
            .setInputData(data ?: Data.EMPTY)
            .build()

        WorkManager.getInstance(context).enqueue(workRequest)
    }
}

class ProcessDataWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        processLargeData()
        return Result.success()
    }
}
```

#### 3. Service с Foreground Notification

```kotlin
class LongRunningService : Service() {

    override fun onCreate() {
        super.onCreate()

        // Создаём foreground notification сразу
        val notification = createNotification()
        startForeground(NOTIFICATION_ID, notification)

        // Работу выполняем в фоне
        serviceScope.launch {
            doLongRunningWork()
            stopSelf()
        }
    }
}
```

### Предотвращение ANR: Чеклист

```kotlin
// 1. Никаких долгих операций в main thread
// ПЛОХО
fun onClick() {
    val result = heavyOperation()
}

// ХОРОШО
fun onClick() {
    lifecycleScope.launch {
        val result = withContext(Dispatchers.Default) {
            heavyOperation()
        }
    }
}

// 2. Используйте таймауты для синхронизации
val lock = ReentrantLock()
if (lock.tryLock(100, TimeUnit.MILLISECONDS)) {
    try {
        // Критическая секция
    } finally {
        lock.unlock()
    }
} else {
    // Lock недоступен, обработать альтернативно
}

// 3. Отслеживайте main thread looper
class MainThreadChecker {
    fun checkMainThread() {
        if (Looper.myLooper() == Looper.getMainLooper()) {
            Log.w("MainThread", "Called on main thread!", Exception())
        }
    }
}
```

### ANR Metrics в Firebase

```kotlin
// Включение Performance Monitoring
// build.gradle
implementation("com.google.firebase:firebase-perf-ktx:21.0.1")

// Кастомные traces
val trace = Firebase.performance.newTrace("heavy_operation")
trace.start()
// ... операция
trace.stop()

// Атрибуты для фильтрации
trace.putAttribute("operation_type", "database_query")
trace.putMetric("items_processed", itemCount.toLong())
```

---

## Answer (EN)

**ANR (Application Not Responding)** is a dialog that the system shows to users when an application doesn't respond to user input within a certain time.

### Short Answer

- **Input ANR**: Main thread blocked >5 seconds while handling input
- **Broadcast ANR**: BroadcastReceiver didn't finish in 10 seconds
- **Service ANR**: Service didn't finish in 20 seconds (foreground) or 200 seconds (background)
- **Causes**: long operations on main thread, deadlock, infinite loops

### Detailed Answer

### ANR Types and Timeouts

```
Type                         Timeout
------------------------------------------
Input dispatch               5 seconds
BroadcastReceiver           10 seconds
Service (foreground)        20 seconds
Service (background)       200 seconds
ContentProvider             10 seconds
```

### Main ANR Causes

```kotlin
// 1. Long operations on Main Thread
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)

    // BAD -- blocks main thread
    val data = database.loadAllData() // 10 seconds
    val response = httpClient.get(url) // Network request
    val result = heavyComputation()    // CPU-intensive
}

// 2. Deadlock
class DeadlockExample {
    private val lock1 = Any()
    private val lock2 = Any()

    fun method1() {
        synchronized(lock1) {
            Thread.sleep(100)
            synchronized(lock2) { /* ... */ }
        }
    }

    fun method2() {
        synchronized(lock2) {
            Thread.sleep(100)
            synchronized(lock1) { /* ... */ } // Deadlock!
        }
    }
}

// 3. Infinite loop
fun processData() {
    while (hasMoreData) {
        // Forgot to update hasMoreData
        processItem()
    }
}
```

### Analyzing ANR Trace

When ANR occurs, system creates trace file: `/data/anr/traces.txt`

```
"main" prio=5 tid=1 Blocked
  | group="main" sCount=1 dsCount=0 flags=1 obj=0x73c1e000 self=0x7f8a6c8000
  | sysTid=12345 nice=-10 cgrp=default sched=0/0 handle=0x7f8b6c9530
  | state=S schedstat=( 12345678 123456 100 ) utm=100 stm=50 core=2 HZ=100
  | stack=0x7ff8e9e000-0x7ff8ea0000 stackSize=8192KB
  | held mutexes=
  at com.example.app.MainActivity.loadData(MainActivity.kt:45)
  - waiting to lock <0x0abc1234> (a java.lang.Object) held by thread 15
  at com.example.app.MainActivity.onCreate(MainActivity.kt:20)
  at android.app.Activity.performCreate(Activity.java:8000)
```

**Key information:**
- `tid=1` -- Thread ID (1 = main thread)
- `Blocked` -- thread state
- `waiting to lock` -- waiting for lock held by another thread
- Stack trace shows where thread is blocked

### Debugging Tools

#### 1. Android Studio Profiler

```kotlin
// Record CPU trace during ANR
Debug.startMethodTracing("anr_trace")
// ... code that may cause ANR
Debug.stopMethodTracing()
// File: /sdcard/Android/data/<package>/files/anr_trace.trace
```

#### 2. Perfetto / Systrace

```bash
# Record system trace
adb shell perfetto \
  -c - --txt \
  -o /data/misc/perfetto-traces/trace \
<<EOF
buffers: {
    size_kb: 63488
    fill_policy: DISCARD
}
data_sources: {
    config {
        name: "linux.ftrace"
        ftrace_config {
            ftrace_events: "sched/sched_switch"
            ftrace_events: "power/suspend_resume"
            atrace_categories: "am"
            atrace_categories: "wm"
            atrace_apps: "com.example.app"
        }
    }
}
duration_ms: 10000
EOF

# Get trace
adb pull /data/misc/perfetto-traces/trace
```

#### 3. Play Console ANR Reports

```kotlin
// Programmatic ANR information
class AnrWatchdog(
    private val timeout: Long = 5000L
) : Thread("ANR-Watchdog") {

    private val mainHandler = Handler(Looper.getMainLooper())
    @Volatile private var tick = 0L
    @Volatile private var reported = false

    override fun run() {
        while (!isInterrupted) {
            tick = 0L
            reported = false

            mainHandler.post { tick = System.currentTimeMillis() }

            sleep(timeout)

            if (tick == 0L && !reported) {
                reported = true
                val stackTrace = Looper.getMainLooper().thread.stackTrace
                Log.e("ANR", "Main thread blocked:\n${stackTrace.joinToString("\n")}")
                // Send to crash reporting
            }
        }
    }
}
```

### Fixing ANR

#### 1. Move to Background Thread

```kotlin
// BAD
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val users = database.getAllUsers() // Blocks!
    }
}

// GOOD -- Coroutines
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            val users = withContext(Dispatchers.IO) {
                database.getAllUsers()
            }
            updateUI(users)
        }
    }
}
```

#### 2. BroadcastReceiver with WorkManager

```kotlin
// BAD -- long work in onReceive
class MyReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // 10 second timeout!
        processLargeData() // 30 seconds
    }
}

// GOOD -- delegate to WorkManager
class MyReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val data = intent.extras?.let { Data.Builder().putAll(it).build() }

        val workRequest = OneTimeWorkRequestBuilder<ProcessDataWorker>()
            .setInputData(data ?: Data.EMPTY)
            .build()

        WorkManager.getInstance(context).enqueue(workRequest)
    }
}

class ProcessDataWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        processLargeData()
        return Result.success()
    }
}
```

#### 3. Service with Foreground Notification

```kotlin
class LongRunningService : Service() {

    override fun onCreate() {
        super.onCreate()

        // Create foreground notification immediately
        val notification = createNotification()
        startForeground(NOTIFICATION_ID, notification)

        // Do work in background
        serviceScope.launch {
            doLongRunningWork()
            stopSelf()
        }
    }
}
```

### ANR Prevention: Checklist

```kotlin
// 1. No long operations on main thread
// BAD
fun onClick() {
    val result = heavyOperation()
}

// GOOD
fun onClick() {
    lifecycleScope.launch {
        val result = withContext(Dispatchers.Default) {
            heavyOperation()
        }
    }
}

// 2. Use timeouts for synchronization
val lock = ReentrantLock()
if (lock.tryLock(100, TimeUnit.MILLISECONDS)) {
    try {
        // Critical section
    } finally {
        lock.unlock()
    }
} else {
    // Lock unavailable, handle alternatively
}

// 3. Monitor main thread looper
class MainThreadChecker {
    fun checkMainThread() {
        if (Looper.myLooper() == Looper.getMainLooper()) {
            Log.w("MainThread", "Called on main thread!", Exception())
        }
    }
}
```

### ANR Metrics in Firebase

```kotlin
// Enable Performance Monitoring
// build.gradle
implementation("com.google.firebase:firebase-perf-ktx:21.0.1")

// Custom traces
val trace = Firebase.performance.newTrace("heavy_operation")
trace.start()
// ... operation
trace.stop()

// Attributes for filtering
trace.putAttribute("operation_type", "database_query")
trace.putMetric("items_processed", itemCount.toLong())
```

---

## Ссылки (RU)

- [ANRs](https://developer.android.com/topic/performance/vitals/anr)
- [Debug ANRs](https://developer.android.com/topic/performance/anr)
- [Perfetto](https://perfetto.dev/docs/)

## References (EN)

- [ANRs](https://developer.android.com/topic/performance/vitals/anr)
- [Debug ANRs](https://developer.android.com/topic/performance/anr)
- [Perfetto](https://perfetto.dev/docs/)

## Follow-ups (EN)

- How to read and analyze traces.txt file?
- What is the difference between ANR and crash?
- How does Android 14 handle ANRs differently?
- How to implement ANR detection in production apps?

## Дополнительные Вопросы (RU)

- Как читать и анализировать файл traces.txt?
- В чём разница между ANR и crash?
- Как Android 14 обрабатывает ANR по-другому?
- Как реализовать обнаружение ANR в production приложениях?
