---
id: 20251020-200000
title: Dagger Multibinding / Multibinding в Dagger
aliases: ["Dagger Multibinding", "Multibinding в Dagger"]
topic: android
subtopics: [di-hilt, architecture-modularization]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related:
  - q-dagger-component-dependencies--android--hard
  - q-dagger-custom-scopes--android--hard
  - q-dagger-framework-overview--android--hard
created: 2025-10-20
updated: 2025-10-29
tags: [android/di-hilt, android/architecture-modularization, dagger, dependency-injection, multibinding, difficulty/hard]
sources: []
---

# Вопрос (RU)
> Объясните Dagger/Hilt Multibinding (IntoSet, IntoMap, Multibinds). Как бы вы использовали это для реализации плагинной архитектуры или системы feature-модулей?

# Question (EN)
> Explain Dagger/Hilt Multibinding (IntoSet, IntoMap, Multibinds). How would you use it to implement a plugin architecture or feature module system?

---

## Ответ (RU)

Multibinding позволяет множественным модулям вносить элементы в общую коллекцию (Set/Map), инъецируемую как единая зависимость. Основа для plugin-based и feature-modular архитектур.

### Типы Multibinding

**@IntoSet** - добавление элемента в Set:

```kotlin
// ✅ Правильно: каждый модуль добавляет плагин
@Module
abstract class AnalyticsModule {
    @Binds @IntoSet
    abstract fun plugin(impl: AnalyticsPlugin): AppPlugin
}

@Module
abstract class LoggingModule {
    @Binds @IntoSet
    abstract fun plugin(impl: LoggingPlugin): AppPlugin
}

// Использование: получаем все плагины
class PluginManager @Inject constructor(
    private val plugins: Set<@JvmSuppressWildcards AppPlugin>
)
```

**@IntoMap** - добавление в Map по ключу:

```kotlin
// ✅ Правильно: feature registry с ключами
@MapKey
annotation class FeatureKey(val value: String)

@Module
abstract class FeatureModule {
    @Binds @IntoMap
    @FeatureKey("login")
    abstract fun login(impl: LoginFeature): Feature

    @Binds @IntoMap
    @FeatureKey("payment")
    abstract fun payment(impl: PaymentFeature): Feature
}

class FeatureRouter @Inject constructor(
    private val features: Map<String, @JvmSuppressWildcards Feature>
) {
    fun route(key: String) = features[key]?.execute()
}
```

**@ElementsIntoSet** - добавление нескольких элементов:

```kotlin
// ✅ Правильно: bulk добавление
@Module
object ConfigModule {
    @Provides @ElementsIntoSet
    fun providers(): Set<ConfigProvider> = setOf(
        RemoteConfig(),
        LocalConfig(),
        DefaultConfig()
    )
}
```

**@Multibinds** - декларация пустой коллекции:

```kotlin
// ✅ Правильно: опциональные коллекции
@Module
abstract class BaseModule {
    @Multibinds
    abstract fun plugins(): Set<AppPlugin>  // Может быть пустой
}
```

### Plugin Architecture

```kotlin
// Интерфейс плагина
interface AppPlugin {
    val priority: Int
    fun initialize(context: Context)
}

// Модули добавляют плагины независимо
@Module
@InstallIn(SingletonComponent::class)
abstract class AnalyticsModule {
    @Binds @IntoSet
    abstract fun plugin(impl: AnalyticsPlugin): AppPlugin
}

@Module
@InstallIn(SingletonComponent::class)
abstract class CrashModule {
    @Binds @IntoSet
    abstract fun plugin(impl: CrashPlugin): AppPlugin
}

// Менеджер инициализирует все плагины
@Singleton
class PluginManager @Inject constructor(
    private val plugins: Set<@JvmSuppressWildcards AppPlugin>
) {
    fun initialize(context: Context) {
        plugins.sortedBy { it.priority }
            .forEach { it.initialize(context) }
    }
}
```

### Feature Module System

