---
id: android-298
title: Compose Modifiers / Модификаторы в Compose
aliases: [Compose Modifiers, Jetpack Compose Modifiers, Модификаторы в Compose]
topic: android
subtopics:
  - ui-compose
  - ui-state
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
sources: []
status: draft
moc: moc-android
related:
  - c-compose-state
  - c-jetpack-compose
  - c-viewmodel
  - q-api-file-upload-server--android--medium
  - q-compose-core-components--android--medium
  - q-compose-custom-animations--android--medium
  - q-how-does-jetpackcompose-work--android--medium
  - q-reduce-app-size--android--medium
  - q-where-is-composition-created-for-calling-composable-function--android--medium
created: 2025-10-15
updated: 2025-10-28
tags: [android/ui-compose, android/ui-state, compose, difficulty/medium, jetpack-compose, modifiers]
date created: Saturday, November 1st 2025, 12:47:07 pm
date modified: Tuesday, November 25th 2025, 8:53:56 pm
---
# Вопрос (RU)

> Что вы знаете о модификаторах (Modifiers) в Jetpack Compose?

# Question (EN)

> What do you know about Modifiers in Jetpack Compose?

---

## Ответ (RU)

**Modifiers (Модификаторы)** в Jetpack Compose — это система декорирования и изменения поведения UI-компонентов. Они применяются через цепочку вызовов и позволяют декларативно настраивать внешний вид, размеры, отступы, поведение и эффекты.

### Основные Категории

1. **Layout (размеры, отступы, выравнивание)**
   - `size()`, `fillMaxWidth()`, `padding()`, `aspectRatio()`, `weight()`

2. **Behavior (клики, скроллинг, жесты)**
   - `clickable()`, `verticalScroll()`, `horizontalScroll()`, `draggable()`

3. **Appearance (фон, границы, формы)**
   - `background()`, `border()`, `clip()`, `shadow()`

4. **Transformations (трансформации)**
   - `rotate()`, `scale()`, `alpha()`, `offset()`, `graphicsLayer()`

5. **Animation (анимации)**
   - `animateContentSize()`, использование с `animateFloatAsState()`

### Порядок Имеет Значение

Последовательность вызовов модификаторов влияет на финальный результат.

```kotlin
// ✅ Фон рисуется вокруг содержимого, включая padding
Text(
    "Background inside padding",
    modifier = Modifier
        .background(Color.Blue) // сначала фон
        .padding(16.dp)         // затем внутренний отступ
)

// ✅ Padding снаружи фона: фон НЕ покрывает внешний отступ
Text(
    "Background without outer padding",
    modifier = Modifier
        .padding(16.dp)         // внешний отступ
        .background(Color.Blue) // фон только внутри области после padding
)
```

### Примеры Использования

**Size & Layout:**

```kotlin
Box(
    modifier = Modifier
        .fillMaxWidth()      // занять всю ширину
        .height(200.dp)      // фиксированная высота
        .padding(16.dp)      // отступы
)

Row {
    Text("1/3", Modifier.weight(1f)) // ✅ занять 1/3 доступного места
    Text("2/3", Modifier.weight(2f)) // ✅ занять 2/3 доступного места
}
```

**Clickable & Interactions:**

```kotlin
var count by remember { mutableStateOf(0) }

Text(
    "Click: $count",
    modifier = Modifier
        .clickable { count++ }  // ✅ обработка кликов
        .padding(16.dp)
)
```

**Custom Modifiers:**

```kotlin
// Создание переиспользуемого модификатора
fun Modifier.card() = this
    .fillMaxWidth()
    .shadow(4.dp, RoundedCornerShape(8.dp))
    .background(Color.White, RoundedCornerShape(8.dp))
    .padding(16.dp)

// Использование
Text("Card content", modifier = Modifier.card())
```

**Conditional Modifiers:**

```kotlin
var isSelected by remember { mutableStateOf(false) }

Text(
    "Toggle",
    modifier = Modifier.then( // ✅ условное объединение с дополнительным Modifier
        if (isSelected)
            Modifier.background(Color.Blue)
        else
            Modifier.border(1.dp, Color.Gray)
    )
)
```

### Best Practices

1. **Порядок важен** — понимайте, как каждый модификатор влияет на размер, измерение и рисование; меняя порядок, вы меняете результат.
2. **Переиспользование** — создавайте именованные цепочки для консистентности.
3. **Extension функции** — оборачивайте сложные комбинации в переиспользуемые модификаторы.
4. **Stateful modifiers** — используйте `Modifier.composed {}` для модификаторов с состоянием или побочными эффектами.

