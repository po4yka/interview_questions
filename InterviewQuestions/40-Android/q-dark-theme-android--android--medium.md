---
id: 20251012-1227126
title: "Dark Theme Android / Темная тема Android"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [dark-theme, ui, theming, daynight, material-design, difficulty/medium]
---
# What is Dark Theme in Android? / Что такое темная тема в Android?

**English**: What's dark theme?

## Answer (EN)
Dark theme is available in Android 10 (API level 29) and higher. It provides an alternative color scheme that uses dark backgrounds instead of light ones, offering several important benefits.

## Benefits of Dark Theme

1. **Reduced Power Usage**: Can reduce power consumption by a significant amount, especially on devices with OLED or AMOLED screens where black pixels are turned off
2. **Improved Accessibility**: Improves visibility for users with low vision and those who are sensitive to bright light
3. **Low-light Environment**: Makes it easier for anyone to use a device in a low-light environment, reducing eye strain
4. **Modern Design**: Provides a sleek, modern aesthetic that many users prefer

Dark theme applies to both the Android system UI and apps running on the device.

## Supporting Dark Theme in Your App

### 1. Inherit from DayNight Theme

To support Dark theme, set your app's theme (usually found in `res/values/styles.xml`) to inherit from a `DayNight` theme:

**Using AppCompat:**
```xml
<style name="AppTheme" parent="Theme.AppCompat.DayNight">
    <!-- Customize your theme here -->
</style>
```

**Using Material Components:**
```xml
<style name="AppTheme" parent="Theme.MaterialComponents.DayNight">
    <!-- Customize your theme here -->
</style>
```

This ties the app's main theme to the system-controlled night mode flags and gives the app a default Dark theme when it is enabled.

### 2. Use Theme Attributes

Use theme attributes instead of hardcoded colors to ensure proper appearance in both light and dark themes:

**Important Theme Attributes:**
- `?android:attr/textColorPrimary` - General purpose text color (near-black in light, near-white in dark)
- `?attr/colorControlNormal` - General-purpose icon color
- `?attr/colorSurface` - Surface color for cards, sheets, menus
- `?attr/colorOnSurface` - Color for content on surfaces
- `?android:attr/colorBackground` - Window/screen background color

**Example:**
```xml
<TextView
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:textColor="?android:attr/textColorPrimary"
    android:background="?attr/colorSurface" />
```

### 3. Provide Alternative Resources

Create alternative color resources for dark theme in `res/values-night/`:

**res/values/colors.xml (Light theme):**
```xml
<resources>
    <color name="surface">#FFFFFF</color>
    <color name="onSurface">#000000</color>
    <color name="card_background">#EEEEEE</color>
</resources>
```

**res/values-night/colors.xml (Dark theme):**
```xml
<resources>
    <color name="surface">#121212</color>
    <color name="onSurface">#FFFFFF</color>
    <color name="card_background">#1E1E1E</color>
</resources>
```

## Changing Themes In-App

You can allow users to change the app's theme while the app is running. The recommended options are:

- **Light** - `MODE_NIGHT_NO`
- **Dark** - `MODE_NIGHT_YES`
- **System default** - `MODE_NIGHT_FOLLOW_SYSTEM` (recommended default)

**Implementation:**
```kotlin
import androidx.appcompat.app.AppCompatDelegate

class SettingsActivity : AppCompatActivity() {

    fun setThemeMode(mode: String) {
        when (mode) {
            "light" -> AppCompatDelegate.setDefaultNightMode(
                AppCompatDelegate.MODE_NIGHT_NO
            )
            "dark" -> AppCompatDelegate.setDefaultNightMode(
                AppCompatDelegate.MODE_NIGHT_YES
            )
            "system" -> AppCompatDelegate.setDefaultNightMode(
                AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM
            )
        }
    }
}
```

**Saving User Preference:**
```kotlin
// Save preference
fun saveThemePreference(mode: Int) {
    val prefs = getSharedPreferences("settings", Context.MODE_PRIVATE)
    prefs.edit().putInt("theme_mode", mode).apply()
}

// Apply saved preference on app start
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        val prefs = getSharedPreferences("settings", Context.MODE_PRIVATE)
        val themeMode = prefs.getInt(
            "theme_mode",
            AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM
        )
        AppCompatDelegate.setDefaultNightMode(themeMode)
    }
}
```

## Configuration Changes

