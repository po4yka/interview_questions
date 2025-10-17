---
id: "20251015082237392"
title: "Dagger Component Dependencies / Зависимости компонентов Dagger"
topic: android
difficulty: hard
status: draft
created: 2025-10-11
tags: - android
  - dependency-injection
  - dagger
  - hilt
  - architecture
  - advanced
related:   - q-dagger-custom-scopes--di--hard
  - q-dagger-multibinding--di--hard
  - q-hilt-entry-points--di--medium
---
# Question (EN)
What's the difference between Component Dependencies and Subcomponents in Dagger? When would you use one over the other? How does Hilt handle this?

## Answer (EN)
### Overview

**Component Dependencies** and **Subcomponents** are two ways to compose Dagger components with different characteristics:

| Aspect | Component Dependencies | Subcomponents |
|--------|----------------------|---------------|
| **Relationship** | Has-a (aggregation) | Is-a (inheritance) |
| **Scope Isolation** | Separate scopes | Share parent scope |
| **Dependency Access** | Only explicit provisions | All parent dependencies |
| **Creation** | Independent | Created by parent |
| **Binding Conflict** | Isolated | Can override parent |
| **Lifecycle** | Independent | Tied to parent |

### Component Dependencies

Component dependencies allow one component to depend on another component:

```kotlin
// Parent component
@Singleton
@Component(modules = [AppModule::class])
interface AppComponent {
    // Must explicitly expose what child components can use
    fun appDatabase(): AppDatabase
    fun apiService(): ApiService
    fun sharedPreferences(): SharedPreferences
}

// Child component that depends on parent
@ActivityScope
@Component(
    dependencies = [AppComponent::class], // Component dependency
    modules = [ActivityModule::class]
)
interface ActivityComponent {
    fun inject(activity: MainActivity)

    // Can use appDatabase(), apiService(), sharedPreferences() from AppComponent
}

// Usage
class MainActivity : AppCompatActivity() {

    @Inject
    lateinit var activityTracker: ActivityTracker

    @Inject
    lateinit var appDatabase: AppDatabase // From AppComponent

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Create activity component with app component as dependency
        val appComponent = (application as MyApplication).appComponent
        DaggerActivityComponent.builder()
            .appComponent(appComponent) // Pass parent component
            .build()
            .inject(this)
    }
}
```

**Key characteristics:**
- Parent must **explicitly expose** dependencies via methods
- Child component **cannot access** unexposed dependencies
- **Separate lifecycles** - parent and child managed independently
- **No scope sharing** - each has its own scope
- **No binding conflicts** - isolated bindings

### Subcomponents

Subcomponents create a hierarchical relationship where the child is part of the parent:

```kotlin
// Parent component
@Singleton
@Component(modules = [AppModule::class])
interface AppComponent {
    // Factory or builder for creating subcomponent
    fun activityComponentFactory(): ActivityComponent.Factory
}

// Child subcomponent
@ActivityScope
@Subcomponent(modules = [ActivityModule::class])
interface ActivityComponent {

    @Subcomponent.Factory
    interface Factory {
        fun create(): ActivityComponent
    }

    fun inject(activity: MainActivity)

    // Can access ALL dependencies from AppComponent
    // No need for explicit exposure
}

// Usage
class MainActivity : AppCompatActivity() {

    @Inject
    lateinit var activityTracker: ActivityTracker

    @Inject
    lateinit var appDatabase: AppDatabase // Automatically available from parent

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Create subcomponent through parent
        val appComponent = (application as MyApplication).appComponent
        appComponent.activityComponentFactory()
            .create()
            .inject(this)
    }
}
```

**Key characteristics:**
- Child can access **all parent dependencies** automatically
- **Shared scope** - child inherits parent's bindings
- **Tied lifecycle** - child created through parent
- **Can override** parent bindings in child scope
- **Tighter coupling** - child depends on parent structure

### Real-World Example: Component Dependencies

```kotlin
// Application level component
@Singleton
@Component(modules = [
    NetworkModule::class,
    DatabaseModule::class,
    AnalyticsModule::class
])
interface AppComponent {
    // Explicitly expose what features can use
    fun apiService(): ApiService
    fun database(): AppDatabase
    fun analytics(): Analytics
    fun imageLoader(): ImageLoader

    // Factory for creating feature components
    interface Factory {
        fun create(@BindsInstance application: Application): AppComponent
    }
}

// Feature component with dependencies
@FeatureScope
@Component(
    dependencies = [AppComponent::class],
    modules = [UserFeatureModule::class]
)
interface UserFeatureComponent {

    fun inject(activity: UserProfileActivity)
    fun inject(fragment: UserDetailsFragment)

    @Component.Factory
    interface Factory {
        fun create(appComponent: AppComponent): UserFeatureComponent
    }
}

@Module
class UserFeatureModule {

    @Provides
    @FeatureScope
    fun provideUserRepository(
        apiService: ApiService, // From AppComponent
        database: AppDatabase // From AppComponent
    ): UserRepository {
        return UserRepository(apiService, database)
    }

    @Provides
    @FeatureScope
    fun provideUserViewModel(
        repository: UserRepository,
        analytics: Analytics // From AppComponent
    ): UserViewModel {
        return UserViewModel(repository, analytics)
    }
}

// Feature-specific scope
@Scope
@Retention(AnnotationRetention.BINARY)
annotation class FeatureScope

// Usage
class UserProfileActivity : AppCompatActivity() {

    private lateinit var userFeatureComponent: UserFeatureComponent

    @Inject
    lateinit var userViewModel: UserViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Get app component
        val appComponent = (application as MyApplication).appComponent

        // Create feature component
        userFeatureComponent = DaggerUserFeatureComponent.factory()
            .create(appComponent)

        // Inject
        userFeatureComponent.inject(this)
    }
}
```

