---
id: android-koin-004
title: Koin ViewModel Injection / Инъекция ViewModel в Koin
aliases:
- Koin ViewModel
- viewModel DSL
- koinViewModel
topic: android
subtopics:
- di-koin
- dependency-injection
- architecture
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-koin-setup-modules--koin--medium
- q-koin-inject-get--koin--medium
- q-koin-compose--koin--medium
created: 2026-01-23
updated: 2026-01-23
tags:
- android/di-koin
- android/viewmodel
- dependency-injection
- difficulty/medium
- koin
anki_cards:
- slug: android-koin-004-0-en
  language: en
- slug: android-koin-004-0-ru
  language: ru
---
# Vopros (RU)
> Как использовать Koin для инъекции ViewModel? Объясните viewModel DSL и интеграцию с Activity/Fragment и Compose.

# Question (EN)
> How do you use Koin for ViewModel injection? Explain the viewModel DSL and integration with Activity/Fragment and Compose.

---

## Otvet (RU)

Koin предоставляет специальный DSL для работы с Android ViewModel, который автоматически интегрируется с `ViewModelStore` и правильно управляет жизненным циклом.

### Подключение зависимостей

```kotlin
// build.gradle.kts
dependencies {
    implementation("io.insert-koin:koin-android:3.5.6")

    // Для Jetpack Compose
    implementation("io.insert-koin:koin-androidx-compose:3.5.6")
}
```

### Определение ViewModel в модуле

```kotlin
val viewModelModule = module {
    // Базовое определение ViewModel
    viewModel { MainViewModel() }

    // ViewModel с зависимостями
    viewModel { UserViewModel(get(), get()) }

    // ViewModel с параметрами
    viewModel { (userId: String) ->
        ProfileViewModel(userId, get())
    }

    // ViewModel с SavedStateHandle
    viewModel { params ->
        DetailViewModel(
            savedStateHandle = params.get(),
            repository = get()
        )
    }
}
```

### Использование в Activity

```kotlin
class MainActivity : AppCompatActivity() {

    // Стандартная инъекция ViewModel
    private val viewModel: MainViewModel by viewModel()

    // ViewModel с параметрами
    private val userViewModel: UserViewModel by viewModel {
        parametersOf(intent.getStringExtra("USER_ID"))
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        viewModel.data.observe(this) { data ->
            // Обработка данных
        }
    }
}
```

### Использование в Fragment

```kotlin
class UserFragment : Fragment() {

    // ViewModel привязанная к Fragment
    private val viewModel: UserViewModel by viewModel()

    // ViewModel привязанная к Activity (shared)
    private val sharedViewModel: SharedViewModel by activityViewModel()

    // ViewModel с параметрами из arguments
    private val profileViewModel: ProfileViewModel by viewModel {
        parametersOf(requireArguments().getString("userId"))
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewModel.state.observe(viewLifecycleOwner) { state ->
            // Обработка состояния
        }
    }
}
```

### Shared ViewModel между Fragments

```kotlin
val sharedModule = module {
    // ViewModel для sharing между fragments
    viewModel { SharedCartViewModel(get()) }
}

class CartFragment : Fragment() {
    // Получаем ViewModel от Activity
    private val cartViewModel: SharedCartViewModel by activityViewModel()
}

class CheckoutFragment : Fragment() {
    // Та же ViewModel от той же Activity
    private val cartViewModel: SharedCartViewModel by activityViewModel()

    // Оба fragment работают с одним экземпляром
}
```

### SavedStateHandle

```kotlin
val viewModelModule = module {
    // ViewModel с SavedStateHandle для сохранения состояния
    viewModel { params ->
        SearchViewModel(
            savedStateHandle = params.get(), // Автоматически предоставляется
            repository = get()
        )
    }
}

class SearchViewModel(
    private val savedStateHandle: SavedStateHandle,
    private val repository: SearchRepository
) : ViewModel() {

    // Состояние сохраняется при process death
    var searchQuery: String
        get() = savedStateHandle["query"] ?: ""
        set(value) { savedStateHandle["query"] = value }

    // StateFlow из SavedStateHandle
    val query: StateFlow<String> = savedStateHandle.getStateFlow("query", "")
}
```

