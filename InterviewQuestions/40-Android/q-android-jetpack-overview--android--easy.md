---
tags:
  - android
  - jetpack
  - androidx
  - libraries
difficulty: easy
---

# Что такое Android Jetpack?

**English**: What is Android Jetpack?

## Answer

Android Jetpack — это набор библиотек, инструментов и рекомендаций от Google, предназначенных для упрощения разработки высококачественных Android-приложений. Jetpack помогает разработчикам следовать лучшим практикам, сокращает количество шаблонного кода и делает разработку проще и быстрее.

### Основные компоненты Jetpack

#### 1. Architecture Components

Компоненты для построения надежной архитектуры приложения.

```kotlin
// ViewModel - сохранение данных при изменении конфигурации
class UserViewModel : ViewModel() {
    private val _users = MutableLiveData<List<User>>()
    val users: LiveData<List<User>> = _users

    fun loadUsers() {
        viewModelScope.launch {
            _users.value = repository.getUsers()
        }
    }
}

// LiveData - наблюдаемые данные с учетом жизненного цикла
viewModel.users.observe(viewLifecycleOwner) { users ->
    adapter.submitList(users)
}

// Room - ORM для SQLite
@Entity(tableName = "users")
data class User(
    @PrimaryKey val id: Int,
    val name: String,
    val email: String
)

@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    suspend fun getAllUsers(): List<User>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: User)
}

@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}
```

#### 2. Navigation Component

Управление навигацией между экранами.

```kotlin
// Navigation Graph (nav_graph.xml)
<navigation xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:id="@+id/nav_graph"
    app:startDestination="@id/homeFragment">

    <fragment
        android:id="@+id/homeFragment"
        android:name="com.example.HomeFragment">
        <action
            android:id="@+id/action_home_to_details"
            app:destination="@id/detailsFragment" />
    </fragment>

    <fragment
        android:id="@+id/detailsFragment"
        android:name="com.example.DetailsFragment" />
</navigation>

// Навигация в коде
findNavController().navigate(R.id.action_home_to_details)

// С аргументами (Safe Args)
val action = HomeFragmentDirections.actionHomeToDetails(userId = 123)
findNavController().navigate(action)
```

#### 3. WorkManager

Фоновые задачи, гарантированное выполнение.

```kotlin
// Создание Worker
class UploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            val data = inputData.getString("file_path")
            uploadFile(data)
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}

// Запуск работы
val uploadRequest = OneTimeWorkRequestBuilder<UploadWorker>()
    .setInputData(workDataOf("file_path" to "/path/to/file"))
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
    )
    .build()

WorkManager.getInstance(context).enqueue(uploadRequest)

// Периодические задачи
val periodicWork = PeriodicWorkRequestBuilder<SyncWorker>(
    15, TimeUnit.MINUTES
).build()

WorkManager.getInstance(context).enqueue(periodicWork)
```

#### 4. DataStore

Современная замена SharedPreferences.

```kotlin
// Preferences DataStore
val Context.dataStore: DataStore<Preferences> by preferencesDataStore(
    name = "settings"
)

// Сохранение данных
suspend fun saveUserPreference(key: String, value: String) {
    context.dataStore.edit { preferences ->
        preferences[stringPreferencesKey(key)] = value
    }
}

// Чтение данных
val userPreferencesFlow: Flow<String> = context.dataStore.data
    .map { preferences ->
        preferences[stringPreferencesKey("user_name")] ?: "Unknown"
    }

// Proto DataStore (для типизированных данных)
val Context.userPreferencesStore: DataStore<UserPreferences> by dataStore(
    fileName = "user_prefs.pb",
    serializer = UserPreferencesSerializer
)
```

#### 5. Paging

Загрузка больших данных порциями.

```kotlin
// PagingSource
class UserPagingSource(
    private val apiService: ApiService
) : PagingSource<Int, User>() {

    override suspend fun load(
        params: LoadParams<Int>
    ): LoadResult<Int, User> {
        return try {
            val page = params.key ?: 1
            val response = apiService.getUsers(page, params.loadSize)

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
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    val users: Flow<PagingData<User>> = Pager(
        config = PagingConfig(pageSize = 20),
        pagingSourceFactory = { UserPagingSource(repository.apiService) }
    ).flow.cachedIn(viewModelScope)
}

// В Fragment/Activity
val adapter = UserPagingAdapter()
recyclerView.adapter = adapter

lifecycleScope.launch {
    viewModel.users.collectLatest { pagingData ->
        adapter.submitData(pagingData)
    }
}
```

#### 6. Hilt (Dependency Injection)

Упрощенный DI на основе Dagger.

```kotlin
// Application
@HiltAndroidApp
class MyApplication : Application()

// Activity
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository
}

// Module
@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    @Provides
    @Singleton
    fun provideRetrofit(): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    @Singleton
    fun provideApiService(retrofit: Retrofit): ApiService {
        return retrofit.create(ApiService::class.java)
    }
}

// ViewModel с Hilt
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel()
```

#### 7. Compose (Modern UI Toolkit)

Декларативный UI фреймворк.

```kotlin
@Composable
fun UserListScreen(
    viewModel: UserViewModel = hiltViewModel()
) {
    val users by viewModel.users.collectAsState()

    LazyColumn {
        items(users) { user ->
            UserItem(user = user)
        }
    }
}

@Composable
fun UserItem(user: User) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp)
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            AsyncImage(
                model = user.avatarUrl,
                contentDescription = null,
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape)
            )

            Spacer(modifier = Modifier.width(16.dp))

            Column {
                Text(
                    text = user.name,
                    style = MaterialTheme.typography.titleMedium
                )
                Text(
                    text = user.email,
                    style = MaterialTheme.typography.bodySmall
                )
            }
        }
    }
}
```

