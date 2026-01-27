---
id: android-hilt-007
title: Hilt Entry Points / Точки входа Hilt
aliases:
- Hilt Entry Points
- EntryPoint
- EntryPointAccessors
- Non-Android Classes DI
topic: android
subtopics:
- di-hilt
- architecture
question_kind: theory
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-hilt-setup-annotations--hilt--medium
- q-hilt-modules-provides--hilt--medium
- q-hilt-custom-components--hilt--hard
created: 2026-01-23
updated: 2026-01-23
tags:
- android/di-hilt
- android/architecture
- difficulty/hard
- hilt
- entry-point
- dependency-injection
anki_cards:
- slug: android-hilt-007-0-en
  language: en
- slug: android-hilt-007-0-ru
  language: ru
---
# Vopros (RU)
> Что такое @EntryPoint в Hilt? Когда и как использовать EntryPointAccessors для получения зависимостей в классах, не поддерживающих стандартную инъекцию?

# Question (EN)
> What is @EntryPoint in Hilt? When and how to use EntryPointAccessors to obtain dependencies in classes that don't support standard injection?

---

## Otvet (RU)

`@EntryPoint` - это механизм в Hilt для получения зависимостей из DI-графа в классах, которые не поддерживают стандартную инъекцию через `@AndroidEntryPoint` или `@Inject`. Это необходимо для интеграции с кодом, который Hilt не контролирует.

### Когда нужен @EntryPoint

1. **ContentProvider** - создается системой до Application
2. **Классы из сторонних библиотек** - не можете добавить аннотации
3. **Кастомные View** без Fragment/Activity контекста
4. **Callback-классы** - создаваемые фреймворками
5. **Legacy код** - постепенная миграция на DI

### Базовый пример: ContentProvider

```kotlin
// 1. Определяем Entry Point интерфейс
@EntryPoint
@InstallIn(SingletonComponent::class)
interface MyContentProviderEntryPoint {
    fun userRepository(): UserRepository
    fun analyticsService(): AnalyticsService
}

// 2. Используем в ContentProvider
class MyContentProvider : ContentProvider() {

    private lateinit var userRepository: UserRepository
    private lateinit var analyticsService: AnalyticsService

    override fun onCreate(): Boolean {
        val context = context ?: return false

        // Получаем зависимости через EntryPointAccessors
        val entryPoint = EntryPointAccessors.fromApplication(
            context.applicationContext,
            MyContentProviderEntryPoint::class.java
        )

        userRepository = entryPoint.userRepository()
        analyticsService = entryPoint.analyticsService()

        return true
    }

    override fun query(
        uri: Uri,
        projection: Array<out String>?,
        selection: String?,
        selectionArgs: Array<out String>?,
        sortOrder: String?
    ): Cursor? {
        // Используем userRepository
        return null
    }

    // Остальные методы ContentProvider...
    override fun getType(uri: Uri): String? = null
    override fun insert(uri: Uri, values: ContentValues?): Uri? = null
    override fun delete(uri: Uri, selection: String?, selectionArgs: Array<out String>?) = 0
    override fun update(uri: Uri, values: ContentValues?, selection: String?, selectionArgs: Array<out String>?) = 0
}
```

### Различные способы получения EntryPoint

```kotlin
@EntryPoint
@InstallIn(SingletonComponent::class)
interface AppEntryPoint {
    fun userRepository(): UserRepository
    fun logger(): Logger
}

// 1. Из Application context
val entryPoint = EntryPointAccessors.fromApplication(
    context.applicationContext,
    AppEntryPoint::class.java
)

// 2. Из Activity (для ActivityComponent)
@EntryPoint
@InstallIn(ActivityComponent::class)
interface ActivityEntryPoint {
    fun navigator(): Navigator
}

val activityEntryPoint = EntryPointAccessors.fromActivity(
    activity,
    ActivityEntryPoint::class.java
)

// 3. Из Fragment (для FragmentComponent)
@EntryPoint
@InstallIn(FragmentComponent::class)
interface FragmentEntryPoint {
    fun imageLoader(): ImageLoader
}

val fragmentEntryPoint = EntryPointAccessors.fromFragment(
    fragment,
    FragmentEntryPoint::class.java
)
```