### Jetpack Compose Integration

```kotlin
val composeModule = module {
    viewModel { HomeViewModel(get()) }
    viewModel { (id: String) -> DetailViewModel(id, get()) }
}

@Composable
fun HomeScreen() {
    // koinViewModel() для Compose
    val viewModel: HomeViewModel = koinViewModel()

    val state by viewModel.state.collectAsStateWithLifecycle()

    HomeContent(
        state = state,
        onAction = viewModel::handleAction
    )
}

@Composable
fun DetailScreen(itemId: String) {
    // ViewModel с параметрами в Compose
    val viewModel: DetailViewModel = koinViewModel {
        parametersOf(itemId)
    }

    DetailContent(viewModel)
}
```

### Navigation Compose с Koin

```kotlin
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController, startDestination = "home") {
        composable("home") {
            val viewModel: HomeViewModel = koinViewModel()
            HomeScreen(viewModel, navController)
        }

        composable(
            route = "detail/{id}",
            arguments = listOf(navArgument("id") { type = NavType.StringType })
        ) { backStackEntry ->
            val id = backStackEntry.arguments?.getString("id") ?: ""

            // ViewModel привязанная к NavBackStackEntry
            val viewModel: DetailViewModel = koinViewModel {
                parametersOf(id)
            }

            DetailScreen(viewModel)
        }

        // Shared ViewModel в navigation graph
        navigation(
            startDestination = "checkout/cart",
            route = "checkout"
        ) {
            composable("checkout/cart") { entry ->
                // ViewModel с scope навигационного графа
                val parentEntry = remember(entry) {
                    navController.getBackStackEntry("checkout")
                }
                val viewModel: CheckoutViewModel = koinViewModel(
                    viewModelStoreOwner = parentEntry
                )
                CartScreen(viewModel)
            }

            composable("checkout/payment") { entry ->
                val parentEntry = remember(entry) {
                    navController.getBackStackEntry("checkout")
                }
                // Тот же экземпляр ViewModel
                val viewModel: CheckoutViewModel = koinViewModel(
                    viewModelStoreOwner = parentEntry
                )
                PaymentScreen(viewModel)
            }
        }
    }
}
```

### ViewModel Factory

```kotlin
val factoryModule = module {
    // Кастомная factory для ViewModel
    viewModel { params ->
        val userId: String = params.get()
        val savedStateHandle: SavedStateHandle = params.get()

        UserProfileViewModel(
            userId = userId,
            savedStateHandle = savedStateHandle,
            repository = get(),
            analytics = get()
        )
    }
}

// Использование с множественными параметрами
class ProfileActivity : AppCompatActivity() {
    private val viewModel: UserProfileViewModel by viewModel {
        parametersOf(
            intent.getStringExtra("USER_ID"),
            // SavedStateHandle передается автоматически
        )
    }
}
```

### Тестирование ViewModel

```kotlin
class UserViewModelTest {

    @get:Rule
    val koinTestRule = KoinTestRule.create {
        modules(
            module {
                single<UserRepository> { FakeUserRepository() }
                viewModel { UserViewModel(get()) }
            }
        )
    }

    @Test
    fun `test load user`() = runTest {
        val viewModel: UserViewModel = get()

        viewModel.loadUser("123")

        val state = viewModel.state.value
        assertEquals("John", state.user?.name)
    }
}
```

### Лучшие практики

1. **Один viewModel per screen** - не переиспользуйте ViewModel между разными экранами
2. **Используйте SavedStateHandle** - для сохранения при process death
3. **activityViewModel()** - для shared state между fragments
4. **koinViewModel()** в Compose - вместо by viewModel()
5. **Параметры через parametersOf** - не храните в конструкторе ViewModel

```kotlin
// Хорошо: параметры через Koin
viewModel { (id: String) -> DetailViewModel(id, get()) }

// Плохо: ViewModel зависит от внешнего состояния
viewModel { DetailViewModel(SomeGlobalState.currentId, get()) }
```

---

## Answer (EN)

