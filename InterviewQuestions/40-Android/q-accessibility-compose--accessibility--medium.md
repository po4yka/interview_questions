---
tags:
  - android
  - accessibility
  - compose
  - talkback
  - inclusive-design
difficulty: medium
status: draft
related:
  - q-accessibility-talkback--accessibility--medium
  - q-accessibility-testing--accessibility--medium
  - q-custom-view-accessibility--custom-views--medium
created: 2025-10-11
---

# Question (EN)
How do you make Jetpack Compose UIs accessible? What are the key considerations for TalkBack support, content descriptions, semantic properties, and accessibility actions in Compose?

## Answer (EN)
### Overview

**Accessibility in Compose** ensures your app is usable by people with disabilities. Key aspects:
- ✅ Screen reader support (TalkBack)
- ✅ Content descriptions for non-text elements
- ✅ Semantic properties for meaningful navigation
- ✅ Touch target sizes (minimum 48dp)
- ✅ Sufficient color contrast
- ✅ Custom accessibility actions

### Basic Accessibility in Compose

**Content descriptions**:

```kotlin
@Composable
fun AccessibleImage() {
    Image(
        painter = painterResource(R.drawable.profile_photo),
        contentDescription = "User profile photo", // ✅ GOOD
        modifier = Modifier.size(64.dp)
    )

    // ❌ BAD - Decorative images should use null
    Image(
        painter = painterResource(R.drawable.background_pattern),
        contentDescription = null, // Decorative, no semantic meaning
        modifier = Modifier.fillMaxSize()
    )
}

@Composable
fun AccessibleIcon() {
    Icon(
        imageVector = Icons.Default.Favorite,
        contentDescription = "Add to favorites", // ✅ Action description
        modifier = Modifier.clickable { /* ... */ }
    )
}

@Composable
fun AccessibleButton() {
    IconButton(onClick = { /* delete */ }) {
        Icon(
            imageVector = Icons.Default.Delete,
            contentDescription = "Delete item" // ✅ Clear action
        )
    }
}
```

### Semantic Properties

**Modifier.semantics** - Add semantic information:

```kotlin
@Composable
fun CustomToggle(
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit
) {
    Box(
        modifier = Modifier
            .size(48.dp)
            .clickable { onCheckedChange(!checked) }
            .semantics {
                // Mark as toggleable
                this.role = Role.Switch
                this.toggleableState = ToggleableState(checked)
                this.contentDescription = if (checked) {
                    "Notifications enabled"
                } else {
                    "Notifications disabled"
                }
            }
            .background(
                color = if (checked) Color.Green else Color.Gray,
                shape = CircleShape
            )
    )
}

@Composable
fun CustomRating(rating: Float) {
    Row(
        modifier = Modifier.semantics(mergeDescendants = true) {
            // Merge child semantics into single announcement
            this.contentDescription = "$rating out of 5 stars"
        }
    ) {
        repeat(5) { index ->
            Icon(
                imageVector = if (index < rating) {
                    Icons.Default.Star
                } else {
                    Icons.Default.StarBorder
                },
                contentDescription = null, // Merged into parent
                tint = Color.Yellow
            )
        }
    }
}

@Composable
fun CustomSlider(
    value: Float,
    onValueChange: (Float) -> Unit,
    valueRange: ClosedFloatingPointRange<Float> = 0f..100f
) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(48.dp)
            .semantics {
                this.role = Role.Slider
                this.setProgress { targetValue ->
                    onValueChange(targetValue)
                    true
                }
                this.progressBarRangeInfo = ProgressBarRangeInfo(
                    current = value,
                    range = valueRange
                )
                this.contentDescription = "Volume: ${value.toInt()}%"
            }
    ) {
        // Custom slider UI
    }
}
```

### Accessibility Actions

**Custom actions for complex interactions**:

