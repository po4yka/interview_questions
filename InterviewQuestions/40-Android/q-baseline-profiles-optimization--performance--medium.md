---
id: 20251011-220008
title: "Baseline Profiles Optimization / Оптимизация с Baseline Profiles"
aliases: []

# Classification
topic: android
subtopics:
  - performance
  - baseline-profiles
  - optimization
  - startup
  - jank
question_kind: practical
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru, android/performance, android/baseline-profiles, android/optimization, android/startup, android/jank, android/aot, android/macrobenchmark, difficulty/medium]
source: Original
source_note: Baseline profiles performance optimization

# Workflow & relations
status: draft
moc: moc-android
related: [macrobenchmark-startup, app-startup-optimization, jank-detection-frame-metrics]

# Timestamps
created: 2025-10-11
updated: 2025-10-11

tags: [en, ru, android/performance, android/baseline-profiles, android/optimization, android/startup, android/jank, android/aot, android/macrobenchmark, difficulty/medium]
---
# Question (EN)
> Generate and use Baseline Profiles for app startup and jank optimization. Set up Macrobenchmark for profile generation. Measure performance improvements in production.

# Вопрос (RU)
> Генерируйте и используйте Baseline Profiles для оптимизации запуска и рывков приложения. Настройте Macrobenchmark для генерации профилей. Измерьте улучшения производительности в продакшне.

---

## Answer (EN)

### Overview

**Baseline Profiles** tell the Android Runtime (ART) which code paths to ahead-of-time (AOT) compile for faster startup and smoother runtime performance.

**How it works:**
```
Without Baseline Profile:
1. App starts
2. Code runs interpreted (slow)
3. JIT compiler identifies hot code
4. Compiles hot code over time
Result: Slow initial startup, gradual improvement

With Baseline Profile:
1. App installs with profile
2. ART pre-compiles critical code (AOT)
3. App starts
4. Pre-compiled code runs immediately (fast)
Result: Fast startup from first launch
```

**Performance Improvements:**
- 30-40% faster cold startup
- 15-20% reduction in jank (dropped frames)
- 10-15% faster initial screen rendering
- Consistent performance from first launch

### Complete Baseline Profile Setup

#### 1. Project Structure

```
MyApp/
 app/                          # Main app module
 benchmark/                    # Macrobenchmark module (from earlier)
 baseline-profile/             # New profile generation module
    build.gradle.kts
    src/
        main/
            AndroidManifest.xml
        androidTest/
            java/
                com/example/baselineprofile/
                    BaselineProfileGenerator.kt
 settings.gradle.kts
```

#### 2. Add Baseline Profile Module

**settings.gradle.kts:**
```kotlin
include(":app")
include(":baseline-profile")
```

**baseline-profile/build.gradle.kts:**
```kotlin
plugins {
    id("com.android.test")
    id("org.jetbrains.kotlin.android")
    id("androidx.baselineprofile")
}

android {
    namespace = "com.example.baselineprofile"
    compileSdk = 34

    defaultConfig {
        minSdk = 28  // Baseline profiles require API 28+
        targetSdk = 34

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    targetProjectPath = ":app"

    testOptions {
        managedDevices {
            devices {
                // Use API 31+ for best profile generation
                create<ManagedVirtualDevice>("pixel6Api31") {
                    device = "Pixel 6"
                    apiLevel = 31
                    systemImageSource = "aosp"
                }
            }
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    implementation("androidx.test.ext:junit:1.1.5")
    implementation("androidx.test.espresso:espresso-core:3.5.1")
    implementation("androidx.test.uiautomator:uiautomator:2.3.0")
    implementation("androidx.benchmark:benchmark-macro-junit4:1.2.2")
}

baselineProfile {
    // Configure profile generation
    managedDevices += "pixel6Api31"
    useConnectedDevices = false
}
```

**baseline-profile/src/main/AndroidManifest.xml:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
</manifest>
```

#### 3. Configure App Module

**app/build.gradle.kts:**
```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("androidx.baselineprofile")  // Add plugin
}

android {
    // ... existing configuration

    buildTypes {
        release {
            // Enable baseline profile
            isProfileable = true
        }

        create("benchmark") {
            initWith(getByName("release"))
            signingConfig = signingConfigs.getByName("debug")
            matchingFallbacks += listOf("release")
            isDebuggable = false
            isProfileable = true  // Required for profile generation
        }
    }
}

