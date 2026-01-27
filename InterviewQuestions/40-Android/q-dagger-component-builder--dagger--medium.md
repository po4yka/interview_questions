---
id: android-dagger-007
title: Dagger Component.Builder and Component.Factory / Component.Builder и Component.Factory
  в Dagger
aliases:
- Component Builder
- Component Factory
- BindsInstance
topic: android
subtopics:
- dagger
- di-dagger
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-dependency-injection
- q-dagger-component-module--dagger--medium
- q-dagger-inject-provides--dagger--medium
created: 2026-01-23
updated: 2026-01-23
tags:
- android/di-dagger
- dependency-injection
- difficulty/medium
- dagger
- component-builder
- component-factory
- binds-instance
anki_cards:
- slug: android-dagger-007-0-en
  language: en
- slug: android-dagger-007-0-ru
  language: ru
---
# Вопрос (RU)
> Что такое @Component.Builder и @Component.Factory в Dagger и когда что использовать?

# Question (EN)
> What are @Component.Builder and @Component.Factory in Dagger and when to use each?

---

## Ответ (RU)

**@Component.Builder** и **@Component.Factory** - это механизмы для создания компонентов с внешними зависимостями (runtime параметрами). Они позволяют передать в граф объекты, которые не могут быть созданы Dagger.

### Зачем Нужны

Dagger не может создать некоторые объекты:
- `Application` / `Context` - создаются системой Android
- `Activity` / `Fragment` - создаются системой
- Runtime параметры (userId, configuration)

Эти объекты нужно передать извне при создании компонента.

### @Component.Builder - Пошаговая Сборка

Builder позволяет устанавливать параметры по одному:

```kotlin
@Singleton
@Component(modules = [AppModule::class, NetworkModule::class])
interface AppComponent {

    fun inject(activity: MainActivity)

    @Component.Builder
    interface Builder {
        // Передаём модуль с runtime-зависимостями
        fun appModule(module: AppModule): Builder

        // @BindsInstance - передаём объект напрямую в граф
        @BindsInstance
        fun application(application: Application): Builder

        @BindsInstance
        fun baseUrl(@Named("baseUrl") url: String): Builder

        fun build(): AppComponent
    }
}
```

**Использование Builder:**

```kotlin
class MyApplication : Application() {

    lateinit var appComponent: AppComponent
        private set

    override fun onCreate() {
        super.onCreate()
        appComponent = DaggerAppComponent.builder()
            .application(this)
            .baseUrl(BuildConfig.API_BASE_URL)
            .appModule(AppModule()) // Если модуль требует параметров
            .build()
    }
}
```

### @Component.Factory - Однострочное Создание

Factory создаёт компонент за один вызов метода:

```kotlin
@Singleton
@Component(modules = [AppModule::class, NetworkModule::class])
interface AppComponent {

    fun inject(activity: MainActivity)

    @Component.Factory
    interface Factory {
        fun create(
            @BindsInstance application: Application,
            @BindsInstance @Named("baseUrl") baseUrl: String
        ): AppComponent
    }
}
```

**Использование Factory:**

```kotlin
class MyApplication : Application() {

    lateinit var appComponent: AppComponent
        private set

    override fun onCreate() {
        super.onCreate()
        appComponent = DaggerAppComponent.factory()
            .create(
                application = this,
                baseUrl = BuildConfig.API_BASE_URL
            )
    }
}
```

### @BindsInstance - Инъекция Runtime Значений

`@BindsInstance` добавляет объект напрямую в dependency graph:

```kotlin
@Component
interface UserComponent {

    @Component.Factory
    interface Factory {
        fun create(
            @BindsInstance user: User,
            @BindsInstance @Named("userId") userId: String
        ): UserComponent
    }
}

// Теперь User и userId можно инжектить
class UserPresenter @Inject constructor(
    private val user: User,
    @Named("userId") private val userId: String
) {
    // ...
}
```