### Использование в кастомных View

```kotlin
// Entry Point для View
@EntryPoint
@InstallIn(SingletonComponent::class)
interface CustomViewEntryPoint {
    fun imageLoader(): ImageLoader
    fun analyticsService(): AnalyticsService
}

class CustomAvatarView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : FrameLayout(context, attrs, defStyleAttr) {

    private val imageLoader: ImageLoader
    private val analyticsService: AnalyticsService

    init {
        // Получаем зависимости через EntryPoint
        val entryPoint = EntryPointAccessors.fromApplication(
            context.applicationContext,
            CustomViewEntryPoint::class.java
        )

        imageLoader = entryPoint.imageLoader()
        analyticsService = entryPoint.analyticsService()

        // Inflate layout
        LayoutInflater.from(context).inflate(R.layout.view_custom_avatar, this, true)
    }

    fun loadAvatar(url: String) {
        analyticsService.logEvent("avatar_load_started")
        imageLoader.load(url, findViewById(R.id.avatarImage))
    }
}
```

### Интеграция со сторонними библиотеками

```kotlin
// Пример: Кастомный Glide module
@EntryPoint
@InstallIn(SingletonComponent::class)
interface GlideEntryPoint {
    fun okHttpClient(): OkHttpClient
}

@GlideModule
class MyGlideModule : AppGlideModule() {

    override fun registerComponents(
        context: Context,
        glide: Glide,
        registry: Registry
    ) {
        val entryPoint = EntryPointAccessors.fromApplication(
            context.applicationContext,
            GlideEntryPoint::class.java
        )

        val okHttpClient = entryPoint.okHttpClient()

        registry.replace(
            GlideUrl::class.java,
            InputStream::class.java,
            OkHttpUrlLoader.Factory(okHttpClient)
        )
    }
}

// Пример: Firebase MessagingService
@EntryPoint
@InstallIn(SingletonComponent::class)
interface FirebaseEntryPoint {
    fun notificationManager(): NotificationManager
    fun userRepository(): UserRepository
    fun analyticsService(): AnalyticsService
}

class MyFirebaseMessagingService : FirebaseMessagingService() {

    override fun onMessageReceived(message: RemoteMessage) {
        val entryPoint = EntryPointAccessors.fromApplication(
            applicationContext,
            FirebaseEntryPoint::class.java
        )

        val notificationManager = entryPoint.notificationManager()
        val analyticsService = entryPoint.analyticsService()

        analyticsService.logEvent("push_received", mapOf(
            "title" to (message.notification?.title ?: "")
        ))

        // Показываем уведомление
        message.notification?.let { notification ->
            notificationManager.showNotification(
                title = notification.title ?: "",
                body = notification.body ?: ""
            )
        }
    }

    override fun onNewToken(token: String) {
        val entryPoint = EntryPointAccessors.fromApplication(
            applicationContext,
            FirebaseEntryPoint::class.java
        )

        // Сохраняем токен
        CoroutineScope(Dispatchers.IO).launch {
            entryPoint.userRepository().updateFcmToken(token)
        }
    }
}
```

### WorkManager без @HiltWorker

Иногда нужен ручной контроль над Worker:

```kotlin
@EntryPoint
@InstallIn(SingletonComponent::class)
interface WorkerEntryPoint {
    fun syncRepository(): SyncRepository
    fun errorReporter(): ErrorReporter
}

class ManualSyncWorker(
    appContext: Context,
    workerParams: WorkerParameters
) : CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result {
        val entryPoint = EntryPointAccessors.fromApplication(
            applicationContext,
            WorkerEntryPoint::class.java
        )

        val syncRepository = entryPoint.syncRepository()
        val errorReporter = entryPoint.errorReporter()

        return try {
            syncRepository.performSync()
            Result.success()
        } catch (e: Exception) {
            errorReporter.report(e)
            if (runAttemptCount < 3) Result.retry() else Result.failure()
        }
    }
}
```

