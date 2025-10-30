---
id: 20251012-122787
title: Baseline Profiles Android / Базовые профили Android
aliases: ["Baseline Profiles Android", "Базовые профили Android"]
topic: android
subtopics: [performance-startup, gradle, profiling]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related:
  - c-jit-aot-compilation
  - q-android-build-optimization--android--medium
  - q-app-startup-optimization--android--medium
  - q-android-performance-measurement-tools--android--medium
created: 2025-10-15
updated: 2025-10-30
sources: []
tags: [android/performance-startup, android/gradle, android/profiling, performance, aot, difficulty/medium]
date created: Thursday, October 30th 2025, 11:50:58 am
date modified: Thursday, October 30th 2025, 12:43:24 pm
---

# Вопрос (RU)
> Что такое Baseline Profiles в Android и как они работают?

# Question (EN)
> What are Baseline Profiles in Android and how do they work?

---

## Ответ (RU)

### Концепция

Baseline Profiles — это метаданные компиляции, которые сообщают Android Runtime (ART), какие методы и классы критичны для запуска. ART использует эту информацию для предварительной (AOT) компиляции горячих путей при установке, избегая интерпретации и JIT-компиляции во время первых запусков.

**Типичный путь без профиля**:
```
Запуск → Интерпретация байткода → JIT-компиляция горячих методов → Нативный код
  (медленно)                          (на 2-3 запуске)            (быстро)
```

**С Baseline Profile**:
```
Установка → AOT-компиляция критичных методов → Запуск → Нативный код сразу
             (dex2oat применяет профиль)       (быстро)
```

### Реализация

**1. Gradle Setup**:
```kotlin
// ✅ Минимальная конфигурация для включения поддержки профилей
plugins {
    id("androidx.baselineprofile")
}

android {
    defaultConfig {
        // Профили работают с Android 7+, максимальный эффект на Android 9+
        minSdk = 24
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

**3. Формат профиля** (`.txt`):
```
HSPLcom/app/MainActivity;->onCreate(Landroid/os/Bundle;)V
SPLcom/app/ui/FeedScreen;->Content(Landroidx/compose/runtime/Composer;I)V
Lcom/app/data/FeedRepository;

# H=Hot (>90% выполнения), S=Startup, P=Post-startup, L=Class load
```

**4. Верификация в продакшене**:
```kotlin
// ✅ Проверка установки профиля на устройстве
val status = ProfileVerifier.getCompilationStatusAsync().await()
when {
    status.profileInstallResultCode == RESULT_CODE_COMPILED_WITH_PROFILE ->
        Log.i("Profile", "Профиль применён и скомпилирован")
    status.profileInstallResultCode == RESULT_CODE_PROFILE_ENQUEUED_FOR_COMPILATION ->
        Log.w("Profile", "Профиль в очереди на компиляцию")
    else ->
        Log.e("Profile", "Профиль не установлен: ${status.profileInstallResultCode}")
}
```

### Производительность

- **Холодный запуск**: 20-40% быстрее (зависит от покрытия критичных методов)
- **Первая отрисовка UI**: 30-50% быстрее (Compose-приложения получают максимум)
- **Стабильность**: до 60% меньше пропущенных кадров в первых сессиях

### Лучшие Практики

- Профилируйте только **критичные пути** (запуск, первая навигация, ключевые действия)
- Держите размер профиля **<200KB** (большие профили замедляют установку)
- **Регенерируйте** при изменении критичных путей (не каждый релиз)
- **Тестируйте на реальных устройствах** (эмуляторы не показывают реальную производительность)
- **Мониторьте установку** в продакшене через `ProfileVerifier`

## Answer (EN)

### Concept

Baseline Profiles are compilation metadata that tell Android Runtime (ART) which methods and classes are critical for startup. ART uses this information to pre-compile (AOT) hot paths during installation, avoiding interpretation and JIT compilation during initial launches.

**Typical path without profile**:
```
Launch → Interpret bytecode → JIT compile hot methods → Native code
 (slow)                          (on 2nd-3rd run)        (fast)
```

**With Baseline Profile**:
```
Install → AOT compile critical methods → Launch → Native code immediately
           (dex2oat applies profile)      (fast)
```

### Implementation

**1. Gradle Setup**:
```kotlin
// ✅ Minimal configuration to enable profile support
plugins {
    id("androidx.baselineprofile")
}

android {
    defaultConfig {
        // Profiles work on Android 7+, max effect on Android 9+
        minSdk = 24
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

**3. Profile Format** (`.txt`):
```
HSPLcom/app/MainActivity;->onCreate(Landroid/os/Bundle;)V
SPLcom/app/ui/FeedScreen;->Content(Landroidx/compose/runtime/Composer;I)V
Lcom/app/data/FeedRepository;

# H=Hot (>90% execution), S=Startup, P=Post-startup, L=Class load
```

**4. Production Verification**:
```kotlin
// ✅ Check profile installation on device
val status = ProfileVerifier.getCompilationStatusAsync().await()
when {
    status.profileInstallResultCode == RESULT_CODE_COMPILED_WITH_PROFILE ->
        Log.i("Profile", "Profile applied and compiled")
    status.profileInstallResultCode == RESULT_CODE_PROFILE_ENQUEUED_FOR_COMPILATION ->
        Log.w("Profile", "Profile queued for compilation")
    else ->
        Log.e("Profile", "Profile not installed: ${status.profileInstallResultCode}")
}
```

### Performance

- **Cold startup**: 20-40% faster (depends on critical method coverage)
- **First UI render**: 30-50% faster (Compose apps benefit most)
- **Stability**: up to 60% fewer dropped frames in early sessions

### Best Practices

- Profile only **critical paths** (startup, first navigation, key actions)
- Keep profile size **<200KB** (large profiles slow installation)
- **Regenerate** when critical paths change (not every release)
- **Test on real devices** (emulators don't show real performance)
- **Monitor installation** in production via `ProfileVerifier`

## Follow-ups

- How do you measure baseline profile effectiveness in production (compile status, startup metrics)?
- When should you regenerate baseline profiles (major refactors, new critical flows)?
- How do baseline profiles interact with R8/ProGuard obfuscation?
- What's the tradeoff between profile size and APK/AAB size increase?
- How do you handle baseline profiles in multi-module Gradle projects?

## References

- [[c-jit-aot-compilation]] — JIT vs AOT compilation fundamentals
- [[c-android-runtime-art]] — Android Runtime architecture and dex2oat
- https://developer.android.com/topic/performance/baselineprofiles — Official Android baseline profiles guide

## Related Questions

### Prerequisites (Easier)
- [[q-app-startup-optimization--android--medium]] — General startup optimization techniques
- [[q-android-build-optimization--android--medium]] — Gradle build configuration for performance

### Related (Same Level)
- [[q-android-performance-measurement-tools--android--medium]] — Profilers and measurement tools
- [[q-r8-proguard-optimization--android--medium]] — Code shrinking and optimization
- [[q-app-startup-library--android--medium]] — Androidx Startup library for initialization

### Advanced (Harder)
- [[q-android-runtime-art--android--hard]] — Deep dive into ART internals
- [[q-dex-optimization-strategies--android--hard]] — Advanced DEX optimization techniques
