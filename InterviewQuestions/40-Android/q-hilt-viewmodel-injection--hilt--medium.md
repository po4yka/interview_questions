---
id: android-hilt-004
title: Hilt ViewModel Injection / Инъекция ViewModel в Hilt
aliases: [Hilt ViewModel, ViewModel Injection, HiltViewModel, ViewModel DI]
topic: android
subtopics: [di-hilt, architecture, viewmodel]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-hilt-setup-annotations--hilt--medium, q-hilt-assisted-injection--hilt--hard, q-viewmodel-pattern--android--easy]
created: 2026-01-23
updated: 2026-01-23
tags: [android/di-hilt, android/architecture, android/viewmodel, difficulty/medium, hilt, viewmodel, dependency-injection]

---
# Vopros (RU)
> Как работает инъекция ViewModel с Hilt? Объясните @HiltViewModel и различные способы получения ViewModel.

# Question (EN)
> How does ViewModel injection work with Hilt? Explain @HiltViewModel and the different ways to obtain a ViewModel.

---

## Otvet (RU)

Hilt значительно упрощает работу с ViewModel, предоставляя механизм constructor injection через аннотацию `@HiltViewModel`. Это устраняет необходимость в ручном создании ViewModelFactory.

### Базовая инъекция ViewModel

```kotlin
@HiltViewModel
class UserViewModel @Inject constructor(
    private val userRepository: UserRepository,
    private val analyticsService: AnalyticsService
) : ViewModel() {

    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()

    init {
        loadUsers()
    }

    private fun loadUsers() {
        viewModelScope.launch {
            _users.value = userRepository.getUsers()
        }
    }
}
```

### Получение ViewModel в Activity

```kotlin
@AndroidEntryPoint
class UserActivity : AppCompatActivity() {

    // Способ 1: Делегат by viewModels()
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_user)

        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.users.collect { users ->
                    updateUserList(users)
                }
            }
        }
    }
}
```

### Получение ViewModel в Fragment

```kotlin
@AndroidEntryPoint
class UserFragment : Fragment() {

    // ViewModel привязана к жизненному циклу Fragment
    private val viewModel: UserViewModel by viewModels()

    // Shared ViewModel - привязана к Activity
    private val sharedViewModel: SharedViewModel by activityViewModels()

    // ViewModel с кастомным ViewModelStoreOwner
    private val parentViewModel: ParentViewModel by viewModels(
        ownerProducer = { requireParentFragment() }
    )

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Использование ViewModel
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.users.collect { users ->
                    // Обновление UI
                }
            }
        }
    }
}
```

### SavedStateHandle - сохранение состояния

Hilt автоматически предоставляет `SavedStateHandle` в конструктор ViewModel:

```kotlin
@HiltViewModel
class DetailViewModel @Inject constructor(
    private val repository: UserRepository,
    private val savedStateHandle: SavedStateHandle // Автоматически инжектится
) : ViewModel() {

    // Получение аргументов навигации
    private val userId: String = savedStateHandle.get<String>("userId")
        ?: throw IllegalArgumentException("userId is required")

    // Сохранение состояния, которое переживет process death
    private val _searchQuery = savedStateHandle.getStateFlow("searchQuery", "")
    val searchQuery: StateFlow<String> = _searchQuery

    fun setSearchQuery(query: String) {
        savedStateHandle["searchQuery"] = query
    }

    // Работа с nullable значениями
    val selectedTab: Int?
        get() = savedStateHandle.get<Int>("selectedTab")

    fun selectTab(tabIndex: Int) {
        savedStateHandle["selectedTab"] = tabIndex
    }

    // LiveData из SavedStateHandle
    val filterLiveData: MutableLiveData<String> =
        savedStateHandle.getLiveData("filter", "all")
}
```

### ViewModel с Jetpack Compose

```kotlin
@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            MyTheme {
                MainScreen()
            }
        }
    }
}

@Composable
fun MainScreen(
    viewModel: MainViewModel = hiltViewModel() // Получение ViewModel в Compose
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    when (val state = uiState) {
        is UiState.Loading -> LoadingScreen()
        is UiState.Success -> ContentScreen(state.data)
        is UiState.Error -> ErrorScreen(state.message)
    }
}

// Nested Composable с той же ViewModel
@Composable
fun UserList(
    viewModel: MainViewModel = hiltViewModel() // Та же инстанция, если в том же NavBackStackEntry
) {
    val users by viewModel.users.collectAsStateWithLifecycle()

    LazyColumn {
        items(users) { user ->
            UserItem(user)
        }
    }
}
```

### ViewModel для Navigation Compose