### Комплексный пример: Инициализатор приложения

```kotlin
// Entry Point для App Startup
@EntryPoint
@InstallIn(SingletonComponent::class)
interface InitializerEntryPoint {
    fun appConfig(): AppConfig
    fun crashReporter(): CrashReporter
    fun analyticsService(): AnalyticsService
    fun featureFlagManager(): FeatureFlagManager
}

// App Startup Initializer
class AnalyticsInitializer : Initializer<AnalyticsService> {

    override fun create(context: Context): AnalyticsService {
        val entryPoint = EntryPointAccessors.fromApplication(
            context.applicationContext,
            InitializerEntryPoint::class.java
        )

        val analyticsService = entryPoint.analyticsService()
        val appConfig = entryPoint.appConfig()

        analyticsService.initialize(
            apiKey = appConfig.analyticsApiKey,
            enableDebug = appConfig.isDebug
        )

        return analyticsService
    }

    override fun dependencies(): List<Class<out Initializer<*>>> {
        return listOf(CrashReporterInitializer::class.java)
    }
}

class CrashReporterInitializer : Initializer<CrashReporter> {

    override fun create(context: Context): CrashReporter {
        val entryPoint = EntryPointAccessors.fromApplication(
            context.applicationContext,
            InitializerEntryPoint::class.java
        )

        val crashReporter = entryPoint.crashReporter()
        crashReporter.initialize()

        return crashReporter
    }

    override fun dependencies(): List<Class<out Initializer<*>>> = emptyList()
}

class FeatureFlagInitializer : Initializer<FeatureFlagManager> {

    override fun create(context: Context): FeatureFlagManager {
        val entryPoint = EntryPointAccessors.fromApplication(
            context.applicationContext,
            InitializerEntryPoint::class.java
        )

        val featureFlagManager = entryPoint.featureFlagManager()

        // Синхронная инициализация
        runBlocking {
            featureFlagManager.fetchFlags()
        }

        return featureFlagManager
    }

    override fun dependencies(): List<Class<out Initializer<*>>> {
        return listOf(AnalyticsInitializer::class.java)
    }
}
```

### Правила и best practices

1. **Минимизируйте использование** - @EntryPoint это "escape hatch", предпочитайте стандартную инъекцию
2. **Группируйте зависимости** - один EntryPoint интерфейс на use case
3. **Правильный компонент** - используйте @InstallIn, соответствующий lifecycle
4. **Кэшируйте результат** - не вызывайте EntryPointAccessors многократно
5. **Документируйте** - объясняйте, почему нужен EntryPoint

```kotlin
// Хорошо: Один раз получаем в init
class MyCustomView(context: Context) : View(context) {
    private val imageLoader: ImageLoader

    init {
        val entryPoint = EntryPointAccessors.fromApplication(
            context.applicationContext,
            ViewEntryPoint::class.java
        )
        imageLoader = entryPoint.imageLoader()
    }
}

// Плохо: Каждый раз получаем заново
class MyCustomView(context: Context) : View(context) {
    fun loadImage(url: String) {
        // НЕ ДЕЛАЙТЕ ТАК - создает накладные расходы
        val entryPoint = EntryPointAccessors.fromApplication(
            context.applicationContext,
            ViewEntryPoint::class.java
        )
        entryPoint.imageLoader().load(url, this)
    }
}
```

---

## Answer (EN)

`@EntryPoint` is a mechanism in Hilt for obtaining dependencies from the DI graph in classes that don't support standard injection through `@AndroidEntryPoint` or `@Inject`. This is necessary for integration with code that Hilt doesn't control.

