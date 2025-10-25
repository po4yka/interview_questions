---
id: 20251016-164009
title: "List To Detail Navigation / Навигация от списка к детализации"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-memory-leak-detection--performance--medium, q-measure-project-size--android--easy, q-view-fundamentals--android--easy]
created: 2025-10-15
tags: [android/navigation, bundle, data-passing, intent, master-detail, navigation, navigation-component, ui-patterns, viewmodel, difficulty/medium]
---

# С помощью чего делается переход со списков на деталки?

**English**: How do you implement navigation from a list to detail screens?

## Answer (EN)
To implement transitions from a **list** to an **item detail screen** in Android, you use **Intent**, **Bundle**, **ViewModel**, and navigation tools such as **Navigation Component**.

The basic approach uses **Intent and Bundle** to pass data between Activities. The modern approach involves using **Navigation Component** with a navigation graph and passing data through arguments.

## Approach 1: Intent + Bundle (Activity to Activity)

### Basic Implementation

```kotlin
// List Activity
class UserListActivity : AppCompatActivity() {
    private lateinit var adapter: UserAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        adapter = UserAdapter { user ->
            // Navigate to detail
            openUserDetail(user)
        }

        recyclerView.adapter = adapter
    }

    private fun openUserDetail(user: User) {
        val intent = Intent(this, UserDetailActivity::class.java)
        intent.putExtra("USER_ID", user.id)
        intent.putExtra("USER_NAME", user.name)
        intent.putExtra("USER_EMAIL", user.email)
        startActivity(intent)
    }
}

// Detail Activity
class UserDetailActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val userId = intent.getIntExtra("USER_ID", -1)
        val userName = intent.getStringExtra("USER_NAME")
        val userEmail = intent.getStringExtra("USER_EMAIL")

        // Display user details
        nameTextView.text = userName
        emailTextView.text = userEmail
    }
}
```

### Passing Parcelable Objects

```kotlin
// Make User Parcelable
@Parcelize
data class User(
    val id: Int,
    val name: String,
    val email: String,
    val avatarUrl: String
) : Parcelable

// List Activity
private fun openUserDetail(user: User) {
    val intent = Intent(this, UserDetailActivity::class.java)
    intent.putExtra("USER", user)  // Pass entire object
    startActivity(intent)
}

// Detail Activity
class UserDetailActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val user = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            intent.getParcelableExtra("USER", User::class.java)
        } else {
            @Suppress("DEPRECATION")
            intent.getParcelableExtra("USER")
        }

        user?.let {
            displayUser(it)
        }
    }

    private fun displayUser(user: User) {
        nameTextView.text = user.name
        emailTextView.text = user.email
        Glide.with(this).load(user.avatarUrl).into(avatarImageView)
    }
}
```

---

## Approach 2: Navigation Component (Fragment to Fragment)

### Setup Navigation Graph

**res/navigation/nav_graph.xml:**

```xml
<navigation xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:id="@+id/nav_graph"
    app:startDestination="@id/userListFragment">

    <fragment
        android:id="@+id/userListFragment"
        android:name="com.example.UserListFragment">
        <action
            android:id="@+id/action_list_to_detail"
            app:destination="@id/userDetailFragment" />
    </fragment>

    <fragment
        android:id="@+id/userDetailFragment"
        android:name="com.example.UserDetailFragment">
        <argument
            android:name="userId"
            app:argType="integer" />
        <argument
            android:name="userName"
            app:argType="string" />
    </fragment>
</navigation>
```

### List Fragment

```kotlin
class UserListFragment : Fragment() {
    private lateinit var adapter: UserAdapter

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        adapter = UserAdapter { user ->
            // Navigate to detail with arguments
            val action = UserListFragmentDirections
                .actionListToDetail(user.id, user.name)
            findNavController().navigate(action)
        }

        recyclerView.adapter = adapter
    }
}

// RecyclerView Adapter
class UserAdapter(
    private val onItemClick: (User) -> Unit
) : RecyclerView.Adapter<UserAdapter.ViewHolder>() {

    private var users = listOf<User>()

    inner class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        fun bind(user: User) {
            itemView.findViewById<TextView>(R.id.nameText).text = user.name
            itemView.setOnClickListener { onItemClick(user) }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_user, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(users[position])
    }

    override fun getItemCount() = users.size

    fun submitList(newUsers: List<User>) {
        users = newUsers
        notifyDataSetChanged()
    }
}
```

