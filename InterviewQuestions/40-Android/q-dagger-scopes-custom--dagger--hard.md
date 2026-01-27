---
id: android-dagger-004
title: Dagger Scopes and Custom Scopes / Scopes и Custom Scopes в Dagger
aliases:
- Dagger Scopes
- Custom Scopes
- Области видимости Dagger
topic: android
subtopics:
- dagger
- di-dagger
question_kind: theory
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-dependency-injection
- q-dagger-component-module--dagger--medium
- q-dagger-subcomponents--dagger--hard
created: 2026-01-23
updated: 2026-01-23
tags:
- android/di-dagger
- dependency-injection
- difficulty/hard
- dagger
- scope
- singleton
anki_cards:
- slug: android-dagger-004-0-en
  language: en
- slug: android-dagger-004-0-ru
  language: ru
---
# Вопрос (RU)
> Что такое @Scope в Dagger, как работают scopes и как создать custom scope?

# Question (EN)
> What is @Scope in Dagger, how do scopes work, and how do you create a custom scope?

---

## Ответ (RU)

**@Scope** в Dagger - это механизм управления временем жизни зависимостей. Scope гарантирует, что в рамках одного компонента будет создан только один экземпляр зависимости.

### Как Работают Scopes

```
Без scope: Каждый запрос = новый экземпляр
С scope: Один экземпляр на компонент с этим scope
```

```kotlin
// Без scope - каждый раз новый объект
@Provides
fun provideAnalytics(): Analytics {
    return Analytics() // Каждый @Inject получит новый экземпляр
}

// С scope - один объект на компонент
@Singleton
@Provides
fun provideDatabase(context: Context): AppDatabase {
    return Room.databaseBuilder(...).build() // Один на всё приложение
}
```

### @Singleton - Встроенный Scope

`@Singleton` - единственный предопределённый scope в Dagger. Гарантирует один экземпляр на компонент.

```kotlin
@Singleton
@Component(modules = [AppModule::class])
interface AppComponent {
    // Все @Singleton зависимости живут столько, сколько этот компонент
}

@Module
class AppModule {

    @Singleton
    @Provides
    fun provideRetrofit(): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .build()
    }
}

// Или на классе
@Singleton
class UserManager @Inject constructor(
    private val userDao: UserDao
) {
    // Один экземпляр на весь AppComponent
}
```

### Создание Custom Scopes

Custom scope - это просто аннотация, помеченная `@Scope`:

```kotlin
import javax.inject.Scope

@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class ActivityScope

@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class FragmentScope

@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class FeatureScope

@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class UserScope // Пока пользователь залогинен
```

### Применение Custom Scopes

```kotlin
// Компонент с custom scope
@ActivityScope
@Subcomponent(modules = [ActivityModule::class])
interface ActivityComponent {
    fun inject(activity: MainActivity)
    fun fragmentComponent(): FragmentComponent.Factory

    @Subcomponent.Factory
    interface Factory {
        fun create(@BindsInstance activity: Activity): ActivityComponent
    }
}

// Модуль с scoped зависимостями
@Module
class ActivityModule {

    @ActivityScope
    @Provides
    fun providePresenter(
        repository: UserRepository,
        analytics: Analytics
    ): MainPresenter {
        return MainPresenter(repository, analytics)
    }
}

// Или на классе
@ActivityScope
class ActivityNavigator @Inject constructor(
    private val activity: Activity
) {
    fun navigateTo(screen: Screen) {
        // Один навигатор на Activity
    }
}
```

### Правила Scopes

**1. Scope компонента должен совпадать со scope зависимостей:**

```kotlin
// Правильно: @ActivityScope компонент содержит @ActivityScope зависимости
@ActivityScope
@Subcomponent(modules = [ActivityModule::class])
interface ActivityComponent

@ActivityScope
class ActivityPresenter @Inject constructor()

// Ошибка компиляции: scope не совпадает
@FragmentScope // ОШИБКА!
class WrongPresenter @Inject constructor()
```

