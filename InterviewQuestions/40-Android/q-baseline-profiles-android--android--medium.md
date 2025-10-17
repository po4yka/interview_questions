---
id: "20251015082237491"
title: "Baseline Profiles Android"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [performance, baseline-profiles, aot, optimization, app-startup, difficulty/medium]
---
# Baseline Profiles in Android

**Сложность**: Medium
**Источник**: Amit Shekhar Android Interview Questions

# Question (EN)
> What are Baseline Profiles in Android? How do they improve app performance and how do you generate them?

# Вопрос (RU)
> Что такое Baseline Profiles в Android? Как они улучшают производительность приложения и как их генерировать?

---

## Answer (EN)

Baseline Profiles are a performance optimization feature that tells the Android Runtime (ART) which code paths to pre-compile (AOT) ahead of time, reducing app startup time and jank during critical user journeys.

#### 1. **How Baseline Profiles Work**

```
Traditional JIT Compilation:
App Start → Interpret bytecode → Profile → JIT compile hot code → Fast execution
          (slow)                                              (after warmup)

With Baseline Profile:
App Install → AOT compile profiled code → App Start → Fast execution
                                         (fast)      (immediately)
```

**Performance Impact:**

```kotlin
// Without Baseline Profile:
Cold start: 1200ms
Warm start: 800ms
First interaction: 150ms (+ JIT compilation time)

// With Baseline Profile:
Cold start: 800ms (-33%)
Warm start: 500ms (-38%)
First interaction: 80ms (-47%)
```

#### 2. **Creating Baseline Profiles**

**Setup (build.gradle.kts):**

```kotlin
// Module-level build.gradle.kts
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("androidx.baselineprofile")
}

android {
    defaultConfig {
        // ...
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            signingConfig = signingConfigs.getByName("debug")
        }

        create("benchmark") {
            initWith(getByName("release"))
            matchingFallbacks += listOf("release")
            proguardFiles("benchmark-rules.pro")
        }
    }
}
```

**Baseline Profile Module:**

```kotlin
// Create separate module: baselineprofile

// baselineprofile/build.gradle.kts
plugins {
    id("com.android.test")
    id("org.jetbrains.kotlin.android")
    id("androidx.baselineprofile")
}

android {
    namespace = "com.example.app.baselineprofile"
    compileSdk = 34

    defaultConfig {
        minSdk = 28
        targetSdk = 34
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    targetProjectPath = ":app"

    testOptions {
        managedDevices {
            devices {
                create<com.android.build.api.dsl.ManagedVirtualDevice>("pixel6Api31") {
                    device = "Pixel 6"
                    apiLevel = 31
                    systemImageSource = "aosp"
                }
            }
        }
    }
}
```

**Generating Profile:**

```kotlin
// baselineprofile/src/main/java/StartupBenchmark.kt
@RunWith(AndroidJUnit4::class)
class StartupBenchmark {

    @get:Rule
    val baselineProfileRule = BaselineProfileRule()

    @Test
    fun startup() = baselineProfileRule.collect(
        packageName = "com.example.app",
        profileBlock = {
            pressHome()
            startActivityAndWait()
        }
    )
}

// Advanced profile with user journeys
@Test
fun generateBaselineProfile() = baselineProfileRule.collect(
    packageName = "com.example.app",
    maxIterations = 15,
    profileBlock = {
        // Critical user journey 1: App launch and browse feed
        pressHome()
        startActivityAndWait()

        // Scroll feed
        device.findObject(By.res("feed_list"))?.let { list ->
            repeat(10) {
                list.scroll(Direction.DOWN, 0.8f)
                Thread.sleep(100)
            }
        }

        // Critical user journey 2: Search
        device.findObject(By.res("search_button"))?.click()
        device.findObject(By.res("search_input"))?.text = "test query"
        Thread.sleep(500)

        // Critical user journey 3: View details
        device.findObject(By.res("first_item"))?.click()
        Thread.sleep(1000)

        // Critical user journey 4: Settings
        device.pressBack()
        device.pressBack()
        device.findObject(By.res("settings_button"))?.click()
        Thread.sleep(500)
    }
)
```

**Running Generation:**

```bash
# Generate baseline profile
./gradlew :baselineprofile:pixel6Api31BaselineProfileBenchmark

# Output location:
# app/src/main/baseline-prof.txt
```

#### 3. **Baseline Profile Format**

