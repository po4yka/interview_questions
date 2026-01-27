---
id: android-hilt-008
title: Hilt in Multi-module Projects / Hilt в многомодульных проектах
aliases:
- Hilt Multimodule
- Multi-module DI
- Hilt Gradle Modules
- Feature Modules Hilt
topic: android
subtopics:
- di-hilt
- architecture
- modularization
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
- android/modularization
- difficulty/hard
- hilt
- multimodule
- dependency-injection
anki_cards:
- slug: android-hilt-008-0-en
  language: en
- slug: android-hilt-008-0-ru
  language: ru
---
# Vopros (RU)
> Как организовать Hilt в многомодульном Android-проекте? Какие паттерны и best practices существуют?

# Question (EN)
> How do you organize Hilt in a multi-module Android project? What patterns and best practices exist?

---

## Otvet (RU)

Многомодульные проекты с Hilt требуют особого внимания к организации зависимостей, чтобы сохранить преимущества модуляризации (изоляция, переиспользование, параллельная сборка) и при этом обеспечить корректную работу DI.

### Типичная структура модулей

```
app/                          # Application module
    - @HiltAndroidApp
    - Aggregates all feature modules

core/
    core-common/              # Shared utilities, extensions
    core-data/                # Repositories, data sources
    core-network/             # Retrofit, OkHttp setup
    core-database/            # Room database
    core-domain/              # Use cases, domain models
    core-ui/                  # Shared UI components

feature/
    feature-auth/             # Authentication feature
    feature-home/             # Home screen
    feature-profile/          # User profile
    feature-settings/         # Settings
```

### Настройка Gradle для модулей

```kotlin
// build.gradle.kts (root)
plugins {
    id("com.google.dagger.hilt.android") version "2.52" apply false
    id("com.google.devtools.ksp") version "2.0.0-1.0.21" apply false
}

// build.gradle.kts (app module)
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("com.google.dagger.hilt.android")
    id("com.google.devtools.ksp")
}

dependencies {
    implementation("com.google.dagger:hilt-android:2.52")
    ksp("com.google.dagger:hilt-android-compiler:2.52")

    // Feature modules
    implementation(project(":feature:feature-auth"))
    implementation(project(":feature:feature-home"))
    implementation(project(":feature:feature-profile"))

    // Core modules
    implementation(project(":core:core-data"))
    implementation(project(":core:core-network"))
}

// build.gradle.kts (feature module)
plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.android")
    id("com.google.dagger.hilt.android")
    id("com.google.devtools.ksp")
}

dependencies {
    implementation("com.google.dagger:hilt-android:2.52")
    ksp("com.google.dagger:hilt-android-compiler:2.52")

    implementation(project(":core:core-domain"))
    implementation(project(":core:core-ui"))
}
```

### Паттерн: Core Module с общими зависимостями

```kotlin
// :core:core-network
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient {
        return OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .addInterceptor(HttpLoggingInterceptor())
            .build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl(BuildConfig.BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }
}

// :core:core-database
@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideDatabase(
        @ApplicationContext context: Context
    ): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "app_database"
        ).build()
    }
}
```

### Паттерн: Feature Module с изолированными зависимостями

