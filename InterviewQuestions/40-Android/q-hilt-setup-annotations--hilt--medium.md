---
id: android-hilt-001
title: Hilt Setup Annotations / Аннотации настройки Hilt
aliases:
- Hilt Setup Annotations
- Аннотации настройки Hilt
- HiltAndroidApp
- AndroidEntryPoint
- HiltViewModel
topic: android
subtopics:
- di-hilt
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
- q-hilt-modules-provides--hilt--medium
- q-hilt-scopes--hilt--hard
- q-hilt-viewmodel-injection--hilt--medium
- q-test-doubles-dependency-injection--android--medium
created: 2026-01-23
updated: 2026-01-23
tags:
- android/di-hilt
- android/architecture
- difficulty/medium
- hilt
- dependency-injection
anki_cards:
- slug: android-hilt-001-0-en
  language: en
- slug: android-hilt-001-0-ru
  language: ru
---
# Vopros (RU)
> Какие основные аннотации используются для настройки Hilt в Android-приложении? Объясните @HiltAndroidApp, @AndroidEntryPoint и @HiltViewModel.

# Question (EN)
> What are the core annotations used to set up Hilt in an Android application? Explain @HiltAndroidApp, @AndroidEntryPoint, and @HiltViewModel.

---

## Otvet (RU)

Hilt - это библиотека dependency injection для Android, построенная поверх Dagger 2. Она упрощает настройку DI, предоставляя стандартизированные компоненты и аннотации, которые автоматически привязываются к жизненному циклу Android.

### @HiltAndroidApp

Эта аннотация обязательна и должна быть применена к классу `Application`. Она запускает генерацию кода Hilt и создает базовый компонент приложения.

```kotlin
@HiltAndroidApp
class MyApplication : Application() {
    // Hilt автоматически генерирует необходимые компоненты
    // Можно добавить логику инициализации приложения

    override fun onCreate() {
        super.onCreate()
        // Инициализация библиотек, логирования и т.д.
    }
}
```

**Что происходит под капотом:**
- Генерируется `SingletonComponent` - корневой компонент иерархии
- Создается базовый класс `Hilt_MyApplication`, от которого наследуется ваш Application
- Инициализируется граф зависимостей при старте приложения

### @AndroidEntryPoint

Эта аннотация применяется к Android-классам, в которые нужно инжектить зависимости: Activity, Fragment, View, Service, BroadcastReceiver.

```kotlin
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    @Inject
    lateinit var analyticsService: AnalyticsService

    @Inject
    lateinit var userRepository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Зависимости уже инжектированы к этому моменту
        analyticsService.logScreenView("MainActivity")
    }
}

@AndroidEntryPoint
class UserFragment : Fragment() {

    @Inject
    lateinit var userRepository: UserRepository

    // ViewModel тоже можно получить
    private val viewModel: UserViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        // Работа с инжектированными зависимостями
    }
}
```

**Поддерживаемые классы:**
- `Activity` (наследники ComponentActivity)
- `Fragment` (из androidx.fragment)
- `View`
- `Service`
- `BroadcastReceiver`

**Важно:** Если Fragment помечен `@AndroidEntryPoint`, то Activity, содержащая этот Fragment, тоже должна быть помечена `@AndroidEntryPoint`.

### @HiltViewModel

Специальная аннотация для ViewModel, позволяющая инжектить зависимости через конструктор.

```kotlin
@HiltViewModel
class UserViewModel @Inject constructor(
    private val userRepository: UserRepository,
    private val analyticsService: AnalyticsService,
    private val savedStateHandle: SavedStateHandle // Автоматически предоставляется Hilt
) : ViewModel() {

    private val userId: String = savedStateHandle.get<String>("userId") ?: ""

    private val _uiState = MutableStateFlow<UserUiState>(UserUiState.Loading)
    val uiState: StateFlow<UserUiState> = _uiState.asStateFlow()

    init {
        loadUser()
    }

    private fun loadUser() {
        viewModelScope.launch {
            try {
                val user = userRepository.getUser(userId)
                _uiState.value = UserUiState.Success(user)
            } catch (e: Exception) {
                _uiState.value = UserUiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}

sealed interface UserUiState {
    data object Loading : UserUiState
    data class Success(val user: User) : UserUiState
    data class Error(val message: String) : UserUiState
}
```