```kotlin
@Composable
fun EmailListItem(
    email: Email,
    onDelete: () -> Unit,
    onArchive: () -> Unit,
    onMarkUnread: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { /* Open email */ }
            .semantics {
                // Primary action (click)
                this.contentDescription = "Email from ${email.sender}: ${email.subject}"

                // Custom actions for TalkBack menu
                customActions = listOf(
                    CustomAccessibilityAction(
                        label = "Delete",
                        action = {
                            onDelete()
                            true
                        }
                    ),
                    CustomAccessibilityAction(
                        label = "Archive",
                        action = {
                            onArchive()
                            true
                        }
                    ),
                    CustomAccessibilityAction(
                        label = "Mark as unread",
                        action = {
                            onMarkUnread()
                            true
                        }
                    )
                )
            }
    ) {
        // Email content
        Column(modifier = Modifier.padding(16.dp)) {
            Text(text = email.sender, style = MaterialTheme.typography.titleMedium)
            Text(text = email.subject, style = MaterialTheme.typography.bodyMedium)
        }
    }
}
```

**How it works:**
- User focuses on email item with TalkBack
- Single-tap to hear description
- TalkBack menu shows custom actions: "Delete", "Archive", "Mark as unread"
- User selects action from menu

### Merge Descendants

**Simplify complex UI for screen readers**:

```kotlin
@Composable
fun ProductCard(product: Product) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { /* View product */ }
            .semantics(mergeDescendants = true) {
                // ✅ GOOD - Single announcement
                contentDescription = buildString {
                    append(product.name)
                    append(", ")
                    append("$${product.price}")
                    if (product.rating > 0) {
                        append(", ${product.rating} stars")
                    }
                    if (product.inStock) {
                        append(", In stock")
                    } else {
                        append(", Out of stock")
                    }
                }
            }
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(text = product.name)
            Text(text = "$${product.price}")
            RatingBar(rating = product.rating)
            Text(
                text = if (product.inStock) "In stock" else "Out of stock",
                color = if (product.inStock) Color.Green else Color.Red
            )
        }
    }
}

// Without mergeDescendants, TalkBack would announce each child separately:
// "iPhone 15" -> "$999" -> "4.5 stars" -> "In stock"
// With mergeDescendants:
// "iPhone 15, $999, 4.5 stars, In stock"
```

### Clear vs Merge Semantics

```kotlin
@Composable
fun SemanticExamples() {
    // Example 1: clearAndSetSemantics - Replace all child semantics
    Row(
        modifier = Modifier
            .clickable { /* ... */ }
            .clearAndSetSemantics {
                // ✅ Completely override child semantics
                contentDescription = "Settings button"
                role = Role.Button
            }
    ) {
        Icon(Icons.Default.Settings, contentDescription = "Icon") // Ignored
        Text("Settings") // Ignored
    }

    // Example 2: semantics(mergeDescendants = true) - Merge children
    Row(
        modifier = Modifier
            .clickable { /* ... */ }
            .semantics(mergeDescendants = true) {
                // ✅ Merge with children: "Icon, Settings"
                // Can add additional properties
            }
    ) {
        Icon(Icons.Default.Settings, contentDescription = "Icon")
        Text("Settings")
    }

    // Example 3: No semantic modifier - Each child announced separately
    Row(
        modifier = Modifier.clickable { /* ... */ }
    ) {
        // ❌ TalkBack announces each child individually
        Icon(Icons.Default.Settings, contentDescription = "Icon")
        Text("Settings")
    }
}
```

### State Descriptions

**Provide state information**:

```kotlin
@Composable
fun DownloadButton(
    downloadState: DownloadState,
    onDownloadClick: () -> Unit
) {
    Button(
        onClick = onDownloadClick,
        enabled = downloadState is DownloadState.Idle,
        modifier = Modifier.semantics {
            this.stateDescription = when (downloadState) {
                is DownloadState.Idle -> "Ready to download"
                is DownloadState.Downloading -> "Downloading: ${downloadState.progress}%"
                is DownloadState.Completed -> "Download completed"
                is DownloadState.Error -> "Download failed: ${downloadState.message}"
            }
        }
    ) {
        when (downloadState) {
            is DownloadState.Idle -> Text("Download")
            is DownloadState.Downloading -> {
                CircularProgressIndicator(
                    progress = downloadState.progress / 100f,
                    modifier = Modifier.size(24.dp)
                )
            }
            is DownloadState.Completed -> Icon(Icons.Default.Check, null)
            is DownloadState.Error -> Icon(Icons.Default.Error, null)
        }
    }
}

sealed class DownloadState {
    object Idle : DownloadState()
    data class Downloading(val progress: Int) : DownloadState()
    object Completed : DownloadState()
    data class Error(val message: String) : DownloadState()
}
```

