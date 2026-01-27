---
id: android-perf-005
title: Android Profiler Tools / Инструменты Android Profiler
aliases:
- Android Profiler
- CPU Profiler
- Memory Profiler
- Network Profiler
- Инструменты Профилирования
topic: android
subtopics:
- performance
- debugging
- profiling
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-memory-leaks-detection--performance--medium
- q-anr-debugging--performance--hard
- q-baseline-profiles--performance--hard
created: 2026-01-23
updated: 2026-01-23
tags:
- android/performance
- android/debugging
- difficulty/medium
- profiler
- cpu
- memory
- network
anki_cards:
- slug: android-perf-005-0-en
  language: en
- slug: android-perf-005-0-ru
  language: ru
---
# Вопрос (RU)

> Какие инструменты профилирования есть в Android Studio? Объясните CPU, Memory, Network и Energy Profiler.

# Question (EN)

> What profiling tools are available in Android Studio? Explain CPU, Memory, Network, and Energy Profiler.

---

## Ответ (RU)

**Android Profiler** -- это набор инструментов в Android Studio для анализа производительности приложения в реальном времени. Он помогает находить bottleneck-и в CPU, памяти, сети и энергопотреблении.

### Краткий Ответ

- **CPU Profiler** -- анализ использования CPU, трейсы методов, flame charts
- **Memory Profiler** -- heap dump, отслеживание аллокаций, утечки памяти
- **Network Profiler** -- мониторинг сетевых запросов, тела запросов/ответов
- **Energy Profiler** -- анализ энергопотребления, wakelocks, jobs

### Подробный Ответ

### Открытие Profiler

```
View -> Tool Windows -> Profiler
или
Run -> Profile 'app'

Требования:
- debuggable = true в build.gradle
- Подключённое устройство или эмулятор
- API 26+ для полной функциональности
```

### CPU Profiler

#### Типы Записи

```kotlin
// 1. Sample Java/Kotlin Methods (лёгкий, рекомендуется)
// Захватывает стек каждые ~1ms

// 2. Trace Java/Kotlin Methods (тяжёлый, детальный)
// Записывает вход/выход каждого метода

// 3. Sample C/C++ Functions
// Для NDK кода

// 4. Trace System Calls
// Systrace для системных событий
```

#### Программная Запись

```kotlin
class MyActivity : AppCompatActivity() {

    fun profileHeavyOperation() {
        // Начинаем запись
        Debug.startMethodTracing("my_trace")

        // Код для профилирования
        heavyOperation()

        // Останавливаем запись
        Debug.stopMethodTracing()

        // Файл: /sdcard/Android/data/<package>/files/my_trace.trace
    }
}
```

#### Чтение Flame Chart

```
Flame Chart показывает:
- Ось X: время выполнения
- Ось Y: глубина стека вызовов
- Ширина блока: время в методе

Цвета:
- Зелёный: системные методы
- Синий: third-party библиотеки
- Оранжевый: ваш код

Ищите:
- Широкие блоки (долгие методы)
- Глубокие стеки (много вложенных вызовов)
- Повторяющиеся паттерны (лишние вызовы)
```

#### Top Down / Bottom Up

```kotlin
// Top Down: от вызывающего к вызываемому
main()
  └── onCreate()
        └── loadData()
              └── parseJson()

// Bottom Up: от самого времязатратного вверх
parseJson() ← 500ms
  ← loadData()
    ← onCreate()
      ← main()
```

### Memory Profiler

#### Live Allocations

```kotlin
// Включить запись аллокаций в реальном времени
// Показывает:
// - Количество объектов каждого типа
// - Размер аллокаций
// - Stack trace создания

class AllocationTracker {
    fun trackAllocations() {
        // В Profiler видим все new Object()
        val list = mutableListOf<String>()
        repeat(10000) {
            list.add("Item $it") // Видим 10000 String аллокаций
        }
    }
}
```

#### Heap Dump Analysis

