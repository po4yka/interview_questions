---
id: android-test-004
title: Compose Testing Semantics / Семантика тестирования Compose
aliases:
- Compose Testing Semantics
- Семантика тестирования Compose
topic: android
subtopics:
- testing-ui
- ui-compose
- testing
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-testing
- c-jetpack-compose
- q-testing-compose-ui--android--medium
- q-jetpack-compose-basics--android--medium
created: 2026-01-23
updated: 2026-01-23
tags:
- android/testing-ui
- android/ui-compose
- difficulty/medium
- compose
- semantics
- test-tags
- accessibility
anki_cards:
- slug: android-test-004-0-en
  language: en
- slug: android-test-004-0-ru
  language: ru
---
# Vopros (RU)

> Что такое семантика в Compose и как использовать test tags для тестирования UI?

# Question (EN)

> What are semantics in Compose and how do you use test tags for UI testing?

---

## Otvet (RU)

**Семантика (Semantics)** в Compose - это способ описания UI-элементов для accessibility-сервисов и тестового фреймворка. Test tags - это специальные семантические свойства для идентификации элементов в тестах.

### Краткий Ответ

- **Semantics** - метаданные UI для accessibility и тестирования
- **testTag** - уникальный идентификатор элемента для тестов
- **contentDescription** - описание для screen readers
- Семантика объединяется по иерархии (mergeDescendants)

### Подробный Ответ

### Что такое Семантика

```kotlin
// Семантика - это невидимые метаданные, описывающие UI
@Composable
fun ProfileCard(user: User) {
    Card(
        modifier = Modifier
            .semantics {
                // Семантические свойства
                contentDescription = "Profile card for ${user.name}"
                testTag = "profile_card"
            }
    ) {
        Text(user.name)
    }
}
```

### Test Tags - Основной Способ Идентификации

```kotlin
@Composable
fun LoginScreen(
    email: String,
    onEmailChange: (String) -> Unit,
    password: String,
    onPasswordChange: (String) -> Unit,
    onLogin: () -> Unit,
    isLoading: Boolean
) {
    Column(modifier = Modifier.testTag("login_screen")) {
        TextField(
            value = email,
            onValueChange = onEmailChange,
            label = { Text("Email") },
            modifier = Modifier.testTag("email_input")
        )

        TextField(
            value = password,
            onValueChange = onPasswordChange,
            label = { Text("Password") },
            visualTransformation = PasswordVisualTransformation(),
            modifier = Modifier.testTag("password_input")
        )

        Button(
            onClick = onLogin,
            enabled = !isLoading,
            modifier = Modifier.testTag("login_button")
        ) {
            if (isLoading) {
                CircularProgressIndicator(
                    modifier = Modifier
                        .size(16.dp)
                        .testTag("loading_indicator")
                )
            } else {
                Text("Login")
            }
        }
    }
}
```

### Тестирование с Test Tags

```kotlin
class LoginScreenTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun emailInput_acceptsText() {
        composeTestRule.setContent {
            LoginScreen(
                email = "",
                onEmailChange = {},
                password = "",
                onPasswordChange = {},
                onLogin = {},
                isLoading = false
            )
        }

        // Поиск по testTag - самый надежный способ
        composeTestRule
            .onNodeWithTag("email_input")
            .performTextInput("test@example.com")

        composeTestRule
            .onNodeWithTag("email_input")
            .assertTextContains("test@example.com")
    }

    @Test
    fun loginButton_showsLoading() {
        composeTestRule.setContent {
            LoginScreen(
                email = "test@example.com",
                onEmailChange = {},
                password = "password",
                onPasswordChange = {},
                onLogin = {},
                isLoading = true
            )
        }

        composeTestRule
            .onNodeWithTag("loading_indicator")
            .assertIsDisplayed()

        composeTestRule
            .onNodeWithTag("login_button")
            .assertIsNotEnabled()
    }
}
```

### Семантические Matchers

```kotlin
@Test
fun semanticMatchersExample() {
    composeTestRule.setContent {
        ProfileScreen()
    }

    // По testTag
    composeTestRule.onNodeWithTag("profile_image").assertExists()

    // По contentDescription (для accessibility)
    composeTestRule
        .onNodeWithContentDescription("User avatar")
        .assertExists()

    // По тексту
    composeTestRule
        .onNodeWithText("John Doe")
        .assertExists()

    // Комбинация условий
    composeTestRule
        .onNode(
            hasTestTag("submit_button") and isEnabled()
        )
        .assertExists()

    // Поиск внутри контейнера
    composeTestRule
        .onNodeWithTag("user_list")
        .onChildren()
        .filter(hasTestTag("user_item"))
        .assertCountEquals(5)
}
```

