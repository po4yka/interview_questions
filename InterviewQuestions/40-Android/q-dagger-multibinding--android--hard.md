---
id: android-459
title: Dagger Multibinding / Multibinding в Dagger
aliases: [Dagger Multibinding, Multibinding в Dagger]
topic: android
subtopics: [architecture-modularization, di-hilt]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-dagger-component-dependencies--android--hard, q-dagger-custom-scopes--android--hard, q-dagger-framework-overview--android--hard, q-dagger-purpose--android--easy]
created: 2025-10-20
updated: 2025-11-02
tags: [android/architecture-modularization, android/di-hilt, dagger, dependency-injection, difficulty/hard, multibinding]
sources: []
---
# Вопрос (RU)
> Объясните Dagger/Hilt Multibinding (IntoSet, IntoMap, Multibinds). Как бы вы использовали это для реализации плагинной архитектуры или системы feature-модулей?

# Question (EN)
> Explain Dagger/Hilt Multibinding (IntoSet, IntoMap, Multibinds). How would you use it to implement a plugin architecture or feature module system?

---

## Ответ (RU)

Multibinding позволяет множественным модулям вносить элементы в общую коллекцию (`Set`/`Map`), инъецируемую как единая зависимость. Это основа для plugin-based и feature-modular архитектур, где каждый модуль независимо регистрирует свои компоненты без прямых зависимостей между модулями.

### Типы Multibinding

**`@IntoSet`** — добавление элемента в `Set`. Каждый модуль независимо добавляет свой элемент. Порядок не гарантирован, но можно сортировать по приоритету после инъекции.

```kotlin
@Module
abstract class AnalyticsModule {
    @Binds @IntoSet
    abstract fun plugin(impl: AnalyticsPlugin): AppPlugin
}

class PluginManager @Inject constructor(
    private val plugins: Set<@JvmSuppressWildcards AppPlugin>
)
```

**`@IntoMap`** — добавление в `Map` по ключу (через `@MapKey` аннотацию) для динамической маршрутизации. Ключи должны быть уникальными — дубликаты вызывают ошибку компиляции.

```kotlin
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

**`@Multibinds`** — декларация пустой коллекции (для опциональных зависимостей). Гарантирует, что коллекция доступна для инъекции, даже если ни один модуль не добавляет элементы. Полезно для опциональных плагинов.

```kotlin
@Module
abstract class BaseModule {
    @Multibinds
    abstract fun plugins(): Set<AppPlugin>  // Может быть пустой
}
```

### Plugin Architecture

Независимые модули регистрируют плагины через `@IntoSet`, менеджер инициализирует их с учетом приоритета. Это позволяет добавлять новые плагины без изменения кода менеджера — достаточно создать новый модуль с `@Binds @IntoSet`.

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

Динамическая навигация без прямых зависимостей между модулями. Каждый feature-модуль регистрирует свою точку входа через `@IntoMap`, центральный `Navigator` использует `Map` для маршрутизации. Это устраняет compile-time зависимости между feature-модулями.

```kotlin
// ❌ Жесткая зависимость — требует compile-time зависимости от LoginActivity
class MainActivity {
    fun navigate(screen: String) = when (screen) {
        "login" -> startActivity<LoginActivity>()
        else -> {}
    }
}

// ✅ Динамическая навигация — нет compile-time зависимостей
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

Разделение коллекций по назначению через квалификаторы (`@Qualifier`). Позволяет иметь несколько независимых `Set`/`Map` одного типа для разных целей (например, `@StartupPlugins` и `@BackgroundPlugins`).

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

Multibinding allows multiple modules to contribute elements to a shared collection (`Set`/`Map`) injected as a single dependency. This is the foundation for plugin-based and feature-modular architectures, where each module independently registers its components without direct dependencies between modules.

### Multibinding Types

**`@IntoSet`** — adds element to `Set`. Each module independently contributes its element. Order is not guaranteed, but can be sorted by priority after injection.

```kotlin
@Module
abstract class AnalyticsModule {
    @Binds @IntoSet
    abstract fun plugin(impl: AnalyticsPlugin): AppPlugin
}

class PluginManager @Inject constructor(
    private val plugins: Set<@JvmSuppressWildcards AppPlugin>
)
```

**`@IntoMap`** — adds to `Map` by key (via `@MapKey` annotation) for dynamic routing. Keys must be unique — duplicates cause compilation error.

```kotlin
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

**`@Multibinds`** — declares empty collection (for optional dependencies). Ensures collection is available for injection even if no modules contribute elements. Useful for optional plugins.

```kotlin
@Module
abstract class BaseModule {
    @Multibinds
    abstract fun plugins(): Set<AppPlugin>  // Can be empty
}
```

### Plugin Architecture

Independent modules register plugins via `@IntoSet`, manager initializes them with priority ordering. This allows adding new plugins without modifying manager code — just create a new module with `@Binds @IntoSet`.

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

Dynamic navigation without direct dependencies between modules. Each feature module registers its entry point via `@IntoMap`, central `Navigator` uses `Map` for routing. This eliminates compile-time dependencies between feature modules.

```kotlin
// ❌ Tight coupling — requires compile-time dependency on LoginActivity
class MainActivity {
    fun navigate(screen: String) = when (screen) {
        "login" -> startActivity<LoginActivity>()
        else -> {}
    }
}

// ✅ Dynamic navigation — no compile-time dependencies
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

Separate collections by purpose using qualifiers (`@Qualifier`). Allows multiple independent `Set`/`Map` of same type for different purposes (e.g., `@StartupPlugins` and `@BackgroundPlugins`).

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

- How do you handle ordering/priority between multibinding contributions?
- Can you combine `@IntoSet` with qualifiers for separate collections?
- What happens if multibinding `Map` has duplicate keys?
- How do you test classes that depend on multibinding collections?
- What's the performance impact of large multibinding collections at compile-time?

## References

- [[c-dagger]] — Dagger fundamentals
- [[c-hilt]] — Hilt DI framework
- [[c-dependency-injection]] — DI principles
- [Dagger Multibindings Guide](https://dagger.dev/dev-guide/multibindings.html)

## Related Questions

### Prerequisites (Easier)
- [[q-dagger-inject-annotation--android--easy]] — Basic injection
- [[q-dagger-main-elements--android--medium]] — Module binding methods
- Understanding of `@Binds` and `@Provides`

### Related (Same Level)
- [[q-dagger-custom-scopes--android--hard]] — Custom scope creation
- [[q-dagger-component-dependencies--android--hard]] — Component relationships

### Advanced (Harder)
- [[q-dagger-framework-overview--android--hard]] — Complete Dagger architecture
- Large-scale modularization patterns
