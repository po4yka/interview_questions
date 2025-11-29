---
id: android-027
title: What is setHasFixedSize(true) in RecyclerView? / Что такое setHasFixedSize(true) в RecyclerView?
aliases: [setHasFixedSize in RecyclerView, setHasFixedSize в RecyclerView]
topic: android
subtopics:
  - performance-memory
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
  - c-memory-management
  - q-handler-looper-main-thread--android--medium
  - q-how-to-change-number-of-columns-in-recyclerview-based-on-orientation--android--easy
  - q-how-to-change-the-number-of-columns-in-recyclerview-depending-on-orientation--android--easy
  - q-recyclerview-itemdecoration-advanced--android--medium
  - q-what-events-are-activity-methods-tied-to--android--medium
created: 2025-10-06
updated: 2025-11-10
sources:
  - "https://github.com/amitshekhariitbhu/android-interview-questions"
tags: [android/performance-memory, android/ui-views, difficulty/easy]

date created: Saturday, November 1st 2025, 12:47:02 pm
date modified: Tuesday, November 25th 2025, 8:53:57 pm
---
# Вопрос (RU)

> Что такое setHasFixedSize(true) в RecyclerView?

# Question (EN)

> What is setHasFixedSize(true) in RecyclerView?

---

## Ответ (RU)

`setHasFixedSize(true)` — метод оптимизации RecyclerView, сообщающий, что **размер самого RecyclerView (ширина/высота) не должен меняться** при изменении данных адаптера.

Это позволяет RecyclerView не запрашивать лишние пересчёты своего размера у родителя при notify* вызовах, если изменения не влияют на габариты контейнера.

### Как Работает

Когда вызывается `setHasFixedSize(true)`:
- RecyclerView считает свой размер фиксированным относительно родителя.
- При изменении элементов (insert/remove/update), если предполагается, что это не меняет общий размер контейнера, RecyclerView может избегать повторных `requestLayout()` для себя/родителя.
- Пересчёт выполняется только для затронутых `itemView` и их размещения внутри уже заданной области; иерархия родителей не прогоняется лишний раз.

Важно: это не гарантирует полного отсутствия layout-проходов — дочерние элементы всё равно могут измеряться и раскладываться. Оптимизация касается именно стабильности размеров контейнера.

### Когда Использовать

**✅ Используйте, когда размер RecyclerView логически фиксирован:**

```kotlin
// ✅ RecyclerView заполняет родителя, размер задаётся внешним layout'ом
<RecyclerView
    android:layout_width="match_parent"
    android:layout_height="match_parent" />

recyclerView.setHasFixedSize(true)
```

```kotlin
// ✅ Фиксированная высота/ширина
<RecyclerView
    android:layout_width="match_parent"
    android:layout_height="400dp" />

recyclerView.setHasFixedSize(true)
```

```kotlin
// ✅ ConstraintLayout с жёсткими ограничениями — размер зависит от constraint'ов, а не от данных списка
<ConstraintLayout>
    <RecyclerView
        android:layout_width="0dp"
        android:layout_height="0dp"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintBottom_toBottomOf="parent" />
</ConstraintLayout>

recyclerView.setHasFixedSize(true)
```

**⚠️ Осторожно / обычно НЕ используйте**, когда:

```kotlin
// ⚠️ wrap_content — размер контейнера зависит от количества/размера элементов
<RecyclerView
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />

recyclerView.setHasFixedSize(true) // Противоречит контракту: размер НЕ фиксирован.
```

Технически код не упадёт, но вы даёте RecyclerView ложное обещание, что может привести к некорректному UI (например, контейнер не перерастёт при добавлении элементов).

### Пример Использования

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        binding.recyclerView.apply {
            layoutManager = LinearLayoutManager(context)
            adapter = UserAdapter()
            setHasFixedSize(true) // ✅ Оптимизация: размер задаётся родителем и не зависит от данных
        }
    }
}
```

### Влияние На Производительность

| Сценарий | With setHasFixedSize(true) | Without |
|----------|----------------------------|---------|
| Поведение при add/remove | Не инициирует перерасчёт размеров контейнера, если он считается фиксированным | Может запрашивать перерасчёт размеров контейнера |
| Пересчёт родителей | Сокращается, если размер RecyclerView стабилен | Возможен пересчёт родительской иерархии |
| Производительность | Потенциально быстрее за счёт уменьшения числа requestLayout для контейнера | Потенциально медленнее при частых изменениях |
| Использование с wrap_content | Не рекомендуется: может привести к неверному layout'у | Корректно, размеры пересчитываются |
| Использование с match_parent/фикс. размером | Рекомендуется | Работает, но без оптимизации |

### Рекомендуемые Практики

```kotlin
// ✅ ХОРОШО — комбинируйте с другими оптимизациями, когда размер контейнера стабилен
recyclerView.apply {
    setHasFixedSize(true)
    setItemViewCacheSize(20) // Пример: настройка кеша по необходимости
}
```

```kotlin
// ⚠️ ПЛОХО — использование с wrap_content при динамическом размере контента
recyclerView.setHasFixedSize(true) // Нарушает предположение о "фиксированном" размере.
```

Ключевой момент: `setHasFixedSize(true)` относится к стабильности РАЗМЕРА КОНТЕЙНЕРА RecyclerView, а не к ограничению изменений количества элементов. Вы по-прежнему можете свободно добавлять/удалять/обновлять элементы; вы лишь обещаете, что это не требует изменения измеренной ширины/высоты самого RecyclerView.

---

## Answer (EN)

`setHasFixedSize(true)` is a RecyclerView performance optimization hint that tells it **the RecyclerView's own width/height are not expected to change** when the adapter data changes.

This allows RecyclerView to avoid unnecessary size remeasure/layout requests to its parent on notify* calls when changes are not supposed to affect the container bounds.

### How It Works

When you call `setHasFixedSize(true)`:
- RecyclerView treats its overall size as stable with respect to its parent.
- On item insert/remove/update, if the container size is logically independent from item count/size, RecyclerView can skip extra `requestLayout()` for itself/parent.
- It still measures and lays out affected child views, but avoids re-running full parent hierarchy layout for every data change when not needed.

Important: this does NOT eliminate all layout passes. It only optimizes how aggressively RecyclerView asks to re-measure itself and its parents.

### When to Use

**✅ Use when the RecyclerView size is logically fixed:**

```kotlin
// ✅ RecyclerView fills parent; size is controlled by parent, not by data
<RecyclerView
    android:layout_width="match_parent"
    android:layout_height="match_parent" />

