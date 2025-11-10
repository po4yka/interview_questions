---
id: android-336
title: Типы запуска приложения в Android / App Start Types Android
aliases: ["Типы запуска приложения в Android", "App Start Types Android"]
topic: android
subtopics: [performance-startup]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-performance-measurement-tools--android--medium]
sources: []
created: 2025-10-15
updated: 2025-11-10
tags: [android/performance-startup, difficulty/medium, performance, startup]

---

# Вопрос (RU)
> Какие существуют типы запуска Android-приложения (cold/warm/hot), и как оптимизировать каждый из них?

# Question (EN)
> What are the Android app start types and how do you optimize each?

---

## Ответ (RU)

Три типа запуска Android-приложения определяются состоянием процесса:
- **Cold старт (холодный)**: процесс приложения отсутствует; системе нужно создать процесс и инициализировать приложение.
- **Warm старт (тёплый)**: процесс жив, но приложение не на экране; `Activity` и/или её состояние нужно пересоздать или реинициализировать.
- **Hot старт (горячий)**: процесс жив, та же `Activity` остаётся в памяти; требуется только возобновить UI.

Каждый тип требует своей стратегии оптимизации и измерения метрик.

### Метрики запуска

- **TTID (Time To Initial Display)**: время до отображения первого кадра UI.
- **TTFD (Time To Full Display)**: время до полного отображения `Activity` и готовности к взаимодействию; сигнализируется через `reportFullyDrawn()`.
- **Инструменты**: Android Vitals (прод), Macrobenchmark (CI), Perfetto (локальный профилинг).

```kotlin
// Сигнализируем готовность полностью отрисованного экрана
class MainActivity : AppCompatActivity() {
    override fun onResume() {
        super.onResume()
        window.decorView.post { reportFullyDrawn() }
    }
}
```

### Cold Start (холодный запуск)

**Цель**: минимизировать критический путь (старт процесса → первый кадр).

```kotlin
// Контролируем инициализацию + откладываем тяжёлые операции
class App : Application() {
    override fun onCreate() {
        super.onCreate()
        if (BuildConfig.DEBUG) {
            StrictMode.setThreadPolicy(
                StrictMode.ThreadPolicy.Builder()
                    .detectAll()
                    .penaltyLog()
                    .build()
            )
        }
        initCrashReporting()  // только действительно критичный функционал
        // Тяжёлые SDK откладываем за пределы критического пути запуска
        Handler(Looper.getMainLooper()).post {
            initAnalytics()
            initAds()
        }
    }
}
```

**Baseline profiles**: предварительная компиляция горячих путей для снижения зависимости от прогрева JIT.

### Warm Start (тёплый запуск)

**Цель**: быстрое восстановление UI/состояния, когда процесс уже жив.

```kotlin
// ViewModel + SavedStateHandle помогают избежать лишних пересозданий состояния
class MainVm(state: SavedStateHandle) : ViewModel() {
    val uiState = state.getLiveData("ui", defaultState())
}

// Минимум работы в onCreate
class MainActivity : AppCompatActivity() {
    private val vm by viewModels<MainVm>()
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        savedInstanceState?.getString("q")?.let { restoreQuery(it) }
    }
}
```

### Hot Start (горячий запуск)

**Цель**: минимальная работа в `onResume`, батчинг обновлений.

```kotlin
// Lifecycle-aware возобновление работы только в нужных состояниях
class MainActivity : AppCompatActivity() {
    override fun onResume() {
        super.onResume()
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                refreshIfStale()
            }
        }
    }
}
```

### Бюджеты и ограничения

- **Рекомендуемые целевые бюджеты** (не официальные гарантии): Cold < 500ms, Warm < 300ms, Hot < 100ms (зависят от устройства и категории приложения).
- **Запрещено**: выполнять диск/сеть на главном потоке во время запуска.
- **CI**: сценарии с Macrobenchmark с порогами и алертами на регрессии.

---

## Answer (EN)

**Three Android app start types** are defined by process state:
- **Cold** start: no app process exists; the system must create the process and initialize the app.
- **Warm** start: process is alive but app is not currently visible; the `Activity` and/or its state must be recreated or re-initialized.
- **Hot** start: process is alive and the same `Activity` remains in memory; only UI resume is needed.

Each type requires specific optimization with measurable metrics.

### Startup Metrics

- **TTID (Time To Initial Display)**: time to the first UI frame.
- **TTFD (Time To Full Display)**: time until the `Activity` is fully drawn and ready for user interaction; signaled via `reportFullyDrawn()`.
- **Tools**: Android Vitals (prod), Macrobenchmark (CI), Perfetto (local profiling).