### When @EntryPoint is Needed

1. **ContentProvider** - created by the system before Application
2. **Third-party library classes** - can't add annotations
3. **Custom Views** without Fragment/Activity context
4. **Callback classes** - created by frameworks
5. **Legacy code** - gradual migration to DI

### Basic Example: ContentProvider

```kotlin
// 1. Define Entry Point interface
@EntryPoint
@InstallIn(SingletonComponent::class)
interface MyContentProviderEntryPoint {
    fun userRepository(): UserRepository
    fun analyticsService(): AnalyticsService
}

// 2. Use in ContentProvider
class MyContentProvider : ContentProvider() {

    private lateinit var userRepository: UserRepository
    private lateinit var analyticsService: AnalyticsService

    override fun onCreate(): Boolean {
        val context = context ?: return false

        // Get dependencies through EntryPointAccessors
        val entryPoint = EntryPointAccessors.fromApplication(
            context.applicationContext,
            MyContentProviderEntryPoint::class.java
        )

        userRepository = entryPoint.userRepository()
        analyticsService = entryPoint.analyticsService()

        return true
    }

    override fun query(
        uri: Uri,
        projection: Array<out String>?,
        selection: String?,
        selectionArgs: Array<out String>?,
        sortOrder: String?
    ): Cursor? {
        // Use userRepository
        return null
    }

    // Other ContentProvider methods...
    override fun getType(uri: Uri): String? = null
    override fun insert(uri: Uri, values: ContentValues?): Uri? = null
    override fun delete(uri: Uri, selection: String?, selectionArgs: Array<out String>?) = 0
    override fun update(uri: Uri, values: ContentValues?, selection: String?, selectionArgs: Array<out String>?) = 0
}
```

### Different Ways to Obtain EntryPoint

```kotlin
@EntryPoint
@InstallIn(SingletonComponent::class)
interface AppEntryPoint {
    fun userRepository(): UserRepository
    fun logger(): Logger
}

// 1. From Application context
val entryPoint = EntryPointAccessors.fromApplication(
    context.applicationContext,
    AppEntryPoint::class.java
)

// 2. From Activity (for ActivityComponent)
@EntryPoint
@InstallIn(ActivityComponent::class)
interface ActivityEntryPoint {
    fun navigator(): Navigator
}

val activityEntryPoint = EntryPointAccessors.fromActivity(
    activity,
    ActivityEntryPoint::class.java
)

// 3. From Fragment (for FragmentComponent)
@EntryPoint
@InstallIn(FragmentComponent::class)
interface FragmentEntryPoint {
    fun imageLoader(): ImageLoader
}

val fragmentEntryPoint = EntryPointAccessors.fromFragment(
    fragment,
    FragmentEntryPoint::class.java
)
```

### Usage in Custom Views

```kotlin
// Entry Point for View
@EntryPoint
@InstallIn(SingletonComponent::class)
interface CustomViewEntryPoint {
    fun imageLoader(): ImageLoader
    fun analyticsService(): AnalyticsService
}

class CustomAvatarView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : FrameLayout(context, attrs, defStyleAttr) {

    private val imageLoader: ImageLoader
    private val analyticsService: AnalyticsService

    init {
        // Get dependencies through EntryPoint
        val entryPoint = EntryPointAccessors.fromApplication(
            context.applicationContext,
            CustomViewEntryPoint::class.java
        )

        imageLoader = entryPoint.imageLoader()
        analyticsService = entryPoint.analyticsService()

        // Inflate layout
        LayoutInflater.from(context).inflate(R.layout.view_custom_avatar, this, true)
    }

    fun loadAvatar(url: String) {
        analyticsService.logEvent("avatar_load_started")
        imageLoader.load(url, findViewById(R.id.avatarImage))
    }
}
```

### Integration with Third-party Libraries

