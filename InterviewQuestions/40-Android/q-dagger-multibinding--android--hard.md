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
updated: 2025-10-30
tags: [android/di-hilt, android/architecture-modularization, dagger, dependency-injection, multibinding, difficulty/hard]
sources: []
date created: Thursday, October 30th 2025, 12:03:46 pm
date modified: Thursday, October 30th 2025, 12:47:29 pm
---

# Вопрос (RU)
> Объясните Dagger/Hilt Multibinding (IntoSet, IntoMap, Multibinds). Как бы вы использовали это для реализации плагинной архитектуры или системы feature-модулей?

# Question (EN)
> Explain Dagger/Hilt Multibinding (IntoSet, IntoMap, Multibinds). How would you use it to implement a plugin architecture or feature module system?

---

## Ответ (RU)

Multibinding позволяет множественным модулям вносить элементы в общую коллекцию (Set/Map), инъецируемую как единая зависимость. Основа для plugin-based и feature-modular архитектур.

### Типы Multibinding

**@IntoSet** - добавление элемента в Set. Каждый модуль независимо добавляет свой элемент:

```kotlin
// ✅ Правильно: каждый модуль добавляет плагин
@Module
abstract class AnalyticsModule {
    @Binds @IntoSet
    abstract fun plugin(impl: AnalyticsPlugin): AppPlugin
}

class PluginManager @Inject constructor(
    private val plugins: Set<@JvmSuppressWildcards AppPlugin>
)
```

**@IntoMap** - добавление в Map по ключу для динамической маршрутизации:

```kotlin
// ✅ Правильно: feature registry с ключами
@MapKey
annotation class FeatureKey(val value: String)

@Module
abstract class FeatureModule {
    @Binds @IntoMap @FeatureKey("login")
    abstract fun login(impl: LoginFeature): Feature
}

class Router @Inject constructor(
    private val features: Map<String, @JvmSuppressWildcards Feature>
)
```

**@Multibinds** - декларация пустой коллекции (для опциональных зависимостей):

```kotlin
@Module
abstract class BaseModule {
    @Multibinds
    abstract fun plugins(): Set<AppPlugin>  // Может быть пустой
}
```

### Plugin Architecture

Независимые модули регистрируют плагины, менеджер инициализирует их с учетом приоритета:

```kotlin
interface AppPlugin {
    val priority: Int
    fun initialize(context: Context)
}

@Module
@InstallIn(SingletonComponent::class)
abstract class AnalyticsModule {
    @Binds @IntoSet
    abstract fun plugin(impl: AnalyticsPlugin): AppPlugin
}

@Singleton
class PluginManager @Inject constructor(
    private val plugins: Set<@JvmSuppressWildcards AppPlugin>
) {
    fun initialize(context: Context) {
        plugins.sortedBy { it.priority }.forEach { it.initialize(context) }
    }
}
```

### Feature Module System

Динамическая навигация без прямых зависимостей между модулями:

```kotlin
// ❌ Неправильно: жесткая зависимость
class MainActivity {
    fun navigate(screen: String) = when (screen) {
        "login" -> startActivity<LoginActivity>()  // Прямая зависимость
        else -> {}
    }
}

// ✅ Правильно: динамическая навигация через Map
@MapKey
annotation class FeatureKey(val value: String)

interface FeatureEntry {
    fun createIntent(context: Context): Intent
}

@Module
@InstallIn(SingletonComponent::class)
abstract class LoginModule {
    @Binds @IntoMap @FeatureKey("login")
    abstract fun entry(impl: LoginFeatureEntry): FeatureEntry
}

class Navigator @Inject constructor(
    private val entries: Map<String, @JvmSuppressWildcards FeatureEntry>
) {
    fun navigate(context: Context, feature: String) {
        entries[feature]?.createIntent(context)?.let(context::startActivity)
    }
}
```

### Qualified Multibindings

Разделение коллекций по назначению через квалификаторы:

```kotlin
@Qualifier
annotation class StartupPlugins

@Qualifier
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

**@IntoSet** - adds element to Set. Each module independently contributes its element:

```kotlin
// ✅ Correct: each module contributes plugin
@Module
abstract class AnalyticsModule {
    @Binds @IntoSet
    abstract fun plugin(impl: AnalyticsPlugin): AppPlugin
}

class PluginManager @Inject constructor(
    private val plugins: Set<@JvmSuppressWildcards AppPlugin>
)
```

**@IntoMap** - adds to Map by key for dynamic routing:

```kotlin
// ✅ Correct: feature registry with keys
@MapKey
annotation class FeatureKey(val value: String)

@Module
abstract class FeatureModule {
    @Binds @IntoMap @FeatureKey("login")
    abstract fun login(impl: LoginFeature): Feature
}

class Router @Inject constructor(
    private val features: Map<String, @JvmSuppressWildcards Feature>
)
```

**@Multibinds** - declares empty collection (for optional dependencies):

```kotlin
@Module
abstract class BaseModule {
    @Multibinds
    abstract fun plugins(): Set<AppPlugin>  // Can be empty
}
```

### Plugin Architecture

Independent modules register plugins, manager initializes them with priority ordering:

```kotlin
interface AppPlugin {
    val priority: Int
    fun initialize(context: Context)
}

@Module
@InstallIn(SingletonComponent::class)
abstract class AnalyticsModule {
    @Binds @IntoSet
    abstract fun plugin(impl: AnalyticsPlugin): AppPlugin
}

@Singleton
class PluginManager @Inject constructor(
    private val plugins: Set<@JvmSuppressWildcards AppPlugin>
) {
    fun initialize(context: Context) {
        plugins.sortedBy { it.priority }.forEach { it.initialize(context) }
    }
}
```

### Feature Module System

Dynamic navigation without direct dependencies between modules:

```kotlin
// ❌ Wrong: tight coupling
class MainActivity {
    fun navigate(screen: String) = when (screen) {
        "login" -> startActivity<LoginActivity>()  // Direct dependency
        else -> {}
    }
}

// ✅ Correct: dynamic navigation via Map
@MapKey
annotation class FeatureKey(val value: String)

interface FeatureEntry {
    fun createIntent(context: Context): Intent
}

@Module
@InstallIn(SingletonComponent::class)
abstract class LoginModule {
    @Binds @IntoMap @FeatureKey("login")
    abstract fun entry(impl: LoginFeatureEntry): FeatureEntry
}

class Navigator @Inject constructor(
    private val entries: Map<String, @JvmSuppressWildcards FeatureEntry>
) {
    fun navigate(context: Context, feature: String) {
        entries[feature]?.createIntent(context)?.let(context::startActivity)
    }
}
```

### Qualified Multibindings

Separate collections by purpose using qualifiers:

```kotlin
@Qualifier
annotation class StartupPlugins

@Qualifier
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
- [[q-dagger-main-elements--android--medium]] - Module binding methods

### Related (Same Level)
- [[q-dagger-custom-scopes--android--hard]] - Custom scope creation
- [[q-dagger-component-dependencies--android--hard]] - Component relationships

### Advanced (Harder)
- [[q-dagger-framework-overview--android--hard]] - Complete Dagger architecture
