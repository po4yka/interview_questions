---
id: android-hilt-010
title: Hilt Custom Components / Кастомные компоненты Hilt
aliases:
- Hilt Custom Components
- Custom Component Hierarchy
- DefineComponent
- Custom Scopes Hilt
topic: android
subtopics:
- di-hilt
- architecture
question_kind: theory
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-hilt-scopes--hilt--hard
- q-hilt-modules-provides--hilt--medium
- q-hilt-entry-points--hilt--hard
created: 2026-01-23
updated: 2026-01-23
tags:
- android/di-hilt
- android/architecture
- difficulty/hard
- hilt
- custom-components
- dependency-injection
anki_cards:
- slug: android-hilt-010-0-en
  language: en
- slug: android-hilt-010-0-ru
  language: ru
---
# Vopros (RU)
> Как создавать кастомные компоненты и scopes в Hilt? Когда это необходимо и как правильно организовать иерархию?

# Question (EN)
> How do you create custom components and scopes in Hilt? When is this necessary and how do you properly organize the hierarchy?

---

## Otvet (RU)

Хотя стандартные компоненты Hilt покрывают большинство случаев, иногда требуется создать кастомный компонент для специфичного жизненного цикла, не соответствующего стандартным Android-компонентам.

### Когда нужны кастомные компоненты

1. **User Session** - зависимости, привязанные к авторизованному пользователю
2. **Feature Flow** - многоэкранный процесс (checkout, onboarding)
3. **Background Task** - долгоживущие операции
4. **Custom Lifecycle** - нестандартные жизненные циклы

### Создание кастомного компонента

```kotlin
// 1. Определяем кастомный Scope
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class UserSessionScope

// 2. Определяем компонент
@DefineComponent(parent = SingletonComponent::class)
interface UserSessionComponent

// 3. Определяем Builder для компонента
@DefineComponent.Builder
interface UserSessionComponentBuilder {
    fun setUser(@BindsInstance user: User): UserSessionComponentBuilder
    fun build(): UserSessionComponent
}
```

### Управление жизненным циклом компонента

```kotlin
// Менеджер компонента
@Singleton
class UserSessionComponentManager @Inject constructor(
    private val componentBuilder: Provider<UserSessionComponentBuilder>
) {

    private var currentComponent: UserSessionComponent? = null
    private var currentUser: User? = null

    fun startSession(user: User) {
        if (currentComponent != null) {
            endSession()
        }

        currentUser = user
        currentComponent = componentBuilder.get()
            .setUser(user)
            .build()
    }

    fun endSession() {
        currentComponent = null
        currentUser = null
    }

    fun getComponent(): UserSessionComponent {
        return currentComponent
            ?: throw IllegalStateException("No active user session")
    }

    fun isSessionActive(): Boolean = currentComponent != null

    fun getCurrentUser(): User? = currentUser
}
```

### Модуль для кастомного компонента

```kotlin
@Module
@InstallIn(UserSessionComponent::class)
object UserSessionModule {

    @Provides
    @UserSessionScope
    fun provideUserPreferences(user: User): UserPreferences {
        return UserPreferences(userId = user.id)
    }

    @Provides
    @UserSessionScope
    fun provideUserApiService(
        retrofit: Retrofit, // Из SingletonComponent
        user: User
    ): UserApiService {
        return retrofit.create(UserApiService::class.java)
    }
}

@Module
@InstallIn(UserSessionComponent::class)
abstract class UserSessionBindingsModule {

    @Binds
    @UserSessionScope
    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository

    @Binds
    @UserSessionScope
    abstract fun bindUserAnalytics(impl: UserAnalyticsImpl): UserAnalytics
}
```

### EntryPoint для доступа к зависимостям

```kotlin
@EntryPoint
@InstallIn(UserSessionComponent::class)
interface UserSessionEntryPoint {
    fun userRepository(): UserRepository
    fun userPreferences(): UserPreferences
    fun userAnalytics(): UserAnalytics
}

// Использование
class SomeClass @Inject constructor(
    private val sessionManager: UserSessionComponentManager
) {

    fun doSomethingWithUser() {
        val entryPoint = EntryPoints.get(
            sessionManager.getComponent(),
            UserSessionEntryPoint::class.java
        )

        val repository = entryPoint.userRepository()
        // Используем repository...
    }
}
```

### Полный пример: User Session Flow