**Benefits of Component Dependencies:**
-  **Modular** - Each feature is independent
-  **Explicit contracts** - Clear what each feature can use
-  **Testable** - Easy to mock AppComponent for testing
-  **Dynamic features** - Can load/unload features
-  **Multi-module** - Different Gradle modules can have different components

### Real-World Example: Subcomponents

```kotlin
// Application component with subcomponents
@Singleton
@Component(modules = [
    AppModule::class,
    SubcomponentsModule::class // Declares subcomponents
])
interface AppComponent {
    fun activityComponentFactory(): ActivityComponent.Factory
    fun serviceComponentFactory(): ServiceComponent.Factory

    @Component.Factory
    interface Factory {
        fun create(@BindsInstance application: Application): AppComponent
    }
}

// Module declaring subcomponents
@Module(subcomponents = [
    ActivityComponent::class,
    ServiceComponent::class
])
object SubcomponentsModule

// Activity subcomponent
@ActivityScope
@Subcomponent(modules = [ActivityModule::class])
interface ActivityComponent {

    @Subcomponent.Factory
    interface Factory {
        fun create(@BindsInstance activity: Activity): ActivityComponent
    }

    fun inject(activity: MainActivity)

    // Can access everything from AppComponent
}

@Module
class ActivityModule {

    @Provides
    @ActivityScope
    fun provideActivityTracker(
        activity: Activity,
        analytics: Analytics // From parent AppComponent
    ): ActivityTracker {
        return ActivityTracker(activity, analytics)
    }

    @Provides
    @ActivityScope
    fun provideNavigationController(
        activity: Activity
    ): NavigationController {
        return NavigationController(activity)
    }
}

// Service subcomponent
@ServiceScope
@Subcomponent(modules = [ServiceModule::class])
interface ServiceComponent {

    @Subcomponent.Factory
    interface Factory {
        fun create(@BindsInstance service: Service): ServiceComponent
    }

    fun inject(service: DataSyncService)
}

@Module
class ServiceModule {

    @Provides
    @ServiceScope
    fun provideSyncManager(
        service: Service,
        apiService: ApiService, // From parent AppComponent
        database: AppDatabase // From parent AppComponent
    ): SyncManager {
        return SyncManager(service, apiService, database)
    }
}

// Custom scopes
@Scope
@Retention(AnnotationRetention.BINARY)
annotation class ActivityScope

@Scope
@Retention(AnnotationRetention.BINARY)
annotation class ServiceScope

// Usage in Activity
class MainActivity : AppCompatActivity() {

    @Inject
    lateinit var activityTracker: ActivityTracker

    @Inject
    lateinit var navigationController: NavigationController

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Create subcomponent through parent
        val appComponent = (application as MyApplication).appComponent
        appComponent.activityComponentFactory()
            .create(this) // Pass activity instance
            .inject(this)
    }
}
```

**Benefits of Subcomponents:**
-  **Automatic dependency access** - No need to expose explicitly
-  **Scope inheritance** - Child can use parent bindings
-  **Simpler setup** - Less boilerplate
-  **Binding override** - Can override parent bindings in child
-  **Hierarchical structure** - Clear parent-child relationship

### Advanced: Mixing Both Approaches

```kotlin
// Core component (used as dependency)
@Singleton
@Component(modules = [CoreModule::class])
interface CoreComponent {
    fun apiService(): ApiService
    fun database(): AppDatabase
}

// App component (depends on core, has subcomponents)
@Singleton
@Component(
    dependencies = [CoreComponent::class], // Component dependency
    modules = [AppModule::class, SubcomponentsModule::class]
)
interface AppComponent {
    fun activityComponentFactory(): ActivityComponent.Factory

    @Component.Factory
    interface Factory {
        fun create(coreComponent: CoreComponent): AppComponent
    }
}

// Activity subcomponent
@ActivityScope
@Subcomponent(modules = [ActivityModule::class])
interface ActivityComponent {

    @Subcomponent.Factory
    interface Factory {
        fun create(): ActivityComponent
    }

    fun inject(activity: MainActivity)

    // Can access:
    // - AppComponent dependencies (subcomponent)
    // - CoreComponent exposed dependencies (through AppComponent)
}
```

### Hilt Approach

**Hilt simplifies this by using a predefined component hierarchy:**

