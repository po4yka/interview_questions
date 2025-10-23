---
id: 20251012-122782
title: App Start Types Android / Типы запуска приложения Android
aliases:
- App Start Types Android
- Типы запуска приложения Android
topic: android
subtopics:
- performance-memory
- app-startup
- lifecycle
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- q-android-performance-measurement-tools--android--medium
- q-android-build-optimization--android--medium
- q-android-app-lag-analysis--android--medium
created: 2025-10-15
updated: 2025-10-15
tags:
- android/performance-memory
- android/app-startup
- android/lifecycle
- difficulty/medium
---

## Answer (EN)
**App Start Types** categorize launches by memory/process state: cold (no process), warm (process alive, Activity recreated), hot (Activity resumed). Optimize per type with measurable budgets and strict main-thread discipline.

### Terminology and Metrics
- **TTID (Time To Initial Display)**: first frame drawn; user sees UI.
- **TTFD (Time To Full Display)**: UI is fully interactive; call `reportFullyDrawn()` as the signal.
- **Sources of truth**: Android Vitals (prod), Perfetto/Startup Profiler (dev), Macrobenchmark (CI).

```kotlin
// Marking full display (TTFD)
class MainActivity : AppCompatActivity() {
    override fun onResume() {
        super.onResume()
        window.decorView.post { reportFullyDrawn() }
    }
}
```

```kotlin
// Frame metrics collection (jank, long frames)
class MainActivity : AppCompatActivity() {
    private val aggregator = FrameMetricsAggregator()
    override fun onStart() { super.onStart(); aggregator.add(this) }
    override fun onStop() {
        val metrics = aggregator.remove(this) // inspect metrics[FrameMetricsAggregator.TOTAL_INDEX]
        super.onStop()
    }
}
```

### Cold Start (no process)
- **Goal**: minimize work on the critical path (process start → first frame).
- **Tactics**:
  - Defer non-critical SDKs; disable auto-inits (prefer `androidx.startup`).
  - Remove/merge unnecessary `ContentProvider`s; each adds startup IPC.
  - Keep Application `onCreate` fast; IO off main; precompute off main.
  - Ship and install **baseline profiles** to avoid cold-start JIT warms.

```kotlin
// Strict main-thread policy during startup
class App : Application() {
    override fun onCreate() {
        super.onCreate()
        StrictMode.setThreadPolicy(StrictMode.ThreadPolicy.Builder()
            .detectAll().penaltyLog().build())
        // Critical-only init
        initCrashReporting()
        // Defer heavy work
        Handler(Looper.getMainLooper()).post { initAnalytics(); initAds() }
    }
}
```

```kotlin
// Trace critical sections for Perfetto timeline
object StartupTrace {
    inline fun <T> section(name: String, block: () -> T): T {
        Trace.beginSection(name); return try { block() } finally { Trace.endSection() }
    }
}
```

### Warm Start (process alive, Activity recreated)
- **Goal**: reconstruct UI/state with minimal work.
- **Tactics**:
  - Use `ViewModel` + `SavedStateHandle` to avoid recomputation.
  - Persist only essentials in `savedInstanceState` (bytes budget!).
  - Avoid deep view trees; prefer ViewBinding/Compose.

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
- **Goal**: keep `onResume` nearly empty; coalesce updates.
- **Tactics**:
  - Use `lifecycleScope` with `repeatOnLifecycle` to resume flows.
  - Debounce expensive UI work; batch model updates.

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
- Precompile hot paths (class loading, DI graph, first screen) to reduce cold-start JIT.
- Generate with Macrobenchmark; ship with `profileinstaller` so Play can install profiles.

```kotlin
// Macrobenchmark example (cold/warm/hot measurement & profile collection)
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

### Compose-specific startup patterns
- Prefer lazy composition; avoid heavy `LaunchedEffect` in root.
- Use `remember/rememberSaveable` for state survival across warm starts.

```kotlin
@Composable
fun MainScreen(vm: MainVm) {
    val state by vm.uiState.observeAsState()
    LazyColumn { items(state.items) { ItemRow(it) } }
}
```

### Guardrails and Budgets
- **Budgets**: Cold < 500ms, Warm < 300ms, Hot < 100ms (device-dependent).
- **No main-thread disk/network** on the startup path.
- **≤ 1 ContentProvider** on critical path; gate new SDKs.
- **CI**: macrobench threshold + alert on regressions (fail build on drift).

---

## Follow-ups

- How do you measure startup time in production?
- What's the difference between reportFullyDrawn() and first frame?
- How do you optimize startup for different device capabilities?
- What are the trade-offs of lazy initialization?

## References

- [App Startup Library](https://developer.android.com/topic/libraries/app-startup)
- [App Startup Performance](https://developer.android.com/topic/performance/vitals/launch-time)

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]]
- [[q-android-project-parts--android--easy]]

### Related (Same Level)
- [[q-android-performance-measurement-tools--android--medium]]
- [[q-android-build-optimization--android--medium]]
- [[q-android-app-lag-analysis--android--medium]]

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]]