### Touch Target Sizes

**Minimum 48dp for interactive elements**:

```kotlin
@Composable
fun AccessibleIconButton() {
    // ✅ GOOD - Minimum 48dp touch target
    IconButton(
        onClick = { /* ... */ },
        modifier = Modifier
            .size(48.dp) // Minimum size
            .semantics {
                contentDescription = "Delete"
            }
    ) {
        Icon(
            imageVector = Icons.Default.Delete,
            contentDescription = null, // Handled by parent
            modifier = Modifier.size(24.dp) // Icon size
        )
    }

    // ❌ BAD - Too small
    Icon(
        imageVector = Icons.Default.Delete,
        contentDescription = "Delete",
        modifier = Modifier
            .size(24.dp) // Only 24dp touch target!
            .clickable { /* ... */ }
    )

    // ✅ GOOD - Use padding to increase touch target
    Icon(
        imageVector = Icons.Default.Delete,
        contentDescription = "Delete",
        modifier = Modifier
            .size(24.dp)
            .clickable { /* ... */ }
            .padding(12.dp) // Adds 12dp on each side = 48dp total
    )
}
```

### Heading Semantics

**Structure content with headings**:

```kotlin
@Composable
fun AccessibleScreen() {
    Column {
        // ✅ Mark as heading for navigation
        Text(
            text = "Settings",
            style = MaterialTheme.typography.headlineLarge,
            modifier = Modifier.semantics {
                heading() // TalkBack can jump between headings
            }
        )

        Text(
            text = "Account Settings",
            style = MaterialTheme.typography.titleMedium,
            modifier = Modifier.semantics {
                heading()
            }
        )

        SwitchRow(
            title = "Notifications",
            checked = true,
            onCheckedChange = {}
        )

        SwitchRow(
            title = "Auto-sync",
            checked = false,
            onCheckedChange = {}
        )

        Text(
            text = "Privacy Settings",
            style = MaterialTheme.typography.titleMedium,
            modifier = Modifier.semantics {
                heading()
            }
        )

        SwitchRow(
            title = "Location Services",
            checked = true,
            onCheckedChange = {}
        )
    }
}
```

### Text Alternatives for Complex Content

```kotlin
@Composable
fun ChartWithAccessibility(data: List<DataPoint>) {
    // Visual chart
    Canvas(
        modifier = Modifier
            .fillMaxWidth()
            .height(200.dp)
            .semantics {
                // ✅ Provide text alternative for screen readers
                contentDescription = buildString {
                    append("Sales chart showing ")
                    append("${data.size} data points. ")
                    append("Highest value: ${data.maxOf { it.value }} ")
                    append("on ${data.maxBy { it.value }.date}. ")
                    append("Lowest value: ${data.minOf { it.value }} ")
                    append("on ${data.minBy { it.value }.date}.")
                }
            }
    ) {
        // Draw chart...
    }
}

@Composable
fun GraphWithAccessibility() {
    Box {
        // Visual graph
        Image(
            painter = painterResource(R.drawable.graph),
            contentDescription = "Sales increased by 25% from January to December, " +
                "with a peak in November at $50,000"
        )

        // Hidden but accessible data table for screen readers
        Column(
            modifier = Modifier.semantics {
                invisibleToUser() // Hidden visually but read by TalkBack
            }
        ) {
            Text("January: $30,000")
            Text("February: $32,000")
            // ... more data
        }
    }
}
```

### Live Regions

**Announce dynamic content updates**:

