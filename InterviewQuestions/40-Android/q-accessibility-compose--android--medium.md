---
id: 20251012-122749
title: Доступность в Compose / Accessibility in Compose
aliases:
  - Доступность в Compose
  - Compose Accessibility
  - Доступность Compose
  - Accessibility Compose
topic: android
subtopics: [ui-accessibility, ui-compose]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related:
  - c-accessibility
  - c-jetpack-compose
  - q-accessibility-talkback--android--medium
  - q-accessibility-testing--android--medium
  - q-custom-view-accessibility--android--medium
created: 2025-10-11
updated: 2025-10-27
sources:
  - https://developer.android.com/jetpack/compose/accessibility
  - https://developer.android.com/guide/topics/ui/accessibility
tags: [android/ui-accessibility, android/ui-compose, difficulty/medium]
---
# Вопрос (RU)
> Что такое Доступность в Compose?

---

# Question (EN)
> What is Accessibility in Compose?

---

## Ответ (RU)

**Доступность в Compose** гарантирует, что приложение доступно для людей с ограниченными возможностями через TalkBack, семантические свойства, описания контента, достаточный размер сенсорных элементов (минимум 48dp) и контраст цветов.

### Ключевые концепции

**1. Content Descriptions** — описания для изображений и иконок:

```kotlin
// ✅ ПРАВИЛЬНО — описание для важного контента
Image(
    painter = painterResource(R.drawable.profile_photo),
    contentDescription = "User profile photo",
    modifier = Modifier.size(64.dp)
)

// ✅ ПРАВИЛЬНО — null для декоративных элементов
Image(
    painter = painterResource(R.drawable.background_pattern),
    contentDescription = null, // Декоративное изображение
    modifier = Modifier.fillMaxSize()
)
```

**2. Semantic Properties** — семантическая информация для элементов:

```kotlin
@Composable
fun CustomToggle(checked: Boolean, onCheckedChange: (Boolean) -> Unit) {
    Box(
        modifier = Modifier
            .size(48.dp)
            .clickable { onCheckedChange(!checked) }
            .semantics {
                role = Role.Switch
                toggleableState = ToggleableState(checked)
                contentDescription = if (checked) {
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
```

**3. Merge Descendants** — группировка семантической информации:

```kotlin
@Composable
fun ProductCard(product: Product) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { /* View product */ }
            .semantics(mergeDescendants = true) {
                contentDescription = buildString {
                    append("${product.name}, $${product.price}")
                    if (product.rating > 0) append(", ${product.rating} stars")
                    append(if (product.inStock) ", In stock" else ", Out of stock")
                }
            }
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(product.name)
            Text("$${product.price}")
            RatingBar(rating = product.rating)
            Text(
                text = if (product.inStock) "In stock" else "Out of stock",
                color = if (product.inStock) Color.Green else Color.Red
            )
        }
    }
}
```

**4. Touch Target Sizes** — минимальный размер 48dp:

```kotlin
// ✅ ПРАВИЛЬНО — минимум 48dp для кликабельных элементов
IconButton(
    onClick = { /* ... */ },
    modifier = Modifier.size(48.dp) // ✅ Минимальный размер
) {
    Icon(
        imageVector = Icons.Default.Delete,
        contentDescription = "Delete",
        modifier = Modifier.size(24.dp) // Размер иконки
    )
}

// ❌ НЕПРАВИЛЬНО — слишком маленький
Icon(
    imageVector = Icons.Default.Delete,
    contentDescription = "Delete",
    modifier = Modifier
        .size(24.dp) // ❌ Только 24dp!
        .clickable { /* ... */ }
)
```

**5. Custom Accessibility Actions** — дополнительные действия:

```kotlin
@Composable
fun EmailListItem(email: Email, onDelete: () -> Unit, onArchive: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { /* Open email */ }
            .semantics {
                contentDescription = "Email from ${email.sender}: ${email.subject}"
                customActions = listOf(
                    CustomAccessibilityAction("Delete") { onDelete(); true },
                    CustomAccessibilityAction("Archive") { onArchive(); true }
                )
            }
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(email.sender, style = MaterialTheme.typography.titleMedium)
            Text(email.subject, style = MaterialTheme.typography.bodyMedium)
        }
    }
}
```

**6. Live Regions** — объявления динамических изменений:

```kotlin
@Composable
fun LiveSearchResults(query: String, results: List<SearchResult>, isLoading: Boolean) {
    Column {
        TextField(value = query, onValueChange = { }, label = { Text("Search") })

        Text(
            text = when {
                isLoading -> "Searching..."
                results.isEmpty() -> "No results found"
                else -> "${results.size} results found"
            },
            modifier = Modifier.semantics {
                liveRegion = LiveRegionMode.Polite // ✅ Объявление изменений
            }
        )

        LazyColumn {
            items(results) { result -> ResultItem(result) }
        }
    }
}
```

### Best Practices

