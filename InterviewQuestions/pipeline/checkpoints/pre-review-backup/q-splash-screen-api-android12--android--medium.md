---
id: 20251017-144925
title: "Splash Screen API (Android 12+)"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [splash-screen, android12, app-startup, ui, difficulty/medium, android/views, android/app-startup, android/ui-animation]
language_tags: [splash-screen, android12, app-startup, ui, difficulty/medium, android/views, android/app-startup, android/ui-animation]
moc: moc-android
related: [q-parsing-optimization-android--android--medium, q-paging-library-3--android--medium, q-multiple-manifests-multimodule--android--medium]
original_language: en
source: https://github.com/Kirchhoff-/Android-Interview-Questions
subtopics:
  - ui-views
  - app-startup
  - ui-animation
---
# Splash Screen API (Android 12+) / API Splash Screen (Android 12+)

**English**: What do you know about Splash Screen API?

**Русский**: Что вы знаете об API Splash Screen?

## Answer (EN)
**English**:

The **Splash Screen** is the first screen visible to the user when the application is launched. This is an important screen where the user gets the first impression of the application.

### When Splash Screen Shows

When a user launches an app while the app's process isn't running (a cold start) or the `Activity` isn't created (a warm start), the following events occur:
- The system shows the splash screen using themes and any animations that you define
- When the app is ready, the splash screen is dismissed and the app displays

**Note**: The splash screen never shows during a hot start.

### Android 12 Changes

