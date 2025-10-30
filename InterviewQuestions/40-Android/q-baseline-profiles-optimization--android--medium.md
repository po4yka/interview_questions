---
id: 20251011-220008
title: Baseline Profiles Optimization / Оптимизация с Baseline Profiles
aliases: [Baseline Profiles Optimization, Оптимизация с Baseline Profiles]
topic: android
subtopics: [gradle, performance-startup, profiling]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-performance-measurement-tools--android--medium, q-app-startup-optimization--android--medium]
sources: []
created: 2025-10-11
updated: 2025-10-29
tags: [android/gradle, android/performance-startup, android/profiling, difficulty/medium]
---
# Вопрос (RU)
> Как оптимизировать Android-приложение с помощью Baseline Profiles?

# Question (EN)
> How to optimize an Android app using Baseline Profiles?

---

## Ответ (RU)

**Baseline Profiles** — механизм AOT-компиляции критических путей кода при установке. ART компилирует указанные методы заранее, минуя JIT, что ускоряет холодный старт на 30-40%.

**Без профиля**: Запуск → Интерпретация → JIT по мере использования
**С профилем**: Установка → AOT критического кода → Быстрый запуск

### Реализация

**1. Модуль профилирования**:
```kotlin
// baseline-profile/build.gradle.kts
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

**2. Генератор**:
```kotlin
@Test
fun generate() = rule.collect(packageName = "com.example.app") {
    // ✅ Только критические сценарии
    pressHome()
    startActivityAndWait()
    device.findObject(By.text("Home")).click()
    // ❌ Избегайте редких user flows
}
```

**3. Применение**:
```kotlin
// app/build.gradle.kts
plugins {
    id("androidx.baselineprofile")
}

baselineProfile {
    managedDevices += "pixel6Api33"
}
```

**4. Верификация**:
```kotlin
// ✅ Проверка в production
val status = ProfileVerifier.getCompilationStatusAsync().get()
when (status.profileInstallResultCode) {
    CompilationStatus.RESULT_CODE_COMPILED_WITH_PROFILE -> { /* OK */ }
    CompilationStatus.RESULT_CODE_NO_PROFILE -> { /* Fallback to JIT */ }
}
```

**5. Бенчмаркинг**:
```kotlin
@Test
fun startup() = benchmarkRule.measureRepeated(
    packageName = "com.example.app",
    metrics = listOf(StartupTimingMetric()),
    startupMode = StartupMode.COLD
) {
    pressHome()
    startActivityAndWait()
}
```

### Лучшие Практики

- Покрывайте критические пути (запуск, первый рендер)
- Размер профиля < 200KB
- Тестируйте на реальных устройствах
- Перегенерируйте после рефакторинга
- Автоматизируйте в CI/CD

## Answer (EN)

**Baseline Profiles** instruct Android Runtime to AOT-compile critical code paths at install time, bypassing JIT. This achieves 30-40% faster cold startup.

**Without Profile**: Launch → Interpret → JIT gradually
**With Profile**: Install → AOT critical paths → Fast launch

### Implementation

**1. Profile Generation Module**:
```kotlin
// baseline-profile/build.gradle.kts
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

**2. Generator**:
```kotlin
@Test
fun generate() = rule.collect(packageName = "com.example.app") {
    // ✅ Cover critical flows only
    pressHome()
    startActivityAndWait()
    device.findObject(By.text("Home")).click()
    // ❌ Avoid rare user journeys
}
```

**3. App Configuration**:
```kotlin
// app/build.gradle.kts
plugins {
    id("androidx.baselineprofile")
}

baselineProfile {
    managedDevices += "pixel6Api33"
}
```

**4. Production Verification**:
```kotlin
// ✅ Check profile installation
val status = ProfileVerifier.getCompilationStatusAsync().get()
when (status.profileInstallResultCode) {
    CompilationStatus.RESULT_CODE_COMPILED_WITH_PROFILE -> { /* OK */ }
    CompilationStatus.RESULT_CODE_NO_PROFILE -> { /* Fallback to JIT */ }
}
```

**5. Benchmarking**:
```kotlin
@Test
fun startup() = benchmarkRule.measureRepeated(
    packageName = "com.example.app",
    metrics = listOf(StartupTimingMetric()),
    startupMode = StartupMode.COLD
) {
    pressHome()
    startActivityAndWait()
}
```

### Best Practices

- Cover critical paths (startup, first render)
- Keep profile size < 200KB
- Test on real devices
- Regenerate after refactoring
- Automate in CI/CD

## Follow-ups

- How does profile size correlate with compile time and app size?
- What happens when a profile references methods removed during R8 shrinking?
- Can you combine baseline profiles with R8 full mode optimization?
- How do you validate profile effectiveness across different API levels?
- What strategies exist for profiling modularized apps with dynamic feature modules?

## References

- [[q-android-performance-measurement-tools--android--medium]]
- [[q-app-startup-optimization--android--medium]]
- https://developer.android.com/topic/performance/baselineprofiles

## Related Questions

### Prerequisites (Easier)
- [[q-app-startup-optimization--android--medium]] - Startup optimization fundamentals

### Related (Same Level)
- [[q-android-performance-measurement-tools--android--medium]] - Macrobenchmark and profiling tools

### Advanced (Harder)
- Understanding ART compilation strategies and dex2oat internals
- Analyzing compiler output for profile verification
