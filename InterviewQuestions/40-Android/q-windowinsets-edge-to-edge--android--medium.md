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
related: [c-jetpack-compose]
created: 2025-10-12
updated: 2025-10-29
tags: [android/ui-compose, android/ui-views, difficulty/medium, edge-to-edge, immersive, system-ui, windowinsets]
sources: ["https://developer.android.com/develop/ui/views/layout/edge-to-edge"]
date created: Saturday, November 1st 2025, 1:26:42 pm
date modified: Tuesday, November 25th 2025, 8:53:55 pm
---

# Вопрос (RU)
> Что такое WindowInsets и как реализовать edge-to-edge дизайн?

# Question (EN)
> What are WindowInsets and how to implement edge-to-edge design?

---

## Ответ (RU)

**Концепция:**
WindowInsets предоставляют информацию о системных UI элементах (status bar, navigation bar, клавиатура, вырезы экрана), позволяя приложению адаптировать контент под любые конфигурации устройств и создавать иммерсивный edge-to-edge опыт. Суть edge-to-edge — уметь либо рисовать контент под системными элементами, либо корректно отступать от них, используя данные insets вместо жёстких значений.

**Edge-to-Edge в Compose:**

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge() // ✅ Позволяет рисовать за системными барами и настраивает дефолтные insets
        setContent { MainScreen() }
    }
}

@Composable
fun MainScreen() {
    Scaffold { paddingValues ->
        // ✅ Используем paddingValues от Scaffold, в который уже входят системные отступы,
        // если Scaffold настроен с учётом edge-to-edge.
        Content(Modifier.padding(paddingValues))
    }
}
```

Если нужно вручную контролировать отступы под системные бары (например, для кастомного layout), применяйте WindowInsets к конкретным контейнерам:

```kotlin
@Composable
fun EdgeToEdgeScreen() {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .windowInsetsPadding(WindowInsets.systemBars) // ✅ Добавляем отступы один раз в нужном месте
    ) {
        Content(Modifier.fillMaxSize())
    }
}
```

**Основные типы WindowInsets:**

```kotlin
// Системные элементы
WindowInsets.systemBars       // Status + Navigation bars
WindowInsets.statusBars       // Только status bar
WindowInsets.navigationBars   // Только navigation bar

// Динамические элементы
WindowInsets.ime              // ✅ Клавиатура (Input Method Editor)
WindowInsets.displayCutout    // Вырезы экрана (notch, camera hole)

// Безопасные области
WindowInsets.safeDrawing      // ✅ Области, где безопасно располагать основной контент
WindowInsets.safeGestures     // Зоны системных жестов (для учета навигационных жестов)
```

Важно: не дублируйте одни и те же Insets в разных местах (например, `systemBarsPadding` + `windowInsetsPadding(WindowInsets.systemBars)` на одном и том же контейнере).

**Обработка клавиатуры:**

```kotlin
@Composable
fun ChatScreen() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .imePadding() // ✅ Контент надстраивается над клавиатурой
    ) {
        LazyColumn(modifier = Modifier.weight(1f)) {
            items(messages) { MessageItem(it) }
        }

        TextField(
            value = text,
            onValueChange = { text = it },
            // ✅ Не дублируем Insets: если используем imePadding() на родителе,
            // не добавляем .windowInsetsPadding(WindowInsets.ime) на TextField.
            modifier = Modifier.fillMaxWidth()
        )
    }
}
```

Если `imePadding()` не подходит (сложная раскладка, несколько панелей), можно использовать `WindowInsets.ime` вручную, но важно следить, чтобы Insets не применялись дважды.

**Immersive режим для медиа:**

```kotlin
@Composable
fun VideoPlayer() {
    val view = LocalView.current
    val activity = LocalContext.current as Activity // Требуется контекст Activity
    val insetsController = remember {
        WindowCompat.getInsetsController(activity.window, view)
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

На новых API поведение системных баров может отличаться; важно тестировать жесты и видимость баров на актуальных версиях Android.

См. также: [[c-jetpack-compose]].

## Answer (EN)

**Concept:**
WindowInsets provide information about system UI elements (status bar, navigation bar, keyboard, screen cutouts), enabling apps to adapt content to any device configuration and build immersive edge-to-edge experiences. The key idea: either draw behind system bars or offset your content using insets instead of hardcoded dimensions.

**Edge-to-Edge in Compose:**

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge() // ✅ Enables drawing behind system bars and configures sensible defaults
        setContent { MainScreen() }
    }
}

