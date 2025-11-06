---
id: android-384
title: ViewModel Pattern / Паттерн ViewModel
aliases:
- ViewModel Pattern
- Паттерн ViewModel
topic: android
subtopics:
- architecture-mvvm
- lifecycle
question_kind: theory
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-architecture-patterns
- c-mvvm-pattern
- q-viewmodel-vs-onsavedinstancestate--android--medium
- q-what-is-activity-and-what-is-it-used-for--android--medium
created: 2025-10-15
updated: 2025-10-31
tags:
- android/architecture-mvvm
- android/lifecycle
- architecture-mvvm
- difficulty/easy
- mvvm
- viewmodel
---

# Вопрос (RU)
> Паттерн `ViewModel`

# Question (EN)
> `ViewModel` Pattern

---

## Answer (EN)
`ViewModel` implements the MVVM (Model-`View`-`ViewModel`) pattern. `ViewModel` is responsible for managing data and business logic, isolating them from the `View`, which simplifies testing and ensures separation of concerns between layers.


# Question (EN)
> `ViewModel` Pattern

---


---


## Answer (EN)
`ViewModel` implements the MVVM (Model-`View`-`ViewModel`) pattern. `ViewModel` is responsible for managing data and business logic, isolating them from the `View`, which simplifies testing and ensures separation of concerns between layers.

## Ответ (RU)

`ViewModel` реализует архитектурный паттерн MVVM (Model-`View`-`ViewModel`). `ViewModel` выполняет роль посредника между Model (данные и бизнес-логика) и `View` (UI компоненты), обеспечивая четкое разделение ответственности.

### Основные Характеристики Паттерна MVVM С `ViewModel`

**Model-`View`-`ViewModel` (MVVM):**
- **Model**: Данные и бизнес-логика приложения
- **`View`**: UI компоненты (`Activity`, `Fragment`, Composable)
- **`ViewModel`**: Управляет UI состоянием и обрабатывает бизнес-логику

**Преимущества использования `ViewModel`:**

1. **Разделение ответственности** (Separation of Concerns):
   - `View` отвечает только за отображение
   - `ViewModel` управляет состоянием и логикой
   - Model содержит данные и бизнес-правила

2. **Переживает изменения конфигурации**:
   - Сохраняет данные при повороте экрана
   - Не пересоздается при configuration changes
   - Автоматически очищается когда больше не нужен

3. **Упрощенное тестирование**:
   - `ViewModel` не зависит от Android framework
   - Легко покрывается unit тестами
   - Можно тестировать без UI

4. **Управление жизненным циклом**:
   - Связан с жизненным циклом Activity/`Fragment`
   - Автоматически очищается через onCleared()
   - Предотвращает утечки памяти

### Пример Реализации MVVM

```kotlin
// Model - Domain model или data class
data class User(
    val id: Int,
    val name: String,
    val email: String
)

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
            viewModel.userState.collect { state ->
                when (state) {
                    is UiState.Loading -> showLoading()
                    is UiState.Success -> showUser(state.data)
                    is UiState.Error -> showError(state.message)
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

### Ключевые Принципы MVVM В Android

1. **Однонаправленный поток данных**: `View` наблюдает за `ViewModel`, но `ViewModel` не знает о `View`
2. **Reactive подход**: Использование `LiveData`, `StateFlow`, `Flow` для наблюдения за изменениями
3. **Dependency Injection**: `ViewModel` получает зависимости через конструктор
4. **Тестируемость**: `ViewModel` легко тестируется изолированно от UI

### Сравнение С Другими Паттернами

**MVVM vs MVP:**
- MVP: Presenter напрямую управляет `View` через интерфейс
- MVVM: `ViewModel` не знает о `View`, использует reactive подход

**MVVM vs MVI:**
- MVI: Более строгий однонаправленный поток с immutable состоянием
- MVVM: Более гибкий, может использовать mutable или immutable состояние

### Резюме

`ViewModel` реализует паттерн MVVM, обеспечивая четкое разделение между UI логикой (`ViewModel`) и отображением (`View`). Это упрощает тестирование, делает код более поддерживаемым и решает проблемы с жизненным циклом Android компонентов. `ViewModel` автоматически сохраняет состояние при изменениях конфигурации и предоставляет удобный способ управления UI состоянием через reactive streams.



---


## Follow-ups

- [[c-architecture-patterns]]
- [[c-mvvm-pattern]]
- [[q-viewmodel-vs-onsavedinstancestate--android--medium]]


## References

- [Architecture](https://developer.android.com/topic/architecture)
- [Android Documentation](https://developer.android.com/docs)
- [`Lifecycle`](https://developer.android.com/topic/libraries/architecture/lifecycle)


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

