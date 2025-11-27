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
related: [c-activity-lifecycle, c-lifecycle]
created: 2025-10-15
updated: 2025-11-10
tags: [android/app-startup, android/ui-animation, android/ui-views, android12, difficulty/medium, splash-screen]
sources: ["https://github.com/Kirchhoff-/Android-Interview-Questions"]

date created: Saturday, November 1st 2025, 1:24:29 pm
date modified: Tuesday, November 25th 2025, 8:53:56 pm
---
# Вопрос (RU)

> Что вы знаете об API Splash Screen в Android 12+?

# Question (EN)

> What do you know about the Splash Screen API in Android 12+?

## Ответ (RU)

**Splash Screen** — первый экран, отображаемый при запуске приложения. Начиная с Android 12 (API 31), система автоматически добавляет системный splash screen для лаунчер-`Activity` при холодном и тёплом старте приложений, таргетирующих 31+.

### Когда Отображается

- **Холодный старт**: процесс приложения не запущен.
- **Тёплый старт**: процесс запущен, но `Activity` ещё не создана.
- **Обычно не отображается** при горячем старте (`Activity` уже в памяти и готова к показу), хотя конкретное поведение зависит от состояния задачи и жизненного цикла `Activity`.

### Ключевые Изменения В Android 12

Система автоматически создаёт splash screen:
- используя иконку запуска приложения (или заданную `windowSplashScreenAnimatedIcon`),
- используя атрибуты темы `windowSplashScreenBackground` и связанные с ним (например, `windowSplashScreenIconBackgroundColor`).

Системный сплэш:
- показывается автоматически, без отдельной Splash-`Activity`;
- применяется только к лаунчер-`Activity`; не следует назначать тему `Theme.SplashScreen` вторичным `Activity`;
- имеет минимальное и максимальное время показа, контролируемое системой; система скрывает его, как только приложение готово, и не позволяет удерживать экран слишком долго. Дополнительно можно слегка задержать скрытие с помощью `setKeepOnScreenCondition`, но условие должно быстро стать `false`.

### Рекомендуемый Подход: Compat Library

Используйте **androidx.core:core-splashscreen** для единообразного поведения на Android 12+ и более ранних версиях, а также для использования нового API в приложениях с `targetSdk` ниже 31.

**Пример интеграции**:

```kotlin
// ✅ Правильный порядок вызовов
class MainActivity : ComponentActivity() { // или AppCompatActivity
    override fun onCreate(savedInstanceState: Bundle?) {
        installSplashScreen()  // До super.onCreate()
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}
```

```xml
<!-- ✅ Минимальная тема splash screen для лаунчер-Activity -->
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
    android:exported="true"
    android:theme="@style/Theme.App.Starting">
    <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.LAUNCHER" />
    </intent-filter>
</activity>  <!-- ✅ Используем splash-тему только для лаунчер-Activity -->
```

### Миграция Существующих Splash Screen `Activity`

**Вариант 1: Routing `Activity`** — используйте `setKeepOnScreenCondition` из `core-splashscreen` на лаунчер-/роутинговой `Activity`:

```kotlin
// ✅ Сохраняем splash screen, пока не завершён роутинг
class RoutingActivity : ComponentActivity() {
    private var isReady = false

    override fun onCreate(savedInstanceState: Bundle?) {
        val splashScreen = installSplashScreen()
        splashScreen.setKeepOnScreenCondition { !isReady }
        super.onCreate(savedInstanceState)

        // Логика роутинга / инициализации (должна быть быстрой)
        navigateToDestination()
        isReady = true
        finish()
    }
}
```

Важно: условие в `setKeepOnScreenCondition` должно как можно скорее стать `false` (как только инициализация завершена), иначе система будет вынуждена удерживать сплэш-экран дольше положенного и ухудшится UX.

**Вариант 2: Удалить custom `Activity`** (рекомендуется):
- используйте ленивую инициализацию компонентов;
- показывайте placeholder UI во время загрузки данных;
- применяйте кэширование для быстрого отображения контента;
- не выполняйте долгие операции на сплэш-экране — переносите их в фоновые потоки / отложенную инициализацию, оставляя системный splash максимально коротким.

## Answer (EN)

**Splash Screen** is the first screen displayed when launching an app. Starting with Android 12 (API 31), the system automatically adds a system splash screen for the launcher `Activity` on cold and warm starts for apps targeting 31+.

### When It Shows

- **Cold start**: app process isn't running.
- **Warm start**: process is running but the `Activity` has not been created yet.
- **Typically not shown** on hot start (`Activity` already in memory and ready to display), though behavior can depend on the task state and `Activity` lifecycle transitions.

### Key Changes in Android 12

The system automatically constructs the splash screen:
- using the app launcher icon (or an explicitly set `windowSplashScreenAnimatedIcon`),
- using theme attributes such as `windowSplashScreenBackground` and related properties (e.g., `windowSplashScreenIconBackgroundColor`).