Koin provides a special DSL for working with Android ViewModel that automatically integrates with `ViewModelStore` and properly manages lifecycle.

### Adding Dependencies

```kotlin
// build.gradle.kts
dependencies {
    implementation("io.insert-koin:koin-android:3.5.6")

    // For Jetpack Compose
    implementation("io.insert-koin:koin-androidx-compose:3.5.6")
}
```

### Defining ViewModel in Module

```kotlin
val viewModelModule = module {
    // Basic ViewModel definition
    viewModel { MainViewModel() }

    // ViewModel with dependencies
    viewModel { UserViewModel(get(), get()) }

    // ViewModel with parameters
    viewModel { (userId: String) ->
        ProfileViewModel(userId, get())
    }

    // ViewModel with SavedStateHandle
    viewModel { params ->
        DetailViewModel(
            savedStateHandle = params.get(),
            repository = get()
        )
    }
}
```

### Usage in Activity

```kotlin
class MainActivity : AppCompatActivity() {

    // Standard ViewModel injection
    private val viewModel: MainViewModel by viewModel()

    // ViewModel with parameters
    private val userViewModel: UserViewModel by viewModel {
        parametersOf(intent.getStringExtra("USER_ID"))
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        viewModel.data.observe(this) { data ->
            // Handle data
        }
    }
}
```

### Usage in Fragment

```kotlin
class UserFragment : Fragment() {

    // ViewModel scoped to Fragment
    private val viewModel: UserViewModel by viewModel()

    // ViewModel scoped to Activity (shared)
    private val sharedViewModel: SharedViewModel by activityViewModel()

    // ViewModel with parameters from arguments
    private val profileViewModel: ProfileViewModel by viewModel {
        parametersOf(requireArguments().getString("userId"))
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewModel.state.observe(viewLifecycleOwner) { state ->
            // Handle state
        }
    }
}
```

### Shared ViewModel Between Fragments

```kotlin
val sharedModule = module {
    // ViewModel for sharing between fragments
    viewModel { SharedCartViewModel(get()) }
}

class CartFragment : Fragment() {
    // Get ViewModel from Activity
    private val cartViewModel: SharedCartViewModel by activityViewModel()
}

class CheckoutFragment : Fragment() {
    // Same ViewModel from same Activity
    private val cartViewModel: SharedCartViewModel by activityViewModel()

    // Both fragments work with the same instance
}
```

### SavedStateHandle

```kotlin
val viewModelModule = module {
    // ViewModel with SavedStateHandle for state preservation
    viewModel { params ->
        SearchViewModel(
            savedStateHandle = params.get(), // Automatically provided
            repository = get()
        )
    }
}

class SearchViewModel(
    private val savedStateHandle: SavedStateHandle,
    private val repository: SearchRepository
) : ViewModel() {

    // State survives process death
    var searchQuery: String
        get() = savedStateHandle["query"] ?: ""
        set(value) { savedStateHandle["query"] = value }

    // StateFlow from SavedStateHandle
    val query: StateFlow<String> = savedStateHandle.getStateFlow("query", "")
}
```

### Jetpack Compose Integration

```kotlin
val composeModule = module {
    viewModel { HomeViewModel(get()) }
    viewModel { (id: String) -> DetailViewModel(id, get()) }
}

@Composable
fun HomeScreen() {
    // koinViewModel() for Compose
    val viewModel: HomeViewModel = koinViewModel()

    val state by viewModel.state.collectAsStateWithLifecycle()

    HomeContent(
        state = state,
        onAction = viewModel::handleAction
    )
}

@Composable
fun DetailScreen(itemId: String) {
    // ViewModel with parameters in Compose
    val viewModel: DetailViewModel = koinViewModel {
        parametersOf(itemId)
    }

    DetailContent(viewModel)
}
```

### Navigation Compose with Koin

