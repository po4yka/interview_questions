---
id: android-hilt-003
title: Hilt Scopes / Области видимости Hilt
aliases:
- Hilt Scopes
- Области видимости Hilt
- Singleton
- ViewModelScoped
- ActivityScoped
- FragmentScoped
topic: android
subtopics:
- di-hilt
- architecture
- lifecycle
question_kind: theory
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-hilt-setup-annotations--hilt--medium
- q-hilt-modules-provides--hilt--medium
- q-hilt-custom-components--hilt--hard
created: 2026-01-23
updated: 2026-01-23
tags:
- android/di-hilt
- android/architecture
- android/lifecycle
- difficulty/hard
- hilt
- scopes
- dependency-injection
anki_cards:
- slug: android-hilt-003-0-en
  language: en
- slug: android-hilt-003-0-ru
  language: ru
---
# Vopros (RU)
> Объясните систему scopes в Hilt: @Singleton, @ViewModelScoped, @ActivityScoped, @FragmentScoped. Как правильно выбрать scope для зависимости?

# Question (EN)
> Explain the scope system in Hilt: @Singleton, @ViewModelScoped, @ActivityScoped, @FragmentScoped. How do you choose the right scope for a dependency?

---

## Otvet (RU)

Scope в Hilt определяет время жизни зависимости и гарантирует, что в пределах этого scope будет использоваться один и тот же экземпляр объекта. Правильный выбор scope критически важен для управления памятью и корректной работы приложения.

### Иерархия компонентов Hilt

```
SingletonComponent (Application)
    |
    +-- ActivityRetainedComponent (переживает конфиг. изменения)
    |       |
    |       +-- ViewModelComponent (одна ViewModel)
    |       |
    |       +-- ActivityComponent (одна Activity)
    |               |
    |               +-- FragmentComponent (один Fragment)
    |               |       |
    |               |       +-- ViewWithFragmentComponent
    |               |
    |               +-- ViewComponent
    |
    +-- ServiceComponent (один Service)
```

### @Singleton

Самый широкий scope. Объект создается один раз при старте приложения и живет до его завершения.

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "app_database"
        ).build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .build()
    }
}

// Repository как Singleton
@Singleton
class UserRepository @Inject constructor(
    private val database: AppDatabase,
    private val apiService: ApiService
) {
    // Один экземпляр на всё приложение
}
```

**Когда использовать:**
- База данных, кэши
- Сетевые клиенты (Retrofit, OkHttp)
- Глобальные репозитории
- Аналитика, логирование
- Shared state между фичами

**Осторожно:**
- Утечки памяти (не храните ссылки на Activity/Fragment)
- Слишком много Singleton-ов увеличивает время старта

### @ActivityRetainedScoped

Объект переживает конфигурационные изменения (поворот экрана), но уничтожается когда Activity финально уничтожена.

```kotlin
@Module
@InstallIn(ActivityRetainedComponent::class)
abstract class ActivityRetainedModule {

    @Binds
    @ActivityRetainedScoped
    abstract fun bindSessionManager(impl: SessionManagerImpl): SessionManager
}

@ActivityRetainedScoped
class SessionManagerImpl @Inject constructor(
    private val authRepository: AuthRepository
) : SessionManager {

    private var currentSession: Session? = null

    override fun getCurrentSession(): Session? = currentSession

    override fun setSession(session: Session) {
        currentSession = session
    }
}
```

**Когда использовать:**
- Состояние, которое должно пережить поворот экрана
- Данные сессии в рамках Activity
- Временные кэши для Activity

### @ViewModelScoped

Объект привязан к жизненному циклу конкретной ViewModel. Уничтожается вместе с ViewModel.

```kotlin
@Module
@InstallIn(ViewModelComponent::class)
abstract class ViewModelModule {

    @Binds
    @ViewModelScoped
    abstract fun bindFormValidator(impl: FormValidatorImpl): FormValidator
}

@ViewModelScoped
class FormValidatorImpl @Inject constructor() : FormValidator {

    private val validationErrors = mutableMapOf<String, String>()

    override fun validate(field: String, value: String): Boolean {
        // Логика валидации
        return true
    }

    override fun getErrors(): Map<String, String> = validationErrors
}

