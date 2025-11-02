---
id: android-062
title: "WindowInsets & Edge-to-Edge / WindowInsets и Edge-to-Edge"
aliases: ["WindowInsets & Edge-to-Edge", "WindowInsets и Edge-to-Edge"]
topic: android
subtopics: [ui-compose, ui-views]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-windowinsets, q-compose-navigation-advanced--android--medium, q-compose-scaffold--android--medium]
created: 2025-10-12
updated: 2025-10-29
tags: [android/ui-compose, android/ui-views, windowinsets, edge-to-edge, system-ui, immersive, difficulty/medium]
sources: ["https://developer.android.com/develop/ui/views/layout/edge-to-edge"]
date created: Wednesday, October 29th 2025, 1:00:50 pm
date modified: Thursday, October 30th 2025, 3:16:49 pm
---

# Вопрос (RU)
> Что такое WindowInsets и как реализовать edge-to-edge дизайн?

# Question (EN)
> What are WindowInsets and how to implement edge-to-edge design?

---

## Ответ (RU)

**Концепция:**
WindowInsets предоставляют информацию о системных UI элементах (status bar, navigation bar, клавиатура, вырезы экрана), позволяя приложению адаптировать контент под любые конфигурации устройств и создавать иммерсивный edge-to-edge опыт.

**Edge-to-Edge в Compose:**

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge() // ✅ Позволяет рисовать за системными барами
        setContent { MainScreen() }
    }
}

@Composable
fun MainScreen() {
    Scaffold(
        modifier = Modifier
            .fillMaxSize()
            .windowInsetsPadding(WindowInsets.systemBars) // ✅ Автоматический padding
    ) { paddingValues ->
        // ❌ НЕ используйте .padding(paddingValues) дважды
        Content(paddingValues)
    }
}
```

**Основные типы WindowInsets:**

```kotlin
// Системные элементы
WindowInsets.systemBars       // Status + Navigation bars
WindowInsets.statusBars        // Только status bar
WindowInsets.navigationBars    // Только navigation bar

// Динамические элементы
WindowInsets.ime              // ✅ Клавиатура (Input Method Editor)
WindowInsets.displayCutout    // Вырезы экрана (notch, camera hole)

// Безопасные области
WindowInsets.safeDrawing      // ✅ Комбинация всех системных insets
WindowInsets.safeGestures     // Зоны системных жестов
```

**Обработка клавиатуры:**

```kotlin
@Composable
fun ChatScreen() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .imePadding() // ✅ Автоматически адаптируется под клавиатуру
    ) {
        LazyColumn(modifier = Modifier.weight(1f)) {
            items(messages) { MessageItem(it) }
        }

        TextField(
            value = text,
            onValueChange = { text = it },
            // ❌ НЕ добавляйте .windowInsetsPadding(WindowInsets.ime) вручную
            modifier = Modifier.fillMaxWidth()
        )
    }
}
```

**Immersive режим для медиа:**

```kotlin
@Composable
fun VideoPlayer() {
    val view = LocalView.current
    val insetsController = remember {
        WindowCompat.getInsetsController(
            (view.context as Activity).window,
            view
        )
    }

    DisposableEffect(Unit) {
        // ✅ Скрываем системные бары для полноэкранного видео
        insetsController.hide(WindowInsetsCompat.Type.systemBars())
        insetsController.systemBarsBehavior =
            WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE

        onDispose {
            insetsController.show(WindowInsetsCompat.Type.systemBars())
        }
    }
}
```

## Answer (EN)

**Concept:**
WindowInsets provide information about system UI elements (status bar, navigation bar, keyboard, screen cutouts), allowing apps to adapt content for any device configuration and create immersive edge-to-edge experiences.

**Edge-to-Edge in Compose:**

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge() // ✅ Allows drawing behind system bars
        setContent { MainScreen() }
    }
}

@Composable
fun MainScreen() {
    Scaffold(
        modifier = Modifier
            .fillMaxSize()
            .windowInsetsPadding(WindowInsets.systemBars) // ✅ Automatic padding
    ) { paddingValues ->
        // ❌ DON'T use .padding(paddingValues) twice
        Content(paddingValues)
    }
}
```

**Main WindowInsets Types:**

```kotlin
// System elements
WindowInsets.systemBars       // Status + Navigation bars
WindowInsets.statusBars        // Status bar only
WindowInsets.navigationBars    // Navigation bar only

// Dynamic elements
WindowInsets.ime              // ✅ Keyboard (Input Method Editor)
WindowInsets.displayCutout    // Screen cutouts (notch, camera hole)

// Safe areas
WindowInsets.safeDrawing      // ✅ Combination of all system insets
WindowInsets.safeGestures     // System gesture zones
```

**Keyboard Handling:**

```kotlin
@Composable
fun ChatScreen() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .imePadding() // ✅ Automatically adapts to keyboard
    ) {
        LazyColumn(modifier = Modifier.weight(1f)) {
            items(messages) { MessageItem(it) }
        }

        TextField(
            value = text,
            onValueChange = { text = it },
            // ❌ DON'T add .windowInsetsPadding(WindowInsets.ime) manually
            modifier = Modifier.fillMaxWidth()
        )
    }
}
```

**Immersive Mode for Media:**

```kotlin
@Composable
fun VideoPlayer() {
    val view = LocalView.current
    val insetsController = remember {
        WindowCompat.getInsetsController(
            (view.context as Activity).window,
            view
        )
    }

    DisposableEffect(Unit) {
        // ✅ Hide system bars for fullscreen video
        insetsController.hide(WindowInsetsCompat.Type.systemBars())
        insetsController.systemBarsBehavior =
            WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE

        onDispose {
            insetsController.show(WindowInsetsCompat.Type.systemBars())
        }
    }
}
```

---

## Follow-ups

- How do you handle WindowInsets in landscape orientation with different aspect ratios?
- What's the difference between `windowInsetsPadding()` and `systemBarsPadding()`?
- How do you implement edge-to-edge with BottomSheet and Modal dialogs?
- What are the performance implications of WindowInsets recomposition?
- How do you test edge-to-edge layouts across different device configurations?

## References

- [[c-windowinsets]] - WindowInsets concept note
- [[c-compose-modifiers]] - Compose Modifier system
- [[c-android-system-ui]] - Android System UI overview
- [Edge-to-Edge Guide](https://developer.android.com/develop/ui/views/layout/edge-to-edge)
- [WindowInsets API Reference](https://developer.android.com/reference/kotlin/androidx/compose/foundation/layout/WindowInsets)

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
