---
id: android-253
title: Testing Compose UI / Тестирование Compose UI
aliases:
- Testing Compose UI
- Тестирование Compose UI
topic: android
subtopics:
- testing-ui
- ui-compose
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-jetpack-compose
- c-testing
- q-what-is-diffutil-for--android--medium
created: 2025-10-15
updated: 2025-11-10
tags:
- android/testing-ui
- android/ui-compose
- difficulty/medium
- jetpack-compose
- testing
- ui-testing

---

# Вопрос (RU)
> Тестирование Compose UI

# Question (EN)
> Testing Compose UI

## Ответ (RU)
Тестирование Compose UI использует тестовый API Compose для декларативного поиска, взаимодействия и проверки UI-компонентов.

### Базовая настройка

```kotlin
class LoginScreenTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun loginButton_clickable_when_fields_filled() {
        // Устанавливаем контент
        composeTestRule.setContent {
            LoginScreen()
        }

        // Находим и взаимодействуем
        composeTestRule.onNodeWithText("Email").performTextInput("user@example.com")
        composeTestRule.onNodeWithText("Password").performTextInput("password123")

        // Проверяем
        composeTestRule.onNodeWithText("Login").assertIsEnabled()
    }
}
```

`createComposeRule`:
- Создает изолированную среду для тестирования Compose.
- Управляет жизненным циклом композиции.
- Синхронизируется с рекомпозициями и idling-ресурсами.
- Предоставляет finders, assertions и actions.

### Поисковые функции (Finders) — поиск элементов

```kotlin
// По тексту
composeTestRule.onNodeWithText("Submit")
composeTestRule.onNodeWithText("Submit", ignoreCase = true)
composeTestRule.onNodeWithText("Submit", substring = true)

// По contentDescription (для доступности)
composeTestRule.onNodeWithContentDescription("Profile picture")

// По тестовому тегу
composeTestRule.onNodeWithTag("login_button")

// По семантическим свойствам / matcher-ам
composeTestRule.onNode(hasText("Submit"))
composeTestRule.onNode(isEnabled())
composeTestRule.onNode(hasClickAction())

// Комбинация условий
composeTestRule.onNode(
    hasText("Submit") and isEnabled() and hasClickAction()
)

// Поиск нескольких элементов
composeTestRule.onAllNodesWithText("Item")
composeTestRule.onAllNodesWithTag("list_item")

// Фильтрация
composeTestRule.onAllNodesWithText("Item")
    .filter(isEnabled())
    .onFirst()
```

### Тестовые теги — предпочтительный способ

```kotlin
// Composable с тестовыми тегами
@Composable
fun LoginScreen(
    email: String,
    onEmailChange: (String) -> Unit,
    password: String,
    onPasswordChange: (String) -> Unit,
    onLogin: () -> Unit,
    isLoginEnabled: Boolean
) {
    Column {
        TextField(
            value = email,
            onValueChange = onEmailChange,
            modifier = Modifier.testTag("email_input")
        )

        TextField(
            value = password,
            onValueChange = onPasswordChange,
            modifier = Modifier.testTag("password_input")
        )

        Button(
            onClick = onLogin,
            enabled = isLoginEnabled,
            modifier = Modifier.testTag("login_button")
        ) {
            Text("Login")
        }
    }
}

// Тест с использованием тестовых тегов
@Test
fun loginButton_enabled_when_fields_valid() {
    composeTestRule.setContent {
        LoginScreen(
            email = "",
            onEmailChange = {},
            password = "",
            onPasswordChange = {},
            onLogin = {},
            isLoginEnabled = true
        )
    }

    composeTestRule.onNodeWithTag("login_button")
        .assertIsEnabled()
}
```

Почему тестовые теги лучше:
- Не зависят от текста (устойчивы к локализации).
- Стабильнее при рефакторинге.
- Явно помечают тестируемые элементы.
- Обычно эффективнее поиска по тексту.

### Действия (Actions) — взаимодействие с элементами

```kotlin
// Клик
composeTestRule.onNodeWithTag("button").performClick()

// Ввод текста
composeTestRule.onNodeWithTag("input").performTextInput("Hello")
composeTestRule.onNodeWithTag("input").performTextClearance()
composeTestRule.onNodeWithTag("input").performTextReplacement("New text")

// Скролл в LazyColumn/LazyRow
composeTestRule.onNodeWithTag("list").performScrollToIndex(10)
composeTestRule.onNodeWithTag("list").performScrollToNode(hasText("Item 10"))

// Жесты
composeTestRule.onNodeWithTag("image")
    .performTouchInput {
        swipeLeft()
        swipeRight()
        swipeUp()
        swipeDown()
    }

// Долгое нажатие
composeTestRule.onNodeWithTag("item").performTouchInput {
    longClick()
}
```

