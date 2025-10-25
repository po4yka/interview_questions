---
id: 20251012-122753
title: Accessibility Talkback / Доступность и TalkBack
aliases: [TalkBack Accessibility, Доступность TalkBack]
topic: android
subtopics:
  - ui-accessibility
  - ui-navigation
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - q-accessibility-compose--android--medium
  - q-accessibility-testing--android--medium
  - q-custom-view-accessibility--android--medium
created: 2025-10-11
updated: 2025-10-15
tags: [android/ui-accessibility, android/ui-navigation, difficulty/medium]
date created: Saturday, October 25th 2025, 1:26:31 pm
date modified: Saturday, October 25th 2025, 4:53:22 pm
---

# Question (EN)
> How do you implement TalkBack support in Android apps?

# Вопрос (RU)
> Как реализовать поддержку TalkBack в Android-приложениях?

---

## Answer (EN)

TalkBack is Android's built-in screen reader that helps blind and visually impaired users interact with apps through spoken feedback. Implementing TalkBack support requires providing proper content descriptions, managing focus order, and ensuring all interactive elements are accessible.

**Key Implementation Areas:**

**1. Content Descriptions**

Provide meaningful descriptions for UI elements:

```kotlin
// View-based
ImageView(context).apply {
    contentDescription = "Profile picture"
}

Button(context).apply {
    contentDescription = "Submit form"
}

// Jetpack Compose
Image(
    painter = painterResource(R.drawable.profile),
    contentDescription = "Profile picture"
)

Button(onClick = { }) {
    Text("Submit")
    // Button text is automatically read, but you can add more context
}

Icon(
    imageVector = Icons.Default.Delete,
    contentDescription = "Delete item"
)
```

**2. Focus Order Management**

Control TalkBack navigation order:

```kotlin
// View-based
view.accessibilityTraversalBefore = R.id.next_view
view.accessibilityTraversalAfter = R.id.previous_view

// Compose
Column(
    modifier = Modifier
        .semantics {
            // Custom traversal order
            traversalIndex = 1f
        }
) {
    // Content
}
```

**3. Custom Actions**

Add accessibility actions for complex interactions:

```kotlin
// View-based
ViewCompat.addAccessibilityAction(
    view,
    "Mark as favorite"
) { _, _ ->
    markAsFavorite()
    true
}

// Compose
Box(
    modifier = Modifier.semantics {
        customActions = listOf(
            CustomAccessibilityAction("Mark as favorite") {
                markAsFavorite()
                true
            }
        )
    }
)
```

**4. Live Regions**

Announce dynamic content changes:

```kotlin
// View-based
textView.apply {
    ViewCompat.setAccessibilityLiveRegion(
        this,
        ViewCompat.ACCESSIBILITY_LIVE_REGION_POLITE
    )
}

// Compose
var message by remember { mutableStateOf("") }

Text(
    text = message,
    modifier = Modifier.semantics {
        liveRegion = LiveRegionMode.Polite
    }
)
```

**5. Semantic Properties**

Merge or clear semantics for better experience:

```kotlin
// Compose - Merge child semantics
Row(
    modifier = Modifier.semantics(mergeDescendants = true) {}
) {
    Icon(Icons.Default.Star, contentDescription = null)
    Text("Favorite")
    // TalkBack reads: "Favorite, button"
}

// Clear semantics for decorative elements
Divider(
    modifier = Modifier.semantics {
        invisibleToUser()
    }
)
```

**6. State Descriptions**

Provide state information:

```kotlin
// View-based
checkbox.apply {
    stateDescription = if (isChecked) "Selected" else "Not selected"
}

// Compose
Checkbox(
    checked = isChecked,
    onCheckedChange = { },
    modifier = Modifier.semantics {
        stateDescription = if (isChecked) "Selected" else "Not selected"
    }
)
```

**Best Practices:**

- **Meaningful descriptions**: Describe purpose, not implementation details
- **Avoid redundancy**: Don't repeat information already provided by the element type
- **Test with TalkBack**: Enable TalkBack on a real device and navigate through your app
- **Handle edge cases**: Empty states, loading states, error states
- **Use semantic grouping**: Combine related elements into single focus targets
- **Provide alternatives**: Ensure all functionality is accessible through TalkBack

**Common Pitfalls:**

