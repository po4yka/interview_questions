---
topic: android
tags:
  - android
  - dagger
  - hilt
  - dependency-injection
  - build-optimization
  - performance
difficulty: medium
---

# Оптимизация времени сборки с Dagger

**English**: How to minimize Dagger's impact on build time?

## Answer

Для минимизации влияния Dagger на время сборки можно воспользоваться несколькими стратегиями и практиками, которые помогут оптимизировать процесс компиляции.

### 1. Использование Hilt вместо Dagger

Hilt упрощает настройку и сокращает boilerplate код, что ускоряет компиляцию.

```kotlin
// ❌ Dagger - много кода, медленная компиляция
@Component(modules = [NetworkModule::class, DatabaseModule::class, RepositoryModule::class])
@Singleton
interface AppComponent {
    fun inject(activity: MainActivity)
    fun inject(fragment: UserFragment)
    // ... десятки inject методов
}

@Module
class NetworkModule {
    @Provides
    @Singleton
    fun provideRetrofit(): Retrofit { /* ... */ }
}

// ✓ Hilt - меньше кода, быстрее компилируется
@HiltAndroidApp
class MyApplication : Application()

@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository
}

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Singleton
    fun provideRetrofit(): Retrofit { /* ... */ }
}
```

### 2. Разделение модулей (Modularization)

Разбейте большие модули на несколько меньших, логически связанных компонентов.

```kotlin
// ❌ НЕПРАВИЛЬНО - один огромный модуль
@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    // 50+ @Provides методов
    @Provides fun provideRetrofit(): Retrofit { /* ... */ }
    @Provides fun provideGlide(): RequestManager { /* ... */ }
    @Provides fun provideDatabase(): AppDatabase { /* ... */ }
    @Provides fun provideSharedPrefs(): SharedPreferences { /* ... */ }
    // ... еще 46 методов
}

// ✓ ПРАВИЛЬНО - разделенные модули
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Singleton
    fun provideRetrofit(): Retrofit { /* ... */ }

    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient { /* ... */ }
}

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {
    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(context, AppDatabase::class.java, "app.db").build()
    }
}

@Module
@InstallIn(SingletonComponent::class)
object ImageModule {
    @Provides
    fun provideGlide(@ApplicationContext context: Context): RequestManager {
        return Glide.with(context)
    }
}
```

### 3. Использование компонентов с Subcomponents

Изолируйте изменения в разных частях приложения.

```kotlin
// Feature-specific components
@Module
@InstallIn(ActivityComponent::class)
object UserFeatureModule {
    @Provides
    @ActivityScoped
    fun provideUserViewModel(repository: UserRepository): UserViewModel {
        return UserViewModel(repository)
    }
}

@Module
@InstallIn(FragmentComponent::class)
object ProfileFeatureModule {
    @Provides
    fun provideProfileAdapter(): ProfileAdapter {
        return ProfileAdapter()
    }
}

// Изменения в ProfileFeatureModule не триггерят перекомпиляцию UserFeatureModule
```

### 4. Избегание избыточных зависимостей

```kotlin
// ❌ НЕПРАВИЛЬНО - слишком много зависимостей в конструкторе
@HiltViewModel
class MainViewModel @Inject constructor(
    private val userRepo: UserRepository,
    private val productRepo: ProductRepository,
    private val orderRepo: OrderRepository,
    private val paymentRepo: PaymentRepository,
    private val analyticsRepo: AnalyticsRepository,
    private val settingsRepo: SettingsRepository,
    private val notificationRepo: NotificationRepository
    // ... еще 10 репозиториев
) : ViewModel() {
    // Dagger генерирует много кода для всех этих зависимостей
}

// ✓ ПРАВИЛЬНО - использовать Facade или UseCase паттерн
@HiltViewModel
class MainViewModel @Inject constructor(
    private val mainUseCases: MainUseCases
) : ViewModel()

class MainUseCases @Inject constructor(
    private val userRepo: UserRepository,
    private val productRepo: ProductRepository
    // Только необходимые зависимости
) {
    suspend fun loadMainData() = coroutineScope {
        val users = async { userRepo.getUsers() }
        val products = async { productRepo.getProducts() }
        MainData(users.await(), products.await())
    }
}
```