### Semantics Modifier

```kotlin
@Composable
fun AccessibleButton(
    text: String,
    onClick: () -> Unit,
    testTag: String
) {
    Button(
        onClick = onClick,
        modifier = Modifier
            .testTag(testTag)
            .semantics {
                // Описание для screen readers
                contentDescription = "Button: $text"

                // Роль элемента
                role = Role.Button

                // Состояние
                stateDescription = "Clickable"
            }
    ) {
        Text(text)
    }
}

@Composable
fun ProgressBar(
    progress: Float,
    modifier: Modifier = Modifier
) {
    LinearProgressIndicator(
        progress = { progress },
        modifier = modifier
            .testTag("progress_bar")
            .semantics {
                // Информация о прогрессе для accessibility
                progressBarRangeInfo = ProgressBarRangeInfo(
                    current = progress,
                    range = 0f..1f
                )
            }
    )
}
```

### Тестирование Семантических Свойств

```kotlin
@Test
fun progressBar_hasCorrectProgress() {
    composeTestRule.setContent {
        ProgressBar(progress = 0.5f)
    }

    composeTestRule
        .onNodeWithTag("progress_bar")
        .assert(
            hasProgressBarRangeInfo(
                ProgressBarRangeInfo(
                    current = 0.5f,
                    range = 0f..1f
                )
            )
        )
}

@Test
fun button_hasCorrectContentDescription() {
    composeTestRule.setContent {
        AccessibleButton(
            text = "Submit",
            onClick = {},
            testTag = "submit_btn"
        )
    }

    composeTestRule
        .onNodeWithTag("submit_btn")
        .assertContentDescriptionContains("Button: Submit")
}
```

### Объединение Семантики (Merge Semantics)

```kotlin
@Composable
fun ListItem(
    title: String,
    subtitle: String
) {
    // По умолчанию семантика дочерних элементов объединяется
    Row(
        modifier = Modifier
            .clickable { }
            .semantics(mergeDescendants = true) {
                testTag = "list_item"
            }
    ) {
        Column {
            Text(title)
            Text(subtitle)
        }
    }
}

// Тест
@Test
fun listItem_mergedSemantics() {
    composeTestRule.setContent {
        ListItem(title = "Title", subtitle = "Subtitle")
    }

    // При mergeDescendants = true текст объединяется
    composeTestRule
        .onNodeWithTag("list_item")
        .assertTextContains("Title")
        .assertTextContains("Subtitle")
}
```

### useUnmergedTree для Вложенных Элементов

```kotlin
@Composable
fun CardWithActions(
    title: String,
    onEdit: () -> Unit,
    onDelete: () -> Unit
) {
    Card(modifier = Modifier.testTag("card")) {
        Column {
            Text(
                text = title,
                modifier = Modifier.testTag("card_title")
            )
            Row {
                IconButton(
                    onClick = onEdit,
                    modifier = Modifier.testTag("edit_button")
                ) {
                    Icon(Icons.Default.Edit, contentDescription = "Edit")
                }
                IconButton(
                    onClick = onDelete,
                    modifier = Modifier.testTag("delete_button")
                ) {
                    Icon(Icons.Default.Delete, contentDescription = "Delete")
                }
            }
        }
    }
}

@Test
fun cardWithActions_useUnmergedTree() {
    composeTestRule.setContent {
        CardWithActions(
            title = "Item",
            onEdit = {},
            onDelete = {}
        )
    }

    // Без useUnmergedTree вложенные теги могут быть недоступны
    composeTestRule
        .onNodeWithTag("edit_button", useUnmergedTree = true)
        .performClick()

    composeTestRule
        .onNodeWithTag("delete_button", useUnmergedTree = true)
        .assertExists()
}
```

### Семантика для LazyColumn

```kotlin
@Composable
fun UserList(users: List<User>) {
    LazyColumn(modifier = Modifier.testTag("user_list")) {
        items(users, key = { it.id }) { user ->
            UserItem(
                user = user,
                modifier = Modifier.testTag("user_item_${user.id}")
            )
        }
    }
}

@Test
fun userList_scrollToItem() {
    val users = (1..100).map { User(it.toString(), "User $it") }

    composeTestRule.setContent {
        UserList(users = users)
    }

    // Скролл к элементу по testTag
    composeTestRule
        .onNodeWithTag("user_list")
        .performScrollToNode(hasTestTag("user_item_50"))

    composeTestRule
        .onNodeWithTag("user_item_50")
        .assertIsDisplayed()
}
```

