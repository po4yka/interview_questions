---
id: 20251012-1227117
title: "Dagger Field Injection / Инъекция полей Dagger"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-test-coverage-quality-metrics--testing--medium, q-transaction-too-large-exception--android--medium, q-dark-theme-android--android--medium]
created: 2025-10-15
tags: [android/di-hilt, dagger, dependency-injection, di-hilt, platform/android, difficulty/medium]
---
# Какие особенности инжекта в поле при помощи Dagger?

**English**: What are the features of field injection using Dagger?

## Answer (EN)
Field injection in Dagger allows automatic dependency injection into class fields using the `@Inject` annotation. This approach has specific characteristics, advantages, and limitations compared to constructor and method injection.

### Field Injection Basics

```kotlin
class MainActivity : AppCompatActivity() {

    @Inject
    lateinit var repository: UserRepository

    @Inject
    lateinit var analytics: Analytics

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Must call inject before using dependencies
        (application as MyApp).appComponent.inject(this)

        // Now safe to use injected fields
        val user = repository.getUser()
        analytics.logEvent("screen_viewed")
    }
}
```

### Key Features

#### 1. Requires Manual Injection Call

Unlike constructor injection, field injection requires explicitly calling an inject method.

```kotlin
// Component definition
@Component(modules = [AppModule::class])
interface AppComponent {
    // Must declare inject method for each class
    fun inject(activity: MainActivity)
    fun inject(fragment: UserFragment)
}

// Usage in Activity
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    (application as MyApp).appComponent.inject(this)
    // Fields are now injected
}
```

#### 2. Cannot Be Final/Val

Field injection only works with mutable fields (`var`, not `val`).

```kotlin
class MyActivity : AppCompatActivity() {

    @Inject
    lateinit var repository: UserRepository  // Works with lateinit var

    @Inject
    val analytics: Analytics? = null  // Won't work with val
}
```

#### 3. Requires lateinit or Nullable

```kotlin
// GOOD: Using lateinit
@Inject
lateinit var repository: UserRepository

// ACCEPTABLE: Nullable field
@Inject
var analytics: Analytics? = null

// BAD: Non-null without lateinit
@Inject
var database: AppDatabase  // Compile error
```

#### 4. Limited to Non-Private Fields

Dagger cannot inject private fields.

```kotlin
class MyClass {
    @Inject
    lateinit var publicRepo: Repository  // Works

    @Inject
    internal lateinit var internalRepo: Repository  // Works

    @Inject
    private lateinit var privateRepo: Repository  // Won't work
}
```

#### 5. Android Components Compatibility

Field injection is the **only option** for Android framework classes where you don't control the constructor.

```kotlin
// Activity - no control over constructor
class MainActivity : AppCompatActivity() {
    @Inject lateinit var viewModel: UserViewModel  // Field injection required
}

// Fragment - no control over constructor
class UserFragment : Fragment() {
    @Inject lateinit var adapter: UserAdapter  // Field injection required
}

// BroadcastReceiver - system instantiates
class MyReceiver : BroadcastReceiver() {
    @Inject lateinit var repository: Repository

    override fun onReceive(context: Context?, intent: Intent?) {
        (context?.applicationContext as MyApp).appComponent.inject(this)
        // Use repository
    }
}
```

### Comparison with Constructor Injection

#### Constructor Injection (Preferred for Regular Classes)

```kotlin
// BEST for regular classes
class UserRepository @Inject constructor(
    private val api: ApiService,
    private val database: UserDao
) {
    // Dependencies are final, immutable
    // Testable without framework
    // Clear dependencies
}

// Usage in test
@Test
fun testRepository() {
    val mockApi = mock<ApiService>()
    val mockDao = mock<UserDao>()
    val repository = UserRepository(mockApi, mockDao)  // Easy to test
}
```

#### Field Injection (Required for Framework Classes)

```kotlin
// NECESSARY for Activities/Fragments
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        inject()
        // Use repository
    }
}

// HARDER to test
@Test
fun testActivity() {
    // More complex test setup required
    // Need to mock DI framework
}
```

