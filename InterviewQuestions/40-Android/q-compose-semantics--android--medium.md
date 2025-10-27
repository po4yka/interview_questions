---
id: 20251012-122710
title: Semantics in Jetpack Compose / Семантика в Jetpack Compose
aliases: ["Semantics in Jetpack Compose", "Семантика в Jetpack Compose"]
topic: android
subtopics: [a11y, testing-unit, ui-compose]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-compose-modifier-system--android--medium, q-compose-performance-optimization--android--hard, q-compose-testing--android--medium]
created: 2025-10-06
updated: 2025-10-27
tags: [android/a11y, android/testing-unit, android/ui-compose, difficulty/medium]
sources: [https://developer.android.com/jetpack/compose/semantics]
---

# Вопрос (RU)
> Что такое семантика в Jetpack Compose и зачем она нужна?

# Question (EN)
> What is Semantics in Jetpack Compose and why is it needed?

---

## Ответ (RU)

### Концепция
Semantics — это механизм в Compose для передачи смысла и структуры UI сервисам доступности (TalkBack, Switch Access) и тестовым API. Система семантики создаёт параллельное дерево узлов с метаданными, которое описывает *назначение* элементов, а не их визуальное представление.

Ключевые свойства: `contentDescription`, `role`, `stateDescription`, `progressBarRangeInfo`, `selected`, `disabled`.

### Основные паттерны

**Доступная кнопка**
```kotlin
Box(
  Modifier
    .clickable(onClick = onClick)
    .semantics {
      contentDescription = "Отправить"
      role = Role.Button
    }
) {
  Text("Отправить")
}
```

**Изображение с описанием**
```kotlin
// ✅ Правильно: описание для важного контента
Image(
  painter = painterResource(R.drawable.profile),
  contentDescription = "Фото профиля пользователя"
)

// ✅ Декоративное изображение
Image(
  painter = painterResource(R.drawable.divider),
  contentDescription = null // явно указываем отсутствие
)
```

**Индикатор прогресса**
```kotlin
Box(
  Modifier.semantics {
    progressBarRangeInfo = ProgressBarRangeInfo(
      current = progress,
      range = 0f..1f
    )
    stateDescription = "${(progress * 100).toInt()}%"
  }
) {
  LinearProgressIndicator(progress)
}
```

**Объединение дочерних элементов**
```kotlin
// ✅ TalkBack прочитает "Иван Иванов" вместо двух отдельных текстов
Row(
  Modifier.semantics(mergeDescendants = true) {
    contentDescription = "$firstName $lastName"
  }
) {
  Text(firstName)
  Text(lastName)
}
```

**Тестовые селекторы**
```kotlin
// UI
Button(
  onClick = onSubmit,
  modifier = Modifier.testTag("submit_button")
) {
  Text("Отправить")
}

// Тест
composeTestRule
  .onNodeWithTag("submit_button")
  .assertIsEnabled()
  .performClick()
```

### Рекомендации
- Всегда устанавливайте `contentDescription` для информативных изображений и иконок
- Используйте `mergeDescendants = true` для составных элементов, чтобы избежать дублирующихся объявлений
- Применяйте `testTag` вместо текстовых селекторов для стабильности тестов

## Answer (EN)

### Concept
Semantics is a Compose mechanism for exposing UI meaning and structure to accessibility services (TalkBack, Switch Access) and test APIs. The semantics system creates a parallel tree of nodes with metadata that describes the *purpose* of elements, not their visual representation.

Key properties: `contentDescription`, `role`, `stateDescription`, `progressBarRangeInfo`, `selected`, `disabled`.

### Core Patterns

**Accessible button**
```kotlin
Box(
  Modifier
    .clickable(onClick = onClick)
    .semantics {
      contentDescription = "Submit"
      role = Role.Button
    }
) {
  Text("Submit")
}
```

**Image with description**
```kotlin
// ✅ Correct: description for meaningful content
Image(
  painter = painterResource(R.drawable.profile),
  contentDescription = "User profile photo"
)

// ✅ Decorative image
Image(
  painter = painterResource(R.drawable.divider),
  contentDescription = null // explicitly mark as decorative
)
```

**Progress indicator**
```kotlin
Box(
  Modifier.semantics {
    progressBarRangeInfo = ProgressBarRangeInfo(
      current = progress,
      range = 0f..1f
    )
    stateDescription = "${(progress * 100).toInt()}%"
  }
) {
  LinearProgressIndicator(progress)
}
```

**Merging child semantics**
```kotlin
// ✅ TalkBack will read "John Doe" instead of two separate texts
Row(
  Modifier.semantics(mergeDescendants = true) {
    contentDescription = "$firstName $lastName"
  }
) {
  Text(firstName)
  Text(lastName)
}
```

**Test selectors**
```kotlin
// UI
Button(
  onClick = onSubmit,
  modifier = Modifier.testTag("submit_button")
) {
  Text("Submit")
}

// Test
composeTestRule
  .onNodeWithTag("submit_button")
  .assertIsEnabled()
  .performClick()
```

### Guidelines
- Always set `contentDescription` for informative images and icons
- Use `mergeDescendants = true` for compound elements to avoid duplicate announcements
- Apply `testTag` instead of text selectors for test stability

## Follow-ups
- How to handle live region announcements for dynamic content updates?
- When should semantics be cleared with `clearAndSetSemantics` for performance?
- How to implement custom semantics properties for domain-specific accessibility?

## References
- [[c-jetpack-compose]]
- https://developer.android.com/jetpack/compose/semantics
- https://developer.android.com/guide/topics/ui/accessibility

## Related Questions

### Prerequisites
- [[q-android-jetpack-overview--android--easy]]
- [[q-compose-modifier-system--android--medium]]

### Related
- [[q-compose-testing--android--medium]]
- Understanding TalkBack behavior and gestures

### Advanced
- [[q-compose-performance-optimization--android--hard]]
- Implementing custom accessibility actions with `customActions`
