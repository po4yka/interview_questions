---
topic: android
tags:
  - android
  - android/architecture-clean
  - android/lifecycle
  - architecture-clean
  - databinding
  - lifecycle
  - livedata
  - navigation
  - paging
  - platform/android
  - room
  - viewmodel
  - workmanager
difficulty: easy
status: reviewed
---

# What libraries are in Architecture Components?

**Russian**: Какие библиотеки есть в Architecture Components?

**English**: What libraries are in Architecture Components?

## Answer

Android Architecture Components is a collection of libraries designed to help build robust, testable, and maintainable apps. The main libraries include:

1. **ViewModel** - Manages UI-related data in a lifecycle-conscious way
2. **LiveData** - Observable data holder that respects lifecycle
3. **Room** - SQLite database abstraction layer
4. **WorkManager** - Manages deferrable background work
5. **Data Binding** - Binds UI components to data sources declaratively
6. **Paging** - Loads and displays large datasets gradually
7. **Navigation** - Handles in-app navigation
8. **Lifecycle** - Manages activity and fragment lifecycles

---

## Library Details

### 1. ViewModel

Stores and manages UI-related data in a lifecycle-conscious way, surviving configuration changes.

```kotlin
class UserViewModel : ViewModel() {
    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user

    fun loadUser(userId: String) {
        viewModelScope.launch {
            _user.value = repository.getUser(userId)
        }
    }

    override fun onCleared() {
        super.onCleared()
        // Cleanup resources
    }
}

// In Activity/Fragment
class ProfileActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        viewModel.user.observe(this) { user ->
            nameTextView.text = user.name
        }
    }
}
```

**Benefits:**
- Survives configuration changes (screen rotation)
- Separates UI logic from UI controllers
- Lifecycle-aware via ViewModelScope
- Shared between fragments

---

### 2. LiveData

Observable data holder that respects the lifecycle of components like Activities and Fragments.

```kotlin
class TimerViewModel : ViewModel() {
    private val _seconds = MutableLiveData<Int>(0)
    val seconds: LiveData<Int> = _seconds

    fun startTimer() {
        viewModelScope.launch {
            repeat(60) {
                delay(1000)
                _seconds.value = (seconds.value ?: 0) + 1
            }
        }
    }
}

// In Activity
viewModel.seconds.observe(this) { seconds ->
    timerTextView.text = "$seconds seconds"
}
```

**Benefits:**
- No memory leaks (lifecycle-aware)
- Updates only when UI is active (STARTED/RESUMED state)
- No manual lifecycle management needed
- Data always consistent with lifecycle state

**LiveData vs Flow:**

```kotlin
// LiveData - lifecycle-aware by default
val userLiveData: LiveData<User> = repository.getUserLiveData()

// Flow - needs lifecycle scope
val userFlow: Flow<User> = repository.getUserFlow()
userFlow.flowWithLifecycle(lifecycle).collect { user ->
    // Process user
}
```

---

### 3. Room

Abstraction layer over SQLite, providing compile-time query verification and easy database migrations.

```kotlin
// Entity
@Entity(tableName = "users")
data class User(
    @PrimaryKey val id: String,
    @ColumnInfo(name = "full_name") val name: String,
    val email: String,
    val age: Int
)

// DAO
@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUser(userId: String): User?

    @Query("SELECT * FROM users ORDER BY full_name ASC")
    fun getAllUsersFlow(): Flow<List<User>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: User)

    @Delete
    suspend fun deleteUser(user: User)

    @Query("DELETE FROM users WHERE id = :userId")
    suspend fun deleteUserById(userId: String)
}

// Database
@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}

// Usage
class UserRepository(private val userDao: UserDao) {
    val allUsers: Flow<List<User>> = userDao.getAllUsersFlow()

    suspend fun getUser(userId: String): User? {
        return userDao.getUser(userId)
    }

    suspend fun insertUser(user: User) {
        userDao.insertUser(user)
    }
}
```

**Benefits:**
- Compile-time SQL query verification
- Simpler than raw SQLite
- Works with LiveData, Flow, RxJava
- Automatic migrations support
- Type-safe queries