### Категории Jetpack библиотек

| Категория | Библиотеки | Назначение |
|-----------|-----------|------------|
| **Foundation** | AppCompat, KTX, Multidex | Базовая совместимость и расширения |
| **Architecture** | ViewModel, LiveData, Room, WorkManager, Navigation | Архитектура приложения |
| **UI** | Compose, Fragment, RecyclerView, ViewPager2 | Компоненты интерфейса |
| **Behavior** | Permissions, Notifications, Preferences | Поведение приложения |
| **Data** | DataStore, Paging, Room | Работа с данными |

### Преимущества использования Jetpack

**1. Обратная совместимость**

```kotlin
// Работает на Android 5.0+ вместо только на новых версиях
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // API доступен на старых версиях
        val color = ContextCompat.getColor(this, R.color.primary)
    }
}
```

**2. Следование best practices**

```kotlin
// ViewModel автоматически переживает изменения конфигурации
class MyViewModel : ViewModel() {
    // Данные сохраняются при повороте экрана
    val userData = MutableLiveData<User>()

    // Корутины автоматически отменяются
    fun loadData() {
        viewModelScope.launch {
            userData.value = repository.getUser()
        }
    }
}
```

**3. Меньше boilerplate кода**

```kotlin
// До Jetpack - ручное управление жизненным циклом
class OldActivity : Activity() {
    private var handler: Handler? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        handler = Handler()
    }

    override fun onDestroy() {
        handler?.removeCallbacksAndMessages(null)
        handler = null
        super.onDestroy()
    }
}

// С Jetpack - автоматическое управление
class NewActivity : AppCompatActivity() {
    private val viewModel: MyViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Автоматическая очистка при уничтожении
        viewModel.loadData()
    }
}
```

**4. Lifecycle-aware компоненты**

```kotlin
// Автоматическая подписка/отписка
viewModel.users.observe(viewLifecycleOwner) { users ->
    // Вызывается только когда Fragment активен
    adapter.submitList(users)
}

// Корутины с учетом жизненного цикла
lifecycleScope.launch {
    // Автоматически отменяется при уничтожении
    fetchData()
}

repeatOnLifecycle(Lifecycle.State.STARTED) {
    viewModel.uiState.collect { state ->
        // Собирается только когда Activity видима
        updateUI(state)
    }
}
```

### Зависимости

```gradle
// app/build.gradle
dependencies {
    // Core
    implementation "androidx.core:core-ktx:1.12.0"
    implementation "androidx.appcompat:appcompat:1.6.1"

    // Architecture
    implementation "androidx.lifecycle:lifecycle-viewmodel-ktx:2.6.2"
    implementation "androidx.lifecycle:lifecycle-livedata-ktx:2.6.2"
    implementation "androidx.lifecycle:lifecycle-runtime-ktx:2.6.2"

    // Room
    implementation "androidx.room:room-runtime:2.6.0"
    implementation "androidx.room:room-ktx:2.6.0"
    ksp "androidx.room:room-compiler:2.6.0"

    // Navigation
    implementation "androidx.navigation:navigation-fragment-ktx:2.7.5"
    implementation "androidx.navigation:navigation-ui-ktx:2.7.5"

    // WorkManager
    implementation "androidx.work:work-runtime-ktx:2.9.0"

    // DataStore
    implementation "androidx.datastore:datastore-preferences:1.0.0"

    // Paging
    implementation "androidx.paging:paging-runtime-ktx:3.2.1"

    // Hilt
    implementation "com.google.dagger:hilt-android:2.48"
    ksp "com.google.dagger:hilt-compiler:2.48"

    // Compose
    implementation platform("androidx.compose:compose-bom:2023.10.01")
    implementation "androidx.compose.ui:ui"
    implementation "androidx.compose.material3:material3"
    implementation "androidx.compose.ui:ui-tooling-preview"
    implementation "androidx.activity:activity-compose:1.8.0"
}
```

### Миграция на Jetpack

**Шаг 1: Перейти на AndroidX**

```gradle
// gradle.properties
android.useAndroidX=true
android.enableJetifier=true
```

**Шаг 2: Заменить старые компоненты**

```kotlin
// ❌ Старый код
import android.support.v7.app.AppCompatActivity
import android.arch.lifecycle.ViewModel

// ✓ Новый код
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.ViewModel
```

**Шаг 3: Внедрить Architecture Components**

```kotlin
// ❌ До (хранение данных в Activity)
class MainActivity : AppCompatActivity() {
    private var users: List<User>? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Данные теряются при повороте
        loadUsers()
    }
}

// ✓ После (ViewModel)
class MainActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Данные сохраняются
        viewModel.users.observe(this) { users ->
            updateUI(users)
        }
    }
}
```

**English**: Android Jetpack is a suite of libraries, tools, and guidance from Google for building high-quality Android apps. It includes **Architecture Components** (ViewModel, LiveData, Room), **Navigation** component, **WorkManager** for background tasks, **DataStore** (SharedPreferences replacement), **Paging** for large datasets, **Hilt** for DI, and **Compose** for modern UI. Benefits: backward compatibility, best practices, less boilerplate, lifecycle-aware components. All libraries use `androidx.*` namespace and work together seamlessly.
