---
id: 20251012-122711
title: "Material3 Dynamic Color Theming / Динамические цвета Material3"
aliases: ["Material3 Dynamic Color Theming", "Динамические цвета Material3"]
topic: android
subtopics: [ui-compose, ui-theming]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-single-activity-approach--android--medium, q-compose-semantics--android--medium]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [android/ui-compose, android/ui-theming, design, material3, dynamic-color, difficulty/medium]
---
# Вопрос (RU)
> Как работает динамический цвет Material 3? Объясните генерацию цветовой схемы из обоев, реализацию пользовательских тем и обработку светлого/тёмного режимов с динамической темизацией.

# Question (EN)
> How does Material 3 dynamic color work? Explain the color scheme generation from wallpaper, implementing custom themes, and handling light/dark modes with dynamic theming.

---

## Ответ (RU)

**Динамический цвет** — ключевая особенность Material 3, позволяющая приложениям адаптировать цветовую схему на основе обоев пользователя, создавая персонализированный опыт.

### Принцип работы

**Извлечение цвета (Android 12+)**
- Система анализирует обои и извлекает доминирующие цвета
- Генерирует гармоничную тональную палитру (TonalPalette)
- Создаёт светлую и тёмную схемы
- Предоставляет через `dynamicLightColorScheme()` / `dynamicDarkColorScheme()`

### Базовая реализация

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

### Цветовые роли

Material 3 определяет 25+ семантических ролей:

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

// ❌ Хардкод цветов
Button(colors = ButtonDefaults.buttonColors(
    containerColor = Color.Blue // Игнорирует тему
)) { Text("Плохо") }
```

### Пользовательские темы

**Создание собственной схемы:**

1. Используйте [Material Theme Builder](https://m3.material.io/theme-builder)
2. Загрузите обои или выберите seed color
3. Экспортируйте Kotlin код

```kotlin
// Сгенерированная схема
val CustomLightScheme = lightColorScheme(
    primary = Color(0xFF6750A4),
    onPrimary = Color(0xFFFFFFFF),
    primaryContainer = Color(0xFFEADDFF)
    // ... остальные 22 роли
)
```

### Управление темой пользователем

```kotlin
// Хранение настроек
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

### Светлая/тёмная тема

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

**Ручное управление:**

```kotlin
enum class ThemeMode { LIGHT, DARK, SYSTEM }

@Composable
fun App(themeMode: ThemeMode) {
    val systemDark = isSystemInDarkTheme()
    val darkTheme = when (themeMode) {
        ThemeMode.LIGHT -> false
        ThemeMode.DARK -> true
        ThemeMode.SYSTEM -> systemDark
    }

    AppTheme(darkTheme = darkTheme) { MainScreen() }
}
```

### Тональная elevation

Material 3 использует цветовую tint вместо теней:

```kotlin
Card(
    elevation = CardDefaults.cardElevation(
        defaultElevation = 6.dp // ✅ Elevation применяет tint
    ),
    colors = CardDefaults.cardColors(
        containerColor = MaterialTheme.colorScheme.surface
    )
) {
    // Чем выше elevation, тем больше surface tint overlay
}
```

**Уровни elevation:**

| Уровень | dp | Использование |
|---------|-----|---------------|
| 0 | 0dp | Фон, базовая поверхность |
| 1 | 1dp | Карты в покое |
| 3 | 6dp | App bar, FAB |
| 4 | 8dp | Navigation drawer |
| 5 | 12dp | Modal bottom sheet |

### Inverse цвета

Для высококонтрастных оверлеев (Snackbar):

```kotlin
Snackbar(
    containerColor = MaterialTheme.colorScheme.inverseSurface,
    contentColor = MaterialTheme.colorScheme.inverseOnSurface,
    actionColor = MaterialTheme.colorScheme.inversePrimary
) { Text("Сообщение отправлено") }
```

### Лучшие практики

1. **Всегда предоставляйте fallback** для Android < 12
2. **Используйте семантические роли** (`MaterialTheme.colorScheme.*`), не хардкод
3. **Тестируйте** с динамическими и статическими темами
4. **Предоставляйте пользовательский контроль** (toggle для динамических цветов)
5. **Следуйте elevation guidelines** (не используйте произвольные значения)