---

### 4. WorkManager

Manages deferrable, guaranteed background work even if the app exits or device restarts.

```kotlin
class DataSyncWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            val userId = inputData.getString("user_id") ?: return Result.failure()

            syncUserData(userId)

            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }

    private suspend fun syncUserData(userId: String) {
        // Sync logic
    }
}

// Schedule work
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED)
    .setRequiresBatteryNotLow(true)
    .build()

val syncRequest = OneTimeWorkRequestBuilder<DataSyncWorker>()
    .setConstraints(constraints)
    .setInputData(workDataOf("user_id" to "user123"))
    .build()

WorkManager.getInstance(context).enqueue(syncRequest)

// Periodic work
val periodicSyncRequest = PeriodicWorkRequestBuilder<DataSyncWorker>(
    repeatInterval = 15,
    repeatIntervalTimeUnit = TimeUnit.MINUTES
).build()

WorkManager.getInstance(context).enqueueUniquePeriodicWork(
    "periodic-sync",
    ExistingPeriodicWorkPolicy.KEEP,
    periodicSyncRequest
)
```

**Benefits:**
- Guaranteed execution (survives app/device restarts)
- Respects system constraints (network, battery, storage)
- Backward compatible (uses JobScheduler, AlarmManager internally)
- Supports chaining and unique work

---

### 5. Data Binding

Binds UI components in layouts to data sources using declarative format.

```xml
<!-- activity_user.xml -->
<layout xmlns:android="http://schemas.android.com/apk/res/android">
    <data>
        <variable
            name="user"
            type="com.example.User" />
        <variable
            name="viewModel"
            type="com.example.UserViewModel" />
    </data>

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:orientation="vertical">

        <TextView
            android:text="@{user.name}"
            android:visibility="@{user.isActive ? View.VISIBLE : View.GONE}"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content" />

        <Button
            android:text="Save"
            android:onClick="@{() -> viewModel.saveUser(user)}"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content" />
    </LinearLayout>
</layout>
```

```kotlin
// In Activity
class UserActivity : AppCompatActivity() {
    private lateinit var binding: ActivityUserBinding
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = DataBindingUtil.setContentView(this, R.layout.activity_user)

        binding.user = User("John", true)
        binding.viewModel = viewModel
        binding.lifecycleOwner = this
    }
}
```

**Benefits:**
- Eliminates findViewById calls
- Type-safe view access
- Declarative UI updates
- Two-way data binding support

**Note:** ViewBinding is now preferred over Data Binding for simple view binding without complex logic in XML.

---

### 6. Paging

Loads and displays large datasets gradually in RecyclerView.

```kotlin
// PagingSource
class UserPagingSource(
    private val api: UserApi
) : PagingSource<Int, User>() {

    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, User> {
        return try {
            val page = params.key ?: 1
            val response = api.getUsers(page = page, pageSize = params.loadSize)

            LoadResult.Page(
                data = response.users,
                prevKey = if (page == 1) null else page - 1,
                nextKey = if (response.users.isEmpty()) null else page + 1
            )
        } catch (e: Exception) {
            LoadResult.Error(e)
        }
    }

    override fun getRefreshKey(state: PagingState<Int, User>): Int? {
        return state.anchorPosition?.let { anchorPosition ->
            state.closestPageToPosition(anchorPosition)?.prevKey?.plus(1)
                ?: state.closestPageToPosition(anchorPosition)?.nextKey?.minus(1)
        }
    }
}

// ViewModel
class UserListViewModel(private val api: UserApi) : ViewModel() {
    val users: Flow<PagingData<User>> = Pager(
        config = PagingConfig(
            pageSize = 20,
            enablePlaceholders = false,
            prefetchDistance = 5
        ),
        pagingSourceFactory = { UserPagingSource(api) }
    ).flow.cachedIn(viewModelScope)
}

// Adapter
class UserPagingAdapter : PagingDataAdapter<User, UserViewHolder>(USER_COMPARATOR) {
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): UserViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_user, parent, false)
        return UserViewHolder(view)
    }

    override fun onBindViewHolder(holder: UserViewHolder, position: Int) {
        val user = getItem(position)
        if (user != null) {
            holder.bind(user)
        }
    }

    companion object {
        private val USER_COMPARATOR = object : DiffUtil.ItemCallback<User>() {
            override fun areItemsTheSame(oldItem: User, newItem: User): Boolean {
                return oldItem.id == newItem.id
            }

            override fun areContentsTheSame(oldItem: User, newItem: User): Boolean {
                return oldItem == newItem
            }
        }
    }
}

// In Activity/Fragment
class UserListFragment : Fragment() {
    private val viewModel: UserListViewModel by viewModels()
    private val adapter = UserPagingAdapter()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        recyclerView.adapter = adapter

        lifecycleScope.launch {
            viewModel.users.collectLatest { pagingData ->
                adapter.submitData(pagingData)
            }
        }
    }
}
```