```kotlin
// === ОПРЕДЕЛЕНИЕ КОМПОНЕНТА ===

@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class UserSessionScope

@DefineComponent(parent = SingletonComponent::class)
interface UserSessionComponent

@DefineComponent.Builder
interface UserSessionComponentBuilder {
    fun setUser(@BindsInstance user: User): UserSessionComponentBuilder
    fun setAuthToken(@BindsInstance @AuthToken token: String): UserSessionComponentBuilder
    fun build(): UserSessionComponent
}

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class AuthToken

// === МОДУЛИ ===

@Module
@InstallIn(UserSessionComponent::class)
object UserSessionModule {

    @Provides
    @UserSessionScope
    fun provideAuthenticatedOkHttpClient(
        @AuthToken token: String,
        baseClient: OkHttpClient // Из SingletonComponent
    ): OkHttpClient {
        return baseClient.newBuilder()
            .addInterceptor { chain ->
                val request = chain.request().newBuilder()
                    .addHeader("Authorization", "Bearer $token")
                    .build()
                chain.proceed(request)
            }
            .build()
    }

    @Provides
    @UserSessionScope
    fun provideUserRetrofit(
        authenticatedClient: OkHttpClient,
        gson: Gson // Из SingletonComponent
    ): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .client(authenticatedClient)
            .addConverterFactory(GsonConverterFactory.create(gson))
            .build()
    }
}

// === МЕНЕДЖЕР СЕССИИ ===

@Singleton
class SessionManager @Inject constructor(
    private val componentBuilder: Provider<UserSessionComponentBuilder>,
    private val authRepository: AuthRepository
) {

    private val _sessionState = MutableStateFlow<SessionState>(SessionState.LoggedOut)
    val sessionState: StateFlow<SessionState> = _sessionState.asStateFlow()

    private var component: UserSessionComponent? = null

    suspend fun login(email: String, password: String): Result<User> {
        return authRepository.login(email, password)
            .onSuccess { authResult ->
                startSession(authResult.user, authResult.token)
            }
    }

    private fun startSession(user: User, token: String) {
        component = componentBuilder.get()
            .setUser(user)
            .setAuthToken(token)
            .build()

        _sessionState.value = SessionState.LoggedIn(user)
    }

    suspend fun logout() {
        authRepository.logout()
        endSession()
    }

    private fun endSession() {
        component = null
        _sessionState.value = SessionState.LoggedOut
    }

    fun requireComponent(): UserSessionComponent {
        return component ?: throw IllegalStateException("User not logged in")
    }

    fun isLoggedIn(): Boolean = component != null
}

sealed interface SessionState {
    data object LoggedOut : SessionState
    data class LoggedIn(val user: User) : SessionState
}

// === ENTRY POINT ===

@EntryPoint
@InstallIn(UserSessionComponent::class)
interface UserSessionEntryPoint {
    fun userProfileRepository(): UserProfileRepository
    fun userSettingsRepository(): UserSettingsRepository
    fun userAnalyticsService(): UserAnalyticsService
}

// === ИСПОЛЬЗОВАНИЕ В VIEWMODEL ===

@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val sessionManager: SessionManager
) : ViewModel() {

    private val _profile = MutableStateFlow<ProfileState>(ProfileState.Loading)
    val profile: StateFlow<ProfileState> = _profile.asStateFlow()

    init {
        loadProfile()
    }

    private fun loadProfile() {
        viewModelScope.launch {
            try {
                val entryPoint = EntryPoints.get(
                    sessionManager.requireComponent(),
                    UserSessionEntryPoint::class.java
                )

                val repository = entryPoint.userProfileRepository()
                val profile = repository.getCurrentUserProfile()

                _profile.value = ProfileState.Success(profile)
            } catch (e: Exception) {
                _profile.value = ProfileState.Error(e.message ?: "")
            }
        }
    }
}

// === ИСПОЛЬЗОВАНИЕ В ACTIVITY ===

@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    @Inject
    lateinit var sessionManager: SessionManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            sessionManager.sessionState.collect { state ->
                when (state) {
                    is SessionState.LoggedOut -> navigateToLogin()
                    is SessionState.LoggedIn -> navigateToHome()
                }
            }
        }
    }
}
```

### Пример: Feature Flow Component

```kotlin
// Компонент для checkout flow
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class CheckoutScope

@DefineComponent(parent = ActivityRetainedComponent::class)
interface CheckoutComponent

@DefineComponent.Builder
interface CheckoutComponentBuilder {
    fun setCartId(@BindsInstance cartId: String): CheckoutComponentBuilder
    fun build(): CheckoutComponent
}

@Module
@InstallIn(CheckoutComponent::class)
object CheckoutModule {

    @Provides
    @CheckoutScope
    fun provideCheckoutState(cartId: String): CheckoutState {
        return CheckoutState(cartId = cartId)
    }
}

// Менеджер checkout flow
class CheckoutFlowManager @Inject constructor(
    private val componentBuilder: Provider<CheckoutComponentBuilder>
) {

    private var component: CheckoutComponent? = null

    fun startCheckout(cartId: String) {
        component = componentBuilder.get()
            .setCartId(cartId)
            .build()
    }

    fun finishCheckout() {
        component = null
    }

    fun getComponent(): CheckoutComponent {
        return component ?: throw IllegalStateException("Checkout not started")
    }
}
```

### Иерархия кастомных компонентов

```
SingletonComponent
    |
    +-- UserSessionComponent (custom)
    |       |
    |       +-- UserFeatureComponent (custom, optional)
    |
    +-- ActivityRetainedComponent
            |
            +-- CheckoutComponent (custom)
```