```
# Generated baseline profile (baseline-prof.txt)

# Human-readable rules format:
Lcom/example/app/MainActivity;
Lcom/example/app/ui/HomeScreen;
Lcom/example/app/viewmodel/HomeViewModel;-><init>()V
Lcom/example/app/repository/ArticleRepository;->getArticles()Ljava/util/List;
HSPLcom/example/app/ui/theme/ThemeKt;->AppTheme(ZLkotlin/jvm/functions/Function2;Landroidx/compose/runtime/Composer;II)V

# Flags:
# H - Hot method (executed frequently)
# S - Startup method (executed during app start)
# P - Post-startup method (executed after startup)
# L - Class/method reference
```

**Manual Profile Creation:**

```
# baseline-prof.txt (can be manually created/edited)

# Core Application classes
Lcom/example/app/MyApplication;
Lcom/example/app/di/AppModule;

# Main Activity and critical screens
Lcom/example/app/MainActivity;
HSPLcom/example/app/ui/HomeScreen;
HSPLcom/example/app/ui/ArticleListScreen;

# ViewModels used at startup
Lcom/example/app/viewmodel/HomeViewModel;
Lcom/example/app/viewmodel/HomeViewModel;-><init>(Lcom/example/app/repository/ArticleRepository;)V

# Critical repository methods
HSPLcom/example/app/repository/ArticleRepository;->getCachedArticles()Ljava/util/List;
SPLcom/example/app/repository/ArticleRepository;->syncArticles()V

# Database DAOs
Lcom/example/app/data/ArticleDao;
Lcom/example/app/data/ArticleDao_Impl;

# Compose runtime (if using Jetpack Compose)
Landroidx/compose/runtime/ComposerKt;
Landroidx/compose/ui/platform/AndroidComposeView;
```

#### 4. **Verifying Profile Installation**

```kotlin
class ProfileVerifier {

    fun checkProfileInstallation(context: Context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            val status = ProfileVerifier.getCompilationStatusAsync().get()

            Log.d("BaselineProfile", """
                Profile Status:
                - Has reference profile: ${status.hasReferenceProfile()}
                - Profile install result code: ${status.profileInstallResultCode}
                - Is compiled: ${status.isCompiledWithProfile}
            """.trimIndent())

            when (status.profileInstallResultCode) {
                ProfileVerifier.CompilationStatus.RESULT_CODE_NO_PROFILE -> {
                    Log.w("BaselineProfile", "No baseline profile found")
                }
                ProfileVerifier.CompilationStatus.RESULT_CODE_COMPILED_WITH_PROFILE -> {
                    Log.i("BaselineProfile", "App compiled with profile")
                }
                ProfileVerifier.CompilationStatus.RESULT_CODE_PROFILE_ENQUEUED_FOR_COMPILATION -> {
                    Log.i("BaselineProfile", "Profile enqueued for compilation")
                }
                else -> {
                    Log.w("BaselineProfile", "Unknown profile status")
                }
            }
        }
    }
}

// Check in Application.onCreate()
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        if (BuildConfig.DEBUG) {
            ProfileVerifier().checkProfileInstallation(this)
        }
    }
}
```

**Manual Profile Installation (Testing):**

```bash
# Install APK with baseline profile
adb install -r app-release.apk

# Force profile compilation (for testing)
adb shell cmd package compile -f -m speed-profile com.example.app

# Verify compilation
adb shell dumpsys package dexopt | grep com.example.app

# Output should show:
# [com.example.app]
#   path: /data/app/~~xxx/com.example.app-xxx/base.apk
#   arm64: [status=speed-profile] [reason=install]
```

#### 5. **Benchmarking Impact**

```kotlin
// Create benchmark module to measure improvements

@RunWith(AndroidJUnit4::class)
class StartupBenchmark {

    @get:Rule
    val benchmarkRule = MacrobenchmarkRule()

    @Test
    fun startupNoCompilation() = benchmark(CompilationMode.None())

    @Test
    fun startupBaselineProfile() = benchmark(CompilationMode.Partial(
        warmupIterations = 3
    ))

    @Test
    fun startupFullCompilation() = benchmark(CompilationMode.Full())

    private fun benchmark(compilationMode: CompilationMode) {
        benchmarkRule.measureRepeated(
            packageName = "com.example.app",
            metrics = listOf(StartupTimingMetric()),
            iterations = 10,
            compilationMode = compilationMode,
            startupMode = StartupMode.COLD
        ) {
            pressHome()
            startActivityAndWait()
        }
    }
}

// Run benchmarks
// ./gradlew :benchmark:connectedBenchmarkAndroidTest

// Results:
// startupNoCompilation       timeToInitialDisplayMs   min 856,   median 892,   max 1024
// startupBaselineProfile     timeToInitialDisplayMs   min 524,   median 558,   max 612
// startupFullCompilation     timeToInitialDisplayMs   min 498,   median 532,   max 589
```

#### 6. **Library Baseline Profiles**