@HiltViewModel
class RegistrationViewModel @Inject constructor(
    private val formValidator: FormValidator, // ViewModelScoped
    private val userRepository: UserRepository // Singleton
) : ViewModel() {

    fun validateForm(email: String, password: String): Boolean {
        return formValidator.validate("email", email) &&
               formValidator.validate("password", password)
    }
}
```

**Когда использовать:**
- State holders для конкретного экрана
- Валидаторы форм
- Пагинаторы
- Use cases, специфичные для экрана

### @ActivityScoped

Объект привязан к жизненному циклу Activity. НЕ переживает конфигурационные изменения.

```kotlin
@Module
@InstallIn(ActivityComponent::class)
abstract class ActivityModule {

    @Binds
    @ActivityScoped
    abstract fun bindNavigator(impl: NavigatorImpl): Navigator
}

@ActivityScoped
class NavigatorImpl @Inject constructor(
    private val activity: Activity
) : Navigator {

    override fun navigateTo(destination: Destination) {
        val intent = when (destination) {
            is Destination.Profile -> Intent(activity, ProfileActivity::class.java)
            is Destination.Settings -> Intent(activity, SettingsActivity::class.java)
        }
        activity.startActivity(intent)
    }
}

// Получение Activity в модуле
@Module
@InstallIn(ActivityComponent::class)
object ActivityBindingsModule {

    @Provides
    fun provideActivity(activity: Activity): AppCompatActivity {
        return activity as AppCompatActivity
    }
}
```

**Когда использовать:**
- Зависимости, требующие Activity context
- Навигация внутри Activity
- Диалоги, Snackbar managers
- Permissions handlers

**Осторожно:**
- Пересоздается при каждом повороте экрана
- Может привести к утечкам, если сохранять ссылки неправильно

### @FragmentScoped

Объект привязан к жизненному циклу Fragment.

```kotlin
@Module
@InstallIn(FragmentComponent::class)
abstract class FragmentModule {

    @Binds
    @FragmentScoped
    abstract fun bindImageLoader(impl: ImageLoaderImpl): ImageLoader
}

@FragmentScoped
class ImageLoaderImpl @Inject constructor(
    private val fragment: Fragment
) : ImageLoader {

    private val glideRequestManager = Glide.with(fragment)

    override fun load(url: String, imageView: ImageView) {
        glideRequestManager
            .load(url)
            .placeholder(R.drawable.placeholder)
            .into(imageView)
    }
}
```

**Когда использовать:**
- Зависимости, требующие Fragment context
- Локальные state managers для Fragment
- View-specific utilities

### Сравнение scopes

| Scope | Компонент | Время жизни | Переживает config change |
|-------|-----------|-------------|--------------------------|
| `@Singleton` | SingletonComponent | Приложение | Да |
| `@ActivityRetainedScoped` | ActivityRetainedComponent | Activity (retained) | Да |
| `@ViewModelScoped` | ViewModelComponent | ViewModel | Да |
| `@ActivityScoped` | ActivityComponent | Activity | Нет |
| `@FragmentScoped` | FragmentComponent | Fragment | Нет |
| `@ViewScoped` | ViewComponent | View | Нет |
| `@ServiceScoped` | ServiceComponent | Service | N/A |

### Unscoped зависимости

Если не указывать scope, каждый раз создается новый экземпляр:

```kotlin
// Без scope - новый экземпляр при каждом injection
class DateFormatter @Inject constructor() {
    fun format(date: Date): String = SimpleDateFormat("dd.MM.yyyy").format(date)
}

// Каждый вызов создаст новый DateFormatter
@HiltViewModel
class EventViewModel @Inject constructor(
    private val dateFormatter: DateFormatter // Новый экземпляр
) : ViewModel()

@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val dateFormatter: DateFormatter // Другой новый экземпляр
) : ViewModel()
```

**Когда использовать unscoped:**
- Легковесные stateless объекты
- Утилиты без состояния
- Factory-классы
- Когда каждому потребителю нужен свой экземпляр

### Правила выбора scope

```kotlin
// 1. Задайте вопрос: нужен ли единственный экземпляр?
//    Нет -> Unscoped (без аннотации scope)

// 2. Какова область общего использования?
class ChooseScopeExample {

    // Глобальное состояние, разделяемое всем приложением
    @Singleton
    class AppConfiguration @Inject constructor()

    // Состояние экрана, должно пережить поворот
    @ViewModelScoped
    class ScreenStateHolder @Inject constructor()

