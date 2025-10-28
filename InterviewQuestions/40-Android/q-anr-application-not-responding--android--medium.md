---
id: 20251012-122778
title: ANR (Application Not Responding) / ANR (Приложение не отвечает)
aliases: ["ANR (Application Not Responding)", "ANR (Приложение не отвечает)"]
topic: android
subtopics: [performance-rendering, profiling, strictmode-anr]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-build-optimization--android--medium, q-android-performance-measurement-tools--android--medium, q-android-testing-strategies--android--medium]
created: 2025-10-05
updated: 2025-10-28
sources: []
tags: [android/performance-rendering, android/profiling, android/strictmode-anr, difficulty/medium]
---
# Вопрос (RU)
> Что такое ANR (Приложение не отвечает)?

## Ответ (RU)

**ANR (Application Not Responding)** — это ошибка, возникающая когда UI-поток Android-приложения блокируется на слишком длительное время. Система отображает диалог, позволяющий пользователю принудительно завершить приложение.

**Причины возникновения ANR:**

Main-поток (UI-поток) отвечает за обработку пользовательского ввода и обновление интерфейса. Android-система мониторит отзывчивость этого потока и показывает ANR-диалог при превышении таймаутов:

- **Input dispatching timeout**: Нет ответа на события ввода в течение 5 секунд
- **Service timeout**: Методы сервиса выполняются слишком долго (20 сек для фоновых, 10 сек для foreground)
- **BroadcastReceiver timeout**: Receiver не завершается в пределах 10 секунд

**Типичные ошибки:**

```kotlin
// ❌ ПЛОХО: Блокирующие операции на main thread
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val data = File("large_file.txt").readText()  // I/O блокировка
        val result = calculateFibonacci(40)            // CPU-интенсивная операция
        val response = httpClient.get(url).execute()   // Синхронный network call
    }
}

// ✅ ХОРОШО: Асинхронное выполнение с корутинами
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch(Dispatchers.IO) {
            val data = File("large_file.txt").readText()
            withContext(Dispatchers.Main) {
                updateUI(data)  // Обновление UI на main thread
            }
        }
    }
}
```

**Предотвращение ANR:**

1. **Используйте WorkManager** для длительных фоновых операций
2. **Минимизируйте работу в lifecycle callbacks** (onCreate, onStart)
3. **Избегайте синхронизации с длинными блокировками**
4. **Используйте goAsync()** в BroadcastReceiver для асинхронной работы

**Диагностика в production:**

- **Android Vitals** в Play Console показывает ANR rate
- **ANR traces** (`/data/anr/traces.txt`) содержат стек всех потоков в момент ANR
- **StrictMode** помогает детектировать ANR-причины во время разработки

```kotlin
// Включение StrictMode для детекции проблем
if (BuildConfig.DEBUG) {
    StrictMode.setThreadPolicy(
        StrictMode.ThreadPolicy.Builder()
            .detectDiskReads()
            .detectDiskWrites()
            .detectNetwork()
            .penaltyLog()
            .build()
    )
}
```

**Ключевой принцип:** Main thread должен выполнять только лёгкие UI-операции (< 16ms для 60 FPS). Всё остальное — на background потоки или корутины с Dispatchers.IO/Default.

---

# Question (EN)
> What is ANR (Application Not Responding)?

## Answer (EN)

**ANR (Application Not Responding)** is an error that occurs when the Android UI thread is blocked for too long. The system displays a dialog allowing the user to force close the application.

**ANR Triggers:**

The main thread handles user input and UI updates. The Android system monitors thread responsiveness and shows an ANR dialog when timeouts are exceeded:

- **Input dispatching timeout**: No response to input events within 5 seconds
- **Service timeout**: Service methods take too long (20 sec for background, 10 sec for foreground)
- **BroadcastReceiver timeout**: Receiver doesn't finish within 10 seconds

**Common Mistakes:**

```kotlin
// ❌ BAD: Blocking operations on main thread
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val data = File("large_file.txt").readText()  // I/O blocking
        val result = calculateFibonacci(40)            // CPU-intensive operation
        val response = httpClient.get(url).execute()   // Synchronous network call
    }
}

// ✅ GOOD: Asynchronous execution with coroutines
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch(Dispatchers.IO) {
            val data = File("large_file.txt").readText()
            withContext(Dispatchers.Main) {
                updateUI(data)  // Update UI on main thread
            }
        }
    }
}
```

**ANR Prevention:**

1. **Use WorkManager** for long-running background operations
2. **Minimize work in lifecycle callbacks** (onCreate, onStart)
3. **Avoid synchronization with long locks**
4. **Use goAsync()** in BroadcastReceiver for async work

**Production Diagnostics:**

- **Android Vitals** in Play Console shows ANR rate
- **ANR traces** (`/data/anr/traces.txt`) contain stack traces of all threads at ANR time
- **StrictMode** helps detect ANR causes during development

```kotlin
// Enable StrictMode for problem detection
if (BuildConfig.DEBUG) {
    StrictMode.setThreadPolicy(
        StrictMode.ThreadPolicy.Builder()
            .detectDiskReads()
            .detectDiskWrites()
            .detectNetwork()
            .penaltyLog()
            .build()
    )
}
```

**Key principle:** Main thread should only handle lightweight UI operations (< 16ms for 60 FPS). Everything else goes to background threads or coroutines with Dispatchers.IO/Default.

---

## Follow-ups

- How do you analyze ANR traces in production to identify root causes?
- What's the relationship between ANR rate and app quality metrics in Play Console?
- How does Baseline Profiles optimization help reduce ANR occurrences?
- When should you use WorkManager vs coroutines for background operations?
- How do you handle ANRs caused by system-level issues (e.g., slow Binder calls)?

## References

- [Android ANR Documentation](https://developer.android.com/topic/performance/vitals/anr)
- [Diagnose and Fix ANRs](https://developer.android.com/topic/performance/anrs/diagnose-and-fix-anrs)
- [[c-coroutines]]

## Related Questions

### Prerequisites
- [[q-android-app-components--android--easy]] — Understanding Android components and their lifecycle
- [[q-android-project-parts--android--easy]] — Basic Android application structure

### Related
- [[q-android-performance-measurement-tools--android--medium]] — Tools for measuring and profiling performance
- [[q-android-testing-strategies--android--medium]] — Testing approaches including performance testing
- [[q-android-build-optimization--android--medium]] — Build optimizations that can affect app performance

### Advanced
- [[q-android-runtime-internals--android--hard]] — Deep dive into Android runtime architecture
- Questions about memory leaks and their impact on ANR
- Questions about Binder IPC and cross-process communication performance