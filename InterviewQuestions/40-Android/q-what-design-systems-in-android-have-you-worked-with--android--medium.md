---
id: 20251012-122711144
title: "What Design Systems In Android Have You Worked With / С какими дизайн-системами Android вы работали"
aliases: ["What Design Systems In Android Have You Worked With", "С какими дизайн-системами Android вы работали"]
topic: android
subtopics: [ui-theming, ui-widgets]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-material-design, c-design-tokens, q-how-to-implement-dark-theme--android--medium]
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [android/ui-theming, android/ui-widgets, material-design, design-system, ui, difficulty/medium]
---
# Вопрос (RU)

> С какими дизайн-системами в Android вы работали?

# Question (EN)

> What design systems in Android have you worked with?

---

## Ответ (RU)

Дизайн-система — это набор переиспользуемых компонентов, правил и паттернов, обеспечивающих консистентность UI. В Android основная система — Material Design от Google.

### Material Design

**Material Design** — стандарт для Android, интегрированный в экосистему через библиотеку Material Components.

**Ключевые элементы**:
- Цветовые схемы (primary, secondary, surface)
- Типографика и иконки
- Elevation (тени для глубины)
- Shape theming (кастомизация форм)
- Motion (анимации и переходы)

**Пример базовой темы**:

```kotlin
// ✅ Material 3 тема с динамическими цветами (Android 12+)
<style name="AppTheme" parent="Theme.Material3.DayNight">
    <item name="colorPrimary">@color/md_theme_primary</item>
    <item name="colorOnPrimary">@color/md_theme_on_primary</item>
    <item name="colorSecondary">@color/md_theme_secondary</item>
</style>
```

**Использование компонентов**:

```xml
<!-- ✅ MaterialButton с иконкой и скруглением -->
<com.google.android.material.button.MaterialButton
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="Confirm"
    app:icon="@drawable/ic_check"
    app:cornerRadius="8dp" />

<!-- ✅ MaterialCardView с elevation -->
<com.google.android.material.card.MaterialCardView
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:cardElevation="4dp"
    app:cardCornerRadius="12dp">
    <!-- Контент карточки -->
</com.google.android.material.card.MaterialCardView>
```

### Кастомные дизайн-системы

Многие компании создают собственные системы на базе Material Design, используя **design tokens** для централизации стилей.

```kotlin
// ✅ Design tokens для переиспользования
object DesignTokens {
    object Colors {
        val Primary = Color(0xFF1976D2)
        val Secondary = Color(0xFFFFC107)
        val Error = Color(0xFFD32F2F)
    }

    object Typography {
        val H1 = TextStyle(fontSize = 32.sp, fontWeight = FontWeight.Bold)
        val Body1 = TextStyle(fontSize = 16.sp)
    }

    object Spacing {
        val Small = 8.dp
        val Medium = 16.dp
        val Large = 24.dp
    }
}
```

**Преимущества**:
- Консистентность UI во всем приложении
- Простота обновления стилей (один источник правды)
- Поддержка темной темы и accessibility
- Сокращение дублирования кода

### Fluent Design (Microsoft) и HIG (Apple)

**Fluent** и **HIG** — системы для Windows/iOS, редко используются напрямую в Android, но их принципы полезны для кросс-платформенных приложений.

```kotlin
// ❌ Избегайте смешивания стилей из разных систем
// ✅ Придерживайтесь одной системы для консистентности
```

## Answer (EN)

A design system is a collection of reusable components, guidelines, and patterns that ensure UI consistency. In Android, the primary system is Material Design by Google.

### Material Design

**Material Design** is the standard for Android, integrated through the Material Components library.

**Key elements**:
- Color schemes (primary, secondary, surface)
- Typography and icons
- Elevation (shadows for depth)
- Shape theming (customization)
- Motion (animations and transitions)

**Example theme setup**:

```kotlin
// ✅ Material 3 theme with dynamic colors (Android 12+)
<style name="AppTheme" parent="Theme.Material3.DayNight">
    <item name="colorPrimary">@color/md_theme_primary</item>
    <item name="colorOnPrimary">@color/md_theme_on_primary</item>
    <item name="colorSecondary">@color/md_theme_secondary</item>
</style>
```

**Using components**:

```xml
<!-- ✅ MaterialButton with icon and rounded corners -->
<com.google.android.material.button.MaterialButton
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="Confirm"
    app:icon="@drawable/ic_check"
    app:cornerRadius="8dp" />

<!-- ✅ MaterialCardView with elevation -->
<com.google.android.material.card.MaterialCardView
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:cardElevation="4dp"
    app:cardCornerRadius="12dp">
    <!-- Card content -->
</com.google.android.material.card.MaterialCardView>
```

### Custom Design Systems

Many companies build custom systems on top of Material Design, using **design tokens** for centralized styling.

```kotlin
// ✅ Design tokens for reusability
object DesignTokens {
    object Colors {
        val Primary = Color(0xFF1976D2)
        val Secondary = Color(0xFFFFC107)
        val Error = Color(0xFFD32F2F)
    }

    object Typography {
        val H1 = TextStyle(fontSize = 32.sp, fontWeight = FontWeight.Bold)
        val Body1 = TextStyle(fontSize = 16.sp)
    }

    object Spacing {
        val Small = 8.dp
        val Medium = 16.dp
        val Large = 24.dp
    }
}
```

**Benefits**:
- UI consistency across the app
- Easy style updates (single source of truth)
- Dark theme and accessibility support
- Reduced code duplication

### Fluent Design (Microsoft) and HIG (Apple)

**Fluent** and **HIG** are systems for Windows/iOS, rarely used directly in Android, but their principles are useful for cross-platform apps.

```kotlin
// ❌ Avoid mixing styles from different systems
// ✅ Stick to one system for consistency
```

---

## Follow-ups

- How do you implement a custom design system in a large Android codebase?
- What are the key differences between Material 2 and Material 3?
- How do you ensure design system consistency across multiple teams?
- What tools (Figma, Sketch) do you use to sync design tokens with code?
- How do you handle platform-specific design requirements in cross-platform apps?

## References

- [[c-material-design]]
- [[c-design-tokens]]
- [[c-theming]]
- [Material Design Guidelines](https://m3.material.io/)
- [Material Components for Android](https://github.com/material-components/material-components-android)

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-material-design--android--easy]]
- [[q-how-to-apply-theme-to-activity--android--easy]]

### Related (Same Level)
- [[q-how-to-implement-dark-theme--android--medium]]
- [[q-how-to-create-custom-view--android--medium]]

### Advanced (Harder)
- [[q-clean-architecture-android--android--hard]]
- [[q-how-to-optimize-rendering-performance--android--hard]]
