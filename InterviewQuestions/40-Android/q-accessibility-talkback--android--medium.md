---
id: android-055
title: Accessibility TalkBack / Доступность и TalkBack
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
status: reviewed
moc: moc-android
related:
  - c-accessibility
  - q-accessibility-compose--android--medium
  - q-accessibility-testing--android--medium
  - q-custom-view-accessibility--android--medium
created: 2025-10-11
updated: 2025-10-29
tags: [accessibility, android/ui-accessibility, android/ui-navigation, difficulty/medium, talkback]
sources:
  - https://developer.android.com/guide/topics/ui/accessibility
  - https://developer.android.com/jetpack/compose/accessibility
---

# Вопрос (RU)
> Как реализовать поддержку TalkBack в Android-приложениях?

# Question (EN)
> How do you implement TalkBack support in Android apps?

---

## Ответ (RU)

[[c-accessibility|TalkBack]] - встроенная программа чтения с экрана Android для незрячих и слабовидящих пользователей, обеспечивающая голосовую обратную связь.

### 1. Описания Контента

Каждый значимый UI элемент должен иметь осмысленное описание, объясняющее назначение:

```kotlin
// ✅ Описывает назначение, а не внешний вид
Image(
    painter = painterResource(R.drawable.profile_photo),
    contentDescription = "Фото профиля пользователя"
)

Icon(
    imageVector = Icons.Default.Delete,
    contentDescription = "Удалить элемент"
)

// ❌ Слишком общее описание
Image(
    painter = painterResource(R.drawable.icon),
    contentDescription = "Картинка"
)
```

**Декоративные элементы**: используйте `contentDescription = null` для иконок, которые дублируют текст рядом.

### 2. Семантическое Объединение

Группируйте связанные элементы, чтобы TalkBack читал их как единое целое:

```kotlin
// ✅ Объединяет иконку и текст в одно объявление
Row(
    modifier = Modifier.semantics(mergeDescendants = true) {}
) {
    Icon(Icons.Default.Star, contentDescription = null)
    Text("Избранное")
    // TalkBack: "Избранное, кнопка"
}

// ✅ Скрывает декоративные элементы
Divider(
    modifier = Modifier.semantics {
        invisibleToUser()
    }
)
```

### 3. Порядок Фокуса

Контролируйте навигацию TalkBack для логической последовательности:

```kotlin
// Compose - явный порядок обхода
Column(
    modifier = Modifier.semantics {
        traversalIndex = 1f
    }
) { /* Первый элемент */ }

// View-based
view.accessibilityTraversalBefore = R.id.next_view
view.accessibilityTraversalAfter = R.id.previous_view
```

### 4. Пользовательские Действия

Добавляйте кастомные действия для контекстных операций:

```kotlin
Box(
    modifier = Modifier.semantics {
        customActions = listOf(
            CustomAccessibilityAction("Добавить в избранное") {
                markAsFavorite()
                true
            },
            CustomAccessibilityAction("Поделиться") {
                shareItem()
                true
            }
        )
    }
)
```

### 5. Живые Регионы

Уведомляйте пользователей об изменениях без фокуса:

```kotlin
var statusMessage by remember { mutableStateOf("") }

Text(
    text = statusMessage,
    modifier = Modifier.semantics {
        liveRegion = LiveRegionMode.Polite // Не прерывает текущее чтение
    }
)

// Для срочных уведомлений
Text(
    text = errorMessage,
    modifier = Modifier.semantics {
        liveRegion = LiveRegionMode.Assertive // Прерывает чтение
    }
)
```

**Практические советы**:

- Описывайте **назначение**, а не внешний вид ("Отправить", а не "Синяя кнопка")
- Избегайте **избыточности** (TalkBack автоматически добавляет "кнопка")
- Тестируйте с **реальным TalkBack** на устройстве
- Используйте **короткие и ясные** описания (3-5 слов)

## Answer (EN)

[[c-accessibility|TalkBack]] is Android's built-in screen reader for blind and visually impaired users, providing spoken feedback for app navigation.

### 1. Content Descriptions

Every meaningful UI element needs a descriptive label explaining its purpose:

```kotlin
// ✅ Describes purpose, not appearance
Image(
    painter = painterResource(R.drawable.profile_photo),
    contentDescription = "User profile picture"
)

Icon(
    imageVector = Icons.Default.Delete,
    contentDescription = "Delete item"
)

// ❌ Too generic
Image(
    painter = painterResource(R.drawable.icon),
    contentDescription = "Image"
)
```

**Decorative elements**: use `contentDescription = null` for icons that duplicate nearby text.

### 2. Semantic Merging

Group related elements so TalkBack reads them as one unit:

```kotlin
// ✅ Merges icon and text into single announcement
Row(
    modifier = Modifier.semantics(mergeDescendants = true) {}
) {
    Icon(Icons.Default.Star, contentDescription = null)
    Text("Favorite")
    // TalkBack: "Favorite, button"
}

// ✅ Hides decorative elements
Divider(
    modifier = Modifier.semantics {
        invisibleToUser()
    }
)
```

### 3. Focus Order

Control TalkBack navigation for logical flow:

```kotlin
// Compose - explicit traversal order
Column(
    modifier = Modifier.semantics {
        traversalIndex = 1f
    }
) { /* First element */ }

// View-based
view.accessibilityTraversalBefore = R.id.next_view
view.accessibilityTraversalAfter = R.id.previous_view
```

### 4. Custom Actions

Add custom actions for contextual operations:

```kotlin
Box(
    modifier = Modifier.semantics {
        customActions = listOf(
            CustomAccessibilityAction("Mark as favorite") {
                markAsFavorite()
                true
            },
            CustomAccessibilityAction("Share") {
                shareItem()
                true
            }
        )
    }
)
```

### 5. Live Regions

Announce changes without requiring focus:

```kotlin
var statusMessage by remember { mutableStateOf("") }

Text(
    text = statusMessage,
    modifier = Modifier.semantics {
        liveRegion = LiveRegionMode.Polite // Doesn't interrupt current reading
    }
)

// For urgent notifications
Text(
    text = errorMessage,
    modifier = Modifier.semantics {
        liveRegion = LiveRegionMode.Assertive // Interrupts reading
    }
)
```

**Practical Tips**:

- Describe **purpose**, not appearance ("Submit", not "Blue button")
- Avoid **redundancy** (TalkBack automatically adds "button")
- Test with **real TalkBack** on device
- Use **short and clear** descriptions (3-5 words)

---

## Follow-ups

- How do you test TalkBack support in automated tests?
- What happens to nested interactive elements in Compose?
- How to handle complex UI like carousels and tabs?
- When should you use `mergeDescendants` vs separate announcements?
- How to optimize TalkBack for dynamic content updates?

## References

- [[c-accessibility]]
- [[q-accessibility-compose--android--medium]]
- [[q-accessibility-testing--android--medium]]
- [[q-custom-view-accessibility--android--medium]]
- https://developer.android.com/guide/topics/ui/accessibility/testing
- https://support.google.com/accessibility/android/answer/6283677

## Related Questions

### Related (Same Level)
- [[q-accessibility-compose--android--medium]]
- [[q-accessibility-testing--android--medium]]
- [[q-custom-view-accessibility--android--medium]]
