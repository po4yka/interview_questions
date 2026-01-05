---
id: android-384
title: ViewModel Pattern / Паттерн ViewModel
aliases: [ViewModel Pattern, Паттерн ViewModel]
topic: android
subtopics: [architecture-mvvm, lifecycle]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android, c-android-lifecycle, q-mvp-pattern--android--medium, q-mvvm-pattern--android--medium, q-viewmodel-vs-onsavedinstancestate--android--medium, q-what-is-activity-and-what-is-it-used-for--android--medium, q-what-is-viewmodel--android--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [android/architecture-mvvm, android/lifecycle, architecture-mvvm, difficulty/easy, mvvm, viewmodel]

---
# Вопрос (RU)
> Паттерн `ViewModel`

# Question (EN)
> `ViewModel` Pattern

---

## Ответ (RU)
В Android при использовании MVVM `ViewModel` представляет слой "`ViewModel`". Он:
- Хранит и предоставляет состояние UI для `View` (`Activity`/`Fragment`/Composable).
- Содержит презентационную логику и координирует обращения к Model (репозитории/юзкейсы), вынося эту логику из `View`.
- Учитывает жизненный цикл в том смысле, что AndroidX `ViewModel` сохраняется при изменениях конфигурации, пока жив её scope (`Activity`, `Fragment` или другой владелец), и очищается через `onCleared()` когда scope уничтожается.
- Обеспечивает разделение ответственности и повышает тестируемость, так как не должен напрямую зависеть от UI-компонентов Android.

### Основные Характеристики Паттерна MVVM С `ViewModel`

**Model-`View`-`ViewModel` (MVVM):**
- **Model**: Данные и бизнес-логика приложения.
- **`View`**: UI-компоненты (`Activity`, `Fragment`, Composable), отвечающие за отображение.
- **`ViewModel`**: Управляет состоянием UI и частью бизнес/презентационной логики, не зная о конкретной реализации `View`.

**Key MVVM Aspects with `ViewModel` (EN summary):**
- **Model**: Данные приложения и бизнес-логика.
- **`View`**: UI-компоненты, отвечающие только за рендеринг и ввод.
- **`ViewModel`**: Хранит состояние, предоставляет его как observable-данные и вызывает Model; не хранит ссылки на конкретные классы `View`.

### Преимущества Использования `ViewModel` / Benefits

1. **Разделение ответственности (Separation of Concerns):**
   - `View` отвечает за отображение и ввод пользователя.
   - `ViewModel` управляет UI-состоянием и логикой представления.
   - Model содержит данные и бизнес-правила.

2. **Работа с изменениями конфигурации:**
   - Инстанс `ViewModel` сохраняется при повороте экрана и других configuration changes, пока жив владелец (например, `Activity` или `Fragment`).
   - `ViewModel` создаётся заново, когда владелец окончательно уничтожается (например, при выходе назад).
   - `ViewModel` сам по себе не сохраняет данные при убийстве процесса; для этого используют `SavedStateHandle` или другие механизмы сохранения состояния.

3. **Упрощенное тестирование / Easier testing:**
   - `ViewModel` не должен зависеть от Android UI framework-компонентов.
   - Логика в `ViewModel` легко покрывается unit-тестами без запуска UI.

4. **Управление жизненным циклом / Lifecycle scoping:**
   - `ViewModel` привязан к жизненному циклу своего владельца (`Activity`/`Fragment`/`NavBackStackEntry` и т.п.) через `ViewModelStore`.
   - Не получает стандартные callbacks жизненного цикла (`onStart`/`onStop` и т.д.), только `onCleared()` при уничтожении scope.
   - Помогает предотвратить утечки памяти, так как `ViewModel` не должен хранить ссылки на `View`.

### Пример Реализации MVVM / MVVM Example

