---
id: android-461
title: Dark Theme Android / Темная тема Android
aliases: [Dark Theme Android, Темная тема Android]
topic: android
subtopics:
  - ui-theming
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-android-components
  - q-android-lint-tool--android--medium
  - q-main-thread-android--android--medium
  - q-parsing-optimization-android--android--medium
created: 2025-10-20
updated: 2025-11-10
tags: [android/ui-theming, dark-theme, daynight, difficulty/medium, material-design, theming]
sources:
  - "https://developer.android.com/guide/topics/ui/look-and-feel/darktheme"

date created: Saturday, November 1st 2025, 1:27:37 pm
date modified: Tuesday, November 25th 2025, 8:54:01 pm
---
# Вопрос (RU)
> Как реализовать темную тему в Android? Объясните ключевые подходы и преимущества.

# Question (EN)
> How to implement dark theme in Android? Explain key approaches and benefits.

## Ответ (RU)

Темная тема в Android — это режим оформления, при котором UI использует темную цветовую схему. Начиная с Android 10 (API 29) темная тема стала системной настройкой, но через `DayNight`-темы (`AppCompat` / `MaterialComponents`) и ресурсные квалификаторы (`values-night`) её можно корректно поддерживать и на более старых версиях.

Основные преимущества:
- экономия батареи на OLED-экранах (за счет того, что темные/черные пиксели потребляют меньше энергии);
- снижение зрительной нагрузки в условиях низкой освещенности;
- единообразие с системными настройками пользователя.

### Ключевые Подходы

**1. DayNight темы**

Используйте `Theme.MaterialComponents.DayNight` или `Theme.AppCompat.DayNight` с автоматическим переключением на основе системных настроек (где доступно) или выбранного режима приложения:

```xml
<!-- res/values/themes.xml -->
<style name="AppTheme" parent="Theme.MaterialComponents.DayNight">
    <item name="colorPrimary">@color/purple_500</item>
    <item name="colorOnPrimary">@color/white</item>
</style>
```

**2. Атрибуты темы вместо hardcoded цветов**

Всегда используйте атрибуты темы (`?attr/...`) вместо жестко заданных цветов — они автоматически адаптируются к текущей теме:

```xml
<!-- ❌ Неправильно: жестко заданные цвета -->
<TextView
    android:textColor="#000000"
    android:background="#FFFFFF" />

<!-- ✅ Правильно: атрибуты темы -->
<TextView
    android:textColor="?attr/colorOnSurface"
    android:background="?attr/colorSurface" />
```

**3. Альтернативные ресурсы (values-night/)**

Создайте папку `res/values-night/` для ресурсов, специфичных для темной темы. Android (и AppCompat) автоматически выбирает правильную папку на основе текущей темы/ночного режима:

```xml
<!-- res/values/colors.xml -->
<color name="surface">#FFFFFF</color>

<!-- res/values-night/colors.xml -->
<color name="surface">#121212</color>
```

**4. Программное управление темой**

Используйте `AppCompatDelegate.setDefaultNightMode()` для программного переключения темы. Рекомендуется использовать `MODE_NIGHT_FOLLOW_SYSTEM`, чтобы соответствовать системным настройкам пользователя (на устройствах, где это поддерживается):

```kotlin
// В Application.onCreate() или Activity
AppCompatDelegate.setDefaultNightMode(
    AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM // Рекомендуется
    // MODE_NIGHT_YES — принудительно темная тема
    // MODE_NIGHT_NO — принудительно светлая тема
    // MODE_NIGHT_AUTO_BATTERY — темная тема при активированном режимe энергосбережения
    // MODE_NIGHT_AUTO — (устаревший) автоматический выбор на основе времени суток/расположения
)
```

### Критические Детали

**Обработка изменения темы**

При изменении ночного режима через `AppCompatDelegate` активити по умолчанию пересоздается (вызывается `onCreate()` заново), чтобы корректно применить новую тему. Это требует сохранения состояния через `onSaveInstanceState()` и/или `ViewModel`.

```kotlin
class MainActivity : AppCompatActivity() {
    fun switchTheme(nightMode: Int) {
        if (AppCompatDelegate.getDefaultNightMode() != nightMode) {
            AppCompatDelegate.setDefaultNightMode(nightMode)
            // Activity будет автоматически пересоздана для применения темы
        }
    }
}
```

**Рекомендации Material Design**

- Фон: используйте почти черный (`#121212`) вместо чистого черного (`#000000`) для лучшей читаемости и снижения артефактов на OLED.
- Elevation: используйте elevation overlays и поверхности из Material-темы (`colorSurface`, `colorSurfaceVariant` и т.п.), а не ручные тени.
- Текст: обеспечивайте достаточный контраст (минимум 4.5:1 для обычного текста и 3:1 для крупного текста).
- Акцентные цвета: проверяйте, что они хорошо читаются как на светлом, так и на темном фоне.

## Answer (EN)

Dark theme in Android is a UI mode where the interface uses a dark color scheme. Starting from Android 10 (API 29), dark theme is exposed as a system setting, but with `DayNight` themes (`AppCompat` / `MaterialComponents`) and `values-night` resources you can support it properly on earlier API levels as well.

Main benefits:
- battery savings on OLED screens (because dark/black pixels consume less power);
- reduced eye strain in low-light conditions;
- consistency with user system preference.

