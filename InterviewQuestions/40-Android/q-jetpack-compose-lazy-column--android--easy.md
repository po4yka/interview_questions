---
id: 20251012-12271114
title: "Jetpack Compose Lazy Column"
topic: android
difficulty: easy
status: draft
moc: moc-android
related: [q-privacy-sandbox-fledge--privacy--hard, q-sharedpreferences-commit-vs-apply--android--easy, q-what-is-a-view-and-what-is-responsible-for-its-visual-part--android--medium]
created: 2025-10-15
tags: [android/ui-compose, difficulty/easy, jetpack-compose, lazy-column, platform/android, ui-compose]
date created: Saturday, October 25th 2025, 1:26:31 pm
date modified: Saturday, October 25th 2025, 4:10:57 pm
---

# Как В Jetpack Compose Создать Список, Аналогичный RecyclerView?

**English**: How to create a RecyclerView-like list in Jetpack Compose?

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

## Related Questions

### Hub
- [[q-jetpack-compose-basics--android--medium]] - Comprehensive Compose introduction

### Next Steps (Medium)
- [[q-how-does-jetpack-compose-work--android--medium]] - How Compose works
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Essential Compose components
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - RecyclerView in Compose
- [[q-mutable-state-compose--android--medium]] - MutableState basics
- [[q-remember-vs-remembersaveable-compose--android--medium]] - remember vs rememberSaveable