```kotlin
// Hilt uses subcomponents internally
// SingletonComponent (app scope)
//   ↓
// ActivityRetainedComponent (survives config changes)
//   ↓
// ViewModelComponent (ViewModel scope)
//   ↓
// ActivityComponent (Activity scope)
//   ↓
// FragmentComponent (Fragment scope)
//   ↓
// ViewComponent (View scope)

// Everything is automatically handled
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    @Inject
    lateinit var appDatabase: AppDatabase // From SingletonComponent

    @Inject
    lateinit var activityTracker: ActivityTracker // From ActivityComponent

    // No manual component creation!
}

// Modules are installed in specific components
@Module
@InstallIn(SingletonComponent::class) // App-level dependencies
object AppModule {
    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(context, AppDatabase::class.java, "app_db")
            .build()
    }
}

@Module
@InstallIn(ActivityComponent::class) // Activity-level dependencies
object ActivityModule {
    @Provides
    @ActivityScoped
    fun provideActivityTracker(activity: Activity, analytics: Analytics): ActivityTracker {
        return ActivityTracker(activity, analytics)
    }
}
```

**Hilt benefits:**
-  No manual component creation
-  Predefined hierarchy
-  Automatic scoping
-  Standard component lifecycle

**Hilt limitations:**
-  Can't use component dependencies for features
-  Fixed component hierarchy
-  Less flexibility for custom architectures

**When to use plain Dagger instead of Hilt:**
- Need component dependencies for modular features
- Need custom component hierarchy
- Need more control over component lifecycle
- Working with multi-module project with dynamic features

### Production Example: Multi-Module App with Component Dependencies

```kotlin
// :app module - App component
@Singleton
@Component(modules = [AppModule::class])
interface AppComponent {
    // Expose core dependencies
    fun retrofit(): Retrofit
    fun database(): AppDatabase
    fun context(): Context

    @Component.Factory
    interface Factory {
        fun create(@BindsInstance context: Context): AppComponent
    }
}

// :feature:user module - User feature component
@FeatureScope
@Component(
    dependencies = [AppComponent::class],
    modules = [UserFeatureModule::class]
)
interface UserFeatureComponent {
    fun inject(activity: UserActivity)

    @Component.Factory
    interface Factory {
        fun create(appComponent: AppComponent): UserFeatureComponent
    }
}

// Feature entry point
object UserFeature {
    private var component: UserFeatureComponent? = null

    fun init(appComponent: AppComponent) {
        if (component == null) {
            component = DaggerUserFeatureComponent.factory()
                .create(appComponent)
        }
    }

    fun getComponent(): UserFeatureComponent {
        return component ?: throw IllegalStateException("UserFeature not initialized")
    }

    fun destroy() {
        component = null
    }
}

// :feature:shop module - Shop feature component
@FeatureScope
@Component(
    dependencies = [AppComponent::class],
    modules = [ShopFeatureModule::class]
)
interface ShopFeatureComponent {
    fun inject(activity: ShopActivity)

    @Component.Factory
    interface Factory {
        fun create(appComponent: AppComponent): ShopFeatureComponent
    }
}

// Feature entry point
object ShopFeature {
    private var component: ShopFeatureComponent? = null

    fun init(appComponent: AppComponent) {
        if (component == null) {
            component = DaggerShopFeatureComponent.factory()
                .create(appComponent)
        }
    }

    fun getComponent(): ShopFeatureComponent {
        return component ?: throw IllegalStateException("ShopFeature not initialized")
    }

    fun destroy() {
        component = null
    }
}

// In Application
class MyApplication : Application() {

    lateinit var appComponent: AppComponent

    override fun onCreate() {
        super.onCreate()

        appComponent = DaggerAppComponent.factory()
            .create(this)

        // Initialize features
        UserFeature.init(appComponent)
        ShopFeature.init(appComponent)
    }
}

// Usage in feature
class UserActivity : AppCompatActivity() {

    @Inject
    lateinit var userRepository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        UserFeature.getComponent().inject(this)
    }
}
```

### Testing: Component Dependencies vs Subcomponents

```kotlin
// Testing with Component Dependencies - Easy to mock
@Test
fun testUserFeature() {
    // Create fake app component
    val fakeAppComponent = object : AppComponent {
        override fun apiService() = FakeApiService()
        override fun database() = FakeDatabase()
        override fun analytics() = FakeAnalytics()
        override fun imageLoader() = FakeImageLoader()
    }

    // Create feature component with fake dependencies
    val userFeatureComponent = DaggerUserFeatureComponent.factory()
        .create(fakeAppComponent)

    // Test with fake dependencies
    val activity = UserProfileActivity()
    userFeatureComponent.inject(activity)

    // Assertions...
}

// Testing with Subcomponents - Need to mock parent
@Test
fun testActivitySubcomponent() {
    // Need to create entire app component
    val appComponent = DaggerAppComponent.builder()
        .appModule(FakeAppModule())
        .build()

    // Create subcomponent
    val activityComponent = appComponent.activityComponentFactory()
        .create(FakeActivity())

    // Test...
}
```

