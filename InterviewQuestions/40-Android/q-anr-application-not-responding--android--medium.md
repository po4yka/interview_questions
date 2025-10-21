---
id: 20251012-122778
title: ANR (Application Not Responding) / ANR (Приложение не отвечает)
aliases: [ANR (Application Not Responding), ANR (Приложение не отвечает)]
topic: android
subtopics: [strictmode-anr, performance-rendering, profiling]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: reviewed
moc: moc-android
related: [q-android-performance-measurement-tools--android--medium, q-android-testing-strategies--android--medium, q-android-build-optimization--android--medium]
created: 2025-10-05
updated: 2025-10-15
tags: [android/strictmode-anr, android/performance-rendering, android/profiling, anr, performance, main-thread, debugging, difficulty/medium]
---
# Question (EN)
> What is ANR (Application Not Responding)?

# Вопрос (RU)
> Что такое ANR (Application Not Responding)?

---

## Answer (EN)

**ANR (Application Not Responding)** occurs when the UI thread of an Android app is blocked for too long, causing the system to display a dialog allowing users to force quit the app.

**ANR Theory:**
ANRs happen when the main thread, responsible for UI updates and user input processing, becomes unresponsive. The system monitors main thread responsiveness and triggers ANR dialogs when timeouts are exceeded.

**ANR Triggers:**
- **Input dispatching timeout**: No response to input events within 5 seconds
- **Service execution**: Service methods take too long to complete
- **Foreground service**: `startForeground()` not called within 5 seconds
- **Broadcast receiver**: Receiver doesn't finish within timeout period
- **JobScheduler**: Job service methods exceed time limits

**Common Causes:**

**System Issues:**
- Slow binder calls due to system server issues
- High device load preventing thread scheduling

**App Issues:**
- Blocking I/O operations on main thread
- Long calculations on main thread
- Synchronous binder calls to slow processes
- Lock contention with other threads
- Deadlocks between threads

**ANR Detection and Diagnosis:**

```kotlin
// Common ANR causes in code
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // BAD: Blocking I/O on main thread
        val data = File("large_file.txt").readText()

        // BAD: Long calculation on main thread
        val result = calculateFibonacci(40)

        // BAD: Synchronous network call
        val response = httpClient.get("https://api.example.com/data").execute()
    }
}

// GOOD: Move blocking operations off main thread
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch(Dispatchers.IO) {
            val data = File("large_file.txt").readText()
            val result = calculateFibonacci(40)
            val response = httpClient.get("https://api.example.com/data").execute()

            withContext(Dispatchers.Main) {
                // Update UI with results
            }
        }
    }
}
```

**ANR Prevention Strategies:**

**1. Keep Main Thread Unblocked:**
```kotlin
// Use background threads for heavy work
lifecycleScope.launch(Dispatchers.IO) {
    val result = performHeavyWork()
    withContext(Dispatchers.Main) {
        updateUI(result)
    }
}
```

**2. Optimize Service Operations:**
```kotlin
class MyService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Do minimal work here
        lifecycleScope.launch(Dispatchers.IO) {
            performBackgroundWork()
        }
        return START_STICKY
    }
}
```

**3. Use Async Broadcast Receivers:**
```kotlin
class MyReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val pendingResult = goAsync()
        Thread {
            // Do work in background
            performWork()
            pendingResult.finish()
        }.start()
    }
}
```

**4. Minimize Lock Contention:**
```kotlin
// BAD: Long operation holding lock
synchronized(lockObject) {
    performLongOperation()
    updateUI()
}

// GOOD: Minimize lock scope
val result = synchronized(lockObject) {
    performLongOperation()
}
updateUI(result)
```

**ANR Monitoring:**
- **Android Vitals**: Monitor ANR rates in Play Console
- **StrictMode**: Detect ANR-causing operations in debug builds
- **Profiling**: Use Android Studio Profiler to identify bottlenecks

**Best Practices:**
- Move all blocking I/O off main thread
- Use coroutines or background threads for heavy work
- Minimize work in lifecycle methods
- Optimize app startup time
- Use async operations for network calls
- Avoid tight loops on main thread
- Test on low-end devices

## Ответ (RU)

**ANR (Application Not Responding)** возникает, когда UI-поток приложения Android блокируется слишком долго, заставляя систему показывать диалог, позволяющий пользователям принудительно закрыть приложение.

