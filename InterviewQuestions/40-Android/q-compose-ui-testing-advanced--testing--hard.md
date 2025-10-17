---
id: 20251017-115621
title: "Compose Ui Testing Advanced"
topic: testing
difficulty: hard
status: draft
created: 2025-10-15
tags: [compose-testing, ui-testing, semantics, accessibility, difficulty/hard]
---
# Advanced Compose UI Testing

**English**: Test complex Compose UI scenarios: animations, gestures, semantic matchers, and accessibility. Handle async operations.

**Russian**: Тестируйте сложные UI сценарии в Compose: анимации, жесты, semantic matchers и доступность. Обрабатывайте async операции.

## Answer (EN)

Compose UI testing uses the semantic tree rather than view hierarchy, enabling more robust and maintainable tests. Advanced testing requires understanding semantics, custom matchers, and async handling.

### Basic Compose Test Setup

```kotlin
dependencies {
    androidTestImplementation("androidx.compose.ui:ui-test-junit4:1.5.4")
    debugImplementation("androidx.compose.ui:ui-test-manifest:1.5.4")
}

class LoginScreenTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun loginScreen_displaysCorrectly() {
        composeTestRule.setContent {
            LoginScreen()
        }

        composeTestRule.onNodeWithText("Login").assertExists()
        composeTestRule.onNodeWithText("Email").assertExists()
        composeTestRule.onNodeWithText("Password").assertExists()
    }
}
```

### Semantic Tree and Matchers

Compose tests use the semantic tree, not the View hierarchy:

```kotlin
@Test
fun semanticMatchers_examples() {
    composeTestRule.setContent {
        Column {
            Text("Title", modifier = Modifier.testTag("title"))
            Button(onClick = {}) {
                Text("Click Me")
            }
            TextField(
                value = "",
                onValueChange = {},
                label = { Text("Input") }
            )
        }
    }

    // Find by test tag
    composeTestRule.onNodeWithTag("title").assertExists()

    // Find by text
    composeTestRule.onNodeWithText("Title").assertExists()

    // Find by content description
    composeTestRule.onNodeWithContentDescription("Close").assertExists()

    // Find parent/children
    composeTestRule
        .onNodeWithText("Click Me")
        .onParent()
        .assertHasClickAction()

    // Find all nodes
    composeTestRule
        .onAllNodesWithText("Item")
        .assertCountEquals(3)
}
```

### Custom Semantic Matchers

```kotlin
// Custom matcher for checking if node is enabled
fun isEnabled(): SemanticsMatcher {
    return SemanticsMatcher("is enabled") {
        it.config.getOrElse(SemanticsProperties.Disabled) { null } == null
    }
}

// Custom matcher for specific state
fun hasProgressValue(value: Float): SemanticsMatcher {
    return SemanticsMatcher("has progress value $value") {
        val current = it.config.getOrElse(SemanticsProperties.ProgressBarRangeInfo) {
            return@SemanticsMatcher false
        }
        current.current == value
    }
}

// Custom matcher for text color (requires custom semantics)
fun hasTextColor(color: Color): SemanticsMatcher {
    return SemanticsMatcher("has text color ${color.toArgb()}") {
        val textColor = it.config.getOrElse(CustomSemantics.TextColor) { return@SemanticsMatcher false }
        textColor == color
    }
}

// Usage
@Test
fun customMatchers_test() {
    composeTestRule.setContent {
        Button(onClick = {}, enabled = false) {
            Text("Disabled Button")
        }
    }

    composeTestRule
        .onNodeWithText("Disabled Button")
        .assert(!isEnabled())
}
```

### Testing User Interactions

```kotlin
@Test
fun userInteractions_test() {
    var clickCount = 0

    composeTestRule.setContent {
        Column {
            var text by remember { mutableStateOf("") }

            TextField(
                value = text,
                onValueChange = { text = it },
                modifier = Modifier.testTag("input")
            )

            Button(
                onClick = { clickCount++ },
                modifier = Modifier.testTag("button")
            ) {
                Text("Click")
            }

            Text("Clicks: $clickCount")
        }
    }

    // Type text
    composeTestRule
        .onNodeWithTag("input")
        .performTextInput("Hello")

    composeTestRule
        .onNodeWithText("Hello")
        .assertExists()

    // Click button
    composeTestRule
        .onNodeWithTag("button")
        .performClick()

    composeTestRule
        .onNodeWithText("Clicks: 1")
        .assertExists()

    // Clear text
    composeTestRule
        .onNodeWithTag("input")
        .performTextClearance()

    // Replace text
    composeTestRule
        .onNodeWithTag("input")
        .performTextReplacement("New Text")
}
```

### Testing Gestures