recyclerView.setHasFixedSize(true)
```

```kotlin
// ✅ Fixed dimensions
<RecyclerView
    android:layout_width="match_parent"
    android:layout_height="400dp" />

recyclerView.setHasFixedSize(true)
```

```kotlin
// ✅ ConstraintLayout constraints define a fixed area; data shouldn't change its bounds
<ConstraintLayout>
    <RecyclerView
        android:layout_width="0dp"
        android:layout_height="0dp"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintBottom_toBottomOf="parent" />
</ConstraintLayout>

recyclerView.setHasFixedSize(true)
```

**⚠️ Be careful / generally DON'T use** when:

```kotlin
// ⚠️ wrap_content - container size depends on item count/size
<RecyclerView
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />

recyclerView.setHasFixedSize(true) // Misleading hint: size is not actually fixed.
```

Technically this compiles and runs, but you are giving RecyclerView a wrong contract, which can cause incorrect layout (e.g., the view not expanding when items are added).

### Usage Example

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        binding.recyclerView.apply {
            layoutManager = LinearLayoutManager(context)
            adapter = UserAdapter()
            setHasFixedSize(true) // ✅ Optimization: size is driven by parent, not data
        }
    }
}
```

### Performance Impact

| Scenario | With setHasFixedSize(true) | Without |
|----------|----------------------------|---------|
| Remeasure on add/remove | Avoids triggering container size remeasure when size is fixed | May trigger container/parent remeasure when data changes |
| Parent hierarchy remeasure | Reduced in stable-size scenarios | More frequent in dynamic-size scenarios |
| Performance | Potentially faster due to fewer unnecessary requestLayout calls | Potentially slower on frequent updates |
| Use with wrap_content | Not recommended; may cause incorrect layout behavior | Recommended when size must follow content |
| Use with match_parent/fixed size | Recommended | Works but without this optimization |

### Best Practices

```kotlin
// ✅ GOOD - Combine with other optimizations when size is stable
recyclerView.apply {
    setHasFixedSize(true)
    setItemViewCacheSize(20) // Example: tune cache as needed
}
```

```kotlin
// ⚠️ BAD - Using with wrap_content when content size is dynamic
recyclerView.setHasFixedSize(true) // Violates the "fixed size" assumption.
```

Key Point: `setHasFixedSize(true)` is about the stability of the RecyclerView CONTAINER size, not about preventing item count changes. You can still freely add/remove/update items; you just promise that doing so should not require the RecyclerView itself to change its measured width/height.

---

## Follow-ups

- What other RecyclerView optimizations can be combined with `setHasFixedSize(true)`?
- How does `setHasFixedSize()` interact with `DiffUtil` and `ListAdapter`?
- What performance metrics should be measured to validate the optimization impact?
- When should you use `setItemViewCacheSize()` vs `RecycledViewPool`?

## References

- https://developer.android.com/reference/androidx/recyclerview/widget/RecyclerView#setHasFixedSize(boolean)
- https://developer.android.com/topic/performance/rendering/recyclerview

## Related Questions

### Prerequisites / Concepts

- [[c-memory-management]]

### Prerequisites

- [[q-what-events-are-activity-methods-tied-to--android--medium]] - `Activity` lifecycle basics
- [[q-handler-looper-main-thread--android--medium]] - Main thread and performance

### Related (Same Level)

- RecyclerView adapter optimization techniques
- ViewHolder pattern and recycling mechanism
- DiffUtil for efficient list updates

### Advanced (Harder)

- [[q-macrobenchmark-startup--android--medium]] - Macrobenchmark performance testing
- [[q-app-startup-optimization--android--medium]] - App startup optimization
- [[q-baseline-profiles-optimization--android--medium]] - Baseline profiles for optimization