### Утверждения (Assertions) — проверка состояния

```kotlin
// Существование
composeTestRule.onNodeWithText("Welcome").assertExists()
composeTestRule.onNodeWithText("Error").assertDoesNotExist()

// Видимость
composeTestRule.onNodeWithTag("loading").assertIsDisplayed()
composeTestRule.onNodeWithTag("content").assertIsNotDisplayed()

// Доступность (enabled/disabled)
composeTestRule.onNodeWithTag("button").assertIsEnabled()
composeTestRule.onNodeWithTag("button").assertIsNotEnabled()

// Выбор (selected)
composeTestRule.onNodeWithTag("checkbox").assertIsSelected()
composeTestRule.onNodeWithTag("checkbox").assertIsNotSelected()

// Текст
composeTestRule.onNodeWithTag("title").assertTextEquals("Welcome")
composeTestRule.onNodeWithTag("title").assertTextContains("Wel")

// Описание контента
composeTestRule.onNodeWithTag("icon")
    .assertContentDescriptionEquals("User profile")

// Количество элементов
composeTestRule.onAllNodesWithTag("list_item").assertCountEquals(10)

// Пример для custom semantics
composeTestRule.onNodeWithTag("progress")
    .assert(hasProgressBarRangeInfo(ProgressBarRangeInfo(0.5f, 0f..1f)))
```

### Тестирование изменения состояния

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Column(modifier = Modifier.testTag("counter")) {
        Text(
            text = "Count: $count",
            modifier = Modifier.testTag("count_text")
        )

        Button(
            onClick = { count++ },
            modifier = Modifier.testTag("increment_button")
        ) {
            Text("Increment")
        }
    }
}

@Test
fun counter_increments_on_button_click() {
    composeTestRule.setContent {
        Counter()
    }

    // Начальное состояние
    composeTestRule.onNodeWithTag("count_text")
        .assertTextEquals("Count: 0")

    // Кликаем
    composeTestRule.onNodeWithTag("increment_button").performClick()

    // Проверяем изменение
    composeTestRule.onNodeWithTag("count_text")
        .assertTextEquals("Count: 1")

    // Еще раз
    composeTestRule.onNodeWithTag("increment_button").performClick()

    composeTestRule.onNodeWithTag("count_text")
        .assertTextEquals("Count: 2")
}
```

### Тестирование LazyColumn/LazyRow

```kotlin
@Composable
fun UserList(users: List<User>) {
    LazyColumn(modifier = Modifier.testTag("user_list")) {
        items(users) { user ->
            UserItem(
                user = user,
                modifier = Modifier.testTag("user_item_${user.id}")
            )
        }
    }
}

@Test
fun userList_displays_all_users() {
    val users = listOf(
        User(1, "Alice"),
        User(2, "Bob"),
        User(3, "Charlie")
    )

    composeTestRule.setContent {
        UserList(users)
    }

    // Проверяем элементы по тегам
    composeTestRule.onNodeWithTag("user_item_1").assertExists()
    composeTestRule.onNodeWithTag("user_item_2").assertExists()
    composeTestRule.onNodeWithTag("user_item_3").assertExists()

    // Проверяем текст
    composeTestRule.onNodeWithText("Alice").assertExists()
    composeTestRule.onNodeWithText("Bob").assertExists()
    composeTestRule.onNodeWithText("Charlie").assertExists()
}