**Benefits:**
- Loads data on-demand (memory efficient)
- Built-in loading states and retry logic
- Works with Room, Retrofit, custom sources
- Handles placeholders and item updates

**Paging 3 vs Paging 2:**
- Paging 3 uses Kotlin Flow instead of LiveData
- Better support for coroutines
- Improved error handling
- More flexible architecture

---

### 7. Navigation

Handles fragment transactions and navigation between destinations.

```kotlin
// nav_graph.xml
<navigation xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:id="@+id/nav_graph"
    app:startDestination="@id/homeFragment">

    <fragment
        android:id="@+id/homeFragment"
        android:name="com.example.HomeFragment"
        android:label="Home">
        <action
            android:id="@+id/action_home_to_profile"
            app:destination="@id/profileFragment" />
    </fragment>

    <fragment
        android:id="@+id/profileFragment"
        android:name="com.example.ProfileFragment"
        android:label="Profile">
        <argument
            android:name="userId"
            app:argType="string" />
    </fragment>
</navigation>

// In Activity
class MainActivity : AppCompatActivity() {
    private lateinit var navController: NavController

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val navHostFragment = supportFragmentManager
            .findFragmentById(R.id.nav_host_fragment) as NavHostFragment
        navController = navHostFragment.navController

        setupActionBarWithNavController(navController)
    }

    override fun onSupportNavigateUp(): Boolean {
        return navController.navigateUp() || super.onSupportNavigateUp()
    }
}

// Navigate with arguments
class HomeFragment : Fragment() {
    private val navController by lazy { findNavController() }

    private fun openProfile(userId: String) {
        val action = HomeFragmentDirections.actionHomeToProfile(userId)
        navController.navigate(action)
    }
}

// Receive arguments
class ProfileFragment : Fragment() {
    private val args: ProfileFragmentArgs by navArgs()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        val userId = args.userId
        loadUserData(userId)
    }
}
```

**Benefits:**
- Type-safe argument passing with Safe Args
- Visualize navigation graph
- Deep link support
- Back stack management
- Animation transitions

---

### 8. Lifecycle

Lifecycle-aware components that respond to lifecycle changes.

```kotlin
class LocationObserver(private val context: Context) : DefaultLifecycleObserver {

    override fun onStart(owner: LifecycleOwner) {
        super.onStart(owner)
        startLocationUpdates()
    }

    override fun onStop(owner: LifecycleOwner) {
        super.onStop(owner)
        stopLocationUpdates()
    }

    private fun startLocationUpdates() {
        // Start listening to location
    }

    private fun stopLocationUpdates() {
        // Stop listening
    }
}

// Usage in Activity
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val locationObserver = LocationObserver(this)
        lifecycle.addObserver(locationObserver)
    }
}

// ProcessLifecycleOwner - App lifecycle
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()

        ProcessLifecycleOwner.get().lifecycle.addObserver(object : DefaultLifecycleObserver {
            override fun onStart(owner: LifecycleOwner) {
                // App came to foreground
            }

            override fun onStop(owner: LifecycleOwner) {
                // App went to background
            }
        })
    }
}
```