### Detail Fragment

```kotlin
class UserDetailFragment : Fragment() {
    private val args: UserDetailFragmentArgs by navArgs()
    private val viewModel: UserDetailViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Get arguments
        val userId = args.userId
        val userName = args.userName

        // Load full user data
        viewModel.loadUser(userId)

        // Observe data
        viewModel.user.observe(viewLifecycleOwner) { user ->
            displayUser(user)
        }
    }

    private fun displayUser(user: User) {
        nameTextView.text = user.name
        emailTextView.text = user.email
        bioTextView.text = user.bio
    }
}
```

---

## Approach 3: Shared ViewModel (Recommended for Fragments)

```kotlin
// Shared ViewModel (activity-scoped)
class UserViewModel : ViewModel() {
    private val _selectedUser = MutableLiveData<User?>()
    val selectedUser: LiveData<User?> = _selectedUser

    fun selectUser(user: User) {
        _selectedUser.value = user
    }
}

// List Fragment
class UserListFragment : Fragment() {
    private val viewModel: UserViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        adapter = UserAdapter { user ->
            // Store user in shared ViewModel
            viewModel.selectUser(user)

            // Navigate
            findNavController().navigate(R.id.action_list_to_detail)
        }
    }
}

// Detail Fragment
class UserDetailFragment : Fragment() {
    private val viewModel: UserViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Observe selected user from shared ViewModel
        viewModel.selectedUser.observe(viewLifecycleOwner) { user ->
            user?.let { displayUser(it) }
        }
    }
}
```

---

## Approach 4: Safe Args Plugin (Type-Safe)

**build.gradle (project):**

```kotlin
buildscript {
    dependencies {
        classpath "androidx.navigation:navigation-safe-args-gradle-plugin:2.7.0"
    }
}
```

**build.gradle (app):**

```kotlin
plugins {
    id 'androidx.navigation.safeargs.kotlin'
}
```

**Navigation Graph:**

```xml
<fragment
    android:id="@+id/userDetailFragment"
    android:name="com.example.UserDetailFragment">
    <argument
        android:name="user"
        app:argType="com.example.User" />  <!-- Custom type -->
</fragment>
```

**Usage:**

```kotlin
// List Fragment - Type-safe navigation
val action = UserListFragmentDirections.actionListToDetail(user)
findNavController().navigate(action)

// Detail Fragment - Type-safe argument retrieval
val args: UserDetailFragmentArgs by navArgs()
val user = args.user
```

---

## Approach 5: Deep Links

```xml
<fragment
    android:id="@+id/userDetailFragment"
    android:name="com.example.UserDetailFragment">
    <argument
        android:name="userId"
        app:argType="integer" />
    <deepLink
        app:uri="myapp://user/{userId}" />
</fragment>
```

**Navigate via URI:**

```kotlin
val uri = Uri.parse("myapp://user/$userId")
findNavController().navigate(uri)
```

---

## Comparison Table

| Approach | Pros | Cons | Use Case |
|----------|------|------|----------|
| **Intent + Bundle** | Simple, familiar | Boilerplate, not type-safe | Activity-based apps |
| **Intent + Parcelable** | Pass entire objects | Size limit (1MB) | Small to medium objects |
| **Navigation Component** | Type-safe, visual graph | Learning curve | Modern Fragment-based apps |
| **Shared ViewModel** | Simple, reactive | Activity-scoped only | Related screens |
| **Safe Args** | Compile-time safety | Build overhead | Complex navigation |
| **Deep Links** | External navigation | Setup required | Shareable URLs |

---

## Best Practices

**1. Pass only necessary data:**

```kotlin
// - BAD - Pass entire list
intent.putParcelableArrayListExtra("USERS", ArrayList(allUsers))

// - GOOD - Pass only ID
intent.putExtra("USER_ID", userId)

// Load full data in detail screen
viewModel.loadUser(userId)
```

**2. Use ViewModel for data loading:**

```kotlin
class UserDetailViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user

    fun loadUser(userId: Int) {
        viewModelScope.launch {
            _user.value = repository.getUserById(userId)
        }
    }
}
```

**3. Handle configuration changes:**

```kotlin
// ViewModel survives rotation
class UserDetailFragment : Fragment() {
    private val viewModel: UserDetailViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Only load if not already loaded
        if (viewModel.user.value == null) {
            viewModel.loadUser(args.userId)
        }
    }
}
```

