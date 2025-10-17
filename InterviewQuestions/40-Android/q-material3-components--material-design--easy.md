---
id: 20251016-162207
title: "Material3 Components / Компоненты Material3"
topic: ui-ux-accessibility
difficulty: easy
status: draft
created: 2025-10-13
tags: [design, material3, ui-components, design-system, difficulty/easy]
moc: moc-ui-ux-accessibility
related: []
subtopics: [material-design]
---
# Material 3 Components

# Question (EN)
> What are the key differences between Material 2 and Material 3? List the main Material 3 components and their use cases. How do you migrate from Material 2 to Material 3?

# Вопрос (RU)
> Каковы ключевые различия между Material 2 и Material 3? Перечислите основные компоненты Material 3 и их случаи использования. Как мигрировать с Material 2 на Material 3?

---

## Answer (EN)

**Material 3** (Material You) is Google's latest design system that brings personalization, accessibility, and modern design principles. It's a significant evolution from Material Design 2.

### Key Differences: Material 2 vs Material 3

| Feature | Material 2 | Material 3 |
|---------|------------|------------|
| **Design** | Fixed color palette | Dynamic color system |
| **Personalization** | Static themes | User-personalized themes |
| **Typography** | Roboto font | Variable fonts support |
| **Shapes** | Fixed corner radius | More rounded, adaptive |
| **Color roles** | Primary, Secondary | 25+ semantic color roles |
| **Elevation** | Shadow-based | Tonal surfaces |
| **Components** | 100+ components | Refreshed, modern set |

---

### Material 3 Color System

**Dynamic color** - Colors adapt from user's wallpaper (Android 12+).

```kotlin
// Material 3 theme
@Composable
fun MyApp() {
    val dynamicColor = Build.VERSION.SDK_INT >= Build.VERSION_CODES.S
    val colorScheme = when {
        dynamicColor -> dynamicLightColorScheme(LocalContext.current)
        else -> lightColorScheme(
            primary = Color(0xFF6750A4),
            onPrimary = Color(0xFFFFFFFF),
            primaryContainer = Color(0xFFEADDFF),
            onPrimaryContainer = Color(0xFF21005D),
            // ... 25+ color roles
        )
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        shapes = Shapes
    ) {
        // App content
    }
}
```

**Color roles (25+ semantic colors):**

| Role | Usage |
|------|-------|
| `primary` | Key actions, buttons |
| `onPrimary` | Text/icons on primary |
| `primaryContainer` | Less prominent primary |
| `secondary` | Secondary actions |
| `tertiary` | Tertiary actions |
| `surface` | Card, sheet backgrounds |
| `surfaceVariant` | Subtle surface |
| `outline` | Borders, dividers |
| `error` | Error states |
| `background` | Screen background |

---

### Main Material 3 Components

#### 1. **Buttons**

```kotlin
// Filled Button (primary action)
Button(onClick = { /* ... */ }) {
    Text("Save")
}

// Filled Tonal Button (secondary action)
FilledTonalButton(onClick = { /* ... */ }) {
    Text("Cancel")
}

// Outlined Button (tertiary action)
OutlinedButton(onClick = { /* ... */ }) {
    Text("Learn More")
}

// Text Button (lowest emphasis)
TextButton(onClick = { /* ... */ }) {
    Text("Skip")
}

// Extended FAB with icon and text
ExtendedFloatingActionButton(
    onClick = { /* ... */ },
    icon = { Icon(Icons.Filled.Add, "Add") },
    text = { Text("Create") }
)
```

**Use cases:**
- **Filled**: Primary action (Save, Submit, Confirm)
- **Filled Tonal**: Secondary action (Cancel, Back)
- **Outlined**: Tertiary action (Learn More, Details)
- **Text**: Lowest priority (Skip, Dismiss)

---

#### 2. **Cards**

