---
id: "20251023-120400"
title: "Dagger / Dagger DI"
aliases: ["Dagger 2", "Dagger DI", "Dagger", "Dependency Injection Framework"]
summary: "Compile-time dependency injection framework for Java and Android using code generation"
topic: "android"
subtopics: ["architecture", "dagger", "dependency-injection"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-android"
related: []
created: "2025-10-23"
updated: "2025-10-23"
tags: ["android", "architecture", "concept", "dagger", "dependency-injection", "difficulty/medium"]
---

# Dagger / Dagger DI

## Summary (EN)

Dagger is a fully compile-time dependency injection framework for Java and Android that uses annotation processing to generate code for dependency injection. Unlike runtime DI frameworks, Dagger validates dependencies at compile-time and generates efficient code without using reflection, resulting in excellent runtime performance. While Dagger has a steep learning curve due to its concepts (Components, Modules, Scopes), it provides type-safe and performant dependency injection.

## Краткое Описание (RU)

Dagger — это полностью компилируемый фреймворк внедрения зависимостей для Java и Android, который использует обработку аннотаций для генерации кода инъекции зависимостей. В отличие от runtime DI-фреймворков, Dagger проверяет зависимости во время компиляции и генерирует эффективный код без использования рефлексии, что обеспечивает отличную производительность. Хотя Dagger имеет крутую кривую обучения из-за своих концепций (Components, Modules, Scopes), он обеспечивает типобезопасное и производительное внедрение зависимостей.

## Key Points (EN)

- **Compile-time**: Generates code during compilation, no runtime overhead
- **Type-safe**: Compile-time verification of dependency graphs
- **Components**: Define injection points and dependency scope
- **Modules**: Provide dependencies through @Provides or @Binds
- **Scopes**: Control lifetime of dependencies (@Singleton, custom scopes)
- **Subcomponents**: Hierarchical component structure for nested scopes

## Ключевые Моменты (RU)

- **Время компиляции**: Генерирует код во время компиляции, нет накладных расходов во время выполнения
- **Типобезопасность**: Проверка графа зависимостей во время компиляции
- **Компоненты**: Определяют точки инъекции и область видимости зависимостей
- **Модули**: Предоставляют зависимости через @Provides или @Binds
- **Области видимости**: Управление жизненным циклом зависимостей (@Singleton, кастомные scope)
- **Подкомпоненты**: Иерархическая структура компонентов для вложенных областей

## Core Concepts

### 1. Components

Components are interfaces that define the connection between providers (modules) and consumers (injection sites).

```kotlin
@Singleton
@Component(modules = [NetworkModule::class, DatabaseModule::class])
interface AppComponent {
    // Injection methods
    fun inject(activity: MainActivity)

    // Provision methods
    fun getRepository(): UserRepository

    // Subcomponent builders
    fun activityComponent(): ActivityComponent.Factory
}
```

### 2. Modules

Modules provide dependencies that cannot be constructor-injected (interfaces, third-party classes, complex initialization).

```kotlin
@Module
object NetworkModule {

    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com")
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient {
        return OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .build()
    }

    @Provides
    @Singleton
    fun provideApiService(retrofit: Retrofit): ApiService {
        return retrofit.create(ApiService::class.java)
    }
}
```

### 3. @Inject Constructor

The simplest way to provide a dependency - annotate the constructor.

```kotlin
// Automatically provided by Dagger
class UserRepository @Inject constructor(
    private val apiService: ApiService,
    private val database: UserDatabase,
    private val preferences: UserPreferences
) {
    // Implementation
}
```

### 4. @Binds For Interfaces

More efficient way to bind interface implementations (compared to @Provides).

```kotlin
@Module
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindUserRepository(
        impl: UserRepositoryImpl
    ): UserRepository

    @Binds
    abstract fun bindAuthRepository(
        impl: AuthRepositoryImpl
    ): AuthRepository
}
```

## Scopes

### Predefined Scope: @Singleton

```kotlin
@Singleton
@Component(modules = [AppModule::class])
interface AppComponent {
    // Component implementation
}

@Module
object AppModule {
    @Provides
    @Singleton  // Single instance for app lifetime
    fun provideDatabase(context: Context): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "app-database"
        ).build()
    }
}
```

### Custom Scopes

```kotlin
// Define custom scope
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class ActivityScope

// Use custom scope
@ActivityScope
@Subcomponent(modules = [ActivityModule::class])
interface ActivityComponent {
    fun inject(activity: MainActivity)
}

@Module
object ActivityModule {
    @Provides
    @ActivityScope  // Lives as long as Activity
    fun provideLocationManager(activity: Activity): LocationManager {
        return activity.getSystemService(Context.LOCATION_SERVICE) as LocationManager
    }
}
```

## Subcomponents

Subcomponents inherit and extend parent component's dependency graph.

```kotlin
// Parent component
@Singleton
@Component(modules = [AppModule::class])
interface AppComponent {
    fun activityComponentFactory(): ActivityComponent.Factory
}

// Child subcomponent
@ActivityScope
@Subcomponent(modules = [ActivityModule::class])
interface ActivityComponent {
    fun inject(activity: MainActivity)

    @Subcomponent.Factory
    interface Factory {
        fun create(): ActivityComponent
    }
}

// Usage
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val activityComponent = (application as MyApp)
            .appComponent
            .activityComponentFactory()
            .create()

        activityComponent.inject(this)
    }
}
```

## Qualifiers

Distinguish between multiple instances of the same type.

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
object InterceptorModule {

    @Provides
    @AuthInterceptor
    fun provideAuthInterceptor(tokenManager: TokenManager): Interceptor {
        return AuthInterceptor(tokenManager)
    }

    @Provides
    @LoggingInterceptor
    fun provideLoggingInterceptor(): Interceptor {
        return HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }
    }
}

