---
topic: android
tags:
  - android
  - android/dependency-injection
  - dagger
  - dependency-injection
  - hilt
  - lifecycle
  - scope
difficulty: medium
status: draft
date_created: 2025-10-13
date_updated: 2025-10-13
moc: moc-android
related_questions: []
---

# Что такое scope в Dagger и как они работают?

**English**: What is scope in Dagger and how do they work?

## Answer (EN)
**Scopes** in Dagger control the **lifetime** of dependencies. They ensure objects are reused within a specific lifecycle, preventing unnecessary object creation.

**Key concepts:**
- Use `@Scope` annotations (@Singleton, @ActivityScope, etc.)
- Bind scopes to Dagger components
- Objects live as long as their component lives
- Prevents memory leaks and improves performance

---

## What is Scope?

A **scope** defines how long a dependency instance should live:

```kotlin
// Without scope: NEW instance every time
class UserRepository @Inject constructor(
    private val api: ApiService
)

// With scope: SAME instance within scope
@Singleton
class UserRepository @Inject constructor(
    private val api: ApiService
)
```

---

## Built-in Scopes

### @Singleton

Lives for the entire application lifecycle:

```kotlin
@Singleton
@Component(modules = [AppModule::class])
interface AppComponent {
    fun inject(app: MyApplication)
}

@Module
class AppModule {
    @Provides
    @Singleton
    fun provideDatabase(context: Context): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "app_database"
        ).build()
    }
}
```

---

## Custom Scopes

### @ActivityScope

Lives for Activity lifecycle:

```kotlin
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class ActivityScope

@ActivityScope
@Subcomponent
interface ActivityComponent {
    fun inject(activity: MainActivity)
}

@ActivityScope
class ActivityPresenter @Inject constructor(
    private val repository: UserRepository
) {
    // Same instance within Activity
}
```

### @FragmentScope

Lives for Fragment lifecycle:

```kotlin
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class FragmentScope

@FragmentScope
@Subcomponent
interface FragmentComponent {
    fun inject(fragment: UserFragment)
}
```

---

## How Scopes Work

### Component Hierarchy

```

   AppComponent      @Singleton
  (Application)     

            depends on
           ↓

 ActivityComponent   @ActivityScope
   (Activity)       

            depends on
           ↓

 FragmentComponent   @FragmentScope
   (Fragment)       

```

**Rules:**
- Parent component can provide dependencies to child
- Child component CANNOT have wider scope than parent
- One scope per component

---

## Complete Example

### 1. Define Custom Scopes

```kotlin
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class ActivityScope

@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class FragmentScope
```

### 2. Create Components

```kotlin
// Application level
@Singleton
@Component(modules = [AppModule::class])
interface AppComponent {
    fun activityComponent(): ActivityComponent.Factory
}

// Activity level
@ActivityScope
@Subcomponent(modules = [ActivityModule::class])
interface ActivityComponent {
    fun inject(activity: MainActivity)
    fun fragmentComponent(): FragmentComponent.Factory

    @Subcomponent.Factory
    interface Factory {
        fun create(): ActivityComponent
    }
}

// Fragment level
@FragmentScope
@Subcomponent
interface FragmentComponent {
    fun inject(fragment: UserFragment)

    @Subcomponent.Factory
    interface Factory {
        fun create(): FragmentComponent
    }
}
```

### 3. Scoped Dependencies

```kotlin
// Singleton: Lives for entire app
@Singleton
class UserRepository @Inject constructor(
    private val api: ApiService,
    private val database: AppDatabase
)

// Activity scope: Lives for Activity
@ActivityScope
class ActivityPresenter @Inject constructor(
    private val repository: UserRepository
) {
    fun loadUser(userId: String) { /* ... */ }
}

// Fragment scope: Lives for Fragment
@FragmentScope
class FragmentViewModel @Inject constructor(
    private val presenter: ActivityPresenter
) {
    fun displayUser() { /* ... */ }
}
```

### 4. Usage