```kotlin
// Example: Firebase MessagingService
@EntryPoint
@InstallIn(SingletonComponent::class)
interface FirebaseEntryPoint {
    fun notificationManager(): NotificationManager
    fun userRepository(): UserRepository
    fun analyticsService(): AnalyticsService
}

class MyFirebaseMessagingService : FirebaseMessagingService() {

    override fun onMessageReceived(message: RemoteMessage) {
        val entryPoint = EntryPointAccessors.fromApplication(
            applicationContext,
            FirebaseEntryPoint::class.java
        )

        val notificationManager = entryPoint.notificationManager()
        val analyticsService = entryPoint.analyticsService()

        analyticsService.logEvent("push_received", mapOf(
            "title" to (message.notification?.title ?: "")
        ))

        // Show notification
        message.notification?.let { notification ->
            notificationManager.showNotification(
                title = notification.title ?: "",
                body = notification.body ?: ""
            )
        }
    }

    override fun onNewToken(token: String) {
        val entryPoint = EntryPointAccessors.fromApplication(
            applicationContext,
            FirebaseEntryPoint::class.java
        )

        // Save token
        CoroutineScope(Dispatchers.IO).launch {
            entryPoint.userRepository().updateFcmToken(token)
        }
    }
}
```

### Rules and Best Practices

1. **Minimize usage** - @EntryPoint is an "escape hatch", prefer standard injection
2. **Group dependencies** - one EntryPoint interface per use case
3. **Correct component** - use @InstallIn matching the lifecycle
4. **Cache the result** - don't call EntryPointAccessors multiple times
5. **Document** - explain why EntryPoint is needed

```kotlin
// Good: Get once in init
class MyCustomView(context: Context) : View(context) {
    private val imageLoader: ImageLoader

    init {
        val entryPoint = EntryPointAccessors.fromApplication(
            context.applicationContext,
            ViewEntryPoint::class.java
        )
        imageLoader = entryPoint.imageLoader()
    }
}

// Bad: Get every time
class MyCustomView(context: Context) : View(context) {
    fun loadImage(url: String) {
        // DON'T DO THIS - creates overhead
        val entryPoint = EntryPointAccessors.fromApplication(
            context.applicationContext,
            ViewEntryPoint::class.java
        )
        entryPoint.imageLoader().load(url, this)
    }
}
```

---

## Dopolnitelnye Voprosy (RU)

- Почему ContentProvider нельзя использовать с @AndroidEntryPoint?
- Как тестировать классы, использующие @EntryPoint?
- Какие есть альтернативы @EntryPoint для кастомных View?
- Как избежать memory leaks при использовании @EntryPoint?

## Follow-ups

- Why can't ContentProvider use @AndroidEntryPoint?
- How do you test classes that use @EntryPoint?
- What are alternatives to @EntryPoint for custom Views?
- How do you avoid memory leaks when using @EntryPoint?

---

## Ssylki (RU)

- [Hilt Entry Points](https://developer.android.com/training/dependency-injection/hilt-android#not-supported)
- [Dagger Entry Points](https://dagger.dev/hilt/entry-points.html)

## References

- [Hilt Entry Points](https://developer.android.com/training/dependency-injection/hilt-android#not-supported)
- [Dagger Entry Points](https://dagger.dev/hilt/entry-points.html)

---

## Svyazannye Voprosy (RU)

### Medium
- [[q-hilt-setup-annotations--hilt--medium]]
- [[q-hilt-modules-provides--hilt--medium]]

### Hard
- [[q-hilt-custom-components--hilt--hard]]
- [[q-hilt-scopes--hilt--hard]]
- [[q-hilt-multimodule--hilt--hard]]

## Related Questions

### Medium
- [[q-hilt-setup-annotations--hilt--medium]]
- [[q-hilt-modules-provides--hilt--medium]]

### Hard
- [[q-hilt-custom-components--hilt--hard]]
- [[q-hilt-scopes--hilt--hard]]
- [[q-hilt-multimodule--hilt--hard]]
