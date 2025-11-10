---
id: android-078
title: Material3 Components / Компоненты Material3
aliases:
- Material3 Components
- Компоненты Material3
topic: android
subtopics:
- ui-compose
- ui-theming
question_kind: theory
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-compose-state
- c-jetpack-compose
created: 2025-10-13
updated: 2025-11-10
tags:
- android
- android/ui-compose
- android/ui-theming
- design-system
- difficulty/easy
- material3
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
| **Цвета** | Фиксированная палитра | Динамическая система (25+ ролей) |
| **Персонализация** | Статические темы | Темы из обоев пользователя |
| **Elevation** | На основе теней | Тональные поверхности + обновлённые elevation-токены |

### Основные Компоненты Material 3

**1. Кнопки (основные варианты):**
```kotlin
// ✅ Filled — основное действие
Button(onClick = {}) { Text("Save") }

// ✅ FilledTonalButton — вторичное действие
FilledTonalButton(onClick = {}) { Text("Cancel") }

// ✅ OutlinedButton — второстепенные / менее заметные действия
OutlinedButton(onClick = {}) { Text("Secondary") }

// ✅ TextButton — контекстные/микро-действия без акцента
TextButton(onClick = {}) { Text("More") }

// ✅ ElevatedButton — акцент при необходимости отделить от фона
ElevatedButton(onClick = {}) { Text("Action") }

// ❌ Не используйте Filled для всех кнопок
```

**2. Навигация:**
- `NavigationBar` — нижняя навигация (ранее `BottomNavigation`)
- `NavigationBarItem` — элементы нижней навигации
- `NavigationRail` — боковая навигация для больших экранов
- `ModalNavigationDrawer` — выдвижное меню

**3. App Bar:**
- `TopAppBar` — стандартный
- `MediumTopAppBar` — средний с прокруткой
- `LargeTopAppBar` — большой

**4. Карточки:**
```kotlin
// ✅ Используйте семантические цвета
Card(
    colors = CardDefaults.cardColors(
        containerColor = MaterialTheme.colorScheme.surfaceVariant // ✅
    ),
    elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
)

// ❌ Не хардкодьте цвета
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

**2. Обновить theme:**
```kotlin
// До: Material 2
MaterialTheme(colors = lightColors())

// После: Material 3
MaterialTheme(colorScheme = lightColorScheme())
```

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
    val colorScheme = when {
        Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            dynamicLightColorScheme(LocalContext.current) // ✅ Из обоев
        }
        else -> lightColorScheme() // ✅ Корректный fallback для старых устройств
    }
    MaterialTheme(colorScheme = colorScheme, content = content)
}
```

### Best Practices

1. **Используйте семантические цветовые роли** (`primary`, `surfaceVariant`) вместо хардкода
2. **Включайте динамические цвета** на Android 12+, с корректным fallback для более старых версий
3. **Соблюдайте иерархию кнопок:** Filled → FilledTonal → Elevated → Outlined → Text
4. **Учитывайте обновлённую модель elevation:** уровни для фона, контейнеров, навигации и модальных элементов, опираясь на токены M3

---

## Answer (EN)

**Material 3** (Material You) is Google's design system with personalization, dynamic colors, and modern components.

### Key Differences: Material 2 Vs Material 3

| Feature | Material 2 | Material 3 |
|---------|------------|------------|
| **Colors** | Fixed palette | Dynamic system (25+ roles) |
| **Personalization** | Static themes | Themes from user wallpaper |
| **Elevation** | Shadow-based | Tonal surfaces + updated elevation tokens |

### Main Material 3 Components

**1. Buttons (core variants):**
```kotlin
// ✅ Filled — primary action
Button(onClick = {}) { Text("Save") }

// ✅ FilledTonalButton — secondary / alternative primary
FilledTonalButton(onClick = {}) { Text("Cancel") }

// ✅ OutlinedButton — less prominent secondary actions
OutlinedButton(onClick = {}) { Text("Secondary") }

// ✅ TextButton — inline / contextual actions
TextButton(onClick = {}) { Text("More") }

// ✅ ElevatedButton — when emphasis is needed against the background
ElevatedButton(onClick = {}) { Text("Action") }

// ❌ Don't use Filled for all buttons
```

**2. Navigation:**
- `NavigationBar` — bottom navigation (previously `BottomNavigation`)
- `NavigationBarItem` — bottom navigation items
- `NavigationRail` — side navigation for larger screens
- `ModalNavigationDrawer` — drawer menu

**3. App Bar:**
- `TopAppBar` — standard
- `MediumTopAppBar` — medium with scroll behavior
- `LargeTopAppBar` — large

**4. Cards:**
```kotlin
// ✅ Use semantic colors
Card(
    colors = CardDefaults.cardColors(
        containerColor = MaterialTheme.colorScheme.surfaceVariant // ✅
    ),
    elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
)

// ❌ Don't hardcode colors
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

**2. Update theme:**
```kotlin
// Before: Material 2
MaterialTheme(colors = lightColors())

// After: Material 3
MaterialTheme(colorScheme = lightColorScheme())
```

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
    val colorScheme = when {
        Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            dynamicLightColorScheme(LocalContext.current) // ✅ From wallpaper
        }
        else -> lightColorScheme() // ✅ Correct fallback when dynamic color is unavailable
    }
    MaterialTheme(colorScheme = colorScheme, content = content)
}
```

### Best Practices

1. **Use semantic color roles** (`primary`, `surfaceVariant`) instead of hardcoding
2. **Enable dynamic colors** on Android 12+ with a proper fallback on lower versions
3. **Follow button hierarchy:** Filled → FilledTonal → Elevated → Outlined → Text
4. **Align with the updated elevation model:** use appropriate levels/tokens for background, containers, navigation, and modal elements

---

## Дополнительные вопросы (RU)

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

## Связанные вопросы (RU)

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
