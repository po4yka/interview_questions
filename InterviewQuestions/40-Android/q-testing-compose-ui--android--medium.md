---
topic: android
tags:
  - android
  - jetpack-compose
  - testing
  - ui-testing
  - compose-test
difficulty: medium
status: reviewed
---

# Testing Compose UI

**English**: How do you test Jetpack Compose UI? What are the key APIs and best practices?

## Answer

**Compose UI testing** использует декларативный API для поиска, взаимодействия и верификации composable функций.

### Основной setup

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

**createComposeRule**:
- - Создает isolated тестовую среду
- - Управляет композицией lifecycle
- - Синхронизируется с recomposition
- - Предоставляет finders, assertions, actions

### Finders - поиск элементов

```kotlin
// По тексту
composeTestRule.onNodeWithText("Submit")
composeTestRule.onNodeWithText("Submit", ignoreCase = true)
composeTestRule.onNodeWithText("Submit", substring = true)

// По content description (для accessibility)
composeTestRule.onNodeWithContentDescription("Profile picture")

// По test tag
composeTestRule.onNodeWithTag("login_button")

// По semantic property
composeTestRule.onNode(hasText("Submit"))
composeTestRule.onNode(isEnabled())
composeTestRule.onNode(hasClickAction())

// Комбинирование условий
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

### Test Tags - лучший способ для тестирования

```kotlin
// Composable с test tags
@Composable
fun LoginScreen() {
    Column {
        TextField(
            value = email,
            onValueChange = { email = it },
            modifier = Modifier.testTag("email_input")
        )

        TextField(
            value = password,
            onValueChange = { password = it },
            modifier = Modifier.testTag("password_input")
        )

        Button(
            onClick = onLogin,
            modifier = Modifier.testTag("login_button")
        ) {
            Text("Login")
        }
    }
}

// Тест с test tags
@Test
fun loginButton_enabled_when_fields_valid() {
    composeTestRule.setContent {
        LoginScreen()
    }

    composeTestRule.onNodeWithTag("email_input")
        .performTextInput("user@example.com")

    composeTestRule.onNodeWithTag("password_input")
        .performTextInput("password123")

    composeTestRule.onNodeWithTag("login_button")
        .assertIsEnabled()
}
```

**Почему test tags лучше**:
- - Не зависят от текста (локализация)
- - Более стабильны при рефакторинге
- - Явно показывают testable элементы
- - Работают быстрее чем text search

### Actions - взаимодействие с элементами

```kotlin
// Click
composeTestRule.onNodeWithTag("button").performClick()

// Text input
composeTestRule.onNodeWithTag("input").performTextInput("Hello")
composeTestRule.onNodeWithTag("input").performTextClearance()
composeTestRule.onNodeWithTag("input").performTextReplacement("New text")

// Scroll
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

composeTestRule.onNodeWithTag("map")
    .performTouchInput {
        pinch() // Zoom
    }

// Long click
composeTestRule.onNodeWithTag("item").performTouchInput {
    longClick()
}
```

### Assertions - проверка состояния

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

// Custom semantics
composeTestRule.onNodeWithTag("progress")
    .assert(hasProgressBarRangeInfo(ProgressBarRangeInfo(0.5f, 0f..1f)))
```

### Тестирование State изменений

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

    // Verify count
    composeTestRule.onAllNodesWithTag("user_item_", useUnmergedTree = true)
        .assertCountEquals(3)

    // Verify specific items
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

    // Item 100 not visible initially
    composeTestRule.onNodeWithTag("user_item_100").assertDoesNotExist()

    // Scroll to bottom
    composeTestRule.onNodeWithTag("user_list")
        .performScrollToIndex(99)

    // Now visible
    composeTestRule.onNodeWithTag("user_item_100").assertExists()
}
```

### Тестирование с ViewModel

```kotlin
class ProductsScreenTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    private lateinit var viewModel: ProductsViewModel

    @Before
    fun setup() {
        viewModel = ProductsViewModel(fakeRepository)
    }

    @Test
    fun productsScreen_shows_loading_initially() {
        composeTestRule.setContent {
            ProductsScreen(viewModel = viewModel)
        }

        // Loading indicator visible
        composeTestRule.onNodeWithTag("loading_indicator")
            .assertIsDisplayed()
    }

    @Test
    fun productsScreen_shows_products_after_loading() {
        fakeRepository.setProducts(testProducts)

        composeTestRule.setContent {
            ProductsScreen(viewModel = viewModel)
        }

        // Trigger load
        viewModel.loadProducts()

        // Wait for loading to complete
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule.onAllNodesWithTag("product_item")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Verify products displayed
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

        composeTestRule.onNodeWithText("Network error").assertExists()
        composeTestRule.onNodeWithTag("retry_button").assertExists()
    }
}
```

### waitUntil - ожидание состояния

```kotlin
// Ждем пока элемент появится
composeTestRule.waitUntil(timeoutMillis = 5000) {
    composeTestRule.onAllNodesWithText("Data loaded")
        .fetchSemanticsNodes().isNotEmpty()
}

