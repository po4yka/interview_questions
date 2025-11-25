---
id: android-304
title: Which Layout Allows Views To Overlap / Какой layout позволяет View перекрываться
aliases: [Which Layout Allows Views To Overlap, Какой layout позволяет View перекрываться]
topic: android
subtopics:
  - ui-compose
  - ui-views
question_kind: theory
difficulty: easy
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-compose-state
  - c-jetpack-compose
  - q-jetpack-compose-lazy-column--android--easy
  - q-touch-event-handling-custom-views--android--medium
  - q-viewgroup-vs-view-differences--android--easy
  - q-what-is-layout-types-and-when-to-use--android--easy
  - q-which-class-to-use-for-rendering-view-in-background-thread--android--hard
  - q-which-layout-for-large-list--android--easy
created: 2025-10-15
updated: 2025-10-30
sources: []
tags: [android, android/ui-compose, android/ui-views, compose, difficulty/easy, framelayout, layouts]
date created: Saturday, November 1st 2025, 12:47:10 pm
date modified: Tuesday, November 25th 2025, 8:53:55 pm
---

# Вопрос (RU)

> Какой layout в Android позволяет View перекрываться друг с другом?

# Question (EN)

> Which layout in Android allows views to overlap each other?

---

## Ответ (RU)

В Android существует два основных простых варианта для наложения элементов (перекрытия):

### FrameLayout (Система View)

**FrameLayout** — простейший контейнер для наложения views. Дочерние элементы размещаются один поверх другого, последний добавленный отображается сверху.

**Ключевые особенности**:
- Дочерние элементы рисуются в порядке добавления
- Позиционирование через `layout_gravity` (center, top|start, bottom|end и т.д.)
- Оптимален для одного основного view с небольшими наложениями
- Z-порядок по умолчанию определяется очередностью добавления (может быть изменён через `elevation`/`translationZ`)

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
- Значки на изображениях (notification badge)
- Простые наложения с затемнением

> Также перекрытие можно получить и в других контейнерах (например, `ConstraintLayout`, `RelativeLayout`) при соответствующей конфигурации, но для простого наложения обычно используют именно `FrameLayout`.

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
fun BadgedImage(count: Int, imageUrl: String) {
    Box(modifier = Modifier.size(100.dp)) {
        // ✅ Базовый слой
        AsyncImage(
            model = imageUrl,
            contentDescription = "Profile",
            modifier = Modifier.fillMaxSize()
        )

        // ✅ Badge с правильным порядком отрисовки / z-index
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

        // ✅ Затемнение-оверлей поверх контента
        if (isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(Color.Black.copy(alpha = 0.7f))
                    .pointerInput(Unit) {
                        // Поглощаем все события, чтобы блокировать взаимодействие под оверлеем
                        awaitPointerEventScope {
                            while (true) {
                                awaitPointerEvent()
                            }
                        }
                    },
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        }
    }
}
```

---

### Сравнение: FrameLayout Vs Box

| Критерий | FrameLayout | Box |
|----------|-------------|-----|
| **Система** | View System | Jetpack Compose |
| **Определение** | XML/Kotlin | @Composable функция |
| **Выравнивание** | `layout_gravity` | `Modifier.align()` |
| **Z-контроль** | Порядок добавления (+ `elevation`/`translationZ`) | Порядок + `zIndex()` |
| **Производительность** | Простая отрисовка | Overhead рекомпозиции |

---

**Резюме**:
- **FrameLayout** — для View System, простое наложение views
- **Box** — для Compose, декларативное наложение composables
- Оба по умолчанию используют принцип "последний сверху"
- Box предоставляет более гибкий контроль через модификаторы
- Для сложных схем позиционирования и перекрытия могут использоваться `ConstraintLayout`/другие контейнеры

---

## Answer (EN)

In Android, there are two main simple approaches for creating layouts where UI elements can overlap:

### FrameLayout (View System)

**FrameLayout** is the simplest container for overlaying views. Child views are stacked on top of each other, with the last added view drawn on top.

**Key characteristics**:
- Children are drawn in the order they're added
- Positioning via `layout_gravity` (center, top|start, bottom|end, etc.)
- Optimal for one primary view with small overlays
- Z-order by default is determined by addition sequence (can be adjusted via `elevation`/`translationZ`)

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

> Note: Overlapping can also be achieved in other containers (e.g., `ConstraintLayout`, `RelativeLayout`) with appropriate constraints/attributes, but `FrameLayout` is typically used for simple overlays.

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
fun BadgedImage(count: Int, imageUrl: String) {
    Box(modifier = Modifier.size(100.dp)) {
        // ✅ Base layer
        AsyncImage(
            model = imageUrl,
            contentDescription = "Profile",
            modifier = Modifier.fillMaxSize()
        )

        // ✅ Badge with correct drawing order / z-index
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

        // ✅ Dimmed overlay drawn above the content
        if (isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(Color.Black.copy(alpha = 0.7f))
                    .pointerInput(Unit) {
                        // Consume all pointer events to block interaction under the overlay
                        awaitPointerEventScope {
                            while (true) {
                                awaitPointerEvent()
                            }
                        }
                    },
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        }
    }
}
```

---

### Comparison: FrameLayout Vs Box

| Criterion | FrameLayout | Box |
|-----------|-------------|-----|
| **System** | View System | Jetpack Compose |
| **Definition** | XML/Kotlin | @Composable function |
| **Alignment** | `layout_gravity` | `Modifier.align()` |
| **Z-control** | Addition order (+ `elevation`/`translationZ`) | Order + `zIndex()` |
| **Performance** | Simple rendering | Recomposition overhead |

---

**Summary**:
- **FrameLayout** — for the View System, simple view overlay
- **Box** — for Compose, declarative composable overlay
- Both use "last on top" principle by default
- Box provides more flexible control via modifiers
- `ConstraintLayout` or other containers can be used for more complex overlapping/positioning scenarios

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

### Prerequisites / Concepts

- [[c-compose-state]]
- [[c-jetpack-compose]]


### Prerequisites (Easier)
- [[q-viewgroup-vs-view-differences--android--easy]] — Understanding View hierarchy
- [[q-what-is-layout-types-and-when-to-use--android--easy]] — Layout types overview
- [[q-how-to-choose-layout-for-fragment--android--easy]] — Choosing the right layout

### Related (Same Level)
- [[q-which-layout-for-large-list--android--easy]] — RecyclerView for lists
- [[q-how-to-fix-a-bad-element-layout--android--easy]] — Layout debugging

### Advanced (Harder)
- [[q-is-layoutinflater-a-singleton-and-why--android--medium]] — LayoutInflater internals
- [[q-what-is-layout-performance-measured-in--android--medium]] — Layout performance
- [[q-compose-custom-layout--android--hard]] — Custom Compose layouts
- [[q-custom-viewgroup-layout--android--hard]] — Custom ViewGroup creation