**Benefits:**
- Avoid memory leaks
- Automatic lifecycle management
- Reusable components
- Process-level lifecycle awareness

---

## Library Comparison Table

| Library | Purpose | Main Use Case |
|---------|---------|---------------|
| **ViewModel** | UI state management | Survive configuration changes, share data between fragments |
| **LiveData** | Observable data | Lifecycle-aware UI updates |
| **Room** | Database | Local data persistence with SQLite |
| **WorkManager** | Background work | Guaranteed background tasks (sync, uploads) |
| **Data Binding** | View binding | Declarative UI binding (less common now) |
| **Paging** | Data loading | Large datasets in lists (infinite scroll) |
| **Navigation** | Screen navigation | Fragment/Activity navigation with type safety |
| **Lifecycle** | Lifecycle awareness | Automatic resource management |

---

## Modern Alternatives

Some Architecture Components are being replaced or complemented by modern alternatives:

**Data Binding → ViewBinding**
```kotlin
// ViewBinding (preferred)
class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.textView.text = "Hello"
    }
}
```

**LiveData → StateFlow/SharedFlow**
```kotlin
// StateFlow (modern alternative)
class UserViewModel : ViewModel() {
    private val _user = MutableStateFlow<User?>(null)
    val user: StateFlow<User?> = _user.asStateFlow()

    fun loadUser(userId: String) {
        viewModelScope.launch {
            _user.value = repository.getUser(userId)
        }
    }
}

// In Fragment
lifecycleScope.launch {
    viewModel.user.collect { user ->
        nameTextView.text = user?.name
    }
}
```

**Fragments + Navigation → Jetpack Compose Navigation**
```kotlin
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = "home") {
        composable("home") { HomeScreen(navController) }
        composable("profile/{userId}") { backStackEntry ->
            val userId = backStackEntry.arguments?.getString("userId")
            ProfileScreen(userId)
        }
    }
}
```

---

## Summary

**Core Architecture Components:**

1. **ViewModel** - UI state + survives config changes
2. **LiveData** - Lifecycle-aware observable (or use StateFlow)
3. **Room** - SQLite abstraction with type safety
4. **WorkManager** - Guaranteed background work
5. **Data Binding** - Declarative UI binding (ViewBinding preferred)
6. **Paging** - Efficient large dataset loading
7. **Navigation** - Type-safe navigation graph
8. **Lifecycle** - Lifecycle-aware components

**When to use each:**
- **ViewModel**: Always for UI logic
- **LiveData/StateFlow**: Observable UI state
- **Room**: Local database needs
- **WorkManager**: Background tasks that must run
- **ViewBinding**: View references (not Data Binding)
- **Paging**: Lists with 100+ items
- **Navigation**: Multi-screen Fragment apps
- **Lifecycle**: Custom lifecycle-aware components

**Modern stack:**
- ViewModel + StateFlow/SharedFlow
- Room for database
- WorkManager for background work
- ViewBinding for views
- Jetpack Compose for UI (replaces Fragments + Data Binding)

---

## Ответ

Android Architecture Components - это набор библиотек, разработанных для создания надежных, тестируемых и поддерживаемых приложений. Основные библиотеки:

1. **ViewModel** - Управляет данными UI с учетом жизненного цикла
2. **LiveData** - Наблюдаемый holder данных, учитывающий lifecycle
3. **Room** - Слой абстракции над SQLite базой данных
4. **WorkManager** - Управляет отложенными фоновыми задачами
5. **Data Binding** - Декларативная привязка UI компонентов к данным
6. **Paging** - Постепенная загрузка и отображение больших наборов данных
7. **Navigation** - Управление навигацией внутри приложения
8. **Lifecycle** - Управление жизненными циклами activity и fragment

### Краткое описание каждой библиотеки:

**ViewModel:**
```kotlin
class UserViewModel : ViewModel() {
    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user

    fun loadUser(userId: String) {
        viewModelScope.launch {
            _user.value = repository.getUser(userId)
        }
    }
}
```
- Переживает изменения конфигурации (поворот экрана)
- Отделяет UI логику от UI контроллеров
- Может быть разделена между фрагментами