dependencies {
    // Baseline profile dependency
    implementation("androidx.profileinstaller:profileinstaller:1.3.1")

    // Profile will be generated and included automatically
    "baselineProfile"(project(":baseline-profile"))
}
```

### Generate Baseline Profile

**BaselineProfileGenerator.kt:**
```kotlin
package com.example.baselineprofile

import android.os.Build
import androidx.annotation.RequiresApi
import androidx.benchmark.macro.junit4.BaselineProfileRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.filters.LargeTest
import androidx.test.uiautomator.By
import androidx.test.uiautomator.Direction
import androidx.test.uiautomator.Until
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * Baseline Profile Generator
 *
 * Generates profiles for critical user journeys:
 * - App startup
 * - Home screen browsing
 * - Settings navigation
 * - Search functionality
 *
 * Run:
 * ./gradlew :baseline-profile:generateBaselineProfile
 *
 * Output:
 * app/src/main/baseline-prof.txt
 */
@RequiresApi(Build.VERSION_CODES.P)
@LargeTest
@RunWith(AndroidJUnit4::class)
class BaselineProfileGenerator {

    @get:Rule
    val rule = BaselineProfileRule()

    @Test
    fun generate() {
        rule.collect(
            packageName = "com.example.myapp",
            includeInStartupProfile = true,  // Include in startup profile
            profileBlock = {
                // Critical user journeys to profile

                // Journey 1: App Startup
                pressHome()
                startActivityAndWait()
                waitForAsyncContent()

                // Journey 2: Browse Home Screen
                browseHomeScreen()

                // Journey 3: Navigate to Settings
                navigateToSettings()

                // Journey 4: Use Search
                performSearch()

                // Journey 5: View Details
                viewItemDetails()

                // Journey 6: Scroll List
                scrollThroughList()
            }
        )
    }

    /**
     * Wait for async content to load after startup
     */
    private fun BaselineProfileRule.ProfileBlock.waitForAsyncContent() {
        device.wait(
            Until.hasObject(By.res(packageName, "main_content")),
            5_000
        )

        // Wait for network content
        device.wait(
            Until.hasObject(By.res(packageName, "content_loaded")),
            10_000
        )
    }

    /**
     * Browse home screen content
     */
    private fun BaselineProfileRule.ProfileBlock.browseHomeScreen() {
        val scrollable = device.findObject(By.res(packageName, "home_recyclerview"))
        scrollable?.apply {
            // Scroll down to trigger ViewHolder binding
            repeat(5) {
                scroll(Direction.DOWN, 0.8f)
                device.waitForIdle()
            }

            // Scroll back up
            repeat(5) {
                scroll(Direction.UP, 0.8f)
                device.waitForIdle()
            }
        }
    }

    /**
     * Navigate to settings screen
     */
    private fun BaselineProfileRule.ProfileBlock.navigateToSettings() {
        // Open navigation drawer
        val menuButton = device.findObject(By.desc("Menu"))
        menuButton?.click()
        device.waitForIdle()

        // Click settings
        val settingsButton = device.findObject(By.text("Settings"))
        settingsButton?.click()
        device.waitForIdle()

        // Wait for settings to load
        device.wait(
            Until.hasObject(By.res(packageName, "settings_container")),
            2_000
        )

        // Navigate back
        device.pressBack()
        device.waitForIdle()
    }

    /**
     * Perform search operation
     */
    private fun BaselineProfileRule.ProfileBlock.performSearch() {
        // Open search
        val searchButton = device.findObject(By.desc("Search"))
        searchButton?.click()
        device.waitForIdle()

        // Type search query
        val searchField = device.findObject(By.res(packageName, "search_field"))
        searchField?.text = "test query"
        device.waitForIdle()

        // Wait for results
        device.wait(
            Until.hasObject(By.res(packageName, "search_results")),
            3_000
        )

        // Close search
        device.pressBack()
        device.waitForIdle()
    }