### Complete Example with Hilt

```kotlin
// 1. Application setup
@HiltAndroidApp
class MyApp : Application()

// 2. Module definition
@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides
    @Singleton
    fun provideDatabase(
        @ApplicationContext context: Context
    ): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "app_db"
        ).build()
    }

    @Provides
    @Singleton
    fun provideRepository(database: AppDatabase): UserRepository {
        return UserRepository(database.userDao())
    }
}

// 3. Field injection in Activity
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    @Inject
    lateinit var repository: UserRepository

    @Inject
    lateinit var analytics: Analytics

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Hilt automatically injects before onCreate
        // No manual inject() call needed!

        lifecycleScope.launch {
            val users = repository.getUsers()
            displayUsers(users)
        }

        analytics.logEvent("main_activity_created")
    }
}

// 4. Field injection in Fragment
@AndroidEntryPoint
class UserFragment : Fragment() {

    @Inject
    lateinit var adapter: UserAdapter

    private val viewModel: UserViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // adapter is already injected by Hilt
        recyclerView.adapter = adapter

        viewModel.users.observe(viewLifecycleOwner) { users ->
            adapter.submitList(users)
        }
    }
}
```

### Scope Support

Field injection respects scopes just like constructor injection.

```kotlin
// Singleton scope
@Singleton
class GlobalRepository @Inject constructor(
    private val api: ApiService
)

// Activity scope
@ActivityScoped
class ActivityPresenter @Inject constructor(
    private val repository: GlobalRepository
)

// Usage with field injection
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    @Inject
    lateinit var globalRepo: GlobalRepository  // Singleton

    @Inject
    lateinit var presenter: ActivityPresenter  // Activity-scoped

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Both injected with appropriate scopes
    }
}
```

### Advantages of Field Injection

**1. Only Option for Android Framework Classes**

```kotlin
// Cannot use constructor injection here
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: Repository  // Field injection required
}
```

**2. Less Verbose for Many Dependencies**

```kotlin
// With field injection - cleaner for many deps
@AndroidEntryPoint
class MyActivity : AppCompatActivity() {
    @Inject lateinit var repo1: Repository1
    @Inject lateinit var repo2: Repository2
    @Inject lateinit var repo3: Repository3
    @Inject lateinit var analytics: Analytics
    @Inject lateinit var logger: Logger
}

// Constructor injection would be verbose
class MyClass @Inject constructor(
    private val repo1: Repository1,
    private val repo2: Repository2,
    private val repo3: Repository3,
    private val analytics: Analytics,
    private val logger: Logger
)
```

**3. Hilt Simplifies Usage**

```kotlin
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: Repository

    // No manual inject() call needed with Hilt!
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // repository already injected
    }
}
```

### Disadvantages of Field Injection

**1. Harder to Test**

```kotlin
// Field injection - complex test setup
@Test
fun testActivity() {
    val mockRepo = mock<Repository>()
    // Need to mock entire DI framework
    // Or use Hilt test APIs
    val scenario = launchActivity<MainActivity>()
    // Harder to inject mock
}

// Constructor injection - easy testing
@Test
fun testClass() {
    val mockRepo = mock<Repository>()
    val myClass = MyClass(mockRepo)  // Simple!
}
```

**2. Cannot Be Immutable**

```kotlin
@Inject
lateinit var repository: Repository  // Must be var, not val
```

**3. Requires Manual Call (without Hilt)**

```kotlin
// Dagger (without Hilt)
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    appComponent.inject(this)  // Manual call required
    // Use dependencies
}
```

**4. Hidden Dependencies**

```kotlin
// Not obvious what dependencies exist
class MyActivity : AppCompatActivity() {
    @Inject lateinit var repository: Repository
    // Dependencies hidden in fields
}

// Constructor makes dependencies explicit
class MyClass @Inject constructor(
    private val repository: Repository  // Clear dependency
)
```

### Best Practices

**1. Use Constructor Injection When Possible**

