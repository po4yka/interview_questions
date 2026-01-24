---
id: android-003
title: ANR (Application Not Responding) / ANR (Приложение не отвечает)
aliases:
- ANR (Application Not Responding)
- ANR (Приложение не отвечает)
topic: android
subtopics:
- performance-rendering
- profiling
- strictmode-anr
question_kind: android
difficulty: medium
original_language: ru
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-lifecycle
- q-android-app-lag-analysis--android--medium
- q-optimize-memory-usage-android--android--medium
- q-performance-monitoring-jank-compose--android--medium
- q-recomposition-compose--android--medium
created: 2025-10-05
updated: 2025-11-10
sources: []
tags:
- android/performance-rendering
- android/profiling
- android/strictmode-anr
- debugging
- difficulty/medium
- performance
anki_cards:
- slug: android-003-0-en
  language: en
  anki_id: 1768364267073
  synced_at: '2026-01-23T16:45:05.662956'
- slug: android-003-0-ru
  language: ru
  anki_id: 1768364267096
  synced_at: '2026-01-23T16:45:05.664453'
---
# Вопрос (RU)
> Что такое ANR (`Application` Not Responding) и как его предотвратить?

# Question (EN)
> What is ANR (`Application` Not Responding) and how to prevent it?

---

## Ответ (RU)

**ANR (`Application` Not Responding)** — состояние, когда приложение слишком долго не отвечает на важные события (ввод пользователя, broadcast, операции сервиса) из-за блокировки или перегрузки UI-потока. В этом случае система показывает ANR-диалог, и при выборе пользователем — может завершить приложение.

**Типы ANR с типичными таймаутами (могут отличаться по версии/устройству):**

- **Input dispatching**: нет ответа на ввод в течение ~5 секунд (main thread не обрабатывает input events)
- **`BroadcastReceiver`**: onReceive не завершается за ~10 секунд
- **`Service`**:
  - стартованный сервис в фоне: долгий вызов (обычно ~20 секунд)
  - сервис, работающий на переднем плане (foreground): допускается существенно больше времени (исторически до ~200 секунд), но длительные синхронные операции всё равно рискованны и должны выноситься из main thread

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

**`BroadcastReceiver` и goAsync():**

