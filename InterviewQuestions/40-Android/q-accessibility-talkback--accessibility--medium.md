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

# Вопрос (RU)
Как работает TalkBack в Android? Как оптимизировать View и Compose UI для навигации TalkBack? Что такое focus order, traversal order и accessibility focus?

---

## Answer (EN)

TalkBack is Android's built-in screen reader that provides spoken feedback for users who are blind or have low vision. Understanding TalkBack navigation is crucial for creating accessible apps.

#### Navigation Gestures

```
Swipe right     → Move to next element
Swipe left      → Move to previous element
Swipe up        → Change granularity (characters, words, lines, paragraphs)
Swipe down      → Change granularity
Double-tap      → Activate (click) current element
Two-finger tap  → Pause/resume TalkBack
TalkBack menu   → Swipe down then right (custom actions)
```

#### What TalkBack Announces

1. Element type - Button, text field, checkbox, etc.
2. Content - Text, content description
3. State - Checked, selected, expanded, etc.
4. Position - "Item 1 of 10"
5. Hint - What happens when activated

#### Focus Order

Default focus order: left-to-right, top-to-bottom in LTR layouts; right-to-left, top-to-bottom in RTL layouts.

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

#### Custom Traversal Order

**XML Views - traversalBefore/After**:

```xml
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

#### Focus Management

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
                focusRequester.requestFocus()
            }
        }
    }
}
```

#### Grouping Related Content

**Problem: Too many individual elements**:

```kotlin
// BAD - Each element announced separately
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
// GOOD - Single announcement
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

#### Handling Complex Lists

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
                        contentDescription = buildString {
                            append(item.title)
                            append(", ")
                            append(item.description)
                            append(". Item ${index + 1} of ${items.size}")
                        }

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

#### Hiding Decorative Elements

```kotlin
@Composable
fun DecorativeElementsExample() {
    Row {
        // BAD - Decorative image with description
        Image(
            painter = painterResource(R.drawable.decorative_pattern),
            contentDescription = "Decorative pattern", // Wrong!
            modifier = Modifier.size(100.dp)
        )

        // GOOD - Decorative image without description
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

#### Announcing Changes

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
            }
        )

        LazyColumn {
            items(results) { result ->
                SearchResultItem(result)
            }
        }
    }
}
```

#### Testing with TalkBack

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

    composeTestRule
        .onNodeWithText("Click me")
        .assertHasClickAction()
        .assert(hasContentDescription("Click me"))
}
```

#### Common TalkBack Issues

1. **Missing content descriptions**
   ```kotlin
   // BAD
   Icon(Icons.Default.Delete, contentDescription = "")

   // GOOD
   Icon(Icons.Default.Delete, contentDescription = "Delete item")
   ```

2. **Redundant descriptions**
   ```kotlin
   // BAD
   Button(onClick = {}) {
       Text("Submit", modifier = Modifier.semantics {
           contentDescription = "Submit button" // Redundant!
       })
   }

   // GOOD
   Button(onClick = {}) {
       Text("Submit") // Button role is implicit
   }
   ```

3. **Too many separate elements**
   ```kotlin
   // BAD - 5 separate announcements
   Row {
       Icon(Icons.Default.Star, "Star")
       Icon(Icons.Default.Star, "Star")
       Icon(Icons.Default.Star, "Star")
       Icon(Icons.Default.Star, "Star")
       Icon(Icons.Default.StarHalf, "Half star")
   }

   // GOOD - Single announcement
   Row(modifier = Modifier.semantics(mergeDescendants = true) {
       contentDescription = "4.5 stars"
   }) {
       repeat(4) { Icon(Icons.Default.Star, null) }
       Icon(Icons.Default.StarHalf, null)
   }
   ```

#### Best Practices

1. Test with TalkBack enabled
2. Keep descriptions concise
3. Group related content
4. Announce dynamic changes
5. Provide custom actions
6. Respect focus order
7. Hide decorative elements
8. Test with users

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