```kotlin
// PREFER constructor injection for regular classes
class UserRepository @Inject constructor(
    private val api: ApiService,
    private val dao: UserDao
)
```

**2. Use Field Injection for Android Components**

```kotlin
// USE field injection for framework classes
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository
}
```

**3. Always Use lateinit with @Inject**

```kotlin
// GOOD
@Inject lateinit var repository: Repository

// BAD
@Inject var repository: Repository? = null
```

**4. Keep Injection Early in Lifecycle**

```kotlin
@AndroidEntryPoint
class MyFragment : Fragment() {
    @Inject lateinit var adapter: Adapter

    // Hilt injects before onAttach()
    override fun onAttach(context: Context) {
        super.onAttach(context)
        // adapter is already available
    }
}
```

**5. Use Hilt for Android Components**

```kotlin
// MODERN: Use Hilt
@HiltAndroidApp
class MyApp : Application()

@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: Repository
    // Automatic injection!
}

// OLD: Manual Dagger
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: Repository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        (application as MyApp).component.inject(this)
    }
}
```

### Testing Field-Injected Classes

```kotlin
// Hilt testing
@HiltAndroidTest
class MainActivityTest {

    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @BindValue
    @JvmField
    val mockRepository: Repository = mock()

    @Test
    fun testActivity() {
        hiltRule.inject()

        val scenario = launchActivity<MainActivity>()
        // mockRepository is injected instead of real one
    }
}
```

### Summary

**Field Injection Features:**

| Feature | Description |
|---------|-------------|
| **Syntax** | `@Inject lateinit var dependency: Type` |
| **Mutability** | Must use `var`, cannot be `val` |
| **Nullability** | Requires `lateinit` or nullable type |
| **Visibility** | Cannot be `private` |
| **Timing** | Injected after construction |
| **Testing** | More difficult than constructor injection |
| **Use Case** | Android framework classes (Activity, Fragment) |

**When to Use:**
-  Android components (Activity, Fragment, BroadcastReceiver)
-  Classes where constructor injection is impossible
-  Regular classes (prefer constructor injection)

**Best Practice:**
- Use **constructor injection** for regular classes
- Use **field injection** only for Android framework classes
- Use **Hilt** to simplify field injection setup

## Ответ (RU)
Инжект в поле через Dagger позволяет автоматически внедрять зависимости в поля класса с помощью аннотации `@Inject`. Этот подход имеет специфические характеристики и ограничения.

### Основные особенности

**1. Требует ручного вызова inject()**

В отличие от constructor injection, field injection требует явного вызова метода inject.

```kotlin
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    (application as MyApp).appComponent.inject(this)
    // Теперь поля внедрены
}
```

**2. Нельзя использовать final/val**

Field injection работает только с изменяемыми полями (`var`, не `val`).

**3. Требует lateinit или nullable**

```kotlin
@Inject
lateinit var repository: UserRepository  // С lateinit
```

**4. Не работает с private полями**

Dagger не может внедрять в приватные поля.

**5. Единственная опция для Android компонентов**

Field injection необходим для Activity, Fragment, BroadcastReceiver, где нет контроля над конструктором.

### С Hilt (современный подход)

```kotlin
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    // Hilt автоматически внедряет до onCreate!
    // Не нужен ручной вызов inject()
}
```

### Преимущества

- Единственная опция для Android framework классов
- Менее многословен при многих зависимостях
- Hilt упрощает использование

### Недостатки

- Сложнее тестировать
- Нельзя сделать immutable
- Скрытые зависимости (не очевидны из сигнатуры)

### Лучшие практики

1. **Используйте constructor injection когда возможно** (для обычных классов)
2. **Используйте field injection для Android компонентов** (Activity, Fragment)
3. **Всегда используйте lateinit** с @Inject
4. **Используйте Hilt** для упрощения setup

## Related Questions

- [[q-test-coverage-quality-metrics--testing--medium]]
- [[q-transaction-too-large-exception--android--medium]]
- [[q-dark-theme-android--android--medium]]
