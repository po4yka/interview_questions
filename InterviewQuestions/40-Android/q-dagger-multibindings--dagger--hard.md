---
id: android-dagger-005
title: Dagger Multibindings / Multibindings в Dagger
aliases: [Dagger Multibindings, IntoSet, IntoMap]
topic: android
subtopics: [dagger, di-dagger]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-dependency-injection, q-dagger-component-module--dagger--medium, q-dagger-scopes-custom--dagger--hard]
created: 2026-01-23
updated: 2026-01-23
tags: [android/di-dagger, dependency-injection, difficulty/hard, dagger, multibindings, into-set, into-map]

---
# Вопрос (RU)
> Что такое Multibindings в Dagger и как использовать @IntoSet и @IntoMap?

# Question (EN)
> What are Multibindings in Dagger and how do you use @IntoSet and @IntoMap?

---

## Ответ (RU)

**Multibindings** позволяют собирать множество зависимостей в коллекцию (Set или Map) без явного указания всех элементов в одном месте. Это мощный паттерн для расширяемых систем.

### @IntoSet - Сборка в Set

Каждый `@IntoSet` метод добавляет элемент в общий `Set`:

```kotlin
// Определяем несколько interceptors в разных модулях
@Module
class NetworkModule {

    @Provides
    @IntoSet
    fun provideLoggingInterceptor(): Interceptor {
        return HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }
    }

    @Provides
    @IntoSet
    fun provideAuthInterceptor(tokenProvider: TokenProvider): Interceptor {
        return AuthInterceptor(tokenProvider)
    }
}

@Module
class AnalyticsModule {

    @Provides
    @IntoSet
    fun provideAnalyticsInterceptor(analytics: Analytics): Interceptor {
        return AnalyticsInterceptor(analytics)
    }
}

// Инжектим весь Set
@Module
class OkHttpModule {

    @Provides
    fun provideOkHttpClient(
        interceptors: Set<@JvmSuppressWildcards Interceptor>
    ): OkHttpClient {
        return OkHttpClient.Builder().apply {
            interceptors.forEach { addInterceptor(it) }
        }.build()
    }
}
```

### @ElementsIntoSet - Добавление Нескольких Элементов

```kotlin
@Module
class ValidatorsModule {

    @Provides
    @ElementsIntoSet
    fun provideDefaultValidators(): Set<Validator> {
        return setOf(
            EmailValidator(),
            PhoneValidator(),
            PasswordValidator()
        )
    }

    @Provides
    @IntoSet
    fun provideCustomValidator(): Validator {
        return CustomValidator()
    }
}

// Использование
class FormValidator @Inject constructor(
    private val validators: Set<@JvmSuppressWildcards Validator>
) {
    fun validate(form: Form): List<ValidationError> {
        return validators.flatMap { it.validate(form) }
    }
}
```

### @IntoMap - Сборка в Map

`@IntoMap` требует аннотацию с ключом для каждого элемента:

```kotlin
// Встроенные ключи
@Module
class ViewModelModule {

    @Provides
    @IntoMap
    @ClassKey(HomeViewModel::class)
    fun provideHomeViewModel(
        repository: HomeRepository
    ): ViewModel {
        return HomeViewModel(repository)
    }

    @Provides
    @IntoMap
    @ClassKey(ProfileViewModel::class)
    fun provideProfileViewModel(
        userRepository: UserRepository
    ): ViewModel {
        return ProfileViewModel(userRepository)
    }
}

// Использование
class ViewModelFactory @Inject constructor(
    private val viewModels: Map<Class<*>, @JvmSuppressWildcards Provider<ViewModel>>
) : ViewModelProvider.Factory {

    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        val provider = viewModels[modelClass]
            ?: throw IllegalArgumentException("Unknown ViewModel: $modelClass")
        return provider.get() as T
    }
}
```

### Custom Map Keys

Создание собственного ключа для Map:

```kotlin
// Определяем аннотацию-ключ
@MapKey
@Retention(AnnotationRetention.RUNTIME)
annotation class ScreenKey(val value: KClass<out Screen>)

// Используем в модуле
@Module
abstract class ScreenModule {

    @Binds
    @IntoMap
    @ScreenKey(HomeScreen::class)
    abstract fun bindHomeScreen(screen: HomeScreen): Screen

    @Binds
    @IntoMap
    @ScreenKey(ProfileScreen::class)
    abstract fun bindProfileScreen(screen: ProfileScreen): Screen
}

// Navigator использует Map
class Navigator @Inject constructor(
    private val screens: Map<KClass<out Screen>, @JvmSuppressWildcards Provider<Screen>>
) {
    fun navigateTo(screenClass: KClass<out Screen>) {
        val screen = screens[screenClass]?.get()
            ?: throw IllegalArgumentException("Unknown screen: $screenClass")
        screen.show()
    }
}
```