### 5. Использование @Binds вместо @Provides

`@Binds` генерирует меньше кода чем `@Provides`.

```kotlin
// ❌ МЕДЛЕННЕЕ - @Provides
@Module
@InstallIn(SingletonComponent::class)
object RepositoryModule {
    @Provides
    @Singleton
    fun provideUserRepository(impl: UserRepositoryImpl): UserRepository {
        return impl
    }
}

// ✓ БЫСТРЕЕ - @Binds
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {
    @Binds
    @Singleton
    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository
}
```

### 6. Ограничение Scopes

Используйте минимально необходимые scope'ы.

```kotlin
// ❌ НЕПРАВИЛЬНО - слишком много singleton'ов
@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    @Provides
    @Singleton
    fun provideAdapter(): MyAdapter = MyAdapter() // Зачем singleton для adapter?

    @Provides
    @Singleton
    fun provideFormatter(): DateFormatter = DateFormatter() // Тоже не нужен
}

// ✓ ПРАВИЛЬНО - используйте @Unscoped или подходящий scope
@Module
@InstallIn(ActivityComponent::class)
object ActivityModule {
    @Provides
    @ActivityScoped // Живет только пока Activity
    fun provideAdapter(): MyAdapter = MyAdapter()

    @Provides // Unscoped - создается каждый раз
    fun provideFormatter(): DateFormatter = DateFormatter()
}
```

### 7. Gradle оптимизации

```kotlin
// gradle.properties
org.gradle.jvmargs=-Xmx4096m -XX:MaxMetaspaceSize=1024m -XX:+HeapDumpOnOutOfMemoryError
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.configureondemand=true

# Kapt оптимизации
kapt.incremental.apt=true
kapt.use.worker.api=true
kapt.include.compile.classpath=false

# Android Studio / Gradle
android.enableJetifier=true
android.useAndroidX=true
```

```gradle
// app/build.gradle
android {
    // Incremental annotation processing
    kapt {
        useBuildCache = true
        correctErrorTypes = true

        javacOptions {
            option("-Xmaxerrs", 500)
        }

        arguments {
            arg("dagger.formatGeneratedSource", "disabled")
            arg("dagger.gradle.incremental", "enabled")
        }
    }
}

dependencies {
    // Используйте kapt вместо annotationProcessor
    kapt "com.google.dagger:hilt-compiler:2.48"

    // Не включайте ненужные процессоры
    // kapt "some.unused.processor:1.0"
}
```

### 8. Использование KSP (вместо kapt)

KSP (Kotlin Symbol Processing) значительно быстрее kapt.

```gradle
// build.gradle (project level)
plugins {
    id 'com.google.devtools.ksp' version '1.9.10-1.0.13' apply false
}

// build.gradle (app level)
plugins {
    id 'com.google.devtools.ksp'
}

dependencies {
    // Заменить kapt на ksp для Hilt (когда доступно)
    ksp "com.google.dagger:hilt-compiler:2.48"

    // Room уже поддерживает KSP
    ksp "androidx.room:room-compiler:2.6.0"
}

// ВАЖНО: Убедитесь что Hilt поддерживает KSP в вашей версии
```

### 9. Проверка зависимостей с помощью Build Analyzer

```kotlin
// Android Studio: Build -> Analyze Build...
// Показывает какие задачи занимают больше всего времени

// Пример оптимизации на основе анализа:
// Если видите что kapt занимает 60% времени:

// 1. Проверить лишние annotation processors
configurations.all {
    resolutionStrategy.eachDependency { details ->
        if (details.requested.group == 'com.google.dagger') {
            details.useVersion '2.48' // Latest stable
        }
    }
}

// 2. Исключить транзитивные зависимости
implementation("some.library:name:1.0") {
    exclude group: 'com.google.dagger'
}
```

### 10. Ленивая инициализация

