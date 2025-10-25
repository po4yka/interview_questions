---
id: 20251012-400004
title: "WindowInsets & Edge-to-Edge / WindowInsets и Edge-to-Edge"
aliases: [WindowInsets & Edge-to-Edge, WindowInsets и Edge-to-Edge]
topic: android
subtopics: [ui-system-ui, windowinsets]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-windowinsets, q-compose-navigation-advanced--android--medium, q-compose-scaffold--android--medium]
created: 2025-10-12
updated: 2025-01-25
tags: [android/ui-system-ui, android/windowinsets, windowinsets, edge-to-edge, system-ui, immersive, difficulty/medium]
sources: [https://developer.android.com/develop/ui/views/layout/edge-to-edge]
---

# Вопрос (RU)
> Что такое WindowInsets и как реализовать edge-to-edge дизайн?

# Question (EN)
> What are WindowInsets and how to implement edge-to-edge design?

---

## Ответ (RU)

**Теория WindowInsets:**
WindowInsets предоставляют информацию о системных элементах UI (status bar, navigation bar, клавиатура, вырезы), позволяя приложению адаптировать контент и создавать иммерсивный edge-to-edge опыт.

**Edge-to-Edge активация:**
Позволяет приложению рисовать за системными барами для создания полноэкранного опыта.

```kotlin
// Активация edge-to-edge
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge() // Позволяет рисовать за системными барами
        setContent { MainScreen() }
    }
}
```

**WindowInsets в Compose:**
Доступ к различным типам insets для адаптации UI под системные элементы.

```kotlin
@Composable
fun WindowInsetsExample() {
    val systemBars = WindowInsets.systemBars
    val statusBarHeight = systemBars.asPaddingValues().calculateTopPadding()
    val navigationBarHeight = systemBars.asPaddingValues().calculateBottomPadding()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .windowInsetsPadding(WindowInsets.systemBars) // Автоматический padding
    ) {
        Text("Контент избегает системных баров")
    }
}
```

**Типы WindowInsets:**
Различные insets для разных системных элементов и безопасных областей.

```kotlin
// Основные типы insets
val systemBars = WindowInsets.systemBars // Status + Navigation
val statusBars = WindowInsets.statusBars // Только status bar
val navigationBars = WindowInsets.navigationBars // Только navigation bar
val ime = WindowInsets.ime // Клавиатура
val displayCutout = WindowInsets.displayCutout // Вырезы (notch)
val safeDrawing = WindowInsets.safeDrawing // Безопасная область рисования
```

**Обработка клавиатуры:**
Автоматическая адаптация UI при появлении клавиатуры.

```kotlin
@Composable
fun KeyboardHandlingExample() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .imePadding() // Автоматически поднимает контент над клавиатурой
    ) {
        LazyColumn(modifier = Modifier.weight(1f)) {
            items(50) { Text("Item $it") }
        }

        TextField(
            value = text,
            onValueChange = { text = it },
            modifier = Modifier.fillMaxWidth()
        )
    }
}
```

**Обработка вырезов:**
Адаптация контента под вырезы экрана (notch, camera hole).

```kotlin
@Composable
fun DisplayCutoutExample() {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black) // Фон за вырезом
    ) {
        TopAppBar(
            title = { Text("Title") },
            modifier = Modifier
                .windowInsetsPadding(WindowInsets.displayCutout) // Избегает выреза
                .windowInsetsPadding(WindowInsets.statusBars)
        )
    }
}
```

**Immersive режим:**
Скрытие системных баров для полноэкранного опыта.

```kotlin
@Composable
fun ImmersiveContent() {
    val view = LocalView.current
    var isImmersive by remember { mutableStateOf(false) }

    DisposableEffect(isImmersive) {
        val window = (view.context as Activity).window
        val insetsController = WindowCompat.getInsetsController(window, view)

        if (isImmersive) {
            insetsController.hide(WindowInsetsCompat.Type.systemBars())
        } else {
            insetsController.show(WindowInsetsCompat.Type.systemBars())
        }

        onDispose {
            insetsController.show(WindowInsetsCompat.Type.systemBars())
        }
    }
}
```

## Answer (EN)

**WindowInsets Theory:**
WindowInsets provide information about system UI elements (status bar, navigation bar, keyboard, cutouts), allowing apps to adapt content and create immersive edge-to-edge experiences.

**Edge-to-Edge Activation:**
Allows apps to draw behind system bars for full-screen experience.

```kotlin
// Enable edge-to-edge
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge() // Allows drawing behind system bars
        setContent { MainScreen() }
    }
}
```

**WindowInsets in Compose:**
Access to different inset types for adapting UI to system elements.

```kotlin
@Composable
fun WindowInsetsExample() {
    val systemBars = WindowInsets.systemBars
    val statusBarHeight = systemBars.asPaddingValues().calculateTopPadding()
    val navigationBarHeight = systemBars.asPaddingValues().calculateBottomPadding()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .windowInsetsPadding(WindowInsets.systemBars) // Automatic padding
    ) {
        Text("Content avoids system bars")
    }
}
```

**WindowInsets Types:**
Different insets for various system elements and safe areas.

```kotlin
// Main inset types
val systemBars = WindowInsets.systemBars // Status + Navigation
val statusBars = WindowInsets.statusBars // Status bar only
val navigationBars = WindowInsets.navigationBars // Navigation bar only
val ime = WindowInsets.ime // Keyboard
val displayCutout = WindowInsets.displayCutout // Cutouts (notch)
val safeDrawing = WindowInsets.safeDrawing // Safe drawing area
```

**Keyboard Handling:**
Automatic UI adaptation when keyboard appears.

```kotlin
@Composable
fun KeyboardHandlingExample() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .imePadding() // Automatically lifts content above keyboard
    ) {
        LazyColumn(modifier = Modifier.weight(1f)) {
            items(50) { Text("Item $it") }
        }

        TextField(
            value = text,
            onValueChange = { text = it },
            modifier = Modifier.fillMaxWidth()
        )
    }
}
```

**Cutout Handling:**
Adapting content to screen cutouts (notch, camera hole).

```kotlin
@Composable
fun DisplayCutoutExample() {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black) // Background behind cutout
    ) {
        TopAppBar(
            title = { Text("Title") },
            modifier = Modifier
                .windowInsetsPadding(WindowInsets.displayCutout) // Avoids cutout
                .windowInsetsPadding(WindowInsets.statusBars)
        )
    }
}
```

**Immersive Mode:**
Hiding system bars for full-screen experience.

```kotlin
@Composable
fun ImmersiveContent() {
    val view = LocalView.current
    var isImmersive by remember { mutableStateOf(false) }

    DisposableEffect(isImmersive) {
        val window = (view.context as Activity).window
        val insetsController = WindowCompat.getInsetsController(window, view)

        if (isImmersive) {
            insetsController.hide(WindowInsetsCompat.Type.systemBars())
        } else {
            insetsController.show(WindowInsetsCompat.Type.systemBars())
        }

        onDispose {
            insetsController.show(WindowInsetsCompat.Type.systemBars())
        }
    }
}
```

---

## Follow-ups

- How do you handle WindowInsets in landscape orientation?
- What's the difference between windowInsetsPadding and padding?
- How do you implement edge-to-edge with bottom sheets?
- What are the performance implications of WindowInsets?

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - App components
- [[q-compose-basics--android--easy]] - Compose basics

### Related (Same Level)
- [[q-compose-navigation-advanced--android--medium]] - Compose navigation
- [[q-compose-scaffold--android--medium]] - Compose Scaffold
- [[q-compose-custom-layout--jetpack-compose--hard]] - Custom layouts

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Performance optimization
- [[q-android-runtime-internals--android--hard]] - Runtime internals
