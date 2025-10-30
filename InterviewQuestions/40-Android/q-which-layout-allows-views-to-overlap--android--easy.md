---
id: 20251017-104930
title: "Which Layout Allows Views To Overlap / Какой layout позволяет View перекрываться"
aliases: ["Which Layout Allows Views To Overlap", "Какой layout позволяет View перекрываться"]
topic: android
subtopics: [ui-views, ui-compose]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-what-is-layout-types-and-when-to-use--android--easy, q-viewgroup-vs-view-differences--android--easy, q-jetpack-compose-lazy-column--android--easy]
created: 2025-10-15
updated: 2025-10-29
sources: []
tags: [android, android/ui-views, android/ui-compose, layouts, framelayout, compose, difficulty/easy]
---
# Вопрос (RU)

> Какой layout в Android позволяет View перекрываться друг с другом?

# Question (EN)

> Which layout in Android allows views to overlap each other?

---

## Ответ (RU)

В Android существует два основных способа создания макетов с наложением элементов:

### FrameLayout (Система View)

**FrameLayout** — простейший контейнер для наложения views. Дочерние элементы размещаются один поверх другого, последний добавленный отображается сверху.

**Ключевые особенности**:
- Дочерние элементы рисуются в порядке добавления
- Позиционирование через `layout_gravity` (center, top|start, bottom|end и т.д.)
- Оптимален для одного основного view с небольшими наложениями
- Z-порядок определяется очередностью добавления

**Пример: Изображение со значком**:

```xml
<FrameLayout
    android:layout_width="100dp"
    android:layout_height="100dp">

    <!-- ✅ Базовый слой -->
    <ImageView
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:src="@drawable/avatar"
        android:scaleType="centerCrop" />

    <!-- ✅ Наложенный значок -->
    <TextView
        android:layout_width="24dp"
        android:layout_height="24dp"
        android:layout_gravity="top|end"
        android:layout_margin="4dp"
        android:background="@drawable/circle_red"
        android:gravity="center"
        android:text="5"
        android:textColor="@android:color/white" />
</FrameLayout>
```

**Программное создание**:

```kotlin
val frameLayout = FrameLayout(context).apply {
    addView(ImageView(context).apply {
        layoutParams = FrameLayout.LayoutParams(MATCH_PARENT, MATCH_PARENT)
        setImageResource(R.drawable.background)
    })

    // ✅ Правильно: последний добавленный view будет сверху
    addView(TextView(context).apply {
        text = "Overlay"
        layoutParams = FrameLayout.LayoutParams(
            WRAP_CONTENT, WRAP_CONTENT, Gravity.CENTER
        )
    })
}
```

**Типичные use cases**:
- Экран загрузки поверх контента
- Значки на изображениях (notifications badge)
- Простые наложения с затемнением

---

### Box (Jetpack Compose)

**Box** — Compose-эквивалент FrameLayout с декларативным API.

**Ключевые особенности**:
- Дочерние composables накладываются в порядке объявления
- Выравнивание через `Modifier.align(Alignment.TopStart)` и т.д.
- Явный контроль z-порядка через `Modifier.zIndex()`
- Более гибкое позиционирование с `offset()`

**Пример: Badge на изображении**:

```kotlin
@Composable
fun BadgedImage(count: Int) {
    Box(modifier = Modifier.size(100.dp)) {
        // ✅ Базовый слой
        AsyncImage(
            model = imageUrl,
            contentDescription = "Profile",
            modifier = Modifier.fillMaxSize()
        )

        // ✅ Badge с правильным z-index
        if (count > 0) {
            Box(
                modifier = Modifier
                    .size(24.dp)
                    .align(Alignment.TopEnd)
                    .offset(x = (-4).dp, y = 4.dp)
                    .background(Color.Red, CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = count.toString(),
                    color = Color.White,
                    fontSize = 12.sp
                )
            }
        }
    }
}
```

**Loading overlay**:

```kotlin
@Composable
fun ContentWithLoading(isLoading: Boolean, content: @Composable () -> Unit) {
    Box(modifier = Modifier.fillMaxSize()) {
        content()

        // ✅ Правильно: блокирует взаимодействие
        if (isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(Color.Black.copy(alpha = 0.7f))
                    .clickable(enabled = false) { },  // ✅ Блокирует клики
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        }
    }
}
```

---

### Сравнение: FrameLayout vs Box

| Критерий | FrameLayout | Box |
|----------|-------------|-----|
| **Система** | View System | Jetpack Compose |
| **Определение** | XML/Kotlin | @Composable функция |
| **Выравнивание** | `layout_gravity` | `Modifier.align()` |
| **Z-контроль** | Порядок добавления | Порядок + `zIndex()` |
| **Производительность** | Базовая отрисовка | Recomposition overhead |

---

**Резюме**:
- **FrameLayout** — для View System, простое наложение views
- **Box** — для Compose, декларативное наложение composables
- Оба используют принцип "последний сверху" по умолчанию
- Box предоставляет более гибкий контроль через модификаторы

---

## Answer (EN)

In Android, there are two main approaches for creating layouts where UI elements can overlap:

### FrameLayout (View System)

**FrameLayout** is the simplest container for overlaying views. Child views are stacked on top of each other, with the last added view drawn on top.

**Key characteristics**:
- Children are drawn in the order they're added
- Positioning via `layout_gravity` (center, top|start, bottom|end, etc.)
- Optimal for one primary view with small overlays
- Z-order determined by addition sequence

**Example: Image with badge**:

```xml
<FrameLayout
    android:layout_width="100dp"
    android:layout_height="100dp">

    <!-- ✅ Base layer -->
    <ImageView
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:src="@drawable/avatar"
        android:scaleType="centerCrop" />

    <!-- ✅ Overlay badge -->
    <TextView
        android:layout_width="24dp"
        android:layout_height="24dp"
        android:layout_gravity="top|end"
        android:layout_margin="4dp"
        android:background="@drawable/circle_red"
        android:gravity="center"
        android:text="5"
        android:textColor="@android:color/white" />
</FrameLayout>
```

**Programmatic creation**:

```kotlin
val frameLayout = FrameLayout(context).apply {
    addView(ImageView(context).apply {
        layoutParams = FrameLayout.LayoutParams(MATCH_PARENT, MATCH_PARENT)
        setImageResource(R.drawable.background)
    })

    // ✅ Correct: last added view will be on top
    addView(TextView(context).apply {
        text = "Overlay"
        layoutParams = FrameLayout.LayoutParams(
            WRAP_CONTENT, WRAP_CONTENT, Gravity.CENTER
        )
    })
}
```

**Common use cases**:
- Loading screen over content
- Badges on images (notification badge)
- Simple overlays with dimming

---

### Box (Jetpack Compose)

**Box** is the Compose equivalent of FrameLayout with a declarative API.

**Key characteristics**:
- Child composables are stacked in declaration order
- Alignment via `Modifier.align(Alignment.TopStart)`, etc.
- Explicit z-order control via `Modifier.zIndex()`
- More flexible positioning with `offset()`

**Example: Badge on image**:

```kotlin
@Composable
fun BadgedImage(count: Int) {
    Box(modifier = Modifier.size(100.dp)) {
        // ✅ Base layer
        AsyncImage(
            model = imageUrl,
            contentDescription = "Profile",
            modifier = Modifier.fillMaxSize()
        )

        // ✅ Badge with proper z-index
        if (count > 0) {
            Box(
                modifier = Modifier
                    .size(24.dp)
                    .align(Alignment.TopEnd)
                    .offset(x = (-4).dp, y = 4.dp)
                    .background(Color.Red, CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = count.toString(),
                    color = Color.White,
                    fontSize = 12.sp
                )
            }
        }
    }
}
```

**Loading overlay**:

```kotlin
@Composable
fun ContentWithLoading(isLoading: Boolean, content: @Composable () -> Unit) {
    Box(modifier = Modifier.fillMaxSize()) {
        content()

        // ✅ Correct: blocks interaction
        if (isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(Color.Black.copy(alpha = 0.7f))
                    .clickable(enabled = false) { },  // ✅ Blocks clicks
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        }
    }
}
```

---

### Comparison: FrameLayout vs Box

| Criterion | FrameLayout | Box |
|-----------|-------------|-----|
| **System** | View System | Jetpack Compose |
| **Definition** | XML/Kotlin | @Composable function |
| **Alignment** | `layout_gravity` | `Modifier.align()` |
| **Z-control** | Addition order | Order + `zIndex()` |
| **Performance** | Basic rendering | Recomposition overhead |

---

**Summary**:
- **FrameLayout** — for View System, simple view overlay
- **Box** — for Compose, declarative composable overlay
- Both use "last on top" principle by default
- Box provides more flexible control via modifiers

---

## Follow-ups

- How does `ConstraintLayout` handle overlapping views with `elevation` or `translationZ`?
- What's the performance impact of deeply nested `Box` composables in Compose?
- How do `zIndex()` and drawing order interact in Compose?
- When should you use `Box` with `Modifier.offset()` vs `ConstraintLayout` for complex positioning?
- How do you prevent click events from propagating through overlays in both View System and Compose?

---

## References

- [[q-what-is-layout-types-and-when-to-use--android--easy]] — Overview of Android layout types
- [[q-viewgroup-vs-view-differences--android--easy]] — View hierarchy fundamentals
- [Android Layouts Documentation](https://developer.android.com/develop/ui/views/layout/declaring-layout)
- [Jetpack Compose Layout Documentation](https://developer.android.com/jetpack/compose/layouts/basics)

---

## Related Questions

### Prerequisites
- [[q-viewgroup-vs-view-differences--android--easy]] — Understanding View hierarchy
- [[q-what-is-layout-types-and-when-to-use--android--easy]] — Layout types overview

### Related
- [[q-which-layout-for-large-list--android--easy]] — RecyclerView for lists
- [[q-jetpack-compose-lazy-column--android--easy]] — LazyColumn in Compose

### Advanced
- More complex positioning with ConstraintLayout
- Custom ViewGroup for advanced overlay logic
- Compose layout performance optimization