### Decision Matrix

| Scenario | Use Component Dependencies | Use Subcomponents |
|----------|----------------------------|-------------------|
| **Multi-module project** |  Yes |  No |
| **Dynamic feature modules** |  Yes |  No |
| **Isolated testing** |  Yes |  No |
| **Explicit contracts** |  Yes |  No |
| **Simple hierarchy** |  No |  Yes |
| **Automatic dependency access** |  No |  Yes |
| **Scope inheritance** |  No |  Yes |
| **Override parent bindings** |  No |  Yes |
| **Standard Android lifecycle** |  Use Hilt |  Use Hilt |

### Best Practices

1. **Use Hilt for Standard Android Apps**
   ```kotlin
   //  GOOD - Use Hilt for most apps
   @HiltAndroidApp
   class MyApplication : Application()

   @AndroidEntryPoint
   class MainActivity : AppCompatActivity()

   //  AVOID - Manual Dagger unless you have specific needs
   ```

2. **Use Component Dependencies for Multi-Module**
   ```kotlin
   //  GOOD - Feature modules with component dependencies
   // :app
   interface AppComponent {
       fun apiService(): ApiService
   }

   // :feature:user
   @Component(dependencies = [AppComponent::class])
   interface UserFeatureComponent

   // :feature:shop
   @Component(dependencies = [AppComponent::class])
   interface ShopFeatureComponent
   ```

3. **Use Subcomponents for Hierarchical Scopes**
   ```kotlin
   //  GOOD - Natural parent-child relationship
   @Component
   interface AppComponent {
       fun activityComponentFactory(): ActivityComponent.Factory
   }

   @Subcomponent
   interface ActivityComponent {
       fun fragmentComponentFactory(): FragmentComponent.Factory
   }

   @Subcomponent
   interface FragmentComponent
   ```

4. **Minimize Exposed Dependencies**
   ```kotlin
   //  GOOD - Only expose what's needed
   interface AppComponent {
       fun apiService(): ApiService
       fun database(): AppDatabase
   }

   //  BAD - Exposing everything
   interface AppComponent {
       fun apiService(): ApiService
       fun database(): AppDatabase
       fun retrofit(): Retrofit
       fun okHttpClient(): OkHttpClient
       fun gson(): Gson
       // ... 20 more
   }
   ```

5. **Document Component Relationships**
   ```kotlin
   /**
    * AppComponent - Application-level dependencies
    * Lifecycle: Application.onCreate() to app destroyed
    * Exposes: ApiService, AppDatabase, Analytics
    * Used by: All feature components
    */
   @Singleton
   @Component(modules = [AppModule::class])
   interface AppComponent
   ```

### Common Pitfalls

1. **Forgetting to Expose Dependencies**
   ```kotlin
   //  BAD - apiService not exposed
   @Component
   interface AppComponent {
       fun database(): AppDatabase
       // Missing: fun apiService(): ApiService
   }

   @Component(dependencies = [AppComponent::class])
   interface FeatureComponent
   // Can't use apiService! Compilation error

   //  GOOD - Expose what's needed
   @Component
   interface AppComponent {
       fun database(): AppDatabase
       fun apiService(): ApiService
   }
   ```

2. **Scope Conflicts**
   ```kotlin
   //  BAD - Scope mismatch
   @Singleton
   @Component
   interface AppComponent {
       fun database(): AppDatabase
   }

   @Singleton // BAD - Same scope as parent!
   @Component(dependencies = [AppComponent::class])
   interface FeatureComponent

   //  GOOD - Different scope
   @FeatureScope
   @Component(dependencies = [AppComponent::class])
   interface FeatureComponent
   ```

3. **Memory Leaks with Subcomponents**
   ```kotlin
   //  BAD - Holding reference to subcomponent
   class MainActivity : AppCompatActivity() {
       companion object {
           var activityComponent: ActivityComponent? = null // Memory leak!
       }
   }

   //  GOOD - Don't hold references
   class MainActivity : AppCompatActivity() {
       override fun onCreate(savedInstanceState: Bundle?) {
           super.onCreate(savedInstanceState)
           val component = appComponent.activityComponentFactory().create()
           component.inject(this)
           // Component can be garbage collected
       }
   }
   ```

### Summary

**Component Dependencies vs Subcomponents:**

**Component Dependencies:**
-  Use for: Multi-module projects, dynamic features, isolated testing
-  Characteristics: Explicit contracts, separate lifecycles, modular
-  More boilerplate: Must expose dependencies explicitly

**Subcomponents:**
-  Use for: Hierarchical scopes, simple projects, scope inheritance
-  Characteristics: Automatic access, tighter coupling, less boilerplate
-  Less modular: Child depends on parent structure

**Hilt:**
-  Use for: Standard Android apps, predefined hierarchy
-  Benefits: No manual component management, standard lifecycle
-  Limitations: Fixed hierarchy, no component dependencies

**Decision guide:**
1. Standard Android app → Use Hilt
2. Multi-module with features → Component Dependencies
3. Simple hierarchical scopes → Subcomponents
4. Need flexibility → Plain Dagger with either approach

