---
id: 20251012-1227108
title: Semantics in Jetpack Compose / Семантика в Jetpack Compose
aliases: [Semantics in Jetpack Compose, Семантика в Jetpack Compose]
topic: android
subtopics: [ui-compose, accessibility, testing]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
source: https://developer.android.com/jetpack/compose/semantics
source_note: Official Compose Semantics docs
status: reviewed
moc: moc-android
related: [q-compose-testing--android--medium, q-compose-performance-optimization--android--hard, q-compose-modifier-system--android--medium]
created: 2025-10-06
updated: 2025-10-20
tags: [android/ui-compose, android/accessibility, android/testing, compose/semantics, difficulty/medium]
---
# Question (EN)
> What are Semantics in Jetpack Compose and how do they support accessibility and testing? Show minimal patterns.

# Вопрос (RU)
> Что такое Semantics в Jetpack Compose и как они помогают в доступности и тестировании? Приведите минимальные паттерны.

---

## Answer (EN)

### Concept
- Semantics expose UI meaning/structure to accessibility services and test APIs.
- Key properties: contentDescription, role, stateDescription, progressBarRangeInfo, selected/disabled.

### Minimal patterns

Accessible button semantics
```kotlin
Box(Modifier.clickable(onClick)
    .semantics { contentDescription = "Submit"; role = Role.Button }) {
  Text("Submit")
}
```

Image with alt text
```kotlin
Image(painter = painter, contentDescription = "User profile photo")
```

Custom state (progress)
```kotlin
Box(Modifier.semantics {
  progressBarRangeInfo = ProgressBarRangeInfo(current = progress, range = 0f..1f)
  stateDescription = "${(progress*100).toInt()}%"
}) { /* UI */ }
```

Merging child semantics
```kotlin
Row(Modifier.semantics(mergeDescendants = true) {
  contentDescription = "$firstName $lastName"
}) { Text(firstName); Text(lastName) }
```

Testing selectors
```kotlin
// In UI
Button(Modifier.testTag("submit"), onClick = onSubmit) { Text("Submit") }
// In test
rule.onNodeWithTag("submit").assertIsEnabled().performClick()
rule.onNodeWithText("Submit").assertExists()
```

Guidelines
- Always set contentDescription for non‑decorative images/icons.
- Prefer mergeDescendants for compound labels; avoid duplicate announcements.
- Use testTag for stable, language‑agnostic test selectors.

## Ответ (RU)

### Концепция
- Semantics раскрывают смысл/структуру UI для сервисов доступности и тест‑API.
- Важные свойства: contentDescription, role, stateDescription, progressBarRangeInfo, selected/disabled.

### Минимальные паттерны

Кнопка с семантикой
```kotlin
Box(Modifier.clickable(onClick)
    .semantics { contentDescription = "Submit"; role = Role.Button }) {
  Text("Submit")
}
```

Изображение с alt‑текстом
```kotlin
Image(painter = painter, contentDescription = "User profile photo")
```

Пользовательское состояние (progress)
```kotlin
Box(Modifier.semantics {
  progressBarRangeInfo = ProgressBarRangeInfo(current = progress, range = 0f..1f)
  stateDescription = "${(progress*100).toInt()}%"
}) { /* UI */ }
```

Слияние семантики детей
```kotlin
Row(Modifier.semantics(mergeDescendants = true) {
  contentDescription = "$firstName $lastName"
}) { Text(firstName); Text(lastName) }
```

Селекторы в тестах
```kotlin
// В UI
Button(Modifier.testTag("submit"), onClick = onSubmit) { Text("Submit") }
// В тесте
rule.onNodeWithTag("submit").assertIsEnabled().performClick()
rule.onNodeWithText("Submit").assertExists()
```

Рекомендации
- Всегда указывайте contentDescription для недекоративных изображений/иконок.
- Используйте mergeDescendants для составных подписей; избегайте повторов.
- Применяйте testTag как стабильный, независимый от языка селектор.

---

## Follow-ups
- How to handle live region announcements for dynamic content?
- When to expose vs hide semantics for performance or redundancy?
- How to structure semantics for custom controls (slider, chips)?

## References
- https://developer.android.com/jetpack/compose/semantics
- https://developer.android.com/guide/topics/ui/accessibility

## Related Questions

### Prerequisites (Easier)
- [[q-android-jetpack-overview--android--easy]]

### Related (Same Level)
- [[q-compose-testing--android--medium]]
- [[q-compose-modifier-system--android--medium]]

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]]

