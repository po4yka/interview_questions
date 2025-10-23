---
id: 20251020-200000
title: Dagger Multibinding / Multibinding в Dagger
aliases:
- Dagger Multibinding
- Multibinding в Dagger
topic: android
subtopics:
- dependency-injection
- architecture-patterns
question_kind: android
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- q-dagger-framework-overview--android--hard
- q-dagger-custom-scopes--di--hard
- q-dagger-component-dependencies--di--hard
created: 2025-10-20
updated: 2025-10-20
tags:
- android/dependency-injection
- android/architecture-patterns
- dagger
- hilt
- multibinding
- plugin-architecture
- difficulty/hard
source: https://dagger.dev/api/latest/dagger/Multibinds.html
source_note: Dagger Multibinds API documentation
---# Вопрос (RU)
> Объясните Dagger/Hilt Multibinding (IntoSet, IntoMap, Multibinds). Как бы вы использовали это для реализации плагинной архитектуры или системы feature-модулей?

# Question (EN)
> Explain Dagger/Hilt Multibinding (IntoSet, IntoMap, Multibinds). How would you use it to implement a plugin architecture or feature module system?

## Ответ (RU)

Multibinding в Dagger/Hilt позволяет связывать множественные значения в коллекцию (Set или Map), которая может быть внедрена как единая зависимость. Это критически важно для плагинных архитектур, feature-модулей и расширяемых систем.

### Теория: Принципы Multibinding

**Основные концепции:**
- **Коллективная инъекция** - множественные реализации как единая зависимость
- **Модульная архитектура** - добавление функций без изменения существующего кода
- **Плагинная система** - динамическое расширение функциональности
- **Feature-модули** - изолированные компоненты приложения

**Типы Multibinding:**
- `@IntoSet` - добавляет элемент в Set
- `@ElementsIntoSet` - добавляет несколько элементов в Set
- `@IntoMap` - добавляет запись в Map с ключом
- `@Multibinds` - объявляет пустую коллекцию для инъекции

### 1. @IntoSet - Коллекция плагинов

**Создание коллекции плагинов:**

```kotlin
// Интерфейс плагина
interface Plugin {
    val name: String
    fun initialize(context: Context)
}

// Реализации плагинов
class AnalyticsPlugin @Inject constructor() : Plugin {
    override val name = "Analytics"
    override fun initialize(context: Context) {
        // Инициализация аналитики
    }
}

class CrashReportingPlugin @Inject constructor() : Plugin {
    override val name = "CrashReporting"
    override fun initialize(context: Context) {
        // Инициализация crash reporting
    }
}
```

**Модуль с @IntoSet:**

```kotlin
@Module
abstract class PluginModule {
    @Binds
    @IntoSet
    abstract fun bindAnalyticsPlugin(plugin: AnalyticsPlugin): Plugin

    @Binds
    @IntoSet
    abstract fun bindCrashReportingPlugin(plugin: CrashReportingPlugin): Plugin
}
```

**Использование коллекции:**

```kotlin
class PluginManager @Inject constructor(
    private val plugins: Set<Plugin>
) {
    fun initializeAll(context: Context) {
        plugins.forEach { plugin ->
            plugin.initialize(context)
        }
    }
}
```

### 2. @IntoMap - Ключевые коллекции

**Создание Map с ключами:**

```kotlin
// Тип ключа для Map
@MapKey
annotation class FeatureKey(val value: String)

// Интерфейс feature
interface Feature {
    fun execute()
}

// Реализации features
class LoginFeature @Inject constructor() : Feature {
    override fun execute() {
        // Логика входа
    }
}

class PaymentFeature @Inject constructor() : Feature {
    override fun execute() {
        // Логика платежей
    }
}
```

**Модуль с @IntoMap:**

```kotlin
@Module
abstract class FeatureModule {
    @Binds
    @IntoMap
    @FeatureKey("login")
    abstract fun bindLoginFeature(feature: LoginFeature): Feature

    @Binds
    @IntoMap
    @FeatureKey("payment")
    abstract fun bindPaymentFeature(feature: PaymentFeature): Feature
}
```

**Использование Map:**

```kotlin
class FeatureRouter @Inject constructor(
    private val features: Map<String, @JvmSuppressWildcards Feature>
) {
    fun executeFeature(key: String) {
        features[key]?.execute()
    }
}
```

### 3. @ElementsIntoSet - Множественные элементы

**Добавление нескольких элементов:**

```kotlin
@Module
object NotificationModule {
    @Provides
    @ElementsIntoSet
    fun provideNotificationChannels(): Set<NotificationChannel> {
        return setOf(
            NotificationChannel("general", "General", NotificationManager.IMPORTANCE_DEFAULT),
            NotificationChannel("urgent", "Urgent", NotificationManager.IMPORTANCE_HIGH)
        )
    }
}
```

### 4. @Multibinds - Пустые коллекции

**Объявление пустых коллекций:**

```kotlin
@Module
abstract class EmptyCollectionModule {
    @Multibinds
    abstract fun emptyPluginSet(): Set<Plugin>

    @Multibinds
    abstract fun emptyFeatureMap(): Map<String, @JvmSuppressWildcards Feature>
}
```

### Плагинная архитектура

**Полная реализация плагинной системы:**

```kotlin
// Plugin Registry
class PluginRegistry @Inject constructor(
    private val plugins: Set<Plugin>
) {
    private val pluginMap = plugins.associateBy { it.name }

    fun getPlugin(name: String): Plugin? = pluginMap[name]
    fun getAllPlugins(): Set<Plugin> = plugins
}

// Feature Module System
class FeatureModuleManager @Inject constructor(
    private val features: Map<String, @JvmSuppressWildcards Feature>
) {
    fun executeFeature(featureName: String) {
        features[featureName]?.execute()
    }

    fun getAvailableFeatures(): Set<String> = features.keys
}
```