---

# Вопрос (RU)
В чём разница между Component Dependencies и Subcomponents в Dagger? Когда использовать одно вместо другого? Как Hilt с этим работает?

## Ответ (RU)
### Обзор

**Component Dependencies** и **Subcomponents** — два способа композиции Dagger-компонентов с разными характеристиками:

| Аспект | Component Dependencies | Subcomponents |
|--------|------------------------|---------------|
| **Отношение** | Has-a (агрегация) | Is-a (наследование) |
| **Изоляция Scope** | Отдельные scopes | Разделяют parent scope |
| **Доступ к зависимостям** | Только явно предоставленные | Все parent зависимости |
| **Создание** | Независимое | Создаётся parent'ом |
| **Конфликты Binding** | Изолированные | Может переопределять parent |
| **Жизненный цикл** | Независимый | Привязан к parent |

### Component Dependencies (Зависимости компонентов)

Component dependencies позволяют одному компоненту зависеть от другого:

```kotlin
// Родительский компонент
@Singleton
@Component(modules = [AppModule::class])
interface AppComponent {
    // Должен явно предоставлять то, что может использовать дочерний компонент
    fun appDatabase(): AppDatabase
    fun apiService(): ApiService
    fun sharedPreferences(): SharedPreferences
}

// Дочерний компонент с зависимостью от родителя
@ActivityScope
@Component(
    dependencies = [AppComponent::class], // Зависимость компонента
    modules = [ActivityModule::class]
)
interface ActivityComponent {
    fun inject(activity: MainActivity)

    // Может использовать appDatabase(), apiService(), sharedPreferences() из AppComponent
}

// Использование
class MainActivity : AppCompatActivity() {
    @Inject lateinit var activityTracker: ActivityTracker
    @Inject lateinit var appDatabase: AppDatabase // Из AppComponent

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val appComponent = (application as MyApplication).appComponent
        DaggerActivityComponent.builder()
            .appComponent(appComponent) // Передаем родительский компонент
            .build()
            .inject(this)
    }
}
```

**Ключевые характеристики:**
- Родитель должен **явно предоставлять** зависимости через методы
- Дочерний компонент **не может получить доступ** к непредоставленным зависимостям
- **Отдельные жизненные циклы** - родитель и дочерний управляются независимо
- **Нет общих scope** - каждый имеет свой scope
- **Нет конфликтов binding** - изолированные bindings

### Subcomponents (Подкомпоненты)

Subcomponents создают иерархическую связь, где дочерний является частью родителя:

```kotlin
// Родительский компонент
@Singleton
@Component(modules = [AppModule::class])
interface AppComponent {
    // Factory или builder для создания subcomponent
    fun activityComponentFactory(): ActivityComponent.Factory
}

// Дочерний subcomponent
@ActivityScope
@Subcomponent(modules = [ActivityModule::class])
interface ActivityComponent {

    @Subcomponent.Factory
    interface Factory {
        fun create(): ActivityComponent
    }

    fun inject(activity: MainActivity)

    // Может получить доступ ко ВСЕМ зависимостям из AppComponent
    // Не нужно явное предоставление
}

// Использование
class MainActivity : AppCompatActivity() {
    @Inject lateinit var activityTracker: ActivityTracker
    @Inject lateinit var appDatabase: AppDatabase // Автоматически доступен из parent

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val appComponent = (application as MyApplication).appComponent
        appComponent.activityComponentFactory()
            .create()
            .inject(this)
    }
}
```

**Ключевые характеристики:**
- Дочерний может получить доступ ко **всем зависимостям parent** автоматически
- **Общий scope** - дочерний наследует bindings родителя
- **Связанный жизненный цикл** - дочерний создается через parent
- **Может переопределять** родительские bindings в дочернем scope
- **Более тесная связь** - дочерний зависит от структуры parent

### Реальный пример: Component Dependencies

```kotlin
// Application level компонент
@Singleton
@Component(modules = [
    NetworkModule::class,
    DatabaseModule::class,
    AnalyticsModule::class
])
interface AppComponent {
    // Явно предоставляем что может использовать фича
    fun apiService(): ApiService
    fun database(): AppDatabase
    fun analytics(): Analytics
    fun imageLoader(): ImageLoader

    @Component.Factory
    interface Factory {
        fun create(@BindsInstance application: Application): AppComponent
    }
}

// Feature компонент с зависимостями
@FeatureScope
@Component(
    dependencies = [AppComponent::class],
    modules = [UserFeatureModule::class]
)
interface UserFeatureComponent {
    fun inject(activity: UserProfileActivity)
    fun inject(fragment: UserDetailsFragment)

    @Component.Factory
    interface Factory {
        fun create(appComponent: AppComponent): UserFeatureComponent
    }
}

@Module
class UserFeatureModule {
    @Provides
    @FeatureScope
    fun provideUserRepository(
        apiService: ApiService, // Из AppComponent
        database: AppDatabase // Из AppComponent
    ): UserRepository {
        return UserRepository(apiService, database)
    }

    @Provides
    @FeatureScope
    fun provideUserViewModel(
        repository: UserRepository,
        analytics: Analytics // Из AppComponent
    ): UserViewModel {
        return UserViewModel(repository, analytics)
    }
}

// Использование
class UserProfileActivity : AppCompatActivity() {
    private lateinit var userFeatureComponent: UserFeatureComponent
    @Inject lateinit var userViewModel: UserViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val appComponent = (application as MyApplication).appComponent
        userFeatureComponent = DaggerUserFeatureComponent.factory()
            .create(appComponent)
        userFeatureComponent.inject(this)
    }
}
```