```kotlin
// :feature:feature-auth

// Публичный API модуля
interface AuthRepository {
    suspend fun login(email: String, password: String): Result<User>
    suspend fun logout()
    fun isLoggedIn(): Flow<Boolean>
}

// Внутренняя реализация
internal class AuthRepositoryImpl @Inject constructor(
    private val authApi: AuthApi,
    private val tokenStorage: TokenStorage
) : AuthRepository {

    override suspend fun login(email: String, password: String): Result<User> {
        return runCatching {
            val response = authApi.login(LoginRequest(email, password))
            tokenStorage.saveToken(response.token)
            response.user
        }
    }

    override suspend fun logout() {
        tokenStorage.clearToken()
    }

    override fun isLoggedIn(): Flow<Boolean> {
        return tokenStorage.hasToken()
    }
}

// API интерфейс (internal)
internal interface AuthApi {
    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): LoginResponse
}

// DI модуль
@Module
@InstallIn(SingletonComponent::class)
internal abstract class AuthModule {

    @Binds
    @Singleton
    abstract fun bindAuthRepository(impl: AuthRepositoryImpl): AuthRepository

    companion object {
        @Provides
        @Singleton
        internal fun provideAuthApi(retrofit: Retrofit): AuthApi {
            return retrofit.create(AuthApi::class.java)
        }
    }
}

// ViewModel (public)
@HiltViewModel
class LoginViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {

    private val _loginState = MutableStateFlow<LoginState>(LoginState.Idle)
    val loginState: StateFlow<LoginState> = _loginState.asStateFlow()

    fun login(email: String, password: String) {
        viewModelScope.launch {
            _loginState.value = LoginState.Loading
            authRepository.login(email, password)
                .onSuccess { user ->
                    _loginState.value = LoginState.Success(user)
                }
                .onFailure { error ->
                    _loginState.value = LoginState.Error(error.message ?: "")
                }
        }
    }
}
```

### Паттерн: Интерфейс в domain, реализация в data

```kotlin
// :core:core-domain (чистый Kotlin модуль, без Hilt)
interface UserRepository {
    suspend fun getUser(id: String): User
    suspend fun updateUser(user: User)
    fun observeUser(id: String): Flow<User>
}

data class User(
    val id: String,
    val name: String,
    val email: String
)

// :core:core-data (Android модуль с Hilt)
internal class UserRepositoryImpl @Inject constructor(
    private val userApi: UserApi,
    private val userDao: UserDao,
    @IoDispatcher private val dispatcher: CoroutineDispatcher
) : UserRepository {

    override suspend fun getUser(id: String): User = withContext(dispatcher) {
        try {
            userApi.getUser(id).also { user ->
                userDao.insert(user.toEntity())
            }
        } catch (e: Exception) {
            userDao.getUser(id)?.toDomain() ?: throw e
        }
    }

    override suspend fun updateUser(user: User) = withContext(dispatcher) {
        userApi.updateUser(user)
        userDao.insert(user.toEntity())
    }

    override fun observeUser(id: String): Flow<User> {
        return userDao.observeUser(id)
            .map { it.toDomain() }
            .flowOn(dispatcher)
    }
}

@Module
@InstallIn(SingletonComponent::class)
internal abstract class DataModule {

    @Binds
    @Singleton
    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository
}
```

### Паттерн: API модуля для навигации

```kotlin
// :feature:feature-profile:api (отдельный модуль с публичным API)
interface ProfileNavigator {
    fun navigateToProfile(userId: String)
    fun navigateToEditProfile()
}

// :feature:feature-profile:impl (реализация)
internal class ProfileNavigatorImpl @Inject constructor(
    private val navController: NavController
) : ProfileNavigator {

    override fun navigateToProfile(userId: String) {
        navController.navigate("profile/$userId")
    }

    override fun navigateToEditProfile() {
        navController.navigate("profile/edit")
    }
}

@Module
@InstallIn(ActivityComponent::class)
internal abstract class ProfileNavigatorModule {

    @Binds
    abstract fun bindProfileNavigator(impl: ProfileNavigatorImpl): ProfileNavigator
}

// Использование в другом feature модуле
// :feature:feature-home
@HiltViewModel
class HomeViewModel @Inject constructor(
    private val profileNavigator: ProfileNavigator // Зависимость от API, не от impl
) : ViewModel() {

    fun onUserClicked(userId: String) {
        profileNavigator.navigateToProfile(userId)
    }
}
```

### Агрегация модулей в App

```kotlin
// :app
@HiltAndroidApp
class MyApplication : Application()

// Все модули автоматически обнаруживаются через @InstallIn
// Не нужно явно подключать модули в app

// Зависимости в build.gradle.kts определяют граф:
// app -> feature-auth -> core-domain
//     -> feature-home -> core-domain, core-data
//     -> feature-profile -> core-domain
//     -> core-data -> core-network, core-database
```