```kotlin
// ✅ goAsync() для асинхронной работы (не забыть быстро завершить и вызвать finish())
class MyReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val pendingResult = goAsync()
        CoroutineScope(Dispatchers.IO).launch {
            try {
                database.insert(data) // краткая операция, не использовать для долгих задач
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
- **ANR traces** (через bugreport, Android Vitals или `/data/anr/traces.txt` на dev/root окружениях): stacktrace всех потоков в момент ANR
- **Firebase Crashlytics**: автоматический сбор ANR-отчетов (современные версии SDK)

**Стратегии предотвращения:**

1. Main thread только для лёгких UI-операций; длительные операции должны выполняться в фоне (лимиты ANR — секунды, но ориентируемся на быструю реакцию и избегаем блокировок).
2. `WorkManager` для долгих и отложенных фоновых задач.
3. Минимум тяжёлой работы в lifecycle callbacks (onCreate, onResume).
4. Избегать длинных synchronized-блоков и других блокирующих примитивов на main thread.
5. Использовать Dispatchers.IO для I/O, Dispatchers.Default для CPU-задач.

---

## Answer (EN)

**ANR (`Application` Not Responding)** is a state where the app takes too long to respond to critical events (user input, broadcasts, service operations) due to the UI thread being blocked or overloaded. In this case, the system shows an ANR dialog, and if the user chooses, the app process may be killed.

**ANR types with typical timeouts (may vary by version/device):**

- **Input dispatching**: no response to input within ~5 seconds (main thread not processing input events)
- **`BroadcastReceiver`**: onReceive does not finish within ~10 seconds
- **`Service`**:
  - started/background service: long-running call (usually ~20 seconds)
  - foreground service: significantly higher limit (historically up to ~200 seconds), but long synchronous work on the main thread is still risky and should be offloaded

**Common causes of main thread blocking:**

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

**`BroadcastReceiver` and goAsync():**

```kotlin
// ✅ goAsync() for asynchronous work (must finish quickly and call finish())
class MyReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val pendingResult = goAsync()
        CoroutineScope(Dispatchers.IO).launch {
            try {
                database.insert(data) // short operation, do not use for very long tasks
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
- **ANR traces** (via bugreport, Android Vitals, or `/data/anr/traces.txt` on dev/root environments): stack traces of all threads at the moment of ANR
- **Firebase Crashlytics**: automatic ANR report collection (in recent SDK versions)

**Prevention Strategies:**

1. Use the main thread only for lightweight UI work; move long-running operations off the main thread (ANR limits are in seconds, but you target fast responsiveness and avoid blocking).
2. Use `WorkManager` for long-running and deferrable background work.
3. Minimize heavy work in lifecycle callbacks (onCreate, onResume).
4. Avoid long synchronized blocks and other blocking primitives on the main thread.
5. Use Dispatchers.IO for I/O, Dispatchers.Default for CPU-intensive tasks.

---

## Дополнительные Вопросы (Follow-ups, RU)

- Как анализировать ANR-трейсы из `/data/anr/traces.txt` (или bugreport/Android Vitals), чтобы найти корневую причину блокировки?
- В чем разница между использованием `WorkManager` и корутин для предотвращения ANR в долгих задачах?
- Чем StrictMode `penaltyDeath()` отличается от `penaltyLog()` в контексте обнаружения проблем, приводящих к ANR?
- Допустимы ли краткие I/O-операции (< 50 мс) на главном потоке и в каких случаях?
- Как обрабатывать ANR, вызванные сторонними SDK или системными Binder-вызовами, которые сложно контролировать?

## Follow-ups

- How do you analyze ANR traces from `/data/anr/traces.txt` (or bugreports/Android Vitals) to identify the root cause of blocking?
- What's the difference between `WorkManager` and coroutines for preventing ANRs in long-running tasks?
- How does StrictMode penaltyDeath() differ from penaltyLog() in ANR detection?
- Can brief I/O operations (< 50ms) ever be acceptable on the main thread, and when?
- How do you handle ANRs caused by third-party SDKs or system Binder calls beyond your control?

---

## Ссылки (RU)

- [[c-lifecycle]]
- [[c-coroutines]]
- [ANRs](https://developer.android.com/topic/performance/vitals/anr)
- https://developer.android.com/topic/performance/anrs/diagnose-and-fix-anrs

## References

- [[c-lifecycle]]
- [[c-coroutines]]
- [ANRs](https://developer.android.com/topic/performance/vitals/anr)
- https://developer.android.com/topic/performance/anrs/diagnose-and-fix-anrs

---

## Связанные Вопросы (RU)

### Предварительные (проще)
- [[q-android-app-components--android--easy]] — понимание компонентов и их жизненного цикла
- [[q-android-app-lag-analysis--android--medium]] — анализ лагов и производительности

### Связанные (тот Же уровень)
- [[q-strictmode-debugging--android--medium]] — использование StrictMode для отладки производительности
- [[q-android-performance-measurement-tools--android--medium]] — инструменты измерения производительности на Android

### Продвинутые (сложнее)
- [[q-service-lifecycle-binding--android--hard]] — продвинутые паттерны работы с сервисами
- Глубокий performance-профайлинг (CPU, I/O, Binder, lock contention)

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - Understanding Android components and lifecycle
- [[q-android-app-lag-analysis--android--medium]] - Analyzing app lags and performance issues

### Related (Same Level)
- [[q-strictmode-debugging--android--medium]] - Using StrictMode for performance debugging
- [[q-android-performance-measurement-tools--android--medium]] - Android performance measurement tools

### Advanced (Harder)
- [[q-service-lifecycle-binding--android--hard]] - Advanced service patterns
- Deep performance profiling (CPU, I/O, Binder, lock contention)
