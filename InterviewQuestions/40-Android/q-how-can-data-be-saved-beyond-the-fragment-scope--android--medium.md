---
topic: android
tags:
  - android
difficulty: medium
---

# How can data be saved beyond the fragment scope?

## Answer

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

## Answer (RU)
1. ViewModel: данные сохраняются в памяти до разрушения связанной Activity.

## Related Topics
- ViewModel lifecycle
- Fragment lifecycle
- SavedStateHandle
- Repository pattern
- SharedPreferences vs DataStore