    /**
     * View item details
     */
    private fun BaselineProfileRule.ProfileBlock.viewItemDetails() {
        // Click first item
        val firstItem = device.findObject(By.res(packageName, "item_card"))
        firstItem?.click()
        device.waitForIdle()

        // Wait for details to load
        device.wait(
            Until.hasObject(By.res(packageName, "detail_content")),
            2_000
        )

        // Scroll detail page
        val detailScroll = device.findObject(By.res(packageName, "detail_scroll"))
        detailScroll?.scroll(Direction.DOWN, 0.8f)
        device.waitForIdle()

        // Navigate back
        device.pressBack()
        device.waitForIdle()
    }

    /**
     * Scroll through long list
     */
    private fun BaselineProfileRule.ProfileBlock.scrollThroughList() {
        val list = device.findObject(By.res(packageName, "item_list"))
        list?.apply {
            // Fast scroll to trigger many bindings
            repeat(10) {
                fling(Direction.DOWN)
                device.waitForIdle()
            }
        }
    }
}
```

### Generate and Verify Profile

**Generate profile:**
```bash
# Generate baseline profile
./gradlew :baseline-profile:generateBaselineProfile

# Output location:
# app/src/main/baseline-prof.txt
```

**baseline-prof.txt (example):**
```
# Baseline profile for com.example.myapp
# Generated by androidx.benchmark.macro

# Startup critical paths
Lcom/example/myapp/MainActivity;-><init>()V
Lcom/example/myapp/MainActivity;->onCreate(Landroid/os/Bundle;)V
Lcom/example/myapp/ui/HomeScreenKt;->HomeScreen(Landroidx/compose/runtime/Composer;I)V

# ViewModel initialization
Lcom/example/myapp/viewmodel/HomeViewModel;-><init>(Lcom/example/myapp/repository/Repository;)V
Lcom/example/myapp/viewmodel/HomeViewModel;->loadData()V

# Repository and data layer
Lcom/example/myapp/repository/RepositoryImpl;->fetchData()Ljava/lang/Object;
Lcom/example/myapp/data/database/UserDao_Impl;->getAll()Ljava/util/List;

# Compose UI rendering
Landroidx/compose/ui/platform/AndroidComposeView;->onMeasure(II)V
Landroidx/compose/ui/platform/AndroidComposeView;->onLayout(ZIIII)V

# RecyclerView and adapters
Lcom/example/myapp/adapter/ItemAdapter;->onBindViewHolder(Landroidx/recyclerview/widget/RecyclerView$ViewHolder;I)V
Lcom/example/myapp/adapter/ItemViewHolder;->bind(Lcom/example/myapp/model/Item;)V

# Hot paths identified during profiling
# (Methods called frequently during user journeys)
```

**Verify profile inclusion:**
```bash
# Check if profile is included in APK
unzip -l app/build/outputs/apk/release/app-release.apk | grep baseline

# Should show:
# assets/dexopt/baseline.prof
# assets/dexopt/baseline.profm
```

### Measure Performance Impact

**Benchmark WITH baseline profile:**

**StartupBenchmarkWithProfile.kt:**
```kotlin
@Test
fun startupWithBaselineProfile() {
    benchmarkRule.measureRepeated(
        packageName = PACKAGE_NAME,
        metrics = listOf(StartupTimingMetric()),
        compilationMode = CompilationMode.Partial(
            baselineProfileMode = BaselineProfileMode.Require
        ),
        iterations = 20,
        startupMode = StartupMode.COLD
    ) {
        pressHome()
        startActivityAndWait()
    }
}

@Test
fun startupWithoutBaselineProfile() {
    benchmarkRule.measureRepeated(
        packageName = PACKAGE_NAME,
        metrics = listOf(StartupTimingMetric()),
        compilationMode = CompilationMode.None(),  // No AOT compilation
        iterations = 20,
        startupMode = StartupMode.COLD
    ) {
        pressHome()
        startActivityAndWait()
    }
}
```

**Results:**
```
Without Baseline Profile (interpreted):
  timeToInitialDisplayMs: min 680, median 735, max 820

With Baseline Profile (AOT):
  timeToInitialDisplayMs: min 420, median 485, max 560

Improvement: 34% faster startup (735ms → 485ms)
```

### Library Baseline Profiles

For libraries, generate profiles for common usage patterns:

**library/build.gradle.kts:**
```kotlin
plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.android")
    id("androidx.baselineprofile")
}

