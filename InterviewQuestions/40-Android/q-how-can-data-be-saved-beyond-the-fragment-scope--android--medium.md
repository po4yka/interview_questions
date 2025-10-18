---
id: 20251016-162905
title: "How Can Data Be Saved Beyond The Fragment Scope / Как можно сохранить данные за пределами скоупа Fragment"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-dagger-custom-scopes--di--hard, q-memory-leak-detection--performance--medium, q-alternative-distribution--distribution--medium]
created: 2025-10-15
tags:
  - android
---
# How can data be saved beyond the fragment scope?

## Answer (EN)
Data can be saved beyond Fragment scope using several approaches, each with different lifetime characteristics and use cases.

### 1. ViewModel

ViewModel survives configuration changes and is scoped to Activity or Fragment lifecycle:

```kotlin
// Fragment-scoped ViewModel
class MyFragment : Fragment() {
    private val viewModel: MyViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        viewModel.data.observe(viewLifecycleOwner) { data ->
            // Update UI
        }
    }
}

// Activity-scoped ViewModel (shared across fragments)
class MyFragment : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels()
}
```

**Lifetime**: Until Activity finishes or Fragment is permanently removed
**Data loss**: Process death

### 2. onSaveInstanceState()

Save small amounts of data that survive process death:

```kotlin
class MyFragment : Fragment() {
    private var userName: String = ""

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putString("user_name", userName)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        savedInstanceState?.let {
            userName = it.getString("user_name", "")
        }
    }
}
```

**Lifetime**: Survives process death
**Limitation**: Limited data size (Bundle size restrictions)

### 3. Shared Repository/Database

Persistent storage using Room, SharedPreferences, or DataStore:

```kotlin
class UserRepository(private val userDao: UserDao) {
    val userData: Flow<User> = userDao.getUserFlow()

    suspend fun saveUser(user: User) {
        userDao.insert(user)
    }
}

class MyFragment : Fragment() {
    private val repository: UserRepository by inject()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        lifecycleScope.launch {
            repository.userData.collect { user ->
                // Update UI with persistent data
            }
        }
    }
}
```

**Lifetime**: Survives app restarts and process death
**Use case**: Large datasets, user preferences, cached data

### 4. Parent Activity Scope

Share data across fragments via Activity:

```kotlin
class SharedDataActivity : AppCompatActivity() {
    var sharedData: String = ""
}

class MyFragment : Fragment() {
    private val sharedData: String
        get() = (requireActivity() as SharedDataActivity).sharedData
}
```

**Lifetime**: Until Activity is destroyed
**Use case**: Temporary data sharing between fragments

### 5. Application Class

Global application-level data:

```kotlin
class MyApplication : Application() {
    var globalData: String = ""
}

class MyFragment : Fragment() {
    private val appData: String
        get() = (requireActivity().application as MyApplication).globalData
}
```

**Lifetime**: Until app process is killed
**Warning**: Not recommended for large data or sensitive information

### Comparison Table

| Method | Survives Config Change | Survives Process Death | Data Size | Use Case |
|--------|------------------------|------------------------|-----------|----------|
| ViewModel | Yes | No | Medium | UI state |
| onSaveInstanceState | Yes | Yes | Small | Critical UI state |
| Repository/DB | Yes | Yes | Large | Persistent data |
| Activity Scope | Yes | No | Any | Fragment communication |
| Application | Yes | No | Small | Global state |

### Best Practices

1. **Combine approaches**: Use ViewModel + onSaveInstanceState for robust state management
2. **Minimize Bundle data**: Keep onSaveInstanceState data small and simple
3. **Use Repository pattern**: Separate data management from UI logic
4. **Avoid memory leaks**: Don't hold Fragment references in ViewModels or Application
5. **Consider data sensitivity**: Use encrypted storage for sensitive data

## Ответ (RU)

Данные можно сохранить за пределами области видимости Fragment несколькими способами, каждый из которых имеет различные характеристики времени жизни и случаи использования.

