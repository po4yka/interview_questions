---
tags:
  - android
  - dependency-injection
  - dagger
  - hilt
  - advanced
difficulty: hard
status: draft
related:
  - q-hilt-entry-points--di--medium
  - q-hilt-assisted-injection--di--medium
  - q-dagger-custom-scopes--di--hard
created: 2025-10-11
---

# Question (EN)
Explain Dagger/Hilt Multibinding (IntoSet, IntoMap, Multibinds). How would you use it to implement a plugin architecture or feature module system?

## Answer (EN)
### Overview

**Multibinding** in Dagger/Hilt allows you to bind multiple values into a collection (Set or Map) that can be injected as a single dependency. This is incredibly useful for plugin architectures, feature modules, and extensible systems where you want to add functionality without modifying existing code.

### Types of Multibinding

1. **@IntoSet** - Contributes a single element to a Set
2. **@ElementsIntoSet** - Contributes multiple elements to a Set
3. **@IntoMap** - Contributes a single entry to a Map
4. **@Multibinds** - Declares an empty collection that can be injected

### Basic @IntoSet Example

```kotlin
// Interface for plugins
interface Plugin {
    val name: String
    fun initialize(context: Context)
}

// Plugin implementations
class AnalyticsPlugin @Inject constructor() : Plugin {
    override val name = "Analytics"
    override fun initialize(context: Context) {
        println("Initializing Analytics Plugin")
    }
}

class CrashReportingPlugin @Inject constructor() : Plugin {
    override val name = "CrashReporting"
    override fun initialize(context: Context) {
        println("Initializing Crash Reporting Plugin")
    }
}

class PerformancePlugin @Inject constructor() : Plugin {
    override val name = "Performance"
    override fun initialize(context: Context) {
        println("Initializing Performance Plugin")
    }
}

// Module providing plugins
@Module
@InstallIn(SingletonComponent::class)
abstract class PluginModule {

    @Binds
    @IntoSet
    abstract fun bindAnalyticsPlugin(plugin: AnalyticsPlugin): Plugin

    @Binds
    @IntoSet
    abstract fun bindCrashReportingPlugin(plugin: CrashReportingPlugin): Plugin

    @Binds
    @IntoSet
    abstract fun bindPerformancePlugin(plugin: PerformancePlugin): Plugin
}

// Usage - inject the entire set
@Singleton
class PluginManager @Inject constructor(
    private val plugins: Set<@JvmSuppressWildcards Plugin>
) {

    fun initializeAll(context: Context) {
        plugins.forEach { plugin ->
            println("Initializing plugin: ${plugin.name}")
            plugin.initialize(context)
        }
    }

    fun getPlugin(name: String): Plugin? {
        return plugins.find { it.name == name }
    }
}
```

**Output:**
```
Initializing plugin: Analytics
Initializing Analytics Plugin
Initializing plugin: CrashReporting
Initializing Crash Reporting Plugin
Initializing plugin: Performance
Initializing Performance Plugin
```

### @IntoMap with Custom Keys

Maps require a key annotation. Dagger provides built-in keys, or you can create custom ones:

```kotlin
// Built-in key annotations:
// @StringKey, @IntKey, @LongKey, @ClassKey

// Custom key annotation
@MapKey
annotation class FeatureKey(val value: String)

// Feature interface
interface Feature {
    val id: String
    val displayName: String
    fun isEnabled(): Boolean
    fun open(context: Context)
}

// Feature implementations
class ProfileFeature @Inject constructor() : Feature {
    override val id = "profile"
    override val displayName = "User Profile"
    override fun isEnabled() = true
    override fun open(context: Context) {
        println("Opening Profile")
    }
}

class SettingsFeature @Inject constructor() : Feature {
    override val id = "settings"
    override val displayName = "Settings"
    override fun isEnabled() = true
    override fun open(context: Context) {
        println("Opening Settings")
    }
}

class PremiumFeature @Inject constructor(
    private val premiumManager: PremiumManager
) : Feature {
    override val id = "premium"
    override val displayName = "Premium Features"
    override fun isEnabled() = premiumManager.isPremiumUser()
    override fun open(context: Context) {
        println("Opening Premium Features")
    }
}

// Module providing features
@Module
@InstallIn(SingletonComponent::class)
abstract class FeatureModule {

    @Binds
    @IntoMap
    @FeatureKey("profile")
    abstract fun bindProfileFeature(feature: ProfileFeature): Feature

    @Binds
    @IntoMap
    @FeatureKey("settings")
    abstract fun bindSettingsFeature(feature: SettingsFeature): Feature

    @Binds
    @IntoMap
    @FeatureKey("premium")
    abstract fun bindPremiumFeature(feature: PremiumFeature): Feature
}

// Usage
@Singleton
class FeatureRegistry @Inject constructor(
    private val features: Map<String, @JvmSuppressWildcards Feature>
) {

    fun getFeature(id: String): Feature? {
        return features[id]
    }

    fun getAllFeatures(): List<Feature> {
        return features.values.toList()
    }

    fun getEnabledFeatures(): List<Feature> {
        return features.values.filter { it.isEnabled() }
    }

    fun openFeature(id: String, context: Context) {
        features[id]?.let { feature ->
            if (feature.isEnabled()) {
                feature.open(context)
            } else {
                println("Feature $id is not enabled")
            }
        } ?: println("Feature $id not found")
    }
}

// In Activity
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    @Inject
    lateinit var featureRegistry: FeatureRegistry

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Get all enabled features
        val enabledFeatures = featureRegistry.getEnabledFeatures()
        enabledFeatures.forEach { feature ->
            println("Available: ${feature.displayName}")
        }

        // Open a specific feature
        featureRegistry.openFeature("profile", this)
    }
}
```