### Тестирование в многомодульном проекте

```kotlin
// :feature:feature-auth (тесты)
@HiltAndroidTest
class LoginViewModelTest {

    @get:Rule
    val hiltRule = HiltAndroidRule(this)

    @Inject
    lateinit var authRepository: AuthRepository

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun `login success updates state`() = runTest {
        // Test using injected fake repository
    }
}

// Тестовый модуль, заменяющий production
@Module
@TestInstallIn(
    components = [SingletonComponent::class],
    replaces = [AuthModule::class]
)
abstract class FakeAuthModule {

    @Binds
    @Singleton
    abstract fun bindAuthRepository(impl: FakeAuthRepository): AuthRepository
}

class FakeAuthRepository @Inject constructor() : AuthRepository {
    var shouldSucceed = true
    var loginDelay = 0L

    override suspend fun login(email: String, password: String): Result<User> {
        delay(loginDelay)
        return if (shouldSucceed) {
            Result.success(User("1", "Test User", email))
        } else {
            Result.failure(Exception("Login failed"))
        }
    }

    override suspend fun logout() { /* no-op */ }

    override fun isLoggedIn(): Flow<Boolean> = flowOf(false)
}
```

### Best Practices

1. **Используйте internal** - скрывайте реализации модулей
2. **Публикуйте интерфейсы** - другие модули зависят от абстракций
3. **Избегайте циклических зависимостей** - используйте :api модули
4. **Группируйте по feature** - не по техническому слою
5. **Единый источник версий** - Version Catalogs или buildSrc

```kotlin
// Версии в одном месте (libs.versions.toml)
[versions]
hilt = "2.52"
room = "2.6.1"

[libraries]
hilt-android = { module = "com.google.dagger:hilt-android", version.ref = "hilt" }
hilt-compiler = { module = "com.google.dagger:hilt-android-compiler", version.ref = "hilt" }

[plugins]
hilt = { id = "com.google.dagger.hilt.android", version.ref = "hilt" }
```

---

## Answer (EN)

Multi-module projects with Hilt require special attention to dependency organization to preserve the benefits of modularization (isolation, reusability, parallel builds) while ensuring correct DI operation.

### Typical Module Structure

```
app/                          # Application module
    - @HiltAndroidApp
    - Aggregates all feature modules

core/
    core-common/              # Shared utilities, extensions
    core-data/                # Repositories, data sources
    core-network/             # Retrofit, OkHttp setup
    core-database/            # Room database
    core-domain/              # Use cases, domain models
    core-ui/                  # Shared UI components

feature/
    feature-auth/             # Authentication feature
    feature-home/             # Home screen
    feature-profile/          # User profile
    feature-settings/         # Settings
```

### Gradle Setup for Modules

```kotlin
// build.gradle.kts (root)
plugins {
    id("com.google.dagger.hilt.android") version "2.52" apply false
    id("com.google.devtools.ksp") version "2.0.0-1.0.21" apply false
}

// build.gradle.kts (app module)
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("com.google.dagger.hilt.android")
    id("com.google.devtools.ksp")
}

dependencies {
    implementation("com.google.dagger:hilt-android:2.52")
    ksp("com.google.dagger:hilt-android-compiler:2.52")

    // Feature modules
    implementation(project(":feature:feature-auth"))
    implementation(project(":feature:feature-home"))
    implementation(project(":feature:feature-profile"))

    // Core modules
    implementation(project(":core:core-data"))
    implementation(project(":core:core-network"))
}

// build.gradle.kts (feature module)
plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.android")
    id("com.google.dagger.hilt.android")
    id("com.google.devtools.ksp")
}

dependencies {
    implementation("com.google.dagger:hilt-android:2.52")
    ksp("com.google.dagger:hilt-android-compiler:2.52")

    implementation(project(":core:core-domain"))
    implementation(project(":core:core-ui"))
}
```

### Pattern: Core Module with Shared Dependencies