```kotlin
@Test
fun gestures_swipe() {
    var swipeCount = 0

    composeTestRule.setContent {
        Box(
            modifier = Modifier
                .size(200.dp)
                .testTag("swipeable")
                .swipeable(
                    state = rememberSwipeableState(0),
                    anchors = mapOf(0f to 0, 200f to 1),
                    thresholds = { _, _ -> FractionalThreshold(0.5f) },
                    orientation = Orientation.Horizontal
                )
        ) {
            Text("Swipe me")
        }
    }

    // Swipe left to right
    composeTestRule
        .onNodeWithTag("swipeable")
        .performTouchInput {
            swipeLeft()
        }

    // Swipe with custom parameters
    composeTestRule
        .onNodeWithTag("swipeable")
        .performTouchInput {
            swipe(
                start = Offset(0f, centerY),
                end = Offset(width.toFloat(), centerY),
                durationMillis = 500
            )
        }
}

@Test
fun gestures_scroll() {
    composeTestRule.setContent {
        LazyColumn(modifier = Modifier.testTag("list")) {
            items(100) { index ->
                Text("Item $index", modifier = Modifier.testTag("item_$index"))
            }
        }
    }

    // Scroll to specific item
    composeTestRule
        .onNodeWithTag("list")
        .performScrollToNode(hasTestTag("item_50"))

    composeTestRule
        .onNodeWithTag("item_50")
        .assertIsDisplayed()

    // Scroll by amount
    composeTestRule
        .onNodeWithTag("list")
        .performTouchInput {
            swipeUp()
        }
}

@Test
fun gestures_longClick() {
    var longClicked = false

    composeTestRule.setContent {
        Box(
            modifier = Modifier
                .testTag("box")
                .combinedClickable(
                    onClick = {},
                    onLongClick = { longClicked = true }
                )
        ) {
            Text("Long click me")
        }
    }

    composeTestRule
        .onNodeWithTag("box")
        .performTouchInput {
            longClick()
        }

    assert(longClicked)
}
```

### Testing Animations

```kotlin
@Test
fun animation_waitUntilComplete() {
    var isExpanded by mutableStateOf(false)

    composeTestRule.setContent {
        val height by animateDpAsState(
            targetValue = if (isExpanded) 200.dp else 100.dp,
            label = "height"
        )

        Box(
            modifier = Modifier
                .testTag("animated_box")
                .size(100.dp, height)
                .background(Color.Blue)
        )
    }

    // Trigger animation
    isExpanded = true

    // Wait for animation to complete
    composeTestRule.waitForIdle()

    // Or use mainClock
    composeTestRule.mainClock.advanceTimeBy(500)

    composeTestRule
        .onNodeWithTag("animated_box")
        .assertHeightIsEqualTo(200.dp)
}

@Test
fun animation_autoAdvance() {
    composeTestRule.mainClock.autoAdvance = false

    var count by mutableStateOf(0)

    composeTestRule.setContent {
        LaunchedEffect(Unit) {
            delay(1000)
            count = 1
            delay(1000)
            count = 2
        }

        Text("Count: $count")
    }

    // Initially 0
    composeTestRule.onNodeWithText("Count: 0").assertExists()

    // Advance time
    composeTestRule.mainClock.advanceTimeBy(1000)
    composeTestRule.waitForIdle()

    composeTestRule.onNodeWithText("Count: 1").assertExists()

    // Advance more
    composeTestRule.mainClock.advanceTimeBy(1000)
    composeTestRule.waitForIdle()

    composeTestRule.onNodeWithText("Count: 2").assertExists()
}
```

### Testing Async Operations

```kotlin
@Test
fun asyncOperations_withTimeout() {
    composeTestRule.setContent {
        var data by remember { mutableStateOf<String?>(null) }

        LaunchedEffect(Unit) {
            delay(2000)
            data = "Loaded"
        }

        if (data == null) {
            CircularProgressIndicator(modifier = Modifier.testTag("loading"))
        } else {
            Text(data!!)
        }
    }

    // Assert loading state
    composeTestRule
        .onNodeWithTag("loading")
        .assertExists()

    // Wait for data to load
    composeTestRule.waitUntil(timeoutMillis = 3000) {
        composeTestRule
            .onAllNodesWithText("Loaded")
            .fetchSemanticsNodes()
            .isNotEmpty()
    }

    composeTestRule
        .onNodeWithText("Loaded")
        .assertExists()
}

@Test
fun asyncOperations_withStateFlow() = runTest {
    val viewModel = TestViewModel()

    composeTestRule.setContent {
        val state by viewModel.uiState.collectAsState()

        when (state) {
            is UiState.Loading -> CircularProgressIndicator()
            is UiState.Success -> Text((state as UiState.Success).data)
            is UiState.Error -> Text("Error")
        }
    }

    // Initially loading
    composeTestRule.onNode(isProgressIndicator()).assertExists()

    // Trigger data load
    viewModel.loadData()
    advanceUntilIdle()

    composeTestRule
        .onNodeWithText("Data loaded")
        .assertExists()
}
```

### Testing Accessibility