### String и Int Keys

```kotlin
@Module
class AnalyticsModule {

    @Provides
    @IntoMap
    @StringKey("firebase")
    fun provideFirebaseTracker(): AnalyticsTracker {
        return FirebaseTracker()
    }

    @Provides
    @IntoMap
    @StringKey("amplitude")
    fun provideAmplitudeTracker(): AnalyticsTracker {
        return AmplitudeTracker()
    }
}

class CompositeAnalytics @Inject constructor(
    private val trackers: Map<String, @JvmSuppressWildcards AnalyticsTracker>
) {
    fun track(event: AnalyticsEvent) {
        trackers.values.forEach { it.track(event) }
    }

    fun getTracker(name: String): AnalyticsTracker? {
        return trackers[name]
    }
}
```

### Enum Keys

```kotlin
enum class Environment {
    DEV, STAGING, PROD
}

@MapKey
@Retention(AnnotationRetention.RUNTIME)
annotation class EnvironmentKey(val value: Environment)

@Module
class ConfigModule {

    @Provides
    @IntoMap
    @EnvironmentKey(Environment.DEV)
    fun provideDevConfig(): AppConfig {
        return AppConfig(
            apiUrl = "https://dev.api.example.com",
            loggingEnabled = true
        )
    }

    @Provides
    @IntoMap
    @EnvironmentKey(Environment.PROD)
    fun provideProdConfig(): AppConfig {
        return AppConfig(
            apiUrl = "https://api.example.com",
            loggingEnabled = false
        )
    }
}

class ConfigProvider @Inject constructor(
    private val configs: Map<Environment, @JvmSuppressWildcards AppConfig>
) {
    fun getConfig(environment: Environment): AppConfig {
        return configs[environment]
            ?: throw IllegalStateException("No config for $environment")
    }
}
```

### Multibindings с @Binds

```kotlin
interface Command {
    val name: String
    fun execute(args: List<String>)
}

@MapKey
@Retention(AnnotationRetention.RUNTIME)
annotation class CommandKey(val value: String)

@Module
abstract class CommandsModule {

    @Binds
    @IntoMap
    @CommandKey("help")
    abstract fun bindHelpCommand(command: HelpCommand): Command

    @Binds
    @IntoMap
    @CommandKey("version")
    abstract fun bindVersionCommand(command: VersionCommand): Command

    @Binds
    @IntoMap
    @CommandKey("sync")
    abstract fun bindSyncCommand(command: SyncCommand): Command
}

class HelpCommand @Inject constructor() : Command {
    override val name = "help"
    override fun execute(args: List<String>) { /* ... */ }
}

class CommandProcessor @Inject constructor(
    private val commands: Map<String, @JvmSuppressWildcards Provider<Command>>
) {
    fun process(commandName: String, args: List<String>) {
        val command = commands[commandName]?.get()
            ?: throw UnknownCommandException(commandName)
        command.execute(args)
    }

    fun availableCommands(): Set<String> = commands.keys
}
```

### Multibindings в Разных Модулях

Главное преимущество - модули могут добавлять элементы независимо:

```kotlin
// :core модуль
@Module
class CoreAnalyticsModule {
    @Provides
    @IntoSet
    fun provideCoreTracker(): AnalyticsTracker = CoreTracker()
}

// :feature-profile модуль
@Module
class ProfileAnalyticsModule {
    @Provides
    @IntoSet
    fun provideProfileTracker(): AnalyticsTracker = ProfileTracker()
}

// :feature-payments модуль
@Module
class PaymentsAnalyticsModule {
    @Provides
    @IntoSet
    fun providePaymentsTracker(): AnalyticsTracker = PaymentsTracker()
}

// Все tracker-ы автоматически собираются в один Set
```

### Пустые Multibindings

Для объявления пустой коллекции (когда элементы опциональны):

```kotlin
@Module
abstract class PluginsModule {

    @Multibinds
    abstract fun providePlugins(): Set<Plugin>

    @Multibinds
    abstract fun providePluginMap(): Map<String, Plugin>
}

// Теперь можно инжектить даже если ни один плагин не добавлен
class PluginManager @Inject constructor(
    private val plugins: Set<@JvmSuppressWildcards Plugin> // Может быть пустым
)
```

---

## Answer (EN)

**Multibindings** allow collecting multiple dependencies into a collection (Set or Map) without explicitly listing all elements in one place. This is a powerful pattern for extensible systems.

### @IntoSet - Collecting into Set

