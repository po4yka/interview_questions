---
id: 20251012-122748
title: "Dagger Build Time Optimization"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
updated: 2025-10-15
tags: [dagger, hilt, dependency-injection, build-optimization, performance, android/hilt, android/dependency-injection, android/build-optimization, difficulty/medium]
aliases: []
original_language: en
language_tags: [en, ru]
question_kind: android
moc: moc-android
subtopics:   - dagger
  - hilt
  - dependency-injection
  - build-optimization
related: []
---

# Question (EN)

> How to minimize Dagger's impact on build time?

# Вопрос (RU)

> Оптимизация времени сборки с Dagger

---

## Answer (EN)

To minimize Dagger's impact on build time, you can use several strategies and practices that help optimize the compilation process.

### 1. Use Hilt instead of Dagger

Hilt simplifies setup and reduces boilerplate code, which speeds up compilation.

```kotlin
//  Dagger - много кода, медленная компиляция
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

//  Hilt - меньше кода, быстрее компилируется
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

### 2. Module Separation (Modularization)

Split large modules into several smaller, logically connected components.

```kotlin
//  НЕПРАВИЛЬНО - один огромный модуль
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

//  ПРАВИЛЬНО - разделенные модули
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

### 3. Use Components with Subcomponents

Isolate changes in different parts of the application.

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

### 4. Avoid Excessive Dependencies

```kotlin
//  НЕПРАВИЛЬНО - слишком много зависимостей в конструкторе
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

//  ПРАВИЛЬНО - использовать Facade или UseCase паттерн
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

### 5. Use @Binds instead of @Provides

`@Binds` generates less code than `@Provides`.

```kotlin
//  МЕДЛЕННЕЕ - @Provides
@Module
@InstallIn(SingletonComponent::class)
object RepositoryModule {
    @Provides
    @Singleton
    fun provideUserRepository(impl: UserRepositoryImpl): UserRepository {
        return impl
    }
}

//  БЫСТРЕЕ - @Binds
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {
    @Binds
    @Singleton
    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository
}
```

### 6. Limit Scopes

Use the minimum necessary scopes.

```kotlin
//  НЕПРАВИЛЬНО - слишком много singleton'ов
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

//  ПРАВИЛЬНО - используйте @Unscoped или подходящий scope
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

### 7. Gradle Optimizations

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
```

### 8. Use KSP (instead of kapt)

KSP (Kotlin Symbol Processing) is significantly faster than kapt.

```gradle
// build.gradle (project level)
plugins {
    id 'com.google.devtools.ksp' version '1.9.10-1.0.13' apply false
}

// build.gradle (app level)
plugins {
    id 'com.google.devtools.ksp'
}

// ВАЖНО: Убедитесь что Hilt поддерживает KSP в вашей версии
```

### 9. Check Dependencies with Build Analyzer

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

### 10. Lazy Initialization

```kotlin
//  НЕПРАВИЛЬНО - все создается сразу
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

//  ПРАВИЛЬНО - ленивая инициализация
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

### 11. AssistedInject for Runtime Parameters

Avoid factories that require a lot of generated code.

```kotlin
//  МЕДЛЕННЕЕ - ручная фабрика
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

//  БЫСТРЕЕ - AssistedInject
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

### 12. Minimize Multibindings

```kotlin
//  МЕДЛЕННО - слишком много bindings
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

//  БЫСТРЕЕ - группировка или использование Map
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

### Improvement Metrics

**Before optimization:**

```
Build time: 2m 30s
kapt tasks: 1m 45s (70%)
Dagger components: 15
Total @Provides: 200+
```

**After optimization:**

```
Build time: 1m 10s (-53%)
ksp tasks: 35s (-66%)
Dagger components: 5
Total @Provides: 80
@Binds: 40 (вместо @Provides)
```

### Optimization Checklist

-   [ ] Migrate from Dagger to Hilt
-   [ ] Enable incremental kapt
-   [ ] Split large modules
-   [ ] Replace @Provides with @Binds where possible
-   [ ] Use Provider<T> for lazy initialization
-   [ ] Minimize singleton scopes
-   [ ] Check Build Analyzer
-   [ ] Configure gradle.properties
-   [ ] Consider migration to KSP
-   [ ] Remove unused dependencies
-   [ ] Use AssistedInject for runtime parameters
-   [ ] Optimize Multibindings

**English**: Optimize Dagger build time by: 1) **Use Hilt** instead of Dagger, 2) **Enable incremental kapt** (`kapt.incremental.apt=true`), 3) **Split large modules** into smaller ones, 4) **Use @Binds** instead of @Provides (generates less code), 5) **Migrate to KSP** when available (faster than kapt), 6) **Use Provider<T>** for lazy initialization, 7) **Minimize Singleton scopes**, 8) **Remove unused dependencies**, 9) **Configure gradle.properties** (parallel, caching), 10) **Use AssistedInject** for runtime params. Typical improvement: 50-70% faster builds. Check Build Analyzer to identify bottlenecks.

---

## Ответ (RU)

Для минимизации влияния Dagger на время сборки можно использовать несколько стратегий и практик, которые помогают оптимизировать процесс компиляции.

### Основные стратегии оптимизации

**1. Использовать Hilt вместо Dagger**

