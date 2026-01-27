---
id: android-di-003
title: Manual DI vs Framework / Ручной DI против фреймворка
aliases:
- Manual DI vs Framework
- Constructor Injection
- Ручной DI
- DI без фреймворка
topic: android
subtopics:
- di-hilt
- architecture-clean
question_kind: comparison
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-dependency-injection
- q-di-framework-selection--di--medium
- q-dagger-purpose--android--easy
- q-repository-pattern--android--medium
created: 2026-01-23
updated: 2026-01-23
tags:
- android/di-hilt
- android/architecture-clean
- dependency-injection
- difficulty/medium
- architecture
anki_cards:
- slug: android-di-003-0-en
  language: en
- slug: android-di-003-0-ru
  language: ru
---
# Вопрос (RU)
> Когда стоит использовать ручной DI (Manual DI) вместо фреймворка? Какие преимущества и недостатки у каждого подхода?

# Question (EN)
> When should you use Manual DI instead of a framework? What are the pros and cons of each approach?

---

## Ответ (RU)

### Что Такое Manual DI

Manual DI (ручная инъекция зависимостей) - это паттерн, где зависимости передаются через конструктор или методы без использования DI-фреймворков.

```kotlin
// Manual DI: зависимости передаются явно
class UserViewModel(
    private val repository: UserRepository,
    private val analytics: Analytics
) : ViewModel()

// Создание в контейнере
class AppContainer(context: Context) {
    private val api = ApiClient.create()
    private val db = AppDatabase.create(context)
    private val analytics = FirebaseAnalytics(context)

    val userRepository: UserRepository by lazy {
        UserRepositoryImpl(api, db.userDao())
    }

    fun createUserViewModel() = UserViewModel(userRepository, analytics)
}
```

### Сравнение Подходов

| Аспект | Manual DI | Фреймворк (Hilt/Koin) |
|--------|-----------|----------------------|
| **Зависимости** | Нет | +1 библиотека |
| **Время сборки** | Без overhead | +10-60 сек (Hilt) |
| **Boilerplate** | Больше | Меньше |
| **Compile-time safety** | Через конструктор | Hilt: да, Koin: нет |
| **Магия** | Нет | Codegen / Runtime |
| **Тестируемость** | Отличная | Отличная |
| **Масштабируемость** | Ограниченная | Хорошая |

### Когда Использовать Manual DI

**Подходит:**
- Простые приложения (<15-20 зависимостей)
- SDK и библиотеки
- Микросервисы на Kotlin
- Проекты, где критично время сборки
- Учебные проекты
- Когда команда не знает DI-фреймворки

**Не подходит:**
- Сложные приложения (>50 зависимостей)
- Multi-module проекты
- Проекты с частой ротацией команды
- Когда нужны scoped зависимости

### Паттерны Manual DI

**1. Application Container:**
```kotlin
class MyApplication : Application() {
    lateinit var container: AppContainer
        private set

    override fun onCreate() {
        super.onCreate()
        container = AppContainer(this)
    }
}

class AppContainer(private val context: Context) {
    // Singleton dependencies
    private val retrofit by lazy {
        Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .build()
    }

    private val database by lazy {
        Room.databaseBuilder(context, AppDatabase::class.java, "app.db")
            .build()
    }

    val userRepository: UserRepository by lazy {
        UserRepositoryImpl(
            api = retrofit.create(UserApi::class.java),
            dao = database.userDao()
        )
    }

    val authRepository: AuthRepository by lazy {
        AuthRepositoryImpl(
            api = retrofit.create(AuthApi::class.java)
        )
    }
}
```

**2. Factory Methods:**
```kotlin
class ViewModelFactory(
    private val container: AppContainer
) : ViewModelProvider.Factory {

    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        return when {
            modelClass.isAssignableFrom(UserViewModel::class.java) -> {
                UserViewModel(container.userRepository) as T
            }
            modelClass.isAssignableFrom(AuthViewModel::class.java) -> {
                AuthViewModel(container.authRepository) as T
            }
            else -> throw IllegalArgumentException("Unknown ViewModel: $modelClass")
        }
    }
}

// Использование в Activity
class MainActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels {
        ViewModelFactory((application as MyApplication).container)
    }
}
```

