---
id: android-308
title: "What Is The Layout Called Where Objects Can Overlay Each Other / Как называется layout где объекты могут перекрывать друг друга"
aliases: ["Layout для наложения элементов", "Overlay Layout"]
topic: android
subtopics: [ui-compose, ui-views]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android-ui-composition, q-what-is-known-about-methods-that-redraw-view--android--medium]
sources: []
created: 2025-10-15
updated: 2025-11-10
tags: [android/ui-compose, android/ui-views, box, difficulty/easy, framelayout, layouts]
date created: Saturday, November 1st 2025, 1:25:40 pm
date modified: Tuesday, November 25th 2025, 8:53:55 pm
---

# Вопрос (RU)

> Как называется layout, в котором UI-элементы могут наслаиваться друг на друга?

# Question (EN)

> What is the layout called where UI elements can overlay each other?

## Ответ (RU)

В Android наиболее часто для наложения элементов используются два контейнера:

**FrameLayout** (`View` System) — традиционный контейнер, где дочерние элементы накладываются друг на друга в порядке добавления. Последний добавленный элемент рисуется сверху (также на порядок влияет `elevation`/`translationZ` для L+).

**Box** (Jetpack Compose) — современный composable-контейнер с аналогичной логикой наложения.

См. также: [[c-android-ui-composition]].

### FrameLayout (`View` System)

Основное использование — простые случаи наложения: badge поверх изображения, loading overlay, FAB поверх контента.

**Пример: Overlay с позиционированием**

```xml
<FrameLayout
    android:layout_width="match_parent"
    android:layout_height="200dp">

    <!-- ✅ Базовый слой -->
    <View
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:background="@color/blue" />

    <!-- ✅ layout_gravity для позиционирования -->
    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="center"
        android:text="Center Text" />
</FrameLayout>
```

**Пример: Badge поверх аватара**

```kotlin
// ✅ Программное создание FrameLayout
val sizeInPx = (100 * context.resources.displayMetrics.density).toInt()
val badgeSizeInPx = (24 * context.resources.displayMetrics.density).toInt()

val container = FrameLayout(context).apply {
    layoutParams = FrameLayout.LayoutParams(sizeInPx, sizeInPx)
}

val avatar = ImageView(context).apply {
    setImageResource(R.drawable.avatar)
    scaleType = ImageView.ScaleType.CENTER_CROP
}

val badge = TextView(context).apply {
    text = "5"
    setBackgroundResource(R.drawable.circle_red)
    layoutParams = FrameLayout.LayoutParams(
        badgeSizeInPx,
        badgeSizeInPx,
        Gravity.TOP or Gravity.END
    )
}

container.addView(avatar)
container.addView(badge)  // Добавляется последним = рисуется сверху
```

**Типичные паттерны:**
- Loading overlay — полупрозрачный слой с ProgressBar
- Badge notifications — индикатор поверх иконки
- Floating Action Button — кнопка поверх списка

### Box (Jetpack Compose)

Декларативный эквивалент FrameLayout. Позиционирование через `Modifier.align()`, контроль z-order через `zIndex()` или порядок добавления.

**Пример: Базовое наложение**

```kotlin
@Composable
fun OverlayExample() {
    Box(modifier = Modifier.fillMaxWidth().height(200.dp)) {
        // ✅ Фоновый слой
        Image(
            painter = painterResource(R.drawable.background),
            contentDescription = null,
            modifier = Modifier.fillMaxSize()
        )

        // ✅ Полупрозрачный overlay
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.Black.copy(alpha = 0.5f))
        )

        // ✅ Текст по центру
        Text(
            text = "Overlay Text",
            color = Color.White,
            modifier = Modifier.align(Alignment.Center)
        )
    }
}
```

**Пример: Loading overlay с блокировкой interaction**

```kotlin
@Composable
fun ScreenWithLoading(isLoading: Boolean, content: @Composable () -> Unit) {
    Box(modifier = Modifier.fillMaxSize()) {
        content()

        if (isLoading) {
            // ✅ Overlay перекрывает контент и перехватывает клики
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(Color.Black.copy(alpha = 0.8f))
                    .clickable(
                        indication = null,
                        interactionSource = remember { MutableInteractionSource() }
                    ) {
                        // Пустой onClick: перехватываем события, не пробрасывая вниз
                    },
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        }
    }
}
```

**Преимущества Box:**
- `zIndex()` для явного управления порядком слоёв
- Лямбда-based API для условного отображения
- Интеграция с Modifier chain для гибкости

### Сравнение

| Характеристика | FrameLayout | Box (Compose) |
|----------------|-------------|---------------|
| Система | `View` System | Jetpack Compose |
| Порядок слоёв | Последний сверху (и `elevation`/`translationZ` на L+) | Последний сверху |
| Позиционирование | `layout_gravity` | `Modifier.align()` |
| Z-ordering | Порядок добавления + `elevation`/`translationZ` | `zIndex()` + порядок |

**Выбор:**
- FrameLayout — для legacy `View`-based UI
- Box — для новых Compose UI

## Answer (EN)

In Android, the most commonly used containers for overlaying elements are:

**FrameLayout** (`View` System) — traditional container where children stack in the order they're added. The last child is drawn on top (on L+ `elevation`/`translationZ` also affect drawing order).

**Box** (Jetpack Compose) — modern composable container with similar layering behavior.

See also: [[c-android-ui-composition]].

### FrameLayout (`View` System)

Typical use cases: simple overlays such as badges over images, loading overlays, FABs over content.