// Ждем пока элемент исчезнет
composeTestRule.waitUntil(timeoutMillis = 5000) {
    composeTestRule.onAllNodesWithTag("loading")
        .fetchSemanticsNodes().isEmpty()
}

// Ждем определенное количество элементов
composeTestRule.waitUntil(timeoutMillis = 5000) {
    composeTestRule.onAllNodesWithTag("list_item")
        .fetchSemanticsNodes().size == 10
}
```

### Тестирование Navigation

```kotlin
@Test
fun clicking_product_navigates_to_details() {
    val navController = TestNavHostController(ApplicationProvider.getApplicationContext())

    composeTestRule.setContent {
        navController.setGraph(NavGraph)
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

### Тестирование Dialogs и Bottom Sheets

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

    // Verify dialog visible
    composeTestRule.onNodeWithText("Delete item?").assertExists()

    // Click confirm
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

    // Click cancel
    composeTestRule.onNodeWithTag("cancel_button").performClick()

    assertFalse(confirmed)
    assertTrue(dismissed)
}
```

### unmergedTree - для вложенных элементов

```kotlin
// По умолчанию Compose мержит semantics дочерних элементов
@Composable
fun ListItem(title: String, subtitle: String) {
    Column {
        Text(title)      // Merged
        Text(subtitle)   // Merged
    }
}

// - Не найдет - semantics смержены
composeTestRule.onNodeWithText("Subtitle").assertExists() // FAIL

// - useUnmergedTree = true
composeTestRule.onNodeWithText("Subtitle", useUnmergedTree = true).assertExists()

// Или отключить merging в Composable
@Composable
fun ListItem(title: String, subtitle: String) {
    Column(modifier = Modifier.semantics { testTagsAsResourceId = true }) {
        Text(title, modifier = Modifier.testTag("title"))
        Text(subtitle, modifier = Modifier.testTag("subtitle"))
    }
}

composeTestRule.onNodeWithTag("subtitle").assertExists() // OK
```

### Тестирование Animations

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
    composeTestRule.setContent {
        AnimatedVisibilityExample()
    }

    // Initially hidden
    composeTestRule.onNodeWithTag("animated_content").assertDoesNotExist()

    // Click to show
    composeTestRule.onNodeWithTag("toggle_button").performClick()

    // Wait for animation
    composeTestRule.mainClock.advanceTimeBy(1000)

    // Now visible
    composeTestRule.onNodeWithTag("animated_content").assertExists()

    // Click to hide
    composeTestRule.onNodeWithTag("toggle_button").performClick()

    // Wait for animation
    composeTestRule.mainClock.advanceTimeBy(1000)

    // Hidden again
    composeTestRule.onNodeWithTag("animated_content").assertDoesNotExist()
}
```

### mainClock - контроль времени

```kotlin
@Test
fun test_with_controlled_time() {
    composeTestRule.mainClock.autoAdvance = false

    composeTestRule.setContent {
        TimerScreen()
    }

    // Manually advance time
    composeTestRule.mainClock.advanceTimeBy(1000)

    composeTestRule.onNodeWithText("1 second").assertExists()

    composeTestRule.mainClock.advanceTimeBy(2000)

    composeTestRule.onNodeWithText("3 seconds").assertExists()
}
```

### Screenshot Testing

```kotlin
@Test
fun loginScreen_screenshot() {
    composeTestRule.setContent {
        LoginScreen()
    }

    // Capture screenshot
    composeTestRule.onRoot().captureToImage()
        .asAndroidBitmap()
        .save("login_screen.png")
}

// Или используя screenshot testing libraries (Paparazzi, Shot, etc.)
```

### Best Practices

```kotlin
// - 1. Используйте test tags вместо text
modifier = Modifier.testTag("submit_button")

// - 2. Тестируйте поведение, не реализацию
@Test
fun `clicking submit sends data`() {
    // НЕ тестируем что вызвался viewModel.submit()
    // Тестируем что UI показал success state
    composeTestRule.onNodeWithText("Success").assertExists()
}

// - 3. Используйте meaningful test tags
modifier = Modifier.testTag("email_input") // GOOD
modifier = Modifier.testTag("input1")      // BAD

// - 4. waitUntil для async operations
composeTestRule.waitUntil {
    composeTestRule.onAllNodesWithTag("item")
        .fetchSemanticsNodes().size == expectedSize
}

// - 5. Тестируйте accessibility
composeTestRule.onNodeWithTag("icon")
    .assertContentDescriptionEquals("Profile picture")

// - 6. Группируйте related tests
class LoginScreenTest {
    @Test fun `empty fields show error`() { }
    @Test fun `valid fields enable button`() { }
    @Test fun `clicking login shows loading`() { }
}

// - 7. Setup в @Before
@Before
fun setup() {
    composeTestRule.setContent {
        MyApp()
    }
}
```

### Common Pitfalls

```kotlin
// - 1. Забыли useUnmergedTree
composeTestRule.onNodeWithText("Subtitle").assertExists() // Fail если merged

// - Fix
composeTestRule.onNodeWithText("Subtitle", useUnmergedTree = true).assertExists()

// - 2. Не ждем async операций
viewModel.loadData()
composeTestRule.onNodeWithText("Data").assertExists() // Fail - еще не загружено

// - Fix
viewModel.loadData()
composeTestRule.waitUntil {
    composeTestRule.onAllNodesWithText("Data").fetchSemanticsNodes().isNotEmpty()
}

// - 3. Тестируем text вместо semantics
composeTestRule.onNodeWithText("Submit").performClick()
// Проблема: сломается при локализации

// - Fix
composeTestRule.onNodeWithTag("submit_button").performClick()

// - 4. Забыли mainClock для анимаций
composeTestRule.onNodeWithTag("animated").assertExists() // Fail - анимация еще идет

// - Fix
composeTestRule.mainClock.advanceTimeBy(1000)
composeTestRule.onNodeWithTag("animated").assertExists()
```

### Dependencies

```gradle
androidTestImplementation "androidx.compose.ui:ui-test-junit4:1.5.4"
debugImplementation "androidx.compose.ui:ui-test-manifest:1.5.4"
```

**English**: **Compose UI testing** uses declarative API for finding, interacting, and verifying composable functions.

**Key APIs**: (1) **createComposeRule()** - creates test environment, manages composition lifecycle, syncs with recomposition. (2) **Finders** - onNodeWithText, onNodeWithTag, onNodeWithContentDescription, onNode(matcher). (3) **Actions** - performClick, performTextInput, performScrollTo, performTouchInput. (4) **Assertions** - assertExists, assertIsDisplayed, assertIsEnabled, assertTextEquals.

**Test tags**: Best practice for finding elements. Use `Modifier.testTag("element_id")`. More stable than text (localization). Explicit testable elements. Faster than text search.

**Testing patterns**: Test state changes (click → verify new state). Test lists with scrolling. Test ViewModels with setContent. Use waitUntil for async. Test navigation with TestNavHostController. Test dialogs/bottom sheets visibility.

**unmergedTree**: Compose merges child semantics by default. Use `useUnmergedTree = true` to find nested elements. Or disable merging with semantics modifier.

**Time control**: mainClock.autoAdvance = false for manual time. mainClock.advanceTimeBy(millis) for animations. waitUntil with timeout for async loading.

**Best practices**: Use test tags not text. Test behavior not implementation. Use meaningful tag names. Test accessibility (content descriptions). Group related tests. Setup in @Before. Use waitUntil for async operations.

