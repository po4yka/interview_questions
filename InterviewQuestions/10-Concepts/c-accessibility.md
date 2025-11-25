---
id: "20251025-140000"
title: "Accessibility / Доступность"
aliases: ["Accessibility", "Android Accessibility", "TalkBack", "Доступность", "Специальные возможности Android"]
summary: "Features and APIs that make Android apps usable for people with disabilities"
topic: "android"
subtopics: ["accessibility", "talkback", "ui-ux"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-android"
related: []
created: "2025-10-25"
updated: "2025-10-25"
tags: ["a11y", "accessibility", "android", "concept", "difficulty/medium", "talkback", "ui-ux"]
date created: Saturday, October 25th 2025, 11:03:49 am
date modified: Tuesday, November 25th 2025, 8:54:04 pm
---

# Accessibility / Доступность

## Summary (EN)

Android Accessibility encompasses a set of features, services, and APIs designed to make apps usable by people with visual, auditory, motor, or cognitive disabilities. It includes screen readers like TalkBack, switch access controls, content descriptions, and semantic properties that help assistive technologies understand and navigate app interfaces. Implementing accessibility ensures your app reaches a wider audience and complies with legal accessibility requirements.

## Краткое Описание (RU)

Доступность Android включает набор функций, сервисов и API, предназначенных для людей с нарушениями зрения, слуха, двигательных функций или когнитивных способностей. Включает программы чтения с экрана, такие как TalkBack, элементы управления переключением, описания контента и семантические свойства, которые помогают вспомогательным технологиям понимать и перемещаться по интерфейсам приложений. Реализация доступности обеспечивает охват более широкой аудитории и соответствие юридическим требованиям.

## Key Points (EN)

- **TalkBack Support**: Screen reader that provides spoken feedback for UI elements
- **Content Descriptions**: Text alternatives for non-text UI elements (images, icons, buttons)
- **Touch Target Sizes**: Minimum 48dp x 48dp for interactive elements
- **Focus Management**: Proper focus order and custom focus handling
- **Semantic Properties**: Labels, roles, and states for assistive technologies
- **Contrast Ratios**: Sufficient color contrast for text and UI elements (WCAG guidelines)
- **Accessibility Scanner**: Tool to identify accessibility issues
- **Live Regions**: Announce dynamic content changes to screen readers
- **Custom Actions**: Define custom accessibility actions for complex gestures

## Ключевые Моменты (RU)

- **Поддержка TalkBack**: Программа чтения с экрана с голосовой обратной связью для элементов UI
- **Описания контента**: Текстовые альтернативы для нетекстовых элементов (изображения, иконки, кнопки)
- **Размеры сенсорных целей**: Минимум 48dp x 48dp для интерактивных элементов
- **Управление фокусом**: Правильный порядок фокуса и пользовательская обработка
- **Семантические свойства**: Метки, роли и состояния для вспомогательных технологий
- **Контрастность**: Достаточная контрастность цветов для текста и UI (рекомендации WCAG)
- **Accessibility Scanner**: Инструмент для выявления проблем с доступностью
- **Live Regions**: Объявление динамических изменений контента программам чтения
- **Пользовательские действия**: Определение специальных действий для сложных жестов

## Use Cases

### When to Use

- **All production apps**: Accessibility should be a standard practice, not optional
- **Apps with rich visual content**: Images, charts, icons need descriptions
- **Complex navigation flows**: Custom focus handling for non-standard layouts
- **Form-heavy apps**: Proper labels and hints for input fields
- **Media apps**: Captions, transcripts, and audio descriptions
- **Apps targeting government or enterprise**: Often required by law (ADA, Section 508)

### When to Avoid

- Never avoid accessibility - it should always be implemented
- However, prioritize based on content: static text apps may need less custom work

## Trade-offs

**Pros**:
- **Wider audience**: Reaches 15-20% of population with disabilities
- **Legal compliance**: Meets ADA, WCAG 2.1, Section 508 requirements
- **Better UX for everyone**: Benefits all users (elderly, temporary disabilities)
- **SEO benefits**: Better app structure improves discoverability
- **Improved code quality**: Forces clearer component hierarchy and semantics

**Cons**:
- **Development time**: Requires additional testing and implementation effort
- **Maintenance overhead**: Must maintain content descriptions and semantic properties
- **Testing complexity**: Requires testing with screen readers and accessibility tools
- **Learning curve**: Developers need to understand accessibility best practices

## Implementation Guidelines

### View-based UI

**Content Descriptions**:
```kotlin
// For ImageView, ImageButton, etc.
imageView.contentDescription = "Profile picture of John Doe"

// For decorative images (ignored by TalkBack)
imageView.importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO
```

**Touch Targets**:
```kotlin
// Ensure minimum 48dp touch target
<Button
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:minWidth="48dp"
    android:minHeight="48dp"
    android:text="Click me" />
```

**Custom Actions**:
```kotlin
ViewCompat.addAccessibilityAction(
    view,
    "Mark as favorite"
) { view, arguments ->
    // Handle custom action
    markAsFavorite()
    true
}
```

**Live Regions**:
```xml
<TextView
    android:id="@+id/statusText"
    android:accessibilityLiveRegion="polite"
    android:text="Loading..." />
```

### Jetpack Compose

**Content Descriptions**:
```kotlin
Image(
    painter = painterResource(R.drawable.profile),
    contentDescription = "Profile picture of John Doe"
)

// For decorative images
Image(
    painter = painterResource(R.drawable.background),
    contentDescription = null // Ignored by TalkBack
)
```

**Semantic Properties**:
```kotlin
Row(
    modifier = Modifier.semantics(mergeDescendants = true) {
        contentDescription = "John Doe, Developer, Online"
    }
) {
    Text("John Doe")
    Text("Developer")
    Icon(Icons.Default.Circle, contentDescription = null)
}
```

**Custom Actions**:
```kotlin
Box(
    modifier = Modifier.semantics {
        customActions = listOf(
            CustomAccessibilityAction("Mark as favorite") {
                markAsFavorable()
                true
            }
        )
    }
) {
    // Content
}
```

**Touch Targets**:
```kotlin
IconButton(
    onClick = { /* ... */ },
    modifier = Modifier.minimumInteractiveComponentSize() // Ensures 48dp
) {
    Icon(Icons.Default.Star, contentDescription = "Favorite")
}
```

## Testing Accessibility

### TalkBack Testing
1. Enable TalkBack: Settings → Accessibility → TalkBack
2. Navigate using swipe gestures (right = next, left = previous)
3. Verify all elements are announced clearly
4. Test custom actions with context menu (swipe up then right)

### Accessibility Scanner
```kotlin
// Install from Play Store
// Scan your app screens for issues
// Provides suggestions for improvements
```

### Automated Testing
```kotlin
@Test
fun testAccessibility() {
    composeTestRule.onNodeWithText("Submit")
        .assertIsDisplayed()
        .assertHasClickAction()
        .assertContentDescriptionEquals("Submit form")
}
```

## Common Patterns

### Grouping Related Content
```kotlin
// View-based
<LinearLayout
    android:screenReaderFocusable="true"
    android:focusable="true">
    <TextView android:text="Title" />
    <TextView android:text="Subtitle" />
</LinearLayout>

// Compose
Row(
    modifier = Modifier.semantics(mergeDescendants = true) {}
) {
    Text("Title")
    Text("Subtitle")
}
```

### State Descriptions
```kotlin
// Compose
Switch(
    checked = isEnabled,
    onCheckedChange = { isEnabled = it },
    modifier = Modifier.semantics {
        stateDescription = if (isEnabled) "Enabled" else "Disabled"
    }
)
```

### Headings
```kotlin
// Compose
Text(
    "Section Title",
    modifier = Modifier.semantics { heading() }
)
```

## Best Practices

1. **Test with TalkBack enabled** during development
2. **Provide meaningful content descriptions** - avoid "image" or "button"
3. **Respect system accessibility settings** - font scaling, color inversion
4. **Use semantic HTML/native widgets** when possible
5. **Test with multiple accessibility services** - TalkBack, Switch Access, Voice Access
6. **Maintain contrast ratios** - 4.5:1 for normal text, 3:1 for large text
7. **Don't rely on color alone** - use icons, patterns, or labels
8. **Provide alternatives for time-based media** - captions, transcripts
9. **Make focus order logical** - follows visual layout
10. **Announce dynamic changes** - use live regions or announcements

## Related Concepts

- [[c-jetpack-compose]] - Compose accessibility APIs
- [[c-custom-views]] - Implementing accessibility in custom views
- [[c-viewmodel]] - Managing accessibility state
- [[c-material-design]] - Material Design accessibility guidelines
- [[c-testing]] - Accessibility testing strategies

## References

- [Android Accessibility Overview](https://developer.android.com/guide/topics/ui/accessibility)
- [Accessibility Principles](https://developer.android.com/guide/topics/ui/accessibility/principles)
- [Compose Accessibility](https://developer.android.com/jetpack/compose/accessibility)
- [Testing Accessibility](https://developer.android.com/guide/topics/ui/accessibility/testing)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Material Design Accessibility](https://material.io/design/usability/accessibility.html)
- [Accessibility Scanner Tool](https://play.google.com/store/apps/details?id=com.google.android.apps.accessibility.auditor)