    // Нужен Activity context, но не критично для config changes
    @ActivityScoped
    class ActivityNavigator @Inject constructor()

    // Нужен Fragment для Glide/lifecycle
    @FragmentScoped
    class FragmentImageLoader @Inject constructor()
}

// 3. Правило наименьшего scope
// Используйте наименьший scope, который удовлетворяет требованиям
// Singleton -> ActivityRetained -> ViewModel -> Activity -> Fragment -> Unscoped
```

### Практический пример: правильная организация scopes

```kotlin
// === SINGLETON LAYER ===
@Singleton
class ApiClient @Inject constructor(
    private val okHttpClient: OkHttpClient
)

@Singleton
class UserRepository @Inject constructor(
    private val apiClient: ApiClient,
    private val database: AppDatabase
)

// === VIEWMODEL LAYER ===
@ViewModelScoped
class GetUserProfileUseCase @Inject constructor(
    private val userRepository: UserRepository // Singleton
)

@ViewModelScoped
class ProfileStateReducer @Inject constructor() {
    private var currentState: ProfileState = ProfileState.Initial

    fun reduce(action: ProfileAction): ProfileState {
        currentState = when (action) {
            is ProfileAction.LoadSuccess -> ProfileState.Loaded(action.user)
            is ProfileAction.LoadError -> ProfileState.Error(action.message)
            ProfileAction.Loading -> ProfileState.Loading
        }
        return currentState
    }
}

// === VIEWMODEL ===
@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val getUserProfile: GetUserProfileUseCase, // ViewModelScoped
    private val stateReducer: ProfileStateReducer,     // ViewModelScoped
    private val analyticsService: AnalyticsService     // Singleton
) : ViewModel() {

    private val _state = MutableStateFlow<ProfileState>(ProfileState.Initial)
    val state: StateFlow<ProfileState> = _state.asStateFlow()

    fun loadProfile(userId: String) {
        viewModelScope.launch {
            _state.value = stateReducer.reduce(ProfileAction.Loading)

            getUserProfile(userId)
                .onSuccess { user ->
                    _state.value = stateReducer.reduce(ProfileAction.LoadSuccess(user))
                    analyticsService.logEvent("profile_loaded")
                }
                .onFailure { error ->
                    _state.value = stateReducer.reduce(ProfileAction.LoadError(error.message ?: ""))
                }
        }
    }
}
```

---

## Answer (EN)

Scope in Hilt defines the lifetime of a dependency and guarantees that the same instance of an object will be used within that scope. Choosing the right scope is critical for memory management and correct application behavior.

### Hilt Component Hierarchy

```
SingletonComponent (Application)
    |
    +-- ActivityRetainedComponent (survives config changes)
    |       |
    |       +-- ViewModelComponent (single ViewModel)
    |       |
    |       +-- ActivityComponent (single Activity)
    |               |
    |               +-- FragmentComponent (single Fragment)
    |               |       |
    |               |       +-- ViewWithFragmentComponent
    |               |
    |               +-- ViewComponent
    |
    +-- ServiceComponent (single Service)
```

### @Singleton

The widest scope. Object is created once at application startup and lives until it terminates.

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "app_database"
        ).build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .build()
    }
}

// Repository as Singleton
@Singleton
class UserRepository @Inject constructor(
    private val database: AppDatabase,
    private val apiService: ApiService
) {
    // Single instance for the entire application
}
```

**When to use:**
- Database, caches
- Network clients (Retrofit, OkHttp)
- Global repositories
- Analytics, logging
- Shared state between features

