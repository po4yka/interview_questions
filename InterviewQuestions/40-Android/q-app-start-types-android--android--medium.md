---
id: android-336
title: App Start Types Android / Типы запуска приложения Android
aliases: ["App Start Types Android", "Типы запуска приложения Android"]
topic: android
subtopics: [lifecycle, performance-startup]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related:
  - c-lifecycle
  - c-viewmodel
sources: []
created: 2025-10-15
updated: 2025-10-30
tags: [android/lifecycle, android/performance-startup, difficulty/medium, performance, startup]
---

# Вопрос (RU)
> Какие существуют типы запуска Android-приложения и как оптимизировать каждый из них?


# Question (EN)
> What are the Android app start types and how do you optimize each?


---

## Ответ (RU)

**Три типа запуска** различаются по состоянию процесса: холодный (процесс не существует), теплый (процесс жив, `Activity` пересоздается), горячий (`Activity` возобновляется). Каждый требует специфичной оптимизации с измеримыми метриками.

### Метрики Запуска

- **TTID (Time To Initial Display)**: первый кадр UI
- **TTFD (Time To Full Display)**: полная интерактивность; сигнализируем через `reportFullyDrawn()`
- **Инструменты**: Android Vitals (prod), Macrobenchmark (CI), Perfetto (dev)

```kotlin
// ✅ Сигнализация полной готовности UI
class MainActivity : AppCompatActivity() {
    override fun onResume() {
        super.onResume()
        window.decorView.post { reportFullyDrawn() }
    }
}
```

### Холодный Старт (Cold Start)

**Цель**: минимизировать критический путь (запуск процесса → первый кадр).

```kotlin
// ✅ Контроль инициализации + отложенная загрузка
class App : Application() {
    override fun onCreate() {
        super.onCreate()
        StrictMode.setThreadPolicy(
            StrictMode.ThreadPolicy.Builder()
                .detectAll().penaltyLog().build()
        )
        initCrashReporting()  // только критичное
        // ❌ Тяжелые SDK отложены
        Handler(Looper.getMainLooper()).post {
            initAnalytics()
            initAds()
        }
    }
}
```

**Baseline profiles**: предкомпилируйте горячие пути для устранения JIT-прогрева.

### Теплый Старт (Warm Start)

**Цель**: быстрое восстановление UI/состояния.

```kotlin
// ✅ ViewModel + SavedStateHandle для избежания пересчетов
class MainVm(state: SavedStateHandle) : ViewModel() {
    val uiState = state.getLiveData("ui", defaultState())
}

// ✅ Минимальная работа в onCreate
class MainActivity : AppCompatActivity() {
    private val vm by viewModels<MainVm>()
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        savedInstanceState?.getString("q")?.let { restoreQuery(it) }
    }
}
```

### Горячий Старт (Hot Start)

**Цель**: пустой `onResume`, группировка обновлений.

```kotlin
// ✅ Lifecycle-aware возобновление потоков
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

### Бюджеты И Гарантии

- **Целевые бюджеты**: Холодный < 500ms, Теплый < 300ms, Горячий < 100ms
- **Запреты**: нет disk/network на главном потоке при старте
- **CI**: macrobench пороги + алерты на регрессии

---


## Answer (EN)

**Three Android app start types** differ by process state: cold (no process), warm (process alive, `Activity` recreated), hot (`Activity` resumed). Each requires specific optimization with measurable metrics.

### Startup Metrics

- **TTID (Time To Initial Display)**: first UI frame
- **TTFD (Time To Full Display)**: full interactivity; signal via `reportFullyDrawn()`
- **Tools**: Android Vitals (prod), Macrobenchmark (CI), Perfetto (dev)

```kotlin
// ✅ Signal full display readiness
class MainActivity : AppCompatActivity() {
    override fun onResume() {
        super.onResume()
        window.decorView.post { reportFullyDrawn() }
    }
}
```

### Cold Start

**Goal**: minimize critical path (process start → first frame).

```kotlin
// ✅ Initialization control + deferred loading
class App : Application() {
    override fun onCreate() {
        super.onCreate()
        StrictMode.setThreadPolicy(
            StrictMode.ThreadPolicy.Builder()
                .detectAll().penaltyLog().build()
        )
        initCrashReporting()  // critical only
        // ❌ Heavy SDKs deferred
        Handler(Looper.getMainLooper()).post {
            initAnalytics()
            initAds()
        }
    }
}
```

**Baseline profiles**: precompile hot paths to eliminate JIT warmup.

### Warm Start

**Goal**: fast UI/state reconstruction.

```kotlin
// ✅ ViewModel + SavedStateHandle to avoid recomputation
class MainVm(state: SavedStateHandle) : ViewModel() {
    val uiState = state.getLiveData("ui", defaultState())
}

// ✅ Minimal onCreate work
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

**Goal**: empty `onResume`, batched updates.

```kotlin
// ✅ Lifecycle-aware flow resumption
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

- **Target budgets**: Cold < 500ms, Warm < 300ms, Hot < 100ms
- **Prohibitions**: no main-thread disk/network on startup
- **CI**: macrobench thresholds + regression alerts

---

## Follow-ups

- How does baseline profile generation impact different startup types and what metrics improve most?
- What's the relationship between `ContentProvider` initialization order and cold start performance?
- How do you measure and enforce startup budgets in CI without flaky tests?
- When should you use App Startup library vs manual lazy initialization for SDK init?
- How does process death/recreation differ from configuration changes in terms of warm start optimization?

## References

- [[c-lifecycle]] - `Activity` and application lifecycle fundamentals
- [[c-viewmodel]] - State preservation and `ViewModel` scoping
- https://developer.android.com/topic/performance/vitals/launch-time - App startup performance guide
- https://developer.android.com/topic/libraries/app-startup - App Startup library documentation
- https://developer.android.com/topic/performance/baselineprofiles - Baseline profiles implementation guide

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - Fundamental Android components understanding
 - `Activity` lifecycle basics

### Related (Same Level)
- [[q-android-performance-measurement-tools--android--medium]] - Profiling and benchmarking tools
- [[q-android-app-lag-analysis--android--medium]] - Frame rendering and jank analysis
- [[q-android-build-optimization--android--medium]] - Build-time performance optimization

### Advanced (Harder)
 - Process lifecycle and memory optimization
 - Main thread blocking and ANR prevention