```kotlin
@Composable
fun LiveSearchResults(
    query: String,
    results: List<SearchResult>,
    isLoading: Boolean
) {
    Column {
        TextField(
            value = query,
            onValueChange = { /* update query */ },
            label = { Text("Search") }
        )

        // ✅ Announce result count changes
        Text(
            text = when {
                isLoading -> "Searching..."
                results.isEmpty() -> "No results found"
                else -> "${results.size} results found"
            },
            modifier = Modifier.semantics {
                liveRegion = LiveRegionMode.Polite
                // Polite: Wait for user to pause
                // Assertive: Interrupt immediately
            }
        )

        LazyColumn {
            items(results) { result ->
                ResultItem(result)
            }
        }
    }
}

@Composable
fun LiveNotification(notification: String?) {
    notification?.let {
        Text(
            text = it,
            modifier = Modifier.semantics {
                liveRegion = LiveRegionMode.Assertive // Announce immediately
            }
        )
    }
}
```

### Form Accessibility

```kotlin
@Composable
fun AccessibleForm() {
    var name by remember { mutableStateOf("") }
    var email by remember { mutableStateOf("") }
    var emailError by remember { mutableStateOf<String?>(null) }
    var agreeToTerms by remember { mutableStateOf(false) }

    Column(modifier = Modifier.padding(16.dp)) {
        // Name field
        OutlinedTextField(
            value = name,
            onValueChange = { name = it },
            label = { Text("Full Name") },
            modifier = Modifier
                .fillMaxWidth()
                .semantics {
                    // ✅ Additional context
                    contentDescription = "Full Name, required field"
                }
        )

        Spacer(modifier = Modifier.height(16.dp))

        // Email field with error
        OutlinedTextField(
            value = email,
            onValueChange = {
                email = it
                emailError = if (it.contains("@")) null else "Invalid email"
            },
            label = { Text("Email") },
            isError = emailError != null,
            modifier = Modifier
                .fillMaxWidth()
                .semantics {
                    if (emailError != null) {
                        // ✅ Announce error
                        error(emailError!!)
                    }
                }
        )

        if (emailError != null) {
            Text(
                text = emailError!!,
                color = MaterialTheme.colorScheme.error,
                style = MaterialTheme.typography.bodySmall,
                modifier = Modifier.semantics {
                    liveRegion = LiveRegionMode.Polite
                }
            )
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Checkbox with clear label
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier
                .fillMaxWidth()
                .toggleable(
                    value = agreeToTerms,
                    onValueChange = { agreeToTerms = it },
                    role = Role.Checkbox
                )
                .semantics(mergeDescendants = true) {
                    // ✅ Merge checkbox and text
                }
        ) {
            Checkbox(
                checked = agreeToTerms,
                onCheckedChange = null // Handled by Row
            )
            Text(
                text = "I agree to the Terms and Conditions",
                modifier = Modifier.padding(start = 8.dp)
            )
        }

        Spacer(modifier = Modifier.height(24.dp))

        Button(
            onClick = { /* Submit */ },
            enabled = name.isNotEmpty() && email.isNotEmpty() &&
                      emailError == null && agreeToTerms,
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Submit")
        }
    }
}
```

### Testing Accessibility

```kotlin
@Test
fun testAccessibility_contentDescription() {
    composeTestRule.setContent {
        Icon(
            imageVector = Icons.Default.Home,
            contentDescription = "Navigate to home"
        )
    }

    // Verify content description
    composeTestRule
        .onNodeWithContentDescription("Navigate to home")
        .assertExists()
}

@Test
fun testAccessibility_mergeSemantics() {
    composeTestRule.setContent {
        Row(
            modifier = Modifier.semantics(mergeDescendants = true) {}
        ) {
            Text("Product: ")
            Text("iPhone")
        }
    }

    // Verify merged semantics
    composeTestRule
        .onNodeWithText("Product: iPhone")
        .assertExists()
}

@Test
fun testAccessibility_customAction() {
    var deleteClicked = false

    composeTestRule.setContent {
        Box(
            modifier = Modifier.semantics {
                customActions = listOf(
                    CustomAccessibilityAction("Delete") {
                        deleteClicked = true
                        true
                    }
                )
            }
        )
    }

    // Perform custom action
    composeTestRule
        .onNode(hasAnyAncestor(isRoot()))
        .performSemanticsAction(SemanticsActions.CustomActions) {
            it[0].action()
        }

    assertTrue(deleteClicked)
}
```

