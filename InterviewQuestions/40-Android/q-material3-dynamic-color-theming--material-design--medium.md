---
tags:
  - material-design
  - material3
  - theming
  - dynamic-color
difficulty: medium
status: draft
---

# Material 3 Dynamic Color and Theming

# Question (EN)
> How does Material 3 dynamic color work? Explain the color scheme generation from wallpaper, implementing custom themes, and handling light/dark modes with dynamic theming.

# Вопрос (RU)
> Как работает динамический цвет Material 3? Объясните генерацию цветовой схемы из обоев, реализацию пользовательских тем и обработку светлого/тёмного режимов с динамической темизацией.

---

## Answer (EN)

**Dynamic color** is Material 3's most distinctive feature, allowing apps to adapt their color scheme from the user's wallpaper. This creates a personalized, cohesive experience across the system and apps.

### How Dynamic Color Works

**1. Wallpaper Analysis (Android 12+)**
- System extracts dominant colors from wallpaper
- Generates harmonious color palette (TonalPalette)
- Creates light and dark color schemes
- Exposes schemes to apps via `dynamicLightColorScheme()` and `dynamicDarkColorScheme()`

```
User Wallpaper → Color Extraction → Tonal Palette → Light/Dark Schemes → App Theme
```

---

### Implementing Dynamic Color

**Basic implementation:**

```kotlin
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalContext
import android.os.Build

@Composable
fun AppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true, // Enable dynamic color
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        // Dynamic color available on Android 12+
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context)
            else dynamicLightColorScheme(context)
        }

        // Dark theme
        darkTheme -> DarkColorScheme

        // Light theme
        else -> LightColorScheme
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        shapes = Shapes,
        content = content
    )
}
```

---

### Color Scheme Structure

**Material 3 has 25+ semantic color roles:**

```kotlin
val LightColorScheme = lightColorScheme(
    // Primary colors (key actions, buttons)
    primary = Color(0xFF6750A4),
    onPrimary = Color(0xFFFFFFFF),
    primaryContainer = Color(0xFFEADDFF),
    onPrimaryContainer = Color(0xFF21005D),

    // Secondary colors (less prominent actions)
    secondary = Color(0xFF625B71),
    onSecondary = Color(0xFFFFFFFF),
    secondaryContainer = Color(0xFFE8DEF8),
    onSecondaryContainer = Color(0xFF1D192B),

    // Tertiary colors (accents, complementary)
    tertiary = Color(0xFF7D5260),
    onTertiary = Color(0xFFFFFFFF),
    tertiaryContainer = Color(0xFFFFD8E4),
    onTertiaryContainer = Color(0xFF31111D),

    // Error colors
    error = Color(0xFFB3261E),
    onError = Color(0xFFFFFFFF),
    errorContainer = Color(0xFFF9DEDC),
    onErrorContainer = Color(0xFF410E0B),

    // Surface colors (cards, sheets)
    surface = Color(0xFFFFFBFE),
    onSurface = Color(0xFF1C1B1F),
    surfaceVariant = Color(0xFFE7E0EC),
    onSurfaceVariant = Color(0xFF49454F),

    // Background
    background = Color(0xFFFFFBFE),
    onBackground = Color(0xFF1C1B1F),

    // Outlines
    outline = Color(0xFF79747E),
    outlineVariant = Color(0xFFCAC4D0),

    // Inverse colors (for snackbars, etc.)
    inverseSurface = Color(0xFF313033),
    inverseOnSurface = Color(0xFFF4EFF4),
    inversePrimary = Color(0xFFD0BCFF),

    // Scrim (overlays)
    scrim = Color(0xFF000000),

    // Surface tints
    surfaceTint = Color(0xFF6750A4)
)

val DarkColorScheme = darkColorScheme(
    primary = Color(0xFFD0BCFF),
    onPrimary = Color(0xFF381E72),
    primaryContainer = Color(0xFF4F378B),
    onPrimaryContainer = Color(0xFFEADDFF),

    secondary = Color(0xFFCCC2DC),
    onSecondary = Color(0xFF332D41),
    secondaryContainer = Color(0xFF4A4458),
    onSecondaryContainer = Color(0xFFE8DEF8),

    tertiary = Color(0xFFEFB8C8),
    onTertiary = Color(0xFF492532),
    tertiaryContainer = Color(0xFF633B48),
    onTertiaryContainer = Color(0xFFFFD8E4),

    error = Color(0xFFF2B8B5),
    onError = Color(0xFF601410),
    errorContainer = Color(0xFF8C1D18),
    onErrorContainer = Color(0xFFF9DEDC),

    surface = Color(0xFF1C1B1F),
    onSurface = Color(0xFFE6E1E5),
    surfaceVariant = Color(0xFF49454F),
    onSurfaceVariant = Color(0xFFCAC4D0),

    background = Color(0xFF1C1B1F),
    onBackground = Color(0xFFE6E1E5),

    outline = Color(0xFF938F99),
    outlineVariant = Color(0xFF49454F),

    inverseSurface = Color(0xFFE6E1E5),
    inverseOnSurface = Color(0xFF313033),
    inversePrimary = Color(0xFF6750A4),

    scrim = Color(0xFF000000),
    surfaceTint = Color(0xFFD0BCFF)
)
```

