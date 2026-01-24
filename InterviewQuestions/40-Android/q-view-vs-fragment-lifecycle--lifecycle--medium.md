---
id: android-lc-005
title: View Lifecycle vs Fragment Lifecycle / Жизненный цикл View vs Fragment
aliases: []
topic: android
subtopics:
- lifecycle
- fragment
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
source_note: Android interview preparation
status: draft
moc: moc-android
related:
- c-lifecycle
- c-fragment
created: 2025-01-23
updated: 2025-01-23
tags:
- android/lifecycle
- android/fragment
- difficulty/medium
anki_cards:
- slug: android-lc-005-0-en
  language: en
  anki_id: 1769172236160
  synced_at: '2026-01-23T16:45:05.287685'
- slug: android-lc-005-0-ru
  language: ru
  anki_id: 1769172236183
  synced_at: '2026-01-23T16:45:05.289630'
---
# Question (EN)
> What is the difference between Fragment lifecycle and Fragment View lifecycle?

# Vopros (RU)
> В чём разница между жизненным циклом Fragment и жизненным циклом View Fragment?

---

## Answer (EN)

**Key insight:** Fragment and its View have **separate lifecycles**. Fragment can outlive its View (e.g., when on back stack).

**Fragment lifecycle:**
```
onAttach() -> onCreate() -> onCreateView() -> onViewCreated()
    -> onStart() -> onResume()
    -> onPause() -> onStop() -> onDestroyView() -> onDestroy() -> onDetach()
```

**View lifecycle (shorter):**
```
onCreateView() -> onViewCreated() -> onStart() -> onResume()
    -> onPause() -> onStop() -> onDestroyView()
```

**When they differ:**
```kotlin
// Fragment on back stack:
// - Fragment still exists (onCreate was called)
// - But View is destroyed (onDestroyView was called)
// - When user returns: onCreateView() is called again
```

**Practical implications:**

```kotlin
class MyFragment : Fragment() {
    // Lives with Fragment lifecycle
    private val viewModel: MyViewModel by viewModels()

    // Lives with View lifecycle - use viewLifecycleOwner!
    private var _binding: FragmentMyBinding? = null
    private val binding get() = _binding!!

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // CORRECT: Use viewLifecycleOwner for View observations
        viewModel.data.observe(viewLifecycleOwner) { data ->
            binding.textView.text = data
        }

        // WRONG: Would cause memory leak when View is destroyed
        // viewModel.data.observe(this) { ... }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null  // Prevent memory leak
    }
}
```

**viewLifecycleOwner vs this:**
| Use `viewLifecycleOwner` | Use `this` (Fragment) |
|--------------------------|----------------------|
| LiveData observers for UI | ViewModel creation |
| View-related callbacks | Fragment-scoped data |
| RecyclerView adapters | Navigation observers |
| Coroutine lifecycleScope | - |

**Common mistake:**
```kotlin
// BAD: Leaks when Fragment is on back stack
override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
    someFlow.collect { } // Uses Fragment lifecycle
}

// GOOD: Cancels when View is destroyed
viewLifecycleOwner.lifecycleScope.launch {
    someFlow.collect { }
}
```

## Otvet (RU)

**Ключевое понимание:** Fragment и его View имеют **раздельные жизненные циклы**. Fragment может пережить свой View (например, когда на back stack).

**Жизненный цикл Fragment:**
```
onAttach() -> onCreate() -> onCreateView() -> onViewCreated()
    -> onStart() -> onResume()
    -> onPause() -> onStop() -> onDestroyView() -> onDestroy() -> onDetach()
```

**Жизненный цикл View (короче):**
```
onCreateView() -> onViewCreated() -> onStart() -> onResume()
    -> onPause() -> onStop() -> onDestroyView()
```

**Когда они различаются:**
```kotlin
// Fragment на back stack:
// - Fragment всё ещё существует (onCreate был вызван)
// - Но View уничтожен (onDestroyView был вызван)
// - Когда пользователь возвращается: onCreateView() вызывается снова
```

**Практические последствия:**

```kotlin
class MyFragment : Fragment() {
    // Живёт с жизненным циклом Fragment
    private val viewModel: MyViewModel by viewModels()

    // Живёт с жизненным циклом View - используйте viewLifecycleOwner!
    private var _binding: FragmentMyBinding? = null
    private val binding get() = _binding!!

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // ПРАВИЛЬНО: Используйте viewLifecycleOwner для наблюдений View
        viewModel.data.observe(viewLifecycleOwner) { data ->
            binding.textView.text = data
        }

        // НЕПРАВИЛЬНО: Вызовет утечку памяти когда View уничтожен
        // viewModel.data.observe(this) { ... }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null  // Предотвратить утечку памяти
    }
}
```

**viewLifecycleOwner vs this:**
| Используйте `viewLifecycleOwner` | Используйте `this` (Fragment) |
|----------------------------------|-------------------------------|
| LiveData observers для UI | Создание ViewModel |
| Callback-и связанные с View | Данные на уровне Fragment |
| Адаптеры RecyclerView | Observers навигации |
| lifecycleScope корутин | - |

**Частая ошибка:**
```kotlin
// ПЛОХО: Утекает когда Fragment на back stack
override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
    someFlow.collect { } // Использует lifecycle Fragment
}

// ХОРОШО: Отменяется когда View уничтожается
viewLifecycleOwner.lifecycleScope.launch {
    someFlow.collect { }
}
```

---

## Follow-ups
- What happens if you observe LiveData with Fragment instead of viewLifecycleOwner?
- When is viewLifecycleOwner available?
- How to handle RecyclerView adapter lifecycle properly?

## References
- [[c-lifecycle]]
- [[c-fragment]]
- [[moc-android]]
