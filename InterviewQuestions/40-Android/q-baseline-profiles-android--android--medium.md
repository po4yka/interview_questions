---
id: android-310
title: Baseline Profiles Android / Базовые профили Android
aliases:
- Baseline Profiles Android
- Базовые профили Android
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
- c-android-basics
- q-android-lint-tool--android--medium
- q-android-performance-measurement-tools--android--medium
- q-baseline-profiles-optimization--android--medium
- q-parsing-optimization-android--android--medium
created: 2025-10-15
updated: 2025-11-10
sources: []
tags:
- android/gradle
- android/performance-startup
- android/profiling
- difficulty/medium
anki_cards:
- slug: android-310-0-en
  language: en
  anki_id: 1768364697049
  synced_at: '2026-01-23T16:45:06.104543'
- slug: android-310-0-ru
  language: ru
  anki_id: 1768364697074
  synced_at: '2026-01-23T16:45:06.105520'
---
# Вопрос (RU)
> Что такое Baseline Profiles в Android и как они работают?

# Question (EN)
> What are Baseline Profiles in Android and how do they work?

---

## Ответ (RU)

### Концепция

Baseline Profiles — это метаданные компиляции, которые сообщают Android Runtime (ART), какие методы и классы критичны для запуска и ключевых сценариев. ART использует эту информацию для более агрессивной предварительной (`AOT`) компиляции соответствующих путей (например, при установке через Play или во время фоновых оптимизаций), уменьшая долю интерпретации и `JIT`-компиляции во время первых запусков.

**Типичный путь без профиля**:
```text
Запуск → Интерпретация байткода → JIT-компиляция горячих методов → Нативный код
  (медленно)                          (на 2-3 запуске)            (быстро)
```

**С Baseline Profile**:
```text
Установка/оптимизация → AOT-компиляция критичных методов → Запуск → Нативный код быстрее
        (dex2oat применяет профиль)                         (ускоренный старт)
```

### Реализация

**1. Gradle Setup**:
```kotlin
// ✅ Упрощённый пример включения поддержки baseline profiles
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("androidx.baselineprofile") // применяется в модуле/конфигурации для генерации профилей
}

android {
    defaultConfig {
        // Библиотека baselineprofile поддерживает minSdk >= 21,
        // но максимальный эффект даёт на современных ART-рантаймах (особенно API 28+)
        minSdk = 21
    }
}
```

**2. Генерация профиля**:
```kotlin
// ✅ Инструментированный тест генерирует профиль
@RunWith(AndroidJUnit4::class)
class BaselineProfileGenerator {
    @get:Rule val rule = BaselineProfileRule()

    @Test
    fun generate() = rule.collect(
        packageName = "com.app",
        profileBlock = {
            pressHome()
            startActivityAndWait()
            // Критичный путь: открытие главного экрана
            device.wait(Until.hasObject(By.text("Feed")), 5000)
            device.findObject(By.text("Feed")).click()
            device.waitForIdle()
        }
    )
}
```

**3. Формат профиля** (`.txt`, упрощённый пример):
```text
HSPLcom/app/MainActivity;->onCreate(Landroid/os/Bundle;)V
SPLcom/app/ui/FeedScreen;->Content(Landroidx/compose/runtime/Composer;I)V
Lcom/app/data/FeedRepository;

# H=Hot, S=Startup, P=Post-startup, L=Class load (маркировка, используемая ART для приоритизации)
```

**4. Верификация в продакшене**:
```kotlin
// ✅ Проверка установки профиля на устройстве
val status = ProfileVerifier.getCompilationStatusAsync().await()
when (status.profileInstallResultCode) {
    ProfileVerifier.RESULT_CODE_COMPILED_WITH_PROFILE ->
        Log.i("Profile", "Профиль применён и скомпилирован")
    ProfileVerifier.RESULT_CODE_PROFILE_ENQUEUED_FOR_COMPILATION ->
        Log.w("Profile", "Профиль поставлен в очередь на компиляцию")
    else ->
        Log.e("Profile", "Профиль не установлен: ${status.profileInstallResultCode}")
}
```

### Производительность

(Фактический выигрыш зависит от устройства, версии Android и покрытия профилем; значения ниже иллюстративны, на основе официальных и практических измерений.) Типично наблюдаются диапазоны "до":
- **Холодный запуск**: до ~20–40% быстрее
- **Первая отрисовка UI**: до ~30–50% быстрее (Compose-приложения часто выигрывают больше)
- **Стабильность**: заметно меньше пропущенных кадров в первых сессиях

### Лучшие Практики

- Профилируйте только **критичные пути** (запуск, первая навигация, ключевые действия)
- Избегайте чрезмерно больших профилей (слишком крупные профили могут замедлять установку и оптимизацию)
- **Регенерируйте профили** при изменении критичных путей (особенно после крупных рефакторингов)
- **Тестируйте на реальных устройствах** (эмуляторы не отражают реальные условия исполнения и поведения `AOT`/`JIT`)
- **Мониторьте установку и эффект** в продакшене через `ProfileVerifier`, метрики старта и метрики кадров

## Answer (EN)

### Concept

Baseline Profiles are compilation metadata that tell the Android Runtime (ART) which methods and classes are critical for startup and key flows. ART uses this information to more aggressively precompile (`AOT`) those paths (e.g., at install time via Play or during background optimizations), reducing interpretation and `JIT` work during the first launches.

