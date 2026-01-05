---
id: android-319
title: "List To Detail Navigation / Навигация от списка к детализации"
aliases: ["List To Detail Navigation", "Навигация от списка к детализации"]
topic: android
subtopics: [fragment, intents-deeplinks, ui-navigation]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-activity, c-compose-navigation, c-fragments, c-viewmodel]
sources: []
created: 2025-10-15
updated: 2025-11-10
tags: [android/fragment, android/intents-deeplinks, android/ui-navigation, bundle, difficulty/medium, navigation-component, parcelable]

---
# Вопрос (RU)

> С помощью чего делается переход со списков на деталки в Android?

# Question (EN)

> How do you implement navigation from a list to detail screens in Android?

---

## Ответ (RU)

Переход от списка к экрану деталей обычно реализуется через **`Intent` + `Bundle`** (для `Activity`), **Navigation Component** (для `Fragment`) и **Deep Link-ы**. Для тесно связанных `Fragment` (master-detail в одной `Activity`) можно использовать **shared `ViewModel`** как механизм выбора элемента, но не вместо явной передачи аргументов для независимых экранов.

Современный подход — Single `Activity` архитектура с Navigation Component и Safe Args для type-safe передачи аргументов.

### Основные Подходы

**1. `Intent` + `Bundle` (`Activity` → `Activity`)**

Передача ID элемента, а не всего объекта:

```kotlin
// ✅ Передача только ID
private fun openUserDetail(userId: Int) {
    val intent = Intent(this, UserDetailActivity::class.java)
        .putExtra("USER_ID", userId)
    startActivity(intent)
}

// DetailActivity загружает данные сама
class UserDetailActivity : AppCompatActivity() {
    private val viewModel: UserDetailViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val userId = intent.getIntExtra("USER_ID", -1)
        viewModel.loadUser(userId) // ✅ Загрузка через ViewModel
    }
}

// ❌ ПЛОХО - передача всего списка
intent.putParcelableArrayListExtra("USERS", ArrayList(allUsers))
```

**2. Navigation Component + Safe Args (`Fragment` → `Fragment`)**

Type-safe навигация с автогенерацией классов:

```kotlin
// nav_graph.xml
<fragment
    android:id="@+id/userDetailFragment"
    android:name="com.example.UserDetailFragment">
    <argument
        android:name="userId"
        app:argType="integer" />
</fragment>

// ListFragment - type-safe навигация
class UserListFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        adapter = UserAdapter { userId ->
            val action = UserListFragmentDirections
                .actionListToDetail(userId) // ✅ Compile-time проверка типов
            findNavController().navigate(action)
        }
    }
}

// DetailFragment - type-safe получение аргументов
class UserDetailFragment : Fragment() {
    private val args: UserDetailFragmentArgs by navArgs()
    private val viewModel: UserDetailViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewModel.loadUser(args.userId)
        viewModel.user.observe(viewLifecycleOwner) { user ->
            displayUser(user)
        }
    }
}
```

**3. Shared `ViewModel` (для связанных экранов в одной `Activity`)**

Для master-detail layout или связанных `Fragment` внутри одной `Activity`. Обычно лучше хранить в нём ID выбранного элемента и/или общий state, а данные для детали загружать через `ViewModel` самого детали.

```kotlin
// Activity-scoped ViewModel
class UserViewModel : ViewModel() {
    private val _selectedUserId = MutableLiveData<Int?>()
    val selectedUserId: LiveData<Int?> = _selectedUserId

    fun selectUser(userId: Int) {
        _selectedUserId.value = userId
    }
}

// ListFragment
class UserListFragment : Fragment() {
    private val sharedViewModel: UserViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        adapter = UserAdapter { userId ->
            sharedViewModel.selectUser(userId) // ✅ Сохранить выбранный ID
            findNavController().navigate(R.id.action_list_to_detail)
        }
    }
}

// DetailFragment читает ID из той же ViewModel и загружает данные
class UserDetailFragment : Fragment() {
    private val sharedViewModel: UserViewModel by activityViewModels()
    private val detailViewModel: UserDetailViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        sharedViewModel.selectedUserId.observe(viewLifecycleOwner) { userId ->
            userId?.let { detailViewModel.loadUser(it) }
        }
    }
}
```

### Сравнение Подходов

| Подход | Когда использовать | Преимущества | Недостатки |
|--------|-------------------|-------------|-----------|
| **`Intent` + `Bundle`** | Multi-activity или простые навигационные сценарии | Простой, знакомый | Boilerplate, нет type-safety |
| **Navigation Component** | Современные single-activity приложения | Type-safe (с Safe Args), визуальный граф | Требует настройки |
| **Shared `ViewModel`** | Master-detail и тесно связанные `Fragment` в одной `Activity` | Реактивный, общий state | Не подходит для независимых экранов и deep links |
| **Deep Links** | Внешняя навигация, URL-ы | Можно делиться, индексируются | Требует отдельной конфигурации |

