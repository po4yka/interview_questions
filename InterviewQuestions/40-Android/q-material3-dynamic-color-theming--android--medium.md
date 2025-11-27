---
id: android-157
title: Material3 Dynamic Color Theming / Динамические цвета Material3
aliases: [Material3 Dynamic Color Theming, Динамические цвета Material3]
topic: android
subtopics:
  - ui-compose
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
  - c-compose-state
  - c-jetpack-compose
  - q-accessibility-color-contrast--android--medium
  - q-compose-semantics--android--medium
  - q-how-to-create-dynamic-screens-at-runtime--android--hard
  - q-material3-components--android--easy
  - q-single-activity-approach--android--medium
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android/ui-compose, android/ui-theming, design, difficulty/medium, dynamic-color, material3]
date created: Saturday, November 1st 2025, 12:46:58 pm
date modified: Tuesday, November 25th 2025, 8:53:58 pm
---
# Вопрос (RU)
> Как работает динамический цвет Material 3? Объясните генерацию цветовой схемы из обоев, реализацию пользовательских тем и обработку светлого/тёмного режимов с динамической темизацией.

# Question (EN)
> How does Material 3 dynamic color work? Explain the color scheme generation from wallpaper, implementing custom themes, and handling light/dark modes with dynamic theming.

---

## Ответ (RU)

**Динамический цвет** — ключевая особенность Material 3, позволяющая приложениям адаптировать цветовую схему на основе системной палитры Material You (как правило, сгенерированной из обоев пользователя), создавая персонализированный опыт.

### Принцип Работы

**Извлечение цвета (Android 12+)**
- Система (а не приложение) анализирует обои и извлекает ключевые цвета
- На их основе генерируется гармоничная тональная палитра (например, "тональные палитры" / Tonal Palettes)
- Формируются согласованные светлая и тёмная цветовые схемы
- Приложения получают их через `dynamicLightColorScheme()` / `dynamicDarkColorScheme()` из Material 3 библиотеки

### Базовая Реализация

```kotlin
@Composable
fun AppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        // ✅ Динамический цвет для Android 12+
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context)
            else dynamicLightColorScheme(context)
        }
        // ✅ Fallback для старых версий
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
```

### Цветовые Роли

Material 3 определяет множество семантических ролей (primary, secondary, tertiary, surface, background, error и др.):

```kotlin
val LightColorScheme = lightColorScheme(
    // Primary — ключевые действия
    primary = Color(0xFF6750A4),
    onPrimary = Color(0xFFFFFFFF),
    primaryContainer = Color(0xFFEADDFF),
    onPrimaryContainer = Color(0xFF21005D),

    // Secondary — второстепенные действия
    secondary = Color(0xFF625B71),
    onSecondary = Color(0xFFFFFFFF),

    // Surface — карты, листы
    surface = Color(0xFFFFFBFE),
    onSurface = Color(0xFF1C1B1F),
    surfaceVariant = Color(0xFFE7E0EC),

    // Error — ошибки
    error = Color(0xFFB3261E),
    onError = Color(0xFFFFFFFF)
)
```

**Использование:**

```kotlin
// ✅ Кнопка с primary цветом
Button(
    colors = ButtonDefaults.buttonColors(
        containerColor = MaterialTheme.colorScheme.primary,
        contentColor = MaterialTheme.colorScheme.onPrimary
    )
) { Text("Сохранить") }

// ❌ Жёстко заданный цвет
Button(
    colors = ButtonDefaults.buttonColors(
        containerColor = Color.Blue // Игнорирует тему и динамический цвет
    )
) { Text("Плохо") }
```

### Пользовательские Темы

**Создание собственной схемы:**

