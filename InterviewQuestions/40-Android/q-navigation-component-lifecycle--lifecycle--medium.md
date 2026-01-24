---
id: android-lc-011
title: Navigation Component Lifecycle / Жизненный цикл Navigation Component
aliases: []
topic: android
subtopics:
- lifecycle
- navigation
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
- c-navigation
created: 2025-01-23
updated: 2025-01-23
tags:
- android/lifecycle
- android/navigation
- difficulty/medium
anki_cards:
- slug: android-lc-011-0-en
  language: en
  anki_id: 1769172240535
  synced_at: '2026-01-23T16:45:05.396825'
- slug: android-lc-011-0-ru
  language: ru
  anki_id: 1769172240559
  synced_at: '2026-01-23T16:45:05.398796'
---
# Question (EN)
> How does Navigation Component handle Fragment lifecycle and back stack?

# Vopros (RU)
> Как Navigation Component управляет lifecycle Fragment и back stack?

---

## Answer (EN)

**Navigation Component** manages Fragment transactions and lifecycle automatically, with specific behavior for back stack.

**Key behavior:**
- **Navigate forward**: New Fragment added, previous Fragment's View destroyed (but Fragment stays in memory)
- **Navigate back**: Previous Fragment's View recreated, current Fragment destroyed
- **Configuration change**: All Fragments and Views recreated

**Fragment vs View lifecycle on navigation:**
```
navigate(A -> B):
    A: onPause -> onStop -> onDestroyView (Fragment alive on back stack!)
    B: onCreate -> onCreateView -> onStart -> onResume

popBackStack():
    B: onPause -> onStop -> onDestroyView -> onDestroy
    A: onCreateView -> onStart -> onResume (Fragment was alive!)
```

**Implications for state:**
```kotlin
class MyFragment : Fragment() {
    // Survives back stack (Fragment scope)
    private val viewModel: MyViewModel by viewModels()

    // Destroyed on back stack, recreated on return (View scope)
    private var _binding: FragmentMyBinding? = null

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // MUST use viewLifecycleOwner for View-related observations
        viewModel.data.observe(viewLifecycleOwner) { data ->
            binding.textView.text = data
        }
    }
}
```

**NavGraph-scoped ViewModel:**
```kotlin
// Shared across all fragments in the nav graph
// Cleared when entire graph is popped
val sharedViewModel: CheckoutViewModel by navGraphViewModels(R.id.checkout_graph)
```

**Process death handling:**
```kotlin
// Navigation Component saves:
// - Back stack structure
// - Destination arguments
// - NavController state

// You must save:
// - ViewModel state via SavedStateHandle
// - Custom savedInstanceState data
```

**Deep link lifecycle:**
```kotlin
// Deep link recreates entire back stack
// handleDeepLink() called on each destination

navController.handleDeepLink(intent)
// Results in: Home -> Category -> Product (all created)
```

**Common mistakes:**
```kotlin
// BAD: Using this instead of viewLifecycleOwner
viewModel.data.observe(this) { } // Leaks when on back stack

// BAD: Storing View references in ViewModel
viewModel.textView = binding.textView // Memory leak

// BAD: Not clearing binding
// Missing: _binding = null in onDestroyView()
```

## Otvet (RU)

**Navigation Component** автоматически управляет транзакциями Fragment и lifecycle, с особым поведением для back stack.

**Ключевое поведение:**
- **Навигация вперёд**: Новый Fragment добавлен, View предыдущего Fragment уничтожен (но Fragment остаётся в памяти)
- **Навигация назад**: View предыдущего Fragment пересоздан, текущий Fragment уничтожен
- **Изменение конфигурации**: Все Fragments и Views пересоздаются

**Lifecycle Fragment vs View при навигации:**
```
navigate(A -> B):
    A: onPause -> onStop -> onDestroyView (Fragment жив на back stack!)
    B: onCreate -> onCreateView -> onStart -> onResume

popBackStack():
    B: onPause -> onStop -> onDestroyView -> onDestroy
    A: onCreateView -> onStart -> onResume (Fragment был жив!)
```

**Последствия для состояния:**
```kotlin
class MyFragment : Fragment() {
    // Переживает back stack (область Fragment)
    private val viewModel: MyViewModel by viewModels()

    // Уничтожается на back stack, пересоздаётся при возврате (область View)
    private var _binding: FragmentMyBinding? = null

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // ОБЯЗАТЕЛЬНО использовать viewLifecycleOwner для наблюдений View
        viewModel.data.observe(viewLifecycleOwner) { data ->
            binding.textView.text = data
        }
    }
}
```

**ViewModel с областью NavGraph:**
```kotlin
// Общий для всех фрагментов в nav graph
// Очищается когда весь graph снимается со стека
val sharedViewModel: CheckoutViewModel by navGraphViewModels(R.id.checkout_graph)
```

**Обработка смерти процесса:**
```kotlin
// Navigation Component сохраняет:
// - Структуру back stack
// - Аргументы destination
// - Состояние NavController

// Вы должны сохранить:
// - Состояние ViewModel через SavedStateHandle
// - Кастомные данные savedInstanceState
```

**Lifecycle deep link:**
```kotlin
// Deep link пересоздаёт весь back stack
// handleDeepLink() вызывается на каждом destination

navController.handleDeepLink(intent)
// Результат: Home -> Category -> Product (все созданы)
```

**Частые ошибки:**
```kotlin
// ПЛОХО: Использование this вместо viewLifecycleOwner
viewModel.data.observe(this) { } // Утечка когда на back stack

// ПЛОХО: Хранение ссылок на View в ViewModel
viewModel.textView = binding.textView // Утечка памяти

// ПЛОХО: Не очистить binding
// Отсутствует: _binding = null в onDestroyView()
```

---

## Follow-ups
- How to pass results between Navigation destinations?
- What is the difference between navigate() and popUpTo?
- How does Navigation handle configuration changes?

## References
- [[c-lifecycle]]
- [[c-navigation]]
- [[moc-android]]