```kotlin
// ❌ НЕПРАВИЛЬНО - все создается сразу
@Singleton
class HeavyService @Inject constructor(
    private val database: AppDatabase,
    private val network: ApiService,
    private val imageLoader: ImageLoader
) {
    init {
        // Тяжелая инициализация при создании
        database.init()
        network.warmup()
        imageLoader.preload()
    }
}

// ✓ ПРАВИЛЬНО - ленивая инициализация
@Singleton
class HeavyService @Inject constructor(
    private val databaseProvider: Provider<AppDatabase>,
    private val networkProvider: Provider<ApiService>,
    private val imageLoaderProvider: Provider<ImageLoader>
) {
    private val database by lazy { databaseProvider.get() }
    private val network by lazy { networkProvider.get() }
    private val imageLoader by lazy { imageLoaderProvider.get() }

    // Инициализация только при первом использовании
}
```

### 11. AssistedInject для runtime параметров

Избегайте фабрик которые требуют много generated кода.

```kotlin
// ❌ МЕДЛЕННЕЕ - ручная фабрика
interface UserViewModelFactory {
    fun create(userId: Int): UserViewModel
}

@Module
@InstallIn(ActivityComponent::class)
abstract class ViewModelModule {
    @Binds
    abstract fun bindUserViewModelFactory(
        factory: UserViewModelFactoryImpl
    ): UserViewModelFactory
}

// ✓ БЫСТРЕЕ - AssistedInject
class UserViewModel @AssistedInject constructor(
    private val repository: UserRepository,
    @Assisted private val userId: Int
) : ViewModel() {

    @AssistedFactory
    interface Factory {
        fun create(userId: Int): UserViewModel
    }
}

// Использование
@AndroidEntryPoint
class UserActivity : AppCompatActivity() {
    @Inject lateinit var viewModelFactory: UserViewModel.Factory

    private val viewModel by lazy {
        viewModelFactory.create(intent.getIntExtra("user_id", 0))
    }
}
```

### 12. Минимизация Multibindings

```kotlin
// ❌ МЕДЛЕННО - слишком много bindings
@Module
@InstallIn(SingletonComponent::class)
abstract class FeatureModule {
    @Binds
    @IntoSet
    abstract fun bindFeature1(impl: Feature1): Feature

    @Binds
    @IntoSet
    abstract fun bindFeature2(impl: Feature2): Feature

    // ... 50+ bindings
}

// ✓ БЫСТРЕЕ - группировка или использование Map
@Module
@InstallIn(SingletonComponent::class)
abstract class FeatureModule {
    @Binds
    @IntoMap
    @StringKey("feature1")
    abstract fun bindFeature1(impl: Feature1): Feature

    @Binds
    @IntoMap
    @StringKey("feature2")
    abstract fun bindFeature2(impl: Feature2): Feature
}
```

### Метрики улучшения

**До оптимизации:**
```
Build time: 2m 30s
kapt tasks: 1m 45s (70%)
Dagger components: 15
Total @Provides: 200+
```

**После оптимизации:**
```
Build time: 1m 10s (-53%)
ksp tasks: 35s (-66%)
Dagger components: 5
Total @Provides: 80
@Binds: 40 (вместо @Provides)
```

### Checklist оптимизации

- [ ] Переход с Dagger на Hilt
- [ ] Включить incremental kapt
- [ ] Разделить большие модули
- [ ] Заменить @Provides на @Binds где возможно
- [ ] Использовать Provider<T> для ленивой инициализации
- [ ] Минимизировать singleton scopes
- [ ] Проверить Build Analyzer
- [ ] Настроить gradle.properties
- [ ] Рассмотреть миграцию на KSP
- [ ] Удалить неиспользуемые зависимости
- [ ] Использовать AssistedInject для runtime параметров
- [ ] Оптимизировать Multibindings

**English**: Optimize Dagger build time by: 1) **Use Hilt** instead of Dagger, 2) **Enable incremental kapt** (`kapt.incremental.apt=true`), 3) **Split large modules** into smaller ones, 4) **Use @Binds** instead of @Provides (generates less code), 5) **Migrate to KSP** when available (faster than kapt), 6) **Use Provider<T>** for lazy initialization, 7) **Minimize Singleton scopes**, 8) **Remove unused dependencies**, 9) **Configure gradle.properties** (parallel, caching), 10) **Use AssistedInject** for runtime params. Typical improvement: 50-70% faster builds. Check Build Analyzer to identify bottlenecks.