```kotlin
// Model - Domain model или data class
data class User(
    val id: Int,
    val name: String,
    val email: String
)

interface UserRepository {
    suspend fun getUser(id: Int): User
    suspend fun updateUser(user: User)
}

// ViewModel - Управление состоянием и логикой
class UserViewModel(
    private val userRepository: UserRepository
) : ViewModel() {

    private val _userState = MutableStateFlow<UiState<User>>(UiState.Loading)
    val userState: StateFlow<UiState<User>> = _userState.asStateFlow()

    fun loadUser(userId: Int) {
        viewModelScope.launch {
            _userState.value = UiState.Loading
            try {
                val user = userRepository.getUser(userId)
                _userState.value = UiState.Success(user)
            } catch (e: Exception) {
                _userState.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }

    fun updateUser(user: User) {
        viewModelScope.launch {
            try {
                userRepository.updateUser(user)
                _userState.value = UiState.Success(user)
            } catch (e: Exception) {
                _userState.value = UiState.Error(e.message ?: "Update failed")
            }
        }
    }
}

// View - Fragment отображает данные
class UserFragment : Fragment() {

    private val viewModel: UserViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Наблюдаем за изменениями состояния
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.userState.collect { state ->
                    when (state) {
                        is UiState.Loading -> showLoading()
                        is UiState.Success -> showUser(state.data)
                        is UiState.Error -> showError(state.message)
                    }
                }
            }
        }

        viewModel.loadUser(userId = 123)
    }
}

sealed class UiState<out T> {
    object Loading : UiState<Nothing>()
    data class Success<T>(val data: T) : UiState<T>()
    data class Error(val message: String) : UiState<Nothing>()
}
```

### Ключевые Принципы MVVM В Android / Key MVVM Principles in Android

1. **Однонаправленный поток данных (Unidirectional data flow):**
   - `View` наблюдает за данными из `ViewModel`.
   - `ViewModel` не знает о конкретной реализации `View`.

2. **Реактивный подход (Reactive):**
   - Использование `LiveData`, `StateFlow`, `Flow` или других observable-типов для обновления UI при изменении состояния.

3. **Dependency Injection:**
   - `ViewModel` получает зависимости (репозитории, use cases) через конструктор.

4. **Тестируемость (Testability):**
   - `ViewModel` легко тестировать изолированно от UI и Android framework.

### Сравнение С Другими Паттернами / Comparison with other Patterns

**MVVM vs MVP:**
- MVP: Presenter знает о `View` и управляет ею через интерфейс.
- MVVM: `ViewModel` не знает о `View`; `View` подписывается на состояние и события.

**MVVM vs MVI:**
- MVI: Строгий однонаправленный поток данных, единый immutable state, явные intents.
- MVVM: Более гибкий, допускает разные подходы к состоянию (включая mutable), но рекомендуется стремиться к предсказуемым и явным потокам данных.

### Резюме / Summary

`ViewModel` в Android — это компонент архитектуры MVVM, который:
- Отвечает за управление UI-состоянием и презентационной логикой.
- Не хранит ссылок на `View` и не зависит от UI-компонентов.
- Сохраняется при изменениях конфигурации в пределах своего scope и очищается через `onCleared()`.
- Не обеспечивает автоматического восстановления состояния при убийстве процесса — это ответственность разработчика (например, через `SavedStateHandle`).

Это обеспечивает четкое разделение между логикой и отображением, улучшает тестируемость и помогает корректно работать с жизненным циклом Android-компонентов.

---

## Answer (EN)
In Android MVVM, the `ViewModel` represents the "`ViewModel`" layer of the architecture. It:
- Holds and exposes UI state for the `View` (`Activity`/`Fragment`/Composable).
- Contains presentation logic and orchestrates calls to the Model layer (repositories/use cases), keeping this logic out of the `View`.
- Is lifecycle-aware in the sense that an AndroidX `ViewModel` instance is retained across configuration changes while its scope (`Activity`, `Fragment`, or other owner) is alive and is cleared via `onCleared()` when that scope is finished.
- Helps achieve separation of concerns and makes UI logic easier to test because it should not depend directly on Android UI framework types or hold references to concrete `View` objects.

### Core MVVM Characteristics with `ViewModel`

- **Model**: `Application` data and business logic.
- **`View`**: UI components responsible only for rendering and user interaction.
- **`ViewModel`**: Holds UI state, exposes it as observable data, and coordinates calls to the Model, without knowing concrete `View` implementations.

### Benefits of Using `ViewModel`

1. **Separation of Concerns:**
   - `View` handles rendering and user input only.
   - `ViewModel` owns UI state and presentation logic.
   - Model holds data and business rules.

2. **Handling configuration changes:**
   - A `ViewModel` instance is retained across configuration changes while its owner (`Activity`/`Fragment`) is alive.
   - A new `ViewModel` is created when the owner is truly destroyed (for example, when finishing via back).
   - A `ViewModel` does not automatically restore state after process death; use `SavedStateHandle` or other persistence mechanisms for that.

3. **Easier testing:**
   - `ViewModel` should not depend on Android UI framework types.
   - Its logic can be unit-tested without starting Android UI.

4. **Lifecycle scoping and memory safety:**
   - `ViewModel` is scoped to its owner via `ViewModelStore`.
   - It receives `onCleared()` when its scope is destroyed.
   - It should not keep references to `View`/`Context` that outlive the scope, which helps prevent memory leaks.

