---
id: "20251023-120200"
title: "Hilt / Hilt DI"
aliases: ["Dependency Injection with Hilt", "Hilt DI", "Hilt"]
summary: "Google's officially recommended dependency injection library for Android built on top of Dagger"
topic: "android"
subtopics: ["architecture", "dependency-injection", "hilt"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-android"
related: [c-dependency-injection, c-dagger, c-viewmodel, c-testing, c-mvvm]
created: "2025-10-23"
updated: "2025-10-23"
tags: ["android", "architecture", "concept", "dependency-injection", "difficulty/medium", "hilt"]
---

# Hilt / Hilt DI

## Summary (EN)

Hilt is Google's officially recommended dependency injection library for Android, built on top of Dagger. It reduces the boilerplate code required for Dagger by providing standard Android components with predefined scopes and automatic injection points. Hilt simplifies DI setup with annotations like @HiltAndroidApp, @AndroidEntryPoint, and @Inject, making dependency injection more accessible for Android developers.

## Краткое Описание (RU)

Hilt — официально рекомендуемая Google библиотека внедрения зависимостей для Android, построенная поверх Dagger. Она уменьшает количество шаблонного кода, необходимого для Dagger, предоставляя стандартные Android-компоненты с предопределенными областями видимости и автоматическими точками инъекции. Hilt упрощает настройку DI с помощью аннотаций, таких как @HiltAndroidApp, @AndroidEntryPoint и @Inject.

## Key Points (EN)

- **Built on Dagger**: Uses Dagger's compile-time code generation for performance
- **Reduced boilerplate**: Predefined components and scopes for Android
- **Standard annotations**: @HiltAndroidApp, @AndroidEntryPoint, @Inject
- **Predefined scopes**: @Singleton, @ActivityScoped, @ViewModelScoped, etc.
- **ViewModel integration**: Built-in support for injecting ViewModels

## Ключевые Моменты (RU)

- **Построен на Dagger**: Использует генерацию кода Dagger во время компиляции для производительности
- **Меньше шаблонного кода**: Предопределенные компоненты и области видимости для Android
- **Стандартные аннотации**: @HiltAndroidApp, @AndroidEntryPoint, @Inject
- **Предопределенные области**: @Singleton, @ActivityScoped, @ViewModelScoped и т.д.
- **Интеграция с ViewModel**: Встроенная поддержка инъекции ViewModels

## Setup and Basic Usage

### 1. Application Setup

```kotlin
@HiltAndroidApp
class MyApplication : Application() {
    // Hilt generates a base class that initializes DI
}
```

### 2. Inject into Activity

```kotlin
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    // Field injection
    @Inject lateinit var analytics: AnalyticsService

    // ViewModel injection (Hilt-specific)
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // analytics is automatically injected
    }
}
```

### 3. Inject into Fragment

```kotlin
@AndroidEntryPoint
class UserFragment : Fragment() {

    @Inject lateinit var repository: UserRepository

    private val viewModel: UserViewModel by viewModels()

    // Fragment-specific: can use activityViewModels()
    private val sharedViewModel: SharedViewModel by activityViewModels()
}
```

### 4. Inject into ViewModel

```kotlin
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository,
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    // Use dependencies
}
```

## Modules and Bindings

### Providing Dependencies

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideRetrofit(): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com")
            .build()
    }

    @Provides
    @Singleton
    fun provideApiService(retrofit: Retrofit): ApiService {
        return retrofit.create(ApiService::class.java)
    }
}
```

### Binding Interfaces

```kotlin
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindUserRepository(
        impl: UserRepositoryImpl
    ): UserRepository
}
```

## Predefined Scopes

```kotlin
// Application lifetime
@Singleton

// Activity lifetime
@ActivityScoped
@InstallIn(ActivityComponent::class)

// Fragment lifetime
@FragmentScoped
@InstallIn(FragmentComponent::class)

// ViewModel lifetime
@ViewModelScoped
@InstallIn(ViewModelComponent::class)

// Service lifetime
@ServiceScoped
@InstallIn(ServiceComponent::class)
```

### Scope Example

```kotlin
@Module
@InstallIn(ActivityComponent::class)
object ActivityModule {