**2. Subcomponent должен иметь другой scope чем родитель:**

```kotlin
@Singleton
@Component
interface AppComponent // Singleton scope

@ActivityScope // Другой scope - OK
@Subcomponent
interface ActivityComponent

@ActivityScope // ОШИБКА: такой же scope как родитель
@Subcomponent
interface BadComponent
```

**3. Unscoped зависимости доступны везде:**

```kotlin
// Без scope - можно использовать в любом компоненте
class Logger @Inject constructor() // Новый экземпляр каждый раз

@Module
class UtilModule {
    @Provides // Без scope
    fun provideGson(): Gson = Gson()
}
```

### Типичная Иерархия Scopes

```
@Singleton (AppComponent)
    └── @ActivityScope (ActivityComponent)
            └── @FragmentScope (FragmentComponent)
```

```kotlin
@Singleton
@Component(modules = [AppModule::class])
interface AppComponent {
    fun activityComponent(): ActivityComponent.Factory

    // Singleton зависимости
    fun retrofit(): Retrofit
    fun database(): AppDatabase
}

@ActivityScope
@Subcomponent(modules = [ActivityModule::class])
interface ActivityComponent {
    fun fragmentComponent(): FragmentComponent.Factory
    fun inject(activity: MainActivity)

    @Subcomponent.Factory
    interface Factory {
        fun create(): ActivityComponent
    }
}

@FragmentScope
@Subcomponent(modules = [FragmentModule::class])
interface FragmentComponent {
    fun inject(fragment: HomeFragment)

    @Subcomponent.Factory
    interface Factory {
        fun create(): FragmentComponent
    }
}
```

### Scope и Жизненный Цикл

**Важно:** Scope НЕ управляет жизненным циклом объекта. Он только гарантирует единственность в рамках компонента.

```kotlin
class MyApplication : Application() {

    // Компонент живёт столько, сколько Application держит ссылку
    lateinit var appComponent: AppComponent

    override fun onCreate() {
        super.onCreate()
        appComponent = DaggerAppComponent.create()
    }
}

class MainActivity : AppCompatActivity() {

    // Компонент живёт столько, сколько Activity держит ссылку
    private lateinit var activityComponent: ActivityComponent

    override fun onCreate(savedInstanceState: Bundle?) {
        activityComponent = (application as MyApplication)
            .appComponent
            .activityComponent()
            .create()
        // ...
    }

    override fun onDestroy() {
        super.onDestroy()
        // activityComponent станет eligible для GC
        // вместе со всеми @ActivityScope зависимостями
    }
}
```

### Пример: UserScope для Сессии

```kotlin
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class UserScope

@UserScope
@Subcomponent(modules = [UserModule::class])
interface UserComponent {
    fun inject(activity: ProfileActivity)

    @Subcomponent.Factory
    interface Factory {
        fun create(@BindsInstance user: User): UserComponent
    }
}

// В AppComponent или где управляется сессия
class SessionManager @Inject constructor(
    private val userComponentFactory: UserComponent.Factory
) {
    var userComponent: UserComponent? = null
        private set

    fun login(user: User) {
        userComponent = userComponentFactory.create(user)
    }

    fun logout() {
        userComponent = null // Все @UserScope зависимости освобождаются
    }
}
```

### Anti-patterns

```kotlin
// ПЛОХО: Singleton для stateful объекта привязанного к Activity
@Singleton
class BadNavigator @Inject constructor(
    private val activity: Activity // Activity протечёт!
)

// ХОРОШО: Правильный scope
@ActivityScope
class GoodNavigator @Inject constructor(
    private val activity: Activity
)

// ПЛОХО: Scope на всём подряд (лишний overhead)
@ActivityScope
class SimpleMapper @Inject constructor() // Не нужен scope!

// ХОРОШО: Scope только когда нужна единственность
class SimpleMapper @Inject constructor() // Без scope - чисто и просто
```

