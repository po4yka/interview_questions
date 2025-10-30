---
id: 20251028-120000
title: "Main Causes UI Lag / Основные причины тормозов UI"
aliases: [Main Causes UI Lag, Основные причины тормозов UI, UI Performance, UI Lag]
topic: android
subtopics: [performance-rendering, performance-memory, threads-sync]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-reduce-apk-size-techniques--android--medium, q-mvvm-pattern--android--medium, q-compose-performance-optimization--android--hard]
sources: []
created: 2025-10-15
updated: 2025-10-28
tags: [android/performance-rendering, android/performance-memory, android/threads-sync, performance, ui, threading, difficulty/medium]
date created: Tuesday, October 28th 2025, 9:36:21 pm
date modified: Thursday, October 30th 2025, 3:12:56 pm
---

# Вопрос (RU)

> Какие основные причины торможения UI в Android-приложениях?

# Question (EN)

> What are the main causes of UI lag in Android applications?

---

## Ответ (RU)

Основные причины торможения пользовательского интерфейса (UI lag/jank) в Android:

### 1. Тяжелые операции в главном потоке

**Проблема:** Долгие операции блокируют отрисовку UI.

**Примеры:** сетевые запросы, запросы к БД, файловый I/O, обработка изображений.

**Решение:** Выполнять в фоновых потоках:

```kotlin
// ❌ BAD - блокирует UI
fun loadData() {
    val data = database.getAllUsers()
    updateUI(data)
}

// ✅ GOOD - используем корутины
suspend fun loadData() {
    val data = withContext(Dispatchers.IO) {
        database.getAllUsers()
    }
    updateUI(data)
}
```

**Современные подходы:** [[c-coroutines|Kotlin Coroutines]] (рекомендовано), WorkManager, Flow.

### 2. Неоптимизированные макеты (layouts)

**Проблема:** Сложная иерархия вызывает медленный рендеринг.

**Примеры:** глубоко вложенные LinearLayout, множественные RelativeLayout.

**Решение:** Использовать плоские макеты:

```xml
<!-- ❌ BAD - глубокая вложенность (4 уровня) -->
<LinearLayout>
    <RelativeLayout>
        <LinearLayout>
            <FrameLayout>
                <TextView />
            </FrameLayout>
        </LinearLayout>
    </RelativeLayout>
</LinearLayout>

<!-- ✅ GOOD - плоская иерархия (1 уровень) -->
<ConstraintLayout>
    <TextView
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />
</ConstraintLayout>
```

**Best practices:** ConstraintLayout для сложных UI, ViewStub для условно отображаемых view, merge тег для устранения лишних ViewGroup.

### 3. Неоптимизированная работа с изображениями

**Проблема:** Загрузка больших изображений вызывает проблемы с памятью.

**Примеры:** загрузка полного разрешения для миниатюр, отсутствие кеширования.

**Решение:** Использовать библиотеки для изображений:

```kotlin
// ❌ BAD - ручная загрузка bitmap
val bitmap = BitmapFactory.decodeFile(imagePath)
imageView.setImageBitmap(bitmap)

// ✅ GOOD - Glide
Glide.with(context)
    .load(imageUrl)
    .placeholder(R.drawable.placeholder)
    .into(imageView)

// ✅ GOOD - Coil (Kotlin-first)
imageView.load(imageUrl) {
    crossfade(true)
    placeholder(R.drawable.placeholder)
}
```

**Возможности библиотек:** автоматический ресайз, memory/disk кеширование, async загрузка, lifecycle awareness.

### 4. Частые обновления UI

**Проблема:** Слишком много обновлений UI вызывают избыточный рендеринг.

**Примеры:** обновление всех элементов RecyclerView, избыточный notifyDataSetChanged().

**Решение:** Минимизировать и группировать обновления:

```kotlin
// ❌ BAD - обновляет весь список
adapter.notifyDataSetChanged()

// ✅ GOOD - обновление конкретного элемента
adapter.notifyItemChanged(position)

// ✅ BEST - использовать DiffUtil
val diffResult = DiffUtil.calculateDiff(
    MyDiffCallback(oldList, newList)
)
diffResult.dispatchUpdatesTo(adapter)
```

### 5. Неоптимизированные анимации

**Проблема:** Тяжелые анимации роняют FPS (< 60fps).

**Примеры:** анимация layout изменений, множественные одновременные анимации.

**Решение:** Использовать hardware-accelerated анимации:

```kotlin
// ❌ BAD - layout animation (медленная)
TranslateAnimation(0f, 100f, 0f, 0f).apply {
    duration = 300
    view.startAnimation(this)
}

// ✅ GOOD - ViewPropertyAnimator (hardware-accelerated)
view.animate()
    .translationX(100f)
    .setDuration(300)
    .start()

// ✅ GOOD - Jetpack Compose
AnimatedVisibility(visible = isVisible) {
    Text("Hello")
}
```

### Дополнительные причины

**6. Проблемы с памятью:** Низкая память вызывает GC паузы. Решение: исправить memory leaks (LeakCanary), уменьшить аллокации объектов.

**7. Overdraw:** Отрисовка пикселей несколько раз. Решение: удалить лишние background, использовать "Debug GPU overdraw" в Developer Options.

**8. Медленные Custom Views:** Неэффективный onDraw(). Решение: избегать аллокаций в onDraw(), кешировать Paint объекты.