The system splash:
- is shown automatically without a dedicated Splash `Activity`;
- is applied only to the launcher `Activity`; you should not set `Theme.SplashScreen` on secondary activities;
- has a minimum and maximum display duration controlled by the system; it is dismissed once the app is ready, and the system prevents keeping it for too long. You can slightly delay dismissal with `setKeepOnScreenCondition`, but the condition must become `false` quickly.

### Recommended Approach: Compat Library

Use **androidx.core:core-splashscreen** for consistent behavior across Android 12+ and older versions, and to use the new API even when your `targetSdk` is below 31.

**Integration example**:

```kotlin
// ✅ Correct call order
class MainActivity : ComponentActivity() { // or AppCompatActivity
    override fun onCreate(savedInstanceState: Bundle?) {
        installSplashScreen()  // Before super.onCreate()
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}
```

```xml
<!-- ✅ Minimal splash screen theme for the launcher Activity -->
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
    android:exported="true"
    android:theme="@style/Theme.App.Starting">
    <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.LAUNCHER" />
    </intent-filter>
</activity>  <!-- ✅ Use splash theme only for the launcher Activity -->
```

### Migrating Existing Splash Screen Activities

**Option 1: Routing `Activity`** — use `setKeepOnScreenCondition` from `core-splashscreen` on the launcher/routing `Activity`:

```kotlin
// ✅ Keep splash screen while routing/initialization is in progress
class RoutingActivity : ComponentActivity() {
    private var isReady = false

    override fun onCreate(savedInstanceState: Bundle?) {
        val splashScreen = installSplashScreen()
        splashScreen.setKeepOnScreenCondition { !isReady }
        super.onCreate(savedInstanceState)

        // Routing / initialization logic (should be quick)
        navigateToDestination()
        isReady = true
        finish()
    }
}
```

Important: the condition in `setKeepOnScreenCondition` must become `false` as soon as initialization completes; keeping it `true` for too long would degrade UX and conflict with system expectations for short splash duration.

**Option 2: Remove custom `Activity`** (recommended):
- use lazy initialization for components;
- show placeholder UI while loading data;
- apply caching for fast content display;
- avoid heavy work on the splash screen; move it to background threads or deferred initialization, keeping the system splash as short as possible.

## Дополнительные Вопросы (RU)

- Как `setKeepOnScreenCondition` влияет на время скрытия splash screen?
- Каковы последствия для производительности при использовании анимированных иконок на splash screen?
- Как обрабатывать разные плотности экранов для иконок splash screen?
- Какова связь между `windowSplashScreenAnimationDuration` и производительностью запуска приложения?
- Как настроить анимацию выхода при переходе от splash к основному контенту?

## Follow-ups

- How does `setKeepOnScreenCondition` affect splash screen dismissal timing?
- What are the performance implications of using animated icons in splash screens?
- How do you handle different screen densities for splash screen icons?
- What is the relationship between `windowSplashScreenAnimationDuration` and app startup performance?
- How can you customize the exit animation when transitioning from splash to main content?

## Ссылки (RU)

- [Документация Android Splash Screen API](https://developer.android.com/develop/ui/views/launch/splash-screen)
- [Миграция на Android 12 Splash Screen](https://developer.android.com/develop/ui/views/launch/splash-screen/migrate)
- [[c-activity-lifecycle]]

## References

- [Android Splash Screen API Documentation](https://developer.android.com/develop/ui/views/launch/splash-screen)
- [Migrate to Android 12 Splash Screen](https://developer.android.com/develop/ui/views/launch/splash-screen/migrate)
- [[c-activity-lifecycle]]

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-activity-lifecycle-methods--android--medium]] — Понимание жизненного цикла `Activity`
- [[q-android-manifest-file--android--easy]] — Базовая конфигурация манифеста

### Связанные (того Же уровня)
- [[q-android-app-bundles--android--easy]] — App `Bundle` и распространение
- [[q-android-build-optimization--android--medium]] — Оптимизация запуска и сборки
- [[q-android-performance-measurement-tools--android--medium]] — Измерение производительности запуска

### Продвинутые (сложнее)
- [[q-android-runtime-art--android--medium]] — Детали рантайма ART и влияние на старт
- [[q-android-build-optimization--android--medium]] — Продвинутая оптимизация старта приложения

## Related Questions

### Prerequisites (Easier)
- [[q-activity-lifecycle-methods--android--medium]] - Understanding `Activity` lifecycle
- [[q-android-manifest-file--android--easy]] - Manifest configuration

### Related (Same Level)
- [[q-android-app-bundles--android--easy]] - App `Bundle` basics
- [[q-android-build-optimization--android--medium]] - Build and startup optimization
- [[q-android-performance-measurement-tools--android--medium]] - Startup performance measurement

### Advanced (Harder)
- [[q-android-runtime-art--android--medium]] - ART runtime details and impact on startup
- [[q-android-build-optimization--android--medium]] - Advanced startup optimization