### @Multibinds for Optional Dependencies

Sometimes you want to inject an empty collection if no bindings are provided:

```kotlin
@Module
@InstallIn(SingletonComponent::class)
abstract class InterceptorModule {

    // Declares an empty set that can be injected even if no interceptors are bound
    @Multibinds
    abstract fun bindInterceptors(): Set<Interceptor>

    // If you add interceptors later, they'll be added to this set
    @Binds
    @IntoSet
    abstract fun bindLoggingInterceptor(interceptor: LoggingInterceptor): Interceptor
}

// Usage
@Singleton
class ApiClient @Inject constructor(
    private val interceptors: Set<@JvmSuppressWildcards Interceptor>
) {
    // interceptors will be an empty set if no bindings exist
    // or contain all bound interceptors
}
```

### Real-World Example: Navigation Plugin System

```kotlin
// Navigation destination
data class Destination(
    val route: String,
    val label: String,
    val icon: ImageVector
)

// Screen provider interface
interface ScreenProvider {
    fun getDestinations(): List<Destination>
    fun getScreen(route: String): (@Composable () -> Unit)?
}

// Home module screen provider
class HomeScreenProvider @Inject constructor() : ScreenProvider {

    override fun getDestinations(): List<Destination> = listOf(
        Destination("home", "Home", Icons.Default.Home),
        Destination("feed", "Feed", Icons.Default.List)
    )

    override fun getScreen(route: String): (@Composable () -> Unit)? {
        return when (route) {
            "home" -> { { HomeScreen() } }
            "feed" -> { { FeedScreen() } }
            else -> null
        }
    }
}

// Profile module screen provider
class ProfileScreenProvider @Inject constructor() : ScreenProvider {

    override fun getDestinations(): List<Destination> = listOf(
        Destination("profile", "Profile", Icons.Default.Person),
        Destination("settings", "Settings", Icons.Default.Settings)
    )

    override fun getScreen(route: String): (@Composable () -> Unit)? {
        return when (route) {
            "profile" -> { { ProfileScreen() } }
            "settings" -> { { SettingsScreen() } }
            else -> null
        }
    }
}

// Premium module screen provider (optional feature)
class PremiumScreenProvider @Inject constructor() : ScreenProvider {

    override fun getDestinations(): List<Destination> = listOf(
        Destination("premium", "Premium", Icons.Default.Star)
    )

    override fun getScreen(route: String): (@Composable () -> Unit)? {
        return when (route) {
            "premium" -> { { PremiumScreen() } }
            else -> null
        }
    }
}

// Module
@Module
@InstallIn(SingletonComponent::class)
abstract class NavigationModule {

    @Binds
    @IntoSet
    abstract fun bindHomeScreenProvider(provider: HomeScreenProvider): ScreenProvider

    @Binds
    @IntoSet
    abstract fun bindProfileScreenProvider(provider: ProfileScreenProvider): ScreenProvider

    // Optional - only included if premium feature is enabled
    @Binds
    @IntoSet
    abstract fun bindPremiumScreenProvider(provider: PremiumScreenProvider): ScreenProvider
}

// Navigation registry
@Singleton
class NavigationRegistry @Inject constructor(
    private val screenProviders: Set<@JvmSuppressWildcards ScreenProvider>
) {

    private val destinationMap: Map<String, @Composable () -> Unit> by lazy {
        screenProviders.flatMap { provider ->
            provider.getDestinations().mapNotNull { destination ->
                provider.getScreen(destination.route)?.let { screen ->
                    destination.route to screen
                }
            }
        }.toMap()
    }

    fun getAllDestinations(): List<Destination> {
        return screenProviders.flatMap { it.getDestinations() }
    }

    fun getScreen(route: String): (@Composable () -> Unit)? {
        return destinationMap[route]
    }
}

// Usage in Compose NavHost
@Composable
fun AppNavigation(
    navigationRegistry: NavigationRegistry,
    navController: NavHostController
) {
    NavHost(
        navController = navController,
        startDestination = "home"
    ) {
        // Dynamically add all registered screens
        navigationRegistry.getAllDestinations().forEach { destination ->
            composable(destination.route) {
                navigationRegistry.getScreen(destination.route)?.invoke()
                    ?: ErrorScreen("Screen not found")
            }
        }
    }
}

// Bottom navigation
@Composable
fun BottomNavigation(
    navigationRegistry: NavigationRegistry,
    navController: NavHostController
) {
    NavigationBar {
        navigationRegistry.getAllDestinations().forEach { destination ->
            NavigationBarItem(
                icon = { Icon(destination.icon, contentDescription = null) },
                label = { Text(destination.label) },
                selected = false,
                onClick = { navController.navigate(destination.route) }
            )
        }
    }
}
```