```kotlin
// ❌ Неправильно: жесткая зависимость
class MainActivity {
    fun navigate(screen: String) {
        when (screen) {
            "login" -> startActivity<LoginActivity>()
            "payment" -> startActivity<PaymentActivity>()
        }
    }
}

// ✅ Правильно: динамическая навигация через Map
@MapKey
@Retention(AnnotationRetention.RUNTIME)
annotation class FeatureKey(val value: String)

interface FeatureEntry {
    fun createIntent(context: Context): Intent
}

@Module
@InstallIn(SingletonComponent::class)
abstract class LoginModule {
    @Binds @IntoMap
    @FeatureKey("login")
    abstract fun entry(impl: LoginFeatureEntry): FeatureEntry
}

@Module
@InstallIn(SingletonComponent::class)
abstract class PaymentModule {
    @Binds @IntoMap
    @FeatureKey("payment")
    abstract fun entry(impl: PaymentFeatureEntry): FeatureEntry
}

class Navigator @Inject constructor(
    private val entries: Map<String, @JvmSuppressWildcards FeatureEntry>
) {
    fun navigate(context: Context, feature: String) {
        entries[feature]?.createIntent(context)?.let(context::startActivity)
    }
}
```

### Advanced: Qualified Multibindings

```kotlin
// Разные коллекции для разных целей
@Qualifier
@Retention(AnnotationRetention.RUNTIME)
annotation class StartupPlugins

@Qualifier
@Retention(AnnotationRetention.RUNTIME)
annotation class BackgroundPlugins

@Module
@InstallIn(SingletonComponent::class)
abstract class PluginModule {
    @Binds @IntoSet @StartupPlugins
    abstract fun startup(impl: AnalyticsPlugin): AppPlugin

    @Binds @IntoSet @BackgroundPlugins
    abstract fun background(impl: SyncPlugin): AppPlugin
}

class App : Application() {
    @Inject @StartupPlugins
    lateinit var startupPlugins: Set<@JvmSuppressWildcards AppPlugin>
}
```

## Answer (EN)

Multibinding allows multiple modules to contribute elements to a shared collection (Set/Map) injected as a single dependency. Foundation for plugin-based and feature-modular architectures.

### Multibinding Types

**@IntoSet** - adds element to Set:

```kotlin
// ✅ Correct: each module contributes plugin
@Module
abstract class AnalyticsModule {
    @Binds @IntoSet
    abstract fun plugin(impl: AnalyticsPlugin): AppPlugin
}

@Module
abstract class LoggingModule {
    @Binds @IntoSet
    abstract fun plugin(impl: LoggingPlugin): AppPlugin
}

// Usage: receive all plugins
class PluginManager @Inject constructor(
    private val plugins: Set<@JvmSuppressWildcards AppPlugin>
)
```

**@IntoMap** - adds to Map by key:

```kotlin
// ✅ Correct: feature registry with keys
@MapKey
annotation class FeatureKey(val value: String)

@Module
abstract class FeatureModule {
    @Binds @IntoMap
    @FeatureKey("login")
    abstract fun login(impl: LoginFeature): Feature

    @Binds @IntoMap
    @FeatureKey("payment")
    abstract fun payment(impl: PaymentFeature): Feature
}

class FeatureRouter @Inject constructor(
    private val features: Map<String, @JvmSuppressWildcards Feature>
) {
    fun route(key: String) = features[key]?.execute()
}
```

**@ElementsIntoSet** - adds multiple elements:

```kotlin
// ✅ Correct: bulk addition
@Module
object ConfigModule {
    @Provides @ElementsIntoSet
    fun providers(): Set<ConfigProvider> = setOf(
        RemoteConfig(),
        LocalConfig(),
        DefaultConfig()
    )
}
```

**@Multibinds** - declares empty collection:

```kotlin
// ✅ Correct: optional collections
@Module
abstract class BaseModule {
    @Multibinds
    abstract fun plugins(): Set<AppPlugin>  // Can be empty
}
```