android {
    namespace = "com.example.mylib"

    buildTypes {
        create("benchmark") {
            initWith(getByName("release"))
            isProfileable = true
        }
    }
}

dependencies {
    implementation("androidx.profileinstaller:profileinstaller:1.3.1")
    "baselineProfile"(project(":library-baseline-profile"))
}
```

**Library usage profile generator:**
```kotlin
class LibraryBaselineProfileGenerator {

    @get:Rule
    val rule = BaselineProfileRule()

    @Test
    fun generate() {
        rule.collect(
            packageName = "com.example.mylib.sample",  // Sample app using library
            includeInStartupProfile = true
        ) {
            // Common library usage patterns
            startActivityAndWait()

            // Use library API
            device.wait(Until.hasObject(By.text("Load Data")), 2_000)
            device.findObject(By.text("Load Data"))?.click()
            device.waitForIdle()

            // Process data
            device.wait(Until.hasObject(By.text("Process")), 2_000)
            device.findObject(By.text("Process"))?.click()
            device.waitForIdle()
        }
    }
}
```

### Cloud Profiles (Play Store)

Google Play can generate profiles from real user behavior:

**app/build.gradle.kts:**
```kotlin
android {
    buildTypes {
        release {
            // Enable cloud profile installation
            isProfileable = true
        }
    }
}

dependencies {
    // Required for cloud profiles
    implementation("androidx.profileinstaller:profileinstaller:1.3.1")
}
```

**Monitor cloud profile installation:**
```kotlin
class MyApplication : Application() {

    override fun onCreate() {
        super.onCreate()

        // Check if profile is installed
        val status = ProfileInstaller.writeProfile(this)
        when (status) {
            ProfileInstaller.RESULT_INSTALL_SUCCESS -> {
                Log.d("Profile", "Baseline profile installed successfully")
            }
            ProfileInstaller.RESULT_ALREADY_INSTALLED -> {
                Log.d("Profile", "Baseline profile already installed")
            }
            ProfileInstaller.RESULT_NOT_WRITABLE -> {
                Log.w("Profile", "Profile not writable")
            }
            else -> {
                Log.e("Profile", "Profile installation failed: $status")
            }
        }
    }
}
```

### CI/CD Integration

**GitHub Actions workflow:**
```yaml
name: Generate Baseline Profile

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  generate-profile:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Enable KVM
        run: |
          echo 'KERNEL=="kvm", GROUP="kvm", MODE="0666"' | sudo tee /etc/udev/rules.d/99-kvm4all.rules
          sudo udevadm control --reload-rules
          sudo udevadm trigger --name-match=kvm

      - name: Generate Baseline Profile
        run: |
          ./gradlew :baseline-profile:generateBaselineProfile \
            --no-daemon \
            --stacktrace

      - name: Verify Profile Generated
        run: |
          if [ ! -f "app/src/main/baseline-prof.txt" ]; then
            echo "Baseline profile not generated!"
            exit 1
          fi

          # Show profile size
          wc -l app/src/main/baseline-prof.txt

      - name: Commit Profile (if changed)
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"

          if git diff --quiet app/src/main/baseline-prof.txt; then
            echo "No changes to baseline profile"
          else
            git add app/src/main/baseline-prof.txt
            git commit -m "Update baseline profile [skip ci]"
            git push
          fi