### Advanced: Multi-Module Feature System

```kotlin
// Feature module interface
interface FeatureModule {
    val id: String
    val priority: Int // For ordering
    fun initialize(context: Context)
    fun isEnabled(): Boolean
}

// Analytics feature module
class AnalyticsFeatureModule @Inject constructor(
    private val analytics: Analytics
) : FeatureModule {
    override val id = "analytics"
    override val priority = 100
    override fun initialize(context: Context) {
        analytics.init(context)
    }
    override fun isEnabled() = true
}

// Crash reporting feature module
class CrashReportingFeatureModule @Inject constructor(
    private val crashReporter: CrashReporter
) : FeatureModule {
    override val id = "crash_reporting"
    override val priority = 90
    override fun initialize(context: Context) {
        crashReporter.init(context)
    }
    override fun isEnabled() = true
}

// A/B testing feature module
class ABTestingFeatureModule @Inject constructor(
    private val abTesting: ABTesting,
    private val remoteConfig: RemoteConfig
) : FeatureModule {
    override val id = "ab_testing"
    override val priority = 80
    override fun initialize(context: Context) {
        abTesting.init(context)
    }
    override fun isEnabled() = remoteConfig.getBoolean("ab_testing_enabled")
}

// Module
@Module
@InstallIn(SingletonComponent::class)
abstract class AppFeatureModule {

    @Multibinds
    abstract fun bindFeatureModules(): Set<FeatureModule>

    @Binds
    @IntoSet
    abstract fun bindAnalyticsModule(module: AnalyticsFeatureModule): FeatureModule

    @Binds
    @IntoSet
    abstract fun bindCrashReportingModule(module: CrashReportingFeatureModule): FeatureModule

    @Binds
    @IntoSet
    abstract fun bindABTestingModule(module: ABTestingFeatureModule): FeatureModule
}

// Application startup initializer
@Singleton
class AppInitializer @Inject constructor(
    private val featureModules: Set<@JvmSuppressWildcards FeatureModule>
) {

    fun initialize(context: Context) {
        // Initialize modules in priority order
        featureModules
            .filter { it.isEnabled() }
            .sortedByDescending { it.priority }
            .forEach { module ->
                try {
                    println("Initializing feature module: ${module.id}")
                    module.initialize(context)
                    println("✓ ${module.id} initialized successfully")
                } catch (e: Exception) {
                    println("✗ Failed to initialize ${module.id}: ${e.message}")
                }
            }
    }
}

// In Application
@HiltAndroidApp
class MyApplication : Application() {

    @Inject
    lateinit var appInitializer: AppInitializer

    override fun onCreate() {
        super.onCreate()
        appInitializer.initialize(this)
    }
}
```

### Map Multibinding with ClassKey

Using `@ClassKey` for type-based lookups:

```kotlin
// ViewHolder factory pattern with multibinding
sealed class ListItem {
    data class TextItem(val text: String) : ListItem()
    data class ImageItem(val imageUrl: String) : ListItem()
    data class VideoItem(val videoUrl: String) : ListItem()
}

interface ViewHolderFactory {
    fun createViewHolder(parent: ViewGroup): RecyclerView.ViewHolder
    fun bindViewHolder(holder: RecyclerView.ViewHolder, item: ListItem)
}

class TextViewHolderFactory @Inject constructor() : ViewHolderFactory {
    override fun createViewHolder(parent: ViewGroup): RecyclerView.ViewHolder {
        // Create text ViewHolder
        return TextViewHolder(parent)
    }

    override fun bindViewHolder(holder: RecyclerView.ViewHolder, item: ListItem) {
        (holder as TextViewHolder).bind((item as ListItem.TextItem).text)
    }
}

class ImageViewHolderFactory @Inject constructor(
    private val imageLoader: ImageLoader
) : ViewHolderFactory {
    override fun createViewHolder(parent: ViewGroup): RecyclerView.ViewHolder {
        return ImageViewHolder(parent, imageLoader)
    }

    override fun bindViewHolder(holder: RecyclerView.ViewHolder, item: ListItem) {
        (holder as ImageViewHolder).bind((item as ListItem.ImageItem).imageUrl)
    }
}

class VideoViewHolderFactory @Inject constructor(
    private val videoPlayer: VideoPlayer
) : ViewHolderFactory {
    override fun createViewHolder(parent: ViewGroup): RecyclerView.ViewHolder {
        return VideoViewHolder(parent, videoPlayer)
    }

    override fun bindViewHolder(holder: RecyclerView.ViewHolder, item: ListItem) {
        (holder as VideoViewHolder).bind((item as ListItem.VideoItem).videoUrl)
    }
}

// Module
@Module
@InstallIn(SingletonComponent::class)
abstract class ViewHolderModule {

    @Binds
    @IntoMap
    @ClassKey(ListItem.TextItem::class)
    abstract fun bindTextViewHolderFactory(factory: TextViewHolderFactory): ViewHolderFactory

    @Binds
    @IntoMap
    @ClassKey(ListItem.ImageItem::class)
    abstract fun bindImageViewHolderFactory(factory: ImageViewHolderFactory): ViewHolderFactory

    @Binds
    @IntoMap
    @ClassKey(ListItem.VideoItem::class)
    abstract fun bindVideoViewHolderFactory(factory: VideoViewHolderFactory): ViewHolderFactory
}

// Adapter
class MultiTypeAdapter @Inject constructor(
    private val factories: Map<Class<out ListItem>, @JvmSuppressWildcards ViewHolderFactory>
) : RecyclerView.Adapter<RecyclerView.ViewHolder>() {

    private val items = mutableListOf<ListItem>()

    override fun getItemViewType(position: Int): Int {
        return items[position]::class.java.hashCode()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        val itemClass = items.find { it::class.java.hashCode() == viewType }!!::class.java
        val factory = factories[itemClass]
            ?: throw IllegalArgumentException("No factory for $itemClass")
        return factory.createViewHolder(parent)
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        val item = items[position]
        val factory = factories[item::class.java]
            ?: throw IllegalArgumentException("No factory for ${item::class.java}")
        factory.bindViewHolder(holder, item)
    }

    override fun getItemCount() = items.size

    fun submitList(newItems: List<ListItem>) {
        items.clear()
        items.addAll(newItems)
        notifyDataSetChanged()
    }
}
```

### Multibinding with Qualifiers

Different sets/maps with qualifiers:

```kotlin
// Qualifiers
@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class NetworkInterceptors

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class LoggingInterceptors

// Module
@Module
@InstallIn(SingletonComponent::class)
abstract class InterceptorModule {

    // Network interceptors set
    @Binds
    @IntoSet
    @NetworkInterceptors
    abstract fun bindAuthInterceptor(interceptor: AuthInterceptor): Interceptor

    @Binds
    @IntoSet
    @NetworkInterceptors
    abstract fun bindRetryInterceptor(interceptor: RetryInterceptor): Interceptor

    // Logging interceptors set
    @Binds
    @IntoSet
    @LoggingInterceptors
    abstract fun bindHttpLoggingInterceptor(interceptor: HttpLoggingInterceptor): Interceptor

    @Binds
    @IntoSet
    @LoggingInterceptors
    abstract fun bindCurlLoggingInterceptor(interceptor: CurlLoggingInterceptor): Interceptor
}

// Usage
@Singleton
class ApiClientFactory @Inject constructor(
    @NetworkInterceptors private val networkInterceptors: Set<@JvmSuppressWildcards Interceptor>,
    @LoggingInterceptors private val loggingInterceptors: Set<@JvmSuppressWildcards Interceptor>
) {

    fun create(): OkHttpClient {
        return OkHttpClient.Builder().apply {
            // Add network interceptors
            networkInterceptors.forEach { addInterceptor(it) }
            // Add logging interceptors
            loggingInterceptors.forEach { addInterceptor(it) }
        }.build()
    }
}
```

### Production Example: Event Bus with Subscribers