---

## Summary

**Main approaches for list-to-detail navigation:**

1. **Intent + Bundle** - Pass data between Activities
2. **Navigation Component** - Modern, type-safe Fragment navigation
3. **Shared ViewModel** - Share data between Fragments
4. **Safe Args** - Compile-time type safety
5. **Deep Links** - URI-based navigation

**Recommended approach:**
- **Single Activity + Navigation Component + Safe Args** for modern apps
- **Pass IDs, not objects** - load full data in detail screen
- **Use ViewModel** for data management

## Ответ (RU)

Для реализации переходов от **списка** к экрану **деталей элемента** в Android используются **Intent**, **Bundle**, **ViewModel** и инструменты навигации такие как **Navigation Component**.

Базовый подход использует **Intent и Bundle** для передачи данных между активностями. Современный подход включает использование **Navigation Component** с графом навигации и передачей данных через аргументы.

## Подход 1: Intent + Bundle (Activity to Activity)

### Базовая реализация

```kotlin
// Activity со списком
class UserListActivity : AppCompatActivity() {
    private lateinit var adapter: UserAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        adapter = UserAdapter { user ->
            // Навигация к деталям
            openUserDetail(user)
        }

        recyclerView.adapter = adapter
    }

    private fun openUserDetail(user: User) {
        val intent = Intent(this, UserDetailActivity::class.java)
        intent.putExtra("USER_ID", user.id)
        intent.putExtra("USER_NAME", user.name)
        intent.putExtra("USER_EMAIL", user.email)
        startActivity(intent)
    }
}

// Activity с деталями
class UserDetailActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val userId = intent.getIntExtra("USER_ID", -1)
        val userName = intent.getStringExtra("USER_NAME")
        val userEmail = intent.getStringExtra("USER_EMAIL")

        // Отображение деталей пользователя
        nameTextView.text = userName
        emailTextView.text = userEmail
    }
}
```

### Передача Parcelable объектов

```kotlin
// Сделать User Parcelable
@Parcelize
data class User(
    val id: Int,
    val name: String,
    val email: String,
    val avatarUrl: String
) : Parcelable

// Activity со списком
private fun openUserDetail(user: User) {
    val intent = Intent(this, UserDetailActivity::class.java)
    intent.putExtra("USER", user)  // Передача всего объекта
    startActivity(intent)
}

// Activity с деталями
class UserDetailActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val user = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            intent.getParcelableExtra("USER", User::class.java)
        } else {
            @Suppress("DEPRECATION")
            intent.getParcelableExtra("USER")
        }

        user?.let {
            displayUser(it)
        }
    }

    private fun displayUser(user: User) {
        nameTextView.text = user.name
        emailTextView.text = user.email
        Glide.with(this).load(user.avatarUrl).into(avatarImageView)
    }
}
```

## Подход 2: Navigation Component (Fragment to Fragment)

### Настройка графа навигации

**res/navigation/nav_graph.xml:**

```xml
<navigation xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:id="@+id/nav_graph"
    app:startDestination="@id/userListFragment">

    <fragment
        android:id="@+id/userListFragment"
        android:name="com.example.UserListFragment">
        <action
            android:id="@+id/action_list_to_detail"
            app:destination="@id/userDetailFragment" />
    </fragment>

    <fragment
        android:id="@+id/userDetailFragment"
        android:name="com.example.UserDetailFragment">
        <argument
            android:name="userId"
            app:argType="integer" />
        <argument
            android:name="userName"
            app:argType="string" />
    </fragment>
</navigation>
```

### Fragment со списком

```kotlin
class UserListFragment : Fragment() {
    private lateinit var adapter: UserAdapter

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        adapter = UserAdapter { user ->
            // Навигация к деталям с аргументами
            val action = UserListFragmentDirections
                .actionListToDetail(user.id, user.name)
            findNavController().navigate(action)
        }

        recyclerView.adapter = adapter
    }
}
```

### Fragment с деталями