**Теория ANR:**
ANR происходят, когда главный поток, ответственный за обновление UI и обработку пользовательского ввода, становится неотзывчивым. Система отслеживает отзывчивость главного потока и запускает диалоги ANR при превышении таймаутов.

**Триггеры ANR:**
- **Таймаут диспетчеризации ввода**: Нет ответа на события ввода в течение 5 секунд
- **Выполнение сервиса**: Методы сервиса занимают слишком много времени
- **Сервис переднего плана**: `startForeground()` не вызывается в течение 5 секунд
- **Широковещательный приемник**: Приемник не завершается в течение таймаута
- **JobScheduler**: Методы сервиса заданий превышают временные лимиты

**Распространенные причины:**

**Системные проблемы:**
- Медленные binder-вызовы из-за проблем системного сервера
- Высокая нагрузка устройства, препятствующая планированию потоков

**Проблемы приложения:**
- Блокирующие I/O операции в главном потоке
- Длительные вычисления в главном потоке
- Синхронные binder-вызовы к медленным процессам
- Конкуренция за блокировки с другими потоками
- Взаимные блокировки между потоками

**Обнаружение и диагностика ANR:**

```kotlin
// Распространенные причины ANR в коде
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // ПЛОХО: Блокирующий I/O в главном потоке
        val data = File("large_file.txt").readText()

        // ПЛОХО: Длительное вычисление в главном потоке
        val result = calculateFibonacci(40)

        // ПЛОХО: Синхронный сетевой вызов
        val response = httpClient.get("https://api.example.com/data").execute()
    }
}

// ХОРОШО: Переместить блокирующие операции с главного потока
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch(Dispatchers.IO) {
            val data = File("large_file.txt").readText()
            val result = calculateFibonacci(40)
            val response = httpClient.get("https://api.example.com/data").execute()

            withContext(Dispatchers.Main) {
                // Обновить UI с результатами
            }
        }
    }
}
```

**Стратегии предотвращения ANR:**

**1. Держите главный поток разблокированным:**
```kotlin
// Используйте фоновые потоки для тяжелой работы
lifecycleScope.launch(Dispatchers.IO) {
    val result = performHeavyWork()
    withContext(Dispatchers.Main) {
        updateUI(result)
    }
}
```

**2. Оптимизируйте операции сервиса:**
```kotlin
class MyService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Делайте минимальную работу здесь
        lifecycleScope.launch(Dispatchers.IO) {
            performBackgroundWork()
        }
        return START_STICKY
    }
}
```

**3. Используйте асинхронные широковещательные приемники:**
```kotlin
class MyReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val pendingResult = goAsync()
        Thread {
            // Делайте работу в фоне
            performWork()
            pendingResult.finish()
        }.start()
    }
}
```

**4. Минимизируйте конкуренцию за блокировки:**
```kotlin
// ПЛОХО: Длительная операция удерживает блокировку
synchronized(lockObject) {
    performLongOperation()
    updateUI()
}

// ХОРОШО: Минимизируйте область блокировки
val result = synchronized(lockObject) {
    performLongOperation()
}
updateUI(result)
```

**Мониторинг ANR:**
- **Android Vitals**: Отслеживайте частоту ANR в Play Console
- **StrictMode**: Обнаруживайте операции, вызывающие ANR, в отладочных сборках
- **Профилирование**: Используйте Android Studio Profiler для выявления узких мест

**Лучшие практики:**
- Переместите весь блокирующий I/O с главного потока
- Используйте корутины или фоновые потоки для тяжелой работы
- Минимизируйте работу в методах жизненного цикла
- Оптимизируйте время запуска приложения
- Используйте асинхронные операции для сетевых вызовов
- Избегайте плотных циклов в главном потоке
- Тестируйте на слабых устройствах

---

## Follow-ups

- How do you debug ANR issues in production?
- What's the difference between ANR and crash?
- How do you use StrictMode to detect ANR causes?
- What are the best practices for handling background tasks?

## References

- [Android ANR Documentation](https://developer.android.com/topic/performance/vitals/anr)
- [ANR Diagnosis Guide](https://developer.android.com/topic/performance/anrs/diagnose-and-fix-anrs)

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]]
- [[q-android-project-parts--android--easy]]

### Related (Same Level)
- [[q-android-performance-measurement-tools--android--medium]]
- [[q-android-testing-strategies--android--medium]]
- [[q-android-build-optimization--android--medium]]

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]]