```kotlin
@Composable
fun AppNavHost(
    navController: NavHostController = rememberNavController()
) {
    NavHost(
        navController = navController,
        startDestination = "home"
    ) {
        composable("home") {
            // ViewModel привязана к этому NavBackStackEntry
            HomeScreen(viewModel = hiltViewModel())
        }

        composable(
            route = "user/{userId}",
            arguments = listOf(navArgument("userId") { type = NavType.StringType })
        ) { backStackEntry ->
            // userId автоматически доступен в SavedStateHandle
            UserDetailScreen(viewModel = hiltViewModel())
        }

        // Shared ViewModel между несколькими destinations
        navigation(
            startDestination = "checkout/cart",
            route = "checkout"
        ) {
            composable("checkout/cart") {
                val parentEntry = remember(it) {
                    navController.getBackStackEntry("checkout")
                }
                // Shared ViewModel для всего flow checkout
                val checkoutViewModel: CheckoutViewModel = hiltViewModel(parentEntry)
                CartScreen(viewModel = checkoutViewModel)
            }

            composable("checkout/payment") {
                val parentEntry = remember(it) {
                    navController.getBackStackEntry("checkout")
                }
                val checkoutViewModel: CheckoutViewModel = hiltViewModel(parentEntry)
                PaymentScreen(viewModel = checkoutViewModel)
            }
        }
    }
}

@HiltViewModel
class UserDetailViewModel @Inject constructor(
    private val userRepository: UserRepository,
    savedStateHandle: SavedStateHandle
) : ViewModel() {

    // userId приходит из navigation arguments
    private val userId: String = checkNotNull(savedStateHandle["userId"])

    val user = userRepository.getUserFlow(userId)
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5_000),
            initialValue = null
        )
}
```

### Множественные ViewModel в одном экране

```kotlin
@AndroidEntryPoint
class DashboardFragment : Fragment() {

    // Основная ViewModel экрана
    private val dashboardViewModel: DashboardViewModel by viewModels()

    // ViewModel для виджета погоды
    private val weatherViewModel: WeatherViewModel by viewModels()

    // ViewModel для новостей
    private val newsViewModel: NewsViewModel by viewModels()

    // Shared ViewModel с Activity
    private val appStateViewModel: AppStateViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            // Параллельный сбор данных от разных ViewModel
            launch {
                dashboardViewModel.stats.collect { updateStats(it) }
            }
            launch {
                weatherViewModel.weather.collect { updateWeather(it) }
            }
            launch {
                newsViewModel.news.collect { updateNews(it) }
            }
        }
    }
}
```

### Dependency-граф для ViewModel

```kotlin
// Все зависимости должны быть доступны в ViewModelComponent или выше
@HiltViewModel
class OrderViewModel @Inject constructor(
    // Singleton scope - OK
    private val orderRepository: OrderRepository,

    // ViewModelScoped - OK
    private val orderValidator: OrderValidator,

    // SavedStateHandle - автоматически предоставляется
    private val savedStateHandle: SavedStateHandle,

    // @ApplicationContext - OK
    @ApplicationContext private val appContext: Context

    // @ActivityContext - НЕ доступен в ViewModelComponent!
    // private val activityContext: Context // ОШИБКА компиляции
) : ViewModel()

// Если нужен Activity context - используйте ActivityRetainedComponent
@Module
@InstallIn(ActivityRetainedComponent::class)
object ActivityRetainedModule {

    @Provides
    @ActivityRetainedScoped
    fun provideActivityDependentService(
        activity: Activity
    ): ActivityDependentService {
        return ActivityDependentService(activity)
    }
}
```

### Тестирование ViewModel с Hilt

```kotlin
@HiltAndroidTest
class UserViewModelTest {

    @get:Rule
    val hiltRule = HiltAndroidRule(this)

    @Inject
    lateinit var userRepository: UserRepository

    private lateinit var viewModel: UserViewModel

    @Before
    fun setup() {
        hiltRule.inject()
        viewModel = UserViewModel(
            userRepository = userRepository,
            savedStateHandle = SavedStateHandle()
        )
    }

    @Test
    fun `loadUsers should update state`() = runTest {
        // Arrange
        val expectedUsers = listOf(User("1", "John"))

        // Act
        viewModel.loadUsers()

        // Assert
        assertEquals(expectedUsers, viewModel.users.value)
    }
}

// Замена репозитория на fake для тестов
@Module
@TestInstallIn(
    components = [SingletonComponent::class],
    replaces = [RepositoryModule::class]
)
abstract class FakeRepositoryModule {

    @Binds
    @Singleton
    abstract fun bindUserRepository(
        impl: FakeUserRepository
    ): UserRepository
}
```

---

## Answer (EN)

Hilt significantly simplifies working with ViewModel by providing constructor injection mechanism through the `@HiltViewModel` annotation. This eliminates the need for manually creating ViewModelFactory.

### Basic ViewModel Injection