**Преимущества Component Dependencies:**
-  **Модульность** - Каждая фича независима
-  **Явные контракты** - Понятно что каждая фича может использовать
-  **Тестируемость** - Легко замокировать AppComponent для тестирования
-  **Dynamic features** - Можно загружать/выгружать фичи
-  **Multi-module** - Разные Gradle модули могут иметь разные компоненты

### Реальный пример: Subcomponents

```kotlin
// Application компонент с subcomponents
@Singleton
@Component(modules = [
    AppModule::class,
    SubcomponentsModule::class // Объявляет subcomponents
])
interface AppComponent {
    fun activityComponentFactory(): ActivityComponent.Factory
    fun serviceComponentFactory(): ServiceComponent.Factory

    @Component.Factory
    interface Factory {
        fun create(@BindsInstance application: Application): AppComponent
    }
}

// Модуль объявляющий subcomponents
@Module(subcomponents = [
    ActivityComponent::class,
    ServiceComponent::class
])
object SubcomponentsModule

// Activity subcomponent
@ActivityScope
@Subcomponent(modules = [ActivityModule::class])
interface ActivityComponent {

    @Subcomponent.Factory
    interface Factory {
        fun create(@BindsInstance activity: Activity): ActivityComponent
    }

    fun inject(activity: MainActivity)

    // Может получить доступ ко всему из AppComponent
}

@Module
class ActivityModule {
    @Provides
    @ActivityScope
    fun provideActivityTracker(
        activity: Activity,
        analytics: Analytics // Из parent AppComponent
    ): ActivityTracker {
        return ActivityTracker(activity, analytics)
    }

    @Provides
    @ActivityScope
    fun provideNavigationController(
        activity: Activity
    ): NavigationController {
        return NavigationController(activity)
    }
}
```

**Преимущества Subcomponents:**
-  **Автоматический доступ к зависимостям** - Не нужно предоставлять явно
-  **Наследование scope** - Дочерний может использовать родительские bindings
-  **Упрощенная настройка** - Меньше boilerplate
-  **Переопределение binding** - Может переопределять родительские bindings
-  **Иерархическая структура** - Четкая связь parent-child

### Продвинутый подход: Смешивание обоих методов

```kotlin
// Core компонент (используется как зависимость)
@Singleton
@Component(modules = [CoreModule::class])
interface CoreComponent {
    fun apiService(): ApiService
    fun database(): AppDatabase
}

// App компонент (зависит от core, имеет subcomponents)
@Singleton
@Component(
    dependencies = [CoreComponent::class], // Component dependency
    modules = [AppModule::class, SubcomponentsModule::class]
)
interface AppComponent {
    fun activityComponentFactory(): ActivityComponent.Factory

    @Component.Factory
    interface Factory {
        fun create(coreComponent: CoreComponent): AppComponent
    }
}

// Activity subcomponent
@ActivityScope
@Subcomponent(modules = [ActivityModule::class])
interface ActivityComponent {

    @Subcomponent.Factory
    interface Factory {
        fun create(): ActivityComponent
    }

    fun inject(activity: MainActivity)

    // Может получить доступ к:
    // - AppComponent зависимостям (subcomponent)
    // - CoreComponent предоставленным зависимостям (через AppComponent)
}
```

### Подход Hilt

**Hilt упрощает это используя предопределенную иерархию компонентов:**

```kotlin
// Hilt использует subcomponents внутренне
// SingletonComponent (app scope)
//   ↓
// ActivityRetainedComponent (переживает изменения конфигурации)
//   ↓
// ViewModelComponent (ViewModel scope)
//   ↓
// ActivityComponent (Activity scope)
//   ↓
// FragmentComponent (Fragment scope)
//   ↓
// ViewComponent (View scope)

// Всё обрабатывается автоматически
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    @Inject
    lateinit var appDatabase: AppDatabase // Из SingletonComponent

    @Inject
    lateinit var activityTracker: ActivityTracker // Из ActivityComponent

    // Не нужно ручное создание компонентов!
}

// Модули устанавливаются в определенные компоненты
@Module
@InstallIn(SingletonComponent::class) // Зависимости уровня приложения
object AppModule {
    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(context, AppDatabase::class.java, "app_db")
            .build()
    }
}

@Module
@InstallIn(ActivityComponent::class) // Зависимости уровня Activity
object ActivityModule {
    @Provides
    @ActivityScoped
    fun provideActivityTracker(activity: Activity, analytics: Analytics): ActivityTracker {
        return ActivityTracker(activity, analytics)
    }
}
```

