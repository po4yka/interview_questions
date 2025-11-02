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
status: reviewed
moc: moc-android
related:
  - q-material-design-theming--android--medium
created: 2025-10-20
updated: 2025-11-02
tags: [android/ui-theming, dark-theme, daynight, difficulty/medium, material-design, theming]
sources:
  - https://developer.android.com/guide/topics/ui/look-and-feel/darktheme
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Sunday, November 2nd 2025, 5:51:12 pm
---

# Вопрос (RU)
> Как реализовать темную тему в Android? Объясните ключевые подходы и преимущества.

# Question (EN)
> How to implement dark theme in Android? Explain key approaches and benefits.

## Ответ (RU)

Темная тема в Android (API 29+) — это системная функция, позволяющая приложениям адаптировать UI под темную цветовую схему. Основные преимущества: экономия батареи на OLED-экранах (до 40%) и снижение усталости глаз в условиях низкой освещенности.

### Ключевые Подходы

**1. DayNight темы**

Используйте `Theme.MaterialComponents.DayNight` или `Theme.AppCompat.DayNight` с автоматическим переключением на основе системных настроек:

```xml
<!-- res/values/themes.xml -->
<style name="AppTheme" parent="Theme.MaterialComponents.DayNight">
    <item name="colorPrimary">@color/purple_500</item>
    <item name="colorOnPrimary">@color/white</item>
</style>
```

**2. Атрибуты темы вместо hardcoded цветов**

Всегда используйте theme attributes (`?attr/...`) вместо hardcoded цветов — они автоматически адаптируются к текущей теме:

```xml
<!-- ❌ Неправильно: хардкод -->
<TextView
    android:textColor="#000000"
    android:background="#FFFFFF" />

<!-- ✅ Правильно: атрибуты темы -->
<TextView
    android:textColor="?attr/colorOnSurface"
    android:background="?attr/colorSurface" />
```

**3. Альтернативные ресурсы (values-night/)**

Создайте папку `res/values-night/` для ресурсов, специфичных для темной темы. Android автоматически выбирает правильную папку на основе текущей темы:

```xml
<!-- res/values/colors.xml -->
<color name="surface">#FFFFFF</color>

<!-- res/values-night/colors.xml -->
<color name="surface">#121212</color>
```

**4. Программное управление темой**

Используйте `AppCompatDelegate.setDefaultNightMode()` для программного переключения темы. Рекомендуется использовать `MODE_NIGHT_FOLLOW_SYSTEM` для соответствия системным настройкам:

```kotlin
// В Application.onCreate() или Activity
AppCompatDelegate.setDefaultNightMode(
    AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM // Рекомендуется
    // MODE_NIGHT_YES — принудительно темная
    // MODE_NIGHT_NO — принудительно светлая
    // MODE_NIGHT_AUTO_BATTERY — темная при низком заряде
)
```

### Критические Детали

**Обработка изменения темы**

При переключении темы `Activity` автоматически пересоздается (вызывается `onCreate()` заново). Это позволяет корректно применить новую тему, но требует сохранения состояния через `onSaveInstanceState()` и `ViewModel`.

```kotlin
class MainActivity : AppCompatActivity() {
    fun switchTheme(nightMode: Int) {
        if (AppCompatDelegate.getDefaultNightMode() != nightMode) {
            AppCompatDelegate.setDefaultNightMode(nightMode)
            // Activity автоматически пересоздастся
        }
    }
}
```

**Material Design рекомендации**

- **Фон**: `#121212` вместо чистого черного (`#000000`) для уменьшения смазывания на OLED и лучшей читаемости
- **Elevation**: через alpha-каналы, не тени — `colorSurface` с повышенной alpha для элементов на разных уровнях elevation
- **Текст**: достаточный контраст (минимум 4.5:1 для обычного текста, 3:1 для крупного текста)
- **Акцентные цвета**: должны работать как на светлом, так и на темном фоне

## Answer (EN)

Dark theme in Android (API 29+) is a system feature allowing apps to adapt UI to a dark color scheme. Main benefits: battery savings on OLED screens (up to 40%) and reduced eye strain in low-light conditions.

### Key Approaches

**1. DayNight Themes**

Use `Theme.MaterialComponents.DayNight` or `Theme.AppCompat.DayNight` with automatic switching based on system settings:

```xml
<!-- res/values/themes.xml -->
<style name="AppTheme" parent="Theme.MaterialComponents.DayNight">
    <item name="colorPrimary">@color/purple_500</item>
    <item name="colorOnPrimary">@color/white</item>
</style>
```

**2. Theme Attributes Instead of Hardcoded Colors**

Always use theme attributes (`?attr/...`) instead of hardcoded colors — they automatically adapt to current theme:

```xml
<!-- ❌ Wrong: hardcoded -->
<TextView
    android:textColor="#000000"
    android:background="#FFFFFF" />

<!-- ✅ Correct: theme attributes -->
<TextView
    android:textColor="?attr/colorOnSurface"
    android:background="?attr/colorSurface" />
```

**3. Alternative Resources (values-night/)**

Create `res/values-night/` folder for dark theme-specific resources. Android automatically selects correct folder based on current theme:

```xml
<!-- res/values/colors.xml -->
<color name="surface">#FFFFFF</color>

<!-- res/values-night/colors.xml -->
<color name="surface">#121212</color>
```

**4. Programmatic Theme Control**

Use `AppCompatDelegate.setDefaultNightMode()` for programmatic theme switching. `MODE_NIGHT_FOLLOW_SYSTEM` is recommended to match system settings:

```kotlin
// In Application.onCreate() or Activity
AppCompatDelegate.setDefaultNightMode(
    AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM // Recommended
    // MODE_NIGHT_YES — force dark
    // MODE_NIGHT_NO — force light
    // MODE_NIGHT_AUTO_BATTERY — dark when battery saver active
)
```

### Critical Details

**Handling Theme Changes**

On theme switch, `Activity` automatically recreates (calls `onCreate()` again). This ensures correct theme application but requires preserving state via `onSaveInstanceState()` and `ViewModel`.

```kotlin
class MainActivity : AppCompatActivity() {
    fun switchTheme(nightMode: Int) {
        if (AppCompatDelegate.getDefaultNightMode() != nightMode) {
            AppCompatDelegate.setDefaultNightMode(nightMode)
            // Activity auto-recreates
        }
    }
}
```

**Material Design Guidelines**

- **Background**: `#121212` instead of pure black (`#000000`) to reduce smearing on OLED and improve readability
- **Elevation**: via alpha channels, not shadows — `colorSurface` with elevated alpha for elements at different elevation levels
- **Text**: sufficient contrast (minimum 4.5:1 for normal text, 3:1 for large text)
- **Accent colors**: must work on both light and dark backgrounds

## Follow-ups

- How do you handle drawable tinting for dark theme?
- What's the difference between `MODE_NIGHT_FOLLOW_SYSTEM` and `MODE_NIGHT_AUTO_BATTERY`?
- How do you test dark theme with different elevation levels?
- How to handle `WebView` content in dark theme?
- How to prevent theme flicker during `Activity` recreation?

## References

- [Material Design 3 Dark Mode](https://m3.material.io/styles/color/dark-mode/overview)
- [Android Dark Theme Guide](https://developer.android.com/develop/ui/views/theming/darktheme)

## Related Questions

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