```kotlin
@Test
fun accessibility_contentDescription() {
    composeTestRule.setContent {
        Icon(
            imageVector = Icons.Default.Close,
            contentDescription = "Close dialog",
            modifier = Modifier.testTag("close_icon")
        )
    }

    composeTestRule
        .onNodeWithTag("close_icon")
        .assertContentDescriptionEquals("Close dialog")
}

@Test
fun accessibility_semanticProperties() {
    composeTestRule.setContent {
        Button(
            onClick = {},
            modifier = Modifier.semantics {
                contentDescription = "Submit form"
                stateDescription = "Ready to submit"
            }
        ) {
            Text("Submit")
        }
    }

    composeTestRule
        .onNode(
            hasContentDescription("Submit form") and
            hasStateDescription("Ready to submit")
        )
        .assertExists()
        .assertHasClickAction()
}

@Test
fun accessibility_mergingSemantics() {
    composeTestRule.setContent {
        Row(
            modifier = Modifier
                .testTag("row")
                .semantics(mergeDescendants = true) {}
        ) {
            Icon(Icons.Default.Star, contentDescription = "Rating")
            Text("4.5")
            Text("stars")
        }
    }

    // With merging, all text is combined
    composeTestRule
        .onNodeWithTag("row")
        .assert(hasText("4.5 stars", substring = false))
}
```

### Testing Lists and Collections

```kotlin
@Test
fun lists_filtering() {
    val items = listOf("Apple", "Banana", "Cherry", "Date")

    composeTestRule.setContent {
        var filter by remember { mutableStateOf("") }

        Column {
            TextField(
                value = filter,
                onValueChange = { filter = it },
                modifier = Modifier.testTag("filter")
            )

            LazyColumn {
                items(items.filter { it.contains(filter, ignoreCase = true) }) { item ->
                    Text(item)
                }
            }
        }
    }

    // Initially all items visible
    composeTestRule.onAllNodesWithText("Apple").assertCountEquals(1)
    composeTestRule.onAllNodesWithText("Banana").assertCountEquals(1)

    // Filter
    composeTestRule
        .onNodeWithTag("filter")
        .performTextInput("a")

    // Only items with 'a' visible
    composeTestRule.onNodeWithText("Apple").assertExists()
    composeTestRule.onNodeWithText("Banana").assertExists()
    composeTestRule.onNodeWithText("Cherry").assertDoesNotExist()
}

@Test
fun lists_infiniteScroll() {
    var items by mutableStateOf((0..20).toList())
    var isLoading by mutableStateOf(false)

    composeTestRule.setContent {
        LazyColumn(modifier = Modifier.testTag("list")) {
            items(items) { item ->
                Text("Item $item", modifier = Modifier.testTag("item_$item"))
            }

            if (isLoading) {
                item {
                    CircularProgressIndicator(modifier = Modifier.testTag("loader"))
                }
            }
        }
    }

    // Scroll to bottom
    composeTestRule
        .onNodeWithTag("list")
        .performScrollToNode(hasTestTag("item_20"))

    // Simulate load more
    isLoading = true
    composeTestRule.waitForIdle()

    composeTestRule.onNodeWithTag("loader").assertExists()

    // Add more items
    items = (0..40).toList()
    isLoading = false
    composeTestRule.waitForIdle()

    // Verify new items exist
    composeTestRule
        .onNodeWithTag("list")
        .performScrollToNode(hasTestTag("item_40"))

    composeTestRule.onNodeWithTag("item_40").assertIsDisplayed()
}
```

### Complete Test Suite Example

```kotlin
@HiltAndroidTest
class CompleteScreenTest {
    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @get:Rule(order = 1)
    val composeTestRule = createAndroidComposeRule<MainActivity>()

    private lateinit var repository: FakeRepository

    @Before
    fun setup() {
        hiltRule.inject()
        repository = FakeRepository()
    }

    @Test
    fun productList_loadingState() {
        repository.setDelay(1000)

        composeTestRule.setContent {
            ProductListScreen(viewModel = ProductViewModel(repository))
        }

        // Assert loading indicator shown
        composeTestRule
            .onNode(isProgressIndicator())
            .assertExists()
    }

    @Test
    fun productList_successState() {
        repository.setProducts(
            listOf(
                Product("1", "Product 1", 10.0),
                Product("2", "Product 2", 20.0)
            )
        )

        composeTestRule.setContent {
            ProductListScreen(viewModel = ProductViewModel(repository))
        }

        composeTestRule.waitForIdle()

        // Assert products displayed
        composeTestRule.onNodeWithText("Product 1").assertIsDisplayed()
        composeTestRule.onNodeWithText("Product 2").assertIsDisplayed()
        composeTestRule.onNodeWithText("$10.00").assertIsDisplayed()
    }

    @Test
    fun productList_errorState() {
        repository.setError(Exception("Network error"))

        composeTestRule.setContent {
            ProductListScreen(viewModel = ProductViewModel(repository))
        }

        composeTestRule.waitForIdle()

        // Assert error message
        composeTestRule.onNodeWithText("Network error").assertIsDisplayed()

        // Click retry
        composeTestRule.onNodeWithText("Retry").performClick()

        // Loading indicator should appear again
        composeTestRule.onNode(isProgressIndicator()).assertExists()
    }

    @Test
    fun productList_clickProduct() {
        repository.setProducts(listOf(Product("1", "Product 1", 10.0)))
        var navigatedToId: String? = null

        composeTestRule.setContent {
            ProductListScreen(
                viewModel = ProductViewModel(repository),
                onProductClick = { navigatedToId = it }
            )
        }

        composeTestRule.waitForIdle()

        composeTestRule.onNodeWithText("Product 1").performClick()

        assertEquals("1", navigatedToId)
    }

    @Test
    fun productList_accessibility() {
        repository.setProducts(listOf(Product("1", "Product 1", 10.0)))

        composeTestRule.setContent {
            ProductListScreen(viewModel = ProductViewModel(repository))
        }

        composeTestRule.waitForIdle()

        // Check accessibility properties
        composeTestRule
            .onNodeWithText("Product 1")
            .assertHasClickAction()
            .assert(hasClickLabel("View product details"))
    }
}
```

