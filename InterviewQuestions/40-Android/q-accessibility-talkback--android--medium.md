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
  - c-accessibility
  - q-accessibility-compose--android--medium
  - q-accessibility-testing--android--medium
  - q-custom-view-accessibility--android--medium
created: 2025-10-11
updated: 2025-10-27
tags: [android/ui-accessibility, android/ui-navigation, difficulty/medium]
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

[[c-accessibility|TalkBack]] - это встроенная программа чтения с экрана Android, которая помогает незрячим и слабовидящим пользователям взаимодействовать с приложениями через голосовую обратную связь.

**Ключевые области:**

**1. Описания контента**

```kotlin
// ✅ Осмысленные описания
Image(
    painter = painterResource(R.drawable.profile),
    contentDescription = "Фото профиля" // ✅ Конкретное описание
)

Icon(
    imageVector = Icons.Default.Delete,
    contentDescription = "Удалить элемент" // ✅ Действие
)

// ❌ Плохо - слишком общее
Image(
    painter = painterResource(R.drawable.icon),
    contentDescription = "Картинка" // ❌ Не информативно
)
```

**2. Порядок фокуса**

```kotlin
// Compose - управление порядком навигации
Column(
    modifier = Modifier.semantics {
        traversalIndex = 1f // ✅ Явный порядок
    }
) { /* Контент */ }

// View-based
view.accessibilityTraversalBefore = R.id.next_view // ✅ Контроль навигации
```

**3. Пользовательские действия**

```kotlin
Box(
    modifier = Modifier.semantics {
        customActions = listOf(
            CustomAccessibilityAction("Добавить в избранное") { // ✅ Ясное действие
                markAsFavorite()
                true
            }
        )
    }
)
```

**4. Живые регионы**

```kotlin
var message by remember { mutableStateOf("") }

Text(
    text = message,
    modifier = Modifier.semantics {
        liveRegion = LiveRegionMode.Polite // ✅ Объявляет изменения
    }
)
```

**5. Семантическое объединение**

```kotlin
// ✅ Объединение связанных элементов
Row(
    modifier = Modifier.semantics(mergeDescendants = true) {}
) {
    Icon(Icons.Default.Star, contentDescription = null)
    Text("Избранное")
    // TalkBack читает: "Избранное, кнопка"
}

// ✅ Скрытие декоративных элементов
Divider(
    modifier = Modifier.semantics {
        invisibleToUser() // ✅ Не мешает навигации
    }
)
```

**Лучшие практики:**

- Описывайте **назначение**, а не внешний вид
- Избегайте **избыточности** ("кнопка Отправить" → "Отправить")
- **Тестируйте** на реальном устройстве
- Группируйте **связанные** элементы
- Обрабатывайте **крайние случаи**

## Answer (EN)

[[c-accessibility|TalkBack]] is Android's built-in screen reader helping blind and visually impaired users interact with apps through spoken feedback.

**Key Areas:**

**1. Content Descriptions**

```kotlin
// ✅ Meaningful descriptions
Image(
    painter = painterResource(R.drawable.profile),
    contentDescription = "Profile picture" // ✅ Specific
)

Icon(
    imageVector = Icons.Default.Delete,
    contentDescription = "Delete item" // ✅ Clear action
)

// ❌ Bad - too generic
Image(
    painter = painterResource(R.drawable.icon),
    contentDescription = "Image" // ❌ Not informative
)
```

**2. Focus Order**

```kotlin
// Compose - control navigation order
Column(
    modifier = Modifier.semantics {
        traversalIndex = 1f // ✅ Explicit order
    }
) { /* Content */ }

// View-based
view.accessibilityTraversalBefore = R.id.next_view // ✅ Navigation control
```

**3. Custom Actions**

```kotlin
Box(
    modifier = Modifier.semantics {
        customActions = listOf(
            CustomAccessibilityAction("Mark as favorite") { // ✅ Clear action
                markAsFavorite()
                true
            }
        )
    }
)
```

**4. Live Regions**

```kotlin
var message by remember { mutableStateOf("") }

Text(
    text = message,
    modifier = Modifier.semantics {
        liveRegion = LiveRegionMode.Polite // ✅ Announces changes
    }
)
```

**5. Semantic Merging**

```kotlin
// ✅ Merge related elements
Row(
    modifier = Modifier.semantics(mergeDescendants = true) {}
) {
    Icon(Icons.Default.Star, contentDescription = null)
    Text("Favorite")
    // TalkBack reads: "Favorite, button"
}

// ✅ Hide decorative elements
Divider(
    modifier = Modifier.semantics {
        invisibleToUser() // ✅ No distraction
    }
)
```

**Best Practices:**

- Describe **purpose**, not appearance
- Avoid **redundancy** ("Submit button" → "Submit")
- **Test** on real devices
- Group **related** elements
- Handle **edge cases**

---

## Follow-ups

- What happens without content descriptions?
- How to test TalkBack in automated tests?
- How to handle complex UI (carousels, tabs)?

## References

- [[c-accessibility]]
- [[q-accessibility-compose--android--medium]]
- [[q-accessibility-testing--android--medium]]
- [[q-custom-view-accessibility--android--medium]]