1. Используйте [Material Theme Builder](https://m3.material.io/theme-builder)
2. Загрузите обои или выберите seed color
3. Экспортируйте Kotlin код

```kotlin
// Сгенерированная схема (пример)
val CustomLightScheme = lightColorScheme(
    primary = Color(0xFF6750A4),
    onPrimary = Color(0xFFFFFFFF),
    primaryContainer = Color(0xFFEADDFF)
    // ... определите остальные роли схемы
)
```

### Управление Темой Пользователем

```kotlin
// Хранение настроек (пример; dataStore и DYNAMIC_COLOR_KEY должны быть объявлены отдельно)
class ThemePreferences(context: Context) {
    private val dataStore = context.dataStore

    val useDynamicColor: Flow<Boolean> = dataStore.data
        .map { it[DYNAMIC_COLOR_KEY] ?: true }

    suspend fun setDynamicColor(enabled: Boolean) {
        dataStore.edit { it[DYNAMIC_COLOR_KEY] = enabled }
    }
}

// UI переключателя
@Composable
fun ThemeSettings(preferences: ThemePreferences) {
    val useDynamic by preferences.useDynamicColor.collectAsState(true)
    val scope = rememberCoroutineScope()

    Row {
        Text("Динамические цвета")
        Switch(
            checked = useDynamic,
            onCheckedChange = {
                scope.launch { preferences.setDynamicColor(it) }
            }
        )
    }
}
```

### Светлая/тёмная Тема

**Автоопределение:**

```kotlin
@Composable
fun AppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(), // ✅ Авто
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context)
            else dynamicLightColorScheme(context)
        }
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }

    MaterialTheme(colorScheme = colorScheme, content = content)
}
```

**Ручное управление (пример интеграции с AppTheme):**

```kotlin
enum class ThemeMode { LIGHT, DARK, SYSTEM }

@Composable
fun App(themeMode: ThemeMode, dynamicColor: Boolean) {
    val systemDark = isSystemInDarkTheme()
    val darkTheme = when (themeMode) {
        ThemeMode.LIGHT -> false
        ThemeMode.DARK -> true
        ThemeMode.SYSTEM -> systemDark
    }

    AppTheme(darkTheme = darkTheme, dynamicColor = dynamicColor) {
        MainScreen()
    }
}
```

### Тональная Elevation

Material 3 для поверхностей использует тональное приподнятие: на приподнятых поверхностях применяется прозрачный оттенок (tint), основанный на цвете темы (например, `surfaceTint`/`primary`), вместо того чтобы полагаться только на резкие тени.

```kotlin
Card(
    elevation = CardDefaults.cardElevation(
        defaultElevation = 6.dp // ✅ Elevation добавляет тональный overlay к surface
    ),
    colors = CardDefaults.cardColors(
        containerColor = MaterialTheme.colorScheme.surface
    )
) {
    // Чем выше elevation, тем заметнее тональный overlay поверхности (в дополнение к теням)
}
```

**Примеры уровней elevation (рекомендации):**

| Уровень | dp  | Использование (пример)           |
|---------|-----|----------------------------------|
| 0       | 0dp | Фон, базовая поверхность         |
| 1       | 1dp | Карты в покое                    |
| 3       | 6dp | App bar, FAB                     |
| 4       | 8dp | Navigation drawer                |
| 5       | 12dp| Modal bottom sheet               |

### Inverse Цвета

Для высококонтрастных оверлеев (например, Snackbar на тёмном фоне):

```kotlin
Snackbar(
    containerColor = MaterialTheme.colorScheme.inverseSurface,
    contentColor = MaterialTheme.colorScheme.inverseOnSurface,
    actionColor = MaterialTheme.colorScheme.inversePrimary
) { Text("Сообщение отправлено") }
```

### Лучшие Практики

1. **Всегда предоставляйте fallback** для Android < 12
2. **Используйте семантические роли** (`MaterialTheme.colorScheme.*`), не хардкод
3. **Тестируйте** с динамическими и статическими темами
4. **Предоставляйте пользовательский контроль** (toggle для динамических цветов, если это уместно)
5. **Следуйте рекомендациям по elevation** вместо произвольных значений

---

## Answer (EN)

**Dynamic color** is a key Material 3 feature that lets apps adapt their color scheme from the system Material You palette (typically derived from the user's wallpaper), creating a personalized, cohesive experience.

### How It Works

**Wallpaper-based extraction (Android 12+)**
- The system (not the app) analyzes the wallpaper and extracts key colors
- It generates harmonious tonal palettes from those colors
- It derives consistent light and dark color schemes
- Apps consume them via `dynamicLightColorScheme()` / `dynamicDarkColorScheme()` provided by the Material 3 library

### Basic Implementation

```kotlin
@Composable
fun AppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        // ✅ Dynamic color for Android 12+
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context)
            else dynamicLightColorScheme(context)
        }
        // ✅ Fallback for older versions
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
```

### Color Roles

Material 3 defines multiple semantic color roles (primary, secondary, tertiary, surface, background, error, etc.):

```kotlin
val LightColorScheme = lightColorScheme(
    // Primary — key actions
    primary = Color(0xFF6750A4),
    onPrimary = Color(0xFFFFFFFF),
    primaryContainer = Color(0xFFEADDFF),
    onPrimaryContainer = Color(0xFF21005D),

    // Secondary — less prominent actions
    secondary = Color(0xFF625B71),
    onSecondary = Color(0xFFFFFFFF),

    // Surface — cards, sheets
    surface = Color(0xFFFFFBFE),
    onSurface = Color(0xFF1C1B1F),
    surfaceVariant = Color(0xFFE7E0EC),

    // Error — error states
    error = Color(0xFFB3261E),
    onError = Color(0xFFFFFFFF)
)
```

**Usage:**

```kotlin
// ✅ Button with primary color
Button(
    colors = ButtonDefaults.buttonColors(
        containerColor = MaterialTheme.colorScheme.primary,
        contentColor = MaterialTheme.colorScheme.onPrimary
    )
) { Text("Save") }

// ❌ Hardcoded colors
Button(
    colors = ButtonDefaults.buttonColors(
        containerColor = Color.Blue // Ignores theme and dynamic color
    )
) { Text("Bad") }
```

### Custom Themes

**Creating a custom scheme:**

1. Use [Material Theme Builder](https://m3.material.io/theme-builder)
2. Upload wallpaper or choose a seed color
3. Export Kotlin code

```kotlin
// Generated scheme (example)
val CustomLightScheme = lightColorScheme(
    primary = Color(0xFF6750A4),
    onPrimary = Color(0xFFFFFFFF),
    primaryContainer = Color(0xFFEADDFF)
    // ... define the rest of the roles
)
```

### User Control

```kotlin
// Store preference (example; dataStore and DYNAMIC_COLOR_KEY must be defined separately)
class ThemePreferences(context: Context) {
    private val dataStore = context.dataStore

    val useDynamicColor: Flow<Boolean> = dataStore.data
        .map { it[DYNAMIC_COLOR_KEY] ?: true }

    suspend fun setDynamicColor(enabled: Boolean) {
        dataStore.edit { it[DYNAMIC_COLOR_KEY] = enabled }
    }
}

// Toggle UI
@Composable
fun ThemeSettings(preferences: ThemePreferences) {
    val useDynamic by preferences.useDynamicColor.collectAsState(true)
    val scope = rememberCoroutineScope()

    Row {
        Text("Dynamic Colors")
        Switch(
            checked = useDynamic,
            onCheckedChange = {
                scope.launch { preferences.setDynamicColor(it) }
            }
        )
    }
}
```

### Light/Dark Mode

**Auto-detection:**

```kotlin
@Composable
fun AppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(), // ✅ Auto
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context)
            else dynamicLightColorScheme(context)
        }
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }

    MaterialTheme(colorScheme = colorScheme, content = content)
}
```

**Manual control (example integration with AppTheme):**

```kotlin
enum class ThemeMode { LIGHT, DARK, SYSTEM }

@Composable
fun App(themeMode: ThemeMode, dynamicColor: Boolean) {
    val systemDark = isSystemInDarkTheme()
    val darkTheme = when (themeMode) {
        ThemeMode.LIGHT -> false
        ThemeMode.DARK -> true
        ThemeMode.SYSTEM -> systemDark
    }

    AppTheme(darkTheme = darkTheme, dynamicColor = dynamicColor) {
        MainScreen()
    }
}
```

### Tonal Elevation

Material 3 uses tonal elevation for surfaces: elevated components receive a translucent tint (overlay) derived from the theme (e.g., `surfaceTint`/`primary`) on top of `surface`, rather than relying solely on sharp shadows.

```kotlin
Card(
    elevation = CardDefaults.cardElevation(
        defaultElevation = 6.dp // ✅ Elevation adds a tonal overlay to the surface
    ),
    colors = CardDefaults.cardColors(
        containerColor = MaterialTheme.colorScheme.surface
    )
) {
    // Higher elevation = more pronounced surface tint overlay (in addition to shadows)
}
```

**Elevation levels (example guidance):**

| Level | dp  | Usage (example)          |
|-------|-----|--------------------------|
| 0     | 0dp | Background, base surface |
| 1     | 1dp | Cards at rest            |
| 3     | 6dp | App bar, FAB             |
| 4     | 8dp | Navigation drawer        |
| 5     | 12dp| Modal bottom sheet       |

### Inverse Colors

For high-contrast overlays (e.g., Snackbar on dark surfaces):

```kotlin
Snackbar(
    containerColor = MaterialTheme.colorScheme.inverseSurface,
    contentColor = MaterialTheme.colorScheme.inverseOnSurface,
    actionColor = MaterialTheme.colorScheme.inversePrimary
) { Text("Message sent") }
```

### Best Practices

1. **Always provide fallback** for Android < 12
2. **Use semantic roles** (`MaterialTheme.colorScheme.*`), avoid hardcoded colors
3. **Test** with both dynamic and static themes
4. **Provide user control** (toggle for dynamic colors, when appropriate)
5. **Follow elevation guidelines** instead of arbitrary values

---

## Дополнительные Вопросы (RU)

- Как Material 3 генерирует дополнительные (secondary, tertiary) цвета из одного seed color?
- Какие аспекты доступности важно учитывать при использовании динамических цветов, зависящих от обоев пользователя?
- Как реализовать плавные переходы темы при изменении динамических цветов (например, при смене обоев)?
- Каков эффект динамической темизации на производительность и что важно учесть на более старых устройствах?
- Как обрабатывать случаи, когда палитра обоев даёт недостаточный контраст цветов?

## Follow-ups

- How does Material 3 generate complementary colors (secondary, tertiary) from a single seed color?
- What accessibility considerations exist when using dynamic colors with user wallpapers?
- How can you create smooth theme transitions when dynamic color changes (e.g., wallpaper update)?
- What's the performance impact of dynamic color extraction on older devices?
- How do you handle edge cases where wallpaper has insufficient color contrast?

## Ссылки (RU)

- [Material Design 3 - Dynamic Color](https://m3.material.io/styles/color/dynamic-color/overview)
- [Material Theme Builder](https://m3.material.io/theme-builder)

## References

- [Material Design 3 - Dynamic Color](https://m3.material.io/styles/color/dynamic-color/overview)
- [Material Theme Builder](https://m3.material.io/theme-builder)

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-compose-state]]
- [[c-jetpack-compose]]

### Предпосылки

- [[q-single-activity-approach--android--medium]] — Архитектура приложения для настройки темизации

### Похожие Вопросы

- [[q-compose-semantics--android--medium]] — Доступность при использовании динамических тем

### Продвинутое

- [[q-why-was-the-lifecycle-library-created--android--hard]] — Подходы к lifecycle-aware темизации

## Related Questions

### Prerequisites / Concepts

- [[c-compose-state]]
- [[c-jetpack-compose]]


### Prerequisites
- [[q-single-activity-approach--android--medium]] — App architecture for theming

### Related
- [[q-compose-semantics--android--medium]] — Accessibility with dynamic themes

### Advanced
- [[q-why-was-the-lifecycle-library-created--android--hard]] — Lifecycle-aware theming