```kotlin
// Elevated Card (default)
Card(
    modifier = Modifier.fillMaxWidth(),
    colors = CardDefaults.cardColors(
        containerColor = MaterialTheme.colorScheme.surfaceVariant
    ),
    elevation = CardDefaults.cardElevation(
        defaultElevation = 6.dp
    )
) {
    Column(modifier = Modifier.padding(16.dp)) {
        Text("Card Title", style = MaterialTheme.typography.titleMedium)
        Text("Card content here", style = MaterialTheme.typography.bodyMedium)
    }
}

// Filled Card (tonal surface)
Card(
    modifier = Modifier.fillMaxWidth(),
    colors = CardDefaults.cardColors(
        containerColor = MaterialTheme.colorScheme.surfaceVariant
    )
) {
    // Content
}

// Outlined Card (with border)
OutlinedCard(
    modifier = Modifier.fillMaxWidth(),
    border = BorderStroke(1.dp, MaterialTheme.colorScheme.outline)
) {
    // Content
}
```

---

#### 3. **Navigation Components**

**Navigation Bar (Bottom Navigation):**
```kotlin
NavigationBar {
    NavigationBarItem(
        icon = { Icon(Icons.Filled.Home, "Home") },
        label = { Text("Home") },
        selected = selectedIndex == 0,
        onClick = { selectedIndex = 0 }
    )

    NavigationBarItem(
        icon = { Icon(Icons.Filled.Search, "Search") },
        label = { Text("Search") },
        selected = selectedIndex == 1,
        onClick = { selectedIndex = 1 }
    )

    NavigationBarItem(
        icon = { Icon(Icons.Filled.Person, "Profile") },
        label = { Text("Profile") },
        selected = selectedIndex == 2,
        onClick = { selectedIndex = 2 }
    )
}
```

**Navigation Rail (Side Navigation):**
```kotlin
NavigationRail {
    NavigationRailItem(
        icon = { Icon(Icons.Filled.Home, "Home") },
        label = { Text("Home") },
        selected = selectedIndex == 0,
        onClick = { selectedIndex = 0 }
    )
    // More items...
}
```

**Navigation Drawer:**
```kotlin
ModalNavigationDrawer(
    drawerContent = {
        ModalDrawerSheet {
            Text("Menu", modifier = Modifier.padding(16.dp))
            Divider()
            NavigationDrawerItem(
                label = { Text("Home") },
                selected = selectedIndex == 0,
                onClick = { selectedIndex = 0 },
                icon = { Icon(Icons.Filled.Home, "Home") }
            )
            // More items...
        }
    }
) {
    // Screen content
}
```

---

#### 4. **Top App Bar**

```kotlin
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MyTopAppBar() {
    // Small Top App Bar (default)
    TopAppBar(
        title = { Text("My App") },
        navigationIcon = {
            IconButton(onClick = { /* ... */ }) {
                Icon(Icons.Filled.Menu, "Menu")
            }
        },
        actions = {
            IconButton(onClick = { /* ... */ }) {
                Icon(Icons.Filled.Search, "Search")
            }
        },
        colors = TopAppBarDefaults.topAppBarColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer,
            titleContentColor = MaterialTheme.colorScheme.onPrimaryContainer
        )
    )

    // Medium Top App Bar (with scroll behavior)
    MediumTopAppBar(
        title = { Text("Medium App Bar") },
        scrollBehavior = TopAppBarDefaults.exitUntilCollapsedScrollBehavior()
    )

    // Large Top App Bar
    LargeTopAppBar(
        title = { Text("Large App Bar") }
    )
}
```

---

#### 5. **Text Fields**

```kotlin
var text by remember { mutableStateOf("") }

// Filled Text Field (default)
TextField(
    value = text,
    onValueChange = { text = it },
    label = { Text("Label") },
    placeholder = { Text("Enter text") },
    leadingIcon = { Icon(Icons.Filled.Search, "Search") },
    trailingIcon = {
        IconButton(onClick = { text = "" }) {
            Icon(Icons.Filled.Clear, "Clear")
        }
    }
)

// Outlined Text Field
OutlinedTextField(
    value = text,
    onValueChange = { text = it },
    label = { Text("Outlined") },
    supportingText = { Text("Helper text") }
)
```