### 1. ViewModel

ViewModel переживает изменения конфигурации и привязана к жизненному циклу Activity или Fragment:

```kotlin
// ViewModel с областью видимости Fragment
class MyFragment : Fragment() {
    private val viewModel: MyViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        viewModel.data.observe(viewLifecycleOwner) { data ->
            // Обновить UI
        }
    }
}

// ViewModel с областью видимости Activity (shared между fragments)
class MyFragment : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels()
}
```

**Время жизни**: До завершения Activity или окончательного удаления Fragment
**Потеря данных**: Смерть процесса

### 2. onSaveInstanceState()

Сохранение небольших объёмов данных, которые переживают смерть процесса:

```kotlin
class MyFragment : Fragment() {
    private var userName: String = ""

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putString("user_name", userName)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        savedInstanceState?.let {
            userName = it.getString("user_name", "")
        }
    }
}
```

**Время жизни**: Переживает смерть процесса
**Ограничение**: Ограниченный размер данных (ограничения размера Bundle)

### 3. Shared Repository/Database

Постоянное хранение с использованием Room, SharedPreferences или DataStore:

```kotlin
class UserRepository(private val userDao: UserDao) {
    val userData: Flow<User> = userDao.getUserFlow()

    suspend fun saveUser(user: User) {
        userDao.insert(user)
    }
}

class MyFragment : Fragment() {
    private val repository: UserRepository by inject()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        lifecycleScope.launch {
            repository.userData.collect { user ->
                // Обновить UI с постоянными данными
            }
        }
    }
}
```

**Время жизни**: Переживает перезапуски приложения и смерть процесса
**Случай использования**: Большие наборы данных, пользовательские настройки, кэшированные данные

### 4. Parent Activity Scope

Совместное использование данных между фрагментами через Activity:

```kotlin
class SharedDataActivity : AppCompatActivity() {
    var sharedData: String = ""
}

class MyFragment : Fragment() {
    private val sharedData: String
        get() = (requireActivity() as SharedDataActivity).sharedData
}
```

**Время жизни**: До разрушения Activity
**Случай использования**: Временное совместное использование данных между фрагментами

### 5. Application Class

Глобальные данные на уровне приложения:

```kotlin
class MyApplication : Application() {
    var globalData: String = ""
}

class MyFragment : Fragment() {
    private val appData: String
        get() = (requireActivity().application as MyApplication).globalData
}
```

**Время жизни**: До уничтожения процесса приложения
**Предупреждение**: Не рекомендуется для больших данных или конфиденциальной информации

### Таблица Сравнения

| Метод | Переживает Изменение Конфигурации | Переживает Смерть Процесса | Размер Данных | Случай Использования |
|--------|------------------------|------------------------|-----------|----------|
| ViewModel | Да | Нет | Средний | Состояние UI |
| onSaveInstanceState | Да | Да | Маленький | Критическое состояние UI |
| Repository/DB | Да | Да | Большой | Постоянные данные |
| Activity Scope | Да | Нет | Любой | Коммуникация между Fragment |
| Application | Да | Нет | Маленький | Глобальное состояние |

### Лучшие Практики

1. **Комбинируйте подходы**: Используйте ViewModel + onSaveInstanceState для надёжного управления состоянием
2. **Минимизируйте данные Bundle**: Держите данные onSaveInstanceState маленькими и простыми
3. **Используйте паттерн Repository**: Отделяйте управление данными от логики UI
4. **Избегайте утечек памяти**: Не держите ссылки на Fragment в ViewModels или Application
5. **Учитывайте конфиденциальность данных**: Используйте зашифрованное хранилище для конфиденциальных данных

### Реальные Примеры

#### Пример 1: Комбинирование ViewModel и SavedState