### Best Practices

1. **Минимизируйте кастомные компоненты** - используйте стандартные, когда возможно
2. **Четко определяйте lifecycle** - когда создается и уничтожается
3. **Используйте Provider** для Builder - для отложенного создания
4. **Документируйте иерархию** - чтобы команда понимала структуру
5. **Тестируйте lifecycle** - убедитесь, что компоненты правильно очищаются

### Когда НЕ использовать кастомные компоненты

- Для простого scoping используйте стандартные компоненты
- Для передачи runtime-параметров используйте Assisted Injection
- Для feature modules используйте стандартную модульность Hilt
- Если можно обойтись SavedStateHandle - используйте его

---

## Answer (EN)

While standard Hilt components cover most cases, sometimes a custom component is needed for a specific lifecycle that doesn't match standard Android components.

### When Custom Components Are Needed

1. **User Session** - dependencies bound to authenticated user
2. **Feature Flow** - multi-screen process (checkout, onboarding)
3. **Background Task** - long-running operations
4. **Custom Lifecycle** - non-standard lifecycles

### Creating a Custom Component

```kotlin
// 1. Define custom Scope
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class UserSessionScope

// 2. Define component
@DefineComponent(parent = SingletonComponent::class)
interface UserSessionComponent

// 3. Define Builder for component
@DefineComponent.Builder
interface UserSessionComponentBuilder {
    fun setUser(@BindsInstance user: User): UserSessionComponentBuilder
    fun build(): UserSessionComponent
}
```

### Managing Component Lifecycle

```kotlin
@Singleton
class UserSessionComponentManager @Inject constructor(
    private val componentBuilder: Provider<UserSessionComponentBuilder>
) {

    private var currentComponent: UserSessionComponent? = null

    fun startSession(user: User) {
        if (currentComponent != null) {
            endSession()
        }
        currentComponent = componentBuilder.get()
            .setUser(user)
            .build()
    }

    fun endSession() {
        currentComponent = null
    }

    fun getComponent(): UserSessionComponent {
        return currentComponent
            ?: throw IllegalStateException("No active user session")
    }
}
```

### Module for Custom Component

```kotlin
@Module
@InstallIn(UserSessionComponent::class)
object UserSessionModule {

    @Provides
    @UserSessionScope
    fun provideUserPreferences(user: User): UserPreferences {
        return UserPreferences(userId = user.id)
    }
}
```

### EntryPoint for Accessing Dependencies

```kotlin
@EntryPoint
@InstallIn(UserSessionComponent::class)
interface UserSessionEntryPoint {
    fun userRepository(): UserRepository
    fun userPreferences(): UserPreferences
}

// Usage
val entryPoint = EntryPoints.get(
    sessionManager.getComponent(),
    UserSessionEntryPoint::class.java
)
val repository = entryPoint.userRepository()
```

### Best Practices

1. **Minimize custom components** - use standard ones when possible
2. **Clearly define lifecycle** - when created and destroyed
3. **Use Provider for Builder** - for lazy creation
4. **Document hierarchy** - so team understands structure
5. **Test lifecycle** - ensure components are properly cleaned up

### When NOT to Use Custom Components

- For simple scoping use standard components
- For runtime parameters use Assisted Injection
- For feature modules use standard Hilt modularity
- If SavedStateHandle works - use it

---

## Dopolnitelnye Voprosy (RU)

- Как тестировать классы, зависящие от кастомного компонента?
- Можно ли создать компонент, который является child от ActivityComponent?
- Как обрабатывать зависимости между кастомными компонентами?
- Какие альтернативы кастомным компонентам существуют?

## Follow-ups

- How do you test classes that depend on a custom component?
- Can you create a component that is a child of ActivityComponent?
- How do you handle dependencies between custom components?
- What alternatives to custom components exist?

---

## Ssylki (RU)

- [Hilt Custom Components](https://dagger.dev/hilt/custom-components.html)
- [Dagger Components](https://dagger.dev/dev-guide/)

## References

- [Hilt Custom Components](https://dagger.dev/hilt/custom-components.html)
- [Dagger Components](https://dagger.dev/dev-guide/)

---

## Svyazannye Voprosy (RU)

### Medium
- [[q-hilt-modules-provides--hilt--medium]]
- [[q-hilt-viewmodel-injection--hilt--medium]]

### Hard
- [[q-hilt-scopes--hilt--hard]]
- [[q-hilt-entry-points--hilt--hard]]
- [[q-hilt-assisted-injection--hilt--hard]]
- [[q-hilt-multimodule--hilt--hard]]

## Related Questions

### Medium
- [[q-hilt-modules-provides--hilt--medium]]
- [[q-hilt-viewmodel-injection--hilt--medium]]

### Hard
- [[q-hilt-scopes--hilt--hard]]
- [[q-hilt-entry-points--hilt--hard]]
- [[q-hilt-assisted-injection--hilt--hard]]
- [[q-hilt-multimodule--hilt--hard]]