```kotlin
// Event interface
interface Event

data class UserLoggedInEvent(val userId: String) : Event
data class PurchaseCompletedEvent(val productId: String, val amount: Double) : Event
data class ScreenViewedEvent(val screenName: String) : Event

// Subscriber interface
interface EventSubscriber {
    fun onEvent(event: Event)
}

// Analytics subscriber
@Singleton
class AnalyticsEventSubscriber @Inject constructor(
    private val analytics: Analytics
) : EventSubscriber {

    override fun onEvent(event: Event) {
        when (event) {
            is UserLoggedInEvent -> {
                analytics.setUserId(event.userId)
                analytics.track("user_logged_in")
            }
            is PurchaseCompletedEvent -> {
                analytics.track("purchase_completed", mapOf(
                    "product_id" to event.productId,
                    "amount" to event.amount
                ))
            }
            is ScreenViewedEvent -> {
                analytics.track("screen_viewed", mapOf("screen" to event.screenName))
            }
        }
    }
}

// Crash reporting subscriber
@Singleton
class CrashReportingEventSubscriber @Inject constructor(
    private val crashReporter: CrashReporter
) : EventSubscriber {

    override fun onEvent(event: Event) {
        when (event) {
            is UserLoggedInEvent -> {
                crashReporter.setUserId(event.userId)
            }
            is ScreenViewedEvent -> {
                crashReporter.log("Screen viewed: ${event.screenName}")
            }
            else -> {} // Ignore other events
        }
    }
}

// Database logger subscriber
@Singleton
class DatabaseEventSubscriber @Inject constructor(
    private val database: AppDatabase
) : EventSubscriber {

    override fun onEvent(event: Event) {
        when (event) {
            is UserLoggedInEvent -> {
                database.eventDao().insert(EventEntity("user_logged_in", event.userId))
            }
            is PurchaseCompletedEvent -> {
                database.eventDao().insert(EventEntity("purchase", event.productId))
            }
            else -> {}
        }
    }
}

// Module
@Module
@InstallIn(SingletonComponent::class)
abstract class EventSubscriberModule {

    @Multibinds
    abstract fun bindEventSubscribers(): Set<EventSubscriber>

    @Binds
    @IntoSet
    abstract fun bindAnalyticsSubscriber(subscriber: AnalyticsEventSubscriber): EventSubscriber

    @Binds
    @IntoSet
    abstract fun bindCrashReportingSubscriber(subscriber: CrashReportingEventSubscriber): EventSubscriber

    @Binds
    @IntoSet
    abstract fun bindDatabaseSubscriber(subscriber: DatabaseEventSubscriber): EventSubscriber
}

// Event bus
@Singleton
class EventBus @Inject constructor(
    private val subscribers: Set<@JvmSuppressWildcards EventSubscriber>,
    @ApplicationScope private val scope: CoroutineScope
) {

    private val _events = MutableSharedFlow<Event>(
        replay = 0,
        extraBufferCapacity = 64,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )

    init {
        // Start collecting events and distributing to subscribers
        scope.launch {
            _events.collect { event ->
                subscribers.forEach { subscriber ->
                    try {
                        subscriber.onEvent(event)
                    } catch (e: Exception) {
                        println("Subscriber error: ${e.message}")
                    }
                }
            }
        }
    }

    fun post(event: Event) {
        _events.tryEmit(event)
    }
}

// Usage
@AndroidEntryPoint
class LoginActivity : AppCompatActivity() {

    @Inject
    lateinit var eventBus: EventBus

    private fun onLoginSuccess(userId: String) {
        // This event will be automatically distributed to all subscribers
        eventBus.post(UserLoggedInEvent(userId))
    }
}
```

### Best Practices

1. **Use @JvmSuppressWildcards for Kotlin**
   ```kotlin
   // ✅ GOOD - Suppresses wildcards for Kotlin
   @Inject
   constructor(private val plugins: Set<@JvmSuppressWildcards Plugin>)

   // ❌ BAD - May cause issues with Kotlin generics
   @Inject
   constructor(private val plugins: Set<Plugin>)
   ```

2. **Prefer Abstract Binds over Provides**
   ```kotlin
   // ✅ GOOD - More efficient
   @Binds
   @IntoSet
   abstract fun bindPlugin(plugin: MyPlugin): Plugin

   // ❌ BAD - Less efficient (creates extra method)
   @Provides
   @IntoSet
   fun providePlugin(plugin: MyPlugin): Plugin = plugin
   ```

3. **Use @Multibinds for Optional Collections**
   ```kotlin
   // ✅ GOOD - Can inject even if empty
   @Module
   @InstallIn(SingletonComponent::class)
   abstract class PluginModule {
       @Multibinds
       abstract fun bindPlugins(): Set<Plugin>
   }

   // Now you can inject Set<Plugin> even if no plugins are bound
   ```

4. **Order with Priority When Needed**
   ```kotlin
   // ✅ GOOD - Sort by priority if order matters
   @Singleton
   class PluginManager @Inject constructor(
       private val plugins: Set<@JvmSuppressWildcards Plugin>
   ) {
       fun initialize() {
           plugins.sortedByDescending { it.priority }
               .forEach { it.initialize() }
       }
   }
   ```

