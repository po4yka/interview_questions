---
id: 20251012-122787
title: Baseline Profiles Android / Baseline Profiles Android
aliases: [Baseline Profiles Android, Baseline Profiles, Базовые профили Android]
topic: android
subtopics: [gradle, performance-startup]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related:
  - q-android-build-optimization--android--medium
  - q-app-size-optimization--android--medium
  - q-app-startup-optimization--android--medium
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [android/gradle, android/performance-startup, difficulty/medium]
---

# Вопрос (RU)
> Что такое Baseline Profiles в Android и как они работают?

# Question (EN)
> What are Baseline Profiles in Android and how do they work?

---

## Ответ (RU)

### Что Такое Baseline Profiles

Baseline Profiles сообщают Android Runtime (ART), какие пути кода нужно предварительно скомпилировать (AOT) во время установки, сокращая время запуска и устраняя рывки во время критических пользовательских сценариев.

**Компиляция без профиля**:
Запуск → Интерпретация → Профилирование → JIT компиляция → Быстрое выполнение

**Компиляция с профилем**:
Установка → AOT компиляция профилированного кода → Запуск → Сразу быстрое выполнение

### Влияние На Производительность

- Холодный запуск: на 20-40% быстрее
- Тёплый запуск: на 15-30% быстрее
- Первое взаимодействие: на 30-50% быстрее
- Уменьшение рывков: на 40-60% меньше пропущенных кадров

### Реализация

**Настройка плагина** (см. код в английской секции)

**Генерация профиля**:
Тестируйте критические пользовательские сценарии для создания профиля оптимизации.

**Формат профиля**:
```
HSPLcom/example/app/MainActivity;->onCreate(Landroid/os/Bundle;)V
HSPLcom/example/app/viewmodel/HomeViewModel;-><init>()V
Lcom/example/app/repository/ArticleRepository;->getArticles()Ljava/util/List;

# Флаги: H=Hot, S=Startup, P=Post-startup, L=Class reference
```

### Лучшие Практики

- Профилировать только критические пользовательские сценарии
- Держать размер профиля меньше 200KB
- Перегенерировать при major релизах
- Тестировать на реальных устройствах, не эмуляторах
- Проверять установку в продакшене
- Комбинировать с другими оптимизациями запуска

## Answer (EN)

### What Are Baseline Profiles

Baseline Profiles tell Android Runtime (ART) which code paths to pre-compile (AOT) at install time, reducing startup time and jank during critical user journeys.

**Without Profile**:
App start → Interpret bytecode → Profile → JIT compile → Fast execution

**With Profile**:
App install → AOT compile profiled code → App start → Fast execution immediately

### Performance Impact

- Cold startup: 20-40% faster
- Warm startup: 15-30% faster
- First interaction: 30-50% faster
- Jank reduction: 40-60% fewer dropped frames

### Implementation

**Setup**:
```kotlin
// ✅ Enable baseline profile plugin for AOT compilation
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
// ✅ Test critical user journeys to generate profile
@RunWith(AndroidJUnit4::class)
class BaselineProfileGenerator {
    @get:Rule
    val baselineProfileRule = BaselineProfileRule()

    @Test
    fun generate() = baselineProfileRule.collect(
        packageName = "com.example.app"
    ) {
        pressHome()
        startActivityAndWait()
        device.findObject(By.text("Home")).click()
        device.findObject(By.text("Profile")).click()
    }
}
```

**Profile Format**:
```
HSPLcom/example/app/MainActivity;->onCreate(Landroid/os/Bundle;)V
HSPLcom/example/app/viewmodel/HomeViewModel;-><init>()V
Lcom/example/app/repository/ArticleRepository;->getArticles()Ljava/util/List;

# Flags: H=Hot, S=Startup, P=Post-startup, L=Class reference
```

**Verification**:
```kotlin
// ✅ Check if profile was installed and compiled
fun checkProfileInstallation(context: Context) {
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
        val status = ProfileVerifier.getCompilationStatusAsync().get()
        Log.d("Profile", "Compiled: ${status.isCompiledWithProfile}")
    }
}
```

### Best Practices

**Requirements**:
- Android 9+ (API 28) for full benefits
- Android 7+ (API 24) minimum support
- Release build with R8/ProGuard enabled

**Guidelines**:
- Profile only critical user journeys
- Keep profile size under 200KB
- Regenerate with major releases
- Test on real devices, not emulators
- Verify installation in production
- Combine with other startup optimizations

## Follow-ups

- How do you measure the impact of baseline profiles in production?
- What are the differences between baseline profiles and the startup library?
- How do you handle profile updates when code changes significantly?
- Can baseline profiles negatively impact app size or build time?
- How do you profile multi-module applications?

## References

- [[c-jit-aot-compilation]]
- https://developer.android.com/topic/performance/baselineprofiles

## Related Questions

### Prerequisites (Easier)
- [[q-app-startup-library--android--medium]]
- [[q-android-build-optimization--android--medium]]

### Related (Same Level)
- [[q-app-startup-optimization--android--medium]]
- [[q-jit-vs-aot-compilation--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]]
- [[q-android-runtime-art--android--medium]]