// Inject qualified dependencies
class ApiClient @Inject constructor(
    @AuthInterceptor private val authInterceptor: Interceptor,
    @LoggingInterceptor private val loggingInterceptor: Interceptor
) {
    // Use interceptors
}
```

## Multibindings

Provide sets or maps of dependencies.

```kotlin
// Set multibinding
@Module
abstract class ViewModelModule {

    @Binds
    @IntoSet
    abstract fun bindUserViewModel(viewModel: UserViewModel): ViewModel

    @Binds
    @IntoSet
    abstract fun bindProfileViewModel(viewModel: ProfileViewModel): ViewModel
}

// Inject the set
class ViewModelFactory @Inject constructor(
    private val viewModels: Set<@JvmSuppressWildcards ViewModel>
) : ViewModelProvider.Factory {
    // Use set of ViewModels
}

// Map multibinding
@Module
abstract class FragmentModule {

    @Binds
    @IntoMap
    @ClassKey(UserFragment::class)
    abstract fun bindUserFragment(fragment: UserFragment): Fragment
}
```

## Use Cases

### When to Use

- Complex dependency graphs with many layers
- Performance-critical applications (no runtime overhead)
- Large codebases requiring type-safety
- Applications needing fine-grained control over scopes
- Multiplatform projects (not Android-specific)
- Teams comfortable with advanced DI concepts

### When to Avoid

- Simple applications with few dependencies
- Rapid prototyping (setup overhead)
- Teams new to dependency injection (use Hilt instead)
- Android-only projects (Hilt is simpler)
- Projects requiring fast onboarding (steep learning curve)

## Trade-offs

**Pros**:
- **Compile-time safety**: Catches errors at compile-time, not runtime
- **Zero runtime overhead**: No reflection, generated code is direct calls
- **Performance**: Fastest DI framework for Android
- **Type-safe**: Full type checking of dependency graphs
- **Multiplatform**: Works for Android, JVM, Kotlin Multiplatform
- **Scalability**: Handles complex dependency graphs efficiently

**Cons**:
- **Steep learning curve**: Many concepts to learn (Components, Modules, Scopes, Subcomponents)
- **Boilerplate**: Requires significant setup code
- **Build time**: Increases build time (annotation processing)
- **Error messages**: Can be cryptic and hard to understand
- **Complexity**: Overengineering for simple projects
- **Android specifics**: Requires custom setup for Android components (Hilt solves this)

## Dagger Vs Hilt Vs Koin

| Feature | Dagger | Hilt | Koin |
|---------|--------|------|------|
| **Type** | Compile-time | Compile-time | Runtime |
| **Android integration** | Manual | Built-in | Good |
| **Learning curve** | Steep | Medium | Easy |
| **Boilerplate** | High | Medium | Low |
| **Performance** | Excellent | Excellent | Good |
| **Error detection** | Compile-time | Compile-time | Runtime |
| **Use case** | Complex JVM apps | Android apps | Simple/medium apps |

## Migration to Hilt

Hilt is built on top of Dagger, making migration straightforward.

```kotlin
// Before (Dagger)
@Singleton
@Component(modules = [AppModule::class])
interface AppComponent {
    fun inject(activity: MainActivity)
}

// After (Hilt)
@HiltAndroidApp
class MyApplication : Application()

@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository
}

// Modules remain mostly the same
@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    @Provides
    @Singleton
    fun provideRepository(): UserRepository {
        return UserRepositoryImpl()
    }
}
```

## Best Practices

### DO:
- Use @Inject constructor whenever possible
- Use @Binds for interface implementations (more efficient than @Provides)
- Keep modules focused (single responsibility)
- Use custom scopes for lifecycle management
- Document complex component hierarchies

### DON'T:
- Mix scoped and unscoped dependencies carelessly
- Create circular dependencies
- Over-scope dependencies (use narrowest scope possible)
- Ignore Dagger error messages (they usually point to real issues)
- Use Dagger for trivial projects (overkill)

## Related Questions

- [[q-dagger-vs-hilt--android--medium]]
- [[q-dagger-components-modules--android--hard]]
- [[q-dependency-injection-benefits--android--medium]]
- [[q-dagger-scopes-subcomponents--android--hard]]

## Related Concepts

- [[c-dependency-injection]] - General DI pattern
- [[c-hilt]] - Android-specific DI built on Dagger
- [[c-architecture-patterns]] - DI often used with MVVM, MVP
- [[c-testing]] - DI improves testability

## References

- [Dagger Official Documentation](https://dagger.dev/)
- [Dagger 2 User's Guide](https://dagger.dev/dev-guide/)
- [Square's Dagger Tutorial](https://github.com/google/dagger)
- [Android Developers: Dagger Basics](https://developer.android.com/training/dependency-injection/dagger-basics)
- [Migration from Dagger to Hilt](https://developer.android.com/training/dependency-injection/hilt-migration)
