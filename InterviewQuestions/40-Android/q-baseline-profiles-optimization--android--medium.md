---
id: android-037
title: Baseline Profiles Optimization / Оптимизация с Baseline Profiles
aliases:
- Baseline Profiles Optimization
- Оптимизация с Baseline Profiles
topic: android
subtopics:
- gradle
- performance-startup
- profiling
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- c-performance-optimization
- c-performance
- c-modularization
sources: []
created: 2025-10-11
updated: 2025-10-30
tags:
- android/gradle
- android/performance-startup
- android/profiling
- difficulty/medium
date created: Thursday, October 30th 2025, 11:51:36 am
date modified: Sunday, November 2nd 2025, 1:02:35 pm
---

# Вопрос (RU)
> Как оптимизировать Android-приложение с помощью Baseline Profiles?

# Question (EN)
> How to optimize an Android app using Baseline Profiles?

---

## Ответ (RU)

**Baseline Profiles** — механизм AOT-компиляции критических путей кода при установке приложения. ART предварительно компилирует указанные методы и классы, минуя JIT-интерпретацию, что ускоряет холодный старт на 30-40% и снижает джанк при первом рендеринге.

**Принцип работы**:
- **Без профиля**: Запуск → Интерпретация байткода → Постепенная JIT-компиляция
- **С профилем**: Установка → AOT-компиляция критических путей → Мгновенный нативный код

### Структура Реализации

**1. Модуль генерации профиля**:
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

**2. Тест генерации**:
```kotlin
@Test
fun generateProfile() = baselineRule.collect(
    packageName = "com.example.app"
) {
    // ✅ Критический сценарий: запуск + первый рендер
    pressHome()
    startActivityAndWait()
    device.findObject(By.res("home_screen")).click()

    // ❌ Не включайте редкие сценарии
}
```

**3. Конфигурация приложения**:
```kotlin
// app/build.gradle.kts
plugins {
    id("androidx.baselineprofile")
}

baselineProfile {
    managedDevices += "pixel6Api33"
}
```

**4. Проверка в production**:
```kotlin
val status = ProfileVerifier.getCompilationStatusAsync().get()
when (status.profileInstallResultCode) {
    RESULT_CODE_COMPILED_WITH_PROFILE -> logSuccess()
    RESULT_CODE_NO_PROFILE -> logFallbackToJit()
}
```

### Критерии Качества

- **Размер профиля** < 200KB (больше замедляет установку)
- **Покрытие**: Запуск → Первый рендер → Основной user flow
- **Регенерация**: После рефакторинга или изменения горячих путей
- **CI/CD**: Автоматическая проверка размера и актуальности профиля

## Answer (EN)

**Baseline Profiles** enable AOT-compilation of critical code paths at install time. ART pre-compiles specified methods and classes, bypassing JIT interpretation, achieving 30-40% faster cold startup and reduced jank during first render.

**How it works**:
- **Without Profile**: Launch → Bytecode interpretation → Gradual JIT compilation
- **With Profile**: Install → AOT-compile critical paths → Instant native code

### Implementation Structure

**1. Profile generation module**:
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

**2. Generation test**:
```kotlin
@Test
fun generateProfile() = baselineRule.collect(
    packageName = "com.example.app"
) {
    // ✅ Critical scenario: startup + first render
    pressHome()
    startActivityAndWait()
    device.findObject(By.res("home_screen")).click()

    // ❌ Don't include rare user journeys
}
```

**3. App configuration**:
```kotlin
// app/build.gradle.kts
plugins {
    id("androidx.baselineprofile")
}

baselineProfile {
    managedDevices += "pixel6Api33"
}
```

**4. Production verification**:
```kotlin
val status = ProfileVerifier.getCompilationStatusAsync().get()
when (status.profileInstallResultCode) {
    RESULT_CODE_COMPILED_WITH_PROFILE -> logSuccess()
    RESULT_CODE_NO_PROFILE -> logFallbackToJit()
}
```

### Quality Criteria

- **Profile size** < 200KB (larger slows installation)
- **Coverage**: Startup → First render → Primary user flow
- **Regeneration**: After refactoring or hot path changes
- **CI/CD**: Automated size and freshness validation

## Follow-ups

- How does profile size correlate with compile time and app size increase?
- What happens when a profile references methods removed during R8 shrinking?
- Can you combine baseline profiles with R8 full mode optimization?
- How do you validate profile effectiveness across different API levels and device tiers?
- What strategies exist for profiling modularized apps with dynamic feature modules?

## References

- [[q-android-performance-measurement-tools--android--medium]]
- [[q-app-startup-optimization--android--medium]]
- https://developer.android.com/topic/performance/baselineprofiles
- https://developer.android.com/studio/profile/baselineprofiles

## Related Questions

### Prerequisites / Concepts

- [[c-performance-optimization]]
- [[c-performance]]
- [[c-modularization]]


### Prerequisites (Easier)
- [[q-app-startup-optimization--android--medium]] - Startup optimization fundamentals before AOT compilation

### Related (Same Level)
- [[q-android-performance-measurement-tools--android--medium]] - Macrobenchmark for profile validation
 - R8 interaction with baseline profiles

### Advanced (Harder)
 - ART internals: dex2oat, JIT, AOT trade-offs
 - Profile generation for multi-module apps