@Test
fun userList_scrolls_to_bottom() {
    val users = (1..100).map { User(it, "User $it") }

    composeTestRule.setContent {
        UserList(users)
    }

    // Скроллим до последнего элемента
    composeTestRule.onNodeWithTag("user_list")
        .performScrollToIndex(99)

    composeTestRule.onNodeWithTag("user_item_100").assertExists()
}
```

### Тестирование с ViewModel

```kotlin
class ProductsScreenTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    private lateinit var viewModel: ProductsViewModel
    private lateinit var fakeRepository: FakeProductsRepository

    @Before
    fun setup() {
        fakeRepository = FakeProductsRepository()
        viewModel = ProductsViewModel(fakeRepository)
    }

    @Test
    fun productsScreen_shows_loading_initially() {
        composeTestRule.setContent {
            ProductsScreen(viewModel = viewModel)
        }

        composeTestRule.onNodeWithTag("loading_indicator")
            .assertIsDisplayed()
    }

    @Test
    fun productsScreen_shows_products_after_loading() {
        fakeRepository.setProducts(testProducts)

        composeTestRule.setContent {
            ProductsScreen(viewModel = viewModel)
        }

        viewModel.loadProducts()

        composeTestRule.waitUntil(timeoutMillis = 5_000) {
            composeTestRule.onAllNodesWithTag("product_item")
                .fetchSemanticsNodes().isNotEmpty()
        }

        composeTestRule.onNodeWithText("Product 1").assertExists()
        composeTestRule.onNodeWithText("Product 2").assertExists()
    }

    @Test
    fun productsScreen_shows_error_on_failure() {
        fakeRepository.setError(IOException("Network error"))

        composeTestRule.setContent {
            ProductsScreen(viewModel = viewModel)
        }

        viewModel.loadProducts()

        composeTestRule.waitUntil(timeoutMillis = 5_000) {
            composeTestRule.onAllNodesWithText("Network error")
                .fetchSemanticsNodes().isNotEmpty()
        }

        composeTestRule.onNodeWithText("Network error").assertExists()
        composeTestRule.onNodeWithTag("retry_button").assertExists()
    }
}
```

### `waitUntil` — ожидание состояния

```kotlin
// Ожидание появления элемента
composeTestRule.waitUntil(timeoutMillis = 5_000) {
    composeTestRule.onAllNodesWithText("Data loaded")
        .fetchSemanticsNodes().isNotEmpty()
}

// Ожидание исчезновения элемента
composeTestRule.waitUntil(timeoutMillis = 5_000) {
    composeTestRule.onAllNodesWithTag("loading")
        .fetchSemanticsNodes().isEmpty()
}

// Ожидание определенного количества элементов
composeTestRule.waitUntil(timeoutMillis = 5_000) {
    composeTestRule.onAllNodesWithTag("list_item")
        .fetchSemanticsNodes().size == 10
}
```

### Тестирование навигации (Compose Navigation)

```kotlin
@Test
fun clicking_product_navigates_to_details() {
    val context = ApplicationProvider.getApplicationContext<Context>()
    val navController = TestNavHostController(context).apply {
        navigatorProvider.addNavigator(ComposeNavigator())
    }

    composeTestRule.setContent {
        NavHost(navController = navController, startDestination = "products") {
            composable("products") { ProductsScreen(navController) }
            composable("details/{id}") { DetailsScreen() }
        }
    }

    // Кликаем по продукту
    composeTestRule.onNodeWithTag("product_1").performClick()

    // Проверяем навигацию
    assertEquals("details/1", navController.currentBackStackEntry?.destination?.route)
}
```

### Тестирование диалогов и Bottom Sheet

```kotlin
@Composable
fun DeleteConfirmationDialog(
    onConfirm: () -> Unit,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Delete item?") },
        text = { Text("This action cannot be undone") },
        confirmButton = {
            TextButton(
                onClick = onConfirm,
                modifier = Modifier.testTag("confirm_button")
            ) {
                Text("Delete")
            }
        },
        dismissButton = {
            TextButton(
                onClick = onDismiss,
                modifier = Modifier.testTag("cancel_button")
            ) {
                Text("Cancel")
            }
        }
    )
}

@Test
fun dialog_confirms_deletion() {
    var confirmed = false
    var dismissed = false

    composeTestRule.setContent {
        DeleteConfirmationDialog(
            onConfirm = { confirmed = true },
            onDismiss = { dismissed = true }
        )
    }

    composeTestRule.onNodeWithText("Delete item?").assertExists()

    composeTestRule.onNodeWithTag("confirm_button").performClick()

    assertTrue(confirmed)
    assertFalse(dismissed)
}

@Test
fun dialog_cancels_deletion() {
    var confirmed = false
    var dismissed = false

    composeTestRule.setContent {
        DeleteConfirmationDialog(
            onConfirm = { confirmed = true },
            onDismiss = { dismissed = true }
        )
    }

    composeTestRule.onNodeWithTag("cancel_button").performClick()

    assertFalse(confirmed)
    assertTrue(dismissed)
}
```

### `unmergedTree` — для вложенных элементов

```kotlin
// По умолчанию семантика дочерних элементов может сливаться с родителем
@Composable
fun ListItem(title: String, subtitle: String) {
    Column {
        Text(title)
        Text(subtitle)
    }
}