```kotlin
// Capture Heap Dump -> Analyze

// Ключевые метрики:
// - Allocations: количество объектов
// - Shallow Size: размер самого объекта
// - Retained Size: размер + все удерживаемые объекты

// Поиск утечек:
// 1. Выполнить действие (открыть/закрыть Activity)
// 2. Force GC несколько раз
// 3. Capture Heap Dump
// 4. Искать Activity по имени класса
// 5. Если найден после закрытия -> утечка
```

#### Программный Heap Dump

```kotlin
fun captureHeapDump(context: Context) {
    val heapFile = File(context.cacheDir, "heap_${System.currentTimeMillis()}.hprof")
    Debug.dumpHprofData(heapFile.absolutePath)

    // Анализируем в Android Studio:
    // File -> Open -> выбрать .hprof файл
}
```

### Network Profiler

#### Возможности

```kotlin
// Network Profiler показывает:
// - Timeline всех сетевых запросов
// - Размер отправленных/полученных данных
// - Время каждого запроса
// - Тела запросов/ответов (API 26+)

// Для OkHttp автоматически работает
// Для других клиентов может потребоваться настройка
```

#### Network Inspector (API 26+)

```kotlin
// Показывает детали каждого запроса:
// - URL
// - Method (GET, POST, etc.)
// - Headers
// - Request/Response Body
// - Timing (DNS, Connect, SSL, Request, Response)

// Пример анализа:
// 1. Запрос занял 2 секунды
// 2. Смотрим timing breakdown
// 3. DNS: 500ms -> возможно проблема с DNS
// 4. Response: 1500ms -> большой response или медленный сервер
```

#### Программное Логирование

```kotlin
// OkHttp Interceptor для детального логирования
val client = OkHttpClient.Builder()
    .addInterceptor(HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    })
    .addInterceptor { chain ->
        val request = chain.request()
        val startTime = System.currentTimeMillis()

        val response = chain.proceed(request)

        val duration = System.currentTimeMillis() - startTime
        Log.d("Network", "${request.url} took ${duration}ms")

        response
    }
    .build()
```

### Energy Profiler

#### Компоненты Анализа

```kotlin
// Energy Profiler показывает:
// - CPU использование
// - Network активность
// - GPS использование
// - Wakelocks
// - Jobs и Alarms

// Оптимизация энергопотребления:
// 1. Группировать сетевые запросы (batching)
// 2. Использовать WorkManager вместо AlarmManager
// 3. Освобождать wakelocks
// 4. Минимизировать GPS использование
```

#### Wake Locks

```kotlin
// ПЛОХО -- держим wakelock слишком долго
val wakeLock = powerManager.newWakeLock(
    PowerManager.PARTIAL_WAKE_LOCK,
    "MyApp::MyWakeLock"
)
wakeLock.acquire() // Забыли release!

// ХОРОШО -- ограниченный wakelock
wakeLock.acquire(10 * 60 * 1000L) // Максимум 10 минут
try {
    doWork()
} finally {
    if (wakeLock.isHeld) {
        wakeLock.release()
    }
}
```

### System Trace (Perfetto)

```kotlin
// Запись System Trace в коде
class TracingExample {

    fun tracedMethod() {
        Trace.beginSection("MyMethod")
        try {
            // Код для трейса
            processData()
        } finally {
            Trace.endSection()
        }
    }

    // Или suspend функция
    suspend fun tracedSuspend() = trace("MyCoroutine") {
        delay(100)
        processData()
    }
}
```

### Benchmarking

```kotlin
// Microbenchmark для точных измерений
@RunWith(AndroidJUnit4::class)
class MyBenchmark {

    @get:Rule
    val benchmarkRule = BenchmarkRule()

    @Test
    fun benchmarkSomeOperation() {
        benchmarkRule.measureRepeated {
            // Код для измерения
            runWithTimingDisabled {
                // Setup код (не измеряется)
            }

            // Измеряемый код
            someOperation()
        }
    }
}
```

### Чеклист Профилирования