---

#### 6. **Dialogs and Sheets**

**Alert Dialog:**
```kotlin
AlertDialog(
    onDismissRequest = { showDialog = false },
    title = { Text("Dialog Title") },
    text = { Text("This is the dialog content") },
    confirmButton = {
        TextButton(onClick = { showDialog = false }) {
            Text("Confirm")
        }
    },
    dismissButton = {
        TextButton(onClick = { showDialog = false }) {
            Text("Cancel")
        }
    }
)
```

**Bottom Sheet:**
```kotlin
@OptIn(ExperimentalMaterial3Api::class)
val bottomSheetState = rememberModalBottomSheetState()

ModalBottomSheet(
    onDismissRequest = { showBottomSheet = false },
    sheetState = bottomSheetState
) {
    Column(modifier = Modifier.padding(16.dp)) {
        Text("Bottom Sheet Title", style = MaterialTheme.typography.titleLarge)
        Text("Sheet content here")
    }
}
```

---

#### 7. **Chips**

```kotlin
// Assist Chip (action)
AssistChip(
    onClick = { /* ... */ },
    label = { Text("Assist") },
    leadingIcon = { Icon(Icons.Filled.Check, "Check") }
)

// Filter Chip (filter selection)
FilterChip(
    selected = isSelected,
    onClick = { isSelected = !isSelected },
    label = { Text("Filter") },
    leadingIcon = {
        if (isSelected) Icon(Icons.Filled.Check, "Selected")
        else null
    }
)

// Input Chip (user input)
InputChip(
    selected = false,
    onClick = { /* ... */ },
    label = { Text("Input") },
    trailingIcon = {
        IconButton(onClick = { /* remove */ }) {
            Icon(Icons.Filled.Close, "Remove")
        }
    }
)

// Suggestion Chip (suggestions)
SuggestionChip(
    onClick = { /* ... */ },
    label = { Text("Suggestion") }
)
```

---

#### 8. **Switches, Checkboxes, Radio Buttons**

```kotlin
var switchChecked by remember { mutableStateOf(false) }
var checkboxChecked by remember { mutableStateOf(false) }
var radioSelected by remember { mutableStateOf(0) }

// Switch
Switch(
    checked = switchChecked,
    onCheckedChange = { switchChecked = it }
)

// Checkbox
Checkbox(
    checked = checkboxChecked,
    onCheckedChange = { checkboxChecked = it }
)

// Radio Buttons
RadioButton(
    selected = radioSelected == 0,
    onClick = { radioSelected = 0 }
)
```

---

### Migration from Material 2 to Material 3

**Step 1: Update dependencies**

```gradle
// build.gradle (app)
dependencies {
    // Remove Material 2
    // implementation "androidx.compose.material:material:1.x.x"

    // Add Material 3
    implementation "androidx.compose.material3:material3:1.2.0"

    // Material icons extended (optional)
    implementation "androidx.compose.material:material-icons-extended:1.6.0"
}
```

**Step 2: Update theme**

```kotlin
// Before (Material 2)
import androidx.compose.material.MaterialTheme
import androidx.compose.material.Colors

MaterialTheme(
    colors = lightColors(
        primary = Color(0xFF6200EE),
        // ...
    )
) {
    // Content
}

// After (Material 3)
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme

MaterialTheme(
    colorScheme = lightColorScheme(
        primary = Color(0xFF6750A4),
        onPrimary = Color(0xFFFFFFFF),
        primaryContainer = Color(0xFFEADDFF),
        // ... 25+ color roles
    )
) {
    // Content
}
```

**Step 3: Update imports**

```kotlin
// Before
import androidx.compose.material.Button
import androidx.compose.material.Text
import androidx.compose.material.Icon

// After
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.material3.Icon
```

**Step 4: Update component names**

