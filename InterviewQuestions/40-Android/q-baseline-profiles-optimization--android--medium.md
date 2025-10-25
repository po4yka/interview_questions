---
id: 20251011-220008
title: Baseline Profiles Optimization / Оптимизация с Baseline Profiles
aliases:
- Baseline Profiles Optimization
- Оптимизация с Baseline Profiles
topic: android
subtopics:
- performance-startup
- gradle
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-baseline-profiles-android--android--medium
- q-app-startup-optimization--android--medium
- q-android-performance-measurement-tools--android--medium
created: 2025-10-11
updated: 2025-10-15
tags:
- android/performance-startup
- android/gradle
- difficulty/medium
---

# Вопрос (RU)
> Как оптимизировать Android-приложение с помощью Baseline Profiles?

# Question (EN)
> How to optimize an Android app using Baseline Profiles?

---

## Ответ (RU)

### Что такое Baseline Profiles

**Теория**: Baseline Profiles сообщают Android Runtime (ART), какие пути кода компилировать ahead-of-time (AOT) для более быстрого запуска и плавной работы.

**Как работает**:
- Без профиля: Запуск → Интерпретация кода → JIT компиляция горячего кода → Постепенное улучшение
- С профилем: Установка → AOT компиляция критического кода → Запуск → Сразу быстрое выполнение

**Влияние на производительность**:
- Холодный запуск: на 30-40% быстрее
- Уменьшение рывков: на 15-20% меньше пропущенных кадров
- Начальный рендеринг: на 10-15% быстрее
- Стабильная производительность с первого запуска

### Реализация

(См. код и детали в английской секции - структура проекта, конфигурация модулей, генерация профиля, измерение производительности, облачные профили)

### Лучшие практики

**Генерация профиля**:
- Покрывать только критические пользовательские сценарии
- Тестировать на реальных устройствах, не эмуляторах
- Держать размер профиля меньше 200KB
- Перегенерировать при major релизах

**Мониторинг производительности**:
- Измерять до/после с помощью Macrobenchmark
- Мониторить установку профиля в продакшене
- Отслеживать метрики запуска в аналитике
- Комбинировать с другими оптимизациями запуска

**Интеграция CI/CD**:
- Автоматизировать генерацию профиля в CI
- Хранить baseline-prof.txt под версионным контролем
- Тестировать установку профиля в staging окружении

## Answer (EN)

### What Are Baseline Profiles

**Theory**: Baseline Profiles tell Android Runtime (ART) which code paths to ahead-of-time (AOT) compile for faster startup and smoother runtime performance. Understanding c-jit-aot-compilation is essential for optimization.

**How It Works**:
- Without Profile: App starts → Interpret code → JIT compile hot code → Gradual improvement
- With Profile: App installs → AOT compile critical code → App starts → Fast execution immediately

**Performance Impact**:
- Cold startup: 30-40% faster
- Jank reduction: 15-20% fewer dropped frames
- Initial rendering: 10-15% faster
- Consistent performance from first launch

### Implementation Setup

**Project Structure**:
```
MyApp/
 app/                    # Main app module
 baseline-profile/       # Profile generation module
    build.gradle.kts
    src/androidTest/java/
        BaselineProfileGenerator.kt
```

**Baseline Profile Module (build.gradle.kts)**:
```kotlin
// Theory: Configure test module for profile generation
plugins {
    id("com.android.test")
    id("org.jetbrains.kotlin.android")
    id("androidx.baselineprofile")
}

android {
    defaultConfig {
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    targetProjectPath = ":app"
    testOptions.managedDevices.devices {
        create<ManagedVirtualDevice>("pixel6Api33") {
            device = "Pixel 6"
            apiLevel = 33
            systemImageSource = "aosp"
        }
    }
}

dependencies {
    implementation("androidx.test.ext:junit:1.1.5")
    implementation("androidx.test.espresso:espresso-core:3.5.1")
    implementation("androidx.test.uiautomator:uiautomator:2.2.0")
    implementation("androidx.benchmark:benchmark-macro-junit4:1.2.0")
}
```

