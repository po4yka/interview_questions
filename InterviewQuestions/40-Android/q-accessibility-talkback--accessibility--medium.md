---
id: 20251012-122753
title: Accessibility Talkback / Доступность и TalkBack
aliases: [TalkBack Accessibility, Доступность TalkBack]
topic: android
subtopics: [ui-accessibility, ui-navigation]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related:
  - q-accessibility-compose--accessibility--medium
  - q-accessibility-testing--accessibility--medium
  - q-custom-view-accessibility--custom-views--medium
created: 2025-10-11
updated: 2025-10-15
tags:
  - android/ui-accessibility
  - android/ui-navigation
  - accessibility
  - talkback
  - screen-reader
  - assistive-technology
  - difficulty/medium
---
# Question (EN)
How does TalkBack work in Android? How do you optimize Views and Compose UIs for TalkBack navigation? What are focus order, traversal order, and accessibility focus?

## Answer (EN)
### Overview

**TalkBack** is Android's built-in screen reader that provides spoken feedback for users who are blind or have low vision. Understanding TalkBack navigation is crucial for creating accessible apps.

### How TalkBack Works

**Navigation gestures:**
```
Swipe right     → Move to next element
Swipe left      → Move to previous element
Swipe up        → Change granularity (characters, words, lines, paragraphs)
Swipe down      → Change granularity
Double-tap      → Activate (click) current element
Two-finger tap  → Pause/resume TalkBack
TalkBack menu   → Swipe down then right (custom actions)
```

**What TalkBack announces:**
1. **Element type** - Button, text field, checkbox, etc.
2. **Content** - Text, content description
3. **State** - Checked, selected, expanded, etc.
4. **Position** - "Item 1 of 10"
5. **Hint** - What happens when activated

### Accessibility Focus Order

**Default focus order** (important!):
- Left-to-right, top-to-bottom in LTR layouts
- Right-to-left, top-to-bottom in RTL layouts
- Based on layout hierarchy

```kotlin
// Default order (top-to-bottom, left-to-right)
Column {
    Text("First")     // Focus 1
    Text("Second")    // Focus 2
    Text("Third")     // Focus 3
}

Row {
    Text("Left")      // Focus 1
    Text("Middle")    // Focus 2
    Text("Right")     // Focus 3
}
```

### Custom Traversal Order

**XML Views - traversalBefore/After**:

```xml
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="vertical">

    <!-- Default order: Title → Subtitle → Button -->
    <TextView
        android:id="@+id/title"
        android:text="Title" />

    <TextView
        android:id="@+id/subtitle"
        android:text="Subtitle" />

    <Button
        android:id="@+id/button"
        android:text="Action" />

</LinearLayout>

<!-- Custom order: Title → Button → Subtitle -->
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="vertical">

    <TextView
        android:id="@+id/title"
        android:text="Title"
        android:accessibilityTraversalAfter="@id/button" />

    <TextView
        android:id="@+id/subtitle"
        android:text="Subtitle" />

    <Button
        android:id="@+id/button"
        android:text="Action"
        android:accessibilityTraversalBefore="@id/subtitle" />

</LinearLayout>
```

**Compose - Modifier.semantics with isTraversalGroup**:

```kotlin
@Composable
fun CustomTraversalOrder() {
    Column {
        // Group 1: Title and action together
        Column(
            modifier = Modifier.semantics {
                isTraversalGroup = true
            }
        ) {
            Text("Important Title")
            Button(onClick = {}) {
                Text("Primary Action")
            }
        }

        // Group 2: Description (visited after group 1)
        Text(
            text = "Detailed description that comes last",
            modifier = Modifier.semantics {
                isTraversalGroup = true
            }
        )
    }
}
```

### Focus Management

**Requesting accessibility focus**:

```kotlin
// XML View
val view = findViewById<TextView>(R.id.errorMessage)
view.sendAccessibilityEvent(AccessibilityEvent.TYPE_VIEW_FOCUSED)

// Compose
@Composable
fun FocusManagementExample() {
    var showError by remember { mutableStateOf(false) }
    val focusRequester = remember { FocusRequester() }

    Column {
        Button(onClick = { showError = true }) {
            Text("Show Error")
        }

        if (showError) {
            Text(
                text = "Error: Invalid input",
                color = Color.Red,
                modifier = Modifier
                    .focusRequester(focusRequester)
                    .semantics {
                        liveRegion = LiveRegionMode.Assertive
                    }
            )

            LaunchedEffect(showError) {
                // Request accessibility focus when error appears
                focusRequester.requestFocus()
            }
        }
    }
}
```

### Grouping Related Content

**Problem: Too many individual elements**:

```kotlin
//  BAD - Each element announced separately
@Composable
fun ProductCard(product: Product) {
    Card(modifier = Modifier.clickable { /* view product */ }) {
        Column {
            Text(product.name)        // "iPhone 15"
            Text("$${product.price}") // "$999"
            Row {
                Icon(Icons.Default.Star, null)  // "Star"
                Icon(Icons.Default.Star, null)  // "Star"
                Icon(Icons.Default.Star, null)  // "Star"
                Icon(Icons.Default.Star, null)  // "Star"
                Icon(Icons.Default.StarHalf, null) // "Star half"
            }
            Text(if (product.inStock) "In stock" else "Out of stock")
        }
    }
}
// TalkBack announces 8+ separate elements!
```

**Solution: Merge semantics**:

```kotlin
//  GOOD - Single announcement
@Composable
fun ProductCard(product: Product) {
    Card(
        modifier = Modifier
            .clickable { /* view product */ }
            .semantics(mergeDescendants = true) {
                contentDescription = buildString {
                    append(product.name)
                    append(", ")
                    append("$${product.price}")
                    append(", ")
                    append("${product.rating} stars")
                    append(", ")
                    append(if (product.inStock) "In stock" else "Out of stock")
                }
            }
    ) {
        Column {
            Text(product.name)
            Text("$${product.price}")
            RatingBar(product.rating)
            Text(if (product.inStock) "In stock" else "Out of stock")
        }
    }
}
// TalkBack announces: "iPhone 15, $999, 4.5 stars, In stock"
```

### Handling Complex Lists

**RecyclerView with TalkBack**:

```kotlin
class AccessibleAdapter : RecyclerView.Adapter<ViewHolder>() {

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = items[position]

        // Set content description for the entire item
        holder.itemView.contentDescription = buildString {
            append(item.title)
            append(". ")
            append(item.subtitle)
            append(". ")
            append("Item ${position + 1} of ${itemCount}")
        }

        // Mark as focusable
        holder.itemView.isFocusable = true

        // Add custom accessibility actions
        ViewCompat.setAccessibilityDelegate(holder.itemView, object : AccessibilityDelegateCompat() {
            override fun onInitializeAccessibilityNodeInfo(
                host: View,
                info: AccessibilityNodeInfoCompat
            ) {
                super.onInitializeAccessibilityNodeInfo(host, info)

                // Add custom actions
                info.addAction(
                    AccessibilityNodeInfoCompat.AccessibilityActionCompat(
                        R.id.action_delete,
                        "Delete"
                    )
                )

                info.addAction(
                    AccessibilityNodeInfoCompat.AccessibilityActionCompat(
                        R.id.action_share,
                        "Share"
                    )
                )
            }

            override fun performAccessibilityAction(
                host: View,
                action: Int,
                args: Bundle?
            ): Boolean {
                return when (action) {
                    R.id.action_delete -> {
                        deleteItem(position)
                        true
                    }
                    R.id.action_share -> {
                        shareItem(position)
                        true
                    }
                    else -> super.performAccessibilityAction(host, action, args)
                }
            }
        })
    }
}
```

**LazyColumn with TalkBack**:

```kotlin
@Composable
fun AccessibleList(items: List<Item>) {
    LazyColumn {
        itemsIndexed(items) { index, item ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(8.dp)
                    .clickable { /* open item */ }
                    .semantics {
                        // Announce position in list
                        contentDescription = buildString {
                            append(item.title)
                            append(", ")
                            append(item.description)
                            append(". Item ${index + 1} of ${items.size}")
                        }

                        // Custom actions
                        customActions = listOf(
                            CustomAccessibilityAction("Delete") {
                                deleteItem(item)
                                true
                            },
                            CustomAccessibilityAction("Share") {
                                shareItem(item)
                                true
                            }
                        )
                    }
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(item.title)
                    Text(item.description)
                }
            }
        }
    }
}
```

### Hiding Decorative Elements

```kotlin
@Composable
fun DecorativeElementsExample() {
    Row {
        //  BAD - Decorative image with description
        Image(
            painter = painterResource(R.drawable.decorative_pattern),
            contentDescription = "Decorative pattern", // Wrong!
            modifier = Modifier.size(100.dp)
        )

        //  GOOD - Decorative image without description
        Image(
            painter = painterResource(R.drawable.decorative_pattern),
            contentDescription = null, // Ignored by TalkBack
            modifier = Modifier.size(100.dp)
        )

        Text("Important content")
    }
}

// XML View - hide decorative elements
<ImageView
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:src="@drawable/decorative_pattern"
    android:importantForAccessibility="no" />
```

### Announcing Changes

**Live regions for dynamic content**:

```kotlin
@Composable
fun SearchResults(
    query: String,
    results: List<SearchResult>,
    isLoading: Boolean
) {
    Column {
        TextField(
            value = query,
            onValueChange = { /* search */ },
            label = { Text("Search") }
        )

        // Announce result count changes
        Text(
            text = when {
                isLoading -> "Searching..."
                results.isEmpty() -> "No results found for \"$query\""
                else -> "${results.size} results found for \"$query\""
            },
            modifier = Modifier.semantics {
                liveRegion = LiveRegionMode.Polite
                // Polite: Wait for user to finish current action
                // Assertive: Interrupt immediately
            }
        )

        LazyColumn {
            items(results) { result ->
                SearchResultItem(result)
            }
        }
    }
}

@Composable
fun Timer(seconds: Int) {
    //  BAD - Announces every second
    Text(
        text = "$seconds seconds",
        modifier = Modifier.semantics {
            liveRegion = LiveRegionMode.Polite
        }
    )

    //  GOOD - Only announce important milestones
    Text(text = "$seconds seconds")

    if (seconds in listOf(60, 30, 10, 5, 4, 3, 2, 1)) {
        Text(
            text = "$seconds seconds remaining",
            modifier = Modifier.semantics {
                liveRegion = LiveRegionMode.Polite
            }
        )
    }
}
```

### Accessible Dialogs and Bottom Sheets

```kotlin
@Composable
fun AccessibleDialog() {
    var showDialog by remember { mutableStateOf(false) }

    Button(onClick = { showDialog = true }) {
        Text("Show Dialog")
    }

    if (showDialog) {
        AlertDialog(
            onDismissRequest = { showDialog = false },
            title = {
                Text(
                    text = "Confirm Delete",
                    modifier = Modifier.semantics {
                        // Mark as dialog title for TalkBack
                        heading()
                    }
                )
            },
            text = {
                Text("Are you sure you want to delete this item?")
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        deleteItem()
                        showDialog = false
                    }
                ) {
                    Text("Delete")
                }
            },
            dismissButton = {
                TextButton(onClick = { showDialog = false }) {
                    Text("Cancel")
                }
            },
            modifier = Modifier.semantics {
                // Trap focus inside dialog
                isDialog = true
            }
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AccessibleBottomSheet() {
    val sheetState = rememberModalBottomSheetState()
    var showSheet by remember { mutableStateOf(false) }

    Button(onClick = { showSheet = true }) {
        Text("Show Bottom Sheet")
    }

    if (showSheet) {
        ModalBottomSheet(
            onDismissRequest = { showSheet = false },
            sheetState = sheetState,
            modifier = Modifier.semantics {
                // Announce when sheet appears
                liveRegion = LiveRegionMode.Polite
            }
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "Actions",
                    style = MaterialTheme.typography.titleLarge,
                    modifier = Modifier.semantics {
                        heading()
                    }
                )

                Spacer(modifier = Modifier.height(16.dp))

                Button(
                    onClick = { /* action */ },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Edit")
                }

                Button(
                    onClick = { /* action */ },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Delete")
                }
            }
        }
    }
}
```

