---
id: android-050
title: Доступность в Compose / Accessibility in Compose
aliases: [Accessibility in Compose, Доступность в Compose]
topic: android
subtopics: [ui-accessibility, ui-compose]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-accessibility, q-accessibility-talkback--android--medium, q-accessibility-testing--android--medium, q-compose-semantics--android--medium, q-compose-testing--android--medium]
created: 2025-10-11
updated: 2025-11-10
sources:
  - "https://developer.android.com/guide/topics/ui/accessibility"
  - "https://developer.android.com/jetpack/compose/accessibility"
tags: [accessibility, android/ui-accessibility, android/ui-compose, compose, difficulty/medium, semantics, talkback]
---
# Вопрос (RU)
> Как обеспечить доступность в Jetpack Compose для людей с ограниченными возможностями?

---

# Question (EN)
> How to ensure accessibility in Jetpack Compose for people with disabilities?

---

## Ответ (RU)

**Доступность в Compose** обеспечивает использование приложения людьми с ограниченными возможностями через поддержку сервисов вроде TalkBack, корректные семантические свойства, фокусируемость элементов и соблюдение рекомендуемых минимальных размеров сенсорных целей (около 48dp).

### Ключевые Техники

**1. Content Descriptions** — описания для изображений:

```kotlin
// ✅ Информативный контент
Image(
    painter = painterResource(R.drawable.profile),
    contentDescription = "User profile photo"
)

// ✅ Декоративные элементы
Image(
    painter = painterResource(R.drawable.background),
    contentDescription = null  // Декоративное
)
```

- Для значимых не-текстовых элементов нужно обеспечить текстовый эквивалент (через `contentDescription` или другую семантику), при этом избегая дублирования уже читаемого текста.

**2. Semantic Properties** — семантика для кастомных элементов (если стандартных модификаторов toggleable/selectable недостаточно):

```kotlin
val checked = remember { mutableStateOf(false) }

Box(
    modifier = Modifier
        .semantics {
            role = Role.Switch  // ✅ Тип элемента
            stateDescription = if (checked.value) "On" else "Off"
        }
        .toggleable(
            value = checked.value,
            onValueChange = { checked.value = it },
            role = Role.Switch
        )
)
```

**3. Merge Descendants** — группировка семантики сложных компонентов в один анонс:

```kotlin
Card(
    modifier = Modifier.semantics(mergeDescendants = true) {
        // Потомки будут объединены в один анонс TalkBack,
        // не нужно дублировать contentDescription здесь, если
        // текст потомков уже информативен.
    }
) {
    Column {
        Text(product.name)
        Text("$${product.price}")
        Text(product.stock)
    }
}
```

**4. Touch Target Size** — минимум около 48dp:

```kotlin
// ✅ Правильно: достаточно большой таргет
IconButton(
    onClick = { },
    modifier = Modifier.size(48.dp)  // Ориентир 48dp; Material-компоненты обычно обеспечивают это сами
) {
    Icon(imageVector = Icons.Default.Delete, contentDescription = "Delete")
}

// ❌ Неправильно: слишком маленький таргет
Icon(
    modifier = Modifier
        .size(24.dp)
        .clickable { }  // ❌ 24dp!
)
```

**5. Custom Actions** — дополнительные действия, доступные через TalkBack:

```kotlin
Card(
    modifier = Modifier.semantics {
        // Добавляем дополнительные доступные действия
        this.customActions = listOf(
            CustomAccessibilityAction("Delete") { onDelete(); true },
            CustomAccessibilityAction("Archive") { onArchive(); true }
        )
    }
)
```

### Ключевые Принципы

- **contentDescription**: для значимых визуальных элементов (особенно иконок без подписи) обеспечить читаемое описание; `null` для декоративных, чтобы избежать "шума".
- **Touch targets**: ориентир минимум 48dp для всех интерактивных элементов (учитывать, что многие Material-компоненты обеспечивают это по умолчанию за счёт внутреннего отступа и минимального размера).
- **mergeDescendants**: использовать для объединения сложных компонентов в единое семантическое представление, если покомпонентный анонс мешает восприятию.
- **Semantic properties**: при кастомном поведении использовать `role`, `stateDescription`, `liveRegion` и др.; по возможности предпочитать готовые модификаторы (`clickable`, `toggleable`, `selectable`), которые уже интегрированы с accessibility.
- **Тестирование**: всегда проверять с включённым TalkBack / Switch Access и системными инструментами.

---

## Answer (EN)