```kotlin
@HiltViewModel
class UserViewModel @Inject constructor(
    private val userRepository: UserRepository,
    private val analyticsService: AnalyticsService
) : ViewModel() {

    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()

    init {
        loadUsers()
    }

    private fun loadUsers() {
        viewModelScope.launch {
            _users.value = userRepository.getUsers()
        }
    }
}
```

### Obtaining ViewModel in Activity

```kotlin
@AndroidEntryPoint
class UserActivity : AppCompatActivity() {

    // Method 1: Delegate by viewModels()
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_user)

        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.users.collect { users ->
                    updateUserList(users)
                }
            }
        }
    }
}
```

### Obtaining ViewModel in Fragment

```kotlin
@AndroidEntryPoint
class UserFragment : Fragment() {

    // ViewModel bound to Fragment lifecycle
    private val viewModel: UserViewModel by viewModels()

    // Shared ViewModel - bound to Activity
    private val sharedViewModel: SharedViewModel by activityViewModels()

    // ViewModel with custom ViewModelStoreOwner
    private val parentViewModel: ParentViewModel by viewModels(
        ownerProducer = { requireParentFragment() }
    )

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Using ViewModel
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.users.collect { users ->
                    // Update UI
                }
            }
        }
    }
}
```

### SavedStateHandle - State Preservation

Hilt automatically provides `SavedStateHandle` to the ViewModel constructor:

```kotlin
@HiltViewModel
class DetailViewModel @Inject constructor(
    private val repository: UserRepository,
    private val savedStateHandle: SavedStateHandle // Automatically injected
) : ViewModel() {

    // Getting navigation arguments
    private val userId: String = savedStateHandle.get<String>("userId")
        ?: throw IllegalArgumentException("userId is required")

    // Saving state that survives process death
    private val _searchQuery = savedStateHandle.getStateFlow("searchQuery", "")
    val searchQuery: StateFlow<String> = _searchQuery

    fun setSearchQuery(query: String) {
        savedStateHandle["searchQuery"] = query
    }

    // Working with nullable values
    val selectedTab: Int?
        get() = savedStateHandle.get<Int>("selectedTab")

    fun selectTab(tabIndex: Int) {
        savedStateHandle["selectedTab"] = tabIndex
    }

    // LiveData from SavedStateHandle
    val filterLiveData: MutableLiveData<String> =
        savedStateHandle.getLiveData("filter", "all")
}
```

### ViewModel with Jetpack Compose

```kotlin
@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            MyTheme {
                MainScreen()
            }
        }
    }
}

@Composable
fun MainScreen(
    viewModel: MainViewModel = hiltViewModel() // Getting ViewModel in Compose
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    when (val state = uiState) {
        is UiState.Loading -> LoadingScreen()
        is UiState.Success -> ContentScreen(state.data)
        is UiState.Error -> ErrorScreen(state.message)
    }
}

// Nested Composable with the same ViewModel
@Composable
fun UserList(
    viewModel: MainViewModel = hiltViewModel() // Same instance if in same NavBackStackEntry
) {
    val users by viewModel.users.collectAsStateWithLifecycle()

    LazyColumn {
        items(users) { user ->
            UserItem(user)
        }
    }
}
```

### ViewModel for Navigation Compose

```kotlin
@Composable
fun AppNavHost(
    navController: NavHostController = rememberNavController()
) {
    NavHost(
        navController = navController,
        startDestination = "home"
    ) {
        composable("home") {
            // ViewModel bound to this NavBackStackEntry
            HomeScreen(viewModel = hiltViewModel())
        }

        composable(
            route = "user/{userId}",
            arguments = listOf(navArgument("userId") { type = NavType.StringType })
        ) { backStackEntry ->
            // userId automatically available in SavedStateHandle
            UserDetailScreen(viewModel = hiltViewModel())
        }

        // Shared ViewModel between multiple destinations
        navigation(
            startDestination = "checkout/cart",
            route = "checkout"
        ) {
            composable("checkout/cart") {
                val parentEntry = remember(it) {
                    navController.getBackStackEntry("checkout")
                }
                // Shared ViewModel for entire checkout flow
                val checkoutViewModel: CheckoutViewModel = hiltViewModel(parentEntry)
                CartScreen(viewModel = checkoutViewModel)
            }

            composable("checkout/payment") {
                val parentEntry = remember(it) {
                    navController.getBackStackEntry("checkout")
                }
                val checkoutViewModel: CheckoutViewModel = hiltViewModel(parentEntry)
                PaymentScreen(viewModel = checkoutViewModel)
            }
        }
    }
}

@HiltViewModel
class UserDetailViewModel @Inject constructor(
    private val userRepository: UserRepository,
    savedStateHandle: SavedStateHandle
) : ViewModel() {

    // userId comes from navigation arguments
    private val userId: String = checkNotNull(savedStateHandle["userId"])

    val user = userRepository.getUserFlow(userId)
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5_000),
            initialValue = null
        )
}
```