### Custom Semantic Properties

```kotlin
// Определение кастомного семантического свойства
val PriceKey = SemanticsPropertyKey<Float>("Price")
var SemanticsPropertyReceiver.price by PriceKey

@Composable
fun PriceTag(price: Float) {
    Text(
        text = "$${"%.2f".format(price)}",
        modifier = Modifier.semantics {
            this.price = price
            testTag = "price_tag"
        }
    )
}

// Кастомный matcher
fun hasPrice(expected: Float) = SemanticsMatcher("price = $expected") { node ->
    node.config.getOrNull(PriceKey) == expected
}

@Test
fun priceTag_hasCorrectPrice() {
    composeTestRule.setContent {
        PriceTag(price = 29.99f)
    }

    composeTestRule
        .onNode(hasPrice(29.99f))
        .assertExists()
}
```

### Соглашения по Именованию Test Tags

```kotlin
// Рекомендуемые паттерны именования

// Экраны
Modifier.testTag("login_screen")
Modifier.testTag("home_screen")

// Компоненты
Modifier.testTag("email_input")
Modifier.testTag("password_input")
Modifier.testTag("submit_button")

// Списки и элементы
Modifier.testTag("user_list")
Modifier.testTag("user_item_${user.id}")

// Состояния
Modifier.testTag("loading_indicator")
Modifier.testTag("error_message")
Modifier.testTag("empty_state")

// Константы для переиспользования
object TestTags {
    const val LOGIN_SCREEN = "login_screen"
    const val EMAIL_INPUT = "email_input"
    const val PASSWORD_INPUT = "password_input"
    const val LOGIN_BUTTON = "login_button"

    fun userItem(id: String) = "user_item_$id"
}
```

### Лучшие Практики

1. **Используйте testTag вместо текста** - устойчиво к локализации
2. **Выносите теги в константы** - избегайте опечаток
3. **Используйте осмысленные имена** - `email_input` вместо `tf1`
4. **Добавляйте contentDescription** для accessibility
5. **Учитывайте mergeDescendants** при работе с вложенными элементами
6. **Используйте useUnmergedTree** когда нужны вложенные теги

---

## Answer (EN)

**Semantics** in Compose is a way to describe UI elements for accessibility services and the testing framework. Test tags are special semantic properties for identifying elements in tests.

### Short Version

- **Semantics** - UI metadata for accessibility and testing
- **testTag** - unique identifier for elements in tests
- **contentDescription** - description for screen readers
- Semantics merge by hierarchy (mergeDescendants)

### Detailed Version

### What is Semantics

```kotlin
// Semantics are invisible metadata describing the UI
@Composable
fun ProfileCard(user: User) {
    Card(
        modifier = Modifier
            .semantics {
                // Semantic properties
                contentDescription = "Profile card for ${user.name}"
                testTag = "profile_card"
            }
    ) {
        Text(user.name)
    }
}
```

### Test Tags - Primary Identification Method

```kotlin
@Composable
fun LoginScreen(
    email: String,
    onEmailChange: (String) -> Unit,
    password: String,
    onPasswordChange: (String) -> Unit,
    onLogin: () -> Unit,
    isLoading: Boolean
) {
    Column(modifier = Modifier.testTag("login_screen")) {
        TextField(
            value = email,
            onValueChange = onEmailChange,
            label = { Text("Email") },
            modifier = Modifier.testTag("email_input")
        )

        TextField(
            value = password,
            onValueChange = onPasswordChange,
            label = { Text("Password") },
            visualTransformation = PasswordVisualTransformation(),
            modifier = Modifier.testTag("password_input")
        )

        Button(
            onClick = onLogin,
            enabled = !isLoading,
            modifier = Modifier.testTag("login_button")
        ) {
            if (isLoading) {
                CircularProgressIndicator(
                    modifier = Modifier
                        .size(16.dp)
                        .testTag("loading_indicator")
                )
            } else {
                Text("Login")
            }
        }
    }
}
```

### Testing with Test Tags