---

## Answer (EN)

The main causes of **UI lag** (janky user interface) in Android applications:

### 1. Heavy Operations on Main Thread

**Problem:** Long-running operations block UI rendering.

**Examples:** network requests, database queries, file I/O, image processing.

**Solution:** Execute in background threads:

```kotlin
// ❌ BAD - blocks UI thread
fun loadData() {
    val data = database.getAllUsers()
    updateUI(data)
}

// ✅ GOOD - using Coroutines
suspend fun loadData() {
    val data = withContext(Dispatchers.IO) {
        database.getAllUsers()
    }
    updateUI(data)
}
```

**Modern approaches:** Kotlin Coroutines (recommended), WorkManager, Flow.

### 2. Unoptimized Layouts

**Problem:** Complex view hierarchies cause slow rendering.

**Examples:** deeply nested LinearLayouts, multiple RelativeLayouts.

**Solution:** Use simpler, flatter layouts:

```xml
<!-- ❌ BAD - deeply nested (4 levels) -->
<LinearLayout>
    <RelativeLayout>
        <LinearLayout>
            <FrameLayout>
                <TextView />
            </FrameLayout>
        </LinearLayout>
    </RelativeLayout>
</LinearLayout>

<!-- ✅ GOOD - flat hierarchy (1 level) -->
<ConstraintLayout>
    <TextView
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />
</ConstraintLayout>
```

**Best practices:** ConstraintLayout to reduce nesting, ViewStub for conditionally displayed views, merge tag to eliminate unnecessary ViewGroups.

### 3. Unoptimized Image Handling

**Problem:** Loading large images causes memory issues and lag.

**Examples:** loading full-resolution images for thumbnails, no caching.

**Solution:** Use image loading libraries:

```kotlin
// ❌ BAD - manual bitmap loading
val bitmap = BitmapFactory.decodeFile(imagePath)
imageView.setImageBitmap(bitmap)

// ✅ GOOD - using Glide
Glide.with(context)
    .load(imageUrl)
    .placeholder(R.drawable.placeholder)
    .into(imageView)

// ✅ GOOD - using Coil (Kotlin-first)
imageView.load(imageUrl) {
    crossfade(true)
    placeholder(R.drawable.placeholder)
}
```

**Library features:** automatic resizing, memory/disk caching, async loading, lifecycle awareness.

### 4. Frequent UI Updates

**Problem:** Too many UI updates cause excessive rendering.

**Examples:** updating every item in RecyclerView, excessive notifyDataSetChanged().

**Solution:** Minimize and batch UI updates:

```kotlin
// ❌ BAD - updates entire list
adapter.notifyDataSetChanged()

// ✅ GOOD - update specific item
adapter.notifyItemChanged(position)

// ✅ BEST - use DiffUtil
val diffResult = DiffUtil.calculateDiff(
    MyDiffCallback(oldList, newList)
)
diffResult.dispatchUpdatesTo(adapter)
```

### 5. Unoptimized Animations

**Problem:** Heavy animations drop frames (< 60fps).

**Examples:** animating layout changes, too many simultaneous animations.

**Solution:** Use hardware-accelerated animations:

```kotlin
// ❌ BAD - layout animation (slow)
TranslateAnimation(0f, 100f, 0f, 0f).apply {
    duration = 300
    view.startAnimation(this)
}

// ✅ GOOD - ViewPropertyAnimator (hardware-accelerated)
view.animate()
    .translationX(100f)
    .setDuration(300)
    .start()

// ✅ GOOD - Jetpack Compose animations
AnimatedVisibility(visible = isVisible) {
    Text("Hello")
}
```

### Additional Causes

**6. Memory Issues:** Low memory causes GC pauses. Solution: fix memory leaks (use LeakCanary), reduce object allocations.

**7. Overdraw:** Drawing pixels multiple times wastes GPU. Solution: remove unnecessary backgrounds, use "Debug GPU overdraw" in Developer Options.

**8. Slow Custom Views:** Inefficient onDraw(). Solution: avoid allocations in onDraw(), cache Paint objects.

---

## Follow-ups

- How to measure UI performance? (Use Systrace/Perfetto, Profile GPU Rendering, Layout Inspector, StrictMode)
- What is the 16ms frame budget for 60fps?
- How does DiffUtil calculate differences?
- What are the differences between Glide, Coil, and Picasso?
- How to detect overdraw in your app?

## References

- [Android Performance Patterns](https://www.youtube.com/playlist?list=PLWz5rJ2EKKc9CBxr3BVjPTPoDPLdPIFCE)
- [Systrace Documentation](https://developer.android.com/topic/performance/tracing)
- [ConstraintLayout Guide](https://developer.android.com/develop/ui/views/layout/constraint-layout)
- [Kotlin Coroutines Best Practices](https://developer.android.com/kotlin/coroutines/coroutines-best-practices)

## Related Questions

### Prerequisites (Easier)
- [[q-graphql-vs-rest--networking--easy]] - Networking basics

### Related (Same Level)
- [[q-reduce-apk-size-techniques--android--medium]] - Performance optimization
- [[q-mvvm-pattern--android--medium]] - Architecture patterns
- [[q-build-optimization-gradle--android--medium]] - Build performance
- [[q-compose-modifier-order-performance--android--medium]] - Compose performance

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Advanced performance optimization