When the app's theme changes (either through system setting or AppCompat), it triggers a `uiMode` configuration change. This means Activities will be **automatically recreated**.

### Handling Configuration Changes Manually

In some cases you might want to handle the configuration change yourself (e.g., when a video is playing):

**AndroidManifest.xml:**
```xml
<activity
    android:name=".MyActivity"
    android:configChanges="uiMode" />
```

**Activity:**
```kotlin
override fun onConfigurationChanged(newConfig: Configuration) {
    super.onConfigurationChanged(newConfig)

    val currentNightMode = newConfig.uiMode and Configuration.UI_MODE_NIGHT_MASK
    when (currentNightMode) {
        Configuration.UI_MODE_NIGHT_NO -> {
            // Light mode
            updateThemeColors()
        }
        Configuration.UI_MODE_NIGHT_YES -> {
            // Dark mode
            updateThemeColors()
        }
    }
}
```

## Best Practices

### 1. Notifications and Widgets

For UI surfaces displayed on the device but not directly controlled by your app:

**Notifications:**
- Use system-provided notification templates (e.g., `MessagingStyle`)
- The system handles correct view styling automatically

**Widgets and Custom Notification Views:**
- Test content on both Light and Dark themes
- Avoid common pitfalls:
  - Assuming background is always light
  - Hardcoding text colors
  - Setting hardcoded background with default text color
  - Using static-colored drawable icons

**Solution: Use Theme Attributes**
```kotlin
// For RemoteViews (widgets, custom notifications)
val views = RemoteViews(packageName, R.layout.widget_layout)

// Use theme-aware colors
val textColor = ContextCompat.getColor(
    context,
    android.R.attr.textColorPrimary
)
views.setTextColor(R.id.text_view, textColor)
```

### 2. Launch Screens

If your app has a custom launch screen, modify it to reflect the selected theme:

**Remove hardcoded colors:**
```xml
<!-- BAD: Hardcoded white background -->
<item name="android:windowBackground">@color/white</item>

<!-- GOOD: Use theme attribute -->
<item name="android:windowBackground">?android:attr/colorBackground</item>
```

**Note**: Dark-themed `android:windowBackground` drawables only work on Android Q+.

### 3. Testing Dark Theme

**Check for Issues:**
1. Open app in both light and dark modes
2. Enable "Debug GPU overdraw" to check for rendering issues
3. Test all screens, dialogs, and components
4. Verify custom views handle theme correctly
5. Check that images and icons are visible in both themes

**Common Issues to Fix:**
- White text on white background
- Black icons on black background
- Hardcoded colors not adapting to theme
- Images that blend into dark backgrounds
- Insufficient contrast in either theme

### 4. Force Dark (Android 10+)

For apps targeting Android 10+ that don't implement dark theme, the system can apply **Force Dark** automatically:

```xml
<!-- Enable Force Dark (default is true for targetSdk 29+) -->
<style name="AppTheme" parent="...">
    <item name="android:forceDarkAllowed">true</item>
</style>

<!-- Disable Force Dark for specific views -->
<ImageView
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:forceDarkAllowed="false" />
```

**Note**: It's better to implement proper dark theme support rather than relying on Force Dark.

### 5. Material Design Dark Theme Guidelines

Follow Material Design guidelines for dark theme:
- **Primary surface color**: `#121212`
- **Elevation overlays**: Apply white overlays with increasing opacity for elevated surfaces
- **Color adjustments**: Use desaturated colors in dark theme
- **Contrast**: Ensure minimum 4.5:1 contrast ratio for text

**Elevation Overlay Example:**
```xml
<!-- Material Components automatically applies elevation overlays -->
<com.google.android.material.card.MaterialCardView
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:cardElevation="4dp"
    app:cardBackgroundColor="?attr/colorSurface" />
```

## Checking Current Theme

You can programmatically check the current theme mode:

```kotlin
fun isDarkTheme(context: Context): Boolean {
    val nightModeFlags = context.resources.configuration.uiMode and
        Configuration.UI_MODE_NIGHT_MASK
    return nightModeFlags == Configuration.UI_MODE_NIGHT_YES
}

// In composable (Jetpack Compose)
@Composable
fun MyScreen() {
    val isDarkTheme = isSystemInDarkTheme()

    // Adjust UI based on theme
    if (isDarkTheme) {
        // Dark theme specific logic
    } else {
        // Light theme specific logic
    }
}
```

## Summary