```kotlin
// :core:core-network
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient {
        return OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .addInterceptor(HttpLoggingInterceptor())
            .build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl(BuildConfig.BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }
}
```

### Pattern: Feature Module with Isolated Dependencies

```kotlin
// :feature:feature-auth

// Public API of the module
interface AuthRepository {
    suspend fun login(email: String, password: String): Result<User>
    suspend fun logout()
    fun isLoggedIn(): Flow<Boolean>
}

// Internal implementation
internal class AuthRepositoryImpl @Inject constructor(
    private val authApi: AuthApi,
    private val tokenStorage: TokenStorage
) : AuthRepository {

    override suspend fun login(email: String, password: String): Result<User> {
        return runCatching {
            val response = authApi.login(LoginRequest(email, password))
            tokenStorage.saveToken(response.token)
            response.user
        }
    }

    override suspend fun logout() {
        tokenStorage.clearToken()
    }

    override fun isLoggedIn(): Flow<Boolean> {
        return tokenStorage.hasToken()
    }
}

// DI module
@Module
@InstallIn(SingletonComponent::class)
internal abstract class AuthModule {

    @Binds
    @Singleton
    abstract fun bindAuthRepository(impl: AuthRepositoryImpl): AuthRepository

    companion object {
        @Provides
        @Singleton
        internal fun provideAuthApi(retrofit: Retrofit): AuthApi {
            return retrofit.create(AuthApi::class.java)
        }
    }
}
```

### Pattern: Interface in domain, implementation in data

```kotlin
// :core:core-domain (pure Kotlin module, no Hilt)
interface UserRepository {
    suspend fun getUser(id: String): User
    suspend fun updateUser(user: User)
    fun observeUser(id: String): Flow<User>
}

// :core:core-data (Android module with Hilt)
internal class UserRepositoryImpl @Inject constructor(
    private val userApi: UserApi,
    private val userDao: UserDao,
    @IoDispatcher private val dispatcher: CoroutineDispatcher
) : UserRepository {
    // Implementation...
}

@Module
@InstallIn(SingletonComponent::class)
internal abstract class DataModule {

    @Binds
    @Singleton
    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository
}
```

### Best Practices

1. **Use internal** - hide module implementations
2. **Publish interfaces** - other modules depend on abstractions
3. **Avoid circular dependencies** - use :api modules
4. **Group by feature** - not by technical layer
5. **Single source of versions** - Version Catalogs or buildSrc

---

## Dopolnitelnye Voprosy (RU)

- Как избежать циклических зависимостей между feature-модулями?
- Когда стоит выделять отдельный :api модуль?
- Как организовать навигацию между feature-модулями с Hilt?
- Как оптимизировать время сборки в многомодульном проекте с Hilt?

## Follow-ups

- How do you avoid circular dependencies between feature modules?
- When should you create a separate :api module?
- How do you organize navigation between feature modules with Hilt?
- How do you optimize build time in a multi-module project with Hilt?

---

## Ssylki (RU)

- [Hilt in Multi-module apps](https://developer.android.com/training/dependency-injection/hilt-multi-module)
- [Guide to Android Modularization](https://developer.android.com/topic/modularization)

## References

- [Hilt in Multi-module apps](https://developer.android.com/training/dependency-injection/hilt-multi-module)
- [Guide to Android Modularization](https://developer.android.com/topic/modularization)

---

## Svyazannye Voprosy (RU)

### Medium
- [[q-hilt-setup-annotations--hilt--medium]]
- [[q-hilt-modules-provides--hilt--medium]]

### Hard
- [[q-hilt-scopes--hilt--hard]]
- [[q-hilt-custom-components--hilt--hard]]
- [[q-hilt-entry-points--hilt--hard]]

## Related Questions

### Medium
- [[q-hilt-setup-annotations--hilt--medium]]
- [[q-hilt-modules-provides--hilt--medium]]

### Hard
- [[q-hilt-scopes--hilt--hard]]
- [[q-hilt-custom-components--hilt--hard]]
- [[q-hilt-entry-points--hilt--hard]]