Starting in Android 12, the system applies the [Android system default splash screen](https://developer.android.com/about/versions/12/features/splash-screen) on cold and warm starts for all apps. By default, this system splash screen is constructed using your app's launcher icon element and the `windowBackground` of your theme, if it's a single color.

### SplashScreen Compat Library

You can use the `SplashScreen` API directly, but we strongly recommend using the **Androidx SplashScreen compat library** instead. The compat library uses the `SplashScreen` API, enables backward-compatibility, and creates a consistent look and feel for splash screen display across all Android versions.

**Without compat library**:
- On Android 11 and earlier: splash screen looks the same as before
- On Android 12+: splash screen has the Android 12 look and feel

**With compat library**:
- The system displays the same splash screen on all versions of Android

### How to Add a Splash Screen

#### 1. Add Dependencies

Add the following dependency to your app module's `build.gradle` file:

```gradle
dependencies {
    implementation("androidx.core:core-splashscreen:1.2.0-alpha01")
}
```

#### 2. Add a Theme

Create a splash screen theme in `res/values/styles.xml`. The parent element depends on the icon's shape:
- If the icon is round, use `Theme.SplashScreen`
- If the icon is a different shape, use `Theme.SplashScreen.IconBackground`

```xml
<resources>
    <style name="Theme.App" parent="@android:style/Theme.DeviceDefault" />

    <style name="Theme.App.Starting" parent="Theme.SplashScreen">
        <!-- Set the splash screen background to black -->
        <item name="windowSplashScreenBackground">@android:color/black</item>
        <!-- Use windowSplashScreenAnimatedIcon to add a drawable or an animated drawable -->
        <item name="windowSplashScreenAnimatedIcon">@drawable/splash_screen</item>
        <!-- Set the theme of the Activity that follows your splash screen -->
        <item name="postSplashScreenTheme">@style/Theme.App</item>
    </style>
</resources>
```

For non-round icons, you need to set a background color:

```xml
<style name="Theme.App.Starting" parent="Theme.SplashScreen.IconBackground">
    ...
    <!-- Set a white background behind the splash screen icon -->
    <item name="windowSplashScreenIconBackgroundColor">@android:color/white</item>
</style>
```

#### 3. Create a Drawable for the Theme

Create a new file `res/drawable/splash_screen.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item
        android:width="@dimen/splash_screen_icon_size"
        android:height="@dimen/splash_screen_icon_size"
        android:drawable="@mipmap/ic_launcher"
        android:gravity="center" />
</layer-list>
```

Define icon size in `res/values/dimens.xml`:

```xml
<!-- Round app icon can take all of default space -->
<dimen name="splash_screen_icon_size">48dp</dimen>

<!-- Non-round icon with background must use reduced size -->
<dimen name="splash_screen_icon_size">36dp</dimen>
```

#### 4. Specify the Theme

In your app's manifest file (`AndroidManifest.xml`), replace the theme of the starting activity:

```xml
<manifest>
    <application android:theme="@style/Theme.App.Starting">
       <!-- or -->
       <activity android:theme="@style/Theme.App.Starting">
          <!-- ... -->
</manifest>
```

#### 5. Update Your Starting Activity

Install your splash screen in the starting activity before calling `super.onCreate()`:

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        // Handle the splash screen transition
        installSplashScreen()

        super.onCreate(savedInstanceState)
        setContent {
            WearApp("Wear OS app")
        }
    }
}
```

### Adapting Custom Splash Screen Activities

After you migrate to the splash screen for Android 12 and later, decide what to do with your previous custom splash screen `Activity`. You have the following options:

#### Prevent the Custom Activity from Being Displayed

If your previous splash screen `Activity` is primarily used for routing, you can use `SplashScreen.setKeepOnScreenCondition` to keep the routing activity in place but stop it from rendering:

```kotlin
class RoutingActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        val splashScreen = installSplashScreen()
        super.onCreate(savedInstanceState)

        // Keep the splash screen visible for this Activity
        splashScreen.setKeepOnScreenCondition { true }
        startSomeNextActivity()
        finish()
    }
}
```

#### Keep the Custom Activity for Branding

If you want to use a previous splash screen `Activity` for branding reasons, you can transition from the system splash screen into your custom splash screen `Activity` by customizing the animation for dismissing the splash screen.

#### Remove the Custom Splash Screen Activity

Generally, we recommend removing your previous custom splash screen `Activity` altogether to avoid duplication, increase efficiency, and reduce loading times. Techniques to avoid showing redundant splash screens:

- **Use lazy loading** for your components, modules, or libraries
- **Create placeholders** while loading a small amount of data locally
- **Show placeholders** for network-based loads with indeterminate durations
- **Use caching** - show cached content while loading more recent content

## Ответ (RU)

**Splash Screen** - первый экран при запуске приложения. С Android 12 система автоматически показывает системный splash screen (launcher icon + `windowBackground`).

**Рекомендация:** использовать **Androidx SplashScreen compat library** для единообразного вида на всех версиях Android.

**Основные шаги:** 1) добавить зависимость `androidx.core:core-splashscreen`, 2) создать тему `Theme.SplashScreen`, 3) вызвать `installSplashScreen()` в `onCreate()` перед `super.onCreate()`, 4) опционально удалить старую custom Activity для эффективности.

**Splash Screen** (экран заставки) - это первый экран, видимый пользователю при запуске приложения. Это важный экран, на котором пользователь получает первое впечатление о приложении.

### When Splash Screen Shows

Когда пользователь запускает приложение, когда процесс приложения не запущен (холодный старт) или `Activity` не создана (теплый старт), происходят следующие события:
- Система показывает splash screen, используя темы и анимации, которые вы определили
- Когда приложение готово, splash screen закрывается и отображается приложение

**Примечание**: Splash screen никогда не показывается при горячем старте.

### Android 12 Changes

Начиная с Android 12, система применяет [системный splash screen по умолчанию](https://developer.android.com/about/versions/12/features/splash-screen) при холодном и теплом запуске для всех приложений. По умолчанию этот системный splash screen создается с использованием иконки запуска вашего приложения и `windowBackground` вашей темы, если это один цвет.

### SplashScreen Compat Library

Вы можете использовать `SplashScreen` API напрямую, но мы настоятельно рекомендуем использовать **библиотеку совместимости Androidx SplashScreen**. Библиотека совместимости использует `SplashScreen` API, обеспечивает обратную совместимость и создает согласованный внешний вид splash screen на всех версиях Android.

**Без библиотеки совместимости**:
- На Android 11 и ранее: splash screen выглядит так же, как раньше
- На Android 12+: splash screen имеет внешний вид Android 12

**С библиотекой совместимости**:
- Система отображает одинаковый splash screen на всех версиях Android

### How to Add a Splash Screen

#### 1. Add Dependencies

Добавьте следующую зависимость в файл `build.gradle` модуля приложения:

```gradle
dependencies {
    implementation("androidx.core:core-splashscreen:1.2.0-alpha01")
}
```

#### 2. Add a Theme

Создайте тему splash screen в `res/values/styles.xml`. Родительский элемент зависит от формы иконки:
- Если иконка круглая, используйте `Theme.SplashScreen`
- Если иконка другой формы, используйте `Theme.SplashScreen.IconBackground`

```xml
<resources>
    <style name="Theme.App" parent="@android:style/Theme.DeviceDefault" />

    <style name="Theme.App.Starting" parent="Theme.SplashScreen">
        <!-- Установить черный фон splash screen -->
        <item name="windowSplashScreenBackground">@android:color/black</item>
        <!-- Использовать windowSplashScreenAnimatedIcon для добавления drawable или анимированного drawable -->
        <item name="windowSplashScreenAnimatedIcon">@drawable/splash_screen</item>
        <!-- Установить тему Activity, которая следует за splash screen -->
        <item name="postSplashScreenTheme">@style/Theme.App</item>
    </style>
