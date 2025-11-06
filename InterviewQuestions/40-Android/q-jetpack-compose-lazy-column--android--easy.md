---
id: android-438
title: "Jetpack Compose Lazy Column / LazyColumn в Jetpack Compose"
aliases: ["Compose список", "Jetpack Compose Lazy Column", "LazyColumn в Jetpack Compose"]
topic: android
subtopics: [ui-compose, ui-widgets]
question_kind: android
difficulty: easy
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-jetpack-compose, c-recyclerview, q-jetpack-compose-basics--android--medium, q-which-layout-for-large-list--android--easy]
created: 2025-10-15
updated: 2025-10-30
sources: []
tags: [android/ui-compose, android/ui-widgets, difficulty/easy, jetpack-compose, lazy-list]
---

# Вопрос (RU)

Как в Jetpack Compose создать список, аналогичный `RecyclerView`?

# Question (EN)

How to create a `RecyclerView`-like list in Jetpack Compose?

---

## Ответ (RU)

Используйте **LazyColumn** или **LazyRow** для вертикальных и горизонтальных списков соответственно.

### Основные Характеристики

LazyColumn создает элементы по требованию (lazy) — только видимые на экране:
- Аналог `RecyclerView` с автоматическим переиспользованием
- Не требует настройки Adapter и ViewHolder
- Поддерживает разные типы элементов в одном списке

### Базовый Пример

```kotlin
@Composable
fun ContactsList(contacts: List<Contact>) {
    LazyColumn {
        items(contacts) { contact ->
            ContactRow(contact)  // ✅ Простой синтаксис
        }
    }
}
```

### Работа С Индексами

```kotlin
LazyColumn {
    itemsIndexed(items) { index, item ->
        Text("$index: ${item.name}")  // ✅ Доступ к позиции
    }
}
```

### Разнородные Элементы

```kotlin
LazyColumn {
    item { HeaderView() }           // ✅ Одиночный элемент

    items(messages) { message ->
        MessageCard(message)
    }

    item { FooterView() }
}
```

### Ключевые Различия С `RecyclerView`

| `RecyclerView` | LazyColumn |
|--------------|------------|
| Adapter + ViewHolder | Composable-функции напрямую |
| notifyDataSetChanged() | Автоматическая реакция на State |
| XML-разметка | Декларативный Compose-код |

### Когда Использовать

- **LazyColumn/LazyRow**: динамические списки любого размера
- **Column/Row**: статичный контент из 5-10 элементов (без lazy-загрузки)

## Answer (EN)

Use **LazyColumn** or **LazyRow** for vertical and horizontal lists respectively.

### Core Characteristics

LazyColumn creates items on demand (lazy) — only those visible on screen:
- `RecyclerView` equivalent with automatic recycling
- No need for Adapter or ViewHolder setup
- Supports different item types in one list

### Basic Example

```kotlin
@Composable
fun ContactsList(contacts: List<Contact>) {
    LazyColumn {
        items(contacts) { contact ->
            ContactRow(contact)  // ✅ Simple syntax
        }
    }
}
```

### Working with Indexes

```kotlin
LazyColumn {
    itemsIndexed(items) { index, item ->
        Text("$index: ${item.name}")  // ✅ Access to position
    }
}
```

### Heterogeneous Items

```kotlin
LazyColumn {
    item { HeaderView() }           // ✅ Single item

    items(messages) { message ->
        MessageCard(message)
    }

    item { FooterView() }
}
```

### Key Differences from `RecyclerView`

| `RecyclerView` | LazyColumn |
|--------------|------------|
| Adapter + ViewHolder | Composable functions directly |
| notifyDataSetChanged() | Automatic State reaction |
| XML layout | Declarative Compose code |

### When to Use

- **LazyColumn/LazyRow**: dynamic lists of any size
- **Column/Row**: static content with 5-10 items (no lazy loading)

---

## Follow-ups

- How to add dividers between LazyColumn items?
- What is the `key` parameter in `items()` and why is it important?
- How to implement sticky headers in LazyColumn?
- How does LazyColumn handle item animations?
- What is the difference between `items()` and `itemsIndexed()`?

## References

- [[c-jetpack-compose]] - Jetpack Compose fundamentals
- [[c-recyclerview]] - `RecyclerView` concept for comparison
- [Compose Lists Documentation](https://developer.android.com/jetpack/compose/lists)

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-known-about-recyclerview--android--easy]] - `RecyclerView` basics

### Related (Same Level)
- [[q-which-layout-for-large-list--android--easy]] - When to use different list layouts
- [[q-android-jetpack-overview--android--easy]] - Jetpack components overview

### Advanced (Medium)
- [[q-jetpack-compose-basics--android--medium]] - Comprehensive Compose introduction
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - Advanced LazyColumn patterns
- [[q-mutable-state-compose--android--medium]] - State management in lists
- [[q-recomposition-compose--android--medium]] - How list recomposition works
