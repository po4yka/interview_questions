---
id: 20251012-122749
title: Accessibility Compose / Доступность в Compose
aliases:
- Compose Accessibility
- Доступность Compose
topic: android
subtopics:
- ui-accessibility
- ui-compose
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-accessibility-talkback--android--medium
- q-accessibility-testing--android--medium
- q-custom-view-accessibility--android--medium
created: 2025-10-11
updated: 2025-10-15
tags:
- android/ui-accessibility
- android/ui-compose
- difficulty/medium
---

# Вопрос (RU)
> Что такое Доступность в Compose?

---

# Question (EN)
> What is Accessibility Compose?

## Answer (EN)
[[c-accessibility|Accessibility]] in [[c-jetpack-compose|Jetpack Compose]] ensures your app is usable by people with disabilities. Key aspects: screen reader support (TalkBack), content descriptions, semantic properties, touch target sizes (minimum 48dp), sufficient color contrast, and custom accessibility actions.

#### Content Descriptions

```kotlin
@Composable
fun AccessibleImage() {
    Image(
        painter = painterResource(R.drawable.profile_photo),
        contentDescription = "User profile photo", // GOOD
        modifier = Modifier.size(64.dp)
    )

    // BAD - Decorative images should use null
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
        contentDescription = "Add to favorites", // Action description
        modifier = Modifier.clickable { /* ... */ }
    )
}
```

#### Semantic Properties

Use `Modifier.semantics` to add semantic information:

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
```

#### Accessibility Actions

Custom actions for complex interactions:

```kotlin
@Composable
fun EmailListItem(
    email: Email,
    onDelete: () -> Unit,
    onArchive: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { /* Open email */ }
            .semantics {
                this.contentDescription = "Email from ${email.sender}: ${email.subject}"

                customActions = listOf(
                    CustomAccessibilityAction(
                        label = "Delete",
                        action = { onDelete(); true }
                    ),
                    CustomAccessibilityAction(
                        label = "Archive",
                        action = { onArchive(); true }
                    )
                )
            }
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(text = email.sender, style = MaterialTheme.typography.titleMedium)
            Text(text = email.subject, style = MaterialTheme.typography.bodyMedium)
        }
    }
}
```

#### Merge Descendants

Simplify complex UI for screen readers:

```kotlin
@Composable
fun ProductCard(product: Product) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { /* View product */ }
            .semantics(mergeDescendants = true) {
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
```

#### Touch Target Sizes

Minimum 48dp for interactive elements:

```kotlin
@Composable
fun AccessibleIconButton() {
    // GOOD - Minimum 48dp touch target
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

    // BAD - Too small
    Icon(
        imageVector = Icons.Default.Delete,
        contentDescription = "Delete",
        modifier = Modifier
            .size(24.dp) // Only 24dp touch target!
            .clickable { /* ... */ }
    )
}
```

#### Heading Semantics

Structure content with headings:

```kotlin
@Composable
fun AccessibleScreen() {
    Column {
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
    }
}
```

#### Live Regions

Announce dynamic content updates:

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

        Text(
            text = when {
                isLoading -> "Searching..."
                results.isEmpty() -> "No results found"
                else -> "${results.size} results found"
            },
            modifier = Modifier.semantics {
                liveRegion = LiveRegionMode.Polite
            }
        )

        LazyColumn {
            items(results) { result ->
                ResultItem(result)
            }
        }
    }
}
```

#### Testing

```kotlin
@Test
fun testAccessibility_contentDescription() {
    composeTestRule.setContent {
        Icon(
            imageVector = Icons.Default.Home,
            contentDescription = "Navigate to home"
        )
    }

    composeTestRule
        .onNodeWithContentDescription("Navigate to home")
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

    composeTestRule
        .onNode(hasAnyAncestor(isRoot()))
        .performSemanticsAction(SemanticsActions.CustomActions) {
            it[0].action()
        }

    assertTrue(deleteClicked)
}
```

#### Best Practices

1. Always provide content descriptions
2. Use semantic roles
3. Group related content with mergeDescendants
4. Ensure minimum 48dp touch targets
5. Test with TalkBack enabled

---

## Follow-ups

- What happens if you don't provide content descriptions for images?
- How do you test accessibility with automated tests?
- What's the difference between mergeDescendants and clearAndSetSemantics?
- How do you handle dynamic content updates for screen readers?
- What are the minimum requirements for touch targets?

## References

- [Android Accessibility Guidelines](https://developer.android.com/guide/topics/ui/accessibility)
- [Compose Accessibility Documentation](https://developer.android.com/jetpack/compose/accessibility)
- [TalkBack User Guide](https://support.google.com/accessibility/android/answer/6283677)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

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