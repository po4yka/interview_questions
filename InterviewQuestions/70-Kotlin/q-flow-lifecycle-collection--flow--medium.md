---
id: kotlin-flow-006
title: Flow Lifecycle Collection / Сбор Flow с учётом жизненного цикла
aliases:
- Flow Lifecycle Collection
- flowWithLifecycle repeatOnLifecycle
- Lifecycle-aware Flow collection
topic: kotlin
subtopics:
- coroutines
- flow
- android
- lifecycle
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
source: internal
status: draft
moc: moc-kotlin
related:
- c-kotlin
- c-flow
- c-android-lifecycle
created: 2026-01-23
updated: 2026-01-23
tags:
- coroutines
- difficulty/medium
- flow
- kotlin
- android
- lifecycle
anki_cards:
- slug: kotlin-flow-006-0-en
  language: en
  anki_id: 1769344144041
  synced_at: '2026-01-25T16:29:04.096966'
- slug: kotlin-flow-006-0-ru
  language: ru
  anki_id: 1769344144091
  synced_at: '2026-01-25T16:29:04.098806'
---
# Vopros (RU)
> Как безопасно собирать Flow с учётом жизненного цикла Android? Объясните `flowWithLifecycle` и `repeatOnLifecycle`.

---

# Question (EN)
> How to safely collect Flow with Android lifecycle awareness? Explain `flowWithLifecycle` and `repeatOnLifecycle`.

## Otvet (RU)

### Проблема

При сборе Flow в Activity/Fragment без учёта lifecycle:
- Flow продолжает собираться когда UI в фоне (утечка ресурсов)
- Обновления UI когда приложение свёрнуто
- Потенциальные crashes при обращении к destroyed views

```kotlin
// НЕПРАВИЛЬНО: Flow собирается даже когда Activity в фоне
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                // Продолжает работать когда Activity в фоне!
                updateUI(state)
            }
        }
    }
}
```

### repeatOnLifecycle

`repeatOnLifecycle` запускает блок когда lifecycle достигает указанного состояния и отменяет при выходе из него:

```kotlin
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                // Этот блок запускается когда lifecycle >= STARTED
                // и отменяется когда < STARTED
                viewModel.uiState.collect { state ->
                    updateUI(state)
                }
            }
        }
    }
}
```

**Как работает:**
1. Activity/Fragment становится STARTED -> блок запускается
2. Activity/Fragment становится STOPPED -> блок отменяется
3. Снова STARTED -> блок запускается заново

```kotlin
// Несколько Flow внутри repeatOnLifecycle
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        // Параллельный сбор нескольких Flow
        launch {
            viewModel.uiState.collect { updateUI(it) }
        }
        launch {
            viewModel.events.collect { handleEvent(it) }
        }
    }
}
```

### flowWithLifecycle

`flowWithLifecycle` - оператор Flow, который эмитирует только когда lifecycle в нужном состоянии:

```kotlin
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            viewModel.uiState
                .flowWithLifecycle(lifecycle, Lifecycle.State.STARTED)
                .collect { state ->
                    updateUI(state)
                }
        }
    }
}
```

**Отличие от repeatOnLifecycle:**
- `flowWithLifecycle` - для одного Flow
- `repeatOnLifecycle` - для нескольких Flow или сложной логики

### Сравнение Подходов

| Подход | Когда использовать |
|--------|-------------------|
| `repeatOnLifecycle` | Несколько Flow, сложная логика |
| `flowWithLifecycle` | Один Flow |
| `collectAsState` (Compose) | Jetpack Compose |

### Fragment Considerations

```kotlin
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // ВАЖНО: используйте viewLifecycleOwner, НЕ lifecycle fragment-а
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    binding.textView.text = state.text
                }
            }
        }
    }
}
```

**Почему viewLifecycleOwner:**
- Fragment lifecycle != View lifecycle
- Fragment может существовать без View (detached)
- View lifecycle безопаснее для UI операций

### Jetpack Compose

В Compose используйте `collectAsState()` или `collectAsStateWithLifecycle()`:

```kotlin
@Composable
fun MyScreen(viewModel: MyViewModel) {
    // collectAsStateWithLifecycle учитывает lifecycle
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    // Альтернатива (не учитывает lifecycle):
    // val uiState by viewModel.uiState.collectAsState()

    Text(text = uiState.text)
}
```

`collectAsStateWithLifecycle`:
- Зависимость: `androidx.lifecycle:lifecycle-runtime-compose`
- Автоматически останавливает сбор когда Composable не видим
- Рекомендуется для Android приложений

### Состояния Lifecycle

