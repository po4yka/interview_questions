---
id: 20251006-100008
title: "What is setHasFixedSize(true) in RecyclerView? / Что такое setHasFixedSize(true) в RecyclerView?"
aliases: ["setHasFixedSize in RecyclerView", "setHasFixedSize в RecyclerView"]
topic: android
subtopics: [ui-views, performance-memory]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-what-events-are-activity-methods-tied-to--android--medium, q-handler-looper-main-thread--android--medium]
created: 2025-10-06
updated: 2025-10-27
sources: [https://github.com/amitshekhariitbhu/android-interview-questions]
tags: [android/ui-views, android/performance-memory, difficulty/easy]
---
# Вопрос (RU)

> Что такое setHasFixedSize(true) в RecyclerView?

# Question (EN)

> What is setHasFixedSize(true) in RecyclerView?

---

## Ответ (RU)

`setHasFixedSize(true)` — метод оптимизации RecyclerView, сообщающий, что **размер RecyclerView не изменится** при изменении содержимого адаптера.

### Как работает

Когда вызывается `setHasFixedSize(true)`:
- Добавление/удаление элементов не меняет размеры RecyclerView
- Пропускаются дорогостоящие пересчеты layout
- Только содержимое обновляется, иерархия представлений не пересчитывается

### Когда использовать

**✅ Используйте** когда:

```kotlin
// ✅ RecyclerView заполняет родителя
<RecyclerView
    android:layout_width="match_parent"
    android:layout_height="match_parent" />

recyclerView.setHasFixedSize(true)
```

```kotlin
// ✅ Фиксированные размеры
<RecyclerView
    android:layout_width="match_parent"
    android:layout_height="400dp" />

recyclerView.setHasFixedSize(true)
```

```kotlin
// ✅ Ограничения ConstraintLayout
<ConstraintLayout>
    <RecyclerView
        android:layout_width="0dp"
        android:layout_height="0dp"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintBottom_toBottomOf="parent" />
</ConstraintLayout>

recyclerView.setHasFixedSize(true)
```

**❌ НЕ используйте** когда:

```kotlin
// ❌ wrap_content - размер меняется
<RecyclerView
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />

recyclerView.setHasFixedSize(true) // Неправильно!
```

### Пример использования

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        binding.recyclerView.apply {
            layoutManager = LinearLayoutManager(context)
            adapter = UserAdapter()
            setHasFixedSize(true) // ✅ Оптимизация для match_parent
        }
    }
}
```

### Влияние на производительность

| Сценарий | With setHasFixedSize(true) | Without |
|----------|----------------------------|---------|
| Пересчет при add/remove | Нет | Да |
| Пересчет родителей | Нет | Да |
| Производительность | Быстро | Медленнее |
| Работает с wrap_content | Нет | Да |
| Работает с match_parent | Да | Да |

---

## Answer (EN)

`setHasFixedSize(true)` is a performance optimization method that tells RecyclerView **its size won't change** when adapter content changes.

### How It Works

When you call `setHasFixedSize(true)`:
- Adding/removing items won't trigger RecyclerView dimension changes
- Expensive layout calculations are skipped
- Only content updates, view hierarchy stays intact

### When to Use

**✅ Use** when:

```kotlin
// ✅ RecyclerView fills parent
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
// ✅ ConstraintLayout constraints
<ConstraintLayout>
    <RecyclerView
        android:layout_width="0dp"
        android:layout_height="0dp"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintBottom_toBottomOf="parent" />
</ConstraintLayout>

recyclerView.setHasFixedSize(true)
```

**❌ DON'T use** when:

```kotlin
// ❌ wrap_content - size will change
<RecyclerView
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />

recyclerView.setHasFixedSize(true) // Wrong!
```

### Usage Example

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        binding.recyclerView.apply {
            layoutManager = LinearLayoutManager(context)
            adapter = UserAdapter()
            setHasFixedSize(true) // ✅ Optimization for match_parent
        }
    }
}
```

### Performance Impact

| Scenario | With setHasFixedSize(true) | Without |
|----------|----------------------------|---------|
| Remeasure on add/remove | No | Yes |
| Parent hierarchy remeasure | No | Yes |
| Performance | Fast | Slower |
| Works with wrap_content | No | Yes |
| Works with match_parent | Yes | Yes |

### Best Practices

```kotlin
// ✅ GOOD - Combine with other optimizations
recyclerView.apply {
    setHasFixedSize(true)
    setItemViewCacheSize(20) // Increase cache
}
```

```kotlin
// ❌ BAD - Using with wrap_content
recyclerView.setHasFixedSize(true) // Inconsistent with wrap_content!
```

**Key Point:** This optimizes the RecyclerView **container size**, not adapter item count. You can still add/remove items normally.

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

### Prerequisites

- [[q-what-events-are-activity-methods-tied-to--android--medium]] - Activity lifecycle basics
- [[q-handler-looper-main-thread--android--medium]] - Main thread and performance

### Related (Same Level)

- RecyclerView adapter optimization techniques
- ViewHolder pattern and recycling mechanism
- DiffUtil for efficient list updates

### Advanced (Harder)

- [[q-macrobenchmark-startup--android--medium]] - Macrobenchmark performance testing
- [[q-app-startup-optimization--android--medium]] - App startup optimization
- [[q-baseline-profiles-optimization--android--medium]] - Baseline profiles for optimization