### Сравнение Builder vs Factory

| Критерий | @Component.Builder | @Component.Factory |
|----------|-------------------|-------------------|
| Синтаксис | Пошаговый (chained) | Один вызов |
| Обязательность | Можно пропустить | Все параметры обязательны |
| Когда использовать | Опциональные модули | Все параметры известны |
| Kotlin идиоматичность | Менее | Более |
| Количество кода | Больше | Меньше |

### Builder с Опциональными Модулями

```kotlin
@Component(modules = [
    AppModule::class,
    DebugModule::class // Только для debug
])
interface AppComponent {

    @Component.Builder
    interface Builder {
        @BindsInstance
        fun application(application: Application): Builder

        // Опциональный модуль - можно не вызывать
        fun debugModule(module: DebugModule): Builder

        fun build(): AppComponent
    }
}

// В debug build
appComponent = DaggerAppComponent.builder()
    .application(this)
    .debugModule(DebugModule()) // Только в debug
    .build()

// В release build
appComponent = DaggerAppComponent.builder()
    .application(this)
    // debugModule не вызываем
    .build()
```

### Factory для Subcomponents

```kotlin
@ActivityScope
@Subcomponent(modules = [ActivityModule::class])
interface ActivityComponent {

    fun inject(activity: MainActivity)

    @Subcomponent.Factory
    interface Factory {
        fun create(
            @BindsInstance activity: Activity,
            @BindsInstance @Named("screenName") screenName: String
        ): ActivityComponent
    }
}

// Использование
class MainActivity : AppCompatActivity() {

    @Inject lateinit var presenter: MainPresenter

    override fun onCreate(savedInstanceState: Bundle?) {
        (application as MyApp).appComponent
            .activityComponent()
            .create(
                activity = this,
                screenName = "main"
            )
            .inject(this)

        super.onCreate(savedInstanceState)
    }
}
```

### Модули с Параметрами Конструктора

Если модуль требует параметры, их можно передать через Builder:

```kotlin
@Module
class ConfigModule(private val config: AppConfig) {

    @Provides
    fun provideConfig(): AppConfig = config

    @Provides
    fun provideFeatureFlags(): FeatureFlags {
        return FeatureFlags(config.features)
    }
}

@Component(modules = [ConfigModule::class])
interface AppComponent {

    @Component.Builder
    interface Builder {
        fun configModule(module: ConfigModule): Builder
        fun build(): AppComponent
    }
}

// Создание
val config = AppConfig.load()
appComponent = DaggerAppComponent.builder()
    .configModule(ConfigModule(config))
    .build()
```

### Best Practices

**1. Предпочитайте Factory для простых случаев:**

```kotlin
// Хорошо - простой и понятный
@Component.Factory
interface Factory {
    fun create(@BindsInstance app: Application): AppComponent
}
```

**2. Используйте Builder для сложных сценариев:**

```kotlin
// Хорошо - когда нужна гибкость
@Component.Builder
interface Builder {
    @BindsInstance fun app(app: Application): Builder
    fun analyticsModule(module: AnalyticsModule): Builder // Опционально
    fun build(): AppComponent
}
```

**3. Используйте @Named для различения одинаковых типов:**

```kotlin
@Component.Factory
interface Factory {
    fun create(
        @BindsInstance @Named("debug") isDebug: Boolean,
        @BindsInstance @Named("versionCode") versionCode: Int
    ): AppComponent
}
```

**4. Избегайте передачи модулей без параметров:**

```kotlin
// Плохо - модуль без параметров
@Component.Builder
interface Builder {
    fun networkModule(module: NetworkModule): Builder // Не нужно!
    fun build(): AppComponent
}

// Хорошо - Dagger сам создаст модуль
@Component(modules = [NetworkModule::class])
interface AppComponent {
    @Component.Factory
    interface Factory {
        fun create(@BindsInstance app: Application): AppComponent
    }
}
```

---

## Answer (EN)

