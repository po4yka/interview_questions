---
id: 20251012-1227122
title: "Dagger Problems / Проблемы Dagger"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [android/di-hilt, dagger, dependency-injection, di-hilt, platform/android, difficulty/medium]
---
# Какие проблемы есть у Dagger?

**English**: What problems does Dagger have?

## Answer (EN)
Dagger is a powerful dependency injection framework, but it comes with several challenges and limitations that developers face in real-world projects.

### 1. Steep Learning Curve

Dagger has a complex architecture with many concepts to understand:

```kotlin
// Requires understanding of:
// - @Component, @Subcomponent
// - @Module, @Provides, @Binds
// - @Scope, @Singleton, custom scopes
// - @Qualifier, @Named
// - Component dependencies vs Subcomponents
// - Multibindings (@IntoSet, @IntoMap)

@Component(modules = [AppModule::class, NetworkModule::class])
@Singleton
interface AppComponent {
    fun activityComponentFactory(): ActivityComponent.Factory
    fun inject(app: Application)
}

// Just the basics - but there's so much more complexity
```

**Problem**: New developers struggle to understand the framework, leading to:
- Incorrect usage patterns
- Copy-paste programming without understanding
- Difficulty debugging issues

### 2. Long Compilation Times

Dagger generates code at compile time using annotation processing, which significantly increases build times.

```kotlin
// Each module generates code
@Module
class NetworkModule {
    @Provides
    @Singleton
    fun provideRetrofit(): Retrofit { /* ... */ }
}

// Results in generated classes like:
// - DaggerAppComponent
// - AppModule_ProvideRetrofitFactory
// - NetworkModule_ProvideOkHttpFactory
// etc.
```

**Impact:**
- Clean builds take significantly longer
- Incremental builds slower when changing DI-related code
- Larger projects suffer more (1000+ @Provides methods = slow builds)

**Example:** Large project build times:
- Without Dagger: 45 seconds
- With Dagger: 1.5-2 minutes

### 3. Cryptic Error Messages

Compilation errors from Dagger are often difficult to understand:

```kotlin
@Module
class UserModule {
    @Provides
    fun provideUser(repository: UserRepository): User {
        return repository.getUser()
    }
}

// Forgot to provide UserRepository!

// Error message (simplified):
// error: [Dagger/MissingBinding] UserRepository cannot be provided
// without an @Inject constructor or an @Provides-annotated method.
//     public abstract interface AppComponent {
//                              ^
//       A binding with matching key exists in component: AppComponent
//       UserRepository is injected at
//           UserModule.provideUser(repository)
//       User is provided at
//           AppComponent.provideUser()
```

**Problems:**
- Error messages point to component, not the actual problem location
- Circular dependency errors are hard to trace
- Stack traces through generated code are confusing

### 4. Boilerplate Code

Dagger requires significant amounts of boilerplate:

```kotlin
// For every dependency, you need:

// 1. Module
@Module
object DatabaseModule {
    @Provides
    @Singleton
    fun provideDatabase(app: Application): AppDatabase {
        return Room.databaseBuilder(app, AppDatabase::class.java, "db").build()
    }

    @Provides
    fun provideUserDao(db: AppDatabase): UserDao = db.userDao()

    @Provides
    fun provideProductDao(db: AppDatabase): ProductDao = db.productDao()
}

// 2. Component
@Singleton
@Component(modules = [DatabaseModule::class, NetworkModule::class, /* ... */])
interface AppComponent {
    fun inject(activity: MainActivity)
    fun inject(fragment: ProfileFragment)
    // Must declare inject() for every target
}

// 3. Subcomponents for scoped dependencies
@ActivityScope
@Subcomponent(modules = [ActivityModule::class])
interface ActivityComponent {
    @Subcomponent.Factory
    interface Factory {
        fun create(): ActivityComponent
    }

    fun inject(activity: SomeActivity)
}

// 4. Custom scopes
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class ActivityScope

// Multiply this by dozens of modules and components...
```

### 5. Component Graph Complexity

As projects grow, the component graph becomes difficult to manage:

```kotlin
// Complex hierarchy
@Singleton
@Component
interface AppComponent {
    fun activityComponent(): ActivityComponent.Factory
}

@ActivityScope
@Subcomponent
interface ActivityComponent {
    fun fragmentComponent(): FragmentComponent.Factory
}

@FragmentScope
@Subcomponent
interface FragmentComponent {
    fun inject(fragment: MyFragment)
}

// Question: Where should I put this dependency?
// - AppComponent (singleton)?
// - ActivityComponent (activity-scoped)?
// - FragmentComponent (fragment-scoped)?
// Wrong choice = memory leaks or unnecessary reinstantiation
```

### 6. Multibinding Limitations

While powerful, multibinding has limitations:

```kotlin
@Module
interface ViewModelModule {
    @Binds
    @IntoMap
    @ViewModelKey(HomeViewModel::class)
    fun bindHomeViewModel(viewModel: HomeViewModel): ViewModel

    @Binds
    @IntoMap
    @ViewModelKey(ProfileViewModel::class)
    fun bindProfileViewModel(viewModel: ProfileViewModel): ViewModel
}

// Problems:
// - Must declare @IntoMap for each ViewModel manually
// - No automatic discovery
// - Easy to forget to add new ViewModels
```