```

### Best Practices

1. **Cover Critical Journeys**: Profile most common user flows
2. **Update Regularly**: Regenerate when adding features
3. **Measure Impact**: Benchmark before/after profile
4. **Version Control**: Commit baseline-prof.txt to git
5. **Library Profiles**: Create profiles for reusable libraries
6. **Cloud Profiles**: Enable for Play Store distribution
7. **API 28+ Target**: Baseline profiles require API 28+
8. **Realistic Scenarios**: Profile actual user behavior, not edge cases
9. **Monitor Installation**: Log profile installation status
10. **CI Integration**: Automate profile generation in CI/CD
11. **Combine with Macrobenchmark**: Use same test scenarios
12. **Keep Updated**: Regenerate after significant code changes

### Common Pitfalls

1. **Not Profiling Real Journeys**: Generate profiles for actual user flows
2. **Stale Profiles**: Not updating after code changes
3. **Missing ProfileInstaller**: Dependency required for runtime
4. **Too Narrow**: Only profiling startup, missing hot paths
5. **Not Measuring**: Generating profile but not verifying improvement
6. **API < 28**: Baseline profiles not supported
7. **Debug Builds**: Profiles only work in release/benchmark builds
8. **Not Version Controlled**: Profile should be in git
9. **Overly Complex**: Profiling every possible path (diminishing returns)
10. **Ignoring Cloud Profiles**: Missing real-world optimizations

## Ответ (RU)

### Обзор

**Baseline Profiles** сообщают Android Runtime (ART), какие участки кода необходимо скомпилировать заранее (ahead-of-time, AOT) для более быстрого запуска и плавной работы приложения.

**Принцип работы:**
```
Без Baseline Profile:
1. Приложение запускается
2. Код выполняется в интерпретируемом режиме (медленно)
3. JIT-компилятор определяет горячий код
4. Компилирует горячий код со временем
Результат: Медленный начальный запуск, постепенное улучшение

С Baseline Profile:
1. Приложение устанавливается с профилем
2. ART предварительно компилирует критичный код (AOT)
3. Приложение запускается
4. Предварительно скомпилированный код выполняется сразу (быстро)
Результат: Быстрый запуск с первого раза
```

**Улучшения производительности:**
- На 30-40% быстрее холодный старт
- На 15-20% снижение рывков (dropped frames)
- На 10-15% быстрее начальная отрисовка экрана
- Стабильная производительность с первого запуска

### Полная настройка Baseline Profile

#### 1. Структура проекта

```
MyApp/
 app/                          # Основной модуль приложения
 benchmark/                    # Модуль Macrobenchmark (из предыдущего раздела)
 baseline-profile/             # Новый модуль генерации профилей
    build.gradle.kts
    src/
        main/
            AndroidManifest.xml
        androidTest/
            java/
                com/example/baselineprofile/
                    BaselineProfileGenerator.kt
 settings.gradle.kts
```

#### 2. Добавление модуля Baseline Profile

**settings.gradle.kts:**
```kotlin
include(":app")
include(":baseline-profile")
```

**baseline-profile/build.gradle.kts:**
```kotlin
plugins {
    id("com.android.test")
    id("org.jetbrains.kotlin.android")
    id("androidx.baselineprofile")
}

