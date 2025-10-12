---
id: 20251012-140700
title: "Compose Testing / Тестирование Compose"
aliases: []

# Classification
topic: android
subtopics: [jetpack-compose, testing, ui-testing, semantics, test-rules]
question_kind: practical
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Created for vault completeness

# Workflow & relations
status: draft
moc: moc-android
related: [q-compose-ui-testing-advanced--testing--hard, q-jetpack-compose-basics--android--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [android, jetpack-compose, testing, ui-testing, semantics, difficulty/medium]
---

# Question (EN)
> How to test Jetpack Compose UI? What are ComposeTestRule, semantic matchers, and how to test user interactions, state changes, and async operations?

# Вопрос (RU)
> Как тестировать UI в Jetpack Compose? Что такое ComposeTestRule, semantic matchers и как тестировать взаимодействия пользователя, изменения состояния и async операции?

---

## Answer (EN)

**Compose Testing** uses a semantic tree (not View hierarchy) to find and interact with UI elements, making tests more robust and maintainable. Tests can run synchronously while Compose handles recomposition.

### Setup

#### 1. Add Dependencies

```kotlin
// build.gradle.kts (module level)
android {
    // ...

    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}

dependencies {
    // Compose testing
    androidTestImplementation("androidx.compose.ui:ui-test-junit4:1.5.4")
    debugImplementation("androidx.compose.ui:ui-test-manifest:1.5.4")

    // Optional: for testing ViewModels
    androidTestImplementation("androidx.arch.core:core-testing:2.2.0")

    // Optional: for Hilt testing
    androidTestImplementation("com.google.dagger:hilt-android-testing:2.48")
    kaptAndroidTest("com.google.dagger:hilt-android-compiler:2.48")
}
```

#### 2. Create Test Class

```kotlin
class LoginScreenTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun loginScreen_displaysCorrectly() {
        composeTestRule.setContent {
            LoginScreen()
        }

        // Assertions here
    }
}
```

### ComposeTestRule

**ComposeTestRule** is the entry point for Compose tests. It provides:
- `setContent {}` - Set composable content
- `onNode...()` - Find single node
- `onAllNodes...()` - Find multiple nodes
- `waitForIdle()` - Wait for recomposition
- `mainClock` - Control time

```kotlin
@get:Rule
val composeTestRule = createComposeRule()

// For testing with Activity
@get:Rule
val composeTestRule = createAndroidComposeRule<MainActivity>()
```

### Finding Nodes with Semantic Matchers

#### 1. By Text

```kotlin
@Test
fun findByText() {
    composeTestRule.setContent {
        Text("Welcome")
        Button(onClick = {}) {
            Text("Login")
        }
    }

    // Exact match
    composeTestRule.onNodeWithText("Welcome").assertExists()

    // Substring match
    composeTestRule.onNodeWithText("Wel", substring = true).assertExists()

    // Ignore case
    composeTestRule.onNodeWithText("WELCOME", ignoreCase = true).assertExists()
}
```

#### 2. By Test Tag

**Best practice:** Use `testTag` for stable element identification.

```kotlin
@Composable
fun LoginButton(onClick: () -> Unit) {
    Button(
        onClick = onClick,
        modifier = Modifier.testTag("login_button")  // Test tag
    ) {
        Text("Login")
    }
}

@Test
fun findByTestTag() {
    composeTestRule.setContent {
        LoginButton(onClick = {})
    }

    composeTestRule.onNodeWithTag("login_button")
        .assertExists()
        .assertIsEnabled()
        .assertHasClickAction()
}
```

#### 3. By Content Description

```kotlin
@Test
fun findByContentDescription() {
    composeTestRule.setContent {
        Icon(
            imageVector = Icons.Default.Close,
            contentDescription = "Close dialog"
        )
    }

    composeTestRule
        .onNodeWithContentDescription("Close dialog")
        .assertExists()
}
```

#### 4. By Semantic Properties

```kotlin
@Test
fun findBySemantics() {
    composeTestRule.setContent {
        TextField(
            value = "hello@example.com",
            onValueChange = {},
            modifier = Modifier.semantics {
                testTag = "email_field"
                contentDescription = "Email input"
            }
        )
    }

    // Find using semantic properties
    composeTestRule
        .onNode(
            hasTestTag("email_field") and
            hasContentDescription("Email input")
        )
        .assertExists()
}
```

### Assertions

#### Common Assertions

```kotlin
@Test
fun assertionsExamples() {
    composeTestRule.setContent {
        Column {
            Text("Title", modifier = Modifier.testTag("title"))
            Button(
                onClick = {},
                enabled = false,
                modifier = Modifier.testTag("button")
            ) {
                Text("Disabled")
            }
        }
    }

    // Existence
    composeTestRule.onNodeWithTag("title").assertExists()
    composeTestRule.onNodeWithTag("missing").assertDoesNotExist()

    // Display
    composeTestRule.onNodeWithTag("title").assertIsDisplayed()
    composeTestRule.onNodeWithTag("title").assertIsNotDisplayed()  // If scrolled away

    // Enabled/Disabled
    composeTestRule.onNodeWithTag("button").assertIsNotEnabled()
    composeTestRule.onNodeWithTag("button").assertIsEnabled()  // Would fail

    // Text content
    composeTestRule.onNodeWithTag("title")
        .assertTextEquals("Title")
        .assertTextContains("Tit")

    // Click action
    composeTestRule.onNodeWithTag("button").assertHasClickAction()
}
```

#### Multiple Nodes

```kotlin
@Test
fun multipleNodes() {
    composeTestRule.setContent {
        LazyColumn {
            items(5) { index ->
                Text("Item $index", modifier = Modifier.testTag("item_$index"))
            }
        }
    }

    // Find all nodes with "Item" text
    composeTestRule
        .onAllNodesWithText("Item", substring = true)
        .assertCountEquals(5)

    // Access specific node from collection
    composeTestRule
        .onAllNodesWithText("Item", substring = true)[2]
        .assertTextEquals("Item 2")

    // Filter collection
    composeTestRule
        .onAllNodesWithText("Item", substring = true)
        .filterToOne(hasTestTag("item_3"))
        .assertExists()
}
```

### User Interactions

#### 1. Click

```kotlin
@Test
fun clickInteraction() {
    var clicked = false

    composeTestRule.setContent {
        Button(
            onClick = { clicked = true },
            modifier = Modifier.testTag("button")
        ) {
            Text("Click Me")
        }
    }

    composeTestRule.onNodeWithTag("button").performClick()

    assert(clicked)
}
```

#### 2. Text Input

```kotlin
@Test
fun textInput() {
    var text = ""

    composeTestRule.setContent {
        TextField(
            value = text,
            onValueChange = { text = it },
            modifier = Modifier.testTag("input")
        )
    }

    // Type text
    composeTestRule
        .onNodeWithTag("input")
        .performTextInput("Hello")

    composeTestRule
        .onNodeWithTag("input")
        .assertTextEquals("Hello")

    // Clear text
    composeTestRule
        .onNodeWithTag("input")
        .performTextClearance()

    composeTestRule
        .onNodeWithTag("input")
        .assertTextEquals("")

    // Replace text
    composeTestRule
        .onNodeWithTag("input")
        .performTextReplacement("New Text")

    composeTestRule
        .onNodeWithTag("input")
        .assertTextEquals("New Text")
}
```

#### 3. Scroll

```kotlin
@Test
fun scrollInteraction() {
    composeTestRule.setContent {
        LazyColumn(modifier = Modifier.testTag("list")) {
            items(100) { index ->
                Text("Item $index", modifier = Modifier.testTag("item_$index"))
            }
        }
    }

    // Initially, item 50 is not displayed
    composeTestRule.onNodeWithTag("item_50").assertDoesNotExist()

    // Scroll to item
    composeTestRule
        .onNodeWithTag("list")
        .performScrollToNode(hasTestTag("item_50"))

    // Now it's displayed
    composeTestRule.onNodeWithTag("item_50").assertIsDisplayed()

    // Scroll to top
    composeTestRule
        .onNodeWithTag("list")
        .performScrollToIndex(0)

    composeTestRule.onNodeWithTag("item_0").assertIsDisplayed()
}
```

#### 4. Gestures

```kotlin
@Test
fun gestureInteractions() {
    var swiped = false

    composeTestRule.setContent {
        Box(
            modifier = Modifier
                .size(200.dp)
                .testTag("swipeable")
                .swipeable(
                    state = rememberSwipeableState(0),
                    anchors = mapOf(0f to 0, 200f to 1),
                    thresholds = { _, _ -> FractionalThreshold(0.5f) },
                    orientation = Orientation.Horizontal,
                    onSwipe = { swiped = true }
                )
        )
    }

    // Swipe gestures
    composeTestRule
        .onNodeWithTag("swipeable")
        .performTouchInput {
            swipeLeft()
            swipeRight()
            swipeUp()
            swipeDown()
        }
}
```

### Testing State Changes

#### 1. State Updates

```kotlin
@Test
fun stateChanges() {
    composeTestRule.setContent {
        var count by remember { mutableStateOf(0) }

        Column {
            Text("Count: $count", modifier = Modifier.testTag("counter"))
            Button(
                onClick = { count++ },
                modifier = Modifier.testTag("increment")
            ) {
                Text("Increment")
            }
        }
    }

    // Initial state
    composeTestRule
        .onNodeWithTag("counter")
        .assertTextEquals("Count: 0")

    // Trigger state change
    composeTestRule
        .onNodeWithTag("increment")
        .performClick()

    // Wait for recomposition
    composeTestRule.waitForIdle()

    // Verify new state
    composeTestRule
        .onNodeWithTag("counter")
        .assertTextEquals("Count: 1")
}
```

#### 2. Conditional UI

```kotlin
@Test
fun conditionalUI() {
    composeTestRule.setContent {
        var showDetails by remember { mutableStateOf(false) }

        Column {
            Button(
                onClick = { showDetails = !showDetails },
                modifier = Modifier.testTag("toggle")
            ) {
                Text(if (showDetails) "Hide" else "Show")
            }

            if (showDetails) {
                Text("Details", modifier = Modifier.testTag("details"))
            }
        }
    }

    // Initially hidden
    composeTestRule.onNodeWithTag("details").assertDoesNotExist()

    // Show details
    composeTestRule.onNodeWithTag("toggle").performClick()
    composeTestRule.waitForIdle()

    composeTestRule.onNodeWithTag("details").assertExists()

    // Hide details
    composeTestRule.onNodeWithTag("toggle").performClick()
    composeTestRule.waitForIdle()

    composeTestRule.onNodeWithTag("details").assertDoesNotExist()
}
```

### Testing Async Operations

#### 1. LaunchedEffect

```kotlin
@Test
fun launchedEffect() {
    composeTestRule.setContent {
        var data by remember { mutableStateOf<String?>(null) }

        LaunchedEffect(Unit) {
            delay(1000)
            data = "Loaded"
        }

        if (data == null) {
            CircularProgressIndicator(modifier = Modifier.testTag("loading"))
        } else {
            Text(data!!, modifier = Modifier.testTag("data"))
        }
    }

    // Initially loading
    composeTestRule.onNodeWithTag("loading").assertExists()

    // Wait for data to load
    composeTestRule.waitUntil(timeoutMillis = 2000) {
        composeTestRule
            .onAllNodesWithTag("data")
            .fetchSemanticsNodes()
            .isNotEmpty()
    }

    // Data is loaded
    composeTestRule.onNodeWithTag("data")
        .assertExists()
        .assertTextEquals("Loaded")
}
```

#### 2. ViewModel with StateFlow

```kotlin
class UserViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadUser() {
        viewModelScope.launch {
            delay(500)
            _uiState.value = UiState.Success(User("John", "john@example.com"))
        }
    }
}

sealed interface UiState {
    object Loading : UiState
    data class Success(val user: User) : UiState
    data class Error(val message: String) : UiState
}

data class User(val name: String, val email: String)

@Test
fun viewModelStateFlow() {
    val viewModel = UserViewModel()

    composeTestRule.setContent {
        val uiState by viewModel.uiState.collectAsState()

        when (uiState) {
            is UiState.Loading -> CircularProgressIndicator(Modifier.testTag("loading"))
            is UiState.Success -> {
                val user = (uiState as UiState.Success).user
                Text("Welcome ${user.name}", modifier = Modifier.testTag("welcome"))
            }
            is UiState.Error -> Text("Error", modifier = Modifier.testTag("error"))
        }
    }

    // Initially loading
    composeTestRule.onNodeWithTag("loading").assertExists()

    // Trigger load
    viewModel.loadUser()

    // Wait for success state
    composeTestRule.waitUntil(timeoutMillis = 1000) {
        composeTestRule
            .onAllNodesWithTag("welcome")
            .fetchSemanticsNodes()
            .isNotEmpty()
    }

    composeTestRule
        .onNodeWithTag("welcome")
        .assertTextContains("Welcome John")
}
```

### Testing with Hilt

```kotlin
@HiltAndroidTest
class ProductScreenTest {
    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @get:Rule(order = 1)
    val composeTestRule = createAndroidComposeRule<MainActivity>()

    @Inject
    lateinit var repository: ProductRepository

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun productScreen_loadAndDisplay() {
        composeTestRule.setContent {
            val viewModel: ProductViewModel = hiltViewModel()
            ProductScreen(viewModel = viewModel)
        }

        // Wait for data to load
        composeTestRule.waitForIdle()

        // Verify products displayed
        composeTestRule.onNodeWithText("Product 1").assertIsDisplayed()
    }
}
```

### Real-World Example: Login Form

```kotlin
@Composable
fun LoginScreen(
    onLogin: (String, String) -> Unit = { _, _ -> },
    onForgotPassword: () -> Unit = {}
) {
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var emailError by remember { mutableStateOf<String?>(null) }
    var isLoading by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center
    ) {
        TextField(
            value = email,
            onValueChange = {
                email = it
                emailError = if (it.contains("@")) null else "Invalid email"
            },
            label = { Text("Email") },
            isError = emailError != null,
            modifier = Modifier
                .fillMaxWidth()
                .testTag("email_field")
        )

        emailError?.let {
            Text(
                text = it,
                color = MaterialTheme.colorScheme.error,
                modifier = Modifier.testTag("email_error")
            )
        }

        Spacer(modifier = Modifier.height(8.dp))

        TextField(
            value = password,
            onValueChange = { password = it },
            label = { Text("Password") },
            visualTransformation = PasswordVisualTransformation(),
            modifier = Modifier
                .fillMaxWidth()
                .testTag("password_field")
        )

        Spacer(modifier = Modifier.height(16.dp))

        Button(
            onClick = {
                if (emailError == null && password.isNotEmpty()) {
                    isLoading = true
                    onLogin(email, password)
                }
            },
            enabled = !isLoading && emailError == null && password.isNotEmpty(),
            modifier = Modifier
                .fillMaxWidth()
                .testTag("login_button")
        ) {
            if (isLoading) {
                CircularProgressIndicator(
                    modifier = Modifier.size(20.dp),
                    color = MaterialTheme.colorScheme.onPrimary
                )
            } else {
                Text("Login")
            }
        }

        TextButton(
            onClick = onForgotPassword,
            modifier = Modifier.testTag("forgot_password")
        ) {
            Text("Forgot Password?")
        }
    }
}

class LoginScreenTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun loginScreen_initialState() {
        composeTestRule.setContent {
            LoginScreen()
        }

        composeTestRule.onNodeWithTag("email_field").assertExists()
        composeTestRule.onNodeWithTag("password_field").assertExists()
        composeTestRule.onNodeWithTag("login_button")
            .assertExists()
            .assertIsNotEnabled()
    }

    @Test
    fun loginScreen_emailValidation() {
        composeTestRule.setContent {
            LoginScreen()
        }

        // Enter invalid email
        composeTestRule
            .onNodeWithTag("email_field")
            .performTextInput("invalidemail")

        composeTestRule.waitForIdle()

        // Error shown
        composeTestRule
            .onNodeWithTag("email_error")
            .assertExists()
            .assertTextEquals("Invalid email")

        // Button disabled
        composeTestRule
            .onNodeWithTag("login_button")
            .assertIsNotEnabled()

        // Enter valid email
        composeTestRule
            .onNodeWithTag("email_field")
            .performTextClearance()

        composeTestRule
            .onNodeWithTag("email_field")
            .performTextInput("user@example.com")

        composeTestRule.waitForIdle()

        // Error gone
        composeTestRule.onNodeWithTag("email_error").assertDoesNotExist()
    }

    @Test
    fun loginScreen_submitForm() {
        var submittedEmail = ""
        var submittedPassword = ""

        composeTestRule.setContent {
            LoginScreen(
                onLogin = { email, password ->
                    submittedEmail = email
                    submittedPassword = password
                }
            )
        }

        // Fill form
        composeTestRule
            .onNodeWithTag("email_field")
            .performTextInput("user@example.com")

        composeTestRule
            .onNodeWithTag("password_field")
            .performTextInput("password123")

        composeTestRule.waitForIdle()

        // Button enabled
        composeTestRule.onNodeWithTag("login_button").assertIsEnabled()

        // Submit
        composeTestRule.onNodeWithTag("login_button").performClick()

        // Verify callback
        assertEquals("user@example.com", submittedEmail)
        assertEquals("password123", submittedPassword)
    }

    @Test
    fun loginScreen_forgotPassword() {
        var forgotPasswordClicked = false

        composeTestRule.setContent {
            LoginScreen(
                onForgotPassword = { forgotPasswordClicked = true }
            )
        }

        composeTestRule
            .onNodeWithTag("forgot_password")
            .performClick()

        assert(forgotPasswordClicked)
    }
}
```

### Best Practices

1. **Use testTag for stable identification** - Text can change with localization
2. **Wait for idle** - Call `waitForIdle()` after state changes
3. **Use semantic matchers** - They're more robust than text matching
4. **Test user flows, not implementation** - Focus on what users see and do
5. **Isolate tests** - Each test should be independent
6. **Mock dependencies** - Use Hilt, test doubles, or fake implementations
7. **Test accessibility** - Ensure content descriptions are present
8. **Use descriptive test names** - `loginScreen_invalidEmail_showsError()`
9. **Test edge cases** - Empty states, errors, loading states
10. **Keep tests fast** - Avoid unnecessary delays

### Common Patterns

#### Loading State

```kotlin
@Test
fun showsLoadingState() {
    composeTestRule.setContent {
        LoadingScreen()
    }

    composeTestRule
        .onNode(isProgressIndicator())
        .assertExists()
}

fun isProgressIndicator(): SemanticsMatcher {
    return SemanticsMatcher.expectValue(
        SemanticsProperties.ProgressBarRangeInfo,
        ProgressBarRangeInfo.Indeterminate
    )
}
```

#### Error State

```kotlin
@Test
fun showsErrorState() {
    composeTestRule.setContent {
        ErrorScreen(
            message = "Network error",
            onRetry = {}
        )
    }

    composeTestRule.onNodeWithText("Network error").assertIsDisplayed()
    composeTestRule.onNodeWithText("Retry").assertHasClickAction()
}
```

#### Empty State

```kotlin
@Test
fun showsEmptyState() {
    composeTestRule.setContent {
        ProductList(products = emptyList())
    }

    composeTestRule.onNodeWithText("No products found").assertIsDisplayed()
}
```

---

## Ответ (RU)

**Compose Testing** использует semantic tree (не View hierarchy) для поиска и взаимодействия с UI элементами, делая тесты более надежными и поддерживаемыми.

### Настройка

```kotlin
// build.gradle.kts
dependencies {
    androidTestImplementation("androidx.compose.ui:ui-test-junit4:1.5.4")
    debugImplementation("androidx.compose.ui:ui-test-manifest:1.5.4")
}
```

### ComposeTestRule

```kotlin
class LoginScreenTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun loginScreen_displaysCorrectly() {
        composeTestRule.setContent {
            LoginScreen()
        }
    }
}
```

### Поиск элементов

```kotlin
// По тексту
composeTestRule.onNodeWithText("Welcome").assertExists()

// По testTag (лучшая практика)
composeTestRule.onNodeWithTag("login_button").assertExists()

// По content description
composeTestRule.onNodeWithContentDescription("Close").assertExists()
```

### Взаимодействия

```kotlin
// Клик
composeTestRule.onNodeWithTag("button").performClick()

// Ввод текста
composeTestRule.onNodeWithTag("input").performTextInput("Hello")

// Скролл
composeTestRule
    .onNodeWithTag("list")
    .performScrollToNode(hasTestTag("item_50"))
```

### Тестирование состояния

```kotlin
@Test
fun stateChanges() {
    composeTestRule.setContent {
        var count by remember { mutableStateOf(0) }

        Button(onClick = { count++ }) {
            Text("Count: $count")
        }
    }

    composeTestRule.onNodeWithText("Count: 0").assertExists()
    composeTestRule.onNodeWithTag("button").performClick()
    composeTestRule.waitForIdle()
    composeTestRule.onNodeWithText("Count: 1").assertExists()
}
```

### Тестирование async операций

```kotlin
@Test
fun asyncOperations() {
    // Ждать пока элемент появится
    composeTestRule.waitUntil(timeoutMillis = 2000) {
        composeTestRule
            .onAllNodesWithTag("data")
            .fetchSemanticsNodes()
            .isNotEmpty()
    }
}
```

### Best Practices (Лучшие практики)

1. **Используйте testTag** для стабильной идентификации
2. **Вызывайте waitForIdle()** после изменений состояния
3. **Используйте semantic matchers** - они более надежные
4. **Тестируйте пользовательские потоки**, не реализацию
5. **Изолируйте тесты** - каждый тест должен быть независимым
6. **Мокируйте зависимости** - используйте Hilt или fake implementations
7. **Тестируйте accessibility** - убедитесь что content descriptions присутствуют

---

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
- [[q-compose-stability-skippability--jetpack-compose--hard]] - Stability & skippability
- [[q-stable-classes-compose--android--hard]] - @Stable annotation
- [[q-stable-annotation-compose--android--hard]] - Stability annotations

## References

- [Compose Testing Documentation](https://developer.android.com/jetpack/compose/testing)
- [Testing cheatsheet](https://developer.android.com/jetpack/compose/testing-cheatsheet)
- [Semantics in Compose](https://developer.android.com/jetpack/compose/semantics)

## MOC Links

- [[moc-android]]