5. **Error Handling in Multibinding Consumers**
   ```kotlin
   // ✅ GOOD - Handle individual failures gracefully
   fun initializeAll() {
       plugins.forEach { plugin ->
           try {
               plugin.initialize()
           } catch (e: Exception) {
               println("Failed to initialize ${plugin.name}: ${e.message}")
           }
       }
   }

   // ❌ BAD - One failure breaks all
   fun initializeAll() {
       plugins.forEach { it.initialize() } // Will stop at first failure
   }
   ```

### Performance Considerations

1. **Set vs List**: Multibinding always produces `Set<T>` or `Map<K, V>`, never `List<T>`
2. **Lazy initialization**: Elements are created eagerly unless you use `Lazy<T>` or `Provider<T>`
3. **Memory**: All bound instances are kept in memory (consider using weak references if needed)

```kotlin
// Lazy multibinding
@Singleton
class PluginManager @Inject constructor(
    private val pluginProviders: Set<@JvmSuppressWildcards Provider<Plugin>>
) {
    fun initializeAll() {
        // Plugins are only created when .get() is called
        pluginProviders.forEach { provider ->
            val plugin = provider.get()
            plugin.initialize()
        }
    }
}
```

### Summary

**Dagger/Hilt Multibinding** allows binding multiple values into collections:

**Types**:
- `@IntoSet` - Single element into Set
- `@ElementsIntoSet` - Multiple elements into Set
- `@IntoMap` - Single entry into Map (requires key annotation)
- `@Multibinds` - Declares empty collection

**Use cases**:
- ✅ Plugin architectures
- ✅ Feature module systems
- ✅ Event subscriber patterns
- ✅ Interceptor chains
- ✅ Dynamic navigation
- ✅ Multi-type RecyclerView adapters

**Benefits**:
- Open/Closed Principle (open for extension, closed for modification)
- No need to modify existing code to add features
- Easy to enable/disable features
- Testable (can provide different sets in tests)

**Best practices**:
1. Use `@JvmSuppressWildcards` in Kotlin
2. Prefer `@Binds` over `@Provides`
3. Use `@Multibinds` for optional collections
4. Handle individual element failures gracefully
5. Consider lazy initialization for performance

---

# Вопрос (RU)
Объясните Dagger/Hilt Multibinding (IntoSet, IntoMap, Multibinds). Как бы вы использовали это для реализации плагинной архитектуры или системы feature-модулей?

## Ответ (RU)
### Обзор

**Multibinding** в Dagger/Hilt позволяет связывать несколько значений в коллекцию (Set или Map), которую можно внедрить как единую зависимость. Это невероятно полезно для плагинных архитектур, feature-модулей и расширяемых систем, где вы хотите добавлять функциональность без изменения существующего кода.

### Типы Multibinding

1. **@IntoSet** — добавляет один элемент в Set
2. **@ElementsIntoSet** — добавляет несколько элементов в Set
3. **@IntoMap** — добавляет одну запись в Map
4. **@Multibinds** — объявляет пустую коллекцию, которую можно внедрить

### Базовый пример @IntoSet

```kotlin
// Интерфейс для плагинов
interface Plugin {
    val name: String
    fun initialize(context: Context)
}

// Реализации плагинов
class AnalyticsPlugin @Inject constructor() : Plugin {
    override val name = "Analytics"
    override fun initialize(context: Context) {
        println("Initializing Analytics Plugin")
    }
}

class CrashReportingPlugin @Inject constructor() : Plugin {
    override val name = "CrashReporting"
    override fun initialize(context: Context) {
        println("Initializing Crash Reporting Plugin")
    }
}

class PerformancePlugin @Inject constructor() : Plugin {
    override val name = "Performance"
    override fun initialize(context: Context) {
        println("Initializing Performance Plugin")
    }
}

// Модуль, предоставляющий плагины
@Module
@InstallIn(SingletonComponent::class)
abstract class PluginModule {

    @Binds
    @IntoSet
    abstract fun bindAnalyticsPlugin(plugin: AnalyticsPlugin): Plugin

    @Binds
    @IntoSet
    abstract fun bindCrashReportingPlugin(plugin: CrashReportingPlugin): Plugin

    @Binds
    @IntoSet
    abstract fun bindPerformancePlugin(plugin: PerformancePlugin): Plugin
}

// Использование — внедрение всего Set
@Singleton
class PluginManager @Inject constructor(
    private val plugins: Set<@JvmSuppressWildcards Plugin>
) {

    fun initializeAll(context: Context) {
        plugins.forEach { plugin ->
            println("Initializing plugin: ${plugin.name}")
            plugin.initialize(context)
        }
    }

    fun getPlugin(name: String): Plugin? {
        return plugins.find { it.name == name }
    }
}
```

