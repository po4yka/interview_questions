---
id: 20251012-122787
title: Baseline Profiles Android / Baseline Profiles Android
aliases: [Baseline Profiles Android, Baseline Profiles Android]
topic: android
subtopics: [performance-startup, build-optimization]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: reviewed
moc: moc-android
related: [q-app-startup-optimization--performance--medium, q-app-size-optimization--performance--medium, q-android-build-optimization--android--medium]
created: 2025-10-15
updated: 2025-10-15
tags: [android/performance-startup, android/build-optimization, baseline-profiles, aot, optimization, app-startup, difficulty/medium]
---
# Question (EN)
> What are Baseline Profiles in Android? How do they improve app performance and how do you generate them?

# Вопрос (RU)
> Что такое Baseline Profiles в Android? Как они улучшают производительность приложения и как их генерировать?

---

## Answer (EN)

### What Are Baseline Profiles

**Theory**: Baseline Profiles tell Android Runtime (ART) which code paths to pre-compile (AOT) at install time, reducing startup time and jank during critical user journeys.

**How It Works**:
- Traditional: App start → Interpret bytecode → Profile → JIT compile → Fast execution
- With Profile: App install → AOT compile profiled code → App start → Fast execution immediately

### Performance Impact

**Typical Improvements**:
- Cold startup: 20-40% faster
- Warm startup: 15-30% faster
- First interaction: 30-50% faster
- Jank reduction: 40-60% fewer dropped frames

### Implementation

**Setup (build.gradle.kts)**:
```kotlin
// Theory: Enable baseline profile plugin for AOT compilation
plugins {
    id("androidx.baselineprofile")
}

android {
    buildTypes {
        create("benchmark") {
            initWith(getByName("release"))
            matchingFallbacks += listOf("release")
        }
    }
}
```

**Profile Generation**:
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
        // Critical user journey
        pressHome()
        startActivityAndWait()
        device.findObject(By.text("Home")).click()
        device.findObject(By.text("Profile")).click()
    }
}
```

**Profile Format**:
```
# Generated baseline-prof.txt
HSPLcom/example/app/MainActivity;->onCreate(Landroid/os/Bundle;)V
HSPLcom/example/app/viewmodel/HomeViewModel;-><init>()V
Lcom/example/app/repository/ArticleRepository;->getArticles()Ljava/util/List;

# Flags: H=Hot, S=Startup, P=Post-startup, L=Class reference
```

**Verification**:
```kotlin
// Theory: Check if profile was installed and compiled
class ProfileVerifier {
    fun checkProfileInstallation(context: Context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            val status = ProfileVerifier.getCompilationStatusAsync().get()
            Log.d("Profile", "Compiled with profile: ${status.isCompiledWithProfile}")
        }
    }
}
```

### Requirements and Best Practices

**Requirements**:
- Android 9+ (API 28) for full benefits
- Android 7+ (API 24) minimum support
- Release build with R8/ProGuard enabled

**Best Practices**:
- Profile only critical user journeys
- Keep profile size under 200KB
- Regenerate with major releases
- Test on real devices, not emulators
- Verify installation in production
- Combine with other startup optimizations

## Ответ (RU)

### Что такое Baseline Profiles

**Теория**: Baseline Profiles сообщают Android Runtime (ART), какой код предварительно скомпилировать (AOT) при установке, сокращая время запуска и jank во время критических пользовательских сценариев.

**Как работает**:
- Традиционно: Запуск приложения → Интерпретация байткода → Профилирование → JIT компиляция → Быстрое выполнение
- С профилем: Установка приложения → AOT компиляция профилированного кода → Запуск приложения → Немедленное быстрое выполнение

### Влияние на производительность

**Типичные улучшения**:
- Холодный запуск: на 20-40% быстрее
- Тёплый запуск: на 15-30% быстрее
- Первое взаимодействие: на 30-50% быстрее
- Снижение jank: на 40-60% меньше пропущенных кадров

### Реализация

**Настройка (build.gradle.kts)**:
```kotlin
// Теория: Включить плагин baseline profile для AOT компиляции
plugins {
    id("androidx.baselineprofile")
}

android {
    buildTypes {
        create("benchmark") {
            initWith(getByName("release"))
            matchingFallbacks += listOf("release")
        }
    }
}
```

**Генерация профиля**:
```kotlin
// Теория: Тестировать критические пользовательские сценарии для генерации профиля
@RunWith(AndroidJUnit4::class)
class BaselineProfileGenerator {

    @get:Rule
    val baselineProfileRule = BaselineProfileRule()

    @Test
    fun generate() = baselineProfileRule.collect(
        packageName = "com.example.app"
    ) {
        // Критический пользовательский сценарий
        pressHome()
        startActivityAndWait()
        device.findObject(By.text("Home")).click()
        device.findObject(By.text("Profile")).click()
    }
}
```

**Формат профиля**:
```
# Сгенерированный baseline-prof.txt
HSPLcom/example/app/MainActivity;->onCreate(Landroid/os/Bundle;)V
HSPLcom/example/app/viewmodel/HomeViewModel;-><init>()V
Lcom/example/app/repository/ArticleRepository;->getArticles()Ljava/util/List;

# Флаги: H=Hot, S=Startup, P=Post-startup, L=Ссылка на класс
```

**Верификация**:
```kotlin
// Теория: Проверить установлен ли профиль и скомпилирован ли
class ProfileVerifier {
    fun checkProfileInstallation(context: Context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            val status = ProfileVerifier.getCompilationStatusAsync().get()
            Log.d("Profile", "Скомпилирован с профилем: ${status.isCompiledWithProfile}")
        }
    }
}
```

### Требования и лучшие практики

**Требования**:
- Android 9+ (API 28) для полной поддержки
- Android 7+ (API 24) минимальная поддержка
- Release сборка с включенным R8/ProGuard

**Лучшие практики**:
- Профилировать только критические пользовательские сценарии
- Размер профиля менее 200KB
- Регенерировать при мажорных релизах
- Тестировать на реальных устройствах, не эмуляторах
- Верифицировать установку в production
- Комбинировать с другими оптимизациями запуска

---

## Follow-ups

- How do you measure the impact of baseline profiles?
- What are the differences between baseline profiles and startup libraries?
- How do you handle profile updates in production?

## References

- https://developer.android.com/topic/performance/baselineprofiles

## Related Questions

### Prerequisites (Easier)
- [[q-android-performance-measurement-tools--android--medium]]
- [[q-android-build-optimization--android--medium]]
- [[q-app-startup-library--android--medium]]

### Related (Same Level)
- [[q-app-startup-optimization--performance--medium]]
- [[q-app-size-optimization--performance--medium]]
- [[q-jit-vs-aot-compilation--android--medium]]

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]]
- [[q-android-runtime-art--android--medium]]
- [[q-android-build-optimization--android--medium]]