## Answer (EN)

**Modifiers** in Jetpack Compose are a declarative system for decorating and modifying UI component behavior. They are applied via chained calls and allow configuring appearance, size, padding, behavior, and effects.

### Core Categories

1. **Layout (size, padding, alignment)**
   - `size()`, `fillMaxWidth()`, `padding()`, `aspectRatio()`, `weight()`

2. **Behavior (clicks, scrolling, gestures)**
   - `clickable()`, `verticalScroll()`, `horizontalScroll()`, `draggable()`

3. **Appearance (background, borders, shapes)**
   - `background()`, `border()`, `clip()`, `shadow()`

4. **Transformations**
   - `rotate()`, `scale()`, `alpha()`, `offset()`, `graphicsLayer()`

5. **Animation**
   - `animateContentSize()`, use with `animateFloatAsState()`

### Order Matters

The sequence of modifier calls affects the final result.

```kotlin
// ✅ Background is drawn around content including its padding
Text(
    "Background inside padding",
    modifier = Modifier
        .background(Color.Blue) // background first
        .padding(16.dp)         // then inner padding
)

// ✅ Padding outside background: background does NOT cover the outer padding area
Text(
    "Background without outer padding",
    modifier = Modifier
        .padding(16.dp)         // outer padding
        .background(Color.Blue) // background only inside the padded area
)
```

### Usage Examples

**Size & Layout:**

```kotlin
Box(
    modifier = Modifier
        .fillMaxWidth()      // fill available width
        .height(200.dp)      // fixed height
        .padding(16.dp)      // padding
)

Row {
    Text("1/3", Modifier.weight(1f)) // ✅ take 1/3 of available space
    Text("2/3", Modifier.weight(2f)) // ✅ take 2/3 of available space
}
```

**Clickable & Interactions:**

```kotlin
var count by remember { mutableStateOf(0) }

Text(
    "Click: $count",
    modifier = Modifier
        .clickable { count++ }  // ✅ handle clicks
        .padding(16.dp)
)
```

**Custom Modifiers:**

```kotlin
// Create reusable modifier
fun Modifier.card() = this
    .fillMaxWidth()
    .shadow(4.dp, RoundedCornerShape(8.dp))
    .background(Color.White, RoundedCornerShape(8.dp))
    .padding(16.dp)

// Usage
Text("Card content", modifier = Modifier.card())
```

**Conditional Modifiers:**

```kotlin
var isSelected by remember { mutableStateOf(false) }

Text(
    "Toggle",
    modifier = Modifier.then( // ✅ conditional merge with an extra Modifier
        if (isSelected)
            Modifier.background(Color.Blue)
        else
            Modifier.border(1.dp, Color.Gray)
    )
)
```

### Best Practices

1. **Order matters** — understand how each modifier affects measurement, layout, and drawing; reordering changes the outcome.
2. **Reusability** — create named chains for consistency.
3. **Extension functions** — wrap complex combinations into reusable modifiers.
4. **Stateful modifiers** — use `Modifier.composed {}` for modifiers with state or side effects.

---

## Follow-ups

- How does Modifier chaining impact performance and recomposition?
- When should you use `Modifier.composed {}` vs regular extension functions?
- How do modifiers propagate through the composition tree?
- What's the difference between `clickable()` and `pointerInput()` modifiers?
- How can you create custom layout modifiers using `layout()` or `drawBehind()`?

## References

- Official Compose Modifiers documentation: https://developer.android.com/jetpack/compose/modifiers
- Official Modifier list reference: https://developer.android.com/jetpack/compose/modifiers-list
- Custom modifiers guide: https://developer.android.com/jetpack/compose/custom-modifiers

## Related Questions

### Prerequisites / Concepts

- [[c-compose-state]]
- [[c-jetpack-compose]]
- [[c-viewmodel]]

### Prerequisites (Easier)
- Basic Compose concepts and composable functions
- Understanding of declarative UI principles

### Related (Same Level)
- [[q-where-is-composition-created-for-calling-composable-function--android--medium]] - Composition creation
- State management and recomposition in Compose
- Compose layout system and measurement

### Advanced (Harder)
- Custom layout modifiers with `layout()` and `LayoutModifier`
- Performance optimization with modifier reuse
- Advanced gesture handling with `pointerInput()`