**3. Feature Containers (для модулей):**
```kotlin
// Core container
class CoreContainer(context: Context) {
    val api: ApiService by lazy { ApiClient.create() }
    val database: AppDatabase by lazy { AppDatabase.create(context) }
}

// Feature container
class UserFeatureContainer(
    private val core: CoreContainer
) {
    val userRepository: UserRepository by lazy {
        UserRepositoryImpl(core.api, core.database.userDao())
    }

    fun createUserViewModel() = UserViewModel(userRepository)
}

// Использование
class UserActivity : AppCompatActivity() {
    private val featureContainer by lazy {
        UserFeatureContainer((application as MyApplication).coreContainer)
    }

    private val viewModel: UserViewModel by viewModels {
        viewModelFactory { featureContainer.createUserViewModel() }
    }
}
```

### Manual DI + Compose

```kotlin
// CompositionLocal для контейнера
val LocalAppContainer = staticCompositionLocalOf<AppContainer> {
    error("AppContainer not provided")
}

@Composable
fun App(container: AppContainer) {
    CompositionLocalProvider(LocalAppContainer provides container) {
        MainNavigation()
    }
}

@Composable
fun UserScreen() {
    val container = LocalAppContainer.current
    val viewModel = viewModel { container.createUserViewModel() }

    val state by viewModel.state.collectAsStateWithLifecycle()
    // UI
}
```

### Когда Мигрировать на Фреймворк

Признаки того, что Manual DI перерос проект:

| Признак | Описание |
|---------|----------|
| **>30 зависимостей** | Container становится сложным |
| **Дублирование** | Factory-код повторяется |
| **Scope проблемы** | Сложно управлять lifecycle |
| **Тестирование** | Много boilerplate для mocks |
| **Multi-module** | Сложно организовать контейнеры |

### Рекомендации (2026)

**Manual DI:**
- Простые приложения и прототипы
- SDK без зависимости от Application
- Kotlin backend микросервисы
- Когда хочется полного контроля

**Фреймворк:**
- Средние и большие приложения
- Команды с разным опытом
- Долгоживущие проекты
- Multi-module архитектура

---

## Answer (EN)

### What is Manual DI

Manual DI is a pattern where dependencies are passed through constructors or methods without using DI frameworks.

```kotlin
// Manual DI: dependencies passed explicitly
class UserViewModel(
    private val repository: UserRepository,
    private val analytics: Analytics
) : ViewModel()

// Creation in container
class AppContainer(context: Context) {
    private val api = ApiClient.create()
    private val db = AppDatabase.create(context)
    private val analytics = FirebaseAnalytics(context)

    val userRepository: UserRepository by lazy {
        UserRepositoryImpl(api, db.userDao())
    }

    fun createUserViewModel() = UserViewModel(userRepository, analytics)
}
```

### Approach Comparison

| Aspect | Manual DI | Framework (Hilt/Koin) |
|--------|-----------|----------------------|
| **Dependencies** | None | +1 library |
| **Build time** | No overhead | +10-60 sec (Hilt) |
| **Boilerplate** | More | Less |
| **Compile-time safety** | Via constructor | Hilt: yes, Koin: no |
| **Magic** | None | Codegen / Runtime |
| **Testability** | Excellent | Excellent |
| **Scalability** | Limited | Good |

### When to Use Manual DI

**Suitable:**
- Simple apps (<15-20 dependencies)
- SDKs and libraries
- Kotlin microservices
- Projects where build time is critical
- Learning projects
- When team doesn't know DI frameworks

**Not suitable:**
- Complex apps (>50 dependencies)
- Multi-module projects
- Projects with frequent team rotation
- When scoped dependencies are needed

### Manual DI Patterns

