---
id: android-353
title: "How Can Data Be Saved Beyond The Fragment Scope / Как можно сохранить данные за пределами скоупа Fragment"
aliases: [Fragment Data Persistence, Fragment Scope, ViewModel Scope, Сохранение данных Fragment]
topic: android
subtopics: [architecture-mvvm, datastore, lifecycle]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-repository-pattern, c-viewmodel, q-fragment-vs-activity-lifecycle--android--medium, q-how-to-pass-data-from-one-fragment-to-another--android--medium]
created: 2025-10-15
updated: 2025-10-31
sources: []
tags: [android, android/architecture-mvvm, android/datastore, android/lifecycle, difficulty/medium, fragment, state-management, viewmodel]
date created: Tuesday, October 28th 2025, 9:34:22 am
date modified: Saturday, November 1st 2025, 5:43:35 pm
---

# Вопрос (RU)

> Как можно сохранить данные за пределами области видимости Fragment?

# Question (EN)

> How can data be saved beyond the Fragment scope?

---

## Ответ (RU)

Существует 5 основных подходов для сохранения данных за пределами области видимости Fragment, каждый с различными характеристиками времени жизни.

### 1. ViewModel

ViewModel переживает изменения конфигурации и привязана к жизненному циклу Activity или Fragment.

```kotlin
// ✅ Fragment-scoped ViewModel
class MyFragment : Fragment() {
    private val viewModel: MyViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewModel.data.observe(viewLifecycleOwner) { data ->
            updateUI(data)
        }
    }
}

// ✅ Activity-scoped ViewModel (shared между fragments)
class MyFragment : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels()
}
```

**Время жизни**: До завершения Activity или окончательного удаления Fragment
**Потеря данных**: ❌ Смерть процесса

### 2. SavedStateHandle

Сохранение данных, которые переживают смерть процесса.

```kotlin
class MyViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {
    var userName: String
        get() = savedStateHandle.get<String>("user_name") ?: ""
        set(value) = savedStateHandle.set("user_name", value)
}

// ✅ Автоматически восстанавливается после process death
class MyFragment : Fragment() {
    private val viewModel: MyViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        binding.nameText.text = viewModel.userName // Restored automatically
    }
}
```

**Время жизни**: ✅ Переживает смерть процесса
**Ограничение**: Ограниченный размер данных (Bundle size restrictions)

### 3. Repository + Database

Постоянное хранение с использованием Room, SharedPreferences или DataStore.

```kotlin
class UserRepository(private val userDao: UserDao) {
    val userData: Flow<User> = userDao.getUserFlow()

    suspend fun saveUser(user: User) = userDao.insert(user)
}

class MyFragment : Fragment() {
    private val repository: UserRepository by inject()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        lifecycleScope.launch {
            repository.userData.collect { user ->
                updateUI(user)
            }
        }
    }
}
```

**Время жизни**: ✅ Переживает перезапуски приложения и смерть процесса
**Использование**: Большие наборы данных, настройки, кэш

### 4. Shared ViewModel Pattern

Совместное использование данных между несколькими фрагментами через Activity-scoped ViewModel.

```kotlin
class SharedViewModel : ViewModel() {
    private val _selectedItem = MutableLiveData<Item>()
    val selectedItem: LiveData<Item> = _selectedItem

    fun selectItem(item: Item) {
        _selectedItem.value = item
    }
}

// FragmentA выбирает элемент
class FragmentA : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels()

    private fun onItemClick(item: Item) {
        sharedViewModel.selectItem(item)
    }
}

// FragmentB получает выбранный элемент
class FragmentB : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        sharedViewModel.selectedItem.observe(viewLifecycleOwner) { item ->
            displayItemDetails(item)
        }
    }
}
```

### 5. Application Class

```kotlin
// ❌ Не рекомендуется - используйте DI или Repository
class MyApplication : Application() {
    var globalData: String = ""
}
```

**Предупреждение**: Не рекомендуется для больших данных или конфиденциальной информации

### Таблица Сравнения

| Метод | Config Change | Process Death | Размер | Использование |
|-------|---------------|---------------|--------|---------------|
| ViewModel | ✅ | ❌ | Средний | UI state |
| SavedStateHandle | ✅ | ✅ | Маленький | Критическое состояние |
| Repository/DB | ✅ | ✅ | Большой | Постоянные данные |
| Shared ViewModel | ✅ | ❌ | Любой | Коммуникация между Fragment |
| Application | ✅ | ❌ | Маленький | ❌ Не рекомендуется |

### Лучшие Практики

1. **Комбинируйте подходы**: ViewModel + SavedStateHandle для надёжного управления состоянием
2. **Используйте Repository pattern**: Отделяйте управление данными от UI логики
3. **Избегайте утечек памяти**: Не держите ссылки на Fragment в ViewModel или Application
4. **Учитывайте конфиденциальность**: Используйте EncryptedSharedPreferences для чувствительных данных