</resources>
```

Для некруглых иконок нужно установить цвет фона:

```xml
<style name="Theme.App.Starting" parent="Theme.SplashScreen.IconBackground">
    ...
    <!-- Установить белый фон за иконкой splash screen -->
    <item name="windowSplashScreenIconBackgroundColor">@android:color/white</item>
</style>
```

#### 3. Create a Drawable for the Theme

Создайте новый файл `res/drawable/splash_screen.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item
        android:width="@dimen/splash_screen_icon_size"
        android:height="@dimen/splash_screen_icon_size"
        android:drawable="@mipmap/ic_launcher"
        android:gravity="center" />
</layer-list>
```

Определите размер иконки в `res/values/dimens.xml`:

```xml
<!-- Круглая иконка приложения может занимать все пространство по умолчанию -->
<dimen name="splash_screen_icon_size">48dp</dimen>

<!-- Некруглая иконка с фоном должна использовать уменьшенный размер -->
<dimen name="splash_screen_icon_size">36dp</dimen>
```

#### 4. Specify the Theme

В файле манифеста вашего приложения (`AndroidManifest.xml`) замените тему стартовой activity:

```xml
<manifest>
    <application android:theme="@style/Theme.App.Starting">
       <!-- или -->
       <activity android:theme="@style/Theme.App.Starting">
          <!-- ... -->
</manifest>
```

#### 5. Update Your Starting Activity

Установите splash screen в стартовой activity перед вызовом `super.onCreate()`:

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        // Обработать переход splash screen
        installSplashScreen()

        super.onCreate(savedInstanceState)
        setContent {
            WearApp("Wear OS app")
        }
    }
}
```

### Adapting Custom Splash Screen Activities

После миграции на splash screen для Android 12 и выше решите, что делать с вашей предыдущей пользовательской `Activity` splash screen. У вас есть следующие варианты:

#### Prevent the Custom Activity from Being Displayed

Если ваша предыдущая `Activity` splash screen в основном использовалась для маршрутизации, вы можете использовать `SplashScreen.setKeepOnScreenCondition`, чтобы сохранить activity маршрутизации, но остановить ее отрисовку:

```kotlin
class RoutingActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        val splashScreen = installSplashScreen()
        super.onCreate(savedInstanceState)

        // Сохранить splash screen видимым для этой Activity
        splashScreen.setKeepOnScreenCondition { true }
        startSomeNextActivity()
        finish()
    }
}
```

#### Keep the Custom Activity for Branding

Если вы хотите использовать предыдущую `Activity` splash screen для брендинга, вы можете перейти от системного splash screen к вашей пользовательской `Activity` splash screen, настроив анимацию закрытия splash screen.

#### Remove the Custom Splash Screen Activity

В целом, мы рекомендуем полностью удалить вашу предыдущую пользовательскую `Activity` splash screen, чтобы избежать дублирования, повысить эффективность и сократить время загрузки. Техники для избежания показа избыточных splash screens:

- **Использовать ленивую загрузку** для ваших компонентов, модулей или библиотек
- **Создавать плейсхолдеры** при загрузке небольшого количества данных локально
- **Показывать плейсхолдеры** для загрузок на основе сети с неопределенной длительностью
- **Использовать кэширование** - показывать кэшированный контент при загрузке более свежего контента

## References

- [Migrate your splash screen implementation to Android 12 and later](https://developer.android.com/develop/ui/views/launch/splash-screen/migrate)
- [Splash screens](https://developer.android.com/develop/ui/views/launch/splash-screen)
- [Add a splash screen](https://developer.android.com/training/wearables/apps/splash-screen)

---

## Related Questions

### Prerequisites (Easier)
- [[q-graphql-vs-rest--networking--easy]] - Networking

### Related (Medium)
- [[q-http-protocols-comparison--android--medium]] - Networking
- [[q-api-file-upload-server--android--medium]] - Networking
- [[q-privacy-sandbox-topics-api--privacy--medium]] - Networking
- [[q-api-rate-limiting-throttling--android--medium]] - Networking
- [[q-kmm-ktor-networking--multiplatform--medium]] - Networking

### Advanced (Harder)
- [[q-data-sync-unstable-network--android--hard]] - Networking
