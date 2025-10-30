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
updated: 2025-10-29
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

**Типичные антипаттерны:**

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
// ✅ ХОРОШО: Асинхронное выполнение с корутинами
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch(Dispatchers.IO) {
            val data = File("large.txt").readText()
            withContext(Dispatchers.Main) {
                updateUI(data)
            }
        }
    }
}
```

**BroadcastReceiver и goAsync():**

```kotlin
// ❌ ПЛОХО: Долгая операция в onReceive
class MyReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        database.insert(data)  // Может занять > 10 сек
    }
}
```

```kotlin
// ✅ ХОРОШО: goAsync() для асинхронной работы
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

**Диагностика ANR:**

```kotlin
// StrictMode для детекции проблем в debug-сборках
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
- **Android Vitals** в Play Console показывает ANR rate и affected users
- **ANR traces** (`/data/anr/traces.txt`) содержат stacktrace всех потоков
- **Firebase Crashlytics** может собирать ANR-отчеты

**Стратегии предотвращения:**

1. Main thread только для UI (< 16ms для 60 FPS)
2. WorkManager для долгих фоновых задач
3. Минимум работы в lifecycle callbacks
4. Избегать длинных synchronized блоков

## Answer (EN)

**ANR (Application Not Responding)** is a critical error occurring when the UI thread is blocked. The system displays a force-close dialog to the user.

**ANR Types with Timeouts:**

- **Input dispatching**: no response to input within 5 seconds
- **Service**: methods take > 20 sec (background) or > 10 sec (foreground)
- **BroadcastReceiver**: receiver doesn't finish within 10 seconds

**Common Anti-patterns:**

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
// ✅ GOOD: Asynchronous execution with coroutines
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch(Dispatchers.IO) {
            val data = File("large.txt").readText()
            withContext(Dispatchers.Main) {
                updateUI(data)
            }
        }
    }
}
```

**BroadcastReceiver and goAsync():**

```kotlin
// ❌ BAD: Long operation in onReceive
class MyReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        database.insert(data)  // May take > 10 sec
    }
}
```

```kotlin
// ✅ GOOD: goAsync() for asynchronous work
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

**ANR Diagnostics:**

```kotlin
// StrictMode for detecting issues in debug builds
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
- **Android Vitals** in Play Console shows ANR rate and affected users
- **ANR traces** (`/data/anr/traces.txt`) contain stacktraces of all threads
- **Firebase Crashlytics** can collect ANR reports

**Prevention Strategies:**

1. Main thread only for UI (< 16ms for 60 FPS)
2. WorkManager for long background tasks
3. Minimize work in lifecycle callbacks
4. Avoid long synchronized blocks

---

## Follow-ups

- How do you analyze ANR traces from `/data/anr/traces.txt` to identify blocking operations?
- What's the difference between WorkManager and coroutines for long-running tasks?
- How does StrictMode penaltyDeath() differ from penaltyLog() in ANR prevention?
- When is it acceptable to perform brief I/O operations on the main thread?
- How do you handle ANRs caused by third-party SDK or system Binder calls?

## References

- [[c-lifecycle]]
- [[c-coroutines]]
- [[c-workmanager]]
- https://developer.android.com/topic/performance/vitals/anr
- https://developer.android.com/topic/performance/anrs/diagnose-and-fix-anrs

## Related Questions

### Prerequisites (Easier)
- [[q-what-unifies-android-components--android--easy]]
- [[q-what-is-broadcastreceiver--android--easy]]

### Related (Same Level)
- [[q-strictmode-debugging--android--medium]]
- [[q-multithreading-tools-android--android--medium]]

### Advanced (Harder)
- [[q-service-lifecycle-binding--android--hard]]