---

## Answer (EN)

**@Scope** in Dagger is a mechanism for managing dependency lifecycle. Scope guarantees that only one instance of a dependency will be created within a single component.

### How Scopes Work

```
Without scope: Each request = new instance
With scope: One instance per component with that scope
```

```kotlin
// Without scope - new object every time
@Provides
fun provideAnalytics(): Analytics {
    return Analytics() // Each @Inject gets a new instance
}

// With scope - one object per component
@Singleton
@Provides
fun provideDatabase(context: Context): AppDatabase {
    return Room.databaseBuilder(...).build() // One for entire app
}
```

### @Singleton - Built-in Scope

`@Singleton` is the only predefined scope in Dagger. Guarantees one instance per component.

```kotlin
@Singleton
@Component(modules = [AppModule::class])
interface AppComponent {
    // All @Singleton dependencies live as long as this component
}

@Module
class AppModule {

    @Singleton
    @Provides
    fun provideRetrofit(): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .build()
    }
}

// Or on class
@Singleton
class UserManager @Inject constructor(
    private val userDao: UserDao
) {
    // One instance for entire AppComponent
}
```

### Creating Custom Scopes

Custom scope is just an annotation marked with `@Scope`:

```kotlin
import javax.inject.Scope

@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class ActivityScope

@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class FragmentScope

@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class FeatureScope

@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class UserScope // While user is logged in
```

### Applying Custom Scopes

```kotlin
// Component with custom scope
@ActivityScope
@Subcomponent(modules = [ActivityModule::class])
interface ActivityComponent {
    fun inject(activity: MainActivity)
    fun fragmentComponent(): FragmentComponent.Factory

    @Subcomponent.Factory
    interface Factory {
        fun create(@BindsInstance activity: Activity): ActivityComponent
    }
}

// Module with scoped dependencies
@Module
class ActivityModule {

    @ActivityScope
    @Provides
    fun providePresenter(
        repository: UserRepository,
        analytics: Analytics
    ): MainPresenter {
        return MainPresenter(repository, analytics)
    }
}

// Or on class
@ActivityScope
class ActivityNavigator @Inject constructor(
    private val activity: Activity
) {
    fun navigateTo(screen: Screen) {
        // One navigator per Activity
    }
}
```

### Scope Rules

**1. Component scope must match dependency scopes:**

```kotlin
// Correct: @ActivityScope component contains @ActivityScope dependencies
@ActivityScope
@Subcomponent(modules = [ActivityModule::class])
interface ActivityComponent

@ActivityScope
class ActivityPresenter @Inject constructor()

// Compilation error: scope mismatch
@FragmentScope // ERROR!
class WrongPresenter @Inject constructor()
```

**2. Subcomponent must have different scope than parent:**

```kotlin
@Singleton
@Component
interface AppComponent // Singleton scope

@ActivityScope // Different scope - OK
@Subcomponent
interface ActivityComponent

@ActivityScope // ERROR: same scope as parent
@Subcomponent
interface BadComponent
```

**3. Unscoped dependencies are available everywhere:**

```kotlin
// Without scope - can be used in any component
class Logger @Inject constructor() // New instance every time

@Module
class UtilModule {
    @Provides // No scope
    fun provideGson(): Gson = Gson()
}
```

### Typical Scope Hierarchy

```
@Singleton (AppComponent)
    └── @ActivityScope (ActivityComponent)
            └── @FragmentScope (FragmentComponent)
```

```kotlin
@Singleton
@Component(modules = [AppModule::class])
interface AppComponent {
    fun activityComponent(): ActivityComponent.Factory

    // Singleton dependencies
    fun retrofit(): Retrofit
    fun database(): AppDatabase
}

@ActivityScope
@Subcomponent(modules = [ActivityModule::class])
interface ActivityComponent {
    fun fragmentComponent(): FragmentComponent.Factory
    fun inject(activity: MainActivity)

    @Subcomponent.Factory
    interface Factory {
        fun create(): ActivityComponent
    }
}

@FragmentScope
@Subcomponent(modules = [FragmentModule::class])
interface FragmentComponent {
    fun inject(fragment: HomeFragment)

    @Subcomponent.Factory
    interface Factory {
        fun create(): FragmentComponent
    }
}
```