**Получение ViewModel в Activity/Fragment:**

```kotlin
@AndroidEntryPoint
class UserActivity : AppCompatActivity() {

    // Стандартный способ с делегатом
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                updateUi(state)
            }
        }
    }
}

@AndroidEntryPoint
class UserFragment : Fragment() {

    // ViewModel привязана к Fragment
    private val viewModel: UserViewModel by viewModels()

    // ViewModel привязана к Activity (shared ViewModel)
    private val sharedViewModel: SharedViewModel by activityViewModels()
}
```

### Полный пример настройки

```kotlin
// 1. Application
@HiltAndroidApp
class MyApp : Application()

// 2. Module с зависимостями
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

@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindUserRepository(
        impl: UserRepositoryImpl
    ): UserRepository
}

// 3. Repository
class UserRepositoryImpl @Inject constructor(
    private val apiService: ApiService
) : UserRepository {

    override suspend fun getUser(id: String): User {
        return apiService.getUser(id)
    }
}

// 4. ViewModel
@HiltViewModel
class MainViewModel @Inject constructor(
    private val userRepository: UserRepository
) : ViewModel() {
    // ...
}

// 5. Activity
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    private val viewModel: MainViewModel by viewModels()

    @Inject
    lateinit var analyticsService: AnalyticsService

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Готово к использованию
    }
}
```

### Gradle-зависимости (2026)

```kotlin
// build.gradle.kts (app)
plugins {
    id("com.google.dagger.hilt.android")
    id("com.google.devtools.ksp")
}

dependencies {
    implementation("com.google.dagger:hilt-android:2.52")
    ksp("com.google.dagger:hilt-android-compiler:2.52")

    // Для ViewModel
    implementation("androidx.hilt:hilt-navigation-compose:1.2.0")
}
```

---

## Answer (EN)

Hilt is a dependency injection library for Android built on top of Dagger 2. It simplifies DI setup by providing standardized components and annotations that automatically bind to the Android lifecycle.

### @HiltAndroidApp

This annotation is mandatory and must be applied to the `Application` class. It triggers Hilt code generation and creates the base application component.

```kotlin
@HiltAndroidApp
class MyApplication : Application() {
    // Hilt automatically generates necessary components
    // You can add app initialization logic here

    override fun onCreate() {
        super.onCreate()
        // Initialize libraries, logging, etc.
    }
}
```

**What happens under the hood:**
- Generates `SingletonComponent` - the root component of the hierarchy
- Creates a base class `Hilt_MyApplication` that your Application inherits from
- Initializes the dependency graph at application startup

### @AndroidEntryPoint

This annotation is applied to Android classes that need dependency injection: Activity, Fragment, View, Service, BroadcastReceiver.

```kotlin
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    @Inject
    lateinit var analyticsService: AnalyticsService

    @Inject
    lateinit var userRepository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Dependencies are already injected at this point
        analyticsService.logScreenView("MainActivity")
    }
}

@AndroidEntryPoint
class UserFragment : Fragment() {

    @Inject
    lateinit var userRepository: UserRepository

    // ViewModel can also be obtained
    private val viewModel: UserViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        // Work with injected dependencies
    }
}
```

**Supported classes:**
- `Activity` (ComponentActivity subclasses)
- `Fragment` (from androidx.fragment)
- `View`
- `Service`
- `BroadcastReceiver`

**Important:** If a Fragment is marked with `@AndroidEntryPoint`, the Activity containing that Fragment must also be marked with `@AndroidEntryPoint`.

### @HiltViewModel

A special annotation for ViewModel that allows constructor injection of dependencies.

```kotlin
@HiltViewModel
class UserViewModel @Inject constructor(
    private val userRepository: UserRepository,
    private val analyticsService: AnalyticsService,
    private val savedStateHandle: SavedStateHandle // Automatically provided by Hilt
) : ViewModel() {

    private val userId: String = savedStateHandle.get<String>("userId") ?: ""

    private val _uiState = MutableStateFlow<UserUiState>(UserUiState.Loading)
    val uiState: StateFlow<UserUiState> = _uiState.asStateFlow()

    init {
        loadUser()
    }

    private fun loadUser() {
        viewModelScope.launch {
            try {
                val user = userRepository.getUser(userId)
                _uiState.value = UserUiState.Success(user)
            } catch (e: Exception) {
                _uiState.value = UserUiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}

sealed interface UserUiState {
    data object Loading : UserUiState
    data class Success(val user: User) : UserUiState
    data class Error(val message: String) : UserUiState
}
```