Each `@IntoSet` method adds an element to the shared `Set`:

```kotlin
// Define multiple interceptors in different modules
@Module
class NetworkModule {

    @Provides
    @IntoSet
    fun provideLoggingInterceptor(): Interceptor {
        return HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }
    }

    @Provides
    @IntoSet
    fun provideAuthInterceptor(tokenProvider: TokenProvider): Interceptor {
        return AuthInterceptor(tokenProvider)
    }
}

@Module
class AnalyticsModule {

    @Provides
    @IntoSet
    fun provideAnalyticsInterceptor(analytics: Analytics): Interceptor {
        return AnalyticsInterceptor(analytics)
    }
}

// Inject the entire Set
@Module
class OkHttpModule {

    @Provides
    fun provideOkHttpClient(
        interceptors: Set<@JvmSuppressWildcards Interceptor>
    ): OkHttpClient {
        return OkHttpClient.Builder().apply {
            interceptors.forEach { addInterceptor(it) }
        }.build()
    }
}
```

### @ElementsIntoSet - Adding Multiple Elements

```kotlin
@Module
class ValidatorsModule {

    @Provides
    @ElementsIntoSet
    fun provideDefaultValidators(): Set<Validator> {
        return setOf(
            EmailValidator(),
            PhoneValidator(),
            PasswordValidator()
        )
    }

    @Provides
    @IntoSet
    fun provideCustomValidator(): Validator {
        return CustomValidator()
    }
}

// Usage
class FormValidator @Inject constructor(
    private val validators: Set<@JvmSuppressWildcards Validator>
) {
    fun validate(form: Form): List<ValidationError> {
        return validators.flatMap { it.validate(form) }
    }
}
```

### @IntoMap - Collecting into Map

`@IntoMap` requires a key annotation for each element:

```kotlin
// Built-in keys
@Module
class ViewModelModule {

    @Provides
    @IntoMap
    @ClassKey(HomeViewModel::class)
    fun provideHomeViewModel(
        repository: HomeRepository
    ): ViewModel {
        return HomeViewModel(repository)
    }

    @Provides
    @IntoMap
    @ClassKey(ProfileViewModel::class)
    fun provideProfileViewModel(
        userRepository: UserRepository
    ): ViewModel {
        return ProfileViewModel(userRepository)
    }
}

// Usage
class ViewModelFactory @Inject constructor(
    private val viewModels: Map<Class<*>, @JvmSuppressWildcards Provider<ViewModel>>
) : ViewModelProvider.Factory {

    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        val provider = viewModels[modelClass]
            ?: throw IllegalArgumentException("Unknown ViewModel: $modelClass")
        return provider.get() as T
    }
}
```

### Custom Map Keys

Creating custom key for Map:

```kotlin
// Define key annotation
@MapKey
@Retention(AnnotationRetention.RUNTIME)
annotation class ScreenKey(val value: KClass<out Screen>)

// Use in module
@Module
abstract class ScreenModule {

    @Binds
    @IntoMap
    @ScreenKey(HomeScreen::class)
    abstract fun bindHomeScreen(screen: HomeScreen): Screen

    @Binds
    @IntoMap
    @ScreenKey(ProfileScreen::class)
    abstract fun bindProfileScreen(screen: ProfileScreen): Screen
}

// Navigator uses Map
class Navigator @Inject constructor(
    private val screens: Map<KClass<out Screen>, @JvmSuppressWildcards Provider<Screen>>
) {
    fun navigateTo(screenClass: KClass<out Screen>) {
        val screen = screens[screenClass]?.get()
            ?: throw IllegalArgumentException("Unknown screen: $screenClass")
        screen.show()
    }
}
```

### String and Int Keys

```kotlin
@Module
class AnalyticsModule {

    @Provides
    @IntoMap
    @StringKey("firebase")
    fun provideFirebaseTracker(): AnalyticsTracker {
        return FirebaseTracker()
    }

    @Provides
    @IntoMap
    @StringKey("amplitude")
    fun provideAmplitudeTracker(): AnalyticsTracker {
        return AmplitudeTracker()
    }
}

class CompositeAnalytics @Inject constructor(
    private val trackers: Map<String, @JvmSuppressWildcards AnalyticsTracker>
) {
    fun track(event: AnalyticsEvent) {
        trackers.values.forEach { it.track(event) }
    }

    fun getTracker(name: String): AnalyticsTracker? {
        return trackers[name]
    }
}
```

### Enum Keys