---

## Answer (EN)

**Dynamic color** is Material 3's signature feature, allowing apps to adapt their color scheme from the user's wallpaper, creating a personalized, cohesive experience.

### How It Works

**Wallpaper Analysis (Android 12+)**
- System extracts dominant colors from wallpaper
- Generates harmonious tonal palette (TonalPalette)
- Creates light and dark color schemes
- Exposes via `dynamicLightColorScheme()` / `dynamicDarkColorScheme()`

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

Material 3 defines 25+ semantic roles:

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
Button(colors = ButtonDefaults.buttonColors(
    containerColor = Color.Blue // Ignores theme
)) { Text("Bad") }
```

### Custom Themes

**Creating custom scheme:**

1. Use [Material Theme Builder](https://m3.material.io/theme-builder)
2. Upload wallpaper or choose seed color
3. Export Kotlin code

```kotlin
// Generated scheme
val CustomLightScheme = lightColorScheme(
    primary = Color(0xFF6750A4),
    onPrimary = Color(0xFFFFFFFF),
    primaryContainer = Color(0xFFEADDFF)
    // ... remaining 22 roles
)
```

### User Control

```kotlin
// Store preference
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

**Manual control:**

```kotlin
enum class ThemeMode { LIGHT, DARK, SYSTEM }

@Composable
fun App(themeMode: ThemeMode) {
    val systemDark = isSystemInDarkTheme()
    val darkTheme = when (themeMode) {
        ThemeMode.LIGHT -> false
        ThemeMode.DARK -> true
        ThemeMode.SYSTEM -> systemDark
    }

    AppTheme(darkTheme = darkTheme) { MainScreen() }
}
```

### Tonal Elevation

Material 3 uses color tint instead of shadows:

```kotlin
Card(
    elevation = CardDefaults.cardElevation(
        defaultElevation = 6.dp // ✅ Elevation applies tint
    ),
    colors = CardDefaults.cardColors(
        containerColor = MaterialTheme.colorScheme.surface
    )
) {
    // Higher elevation = more surface tint overlay
}
```

**Elevation levels:**

| Level | dp | Usage |
|-------|-----|-------|
| 0 | 0dp | Background, base surface |
| 1 | 1dp | Cards at rest |
| 3 | 6dp | App bar, FAB |
| 4 | 8dp | Navigation drawer |
| 5 | 12dp | Modal bottom sheet |

### Inverse Colors

For high-contrast overlays (Snackbar):

```kotlin
Snackbar(
    containerColor = MaterialTheme.colorScheme.inverseSurface,
    contentColor = MaterialTheme.colorScheme.inverseOnSurface,
    actionColor = MaterialTheme.colorScheme.inversePrimary
) { Text("Message sent") }
```

### Best Practices

1. **Always provide fallback** for Android < 12
2. **Use semantic roles** (`MaterialTheme.colorScheme.*`), not hardcoded colors
3. **Test** with both dynamic and static themes
4. **Provide user control** (toggle for dynamic colors)
5. **Follow elevation guidelines** (avoid arbitrary values)

---

## Follow-ups

- How does Material 3 generate complementary colors (secondary, tertiary) from a single seed color?
- What accessibility considerations exist when using dynamic colors with user wallpapers?
- How can you create smooth theme transitions when dynamic color changes (e.g., wallpaper update)?
- What's the performance impact of dynamic color extraction on older devices?
- How do you handle edge cases where wallpaper has insufficient color contrast?

## References

- [Material Design 3 - Dynamic Color](https://m3.material.io/styles/color/dynamic-color/overview)
- [Material Theme Builder](https://m3.material.io/theme-builder)

## Related Questions

### Prerequisites
- [[q-single-activity-approach--android--medium]] — App architecture for theming

### Related
- [[q-compose-semantics--android--medium]] — Accessibility with dynamic themes

### Advanced
- [[q-why-was-the-lifecycle-library-created--android--hard]] — Lifecycle-aware theming
