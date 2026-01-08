---id: android-336
title: Типы запуска приложения в Android / App Start Types Android
aliases: ["App Start Types Android", "Типы запуска приложения в Android"]
topic: android
subtopics: [performance-startup]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-app-startup, c-compose-recomposition, c-perfetto, c-power-profiling, q-android-performance-measurement-tools--android--medium]
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

Три типа запуска Android-приложения определяются состоянием процесса и активити:
- **Cold старт (холодный)**: процесс приложения отсутствует; системе нужно создать процесс и инициализировать приложение (`Application`, первый `Activity`/Entry point).
- **Warm старт (тёплый)**: процесс жив, но UI приложения не на экране; `Activity` может быть пересоздана или восстановлена из сохранённого состояния.
- **Hot старт (горячий)**: процесс жив, и `Activity` (или стек активити) остаётся в памяти; требуется только вернуть приложение на экран (выполнить лёгкий путь `onRestart`/`onStart`/`onResume` без тяжёлой инициализации).

Каждый тип требует своей стратегии оптимизации и измерения метрик (см. также [[c-app-startup]]).

### Метрики Запуска

- **TTID (Time To Initial Display)**: время до отображения первого кадра стартовой `Activity`, видимого пользователю.
- **TTFD (Time To Full Display)**: время до полного отображения `Activity` и готовности к взаимодействию; сигнализируется через однократный вызов `reportFullyDrawn()` после того, как критический UI действительно готов.
- **Инструменты**: Android Vitals (прод), Macrobenchmark (CI), Perfetto (локальный профилинг).

```kotlin
// Сигнализируем готовность полностью отрисованного экрана
class MainActivity : AppCompatActivity() {
    private var fullyDrawnReported = false

    override fun onResume() {
        super.onResume()
        if (!fullyDrawnReported) {
            window.decorView.post {
                if (!fullyDrawnReported) {
                    reportFullyDrawn()
                    fullyDrawnReported = true
                }
            }
        }
    }
}
```

### Cold Start (холодный запуск)

**Цель**: минимизировать критический путь (старт процесса → первый кадр стартовой `Activity`).

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

**Baseline profiles**: предварительная компиляция горячих путей для снижения зависимости от прогрева JIT и ускорения холодного и тёплого запусков.

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

**Цель**: минимальная работа в `onRestart`/`onStart`/`onResume`, батчинг обновлений.

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

### Бюджеты И Ограничения

- **Иллюстративные целевые бюджеты** (не официальные гарантии; на практике калибруются под устройство и категорию приложения): Cold ≈ до 500ms, Warm ≈ до 300ms, Hot ≈ до 100ms.
- **Запрещено**: выполнять блокирующие диск/сетевые операции на главном потоке во время запуска.
- **CI**: сценарии с Macrobenchmark с порогами и алертами на регрессии.

---

## Answer (EN)

The three Android app start types are defined by process and activity state:
- **Cold** start: no app process exists; the system must create the process and initialize the app (`Application` and entry `Activity`).
- **Warm** start: process is alive but the app UI is not visible; the `Activity` may need to be recreated or restored from saved state.
- **Hot** start: process is alive and the `Activity` (or activity stack) remains in memory; the app just needs to be brought to the foreground following the light `onRestart`/`onStart`/`onResume` path without heavy re-initialization.

Each type requires specific optimization with measurable metrics (see also [[c-app-startup]]).

### Startup Metrics

- **TTID (Time To Initial Display)**: time until the first frame of the starting `Activity` is drawn and visible to the user.
- **TTFD (Time To Full Display)**: time until the `Activity` is fully drawn and ready for interaction; indicated by a single `reportFullyDrawn()` call once critical UI work is actually complete.
- **Tools**: Android Vitals (prod), Macrobenchmark (CI), Perfetto (local profiling).

```kotlin
// Signal full display readiness
class MainActivity : AppCompatActivity() {
    private var fullyDrawnReported = false

    override fun onResume() {
        super.onResume()
        if (!fullyDrawnReported) {
            window.decorView.post {
                if (!fullyDrawnReported) {
                    reportFullyDrawn()
                    fullyDrawnReported = true
                }
            }
        }
    }
}
```

### Cold Start

**Goal**: minimize the critical path (process start → first frame of the launch `Activity`).

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
        // Heavy SDKs deferred until after the critical startup path
        Handler(Looper.getMainLooper()).post {
            initAnalytics()
            initAds()
        }
    }
}
```

**Baseline profiles**: precompile hot paths to reduce reliance on JIT warmup and improve cold and warm starts.

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

**Goal**: minimal work in `onRestart`/`onStart`/`onResume`, batched updates.

```kotlin
// Lifecycle-aware flow resumption in the right states
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

- **Illustrative target budgets** (not official guarantees; should be tuned for device and app category): Cold ≈ up to 500ms, Warm ≈ up to 300ms, Hot ≈ up to 100ms.
- **Prohibitions**: avoid blocking disk/network operations on the main thread during startup.
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
