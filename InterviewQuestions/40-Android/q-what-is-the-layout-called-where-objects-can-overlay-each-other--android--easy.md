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
related: []
sources: []
created: 2025-10-15
updated: 2025-10-29
tags: [android/ui-compose, android/ui-views, box, difficulty/easy, framelayout, layouts]
---

# Вопрос (RU)

> Как называется layout, в котором UI-элементы могут наслаиваться друг на друга?

# Question (EN)

> What is the layout called where UI elements can overlay each other?

---

## Ответ (RU)

В Android существует два основных контейнера для наложения элементов:

**`FrameLayout`** (`View` System) — традиционный контейнер, где дочерние элементы накладываются друг на друга в порядке добавления. Последний добавленный элемент рисуется сверху.

**Box** (Jetpack Compose) — современный composable-контейнер с аналогичной логикой наложения.

### `FrameLayout` (`View` System)

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
val container = FrameLayout(context).apply {
 layoutParams = FrameLayout.LayoutParams(100.dp, 100.dp)
}

val avatar = ImageView(context).apply {
 setImageResource(R.drawable.avatar)
 scaleType = ImageView.ScaleType.CENTER_CROP
}

val badge = TextView(context).apply {
 text = "5"
 setBackgroundResource(R.drawable.circle_red)
 layoutParams = FrameLayout.LayoutParams(24.dp, 24.dp, Gravity.TOP or Gravity.END)
}

container.addView(avatar)
container.addView(badge) // Добавляется последним = рисуется сверху
```

**Типичные паттерны:**
- Loading overlay — полупрозрачный слой с ProgressBar
- Badge notifications — индикатор поверх иконки
- Floating Action `Button` — кнопка поверх списка

### Box (Jetpack Compose)

Декларативный эквивалент `FrameLayout`. Позиционирование через `Modifier.align()`, контроль z-order через `zIndex()` или порядок добавления.

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

 // ✅ Overlay блокирует клики на основной контент
 if (isLoading) {
 Box(
 modifier = Modifier
 .fillMaxSize()
 .background(Color.Black.copy(alpha = 0.8f))
 .clickable(enabled = false) {}, // Блокировка interaction
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

| Характеристика | `FrameLayout` | Box (Compose) |
|----------------|-------------|---------------|
| Система | `View` System | Jetpack Compose |
| Порядок слоёв | Последний сверху | Последний сверху |
| Позиционирование | `layout_gravity` | `Modifier.align()` |
| Z-ordering | Только порядок добавления | `zIndex()` + порядок |

**Выбор:**
- `FrameLayout` — для legacy `View`-based UI
- Box — для новых Compose UI

## Answer (EN)

Android provides two main containers for overlaying elements:

**`FrameLayout`** (`View` System) — traditional container where children stack in the order they're added. Last child draws on top.

**Box** (Jetpack Compose) — modern composable with similar layering logic.

### `FrameLayout` (`View` System)

Primary use cases: simple overlays like badges over images, loading overlays, FABs over content.

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
val container = FrameLayout(context).apply {
 layoutParams = FrameLayout.LayoutParams(100.dp, 100.dp)
}

val avatar = ImageView(context).apply {
 setImageResource(R.drawable.avatar)
 scaleType = ImageView.ScaleType.CENTER_CROP
}

val badge = TextView(context).apply {
 text = "5"
 setBackgroundResource(R.drawable.circle_red)
 layoutParams = FrameLayout.LayoutParams(24.dp, 24.dp, Gravity.TOP or Gravity.END)
}

container.addView(avatar)
container.addView(badge) // Added last = draws on top
```

**Common Patterns:**
- Loading overlay — semi-transparent layer with ProgressBar
- Badge notifications — indicator over icon
- Floating Action `Button` — button over list

### Box (Jetpack Compose)

Declarative `FrameLayout` equivalent. Positioning via `Modifier.align()`, z-order control via `zIndex()` or add order.

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

 // ✅ Overlay blocks clicks on main content
 if (isLoading) {
 Box(
 modifier = Modifier
 .fillMaxSize()
 .background(Color.Black.copy(alpha = 0.8f))
 .clickable(enabled = false) {}, // Block interactions
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

| Feature | `FrameLayout` | Box (Compose) |
|---------|-------------|---------------|
| System | `View` System | Jetpack Compose |
| Layer Order | Last on top | Last on top |
| Positioning | `layout_gravity` | `Modifier.align()` |
| Z-ordering | Add order only | `zIndex()` + order |

**Choice:**
- `FrameLayout` — for legacy `View`-based UI
- Box — for new Compose UI

---

## Follow-ups

1. How do you implement z-index control in `FrameLayout` without modifying add order?
2. What happens when Box children have the same `zIndex()` value?
3. How does `FrameLayout` handle measurement and layout of overlapping children?
4. Can you nest `FrameLayout`/Box for complex layering scenarios? What's the performance impact?
5. How do you implement drag-and-drop reordering of overlaid elements in both systems?

## References

- - `FrameLayout` deep dive
- - Box composable patterns
- https://developer.android.com/reference/android/widget/`FrameLayout`
- https://developer.android.com/jetpack/compose/layouts/basics

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
