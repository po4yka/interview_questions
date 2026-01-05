---
id: android-026
title: Semantics in Jetpack Compose / Семантика в Jetpack Compose
aliases: [Semantics in Jetpack Compose, Семантика в Jetpack Compose]
topic: android
subtopics: [testing-ui, ui-accessibility, ui-compose]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-jetpack-compose, q-accessibility-compose--android--medium, q-compose-modifier-system--android--medium, q-compose-testing--android--medium, q-how-does-jetpack-compose-work--android--medium]
created: 2025-10-06
updated: 2025-10-30
tags: [accessibility, android/testing-ui, android/ui-accessibility, android/ui-compose, compose, difficulty/medium, testing]
sources:
  - https://developer.android.com/guide/topics/ui/accessibility
  - https://developer.android.com/jetpack/compose/semantics
---
# Вопрос (RU)
> Что такое семантика в Jetpack Compose и зачем она нужна?

# Question (EN)
> What is Semantics in Jetpack Compose and why is it needed?

---

## Ответ (RU)

### Концепция
Semantics — механизм в Compose для передачи смысла UI элементов сервисам доступности (TalkBack, Switch Access), тестовым фреймворкам и другим инструментам. Создаёт параллельное дерево узлов с метаданными, описывающими *назначение* компонентов независимо от визуального представления.

**Ключевые свойства**: `contentDescription`, `role`, `stateDescription`, `progressBarRangeInfo`, `selected`, `disabled`, `onClick`.

### Основные Паттерны

**Доступная кнопка с ролью**
```kotlin
Box(
  Modifier
    .clickable(onClick = onClick)
    .semantics {
      contentDescription = "Отправить форму"
      // clickable уже задаёт роль кнопки по умолчанию; здесь role = Role.Button только делает это явно
      role = Role.Button
    }
) { Icon(Icons.Default.Send) }
```

**Описание изображений**
```kotlin
// ✅ Информативное изображение
Image(
  painter = painterResource(R.drawable.user),
  contentDescription = "Фото профиля: Иван Петров"
)

// ✅ Декоративное изображение
Image(
  painter = painterResource(R.drawable.divider),
  contentDescription = null // TalkBack пропустит
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
    stateDescription = "Загрузка: ${(progress * 100).toInt()}%"
  }
) { LinearProgressIndicator(progress) }
```

**Объединение дочерних элементов**
```kotlin
// ✅ TalkBack прочитает "Иван Иванов, 25 лет" как единое объявление
Row(
  Modifier.semantics(mergeDescendants = true) {
    contentDescription = "$name, $age лет"
  }
) {
  Text(name, style = MaterialTheme.typography.titleMedium)
  Text("$age лет", style = MaterialTheme.typography.bodyMedium)
}

// ❗ mergeDescendants = true объединяет семантику детей в один узел;
// используйте его, когда логически нужен единый элемент, а не всегда автоматически
```

**Тестовые селекторы**
```kotlin
// UI
Button(
  onClick = onSubmit,
  modifier = Modifier.testTag("submit_btn") // ✅ Стабильный селектор
) { Text("Отправить") }

// Тест
composeTestRule
  .onNodeWithTag("submit_btn")
  .assertIsEnabled()
  .performClick()
```

### Критические Правила
- **Информативный контент**: всегда задавайте `contentDescription` для изображений/иконок с полезной информацией
- **Декоративные элементы**: явно указывайте `contentDescription = null`, чтобы TalkBack пропускал их
- **Составные компоненты**: используйте `mergeDescendants = true`, когда несколько визуальных элементов логически образуют один доступный элемент, чтобы избежать лишних и дублирующих объявлений
- **Тестирование**: применяйте `testTag` вместо текстовых селекторов для устойчивости к локализации

## Answer (EN)

### Concept
Semantics is Compose's mechanism for conveying UI element meaning to accessibility services (TalkBack, Switch Access), test frameworks, and other tooling. It creates a parallel tree of nodes with metadata describing component *purpose* independently of visual representation.

**Key properties**: `contentDescription`, `role`, `stateDescription`, `progressBarRangeInfo`, `selected`, `disabled`, `onClick`.

### Core Patterns

**Accessible button with role**
```kotlin
Box(
  Modifier
    .clickable(onClick = onClick)
    .semantics {
      contentDescription = "Submit form"
      // clickable already sets the button role by default; role = Role.Button here is only making it explicit
      role = Role.Button
    }
) { Icon(Icons.Default.Send) }
```

**Image descriptions**
```kotlin
// ✅ Informative image
Image(
  painter = painterResource(R.drawable.user),
  contentDescription = "Profile photo: John Doe"
)

// ✅ Decorative image
Image(
  painter = painterResource(R.drawable.divider),
  contentDescription = null // TalkBack will skip
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
    stateDescription = "Loading: ${(progress * 100).toInt()}%"
  }
) { LinearProgressIndicator(progress) }
```

**Merging child semantics**
```kotlin
// ✅ TalkBack reads "John Doe, 25 years old" as a single announcement
Row(
  Modifier.semantics(mergeDescendants = true) {
    contentDescription = "$name, $age years old"
  }
) {
  Text(name, style = MaterialTheme.typography.titleMedium)
  Text("$age years old", style = MaterialTheme.typography.bodyMedium)
}

// ❗ mergeDescendants = true merges children semantics into a single node;
// use it when they should logically form one accessible element, not blindly in all composites
```

**Test selectors**
```kotlin
// UI
Button(
  onClick = onSubmit,
  modifier = Modifier.testTag("submit_btn") // ✅ Stable selector
) { Text("Submit") }

// Test
composeTestRule
  .onNodeWithTag("submit_btn")
  .assertIsEnabled()
  .performClick()
```

### Critical Rules
- **Informative content**: always provide `contentDescription` for images/icons that convey meaningful information
- **Decorative elements**: explicitly set `contentDescription = null` so TalkBack skips them
- **Compound components**: use `mergeDescendants = true` when multiple visual elements logically represent a single accessible element, to avoid redundant or noisy announcements
- **Testing**: apply `testTag` instead of text selectors to remain resilient to localization

## Follow-ups

- How do `clearAndSetSemantics` and `semantics(mergeDescendants = false) {}` differ in behavior?
- When should you implement custom semantics properties using `SemanticsPropertyKey`?
- How do live region announcements work for dynamic content updates (e.g., `LiveRegionMode`)?
- What are the performance implications of deeply nested semantics trees in large lists?
- How does semantics tree traversal work for multi-window and foldable device scenarios?

## References

- [[c-jetpack-compose]]
- https://developer.android.com/jetpack/compose/semantics
- [Accessibility](https://developer.android.com/guide/topics/ui/accessibility)
- https://developer.android.com/jetpack/compose/testing

## Related Questions

### Prerequisites (Easier)
- [[q-android-jetpack-overview--android--easy]] — Understanding Jetpack libraries
- [[q-compose-modifier-system--android--medium]] — Modifier chaining fundamentals

### Related (Same Level)
- [[q-compose-testing--android--medium]] — Testing Compose UIs with semantics

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] — Optimizing semantics tree for large UIs