```kotlin
class LoginScreenTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun emailInput_acceptsText() {
        composeTestRule.setContent {
            LoginScreen(
                email = "",
                onEmailChange = {},
                password = "",
                onPasswordChange = {},
                onLogin = {},
                isLoading = false
            )
        }

        // Finding by testTag - most reliable approach
        composeTestRule
            .onNodeWithTag("email_input")
            .performTextInput("test@example.com")

        composeTestRule
            .onNodeWithTag("email_input")
            .assertTextContains("test@example.com")
    }

    @Test
    fun loginButton_showsLoading() {
        composeTestRule.setContent {
            LoginScreen(
                email = "test@example.com",
                onEmailChange = {},
                password = "password",
                onPasswordChange = {},
                onLogin = {},
                isLoading = true
            )
        }

        composeTestRule
            .onNodeWithTag("loading_indicator")
            .assertIsDisplayed()

        composeTestRule
            .onNodeWithTag("login_button")
            .assertIsNotEnabled()
    }
}
```

### Semantic Matchers

```kotlin
@Test
fun semanticMatchersExample() {
    composeTestRule.setContent {
        ProfileScreen()
    }

    // By testTag
    composeTestRule.onNodeWithTag("profile_image").assertExists()

    // By contentDescription (for accessibility)
    composeTestRule
        .onNodeWithContentDescription("User avatar")
        .assertExists()

    // By text
    composeTestRule
        .onNodeWithText("John Doe")
        .assertExists()

    // Combining conditions
    composeTestRule
        .onNode(
            hasTestTag("submit_button") and isEnabled()
        )
        .assertExists()

    // Finding within container
    composeTestRule
        .onNodeWithTag("user_list")
        .onChildren()
        .filter(hasTestTag("user_item"))
        .assertCountEquals(5)
}
```

### Semantics Modifier

```kotlin
@Composable
fun AccessibleButton(
    text: String,
    onClick: () -> Unit,
    testTag: String
) {
    Button(
        onClick = onClick,
        modifier = Modifier
            .testTag(testTag)
            .semantics {
                // Description for screen readers
                contentDescription = "Button: $text"

                // Element role
                role = Role.Button

                // State
                stateDescription = "Clickable"
            }
    ) {
        Text(text)
    }
}

@Composable
fun ProgressBar(
    progress: Float,
    modifier: Modifier = Modifier
) {
    LinearProgressIndicator(
        progress = { progress },
        modifier = modifier
            .testTag("progress_bar")
            .semantics {
                // Progress info for accessibility
                progressBarRangeInfo = ProgressBarRangeInfo(
                    current = progress,
                    range = 0f..1f
                )
            }
    )
}
```

### Testing Semantic Properties

```kotlin
@Test
fun progressBar_hasCorrectProgress() {
    composeTestRule.setContent {
        ProgressBar(progress = 0.5f)
    }

    composeTestRule
        .onNodeWithTag("progress_bar")
        .assert(
            hasProgressBarRangeInfo(
                ProgressBarRangeInfo(
                    current = 0.5f,
                    range = 0f..1f
                )
            )
        )
}

@Test
fun button_hasCorrectContentDescription() {
    composeTestRule.setContent {
        AccessibleButton(
            text = "Submit",
            onClick = {},
            testTag = "submit_btn"
        )
    }

    composeTestRule
        .onNodeWithTag("submit_btn")
        .assertContentDescriptionContains("Button: Submit")
}
```

### Merge Semantics

```kotlin
@Composable
fun ListItem(
    title: String,
    subtitle: String
) {
    // By default child semantics are merged
    Row(
        modifier = Modifier
            .clickable { }
            .semantics(mergeDescendants = true) {
                testTag = "list_item"
            }
    ) {
        Column {
            Text(title)
            Text(subtitle)
        }
    }
}

// Test
@Test
fun listItem_mergedSemantics() {
    composeTestRule.setContent {
        ListItem(title = "Title", subtitle = "Subtitle")
    }

    // With mergeDescendants = true text is merged
    composeTestRule
        .onNodeWithTag("list_item")
        .assertTextContains("Title")
        .assertTextContains("Subtitle")
}
```

### useUnmergedTree for Nested Elements