```kotlin
// BAD - Generic descriptions
Image(
    painter = painterResource(R.drawable.icon),
    contentDescription = "Image" // Too generic
)

// GOOD - Specific descriptions
Image(
    painter = painterResource(R.drawable.user_avatar),
    contentDescription = "John Doe's profile picture"
)

// BAD - Redundant information
Button(
    onClick = { },
    modifier = Modifier.semantics {
        contentDescription = "Submit button" // "button" is redundant
    }
) { Text("Submit") }

// GOOD - Clear and concise
Button(onClick = { }) {
    Text("Submit")
    // Automatically announces "Submit, button"
}
```

## Ответ (RU)

TalkBack - это встроенная программа чтения с экрана Android, которая помогает незрячим и слабовидящим пользователям взаимодействовать с приложениями через голосовую обратную связь. Реализация поддержки TalkBack требует предоставления правильных описаний контента, управления порядком фокуса и обеспечения доступности всех интерактивных элементов.

**Ключевые области реализации:**

**1. Описания контента**

Предоставьте осмысленные описания для элементов UI:

```kotlin
// На основе View
ImageView(context).apply {
    contentDescription = "Фото профиля"
}

Button(context).apply {
    contentDescription = "Отправить форму"
}

// Jetpack Compose
Image(
    painter = painterResource(R.drawable.profile),
    contentDescription = "Фото профиля"
)

Icon(
    imageVector = Icons.Default.Delete,
    contentDescription = "Удалить элемент"
)
```

**2. Управление порядком фокуса**

Контролируйте порядок навигации TalkBack:

```kotlin
// На основе View
view.accessibilityTraversalBefore = R.id.next_view
view.accessibilityTraversalAfter = R.id.previous_view

// Compose
Column(
    modifier = Modifier
        .semantics {
            traversalIndex = 1f
        }
) {
    // Контент
}
```

**3. Пользовательские действия**

Добавьте действия доступности для сложных взаимодействий:

```kotlin
// Compose
Box(
    modifier = Modifier.semantics {
        customActions = listOf(
            CustomAccessibilityAction("Добавить в избранное") {
                markAsFavorite()
                true
            }
        )
    }
)
```

**4. Живые регионы**

Объявляйте изменения динамического контента:

```kotlin
// Compose
var message by remember { mutableStateOf("") }

Text(
    text = message,
    modifier = Modifier.semantics {
        liveRegion = LiveRegionMode.Polite
    }
)
```

**5. Семантические свойства**

Объединяйте или очищайте семантику для лучшего опыта:

```kotlin
// Объединение дочерней семантики
Row(
    modifier = Modifier.semantics(mergeDescendants = true) {}
) {
    Icon(Icons.Default.Star, contentDescription = null)
    Text("Избранное")
    // TalkBack читает: "Избранное, кнопка"
}

// Очистка семантики для декоративных элементов
Divider(
    modifier = Modifier.semantics {
        invisibleToUser()
    }
)
```

**Лучшие практики:**

- **Осмысленные описания**: Описывайте назначение, а не детали реализации
- **Избегайте избыточности**: Не повторяйте информацию, уже предоставленную типом элемента
- **Тестируйте с TalkBack**: Включите TalkBack на реальном устройстве и пройдитесь по приложению
- **Обрабатывайте крайние случаи**: Пустые состояния, загрузка, ошибки
- **Используйте семантическую группировку**: Объединяйте связанные элементы в одну цель фокуса
- **Предоставляйте альтернативы**: Обеспечьте доступность всего функционала через TalkBack

---

## Follow-ups

- What happens if you don't provide content descriptions for interactive elements?
- How do you test TalkBack navigation in automated tests?
- What's the difference between focus order and traversal order?
- How do you handle complex UI patterns like carousels with TalkBack?
- What are the performance implications of accessibility features?

## References

- [Android Accessibility Guidelines](https://developer.android.com/guide/topics/ui/accessibility)
- [TalkBack User Guide](https://support.google.com/accessibility/android/answer/6283677)
- [Compose Accessibility Documentation](https://developer.android.com/jetpack/compose/accessibility)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

## Related Questions

### Related (Medium)
- [[q-accessibility-compose--android--medium]] - Accessibility
- [[q-accessibility-testing--android--medium]] - Accessibility
- [[q-custom-view-accessibility--android--medium]] - Accessibility
- [[q-accessibility-color-contrast--android--medium]] - Accessibility
- [[q-accessibility-text-scaling--android--medium]] - Accessibility

