---
id: android-202
title: "What Do You Know About Modifiers / Что вы знаете о модификаторах"
aliases: ["Compose Modifiers", "Модификаторы Compose"]
topic: android
subtopics: [ui-compose, ui-state]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-webp-image-format-android--android--easy, q-how-to-create-list-like-recyclerview-in-compose--android--medium, q-dagger-framework-overview--android--hard]
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [android, android/ui-compose, android/ui-state, difficulty/medium]
---
# Вопрос (RU)

> Что вы знаете о модификаторах в Jetpack Compose?

# Question (EN)

> What do you know about Modifiers in Jetpack Compose?

---

## Ответ (RU)

**Modifiers** в Jetpack Compose — это мощная система для декорирования и изменения поведения composable-функций. Они позволяют настраивать размеры, внешний вид, поведение и позиционирование UI-элементов.

### 1. Основные возможности Modifiers

Модификаторы позволяют:
- Изменять размер, форму, фон
- Добавлять отступы, границы, тени
- Реагировать на жесты (клики, прокрутка, drag)
- Применять трансформации и анимации
- Управлять компоновкой элементов

### 2. Порядок модификаторов имеет значение

Порядок применения модификаторов критически важен для результата.

```kotlin
@Composable
fun ModifierOrderExample() {
    Column {
        // ✅ Отступ ПЕРЕД фоном — фон включает отступ
        Text(
            text = "Padding First",
            modifier = Modifier
                .padding(16.dp)
                .background(Color.Blue)
        )

        // ❌ Фон ПЕРЕД отступом — фон не включает отступ
        Text(
            text = "Background First",
            modifier = Modifier
                .background(Color.Blue)
                .padding(16.dp)
        )
    }
}
```

### 3. Основные категории модификаторов

#### Размеры

```kotlin
Box(
    modifier = Modifier
        .size(100.dp)                    // Фиксированный размер
        .fillMaxWidth()                  // Заполнить ширину
        .fillMaxHeight(0.5f)             // 50% высоты
        .aspectRatio(16f / 9f)           // Соотношение сторон
)
```

#### Отступы и границы

```kotlin
Box(
    modifier = Modifier
        .padding(16.dp)                  // Все стороны
        .padding(horizontal = 16.dp, vertical = 8.dp)
        .border(2.dp, Color.Black, RoundedCornerShape(8.dp))
)
```

#### Клики и взаимодействие

```kotlin
var count by remember { mutableIntStateOf(0) }

Text(
    text = "Click: $count",
    modifier = Modifier
        .clickable { count++ }           // ✅ Простой клик
        .combinedClickable(              // ✅ Клик + долгое нажатие
            onClick = { count++ },
            onLongClick = { count += 10 }
        )
)
```

#### Прокрутка

```kotlin
Column(
    modifier = Modifier
        .height(200.dp)
        .verticalScroll(rememberScrollState())  // ✅ Вертикальная прокрутка
) {
    repeat(20) {
        Text("Item $it")
    }
}
```

### 4. Создание собственных модификаторов

```kotlin
// ✅ Extension-функция для переиспользования
fun Modifier.customCard() = this
    .fillMaxWidth()
    .padding(16.dp)
    .shadow(4.dp, RoundedCornerShape(8.dp))
    .background(Color.White, RoundedCornerShape(8.dp))
    .padding(16.dp)

// ✅ Модификатор с параметрами
fun Modifier.dashedBorder(
    color: Color = Color.Black,
    width: Dp = 1.dp
) = this.drawBehind {
    val pathEffect = PathEffect.dashPathEffect(floatArrayOf(10f, 10f), 0f)
    drawRoundRect(
        color = color,
        style = Stroke(width = width.toPx(), pathEffect = pathEffect)
    )
}
```

### 5. Условные модификаторы

```kotlin
var isSelected by remember { mutableStateOf(false) }

// ✅ Использование .then() для условной логики
Text(
    text = "Toggle",
    modifier = Modifier
        .padding(16.dp)
        .then(
            if (isSelected) {
                Modifier.background(Color.Blue, RoundedCornerShape(8.dp))
            } else {
                Modifier.border(1.dp, Color.Gray, RoundedCornerShape(8.dp))
            }
        )
        .clickable { isSelected = !isSelected }
)
```