### Best Practices

**Передавайте ID, загружайте данные в экране деталей:**
```kotlin
// ✅ ПРАВИЛЬНО
intent.putExtra("USER_ID", userId)
// В DetailScreen:
viewModel.loadUser(userId)

// ❌ РИСК - крупные Parcelable могут превысить лимит Binder-транзакции (около 1MB)
intent.putExtra("USER", user) // Может привести к TransactionTooLargeException
```

**Используйте `ViewModel` для загрузки данных:**
```kotlin
class UserDetailViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _user = MutableStateFlow<User?>(null)
    val user = _user.asStateFlow()

    fun loadUser(userId: Int) {
        viewModelScope.launch {
            _user.value = repository.getUserById(userId)
        }
    }
}
```

**Для Compose Navigation используйте type-safe декларацию маршрутов (пример):**

Ниже показан один из подходов с использованием route-объектов. Обратите внимание, что синтаксис `composable<UserDetailRoute>()` и `toRoute()` требует дополнительных библиотек поверх стандартного `androidx.navigation.compose`.

```kotlin
@Serializable
data class UserDetailRoute(val userId: Int)

NavHost(navController, startDestination = "userList") {
    composable("userList") {
        UserListScreen(
            onUserClick = { userId ->
                navController.navigate("userDetail/$userId")
            }
        )
    }
    composable(
        route = "userDetail/{userId}",
        arguments = listOf(navArgument("userId") { type = NavType.IntType })
    ) { backStackEntry ->
        val userId = backStackEntry.arguments?.getInt("userId")
            ?: error("userId is required")
        UserDetailScreen(userId = userId)
    }
}
```

## Answer (EN)

Navigation from list to detail screens is typically implemented via **`Intent` + `Bundle`** (for Activities), **Navigation Component** (for Fragments), and **deep links**. For tightly related Fragments within a single `Activity` (e.g., master-detail), a **shared `ViewModel`** can be used to coordinate selection, but it should not replace explicit arguments for independent/detail screens that must survive process death or be addressable directly.

The modern approach is a Single-`Activity` architecture with Navigation Component and Safe Args for type-safe argument passing.

### Main Approaches

**1. `Intent` + `Bundle` (`Activity` → `Activity`)**

Pass an ID, not the entire object:

```kotlin
// ✅ Pass only ID
private fun openUserDetail(userId: Int) {
    val intent = Intent(this, UserDetailActivity::class.java)
        .putExtra("USER_ID", userId)
    startActivity(intent)
}

// DetailActivity loads data itself
class UserDetailActivity : AppCompatActivity() {
    private val viewModel: UserDetailViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val userId = intent.getIntExtra("USER_ID", -1)
        viewModel.loadUser(userId) // ✅ Load via ViewModel
    }
}

// ❌ BAD - passing entire list
intent.putParcelableArrayListExtra("USERS", ArrayList(allUsers))
```

**2. Navigation Component + Safe Args (`Fragment` → `Fragment`)**

Type-safe navigation with auto-generated classes:

```kotlin
// nav_graph.xml
<fragment
    android:id="@+id/userDetailFragment"
    android:name="com.example.UserDetailFragment">
    <argument
        android:name="userId"
        app:argType="integer" />
</fragment>

// ListFragment - type-safe navigation
class UserListFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        adapter = UserAdapter { userId ->
            val action = UserListFragmentDirections
                .actionListToDetail(userId) // ✅ Compile-time type checking
            findNavController().navigate(action)
        }
    }
}

// DetailFragment - type-safe argument retrieval
class UserDetailFragment : Fragment() {
    private val args: UserDetailFragmentArgs by navArgs()
    private val viewModel: UserDetailViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewModel.loadUser(args.userId)
        viewModel.user.observe(viewLifecycleOwner) { user ->
            displayUser(user)
        }
    }
}
```

**3. Shared `ViewModel` (for related screens in one `Activity`)**

For master-detail layout or tightly related Fragments within a single `Activity`. Typically you store the selected item ID and/or shared state there, while the detail screen's own `ViewModel` loads its data.