| Проблема | Инструмент | Что Искать |
|----------|------------|------------|
| Jank/лаги | CPU Profiler | Долгие методы на main thread |
| OOM | Memory Profiler | Большие объекты, утечки |
| Медленная сеть | Network Profiler | Большие запросы, много запросов |
| Быстрая разрядка | Energy Profiler | Wakelocks, GPS, постоянная сеть |
| Медленный старт | CPU + System Trace | Инициализация в onCreate |

---

## Answer (EN)

**Android Profiler** is a set of tools in Android Studio for analyzing app performance in real-time. It helps find bottlenecks in CPU, memory, network, and energy consumption.

### Short Answer

- **CPU Profiler** -- CPU usage analysis, method traces, flame charts
- **Memory Profiler** -- heap dump, allocation tracking, memory leaks
- **Network Profiler** -- network request monitoring, request/response bodies
- **Energy Profiler** -- energy consumption analysis, wakelocks, jobs

### Detailed Answer

### Opening Profiler

```
View -> Tool Windows -> Profiler
or
Run -> Profile 'app'

Requirements:
- debuggable = true in build.gradle
- Connected device or emulator
- API 26+ for full functionality
```

### CPU Profiler

#### Recording Types

```kotlin
// 1. Sample Java/Kotlin Methods (lightweight, recommended)
// Captures stack every ~1ms

// 2. Trace Java/Kotlin Methods (heavy, detailed)
// Records entry/exit of every method

// 3. Sample C/C++ Functions
// For NDK code

// 4. Trace System Calls
// Systrace for system events
```

#### Programmatic Recording

```kotlin
class MyActivity : AppCompatActivity() {

    fun profileHeavyOperation() {
        // Start recording
        Debug.startMethodTracing("my_trace")

        // Code to profile
        heavyOperation()

        // Stop recording
        Debug.stopMethodTracing()

        // File: /sdcard/Android/data/<package>/files/my_trace.trace
    }
}
```

#### Reading Flame Chart

```
Flame Chart shows:
- X-axis: execution time
- Y-axis: call stack depth
- Block width: time in method

Colors:
- Green: system methods
- Blue: third-party libraries
- Orange: your code

Look for:
- Wide blocks (long-running methods)
- Deep stacks (many nested calls)
- Repeated patterns (unnecessary calls)
```

#### Top Down / Bottom Up

```kotlin
// Top Down: from caller to callee
main()
  └── onCreate()
        └── loadData()
              └── parseJson()

// Bottom Up: from most time-consuming up
parseJson() ← 500ms
  ← loadData()
    ← onCreate()
      ← main()
```

### Memory Profiler

#### Live Allocations

```kotlin
// Enable real-time allocation recording
// Shows:
// - Object count by type
// - Allocation size
// - Creation stack trace

class AllocationTracker {
    fun trackAllocations() {
        // In Profiler we see all new Object()
        val list = mutableListOf<String>()
        repeat(10000) {
            list.add("Item $it") // See 10000 String allocations
        }
    }
}
```

#### Heap Dump Analysis

```kotlin
// Capture Heap Dump -> Analyze

// Key metrics:
// - Allocations: object count
// - Shallow Size: object's own size
// - Retained Size: size + all retained objects

// Finding leaks:
// 1. Perform action (open/close Activity)
// 2. Force GC several times
// 3. Capture Heap Dump
// 4. Search for Activity by class name
// 5. If found after closing -> leak
```

#### Programmatic Heap Dump

```kotlin
fun captureHeapDump(context: Context) {
    val heapFile = File(context.cacheDir, "heap_${System.currentTimeMillis()}.hprof")
    Debug.dumpHprofData(heapFile.absolutePath)

    // Analyze in Android Studio:
    // File -> Open -> select .hprof file
}
```

### Network Profiler

#### Features

```kotlin
// Network Profiler shows:
// - Timeline of all network requests
// - Sent/received data size
// - Time for each request
// - Request/response bodies (API 26+)

// Works automatically for OkHttp
// Other clients may require configuration
```

#### Network Inspector (API 26+)