**1. Application Container:**
```kotlin
class MyApplication : Application() {
    lateinit var container: AppContainer
        private set

    override fun onCreate() {
        super.onCreate()
        container = AppContainer(this)
    }
}

class AppContainer(private val context: Context) {
    // Singleton dependencies
    private val retrofit by lazy {
        Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .build()
    }

    private val database by lazy {
        Room.databaseBuilder(context, AppDatabase::class.java, "app.db")
            .build()
    }

    val userRepository: UserRepository by lazy {
        UserRepositoryImpl(
            api = retrofit.create(UserApi::class.java),
            dao = database.userDao()
        )
    }

    val authRepository: AuthRepository by lazy {
        AuthRepositoryImpl(
            api = retrofit.create(AuthApi::class.java)
        )
    }
}
```

**2. Factory Methods:**
```kotlin
class ViewModelFactory(
    private val container: AppContainer
) : ViewModelProvider.Factory {

    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        return when {
            modelClass.isAssignableFrom(UserViewModel::class.java) -> {
                UserViewModel(container.userRepository) as T
            }
            modelClass.isAssignableFrom(AuthViewModel::class.java) -> {
                AuthViewModel(container.authRepository) as T
            }
            else -> throw IllegalArgumentException("Unknown ViewModel: $modelClass")
        }
    }
}

// Usage in Activity
class MainActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels {
        ViewModelFactory((application as MyApplication).container)
    }
}
```

**3. Feature Containers (for modules):**
```kotlin
// Core container
class CoreContainer(context: Context) {
    val api: ApiService by lazy { ApiClient.create() }
    val database: AppDatabase by lazy { AppDatabase.create(context) }
}

// Feature container
class UserFeatureContainer(
    private val core: CoreContainer
) {
    val userRepository: UserRepository by lazy {
        UserRepositoryImpl(core.api, core.database.userDao())
    }

    fun createUserViewModel() = UserViewModel(userRepository)
}

// Usage
class UserActivity : AppCompatActivity() {
    private val featureContainer by lazy {
        UserFeatureContainer((application as MyApplication).coreContainer)
    }

    private val viewModel: UserViewModel by viewModels {
        viewModelFactory { featureContainer.createUserViewModel() }
    }
}
```

### Manual DI + Compose

```kotlin
// CompositionLocal for container
val LocalAppContainer = staticCompositionLocalOf<AppContainer> {
    error("AppContainer not provided")
}

@Composable
fun App(container: AppContainer) {
    CompositionLocalProvider(LocalAppContainer provides container) {
        MainNavigation()
    }
}

@Composable
fun UserScreen() {
    val container = LocalAppContainer.current
    val viewModel = viewModel { container.createUserViewModel() }

    val state by viewModel.state.collectAsStateWithLifecycle()
    // UI
}
```

### When to Migrate to Framework

Signs that Manual DI has outgrown the project:

| Sign | Description |
|------|-------------|
| **>30 dependencies** | Container becomes complex |
| **Duplication** | Factory code repeats |
| **Scope issues** | Hard to manage lifecycle |
| **Testing** | Lots of mock boilerplate |
| **Multi-module** | Hard to organize containers |

### Recommendations (2026)

**Manual DI:**
- Simple apps and prototypes
- SDKs without Application dependency
- Kotlin backend microservices
- When you want full control

**Framework:**
- Medium to large applications
- Teams with varied experience
- Long-lived projects
- Multi-module architecture

---

## Follow-ups

- Как организовать тестирование с Manual DI?
- Какие паттерны помогают масштабировать Manual DI?
- Как постепенно мигрировать с Manual DI на Hilt?

## References

- [Manual DI Guide](https://developer.android.com/training/dependency-injection/manual)
- [Android Architecture Guide](https://developer.android.com/topic/architecture)

## Related Questions

### Prerequisites
- [[q-dagger-purpose--android--easy]] - Why use DI
- [[c-dependency-injection]] - DI concept

### Related
- [[q-di-framework-selection--di--medium]] - Framework selection guide
- [[q-repository-pattern--android--medium]] - Repository pattern
- [[q-viewmodel-pattern--android--easy]] - ViewModel basics

### Advanced
- [[q-multi-module-best-practices--android--hard]] - Multi-module DI
- [[q-koin-vs-dagger-philosophy--android--hard]] - DI philosophy
