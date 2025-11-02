---
id: android-185
title: "Splash Screen API (Android 12+) / API Splash Screen (Android 12+)"
aliases: ["API Splash Screen", "Splash Screen API"]
topic: android
subtopics: [app-startup, ui-animation, ui-views]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: []
created: 2025-10-15
updated: 2025-10-29
tags: [android/app-startup, android/ui-animation, android/ui-views, android12, difficulty/medium, splash-screen]
sources: [https://github.com/Kirchhoff-/Android-Interview-Questions]
date created: Saturday, November 1st 2025, 1:24:29 pm
date modified: Saturday, November 1st 2025, 5:43:32 pm
---

# Вопрос (RU)

Что вы знаете об API Splash Screen в Android 12+?

# Question (EN)

What do you know about the Splash Screen API in Android 12+?

## Ответ (RU)

**Splash Screen** — первый экран, отображаемый при запуске приложения. С Android 12 система автоматически применяет системный splash screen при холодном и тёплом старте.

### Когда Отображается

- **Холодный старт**: процесс приложения не запущен
- **Тёплый старт**: процесс запущен, но Activity не создана
- **Не отображается** при горячем старте (Activity уже в памяти)

### Ключевые Изменения В Android 12

Система автоматически создаёт splash screen из:
- Иконки запуска приложения
- `windowBackground` темы (если однотонный)

### Рекомендуемый Подход: Compat Library

Используйте **androidx.core:core-splashscreen** для единообразия на всех версиях Android.

**Пример интеграции**:

```kotlin
// ✅ Правильный порядок вызовов
class MainActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        installSplashScreen()  // До super.onCreate()
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}
```

```xml
<!-- ✅ Минимальная тема splash screen -->
<style name="Theme.App.Starting" parent="Theme.SplashScreen">
    <item name="windowSplashScreenBackground">@color/primary</item>
    <item name="windowSplashScreenAnimatedIcon">@drawable/ic_launcher</item>
    <item name="postSplashScreenTheme">@style/Theme.App</item>
</style>
```

```xml
<!-- AndroidManifest.xml -->
<activity
    android:name=".MainActivity"
    android:theme="@style/Theme.App.Starting">  <!-- ✅ Используем splash тему -->
```

### Миграция Существующих Splash Screen Activity

**Вариант 1: Routing Activity** — используйте `setKeepOnScreenCondition`:

```kotlin
// ✅ Сохраняем splash screen до завершения роутинга
class RoutingActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        installSplashScreen().setKeepOnScreenCondition { true }
        super.onCreate(savedInstanceState)

        // Логика роутинга
        navigateToDestination()
        finish()
    }
}
```

**Вариант 2: Удалить custom Activity** (рекомендуется):
- Используйте ленивую инициализацию компонентов
- Показывайте placeholder UI во время загрузки данных
- Применяйте кэширование для быстрого отображения контента

## Answer (EN)

**Splash Screen** is the first screen displayed when launching an app. Starting with Android 12, the system automatically applies a system splash screen on cold and warm starts.

### When It Shows

- **Cold start**: app process isn't running
- **Warm start**: process running but Activity not created
- **No display** on hot start (Activity already in memory)

### Key Changes in Android 12

The system automatically constructs splash screen from:
- App launcher icon
- Theme's `windowBackground` (if single color)

### Recommended Approach: Compat Library

Use **androidx.core:core-splashscreen** for consistency across all Android versions.

**Integration example**:

```kotlin
// ✅ Correct call order
class MainActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        installSplashScreen()  // Before super.onCreate()
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}
```

```xml
<!-- ✅ Minimal splash screen theme -->
<style name="Theme.App.Starting" parent="Theme.SplashScreen">
    <item name="windowSplashScreenBackground">@color/primary</item>
    <item name="windowSplashScreenAnimatedIcon">@drawable/ic_launcher</item>
    <item name="postSplashScreenTheme">@style/Theme.App</item>
</style>
```

```xml
<!-- AndroidManifest.xml -->
<activity
    android:name=".MainActivity"
    android:theme="@style/Theme.App.Starting">  <!-- ✅ Use splash theme -->
```

### Migrating Existing Splash Screen Activities

**Option 1: Routing Activity** — use `setKeepOnScreenCondition`:

```kotlin
// ✅ Keep splash screen until routing completes
class RoutingActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        installSplashScreen().setKeepOnScreenCondition { true }
        super.onCreate(savedInstanceState)

        // Routing logic
        navigateToDestination()
        finish()
    }
}
```

**Option 2: Remove custom Activity** (recommended):
- Use lazy initialization for components
- Show placeholder UI while loading data
- Apply caching for fast content display

## Follow-ups

- How does `setKeepOnScreenCondition` affect splash screen dismissal timing?
- What are the performance implications of using animated icons in splash screens?
- How do you handle different screen densities for splash screen icons?
- What is the relationship between `windowSplashScreenAnimationDuration` and app startup performance?
- How can you customize the exit animation when transitioning from splash to main content?

## References

- [Android Splash Screen API Documentation](https://developer.android.com/develop/ui/views/launch/splash-screen)
- [Migrate to Android 12 Splash Screen](https://developer.android.com/develop/ui/views/launch/splash-screen/migrate)
- [[c-activity-lifecycle]]
- [[c-android-themes]]

## Related Questions

### Prerequisites (Easier)
- [[q-activity-lifecycle--android--easy]] - Understanding Activity lifecycle
- [[q-android-manifest-basics--android--easy]] - Manifest configuration

### Related (Same Level)
- [[q-app-startup-library--android--medium]] - App initialization
- [[q-app-startup-optimization--android--medium]] - Launch performance
- [[q-theme-styling-android--android--medium]] - Theming system

### Advanced (Harder)
- [[q-custom-activity-transitions--android--hard]] - Advanced transitions
- [[q-startup-performance-profiling--android--hard]] - Performance optimization