To properly support Dark theme:
1. Inherit from `DayNight` theme
2. Use theme attributes instead of hardcoded colors
3. Provide alternative resources in `values-night/`
4. Test thoroughly in both light and dark modes
5. Handle notifications and widgets correctly
6. Allow users to choose theme preference
7. Follow Material Design dark theme guidelines

**Source**: [Dark theme](https://developer.android.com/guide/topics/ui/look-and-feel/darktheme)

## Ответ (RU)
Темная тема доступна в Android 10 (API level 29) и выше. Она предоставляет альтернативную цветовую схему, использующую темные фоны вместо светлых, предлагая несколько важных преимуществ.

## Преимущества темной темы

1. **Снижение энергопотребления**: Может значительно снизить потребление энергии, особенно на устройствах с OLED или AMOLED экранами, где черные пиксели выключены
2. **Улучшенная доступность**: Улучшает видимость для пользователей со слабым зрением и тех, кто чувствителен к яркому свету
3. **Среда с низким освещением**: Облегчает использование устройства в условиях низкой освещенности, снижая напряжение глаз
4. **Современный дизайн**: Обеспечивает элегантную современную эстетику, которую предпочитают многие пользователи

Темная тема применяется как к системному UI Android, так и к приложениям, работающим на устройстве.

## Поддержка темной темы в приложении

### 1. Наследование от DayNight темы

Чтобы поддерживать темную тему, установите тему приложения (обычно находится в `res/values/styles.xml`) для наследования от темы `DayNight`:

**Используя AppCompat:**
```xml
<style name="AppTheme" parent="Theme.AppCompat.DayNight">
    <!-- Настройте тему здесь -->
</style>
```

**Используя Material Components:**
```xml
<style name="AppTheme" parent="Theme.MaterialComponents.DayNight">
    <!-- Настройте тему здесь -->
</style>
```

### 2. Использование атрибутов темы

Используйте атрибуты темы вместо жестко заданных цветов:

**Важные атрибуты темы:**
- `?android:attr/textColorPrimary` - Универсальный цвет текста
- `?attr/colorControlNormal` - Универсальный цвет иконок
- `?attr/colorSurface` - Цвет поверхности для карточек, листов, меню
- `?attr/colorOnSurface` - Цвет контента на поверхностях
- `?android:attr/colorBackground` - Цвет фона окна/экрана

### 3. Альтернативные ресурсы

Создайте альтернативные цветовые ресурсы для темной темы в `res/values-night/`.

## Изменение темы в приложении

Вы можете позволить пользователям изменять тему приложения во время его работы. Рекомендуемые опции:

- **Светлая** - `MODE_NIGHT_NO`
- **Темная** - `MODE_NIGHT_YES`
- **Системная по умолчанию** - `MODE_NIGHT_FOLLOW_SYSTEM` (рекомендуется по умолчанию)

## Изменения конфигурации

Когда тема приложения изменяется (через системные настройки или AppCompat), это вызывает изменение конфигурации `uiMode`. Это означает, что Activity будут автоматически пересозданы.

## Лучшие практики

### 1. Уведомления и виджеты
- Используйте системные шаблоны уведомлений
- Тестируйте контент в обеих темах
- Избегайте жестко заданных цветов

### 2. Экраны запуска
- Удалите жестко заданные цвета
- Используйте атрибуты темы

### 3. Тестирование темной темы
- Проверяйте все экраны в обеих темах
- Проверяйте пользовательские вью
- Убедитесь, что изображения и иконки видимы

### 4. Force Dark (Android 10+)
Для приложений, нацеленных на Android 10+, которые не реализуют темную тему, система может автоматически применить Force Dark.

### 5. Руководство Material Design
Следуйте руководствам Material Design для темной темы:
- Основной цвет поверхности: `#121212`
- Наложения высоты: применяйте белые наложения с увеличивающейся непрозрачностью
- Коррекция цвета: используйте ненасыщенные цвета в темной теме
- Контраст: обеспечьте минимальное соотношение контраста 4.5:1 для текста

## Резюме

Для правильной поддержки темной темы:
1. Наследуйтесь от темы `DayNight`
2. Используйте атрибуты темы вместо жестко заданных цветов
3. Предоставьте альтернативные ресурсы в `values-night/`
4. Тщательно тестируйте в обоих режимах
5. Правильно обрабатывайте уведомления и виджеты
6. Позвольте пользователям выбирать предпочтение темы
7. Следуйте руководствам Material Design для темной темы