// Может не найтись, если subtitle был слит в родителя
composeTestRule.onNodeWithText("Subtitle").assertExists() // Может упасть

// Используем useUnmergedTree = true, чтобы искать без слияния
composeTestRule.onNodeWithText("Subtitle", useUnmergedTree = true).assertExists()

// Или явно управляем семантикой
@Composable
fun ListItemWithTags(title: String, subtitle: String) {
    Column(
        modifier = Modifier.semantics(mergeDescendants = false) {}
    ) {
        Text(title, modifier = Modifier.testTag("title"))
        Text(subtitle, modifier = Modifier.testTag("subtitle"))
    }
}

composeTestRule.onNodeWithTag("subtitle").assertExists() // OK
```

### Тестирование анимаций и `mainClock`

```kotlin
@Composable
fun AnimatedVisibilityExample() {
    var visible by remember { mutableStateOf(false) }

    Column {
        Button(
            onClick = { visible = !visible },
            modifier = Modifier.testTag("toggle_button")
        ) {
            Text("Toggle")
        }

        AnimatedVisibility(visible) {
            Text(
                text = "Animated content",
                modifier = Modifier.testTag("animated_content")
            )
        }
    }
}

@Test
fun animatedVisibility_shows_and_hides_content() {
    composeTestRule.mainClock.autoAdvance = false

    composeTestRule.setContent {
        AnimatedVisibilityExample()
    }

    composeTestRule.onNodeWithTag("animated_content").assertDoesNotExist()

    composeTestRule.onNodeWithTag("toggle_button").performClick()

    composeTestRule.mainClock.advanceTimeBy(1_000)

    composeTestRule.onNodeWithTag("animated_content").assertExists()

    composeTestRule.onNodeWithTag("toggle_button").performClick()

    composeTestRule.mainClock.advanceTimeBy(1_000)

    composeTestRule.onNodeWithTag("animated_content").assertDoesNotExist()
}
```

```kotlin
@Test
fun test_with_controlled_time() {
    composeTestRule.mainClock.autoAdvance = false

    composeTestRule.setContent {
        TimerScreen()
    }

    composeTestRule.mainClock.advanceTimeBy(1_000)
    composeTestRule.onNodeWithText("1 second").assertExists()

    composeTestRule.mainClock.advanceTimeBy(2_000)
    composeTestRule.onNodeWithText("3 seconds").assertExists()
}
```

### Screenshot-тестирование (концептуально)

```kotlin
@Test
fun loginScreen_screenshot() {
    composeTestRule.setContent {
        LoginScreen()
    }

    val bitmap = composeTestRule.onRoot()
        .captureToImage()
        .asAndroidBitmap()

    // Сравниваем bitmap с "золотым" эталонным изображением через библиотеку для screenshot-тестов или кастомный код
}
// Можно использовать специализированные библиотеки screenshot-тестирования (например, Paparazzi, Shot).
```

### Лучшие практики

- Использовать `testTag` вместо текста для стабильных селекторов.
- Проверять поведение и наблюдаемое состояние UI, а не внутренние детали реализации.
- Давать осмысленные имена тегам.
- Использовать `waitUntil` с таймаутом для асинхронных операций.
- Проверять доступность через `contentDescription` и другие семантики.
- Группировать связанные тесты по экрану/фиче.
- Выносить общую настройку в `@Before`.

### Частые ошибки (Common Pitfalls)

```kotlin
// 1. Неиспользование useUnmergedTree, когда это нужно
composeTestRule.onNodeWithText("Subtitle").assertExists() // Может упасть
// Правильно
composeTestRule.onNodeWithText("Subtitle", useUnmergedTree = true).assertExists()

// 2. Неожиданные падения из-за асинхронности
viewModel.loadData()
composeTestRule.onNodeWithText("Data").assertExists() // Может упасть
// Правильно
composeTestRule.waitUntil(timeoutMillis = 5_000) {
    composeTestRule.onAllNodesWithText("Data")
        .fetchSemanticsNodes().isNotEmpty()
}

// 3. Использование текста вместо стабильной семантики
composeTestRule.onNodeWithText("Submit").performClick() // Ломается при локализации
// Правильно
composeTestRule.onNodeWithTag("submit_button").performClick()

