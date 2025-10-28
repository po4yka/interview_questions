---
id: 20251012-122782
title: App Start Types Android / Типы запуска приложения Android
aliases: [App Start Types Android, Типы запуска приложения Android]
topic: android
subtopics:
  - app-startup
  - lifecycle
  - performance-memory
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - q-android-app-lag-analysis--android--medium
  - q-android-build-optimization--android--medium
  - q-android-performance-measurement-tools--android--medium
created: 2025-10-15
updated: 2025-10-28
tags: [android/app-startup, android/lifecycle, android/performance-memory, difficulty/medium]
---
# Вопрос (RU)
> Какие существуют типы запуска Android-приложения и как оптимизировать каждый из них?

## Ответ (RU)

**Типы запуска приложения** классифицируют старт по состоянию процесса и памяти: холодный (процесс не существует), теплый (процесс жив, Activity пересоздается) и горячий (Activity возобновляется). Оптимизация под каждый тип требует соблюдения бюджетов производительности и строгой дисциплины работы с главным потоком. Понимание [[c-lifecycle]] и [[c-viewmodel]] критично для оптимизации каждого типа запуска.

### Терминология и метрики
- **TTID (Time To Initial Display)**: время до отрисовки первого кадра; пользователь видит UI.
- **TTFD (Time To Full Display)**: время до полной интерактивности UI; сигнализируйте через `reportFullyDrawn()`.
- **Источники данных**: Android Vitals (prod), Perfetto/Startup Profiler (dev), Macrobenchmark (CI).

```kotlin
// Сигнализация полной готовности UI (TTFD)
class MainActivity : AppCompatActivity() {
    override fun onResume() {
        super.onResume()
        window.decorView.post { reportFullyDrawn() }
    }
}
```

### Холодный старт (процесс не существует)
- **Цель**: минимизировать работу на критическом пути (запуск процесса → первый кадр).
- **Тактика**:
  - Отложите некритичные SDK; отключите авто-инициализацию (используйте `androidx.startup`).
  - Удалите/объедините лишние `ContentProvider` — каждый добавляет IPC при старте.
  - Держите `Application.onCreate()` быстрым; IO и вычисления — вне главного потока.
  - Используйте **baseline profiles** для устранения JIT-прогрева при холодном старте.

```kotlin
// ✅ Строгий контроль главного потока при старте
class App : Application() {
    override fun onCreate() {
        super.onCreate()
        StrictMode.setThreadPolicy(StrictMode.ThreadPolicy.Builder()
            .detectAll().penaltyLog().build())
        initCrashReporting()  // критичная инициализация
        // ❌ Тяжелая работа откладывается
        Handler(Looper.getMainLooper()).post { initAnalytics(); initAds() }
    }
}
```

### Теплый старт (процесс жив, Activity пересоздается)
- **Цель**: восстановить UI/состояние с минимальными затратами.
- **Тактика**:
  - Используйте `ViewModel` + `SavedStateHandle` для избежания повторных вычислений.
  - Сохраняйте только необходимое в `savedInstanceState` (следите за размером!).
  - Избегайте глубоких иерархий View; предпочитайте ViewBinding/Compose.

```kotlin
class MainVm(state: SavedStateHandle) : ViewModel() {
    val uiState = state.getLiveData("ui", defaultState())
}

class MainActivity : AppCompatActivity() {
    private val vm by viewModels<MainVm>()
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        savedInstanceState?.getString("q")?.let { restoreQuery(it) }
    }
}
```

