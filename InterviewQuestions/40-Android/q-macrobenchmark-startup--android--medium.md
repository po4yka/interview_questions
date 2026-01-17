---\
id: android-040
title: Macrobenchmark for App Startup / Macrobenchmark для запуска приложения
aliases: [Macrobenchmark for App Startup, Macrobenchmark для запуска приложения]
topic: android
subtopics: [testing-benchmark]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
sources: []
status: draft
moc: moc-android
related: [c-perfetto, q-android-performance-measurement-tools--android--medium, q-app-startup-library--android--medium, q-app-startup-optimization--android--medium, q-baseline-profiles-optimization--android--medium, q-fix-slow-app-startup-legacy--android--hard, q-performance-optimization-android--android--medium]
created: 2025-10-11
updated: 2025-11-10
tags: [android/profiling, android/testing-benchmark, difficulty/medium, macrobenchmark, perfetto, performance, startup]
anki_cards:
  - slug: android-040-0-en
    front: "What are the three startup types measured by Macrobenchmark?"
    back: |
      **Startup types**:
      1. **Cold** - process doesn't exist, created from scratch (slowest)
      2. **Warm** - process exists, Activity recreated
      3. **Hot** - Activity in memory, brought to foreground (fastest)

      ```kotlin
      benchmarkRule.measureRepeated(
          startupMode = StartupMode.COLD,
          compilationMode = CompilationMode.Partial(),
          iterations = 10
      ) { startActivityAndWait() }
      ```

      Use Perfetto traces to identify bottlenecks.
    tags:
      - android_testing
      - difficulty::medium
  - slug: android-040-0-ru
    front: "Какие три типа запуска измеряет Macrobenchmark?"
    back: |
      **Типы запуска**:
      1. **Cold** - процесс не существует, создаётся с нуля (самый медленный)
      2. **Warm** - процесс существует, Activity пересоздаётся
      3. **Hot** - Activity в памяти, выводится на передний план (самый быстрый)

      ```kotlin
      benchmarkRule.measureRepeated(
          startupMode = StartupMode.COLD,
          compilationMode = CompilationMode.Partial(),
          iterations = 10
      ) { startActivityAndWait() }
      ```

      Используйте Perfetto-трассировки для поиска узких мест.
    tags:
      - android_testing
      - difficulty::medium

---\
# Вопрос (RU)
> Реализуйте macrobenchmark для запуска приложения. Измерьте холодный, теплый и горячий запуск. Используйте трассировку Perfetto для выявления узких мест и оптимизации на основе результатов.

# Question (EN)
> Implement macrobenchmark for app startup. Measure cold, warm, and hot startup times. Use Perfetto traces to identify bottlenecks and optimize based on results.

---

## Ответ (RU)

### Обзор

**Macrobenchmark** — библиотека Jetpack для измерения производительности приложения на реальных устройствах. Она измеряет сквозную производительность с точки зрения пользователя.

**Типы запуска (ориентиры, не жесткие границы):**
- **Холодный**: процесс не существует, система создает его с нуля (обычно самый медленный; целевые значения могут быть в районе сотен миллисекунд в зависимости от устройства)
- **Теплый**: процесс существует, `Activity` пересоздается (быстрее холодного, но все еще может содержать тяжелую инициализацию UI)
- **Горячий**: `Activity` уже в памяти и выводится на передний план (самый быстрый сценарий)

**Ключевые возможности:**
- Измерения на реальном устройстве с Perfetto-трассировкой
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
    id("com.android.test")  // ✅ Тип модуля для тестирования (instrumentation tests)
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.example.macrobenchmark"
    compileSdk = 34

    targetProjectPath = ":app"  // ✅ Ссылка на тестируемое приложение
    experimentalProperties["android.experimental.self-instrumenting"] = true

    defaultConfig {
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        create("benchmark") {  // ✅ Отдельный build type для бенчмарков в test-модуле
            // Этот build type относится к test-модулю и конфигурации тестового APK.
            isDebuggable = true
            matchingFallbacks += listOf("release")
        }
    }
}