// 4. Игнорирование анимаций/времени
composeTestRule.onNodeWithTag("animated").assertExists() // Может упасть, пока анимация идет
// Правильно
composeTestRule.mainClock.advanceTimeBy(1_000)
composeTestRule.onNodeWithTag("animated").assertExists()
```

### Зависимости

```gradle
androidTestImplementation "androidx.compose.ui:ui-test-junit4:1.5.4"
debugImplementation "androidx.compose.ui:ui-test-manifest:1.5.4"
```

## Answer (EN)
Compose UI testing uses the Compose testing APIs to declaratively find, interact with, and verify composable UI.

### Basic Setup

```kotlin
class LoginScreenTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun loginButton_clickable_when_fields_filled() {
        // Set content
        composeTestRule.setContent {
            LoginScreen()
        }

        // Find & interact
        composeTestRule.onNodeWithText("Email").performTextInput("user@example.com")
        composeTestRule.onNodeWithText("Password").performTextInput("password123")

        // Assert
        composeTestRule.onNodeWithText("Login").assertIsEnabled()
    }
}
```

createComposeRule:
- Creates an isolated Compose test environment.
- Manages the composition lifecycle.
- Synchronizes with recompositions and idling resources.
- Provides finders, assertions, and actions.

### Finders - Finding Elements

```kotlin
// By text
composeTestRule.onNodeWithText("Submit")
composeTestRule.onNodeWithText("Submit", ignoreCase = true)
composeTestRule.onNodeWithText("Submit", substring = true)

// By content description (for accessibility)
composeTestRule.onNodeWithContentDescription("Profile picture")

// By test tag
composeTestRule.onNodeWithTag("login_button")

// By semantic properties / matchers
composeTestRule.onNode(hasText("Submit"))
composeTestRule.onNode(isEnabled())
composeTestRule.onNode(hasClickAction())

// Combining conditions
composeTestRule.onNode(
    hasText("Submit") and isEnabled() and hasClickAction()
)

// Finding multiple elements
composeTestRule.onAllNodesWithText("Item")
composeTestRule.onAllNodesWithTag("list_item")

// Filtering
composeTestRule.onAllNodesWithText("Item")
    .filter(isEnabled())
    .onFirst()
```

### Test Tags - Preferred for Testing

```kotlin
// Composable with test tags
@Composable
fun LoginScreen(
    email: String,
    onEmailChange: (String) -> Unit,
    password: String,
    onPasswordChange: (String) -> Unit,
    onLogin: () -> Unit,
    isLoginEnabled: Boolean
) {
    Column {
        TextField(
            value = email,
            onValueChange = onEmailChange,
            modifier = Modifier.testTag("email_input")
        )

        TextField(
            value = password,
            onValueChange = onPasswordChange,
            modifier = Modifier.testTag("password_input")
        )

        Button(
            onClick = onLogin,
            enabled = isLoginEnabled,
            modifier = Modifier.testTag("login_button")
        ) {
            Text("Login")
        }
    }
}

// Test with test tags
@Test
fun loginButton_enabled_when_fields_valid() {
    composeTestRule.setContent {
        LoginScreen(
            email = "",
            onEmailChange = {},
            password = "",
            onPasswordChange = {},
            onLogin = {},
            isLoginEnabled = true
        )
    }

    composeTestRule.onNodeWithTag("login_button")
        .assertIsEnabled()
}
```

Why test tags are better:
- Do not depend on text (robust to localization).
- More stable during refactoring.
- Explicitly mark testable elements.
- Typically more efficient than searching by text.

### Actions - Interacting with Elements

```kotlin
// Click
composeTestRule.onNodeWithTag("button").performClick()

// Text input
composeTestRule.onNodeWithTag("input").performTextInput("Hello")
composeTestRule.onNodeWithTag("input").performTextClearance()
composeTestRule.onNodeWithTag("input").performTextReplacement("New text")

// Scroll in LazyColumn/LazyRow
composeTestRule.onNodeWithTag("list").performScrollToIndex(10)
composeTestRule.onNodeWithTag("list").performScrollToNode(hasText("Item 10"))

// Gestures
composeTestRule.onNodeWithTag("image")
    .performTouchInput {
        swipeLeft()
        swipeRight()
        swipeUp()
        swipeDown()
    }

// Long click
composeTestRule.onNodeWithTag("item").performTouchInput {
    longClick()
}
```

### Assertions - Verifying State

```kotlin
// Existence
composeTestRule.onNodeWithText("Welcome").assertExists()
composeTestRule.onNodeWithText("Error").assertDoesNotExist()

// Visibility
composeTestRule.onNodeWithTag("loading").assertIsDisplayed()
composeTestRule.onNodeWithTag("content").assertIsNotDisplayed()