---

### Color Role Usage Guide

**Primary colors:**
```kotlin
// Primary - key actions, emphasized buttons
Button(
    colors = ButtonDefaults.buttonColors(
        containerColor = MaterialTheme.colorScheme.primary,
        contentColor = MaterialTheme.colorScheme.onPrimary
    )
) {
    Text("Save")
}

// Primary Container - less prominent primary
FilledTonalButton(
    colors = ButtonDefaults.filledTonalButtonColors(
        containerColor = MaterialTheme.colorScheme.primaryContainer,
        contentColor = MaterialTheme.colorScheme.onPrimaryContainer
    )
) {
    Text("Edit")
}
```

**Surface colors:**
```kotlin
// Surface - cards, sheets
Card(
    colors = CardDefaults.cardColors(
        containerColor = MaterialTheme.colorScheme.surface,
        contentColor = MaterialTheme.colorScheme.onSurface
    )
) {
    Text("Card content")
}

// Surface Variant - subtle differentiation
Card(
    colors = CardDefaults.cardColors(
        containerColor = MaterialTheme.colorScheme.surfaceVariant,
        contentColor = MaterialTheme.colorScheme.onSurfaceVariant
    )
) {
    Text("Variant card")
}
```

---

### Generating Custom Color Schemes

**Using Material Theme Builder:**

