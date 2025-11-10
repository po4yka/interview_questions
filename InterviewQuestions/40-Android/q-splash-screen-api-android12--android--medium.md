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

---

# Вопрос (RU)

> Что вы знаете об API Splash Screen в Android 12+?

# Question (EN)

> What do you know about the Splash Screen API in Android 12+?

## Ответ (RU)

**Splash Screen** — первый экран, отображаемый при запуске приложения. Начиная с Android 12 система автоматически применяет системный splash screen при холодном и тёплом старте.

### Когда Отображается

- **Холодный старт**: процесс приложения не запущен.
- **Тёплый старт**: процесс запущен, но `Activity` ещё не создана.
- **Не отображается** при горячем старте (`Activity` уже в памяти и готова к показу).

### Ключевые Изменения В Android 12

Система автоматически создаёт splash screen:
- Используя иконку запуска приложения (или заданную `windowSplashScreenAnimatedIcon`).
- Используя атрибуты темы `windowSplashScreenBackground` и связанные с ним (например, `windowSplashScreenIconBackgroundColor`).

Системный сплэш:
- Показывается автоматически, без отдельной Splash `Activity`.
- Имеет ограниченную длительность показа — система сама скрывает его, как только приложение готово (и не даст показывать его слишком долго).

### Рекомендуемый Подход: Compat Library

Используйте **androidx.core:core-splashscreen** для единообразия поведения на Android 12+ и более ранних версиях.

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

### Миграция Существующих Splash Screen `Activity`

**Вариант 1: Routing `Activity`** — используйте `setKeepOnScreenCondition`:

```kotlin
// ✅ Сохраняем splash screen, пока не завершён роутинг
class RoutingActivity : ComponentActivity() {
    private var isReady = false

    override fun onCreate(savedInstanceState: Bundle?) {
        val splashScreen = installSplashScreen()
        splashScreen.setKeepOnScreenCondition { !isReady }
        super.onCreate(savedInstanceState)

        // Логика роутинга / инициализации
        navigateToDestination()
        isReady = true
        finish()
    }
}
```

Важно: условие в `setKeepOnScreenCondition` должно стать `false` (как только инициализация завершена), иначе splash screen не будет скрыт.

**Вариант 2: Удалить custom `Activity`** (рекомендуется):
- Используйте ленивую инициализацию компонентов.
- Показывайте placeholder UI во время загрузки данных.
- Применяйте кэширование для быстрого отображения контента.
- Не выполняйте долгие операции на сплэш-экране — перемещайте их в фоновые потоки / отложенную инициализацию.

## Answer (EN)

**Splash Screen** is the first screen displayed when launching an app. Starting with Android 12, the system automatically applies a system splash screen on cold and warm starts.

### When It Shows

- **Cold start**: app process isn't running.
- **Warm start**: process is running but the `Activity` has not been created yet.
- **Not shown** on hot start (`Activity` already in memory and ready to display).

### Key Changes in Android 12

The system automatically constructs the splash screen:
- Using the app launcher icon (or an explicitly set `windowSplashScreenAnimatedIcon`).
- Using theme attributes such as `windowSplashScreenBackground` and related properties (e.g., `windowSplashScreenIconBackgroundColor`).

The system splash:
- Is shown automatically without a dedicated Splash `Activity`.
- Has a bounded display duration — the system hides it once the app is ready and prevents keeping it visible for too long.

### Recommended Approach: Compat Library

Use **androidx.core:core-splashscreen** for consistent behavior across Android 12+ and older versions.

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

**Option 1: Routing `Activity`** — use `setKeepOnScreenCondition`:

```kotlin
// ✅ Keep splash screen while routing/initialization is in progress
class RoutingActivity : ComponentActivity() {
    private var isReady = false

    override fun onCreate(savedInstanceState: Bundle?) {
        val splashScreen = installSplashScreen()
        splashScreen.setKeepOnScreenCondition { !isReady }
        super.onCreate(savedInstanceState)

        // Routing / initialization logic
        navigateToDestination()
        isReady = true
        finish()
    }
}
```

Important: the condition in `setKeepOnScreenCondition` must eventually return `false` once initialization completes; otherwise the splash screen would never be dismissed.

**Option 2: Remove custom `Activity`** (recommended):
- Use lazy initialization for components.
- Show placeholder UI while loading data.
- Apply caching for fast content display.
- Avoid heavy work on the splash screen; move it to background threads or deferred initialization.

## Дополнительные вопросы (RU)

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

## Связанные вопросы (RU)

### Предпосылки (проще)
- [[q-activity-lifecycle-methods--android--medium]] — Понимание жизненного цикла `Activity`
- [[q-android-manifest-file--android--easy]] — Базовая конфигурация манифеста

### Связанные (того же уровня)
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