// Enabled/Disabled
composeTestRule.onNodeWithTag("button").assertIsEnabled()
composeTestRule.onNodeWithTag("button").assertIsNotEnabled()

// Selected
composeTestRule.onNodeWithTag("checkbox").assertIsSelected()
composeTestRule.onNodeWithTag("checkbox").assertIsNotSelected()

// Text
composeTestRule.onNodeWithTag("title").assertTextEquals("Welcome")
composeTestRule.onNodeWithTag("title").assertTextContains("Wel")

// Content description
composeTestRule.onNodeWithTag("icon")
    .assertContentDescriptionEquals("User profile")

// Count
composeTestRule.onAllNodesWithTag("list_item").assertCountEquals(10)

// Custom semantics example
composeTestRule.onNodeWithTag("progress")
    .assert(hasProgressBarRangeInfo(ProgressBarRangeInfo(0.5f, 0f..1f)))
```

### Testing State Changes

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Column(modifier = Modifier.testTag("counter")) {
        Text(
            text = "Count: $count",
            modifier = Modifier.testTag("count_text")
        )

        Button(
            onClick = { count++ },
            modifier = Modifier.testTag("increment_button")
        ) {
            Text("Increment")
        }
    }
}

@Test
fun counter_increments_on_button_click() {
    composeTestRule.setContent {
        Counter()
    }

    // Initial state
    composeTestRule.onNodeWithTag("count_text")
        .assertTextEquals("Count: 0")

    // Click increment
    composeTestRule.onNodeWithTag("increment_button").performClick()

    // Verify state changed
    composeTestRule.onNodeWithTag("count_text")
        .assertTextEquals("Count: 1")

    // Click again
    composeTestRule.onNodeWithTag("increment_button").performClick()

    composeTestRule.onNodeWithTag("count_text")
        .assertTextEquals("Count: 2")
}
```

### Testing LazyColumn/LazyRow

```kotlin
@Composable
fun UserList(users: List<User>) {
    LazyColumn(modifier = Modifier.testTag("user_list")) {
        items(users) { user ->
            UserItem(
                user = user,
                modifier = Modifier.testTag("user_item_${user.id}")
            )
        }
    }
}

@Test
fun userList_displays_all_users() {
    val users = listOf(
        User(1, "Alice"),
        User(2, "Bob"),
        User(3, "Charlie")
    )

    composeTestRule.setContent {
        UserList(users)
    }

    // Verify specific items by tag
    composeTestRule.onNodeWithTag("user_item_1").assertExists()
    composeTestRule.onNodeWithTag("user_item_2").assertExists()
    composeTestRule.onNodeWithTag("user_item_3").assertExists()

    // Verify text
    composeTestRule.onNodeWithText("Alice").assertExists()
    composeTestRule.onNodeWithText("Bob").assertExists()
    composeTestRule.onNodeWithText("Charlie").assertExists()
}

@Test
fun userList_scrolls_to_bottom() {
    val users = (1..100).map { User(it, "User $it") }

    composeTestRule.setContent {
        UserList(users)
    }

    // Scroll to reveal last item
    composeTestRule.onNodeWithTag("user_list")
        .performScrollToIndex(99)

    composeTestRule.onNodeWithTag("user_item_100").assertExists()
}
```

### Testing with `ViewModel`

```kotlin
class ProductsScreenTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    private lateinit var viewModel: ProductsViewModel
    private lateinit var fakeRepository: FakeProductsRepository

    @Before
    fun setup() {
        fakeRepository = FakeProductsRepository()
        viewModel = ProductsViewModel(fakeRepository)
    }

    @Test
    fun productsScreen_shows_loading_initially() {
        composeTestRule.setContent {
            ProductsScreen(viewModel = viewModel)
        }

        composeTestRule.onNodeWithTag("loading_indicator")
            .assertIsDisplayed()
    }

    @Test
    fun productsScreen_shows_products_after_loading() {
        fakeRepository.setProducts(testProducts)

        composeTestRule.setContent {
            ProductsScreen(viewModel = viewModel)
        }

        viewModel.loadProducts()

        composeTestRule.waitUntil(timeoutMillis = 5_000) {
            composeTestRule.onAllNodesWithTag("product_item")
                .fetchSemanticsNodes().isNotEmpty()
        }

        composeTestRule.onNodeWithText("Product 1").assertExists()
        composeTestRule.onNodeWithText("Product 2").assertExists()
    }

    @Test
    fun productsScreen_shows_error_on_failure() {
        fakeRepository.setError(IOException("Network error"))

        composeTestRule.setContent {
            ProductsScreen(viewModel = viewModel)
        }

        viewModel.loadProducts()

        composeTestRule.waitUntil(timeoutMillis = 5_000) {
            composeTestRule.onAllNodesWithText("Network error")
                .fetchSemanticsNodes().isNotEmpty()
        }

        composeTestRule.onNodeWithText("Network error").assertExists()
        composeTestRule.onNodeWithTag("retry_button").assertExists()
    }
}
```