**Profile Generator**:
```kotlin
// Theory: Test critical user journeys to generate profile
@RunWith(AndroidJUnit4::class)
class BaselineProfileGenerator {

    @get:Rule
    val baselineProfileRule = BaselineProfileRule()

    @Test
    fun generate() = baselineProfileRule.collect(
        packageName = "com.example.app"
    ) {
        // Critical user journey: app launch to main screen
        pressHome()
        startActivityAndWait()

        // Navigate through key screens
        device.findObject(By.text("Home")).click()
        device.findObject(By.text("Profile")).click()
        device.findObject(By.text("Settings")).click()

        // Return to home
        device.pressBack()
        device.pressBack()
    }
}
```

**App Module Configuration**:
```kotlin
// Theory: Enable baseline profile consumption in main app
plugins {
    id("com.android.application")
    id("androidx.baselineprofile")
}

android {
    buildTypes {
        release {
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}

baselineProfile {
    // This specifies the managed devices to use that you run the tests on
    managedDevices += "pixel6Api33"
    // This enables using connected devices to generate profiles
    useConnectedDevices = false
}
```

### Performance Measurement

**Macrobenchmark Integration**:
```kotlin
// Theory: Measure startup performance with and without profiles
@RunWith(AndroidJUnit4::class)
class StartupBenchmark {

    @get:Rule
    val benchmarkRule = MacrobenchmarkRule()

    @Test
    fun startup() = benchmarkRule.measureRepeated(
        packageName = "com.example.app",
        metrics = listOf(StartupTimingMetric()),
        iterations = 5,
        startupMode = StartupMode.COLD
    ) {
        pressHome()
        startActivityAndWait()
    }
}
```

**Production Monitoring**:
```kotlin
// Theory: Monitor profile installation in production
class ProfileMonitor {
    fun checkProfileStatus(context: Context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            val status = ProfileVerifier.getCompilationStatusAsync().get()

            when (status.profileInstallResultCode) {
                ProfileVerifier.CompilationStatus.RESULT_CODE_COMPILED_WITH_PROFILE -> {
                    // Profile successfully installed and compiled
                    logMetric("profile_installed", 1)
                }
                ProfileVerifier.CompilationStatus.RESULT_CODE_NO_PROFILE -> {
                    // No profile found
                    logMetric("profile_missing", 1)
                }
                else -> {
                    logMetric("profile_unknown_status", 1)
                }
            }
        }
    }
}
```

### Cloud Profiles

**Setup Cloud Profiles**:
```kotlin
// Theory: Enable cloud profiles for Play Store distribution
dependencies {
    implementation("androidx.profileinstaller:profileinstaller:1.3.1")
}
```

**Cloud Profile Monitoring**:
```kotlin
// Theory: Monitor cloud profile installation
class CloudProfileMonitor {
    fun checkCloudProfileInstallation(context: Context) {
        val status = ProfileInstaller.writeProfile(context)
        when (status) {
            ProfileInstaller.RESULT_INSTALL_SUCCESS -> {
                Log.d("Profile", "Cloud profile installed successfully")
            }
            ProfileInstaller.RESULT_ALREADY_INSTALLED -> {
                Log.d("Profile", "Cloud profile already installed")
            }
            else -> {
                Log.w("Profile", "Cloud profile installation failed: $status")
            }
        }
    }
}
```

### Best Practices

**Profile Generation**:
- Cover critical user journeys only
- Test on real devices, not emulators
- Keep profile size under 200KB
- Regenerate with major releases

**Performance Monitoring**:
- Measure before/after with Macrobenchmark
- Monitor profile installation in production
- Track startup metrics in analytics
- Combine with other startup optimizations

**CI/CD Integration**:
- Automate profile generation in CI
- Version control baseline-prof.txt
- Test profile installation in staging

## Follow-ups

- How do you measure the impact of baseline profiles in production?
- What are the differences between baseline profiles and cloud profiles?
- How do you handle profile updates across app versions?

## References

- https://developer.android.com/topic/performance/baselineprofiles

## Related Questions

### Prerequisites (Easier)
- [[q-baseline-profiles-android--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]
- [[q-app-startup-library--android--medium]]

### Related (Same Level)
- [[q-app-startup-optimization--android--medium]]
- [[q-android-build-optimization--android--medium]]
- [[q-jit-vs-aot-compilation--android--medium]]

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]]
- [[q-android-runtime-art--android--medium]]
- [[q-offline-first-architecture--android--hard]]

