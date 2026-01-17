---id: android-078
id: android-708
anki_cards:
  - slug: android-078-0-en
    front: "What are key differences between Material 2 and Material 3?"
    back: |
      | Feature | M2 | M3 |
      |---------|----|----|
      | Colors | Fixed palette | Dynamic color from wallpaper |
      | Elevation | Shadow-based | Tonal surfaces |
      | Personalization | Static | User-customized |

      **Migration:**
      - `BottomNavigation` -> `NavigationBar`
      - `Card(elevation=4.dp)` -> `CardDefaults.cardElevation()`
      - Use `MaterialTheme.colorScheme` roles
    tags:
      - android_compose
      - difficulty::easy
  - slug: android-078-0-ru
    front: "Какие ключевые различия между Material 2 и Material 3?"
    back: |
      | Функция | M2 | M3 |
      |---------|----|----|
      | Цвета | Фиксированная палитра | Динамические из обоев |
      | Elevation | На основе теней | Тональные поверхности |
      | Персонализация | Статическая | Пользовательская |

      **Миграция:**
      - `BottomNavigation` -> `NavigationBar`
      - `Card(elevation=4.dp)` -> `CardDefaults.cardElevation()`
      - Используйте роли `MaterialTheme.colorScheme`
    tags:
      - android_compose
      - difficulty::easy
title: Material3 Components / Компоненты Material3
aliases: [Material3 Components, Компоненты Material3]
topic: android
subtopics: [ui-compose, ui-theming]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-compose-recomposition, c-compose-state, c-jetpack-compose, c-recomposition, q-compose-core-components--android--medium, q-material3-dynamic-color-theming--android--medium, q-what-are-the-most-important-components-of-compose--android--medium]
created: 2025-10-13
updated: 2025-11-10
tags: [android, android/ui-compose, android/ui-theming, design-system, difficulty/easy, material3]
sources: []

---
# Вопрос (RU)
> Каковы ключевые различия между Material 2 и Material 3? Перечислите основные компоненты Material 3 и их сценарии использования. Как мигрировать с Material 2 на Material 3?

# Question (EN)
> What are the key differences between Material 2 and Material 3? `List` the main Material 3 components and their use cases. How do you migrate from Material 2 to Material 3?

---

## Ответ (RU)

**Material 3** (Material You) — дизайн-система Google с персонализацией, динамическими цветами и современными компонентами.

### Ключевые Различия: Material 2 Vs Material 3

| Функция | Material 2 | Material 3 |
|---------|------------|------------|
| **Цвета** | Фиксированная палитра | Динамическая система (расширенные семантические роли, поддержка dynamic color) |
| **Персонализация** | Статические темы | Темы из обоев пользователя (dynamic color) |
| **Elevation** | На основе теней | Тональные поверхности + обновлённые elevation-токены |

### Основные Компоненты Material 3

**1. Кнопки (основные варианты):**
```kotlin
// ✅ Filled — основное приоритетное действие
Button(onClick = {}) { Text("Save") }

// ✅ FilledTonalButton — важное действие с меньшим акцентом (альтернатива Filled в некоторых сценариях)
FilledTonalButton(onClick = {}) { Text("Cancel") }

// ✅ OutlinedButton — второстепенные / менее заметные действия
OutlinedButton(onClick = {}) { Text("Secondary") }

// ✅ TextButton — контекстные/inline-действия без сильного акцента
TextButton(onClick = {}) { Text("More") }

// ✅ ElevatedButton — акцент, когда нужно визуально отделить от фона
ElevatedButton(onClick = {}) { Text("Action") }

// ❌ Не используйте Filled для всех действий подряд
```

**2. Навигация:**
- `NavigationBar` — нижняя навигация (современная замена `BottomNavigation` из Material 2)
- `NavigationBarItem` — элементы нижней навигации
- `NavigationRail` — боковая навигация для больших экранов
- `ModalNavigationDrawer` — выдвижное меню

**3. App Bar:**
- `TopAppBar` / `CenterAlignedTopAppBar` — стандартные апп-бары
- `MediumTopAppBar` — средний с поддержкой поведения при прокрутке
- `LargeTopAppBar` — большой, для экранов с расширенным заголовком

**4. Карточки:**
```kotlin
// ✅ Используйте семантические роли из MaterialTheme.colorScheme
Card(
    colors = CardDefaults.cardColors(
        containerColor = MaterialTheme.colorScheme.surfaceVariant // ✅
    ),
    elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
)

// ❌ Не хардкодьте цвета вместо использования colorScheme
Card(colors = CardDefaults.cardColors(containerColor = Color(0xFFE8DEF8)))
```