```kotlin
class MyApplication : Application() {
    lateinit var appComponent: AppComponent

    override fun onCreate() {
        super.onCreate()
        appComponent = DaggerAppComponent.create()
    }
}

class MainActivity : AppCompatActivity() {
    @Inject lateinit var presenter: ActivityPresenter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val activityComponent = (application as MyApplication)
            .appComponent
            .activityComponent()
            .create()

        activityComponent.inject(this)

        presenter.loadUser("123") // Same instance within Activity
    }
}
```

---

## Hilt Scopes

Hilt provides predefined components and scopes:

| Component | Scope | Lifetime |
|-----------|-------|----------|
| SingletonComponent | @Singleton | Application |
| ActivityRetainedComponent | @ActivityRetainedScoped | ViewModel |
| ActivityComponent | @ActivityScoped | Activity |
| FragmentComponent | @FragmentScoped | Fragment |
| ViewComponent | @ViewScoped | View |
| ViewWithFragmentComponent | @ViewScoped | View (in Fragment) |
| ServiceComponent | @ServiceScoped | Service |

### Hilt Example

```kotlin
@HiltAndroidApp
class MyApplication : Application()

@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var presenter: ActivityPresenter
}

@ActivityScoped
class ActivityPresenter @Inject constructor(
    private val repository: UserRepository
) {
    // Same instance within Activity
}

@Singleton
class UserRepository @Inject constructor(
    private val api: ApiService
) {
    // Same instance for entire app
}
```

---

## Best Practices

### 1. Use Appropriate Scope

```kotlin
// GOOD: Singleton for app-wide resources
@Singleton
class AppDatabase

// GOOD: ActivityScoped for UI-related logic
@ActivityScoped
class Presenter

// BAD: Singleton for Activity-specific data
@Singleton
class ActivityViewModel // Memory leak!
```

### 2. Avoid Memory Leaks

```kotlin
// BAD: Activity in Singleton scope
@Singleton
class BadRepository @Inject constructor(
    private val activity: Activity // Leaks Activity!
)

// GOOD: Use Application Context
@Singleton
class GoodRepository @Inject constructor(
    @ApplicationContext private val context: Context
)
```

### 3. Match Scope to Lifecycle

```kotlin
//  GOOD
@ActivityScoped
class ActivityPresenter // Lives with Activity

@FragmentScoped
class FragmentViewModel // Lives with Fragment

@Singleton
class ApiClient // Lives for entire app
```

---

## Summary

**What is scope:**
- Controls lifetime of dependencies
- Prevents unnecessary object creation
- Tied to component lifecycle

**How it works:**
1. Annotate class with `@Scope` (e.g., `@Singleton`, `@ActivityScoped`)
2. Bind to component with matching scope
3. Dagger reuses instance within that scope

**Key rules:**
- One scope per component
- Child scope narrower than parent
- Match scope to lifecycle
- Don't leak long-lived references

**Common scopes:**
- `@Singleton` - Application lifetime
- `@ActivityScoped` - Activity lifetime
- `@FragmentScoped` - Fragment lifetime
- `@ViewScoped` - View lifetime

---

## Ответ (RU)
**Scope** в Dagger управляет **временем жизни** зависимостей. Они обеспечивают переиспользование объектов в рамках определенного жизненного цикла.

**Основные концепции:**
- Используйте аннотации `@Scope` (@Singleton, @ActivityScope и т.д.)
- Привязывайте scope к компонентам Dagger
- Объекты живут столько, сколько живет их компонент
- Предотвращает утечки памяти и улучшает производительность

**Пример:**

```kotlin
// Singleton: на весь жизненный цикл приложения
@Singleton
class UserRepository @Inject constructor(
    private val api: ApiService
)

// ActivityScope: на жизненный цикл Activity
@ActivityScope
class Presenter @Inject constructor(
    private val repository: UserRepository
)
```

**Правила:**
- Один scope на компонент
- Дочерний scope уже родительского
- Соответствие scope жизненному циклу
- Не утекайте долгоживущие ссылки

