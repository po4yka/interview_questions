---
anki_cards:
- slug: android-361-0-en
  language: en
  anki_id: 1769330092803
  synced_at: '2026-01-25T13:02:19.712257'
- slug: android-361-0-ru
  language: ru
  anki_id: 1769330092823
  synced_at: '2026-01-25T13:02:19.714558'
- slug: android-732-0-en
  language: en
  anki_id: 1769330092848
  synced_at: '2026-01-25T13:02:19.716110'
- slug: android-732-0-ru
  language: ru
  anki_id: 1769330092874
  synced_at: '2026-01-25T13:02:19.717922'
- slug: q-what-design-systems-in-android-have-you-worked-with--android--medium-0-en
  language: en
  anki_id: 1769330092898
  synced_at: '2026-01-25T13:02:19.720160'
- slug: q-what-design-systems-in-android-have-you-worked-with--android--medium-0-ru
  language: ru
  anki_id: 1769330092925
  synced_at: '2026-01-25T13:02:19.721833'
---
id: android-361
id: android-732
title: "What Design Systems In Android Have You Worked With / С какими дизайн-системами Android вы работали"
aliases: ["What Design Systems In Android Have You Worked With", "С какими дизайн-системами Android вы работали"]
topic: android
subtopics: [ui-theming, ui-widgets]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android-themes, c-android-ui-composition, c-compose-recomposition, c-recomposition, c-wear-compose, q-android-jetpack-overview--android--easy]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android/ui-theming, android/ui-widgets, design-system, difficulty/medium, material-design, ui]
---
# Вопрос (RU)

> С какими дизайн-системами в Android вы работали?

# Question (EN)

> What design systems in Android have you worked with?

---

## Ответ (RU)

Дизайн-система — это набор переиспользуемых компонентов, правил и паттернов, обеспечивающих консистентность UI. В Android основная система — Material Design от Google (см. также [[c-android-themes]] и [[c-android-ui-composition]]).

### Material Design

**Material Design** — стандарт для Android, интегрированный в экосистему через библиотеку Material Components.

**Ключевые элементы**:
- Цветовые схемы (primary, secondary, surface и др.)
- Типографика и иконки
- Elevation (тени для глубины)
- Shape theming (кастомизация форм)
- Motion (анимации и переходы)

**Пример базовой темы (упрощённый M3-пример)**:

```xml
<!-- ✅ Упрощённый пример темы на базе Material 3.
     На практике используйте полный набор M3-атрибутов (colorPrimary, colorSecondary,
     surface, background и т.д.) и dynamic color для Android 12+ при необходимости. -->
<style name="AppTheme" parent="Theme.Material3.DayNight.NoActionBar">
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

### Кастомные Дизайн-системы

Многие компании создают собственные системы на базе Material Design, используя **design tokens** для централизации стилей.

```kotlin
// ✅ Design tokens для переиспользования (пример для Compose-темизации)
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

### Fluent Design (Microsoft) И HIG (Apple)

**Fluent** и **HIG** — системы для экосистем Microsoft и Apple (Windows, iOS, iPadOS, macOS и др.), редко используются напрямую в Android, но их принципы полезны для кросс-платформенных приложений.

```kotlin
// ❌ Избегайте неконтролируемого смешивания визуальных паттернов разных систем в одном Android-приложении.
// ✅ Базируйтесь на одной основной системе (обычно Material) и аккуратно учитывайте другие
//    только на уровне принципов для кросс-платформенного брендирования.
```

## Answer (EN)

A design system is a collection of reusable components, guidelines, and patterns that ensure UI consistency. In Android, the primary system is Material Design by Google (see also [[c-android-themes]] and [[c-android-ui-composition]]).

### Material Design

**Material Design** is the standard for Android, integrated through the Material Components library.

**Key elements**:
- Color schemes (primary, secondary, surface, etc.)
- Typography and icons
- Elevation (shadows for depth)
- Shape theming (customization)
- Motion (animations and transitions)

**Example theme setup (simplified M3 example)**:

```xml
<!-- ✅ Simplified example of a Material 3-based theme.
     In real projects, use the full M3 attribute set (colorPrimary, colorSecondary,
     surface, background, etc.) and dynamic color on Android 12+ when appropriate. -->
<style name="AppTheme" parent="Theme.Material3.DayNight.NoActionBar">
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
// ✅ Design tokens for reusability (example for Compose theming)
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

**Fluent** and **HIG** are systems for Microsoft and Apple ecosystems (Windows, iOS, iPadOS, macOS, etc.), rarely used directly in Android, but their principles are useful for cross-platform apps.

```kotlin
// ❌ Avoid uncontrolled mixing of visual patterns from different systems in a single Android app.
// ✅ Use one primary system (typically Material) and carefully apply others only as guiding
//    principles for cross-platform branding where needed.
```

---

## Дополнительные Вопросы (RU)

- Как вы реализуете кастомную дизайн-систему в крупной Android-кодовой базе?
- В чем ключевые отличия между Material 2 и Material 3?
- Как вы обеспечиваете консистентность дизайн-системы между несколькими командами?
- Какие инструменты (Figma, Sketch) вы используете для синхронизации design tokens с кодом?
- Как вы учитываете платформо-специфичные требования дизайна в кросс-платформенных приложениях?

## Follow-ups

- How do you implement a custom design system in a large Android codebase?
- What are the key differences between Material 2 and Material 3?
- How do you ensure design system consistency across multiple teams?
- What tools (Figma, Sketch) do you use to sync design tokens with code?
- How do you handle platform-specific design requirements in cross-platform apps?

## Ссылки (RU)

- [Material Design Guidelines](https://m3.material.io/)
- [Material Components for Android](https://github.com/material-components/material-components-android)

## References

- [Material Design Guidelines](https://m3.material.io/)
- [Material Components for Android](https://github.com/material-components/material-components-android)

## Связанные Вопросы (RU)

### Предварительные (проще)

- [[q-android-jetpack-overview--android--easy]]
- [[q-android-app-components--android--easy]]

### Похожие (такой Же уровень)

- [[q-accessibility-color-contrast--android--medium]]

### Продвинутые (сложнее)

- [[q-clean-architecture-android--android--hard]]
- [[q-android-build-optimization--android--medium]]

## Related Questions

### Prerequisites (Easier)

- [[q-android-jetpack-overview--android--easy]]
- [[q-android-app-components--android--easy]]

### Related (Same Level)

- [[q-accessibility-color-contrast--android--medium]]

### Advanced (Harder)

- [[q-clean-architecture-android--android--hard]]
- [[q-android-build-optimization--android--medium]]