### waitUntil - Waiting for State

```kotlin
// Wait until element appears
composeTestRule.waitUntil(timeoutMillis = 5_000) {
    composeTestRule.onAllNodesWithText("Data loaded")
        .fetchSemanticsNodes().isNotEmpty()
}

// Wait until element disappears
composeTestRule.waitUntil(timeoutMillis = 5_000) {
    composeTestRule.onAllNodesWithTag("loading")
        .fetchSemanticsNodes().isEmpty()
}

// Wait for specific number of elements
composeTestRule.waitUntil(timeoutMillis = 5_000) {
    composeTestRule.onAllNodesWithTag("list_item")
        .fetchSemanticsNodes().size == 10
}
```

### Testing Navigation (Compose Navigation)

```kotlin
@Test
fun clicking_product_navigates_to_details() {
    val context = ApplicationProvider.getApplicationContext<Context>()
    val navController = TestNavHostController(context).apply {
        navigatorProvider.addNavigator(ComposeNavigator())
    }

    composeTestRule.setContent {
        NavHost(navController = navController, startDestination = "products") {
            composable("products") { ProductsScreen(navController) }
            composable("details/{id}") { DetailsScreen() }
        }
    }

    // Click on product
    composeTestRule.onNodeWithTag("product_1").performClick()

    // Verify navigation
    assertEquals("details/1", navController.currentBackStackEntry?.destination?.route)
}
```

### Testing Dialogs and Bottom Sheets

```kotlin
@Composable
fun DeleteConfirmationDialog(
    onConfirm: () -> Unit,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Delete item?") },
        text = { Text("This action cannot be undone") },
        confirmButton = {
            TextButton(
                onClick = onConfirm,
                modifier = Modifier.testTag("confirm_button")
            ) {
                Text("Delete")
            }
        },
        dismissButton = {
            TextButton(
                onClick = onDismiss,
                modifier = Modifier.testTag("cancel_button")
            ) {
                Text("Cancel")
            }
        }
    )
}

@Test
fun dialog_confirms_deletion() {
    var confirmed = false
    var dismissed = false

    composeTestRule.setContent {
        DeleteConfirmationDialog(
            onConfirm = { confirmed = true },
            onDismiss = { dismissed = true }
        )
    }

    composeTestRule.onNodeWithText("Delete item?").assertExists()

    composeTestRule.onNodeWithTag("confirm_button").performClick()

    assertTrue(confirmed)
    assertFalse(dismissed)
}

@Test
fun dialog_cancels_deletion() {
    var confirmed = false
    var dismissed = false

    composeTestRule.setContent {
        DeleteConfirmationDialog(
            onConfirm = { confirmed = true },
            onDismiss = { dismissed = true }
        )
    }

    composeTestRule.onNodeWithTag("cancel_button").performClick()

    assertFalse(confirmed)
    assertTrue(dismissed)
}
```

### unmergedTree - for Nested Elements

```kotlin
// By default some semantics may be merged into parents
@Composable
fun ListItem(title: String, subtitle: String) {
    Column {
        Text(title)
        Text(subtitle)
    }
}

// May fail if subtitle semantics are merged
composeTestRule.onNodeWithText("Subtitle").assertExists() // Might FAIL

// Use useUnmergedTree = true to search without merged semantics
composeTestRule.onNodeWithText("Subtitle", useUnmergedTree = true).assertExists()

// Or control semantics explicitly
@Composable
fun ListItemWithTags(title: String, subtitle: String) {
    Column(
        modifier = Modifier.semantics(mergeDescendants = false) {}
    ) {
        Text(title, modifier = Modifier.testTag("title"))
        Text(subtitle, modifier = Modifier.testTag("subtitle"))
    }
}

composeTestRule.onNodeWithTag("subtitle").assertExists() // OK
```

### Testing Animations and mainClock