**Преимущества Hilt:**
-  Нет ручного создания компонентов
-  Предопределенная иерархия
-  Автоматический scoping
-  Стандартный жизненный цикл компонентов

**Ограничения Hilt:**
-  Нельзя использовать component dependencies для фич
-  Фиксированная иерархия компонентов
-  Меньше гибкости для кастомной архитектуры

**Когда использовать plain Dagger вместо Hilt:**
- Нужны component dependencies для модульных фич
- Нужна кастомная иерархия компонентов
- Нужен больший контроль над жизненным циклом компонентов
- Работа с multi-module проектом с dynamic features

### Продакшн пример: Мульти-модульное приложение с Component Dependencies

```kotlin
// :app модуль - App компонент
@Singleton
@Component(modules = [AppModule::class])
interface AppComponent {
    // Предоставляем основные зависимости
    fun retrofit(): Retrofit
    fun database(): AppDatabase
    fun context(): Context

    @Component.Factory
    interface Factory {
        fun create(@BindsInstance context: Context): AppComponent
    }
}

// :feature:user модуль - User feature компонент
@FeatureScope
@Component(
    dependencies = [AppComponent::class],
    modules = [UserFeatureModule::class]
)
interface UserFeatureComponent {
    fun inject(activity: UserActivity)

    @Component.Factory
    interface Factory {
        fun create(appComponent: AppComponent): UserFeatureComponent
    }
}

// Точка входа фичи
object UserFeature {
    private var component: UserFeatureComponent? = null

    fun init(appComponent: AppComponent) {
        if (component == null) {
            component = DaggerUserFeatureComponent.factory()
                .create(appComponent)
        }
    }

    fun getComponent(): UserFeatureComponent {
        return component ?: throw IllegalStateException("UserFeature not initialized")
    }

    fun destroy() {
        component = null
    }
}

// :feature:shop модуль - Shop feature компонент
@FeatureScope
@Component(
    dependencies = [AppComponent::class],
    modules = [ShopFeatureModule::class]
)
interface ShopFeatureComponent {
    fun inject(activity: ShopActivity)

    @Component.Factory
    interface Factory {
        fun create(appComponent: AppComponent): ShopFeatureComponent
    }
}

// Точка входа фичи
object ShopFeature {
    private var component: ShopFeatureComponent? = null

    fun init(appComponent: AppComponent) {
        if (component == null) {
            component = DaggerShopFeatureComponent.factory()
                .create(appComponent)
        }
    }

    fun getComponent(): ShopFeatureComponent {
        return component ?: throw IllegalStateException("ShopFeature not initialized")
    }

    fun destroy() {
        component = null
    }
}

// В Application
class MyApplication : Application() {

    lateinit var appComponent: AppComponent

    override fun onCreate() {
        super.onCreate()

        appComponent = DaggerAppComponent.factory()
            .create(this)

        // Инициализируем фичи
        UserFeature.init(appComponent)
        ShopFeature.init(appComponent)
    }
}

// Использование в фиче
class UserActivity : AppCompatActivity() {

    @Inject
    lateinit var userRepository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        UserFeature.getComponent().inject(this)
    }
}
```

### Тестирование: Component Dependencies vs Subcomponents

```kotlin
// Тестирование с Component Dependencies - легко мокировать
@Test
fun testUserFeature() {
    // Создаем фейковый app компонент
    val fakeAppComponent = object : AppComponent {
        override fun apiService() = FakeApiService()
        override fun database() = FakeDatabase()
        override fun analytics() = FakeAnalytics()
        override fun imageLoader() = FakeImageLoader()
    }

    // Создаем feature компонент с фейковыми зависимостями
    val userFeatureComponent = DaggerUserFeatureComponent.factory()
        .create(fakeAppComponent)

    // Тестирование с фейковыми зависимостями
    val activity = UserProfileActivity()
    userFeatureComponent.inject(activity)

    // Проверки...
}

// Тестирование с Subcomponents - нужно мокировать parent
@Test
fun testActivitySubcomponent() {
    // Нужно создать весь app компонент
    val appComponent = DaggerAppComponent.builder()
        .appModule(FakeAppModule())
        .build()

    // Создать subcomponent
    val activityComponent = appComponent.activityComponentFactory()
        .create(FakeActivity())

    // Тестирование...
}
```

### Матрица решений

| Сценарий | Использовать Component Dependencies | Использовать Subcomponents |
|----------|----------------------------|-------------------|
| **Multi-module проект** |  Да |  Нет |
| **Dynamic feature модули** |  Да |  Нет |
| **Изолированное тестирование** |  Да |  Нет |
| **Явные контракты** |  Да |  Нет |
| **Простая иерархия** |  Нет |  Да |
| **Автоматический доступ к зависимостям** |  Нет |  Да |
| **Наследование scope** |  Нет |  Да |
| **Переопределение parent bindings** |  Нет |  Да |
| **Стандартный Android жизненный цикл** |  Используйте Hilt |  Используйте Hilt |