1. Visit [Material Theme Builder](https://m3.material.io/theme-builder)
2. Upload wallpaper or choose source color
3. Customize primary, secondary, tertiary colors
4. Export as Kotlin code

**Generated theme example:**

```kotlin
// Generated from Material Theme Builder
val md_theme_light_primary = Color(0xFF6750A4)
val md_theme_light_onPrimary = Color(0xFFFFFFFF)
val md_theme_light_primaryContainer = Color(0xFFEADDFF)
val md_theme_light_onPrimaryContainer = Color(0xFF21005D)
// ... all 25+ colors

val LightColorScheme = lightColorScheme(
    primary = md_theme_light_primary,
    onPrimary = md_theme_light_onPrimary,
    primaryContainer = md_theme_light_primaryContainer,
    onPrimaryContainer = md_theme_light_onPrimaryContainer,
    // ... map all colors
)
```

---

### User Preference for Dynamic Color

**Allow users to toggle dynamic color:**

```kotlin
// Store preference
class ThemePreferences(private val context: Context) {
    private val dataStore = context.dataStore

    val useDynamicColor: Flow<Boolean> = dataStore.data
        .map { preferences ->
            preferences[DYNAMIC_COLOR_KEY] ?: true
        }

    suspend fun setDynamicColor(enabled: Boolean) {
        dataStore.edit { preferences ->
            preferences[DYNAMIC_COLOR_KEY] = enabled
        }
    }

    companion object {
        private val DYNAMIC_COLOR_KEY = booleanPreferencesKey("use_dynamic_color")
    }
}

// Use in composable
@Composable
fun App() {
    val themePreferences = remember { ThemePreferences(LocalContext.current) }
    val useDynamicColor by themePreferences.useDynamicColor.collectAsState(true)

    AppTheme(
        dynamicColor = useDynamicColor
    ) {
        MainScreen()
    }
}

// Settings screen
@Composable
fun SettingsScreen(themePreferences: ThemePreferences) {
    val useDynamicColor by themePreferences.useDynamicColor.collectAsState(true)
    val scope = rememberCoroutineScope()

    Column {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text("Dynamic Colors")
            Switch(
                checked = useDynamicColor,
                onCheckedChange = { enabled ->
                    scope.launch {
                        themePreferences.setDynamicColor(enabled)
                    }
                }
            )
        }

        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.S) {
            Text(
                "Dynamic colors require Android 12+",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}
```

---

### Dark Mode Handling

**Automatic dark mode detection:**

```kotlin
@Composable
fun AppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(), // Auto-detect
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

    MaterialTheme(
        colorScheme = colorScheme,
        content = content
    )
}
```

**Manual dark mode control:**

```kotlin
enum class ThemeMode {
    LIGHT, DARK, SYSTEM
}

class ThemeViewModel : ViewModel() {
    private val _themeMode = MutableStateFlow(ThemeMode.SYSTEM)
    val themeMode: StateFlow<ThemeMode> = _themeMode.asStateFlow()

    fun setThemeMode(mode: ThemeMode) {
        _themeMode.value = mode
    }
}

@Composable
fun App(viewModel: ThemeViewModel = viewModel()) {
    val themeMode by viewModel.themeMode.collectAsState()
    val systemDarkTheme = isSystemInDarkTheme()

    val darkTheme = when (themeMode) {
        ThemeMode.LIGHT -> false
        ThemeMode.DARK -> true
        ThemeMode.SYSTEM -> systemDarkTheme
    }

    AppTheme(darkTheme = darkTheme) {
        MainScreen()
    }
}
```

---

### Tonal Elevation (Surface Tints)

Material 3 uses **tonal elevation** instead of shadows.

```kotlin
Card(
    elevation = CardDefaults.cardElevation(
        defaultElevation = 6.dp // Elevation level
    ),
    colors = CardDefaults.cardColors(
        containerColor = MaterialTheme.colorScheme.surface
    )
) {
    // Higher elevation = more surface tint overlay
    // Creates subtle color change instead of shadow
}
```

**Elevation levels:**

| Level | dp | Usage |
|-------|-----|-------|
| **0** | 0dp | Background, base surface |
| **1** | 1dp | Cards at rest |
| **2** | 3dp | Cards on hover |
| **3** | 6dp | App bars, FAB at rest |
| **4** | 8dp | Navigation drawer |
| **5** | 12dp | Modal bottom sheets |

**Surface with custom tint:**
```kotlin
Surface(
    tonalElevation = 3.dp,
    color = MaterialTheme.colorScheme.surface,
    contentColor = MaterialTheme.colorScheme.onSurface
) {
    // Content will have subtle tint based on surfaceTint color
}
```

---

### Inverse Colors (Snackbars)

**Inverse colors** for high-contrast overlays:

```kotlin
Snackbar(
    containerColor = MaterialTheme.colorScheme.inverseSurface,
    contentColor = MaterialTheme.colorScheme.inverseOnSurface,
    actionColor = MaterialTheme.colorScheme.inversePrimary
) {
    Text("Message sent")
}
```

---

### Real-World Example: Complete Theme System

```kotlin
// Theme.kt
enum class ThemeMode { LIGHT, DARK, SYSTEM }
enum class ColorMode { DYNAMIC, STATIC }

data class ThemeConfig(
    val themeMode: ThemeMode = ThemeMode.SYSTEM,
    val colorMode: ColorMode = ColorMode.DYNAMIC
)

@Composable
fun AppTheme(
    config: ThemeConfig = ThemeConfig(),
    content: @Composable () -> Unit
) {
    val systemDarkTheme = isSystemInDarkTheme()

    val darkTheme = when (config.themeMode) {
        ThemeMode.LIGHT -> false
        ThemeMode.DARK -> true
        ThemeMode.SYSTEM -> systemDarkTheme
    }

    val dynamicColor = config.colorMode == ColorMode.DYNAMIC &&
            Build.VERSION.SDK_INT >= Build.VERSION_CODES.S

    val colorScheme = when {
        dynamicColor -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context)
            else dynamicLightColorScheme(context)
        }

        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        shapes = Shapes,
        content = content
    )
}

// Usage
@Composable
fun App() {
    val viewModel: ThemeViewModel = viewModel()
    val config by viewModel.themeConfig.collectAsState()

    AppTheme(config = config) {
        MainScreen()
    }
}
```

**Theme Settings Screen:**

```kotlin
@Composable
fun ThemeSettingsScreen(viewModel: ThemeViewModel) {
    val config by viewModel.themeConfig.collectAsState()

    Column(modifier = Modifier.padding(16.dp)) {
        // Theme mode
        Text("Theme", style = MaterialTheme.typography.titleMedium)

        ThemeModeOption(
            label = "Light",
            selected = config.themeMode == ThemeMode.LIGHT,
            onClick = { viewModel.setThemeMode(ThemeMode.LIGHT) }
        )

        ThemeModeOption(
            label = "Dark",
            selected = config.themeMode == ThemeMode.DARK,
            onClick = { viewModel.setThemeMode(ThemeMode.DARK) }
        )

        ThemeModeOption(
            label = "System Default",
            selected = config.themeMode == ThemeMode.SYSTEM,
            onClick = { viewModel.setThemeMode(ThemeMode.SYSTEM) }
        )

        Spacer(modifier = Modifier.height(24.dp))

        // Dynamic color
        Text("Colors", style = MaterialTheme.typography.titleMedium)

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("Dynamic Colors")
                Switch(
                    checked = config.colorMode == ColorMode.DYNAMIC,
                    onCheckedChange = { enabled ->
                        viewModel.setColorMode(
                            if (enabled) ColorMode.DYNAMIC else ColorMode.STATIC
                        )
                    }
                )
            }
        } else {
            Text(
                "Dynamic colors require Android 12+",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
fun ThemeModeOption(
    label: String,
    selected: Boolean,
    onClick: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .padding(vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        RadioButton(
            selected = selected,
            onClick = onClick
        )
        Spacer(modifier = Modifier.width(16.dp))
        Text(label)
    }
}
```

---

### Testing Dynamic Color

**Preview with different schemes:**

```kotlin
@Preview(name = "Light Dynamic", showBackground = true)
@Preview(name = "Dark Dynamic", showBackground = true, uiMode = Configuration.UI_MODE_NIGHT_YES)
@Composable
fun ThemePreview() {
    AppTheme {
        Surface {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Primary", color = MaterialTheme.colorScheme.primary)
                Text("Secondary", color = MaterialTheme.colorScheme.secondary)
                Text("Tertiary", color = MaterialTheme.colorScheme.tertiary)

                Button(onClick = {}) {
                    Text("Button")
                }

                Card {
                    Text("Card", modifier = Modifier.padding(16.dp))
                }
            }
        }
    }
}
```

---

### Best Practices

**1. Always provide fallback for Android < 12**
```kotlin
val colorScheme = when {
    dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
        dynamicLightColorScheme(context)
    }
    else -> LightColorScheme //  Fallback
}
```

**2. Use semantic color roles**
```kotlin
//  DO
Text(color = MaterialTheme.colorScheme.onSurface)

//  DON'T
Text(color = Color.Black)
```

**3. Test with both static and dynamic themes**

**4. Provide user control**
```kotlin
// Let users disable dynamic color if they prefer static
```

**5. Follow tonal elevation guidelines**
```kotlin
// Use appropriate elevation for components
Card(elevation = CardDefaults.cardElevation(defaultElevation = 1.dp))
```

---

### Summary

**Dynamic color benefits:**
- Personalized user experience
- System-wide visual coherence
- Automatic light/dark support
- Accessibility improvements

**Implementation:**
1. Use `dynamicLightColorScheme()` / `dynamicDarkColorScheme()`
2. Provide fallback for Android < 12
3. Define custom light/dark schemes
4. Allow user to toggle dynamic color

**Color scheme:**
- 25+ semantic color roles
- Primary, Secondary, Tertiary families
- Surface variations
- Inverse colors for overlays

**Best practices:**
- Always use semantic roles
- Test with dynamic and static themes
- Provide user control
- Follow elevation guidelines
- Support light and dark modes

---

## Ответ (RU)

**Динамический цвет** - самая отличительная особенность Material 3, позволяющая приложениям адаптировать свою цветовую схему из обоев пользователя.

### Как работает динамический цвет

**1. Анализ обоев (Android 12+)**
- Система извлекает доминирующие цвета из обоев
- Генерирует гармоничную цветовую палитру
- Создаёт светлую и тёмную цветовые схемы
- Предоставляет схемы приложениям

### Реализация

```kotlin
@Composable
fun AppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        // Динамический цвет доступен на Android 12+
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context)
            else dynamicLightColorScheme(context)
        }

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

### Структура цветовой схемы

**Material 3 имеет 25+ семантических цветовых ролей:**

- **Primary** - ключевые действия, кнопки
- **Secondary** - менее заметные действия
- **Tertiary** - акценты, дополнительные цвета
- **Surface** - карты, листы
- **Background** - фон экрана
- **Error** - состояния ошибок

### Использование цветовых ролей

```kotlin
// Кнопка с primary цветом
Button(
    colors = ButtonDefaults.buttonColors(
        containerColor = MaterialTheme.colorScheme.primary,
        contentColor = MaterialTheme.colorScheme.onPrimary
    )
) {
    Text("Сохранить")
}

// Карта с surface цветом
Card(
    colors = CardDefaults.cardColors(
        containerColor = MaterialTheme.colorScheme.surface,
        contentColor = MaterialTheme.colorScheme.onSurface
    )
) {
    Text("Содержимое карты")
}
```

### Предпочтение пользователя

Позвольте пользователям переключать динамический цвет:

```kotlin
Switch(
    checked = useDynamicColor,
    onCheckedChange = { enabled ->
        viewModel.setDynamicColor(enabled)
    }
)
```

### Лучшие практики

1. Всегда предоставляйте fallback для Android < 12
2. Используйте семантические цветовые роли
3. Тестируйте со статическими и динамическими темами
4. Предоставляйте пользовательский контроль
5. Следуйте руководству по elevation