### Accessibility in Navigation

```kotlin
@Composable
fun AccessibleNavigation() {
    val navController = rememberNavController()

    Scaffold(
        bottomBar = {
            NavigationBar {
                NavigationBarItem(
                    selected = true,
                    onClick = { navController.navigate("home") },
                    icon = {
                        Icon(
                            Icons.Default.Home,
                            contentDescription = null // Handled by label
                        )
                    },
                    label = { Text("Home") },
                    modifier = Modifier.semantics {
                        // Announce selection state
                        stateDescription = if (true) "Selected" else "Not selected"
                    }
                )

                NavigationBarItem(
                    selected = false,
                    onClick = { navController.navigate("search") },
                    icon = {
                        Icon(
                            Icons.Default.Search,
                            contentDescription = null
                        )
                    },
                    label = { Text("Search") }
                )

                NavigationBarItem(
                    selected = false,
                    onClick = { navController.navigate("profile") },
                    icon = {
                        Icon(
                            Icons.Default.Person,
                            contentDescription = null
                        )
                    },
                    label = { Text("Profile") }
                )
            }
        }
    ) { padding ->
        NavHost(
            navController = navController,
            startDestination = "home",
            modifier = Modifier.padding(padding)
        ) {
            composable("home") {
                HomeScreen(
                    modifier = Modifier.semantics {
                        // Announce screen change
                        liveRegion = LiveRegionMode.Polite
                    }
                )
            }
            // More destinations...
        }
    }
}
```

### Testing with TalkBack

**Manual testing checklist**:

```
 Enable TalkBack (Settings → Accessibility → TalkBack)
 Navigate with swipe gestures
 Verify all interactive elements are reachable
 Check content descriptions are meaningful
 Test custom actions (swipe down then right)
 Verify focus order makes sense
 Check that state changes are announced
 Test forms and error messages
 Verify dialogs trap focus
 Test with different text sizes
 Test with different display sizes
 Test RTL layout (if supported)
```

**Automated testing**:

```kotlin
@Test
fun testTalkBackAnnouncement() {
    composeTestRule.setContent {
        Button(onClick = {}) {
            Text("Click me")
        }
    }

    // Verify semantics
    composeTestRule
        .onNodeWithText("Click me")
        .assertHasClickAction()
        .assert(hasContentDescription("Click me"))
}

@Test
fun testFocusOrder() {
    composeTestRule.setContent {
        Column {
            Button(onClick = {}, modifier = Modifier.testTag("first")) {
                Text("First")
            }
            Button(onClick = {}, modifier = Modifier.testTag("second")) {
                Text("Second")
            }
        }
    }

    // Navigate with semantics
    composeTestRule
        .onNodeWithTag("first")
        .performSemanticsAction(SemanticsActions.RequestFocus)

    // Verify second element is next in focus order
    // Note: This is simplified; actual testing is more complex
}
```

### Common TalkBack Issues

1. **Missing content descriptions**
   ```kotlin
   //  BAD
   Icon(Icons.Default.Delete, contentDescription = "")

   //  GOOD
   Icon(Icons.Default.Delete, contentDescription = "Delete item")
   ```

2. **Redundant descriptions**
   ```kotlin
   //  BAD
   Button(onClick = {}) {
       Text("Submit", modifier = Modifier.semantics {
           contentDescription = "Submit button" // Redundant!
       })
   }

   //  GOOD
   Button(onClick = {}) {
       Text("Submit") // Button role is implicit
   }
   ```