Hilt упрощает настройку и уменьшает boilerplate код, что ускоряет компиляцию. Hilt автоматически генерирует компоненты и модули, которые пришлось бы писать вручную в Dagger, что значительно сокращает объём генерируемого кода.

**2. Разделение модулей (Modularization)**

Разбиение больших модулей на несколько меньших, логически связанных компонентов позволяет:
- Изолировать изменения в разных частях приложения
- Уменьшить область перекомпиляции
- Ускорить инкрементальную сборку

Вместо одного огромного модуля с 50+ `@Provides` методами, создайте отдельные модули для Network, Database, Image loading и других функциональностей.

**3. Использование @Binds вместо @Provides**

`@Binds` генерирует меньше кода, чем `@Provides`, так как это абстрактный метод, который просто сообщает Dagger о связи между интерфейсом и реализацией. В отличие от `@Provides`, который требует создания экземпляра провайдера, `@Binds` использует более эффективный механизм делегирования.

**4. Использование компонентов с Subcomponents**

Изолируйте изменения в разных частях приложения, используя scope-based компоненты:
- `@ActivityScoped` для зависимостей уровня Activity
- `@FragmentScoped` для зависимостей уровня Fragment
- `@ViewModelScoped` для ViewModel зависимостей

Изменения в одном scope не вызывают перекомпиляцию других scope'ов.

**5. Избегание избыточных зависимостей**

Слишком много зависимостей в конструкторе приводит к большому объёму генерируемого Dagger кода. Используйте паттерны Facade или UseCase для группировки связанных зависимостей.

**6. Ограничение Scopes**

Используйте минимально необходимые scopes. Не делайте всё Singleton'ом если это не требуется. Чем больше Singleton зависимостей, тем больше кода генерирует Dagger для их управления.

**7. Оптимизации Gradle**

Критически важные настройки в `gradle.properties`:
- `org.gradle.parallel=true` - параллельная сборка модулей
- `org.gradle.caching=true` - кэширование результатов сборки
- `kapt.incremental.apt=true` - инкрементальная обработка аннотаций
- `kapt.use.worker.api=true` - использование Gradle Worker API

Дополнительные аргументы kapt:
- `dagger.formatGeneratedSource=disabled` - отключить форматирование генерируемого кода
- `dagger.gradle.incremental=enabled` - включить инкрементальную генерацию Dagger

**8. Миграция на KSP**

KSP (Kotlin Symbol Processing) значительно быстрее kapt. Dagger и Hilt постепенно добавляют поддержку KSP. KSP быстрее по причинам:
- Нативная интеграция с Kotlin компилятором
- Отсутствие промежуточной генерации Java-заглушек
- Более эффективный анализ кода

**9. Build Analyzer**

Используйте Android Studio Build Analyzer (Build → Analyze Build) для выявления узких мест:
- Какие задачи занимают больше всего времени
- Сколько времени тратится на kapt/ksp
- Какие модули замедляют сборку

Это помогает принимать обоснованные решения об оптимизации.

**10. Ленивая инициализация с Provider<T>**

Используйте `Provider<T>` для отложенного создания тяжелых зависимостей. Вместо создания всех зависимостей при инициализации компонента, они создаются только при первом обращении к Provider.

**11. AssistedInject для runtime параметров**

AssistedInject избавляет от необходимости писать ручные фабрики, которые требуют большого объёма генерируемого кода. Dagger генерирует фабрику автоматически с минимальным overhead'ом.

**12. Минимизация Multibindings**

Слишком много bindings в Set или Map замедляет компиляцию. Используйте Map вместо множества отдельных Set bindings, группируйте связанные зависимости.

### Метрики улучшения

**До оптимизации:**
- Время сборки: 2m 30s
- Задачи kapt: 1m 45s (70%)
- Dagger компонентов: 15
- Всего @Provides: 200+

**После оптимизации:**
- Время сборки: 1m 10s (-53%)
- Задачи ksp: 35s (-66%)
- Dagger компонентов: 5
- Всего @Provides: 80
- @Binds: 40 (вместо @Provides)

### Чек-лист оптимизации

- Мигрировать с Dagger на Hilt
- Включить инкрементальный kapt
- Разбить большие модули
- Заменить @Provides на @Binds где возможно
- Использовать Provider<T> для ленивой инициализации
- Минимизировать singleton scopes
- Проверить Build Analyzer
- Настроить gradle.properties
- Рассмотреть миграцию на KSP
- Удалить неиспользуемые зависимости
- Использовать AssistedInject для runtime параметров
- Оптимизировать Multibindings

Типичное улучшение составляет 50-70% ускорения сборки. Используйте Build Analyzer для выявления конкретных узких мест в вашем проекте.

---

## Follow-ups

-   How does Dagger's annotation processing compare to Koin's runtime DI in terms of build time?
-   What are the trade-offs between using @Binds vs @Provides for performance?
-   How can you profile and measure Dagger's impact on your specific build times?

## References

-   `https://dagger.dev/hilt/` — Hilt documentation
-   `https://developer.android.com/training/dependency-injection/hilt-android` — Hilt guide
-   `https://github.com/google/dagger` — Dagger GitHub repository

## Related Questions

### Related (Medium)

-   [[q-android-build-optimization--android--medium]] - Android build optimization
-   [[q-build-optimization-gradle--gradle--medium]] - Gradle optimization
