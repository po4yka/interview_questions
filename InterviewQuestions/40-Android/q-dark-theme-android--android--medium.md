---
id: android-461
title: Dark Theme Android / Темная тема Android
aliases: ["Dark Theme Android", "Темная тема Android"]
topic: android
subtopics: [ui-theming]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-theming-basics--android--medium, q-android-ui-optimization--android--medium, q-material-design-theming--android--medium]
created: 2025-10-20
updated: 2025-10-27
tags: [android/ui-theming, dark-theme, daynight, difficulty/medium, material-design, theming]
sources: [https://developer.android.com/guide/topics/ui/look-and-feel/darktheme]
date created: Monday, October 27th 2025, 10:26:54 pm
date modified: Thursday, October 30th 2025, 12:47:33 pm
---

# Вопрос (RU)
> Как реализовать темную тему в Android? Объясните ключевые подходы и преимущества.

# Question (EN)
> How to implement dark theme in Android? Explain key approaches and benefits.

## Ответ (RU)

Темная тема в Android (API 29+) - это системная функция, позволяющая приложениям адаптировать UI под темную цветовую схему. Основное преимущество - экономия батареи на OLED экранах (до 40%) и снижение усталости глаз.

### Ключевые Подходы

**1. DayNight темы**

Используйте базовую тему с автоматическим переключением:

```xml
<!-- res/values/themes.xml -->
<style name="AppTheme" parent="Theme.MaterialComponents.DayNight">
    <item name="colorPrimary">@color/purple_500</item>
    <item name="colorOnPrimary">@color/white</item>
</style>
```

**2. Атрибуты темы вместо hardcoded цветов**

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

```xml
<!-- res/values/colors.xml -->
<color name="surface">#FFFFFF</color>

<!-- res/values-night/colors.xml -->
<color name="surface">#121212</color>
```

**4. Программное управление темой**

```kotlin
// В Application.onCreate() или Activity
AppCompatDelegate.setDefaultNightMode(
    AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM // Рекомендуется
    // MODE_NIGHT_YES - принудительно темная
    // MODE_NIGHT_NO - принудительно светлая
)
```

### Критические Детали

**Обработка изменения темы**

Activity пересоздается при переключении темы. Для сохранения состояния:

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

- Фон: `#121212` вместо чистого черного (#000000) для уменьшения смазывания на OLED
- Elevation через alpha, не тени: `colorSurface` с повышенной alpha для элементов на разных уровнях
- Текст: достаточный контраст (минимум 4.5:1 для обычного текста)

## Answer (EN)

Dark theme in Android (API 29+) is a system feature allowing apps to adapt UI to a dark color scheme. Main benefits: battery savings on OLED screens (up to 40%) and reduced eye strain.

### Key Approaches

**1. DayNight Themes**

Use base theme with automatic switching:

```xml
<!-- res/values/themes.xml -->
<style name="AppTheme" parent="Theme.MaterialComponents.DayNight">
    <item name="colorPrimary">@color/purple_500</item>
    <item name="colorOnPrimary">@color/white</item>
</style>
```

**2. Theme Attributes Instead of Hardcoded Colors**

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

```xml
<!-- res/values/colors.xml -->
<color name="surface">#FFFFFF</color>

<!-- res/values-night/colors.xml -->
<color name="surface">#121212</color>
```

**4. Programmatic Theme Control**

```kotlin
// In Application.onCreate() or Activity
AppCompatDelegate.setDefaultNightMode(
    AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM // Recommended
    // MODE_NIGHT_YES - force dark
    // MODE_NIGHT_NO - force light
)
```

### Critical Details

**Handling Theme Changes**

Activity recreates on theme switch. To preserve state:

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

- Background: `#121212` instead of pure black (#000000) to reduce smearing on OLED
- Elevation via alpha, not shadows: `colorSurface` with elevated alpha for elements at different levels
- Text: sufficient contrast (minimum 4.5:1 for normal text)

## Follow-ups

- How do you handle drawable tinting for dark theme?
- What's the difference between `MODE_NIGHT_FOLLOW_SYSTEM` and `MODE_NIGHT_AUTO_BATTERY`?
- How do you test dark theme with different elevation levels?
- How to handle WebView content in dark theme?

## References

- [[c-material-design]]
- https://m3.material.io/styles/color/dark-mode/overview
- https://developer.android.com/develop/ui/views/theming/darktheme

## Related Questions

### Prerequisites
- [[q-android-theming-basics--android--medium]] - Understanding Android theming fundamentals

### Related
- [[q-android-ui-optimization--android--medium]] - UI performance optimization techniques
- [[q-material-design-theming--android--medium]] - Material Design theming patterns

### Advanced
- Dynamic theming with Material You (API 31+)
- Custom theme engine with DataStore persistence
- Theme transition animations without recreation