**Accessibility in Compose** ensures app usability for people with disabilities through support of services like TalkBack, correct semantic properties, focusability, and respecting recommended minimum touch target sizes (around 48dp).

### Key Techniques

**1. Content Descriptions** — descriptions for images:

```kotlin
// ✅ Meaningful content
Image(
    painter = painterResource(R.drawable.profile),
    contentDescription = "User profile photo"
)

// ✅ Decorative elements
Image(
    painter = painterResource(R.drawable.background),
    contentDescription = null  // Decorative only
)
```

- For meaningful non-text elements, provide an accessible text alternative (via `contentDescription` or other semantics) while avoiding redundant labels.

**2. Semantic Properties** — semantics for custom elements (when built-in toggleable/selectable modifiers are not enough):

```kotlin
val checked = remember { mutableStateOf(false) }

Box(
    modifier = Modifier
        .semantics {
            role = Role.Switch  // ✅ Element type
            stateDescription = if (checked.value) "On" else "Off"
        }
        .toggleable(
            value = checked.value,
            onValueChange = { checked.value = it },
            role = Role.Switch
        )
)
```

**3. Merge Descendants** — group semantic information of complex components into a single announcement:

```kotlin
Card(
    modifier = Modifier.semantics(mergeDescendants = true) {
        // Children semantics will be merged into a single TalkBack announcement.
        // No need to duplicate contentDescription here if child text is already meaningful.
    }
) {
    Column {
        Text(product.name)
        Text("$${product.price}")
        Text(product.stock)
    }
}
```

**4. Touch Target Size** — minimum around 48dp:

```kotlin
// ✅ Correct: sufficiently large target
IconButton(
    onClick = { },
    modifier = Modifier.size(48.dp)  // 48dp guideline; many Material components ensure this via defaults
) {
    Icon(imageVector = Icons.Default.Delete, contentDescription = "Delete")
}

// ❌ Wrong: too small target
Icon(
    modifier = Modifier
        .size(24.dp)
        .clickable { }  // ❌ 24dp!
)
```

**5. Custom Actions** — additional actions exposed to accessibility services:

```kotlin
Card(
    modifier = Modifier.semantics {
        // Add extra accessible actions
        this.customActions = listOf(
            CustomAccessibilityAction("Delete") { onDelete(); true },
            CustomAccessibilityAction("Archive") { onArchive(); true }
        )
    }
)
```

### Key Principles

- **contentDescription**: ensure meaningful visual elements (especially unlabeled icons) have an accessible name; use `null` for decorative content to avoid noise.
- **Touch targets**: aim for at least 48dp for interactive elements (noting many Material components achieve this through padding/minSize rather than explicit sizes).
- **mergeDescendants**: use to group complex components into a single semantic node when separate announcements harm usability.
- **Semantic properties**: for custom behavior, use `role`, `stateDescription`, `liveRegion`, etc.; prefer built-in modifiers (`clickable`, `toggleable`, `selectable`) that are accessibility-aware.
- **Testing**: always verify with TalkBack / Switch Access and platform accessibility tools enabled.

---

## Дополнительные Вопросы (RU)

- Что происходит, если не указать `contentDescription` для изображений?
- В чём разница между `mergeDescendants` и `clearAndSetSemantics`?
- Как использовать `LiveRegionMode.Polite` vs `LiveRegionMode.Assertive`?
- Как тестировать accessibility с помощью Accessibility Scanner?
- Какие semantic properties кроме `role` и `contentDescription` существуют?

## Follow-ups (EN)

- What happens if you do not specify `contentDescription` for images?
- What is the difference between `mergeDescendants` and `clearAndSetSemantics`?
- How to use `LiveRegionMode.Polite` vs `LiveRegionMode.Assertive`?
- How to test accessibility using Accessibility Scanner?
- Which semantic properties exist besides `role` and `contentDescription`?

## Ссылки (RU)

- [[c-accessibility]] — Основы accessibility
- https://developer.android.com/jetpack/compose/accessibility
- https://developer.android.com/guide/topics/ui/accessibility/testing

## References (EN)

- [[c-accessibility]] — Accessibility basics
- https://developer.android.com/jetpack/compose/accessibility
- https://developer.android.com/guide/topics/ui/accessibility/testing

## Related Questions

### Prerequisites (Easier)
- [[c-accessibility]] — Accessibility concepts

### Related (Same Level)
- [[q-accessibility-talkback--android--medium]] — TalkBack testing
- [[q-accessibility-testing--android--medium]] — Accessibility testing

### Advanced (Harder)