3. **Too many separate elements**
   ```kotlin
   //  BAD - 5 separate announcements
   Row {
       Icon(Icons.Default.Star, "Star")
       Icon(Icons.Default.Star, "Star")
       Icon(Icons.Default.Star, "Star")
       Icon(Icons.Default.Star, "Star")
       Icon(Icons.Default.StarHalf, "Half star")
   }

   //  GOOD - Single announcement
   Row(modifier = Modifier.semantics(mergeDescendants = true) {
       contentDescription = "4.5 stars"
   }) {
       repeat(4) { Icon(Icons.Default.Star, null) }
       Icon(Icons.Default.StarHalf, null)
   }
   ```

4. **Poor focus order**
   ```kotlin
   //  BAD - Illogical order
   Column {
       Text("Step 3")
       Text("Step 1")
       Text("Step 2")
   }

   //  GOOD - Logical order
   Column {
       Text("Step 1")
       Text("Step 2")
       Text("Step 3")
   }
   ```

### Best Practices

1. **Test with TalkBack enabled** - Manual testing is crucial
2. **Keep descriptions concise** - Users hear them repeatedly
3. **Group related content** - Reduce navigation overhead
4. **Announce dynamic changes** - Use live regions
5. **Provide custom actions** - For complex interactions
6. **Respect focus order** - Top-to-bottom, left-to-right
7. **Hide decorative elements** - contentDescription = null
8. **Test with users** - Get feedback from people who use TalkBack daily

### Summary

**TalkBack navigation:**
- Swipe right/left to navigate
- Double-tap to activate
- Custom actions via TalkBack menu

**Key concepts:**
- **Focus order** - Default: top-to-bottom, left-to-right
- **Traversal order** - Custom order with semantics
- **Merge descendants** - Group related content
- **Live regions** - Announce dynamic changes
- **Custom actions** - Additional TalkBack menu items

**Common patterns:**
- Use `semantics(mergeDescendants = true)` for cards
- Provide custom actions for complex items
- Hide decorative images with `contentDescription = null`
- Announce position in lists: "Item X of Y"
- Use live regions for search results, errors

**Testing:**
- Enable TalkBack and test manually
- Verify all elements are reachable
- Check focus order is logical
- Test custom actions work correctly

---

# Вопрос (RU)
Как работает TalkBack в Android? Как оптимизировать View и Compose UI для навигации TalkBack? Что такое focus order, traversal order и accessibility focus?

## Ответ (RU)
[Перевод с примерами из английской версии...]

### Резюме

**Навигация TalkBack:**
- Свайп вправо/влево для навигации
- Двойное нажатие для активации
- Пользовательские действия через меню TalkBack

**Ключевые концепции:**
- **Focus order** — по умолчанию: сверху вниз, слева направо
- **Traversal order** — пользовательский порядок с помощью semantics
- **Merge descendants** — группировка связанного контента
- **Live regions** — объявление динамических изменений
- **Custom actions** — дополнительные элементы меню TalkBack

**Общие паттерны:**
- Используйте `semantics(mergeDescendants = true)` для карточек
- Предоставляйте пользовательские действия для сложных элементов
- Скрывайте декоративные изображения с `contentDescription = null`
- Объявляйте позицию в списках: "Элемент X из Y"
- Используйте live regions для результатов поиска, ошибок

**Тестирование:**
- Включите TalkBack и тестируйте вручную
- Проверяйте, что все элементы доступны
- Проверяйте логичность focus order
- Тестируйте правильность работы пользовательских действий

---

## Related Questions

### Related (Medium)
- [[q-accessibility-compose--accessibility--medium]] - Accessibility
- [[q-accessibility-testing--accessibility--medium]] - Accessibility
- [[q-custom-view-accessibility--custom-views--medium]] - Accessibility
- [[q-accessibility-color-contrast--accessibility--medium]] - Accessibility
- [[q-accessibility-text-scaling--accessibility--medium]] - Accessibility