### Key Approaches

**1. DayNight Themes**

Use `Theme.MaterialComponents.DayNight` or `Theme.AppCompat.DayNight` with automatic switching based on system settings (where available) or the app-selected mode:

```xml
<!-- res/values/themes.xml -->
<style name="AppTheme" parent="Theme.MaterialComponents.DayNight">
    <item name="colorPrimary">@color/purple_500</item>
    <item name="colorOnPrimary">@color/white</item>
</style>
```

**2. Theme Attributes Instead of Hardcoded Colors**

Always use theme attributes (`?attr/...`) instead of hardcoded colors — they automatically adapt to the current theme:

```xml
<!-- ❌ Wrong: hardcoded colors -->
<TextView
    android:textColor="#000000"
    android:background="#FFFFFF" />

<!-- ✅ Correct: theme attributes -->
<TextView
    android:textColor="?attr/colorOnSurface"
    android:background="?attr/colorSurface" />
```

**3. Alternative Resources (values-night/)**

Create a `res/values-night/` folder for dark theme-specific resources. Android (and AppCompat) automatically selects the appropriate folder based on the current theme/night mode:

```xml
<!-- res/values/colors.xml -->
<color name="surface">#FFFFFF</color>

<!-- res/values-night/colors.xml -->
<color name="surface">#121212</color>
```

**4. Programmatic Theme Control**

Use `AppCompatDelegate.setDefaultNightMode()` for programmatic theme switching. `MODE_NIGHT_FOLLOW_SYSTEM` is recommended to match system settings (on devices that expose this setting):

```kotlin
// In Application.onCreate() or Activity
AppCompatDelegate.setDefaultNightMode(
    AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM // Recommended
    // MODE_NIGHT_YES — force dark theme
    // MODE_NIGHT_NO — force light theme
    // MODE_NIGHT_AUTO_BATTERY — dark theme when battery saver is enabled
    // MODE_NIGHT_AUTO — (deprecated) automatic based on time of day/location
)
```

### Critical Details

**Handling Theme Changes**

When night mode is changed via `AppCompatDelegate`, the `Activity` is recreated by default (its `onCreate()` is called again) so that the new theme is fully applied. You must preserve state via `onSaveInstanceState()` and/or `ViewModel`.

```kotlin
class MainActivity : AppCompatActivity() {
    fun switchTheme(nightMode: Int) {
        if (AppCompatDelegate.getDefaultNightMode() != nightMode) {
            AppCompatDelegate.setDefaultNightMode(nightMode)
            // Activity will be recreated automatically to apply the theme
        }
    }
}
```

**Material Design Guidelines**

- Background: use near-black (`#121212`) instead of pure black (`#000000`) to improve readability and reduce artifacts on OLED.
- Elevation: rely on Material elevation overlays/surfaces from the theme (`colorSurface`, `colorSurfaceVariant`, etc.) instead of manual shadows to preserve correct hierarchy in dark theme.
- Text: maintain sufficient contrast (minimum 4.5:1 for normal text, 3:1 for large text).
- Accent colors: ensure they remain legible on both light and dark backgrounds.

## Дополнительные Вопросы (RU)

- Как обрабатывать тонирование (tint) drawable-ресурсов для темной темы?
- В чем разница между `MODE_NIGHT_FOLLOW_SYSTEM` и `MODE_NIGHT_AUTO_BATTERY`?
- Как тестировать темную тему с разными уровнями elevation?
- Как обрабатывать содержимое `WebView` в темной теме?
- Как избежать мерцания темы при пересоздании `Activity`?

## Follow-ups

- How do you handle drawable tinting for dark theme?
- What's the difference between `MODE_NIGHT_FOLLOW_SYSTEM` and `MODE_NIGHT_AUTO_BATTERY`?
- How do you test dark theme with different elevation levels?
- How to handle `WebView` content in dark theme?
- How to prevent theme flicker during `Activity` recreation?

## Ссылки (RU)

- [Material Design 3 Dark Mode](https://m3.material.io/styles/color/dark-mode/overview)
- [Руководство по темной теме Android](https://developer.android.com/develop/ui/views/theming/darktheme)

## References

- [Material Design 3 Dark Mode](https://m3.material.io/styles/color/dark-mode/overview)
- [Android Dark Theme Guide](https://developer.android.com/develop/ui/views/theming/darktheme)

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-android-components]]

### Предпосылки (проще)
- Понимание системы ресурсов Android
- Базовые знания о Material Design theming

### Связанные (такой Же уровень)
- Система цветов Material Design
- Ресурсные квалификаторы и альтернативные ресурсы

### Продвинутое (сложнее)
- Динамическое оформление с Material You (API 31+)
- Кастомный движок тем с сохранением в `DataStore`
- Анимации смены темы без пересоздания

## Related Questions

### Prerequisites / Concepts

- [[c-android-components]]

### Prerequisites (Easier)
- Understanding of Android resource system
- Basic knowledge of Material Design theming

### Related (Same Level)
- Material Design color system
- Resource qualifiers and alternative resources

### Advanced (Harder)
- Dynamic theming with Material You (API 31+)
- Custom theme engine with `DataStore` persistence
- Theme transition animations without recreation