```kotlin
// Activity-scoped ViewModel
class UserViewModel : ViewModel() {
    private val _selectedUserId = MutableLiveData<Int?>()
    val selectedUserId: LiveData<Int?> = _selectedUserId

    fun selectUser(userId: Int) {
        _selectedUserId.value = userId
    }
}

// ListFragment
class UserListFragment : Fragment() {
    private val sharedViewModel: UserViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        adapter = UserAdapter { userId ->
            sharedViewModel.selectUser(userId) // ✅ Store selected ID
            findNavController().navigate(R.id.action_list_to_detail)
        }
    }
}

// DetailFragment observes the same ViewModel and loads data
class UserDetailFragment : Fragment() {
    private val sharedViewModel: UserViewModel by activityViewModels()
    private val detailViewModel: UserDetailViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        sharedViewModel.selectedUserId.observe(viewLifecycleOwner) { userId ->
            userId?.let { detailViewModel.loadUser(it) }
        }
    }
}
```

### Approach Comparison

| Approach | When to Use | Pros | Cons |
|----------|------------|------|------|
| **`Intent` + `Bundle`** | Multi-activity apps or simple flows | Simple, familiar | Boilerplate, not type-safe |
| **Navigation Component** | Modern single-activity apps | Type-safe (with Safe Args), visual graph | Requires setup |
| **Shared `ViewModel`** | Master-detail, tightly coupled Fragments in one `Activity` | Reactive, shared state | Not suitable for independent screens or deep links |
| **Deep Links** | External navigation, URLs | Sharable, indexable | Requires separate configuration |

### Best Practices

**Pass IDs, load data in detail screen:**
```kotlin
// ✅ CORRECT
intent.putExtra("USER_ID", userId)
// In DetailScreen:
viewModel.loadUser(userId)

// ❌ RISKY - large Parcelables can hit Binder transaction limit (~1MB)
intent.putExtra("USER", user) // May cause TransactionTooLargeException
```

**Use `ViewModel` for data loading:**
```kotlin
class UserDetailViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _user = MutableStateFlow<User?>(null)
    val user = _user.asStateFlow()

    fun loadUser(userId: Int) {
        viewModelScope.launch {
            _user.value = repository.getUserById(userId)
        }
    }
}
```

**For Compose Navigation, use explicit routes or typed destinations (example):**

The following shows one approach with route objects. Note that `composable<UserDetailRoute>()` and `toRoute()` style APIs require additional libraries; standard `androidx.navigation.compose` uses string routes and navArgument.

```kotlin
@Serializable
data class UserDetailRoute(val userId: Int)

NavHost(navController, startDestination = "userList") {
    composable("userList") {
        UserListScreen(
            onUserClick = { userId ->
                navController.navigate("userDetail/$userId")
            }
        )
    }
    composable(
        route = "userDetail/{userId}",
        arguments = listOf(navArgument("userId") { type = NavType.IntType })
    ) { backStackEntry ->
        val userId = backStackEntry.arguments?.getInt("userId")
            ?: error("userId is required")
        UserDetailScreen(userId = userId)
    }
}
```

---

## Follow-ups

1. What happens if you pass a large `Parcelable` object through an `Intent` and approach the Binder transaction size limit?
2. How does Navigation Component manage the back stack when using nested navigation graphs in a list-detail flow?
3. How would you design list-to-detail navigation differently for phones vs tablets (e.g., single-pane vs master-detail)?
4. What is the difference between using a shared `ViewModel` and Safe Args for passing data to a detail screen?
5. How do you handle deep links that must route through authentication before opening the detail screen?

## References

- [[c-fragments]] - `Fragment` fundamentals
- [[c-activity]] - `Activity` lifecycle and `Intent` handling
- [[c-viewmodel]] - `ViewModel` for data loading
- [[c-compose-navigation]] - Compose Navigation patterns
- https://developer.android.com/guide/navigation
- https://developer.android.com/guide/components/activities/parcelables-and-bundles

## Related Questions

### Prerequisites (Easier)
- [[q-fragment-basics--android--easy]] - `Fragment` basics
- [[q-what-are-intents-for--android--medium]] - `Intent` fundamentals
- [[q-what-is-viewmodel--android--medium]] - `ViewModel` basics

### Related (Same Level)
- [[q-compose-navigation-advanced--android--medium]] - Navigation in Compose
- [[q-activity-navigation-how-it-works--android--medium]] - `Activity` navigation details
- [[q-how-to-pass-data-from-one-fragment-to-another--android--medium]] - `Fragment` data passing
- [[q-bundle-data-types--android--medium]] - `Bundle` types and limits

### Advanced (Harder)
- [[q-pass-large-data-between-activities--android--hard]] - Handling large data transfers
- [[q-how-to-handle-the-situation-where-activity-can-open-multiple-times-due-to-deeplink--android--medium]] - Deep link navigation
- [[q-single-activity-approach--android--medium]] - Single `Activity` architecture