```kotlin
@Composable
fun CardWithActions(
    title: String,
    onEdit: () -> Unit,
    onDelete: () -> Unit
) {
    Card(modifier = Modifier.testTag("card")) {
        Column {
            Text(
                text = title,
                modifier = Modifier.testTag("card_title")
            )
            Row {
                IconButton(
                    onClick = onEdit,
                    modifier = Modifier.testTag("edit_button")
                ) {
                    Icon(Icons.Default.Edit, contentDescription = "Edit")
                }
                IconButton(
                    onClick = onDelete,
                    modifier = Modifier.testTag("delete_button")
                ) {
                    Icon(Icons.Default.Delete, contentDescription = "Delete")
                }
            }
        }
    }
}

@Test
fun cardWithActions_useUnmergedTree() {
    composeTestRule.setContent {
        CardWithActions(
            title = "Item",
            onEdit = {},
            onDelete = {}
        )
    }

    // Without useUnmergedTree nested tags may be inaccessible
    composeTestRule
        .onNodeWithTag("edit_button", useUnmergedTree = true)
        .performClick()

    composeTestRule
        .onNodeWithTag("delete_button", useUnmergedTree = true)
        .assertExists()
}
```

### Semantics for LazyColumn

```kotlin
@Composable
fun UserList(users: List<User>) {
    LazyColumn(modifier = Modifier.testTag("user_list")) {
        items(users, key = { it.id }) { user ->
            UserItem(
                user = user,
                modifier = Modifier.testTag("user_item_${user.id}")
            )
        }
    }
}

@Test
fun userList_scrollToItem() {
    val users = (1..100).map { User(it.toString(), "User $it") }

    composeTestRule.setContent {
        UserList(users = users)
    }

    // Scroll to element by testTag
    composeTestRule
        .onNodeWithTag("user_list")
        .performScrollToNode(hasTestTag("user_item_50"))

    composeTestRule
        .onNodeWithTag("user_item_50")
        .assertIsDisplayed()
}
```

### Custom Semantic Properties

```kotlin
// Define custom semantic property
val PriceKey = SemanticsPropertyKey<Float>("Price")
var SemanticsPropertyReceiver.price by PriceKey

@Composable
fun PriceTag(price: Float) {
    Text(
        text = "$${"%.2f".format(price)}",
        modifier = Modifier.semantics {
            this.price = price
            testTag = "price_tag"
        }
    )
}

// Custom matcher
fun hasPrice(expected: Float) = SemanticsMatcher("price = $expected") { node ->
    node.config.getOrNull(PriceKey) == expected
}

@Test
fun priceTag_hasCorrectPrice() {
    composeTestRule.setContent {
        PriceTag(price = 29.99f)
    }

    composeTestRule
        .onNode(hasPrice(29.99f))
        .assertExists()
}
```

### Test Tag Naming Conventions

```kotlin
// Recommended naming patterns

// Screens
Modifier.testTag("login_screen")
Modifier.testTag("home_screen")

// Components
Modifier.testTag("email_input")
Modifier.testTag("password_input")
Modifier.testTag("submit_button")

// Lists and items
Modifier.testTag("user_list")
Modifier.testTag("user_item_${user.id}")

// States
Modifier.testTag("loading_indicator")
Modifier.testTag("error_message")
Modifier.testTag("empty_state")

// Constants for reuse
object TestTags {
    const val LOGIN_SCREEN = "login_screen"
    const val EMAIL_INPUT = "email_input"
    const val PASSWORD_INPUT = "password_input"
    const val LOGIN_BUTTON = "login_button"

    fun userItem(id: String) = "user_item_$id"
}
```

### Best Practices

1. **Use testTag instead of text** - robust to localization
2. **Extract tags to constants** - avoid typos
3. **Use meaningful names** - `email_input` not `tf1`
4. **Add contentDescription** for accessibility
5. **Consider mergeDescendants** when working with nested elements
6. **Use useUnmergedTree** when nested tags are needed

---

## Follow-ups

- How do you debug semantics tree in Compose tests?
- What's the difference between semantics and state in Compose?
- How do you test accessibility compliance with semantics?

## References

- https://developer.android.com/jetpack/compose/testing
- https://developer.android.com/jetpack/compose/semantics
- https://developer.android.com/jetpack/compose/accessibility

## Related Questions

### Prerequisites (Easier)
- [[q-jetpack-compose-basics--android--medium]] - Compose fundamentals

### Related (Same Level)
- [[q-testing-compose-ui--android--medium]] - Compose UI testing
- [[q-mockk-basics--testing--medium]] - Mocking in tests

### Advanced (Harder)
- [[q-screenshot-testing--testing--hard]] - Screenshot testing