**Be careful:**
- Memory leaks (don't store references to Activity/Fragment)
- Too many Singletons increase startup time

### @ActivityRetainedScoped

Object survives configuration changes (screen rotation) but is destroyed when Activity is finally destroyed.

```kotlin
@Module
@InstallIn(ActivityRetainedComponent::class)
abstract class ActivityRetainedModule {

    @Binds
    @ActivityRetainedScoped
    abstract fun bindSessionManager(impl: SessionManagerImpl): SessionManager
}

@ActivityRetainedScoped
class SessionManagerImpl @Inject constructor(
    private val authRepository: AuthRepository
) : SessionManager {

    private var currentSession: Session? = null

    override fun getCurrentSession(): Session? = currentSession

    override fun setSession(session: Session) {
        currentSession = session
    }
}
```

**When to use:**
- State that should survive screen rotation
- Session data within an Activity
- Temporary caches for Activity

### @ViewModelScoped

Object is bound to the lifecycle of a specific ViewModel. Destroyed together with the ViewModel.

```kotlin
@Module
@InstallIn(ViewModelComponent::class)
abstract class ViewModelModule {

    @Binds
    @ViewModelScoped
    abstract fun bindFormValidator(impl: FormValidatorImpl): FormValidator
}

@ViewModelScoped
class FormValidatorImpl @Inject constructor() : FormValidator {

    private val validationErrors = mutableMapOf<String, String>()

    override fun validate(field: String, value: String): Boolean {
        // Validation logic
        return true
    }

    override fun getErrors(): Map<String, String> = validationErrors
}

@HiltViewModel
class RegistrationViewModel @Inject constructor(
    private val formValidator: FormValidator, // ViewModelScoped
    private val userRepository: UserRepository // Singleton
) : ViewModel() {

    fun validateForm(email: String, password: String): Boolean {
        return formValidator.validate("email", email) &&
               formValidator.validate("password", password)
    }
}
```

**When to use:**
- State holders for a specific screen
- Form validators
- Paginators
- Screen-specific use cases

### @ActivityScoped

Object is bound to Activity lifecycle. Does NOT survive configuration changes.

```kotlin
@Module
@InstallIn(ActivityComponent::class)
abstract class ActivityModule {

    @Binds
    @ActivityScoped
    abstract fun bindNavigator(impl: NavigatorImpl): Navigator
}

@ActivityScoped
class NavigatorImpl @Inject constructor(
    private val activity: Activity
) : Navigator {

    override fun navigateTo(destination: Destination) {
        val intent = when (destination) {
            is Destination.Profile -> Intent(activity, ProfileActivity::class.java)
            is Destination.Settings -> Intent(activity, SettingsActivity::class.java)
        }
        activity.startActivity(intent)
    }
}
```

**When to use:**
- Dependencies requiring Activity context
- Navigation within Activity
- Dialogs, Snackbar managers
- Permission handlers

**Be careful:**
- Recreated on every screen rotation
- Can cause leaks if references are stored incorrectly

### @FragmentScoped

Object is bound to Fragment lifecycle.

```kotlin
@Module
@InstallIn(FragmentComponent::class)
abstract class FragmentModule {

    @Binds
    @FragmentScoped
    abstract fun bindImageLoader(impl: ImageLoaderImpl): ImageLoader
}

@FragmentScoped
class ImageLoaderImpl @Inject constructor(
    private val fragment: Fragment
) : ImageLoader {

    private val glideRequestManager = Glide.with(fragment)

    override fun load(url: String, imageView: ImageView) {
        glideRequestManager
            .load(url)
            .placeholder(R.drawable.placeholder)
            .into(imageView)
    }
}
```

**When to use:**
- Dependencies requiring Fragment context
- Local state managers for Fragment
- View-specific utilities

### Scope Comparison

| Scope | Component | Lifetime | Survives config change |
|-------|-----------|----------|------------------------|
| `@Singleton` | SingletonComponent | Application | Yes |
| `@ActivityRetainedScoped` | ActivityRetainedComponent | Activity (retained) | Yes |
| `@ViewModelScoped` | ViewModelComponent | ViewModel | Yes |
| `@ActivityScoped` | ActivityComponent | Activity | No |
| `@FragmentScoped` | FragmentComponent | Fragment | No |
| `@ViewScoped` | ViewComponent | View | No |
| `@ServiceScoped` | ServiceComponent | Service | N/A |

### Unscoped Dependencies

If no scope is specified, a new instance is created each time:

```kotlin
// Without scope - new instance on every injection
class DateFormatter @Inject constructor() {
    fun format(date: Date): String = SimpleDateFormat("dd.MM.yyyy").format(date)
}

// Each call creates a new DateFormatter
@HiltViewModel
class EventViewModel @Inject constructor(
    private val dateFormatter: DateFormatter // New instance
) : ViewModel()

@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val dateFormatter: DateFormatter // Another new instance
) : ViewModel()
```

**When to use unscoped:**
- Lightweight stateless objects
- Utilities without state
- Factory classes
- When each consumer needs its own instance

### Scope Selection Rules

```kotlin
// 1. Ask: do I need a single instance?
//    No -> Unscoped (no scope annotation)

// 2. What is the shared usage scope?
class ChooseScopeExample {

    // Global state shared by entire app
    @Singleton
    class AppConfiguration @Inject constructor()

    // Screen state that should survive rotation
    @ViewModelScoped
    class ScreenStateHolder @Inject constructor()

    // Needs Activity context, but not critical for config changes
    @ActivityScoped
    class ActivityNavigator @Inject constructor()

    // Needs Fragment for Glide/lifecycle
    @FragmentScoped
    class FragmentImageLoader @Inject constructor()
}

// 3. Rule of smallest scope
// Use the smallest scope that satisfies requirements
// Singleton -> ActivityRetained -> ViewModel -> Activity -> Fragment -> Unscoped
```

### Practical Example: Proper Scope Organization

```kotlin
// === SINGLETON LAYER ===
@Singleton
class ApiClient @Inject constructor(
    private val okHttpClient: OkHttpClient
)

@Singleton
class UserRepository @Inject constructor(
    private val apiClient: ApiClient,
    private val database: AppDatabase
)

// === VIEWMODEL LAYER ===
@ViewModelScoped
class GetUserProfileUseCase @Inject constructor(
    private val userRepository: UserRepository // Singleton
)

@ViewModelScoped
class ProfileStateReducer @Inject constructor() {
    private var currentState: ProfileState = ProfileState.Initial

    fun reduce(action: ProfileAction): ProfileState {
        currentState = when (action) {
            is ProfileAction.LoadSuccess -> ProfileState.Loaded(action.user)
            is ProfileAction.LoadError -> ProfileState.Error(action.message)
            ProfileAction.Loading -> ProfileState.Loading
        }
        return currentState
    }
}

// === VIEWMODEL ===
@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val getUserProfile: GetUserProfileUseCase, // ViewModelScoped
    private val stateReducer: ProfileStateReducer,     // ViewModelScoped
    private val analyticsService: AnalyticsService     // Singleton
) : ViewModel() {

    private val _state = MutableStateFlow<ProfileState>(ProfileState.Initial)
    val state: StateFlow<ProfileState> = _state.asStateFlow()

    fun loadProfile(userId: String) {
        viewModelScope.launch {
            _state.value = stateReducer.reduce(ProfileAction.Loading)

            getUserProfile(userId)
                .onSuccess { user ->
                    _state.value = stateReducer.reduce(ProfileAction.LoadSuccess(user))
                    analyticsService.logEvent("profile_loaded")
                }
                .onFailure { error ->
                    _state.value = stateReducer.reduce(ProfileAction.LoadError(error.message ?: ""))
                }
        }
    }
}
```

---

## Dopolnitelnye Voprosy (RU)

- Что произойдет, если использовать `@ActivityScoped` зависимость в `@Singleton` классе?
- Как Hilt обрабатывает scope при использовании shared ViewModel между Fragment-ами?
- Когда стоит создавать кастомные scopes?
- Как scopes влияют на тестирование?

## Follow-ups

- What happens if you use an `@ActivityScoped` dependency in a `@Singleton` class?
- How does Hilt handle scope when using a shared ViewModel between Fragments?
- When should you create custom scopes?
- How do scopes affect testing?

---

## Ssylki (RU)

- [Hilt Components](https://developer.android.com/training/dependency-injection/hilt-android#component-hierarchy)
- [Scoping in Dagger](https://dagger.dev/dev-guide/)

## References

- [Hilt Components](https://developer.android.com/training/dependency-injection/hilt-android#component-hierarchy)
- [Scoping in Dagger](https://dagger.dev/dev-guide/)

---

## Svyazannye Voprosy (RU)

### Medium
- [[q-hilt-setup-annotations--hilt--medium]]
- [[q-hilt-modules-provides--hilt--medium]]
- [[q-hilt-viewmodel-injection--hilt--medium]]

### Hard
- [[q-hilt-custom-components--hilt--hard]]
- [[q-hilt-multimodule--hilt--hard]]
- [[q-hilt-entry-points--hilt--hard]]

## Related Questions

### Medium
- [[q-hilt-setup-annotations--hilt--medium]]
- [[q-hilt-modules-provides--hilt--medium]]
- [[q-hilt-viewmodel-injection--hilt--medium]]

### Hard
- [[q-hilt-custom-components--hilt--hard]]
- [[q-hilt-multimodule--hilt--hard]]
- [[q-hilt-entry-points--hilt--hard]]
