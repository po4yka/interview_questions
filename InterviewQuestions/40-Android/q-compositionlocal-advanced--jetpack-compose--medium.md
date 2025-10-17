---
id: "20251015082237277"
title: "Compositionlocal Advanced / CompositionLocal продвинутый уровень"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [compose, composition-local, dependency-injection, best-practices, architecture, difficulty/medium]
---

# CompositionLocal Advanced Usage

# Question (EN)

> When should you use CompositionLocal vs passing parameters? Explain staticCompositionLocalOf vs compositionLocalOf.

# Вопрос (RU)

> Когда следует использовать CompositionLocal вместо передачи параметров? Объясните разницу между staticCompositionLocalOf и compositionLocalOf.

---

## Answer (EN)

**CompositionLocal** is Compose's mechanism for implicitly passing data down the composition tree without explicitly passing parameters through every composable. Think of it as a type-safe dependency injection system scoped to the composition.

### CompositionLocal vs Parameters

**Use Parameters When:**

-   Data is used by immediate children
-   Explicit dependencies are clearer
-   Data changes frequently per composable
-   You want compile-time safety

**Use CompositionLocal When:**

-   Data is needed deep in the tree (cross-cutting concerns)
-   It's awkward to pass through many layers
-   Data represents environmental context (theme, locale, etc.)
-   Data changes infrequently

---

### Basic Usage

**Creating a CompositionLocal:**

```kotlin
// Theme data
data class AppTheme(
    val primaryColor: Color,
    val secondaryColor: Color,
    val typography: Typography
)

// Create CompositionLocal
val LocalAppTheme = compositionLocalOf<AppTheme> {
    error("No AppTheme provided")
}
```

**Providing values:**

```kotlin
@Composable
fun App() {
    val theme = AppTheme(
        primaryColor = Color.Blue,
        secondaryColor = Color.Green,
        typography = Typography.Default
    )

    CompositionLocalProvider(LocalAppTheme provides theme) {
        // All children can access theme
        MainScreen()
    }
}
```

**Consuming values:**

```kotlin
@Composable
fun DeepNestedComponent() {
    // Access theme without explicit parameters
    val theme = LocalAppTheme.current

    Text(
        "Hello",
        color = theme.primaryColor
    )
}
```

---

### staticCompositionLocalOf vs compositionLocalOf

The key difference is **how recomposition is triggered** when the value changes.

#### compositionLocalOf (Dynamic)

**Characteristics:**

-   Tracks reads at the **specific location** where `.current` is accessed
-   Only recomposes consumers that actually read the value
-   More efficient for frequently changing values
-   Small performance overhead per read

```kotlin
val LocalCounter = compositionLocalOf { 0 }

@Composable
fun Parent() {
    var counter by remember { mutableStateOf(0) }

    CompositionLocalProvider(LocalCounter provides counter) {
        Column {
            // Recomposes when counter changes
            Child1()

            // Does NOT recompose (doesn't read LocalCounter)
            Child2()

            Button(onClick = { counter++ }) {
                Text("Increment")
            }
        }
    }
}

@Composable
fun Child1() {
    val counter = LocalCounter.current // Reads value
    Text("Counter: $counter")         // Recomposes
}

@Composable
fun Child2() {
    Text("Static text") // Never recomposes
}
```

**When counter changes:**

-   `Parent` recomposes (owns the state)
-   `Child1` recomposes (reads `LocalCounter.current`)
-   `Child2` does NOT recompose (never reads value)

---

#### staticCompositionLocalOf (Static)

**Characteristics:**

-   Does NOT track individual reads
-   Recomposes **entire composition** below the provider
-   More efficient for rarely changing values (no tracking overhead)
-   Used for truly static or rarely-changing data

```kotlin
val LocalConfig = staticCompositionLocalOf { Config.DEFAULT }

@Composable
fun Parent() {
    var config by remember { mutableStateOf(Config.DEFAULT) }

    CompositionLocalProvider(LocalConfig provides config) {
        Column {
            Child1()
            Child2()
            Button(onClick = { config = Config.DARK }) {
                Text("Change Config")
            }
        }
    }
}

@Composable
fun Child1() {
    val config = LocalConfig.current
    Text("Child1: ${config.name}")
}

@Composable
fun Child2() {
    Text("Static text")
}
```

