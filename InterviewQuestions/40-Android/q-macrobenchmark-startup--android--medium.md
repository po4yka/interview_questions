---
id: android-040
title: Macrobenchmark for App Startup / Macrobenchmark для запуска приложения
aliases:
- Macrobenchmark for App Startup
- Macrobenchmark для запуска приложения
topic: android
subtopics:
- profiling
- testing-benchmark
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
sources: []
status: draft
moc: moc-android
related:
- c-perfetto
- q-android-performance-measurement-tools--android--medium
- q-baseline-profiles-android--android--medium
- q-performance-optimization-android--android--medium
created: 2025-10-11
updated: 2025-01-27
tags:
- android/profiling
- android/testing-benchmark
- difficulty/medium
- macrobenchmark
- perfetto
- performance
- startup
---

# Вопрос (RU)
> Реализуйте macrobenchmark для запуска приложения. Измерьте холодный, теплый и горячий запуск. Используйте трассировку Perfetto для выявления узких мест и оптимизации на основе результатов.

# Question (EN)
> Implement macrobenchmark for app startup. Measure cold, warm, and hot startup times. Use Perfetto traces to identify bottlenecks and optimize based on results.

---

## Ответ (RU)

### Обзор

**Macrobenchmark** - библиотека Jetpack для измерения производительности приложения на реальных устройствах. Измеряет сквозную производительность с точки зрения пользователя.

**Типы запуска:**
- **Холодный**: процесс не существует, система создает его с нуля (самый медленный, 400-800мс)
- **Теплый**: процесс существует, Activity пересоздается (200-400мс)
- **Горячий**: Activity выводится на передний план (50-150мс)

**Ключевые возможности:**
- Измерения на реальном устройстве с Perfetto трассировкой
- Тестирование режимов компиляции (None, Partial, Full)
- Интеграция [[q-baseline-profiles-android--android--medium|Baseline Profiles]]

### Настройка Модуля

**settings.gradle.kts:**
```kotlin
include(":app")
include(":macrobenchmark")  // ✅ Отдельный модуль для бенчмарков
```

**macrobenchmark/build.gradle.kts:**
```kotlin
plugins {
    id("com.android.test")  // ✅ Тип модуля для тестирования
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.example.macrobenchmark"
    compileSdk = 34

    targetProjectPath = ":app"  // ✅ Ссылка на тестируемое приложение
    experimentalProperties["android.experimental.self-instrumenting"] = true

    buildTypes {
        create("benchmark") {  // ✅ Отдельный build type для бенчмарков
            isDebuggable = true
            signingConfig = signingConfigs.getByName("debug")
            matchingFallbacks += listOf("release")
        }
    }
}

dependencies {
    implementation("androidx.benchmark:benchmark-macro-junit4")
    implementation("androidx.test.uiautomator:uiautomator")
}
```

**app/build.gradle.kts:**
```kotlin
android {
    buildTypes {
        create("benchmark") {
            initWith(getByName("release"))
            signingConfig = signingConfigs.getByName("debug")
            isDebuggable = false  // ✅ Близко к релизу, но с debug подписью
            profileable = true  // ✅ Разрешает профилирование
        }
    }
}
```

### Реализация Бенчмарков

**StartupBenchmark.kt:**
```kotlin
@LargeTest
@RunWith(AndroidJUnit4::class)
class StartupBenchmark {
    @get:Rule
    val benchmarkRule = MacrobenchmarkRule()

    // ✅ Холодный запуск без компиляции (худший случай)
    @Test
    fun coldStartupNone() = benchmarkStartup(
        compilationMode = CompilationMode.None(),
        startupMode = StartupMode.COLD
    )

    // ✅ Холодный запуск с Baseline Profile (реальный сценарий Play Store)
    @Test
    fun coldStartupPartial() = benchmarkStartup(
        compilationMode = CompilationMode.Partial(
            baselineProfileMode = BaselineProfileMode.Require
        ),
        startupMode = StartupMode.COLD
    )

    // ✅ Теплый запуск - переключение между приложениями
    @Test
    fun warmStartup() = benchmarkStartup(
        compilationMode = CompilationMode.Partial(),
        startupMode = StartupMode.WARM
    )

    private fun benchmarkStartup(
        compilationMode: CompilationMode,
        startupMode: StartupMode
    ) {
        benchmarkRule.measureRepeated(
            packageName = "com.example.myapp",
            metrics = listOf(StartupTimingMetric()),
            compilationMode = compilationMode,
            iterations = 10,  // ✅ Минимум 5-10 итераций для точности
            startupMode = startupMode,
            setupBlock = { pressHome() }
        ) {
            startActivityAndWait()
            device.wait(Until.hasObject(By.res("main_content")), 5_000)
        }
    }
}
```