```kotlin
class UserDetailFragment : Fragment() {
    private val args: UserDetailFragmentArgs by navArgs()
    private val viewModel: UserDetailViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Получение аргументов
        val userId = args.userId
        val userName = args.userName

        // Загрузка полных данных пользователя
        viewModel.loadUser(userId)

        // Наблюдение за данными
        viewModel.user.observe(viewLifecycleOwner) { user ->
            displayUser(user)
        }
    }

    private fun displayUser(user: User) {
        nameTextView.text = user.name
        emailTextView.text = user.email
        bioTextView.text = user.bio
    }
}
```

## Подход 3: Shared ViewModel (Рекомендуется для Fragments)

```kotlin
// Общая ViewModel (область activity)
class UserViewModel : ViewModel() {
    private val _selectedUser = MutableLiveData<User?>()
    val selectedUser: LiveData<User?> = _selectedUser

    fun selectUser(user: User) {
        _selectedUser.value = user
    }
}

// Fragment со списком
class UserListFragment : Fragment() {
    private val viewModel: UserViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        adapter = UserAdapter { user ->
            // Сохранить пользователя в общей ViewModel
            viewModel.selectUser(user)

            // Навигация
            findNavController().navigate(R.id.action_list_to_detail)
        }
    }
}

// Fragment с деталями
class UserDetailFragment : Fragment() {
    private val viewModel: UserViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Наблюдение за выбранным пользователем из общей ViewModel
        viewModel.selectedUser.observe(viewLifecycleOwner) { user ->
            user?.let { displayUser(it) }
        }
    }
}
```

## Сравнительная таблица

| Подход | Преимущества | Недостатки | Сценарий использования |
|--------|-------------|-----------|----------------------|
| **Intent + Bundle** | Простой, знакомый | Boilerplate, не type-safe | Приложения на основе Activity |
| **Intent + Parcelable** | Передача целых объектов | Ограничение размера (1MB) | Небольшие и средние объекты |
| **Navigation Component** | Type-safe, визуальный граф | Кривая обучения | Современные приложения на основе Fragment |
| **Shared ViewModel** | Простой, реактивный | Только область activity | Связанные экраны |
| **Safe Args** | Безопасность во время компиляции | Overhead сборки | Сложная навигация |
| **Deep Links** | Внешняя навигация | Требуется настройка | Общие URL |

## Лучшие практики

**1. Передавайте только необходимые данные:**

```kotlin
// ПЛОХО - Передача всего списка
intent.putParcelableArrayListExtra("USERS", ArrayList(allUsers))

// ХОРОШО - Передача только ID
intent.putExtra("USER_ID", userId)

// Загрузка полных данных на экране деталей
viewModel.loadUser(userId)
```

**2. Используйте ViewModel для загрузки данных:**

```kotlin
class UserDetailViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user

    fun loadUser(userId: Int) {
        viewModelScope.launch {
            _user.value = repository.getUserById(userId)
        }
    }
}
```

**3. Обрабатывайте изменения конфигурации:**

```kotlin
// ViewModel переживает поворот экрана
class UserDetailFragment : Fragment() {
    private val viewModel: UserDetailViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Загружать только если еще не загружено
        if (viewModel.user.value == null) {
            viewModel.loadUser(args.userId)
        }
    }
}
```

## Резюме

**Основные подходы для навигации список-детали:**

1. **Intent + Bundle** - Передача данных между активностями
2. **Navigation Component** - Современная, type-safe навигация Fragment
3. **Shared ViewModel** - Совместное использование данных между Fragment
4. **Safe Args** - Безопасность типов во время компиляции
5. **Deep Links** - Навигация на основе URI

**Рекомендуемый подход:**
- **Single Activity + Navigation Component + Safe Args** для современных приложений
- **Передавайте ID, а не объекты** - загружайте полные данные на экране деталей
- **Используйте ViewModel** для управления данными

Для реализации переходов от списка к экрану деталей в Android используются Intent, Bundle, ViewModel и Navigation Component. Современный подход предполагает использование Navigation Component с Safe Args для type-safe навигации и передачи только ID элементов, загружая полные данные через ViewModel в экране деталей.


---

## Related Questions

### Related (Medium)
- [[q-compose-navigation-advanced--android--medium]] - Navigation
- [[q-compose-navigation-advanced--android--medium]] - Navigation
- [[q-activity-navigation-how-it-works--android--medium]] - Navigation
- [[q-how-to-handle-the-situation-where-activity-can-open-multiple-times-due-to-deeplink--android--medium]] - Navigation
- [[q-what-navigation-methods-do-you-know--android--medium]] - Navigation