**LiveData:**
```kotlin
viewModel.user.observe(this) { user ->
    nameTextView.text = user.name
}
```
- Автоматически управляет подпиской в зависимости от lifecycle
- Нет утечек памяти
- Обновления только когда UI активен

**Room:**
```kotlin
@Entity
data class User(
    @PrimaryKey val id: String,
    val name: String
)

@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUser(userId: String): User?
}
```
- Проверка SQL запросов на этапе компиляции
- Проще чем чистый SQLite
- Поддержка LiveData, Flow, RxJava

**WorkManager:**
```kotlin
val workRequest = OneTimeWorkRequestBuilder<DataSyncWorker>()
    .setConstraints(constraints)
    .build()

WorkManager.getInstance(context).enqueue(workRequest)
```
- Гарантированное выполнение (переживает перезапуск приложения/устройства)
- Учитывает ограничения системы (сеть, батарея)
- Обратная совместимость

**Data Binding:**
```xml
<TextView
    android:text="@{user.name}"
    android:visibility="@{user.isActive ? View.VISIBLE : View.GONE}" />
```
- Устраняет findViewById вызовы
- Типобезопасный доступ к view
- Декларативные обновления UI

**Примечание:** ViewBinding теперь предпочтительнее Data Binding для простой привязки views.

**Paging:**
```kotlin
val users: Flow<PagingData<User>> = Pager(
    config = PagingConfig(pageSize = 20),
    pagingSourceFactory = { UserPagingSource(api) }
).flow
```
- Загружает данные по требованию (эффективно использует память)
- Встроенные состояния загрузки
- Работает с Room, Retrofit

**Navigation:**
```kotlin
val action = HomeFragmentDirections.actionHomeToProfile(userId)
navController.navigate(action)
```
- Типобезопасная передача аргументов с Safe Args
- Визуализация навиграфа
- Поддержка deep links
- Управление back stack

**Lifecycle:**
```kotlin
class LocationObserver : DefaultLifecycleObserver {
    override fun onStart(owner: LifecycleOwner) {
        startLocationUpdates()
    }

    override fun onStop(owner: LifecycleOwner) {
        stopLocationUpdates()
    }
}
```
- Избегание утечек памяти
- Автоматическое управление lifecycle
- Переиспользуемые компоненты

### Современные альтернативы:

- **Data Binding → ViewBinding** (проще, без логики в XML)
- **LiveData → StateFlow/SharedFlow** (Kotlin Flow, больше функциональности)
- **Fragments + Navigation → Jetpack Compose** (современный UI toolkit)

### Таблица сравнения:

| Библиотека | Назначение | Основное использование |
|-----------|------------|------------------------|
| ViewModel | Управление UI состоянием | Переживание поворотов экрана, шаринг данных |
| LiveData | Наблюдаемые данные | Lifecycle-aware обновления UI |
| Room | База данных | Локальное хранение данных с SQLite |
| WorkManager | Фоновая работа | Гарантированные фоновые задачи (синхронизация) |
| Data Binding | Привязка view | Декларативная привязка UI (сейчас реже) |
| Paging | Загрузка данных | Большие списки (бесконечная прокрутка) |
| Navigation | Навигация | Навигация между Fragment/Activity с типобезопасностью |
| Lifecycle | Lifecycle awareness | Автоматическое управление ресурсами |

### Когда использовать:

- **ViewModel**: Всегда для UI логики
- **LiveData/StateFlow**: Наблюдаемое состояние UI
- **Room**: Локальная база данных
- **WorkManager**: Фоновые задачи, которые должны выполниться
- **ViewBinding**: Доступ к view (не Data Binding)
- **Paging**: Списки с 100+ элементами
- **Navigation**: Многоэкранные Fragment приложения
- **Lifecycle**: Кастомные lifecycle-aware компоненты

**Современный стек:**
- ViewModel + StateFlow/SharedFlow
- Room для базы данных
- WorkManager для фоновой работы
- ViewBinding для views
- Jetpack Compose для UI (заменяет Fragments + Data Binding)