### Best Practices

1. **Use testTag for stable element identification**
2. **Prefer semantic matchers over text when possible**
3. **Test accessibility properties** (content descriptions, click actions)
4. **Handle async operations** with waitUntil or waitForIdle
5. **Test animations** with mainClock control
6. **Use custom matchers** for complex assertions
7. **Test error states and edge cases**
8. **Mock dependencies** with Hilt or manual injection
9. **Keep tests isolated** and independent
10. **Test user flows**, not implementation details

## Ответ (RU)

Тестирование UI в Compose использует семантическое дерево (semantic tree) вместо иерархии View, что обеспечивает более надежные и поддерживаемые тесты. Продвинутое тестирование требует понимания семантики, создания пользовательских matchers и обработки асинхронных операций.

### Базовая настройка Compose тестов

Для тестирования Compose UI необходимо добавить зависимости и создать тестовое правило:

```kotlin
dependencies {
    androidTestImplementation("androidx.compose.ui:ui-test-junit4:1.5.4")
    debugImplementation("androidx.compose.ui:ui-test-manifest:1.5.4")
}

class LoginScreenTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun loginScreen_displaysCorrectly() {
        // Устанавливаем контент для тестирования
        composeTestRule.setContent {
            LoginScreen()
        }

        // Проверяем наличие элементов
        composeTestRule.onNodeWithText("Login").assertExists()
        composeTestRule.onNodeWithText("Email").assertExists()
        composeTestRule.onNodeWithText("Password").assertExists()
    }
}
```

**Ключевые компоненты**:
- `createComposeRule()` - создает правило для тестирования Compose UI
- `setContent {}` - устанавливает composable для тестирования
- `onNodeWithText()` - находит узел по тексту
- `assertExists()` - проверяет существование узла

### Семантическое дерево и сопоставление (Matchers)

Compose тесты используют семантическое дерево, а не иерархию View. Это дерево содержит информацию о UI элементах, доступную для accessibility сервисов и тестов:

```kotlin
@Test
fun semanticMatchers_examples() {
    composeTestRule.setContent {
        Column {
            Text("Title", modifier = Modifier.testTag("title"))
            Button(onClick = {}) {
                Text("Click Me")
            }
            TextField(
                value = "",
                onValueChange = {},
                label = { Text("Input") }
            )
        }
    }

    // Поиск по тестовому тегу (наиболее надежный способ)
    composeTestRule.onNodeWithTag("title").assertExists()

    // Поиск по тексту
    composeTestRule.onNodeWithText("Title").assertExists()

    // Поиск по описанию контента (для accessibility)
    composeTestRule.onNodeWithContentDescription("Close").assertExists()

    // Навигация по родителям/детям
    composeTestRule
        .onNodeWithText("Click Me")
        .onParent()  // Переходим к родительскому узлу (Button)
        .assertHasClickAction()

    // Поиск всех узлов с условием
    composeTestRule
        .onAllNodesWithText("Item")
        .assertCountEquals(3)  // Проверяем количество
}
```

**Основные методы поиска**:
- `onNodeWithTag()` - по тестовому тегу (рекомендуется)
- `onNodeWithText()` - по тексту
- `onNodeWithContentDescription()` - по описанию контента
- `onNode()` - с пользовательским matcher
- `onAllNodes()` - все узлы, соответствующие условию

### Пользовательские семантические Matchers

Создание собственных matchers для специфичных проверок:

```kotlin
// Проверка, включен ли элемент
fun isEnabled(): SemanticsMatcher {
    return SemanticsMatcher("is enabled") {
        // Элемент включен, если свойство Disabled не установлено
        it.config.getOrElse(SemanticsProperties.Disabled) { null } == null
    }
}

// Проверка значения прогресса
fun hasProgressValue(value: Float): SemanticsMatcher {
    return SemanticsMatcher("has progress value $value") {
        val current = it.config.getOrElse(SemanticsProperties.ProgressBarRangeInfo) {
            return@SemanticsMatcher false
        }
        current.current == value
    }
}

// Проверка цвета текста (требует кастомной семантики)
fun hasTextColor(color: Color): SemanticsMatcher {
    return SemanticsMatcher("has text color ${color.toArgb()}") {
        val textColor = it.config.getOrElse(CustomSemantics.TextColor) {
            return@SemanticsMatcher false
        }
        textColor == color
    }
}

// Использование пользовательских matchers
@Test
fun customMatchers_test() {
    composeTestRule.setContent {
        Button(onClick = {}, enabled = false) {
            Text("Disabled Button")
        }
    }

    // Проверяем, что кнопка отключена
    composeTestRule
        .onNodeWithText("Disabled Button")
        .assert(!isEnabled())  // Используем инверсию matcher
}
```

