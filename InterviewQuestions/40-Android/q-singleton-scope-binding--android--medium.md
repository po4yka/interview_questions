---
topic: android
tags:
  - android
  - android/dependency-injection
  - dagger
  - dependency-injection
  - hilt
  - scope
  - singleton
difficulty: medium
status: draft
---

# К какому scope привязан Singleton?

**English**: What scope is @Singleton bound to?

## Answer

**@Singleton** is bound to the **lifetime of the component** that uses it.

- **In Dagger:** Lives as long as the Component exists
- **In Android (with Hilt):** Usually bound to **Application lifecycle**
- **Key point:** NOT a true global singleton - scoped to component

---

## Singleton Scope Binding

### In Dagger (AppComponent)

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
            "database"
        ).build()
    }
}

// In Application
class MyApplication : Application() {
    val appComponent: AppComponent by lazy {
        DaggerAppComponent.create()
    }
}
```

**Lifetime:** `@Singleton` instance lives as long as `AppComponent` exists (usually entire app).

---

### In Hilt (Application Component)

```kotlin
@HiltAndroidApp
class MyApplication : Application()

@Singleton
class UserRepository @Inject constructor(
    private val api: ApiService,
    private val database: AppDatabase
) {
    // Single instance for entire app
}

@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository // Same instance

    @Inject lateinit var database: AppDatabase // Same instance
}

@AndroidEntryPoint
class SecondActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository // SAME instance as MainActivity
}
```

**Lifetime:** Lives for entire application (from app start to termination).

---

## Component Lifetime Examples

### 1. Application Scope (@Singleton)

```kotlin
@Singleton
@Component
interface AppComponent {
    fun repository(): UserRepository
}

@Singleton
class UserRepository @Inject constructor() {
    // Lives for ENTIRE app lifetime
}
```

**Created:** When AppComponent is created (usually in Application.onCreate())
**Destroyed:** When app process is killed

---

### 2. Activity Scope (@ActivityScoped)

```kotlin
@ActivityScoped
@Subcomponent
interface ActivityComponent {
    fun presenter(): Presenter
}

@ActivityScoped
class Presenter @Inject constructor() {
    // Lives for SINGLE Activity instance
}
```

**Created:** When Activity is created
**Destroyed:** When Activity is destroyed (onDestroy)

---

### 3. Custom Component Scope

```kotlin
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class UserScope

@UserScope
@Subcomponent
interface UserComponent {
    fun session(): UserSession
}

@UserScope
class UserSession @Inject constructor() {
    // Lives while user is logged in
}

// Create when user logs in
val userComponent = appComponent.userComponent().create()

// Destroy when user logs out
userComponent = null // Instance will be garbage collected
```

---

## Important Distinctions

### NOT a True Singleton

```kotlin
// ❌ WRONG UNDERSTANDING
@Singleton
class Database @Inject constructor() {
    // This is NOT Java's singleton pattern!
}

// This is NOT the same as:
object Database {
    // True Kotlin singleton
}
```

**@Singleton in Dagger:**
- One instance **per component**
- If you create multiple AppComponents, you get multiple "singletons"

```kotlin
val component1 = DaggerAppComponent.create()
val component2 = DaggerAppComponent.create()

val repo1 = component1.repository() // Instance 1
val repo2 = component2.repository() // Instance 2 (different!)
```

---

## Hilt Component Scopes

| Component | Scope | Lifetime |
|-----------|-------|----------|
| **SingletonComponent** | @Singleton | Application |
| **ActivityRetainedComponent** | @ActivityRetainedScoped | Survives configuration changes |
| **ActivityComponent** | @ActivityScoped | Activity |
| **FragmentComponent** | @FragmentScoped | Fragment |
| **ViewComponent** | @ViewScoped | View |
| **ServiceComponent** | @ServiceScoped | Service |

### Example: Different Scopes

```kotlin
// Application scope
@Singleton
class AppDatabase @Inject constructor()

// Survives rotation
@ActivityRetainedScoped
class UserViewModel @Inject constructor()

// Activity scope
@ActivityScoped
class Presenter @Inject constructor()

// Fragment scope
@FragmentScoped
class FragmentViewModel @Inject constructor()
```

---

## Memory and Lifecycle

### Singleton Can Cause Memory Leaks

```kotlin
// ❌ BAD: Singleton holding Activity reference
@Singleton
class Analytics @Inject constructor(
    private val activity: Activity // LEAK!
) {
    // Activity leaked when it's destroyed
    // But @Singleton keeps reference
}

// ✅ GOOD: Use Application Context
@Singleton
class Analytics @Inject constructor(
    @ApplicationContext private val context: Context
) {
    // Safe: Application context lives forever
}
```

---

### Proper Scope Matching

```kotlin
// ✅ GOOD: Match scope to lifecycle
@Singleton
class NetworkClient // Lives for app

@ActivityScoped
class Presenter // Lives for Activity

@FragmentScoped
class ViewModel // Lives for Fragment

// ❌ BAD: Scope mismatch
@Singleton
class ActivityPresenter // Activity data in app-level scope = leak!
```

---

## Testing Implications

```kotlin
@RunWith(AndroidJUnit4::class)
class RepositoryTest {

    @Test
    fun `singleton provides same instance`() {
        val component = DaggerTestComponent.create()

        val repo1 = component.repository()
        val repo2 = component.repository()

        // Same instance
        assertSame(repo1, repo2)
    }

    @Test
    fun `different components provide different instances`() {
        val component1 = DaggerTestComponent.create()
        val component2 = DaggerTestComponent.create()

        val repo1 = component1.repository()
        val repo2 = component2.repository()

        // Different instances!
        assertNotSame(repo1, repo2)
    }
}
```

---

## Summary

**@Singleton is bound to:**
- The **component's lifetime** (not global)
- In Hilt: **Application component** → entire app lifecycle
- In custom Dagger: Depends on when component is created/destroyed

**Key points:**
- ✅ One instance **per component**
- ✅ Lives as long as component lives
- ❌ NOT a true global singleton
- ❌ Can cause memory leaks if misused

**Best practices:**
```kotlin
// ✅ Application-wide resources
@Singleton
class AppDatabase

// ✅ Use Application Context
@Singleton
class Analytics @Inject constructor(
    @ApplicationContext private val context: Context
)

// ❌ Don't hold Activity references
@Singleton
class Bad @Inject constructor(
    private val activity: Activity // LEAK!
)
```

---

## Ответ

**@Singleton** привязан к **времени жизни компонента**, в котором он используется.

- **В Dagger:** Живет, пока существует Component
- **В Android (с Hilt):** Обычно привязан к **жизненному циклу приложения**
- **Важно:** Это НЕ глобальный singleton - привязан к компоненту

**Пример:**

```kotlin
// В Hilt - живет весь жизненный цикл приложения
@Singleton
class UserRepository @Inject constructor(
    private val api: ApiService
)

// Создается: когда создается AppComponent (обычно в Application.onCreate())
// Уничтожается: когда процесс приложения завершается
```

**Важные моменты:**
- ✅ Один экземпляр **на компонент**
- ✅ Живет столько, сколько живет компонент
- ❌ Может вызвать утечки памяти при неправильном использовании