**Example: Positioned Overlay**

```xml
<FrameLayout
    android:layout_width="match_parent"
    android:layout_height="200dp">

    <!-- ✅ Base layer -->
    <View
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:background="@color/blue" />

    <!-- ✅ layout_gravity for positioning -->
    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="center"
        android:text="Center Text" />
</FrameLayout>
```

**Example: Badge Over Avatar**

```kotlin
// ✅ Programmatic FrameLayout
val sizeInPx = (100 * context.resources.displayMetrics.density).toInt()
val badgeSizeInPx = (24 * context.resources.displayMetrics.density).toInt()

val container = FrameLayout(context).apply {
    layoutParams = FrameLayout.LayoutParams(sizeInPx, sizeInPx)
}

val avatar = ImageView(context).apply {
    setImageResource(R.drawable.avatar)
    scaleType = ImageView.ScaleType.CENTER_CROP
}

val badge = TextView(context).apply {
    text = "5"
    setBackgroundResource(R.drawable.circle_red)
    layoutParams = FrameLayout.LayoutParams(
        badgeSizeInPx,
        badgeSizeInPx,
        Gravity.TOP or Gravity.END
    )
}

container.addView(avatar)
container.addView(badge)  // Added last = draws on top
```

**Common Patterns:**
- Loading overlay — semi-transparent layer with ProgressBar
- Badge notifications — indicator over icon
- Floating Action Button — button over list

### Box (Jetpack Compose)

Declarative equivalent of FrameLayout. Positioning via `Modifier.align()`, z-order control via `zIndex()` or add order.

**Example: Basic Overlay**

```kotlin
@Composable
fun OverlayExample() {
    Box(modifier = Modifier.fillMaxWidth().height(200.dp)) {
        // ✅ Background layer
        Image(
            painter = painterResource(R.drawable.background),
            contentDescription = null,
            modifier = Modifier.fillMaxSize()
        )

        // ✅ Semi-transparent overlay
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.Black.copy(alpha = 0.5f))
        )

        // ✅ Centered text
        Text(
            text = "Overlay Text",
            color = Color.White,
            modifier = Modifier.align(Alignment.Center)
        )
    }
}
```

**Example: Loading Overlay with Interaction Blocking**

```kotlin
@Composable
fun ScreenWithLoading(isLoading: Boolean, content: @Composable () -> Unit) {
    Box(modifier = Modifier.fillMaxSize()) {
        content()

        if (isLoading) {
            // ✅ Overlay covers content and intercepts clicks
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(Color.Black.copy(alpha = 0.8f))
                    .clickable(
                        indication = null,
                        interactionSource = remember { MutableInteractionSource() }
                    ) {
                        // Empty onClick: consume events so they do not pass through
                    },
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        }
    }
}
```

**Box Advantages:**
- `zIndex()` for explicit layer ordering
- Lambda-based API for conditional rendering
- Modifier chain integration for flexibility

### Comparison

| Feature | FrameLayout | Box (Compose) |
|---------|-------------|---------------|
| System | `View` System | Jetpack Compose |
| Layer Order | Last on top (plus `elevation`/`translationZ` on L+) | Last on top |
| Positioning | `layout_gravity` | `Modifier.align()` |
| Z-ordering | Add order + `elevation`/`translationZ` | `zIndex()` + order |

**Choice:**
- FrameLayout — for legacy `View`-based UIs
- Box — for new Compose UIs

## Дополнительные Вопросы (RU)

1. Как управлять порядком наложения (z-index) во `FrameLayout`, не изменяя порядок добавления дочерних вью?
2. Что произойдет, если у нескольких дочерних composable в `Box` одинаковое значение `zIndex()`?
3. Как `FrameLayout` измеряет и раскладывает перекрывающиеся дочерние элементы?
4. Можно ли вкладывать несколько `FrameLayout`/`Box` для сложных слоёв, и как это влияет на производительность?
5. Как реализовать drag-and-drop перераспределение перекрывающихся элементов в обоих подходах?

## Follow-ups

1. How do you implement z-index control in FrameLayout without modifying add order?
2. What happens when Box children have the same `zIndex()` value?
3. How does FrameLayout handle measurement and layout of overlapping children?
4. Can you nest FrameLayout/Box for complex layering scenarios? What's the performance impact?
5. How do you implement drag-and-drop reordering of overlaid elements in both systems?

## Ссылки (RU)

- https://developer.android.com/reference/android/widget/FrameLayout
- https://developer.android.com/jetpack/compose/layouts/basics

## References

- https://developer.android.com/reference/android/widget/FrameLayout
- https://developer.android.com/jetpack/compose/layouts/basics

## Связанные Вопросы (RU)

### Пререквизиты (проще)
- [[q-recyclerview-sethasfixedsize--android--easy]] - основы `View`
- [[q-viewmodel-pattern--android--easy]] - основы архитектуры

### Связанные (тот Же уровень)
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - отрисовка `View`
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - layout-ы в Compose

### Продвинутые (сложнее)
- [[q-compose-custom-layout--android--hard]] - реализация кастомных layout-ов
- [[q-compose-gesture-detection--android--medium]] - обработка жестов в overlay-сценариях

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - `View` fundamentals
- [[q-viewmodel-pattern--android--easy]] - Architecture basics

### Related (Same Level)
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - `View` rendering
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - Compose layouts

### Advanced (Harder)
- [[q-compose-custom-layout--android--hard]] - Custom layout implementation
- [[q-compose-gesture-detection--android--medium]] - Gesture handling in overlays