### Plugin Architecture

```kotlin
// Plugin interface
interface AppPlugin {
    val priority: Int
    fun initialize(context: Context)
}

// Modules add plugins independently
@Module
@InstallIn(SingletonComponent::class)
abstract class AnalyticsModule {
    @Binds @IntoSet
    abstract fun plugin(impl: AnalyticsPlugin): AppPlugin
}

@Module
@InstallIn(SingletonComponent::class)
abstract class CrashModule {
    @Binds @IntoSet
    abstract fun plugin(impl: CrashPlugin): AppPlugin
}

// Manager initializes all plugins
@Singleton
class PluginManager @Inject constructor(
    private val plugins: Set<@JvmSuppressWildcards AppPlugin>
) {
    fun initialize(context: Context) {
        plugins.sortedBy { it.priority }
            .forEach { it.initialize(context) }
    }
}
```

### Feature Module System

```kotlin
// ❌ Wrong: tight coupling
class MainActivity {
    fun navigate(screen: String) {
        when (screen) {
            "login" -> startActivity<LoginActivity>()
            "payment" -> startActivity<PaymentActivity>()
        }
    }
}

// ✅ Correct: dynamic navigation via Map
@MapKey
@Retention(AnnotationRetention.RUNTIME)
annotation class FeatureKey(val value: String)

interface FeatureEntry {
    fun createIntent(context: Context): Intent
}

@Module
@InstallIn(SingletonComponent::class)
abstract class LoginModule {
    @Binds @IntoMap
    @FeatureKey("login")
    abstract fun entry(impl: LoginFeatureEntry): FeatureEntry
}

@Module
@InstallIn(SingletonComponent::class)
abstract class PaymentModule {
    @Binds @IntoMap
    @FeatureKey("payment")
    abstract fun entry(impl: PaymentFeatureEntry): FeatureEntry
}

class Navigator @Inject constructor(
    private val entries: Map<String, @JvmSuppressWildcards FeatureEntry>
) {
    fun navigate(context: Context, feature: String) {
        entries[feature]?.createIntent(context)?.let(context::startActivity)
    }
}
```

### Advanced: Qualified Multibindings

```kotlin
// Different collections for different purposes
@Qualifier
@Retention(AnnotationRetention.RUNTIME)
annotation class StartupPlugins

@Qualifier
@Retention(AnnotationRetention.RUNTIME)
annotation class BackgroundPlugins

@Module
@InstallIn(SingletonComponent::class)
abstract class PluginModule {
    @Binds @IntoSet @StartupPlugins
    abstract fun startup(impl: AnalyticsPlugin): AppPlugin

    @Binds @IntoSet @BackgroundPlugins
    abstract fun background(impl: SyncPlugin): AppPlugin
}

class App : Application() {
    @Inject @StartupPlugins
    lateinit var startupPlugins: Set<@JvmSuppressWildcards AppPlugin>
}
```

---

## Follow-ups

1. How do you handle ordering/priority between multibinding contributions?
2. Can you combine @IntoSet with qualifiers for separate collections?
3. What happens if multibinding Map has duplicate keys?
4. How do you test classes that depend on multibinding collections?
5. What's the performance impact of large multibinding collections at compile-time?

## References

- [[c-dagger]] - Dagger fundamentals
- [[c-hilt]] - Hilt DI framework
- [[c-dependency-injection]] - DI principles
- https://dagger.dev/dev-guide/multibindings.html - Official multibinding guide

## Related Questions

### Prerequisites (Easier)
- [[q-dagger-inject-annotation--android--easy]] - Basic injection
- [[q-dagger-provides-binds--android--medium]] - Module binding methods

### Related (Same Level)
- [[q-dagger-custom-scopes--android--hard]] - Custom scope creation
- [[q-dagger-component-dependencies--android--hard]] - Component relationships

### Advanced (Harder)
- [[q-dagger-framework-overview--android--hard]] - Complete Dagger architecture