### Лучшие практики

1. **Используйте Hilt для стандартных Android приложений**
   ```kotlin
   //  ХОРОШО - Используйте Hilt для большинства приложений
   @HiltAndroidApp
   class MyApplication : Application()

   @AndroidEntryPoint
   class MainActivity : AppCompatActivity()

   //  ИЗБЕГАЙТЕ - Ручной Dagger если нет специфических нужд
   ```

2. **Используйте Component Dependencies для Multi-Module**
   ```kotlin
   //  ХОРОШО - Feature модули с component dependencies
   // :app
   interface AppComponent {
       fun apiService(): ApiService
   }

   // :feature:user
   @Component(dependencies = [AppComponent::class])
   interface UserFeatureComponent

   // :feature:shop
   @Component(dependencies = [AppComponent::class])
   interface ShopFeatureComponent
   ```

3. **Используйте Subcomponents для иерархических Scopes**
   ```kotlin
   //  ХОРОШО - Естественная связь parent-child
   @Component
   interface AppComponent {
       fun activityComponentFactory(): ActivityComponent.Factory
   }

   @Subcomponent
   interface ActivityComponent {
       fun fragmentComponentFactory(): FragmentComponent.Factory
   }

   @Subcomponent
   interface FragmentComponent
   ```

4. **Минимизируйте предоставленные зависимости**
   ```kotlin
   //  ХОРОШО - Предоставляйте только необходимое
   interface AppComponent {
       fun apiService(): ApiService
       fun database(): AppDatabase
   }

   //  ПЛОХО - Предоставление всего
   interface AppComponent {
       fun apiService(): ApiService
       fun database(): AppDatabase
       fun retrofit(): Retrofit
       fun okHttpClient(): OkHttpClient
       // ... еще 20
   }
   ```

5. **Документируйте отношения компонентов**
   ```kotlin
   /**
    * AppComponent - Зависимости уровня приложения
    * Жизненный цикл: Application.onCreate() до уничтожения приложения
    * Предоставляет: ApiService, AppDatabase, Analytics
    * Используется: Всеми feature компонентами
    */
   @Singleton
   @Component(modules = [AppModule::class])
   interface AppComponent
   ```

### Распространенные ошибки

1. **Забывание предоставлять зависимости**
   ```kotlin
   //  ПЛОХО - apiService не предоставлен
   @Component
   interface AppComponent {
       fun database(): AppDatabase
       // Отсутствует: fun apiService(): ApiService
   }

   @Component(dependencies = [AppComponent::class])
   interface FeatureComponent
   // Нельзя использовать apiService! Ошибка компиляции

   //  ХОРОШО - Предоставить что нужно
   @Component
   interface AppComponent {
       fun database(): AppDatabase
       fun apiService(): ApiService
   }
   ```

2. **Конфликты Scope**
   ```kotlin
   //  ПЛОХО - Несоответствие scope
   @Singleton
   @Component
   interface AppComponent {
       fun database(): AppDatabase
   }

   @Singleton // ПЛОХО - Такой же scope как у parent!
   @Component(dependencies = [AppComponent::class])
   interface FeatureComponent

   //  ХОРОШО - Другой scope
   @FeatureScope
   @Component(dependencies = [AppComponent::class])
   interface FeatureComponent
   ```

3. **Утечки памяти с Subcomponents**
   ```kotlin
   //  ПЛОХО - Держим ссылку на subcomponent
   class MainActivity : AppCompatActivity() {
       companion object {
           var activityComponent: ActivityComponent? = null // Утечка памяти!
       }
   }

   //  ХОРОШО - Не держать ссылки
   class MainActivity : AppCompatActivity() {
       override fun onCreate(savedInstanceState: Bundle?) {
           super.onCreate(savedInstanceState)
           val component = appComponent.activityComponentFactory().create()
           component.inject(this)
           // Компонент может быть собран сборщиком мусора
       }
   }
   ```

### Резюме

**Component Dependencies vs Subcomponents:**

**Component Dependencies:**
-  Используйте для: Мульти-модульных проектов, dynamic features, изолированного тестирования
-  Характеристики: Явные контракты, отдельные жизненные циклы, модульность
-  Больше boilerplate: Нужно явно предоставлять зависимости

**Subcomponents:**
-  Используйте для: Иерархических scopes, простых проектов, наследования scope
-  Характеристики: Автоматический доступ, более тесная связь, меньше boilerplate
-  Менее модульно: Child зависит от структуры parent

**Hilt:**
-  Используйте для: Стандартных Android-приложений, предопределённой иерархии
-  Преимущества: Нет ручного управления компонентами, стандартный жизненный цикл
-  Ограничения: Фиксированная иерархия, нет component dependencies

**Руководство по выбору:**
1. Стандартное Android-приложение → Используйте Hilt
2. Мульти-модуль с features → Component Dependencies
3. Простые иерархические scopes → Subcomponents
4. Нужна гибкость → Plain Dagger с любым подходом