```kotlin
class MyViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {
    // Автоматически сохраняется и восстанавливается
    var userName: String
        get() = savedStateHandle.get<String>("user_name") ?: ""
        set(value) = savedStateHandle.set("user_name", value)

    // Не переживает смерть процесса
    val tempData = MutableLiveData<List<Item>>()
}

class MyFragment : Fragment() {
    private val viewModel: MyViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // userName автоматически восстанавливается после смерти процесса
        binding.nameText.text = viewModel.userName

        viewModel.tempData.observe(viewLifecycleOwner) { items ->
            updateList(items)
        }
    }
}
```

#### Пример 2: Shared ViewModel между Fragments

```kotlin
class SharedViewModel : ViewModel() {
    private val _selectedItem = MutableLiveData<Item>()
    val selectedItem: LiveData<Item> = _selectedItem

    fun selectItem(item: Item) {
        _selectedItem.value = item
    }
}

class FragmentA : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels()

    private fun onItemClick(item: Item) {
        sharedViewModel.selectItem(item)
        // Перейти к FragmentB
    }
}

class FragmentB : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Получить тот же экземпляр ViewModel
        sharedViewModel.selectedItem.observe(viewLifecycleOwner) { item ->
            displayItemDetails(item)
        }
    }
}
```

#### Пример 3: Постоянное Хранение с Repository

```kotlin
class NoteRepository(private val noteDao: NoteDao, private val preferences: DataStore<Preferences>) {
    // Database для большого контента
    val notes: Flow<List<Note>> = noteDao.getAllNotes()

    suspend fun saveNote(note: Note) {
        noteDao.insert(note)
    }

    // DataStore для пользовательских настроек
    val sortOrder: Flow<SortOrder> = preferences.data.map { prefs ->
        SortOrder.valueOf(prefs[SORT_ORDER_KEY] ?: SortOrder.DATE.name)
    }

    suspend fun setSortOrder(order: SortOrder) {
        preferences.edit { prefs ->
            prefs[SORT_ORDER_KEY] = order.name
        }
    }
}

class NotesFragment : Fragment() {
    private val repository: NoteRepository by inject()
    private val viewModel: NotesViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Данные переживают всё - даже переустановку приложения (если не очищен кэш)
        lifecycleScope.launch {
            repository.notes.collect { notes ->
                updateNotesList(notes)
            }
        }

        lifecycleScope.launch {
            repository.sortOrder.collect { order ->
                applySortOrder(order)
            }
        }
    }
}
```

### Дерево Решений

```
Какие данные нужно сохранить?

 Состояние UI (выбранная вкладка, scroll позиция)?
   → onSaveInstanceState (маленькие данные)
   → ViewModel + SavedStateHandle (средние данные)

 Данные, загруженные из сети?
   → ViewModel (временный кэш)
   → Repository + Database (постоянный кэш)

 Пользовательские данные (профиль, настройки)?
   → Repository + Database/DataStore

 Коммуникация между Fragments?
   → Shared ViewModel (activityViewModels)
   → Fragment Result API

 Глобальное состояние приложения?
   → Application class (не рекомендуется)
   → Dependency Injection container
   → Repository pattern
```

## Related Topics
- ViewModel lifecycle
- Fragment lifecycle
- SavedStateHandle
- Repository pattern
- SharedPreferences vs DataStore

---

## Related Questions

### Prerequisites (Easier)
- [[q-how-to-choose-layout-for-fragment--android--easy]] - Fragment
- [[q-fragment-basics--android--easy]] - Fragment

### Related (Medium)
- [[q-save-data-outside-fragment--android--medium]] - Fragment
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - Fragment
- [[q-can-state-loss-be-related-to-a-fragment--android--medium]] - Fragment
- [[q-fragment-vs-activity-lifecycle--android--medium]] - Fragment
- [[q-how-to-pass-data-from-one-fragment-to-another--android--medium]] - Fragment

### Advanced (Harder)
- [[q-why-fragment-needs-separate-callback-for-ui-creation--android--hard]] - Fragment