    @Provides
    @ActivityScoped  // Lives as long as the Activity
    fun provideLocationTracker(
        activity: Activity
    ): LocationTracker {
        return LocationTracker(activity)
    }
}
```

## Qualifiers

```kotlin
// Define qualifiers
@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class AuthInterceptor

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class LoggingInterceptor

// Provide qualified dependencies
@Module
@InstallIn(SingletonComponent::class)
object InterceptorModule {

    @Provides
    @AuthInterceptor
    fun provideAuthInterceptor(): Interceptor {
        return AuthInterceptor()
    }

    @Provides
    @LoggingInterceptor
    fun provideLoggingInterceptor(): Interceptor {
        return HttpLoggingInterceptor()
    }
}

// Inject qualified dependencies
class ApiClient @Inject constructor(
    @AuthInterceptor private val authInterceptor: Interceptor,
    @LoggingInterceptor private val loggingInterceptor: Interceptor
)
```

## Use Cases

### When to Use

- Android projects requiring dependency injection
- Applications with complex dependency graphs
- Projects needing ViewModel injection
- Teams wanting official Google DI solution
- Migrating from manual Dagger setup
- Projects requiring scoped dependencies

### When to Avoid

- Very simple apps with minimal dependencies
- Projects already using Dagger with custom setup (migration overhead)
- Non-Android Kotlin projects (use Koin or manual Dagger)
- Learning Android basics (adds complexity for beginners)

## Trade-offs

**Pros**:
- **Official support**: Recommended by Google with ongoing support
- **Less boilerplate**: Compared to raw Dagger (30-40% less code)
- **Type-safe**: Compile-time verification of dependencies
- **Performance**: No runtime overhead (compile-time generation)
- **ViewModel integration**: Simplified ViewModel injection
- **Standard scopes**: Predefined Android component scopes
- **Better error messages**: Clearer than Dagger errors

**Cons**:
- **Build time**: Increases build time due to code generation
- **Learning curve**: Still requires understanding DI concepts
- **Dagger knowledge**: Complex issues may require Dagger understanding
- **Generated code**: Large amount of generated code in build folder
- **Limited customization**: Less flexible than pure Dagger
- **Android-only**: Not suitable for multiplatform projects

## Hilt Vs Dagger Vs Koin

| Feature | Hilt | Dagger | Koin |
|---------|------|--------|------|
| **Type** | Compile-time | Compile-time | Runtime |
| **Boilerplate** | Low | High | Very Low |
| **Learning curve** | Medium | Steep | Easy |
| **Performance** | Excellent | Excellent | Good |
| **Android integration** | Built-in | Manual | Good |
| **Multiplatform** | No | Yes | Yes |
| **Error detection** | Compile-time | Compile-time | Runtime |

## Common Patterns

### Testing with Hilt

```kotlin
@HiltAndroidTest
class UserRepositoryTest {

    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @Inject
    lateinit var repository: UserRepository

    @Before
    fun init() {
        hiltRule.inject()
    }

    @Test
    fun testUserRepository() {
        // Test using injected repository
    }
}

// Replace dependencies in tests
@Module
@TestInstallIn(
    components = [SingletonComponent::class],
    replaces = [RepositoryModule::class]
)
abstract class FakeRepositoryModule {
    @Binds
    abstract fun bindRepository(
        fake: FakeUserRepository
    ): UserRepository
}
```

## Related Questions

- [[q-hilt-vs-dagger--android--medium]]
- [[q-hilt-viewmodel-injection--android--medium]]
- [[q-hilt-modules-scope--android--hard]]
- [[q-dependency-injection-benefits--android--medium]]

## Related Concepts

- [[c-dependency-injection]] - General DI pattern
- [[c-dagger]] - Underlying framework for Hilt
- [[c-viewmodel]] - Commonly injected with Hilt
- [[c-testing]] - Hilt has built-in testing support

## References

- [Hilt Official Documentation](https://developer.android.com/training/dependency-injection/hilt-android)
- [Hilt and Dagger](https://dagger.dev/hilt/)
- [Hilt Codelab](https://developer.android.com/codelabs/android-hilt)
- [Migrating to Hilt](https://developer.android.com/training/dependency-injection/hilt-migration)
- [Hilt Testing](https://developer.android.com/training/dependency-injection/hilt-testing)
