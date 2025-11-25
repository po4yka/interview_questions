---
id: android-037
title: Baseline Profiles Optimization / Оптимизация с Baseline Profiles
aliases: [Baseline Profiles Optimization, Оптимизация с Baseline Profiles]
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
status: draft
moc: moc-android
related:
  - c-modularization
  - c-performance
  - c-performance-optimization
  - q-baseline-profiles-android--android--medium
  - q-canvas-drawing-optimization--android--hard
  - q-dagger-build-time-optimization--android--medium
sources: []
created: 2024-10-11
updated: 2025-11-11
tags: [android/gradle, android/performance-startup, android/profiling, difficulty/medium]
date created: Saturday, November 1st 2025, 1:04:48 pm
date modified: Tuesday, November 25th 2025, 8:54:02 pm
---

# Вопрос (RU)
> Как оптимизировать Android-приложение с помощью Baseline Profiles?

# Question (EN)
> How to optimize an Android app using Baseline Profiles?

---

## Ответ (RU)

**Baseline Profiles** — механизм, позволяющий заранее (AOT) скомпилировать критические пути кода при установке приложения на устройстве, используя сведения о том, какие методы реально важны для старта и ключевых сценариев. ART предварительно компилирует указанные методы и классы, уменьшая долю интерпретации/JIT на первых запусках. Это обычно даёт заметное ускорение холодного старта (часто десятки процентов) и снижает джанк при первом рендеринге и ранних взаимодействиях.

**Принцип работы**:
- **Без профиля**: Запуск → Интерпретация байткода → Постепенная JIT-компиляция по мере использования
- **С профилем**: Установка → AOT-компиляция критических путей из baseline-профиля → Быстрое исполнение без ожидания JIT

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
    // ✅ Критический сценарий: запуск + первый рендер + навигация к основному экрану
    pressHome()
    startActivityAndWait()
    device.findObject(By.res("home_screen")).click()

    // ❌ Не включайте редкие или тяжёлые для установки сценарии
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
val status = ProfileVerifier.getCompilationStatusAsync().get() // ⚠️ вызывайте не с main thread
when (status.profileInstallResultCode) {
    RESULT_CODE_COMPILED_WITH_PROFILE -> logSuccess()
    RESULT_CODE_NO_PROFILE -> logFallbackToJit()
}
```

### Критерии Качества

- **Размер профиля**: по возможности держать компактным (ориентир < ~200KB), чтобы не замедлять установку и не перегружать компиляцию.
- **Покрытие**: запуск → первый рендер → основной пользовательский сценарий (часто используемые экраны/действия).
- **Регенерация**: после рефакторинга, изменения навигации или горячих путей.
- **CI/CD**: автоматическая генерация и проверка актуальности и размера профиля.

## Answer (EN)

**Baseline Profiles** enable ahead-of-time (AOT) compilation of critical code paths at app install time based on a predefined profile of important methods and classes. ART pre-compiles those targets to reduce interpretation/JIT work on first runs. This typically results in significantly faster cold startup (often tens of percent improvement) and less jank during first render and early user interactions.

**How it works**:
- **Without Profile**: Launch → Bytecode interpretation → Gradual JIT compilation as code is executed
- **With Profile**: Install → AOT-compile critical paths from the baseline profile → Faster execution without waiting for JIT

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
    // ✅ Critical scenario: startup + first render + navigate to main screen
    pressHome()
    startActivityAndWait()
    device.findObject(By.res("home_screen")).click()

    // ❌ Don't include rare or installation-costly flows
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
val status = ProfileVerifier.getCompilationStatusAsync().get() // ⚠️ do not call on main thread
when (status.profileInstallResultCode) {
    RESULT_CODE_COMPILED_WITH_PROFILE -> logSuccess()
    RESULT_CODE_NO_PROFILE -> logFallbackToJit()
}
```

### Quality Criteria

- **Profile size**: keep it as small as reasonably possible (a practical target is < ~200KB) to avoid slowing installation and compilation.
- **Coverage**: Startup → First render → Primary, frequently used user flows.
- **Regeneration**: After refactoring, navigation changes, or hot path modifications.
- **CI/CD**: Automated generation and validation of profile size and freshness.

## Дополнительные Вопросы (RU)

- Как размер профиля влияет на время компиляции и увеличение размера приложения?
- Что происходит, если профиль ссылается на методы, удалённые при шринкинге R8?
- Можно ли комбинировать baseline-профили с полной оптимизацией R8 (full mode)?
- Как проверять эффективность профиля на разных API уровнях и классах устройств?
- Какие есть стратегии для профилирования модульных приложений с dynamic feature модулями?

## Follow-ups

- How does profile size correlate with compile time and app size increase?
- What happens when a profile references methods removed during R8 shrinking?
- Can you combine baseline profiles with R8 full mode optimization?
- How do you validate profile effectiveness across different API levels and device tiers?
- What strategies exist for profiling modularized apps with dynamic feature modules?

## Ссылки (RU)

- [[q-android-performance-measurement-tools--android--medium]]
- [[q-app-startup-optimization--android--medium]]
- https://developer.android.com/topic/performance/baselineprofiles
- https://developer.android.com/studio/profile/baselineprofiles

## References

- [[q-android-performance-measurement-tools--android--medium]]
- [[q-app-startup-optimization--android--medium]]
- https://developer.android.com/topic/performance/baselineprofiles
- https://developer.android.com/studio/profile/baselineprofiles

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-performance-optimization]]
- [[c-performance]]
- [[c-modularization]]

### Предпосылки (Проще)

- [[q-app-startup-optimization--android--medium]] - Базовая оптимизация старта до AOT-компиляции

### Связанные (Тот Же уровень)

- [[q-android-performance-measurement-tools--android--medium]] - Macrobenchmark для проверки профилей
- Взаимодействие R8 с baseline-профилями

### Продвинутое (Сложнее)

- Внутреннее устройство ART: dex2oat, JIT, AOT трейд-оффы
- Генерация профилей для мультимодульных приложений

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
