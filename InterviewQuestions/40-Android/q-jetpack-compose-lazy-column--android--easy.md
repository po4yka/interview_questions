---
id: 20251003-140000
title: Jetpack Compose LazyColumn / LazyColumn в Jetpack Compose
aliases: [LazyColumn, RecyclerView in Compose, LazyColumn в Jetpack Compose]

# Classification
topic: android
subtopics: [ui-compose]
question_kind: android
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/1020
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-android
related:
  - c-jetpack-compose
  - c-lazy-lists
  - c-recyclerview

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags (EN only; no leading #)
tags: [jetpack-compose, lazy-column, android/ui-compose, difficulty/easy, easy_kotlin, lang/ru, platform/android]
---

# Question (EN)
> How to create a RecyclerView-like list in Jetpack Compose

# Вопрос (RU)
> Как в Jetpack Compose создать список, аналогичный RecyclerView

---

## Answer (EN)

Use **LazyColumn** or **LazyRow**. They create and display items on demand, saving resources and providing smooth scrolling.

**Key points**:
- LazyColumn/LazyRow are lazy composables
- Items are composed and laid out only when visible
- Similar to RecyclerView's recycling behavior
- More efficient than regular Column/Row for large lists

**Example**:
```kotlin
LazyColumn {
    items(itemsList) { item ->
        ItemRow(item)
    }
}
```

## Ответ (RU)

Используется **LazyColumn** или **LazyRow**. Они создают и отображают элементы по мере необходимости, экономя ресурсы и обеспечивая плавную прокрутку.

**Ключевые моменты**:
- LazyColumn/LazyRow — ленивые компоненты
- Элементы создаются и размещаются только когда видимы
- Аналогично поведению переработки RecyclerView
- Более эффективны чем обычные Column/Row для больших списков

**Пример**:
```kotlin
LazyColumn {
    items(itemsList) { item ->
        ItemRow(item)
    }
}
```

---

## Follow-ups
- How to add item animations in LazyColumn?
- What's the difference between LazyColumn and LazyVerticalGrid?
- How to implement sticky headers in LazyColumn?

## References
- [[c-jetpack-compose]]
- [[c-lazy-lists]]
- [[c-recyclerview]]
- [Jetpack Compose Lists Documentation](https://developer.android.com/jetpack/compose/lists)

## Related Questions
- [[q-recyclerview-basics--android--easy]]
- [[q-compose-state-management--android--medium]]