**Вывод:**
```
Initializing plugin: Analytics
Initializing Analytics Plugin
Initializing plugin: CrashReporting
Initializing Crash Reporting Plugin
Initializing plugin: Performance
Initializing Performance Plugin
```

### @IntoMap с кастомными ключами

Map требуют аннотации ключа. Dagger предоставляет встроенные ключи, или вы можете создать свои:

```kotlin
// Встроенные аннотации ключей:
// @StringKey, @IntKey, @LongKey, @ClassKey

// Кастомная аннотация ключа
@MapKey
annotation class FeatureKey(val value: String)

// Интерфейс feature
interface Feature {
    val id: String
    val displayName: String
    fun isEnabled(): Boolean
    fun open(context: Context)
}

// Реализации feature
class ProfileFeature @Inject constructor() : Feature {
    override val id = "profile"
    override val displayName = "User Profile"
    override fun isEnabled() = true
    override fun open(context: Context) {
        println("Opening Profile")
    }
}

class SettingsFeature @Inject constructor() : Feature {
    override val id = "settings"
    override val displayName = "Settings"
    override fun isEnabled() = true
    override fun open(context: Context) {
        println("Opening Settings")
    }
}

class PremiumFeature @Inject constructor(
    private val premiumManager: PremiumManager
) : Feature {
    override val id = "premium"
    override val displayName = "Premium Features"
    override fun isEnabled() = premiumManager.isPremiumUser()
    override fun open(context: Context) {
        println("Opening Premium Features")
    }
}

// Модуль, предоставляющий features
@Module
@InstallIn(SingletonComponent::class)
abstract class FeatureModule {

    @Binds
    @IntoMap
    @FeatureKey("profile")
    abstract fun bindProfileFeature(feature: ProfileFeature): Feature

    @Binds
    @IntoMap
    @FeatureKey("settings")
    abstract fun bindSettingsFeature(feature: SettingsFeature): Feature

    @Binds
    @IntoMap
    @FeatureKey("premium")
    abstract fun bindPremiumFeature(feature: PremiumFeature): Feature
}

// Использование
@Singleton
class FeatureRegistry @Inject constructor(
    private val features: Map<String, @JvmSuppressWildcards Feature>
) {

    fun getFeature(id: String): Feature? {
        return features[id]
    }

    fun getAllFeatures(): List<Feature> {
        return features.values.toList()
    }

    fun getEnabledFeatures(): List<Feature> {
        return features.values.filter { it.isEnabled() }
    }

    fun openFeature(id: String, context: Context) {
        features[id]?.let { feature ->
            if (feature.isEnabled()) {
                feature.open(context)
            } else {
                println("Feature $id is not enabled")
            }
        } ?: println("Feature $id not found")
    }
}

// В Activity
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    @Inject
    lateinit var featureRegistry: FeatureRegistry

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Получаем все включенные features
        val enabledFeatures = featureRegistry.getEnabledFeatures()
        enabledFeatures.forEach { feature ->
            println("Available: ${feature.displayName}")
        }

        // Открываем конкретный feature
        featureRegistry.openFeature("profile", this)
    }
}
```

### @Multibinds для опциональных зависимостей

Иногда вы хотите внедрить пустую коллекцию, если нет привязок:

```kotlin
@Module
@InstallIn(SingletonComponent::class)
abstract class InterceptorModule {

    // Объявляет пустой set, который можно внедрить, даже если нет interceptor'ов
    @Multibinds
    abstract fun bindInterceptors(): Set<Interceptor>

    // Если вы добавите interceptor'ы позже, они будут добавлены в этот set
    @Binds
    @IntoSet
    abstract fun bindLoggingInterceptor(interceptor: LoggingInterceptor): Interceptor
}

// Использование
@Singleton
class ApiClient @Inject constructor(
    private val interceptors: Set<@JvmSuppressWildcards Interceptor>
) {
    // interceptors будет пустым set, если нет привязок
    // или содержать все связанные interceptor'ы
}
```

### Реальный пример: система плагинов навигации