**Typical path without profile**:
```text
Launch → Interpret bytecode → JIT compile hot methods → Native code
 (slow)                          (on 2nd-3rd run)        (fast)
```

**With Baseline Profile**:
```text
Install/optimization → AOT compile critical methods → Launch → Faster native execution
       (dex2oat applies profile)                        (faster startup)
```

### Implementation

**1. Gradle Setup**:
```kotlin
// ✅ Simplified example to enable baseline profile support
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("androidx.baselineprofile") // applied in the module/configuration responsible for profile generation
}

android {
    defaultConfig {
        // The baselineprofile library supports minSdk >= 21,
        // but the most significant benefits appear on modern ART runtimes (especially API 28+)
        minSdk = 21
    }
}
```

**2. Profile Generation**:
```kotlin
// ✅ Instrumented test generates profile
@RunWith(AndroidJUnit4::class)
class BaselineProfileGenerator {
    @get:Rule val rule = BaselineProfileRule()

    @Test
    fun generate() = rule.collect(
        packageName = "com.app",
        profileBlock = {
            pressHome()
            startActivityAndWait()
            // Critical path: opening main screen
            device.wait(Until.hasObject(By.text("Feed")), 5000)
            device.findObject(By.text("Feed")).click()
            device.waitForIdle()
        }
    )
}
```

**3. Profile Format** (`.txt`, simplified example):
```text
HSPLcom/app/MainActivity;->onCreate(Landroid/os/Bundle;)V
SPLcom/app/ui/FeedScreen;->Content(Landroidx/compose/runtime/Composer;I)V
Lcom/app/data/FeedRepository;

# H=Hot, S=Startup, P=Post-startup, L=Class load (hints used by ART for prioritization)
```

**4. Production Verification**:
```kotlin
// ✅ Check profile installation on device
val status = ProfileVerifier.getCompilationStatusAsync().await()
when (status.profileInstallResultCode) {
    ProfileVerifier.RESULT_CODE_COMPILED_WITH_PROFILE ->
        Log.i("Profile", "Profile applied and compiled")
    ProfileVerifier.RESULT_CODE_PROFILE_ENQUEUED_FOR_COMPILATION ->
        Log.w("Profile", "Profile queued for compilation")
    else ->
        Log.e("Profile", "Profile not installed: ${status.profileInstallResultCode}")
}
```

### Performance

(Actual gains depend on device, Android version, and profile coverage; values below are illustrative "up to" ranges based on official and practical benchmarks.) Commonly reported:
- **Cold startup**: up to ~20–40% faster
- **First UI render**: up to ~30–50% faster (Compose apps often benefit more)
- **Stability**: noticeably fewer dropped frames during early sessions

### Best Practices

- Profile only **critical paths** (startup, first navigation, key actions)
- Avoid excessively large profiles (oversized profiles can slow installation/optimizations)
- **Regenerate** when critical paths change significantly (e.g., major refactors)
- **Test on real devices** (emulators do not accurately reflect real runtime and `AOT`/`JIT` behavior)
- **Monitor installation and impact** in production via `ProfileVerifier`, startup metrics, and frame metrics

## Дополнительные Вопросы (RU)

- Как измерять эффективность baseline profiles в продакшене (статус компиляции, метрики старта)?
- Когда следует регенерировать baseline profiles (крупные рефакторинги, новые критичные сценарии)?
- Как baseline profiles взаимодействуют с обфускацией `R8`/ProGuard?
- В чем компромисс между размером профиля и увеличением размера `APK/AAB`?
- Как работать с baseline profiles в мульти-модульных Gradle-проектах?

## Follow-ups

- How do you measure baseline profile effectiveness in production (compile status, startup metrics)?
- When should you regenerate baseline profiles (major refactors, new critical flows)?
- How do baseline profiles interact with R8/ProGuard obfuscation?
- What's the tradeoff between profile size and APK/AAB size increase?
- How do you handle baseline profiles in multi-module Gradle projects?

## Ссылки (RU)

- https://developer.android.com/topic/performance/baselineprofiles — Официальное руководство по baseline profiles
- [[c-android-basics]] — Базовые концепции Android, контекст для оптимизаций

## References

- https://developer.android.com/topic/performance/baselineprofiles — Official Android baseline profiles guide
- [[c-android-basics]] — Core Android concepts relevant for performance optimizations

## Связанные Вопросы (RU)

### Предпосылки / Концепции

### Предпосылки (проще)

- [[q-app-startup-optimization--android--medium]] — Общие техники оптимизации старта
- [[q-android-build-optimization--android--medium]] — Оптимизация Gradle-сборки для производительности

### Связанные (тот Же уровень)

- [[q-android-performance-measurement-tools--android--medium]] — Профайлеры и инструменты измерения

### Продвинутые (сложнее)

- [[q-app-startup-library--android--medium]] — Библиотека Androidx Startup для инициализации

## Related Questions

### Prerequisites / Concepts

### Prerequisites (Easier)

- [[q-app-startup-optimization--android--medium]] — General startup optimization techniques
- [[q-android-build-optimization--android--medium]] — Gradle build configuration for performance

### Related (Same Level)

- [[q-android-performance-measurement-tools--android--medium]] — Profilers and measurement tools

### Advanced (Harder)

- [[q-app-startup-library--android--medium]] — Androidx Startup library for initialization
