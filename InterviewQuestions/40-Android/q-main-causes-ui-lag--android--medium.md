---
id: android-246
title: "Main Causes UI Lag / Основные причины тормозов UI"
aliases: [Main Causes UI Lag, UI Lag, UI Performance, Основные причины тормозов UI]
topic: android
subtopics: [performance-memory, performance-rendering, threads-sync]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android, q-compose-performance-optimization--android--hard, q-mvvm-pattern--android--medium, q-reduce-apk-size-techniques--android--medium]
sources: []
created: 2025-10-15
updated: 2025-10-28
tags: [android/performance-memory, android/performance-rendering, android/threads-sync, difficulty/medium, performance, threading, ui]

---
# Вопрос (RU)

> Какие основные причины торможения UI в Android-приложениях?

# Question (EN)

> What are the main causes of UI lag in Android applications?

---

## Ответ (RU)

Основные причины торможения пользовательского интерфейса (UI lag/jank) в Android:

### 1. Тяжелые Операции В Главном Потоке

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

**Современные подходы:** [[c-coroutines|Kotlin Coroutines]] (рекомендовано), WorkManager, `Flow`.

### 2. Неоптимизированные Макеты (layouts)

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

**Best practices:** ConstraintLayout для сложных UI, ViewStub для условно отображаемых view, merge тег для устранения лишних `ViewGroup`.

### 3. Неоптимизированная Работа С Изображениями

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

### 4. Частые Обновления UI

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

### 5. Неоптимизированные Анимации

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

### Дополнительные Причины

**6. Проблемы с памятью:** Низкая память вызывает GC паузы. Решение: исправить memory leaks (LeakCanary), уменьшить аллокации объектов.

**7. Overdraw:** Отрисовка пикселей несколько раз. Решение: удалить лишние background, использовать "Debug GPU overdraw" в Developer Options.

**8. Медленные Custom Views:** Неэффективный `onDraw()`. Решение: избегать аллокаций в `onDraw()`, кешировать объекты `Paint`.

---

## Answer (EN)

The main causes of **UI lag** (janky user interface) in Android applications:

### 1. Heavy Operations on Main Thread

**Problem:** `Long`-running operations block UI rendering.

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

**Modern approaches:** Kotlin Coroutines (recommended), WorkManager, `Flow`.

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

**Examples:** updating every item in RecyclerView, excessive `notifyDataSetChanged()`.

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

**8. Slow Custom Views:** Inefficient `onDraw()`. Solution: avoid allocations in `onDraw()`, cache `Paint` objects.

---

## Дополнительные Вопросы (RU)

- Как измерять производительность UI? (Systrace/Perfetto, Profile GPU Rendering, Layout Inspector, StrictMode)
- Что такое бюджет кадра 16 мс для 60fps?
- Как `DiffUtil` вычисляет различия?
- В чем различия между Glide, Coil и Picasso?
- Как обнаружить overdraw в приложении?

## Follow-ups

- How to measure UI performance? (Use Systrace/Perfetto, Profile GPU Rendering, Layout Inspector, StrictMode)
- What is the 16ms frame budget for 60fps?
- How does DiffUtil calculate differences?
- What are the differences between Glide, Coil, and Picasso?
- How to detect overdraw in your app?

## Ссылки (RU)

- Android Performance Patterns
- Документация по Systrace / Perfetto
- Руководство по ConstraintLayout
- Kotlin Coroutines Best Practices

## References

- [Android Performance Patterns](https://www.youtube.com/playlist?list=PLWz5rJ2EKKc9CBxr3BVjPTPoDPLdPIFCE)
- [Systrace Documentation](https://developer.android.com/topic/performance/tracing)
- [ConstraintLayout Guide](https://developer.android.com/develop/ui/views/layout/constraint-layout)
- [Kotlin Coroutines Best Practices](https://developer.android.com/kotlin/coroutines/coroutines-best-practices)

## Связанные Вопросы (RU)

### Базовые (проще)
- [[q-graphql-vs-rest--networking--easy]] - Основы сетевого взаимодействия

### Связанные (того Же уровня)
- [[q-reduce-apk-size-techniques--android--medium]] - Оптимизация производительности
- [[q-mvvm-pattern--android--medium]] - Архитектурные паттерны
- [[q-build-optimization-gradle--android--medium]] - Производительность сборки
- [[q-compose-modifier-order-performance--android--medium]] - Производительность Compose

### Продвинутые (сложнее)
- [[q-compose-performance-optimization--android--hard]] - Продвинутая оптимизация производительности

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