**@Component.Builder** and **@Component.Factory** are mechanisms for creating components with external dependencies (runtime parameters). They allow passing objects that cannot be created by Dagger into the graph.

### Why Needed

Dagger cannot create some objects:
- `Application` / `Context` - created by Android system
- `Activity` / `Fragment` - created by system
- Runtime parameters (userId, configuration)

These objects must be passed from outside when creating the component.

### @Component.Builder - Step-by-Step Assembly

Builder allows setting parameters one by one:

```kotlin
@Singleton
@Component(modules = [AppModule::class, NetworkModule::class])
interface AppComponent {

    fun inject(activity: MainActivity)

    @Component.Builder
    interface Builder {
        // Pass module with runtime dependencies
        fun appModule(module: AppModule): Builder

        // @BindsInstance - pass object directly to graph
        @BindsInstance
        fun application(application: Application): Builder

        @BindsInstance
        fun baseUrl(@Named("baseUrl") url: String): Builder

        fun build(): AppComponent
    }
}
```

**Using Builder:**

```kotlin
class MyApplication : Application() {

    lateinit var appComponent: AppComponent
        private set

    override fun onCreate() {
        super.onCreate()
        appComponent = DaggerAppComponent.builder()
            .application(this)
            .baseUrl(BuildConfig.API_BASE_URL)
            .appModule(AppModule()) // If module requires parameters
            .build()
    }
}
```

### @Component.Factory - Single-Call Creation

Factory creates component in one method call:

```kotlin
@Singleton
@Component(modules = [AppModule::class, NetworkModule::class])
interface AppComponent {

    fun inject(activity: MainActivity)

    @Component.Factory
    interface Factory {
        fun create(
            @BindsInstance application: Application,
            @BindsInstance @Named("baseUrl") baseUrl: String
        ): AppComponent
    }
}
```

**Using Factory:**

```kotlin
class MyApplication : Application() {

    lateinit var appComponent: AppComponent
        private set

    override fun onCreate() {
        super.onCreate()
        appComponent = DaggerAppComponent.factory()
            .create(
                application = this,
                baseUrl = BuildConfig.API_BASE_URL
            )
    }
}
```

### @BindsInstance - Runtime Value Injection

`@BindsInstance` adds object directly to dependency graph:

```kotlin
@Component
interface UserComponent {

    @Component.Factory
    interface Factory {
        fun create(
            @BindsInstance user: User,
            @BindsInstance @Named("userId") userId: String
        ): UserComponent
    }
}

// Now User and userId can be injected
class UserPresenter @Inject constructor(
    private val user: User,
    @Named("userId") private val userId: String
) {
    // ...
}
```

### Builder vs Factory Comparison

| Criterion | @Component.Builder | @Component.Factory |
|-----------|-------------------|-------------------|
| Syntax | Step-by-step (chained) | Single call |
| Required | Can skip calls | All parameters required |
| When to use | Optional modules | All parameters known |
| Kotlin idiomaticity | Less | More |
| Code amount | More | Less |

### Builder with Optional Modules

```kotlin
@Component(modules = [
    AppModule::class,
    DebugModule::class // Debug only
])
interface AppComponent {

    @Component.Builder
    interface Builder {
        @BindsInstance
        fun application(application: Application): Builder

        // Optional module - can skip
        fun debugModule(module: DebugModule): Builder

        fun build(): AppComponent
    }
}

// In debug build
appComponent = DaggerAppComponent.builder()
    .application(this)
    .debugModule(DebugModule()) // Debug only
    .build()

// In release build
appComponent = DaggerAppComponent.builder()
    .application(this)
    // Don't call debugModule
    .build()
```

### Factory for Subcomponents