**Структура SemanticsMatcher**:
- Первый параметр - описание для отладки
- Лямбда принимает `SemanticsNode` и возвращает `Boolean`
- Используйте `config.getOrElse()` для безопасного доступа к свойствам

### Тестирование пользовательских взаимодействий

Имитация действий пользователя - клики, ввод текста, жесты:

```kotlin
@Test
fun userInteractions_test() {
    var clickCount = 0

    composeTestRule.setContent {
        Column {
            var text by remember { mutableStateOf("") }

            TextField(
                value = text,
                onValueChange = { text = it },
                modifier = Modifier.testTag("input")
            )

            Button(
                onClick = { clickCount++ },
                modifier = Modifier.testTag("button")
            ) {
                Text("Click")
            }

            Text("Clicks: $clickCount")
        }
    }

    // Ввод текста в поле
    composeTestRule
        .onNodeWithTag("input")
        .performTextInput("Hello")  // Добавляет текст к существующему

    // Проверяем, что текст отобразился
    composeTestRule
        .onNodeWithText("Hello")
        .assertExists()

    // Клик по кнопке
    composeTestRule
        .onNodeWithTag("button")
        .performClick()

    // Проверяем, что счетчик увеличился
    composeTestRule
        .onNodeWithText("Clicks: 1")
        .assertExists()

    // Очистка текста
    composeTestRule
        .onNodeWithTag("input")
        .performTextClearance()  // Удаляет весь текст

    // Замена текста
    composeTestRule
        .onNodeWithTag("input")
        .performTextReplacement("New Text")  // Заменяет весь текст
}
```

**Методы взаимодействия**:
- `performClick()` - клик по элементу
- `performTextInput()` - ввод текста (добавляет к существующему)
- `performTextReplacement()` - замена текста целиком
- `performTextClearance()` - очистка текста
- `performTouchInput {}` - пользовательские жесты

### Тестирование жестов

Compose тесты поддерживают различные жесты - свайпы, прокрутку, долгое нажатие:

```kotlin
@Test
fun gestures_swipe() {
    var swipeCount = 0

    composeTestRule.setContent {
        Box(
            modifier = Modifier
                .size(200.dp)
                .testTag("swipeable")
                .swipeable(
                    state = rememberSwipeableState(0),
                    anchors = mapOf(0f to 0, 200f to 1),
                    thresholds = { _, _ -> FractionalThreshold(0.5f) },
                    orientation = Orientation.Horizontal
                )
        ) {
            Text("Swipe me")
        }
    }

    // Свайп влево
    composeTestRule
        .onNodeWithTag("swipeable")
        .performTouchInput {
            swipeLeft()  // Предустановленный жест
        }

    // Свайп с пользовательскими параметрами
    composeTestRule
        .onNodeWithTag("swipeable")
        .performTouchInput {
            swipe(
                start = Offset(0f, centerY),  // Начальная точка
                end = Offset(width.toFloat(), centerY),  // Конечная точка
                durationMillis = 500  // Длительность жеста
            )
        }
}

@Test
fun gestures_scroll() {
    composeTestRule.setContent {
        LazyColumn(modifier = Modifier.testTag("list")) {
            items(100) { index ->
                Text("Item $index", modifier = Modifier.testTag("item_$index"))
            }
        }
    }

    // Прокрутка до конкретного элемента
    composeTestRule
        .onNodeWithTag("list")
        .performScrollToNode(hasTestTag("item_50"))

    // Проверяем, что элемент виден на экране
    composeTestRule
        .onNodeWithTag("item_50")
        .assertIsDisplayed()

    // Прокрутка жестом
    composeTestRule
        .onNodeWithTag("list")
        .performTouchInput {
            swipeUp()  // Прокрутка вверх
        }
}

@Test
fun gestures_longClick() {
    var longClicked = false

    composeTestRule.setContent {
        Box(
            modifier = Modifier
                .testTag("box")
                .combinedClickable(
                    onClick = {},
                    onLongClick = { longClicked = true }
                )
        ) {
            Text("Long click me")
        }
    }

    // Выполняем долгое нажатие
    composeTestRule
        .onNodeWithTag("box")
        .performTouchInput {
            longClick()  // Долгое нажатие с параметрами по умолчанию
        }

    // Проверяем результат
    assert(longClicked)
}
```

**Доступные жесты**:
- `swipeLeft()`, `swipeRight()`, `swipeUp()`, `swipeDown()` - базовые свайпы
- `swipe()` - свайп с пользовательскими параметрами
- `longClick()` - долгое нажатие
- `doubleClick()` - двойной клик
- `click()` - клик с указанием позиции
- `performScrollToNode()` - прокрутка до элемента

### Тестирование анимаций

Управление временем анимаций для детерминированных тестов:

```kotlin
@Test
fun animation_waitUntilComplete() {
    var isExpanded by mutableStateOf(false)

    composeTestRule.setContent {
        val height by animateDpAsState(
            targetValue = if (isExpanded) 200.dp else 100.dp,
            label = "height"
        )

        Box(
            modifier = Modifier
                .testTag("animated_box")
                .size(100.dp, height)
                .background(Color.Blue)
        )
    }

    // Запускаем анимацию
    isExpanded = true

    // Ожидаем завершения анимации
    composeTestRule.waitForIdle()  // Ждем, пока все анимации завершатся

    // Или используем mainClock для точного контроля
    composeTestRule.mainClock.advanceTimeBy(500)  // Продвигаем время на 500мс

    // Проверяем финальное состояние
    composeTestRule
        .onNodeWithTag("animated_box")
        .assertHeightIsEqualTo(200.dp)
}

@Test
fun animation_autoAdvance() {
    // Отключаем автоматическое продвижение времени
    composeTestRule.mainClock.autoAdvance = false

    var count by mutableStateOf(0)

    composeTestRule.setContent {
        LaunchedEffect(Unit) {
            delay(1000)  // Задержка 1 секунда
            count = 1
            delay(1000)  // Еще 1 секунда
            count = 2
        }

        Text("Count: $count")
    }

    // Изначально 0
    composeTestRule.onNodeWithText("Count: 0").assertExists()

    // Продвигаем время на 1 секунду
    composeTestRule.mainClock.advanceTimeBy(1000)
    composeTestRule.waitForIdle()  // Даем recomposition завершиться

    // Теперь count = 1
    composeTestRule.onNodeWithText("Count: 1").assertExists()

    // Продвигаем еще на 1 секунду
    composeTestRule.mainClock.advanceTimeBy(1000)
    composeTestRule.waitForIdle()

    // Теперь count = 2
    composeTestRule.onNodeWithText("Count: 2").assertExists()
}
```

**Управление временем**:
- `waitForIdle()` - ожидание завершения всех операций
- `mainClock.autoAdvance` - автоматическое/ручное продвижение времени
- `mainClock.advanceTimeBy()` - продвижение времени на указанную длительность
- `mainClock.advanceTimeByFrame()` - продвижение на один кадр

### Тестирование асинхронных операций

Обработка async операций - загрузка данных, сетевые запросы:

```kotlin
@Test
fun asyncOperations_withTimeout() {
    composeTestRule.setContent {
        var data by remember { mutableStateOf<String?>(null) }

        LaunchedEffect(Unit) {
            delay(2000)  // Имитация сетевого запроса
            data = "Loaded"
        }

        if (data == null) {
            CircularProgressIndicator(modifier = Modifier.testTag("loading"))
        } else {
            Text(data!!)
        }
    }

    // Проверяем состояние загрузки
    composeTestRule
        .onNodeWithTag("loading")
        .assertExists()

    // Ожидаем загрузки данных с таймаутом
    composeTestRule.waitUntil(timeoutMillis = 3000) {
        composeTestRule
            .onAllNodesWithText("Loaded")
            .fetchSemanticsNodes()  // Получаем узлы
            .isNotEmpty()  // Проверяем наличие
    }

    // Проверяем загруженные данные
    composeTestRule
        .onNodeWithText("Loaded")
        .assertExists()
}

@Test
fun asyncOperations_withStateFlow() = runTest {
    val viewModel = TestViewModel()

    composeTestRule.setContent {
        val state by viewModel.uiState.collectAsState()

        when (state) {
            is UiState.Loading -> CircularProgressIndicator()
            is UiState.Success -> Text((state as UiState.Success).data)
            is UiState.Error -> Text("Error")
        }
    }

    // Изначально состояние загрузки
    composeTestRule.onNode(isProgressIndicator()).assertExists()

    // Запускаем загрузку данных
    viewModel.loadData()
    advanceUntilIdle()  // Продвигаем все корутины до idle

    // Проверяем успешное состояние
    composeTestRule
        .onNodeWithText("Data loaded")
        .assertExists()
}
```

**Методы ожидания**:
- `waitForIdle()` - ожидание завершения всех recomposition и задач
- `waitUntil(timeout) {}` - ожидание условия с таймаутом
- `runTest {}` - корутинный скоуп для тестирования с контролем времени
- `advanceUntilIdle()` - продвижение всех корутин до завершения

### Тестирование доступности (Accessibility)

Проверка accessibility свойств для поддержки пользователей с ограниченными возможностями:

```kotlin
@Test
fun accessibility_contentDescription() {
    composeTestRule.setContent {
        Icon(
            imageVector = Icons.Default.Close,
            contentDescription = "Close dialog",  // Описание для screen readers
            modifier = Modifier.testTag("close_icon")
        )
    }

    // Проверяем описание контента
    composeTestRule
        .onNodeWithTag("close_icon")
        .assertContentDescriptionEquals("Close dialog")
}

@Test
fun accessibility_semanticProperties() {
    composeTestRule.setContent {
        Button(
            onClick = {},
            modifier = Modifier.semantics {
                contentDescription = "Submit form"  // Описание действия
                stateDescription = "Ready to submit"  // Описание состояния
            }
        ) {
            Text("Submit")
        }
    }

    // Проверяем семантические свойства
    composeTestRule
        .onNode(
            hasContentDescription("Submit form") and
            hasStateDescription("Ready to submit")
        )
        .assertExists()
        .assertHasClickAction()  // Проверяем наличие действия клика
}

@Test
fun accessibility_mergingSemantics() {
    composeTestRule.setContent {
        Row(
            modifier = Modifier
                .testTag("row")
                .semantics(mergeDescendants = true) {}  // Объединяем семантику детей
        ) {
            Icon(Icons.Default.Star, contentDescription = "Rating")
            Text("4.5")
            Text("stars")
        }
    }

    // С объединением весь текст комбинируется
    composeTestRule
        .onNodeWithTag("row")
        .assert(hasText("4.5 stars", substring = false))
}
```