@Composable
fun MainScreen() {
    Scaffold { paddingValues ->
        // ✅ Use Scaffold's paddingValues, which already accounts for insets
        // when Scaffold is configured for edge-to-edge.
        Content(Modifier.padding(paddingValues))
    }
}
```

If you need manual control over system bar insets (e.g., for a custom layout), apply WindowInsets to specific containers:

```kotlin
@Composable
fun EdgeToEdgeScreen() {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .windowInsetsPadding(WindowInsets.systemBars) // ✅ Apply systemBars insets once at the appropriate level
    ) {
        Content(Modifier.fillMaxSize())
    }
}
```

**Main WindowInsets Types:**

```kotlin
// System elements
WindowInsets.systemBars       // Status + Navigation bars
WindowInsets.statusBars       // Status bar only
WindowInsets.navigationBars   // Navigation bar only

// Dynamic elements
WindowInsets.ime              // ✅ Keyboard (Input Method Editor)
WindowInsets.displayCutout    // Screen cutouts (notch, camera hole)

// Safe areas
WindowInsets.safeDrawing      // ✅ Areas where it's safe to place primary content
WindowInsets.safeGestures     // System gesture zones (consider for gesture navigation)
```

Important: avoid stacking the same insets multiple times (e.g., `systemBarsPadding` plus `windowInsetsPadding(WindowInsets.systemBars)` on the same container).

**Keyboard Handling:**

```kotlin
@Composable
fun ChatScreen() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .imePadding() // ✅ Automatically positions content above the keyboard
    ) {
        LazyColumn(modifier = Modifier.weight(1f)) {
            items(messages) { MessageItem(it) }
        }

        TextField(
            value = text,
            onValueChange = { text = it },
            // ✅ Don't duplicate insets: if imePadding() is applied to the parent,
            // skip .windowInsetsPadding(WindowInsets.ime) on the TextField.
            modifier = Modifier.fillMaxWidth()
        )
    }
}
```

If `imePadding()` alone is not sufficient (complex layouts, multiple bottom elements), you can work with `WindowInsets.ime` directly, but ensure you are not applying the IME insets twice.

**Immersive Mode for Media:**

```kotlin
@Composable
fun VideoPlayer() {
    val view = LocalView.current
    val activity = LocalContext.current as Activity // Requires an Activity context
    val insetsController = remember {
        WindowCompat.getInsetsController(activity.window, view)
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

On newer API levels, system bar behavior and gesture interactions can vary; always verify immersive behavior on target Android versions.

See also: [[c-jetpack-compose]].

---

## Дополнительные Вопросы (RU)

- Как вы обрабатываете WindowInsets в ландшафтной ориентации и на устройствах с разными соотношениями сторон?
- В чем разница между `windowInsetsPadding()` и `systemBarsPadding()`?
- Как реализовать edge-to-edge при использовании BottomSheet и модальных диалогов?
- Каковы последствия для производительности при частых изменениях WindowInsets и перерасчетах компоновки?
- Как вы тестируете edge-to-edge разметку на различных конфигурациях устройств?

## Follow-ups

- How do you handle WindowInsets in landscape orientation with different aspect ratios?
- What's the difference between `windowInsetsPadding()` and `systemBarsPadding()`?
- How do you implement edge-to-edge with BottomSheet and Modal dialogs?
- What are the performance implications of WindowInsets recomposition?
- How do you test edge-to-edge layouts across different device configurations?

## Ссылки (RU)

- [Руководство по Edge-to-Edge](https://developer.android.com/develop/ui/views/layout/edge-to-edge)
- [Справочник по WindowInsets API](https://developer.android.com/reference/kotlin/androidx/compose/foundation/layout/WindowInsets)

## References

- [Edge-to-Edge Guide](https://developer.android.com/develop/ui/views/layout/edge-to-edge)
- [WindowInsets API Reference](https://developer.android.com/reference/kotlin/androidx/compose/foundation/layout/WindowInsets)

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-android-app-components--android--easy]] - Компоненты Android-приложения

### Связанные (средний уровень)
- [[q-compose-navigation-advanced--android--medium]] - Навигация в Compose (продвинутая)
- [[q-compose-custom-layout--android--hard]] - Кастомные layouts в Compose

### Продвинутые (сложнее)
- [[q-compose-performance-optimization--android--hard]] - Оптимизация производительности в Compose
- [[q-android-runtime-internals--android--hard]] - Внутреннее устройство Android Runtime

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - App components

### Related (Same Level)
- [[q-compose-navigation-advanced--android--medium]] - Compose navigation
- [[q-compose-custom-layout--android--hard]] - Custom layouts

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Performance optimization
- [[q-android-runtime-internals--android--hard]] - Runtime internals