| Material 2 | Material 3 |
|------------|------------|
| `Button` | `Button` (same) |
| `OutlinedButton` | `OutlinedButton` (same) |
| `TextButton` | `TextButton` (same) |
| N/A | `FilledTonalButton` (new) |
| `FloatingActionButton` | `FloatingActionButton` (same) |
| N/A | `ExtendedFloatingActionButton` (enhanced) |
| `BottomNavigation` | `NavigationBar` |
| `BottomNavigationItem` | `NavigationBarItem` |
| `TopAppBar` | `TopAppBar` (enhanced) |
| N/A | `MediumTopAppBar` (new) |
| N/A | `LargeTopAppBar` (new) |

**Step 5: Handle breaking changes**

```kotlin
// Material 2: elevation prop
Card(elevation = 4.dp) {
    // ...
}

// Material 3: elevation object
Card(
    elevation = CardDefaults.cardElevation(
        defaultElevation = 4.dp
    )
) {
    // ...
}

// Material 2: backgroundColor
Card(backgroundColor = Color.White) {
    // ...
}

// Material 3: containerColor in colors
Card(
    colors = CardDefaults.cardColors(
        containerColor = Color.White
    )
) {
    // ...
}
```

---

### Dynamic Color (Android 12+)

```kotlin
@Composable
fun AppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true, // Enable on Android 12+
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context)
            else dynamicLightColorScheme(context)
        }

        darkTheme -> darkColorScheme(
            primary = Color(0xFFD0BCFF),
            // ... dark colors
        )

        else -> lightColorScheme(
            primary = Color(0xFF6750A4),
            // ... light colors
        )
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
```

---

### Best Practices

**1. Use semantic color roles**
```kotlin
//  DO - Use semantic roles
Card(
    colors = CardDefaults.cardColors(
        containerColor = MaterialTheme.colorScheme.surfaceVariant
    )
)

//  DON'T - Hardcode colors
Card(colors = CardDefaults.cardColors(containerColor = Color(0xFFE8DEF8)))
```

**2. Respect dynamic theming**
```kotlin
//  Enable dynamic color when available
val colorScheme = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
    dynamicLightColorScheme(context)
} else {
    lightColorScheme()
}
```

**3. Use appropriate button types**
- Filled: Primary action
- Filled Tonal: Secondary action
- Outlined: Tertiary action
- Text: Lowest priority

**4. Follow elevation guidance**
- Level 0: Background, surfaces
- Level 1: Cards, sheets
- Level 2: App bars
- Level 3: FAB, dialogs
- Level 4: Navigation drawer
- Level 5: Modal bottom sheet

---

### Summary

**Material 3 key features:**
- Dynamic color system
- User personalization
- 25+ semantic color roles
- Tonal elevation
- Modernized components
- Better accessibility

**Main components:**
- Buttons (Filled, Tonal, Outlined, Text)
- Cards (Elevated, Filled, Outlined)
- Navigation (Bar, Rail, Drawer)
- Top App Bar (Small, Medium, Large)
- Text Fields (Filled, Outlined)
- Dialogs and Bottom Sheets
- Chips (Assist, Filter, Input, Suggestion)

**Migration steps:**
1. Update dependencies
2. Update theme (colors → colorScheme)
3. Update imports
4. Update component names
5. Handle breaking changes

---

## Ответ (RU)

**Material 3** (Material You) - это новейшая дизайн-система Google, которая привносит персонализацию, доступность и современные принципы дизайна.

### Ключевые различия: Material 2 vs Material 3

| Функция | Material 2 | Material 3 |
|---------|------------|------------|
| **Дизайн** | Фиксированная палитра | Динамическая цветовая система |
| **Персонализация** | Статические темы | Персонализированные темы |
| **Цветовые роли** | Primary, Secondary | 25+ семантических ролей |
| **Elevation** | На основе теней | Тональные поверхности |

### Основные компоненты Material 3

**Кнопки:**
- `Button` - Основное действие
- `FilledTonalButton` - Вторичное действие
- `OutlinedButton` - Третичное действие
- `TextButton` - Самый низкий приоритет