```kotlin
// Shows details for each request:
// - URL
// - Method (GET, POST, etc.)
// - Headers
// - Request/Response Body
// - Timing (DNS, Connect, SSL, Request, Response)

// Analysis example:
// 1. Request took 2 seconds
// 2. Look at timing breakdown
// 3. DNS: 500ms -> possible DNS issue
// 4. Response: 1500ms -> large response or slow server
```

#### Programmatic Logging

```kotlin
// OkHttp Interceptor for detailed logging
val client = OkHttpClient.Builder()
    .addInterceptor(HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    })
    .addInterceptor { chain ->
        val request = chain.request()
        val startTime = System.currentTimeMillis()

        val response = chain.proceed(request)

        val duration = System.currentTimeMillis() - startTime
        Log.d("Network", "${request.url} took ${duration}ms")

        response
    }
    .build()
```

### Energy Profiler

#### Analysis Components

```kotlin
// Energy Profiler shows:
// - CPU usage
// - Network activity
// - GPS usage
// - Wakelocks
// - Jobs and Alarms

// Energy optimization:
// 1. Batch network requests
// 2. Use WorkManager instead of AlarmManager
// 3. Release wakelocks
// 4. Minimize GPS usage
```

#### Wake Locks

```kotlin
// BAD -- holding wakelock too long
val wakeLock = powerManager.newWakeLock(
    PowerManager.PARTIAL_WAKE_LOCK,
    "MyApp::MyWakeLock"
)
wakeLock.acquire() // Forgot to release!

// GOOD -- limited wakelock
wakeLock.acquire(10 * 60 * 1000L) // Maximum 10 minutes
try {
    doWork()
} finally {
    if (wakeLock.isHeld) {
        wakeLock.release()
    }
}
```

### System Trace (Perfetto)

```kotlin
// Recording System Trace in code
class TracingExample {

    fun tracedMethod() {
        Trace.beginSection("MyMethod")
        try {
            // Code to trace
            processData()
        } finally {
            Trace.endSection()
        }
    }

    // Or suspend function
    suspend fun tracedSuspend() = trace("MyCoroutine") {
        delay(100)
        processData()
    }
}
```

### Benchmarking

```kotlin
// Microbenchmark for precise measurements
@RunWith(AndroidJUnit4::class)
class MyBenchmark {

    @get:Rule
    val benchmarkRule = BenchmarkRule()

    @Test
    fun benchmarkSomeOperation() {
        benchmarkRule.measureRepeated {
            // Code to measure
            runWithTimingDisabled {
                // Setup code (not measured)
            }

            // Measured code
            someOperation()
        }
    }
}
```

### Profiling Checklist

| Problem | Tool | What to Look For |
|---------|------|------------------|
| Jank/lag | CPU Profiler | Long methods on main thread |
| OOM | Memory Profiler | Large objects, leaks |
| Slow network | Network Profiler | Large requests, many requests |
| Fast drain | Energy Profiler | Wakelocks, GPS, constant network |
| Slow startup | CPU + System Trace | Initialization in onCreate |

---

## Ссылки (RU)

- [Android Profiler](https://developer.android.com/studio/profile/android-profiler)
- [CPU Profiler](https://developer.android.com/studio/profile/cpu-profiler)
- [Memory Profiler](https://developer.android.com/studio/profile/memory-profiler)
- [Network Profiler](https://developer.android.com/studio/profile/network-profiler)

## References (EN)

- [Android Profiler](https://developer.android.com/studio/profile/android-profiler)
- [CPU Profiler](https://developer.android.com/studio/profile/cpu-profiler)
- [Memory Profiler](https://developer.android.com/studio/profile/memory-profiler)
- [Network Profiler](https://developer.android.com/studio/profile/network-profiler)

## Follow-ups (EN)

- How to profile release builds?
- What is the difference between sampling and tracing?
- How to use Perfetto for advanced system tracing?
- How to profile Jetpack Compose performance?

## Дополнительные Вопросы (RU)

- Как профилировать release сборки?
- В чём разница между sampling и tracing?
- Как использовать Perfetto для продвинутого системного трейсинга?
- Как профилировать производительность Jetpack Compose?