### Scope and Lifecycle

**Important:** Scope does NOT manage object lifecycle. It only guarantees uniqueness within a component.

```kotlin
class MyApplication : Application() {

    // Component lives as long as Application holds reference
    lateinit var appComponent: AppComponent

    override fun onCreate() {
        super.onCreate()
        appComponent = DaggerAppComponent.create()
    }
}

class MainActivity : AppCompatActivity() {

    // Component lives as long as Activity holds reference
    private lateinit var activityComponent: ActivityComponent

    override fun onCreate(savedInstanceState: Bundle?) {
        activityComponent = (application as MyApplication)
            .appComponent
            .activityComponent()
            .create()
        // ...
    }

    override fun onDestroy() {
        super.onDestroy()
        // activityComponent becomes eligible for GC
        // along with all @ActivityScope dependencies
    }
}
```

### Example: UserScope for Session

```kotlin
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class UserScope

@UserScope
@Subcomponent(modules = [UserModule::class])
interface UserComponent {
    fun inject(activity: ProfileActivity)

    @Subcomponent.Factory
    interface Factory {
        fun create(@BindsInstance user: User): UserComponent
    }
}

// In AppComponent or where session is managed
class SessionManager @Inject constructor(
    private val userComponentFactory: UserComponent.Factory
) {
    var userComponent: UserComponent? = null
        private set

    fun login(user: User) {
        userComponent = userComponentFactory.create(user)
    }

    fun logout() {
        userComponent = null // All @UserScope dependencies released
    }
}
```

### Anti-patterns

```kotlin
// BAD: Singleton for stateful object bound to Activity
@Singleton
class BadNavigator @Inject constructor(
    private val activity: Activity // Activity will leak!
)

// GOOD: Correct scope
@ActivityScope
class GoodNavigator @Inject constructor(
    private val activity: Activity
)

// BAD: Scope on everything (unnecessary overhead)
@ActivityScope
class SimpleMapper @Inject constructor() // Doesn't need scope!

// GOOD: Scope only when uniqueness needed
class SimpleMapper @Inject constructor() // No scope - clean and simple
```

---

## Дополнительные Вопросы (RU)

- Как избежать memory leaks при использовании scopes?
- Можно ли иметь зависимость с одним scope в компоненте с другим scope?
- Как правильно организовать scope для ViewModels?

## Follow-ups

- How do you avoid memory leaks when using scopes?
- Can you have a dependency with one scope in a component with a different scope?
- How do you properly organize scope for ViewModels?

## Ссылки (RU)

- [Dagger Scopes](https://dagger.dev/dev-guide/scopes.html)
- [Custom Scopes in Dagger](https://developer.android.com/training/dependency-injection/dagger-android#scopes)

## References

- [Dagger Scopes](https://dagger.dev/dev-guide/scopes.html)
- [Custom Scopes in Dagger](https://developer.android.com/training/dependency-injection/dagger-android#scopes)

## Связанные Вопросы (RU)

### Medium
- [[q-dagger-component-module--dagger--medium]]
- [[q-dagger-inject-provides--dagger--medium]]

### Hard
- [[q-dagger-subcomponents--dagger--hard]]
- [[q-dagger-multibindings--dagger--hard]]
- [[q-dagger-generated-code--dagger--hard]]

## Related Questions

### Medium
- [[q-dagger-component-module--dagger--medium]]
- [[q-dagger-inject-provides--dagger--medium]]

### Hard
- [[q-dagger-subcomponents--dagger--hard]]
- [[q-dagger-multibindings--dagger--hard]]
- [[q-dagger-generated-code--dagger--hard]]
