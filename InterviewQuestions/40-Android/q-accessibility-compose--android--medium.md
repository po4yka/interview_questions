---
id: 20251012-122749
title: Доступность в Compose / Accessibility in Compose
aliases: ["Accessibility in Compose", "Доступность в Compose"]
topic: android
subtopics: [ui-accessibility, ui-compose]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-accessibility, c-jetpack-compose, q-accessibility-talkback--android--medium, q-accessibility-testing--android--medium, q-custom-view-accessibility--android--medium]
created: 2025-10-11
updated: 2025-10-29
sources:
  - https://developer.android.com/jetpack/compose/accessibility
  - https://developer.android.com/guide/topics/ui/accessibility
tags: [android/ui-accessibility, android/ui-compose, accessibility, compose, talkback, semantics, difficulty/medium]
---
# Вопрос (RU)
> Как обеспечить доступность в Jetpack Compose для людей с ограниченными возможностями?

---

# Question (EN)
> How to ensure accessibility in Jetpack Compose for people with disabilities?

---

## Ответ (RU)

**Доступность в Compose** обеспечивает использование приложения людьми с ограниченными возможностями через TalkBack, семантические свойства и минимальные размеры сенсорных целей (48dp).

### Ключевые техники

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

**2. Semantic Properties** — семантика для кастомных элементов:

```kotlin
Box(
    modifier = Modifier
        .semantics {
            role = Role.Switch  // ✅ Тип элемента
            toggleableState = ToggleableState(checked)
            contentDescription = "Notifications $state"
        }
)
```

**3. Merge Descendants** — группировка семантики:

```kotlin
Card(
    modifier = Modifier.semantics(mergeDescendants = true) {
        contentDescription = "${product.name}, $${product.price}, ${product.stock}"
    }
) {
    Column {
        Text(product.name)
        Text("$${product.price}")
        Text(product.stock)
    }
}
```

**4. Touch Target Size** — минимум 48dp:

```kotlin
// ✅ Правильно
IconButton(
    onClick = { },
    modifier = Modifier.size(48.dp)  // ✅ 48dp
) {
    Icon(imageVector = Icons.Default.Delete, contentDescription = "Delete")
}

// ❌ Неправильно
Icon(
    modifier = Modifier.size(24.dp).clickable { }  // ❌ 24dp!
)
```

**5. Custom Actions** — дополнительные действия:

```kotlin
Card(
    modifier = Modifier.semantics {
        customActions = listOf(
            CustomAccessibilityAction("Delete") { onDelete(); true },
            CustomAccessibilityAction("Archive") { onArchive(); true }
        )
    }
)
```

### Ключевые принципы

- **ContentDescription**: обязательно для информативных элементов, `null` для декоративных
- **Touch targets**: минимум 48dp для всех интерактивных элементов
- **MergeDescendants**: группировка сложных компонентов в единое семантическое описание
- **Semantic properties**: `role`, `toggleableState`, `liveRegion` для кастомных элементов
- **Тестирование**: всегда проверять с включенным TalkBack

---

## Answer (EN)

**Accessibility in Compose** ensures app usability for people with disabilities through TalkBack support, semantic properties, and minimum touch target sizes (48dp).

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

**2. Semantic Properties** — semantics for custom elements:

```kotlin
Box(
    modifier = Modifier
        .semantics {
            role = Role.Switch  // ✅ Element type
            toggleableState = ToggleableState(checked)
            contentDescription = "Notifications $state"
        }
)
```

**3. Merge Descendants** — group semantic information:

```kotlin
Card(
    modifier = Modifier.semantics(mergeDescendants = true) {
        contentDescription = "${product.name}, $${product.price}, ${product.stock}"
    }
) {
    Column {
        Text(product.name)
        Text("$${product.price}")
        Text(product.stock)
    }
}
```

**4. Touch Target Size** — minimum 48dp:

```kotlin
// ✅ Correct
IconButton(
    onClick = { },
    modifier = Modifier.size(48.dp)  // ✅ 48dp
) {
    Icon(imageVector = Icons.Default.Delete, contentDescription = "Delete")
}

// ❌ Wrong
Icon(
    modifier = Modifier.size(24.dp).clickable { }  // ❌ 24dp!
)
```

**5. Custom Actions** — additional actions:

```kotlin
Card(
    modifier = Modifier.semantics {
        customActions = listOf(
            CustomAccessibilityAction("Delete") { onDelete(); true },
            CustomAccessibilityAction("Archive") { onArchive(); true }
        )
    }
)
```

### Key Principles

- **ContentDescription**: required for meaningful elements, `null` for decorative
- **Touch targets**: minimum 48dp for all interactive elements
- **MergeDescendants**: group complex components into single semantic description
- **Semantic properties**: `role`, `toggleableState`, `liveRegion` for custom elements
- **Testing**: always verify with TalkBack enabled

---

## Follow-ups

- Что происходит, если не указать contentDescription для изображений?
- В чём разница между `mergeDescendants` и `clearAndSetSemantics`?
- Как использовать `LiveRegionMode.Polite` vs `LiveRegionMode.Assertive`?
- Как тестировать accessibility с помощью Accessibility Scanner?
- Какие semantic properties кроме `role` и `contentDescription` существуют?

## References

- [[c-accessibility]] — Основы accessibility
- [[c-jetpack-compose]] — Jetpack Compose fundamentals
- https://developer.android.com/jetpack/compose/accessibility
- https://developer.android.com/guide/topics/ui/accessibility/testing

## Related Questions

### Prerequisites (Easier)
- [[c-accessibility]] — Accessibility concepts
- [[c-jetpack-compose]] — Jetpack Compose basics

### Related (Same Level)
- [[q-accessibility-talkback--android--medium]] — TalkBack testing
- [[q-accessibility-testing--android--medium]] — Accessibility testing
- [[q-custom-view-accessibility--android--medium]] — Custom view accessibility

### Advanced (Harder)
- [[q-compose-stability-skippability--android--hard]] — Compose stability and skippability
- [[q-compose-modifier-order--android--hard]] — Modifier order importance