```kotlin
enum class Environment {
    DEV, STAGING, PROD
}

@MapKey
@Retention(AnnotationRetention.RUNTIME)
annotation class EnvironmentKey(val value: Environment)

@Module
class ConfigModule {

    @Provides
    @IntoMap
    @EnvironmentKey(Environment.DEV)
    fun provideDevConfig(): AppConfig {
        return AppConfig(
            apiUrl = "https://dev.api.example.com",
            loggingEnabled = true
        )
    }

    @Provides
    @IntoMap
    @EnvironmentKey(Environment.PROD)
    fun provideProdConfig(): AppConfig {
        return AppConfig(
            apiUrl = "https://api.example.com",
            loggingEnabled = false
        )
    }
}

class ConfigProvider @Inject constructor(
    private val configs: Map<Environment, @JvmSuppressWildcards AppConfig>
) {
    fun getConfig(environment: Environment): AppConfig {
        return configs[environment]
            ?: throw IllegalStateException("No config for $environment")
    }
}
```

### Multibindings with @Binds

```kotlin
interface Command {
    val name: String
    fun execute(args: List<String>)
}

@MapKey
@Retention(AnnotationRetention.RUNTIME)
annotation class CommandKey(val value: String)

@Module
abstract class CommandsModule {

    @Binds
    @IntoMap
    @CommandKey("help")
    abstract fun bindHelpCommand(command: HelpCommand): Command

    @Binds
    @IntoMap
    @CommandKey("version")
    abstract fun bindVersionCommand(command: VersionCommand): Command

    @Binds
    @IntoMap
    @CommandKey("sync")
    abstract fun bindSyncCommand(command: SyncCommand): Command
}

class HelpCommand @Inject constructor() : Command {
    override val name = "help"
    override fun execute(args: List<String>) { /* ... */ }
}

class CommandProcessor @Inject constructor(
    private val commands: Map<String, @JvmSuppressWildcards Provider<Command>>
) {
    fun process(commandName: String, args: List<String>) {
        val command = commands[commandName]?.get()
            ?: throw UnknownCommandException(commandName)
        command.execute(args)
    }

    fun availableCommands(): Set<String> = commands.keys
}
```

### Multibindings Across Modules

Main advantage - modules can add elements independently:

```kotlin
// :core module
@Module
class CoreAnalyticsModule {
    @Provides
    @IntoSet
    fun provideCoreTracker(): AnalyticsTracker = CoreTracker()
}

// :feature-profile module
@Module
class ProfileAnalyticsModule {
    @Provides
    @IntoSet
    fun provideProfileTracker(): AnalyticsTracker = ProfileTracker()
}

// :feature-payments module
@Module
class PaymentsAnalyticsModule {
    @Provides
    @IntoSet
    fun providePaymentsTracker(): AnalyticsTracker = PaymentsTracker()
}

// All trackers automatically collected into one Set
```

### Empty Multibindings

To declare empty collection (when elements are optional):

```kotlin
@Module
abstract class PluginsModule {

    @Multibinds
    abstract fun providePlugins(): Set<Plugin>

    @Multibinds
    abstract fun providePluginMap(): Map<String, Plugin>
}

// Now can inject even if no plugins added
class PluginManager @Inject constructor(
    private val plugins: Set<@JvmSuppressWildcards Plugin> // Can be empty
)
```

---

## Дополнительные Вопросы (RU)

- Зачем нужен `@JvmSuppressWildcards` при инжекции коллекций?
- Как использовать multibindings с qualifiers?
- Можно ли комбинировать `@IntoSet` и scopes?

## Follow-ups

- Why is `@JvmSuppressWildcards` needed when injecting collections?
- How do you use multibindings with qualifiers?
- Can you combine `@IntoSet` with scopes?

## Ссылки (RU)

- [Dagger Multibindings](https://dagger.dev/dev-guide/multibindings.html)
- [Map Keys Documentation](https://dagger.dev/api/latest/dagger/MapKey.html)

## References

- [Dagger Multibindings](https://dagger.dev/dev-guide/multibindings.html)
- [Map Keys Documentation](https://dagger.dev/api/latest/dagger/MapKey.html)

## Связанные Вопросы (RU)

### Medium
- [[q-dagger-component-module--dagger--medium]]
- [[q-dagger-lazy-provider--dagger--medium]]

### Hard
- [[q-dagger-scopes-custom--dagger--hard]]
- [[q-dagger-subcomponents--dagger--hard]]
- [[q-dagger-generated-code--dagger--hard]]

## Related Questions

### Medium
- [[q-dagger-component-module--dagger--medium]]
- [[q-dagger-lazy-provider--dagger--medium]]

### Hard
- [[q-dagger-scopes-custom--dagger--hard]]
- [[q-dagger-subcomponents--dagger--hard]]
- [[q-dagger-generated-code--dagger--hard]]