**Карты:**
- `Card` - Elevated card
- `OutlinedCard` - Card с границей

**Навигация:**
- `NavigationBar` - Нижняя навигация
- `NavigationRail` - Боковая навигация
- `ModalNavigationDrawer` - Выдвижное меню

**App Bar:**
- `TopAppBar` - Маленький
- `MediumTopAppBar` - Средний
- `LargeTopAppBar` - Большой

### Миграция с Material 2 на Material 3

**1. Обновить зависимости:**
```gradle
implementation "androidx.compose.material3:material3:1.2.0"
```

**2. Обновить theme:**
```kotlin
// Material 2
MaterialTheme(colors = lightColors())

// Material 3
MaterialTheme(colorScheme = lightColorScheme())
```

**3. Обновить imports:**
```kotlin
// До
import androidx.compose.material.Button

// После
import androidx.compose.material3.Button
```

**4. Обновить имена компонентов:**
- `BottomNavigation` → `NavigationBar`
- `BottomNavigationItem` → `NavigationBarItem`

**5. Использовать подходящие типы кнопок**
- Filled: Основное действие
- Filled Tonal: Вторичное действие
- Outlined: Третичное действие
- Text: Самый низкий приоритет

### Динамический цвет (Android 12+)

```kotlin
@Composable
fun AppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true, // Включить на Android 12+
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context)
            else dynamicLightColorScheme(context)
        }

        darkTheme -> darkColorScheme(
            primary = Color(0xFFD0BCFF),
            // ... темные цвета
        )

        else -> lightColorScheme(
            primary = Color(0xFF6750A4),
            // ... светлые цвета
        )
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
```

### Лучшие практики

**1. Использовать семантические цветовые роли**
```kotlin
//  ДЕЛАЙТЕ - Используйте семантические роли
Card(
    colors = CardDefaults.cardColors(
        containerColor = MaterialTheme.colorScheme.surfaceVariant
    )
)

//  НЕ ДЕЛАЙТЕ - Жестко закодированные цвета
Card(colors = CardDefaults.cardColors(containerColor = Color(0xFFE8DEF8)))
```

**2. Уважать динамическую тематизацию**
```kotlin
//  Включить динамический цвет когда доступно
val colorScheme = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
    dynamicLightColorScheme(context)
} else {
    lightColorScheme()
}
```

**3. Следовать руководству по elevation**
- Уровень 0: Фон, поверхности
- Уровень 1: Карточки, листы
- Уровень 2: App bars
- Уровень 3: FAB, диалоги
- Уровень 4: Navigation drawer
- Уровень 5: Modal bottom sheet

### Резюме Material 3

**Ключевые возможности Material 3:**
- Динамическая цветовая система
- Персонализация пользователя
- 25+ семантических цветовых ролей
- Тональная elevation
- Модернизированные компоненты
- Лучшая доступность

**Основные компоненты:**
- Кнопки (Filled, Tonal, Outlined, Text)
- Карточки (Elevated, Filled, Outlined)
- Навигация (Bar, Rail, Drawer)
- Top App Bar (Small, Medium, Large)
- Text Fields (Filled, Outlined)
- Диалоги и Bottom Sheets
- Chips (Assist, Filter, Input, Suggestion)

**Шаги миграции:**
1. Обновить зависимости
2. Обновить theme (colors → colorScheme)
3. Обновить imports
4. Обновить имена компонентов
5. Обработать breaking changes

---

## Related Questions

### Related (Easy)
- [[q-architecture-components-libraries--android--easy]] - Fundamentals
- [[q-what-unifies-android-components--android--easy]] - Fundamentals
- [[q-android-components-besides-activity--android--easy]] - Fundamentals
- [[q-main-android-components--android--easy]] - Fundamentals
- [[q-android-app-components--android--easy]] - Fundamentals

### Advanced (Harder)
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Fundamentals
- [[q-what-unites-the-main-components-of-an-android-application--android--medium]] - Fundamentals
- [[q-hilt-components-scope--android--medium]] - Fundamentals