```kotlin
// Lifecycle.State по порядку:
// DESTROYED < INITIALIZED < CREATED < STARTED < RESUMED

// STARTED - рекомендуемый выбор для большинства случаев
// Activity/Fragment видны, но могут быть не в фокусе
repeatOnLifecycle(Lifecycle.State.STARTED) { }

// RESUMED - только когда в фокусе
// Используйте для действий требующих активного взаимодействия
repeatOnLifecycle(Lifecycle.State.RESUMED) { }

// CREATED - включает фоновое состояние
// Редко используется для UI
repeatOnLifecycle(Lifecycle.State.CREATED) { }
```

### WhileSubscribed и Lifecycle

`StateFlow` с `WhileSubscribed` хорошо работает с lifecycle-aware collection:

```kotlin
// ViewModel
val uiState: StateFlow<UiState> = repository.observeData()
    .map { UiState.Success(it) }
    .stateIn(
        scope = viewModelScope,
        // Останавливает upstream через 5 секунд после последнего подписчика
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = UiState.Loading
    )

// Activity - сбор останавливается при STOPPED
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.uiState.collect { updateUI(it) }
    }
}

// Результат:
// 1. Activity STOPPED -> collection отменяется
// 2. Через 5 сек без подписчиков -> upstream останавливается
// 3. Activity STARTED -> collection возобновляется, upstream перезапускается
```

### Полный Пример

```kotlin
class UserProfileFragment : Fragment(R.layout.fragment_user_profile) {

    private val viewModel: UserProfileViewModel by viewModels()
    private var _binding: FragmentUserProfileBinding? = null
    private val binding get() = _binding!!

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentUserProfileBinding.bind(view)

        setupObservers()
    }

    private fun setupObservers() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                // Параллельный сбор
                launch {
                    viewModel.profileState.collect { state ->
                        when (state) {
                            is ProfileState.Loading -> showLoading()
                            is ProfileState.Success -> showProfile(state.user)
                            is ProfileState.Error -> showError(state.message)
                        }
                    }
                }

                launch {
                    viewModel.navigationEvents.collect { event ->
                        when (event) {
                            is NavigationEvent.GoToSettings -> navigateToSettings()
                            is NavigationEvent.GoBack -> findNavController().popBackStack()
                        }
                    }
                }
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
```

---

## Answer (EN)

### The Problem

When collecting Flow in Activity/Fragment without lifecycle awareness:
- Flow continues collecting when UI is in background (resource leak)
- UI updates when app is minimized
- Potential crashes when accessing destroyed views

```kotlin
// WRONG: Flow collects even when Activity is in background
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                // Continues running when Activity is in background!
                updateUI(state)
            }
        }
    }
}
```

### repeatOnLifecycle

`repeatOnLifecycle` launches a block when lifecycle reaches the specified state and cancels it when exiting:

```kotlin
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                // This block launches when lifecycle >= STARTED
                // and cancels when < STARTED
                viewModel.uiState.collect { state ->
                    updateUI(state)
                }
            }
        }
    }
}
```

**How it works:**
1. Activity/Fragment becomes STARTED -> block launches
2. Activity/Fragment becomes STOPPED -> block cancels
3. STARTED again -> block relaunches

```kotlin
// Multiple Flows inside repeatOnLifecycle
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        // Parallel collection of multiple Flows
        launch {
            viewModel.uiState.collect { updateUI(it) }
        }
        launch {
            viewModel.events.collect { handleEvent(it) }
        }
    }
}
```

### flowWithLifecycle

`flowWithLifecycle` - Flow operator that emits only when lifecycle is in desired state:

```kotlin
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            viewModel.uiState
                .flowWithLifecycle(lifecycle, Lifecycle.State.STARTED)
                .collect { state ->
                    updateUI(state)
                }
        }
    }
}
```

**Difference from repeatOnLifecycle:**
- `flowWithLifecycle` - for single Flow
- `repeatOnLifecycle` - for multiple Flows or complex logic

### Approach Comparison

| Approach | When to use |
|----------|-------------|
| `repeatOnLifecycle` | Multiple Flows, complex logic |
| `flowWithLifecycle` | Single Flow |
| `collectAsState` (Compose) | Jetpack Compose |

### Fragment Considerations

```kotlin
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // IMPORTANT: use viewLifecycleOwner, NOT fragment's lifecycle
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    binding.textView.text = state.text
                }
            }
        }
    }
}
```

**Why viewLifecycleOwner:**
- Fragment lifecycle != View lifecycle
- Fragment can exist without View (detached)
- View lifecycle is safer for UI operations

### Jetpack Compose

In Compose use `collectAsState()` or `collectAsStateWithLifecycle()`:

```kotlin
@Composable
fun MyScreen(viewModel: MyViewModel) {
    // collectAsStateWithLifecycle respects lifecycle
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    // Alternative (doesn't respect lifecycle):
    // val uiState by viewModel.uiState.collectAsState()

    Text(text = uiState.text)
}
```

`collectAsStateWithLifecycle`:
- Dependency: `androidx.lifecycle:lifecycle-runtime-compose`
- Automatically stops collection when Composable is not visible
- Recommended for Android apps

### Lifecycle States

```kotlin
// Lifecycle.State in order:
// DESTROYED < INITIALIZED < CREATED < STARTED < RESUMED

// STARTED - recommended choice for most cases
// Activity/Fragment visible, but may not be in focus
repeatOnLifecycle(Lifecycle.State.STARTED) { }

// RESUMED - only when in focus
// Use for actions requiring active interaction
repeatOnLifecycle(Lifecycle.State.RESUMED) { }

// CREATED - includes background state
// Rarely used for UI
repeatOnLifecycle(Lifecycle.State.CREATED) { }
```

### WhileSubscribed and Lifecycle

`StateFlow` with `WhileSubscribed` works well with lifecycle-aware collection:

```kotlin
// ViewModel
val uiState: StateFlow<UiState> = repository.observeData()
    .map { UiState.Success(it) }
    .stateIn(
        scope = viewModelScope,
        // Stops upstream 5 seconds after last subscriber
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = UiState.Loading
    )

// Activity - collection stops at STOPPED
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.uiState.collect { updateUI(it) }
    }
}

// Result:
// 1. Activity STOPPED -> collection cancelled
// 2. After 5 sec without subscribers -> upstream stops
// 3. Activity STARTED -> collection resumes, upstream restarts
```

### Full Example

```kotlin
class UserProfileFragment : Fragment(R.layout.fragment_user_profile) {

    private val viewModel: UserProfileViewModel by viewModels()
    private var _binding: FragmentUserProfileBinding? = null
    private val binding get() = _binding!!

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentUserProfileBinding.bind(view)

        setupObservers()
    }

    private fun setupObservers() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                // Parallel collection
                launch {
                    viewModel.profileState.collect { state ->
                        when (state) {
                            is ProfileState.Loading -> showLoading()
                            is ProfileState.Success -> showProfile(state.user)
                            is ProfileState.Error -> showError(state.message)
                        }
                    }
                }

                launch {
                    viewModel.navigationEvents.collect { event ->
                        when (event) {
                            is NavigationEvent.GoToSettings -> navigateToSettings()
                            is NavigationEvent.GoBack -> findNavController().popBackStack()
                        }
                    }
                }
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
```

---

## Dopolnitelnye Voprosy (RU)

1. Почему `repeatOnLifecycle` предпочтительнее `launchWhenStarted`?
2. Как выбрать между `STARTED` и `RESUMED` для repeatOnLifecycle?
3. Как обрабатывать configuration changes с lifecycle-aware collection?
4. Какие проблемы могут возникнуть при использовании fragment lifecycle вместо viewLifecycleOwner?
5. Как тестировать lifecycle-aware Flow collection?

---

## Follow-ups

1. Why is `repeatOnLifecycle` preferred over `launchWhenStarted`?
2. How to choose between `STARTED` and `RESUMED` for repeatOnLifecycle?
3. How to handle configuration changes with lifecycle-aware collection?
4. What problems can arise when using fragment lifecycle instead of viewLifecycleOwner?
5. How to test lifecycle-aware Flow collection?

---

## Ssylki (RU)

- [[c-kotlin]]
- [[c-flow]]
- [Collecting Flows Safely](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow#collect-flows-safely)
- [repeatOnLifecycle API](https://developer.android.com/topic/libraries/architecture/lifecycle#repeatonlifecycle)

---

## References

- [[c-kotlin]]
- [[c-flow]]
- [Collecting Flows Safely](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow#collect-flows-safely)
- [repeatOnLifecycle API](https://developer.android.com/topic/libraries/architecture/lifecycle#repeatonlifecycle)

---

## Svyazannye Voprosy (RU)

### Sredniy Uroven
- [[q-stateflow-vs-sharedflow--flow--medium]]
- [[q-cold-vs-hot-flows--flow--medium]]
- [[q-flow-vs-livedata--flow--medium]]

---

## Related Questions

### Related (Medium)
- [[q-stateflow-vs-sharedflow--flow--medium]] - StateFlow vs SharedFlow
- [[q-cold-vs-hot-flows--flow--medium]] - Cold vs Hot Flows
- [[q-flow-vs-livedata--flow--medium]] - Flow vs LiveData comparison