### 7. Testing Difficulties

Setting up Dagger for tests is complex:

```kotlin
// Production code
@Component(modules = [AppModule::class])
interface AppComponent {
    fun inject(activity: MainActivity)
}

// Test code - requires separate test component
@Component(modules = [TestAppModule::class])
interface TestAppComponent : AppComponent {
    fun inject(test: MainActivityTest)
}

@Module
class TestAppModule {
    @Provides
    fun provideRepository(): Repository {
        return FakeRepository() // Mock implementation
    }
}

class MainActivityTest {
    @Before
    fun setup() {
        val testComponent = DaggerTestAppComponent.create()
        testComponent.inject(this)
        // Complex setup just for testing
    }
}
```

**Alternatives for testing:**
- Manually create dependencies (defeats purpose of DI)
- Use Hilt's testing support (better but still complex)
- Use different DI framework for tests

### 8. Assisted Injection Workarounds

Before Dagger 2.31, injecting runtime parameters was cumbersome:

```kotlin
// Problem: How to inject User with runtime userId?
class UserPresenter(
    private val userId: String, // Runtime parameter
    private val repository: UserRepository // Injected dependency
)

// Old workaround: Factory pattern
interface UserPresenterFactory {
    fun create(userId: String): UserPresenter
}

@Module
interface PresenterModule {
    @Binds
    fun bindFactory(impl: UserPresenterFactoryImpl): UserPresenterFactory
}

// Lots of boilerplate for each assisted dependency
```

**Modern solution:** `@AssistedInject` (Dagger 2.31+)

```kotlin
class UserPresenter @AssistedInject constructor(
    @Assisted private val userId: String,
    private val repository: UserRepository
) {
    @AssistedFactory
    interface Factory {
        fun create(userId: String): UserPresenter
    }
}
```

### 9. Scope Mismatches

Easy to create scope mismatches that lead to runtime errors:

```kotlin
@Singleton
@Component
interface AppComponent {
    fun inject(activity: MainActivity)
}

@Module
class AppModule {
    @Provides
    @ActivityScope // ERROR: ActivityScope in Singleton component!
    fun providePresenter(): Presenter {
        return Presenter()
    }
}

// Compilation error, but not always obvious why
```

### 10. No Automatic Module Inclusion

Unlike Hilt, Dagger requires manual module declaration:

```kotlin
// Dagger - must remember to add every module
@Component(modules = [
    AppModule::class,
    NetworkModule::class,
    DatabaseModule::class,
    RepositoryModule::class,
    // Easy to forget one!
])
interface AppComponent

// Hilt - automatic with @InstallIn
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    // Automatically included
}
```

### Why Hilt Was Created

Google created Hilt to solve many of Dagger's problems:

| Problem | Dagger | Hilt |
|---------|--------|------|
| Learning curve | Steep | Gentler |
| Boilerplate | High | Reduced |
| Component setup | Manual | Automatic |
| Android integration | Manual | Built-in |
| Testing | Complex | Simplified |
| Module organization | Manual | Convention-based |

### Migration Challenges

Moving from manual DI to Dagger is difficult:

```kotlin
// Before Dagger - simple manual DI
class MyApp : Application() {
    val repository by lazy {
        UserRepository(apiService, database)
    }
}

class MainActivity : AppCompatActivity() {
    private val repository = (application as MyApp).repository
}

// After Dagger - requires restructuring entire app
// - Create modules
// - Create components
// - Setup injection points
// - Migrate all manual instantiation
// Major refactoring required!
```

### Summary of Problems

1. **Steep learning curve** - Complex concepts and architecture
2. **Slow compilation** - Code generation increases build times
3. **Cryptic errors** - Difficult to debug compilation failures
4. **Boilerplate code** - Requires many modules, components, scopes
5. **Component complexity** - Hard to maintain large DI graphs
6. **Testing difficulty** - Complex test setup required
7. **No auto-discovery** - Must manually register all dependencies
8. **Scope management** - Easy to create mismatches
9. **Android integration** - Requires manual setup for Activities, Fragments

**Recommendation:** For new Android projects, consider using **Hilt** instead of Dagger directly. Hilt solves most of these problems while building on top of Dagger's proven foundation.

## Ответ (RU)
Dagger имеет ряд проблем: **Крутая кривая обучения** - сложные концепции и архитектура. **Долгая компиляция** - генерация кода увеличивает время сборки. **Загадочные ошибки** - сложно отлаживать ошибки компиляции. **Код-шаблон** - требуется много модулей, компонентов, скоупов. **Сложность компонентов** - трудно поддерживать большие DI-графы. **Сложность тестирования** - требуется сложная настройка тестов. **Нет автообнаружения** - нужно вручную регистрировать зависимости. **Управление скоупами** - легко создать несоответствия. **Интеграция с Android** - требуется ручная настройка для Activity, Fragment.

**Рекомендация:** Для новых Android-проектов лучше использовать **Hilt** вместо Dagger напрямую.