**5. Chips:**
- `AssistChip` — контекстные действия
- `FilterChip` — фильтрация / выбор состояний
- `InputChip` — представление пользовательского ввода/тегов
- `SuggestionChip` — предложения действий или вариантов

### Миграция С Material 2 На Material 3

**1. Обновить зависимости:**
```gradle
implementation("androidx.compose.material3:material3")
```
(версия указывается через BOM или явно в зависимости от конфигурации проекта)

Material 2 (`androidx.compose.material:*`) и Material 3 можно использовать параллельно для постепенной миграции.

**2. Обновить theme (M3):**
```kotlin
// До: Material 2
MaterialTheme(colors = lightColors())

// После: Material 3 (упрощённый пример)
MaterialTheme(
    colorScheme = lightColorScheme(),
    typography = Typography(),
    shapes = Shapes()
)
```
На практике обычно создают свой composable-тему (например, AppTheme),
которая внутри настраивает `MaterialTheme` c `colorScheme`, `typography` и `shapes`.

**3. Обновить imports:**
```kotlin
// До
import androidx.compose.material.Button

// После
import androidx.compose.material3.Button
```

**4. Обновить компоненты:**
- `BottomNavigation` → `NavigationBar`
- `BottomNavigationItem` → `NavigationBarItem`
- Аналогично — использовать M3-версии компонентов (`Card`, `TopAppBar`, `TextField` и др.)

**5. Учесть breaking changes:**
```kotlin
// Material 2
Card(elevation = 4.dp)

// Material 3
Card(elevation = CardDefaults.cardElevation(defaultElevation = 4.dp))
```

### Динамический Цвет (Android 12+)

```kotlin
@Composable
fun AppTheme(content: @Composable () -> Unit) {
    val context = LocalContext.current
    val colorScheme = when {
        Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            dynamicLightColorScheme(context) // ✅ Цвета из обоев (пример для светлой темы)
        }
        else -> lightColorScheme() // ✅ Корректный fallback для устройств без dynamic color
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography(),
        shapes = Shapes(),
        content = content
    )
}
```
(В реальном приложении обычно поддерживают и темную тему через `dynamicDarkColorScheme` / `darkColorScheme`.)

### Best Practices

1. **Используйте семантические цветовые роли из MaterialTheme.colorScheme** (`primary`, `surfaceVariant` и др.) вместо хардкода
2. **Включайте dynamic color** на Android 12+ с корректным fallback для более старых версий
3. **Соблюдайте иерархию кнопок:** Filled → FilledTonal → Elevated → Outlined → Text
4. **Учитывайте обновлённую модель elevation:** используйте токены/уровни M3 для фона, контейнеров, навигации и модальных элементов
5. **Планируйте миграцию:** при необходимости используйте параллельно Material 2 и Material 3 для постепенной замены компонентов

---

## Answer (EN)

**Material 3** (Material You) is Google's design system with personalization, dynamic colors, and modern components.

### Key Differences: Material 2 Vs Material 3

| Feature | Material 2 | Material 3 |
|---------|------------|------------|
| **Colors** | Fixed palette | Extended semantic roles + support for dynamic color |
| **Personalization** | Static themes | Themes derived from user wallpaper (dynamic color) |
| **Elevation** | Shadow-based | Tonal surfaces + updated elevation tokens |

### Main Material 3 Components

**1. Buttons (core variants):**
```kotlin
// ✅ Filled — high-emphasis primary action
Button(onClick = {}) { Text("Save") }

// ✅ FilledTonalButton — important action with lower emphasis (alternative to Filled in some contexts)
FilledTonalButton(onClick = {}) { Text("Cancel") }

// ✅ OutlinedButton — less prominent secondary actions
OutlinedButton(onClick = {}) { Text("Secondary") }

// ✅ TextButton — inline / contextual actions
TextButton(onClick = {}) { Text("More") }

// ✅ ElevatedButton — when emphasis is needed to separate from the background
ElevatedButton(onClick = {}) { Text("Action") }

// ❌ Don't use Filled for every action
```

**2. Navigation:**
- `NavigationBar` — bottom navigation (modern replacement for `BottomNavigation` from Material 2)
- `NavigationBarItem` — bottom navigation items
- `NavigationRail` — side navigation for larger screens
- `ModalNavigationDrawer` — navigation drawer

**3. App Bar:**
- `TopAppBar` / `CenterAlignedTopAppBar` — standard top app bars
- `MediumTopAppBar` — medium bar with scroll behavior
- `LargeTopAppBar` — large bar for expanded title layouts

