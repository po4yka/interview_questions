---
topic: android
tags:
  - android
  - android/ui-compose
  - jetpack-compose
  - lazy-column
  - platform/android
  - ui-compose
difficulty: easy
---

# Как в Jetpack Compose создать список, аналогичный RecyclerView?

**English**: How to create a RecyclerView-like list in Jetpack Compose?

## Answer

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

## Ответ

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