### Инструментация Кода

**MainActivity.kt:**
```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        Trace.beginSection("ActivityStart")  // ✅ Маркер начала
        super.onCreate(savedInstanceState)

        // ✅ Измеряем критичные операции
        Trace.beginSection("NetworkInit")
        networkManager.initialize()
        Trace.endSection()

        Trace.beginSection("LoadMainContent")
        setContent { MainScreen() }
        Trace.endSection()

        Trace.endSection()  // ActivityStart
    }
}
```

**❌ Антипаттерны:**
```kotlin
class BadApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        // ❌ Синхронная инициализация на главном потоке
        initDatabase()  // 95мс блокировки
        loadPreferences()  // 45мс блокировки
        initAnalytics()  // 70мс блокировки
    }
}
```

### Анализ Perfetto Трассировок

**Расположение файлов:**
```text
macrobenchmark/build/outputs/connected_android_test_additional_output/
  <device>/StartupBenchmark_coldStartup/
    iteration001-perfetto-trace.perfetto-trace
```

**Открытие:**
- Android Studio: File → Open → выбрать .perfetto-trace
- Web UI: https://ui.perfetto.dev/

**Типичные узкие места:**

1. **Application.onCreate() > 100мс:**
   - Переместить инициализацию в background
   - Использовать App Startup library для ленивой загрузки

2. **Блокировка главного потока:**
   - Database init должна быть < 50мс или async
   - SharedPreferences < 10мс
   - Network calls только async

3. **Медленная инфляция view > 100мс:**
   - Перейти на Jetpack Compose
   - Использовать ViewStub для отложенной загрузки

4. **GC паузы > 50мс:**
   - Уменьшить аллокации во время запуска
   - Использовать object pools

**SQL-запросы в Perfetto:**
```sql
-- Найти самые долгие операции
SELECT name, dur / 1e6 as ms
FROM slice
WHERE name LIKE '%Init%'
ORDER BY dur DESC LIMIT 10;
```

### Оптимизация На Основе Результатов

**До оптимизации:**
```text
Холодный запуск (None): 850мс
Холодный запуск (Partial): 580мс
Теплый запуск: 320мс

Узкие места:
- Application.onCreate(): 180мс
- Database init: 95мс
- View inflation: 120мс
```

**Стратегия оптимизации:**

1. **Ленивая инициализация с App Startup:**
```kotlin
class DatabaseInitializer : Initializer<DatabaseManager> {
    override fun create(context: Context) =
        DatabaseManager(context).apply {
            initializeInBackground()  // ✅ Async инициализация
        }
}
```

2. **Отложенная загрузка UI:**
```kotlin
setContent {
    val data by produceState<UserData?>(null) {
        value = withContext(Dispatchers.IO) { loadUserData() }
    }
    if (data != null) MainScreen(data!!) else LoadingScreen()
}
```

**После оптимизации:**
```text
Холодный запуск (None): 520мс (-39%)
Холодный запуск (Partial): 380мс (-34%)
Теплый запуск: 180мс (-44%)
```

### Интеграция CI/CD

**GitHub Actions:**
```yaml
- name: Run Benchmarks
  uses: reactivecircus/android-emulator-runner@v2
  with:
    api-level: 29
    script: ./gradlew :macrobenchmark:connectedBenchmarkAndroidTest

- name: Upload Results
  uses: actions/upload-artifact@v3
  with:
    name: benchmark-results
    path: macrobenchmark/build/outputs/
```

### Лучшие Практики