---

## Answer (EN)

There are 5 main approaches to save data beyond Fragment scope, each with different lifetime characteristics.

### 1. ViewModel

ViewModel survives configuration changes and is scoped to Activity or Fragment lifecycle.

```kotlin
// ✅ Fragment-scoped ViewModel
class MyFragment : Fragment() {
    private val viewModel: MyViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewModel.data.observe(viewLifecycleOwner) { data ->
            updateUI(data)
        }
    }
}

// ✅ Activity-scoped ViewModel (shared across fragments)
class MyFragment : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels()
}
```

**Lifetime**: Until Activity finishes or Fragment is permanently removed
**Data loss**: ❌ Process death

### 2. SavedStateHandle

Save data that survives process death.

```kotlin
class MyViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {
    var userName: String
        get() = savedStateHandle.get<String>("user_name") ?: ""
        set(value) = savedStateHandle.set("user_name", value)
}

// ✅ Automatically restored after process death
class MyFragment : Fragment() {
    private val viewModel: MyViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        binding.nameText.text = viewModel.userName // Restored automatically
    }
}
```

**Lifetime**: ✅ Survives process death
**Limitation**: Limited data size (Bundle size restrictions)

### 3. Repository + Database

Persistent storage using Room, SharedPreferences, or DataStore.

```kotlin
class UserRepository(private val userDao: UserDao) {
    val userData: Flow<User> = userDao.getUserFlow()

    suspend fun saveUser(user: User) = userDao.insert(user)
}

class MyFragment : Fragment() {
    private val repository: UserRepository by inject()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        lifecycleScope.launch {
            repository.userData.collect { user ->
                updateUI(user)
            }
        }
    }
}
```

**Lifetime**: ✅ Survives app restarts and process death
**Use case**: Large datasets, user preferences, cached data

### 4. Shared ViewModel Pattern

Share data across multiple fragments via Activity-scoped ViewModel.

```kotlin
class SharedViewModel : ViewModel() {
    private val _selectedItem = MutableLiveData<Item>()
    val selectedItem: LiveData<Item> = _selectedItem

    fun selectItem(item: Item) {
        _selectedItem.value = item
    }
}

// FragmentA selects item
class FragmentA : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels()

    private fun onItemClick(item: Item) {
        sharedViewModel.selectItem(item)
    }
}

// FragmentB receives selected item
class FragmentB : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        sharedViewModel.selectedItem.observe(viewLifecycleOwner) { item ->
            displayItemDetails(item)
        }
    }
}
```

### 5. Application Class

```kotlin
// ❌ Not recommended - use DI or Repository instead
class MyApplication : Application() {
    var globalData: String = ""
}
```

**Warning**: Not recommended for large data or sensitive information

### Comparison Table

| Method | Config Change | Process Death | Size | Use Case |
|--------|---------------|---------------|------|----------|
| ViewModel | ✅ | ❌ | Medium | UI state |
| SavedStateHandle | ✅ | ✅ | Small | Critical state |
| Repository/DB | ✅ | ✅ | Large | Persistent data |
| Shared ViewModel | ✅ | ❌ | Any | Fragment communication |
| Application | ✅ | ❌ | Small | ❌ Not recommended |

### Best Practices

1. **Combine approaches**: Use ViewModel + SavedStateHandle for robust state management
2. **Use Repository pattern**: Separate data management from UI logic
3. **Avoid memory leaks**: Don't hold Fragment references in ViewModels or Application
4. **Consider data sensitivity**: Use EncryptedSharedPreferences for sensitive data

---

## Follow-ups

- How does SavedStateHandle differ from onSaveInstanceState?
- When should I use DataStore instead of SharedPreferences?
- How to prevent memory leaks when sharing data via Application class?
- What's the maximum Bundle size for SavedStateHandle?
- How to share data between fragments in different activities?

## References

- [[c-viewmodel]]
- [[c-repository-pattern]]
- [[c-fragment-lifecycle]]
- https://developer.android.com/topic/libraries/architecture/viewmodel
- https://developer.android.com/topic/libraries/architecture/saving-states

## Related Questions

### Prerequisites (Easier)
- [[q-how-to-choose-layout-for-fragment--android--easy]]
- [[q-fragment-basics--android--easy]]

### Related (Same Level)
- [[q-fragment-vs-activity-lifecycle--android--medium]]
- [[q-can-state-loss-be-related-to-a-fragment--android--medium]]
- [[q-how-to-pass-data-from-one-fragment-to-another--android--medium]]

### Advanced (Harder)
- [[q-why-fragment-needs-separate-callback-for-ui-creation--android--hard]]
