---
id: 20251017-144927
title: "Чем Жизненный Цикл Fragment Отличается От Activity / Fragment vs Activity Lifecycle"
aliases: ["Fragment vs Activity Lifecycle", "Чем отличается жизненный цикл Fragment от Activity"]
topic: android
subtopics: [lifecycle, fragment, activity]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-how-to-write-recyclerview-cache-ahead--android--medium, q-is-layoutinflater-a-singleton-and-why--programming-languages--medium, q-privacy-sandbox-fledge--privacy--hard]
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [android/lifecycle, android/fragment, android/activity, difficulty/medium, fragments, lifecycle]
---

# Вопрос (RU)

Чем жизненный цикл Fragment отличается от жизненного цикла Activity?

# Question (EN)

How does the Fragment lifecycle differ from the Activity lifecycle?

---

## Ответ (RU)

Fragment имеет более детализированный жизненный цикл по сравнению с Activity, включая дополнительные состояния для привязки к Activity и управления View.

### Ключевые отличия

**1. Дополнительные состояния привязки**

Fragment имеет состояния `onAttach()` и `onDetach()`, которые отражают привязку к Activity:

```kotlin
class MyFragment : Fragment() {
    override fun onAttach(context: Context) {
        super.onAttach(context)
        // ✅ Fragment привязан к Activity
    }

    override fun onDetach() {
        super.onDetach()
        // ✅ Fragment отвязан от Activity
    }
}
```

**2. Отдельный жизненный цикл View**

Fragment разделяет свой собственный жизненный цикл и жизненный цикл View, что позволяет уничтожать и пересоздавать View без уничтожения самого Fragment:

```kotlin
class MyFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View = inflater.inflate(R.layout.fragment_my, container, false)

    override fun onDestroyView() {
        super.onDestroyView()
        // ✅ View уничтожен, но Fragment может быть восстановлен
    }
}
```

**3. Порядок состояний**

**Activity** (6 состояний):
```
onCreate → onStart → onResume → onPause → onStop → onDestroy
```

**Fragment** (11 состояний):
```
onAttach → onCreate → onCreateView → onViewCreated →
onStart → onResume → onPause → onStop →
onDestroyView → onDestroy → onDetach
```

**4. ViewLifecycleOwner**

Fragment предоставляет отдельный `viewLifecycleOwner` для наблюдения за данными только пока View существует:

```kotlin
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // ✅ Использовать viewLifecycleOwner вместо this
        viewModel.data.observe(viewLifecycleOwner) { data ->
            // Подписка автоматически отменится при onDestroyView
        }
    }
}
```

**5. Программный back stack**

Fragment поддерживает собственный back stack независимо от системного:

```kotlin
supportFragmentManager.beginTransaction()
    .replace(R.id.container, DetailFragment())
    .addToBackStack(null) // ✅ Добавить в back stack
    .commit()
```

### Сравнительная таблица

| Аспект | Activity | Fragment |
|--------|----------|----------|
| Количество состояний | 6 | 11 |
| View lifecycle | Совпадает с Activity | Отдельный от Fragment |
| Привязка к родителю | — | onAttach/onDetach |
| Back stack | Системный | Программный |
| Вложенность | — | Поддерживает child fragments |

---

## Answer (EN)

Fragment has a more granular lifecycle than Activity, with additional states for Activity binding and View management.

### Key Differences

**1. Additional Attachment States**

Fragment has `onAttach()` and `onDetach()` states that reflect binding to Activity:

```kotlin
class MyFragment : Fragment() {
    override fun onAttach(context: Context) {
        super.onAttach(context)
        // ✅ Fragment attached to Activity
    }

    override fun onDetach() {
        super.onDetach()
        // ✅ Fragment detached from Activity
    }
}
```

**2. Separate View Lifecycle**

Fragment separates its own lifecycle from its View lifecycle, allowing View destruction and recreation without destroying the Fragment itself:

```kotlin
class MyFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View = inflater.inflate(R.layout.fragment_my, container, false)

    override fun onDestroyView() {
        super.onDestroyView()
        // ✅ View destroyed, but Fragment can be restored
    }
}
```

**3. State Order**

**Activity** (6 states):
```
onCreate → onStart → onResume → onPause → onStop → onDestroy
```

**Fragment** (11 states):
```
onAttach → onCreate → onCreateView → onViewCreated →
onStart → onResume → onPause → onStop →
onDestroyView → onDestroy → onDetach
```

**4. ViewLifecycleOwner**

Fragment provides a separate `viewLifecycleOwner` to observe data only while View exists:

```kotlin
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // ✅ Use viewLifecycleOwner instead of this
        viewModel.data.observe(viewLifecycleOwner) { data ->
            // Subscription automatically cancelled on onDestroyView
        }
    }
}
```

**5. Programmatic Back Stack**

Fragment supports its own back stack independent of the system back stack:

```kotlin
supportFragmentManager.beginTransaction()
    .replace(R.id.container, DetailFragment())
    .addToBackStack(null) // ✅ Add to back stack
    .commit()
```

### Comparison Table

| Aspect | Activity | Fragment |
|--------|----------|----------|
| Number of states | 6 | 11 |
| View lifecycle | Same as Activity | Separate from Fragment |
| Parent binding | — | onAttach/onDetach |
| Back stack | System | Programmatic |
| Nesting | — | Supports child fragments |

---

## Follow-ups

- What happens if you observe LiveData with Fragment instead of viewLifecycleOwner?
- How do nested fragments affect the lifecycle order?
- When should you use `setRetainInstance(true)` and is it still recommended?
- How does configuration change affect Fragment lifecycle differently from Activity?

## References

- [Android Fragment Lifecycle Documentation](https://developer.android.com/guide/fragments/lifecycle)
- [ViewLifecycleOwner Best Practices](https://developer.android.com/topic/libraries/architecture/lifecycle)

## Related Questions

### Prerequisites
- [[q-activity-lifecycle-methods--android--medium]] — Activity lifecycle basics
- [[q-what-are-fragments-for-if-there-is-activity--android--medium]] — Fragment purpose

### Related
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] — Lifecycle dependency
- [[q-how-does-fragment-lifecycle-differ-from-activity-v2--android--medium]] — Alternative perspective

### Advanced
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] — Fragment design rationale
- [[q-fragments-and-activity-relationship--android--hard]] — Deep dive into relationship
- [[q-why-fragment-callbacks-differ-from-activity-callbacks--android--hard]] — Callback differences
