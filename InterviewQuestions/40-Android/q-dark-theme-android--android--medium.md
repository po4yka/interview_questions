---
id: 20251020-200000
title: Dark Theme Android / Темная тема Android
aliases:
- Dark Theme Android
- Темная тема Android
topic: android
subtopics:
- ui-theming
- ui-views
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- q-android-theming-basics--android--medium
- q-material-design-theming--android--medium
- q-android-ui-optimization--android--medium
created: 2025-10-20
updated: 2025-10-20
tags:
- android/ui-theming
- android/ui-views
- dark-theme
- theming
- daynight
- material-design
- difficulty/medium
source: https://developer.android.com/guide/topics/ui/look-and-feel/darktheme
source_note: Android Dark Theme documentation
---# Вопрос (RU)
> Что такое темная тема в Android?

# Question (EN)
> What is Dark Theme in Android?

## Ответ (RU)

Темная тема доступна в Android 10 (API level 29) и выше. Она предоставляет альтернативную цветовую схему с темными фонами вместо светлых, предлагая несколько важных преимуществ.

### Теория: Принципы темной темы

**Основные концепции:**
- **Альтернативная цветовая схема** - темные фоны вместо светлых
- **Системная интеграция** - автоматическое переключение с системой
- **Энергоэффективность** - снижение потребления энергии на OLED экранах
- **Доступность** - улучшение видимости для пользователей с нарушениями зрения
- **Современный дизайн** - эстетичный внешний вид

**Принципы работы:**
- Автоматическое переключение с системной темой
- Использование атрибутов темы вместо жестко заданных цветов
- Поддержка DayNight тем
- Интеграция с Material Design

### Преимущества темной темы

**1. Снижение потребления энергии**
- Значительное снижение на OLED/AMOLED экранах
- Черные пиксели полностью выключены
- Экономия батареи до 30-40%

**2. Улучшение доступности**
- Лучшая видимость для пользователей с нарушениями зрения
- Снижение чувствительности к яркому свету
- Уменьшение напряжения глаз

**3. Использование в условиях слабого освещения**
- Комфортное использование в темноте
- Снижение усталости глаз
- Улучшение пользовательского опыта

**4. Современный дизайн**
- Стильный и эстетичный внешний вид
- Соответствие современным трендам
- Предпочтения пользователей

### Реализация темной темы

**1. Наследование от DayNight темы**
```xml
<!-- AppCompat -->
<style name="AppTheme" parent="Theme.AppCompat.DayNight">
    <!-- Настройки темы -->
</style>

<!-- Material Components -->
<style name="AppTheme" parent="Theme.MaterialComponents.DayNight">
    <!-- Настройки темы -->
</style>
```

**2. Использование атрибутов темы**
```xml
<!-- Плохо: жестко заданные цвета -->
<TextView
    android:textColor="#000000"
    android:background="#FFFFFF" />

<!-- Хорошо: атрибуты темы -->
<TextView
    android:textColor="?android:attr/textColorPrimary"
    android:background="?android:attr/colorBackground" />
```

**3. Создание ресурсов для темной темы**
```xml
<!-- res/values/colors.xml -->
<color name="primary_color">#6200EE</color>
<color name="background_color">#FFFFFF</color>

<!-- res/values-night/colors.xml -->
<color name="primary_color">#BB86FC</color>
<color name="background_color">#121212</color>
```

### Программное управление темой

**Принудительное переключение темы:**
```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        // Принудительная темная тема
        AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_YES)

        // Принудительная светлая тема
        AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_NO)

        // Следование системной теме
        AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM)

        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}
```

**Динамическое переключение:**
```kotlin
fun toggleTheme() {
    val currentMode = AppCompatDelegate.getDefaultNightMode()
    val newMode = when (currentMode) {
        AppCompatDelegate.MODE_NIGHT_YES -> AppCompatDelegate.MODE_NIGHT_NO
        else -> AppCompatDelegate.MODE_NIGHT_YES
    }
    AppCompatDelegate.setDefaultNightMode(newMode)
}
```