```kotlin
@Composable
fun AnimatedVisibilityExample() {
    var visible by remember { mutableStateOf(false) }

    Column {
        Button(
            onClick = { visible = !visible },
            modifier = Modifier.testTag("toggle_button")
        ) {
            Text("Toggle")
        }

        AnimatedVisibility(visible) {
            Text(
                text = "Animated content",
                modifier = Modifier.testTag("animated_content")
            )
        }
    }
}

@Test
fun animatedVisibility_shows_and_hides_content() {
    composeTestRule.mainClock.autoAdvance = false

    composeTestRule.setContent {
        AnimatedVisibilityExample()
    }

    composeTestRule.onNodeWithTag("animated_content").assertDoesNotExist()

    composeTestRule.onNodeWithTag("toggle_button").performClick()

    composeTestRule.mainClock.advanceTimeBy(1_000)

    composeTestRule.onNodeWithTag("animated_content").assertExists()

    composeTestRule.onNodeWithTag("toggle_button").performClick()

    composeTestRule.mainClock.advanceTimeBy(1_000)

    composeTestRule.onNodeWithTag("animated_content").assertDoesNotExist()
}
```

```kotlin
@Test
fun test_with_controlled_time() {
    composeTestRule.mainClock.autoAdvance = false

    composeTestRule.setContent {
        TimerScreen()
    }

    composeTestRule.mainClock.advanceTimeBy(1_000)
    composeTestRule.onNodeWithText("1 second").assertExists()

    composeTestRule.mainClock.advanceTimeBy(2_000)
    composeTestRule.onNodeWithText("3 seconds").assertExists()
}
```

### Screenshot Testing (conceptual)

```kotlin
@Test
fun loginScreen_screenshot() {
    composeTestRule.setContent {
        LoginScreen()
    }

    val bitmap = composeTestRule.onRoot()
        .captureToImage()
        .asAndroidBitmap()

    // Compare bitmap with golden image using your screenshot testing library or custom code
}
// Or use dedicated screenshot testing libraries (e.g. Paparazzi, Shot).
```

### Best Practices

- Use test tags instead of text for stable selectors.
- Test behavior and observable UI state, not internal implementation details.
- Use meaningful test tag names.
- Use waitUntil with a timeout for async operations.
- Test accessibility via content descriptions and other semantics.
- Group related tests per screen/feature.
- Use @Before to set up common Compose content or test data.

### Common Pitfalls

```kotlin
// 1. Forgetting useUnmergedTree when needed
composeTestRule.onNodeWithText("Subtitle").assertExists() // May fail
// Fix
composeTestRule.onNodeWithText("Subtitle", useUnmergedTree = true).assertExists()

// 2. Not waiting for async operations
viewModel.loadData()
composeTestRule.onNodeWithText("Data").assertExists() // May fail
// Fix
composeTestRule.waitUntil(timeoutMillis = 5_000) {
    composeTestRule.onAllNodesWithText("Data")
        .fetchSemanticsNodes().isNotEmpty()
}

// 3. Using text instead of stable semantics
composeTestRule.onNodeWithText("Submit").performClick() // Brittle with localization
// Fix
composeTestRule.onNodeWithTag("submit_button").performClick()

// 4. Ignoring animations/time
composeTestRule.onNodeWithTag("animated").assertExists() // May fail if animation running
// Fix
composeTestRule.mainClock.advanceTimeBy(1_000)
composeTestRule.onNodeWithTag("animated").assertExists()
```

### Dependencies

```gradle
androidTestImplementation "androidx.compose.ui:ui-test-junit4:1.5.4"
debugImplementation "androidx.compose.ui:ui-test-manifest:1.5.4"
```

## Follow-ups

- [[c-jetpack-compose]]
- [[c-testing]]
- [[q-what-is-diffutil-for--android--medium]]

## References

- [UI Testing](https://developer.android.com/training/testing/ui-testing)
- [Android Documentation](https://developer.android.com/docs)
- [Jetpack Compose](https://developer.android.com/develop/ui/compose)

## Related Questions

### Hub
- [[q-jetpack-compose-basics--android--medium]] - Comprehensive Compose introduction

### Related (Medium)
- [[q-how-does-jetpack-compose-work--android--medium]] - How Compose works
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Essential Compose components
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - RecyclerView in Compose
- [[q-mutable-state-compose--android--medium]] - MutableState basics
- [[q-remember-vs-remembersaveable-compose--android--medium]] - remember vs rememberSaveable

### Advanced (Harder)
- [[q-compose-stability-skippability--android--hard]] - Stability & skippability
- [[q-stable-classes-compose--android--hard]] - @Stable annotation
- [[q-stable-annotation-compose--android--hard]] - Stability annotations
