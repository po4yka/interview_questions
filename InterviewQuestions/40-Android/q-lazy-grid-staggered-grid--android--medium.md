---\
id: android-071
title: LazyGrid & LazyStaggeredGrid / LazyGrid и LazyStaggeredGrid
aliases: [LazyGrid & LazyStaggeredGrid, LazyGrid и LazyStaggeredGrid]
topic: android
subtopics: [performance-rendering, ui-compose]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android-ui-composition, q-compose-core-components--android--medium, q-compose-lazy-layout-optimization--android--hard, q-dagger-build-time-optimization--android--medium, q-data-sync-unstable-network--android--hard]
created: 2025-10-12
updated: 2025-11-10
tags: [android/performance-rendering, android/ui-compose, difficulty/medium, grid, lazy-layout, performance]
sources:
  - "https://developer.android.com/jetpack/compose/lists"
---\
# Вопрос (RU)
> Как работают LazyGrid и LazyStaggeredGrid в Jetpack Compose?

# Question (EN)
> How do LazyGrid and LazyStaggeredGrid work in Jetpack Compose?

---

## Ответ (RU)

**Теория LazyGrid:**
Под "LazyGrid" в Jetpack Compose обычно подразумеваются ленивые сеточные компоновщики `LazyVerticalGrid` и `LazyHorizontalGrid`. Они отображают элементы в виде сетки с ленивой загрузкой: композируют и размещают только элементы в видимой области (и немного вокруг неё для плавного скролла), а вышедшие за пределы вьюпорта элементы могут быть удалены из композиции.

**Основные типы:**
- `LazyVerticalGrid` — вертикальная прокрутка
- `LazyHorizontalGrid` — горизонтальная прокрутка
- `LazyVerticalStaggeredGrid` — вертикальная сетка с переменной высотой элементов
- `LazyHorizontalStaggeredGrid` — горизонтальная сетка с переменным размером по поперечной оси

Все эти компоненты работают лениво: они создают и размещают только видимые элементы. Staggered-варианты позволяют элементам иметь разную высоту/ширину, формируя "водопадную" сетку.

См. также: [[c-android-ui-composition]]

**Типы колонок:**
```kotlin
// Фиксированные колонки
LazyVerticalGrid(
    columns = GridCells.Fixed(2) // Всегда 2 колонки
) { /* items */ }

// Адаптивные колонки
LazyVerticalGrid(
    columns = GridCells.Adaptive(minSize = 120.dp) // Минимум 120dp на колонку
) { /* items */ }
```

**Span элементов (только для LazyGrid):**
```kotlin
// Элемент занимает несколько колонок
LazyVerticalGrid(
    columns = GridCells.Fixed(3)
) {
    items(
        count = items.size,
        span = { index ->
            // Каждый 4-й элемент занимает все колонки
            if (index % 4 == 0) {
                GridItemSpan(maxLineSpan)
            } else {
                GridItemSpan(1)
            }
        }
    ) { index ->
        GridItem(items[index])
    }
}
```

**StaggeredGrid для переменной высоты:**
```kotlin
// Pinterest-style layout
LazyVerticalStaggeredGrid(
    columns = StaggeredGridCells.Fixed(2),
    verticalItemSpacing = 8.dp
) {
    items(
        count = items.size,
        key = { items[it].id }
    ) { index ->
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .height(items[index].height.dp)
        ) {
            Text("Item ${items[index].id}")
        }
    }
}
```

**Оптимизация производительности:**
```kotlin
// Использование стабильных ключей и contentType для оптимизации
LazyVerticalGrid(
    columns = GridCells.Fixed(2)
) {
    items(
        count = items.size,
        key = { items[it].id }, // Рекомендуется для стабильной идентичности и переиспользования
        contentType = { /* Группируйте элементы с одинаковой структурой содержимого */ "item" }
    ) { index ->
        ItemCard(items[index])
    }
}
```

## Answer (EN)

**LazyGrid Theory:**
In Jetpack Compose, "LazyGrid" typically refers to the lazy grid composables `LazyVerticalGrid` and `LazyHorizontalGrid`. They display items in a grid layout with lazy behavior: only items within (and slightly around) the visible viewport are composed and laid out, and items scrolled far off-screen may be disposed.

**Main types:**
- `LazyVerticalGrid` - vertical scrolling
- `LazyHorizontalGrid` - horizontal scrolling
- `LazyVerticalStaggeredGrid` - vertical grid with variable item heights
- `LazyHorizontalStaggeredGrid` - horizontal grid with variable size along the cross axis

All of these are lazy layouts: they only create and measure visible items. The staggered variants allow items to have varying heights/widths, forming a "waterfall"-style grid.

See also: [[c-android-ui-composition]]

**Column types:**
```kotlin
// Fixed columns
LazyVerticalGrid(
    columns = GridCells.Fixed(2) // Always 2 columns
) { /* items */ }

// Adaptive columns
LazyVerticalGrid(
    columns = GridCells.Adaptive(minSize = 120.dp) // Minimum 120dp per column
) { /* items */ }
```

**Item spans (LazyGrid only):**
```kotlin
// Item spans multiple columns
LazyVerticalGrid(
    columns = GridCells.Fixed(3)
) {
    items(
        count = items.size,
        span = { index ->
            // Every 4th item spans all columns
            if (index % 4 == 0) {
                GridItemSpan(maxLineSpan)
            } else {
                GridItemSpan(1)
            }
        }
    ) { index ->
        GridItem(items[index])
    }
}
```

**StaggeredGrid for variable heights:**
```kotlin
// Pinterest-style layout
LazyVerticalStaggeredGrid(
    columns = StaggeredGridCells.Fixed(2),
    verticalItemSpacing = 8.dp
) {
    items(
        count = items.size,
        key = { items[it].id }
    ) { index ->
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .height(items[index].height.dp)
        ) {
            Text("Item ${items[index].id}")
        }
    }
}
```

**Performance optimization:**
```kotlin
// Using stable keys and contentType to help performance and state stability
LazyVerticalGrid(
    columns = GridCells.Fixed(2)
) {
    items(
        count = items.size,
        key = { items[it].id }, // Recommended for stable item identity and reuse
        contentType = { /* Group items with the same content structure */ "item" }
    ) { index ->
        ItemCard(items[index])
    }
}
```

---

## Follow-ups

- How does LazyGrid prefetching work?
- What's the performance difference between LazyGrid and FlowRow?
- How do you implement drag-and-drop in LazyGrid?

## References

- [Android Documentation](https://developer.android.com/docs)
- [Jetpack Compose](https://developer.android.com/develop/ui/compose)

## Related Questions

### Prerequisites (Easier)
- [[q-jetpack-compose-lazy-column--android--easy]] - LazyColumn basics
- [[q-what-is-known-about-recyclerview--android--easy]] - `RecyclerView` fundamentals
- [[q-which-layout-for-large-list--android--easy]] - Layout choices for lists

### Related (Same Level)
- [[q-jetpack-compose-basics--android--medium]] - Compose fundamentals
- [[q-state-hoisting-compose--android--medium]] - State management in Compose
- [[q-paging-library-3--android--medium]] - Paging with lazy layouts
- [[q-compose-modifier-order-performance--android--medium]] - Modifier performance

### Advanced (Harder)
- [[q-compose-lazy-layout-optimization--android--hard]] - Advanced lazy layout optimization
- [[q-compose-performance-optimization--android--hard]] - Comprehensive Compose performance
- [[q-compose-custom-layout--android--hard]] - Custom layout implementations