```kotlin
@ActivityScope
@Subcomponent(modules = [ActivityModule::class])
interface ActivityComponent {

    fun inject(activity: MainActivity)

    @Subcomponent.Factory
    interface Factory {
        fun create(
            @BindsInstance activity: Activity,
            @BindsInstance @Named("screenName") screenName: String
        ): ActivityComponent
    }
}

// Usage
class MainActivity : AppCompatActivity() {

    @Inject lateinit var presenter: MainPresenter

    override fun onCreate(savedInstanceState: Bundle?) {
        (application as MyApp).appComponent
            .activityComponent()
            .create(
                activity = this,
                screenName = "main"
            )
            .inject(this)

        super.onCreate(savedInstanceState)
    }
}
```

### Modules with Constructor Parameters

If module requires parameters, pass them through Builder:

```kotlin
@Module
class ConfigModule(private val config: AppConfig) {

    @Provides
    fun provideConfig(): AppConfig = config

    @Provides
    fun provideFeatureFlags(): FeatureFlags {
        return FeatureFlags(config.features)
    }
}

@Component(modules = [ConfigModule::class])
interface AppComponent {

    @Component.Builder
    interface Builder {
        fun configModule(module: ConfigModule): Builder
        fun build(): AppComponent
    }
}

// Creation
val config = AppConfig.load()
appComponent = DaggerAppComponent.builder()
    .configModule(ConfigModule(config))
    .build()
```

### Best Practices

**1. Prefer Factory for simple cases:**

```kotlin
// Good - simple and clear
@Component.Factory
interface Factory {
    fun create(@BindsInstance app: Application): AppComponent
}
```

**2. Use Builder for complex scenarios:**

```kotlin
// Good - when flexibility needed
@Component.Builder
interface Builder {
    @BindsInstance fun app(app: Application): Builder
    fun analyticsModule(module: AnalyticsModule): Builder // Optional
    fun build(): AppComponent
}
```

**3. Use @Named to distinguish same types:**

```kotlin
@Component.Factory
interface Factory {
    fun create(
        @BindsInstance @Named("debug") isDebug: Boolean,
        @BindsInstance @Named("versionCode") versionCode: Int
    ): AppComponent
}
```

**4. Avoid passing parameter-less modules:**

```kotlin
// Bad - module without parameters
@Component.Builder
interface Builder {
    fun networkModule(module: NetworkModule): Builder // Not needed!
    fun build(): AppComponent
}

// Good - Dagger creates module itself
@Component(modules = [NetworkModule::class])
interface AppComponent {
    @Component.Factory
    interface Factory {
        fun create(@BindsInstance app: Application): AppComponent
    }
}
```

---

## Дополнительные Вопросы (RU)

- Можно ли использовать и Builder, и Factory в одном компоненте?
- Как работает @BindsInstance с nullable типами?
- Когда модулю нужны параметры конструктора?

## Follow-ups

- Can you use both Builder and Factory in one component?
- How does @BindsInstance work with nullable types?
- When does a module need constructor parameters?

## Ссылки (RU)

- [Component Builder Documentation](https://dagger.dev/dev-guide/component-builders.html)
- [BindsInstance Documentation](https://dagger.dev/api/latest/dagger/BindsInstance.html)

## References

- [Component Builder Documentation](https://dagger.dev/dev-guide/component-builders.html)
- [BindsInstance Documentation](https://dagger.dev/api/latest/dagger/BindsInstance.html)

## Связанные Вопросы (RU)

### Medium
- [[q-dagger-component-module--dagger--medium]]
- [[q-dagger-inject-provides--dagger--medium]]
- [[q-dagger-lazy-provider--dagger--medium]]

### Hard
- [[q-dagger-subcomponents--dagger--hard]]
- [[q-dagger-scopes-custom--dagger--hard]]

## Related Questions

### Medium
- [[q-dagger-component-module--dagger--medium]]
- [[q-dagger-inject-provides--dagger--medium]]
- [[q-dagger-lazy-provider--dagger--medium]]

### Hard
- [[q-dagger-subcomponents--dagger--hard]]
- [[q-dagger-scopes-custom--dagger--hard]]