1. ✅ Всегда указывайте contentDescription для информативных элементов
2. ✅ Используйте null для декоративных элементов
3. ✅ Группируйте семантику через mergeDescendants
4. ✅ Минимальный размер сенсорных элементов — 48dp
5. ✅ Тестируйте с включённым TalkBack

---

## Answer (EN)

**Accessibility in Compose** ensures your app is usable by people with disabilities through TalkBack support, semantic properties, content descriptions, minimum 48dp touch targets, and color contrast.

### Key Concepts

**1. Content Descriptions** — descriptions for images and icons:

```kotlin
// ✅ CORRECT — description for meaningful content
Image(
    painter = painterResource(R.drawable.profile_photo),
    contentDescription = "User profile photo",
    modifier = Modifier.size(64.dp)
)

// ✅ CORRECT — null for decorative images
Image(
    painter = painterResource(R.drawable.background_pattern),
    contentDescription = null, // Decorative, no semantic meaning
    modifier = Modifier.fillMaxSize()
)
```

**2. Semantic Properties** — semantic information for elements:

```kotlin
@Composable
fun CustomToggle(checked: Boolean, onCheckedChange: (Boolean) -> Unit) {
    Box(
        modifier = Modifier
            .size(48.dp)
            .clickable { onCheckedChange(!checked) }
            .semantics {
                role = Role.Switch
                toggleableState = ToggleableState(checked)
                contentDescription = if (checked) {
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
```

**3. Merge Descendants** — group semantic information:

```kotlin
@Composable
fun ProductCard(product: Product) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { /* View product */ }
            .semantics(mergeDescendants = true) {
                contentDescription = buildString {
                    append("${product.name}, $${product.price}")
                    if (product.rating > 0) append(", ${product.rating} stars")
                    append(if (product.inStock) ", In stock" else ", Out of stock")
                }
            }
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(product.name)
            Text("$${product.price}")
            RatingBar(rating = product.rating)
            Text(
                text = if (product.inStock) "In stock" else "Out of stock",
                color = if (product.inStock) Color.Green else Color.Red
            )
        }
    }
}
```

**4. Touch Target Sizes** — minimum 48dp:

```kotlin
// ✅ CORRECT — minimum 48dp for interactive elements
IconButton(
    onClick = { /* ... */ },
    modifier = Modifier.size(48.dp) // ✅ Minimum size
) {
    Icon(
        imageVector = Icons.Default.Delete,
        contentDescription = "Delete",
        modifier = Modifier.size(24.dp) // Icon size
    )
}

// ❌ WRONG — too small
Icon(
    imageVector = Icons.Default.Delete,
    contentDescription = "Delete",
    modifier = Modifier
        .size(24.dp) // ❌ Only 24dp!
        .clickable { /* ... */ }
)
```

**5. Custom Accessibility Actions** — additional actions:

```kotlin
@Composable
fun EmailListItem(email: Email, onDelete: () -> Unit, onArchive: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { /* Open email */ }
            .semantics {
                contentDescription = "Email from ${email.sender}: ${email.subject}"
                customActions = listOf(
                    CustomAccessibilityAction("Delete") { onDelete(); true },
                    CustomAccessibilityAction("Archive") { onArchive(); true }
                )
            }
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(email.sender, style = MaterialTheme.typography.titleMedium)
            Text(email.subject, style = MaterialTheme.typography.bodyMedium)
        }
    }
}
```

**6. Live Regions** — announce dynamic content:

```kotlin
@Composable
fun LiveSearchResults(query: String, results: List<SearchResult>, isLoading: Boolean) {
    Column {
        TextField(value = query, onValueChange = { }, label = { Text("Search") })

        Text(
            text = when {
                isLoading -> "Searching..."
                results.isEmpty() -> "No results found"
                else -> "${results.size} results found"
            },
            modifier = Modifier.semantics {
                liveRegion = LiveRegionMode.Polite // ✅ Announce changes
            }
        )

        LazyColumn {
            items(results) { result -> ResultItem(result) }
        }
    }
}
```

### Best Practices

1. ✅ Always provide contentDescription for meaningful elements
2. ✅ Use null for decorative elements
3. ✅ Group semantics with mergeDescendants
4. ✅ Minimum touch target size is 48dp
5. ✅ Test with TalkBack enabled

---

## Follow-ups

- Что происходит, если не указать contentDescription для изображений?
- Как автоматизированно тестировать доступность?
- В чём разница между mergeDescendants и clearAndSetSemantics?
- Как обработать динамические обновления для screen readers?

## Related Questions

### Prerequisites (Easier)
- [[c-accessibility]] — Accessibility concepts
- [[c-jetpack-compose]] — Jetpack Compose basics

### Related (Same Level)
- [[q-accessibility-talkback--android--medium]] — TalkBack testing
- [[q-accessibility-testing--android--medium]] — Accessibility testing
- [[q-custom-view-accessibility--android--medium]] — Custom view accessibility

### Advanced (Harder)
- [[q-compose-stability-skippability--android--hard]] — Compose stability
- [[q-stable-classes-compose--android--hard]] — @Stable annotation