```kotlin
// If you're creating a library, include baseline profiles

// library/build.gradle.kts
plugins {
    id("com.android.library")
    id("androidx.baselineprofile")
}

android {
    // ...
}

// Library profile will be merged with app profile automatically
```

**Library Profile Example:**

```
# library/src/main/baseline-prof.txt

# Public API surface
Lcom/example/library/MyLibrary;
HSPLcom/example/library/MyLibrary;-><init>()V
HSPLcom/example/library/MyLibrary;->initialize(Landroid/content/Context;)V

# Critical internal classes
Lcom/example/library/internal/DataProcessor;
Lcom/example/library/internal/CacheManager;
```

#### 7. **Best Practices**

```kotlin
// 1. Profile critical user journeys only
@Test
fun criticalJourneys() = baselineProfileRule.collect(
    packageName = "com.example.app",
    profileBlock = {
        // Focus on:
        // - App startup
        // - First screen interaction
        // - Most common user flows
        // - Performance-critical features

        // Don't include:
        // - Rare settings screens
        // - Edge cases
        // - Error handling paths
    }
)

// 2. Keep profile size reasonable
// Target: < 200KB for profile file
// Larger profiles → longer install time

// 3. Update profiles with major releases
// Regenerate when:
// - Major architecture changes
// - New critical features
// - Significant code refactoring

// 4. Test on release builds
// Profiles only effective with R8/ProGuard enabled

// 5. Combine with other optimizations
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        // Baseline profile helps, but still:
        // - Defer non-critical initialization
        // - Use App Startup library
        // - Lazy load libraries
        // - Optimize layouts
    }
}
```

#### 8. **Monitoring in Production**

```kotlin
class PerformanceMonitor {

    fun trackStartupTime(context: Context) {
        // Log startup time with/without profile
        val startupTime = getStartupTime()

        Firebase.analytics.logEvent("app_startup") {
            param("startup_time_ms", startupTime)
            param("has_baseline_profile", hasBaselineProfile(context))
            param("compilation_status", getCompilationStatus(context))
        }
    }

    private fun hasBaselineProfile(context: Context): Boolean {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            val status = ProfileVerifier.getCompilationStatusAsync().get()
            return status.hasReferenceProfile()
        }
        return false
    }
}
```

### Performance Gains

**Typical Improvements:**
- Cold startup: 20-40% faster
- Warm startup: 15-30% faster
- First interaction: 30-50% faster
- Jank reduction: 40-60% fewer dropped frames

**Requirements:**
- Android 9 (API 28) or higher for full benefits
- Android 7 (API 24) minimum for partial support
- Release build with R8/ProGuard enabled

### Best Practices

- [ ] Profile critical user journeys only
- [ ] Keep profile size under 200KB
- [ ] Regenerate with major releases
- [ ] Test on real devices, not emulators
- [ ] Verify installation in production
- [ ] Combine with other startup optimizations
- [ ] Benchmark before/after
- [ ] Include in library modules
- [ ] Monitor performance metrics
- Update documentation with regeneration steps

---

## Ответ (RU)

Baseline Profiles - это оптимизация производительности, которая сообщает Android Runtime (ART), какой код следует предварительно скомпилировать (AOT), сокращая время запуска приложения.

#### Как работает:

**Традиционная JIT-компиляция:**
- Приложение интерпретирует байткод
- Профилирует горячий код
- JIT-компилирует после прогрева
- Быстрое выполнение только после прогрева

**С Baseline Profile:**
- AOT-компиляция профилированного кода при установке
- Быстрый запуск сразу
- Немедленное быстрое выполнение

#### Генерация профиля:

1. **Создать отдельный модуль** для генерации профиля
2. **Написать тесты** критических пользовательских сценариев
3. **Запустить генерацию** на эмуляторе/устройстве
4. **Профиль сохраняется** в `baseline-prof.txt`

#### Формат профиля:

```
H - Hot метод (часто выполняется)
S - Startup метод (при запуске)
P - Post-startup метод (после запуска)
L - Ссылка на класс/метод
```

#### Верификация:

Используйте `ProfileVerifier` для проверки установки профиля в production.

#### Типичные улучшения:

- Холодный запуск: 20-40% быстрее
- Тёплый запуск: 15-30% быстрее
- Первое взаимодействие: 30-50% быстрее
- Снижение jank: 40-60% меньше пропущенных кадров

#### Требования:

- Android 9+ (полная поддержка)
- Android 7+ (частичная поддержка)
- Release сборка с R8/ProGuard

#### Лучшие практики:

- Профилируйте только критические сценарии
- Размер профиля < 200KB
- Регенерируйте при мажорных релизах
- Тестируйте на реальных устройствах
- Верифицируйте в production
- Комбинируйте с другими оптимизациями