### Multiple ViewModels in One Screen

```kotlin
@AndroidEntryPoint
class DashboardFragment : Fragment() {

    // Main screen ViewModel
    private val dashboardViewModel: DashboardViewModel by viewModels()

    // Weather widget ViewModel
    private val weatherViewModel: WeatherViewModel by viewModels()

    // News ViewModel
    private val newsViewModel: NewsViewModel by viewModels()

    // Shared ViewModel with Activity
    private val appStateViewModel: AppStateViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            // Parallel data collection from different ViewModels
            launch {
                dashboardViewModel.stats.collect { updateStats(it) }
            }
            launch {
                weatherViewModel.weather.collect { updateWeather(it) }
            }
            launch {
                newsViewModel.news.collect { updateNews(it) }
            }
        }
    }
}
```

### Dependency Graph for ViewModel

```kotlin
// All dependencies must be available in ViewModelComponent or above
@HiltViewModel
class OrderViewModel @Inject constructor(
    // Singleton scope - OK
    private val orderRepository: OrderRepository,

    // ViewModelScoped - OK
    private val orderValidator: OrderValidator,

    // SavedStateHandle - automatically provided
    private val savedStateHandle: SavedStateHandle,

    // @ApplicationContext - OK
    @ApplicationContext private val appContext: Context

    // @ActivityContext - NOT available in ViewModelComponent!
    // private val activityContext: Context // Compilation ERROR
) : ViewModel()

// If Activity context is needed - use ActivityRetainedComponent
@Module
@InstallIn(ActivityRetainedComponent::class)
object ActivityRetainedModule {

    @Provides
    @ActivityRetainedScoped
    fun provideActivityDependentService(
        activity: Activity
    ): ActivityDependentService {
        return ActivityDependentService(activity)
    }
}
```

### Testing ViewModel with Hilt

```kotlin
@HiltAndroidTest
class UserViewModelTest {

    @get:Rule
    val hiltRule = HiltAndroidRule(this)

    @Inject
    lateinit var userRepository: UserRepository

    private lateinit var viewModel: UserViewModel

    @Before
    fun setup() {
        hiltRule.inject()
        viewModel = UserViewModel(
            userRepository = userRepository,
            savedStateHandle = SavedStateHandle()
        )
    }

    @Test
    fun `loadUsers should update state`() = runTest {
        // Arrange
        val expectedUsers = listOf(User("1", "John"))

        // Act
        viewModel.loadUsers()

        // Assert
        assertEquals(expectedUsers, viewModel.users.value)
    }
}

// Replacing repository with fake for tests
@Module
@TestInstallIn(
    components = [SingletonComponent::class],
    replaces = [RepositoryModule::class]
)
abstract class FakeRepositoryModule {

    @Binds
    @Singleton
    abstract fun bindUserRepository(
        impl: FakeUserRepository
    ): UserRepository
}
```

---

## Dopolnitelnye Voprosy (RU)

- Почему `@ActivityContext` недоступен в `@HiltViewModel`?
- Как передать runtime-параметры в ViewModel (см. Assisted Injection)?
- Как работает `hiltViewModel()` в Compose под капотом?
- Когда использовать `by viewModels()` vs `by activityViewModels()`?

## Follow-ups

- Why is `@ActivityContext` not available in `@HiltViewModel`?
- How do you pass runtime parameters to ViewModel (see Assisted Injection)?
- How does `hiltViewModel()` work in Compose under the hood?
- When to use `by viewModels()` vs `by activityViewModels()`?

---

## Ssylki (RU)

- [Hilt and Jetpack Integrations](https://developer.android.com/training/dependency-injection/hilt-jetpack)
- [ViewModel with Hilt](https://developer.android.com/training/dependency-injection/hilt-jetpack#viewmodels)

## References

- [Hilt and Jetpack Integrations](https://developer.android.com/training/dependency-injection/hilt-jetpack)
- [ViewModel with Hilt](https://developer.android.com/training/dependency-injection/hilt-jetpack#viewmodels)

---

## Svyazannye Voprosy (RU)

### Medium
- [[q-hilt-setup-annotations--hilt--medium]]
- [[q-hilt-qualifiers--hilt--medium]]
- [[q-viewmodel-pattern--android--easy]]
- [[q-hilt-testing--hilt--medium]]

### Hard
- [[q-hilt-assisted-injection--hilt--hard]]
- [[q-hilt-scopes--hilt--hard]]

## Related Questions

### Medium
- [[q-hilt-setup-annotations--hilt--medium]]
- [[q-hilt-qualifiers--hilt--medium]]
- [[q-viewmodel-pattern--android--easy]]
- [[q-hilt-testing--hilt--medium]]

### Hard
- [[q-hilt-assisted-injection--hilt--hard]]
- [[q-hilt-scopes--hilt--hard]]