### 6. Трансформации и анимации

```kotlin
var expanded by remember { mutableStateOf(false) }

Box(
    modifier = Modifier
        .animateContentSize()            // ✅ Плавное изменение размера
        .height(if (expanded) 200.dp else 100.dp)
        .clickable { expanded = !expanded }
)

// ✅ Графические трансформации
Text(
    text = "Transform",
    modifier = Modifier.graphicsLayer {
        rotationZ = 30f
        scaleX = 1.2f
        alpha = 0.8f
    }
)
```

### Лучшие практики

1. **Порядок важен** — применяйте модификаторы в логическом порядке
2. **Переиспользуйте** — создавайте цепочки модификаторов для консистентности
3. **Extension-функции** — инкапсулируйте сложную логику
4. **Избегайте избыточности** — применяйте только необходимые модификаторы
5. **Используйте `composed`** — для модификаторов с состоянием

```kotlin
// ✅ Stateful modifier с composed
fun Modifier.shimmer(): Modifier = composed {
    val transition = rememberInfiniteTransition(label = "shimmer")
    val translateAnim by transition.animateFloat(
        initialValue = 0f,
        targetValue = 1000f,
        animationSpec = infiniteRepeatable(
            tween(1200, easing = FastOutSlowInEasing),
            RepeatMode.Restart
        ),
        label = "shimmer"
    )

    this.background(
        brush = Brush.linearGradient(
            colors = listOf(
                Color.LightGray.copy(alpha = 0.9f),
                Color.LightGray.copy(alpha = 0.2f),
                Color.LightGray.copy(alpha = 0.9f)
            ),
            start = Offset(translateAnim - 1000f, translateAnim - 1000f),
            end = Offset(translateAnim, translateAnim)
        )
    )
}
```

---

## Answer (EN)

**Modifiers** in Jetpack Compose are a powerful system for decorating and modifying composable functions. They allow you to customize sizes, appearance, behavior, and positioning of UI elements.

### 1. Core Modifier Capabilities

Modifiers enable you to:
- Change size, shape, background
- Add padding, borders, shadows
- Respond to gestures (clicks, scrolling, dragging)
- Apply transformations and animations
- Control element layout

### 2. Modifier Order Matters

The order in which modifiers are applied is critical to the final result.

```kotlin
@Composable
fun ModifierOrderExample() {
    Column {
        // ✅ Padding BEFORE background — background includes padding
        Text(
            text = "Padding First",
            modifier = Modifier
                .padding(16.dp)
                .background(Color.Blue)
        )

        // ❌ Background BEFORE padding — background doesn't include padding
        Text(
            text = "Background First",
            modifier = Modifier
                .background(Color.Blue)
                .padding(16.dp)
        )
    }
}
```

### 3. Main Modifier Categories

#### Sizing

```kotlin
Box(
    modifier = Modifier
        .size(100.dp)                    // Fixed size
        .fillMaxWidth()                  // Fill width
        .fillMaxHeight(0.5f)             // 50% of height
        .aspectRatio(16f / 9f)           // Aspect ratio
)
```

#### Padding and Borders

```kotlin
Box(
    modifier = Modifier
        .padding(16.dp)                  // All sides
        .padding(horizontal = 16.dp, vertical = 8.dp)
        .border(2.dp, Color.Black, RoundedCornerShape(8.dp))
)
```

#### Clicks and Interaction

```kotlin
var count by remember { mutableIntStateOf(0) }

Text(
    text = "Click: $count",
    modifier = Modifier
        .clickable { count++ }           // ✅ Simple click
        .combinedClickable(              // ✅ Click + long press
            onClick = { count++ },
            onLongClick = { count += 10 }
        )
)
```

#### Scrolling