### Hilt интеграция

**Автоматическое создание компонентов:**

```kotlin
@HiltAndroidApp
class MyApplication : Application() {
    @Inject
    lateinit var pluginRegistry: PluginRegistry

    @Inject
    lateinit var featureManager: FeatureModuleManager
}
```

## Answer (EN)

Multibinding in Dagger/Hilt allows you to bind multiple values into a collection (Set or Map) that can be injected as a single dependency. This is critically important for plugin architectures, feature modules, and extensible systems.

### Theory: Multibinding Principles

**Core Concepts:**
- **Collective Injection** - multiple implementations as single dependency
- **Modular Architecture** - adding functionality without modifying existing code
- **Plugin System** - dynamic functional extension
- **Feature Modules** - isolated application components

**Multibinding Types:**
- `@IntoSet` - adds element to Set
- `@ElementsIntoSet` - adds multiple elements to Set
- `@IntoMap` - adds entry to Map with key
- `@Multibinds` - declares empty collection for injection

### 1. @IntoSet - Plugin Collections

**Creating plugin collections:**

```kotlin
// Plugin interface
interface Plugin {
    val name: String
    fun initialize(context: Context)
}

// Plugin implementations
class AnalyticsPlugin @Inject constructor() : Plugin {
    override val name = "Analytics"
    override fun initialize(context: Context) {
        // Initialize analytics
    }
}

class CrashReportingPlugin @Inject constructor() : Plugin {
    override val name = "CrashReporting"
    override fun initialize(context: Context) {
        // Initialize crash reporting
    }
}
```

**Module with @IntoSet:**

```kotlin
@Module
abstract class PluginModule {
    @Binds
    @IntoSet
    abstract fun bindAnalyticsPlugin(plugin: AnalyticsPlugin): Plugin

    @Binds
    @IntoSet
    abstract fun bindCrashReportingPlugin(plugin: CrashReportingPlugin): Plugin
}
```

**Using collections:**

```kotlin
class PluginManager @Inject constructor(
    private val plugins: Set<Plugin>
) {
    fun initializeAll(context: Context) {
        plugins.forEach { plugin ->
            plugin.initialize(context)
        }
    }
}
```

### 2. @IntoMap - Keyed Collections

**Creating Map with keys:**

```kotlin
// Key type for Map
@MapKey
annotation class FeatureKey(val value: String)

// Feature interface
interface Feature {
    fun execute()
}

// Feature implementations
class LoginFeature @Inject constructor() : Feature {
    override fun execute() {
        // Login logic
    }
}

class PaymentFeature @Inject constructor() : Feature {
    override fun execute() {
        // Payment logic
    }
}
```

**Module with @IntoMap:**

```kotlin
@Module
abstract class FeatureModule {
    @Binds
    @IntoMap
    @FeatureKey("login")
    abstract fun bindLoginFeature(feature: LoginFeature): Feature

    @Binds
    @IntoMap
    @FeatureKey("payment")
    abstract fun bindPaymentFeature(feature: PaymentFeature): Feature
}
```

**Using Map:**

```kotlin
class FeatureRouter @Inject constructor(
    private val features: Map<String, @JvmSuppressWildcards Feature>
) {
    fun executeFeature(key: String) {
        features[key]?.execute()
    }
}
```

### 3. @ElementsIntoSet - Multiple Elements

**Adding multiple elements:**

```kotlin
@Module
object NotificationModule {
    @Provides
    @ElementsIntoSet
    fun provideNotificationChannels(): Set<NotificationChannel> {
        return setOf(
            NotificationChannel("general", "General", NotificationManager.IMPORTANCE_DEFAULT),
            NotificationChannel("urgent", "Urgent", NotificationManager.IMPORTANCE_HIGH)
        )
    }
}
```

### 4. @Multibinds - Empty Collections

**Declaring empty collections:**

```kotlin
@Module
abstract class EmptyCollectionModule {
    @Multibinds
    abstract fun emptyPluginSet(): Set<Plugin>

    @Multibinds
    abstract fun emptyFeatureMap(): Map<String, @JvmSuppressWildcards Feature>
}
```

### Plugin Architecture

**Complete plugin system implementation:**

```kotlin
// Plugin Registry
class PluginRegistry @Inject constructor(
    private val plugins: Set<Plugin>
) {
    private val pluginMap = plugins.associateBy { it.name }

    fun getPlugin(name: String): Plugin? = pluginMap[name]
    fun getAllPlugins(): Set<Plugin> = plugins
}

// Feature Module System
class FeatureModuleManager @Inject constructor(
    private val features: Map<String, @JvmSuppressWildcards Feature>
) {
    fun executeFeature(featureName: String) {
        features[featureName]?.execute()
    }

    fun getAvailableFeatures(): Set<String> = features.keys
}
```

### Hilt Integration

**Automatic component creation:**

```kotlin
@HiltAndroidApp
class MyApplication : Application() {
    @Inject
    lateinit var pluginRegistry: PluginRegistry

    @Inject
    lateinit var featureManager: FeatureModuleManager
}
```

## Follow-ups

- How do you handle plugin lifecycle management with multibinding?
- What are the performance implications of large multibinding collections?
- How can you implement conditional plugin loading with multibinding?

## Related Questions

### Prerequisites (Easier)
- [[q-dagger-inject-annotation--android--easy]]

### Related (Same Level)
- [[q-dagger-field-injection--android--medium]]

### Advanced (Harder)
- [[q-dagger-framework-overview--android--hard]]
- [[q-dagger-custom-scopes--android--hard]]
- [[q-dagger-component-dependencies--android--hard]]