1. **Запускать на реальных устройствах** - эмуляторы дают неточные результаты
2. **10+ итераций** - минимум для статистической значимости
3. **Тестировать все типы запуска** - холодный/теплый/горячий
4. **Измерять с Baseline Profiles** - соответствует реальному сценарию Play Store
5. **Профилировать перед оптимизацией** - не оптимизировать вслепую
6. **Интегрировать в CI** - отслеживать регрессии автоматически

---

## Answer (EN)

### Overview

**Macrobenchmark** is a Jetpack library for measuring app performance on real devices. Measures end-to-end performance from user's perspective.

**Startup Types:**
- **Cold**: Process doesn't exist, system creates from scratch (slowest, 400-800ms)
- **Warm**: Process exists, Activity recreated (200-400ms)
- **Hot**: Activity brought to foreground (50-150ms)

**Key Capabilities:**
- Real device measurements with Perfetto tracing
- Compilation mode testing (None, Partial, Full)
- [[q-baseline-profiles-android--android--medium|Baseline Profiles]] integration

### Module Setup

**settings.gradle.kts:**
```kotlin
include(":app")
include(":macrobenchmark")  // ✅ Separate module for benchmarks
```

**macrobenchmark/build.gradle.kts:**
```kotlin
plugins {
    id("com.android.test")  // ✅ Test module type
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.example.macrobenchmark"
    compileSdk = 34

    targetProjectPath = ":app"  // ✅ Reference to app under test
    experimentalProperties["android.experimental.self-instrumenting"] = true

    buildTypes {
        create("benchmark") {  // ✅ Dedicated build type for benchmarks
            isDebuggable = true
            signingConfig = signingConfigs.getByName("debug")
            matchingFallbacks += listOf("release")
        }
    }
}

dependencies {
    implementation("androidx.benchmark:benchmark-macro-junit4")
    implementation("androidx.test.uiautomator:uiautomator")
}
```

**app/build.gradle.kts:**
```kotlin
android {
    buildTypes {
        create("benchmark") {
            initWith(getByName("release"))
            signingConfig = signingConfigs.getByName("debug")
            isDebuggable = false  // ✅ Close to release but with debug signing
            profileable = true  // ✅ Allows profiling
        }
    }
}
```

### Benchmark Implementation

**StartupBenchmark.kt:**
```kotlin
@LargeTest
@RunWith(AndroidJUnit4::class)
class StartupBenchmark {
    @get:Rule
    val benchmarkRule = MacrobenchmarkRule()

    // ✅ Cold startup without compilation (worst case)
    @Test
    fun coldStartupNone() = benchmarkStartup(
        compilationMode = CompilationMode.None(),
        startupMode = StartupMode.COLD
    )

    // ✅ Cold startup with Baseline Profile (real Play Store scenario)
    @Test
    fun coldStartupPartial() = benchmarkStartup(
        compilationMode = CompilationMode.Partial(
            baselineProfileMode = BaselineProfileMode.Require
        ),
        startupMode = StartupMode.COLD
    )

    // ✅ Warm startup - switching between apps
    @Test
    fun warmStartup() = benchmarkStartup(
        compilationMode = CompilationMode.Partial(),
        startupMode = StartupMode.WARM
    )

    private fun benchmarkStartup(
        compilationMode: CompilationMode,
        startupMode: StartupMode
    ) {
        benchmarkRule.measureRepeated(
            packageName = "com.example.myapp",
            metrics = listOf(StartupTimingMetric()),
            compilationMode = compilationMode,
            iterations = 10,  // ✅ Minimum 5-10 iterations for accuracy
            startupMode = startupMode,
            setupBlock = { pressHome() }
        ) {
            startActivityAndWait()
            device.wait(Until.hasObject(By.res("main_content")), 5_000)
        }
    }
}
```

### Code Instrumentation

**MainActivity.kt:**
```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        Trace.beginSection("ActivityStart")  // ✅ Mark start
        super.onCreate(savedInstanceState)

        // ✅ Measure critical operations
        Trace.beginSection("NetworkInit")
        networkManager.initialize()
        Trace.endSection()

        Trace.beginSection("LoadMainContent")
        setContent { MainScreen() }
        Trace.endSection()

        Trace.endSection()  // ActivityStart
    }
}
```

