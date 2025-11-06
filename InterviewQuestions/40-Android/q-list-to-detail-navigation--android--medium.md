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
updated: 2025-10-30
tags: [android/fragment, android/intents-deeplinks, android/ui-navigation, bundle, difficulty/medium, navigation-component, parcelable]
---

# Вопрос (RU)

> С помощью чего делается переход со списков на деталки в Android?

# Question (EN)

> How do you implement navigation from a list to detail screens in Android?

---

## Ответ (RU)

Переход от списка к экрану деталей реализуется через **`Intent` + `Bundle`** (для `Activity`), **Navigation Component** (для `Fragment`) или **shared `ViewModel`** (для связанных экранов). Современный подход — Single `Activity` архитектура с Navigation Component и Safe Args для type-safe передачи аргументов.

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
<fragment android:id="@+id/userDetailFragment">
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

**3. Shared `ViewModel` (для связанных экранов)**

Для master-detail layout или связанных `Fragment`:

```kotlin
// Activity-scoped ViewModel
class UserViewModel : ViewModel() {
    private val _selectedUser = MutableLiveData<User?>()
    val selectedUser: LiveData<User?> = _selectedUser

    fun selectUser(user: User) {
        _selectedUser.value = user
    }
}

// ListFragment
class UserListFragment : Fragment() {
    private val sharedViewModel: UserViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        adapter = UserAdapter { user ->
            sharedViewModel.selectUser(user) // ✅ Сохранить в shared ViewModel
            findNavController().navigate(R.id.action_list_to_detail)
        }
    }
}

// DetailFragment читает из той же ViewModel
class UserDetailFragment : Fragment() {
    private val sharedViewModel: UserViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        sharedViewModel.selectedUser.observe(viewLifecycleOwner) { user ->
            user?.let { displayUser(it) }
        }
    }
}
```

### Сравнение Подходов

| Подход | Когда использовать | Преимущества | Недостатки |
|--------|-------------------|-------------|-----------|
| **`Intent` + `Bundle`** | Legacy multi-activity apps | Простой, знакомый | Boilerplate, не type-safe |
| **Navigation Component** | Modern single-activity apps | Type-safe, visual graph | Требует setup |
| **Shared `ViewModel`** | Master-detail, связанные экраны | Реактивный, простой | Только для `Fragment` в одной `Activity` |
| **Deep Links** | External navigation, URLs | Sharable, indexed | Требует отдельной настройки |

### Best Practices

**Передавайте ID, загружайте данные в экране деталей:**
```kotlin
// ✅ ПРАВИЛЬНО
intent.putExtra("USER_ID", userId)
// В DetailScreen:
viewModel.loadUser(userId)

// ❌ НЕПРАВИЛЬНО - обход Parcelable size limit (1MB)
intent.putExtra("USER", user) // Может упасть на больших объектах
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

**Для Compose Navigation используйте type-safe destinations:**
```kotlin
// Compose Navigation
@Serializable
data class UserDetailRoute(val userId: Int)

NavHost(navController, startDestination = UserListRoute) {
    composable<UserListRoute> {
        UserListScreen(
            onUserClick = { userId ->
                navController.navigate(UserDetailRoute(userId))
            }
        )
    }
    composable<UserDetailRoute> { backStackEntry ->
        val route = backStackEntry.toRoute<UserDetailRoute>()
        UserDetailScreen(userId = route.userId)
    }
}
```

## Answer (EN)

Navigation from list to detail screens is implemented via **`Intent` + `Bundle`** (for `Activity`), **Navigation Component** (for `Fragment`), or **shared `ViewModel`** (for related screens). Modern approach is Single `Activity` architecture with Navigation Component and Safe Args for type-safe argument passing.

### Main Approaches

**1. `Intent` + `Bundle` (`Activity` → `Activity`)**

Pass ID only, not the entire object:

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
<fragment android:id="@+id/userDetailFragment">
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

**3. Shared `ViewModel` (for related screens)**

For master-detail layout or related Fragments:

```kotlin
// Activity-scoped ViewModel
class UserViewModel : ViewModel() {
    private val _selectedUser = MutableLiveData<User?>()
    val selectedUser: LiveData<User?> = _selectedUser

    fun selectUser(user: User) {
        _selectedUser.value = user
    }
}

// ListFragment
class UserListFragment : Fragment() {
    private val sharedViewModel: UserViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        adapter = UserAdapter { user ->
            sharedViewModel.selectUser(user) // ✅ Store in shared ViewModel
            findNavController().navigate(R.id.action_list_to_detail)
        }
    }
}

// DetailFragment reads from same ViewModel
class UserDetailFragment : Fragment() {
    private val sharedViewModel: UserViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        sharedViewModel.selectedUser.observe(viewLifecycleOwner) { user ->
            user?.let { displayUser(it) }
        }
    }
}
```

### Approach Comparison

| Approach | When to Use | Pros | Cons |
|----------|------------|------|------|
| **`Intent` + `Bundle`** | Legacy multi-activity apps | Simple, familiar | Boilerplate, not type-safe |
| **Navigation Component** | Modern single-activity apps | Type-safe, visual graph | Requires setup |
| **Shared `ViewModel`** | Master-detail, related screens | Reactive, simple | `Fragment`-only in same `Activity` |
| **Deep Links** | External navigation, URLs | Sharable, indexed | Requires separate configuration |

### Best Practices

**Pass IDs, load data in detail screen:**
```kotlin
// ✅ CORRECT
intent.putExtra("USER_ID", userId)
// In DetailScreen:
viewModel.loadUser(userId)

// ❌ WRONG - hits Parcelable size limit (1MB)
intent.putExtra("USER", user) // May crash on large objects
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

**For Compose Navigation use type-safe destinations:**
```kotlin
// Compose Navigation
@Serializable
data class UserDetailRoute(val userId: Int)

NavHost(navController, startDestination = UserListRoute) {
    composable<UserListRoute> {
        UserListScreen(
            onUserClick = { userId ->
                navController.navigate(UserDetailRoute(userId))
            }
        )
    }
    composable<UserDetailRoute> { backStackEntry ->
        val route = backStackEntry.toRoute<UserDetailRoute>()
        UserDetailScreen(userId = route.userId)
    }
}
```

---

## Follow-ups

1. What happens if you pass a large `Parcelable` object through `Intent` and exceed 1MB TransactionTooLargeException limit?
2. How does Navigation Component handle back stack when using nested navigation graphs?
3. How do you implement master-detail pattern for tablets vs phones with different layouts?
4. What's the difference between `navigate()` and `popUpTo()` + `navigate()` in Navigation Component?
5. How do you handle deep links that require authentication before showing the detail screen?

## References

- [[c-fragments]] - `Fragment` fundamentals
- [[c-activity]] - `Activity` lifecycle and `Intent` handling
- [[c-viewmodel]] - `ViewModel` for data loading
- [[c-compose-navigation]] - Compose Navigation patterns
- [Navigation Component Guide](https://developer.android.com/guide/navigation)
- [`Parcelable` and `Bundle` Best Practices](https://developer.android.com/guide/components/activities/parcelables-and-bundles)

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