### Горячий старт (Activity возобновляется)
- **Цель**: держать `onResume` почти пустым; группировать обновления.
- **Тактика**:
  - Используйте `lifecycleScope` с `repeatOnLifecycle` для возобновления потоков.
  - Применяйте debounce для дорогих UI-операций.

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onResume() {
        super.onResume()
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) { refreshIfStale() }
        }
    }
}
```

### Baseline Profiles (критично для холодного старта)
- Предкомпилируйте горячие пути (загрузка классов, DI-граф, первый экран), чтобы избежать JIT-прогрева.
- Генерируйте через Macrobenchmark; поставляйте с `profileinstaller`, чтобы Play мог установить профили.

```kotlin
// Macrobenchmark для измерения и сбора профилей
class StartupBench {
    @get:Rule val rule = MacrobenchmarkRule()
    @Test fun cold() = rule.measureRepeated(
        packageName = "com.example.app",
        metrics = listOf(StartupTimingMetric()),
        startupMode = StartupMode.COLD,
        iterations = 5
    ) { startActivityAndWait() }
}
```

### Гарантии и бюджеты
- **Бюджеты**: Холодный < 500ms, Теплый < 300ms, Горячий < 100ms (зависит от устройства).
- **Нет disk/network на главном потоке** при старте.
- **≤ 1 ContentProvider** на критическом пути; контролируйте новые SDK.
- **CI**: порог macrobench + алерты на регрессии (фейлить сборку при дрейфе).

---

# Question (EN)
> What are the Android app start types and how do you optimize each?

## Answer (EN)
**App Start Types** categorize launches by memory/process state: cold (no process), warm (process alive, Activity recreated), hot (Activity resumed). Optimize per type with measurable budgets and strict main-thread discipline. Understanding [[c-lifecycle]] and [[c-viewmodel]] helps optimize each start type.

### Terminology and Metrics
- **TTID (Time To Initial Display)**: first frame drawn; user sees UI.
- **TTFD (Time To Full Display)**: UI fully interactive; signal via `reportFullyDrawn()`.
- **Sources**: Android Vitals (prod), Perfetto/Startup Profiler (dev), Macrobenchmark (CI).

```kotlin
// Signal full display readiness (TTFD)
class MainActivity : AppCompatActivity() {
    override fun onResume() {
        super.onResume()
        window.decorView.post { reportFullyDrawn() }
    }
}
```

### Cold Start (no process)
- **Goal**: minimize critical path work (process start → first frame).
- **Tactics**:
  - Defer non-critical SDKs; disable auto-init (use `androidx.startup`).
  - Remove/merge unnecessary `ContentProvider`s—each adds IPC overhead.
  - Keep `Application.onCreate()` fast; move IO off main thread.
  - Ship **baseline profiles** to eliminate cold-start JIT warmup.

```kotlin
// ✅ Strict main-thread discipline at startup
class App : Application() {
    override fun onCreate() {
        super.onCreate()
        StrictMode.setThreadPolicy(StrictMode.ThreadPolicy.Builder()
            .detectAll().penaltyLog().build())
        initCrashReporting()  // critical init only
        // ❌ Heavy work deferred
        Handler(Looper.getMainLooper()).post { initAnalytics(); initAds() }
    }
}
```

### Warm Start (process alive, Activity recreated)
- **Goal**: reconstruct UI/state with minimal overhead.
- **Tactics**:
  - Use `ViewModel` + `SavedStateHandle` to avoid recomputation.
  - Persist only essentials in `savedInstanceState` (watch size!).
  - Avoid deep view hierarchies; prefer ViewBinding/Compose.

```kotlin
class MainVm(state: SavedStateHandle) : ViewModel() {
    val uiState = state.getLiveData("ui", defaultState())
}

class MainActivity : AppCompatActivity() {
    private val vm by viewModels<MainVm>()
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        savedInstanceState?.getString("q")?.let { restoreQuery(it) }
    }
}
```

### Hot Start (Activity resumed)
- **Goal**: keep `onResume` nearly empty; batch updates.
- **Tactics**:
  - Use `lifecycleScope` with `repeatOnLifecycle` to resume flows.
  - Debounce expensive UI operations.

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onResume() {
        super.onResume()
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) { refreshIfStale() }
        }
    }
}
```

### Baseline Profiles (critical for cold start)
- Precompile hot paths (class loading, DI graph, first screen) to reduce JIT overhead.
- Generate with Macrobenchmark; ship with `profileinstaller` for Play to install.

```kotlin
// Macrobenchmark for measurement and profile generation
class StartupBench {
    @get:Rule val rule = MacrobenchmarkRule()
    @Test fun cold() = rule.measureRepeated(
        packageName = "com.example.app",
        metrics = listOf(StartupTimingMetric()),
        startupMode = StartupMode.COLD,
        iterations = 5
    ) { startActivityAndWait() }
}
```

### Guardrails and Budgets
- **Budgets**: Cold < 500ms, Warm < 300ms, Hot < 100ms (device-dependent).
- **No main-thread disk/network** on startup path.
- **≤ 1 ContentProvider** on critical path; gate new SDKs.
- **CI**: macrobench thresholds + regression alerts (fail build on drift).

---

## Follow-ups

- How do you measure TTID vs TTFD in production using Android Vitals?
- What's the impact of baseline profiles on different startup types?
- How do you balance startup speed with feature initialization requirements?
- What are common ContentProvider anti-patterns that slow cold starts?
- How does process importance level affect warm vs hot start behavior?

## References

- [[c-lifecycle]] - Activity and application lifecycle fundamentals
- [[c-viewmodel]] - State preservation across configuration changes
- [App Startup Library](https://developer.android.com/topic/libraries/app-startup) - Official startup optimization guide
- [App Startup Performance](https://developer.android.com/topic/performance/vitals/launch-time) - Android Vitals metrics

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - Fundamental Android components
- [[q-android-project-parts--android--easy]] - Project structure basics

### Related (Same Level)
- [[q-android-performance-measurement-tools--android--medium]] - Profiling and measurement
- [[q-android-build-optimization--android--medium]] - Build-time optimizations
- [[q-android-app-lag-analysis--android--medium]] - Frame jank and UI responsiveness

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]] - Deep dive into Android runtime