**4. Cards:**
```kotlin
// ✅ Use semantic roles from MaterialTheme.colorScheme
Card(
    colors = CardDefaults.cardColors(
        containerColor = MaterialTheme.colorScheme.surfaceVariant // ✅
    ),
    elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
)

// ❌ Don't hardcode colors instead of using colorScheme
Card(colors = CardDefaults.cardColors(containerColor = Color(0xFFE8DEF8)))
```

**5. Chips:**
- `AssistChip` — contextual actions
- `FilterChip` — filtering / toggling options
- `InputChip` — representing user input/tags
- `SuggestionChip` — suggested actions or options

### Migration from Material 2 to Material 3

**1. Update dependencies:**
```gradle
implementation("androidx.compose.material3:material3")
```
(version is provided via BOM or explicitly, depending on your project setup)

Material 2 (`androidx.compose.material:*`) and Material 3 can be used side-by-side to support gradual migration.

**2. Update theme (M3):**
```kotlin
// Before: Material 2
MaterialTheme(colors = lightColors())

// After: Material 3 (simplified example)
MaterialTheme(
    colorScheme = lightColorScheme(),
    typography = Typography(),
    shapes = Shapes()
)
```
In practice, define your own AppTheme composable that configures `MaterialTheme` with `colorScheme`, `typography`, and `shapes`.

**3. Update imports:**
```kotlin
// Before
import androidx.compose.material.Button

// After
import androidx.compose.material3.Button
```

**4. Update components:**
- `BottomNavigation` → `NavigationBar`
- `BottomNavigationItem` → `NavigationBarItem`
- Similarly, adopt M3 versions of components (`Card`, `TopAppBar`, `TextField`, etc.)

**5. Handle breaking changes:**
```kotlin
// Material 2
Card(elevation = 4.dp)

// Material 3
Card(elevation = CardDefaults.cardElevation(defaultElevation = 4.dp))
```

### Dynamic Color (Android 12+)

```kotlin
@Composable
fun AppTheme(content: @Composable () -> Unit) {
    val context = LocalContext.current
    val colorScheme = when {
        Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            dynamicLightColorScheme(context) // ✅ From wallpaper (example for light theme)
        }
        else -> lightColorScheme() // ✅ Fallback when dynamic color is unavailable
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography(),
        shapes = Shapes(),
        content = content
    )
}
```
(In a real app you'd typically support dark theme as well with `dynamicDarkColorScheme` / `darkColorScheme`.)

### Best Practices

1. **Use semantic color roles from MaterialTheme.colorScheme** (`primary`, `surfaceVariant`, etc.) instead of hardcoded colors
2. **Enable dynamic color** on Android 12+ with a proper fallback on lower versions
3. **Follow button hierarchy:** Filled → FilledTonal → Elevated → Outlined → Text
4. **Align with the updated elevation model:** use M3 elevation tokens/levels for background, containers, navigation, and modal elements
5. **Plan migration:** use Material 2 and Material 3 side-by-side when needed to migrate gradually

---

## Дополнительные Вопросы (RU)

- Как технически работает извлечение динамических цветов из обоев?
- В чём плюсы и минусы стратегий миграции с M2 на M3 (постепенная vs одномоментная)?
- Как тестировать компоненты Material 3 на разных версиях Android?
- Какие улучшения по доступности предлагает Material 3 по сравнению с Material 2?
- Как поддерживать собственные цветовые схемы при использовании динамических цветов?

## Follow-ups

- How does dynamic color extraction from wallpaper work technically?
- What are the trade-offs between M2 and M3 migration strategies (gradual vs all-at-once)?
- How do you test Material 3 components across different Android versions?
- What accessibility improvements does Material 3 provide over Material 2?
- How do you handle custom color schemes while supporting dynamic colors?

## Ссылки (RU)

- Material Design 3 Guidelines: https://m3.material.io/
- Документация по Compose Material 3: https://developer.android.com/jetpack/compose/designsystems/material3

## References

- Material Design 3 Guidelines: https://m3.material.io/
- Compose Material 3 docs: https://developer.android.com/jetpack/compose/designsystems/material3

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-compose-state]]
- [[c-jetpack-compose]]

### Предпосылки
- Базовые знания Jetpack Compose
- Основы темизации в Compose

### Связанные
- Управление состоянием в Compose
- Оптимизация производительности в Compose

### Продвинутые
- Построение собственных дизайн-систем
- Доступность в Compose

## Related Questions

### Prerequisites / Concepts

- [[c-compose-state]]
- [[c-jetpack-compose]]

### Prerequisites
- Jetpack Compose basics
- Compose theming fundamentals

### Related
- State management in Compose
- Compose performance optimization

### Advanced
- Building custom design systems
- Accessibility in Compose