**Accessibility свойства**:
- `contentDescription` - описание элемента для screen readers
- `stateDescription` - описание текущего состояния
- `semantics(mergeDescendants = true)` - объединение семантики детей
- `assertHasClickAction()` - проверка наличия действия клика
- Всегда тестируйте accessibility для инклюзивности приложения

### Тестирование списков и коллекций

Работа с LazyColumn, LazyRow, фильтрация и бесконечная прокрутка:

```kotlin
@Test
fun lists_filtering() {
    val items = listOf("Apple", "Banana", "Cherry", "Date")

    composeTestRule.setContent {
        var filter by remember { mutableStateOf("") }

        Column {
            TextField(
                value = filter,
                onValueChange = { filter = it },
                modifier = Modifier.testTag("filter")
            )

            LazyColumn {
                items(items.filter { it.contains(filter, ignoreCase = true) }) { item ->
                    Text(item)
                }
            }
        }
    }

    // Изначально все элементы видны
    composeTestRule.onAllNodesWithText("Apple").assertCountEquals(1)
    composeTestRule.onAllNodesWithText("Banana").assertCountEquals(1)

    // Применяем фильтр
    composeTestRule
        .onNodeWithTag("filter")
        .performTextInput("a")

    // Только элементы с 'a' видны
    composeTestRule.onNodeWithText("Apple").assertExists()
    composeTestRule.onNodeWithText("Banana").assertExists()
    composeTestRule.onNodeWithText("Cherry").assertDoesNotExist()  // Нет 'a'
}

@Test
fun lists_infiniteScroll() {
    var items by mutableStateOf((0..20).toList())
    var isLoading by mutableStateOf(false)

    composeTestRule.setContent {
        LazyColumn(modifier = Modifier.testTag("list")) {
            items(items) { item ->
                Text("Item $item", modifier = Modifier.testTag("item_$item"))
            }

            // Индикатор загрузки в конце списка
            if (isLoading) {
                item {
                    CircularProgressIndicator(modifier = Modifier.testTag("loader"))
                }
            }
        }
    }

    // Прокручиваем до конца списка
    composeTestRule
        .onNodeWithTag("list")
        .performScrollToNode(hasTestTag("item_20"))

    // Имитируем загрузку следующей страницы
    isLoading = true
    composeTestRule.waitForIdle()

    composeTestRule.onNodeWithTag("loader").assertExists()

    // Добавляем больше элементов
    items = (0..40).toList()
    isLoading = false
    composeTestRule.waitForIdle()

    // Проверяем наличие новых элементов
    composeTestRule
        .onNodeWithTag("list")
        .performScrollToNode(hasTestTag("item_40"))

    composeTestRule.onNodeWithTag("item_40").assertIsDisplayed()
}
```

**Работа со списками**:
- `performScrollToNode()` - прокрутка до конкретного элемента
- `assertIsDisplayed()` - проверка видимости на экране
- `assertCountEquals()` - проверка количества элементов
- Тестируйте фильтрацию, пагинацию, пустые состояния

### Полный пример тестового набора

Комплексный тест с Hilt, несколькими состояниями и accessibility:

```kotlin
@HiltAndroidTest
class CompleteScreenTest {
    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @get:Rule(order = 1)
    val composeTestRule = createAndroidComposeRule<MainActivity>()

    private lateinit var repository: FakeRepository

    @Before
    fun setup() {
        hiltRule.inject()
        repository = FakeRepository()
    }

    @Test
    fun productList_loadingState() {
        repository.setDelay(1000)  // Задержка для имитации загрузки

        composeTestRule.setContent {
            ProductListScreen(viewModel = ProductViewModel(repository))
        }

        // Проверяем индикатор загрузки
        composeTestRule
            .onNode(isProgressIndicator())
            .assertExists()
    }

    @Test
    fun productList_successState() {
        // Подготавливаем тестовые данные
        repository.setProducts(
            listOf(
                Product("1", "Product 1", 10.0),
                Product("2", "Product 2", 20.0)
            )
        )

        composeTestRule.setContent {
            ProductListScreen(viewModel = ProductViewModel(repository))
        }

        composeTestRule.waitForIdle()

        // Проверяем отображение продуктов
        composeTestRule.onNodeWithText("Product 1").assertIsDisplayed()
        composeTestRule.onNodeWithText("Product 2").assertIsDisplayed()
        composeTestRule.onNodeWithText("$10.00").assertIsDisplayed()
    }

    @Test
    fun productList_errorState() {
        // Имитируем ошибку
        repository.setError(Exception("Network error"))

        composeTestRule.setContent {
            ProductListScreen(viewModel = ProductViewModel(repository))
        }

        composeTestRule.waitForIdle()

        // Проверяем сообщение об ошибке
        composeTestRule.onNodeWithText("Network error").assertIsDisplayed()

        // Нажимаем кнопку повтора
        composeTestRule.onNodeWithText("Retry").performClick()

        // Индикатор загрузки должен появиться снова
        composeTestRule.onNode(isProgressIndicator()).assertExists()
    }

    @Test
    fun productList_clickProduct() {
        repository.setProducts(listOf(Product("1", "Product 1", 10.0)))
        var navigatedToId: String? = null

        composeTestRule.setContent {
            ProductListScreen(
                viewModel = ProductViewModel(repository),
                onProductClick = { navigatedToId = it }  // Захватываем навигацию
            )
        }

        composeTestRule.waitForIdle()

        // Кликаем на продукт
        composeTestRule.onNodeWithText("Product 1").performClick()

        // Проверяем, что навигация произошла
        assertEquals("1", navigatedToId)
    }

    @Test
    fun productList_accessibility() {
        repository.setProducts(listOf(Product("1", "Product 1", 10.0)))

        composeTestRule.setContent {
            ProductListScreen(viewModel = ProductViewModel(repository))
        }

        composeTestRule.waitForIdle()

        // Проверяем accessibility свойства
        composeTestRule
            .onNodeWithText("Product 1")
            .assertHasClickAction()  // Элемент кликабельный
            .assert(hasClickLabel("View product details"))  // Есть описание действия
    }
}
```

**Организация тестов**:
- Используйте `@Before` для настройки
- Создавайте отдельные тесты для каждого состояния
- Используйте fake/mock зависимости
- Тестируйте навигацию через колбэки
- Всегда проверяйте accessibility

### Лучшие практики тестирования Compose UI

1. **Используйте testTag для стабильной идентификации**
   - testTag не зависит от локализации и изменений текста
   - Добавляйте к элементам, с которыми взаимодействуете в тестах

2. **Предпочитайте semantic matchers тексту когда возможно**
   - `hasContentDescription()` вместо `onNodeWithText()`
   - Тесты остаются работоспособными при изменении UI текстов

3. **Тестируйте accessibility свойства**
   - Проверяйте contentDescription для всех важных элементов
   - Используйте `assertHasClickAction()` для интерактивных элементов
   - Тестируйте навигацию клавиатурой и screen reader

4. **Обрабатывайте async операции корректно**
   - Используйте `waitUntil()` с таймаутом для асинхронных операций
   - `waitForIdle()` для ожидания recomposition
   - `runTest {}` для корутин с контролем времени

5. **Тестируйте анимации с контролем времени**
   - Отключайте `autoAdvance` для детерминированных тестов
   - Используйте `mainClock.advanceTimeBy()` для точного контроля
   - Проверяйте промежуточные и финальные состояния

6. **Используйте custom matchers для сложных проверок**
   - Создавайте переиспользуемые matchers для частых проверок
   - Инкапсулируйте сложную логику проверки
   - Давайте понятные описания для отладки

7. **Тестируйте error states и edge cases**
   - Пустые списки, состояния загрузки, ошибки сети
   - Проверяйте кнопки retry и обработку ошибок
   - Тестируйте граничные значения и некорректный ввод

8. **Мокируйте зависимости**
   - Используйте Hilt для инъекции тестовых зависимостей
   - Создавайте fake реализации репозиториев
   - Изолируйте UI тесты от реальных сервисов

9. **Держите тесты изолированными и независимыми**
   - Каждый тест должен быть автономным
   - Не полагайтесь на порядок выполнения тестов
   - Сбрасывайте состояние в `@Before` или `@After`

10. **Тестируйте пользовательские потоки, не детали реализации**
    - Фокусируйтесь на том, что видит пользователь
    - Избегайте тестирования внутренней структуры composables
    - Тестируйте поведение, а не реализацию

### Дополнительные советы

**Отладка тестов**:
```kotlin
// Вывод семантического дерева для отладки
composeTestRule.onRoot().printToLog("TAG")

// Вывод всех узлов с определенным условием
composeTestRule.onAllNodes(hasText("")).fetchSemanticsNodes().forEach {
    println(it.config)
}
```

**Тестирование с реальным Activity**:
```kotlin
// Используйте createAndroidComposeRule для интеграционных тестов
@get:Rule
val composeTestRule = createAndroidComposeRule<MainActivity>()
```

**Комбинирование matchers**:
```kotlin
// Используйте and, or для комплексных условий
composeTestRule.onNode(
    hasText("Submit") and isEnabled() and hasClickAction()
).performClick()
```

---

## Related Questions

### Prerequisites (Easier)
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - Compose, Ui
- [[q-testing-compose-ui--android--medium]] - Compose, Testing
- [[q-compose-testing--android--medium]] - Compose, Testing

### Related (Medium)
- [[q-compose-stability-skippability--jetpack-compose--hard]] - Compose
- [[q-compose-custom-layout--jetpack-compose--hard]] - Compose
- [[q-compose-performance-optimization--android--hard]] - Compose
