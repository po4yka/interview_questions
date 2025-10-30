---
id: 20251012-122778
title: ANR (Application Not Responding) / ANR (Приложение не отвечает)
aliases: ["ANR (Application Not Responding)", "ANR (Приложение не отвечает)"]
topic: android
subtopics: [performance-rendering, profiling, strictmode-anr]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-lifecycle, c-coroutines, c-workmanager, q-strictmode-debugging--android--medium]
created: 2025-10-05
updated: 2025-10-30
sources: []
tags: [android/performance-rendering, android/profiling, android/strictmode-anr, performance, debugging, difficulty/medium]
---
# Вопрос (RU)
> Что такое ANR (Application Not Responding) и как его предотвратить?

# Question (EN)
> What is ANR (Application Not Responding) and how to prevent it?

---

## Ответ (RU)

**ANR (Application Not Responding)** — критическая ошибка, возникающая при блокировке UI-потока. Система показывает диалог принудительного завершения приложения.

**Типы ANR с таймаутами:**

- **Input dispatching**: нет ответа на ввод в течение 5 секунд
- **Service**: методы сервиса выполняются > 20 сек (background) или > 10 сек (foreground)
- **BroadcastReceiver**: receiver не завершается за 10 секунд

**Типичные причины блокировки main thread:**

```kotlin
// ❌ ПЛОХО: Блокировка main thread
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        File("large.txt").readText()  // I/O блокировка
        calculatePrimes(1_000_000)    // CPU-интенсивная задача
        httpClient.get(url).execute() // Синхронный network call
    }
}
```

```kotlin
// ✅ ХОРОШО: Асинхронное выполнение
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycleScope.launch(Dispatchers.IO) {
            val data = File("large.txt").readText()
            withContext(Dispatchers.Main) { updateUI(data) }
        }
    }
}
```

**BroadcastReceiver и goAsync():**

```kotlin
// ✅ goAsync() для асинхронной работы
class MyReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val pendingResult = goAsync()
        CoroutineScope(Dispatchers.IO).launch {
            try {
                database.insert(data)
            } finally {
                pendingResult.finish()
            }
        }
    }
}
```

**Диагностика и мониторинг:**

```kotlin
// StrictMode для детекции в debug
if (BuildConfig.DEBUG) {
    StrictMode.setThreadPolicy(
        StrictMode.ThreadPolicy.Builder()
            .detectAll()
            .penaltyLog()
            .build()
    )
}
```

**Production-мониторинг:**
- **Android Vitals** в Play Console: ANR rate, affected users, traces
- **ANR traces** (`/data/anr/traces.txt`): stacktrace всех потоков в момент ANR
- **Firebase Crashlytics**: автоматический сбор ANR-отчетов

**Стратегии предотвращения:**

1. Main thread только для UI (< 16ms для 60 FPS)
2. WorkManager для долгих фоновых задач
3. Минимум работы в lifecycle callbacks (onCreate, onResume)
4. Избегать длинных synchronized блоков
5. Использовать Dispatchers.IO для I/O, Dispatchers.Default для CPU-задач

## Answer (EN)

**ANR (Application Not Responding)** is a critical error occurring when the UI thread is blocked. The system displays a force-close dialog to the user.

**ANR Types with Timeouts:**

- **Input dispatching**: no response to input within 5 seconds
- **Service**: methods take > 20 sec (background) or > 10 sec (foreground)
- **BroadcastReceiver**: receiver doesn't finish within 10 seconds

**Common Causes of Main Thread Blocking:**

```kotlin
// ❌ BAD: Blocking main thread
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        File("large.txt").readText()  // I/O blocking
        calculatePrimes(1_000_000)    // CPU-intensive task
        httpClient.get(url).execute() // Synchronous network call
    }
}
```

```kotlin
// ✅ GOOD: Asynchronous execution
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycleScope.launch(Dispatchers.IO) {
            val data = File("large.txt").readText()
            withContext(Dispatchers.Main) { updateUI(data) }
        }
    }
}
```

**BroadcastReceiver and goAsync():**

```kotlin
// ✅ goAsync() for asynchronous work
class MyReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val pendingResult = goAsync()
        CoroutineScope(Dispatchers.IO).launch {
            try {
                database.insert(data)
            } finally {
                pendingResult.finish()
            }
        }
    }
}
```

**Diagnostics and Monitoring:**

```kotlin
// StrictMode for debug detection
if (BuildConfig.DEBUG) {
    StrictMode.setThreadPolicy(
        StrictMode.ThreadPolicy.Builder()
            .detectAll()
            .penaltyLog()
            .build()
    )
}
```

**Production Monitoring:**
- **Android Vitals** in Play Console: ANR rate, affected users, traces
- **ANR traces** (`/data/anr/traces.txt`): stacktraces of all threads at ANR moment
- **Firebase Crashlytics**: automatic ANR report collection

**Prevention Strategies:**

1. Main thread only for UI (< 16ms for 60 FPS)
2. WorkManager for long background tasks
3. Minimize work in lifecycle callbacks (onCreate, onResume)
4. Avoid long synchronized blocks
5. Use Dispatchers.IO for I/O, Dispatchers.Default for CPU tasks

---

## Follow-ups

- How do you analyze ANR traces from `/data/anr/traces.txt` to identify the root cause of blocking?
- What's the difference between WorkManager and coroutines for preventing ANRs in long-running tasks?
- How does StrictMode penaltyDeath() differ from penaltyLog() in ANR detection?
- Can brief I/O operations (< 50ms) ever be acceptable on the main thread, and when?
- How do you handle ANRs caused by third-party SDKs or system Binder calls beyond your control?

## References

- [[c-lifecycle]]
- [[c-coroutines]]
- [[c-workmanager]]
- [[c-strictmode]]
- https://developer.android.com/topic/performance/vitals/anr
- https://developer.android.com/topic/performance/anrs/diagnose-and-fix-anrs

## Related Questions

### Prerequisites (Easier)
- [[q-what-unifies-android-components--android--easy]] - Understanding Android component lifecycle
- [[q-what-is-broadcastreceiver--android--easy]] - BroadcastReceiver basics

### Related (Same Level)
- [[q-strictmode-debugging--android--medium]] - Using StrictMode for performance debugging
- [[q-multithreading-tools-android--android--medium]] - Android threading mechanisms

### Advanced (Harder)
- [[q-service-lifecycle-binding--android--hard]] - Advanced service patterns
- [[q-profiling-systrace--android--hard]] - Deep performance profiling