**When config changes:**

-   `Parent` recomposes
-   `Child1` recomposes (entire subtree recomposes)
-   `Child2` recomposes (entire subtree recomposes, even though it doesn't read the value!)

---

### Comparison Table

| Feature                           | compositionLocalOf                 | staticCompositionLocalOf     |
| --------------------------------- | ---------------------------------- | ---------------------------- |
| **Recomposition scope**           | Only consumers that read the value | Entire subtree               |
| **Read tracking**                 | Yes                                | No                           |
| **Performance (stable values)**   | Slower (tracking overhead)         | Faster (no tracking)         |
| **Performance (changing values)** | Faster (targeted recomposition)    | Slower (broad recomposition) |
| **Best for**                      | Frequently changing values         | Rarely changing values       |
| **Memory overhead**               | Higher (per-read tracking)         | Lower                        |
| **Examples**                      | Colors, dimensions                 | Configuration, locale        |

---

### Real-World Examples

#### Example 1: Theme System

```kotlin
// Theme that might change at runtime (dark/light mode)
data class AppTheme(
    val colors: ColorScheme,
    val typography: Typography,
    val shapes: Shapes
)

// Use compositionLocalOf (changes at runtime)
val LocalAppTheme = compositionLocalOf<AppTheme> {
    error("No theme provided")
}

@Composable
fun ThemedApp() {
    var isDarkMode by remember { mutableStateOf(false) }

    val theme = if (isDarkMode) {
        AppTheme(
            colors = darkColorScheme(),
            typography = Typography.Default,
            shapes = Shapes()
        )
    } else {
        AppTheme(
            colors = lightColorScheme(),
            typography = Typography.Default,
            shapes = Shapes()
        )
    }

    CompositionLocalProvider(LocalAppTheme provides theme) {
        Scaffold(
            floatingActionButton = {
                FloatingActionButton(
                    onClick = { isDarkMode = !isDarkMode }
                ) {
                    Icon(Icons.Default.DarkMode, "Toggle theme")
                }
            }
        ) {
            MainContent()
        }
    }
}

@Composable
fun ThemedButton() {
    // Only this composable recomposes when theme changes
    val theme = LocalAppTheme.current

    Button(
        colors = ButtonDefaults.buttonColors(
            containerColor = theme.colors.primary
        )
    ) {
        Text("Themed Button")
    }
}
```

---

#### Example 2: App Configuration

```kotlin
// Configuration that never changes after app start
data class AppConfig(
    val apiUrl: String,
    val featureFlags: Map<String, Boolean>,
    val buildVersion: String
)

// Use staticCompositionLocalOf (static after initialization)
val LocalAppConfig = staticCompositionLocalOf {
    AppConfig(
        apiUrl = "",
        featureFlags = emptyMap(),
        buildVersion = ""
    )
}

@Composable
fun App() {
    // Load config once at app start
    val config = remember {
        AppConfig(
            apiUrl = "https://api.example.com",
            featureFlags = mapOf("newFeature" to true),
            buildVersion = "1.0.0"
        )
    }

    CompositionLocalProvider(LocalAppConfig provides config) {
        MainApp()
    }
}

@Composable
fun FeatureGatedScreen() {
    val config = LocalAppConfig.current

    if (config.featureFlags["newFeature"] == true) {
        NewFeatureScreen()
    } else {
        OldFeatureScreen()
    }
}
```

---

#### Example 3: User Context

```kotlin
// User info that changes when user logs in/out
data class User(
    val id: String,
    val name: String,
    val email: String,
    val avatarUrl: String?
)

// Use compositionLocalOf (changes on login/logout)
val LocalUser = compositionLocalOf<User?> { null }

@Composable
fun AuthenticatedApp(viewModel: AuthViewModel) {
    val user by viewModel.currentUser.collectAsState()

    CompositionLocalProvider(LocalUser provides user) {
        if (user != null) {
            MainApp()
        } else {
            LoginScreen()
        }
    }
}

@Composable
fun UserAvatar() {
    val user = LocalUser.current

    if (user != null) {
        AsyncImage(
            model = user.avatarUrl,
            contentDescription = user.name
        )
    } else {
        Icon(Icons.Default.Person, "Guest")
    }
}

@Composable
fun WelcomeMessage() {
    val user = LocalUser.current
    Text("Welcome, ${user?.name ?: "Guest"}!")
}
```

---

### Multiple CompositionLocal Providers

You can provide multiple values at once:

```kotlin
@Composable
fun App() {
    val theme = remember { AppTheme(...) }
    val user = remember { User(...) }
    val config = remember { AppConfig(...) }

    CompositionLocalProvider(
        LocalAppTheme provides theme,
        LocalUser provides user,
        LocalAppConfig provides config
    ) {
        MainScreen()
    }
}
```

---

### Nested Providers (Overriding)

Inner providers override outer providers:

```kotlin
val LocalColor = compositionLocalOf { Color.Red }

@Composable
fun NestedProviders() {
    CompositionLocalProvider(LocalColor provides Color.Blue) {
        Text("Blue: ${LocalColor.current}") // Blue

        CompositionLocalProvider(LocalColor provides Color.Green) {
            Text("Green: ${LocalColor.current}") // Green
        }

        Text("Blue again: ${LocalColor.current}") // Blue
    }
}
```

---

### Anti-Patterns

#### DON'T: Use CompositionLocal for simple parameter passing

```kotlin
//  BAD: Unnecessary CompositionLocal
val LocalName = compositionLocalOf { "" }

@Composable
fun Parent(name: String) {
    CompositionLocalProvider(LocalName provides name) {
        Child()
    }
}

@Composable
fun Child() {
    val name = LocalName.current
    Text(name)
}

//  GOOD: Just pass parameters
@Composable
fun Parent(name: String) {
    Child(name)
}

@Composable
fun Child(name: String) {
    Text(name)
}
```

---

#### DON'T: Use CompositionLocal for business logic

```kotlin
//  BAD: Business logic in CompositionLocal
val LocalRepository = compositionLocalOf<UserRepository> {
    error("No repository")
}

@Composable
fun UserScreen() {
    val repository = LocalRepository.current
    val user = repository.getUser() // Business logic
    Text(user.name)
}

//  GOOD: Use ViewModel
@Composable
fun UserScreen(viewModel: UserViewModel) {
    val user by viewModel.user.collectAsState()
    Text(user.name)
}
```

---

#### DON'T: Overuse staticCompositionLocalOf

```kotlin
//  BAD: Using static for frequently changing value
val LocalSelectedTab = staticCompositionLocalOf { 0 }

@Composable
fun TabScreen() {
    var selectedTab by remember { mutableStateOf(0) }

    CompositionLocalProvider(LocalSelectedTab provides selectedTab) {
        // Entire tree recomposes on every tab change!
        TabContent()
    }
}

//  GOOD: Use dynamic CompositionLocal or state hoisting
val LocalSelectedTab = compositionLocalOf { 0 }
```

---

### CompositionLocal with Material Theme

Material3 uses CompositionLocal extensively:

```kotlin
// Material3 provides these CompositionLocals
@Composable
fun MaterialTheme(
    colorScheme: ColorScheme = MaterialTheme.colorScheme,
    typography: Typography = MaterialTheme.typography,
    shapes: Shapes = MaterialTheme.shapes,
    content: @Composable () -> Unit
) {
    CompositionLocalProvider(
        LocalColorScheme provides colorScheme,
        LocalTypography provides typography,
        LocalShapes provides shapes
    ) {
        content()
    }
}

// Usage
@Composable
fun ThemedComponent() {
    // Access theme values
    val colors = MaterialTheme.colorScheme
    val typography = MaterialTheme.typography

    Text(
        "Themed",
        color = colors.primary,
        style = typography.headlineMedium
    )
}
```

---

### Custom Design System Example

```kotlin
// Custom design system
data class CustomTheme(
    val colors: CustomColors,
    val dimensions: Dimensions,
    val animations: AnimationSpecs
)

data class CustomColors(
    val brand: Color,
    val accent: Color,
    val background: Color,
    val surface: Color
)

data class Dimensions(
    val paddingSmall: Dp,
    val paddingMedium: Dp,
    val paddingLarge: Dp,
    val cornerRadius: Dp
)

data class AnimationSpecs(
    val fast: Int,
    val normal: Int,
    val slow: Int
)

// Create CompositionLocals
private val LocalCustomColors = compositionLocalOf { CustomColors(...) }
private val LocalDimensions = staticCompositionLocalOf { Dimensions(...) }
private val LocalAnimations = staticCompositionLocalOf { AnimationSpecs(...) }

// Theme object for convenient access
object CustomMaterialTheme {
    val colors: CustomColors
        @Composable
        @ReadOnlyComposable
        get() = LocalCustomColors.current

    val dimensions: Dimensions
        @Composable
        @ReadOnlyComposable
        get() = LocalDimensions.current

    val animations: AnimationSpecs
        @Composable
        @ReadOnlyComposable
        get() = LocalAnimations.current
}

// Provider composable
@Composable
fun CustomMaterialTheme(
    colors: CustomColors = CustomMaterialTheme.colors,
    dimensions: Dimensions = CustomMaterialTheme.dimensions,
    animations: AnimationSpecs = CustomMaterialTheme.animations,
    content: @Composable () -> Unit
) {
    CompositionLocalProvider(
        LocalCustomColors provides colors,
        LocalDimensions provides dimensions,
        LocalAnimations provides animations
    ) {
        content()
    }
}

// Usage
@Composable
fun CustomThemedCard() {
    Card(
        modifier = Modifier.padding(CustomMaterialTheme.dimensions.paddingMedium),
        shape = RoundedCornerShape(CustomMaterialTheme.dimensions.cornerRadius),
        colors = CardDefaults.cardColors(
            containerColor = CustomMaterialTheme.colors.surface
        )
    ) {
        Text(
            "Custom themed",
            color = CustomMaterialTheme.colors.brand
        )
    }
}
```

---

### Testing with CompositionLocal

```kotlin
@Test
fun testComposableWithCustomTheme() {
    composeTestRule.setContent {
        val testTheme = AppTheme(
            primaryColor = Color.Red,
            secondaryColor = Color.Blue,
            typography = Typography.Default
        )

        CompositionLocalProvider(LocalAppTheme provides testTheme) {
            ThemedButton()
        }
    }

    composeTestRule
        .onNodeWithText("Themed Button")
        .assertExists()
}

@Test
fun testComposableWithDefaultTheme() {
    // Test that default is used when no provider
    composeTestRule.setContent {
        assertThrows<IllegalStateException> {
            LocalAppTheme.current // Should throw if no default
        }
    }
}
```

---

### Best Practices

**1. Choose the right type:**

```kotlin
//  DO: Use compositionLocalOf for runtime values
val LocalTheme = compositionLocalOf { Theme.Light }

//  DO: Use staticCompositionLocalOf for constants
val LocalApiUrl = staticCompositionLocalOf { "https://api.example.com" }
```

**2. Provide meaningful defaults or errors:**

```kotlin
//  DO: Clear error message
val LocalUser = compositionLocalOf<User?> {
    error("LocalUser not provided. Wrap content with UserProvider.")
}

//  DON'T: Silent failure
val LocalUser = compositionLocalOf<User?> { null }
```

**3. Use for cross-cutting concerns:**

```kotlin
//  GOOD use cases:
- Theming (colors, typography, shapes)
- Localization (strings, formatters)
- Accessibility (font scaling, contrast)
- Platform info (window size, orientation)
- Navigation (back handler, nav controller)
- Dependency injection (repositories, but sparingly)

//  BAD use cases:
- Simple data passing (use parameters)
- Business logic (use ViewModels)
- Screen state (use state hoisting)
```

**4. Document your CompositionLocals:**

```kotlin
/**
 * Provides the current [AppTheme] down the composition tree.
 *
 * @throws IllegalStateException if accessed before a theme is provided
 * @sample com.example.ThemeUsageSample
 */
val LocalAppTheme = compositionLocalOf<AppTheme> {
    error("No AppTheme provided")
}
```

**5. Consider alternatives first:**

```
1. Can you pass parameters directly? → Use parameters
2. Is it ViewModel data? → Use ViewModel
3. Is it truly cross-cutting? → Use CompositionLocal
```

---

## Ответ (RU)

**CompositionLocal** — это механизм Compose для неявной передачи данных вниз по дереву композиции без явной передачи параметров через каждую composable-функцию. Это типобезопасная система внедрения зависимостей, ограниченная областью композиции.

### CompositionLocal vs Параметры

**Используйте параметры когда:**

-   Данные используются непосредственными дочерними элементами
-   Явные зависимости более понятны
-   Данные часто меняются для каждого composable
-   Нужна безопасность на уровне компиляции

**Используйте CompositionLocal когда:**

-   Данные нужны глубоко в дереве (сквозные задачи)
-   Неудобно передавать через много слоев
-   Данные представляют контекст окружения (тема, локаль и т.д.)
-   Данные редко меняются

### staticCompositionLocalOf vs compositionLocalOf

**compositionLocalOf (Динамический):**

-   Отслеживает чтения в конкретном месте, где вызывается `.current`
-   Перекомпонует только потребителей, которые действительно читают значение
-   Более эффективен для часто изменяющихся значений

**staticCompositionLocalOf (Статический):**

-   НЕ отслеживает отдельные чтения
-   Перекомпонует **всю композицию** ниже провайдера
-   Более эффективен для редко меняющихся значений (нет накладных расходов на отслеживание)

### Когда использовать что

| Тип значения                | Рекомендуемый вариант    |
| --------------------------- | ------------------------ |
| Цвета темы (меняются)       | compositionLocalOf       |
| Типографика темы (меняется) | compositionLocalOf       |
| URL API (константа)         | staticCompositionLocalOf |
| Конфигурация приложения     | staticCompositionLocalOf |
| Информация о пользователе   | compositionLocalOf       |
| Локаль (редко меняется)     | staticCompositionLocalOf |

### Лучшие практики

1. Выбирайте правильный тип на основе частоты изменений
2. Предоставляйте осмысленные значения по умолчанию или ошибки
3. Используйте для сквозных задач, а не для простой передачи данных
4. Документируйте ваши CompositionLocals
5. Рассматривайте альтернативы сначала (параметры, ViewModel)

CompositionLocal — мощный инструмент для управления глобальным контекстом, но его следует использовать разумно.

---

## Related Questions

### Hub

-   [[q-jetpack-compose-basics--android--medium]] - Comprehensive Compose introduction

### Related (Medium)

-   [[q-how-does-jetpack-compose-work--android--medium]] - How Compose works
-   [[q-what-are-the-most-important-components-of-compose--android--medium]] - Essential Compose components
-   [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - RecyclerView in Compose
-   [[q-mutable-state-compose--android--medium]] - MutableState basics
-   [[q-remember-vs-remembersaveable-compose--android--medium]] - remember vs rememberSaveable

### Advanced (Harder)

-   [[q-compose-stability-skippability--jetpack-compose--hard]] - Stability & skippability
-   [[q-stable-classes-compose--android--hard]] - @Stable annotation
-   [[q-stable-annotation-compose--android--hard]] - Stability annotations

---

## Follow-ups

-   When should CompositionLocal be avoided in favor of explicit parameters?
-   How do staticCompositionLocalOf vs compositionLocalOf impact recomposition scope?
-   How do you test CompositionLocal usage in complex trees?

## References

-   `https://developer.android.com/jetpack/compose/compositionlocal` — CompositionLocal
-   `https://developer.android.com/jetpack/compose/performance` — Performance & recomposition
-   `https://developer.android.com/jetpack/compose/state` — State and effects