```kotlin
// Signal full display readiness
class MainActivity : AppCompatActivity() {
    override fun onResume() {
        super.onResume()
        window.decorView.post { reportFullyDrawn() }
    }
}
```

### Cold Start

**Goal**: minimize the critical path (process start → first frame).

```kotlin
// Initialization control + deferred loading
class App : Application() {
    override fun onCreate() {
        super.onCreate()
        if (BuildConfig.DEBUG) {
            StrictMode.setThreadPolicy(
                StrictMode.ThreadPolicy.Builder()
                    .detectAll()
                    .penaltyLog()
                    .build()
            )
        }
        initCrashReporting()  // critical only
        // Heavy SDKs deferred until after the critical path
        Handler(Looper.getMainLooper()).post {
            initAnalytics()
            initAds()
        }
    }
}
```

**Baseline profiles**: precompile hot paths to reduce reliance on JIT warmup.

### Warm Start

**Goal**: fast UI/state reconstruction when the process is already alive.

```kotlin
// ViewModel + SavedStateHandle to avoid unnecessary recomputation
class MainVm(state: SavedStateHandle) : ViewModel() {
    val uiState = state.getLiveData("ui", defaultState())
}

// Minimal work in onCreate
class MainActivity : AppCompatActivity() {
    private val vm by viewModels<MainVm>()
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        savedInstanceState?.getString("q")?.let { restoreQuery(it) }
    }
}
```

### Hot Start

**Goal**: minimal `onResume` work, batched updates.

```kotlin
// Lifecycle-aware flow resumption
class MainActivity : AppCompatActivity() {
    override fun onResume() {
        super.onResume()
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                refreshIfStale()
            }
        }
    }
}
```

### Budgets and Guardrails

- **Suggested target budgets** (not official guarantees): Cold < 500ms, Warm < 300ms, Hot < 100ms (vary by device and app category).
- **Prohibitions**: no disk/network operations on the main thread during startup.
- **CI**: Macrobenchmark library scenarios with thresholds and regression alerts.

---

## Follow-ups (RU)

- Как генерация baseline-профилей влияет на разные типы запуска и какие метрики улучшаются сильнее всего?
- Как порядок инициализации `ContentProvider` влияет на производительность холодного запуска?
- Как измерять и жестко контролировать бюджеты запуска в CI без флаки-тестов?
- Когда стоит использовать библиотеку App Startup, а когда — ручную ленивую инициализацию SDK?
- Чем отличается восстановление после убийства процесса от конфигурационных изменений с точки зрения оптимизации тёплого старта?

## Follow-ups (EN)

- How does baseline profile generation affect different start types and which metrics improve the most?
- How does the initialization order of `ContentProvider` impact cold start performance?
- How can you measure and strictly enforce startup budgets in CI without flaky tests?
- When should you use the App Startup library vs. manual lazy SDK initialization?
- How does recovery after process death differ from configuration changes in terms of warm start optimization?

## References (RU)

- https://developer.android.com/topic/performance/vitals/launch-time - руководство по производительности запуска
- https://developer.android.com/topic/libraries/app-startup - документация по библиотеке App Startup
- https://developer.android.com/topic/performance/baselineprofiles - руководство по baseline-профилям

## References (EN)

- https://developer.android.com/topic/performance/vitals/launch-time - launch performance guide
- https://developer.android.com/topic/libraries/app-startup - App Startup library documentation
- https://developer.android.com/topic/performance/baselineprofiles - baseline profiles guide

## Related Questions (RU)

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - фундаментальные компоненты Android-приложения

### Related (Same Level)
- [[q-android-performance-measurement-tools--android--medium]] - инструменты профилирования и бенчмаркинга
- [[q-android-app-lag-analysis--android--medium]] - анализ лагов и просадок FPS
- [[q-android-build-optimization--android--medium]] - оптимизация сборки и сопутствующей инфраструктуры

### Advanced (Harder)
- Оптимизация жизненного цикла процесса и использования памяти
- Предотвращение блокировок главного потока и ANR

## Related Questions (EN)

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - core Android application components

### Related (Same Level)
- [[q-android-performance-measurement-tools--android--medium]] - profiling and benchmarking tools
- [[q-android-app-lag-analysis--android--medium]] - analyzing jank and FPS drops
- [[q-android-build-optimization--android--medium]] - build optimization and related infrastructure

### Advanced (Harder)
- Optimizing process lifecycle and memory usage
- Preventing main thread blocking and ANRs