```kotlin
// Назначение навигации
data class Destination(
    val route: String,
    val label: String,
    val icon: ImageVector
)

// Интерфейс провайдера экранов
interface ScreenProvider {
    fun getDestinations(): List<Destination>
    fun getScreen(route: String): (@Composable () -> Unit)?
}

// Провайдер экранов для модуля Home
class HomeScreenProvider @Inject constructor() : ScreenProvider {

    override fun getDestinations(): List<Destination> = listOf(
        Destination("home", "Home", Icons.Default.Home),
        Destination("feed", "Feed", Icons.Default.List)
    )

    override fun getScreen(route: String): (@Composable () -> Unit)? {
        return when (route) {
            "home" -> { { HomeScreen() } }
            "feed" -> { { FeedScreen() } }
            else -> null
        }
    }
}

// Провайдер экранов для модуля Profile
class ProfileScreenProvider @Inject constructor() : ScreenProvider {

    override fun getDestinations(): List<Destination> = listOf(
        Destination("profile", "Profile", Icons.Default.Person),
        Destination("settings", "Settings", Icons.Default.Settings)
    )

    override fun getScreen(route: String): (@Composable () -> Unit)? {
        return when (route) {
            "profile" -> { { ProfileScreen() } }
            "settings" -> { { SettingsScreen() } }
            else -> null
        }
    }
}

// Провайдер экранов для модуля Premium (опциональный feature)
class PremiumScreenProvider @Inject constructor() : ScreenProvider {

    override fun getDestinations(): List<Destination> = listOf(
        Destination("premium", "Premium", Icons.Default.Star)
    )

    override fun getScreen(route: String): (@Composable () -> Unit)? {
        return when (route) {
            "premium" -> { { PremiumScreen() } }
            else -> null
        }
    }
}

// Модуль
@Module
@InstallIn(SingletonComponent::class)
abstract class NavigationModule {

    @Binds
    @IntoSet
    abstract fun bindHomeScreenProvider(provider: HomeScreenProvider): ScreenProvider

    @Binds
    @IntoSet
    abstract fun bindProfileScreenProvider(provider: ProfileScreenProvider): ScreenProvider

    // Опционально — включается только если premium feature активен
    @Binds
    @IntoSet
    abstract fun bindPremiumScreenProvider(provider: PremiumScreenProvider): ScreenProvider
}

// Реестр навигации
@Singleton
class NavigationRegistry @Inject constructor(
    private val screenProviders: Set<@JvmSuppressWildcards ScreenProvider>
) {

    private val destinationMap: Map<String, @Composable () -> Unit> by lazy {
        screenProviders.flatMap { provider ->
            provider.getDestinations().mapNotNull { destination ->
                provider.getScreen(destination.route)?.let { screen ->
                    destination.route to screen
                }
            }
        }.toMap()
    }

    fun getAllDestinations(): List<Destination> {
        return screenProviders.flatMap { it.getDestinations() }
    }

    fun getScreen(route: String): (@Composable () -> Unit)? {
        return destinationMap[route]
    }
}

// Использование в Compose NavHost
@Composable
fun AppNavigation(
    navigationRegistry: NavigationRegistry,
    navController: NavHostController
) {
    NavHost(
        navController = navController,
        startDestination = "home"
    ) {
        // Динамически добавляем все зарегистрированные экраны
        navigationRegistry.getAllDestinations().forEach { destination ->
            composable(destination.route) {
                navigationRegistry.getScreen(destination.route)?.invoke()
                    ?: ErrorScreen("Screen not found")
            }
        }
    }
}

// Bottom navigation
@Composable
fun BottomNavigation(
    navigationRegistry: NavigationRegistry,
    navController: NavHostController
) {
    NavigationBar {
        navigationRegistry.getAllDestinations().forEach { destination ->
            NavigationBarItem(
                icon = { Icon(destination.icon, contentDescription = null) },
                label = { Text(destination.label) },
                selected = false,
                onClick = { navController.navigate(destination.route) }
            )
        }
    }
}
```

[Продолжение с остальными примерами из английской версии...]

### Резюме

**Dagger/Hilt Multibinding** позволяет связывать несколько значений в коллекции:

**Типы**:
- `@IntoSet` — один элемент в Set
- `@ElementsIntoSet` — несколько элементов в Set
- `@IntoMap` — одна запись в Map (требует аннотацию ключа)
- `@Multibinds` — объявляет пустую коллекцию

**Применения**:
- ✅ Плагинные архитектуры
- ✅ Системы feature-модулей
- ✅ Паттерны подписчиков событий
- ✅ Цепочки interceptor'ов
- ✅ Динамическая навигация
- ✅ Многотипные адаптеры RecyclerView

**Преимущества**:
- Принцип Open/Closed (открыт для расширения, закрыт для изменения)
- Не нужно изменять существующий код для добавления features
- Легко включать/отключать features
- Тестируемо (можно предоставить разные наборы в тестах)

**Лучшие практики**:
1. Используйте `@JvmSuppressWildcards` в Kotlin
2. Предпочитайте `@Binds` над `@Provides`
3. Используйте `@Multibinds` для опциональных коллекций
4. Обрабатывайте сбои отдельных элементов корректно
5. Рассмотрите ленивую инициализацию для производительности