android {
    namespace = "com.example.baselineprofile"
    compileSdk = 34

    defaultConfig {
        minSdk = 28  // Baseline profiles требуют API 28+
        targetSdk = 34

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    targetProjectPath = ":app"

    testOptions {
        managedDevices {
            devices {
                // Используйте API 31+ для лучшей генерации профилей
                create<ManagedVirtualDevice>("pixel6Api31") {
                    device = "Pixel 6"
                    apiLevel = 31
                    systemImageSource = "aosp"
                }
            }
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    implementation("androidx.test.ext:junit:1.1.5")
    implementation("androidx.test.espresso:espresso-core:3.5.1")
    implementation("androidx.test.uiautomator:uiautomator:2.3.0")
    implementation("androidx.benchmark:benchmark-macro-junit4:1.2.2")
}

baselineProfile {
    // Настройка генерации профилей
    managedDevices += "pixel6Api31"
    useConnectedDevices = false
}
```

**baseline-profile/src/main/AndroidManifest.xml:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
</manifest>
```

#### 3. Настройка модуля приложения

**app/build.gradle.kts:**
```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("androidx.baselineprofile")  // Добавляем плагин
}

android {
    // ... существующая конфигурация

    buildTypes {
        release {
            // Включаем baseline profile
            isProfileable = true
        }

        create("benchmark") {
            initWith(getByName("release"))
            signingConfig = signingConfigs.getByName("debug")
            matchingFallbacks += listOf("release")
            isDebuggable = false
            isProfileable = true  // Требуется для генерации профилей
        }
    }
}

dependencies {
    // Зависимость для Baseline profile
    implementation("androidx.profileinstaller:profileinstaller:1.3.1")

    // Профиль будет сгенерирован и включен автоматически
    "baselineProfile"(project(":baseline-profile"))
}
```

### Генерация Baseline Profile

**BaselineProfileGenerator.kt:**
```kotlin
package com.example.baselineprofile

import android.os.Build
import androidx.annotation.RequiresApi
import androidx.benchmark.macro.junit4.BaselineProfileRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.filters.LargeTest
import androidx.test.uiautomator.By
import androidx.test.uiautomator.Direction
import androidx.test.uiautomator.Until
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * Генератор Baseline Profile
 *
 * Генерирует профили для критических пользовательских сценариев:
 * - Запуск приложения
 * - Просмотр главного экрана
 * - Навигация в настройки
 * - Функционал поиска
 *
 * Запуск:
 * ./gradlew :baseline-profile:generateBaselineProfile
 *
 * Результат:
 * app/src/main/baseline-prof.txt
 */
@RequiresApi(Build.VERSION_CODES.P)
@LargeTest
@RunWith(AndroidJUnit4::class)
class BaselineProfileGenerator {

    @get:Rule
    val rule = BaselineProfileRule()

    @Test
    fun generate() {
        rule.collect(
            packageName = "com.example.myapp",
            includeInStartupProfile = true,  // Включить в startup profile
            profileBlock = {
                // Критические пользовательские сценарии для профилирования

                // Сценарий 1: Запуск приложения
                pressHome()
                startActivityAndWait()
                waitForAsyncContent()

                // Сценарий 2: Просмотр главного экрана
                browseHomeScreen()

                // Сценарий 3: Навигация в настройки
                navigateToSettings()

                // Сценарий 4: Использование поиска
                performSearch()

                // Сценарий 5: Просмотр деталей
                viewItemDetails()

                // Сценарий 6: Прокрутка списка
                scrollThroughList()
            }
        )
    }

    /**
     * Ожидание загрузки асинхронного контента после запуска
     */
    private fun BaselineProfileRule.ProfileBlock.waitForAsyncContent() {
        device.wait(
            Until.hasObject(By.res(packageName, "main_content")),
            5_000
        )

        // Ожидание сетевого контента
        device.wait(
            Until.hasObject(By.res(packageName, "content_loaded")),
            10_000
        )
    }

    /**
     * Просмотр контента главного экрана
     */
    private fun BaselineProfileRule.ProfileBlock.browseHomeScreen() {
        val scrollable = device.findObject(By.res(packageName, "home_recyclerview"))
        scrollable?.apply {
            // Прокрутка вниз для триггера привязки ViewHolder
            repeat(5) {
                scroll(Direction.DOWN, 0.8f)
                device.waitForIdle()
            }

            // Прокрутка обратно вверх
            repeat(5) {
                scroll(Direction.UP, 0.8f)
                device.waitForIdle()
            }
        }
    }

    /**
     * Навигация на экран настроек
     */
    private fun BaselineProfileRule.ProfileBlock.navigateToSettings() {
        // Открываем навигационный drawer
        val menuButton = device.findObject(By.desc("Menu"))
        menuButton?.click()
        device.waitForIdle()

        // Кликаем на настройки
        val settingsButton = device.findObject(By.text("Settings"))
        settingsButton?.click()
        device.waitForIdle()

        // Ожидаем загрузки настроек
        device.wait(
            Until.hasObject(By.res(packageName, "settings_container")),
            2_000
        )

        // Возвращаемся назад
        device.pressBack()
        device.waitForIdle()
    }

    /**
     * Выполнение операции поиска
     */
    private fun BaselineProfileRule.ProfileBlock.performSearch() {
        // Открываем поиск
        val searchButton = device.findObject(By.desc("Search"))
        searchButton?.click()
        device.waitForIdle()

        // Вводим поисковый запрос
        val searchField = device.findObject(By.res(packageName, "search_field"))
        searchField?.text = "test query"
        device.waitForIdle()

        // Ожидаем результаты
        device.wait(
            Until.hasObject(By.res(packageName, "search_results")),
            3_000
        )

        // Закрываем поиск
        device.pressBack()
        device.waitForIdle()
    }

    /**
     * Просмотр деталей элемента
     */
    private fun BaselineProfileRule.ProfileBlock.viewItemDetails() {
        // Кликаем на первый элемент
        val firstItem = device.findObject(By.res(packageName, "item_card"))
        firstItem?.click()
        device.waitForIdle()

        // Ожидаем загрузки деталей
        device.wait(
            Until.hasObject(By.res(packageName, "detail_content")),
            2_000
        )

        // Прокручиваем страницу деталей
        val detailScroll = device.findObject(By.res(packageName, "detail_scroll"))
        detailScroll?.scroll(Direction.DOWN, 0.8f)
        device.waitForIdle()

        // Возвращаемся назад
        device.pressBack()
        device.waitForIdle()
    }

    /**
     * Прокрутка длинного списка
     */
    private fun BaselineProfileRule.ProfileBlock.scrollThroughList() {
        val list = device.findObject(By.res(packageName, "item_list"))
        list?.apply {
            // Быстрая прокрутка для триггера множественных привязок
            repeat(10) {
                fling(Direction.DOWN)
                device.waitForIdle()
            }
        }
    }
}
```

### Генерация и проверка профиля

**Генерация профиля:**
```bash
# Генерируем baseline profile
./gradlew :baseline-profile:generateBaselineProfile

# Расположение результата:
# app/src/main/baseline-prof.txt
```

**baseline-prof.txt (пример):**
```
# Baseline profile для com.example.myapp
# Сгенерирован androidx.benchmark.macro

# Критические пути запуска
Lcom/example/myapp/MainActivity;-><init>()V
Lcom/example/myapp/MainActivity;->onCreate(Landroid/os/Bundle;)V
Lcom/example/myapp/ui/HomeScreenKt;->HomeScreen(Landroidx/compose/runtime/Composer;I)V

# Инициализация ViewModel
Lcom/example/myapp/viewmodel/HomeViewModel;-><init>(Lcom/example/myapp/repository/Repository;)V
Lcom/example/myapp/viewmodel/HomeViewModel;->loadData()V

# Repository и data layer
Lcom/example/myapp/repository/RepositoryImpl;->fetchData()Ljava/lang/Object;
Lcom/example/myapp/data/database/UserDao_Impl;->getAll()Ljava/util/List;

# Compose UI отрисовка
Landroidx/compose/ui/platform/AndroidComposeView;->onMeasure(II)V
Landroidx/compose/ui/platform/AndroidComposeView;->onLayout(ZIIII)V

# RecyclerView и адаптеры
Lcom/example/myapp/adapter/ItemAdapter;->onBindViewHolder(Landroidx/recyclerview/widget/RecyclerView$ViewHolder;I)V
Lcom/example/myapp/adapter/ItemViewHolder;->bind(Lcom/example/myapp/model/Item;)V

# Горячие пути, определенные при профилировании
# (Методы, часто вызываемые во время пользовательских сценариев)
```

**Проверка включения профиля:**
```bash
# Проверяем, включен ли профиль в APK
unzip -l app/build/outputs/apk/release/app-release.apk | grep baseline

# Должно показать:
# assets/dexopt/baseline.prof
# assets/dexopt/baseline.profm
```

### Измерение влияния на производительность

**Бенчмарк С baseline profile:**

**StartupBenchmarkWithProfile.kt:**
```kotlin
@Test
fun startupWithBaselineProfile() {
    benchmarkRule.measureRepeated(
        packageName = PACKAGE_NAME,
        metrics = listOf(StartupTimingMetric()),
        compilationMode = CompilationMode.Partial(
            baselineProfileMode = BaselineProfileMode.Require
        ),
        iterations = 20,
        startupMode = StartupMode.COLD
    ) {
        pressHome()
        startActivityAndWait()
    }
}

@Test
fun startupWithoutBaselineProfile() {
    benchmarkRule.measureRepeated(
        packageName = PACKAGE_NAME,
        metrics = listOf(StartupTimingMetric()),
        compilationMode = CompilationMode.None(),  // Без AOT компиляции
        iterations = 20,
        startupMode = StartupMode.COLD
    ) {
        pressHome()
        startActivityAndWait()
    }
}
```

**Результаты:**
```
Без Baseline Profile (интерпретируемый режим):
  timeToInitialDisplayMs: min 680, median 735, max 820

С Baseline Profile (AOT):
  timeToInitialDisplayMs: min 420, median 485, max 560

Улучшение: на 34% быстрее запуск (735ms → 485ms)
```

### Baseline Profiles для библиотек

Для библиотек генерируйте профили для общих паттернов использования:

**library/build.gradle.kts:**
```kotlin
plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.android")
    id("androidx.baselineprofile")
}

android {
    namespace = "com.example.mylib"

    buildTypes {
        create("benchmark") {
            initWith(getByName("release"))
            isProfileable = true
        }
    }
}

dependencies {
    implementation("androidx.profileinstaller:profileinstaller:1.3.1")
    "baselineProfile"(project(":library-baseline-profile"))
}
```

### Облачные профили (Play Store)

Google Play может генерировать профили на основе реального поведения пользователей:

**app/build.gradle.kts:**
```kotlin
android {
    buildTypes {
        release {
            // Включаем установку облачных профилей
            isProfileable = true
        }
    }
}

dependencies {
    // Необходимо для облачных профилей
    implementation("androidx.profileinstaller:profileinstaller:1.3.1")
}
```

**Мониторинг установки облачных профилей:**
```kotlin
class MyApplication : Application() {

    override fun onCreate() {
        super.onCreate()

        // Проверяем, установлен ли профиль
        val status = ProfileInstaller.writeProfile(this)
        when (status) {
            ProfileInstaller.RESULT_INSTALL_SUCCESS -> {
                Log.d("Profile", "Baseline profile установлен успешно")
            }
            ProfileInstaller.RESULT_ALREADY_INSTALLED -> {
                Log.d("Profile", "Baseline profile уже установлен")
            }
            ProfileInstaller.RESULT_NOT_WRITABLE -> {
                Log.w("Profile", "Профиль недоступен для записи")
            }
            else -> {
                Log.e("Profile", "Установка профиля не удалась: $status")
            }
        }
    }
}
```

### Лучшие практики

1. **Охватывайте критические сценарии**: Профилируйте наиболее распространенные пользовательские потоки
2. **Регулярно обновляйте**: Перегенерируйте при добавлении функций
3. **Измеряйте эффект**: Проводите бенчмарки до/после профиля
4. **Контроль версий**: Коммитьте baseline-prof.txt в git
5. **Профили библиотек**: Создавайте профили для переиспользуемых библиотек
6. **Облачные профили**: Включайте для распространения через Play Store
7. **Цель API 28+**: Baseline profiles требуют API 28+
8. **Реалистичные сценарии**: Профилируйте реальное поведение пользователей, а не крайние случаи
9. **Мониторинг установки**: Логируйте статус установки профиля
10. **Интеграция CI**: Автоматизируйте генерацию профилей в CI/CD
11. **Совмещайте с Macrobenchmark**: Используйте те же тестовые сценарии
12. **Поддерживайте актуальность**: Перегенерируйте после значительных изменений кода

### Распространенные ошибки

1. **Не профилируют реальные сценарии**: Генерация профилей не для реальных пользовательских потоков
2. **Устаревшие профили**: Не обновляют после изменений кода
3. **Отсутствует ProfileInstaller**: Зависимость необходима для runtime
4. **Слишком узко**: Профилирование только запуска, пропуск горячих путей
5. **Не измеряют**: Генерируют профиль, но не проверяют улучшение
6. **API < 28**: Baseline profiles не поддерживаются
7. **Debug сборки**: Профили работают только в release/benchmark сборках
8. **Не под контролем версий**: Профиль должен быть в git
9. **Чрезмерная сложность**: Профилирование каждого возможного пути (убывающая отдача)
10. **Игнорирование облачных профилей**: Пропуск оптимизаций из реального мира

---

## References
- [Baseline Profiles](https://developer.android.com/topic/performance/baselineprofiles)
- [ProfileInstaller](https://developer.android.com/jetpack/androidx/releases/profileinstaller)
- [Macrobenchmark](https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview)

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - Recyclerview
### Related (Medium)
- [[q-app-startup-optimization--performance--medium]] - Performance
- [[q-app-size-optimization--performance--medium]] - Performance
- [[q-macrobenchmark-startup--performance--medium]] - Performance
- [[q-memory-leak-detection--performance--medium]] - Performance
### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Jetpack Compose