**❌ Anti-patterns:**
```kotlin
class BadApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        // ❌ Synchronous initialization on main thread
        initDatabase()  // 95ms blocking
        loadPreferences()  // 45ms blocking
        initAnalytics()  // 70ms blocking
    }
}
```

### Perfetto Trace Analysis

**File Location:**
```text
macrobenchmark/build/outputs/connected_android_test_additional_output/
  <device>/StartupBenchmark_coldStartup/
    iteration001-perfetto-trace.perfetto-trace
```

**Opening:**
- Android Studio: File → Open → select .perfetto-trace
- Web UI: https://ui.perfetto.dev/

**Common Bottlenecks:**

1. **Application.onCreate() > 100ms:**
   - Move initialization to background
   - Use App Startup library for lazy loading

2. **Main thread blocking:**
   - Database init should be < 50ms or async
   - SharedPreferences < 10ms
   - Network calls must be async

3. **Slow view inflation > 100ms:**
   - Migrate to Jetpack Compose
   - Use ViewStub for deferred loading

4. **GC pauses > 50ms:**
   - Reduce allocations during startup
   - Use object pools

**SQL queries in Perfetto:**
```sql
-- Find longest operations
SELECT name, dur / 1e6 as ms
FROM slice
WHERE name LIKE '%Init%'
ORDER BY dur DESC LIMIT 10;
```

### Optimization Based on Results

**Before Optimization:**
```text
Cold startup (None): 850ms
Cold startup (Partial): 580ms
Warm startup: 320ms

Bottlenecks:
- Application.onCreate(): 180ms
- Database init: 95ms
- View inflation: 120ms
```

**Optimization Strategy:**

1. **Lazy initialization with App Startup:**
```kotlin
class DatabaseInitializer : Initializer<DatabaseManager> {
    override fun create(context: Context) =
        DatabaseManager(context).apply {
            initializeInBackground()  // ✅ Async initialization
        }
}
```

2. **Deferred UI loading:**
```kotlin
setContent {
    val data by produceState<UserData?>(null) {
        value = withContext(Dispatchers.IO) { loadUserData() }
    }
    if (data != null) MainScreen(data!!) else LoadingScreen()
}
```

**After Optimization:**
```text
Cold startup (None): 520ms (-39%)
Cold startup (Partial): 380ms (-34%)
Warm startup: 180ms (-44%)
```

### CI/CD Integration

**GitHub Actions:**
```yaml
- name: Run Benchmarks
  uses: reactivecircus/android-emulator-runner@v2
  with:
    api-level: 29
    script: ./gradlew :macrobenchmark:connectedBenchmarkAndroidTest

- name: Upload Results
  uses: actions/upload-artifact@v3
  with:
    name: benchmark-results
    path: macrobenchmark/build/outputs/
```

### Best Practices

1. **Run on real devices** - emulators give inaccurate results
2. **10+ iterations** - minimum for statistical significance
3. **Test all startup types** - cold/warm/hot
4. **Measure with Baseline Profiles** - matches real Play Store scenario
5. **Profile before optimizing** - don't optimize blindly
6. **Integrate into CI** - track regressions automatically

---

## Follow-ups

- How to generate and integrate Baseline Profiles for optimal startup performance?
- What are the trade-offs between CompilationMode.None, Partial, and Full in production?
- How to detect and prevent startup regressions in CI/CD before reaching production?
- What metrics should trigger alerts for unacceptable startup performance?
- How to optimize startup for different device tiers (low-end vs high-end)?

## References

- [[q-baseline-profiles-android--android--medium]] - Baseline Profiles for performance
- [[q-android-performance-measurement-tools--android--medium]] - Performance measurement tools
- https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview
- https://perfetto.dev/

## Related Questions

### Prerequisites / Concepts

- [[c-perfetto]]


### Prerequisites
- [[q-recyclerview-sethasfixedsize--android--easy]] - Basic performance optimization

### Related
- [[q-memory-leak-detection--android--medium]] - Memory profiling
- [[q-baseline-profiles-optimization--android--medium]] - Baseline Profiles optimization

### Advanced
- [[q-compose-performance-optimization--android--hard]] - Advanced Compose optimization
