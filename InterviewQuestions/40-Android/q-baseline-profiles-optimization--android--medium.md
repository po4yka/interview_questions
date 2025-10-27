---
id: 20251011-220008
title: Baseline Profiles Optimization / Оптимизация с Baseline Profiles
aliases: [Baseline Profiles Optimization, Оптимизация с Baseline Profiles]
topic: android
subtopics:
  - gradle
  - performance-startup
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - q-android-performance-measurement-tools--android--medium
  - q-app-startup-optimization--android--medium
sources: []
created: 2025-10-11
updated: 2025-01-27
tags: [android/gradle, android/performance-startup, difficulty/medium]
---
# Вопрос (RU)
> Как оптимизировать Android-приложение с помощью Baseline Profiles?

# Question (EN)
> How to optimize an Android app using Baseline Profiles?

---

## Ответ (RU)

### Концепция

**Baseline Profiles** — механизм AOT-компиляции критических путей кода при установке приложения. ART компилирует указанные методы и классы заранее, минуя JIT, что ускоряет холодный старт на 30-40% и снижает количество пропущенных кадров.

**Как работает**:
- Без профиля: Запуск → Интерпретация → JIT по мере использования
- С профилем: Установка → AOT критического кода → Запуск сразу оптимизирован

### Реализация

**1. Структура модуля профилирования** (baseline-profile/build.gradle.kts):
```kotlin
// ✅ Модуль тестирования для генерации профиля
plugins {
    id("com.android.test")
    id("androidx.baselineprofile")
}

android {
    targetProjectPath = ":app"
    testOptions.managedDevices.devices {
        create<ManagedVirtualDevice>("pixel6Api33") {
            device = "Pixel 6"
            apiLevel = 33
        }
    }
}
```

**2. Генератор профиля**:
```kotlin
@RunWith(AndroidJUnit4::class)
class BaselineProfileGenerator {
    @get:Rule
    val rule = BaselineProfileRule()

    @Test
    fun generate() = rule.collect(
        packageName = "com.example.app"
    ) {
        // ✅ Покрывайте только критические сценарии запуска
        pressHome()
        startActivityAndWait()

        device.findObject(By.text("Home")).click()
        device.findObject(By.text("Profile")).click()
        // ❌ Не добавляйте редкие user flows
    }
}
```

**3. Конфигурация app модуля**:
```kotlin
// ✅ Включение применения профиля
plugins {
    id("androidx.baselineprofile")
}

baselineProfile {
    managedDevices += "pixel6Api33"
}
```

**4. Мониторинг в production**:
```kotlin
// ✅ Проверяйте установку профиля
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
    val status = ProfileVerifier.getCompilationStatusAsync().get()
    when (status.profileInstallResultCode) {
        CompilationStatus.RESULT_CODE_COMPILED_WITH_PROFILE -> {
            // Профиль применён
        }
        CompilationStatus.RESULT_CODE_NO_PROFILE -> {
            // Профиль отсутствует
        }
    }
}
```

### Лучшие Практики

- Покрывайте только критические пути (запуск, главный экран)
- Тестируйте на реальных устройствах
- Держите размер профиля < 200KB
- Перегенерируйте при крупных изменениях кодовой базы
- Измеряйте эффект через [[q-android-performance-measurement-tools--android--medium|Macrobenchmark]]
- Автоматизируйте генерацию в CI/CD

## Answer (EN)

### Concept

**Baseline Profiles** instruct Android Runtime (ART) to AOT-compile critical code paths at install time, bypassing JIT interpretation. This achieves 30-40% faster cold startup and reduces jank by pre-optimizing hot methods.

**How It Works**:
- Without Profile: App starts → Interpret code → JIT compile gradually
- With Profile: Install → AOT compile critical paths → Launch immediately optimized

### Implementation

**1. Profile Generation Module** (baseline-profile/build.gradle.kts):
```kotlin
// ✅ Test module for generating baseline profile
plugins {
    id("com.android.test")
    id("androidx.baselineprofile")
}

android {
    targetProjectPath = ":app"
    testOptions.managedDevices.devices {
        create<ManagedVirtualDevice>("pixel6Api33") {
            device = "Pixel 6"
            apiLevel = 33
        }
    }
}
```

**2. Profile Generator**:
```kotlin
@RunWith(AndroidJUnit4::class)
class BaselineProfileGenerator {
    @get:Rule
    val rule = BaselineProfileRule()

    @Test
    fun generate() = rule.collect(
        packageName = "com.example.app"
    ) {
        // ✅ Cover only critical startup flows
        pressHome()
        startActivityAndWait()

        device.findObject(By.text("Home")).click()
        device.findObject(By.text("Profile")).click()
        // ❌ Don't include rare user journeys
    }
}
```

**3. App Module Configuration**:
```kotlin
// ✅ Enable profile consumption
plugins {
    id("androidx.baselineprofile")
}

baselineProfile {
    managedDevices += "pixel6Api33"
}
```

**4. Production Monitoring**:
```kotlin
// ✅ Verify profile installation
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
    val status = ProfileVerifier.getCompilationStatusAsync().get()
    when (status.profileInstallResultCode) {
        CompilationStatus.RESULT_CODE_COMPILED_WITH_PROFILE -> {
            // Profile applied successfully
        }
        CompilationStatus.RESULT_CODE_NO_PROFILE -> {
            // Profile missing
        }
    }
}
```

**5. Benchmarking**:
```kotlin
@RunWith(AndroidJUnit4::class)
class StartupBenchmark {
    @get:Rule
    val benchmarkRule = MacrobenchmarkRule()

    @Test
    fun startup() = benchmarkRule.measureRepeated(
        packageName = "com.example.app",
        metrics = listOf(StartupTimingMetric()),
        startupMode = StartupMode.COLD
    ) {
        pressHome()
        startActivityAndWait()
    }
}
```

### Best Practices

- Focus on critical paths (startup, main screen navigation)
- Test on real devices for accurate profiling
- Keep profile size < 200KB
- Regenerate after significant code changes
- Measure impact with [[q-android-performance-measurement-tools--android--medium|Macrobenchmark]]
- Automate generation in CI/CD pipeline

## Follow-ups

- How does profile size correlate with compile time and app size?
- What's the trade-off between baseline profiles and R8 full mode optimization?
- How do you validate profile effectiveness for different Android API levels?
- What happens when a baseline profile references methods removed during ProGuard/R8 shrinking?

## References

- https://developer.android.com/topic/performance/baselineprofiles

## Related Questions

### Prerequisites (Easier)
- [[q-android-performance-measurement-tools--android--medium]]
- [[q-app-startup-optimization--android--medium]]

### Related (Same Level)
- [[q-app-startup-optimization--android--medium]]

### Advanced (Harder)
- Understanding ART compilation strategies
- Analyzing dex2oat compiler output for profile verification

