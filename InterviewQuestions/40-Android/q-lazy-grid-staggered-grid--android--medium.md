---
id: android-071
title: LazyGrid & LazyStaggeredGrid / LazyGrid и LazyStaggeredGrid
aliases:
- LazyGrid & LazyStaggeredGrid
- LazyGrid и LazyStaggeredGrid
topic: android
subtopics:
- performance-rendering
- ui-compose
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-lazy-grid
created: 2025-10-12
updated: 2025-10-31
tags:
- android/performance-rendering
- android/ui-compose
- difficulty/medium
- grid
- jetpack-compose
- lazy-layout
- performance
sources:
- https://developer.android.com/jetpack/compose/lists
---

# Вопрос (RU)
> Как работают LazyGrid и LazyStaggeredGrid в Jetpack Compose?

# Question (EN)
> How do LazyGrid and LazyStaggeredGrid work in Jetpack Compose?

---

## Ответ (RU)

**Теория LazyGrid:**
LazyGrid - это композабл для отображения элементов в виде сетки с ленивой загрузкой. Оптимизирует производительность, создавая только видимые элементы. Поддерживает фиксированные и адаптивные колонки.

**Основные типы:**
- `LazyVerticalGrid` - вертикальная прокрутка
- `LazyHorizontalGrid` - горизонтальная прокрутка
- `LazyVerticalStaggeredGrid` - сетка с переменной высотой элементов

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

**Span элементов:**
```kotlin
// Элемент занимает несколько колонок
LazyVerticalGrid(
    columns = GridCells.Fixed(3)
) {
    items(
        count = items.size,
        span = { index ->
            // Каждый 4-й элемент занимает все колонки
            GridItemSpan(if (index % 4 == 0) maxLineSpan else 1)
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
// Использование ключей для оптимизации
LazyVerticalGrid(
    columns = GridCells.Fixed(2)
) {
    items(
        count = items.size,
        key = { items[it].id }, // Обязательно для производительности
        contentType = { items[it]::class } // Помогает переиспользованию
    ) { index ->
        ItemCard(items[index])
    }
}
```

## Answer (EN)

**LazyGrid Theory:**
LazyGrid is a composable for displaying items in a grid layout with lazy loading. Optimizes performance by creating only visible items. Supports fixed and adaptive columns.

**Main types:**
- `LazyVerticalGrid` - vertical scrolling
- `LazyHorizontalGrid` - horizontal scrolling
- `LazyVerticalStaggeredGrid` - grid with variable item heights

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

**Item spans:**
```kotlin
// Item spans multiple columns
LazyVerticalGrid(
    columns = GridCells.Fixed(3)
) {
    items(
        count = items.size,
        span = { index ->
            // Every 4th item spans all columns
            GridItemSpan(if (index % 4 == 0) maxLineSpan else 1)
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
// Using keys for optimization
LazyVerticalGrid(
    columns = GridCells.Fixed(2)
) {
    items(
        count = items.size,
        key = { items[it].id }, // Essential for performance
        contentType = { items[it]::class } // Helps reuse
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

### Prerequisites / Concepts

- [[c-lazy-grid]]


### Prerequisites (Easier)
- Related content to be added

### Related (Same Level)
- Related content to be added

### Advanced (Harder)
- Related content to be added