### Best Practices

1. **Always Provide Content Descriptions**
   ```kotlin
   // ✅ GOOD
   Icon(Icons.Default.Search, contentDescription = "Search")

   // ❌ BAD
   Icon(Icons.Default.Search, contentDescription = "Search icon")
   // Don't say "icon" - it's redundant

   // ✅ GOOD - Describe action, not appearance
   Icon(Icons.Default.Delete, contentDescription = "Delete item")

   // ❌ BAD
   Icon(Icons.Default.Delete, contentDescription = "Trash can")
   ```

2. **Use Semantic Roles**
   ```kotlin
   // ✅ GOOD
   Box(
       modifier = Modifier
           .clickable { /* ... */ }
           .semantics { role = Role.Button }
   )

   // Provides proper TalkBack announcement: "Button, [description]"
   ```

3. **Group Related Content**
   ```kotlin
   // ✅ GOOD - Group related elements
   Card(
       modifier = Modifier.semantics(mergeDescendants = true) {
           contentDescription = "Product card: iPhone 15, $999"
       }
   ) {
       // Product details
   }

   // ❌ BAD - Each element announced separately
   Card {
       Text("iPhone 15") // Announces: "iPhone 15"
       Text("$999")      // Announces: "$999"
   }
   ```

4. **Minimum Touch Targets**
   ```kotlin
   // ✅ GOOD - 48dp minimum
   IconButton(
       onClick = { },
       modifier = Modifier.size(48.dp)
   ) {
       Icon(Icons.Default.Delete, "Delete", Modifier.size(24.dp))
   }

   // ❌ BAD - Too small
   Icon(
       Icons.Default.Delete,
       "Delete",
       Modifier.size(24.dp).clickable { }
   )
   ```

5. **Test with TalkBack**
   ```
   ✅ Enable TalkBack and test your app
   ✅ Navigate using swipe gestures
   ✅ Verify all interactive elements are reachable
   ✅ Check that descriptions are clear and concise
   ✅ Test custom actions from TalkBack menu
   ```

### Summary

**Key accessibility features in Compose:**
- ✅ **Content descriptions** - Describe images, icons, buttons
- ✅ **Semantic properties** - Role, state, actions
- ✅ **Merge descendants** - Group related content
- ✅ **Custom actions** - Additional TalkBack menu items
- ✅ **Headings** - Structure content for navigation
- ✅ **Live regions** - Announce dynamic changes
- ✅ **Touch targets** - Minimum 48dp
- ✅ **State descriptions** - Loading, error states

**Testing accessibility:**
- Enable TalkBack and test manually
- Use Compose test APIs to verify semantics
- Check with Accessibility Scanner

**Remember:**
- Accessibility benefits everyone
- Design for accessibility from the start
- Test with real screen readers
- Get feedback from users with disabilities

---

# Вопрос (RU)
Как сделать Jetpack Compose UI доступным? Какие ключевые аспекты для поддержки TalkBack, content descriptions, semantic properties и accessibility actions в Compose?

## Ответ (RU)
[Перевод с примерами из английской версии...]

### Резюме

**Ключевые функции доступности в Compose:**
- ✅ **Content descriptions** — описывают изображения, иконки, кнопки
- ✅ **Semantic properties** — роль, состояние, действия
- ✅ **Merge descendants** — группируют связанный контент
- ✅ **Custom actions** — дополнительные элементы меню TalkBack
- ✅ **Headings** — структурируют контент для навигации
- ✅ **Live regions** — объявляют динамические изменения
- ✅ **Touch targets** — минимум 48dp
- ✅ **State descriptions** — состояния загрузки, ошибок

**Тестирование доступности:**
- Включите TalkBack и тестируйте вручную
- Используйте Compose test API для проверки семантики
- Проверяйте с помощью Accessibility Scanner

**Помните:**
- Доступность полезна всем
- Проектируйте для доступности с самого начала
- Тестируйте с реальными screen readers
- Получайте обратную связь от пользователей с ограниченными возможностями