### MVVM Example

```kotlin
// Model - domain model or data class
data class User(
    val id: Int,
    val name: String,
    val email: String
)

interface UserRepository {
    suspend fun getUser(id: Int): User
    suspend fun updateUser(user: User)
}

// ViewModel - state and presentation logic
class UserViewModel(
    private val userRepository: UserRepository
) : ViewModel() {

    private val _userState = MutableStateFlow<UiState<User>>(UiState.Loading)
    val userState: StateFlow<UiState<User>> = _userState.asStateFlow()

    fun loadUser(userId: Int) {
        viewModelScope.launch {
            _userState.value = UiState.Loading
            try {
                val user = userRepository.getUser(userId)
                _userState.value = UiState.Success(user)
            } catch (e: Exception) {
                _userState.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }

    fun updateUser(user: User) {
        viewModelScope.launch {
            try {
                userRepository.updateUser(user)
                _userState.value = UiState.Success(user)
            } catch (e: Exception) {
                _userState.value = UiState.Error(e.message ?: "Update failed")
            }
        }
    }
}

// View - Fragment renders data
class UserFragment : Fragment() {

    private val viewModel: UserViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Observe state changes
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.userState.collect { state ->
                    when (state) {
                        is UiState.Loading -> showLoading()
                        is UiState.Success -> showUser(state.data)
                        is UiState.Error -> showError(state.message)
                    }
                }
            }
        }

        viewModel.loadUser(userId = 123)
    }
}

sealed class UiState<out T> {
    object Loading : UiState<Nothing>()
    data class Success<T>(val data: T) : UiState<T>()
    data class Error(val message: String) : UiState<Nothing>()
}
```

### Key MVVM Principles in Android

1. **Unidirectional data flow:**
   - `View` observes data exposed by `ViewModel`.
   - `ViewModel` does not know concrete `View` implementations.

2. **Reactive updates:**
   - Use `LiveData`, `StateFlow`, `Flow`, or other observable types to update the UI when state changes.

3. **Dependency Injection:**
   - `ViewModel` receives dependencies (repositories, use cases) via its constructor.

4. **Testability:**
   - `ViewModel` is easy to test in isolation from UI and the Android framework.

### Comparison with other Patterns

**MVVM vs MVP:**
- MVP: Presenter knows about the `View` and controls it through an interface.
- MVVM: `ViewModel` does not know the `View`; `View` subscribes to its state and events.

**MVVM vs MVI:**
- MVI: Strict unidirectional data flow, single immutable state, explicit intents.
- MVVM: More flexible, allows various approaches to state (including mutable), but you should still aim for predictable and explicit data flows.

### Summary

In Android, `ViewModel` in MVVM:
- Owns UI state and presentation logic.
- Does not keep references to `View` and avoids depending on Android UI components.
- Survives configuration changes within its scope and is cleared via `onCleared()`.
- Does not automatically restore state after process death; the developer must handle persistence (for example, with `SavedStateHandle`).

This leads to clear separation between logic and rendering, better testability, and more robust lifecycle handling.

---

## Follow-ups

- [[q-viewmodel-vs-onsavedinstancestate--android--medium]]
- Как `ViewModel` помогает избежать утечек памяти по сравнению с хранением ссылок на `Context` или `View`?
- В каких случаях `ViewModel` не подходит, и вы бы предпочли другой архитектурный подход (например, MVI или Presenter)?
- Как использовать `SavedStateHandle` вместе с `ViewModel` для восстановления состояния после убийства процесса?
- Как вы будете тестировать `ViewModel`, которая использует `coroutines` и несколько зависимостей (репозиторий, use case)?

## References

- [[c-android]]
- [Architecture](https://developer.android.com/topic/architecture)
- [Android Documentation](https://developer.android.com/docs)
- [Lifecycle](https://developer.android.com/topic/libraries/architecture/lifecycle)

## Related Questions

### Hub
- [[q-clean-architecture-android--android--hard]] - Clean Architecture principles

### Same Level (Easy)
- [[q-architecture-components-libraries--android--easy]] - Architecture Components overview

### Next Steps (Medium)
- [[q-mvvm-pattern--android--medium]] - MVVM pattern explained
- [[q-mvvm-vs-mvp-differences--android--medium]] - MVVM vs MVP comparison
- [[q-what-is-viewmodel--android--medium]] - What is `ViewModel`
- [[q-why-is-viewmodel-needed-and-what-happens-in-it--android--medium]] - `ViewModel` purpose & internals