### Лучшие практики

**1. Использование атрибутов темы**
- Всегда используйте `?android:attr/` или `?attr/`
- Избегайте жестко заданных цветов
- Тестируйте на обеих темах

**2. Создание ресурсов для ночной темы**
- Создавайте папки `values-night/`
- Используйте соответствующие цвета для темной темы
- Проверяйте контрастность

**3. Тестирование**
- Тестируйте на обеих темах
- Проверяйте читаемость текста
- Убедитесь в правильном отображении изображений

## Answer (EN)

Dark theme is available in Android 10 (API level 29) and higher. It provides an alternative color scheme with dark backgrounds instead of light ones, offering several important benefits.

### Theory: Dark Theme Principles

**Core Concepts:**
- **Alternative color scheme** - dark backgrounds instead of light ones
- **System integration** - automatic switching with system
- **Energy efficiency** - reduced power consumption on OLED screens
- **Accessibility** - improved visibility for users with vision impairments
- **Modern design** - aesthetic appearance

**Working Principles:**
- Automatic switching with system theme
- Using theme attributes instead of hardcoded colors
- DayNight theme support
- Material Design integration

### Dark Theme Benefits

**1. Reduced Power Consumption**
- Significant reduction on OLED/AMOLED screens
- Black pixels are completely turned off
- Battery savings up to 30-40%

**2. Improved Accessibility**
- Better visibility for users with vision impairments
- Reduced sensitivity to bright light
- Decreased eye strain

**3. Low-light Environment Usage**
- Comfortable use in darkness
- Reduced eye fatigue
- Improved user experience

**4. Modern Design**
- Stylish and aesthetic appearance
- Compliance with modern trends
- User preferences

### Dark Theme Implementation

**1. Inherit from DayNight Theme**
```xml
<!-- AppCompat -->
<style name="AppTheme" parent="Theme.AppCompat.DayNight">
    <!-- Theme settings -->
</style>

<!-- Material Components -->
<style name="AppTheme" parent="Theme.MaterialComponents.DayNight">
    <!-- Theme settings -->
</style>
```

**2. Using Theme Attributes**
```xml
<!-- Bad: hardcoded colors -->
<TextView
    android:textColor="#000000"
    android:background="#FFFFFF" />

<!-- Good: theme attributes -->
<TextView
    android:textColor="?android:attr/textColorPrimary"
    android:background="?android:attr/colorBackground" />
```

**3. Creating Resources for Dark Theme**
```xml
<!-- res/values/colors.xml -->
<color name="primary_color">#6200EE</color>
<color name="background_color">#FFFFFF</color>

<!-- res/values-night/colors.xml -->
<color name="primary_color">#BB86FC</color>
<color name="background_color">#121212</color>
```

### Programmatic Theme Management

**Forced Theme Switching:**
```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        // Force dark theme
        AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_YES)

        // Force light theme
        AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_NO)

        // Follow system theme
        AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM)

        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}
```

**Dynamic Theme Switching:**
```kotlin
fun toggleTheme() {
    val currentMode = AppCompatDelegate.getDefaultNightMode()
    val newMode = when (currentMode) {
        AppCompatDelegate.MODE_NIGHT_YES -> AppCompatDelegate.MODE_NIGHT_NO
        else -> AppCompatDelegate.MODE_NIGHT_YES
    }
    AppCompatDelegate.setDefaultNightMode(newMode)
}
```

### Best Practices

**1. Using Theme Attributes**
- Always use `?android:attr/` or `?attr/`
- Avoid hardcoded colors
- Test on both themes

**2. Creating Night Theme Resources**
- Create `values-night/` folders
- Use appropriate colors for dark theme
- Check contrast ratios

**3. Testing**
- Test on both themes
- Check text readability
- Ensure proper image display

## Follow-ups

- How do you handle images in dark theme?
- What are the Material Design guidelines for dark theme?
- How do you test dark theme compatibility?
