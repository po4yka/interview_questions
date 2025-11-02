---
id: android-078
title: "Material3 Components / Компоненты Material3"
aliases: ["Material3 Components", "Компоненты Material3"]
topic: android
subtopics: [ui-compose, ui-theming]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: []
created: 2025-10-13
updated: 2025-01-27
tags: [android, android/ui-compose, android/ui-theming, design-system, difficulty/easy, material3]
sources: []
date created: Monday, October 27th 2025, 3:43:58 pm
date modified: Saturday, November 1st 2025, 5:43:29 pm
---

# Вопрос (RU)
> Каковы ключевые различия между Material 2 и Material 3? Перечислите основные компоненты Material 3. Как мигрировать с Material 2 на Material 3?

# Question (EN)
> What are the key differences between Material 2 and Material 3? List the main Material 3 components and their use cases. How do you migrate from Material 2 to Material 3?

---

## Ответ (RU)

**Material 3** (Material You) — дизайн-система Google с персонализацией, динамическими цветами и современными компонентами.

### Ключевые Различия: Material 2 Vs Material 3

| Функция | Material 2 | Material 3 |
|---------|------------|------------|
| **Цвета** | Фиксированная палитра | Динамическая система (25+ ролей) |
| **Персонализация** | Статические темы | Темы из обоев пользователя |
| **Elevation** | На основе теней | Тональные поверхности |

### Основные Компоненты Material 3

**1. Кнопки:**
```kotlin
// ✅ Filled — основное действие
Button(onClick = {}) { Text("Save") }

// ✅ FilledTonalButton — вторичное действие
FilledTonalButton(onClick = {}) { Text("Cancel") }

// ❌ Не используйте Filled для всех кнопок
```

**2. Навигация:**
- `NavigationBar` — нижняя навигация (было `BottomNavigation`)
- `NavigationRail` — боковая навигация
- `ModalNavigationDrawer` — выдвижное меню

**3. App Bar:**
- `TopAppBar` — обычный
- `MediumTopAppBar` — средний с прокруткой
- `LargeTopAppBar` — большой

**4. Карточки:**
```kotlin
// ✅ Используйте семантические цвета
Card(
    colors = CardDefaults.cardColors(
        containerColor = MaterialTheme.colorScheme.surfaceVariant // ✅
    )
)

// ❌ Не хардкодьте цвета
Card(colors = CardDefaults.cardColors(containerColor = Color(0xFFE8DEF8)))
```

**5. Chips:**
- `AssistChip` — действия
- `FilterChip` — фильтры
- `InputChip` — ввод пользователя
- `SuggestionChip` — предложения

### Миграция С Material 2 На Material 3

**1. Обновить зависимости:**
```gradle
implementation "androidx.compose.material3:material3" // без версии
```

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

**5. Исправить breaking changes:**
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
        else -> lightColorScheme() // ❌ Fallback
    }
    MaterialTheme(colorScheme = colorScheme, content = content)
}
```

### Best Practices

1. **Используйте семантические цветовые роли** (`primary`, `surfaceVariant`) вместо хардкода
2. **Включайте динамические цвета** на Android 12+
3. **Соблюдайте иерархию кнопок:** Filled → Tonal → Outlined → Text
4. **Следуйте elevation:** Level 0 (фон) → Level 5 (модальные окна)

---

## Answer (EN)

**Material 3** (Material You) is Google's design system with personalization, dynamic colors, and modern components.

### Key Differences: Material 2 Vs Material 3

| Feature | Material 2 | Material 3 |
|---------|------------|------------|
| **Colors** | Fixed palette | Dynamic system (25+ roles) |
| **Personalization** | Static themes | Themes from user wallpaper |
| **Elevation** | Shadow-based | Tonal surfaces |

### Main Material 3 Components

**1. Buttons:**
```kotlin
// ✅ Filled — primary action
Button(onClick = {}) { Text("Save") }

// ✅ FilledTonalButton — secondary action
FilledTonalButton(onClick = {}) { Text("Cancel") }

// ❌ Don't use Filled for all buttons
```

**2. Navigation:**
- `NavigationBar` — bottom navigation (was `BottomNavigation`)
- `NavigationRail` — side navigation
- `ModalNavigationDrawer` — drawer menu

**3. App Bar:**
- `TopAppBar` — standard
- `MediumTopAppBar` — medium with scroll
- `LargeTopAppBar` — large

**4. Cards:**
```kotlin
// ✅ Use semantic colors
Card(
    colors = CardDefaults.cardColors(
        containerColor = MaterialTheme.colorScheme.surfaceVariant // ✅
    )
)

// ❌ Don't hardcode colors
Card(colors = CardDefaults.cardColors(containerColor = Color(0xFFE8DEF8)))
```

**5. Chips:**
- `AssistChip` — actions
- `FilterChip` — filters
- `InputChip` — user input
- `SuggestionChip` — suggestions

### Migration from Material 2 to Material 3

**1. Update dependencies:**
```gradle
implementation "androidx.compose.material3:material3" // no version
```

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
        else -> lightColorScheme() // ❌ Fallback
    }
    MaterialTheme(colorScheme = colorScheme, content = content)
}
```

### Best Practices

1. **Use semantic color roles** (`primary`, `surfaceVariant`) instead of hardcoding
2. **Enable dynamic colors** on Android 12+
3. **Follow button hierarchy:** Filled → Tonal → Outlined → Text
4. **Follow elevation:** Level 0 (background) → Level 5 (modal)

---

## Follow-ups

- How does dynamic color extraction from wallpaper work technically?
- What are the trade-offs between M2 and M3 migration strategies (gradual vs all-at-once)?
- How do you test Material 3 components across different Android versions?
- What accessibility improvements does Material 3 provide over Material 2?
- How do you handle custom color schemes while supporting dynamic colors?

## References

- Material Design 3 Guidelines: https://m3.material.io/
- Compose Material 3 docs: https://developer.android.com/jetpack/compose/designsystems/material3

## Related Questions

### Prerequisites
- Jetpack Compose basics
- Compose theming fundamentals

### Related
- State management in Compose
- Compose performance optimization

### Advanced
- Building custom design systems
- Accessibility in Compose
