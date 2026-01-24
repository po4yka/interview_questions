---
id: kotlin-256
title: Compose Internals and Recomposition / Внутреннее устройство Compose и рекомпозиция
aliases:
- Compose Internals
- Recomposition
- Внутреннее устройство Compose
topic: kotlin
subtopics:
- compose
- internals
- recomposition
question_kind: theory
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-compose
- c-internals
created: 2026-01-23
updated: 2026-01-23
tags:
- kotlin
- compose
- recomposition
- slot-table
- remember
- difficulty/hard
anki_cards:
- slug: kotlin-256-0-en
  language: en
  anki_id: 1769170312746
  synced_at: '2026-01-23T17:03:50.837082'
- slug: kotlin-256-0-ru
  language: ru
  anki_id: 1769170312771
  synced_at: '2026-01-23T17:03:50.840893'
---
# Вопрос (RU)
> Как работает рекомпозиция в Jetpack Compose? Что такое Slot Table и как работает remember?

# Question (EN)
> How does recomposition work in Jetpack Compose? What is Slot Table and how does remember work?

---

## Ответ (RU)

**Рекомпозиция** - процесс повторного вызова composable функций при изменении состояния.

**Slot Table:**
Внутренняя структура данных Compose для хранения:
- Состояния composable функций
- Данных remember
- Информации о структуре UI

```
Slot Table (упрощённо):
┌─────────────────────────────────────┐
│ Group: Column                       │
│   ├── Group: Text("Hello")          │
│   │     └── State: text = "Hello"   │
│   └── Group: Button                 │
│         └── Remember: onClick       │
└─────────────────────────────────────┘
```

**Как работает remember:**
```kotlin
@Composable
fun Counter() {
    // remember сохраняет значение в Slot Table
    // при рекомпозиции значение извлекается, а не создаётся заново
    var count by remember { mutableStateOf(0) }

    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}
```

**remember vs rememberSaveable:**
```kotlin
// remember - переживает рекомпозицию
var count by remember { mutableStateOf(0) }

// rememberSaveable - переживает смену конфигурации
var count by rememberSaveable { mutableStateOf(0) }
```

**derivedStateOf - оптимизация зависимых состояний:**
```kotlin
@Composable
fun FilteredList(items: List<Item>, query: String) {
    // БЕЗ derivedStateOf: фильтрация при каждой рекомпозиции
    val filtered = items.filter { it.name.contains(query) }

    // С derivedStateOf: фильтрация только при изменении items или query
    val filtered by remember(items, query) {
        derivedStateOf { items.filter { it.name.contains(query) } }
    }
}
```

**CompositionLocal - передача данных через дерево:**
```kotlin
// Определение
val LocalTheme = compositionLocalOf { Theme.Light }

// Предоставление значения
CompositionLocalProvider(LocalTheme provides Theme.Dark) {
    MyComposable()
}

// Чтение
@Composable
fun MyComposable() {
    val theme = LocalTheme.current
}
```

**Ключи для рекомпозиции:**
```kotlin
@Composable
fun ItemList(items: List<Item>) {
    Column {
        items.forEach { item ->
            // key помогает Compose идентифицировать элементы
            key(item.id) {
                ItemRow(item)
            }
        }
    }
}
```

**Фазы Compose:**
1. **Composition** - построение дерева UI
2. **Layout** - измерение и позиционирование
3. **Drawing** - отрисовка на экране

## Answer (EN)

**Recomposition** - process of re-calling composable functions when state changes.

**Slot Table:**
Internal Compose data structure for storing:
- Composable function state
- Remember data
- UI structure information

```
Slot Table (simplified):
┌─────────────────────────────────────┐
│ Group: Column                       │
│   ├── Group: Text("Hello")          │
│   │     └── State: text = "Hello"   │
│   └── Group: Button                 │
│         └── Remember: onClick       │
└─────────────────────────────────────┘
```

**How remember Works:**
```kotlin
@Composable
fun Counter() {
    // remember stores value in Slot Table
    // on recomposition, value is retrieved, not recreated
    var count by remember { mutableStateOf(0) }

    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}
```

**remember vs rememberSaveable:**
```kotlin
// remember - survives recomposition
var count by remember { mutableStateOf(0) }

// rememberSaveable - survives configuration changes
var count by rememberSaveable { mutableStateOf(0) }
```

**derivedStateOf - Optimizing Dependent State:**
```kotlin
@Composable
fun FilteredList(items: List<Item>, query: String) {
    // WITHOUT derivedStateOf: filtering on every recomposition
    val filtered = items.filter { it.name.contains(query) }

    // WITH derivedStateOf: filtering only when items or query change
    val filtered by remember(items, query) {
        derivedStateOf { items.filter { it.name.contains(query) } }
    }
}
```

**CompositionLocal - Passing Data Through Tree:**
```kotlin
// Definition
val LocalTheme = compositionLocalOf { Theme.Light }

// Providing value
CompositionLocalProvider(LocalTheme provides Theme.Dark) {
    MyComposable()
}

// Reading
@Composable
fun MyComposable() {
    val theme = LocalTheme.current
}
```

**Keys for Recomposition:**
```kotlin
@Composable
fun ItemList(items: List<Item>) {
    Column {
        items.forEach { item ->
            // key helps Compose identify elements
            key(item.id) {
                ItemRow(item)
            }
        }
    }
}
```

**Compose Phases:**
1. **Composition** - building UI tree
2. **Layout** - measuring and positioning
3. **Drawing** - rendering to screen

---

## Follow-ups

- What triggers recomposition vs relayout vs redraw?
- How does Compose handle structural changes in the UI tree?
- What is the difference between compositionLocalOf and staticCompositionLocalOf?