**Obtaining ViewModel in Activity/Fragment:**

```kotlin
@AndroidEntryPoint
class UserActivity : AppCompatActivity() {

    // Standard approach with delegate
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                updateUi(state)
            }
        }
    }
}

@AndroidEntryPoint
class UserFragment : Fragment() {

    // ViewModel scoped to Fragment
    private val viewModel: UserViewModel by viewModels()

    // ViewModel scoped to Activity (shared ViewModel)
    private val sharedViewModel: SharedViewModel by activityViewModels()
}
```

### Complete Setup Example

```kotlin
// 1. Application
@HiltAndroidApp
class MyApp : Application()

// 2. Module with dependencies
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

@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindUserRepository(
        impl: UserRepositoryImpl
    ): UserRepository
}

// 3. Repository
class UserRepositoryImpl @Inject constructor(
    private val apiService: ApiService
) : UserRepository {

    override suspend fun getUser(id: String): User {
        return apiService.getUser(id)
    }
}

// 4. ViewModel
@HiltViewModel
class MainViewModel @Inject constructor(
    private val userRepository: UserRepository
) : ViewModel() {
    // ...
}

// 5. Activity
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    private val viewModel: MainViewModel by viewModels()

    @Inject
    lateinit var analyticsService: AnalyticsService

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Ready to use
    }
}
```

### Gradle Dependencies (2026)

```kotlin
// build.gradle.kts (app)
plugins {
    id("com.google.dagger.hilt.android")
    id("com.google.devtools.ksp")
}

dependencies {
    implementation("com.google.dagger:hilt-android:2.52")
    ksp("com.google.dagger:hilt-android-compiler:2.52")

    // For ViewModel
    implementation("androidx.hilt:hilt-navigation-compose:1.2.0")
}
```

---

## Dopolnitelnye Voprosy (RU)

- Почему Activity должна быть помечена `@AndroidEntryPoint`, если её Fragment тоже помечен?
- Как Hilt обрабатывает конфигурационные изменения для ViewModel?
- Можно ли использовать `@AndroidEntryPoint` с кастомными View?
- Чем отличается `@HiltViewModel` от стандартного Dagger-подхода к ViewModel?

## Follow-ups

- Why must an Activity be marked with `@AndroidEntryPoint` if its Fragment is also marked?
- How does Hilt handle configuration changes for ViewModel?
- Can you use `@AndroidEntryPoint` with custom Views?
- How does `@HiltViewModel` differ from the standard Dagger approach to ViewModel?

---

## Ssylki (RU)

- [Hilt Documentation](https://developer.android.com/training/dependency-injection/hilt-android)
- [Hilt and Jetpack](https://developer.android.com/training/dependency-injection/hilt-jetpack)

## References

- [Hilt Documentation](https://developer.android.com/training/dependency-injection/hilt-android)
- [Hilt and Jetpack](https://developer.android.com/training/dependency-injection/hilt-jetpack)

---

## Svyazannye Voprosy (RU)

### Medium
- [[q-hilt-modules-provides--hilt--medium]]
- [[q-hilt-viewmodel-injection--hilt--medium]]
- [[q-hilt-qualifiers--hilt--medium]]
- [[q-hilt-testing--hilt--medium]]

### Hard
- [[q-hilt-scopes--hilt--hard]]
- [[q-hilt-assisted-injection--hilt--hard]]
- [[q-hilt-entry-points--hilt--hard]]

## Related Questions

### Medium
- [[q-hilt-modules-provides--hilt--medium]]
- [[q-hilt-viewmodel-injection--hilt--medium]]
- [[q-hilt-qualifiers--hilt--medium]]
- [[q-hilt-testing--hilt--medium]]

### Hard
- [[q-hilt-scopes--hilt--hard]]
- [[q-hilt-assisted-injection--hilt--hard]]
- [[q-hilt-entry-points--hilt--hard]]