dependencies {
    implementation("androidx.benchmark:benchmark-macro-junit4:1.2.4")
    implementation("androidx.test.uiautomator:uiautomator:2.3.0")
}
```

**app/build.gradle.kts:**
```kotlin
android {
    buildTypes {
        create("benchmark") {
            initWith(getByName("release"))
            signingConfig = signingConfigs.getByName("debug")
            isDebuggable = false  // ✅ Целевое приложение максимально близко к релизу
            profileable = true    // ✅ Разрешает профилирование релизоподобной сборки
        }
    }

    defaultConfig {
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
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

    // ✅ Теплый запуск — переключение между приложениями
    @Test
    fun warmStartup() = benchmarkStartup(
        compilationMode = CompilationMode.Partial(),
        startupMode = StartupMode.WARM
    )

    // ✅ Горячий запуск — возврат приложения на передний план
    @Test
    fun hotStartup() = benchmarkStartup(
        compilationMode = CompilationMode.Partial(),
        startupMode = StartupMode.HOT
    )

    private fun benchmarkStartup(
        compilationMode: CompilationMode,
        startupMode: StartupMode
    ) {
        benchmarkRule.measureRepeated(
            packageName = "com.example.myapp",
            metrics = listOf(StartupTimingMetric()),
            compilationMode = compilationMode,
            iterations = 10,  // ✅ Минимум 5–10 итераций для более стабильных результатов
            startupMode = startupMode,
            setupBlock = {
                // Методы pressHome() и device предоставляются MacrobenchmarkRule / UiAutomator
                pressHome()
            }
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
        Trace.beginSection("ActivityStart")  // ✅ Маркер начала критического пути
        super.onCreate(savedInstanceState)

        // ✅ Измеряем потенциально тяжелые операции
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
        // ❌ Синхронная тяжелая инициализация на главном потоке при старте
        initDatabase()      // Длительная блокировка старта
        loadPreferences()   // Дополнительная задержка
        initAnalytics()     // Сетевые/IO операции в onCreate()
    }
}
```

### Анализ Perfetto-трассировок

**Расположение файлов (может отличаться в разных версиях инструментов):**
```text
macrobenchmark/build/outputs/connected_android_test_additional_output/
  <device>/StartupBenchmark_coldStartupNone/
    iteration001-perfetto-trace.perfetto-trace
```

**Открытие:**
- Android Studio: File → Open → выбрать .perfetto-trace
- Web UI: https://ui.perfetto.dev/

**Типичные узкие места (руководящие ориентиры):**

1. **`Application`.onCreate() заметно > ~100 мс:**
   - Перенести не критичные для первого кадра инициализации в background
   - Использовать App Startup / ленивую инициализацию компонентов

2. **Блокировка главного потока:**
   - Инициализацию БД по возможности делать асинхронно или подготовить заранее; избегать длительных (> десятков мс) операций
   - Чтение `SharedPreferences` делать минимальным и быстрым, дорогое — переносить
   - Все сетевые вызовы — только асинхронно

3. **Медленная инфляция view / построение UI:**
   - Оптимизировать layout'ы или использовать ленивую загрузку части UI (включая ViewStub, отложенный контент в Compose)

4. **GC-паузы:**
   - Уменьшать аллокации во время запуска
   - Продвинутые техники (например, object pool'ы) использовать осторожно и только по результатам профилирования

**SQL-запросы в Perfetto:**
```sql
-- Найти самые долгие операции по имени
SELECT name, dur / 1e6 AS ms
FROM slice
WHERE name LIKE '%Init%'
ORDER BY ms DESC
LIMIT 10;
```

### Оптимизация На Основе Результатов

**До оптимизации (пример):**
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
    override fun create(context: Context): DatabaseManager =
        DatabaseManager(context).apply {
            // ✅ Не блокировать create() тяжелой работой; запускать длительную инициализацию в фоне
            initializeInBackground()  // Асинхронная/отложенная инициализация
        }

    override fun dependencies(): List<Class<out Initializer<*>>> = emptyList()
}
```

2. **Отложенная загрузка UI:**
```kotlin
@Composable
fun MainContent() {
    val data by produceState<UserData?>(initialValue = null) {
        // Блок produceState выполняется в suspend-контексте
        value = loadUserData() // Сделайте loadUserData() suspend и переключайте dispatcher внутри
    }

    if (data != null) {
        MainScreen(data!!)
    } else {
        LoadingScreen()
    }
}
```

**После оптимизации (примерные результаты):**
```text
Холодный запуск (None): 520мс
Холодный запуск (Partial): 380мс
Теплый запуск: 180мс
```

### Интеграция CI/CD

> Предпочтительно запускать macrobenchmark'и на физических устройствах. Пример ниже показывает базовую интеграцию; для надежных метрик используйте реальные девайсы (device farm / локальный стенд).

**GitHub Actions (пример):**
```yaml
- name: Run Benchmarks (emulator example - less stable)
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

1. Запускать на реальных устройствах — эмуляторы дают менее надежные результаты
2. Использовать 10+ итераций для стабильной статистики
3. Тестировать все типы запуска — холодный/тёплый/горячий (добавляя отдельные тесты для HOT)
4. Измерять с Baseline Profiles — соответствует реальному сценарию Play Store
5. Профилировать перед оптимизацией — не оптимизировать вслепую
6. Интегрировать в CI (по возможности с реальными девайсами) для отслеживания регрессий

---

## Answer (EN)

### Overview

**Macrobenchmark** is a Jetpack library for measuring app performance on real devices. It measures end-to-end performance from the user's perspective.

**Startup Types (guidelines, not strict guarantees):**
- **Cold**: Process doesn't exist, system creates it from scratch (typically the slowest; actual times vary by device and app complexity)
- **Warm**: Process exists, `Activity` is recreated (faster than cold but may still involve heavy UI setup)
- **Hot**: `Activity` is already in memory and brought to the foreground (fastest scenario)

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
    id("com.android.test")  // ✅ Test module type (instrumentation tests)
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.example.macrobenchmark"
    compileSdk = 34

    targetProjectPath = ":app"  // ✅ Reference to app under test
    experimentalProperties["android.experimental.self-instrumenting"] = true

    defaultConfig {
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        create("benchmark") {  // ✅ Dedicated build type for the test module
            // This build type configures the test APK; it can be debuggable.
            isDebuggable = true
            matchingFallbacks += listOf("release")
        }
    }
}

dependencies {
    implementation("androidx.benchmark:benchmark-macro-junit4:1.2.4")
    implementation("androidx.test.uiautomator:uiautomator:2.3.0")
}
```

**app/build.gradle.kts:**
```kotlin
android {
    buildTypes {
        create("benchmark") {
            initWith(getByName("release"))
            signingConfig = signingConfigs.getByName("debug")
            isDebuggable = false  // ✅ Target app is release-like
            profileable = true    // ✅ Allows profiling of the release-like build
        }
    }

    defaultConfig {
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
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

    // ✅ Cold startup with Baseline Profile (real Play Store-like scenario)
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

    // ✅ Hot startup - bringing app back to foreground
    @Test
    fun hotStartup() = benchmarkStartup(
        compilationMode = CompilationMode.Partial(),
        startupMode = StartupMode.HOT
    )

    private fun benchmarkStartup(
        compilationMode: CompilationMode,
        startupMode: StartupMode
    ) {
        benchmarkRule.measureRepeated(
            packageName = "com.example.myapp",
            metrics = listOf(StartupTimingMetric()),
            compilationMode = compilationMode,
            iterations = 10,  // ✅ At least 5–10 iterations for stable results
            startupMode = startupMode,
            setupBlock = {
                // pressHome() and device are provided via MacrobenchmarkRule / UiAutomator
                pressHome()
            }
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
        Trace.beginSection("ActivityStart")  // ✅ Mark start of the critical path
        super.onCreate(savedInstanceState)

        // ✅ Measure potentially heavy operations
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
        // ❌ Heavy synchronous initialization on the main thread at startup
        initDatabase()
        loadPreferences()
        initAnalytics()
    }
}
```

### Perfetto Trace Analysis

**File Location (may vary with tooling versions):**
```text
macrobenchmark/build/outputs/connected_android_test_additional_output/
  <device>/StartupBenchmark_coldStartupNone/
    iteration001-perfetto-trace.perfetto-trace
```

**Opening:**
- Android Studio: File → Open → select .perfetto-trace
- Web UI: https://ui.perfetto.dev/

**Common Bottlenecks (guidelines):**

1. **`Application`.onCreate() significantly > ~100ms:**
   - Move non-critical initialization off the main thread
   - Use App Startup / lazy initialization for non-essential components

2. **Main thread blocking:**
   - Avoid long (> tens of ms) DB setup; make heavy work async or precomputed
   - Keep `SharedPreferences` reads minimal and fast; move heavy processing elsewhere
   - Network calls must be async

3. **Slow view inflation / UI construction:**
   - Optimize layouts or defer non-critical UI
   - Use mechanisms like ViewStub or deferred Compose content for lazy loading

4. **GC pauses:**
   - Reduce allocations during startup
   - Consider advanced techniques (like object pools) only when justified by profiling

**SQL queries in Perfetto:**
```sql
-- Find longest operations by name
SELECT name, dur / 1e6 AS ms
FROM slice
WHERE name LIKE '%Init%'
ORDER BY ms DESC
LIMIT 10;
```

### Optimization Based on Results

**Before Optimization (example):**
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
    override fun create(context: Context): DatabaseManager =
        DatabaseManager(context).apply {
            // ✅ Avoid heavy blocking work in create(); start long-running init in background
            initializeInBackground()  // Async / deferred initialization
        }

    override fun dependencies(): List<Class<out Initializer<*>>> = emptyList()
}
```

2. **Deferred UI loading:**
```kotlin
@Composable
fun MainContent() {
    val data by produceState<UserData?>(initialValue = null) {
        // This block runs in a suspend context
        value = loadUserData() // Make loadUserData() suspend and switch dispatcher inside it
    }

    if (data != null) {
        MainScreen(data!!)
    } else {
        LoadingScreen()
    }
}
```

**After Optimization (example):**
```text
Cold startup (None): 520ms
Cold startup (Partial): 380ms
Warm startup: 180ms
```

### CI/CD Integration

> Prefer running macrobenchmarks on physical devices. The example below uses an emulator and is mainly illustrative; for reliable performance signals, integrate with real-device labs or dedicated hardware.

**GitHub Actions (example):**
```yaml
- name: Run Benchmarks (emulator example - less stable)
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

1. Run on real devices where possible — emulators produce less stable results
2. Use 10+ iterations for statistically meaningful numbers
3. Cover all relevant startup types — cold/warm/hot (add dedicated HOT tests)
4. Measure with Baseline Profiles — aligns with real Play Store behavior
5. Always profile before optimizing — avoid blind micro-optimizations
6. Integrate into CI (ideally with real devices) to catch regressions early

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