```kotlin
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController, startDestination = "home") {
        composable("home") {
            val viewModel: HomeViewModel = koinViewModel()
            HomeScreen(viewModel, navController)
        }

        composable(
            route = "detail/{id}",
            arguments = listOf(navArgument("id") { type = NavType.StringType })
        ) { backStackEntry ->
            val id = backStackEntry.arguments?.getString("id") ?: ""

            // ViewModel scoped to NavBackStackEntry
            val viewModel: DetailViewModel = koinViewModel {
                parametersOf(id)
            }

            DetailScreen(viewModel)
        }

        // Shared ViewModel in navigation graph
        navigation(
            startDestination = "checkout/cart",
            route = "checkout"
        ) {
            composable("checkout/cart") { entry ->
                // ViewModel scoped to navigation graph
                val parentEntry = remember(entry) {
                    navController.getBackStackEntry("checkout")
                }
                val viewModel: CheckoutViewModel = koinViewModel(
                    viewModelStoreOwner = parentEntry
                )
                CartScreen(viewModel)
            }

            composable("checkout/payment") { entry ->
                val parentEntry = remember(entry) {
                    navController.getBackStackEntry("checkout")
                }
                // Same ViewModel instance
                val viewModel: CheckoutViewModel = koinViewModel(
                    viewModelStoreOwner = parentEntry
                )
                PaymentScreen(viewModel)
            }
        }
    }
}
```

### ViewModel Factory

```kotlin
val factoryModule = module {
    // Custom factory for ViewModel
    viewModel { params ->
        val userId: String = params.get()
        val savedStateHandle: SavedStateHandle = params.get()

        UserProfileViewModel(
            userId = userId,
            savedStateHandle = savedStateHandle,
            repository = get(),
            analytics = get()
        )
    }
}

// Usage with multiple parameters
class ProfileActivity : AppCompatActivity() {
    private val viewModel: UserProfileViewModel by viewModel {
        parametersOf(
            intent.getStringExtra("USER_ID"),
            // SavedStateHandle is passed automatically
        )
    }
}
```

### Testing ViewModel

```kotlin
class UserViewModelTest {

    @get:Rule
    val koinTestRule = KoinTestRule.create {
        modules(
            module {
                single<UserRepository> { FakeUserRepository() }
                viewModel { UserViewModel(get()) }
            }
        )
    }

    @Test
    fun `test load user`() = runTest {
        val viewModel: UserViewModel = get()

        viewModel.loadUser("123")

        val state = viewModel.state.value
        assertEquals("John", state.user?.name)
    }
}
```

### Best Practices

1. **One viewModel per screen** - don't reuse ViewModel across different screens
2. **Use SavedStateHandle** - for process death survival
3. **activityViewModel()** - for shared state between fragments
4. **koinViewModel()** in Compose - instead of by viewModel()
5. **Parameters via parametersOf** - don't store in ViewModel constructor

```kotlin
// Good: parameters via Koin
viewModel { (id: String) -> DetailViewModel(id, get()) }

// Bad: ViewModel depends on external state
viewModel { DetailViewModel(SomeGlobalState.currentId, get()) }
```

---

## Dopolnitelnye Voprosy (RU)

- Как правильно шарить ViewModel между вложенными навигационными графами?
- В чем разница между viewModel() и sharedViewModel() в Koin?
- Как тестировать ViewModel с SavedStateHandle?

## Follow-ups

- How do you properly share ViewModel between nested navigation graphs?
- What is the difference between viewModel() and sharedViewModel() in Koin?
- How do you test ViewModel with SavedStateHandle?

## Ssylki (RU)

- [Koin ViewModel](https://insert-koin.io/docs/reference/koin-android/viewmodel)
- [Koin Compose](https://insert-koin.io/docs/reference/koin-compose/compose)

## References

- [Koin ViewModel](https://insert-koin.io/docs/reference/koin-android/viewmodel)
- [Koin Compose](https://insert-koin.io/docs/reference/koin-compose/compose)

## Svyazannye Voprosy (RU)

### Medium
- [[q-koin-setup-modules--koin--medium]]
- [[q-koin-compose--koin--medium]]
- [[q-koin-parameters--koin--medium]]

## Related Questions

### Medium
- [[q-koin-setup-modules--koin--medium]]
- [[q-koin-compose--koin--medium]]
- [[q-koin-parameters--koin--medium]]