```kotlin
Column(
    modifier = Modifier
        .height(200.dp)
        .verticalScroll(rememberScrollState())  // ✅ Vertical scroll
) {
    repeat(20) {
        Text("Item $it")
    }
}
```

### 4. Creating Custom Modifiers

```kotlin
// ✅ Extension function for reusability
fun Modifier.customCard() = this
    .fillMaxWidth()
    .padding(16.dp)
    .shadow(4.dp, RoundedCornerShape(8.dp))
    .background(Color.White, RoundedCornerShape(8.dp))
    .padding(16.dp)

// ✅ Modifier with parameters
fun Modifier.dashedBorder(
    color: Color = Color.Black,
    width: Dp = 1.dp
) = this.drawBehind {
    val pathEffect = PathEffect.dashPathEffect(floatArrayOf(10f, 10f), 0f)
    drawRoundRect(
        color = color,
        style = Stroke(width = width.toPx(), pathEffect = pathEffect)
    )
}
```

### 5. Conditional Modifiers

```kotlin
var isSelected by remember { mutableStateOf(false) }

// ✅ Using .then() for conditional logic
Text(
    text = "Toggle",
    modifier = Modifier
        .padding(16.dp)
        .then(
            if (isSelected) {
                Modifier.background(Color.Blue, RoundedCornerShape(8.dp))
            } else {
                Modifier.border(1.dp, Color.Gray, RoundedCornerShape(8.dp))
            }
        )
        .clickable { isSelected = !isSelected }
)
```

### 6. Transformations and Animations

```kotlin
var expanded by remember { mutableStateOf(false) }

Box(
    modifier = Modifier
        .animateContentSize()            // ✅ Smooth size change
        .height(if (expanded) 200.dp else 100.dp)
        .clickable { expanded = !expanded }
)

// ✅ Graphics transformations
Text(
    text = "Transform",
    modifier = Modifier.graphicsLayer {
        rotationZ = 30f
        scaleX = 1.2f
        alpha = 0.8f
    }
)
```

### Best Practices

1. **Order matters** — apply modifiers in logical sequence
2. **Reuse** — create modifier chains for consistency
3. **Extension functions** — encapsulate complex logic
4. **Avoid redundancy** — apply only necessary modifiers
5. **Use `composed`** — for stateful modifiers

```kotlin
// ✅ Stateful modifier with composed
fun Modifier.shimmer(): Modifier = composed {
    val transition = rememberInfiniteTransition(label = "shimmer")
    val translateAnim by transition.animateFloat(
        initialValue = 0f,
        targetValue = 1000f,
        animationSpec = infiniteRepeatable(
            tween(1200, easing = FastOutSlowInEasing),
            RepeatMode.Restart
        ),
        label = "shimmer"
    )

    this.background(
        brush = Brush.linearGradient(
            colors = listOf(
                Color.LightGray.copy(alpha = 0.9f),
                Color.LightGray.copy(alpha = 0.2f),
                Color.LightGray.copy(alpha = 0.9f)
            ),
            start = Offset(translateAnim - 1000f, translateAnim - 1000f),
            end = Offset(translateAnim, translateAnim)
        )
    )
}
```

---

## Follow-ups

- How does `Modifier.composed` differ from regular extension functions?
- What's the performance impact of deeply nested modifiers?
- How do you test custom modifiers?
- When should you use `graphicsLayer` vs separate transformation modifiers?
- How do modifiers interact with `remember` and recomposition scope?

## References

- [[c-jetpack-compose]]
- [[c-compose-recomposition]]
- [Compose Modifiers Official Docs](https://developer.android.com/jetpack/compose/modifiers)
- [Compose API Guidelines](https://github.com/androidx/androidx/blob/androidx-main/compose/docs/compose-api-guidelines.md)

## Related Questions

### Prerequisites
- [[q-jetpack-compose-basics--android--easy]]
- [[q-compose-state-management--android--medium]]

### Related
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]]
- [[q-compose-layout-system--android--medium]]

### Advanced
- [[q-compose-performance-optimization--android--hard]]
- [[q-custom-layout-in-compose--android--hard]]
