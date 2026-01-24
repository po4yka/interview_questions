---
id: android-lc-018
title: Coroutine Lifecycle Scopes / Lifecycle Scopes для корутин
aliases: []
topic: android
subtopics:
- lifecycle
- coroutines
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
- c-coroutines
created: 2025-01-23
updated: 2025-01-23
tags:
- android/lifecycle
- android/coroutines
- difficulty/medium
anki_cards:
- slug: android-lc-018-0-en
  language: en
  anki_id: 1769172276682
  synced_at: '2026-01-23T16:45:06.116677'
- slug: android-lc-018-0-ru
  language: ru
  anki_id: 1769172276707
  synced_at: '2026-01-23T16:45:06.117937'
---
# Question (EN)
> What are lifecycleScope, viewModelScope, and viewLifecycleOwner.lifecycleScope?

# Vopros (RU)
> Что такое lifecycleScope, viewModelScope и viewLifecycleOwner.lifecycleScope?

---

## Answer (EN)

**Lifecycle-aware coroutine scopes** automatically cancel when their owner is destroyed, preventing leaks and crashes.

**Three main scopes:**

| Scope | Owner | Cancelled when | Use case |
|-------|-------|----------------|----------|
| `lifecycleScope` | Activity/Fragment | Activity/Fragment destroyed | One-shot operations |
| `viewModelScope` | ViewModel | ViewModel cleared | Data loading, transformations |
| `viewLifecycleOwner.lifecycleScope` | Fragment's View | View destroyed | UI updates |

**lifecycleScope (Activity/Fragment):**
```kotlin
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // Cancelled when Fragment is DESTROYED
        lifecycleScope.launch {
            val data = repository.fetchData()
            // Safe: if Fragment destroyed, this line never runs
            binding.textView.text = data
        }
    }
}
```

**viewModelScope:**
```kotlin
class MyViewModel : ViewModel() {
    private val _data = MutableStateFlow<Data?>(null)
    val data: StateFlow<Data?> = _data

    fun loadData() {
        // Cancelled when ViewModel is cleared
        viewModelScope.launch {
            _data.value = repository.fetchData()
        }
    }
}
```

**viewLifecycleOwner.lifecycleScope (Fragment View):**
```kotlin
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // Cancelled when Fragment's VIEW is destroyed (not Fragment itself)
        // Critical for proper cleanup when on back stack
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.data.collect { data ->
                binding.textView.text = data
            }
        }
    }
}
```

**Lifecycle-aware collection:**
```kotlin
// Launch only when at least STARTED
viewLifecycleOwner.lifecycleScope.launch {
    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.uiState.collect { state ->
            updateUI(state)
        }
    }
}

// Shorthand (since lifecycle-runtime-ktx 2.4.0)
viewLifecycleOwner.lifecycleScope.launchWhenStarted {
    viewModel.uiState.collect { state ->
        updateUI(state)
    }
}
```

**Common mistakes:**
```kotlin
// BAD: Using lifecycleScope in Fragment for UI updates
// Leaks when Fragment on back stack but View destroyed
lifecycleScope.launch {
    viewModel.data.collect { binding.textView.text = it }
}

// GOOD: Use viewLifecycleOwner for View operations
viewLifecycleOwner.lifecycleScope.launch {
    viewModel.data.collect { binding.textView.text = it }
}

// BAD: GlobalScope - never cancelled, leaks
GlobalScope.launch { repository.fetchData() }

// GOOD: viewModelScope - cancelled when ViewModel cleared
viewModelScope.launch { repository.fetchData() }
```

**Custom lifecycle scope:**
```kotlin
class MyLifecycleObserver : DefaultLifecycleObserver {
    private var scope: CoroutineScope? = null

    override fun onStart(owner: LifecycleOwner) {
        scope = CoroutineScope(Dispatchers.Main + SupervisorJob())
    }

    override fun onStop(owner: LifecycleOwner) {
        scope?.cancel()
        scope = null
    }
}
```

## Otvet (RU)

**Lifecycle-aware coroutine scopes** автоматически отменяются когда их владелец уничтожается, предотвращая утечки и краши.

**Три основные области:**

| Scope | Владелец | Отменяется когда | Применение |
|-------|----------|------------------|------------|
| `lifecycleScope` | Activity/Fragment | Activity/Fragment уничтожен | Одноразовые операции |
| `viewModelScope` | ViewModel | ViewModel очищен | Загрузка данных, трансформации |
| `viewLifecycleOwner.lifecycleScope` | View Fragment | View уничтожен | UI обновления |

**lifecycleScope (Activity/Fragment):**
```kotlin
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // Отменяется когда Fragment DESTROYED
        lifecycleScope.launch {
            val data = repository.fetchData()
            // Безопасно: если Fragment уничтожен, эта строка не выполнится
            binding.textView.text = data
        }
    }
}
```

**viewModelScope:**
```kotlin
class MyViewModel : ViewModel() {
    private val _data = MutableStateFlow<Data?>(null)
    val data: StateFlow<Data?> = _data

    fun loadData() {
        // Отменяется когда ViewModel очищается
        viewModelScope.launch {
            _data.value = repository.fetchData()
        }
    }
}
```

**viewLifecycleOwner.lifecycleScope (View Fragment):**
```kotlin
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // Отменяется когда VIEW Fragment уничтожается (не сам Fragment)
        // Критично для правильной очистки когда на back stack
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.data.collect { data ->
                binding.textView.text = data
            }
        }
    }
}
```

**Lifecycle-aware сбор:**
```kotlin
// Запуск только когда минимум STARTED
viewLifecycleOwner.lifecycleScope.launch {
    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.uiState.collect { state ->
            updateUI(state)
        }
    }
}

// Сокращённо (с lifecycle-runtime-ktx 2.4.0)
viewLifecycleOwner.lifecycleScope.launchWhenStarted {
    viewModel.uiState.collect { state ->
        updateUI(state)
    }
}
```

**Частые ошибки:**
```kotlin
// ПЛОХО: Использование lifecycleScope во Fragment для UI обновлений
// Утечка когда Fragment на back stack но View уничтожен
lifecycleScope.launch {
    viewModel.data.collect { binding.textView.text = it }
}

// ХОРОШО: Используйте viewLifecycleOwner для операций с View
viewLifecycleOwner.lifecycleScope.launch {
    viewModel.data.collect { binding.textView.text = it }
}

// ПЛОХО: GlobalScope - никогда не отменяется, утечки
GlobalScope.launch { repository.fetchData() }

// ХОРОШО: viewModelScope - отменяется когда ViewModel очищается
viewModelScope.launch { repository.fetchData() }
```

**Кастомный lifecycle scope:**
```kotlin
class MyLifecycleObserver : DefaultLifecycleObserver {
    private var scope: CoroutineScope? = null

    override fun onStart(owner: LifecycleOwner) {
        scope = CoroutineScope(Dispatchers.Main + SupervisorJob())
    }

    override fun onStop(owner: LifecycleOwner) {
        scope?.cancel()
        scope = null
    }
}
```

---

## Follow-ups
- What is repeatOnLifecycle and when to use it?
- How to handle structured concurrency with lifecycleScope?
- What happens to coroutines when configuration changes?

## References
- [[c-lifecycle]]
- [[c-coroutines]]
- [[moc-android]]
