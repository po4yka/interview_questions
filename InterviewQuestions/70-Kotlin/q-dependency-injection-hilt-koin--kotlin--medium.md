---
id: kotlin-250
title: Dependency Injection Hilt vs Koin / DI Hilt против Koin
aliases:
- Hilt vs Koin
- Dependency Injection Android
- DI Hilt против Koin
topic: kotlin
subtopics:
- dependency-injection
- hilt
- koin
- architecture
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-kotlin
- c-architecture
created: 2026-01-23
updated: 2026-01-23
tags:
- kotlin
- hilt
- koin
- dependency-injection
- difficulty/medium
anki_cards:
- slug: kotlin-250-0-en
  language: en
  anki_id: 1769170314596
  synced_at: '2026-01-23T17:03:50.916540'
- slug: kotlin-250-0-ru
  language: ru
  anki_id: 1769170314621
  synced_at: '2026-01-23T17:03:50.918433'
---
# Вопрос (RU)
> В чём разница между Hilt и Koin? Когда использовать каждый фреймворк?

# Question (EN)
> What is the difference between Hilt and Koin? When should you use each framework?

---

## Ответ (RU)

**Hilt** - DI фреймворк на основе Dagger с генерацией кода в compile-time.
**Koin** - легковесный service locator с DSL конфигурацией в runtime.

**Сравнение:**

| Аспект | Hilt | Koin |
|--------|------|------|
| Тип | Compile-time DI | Runtime service locator |
| Проверка зависимостей | При компиляции | При запуске |
| Производительность | Быстрее в runtime | Медленнее старт |
| Кривая обучения | Сложнее | Проще |
| Размер | Больше (codegen) | Меньше |

**Hilt пример:**
```kotlin
// Модуль
@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    @Provides
    @Singleton
    fun provideApi(): ApiService = Retrofit.Builder()
        .baseUrl("https://api.example.com")
        .build()
        .create(ApiService::class.java)
}

// Использование
@HiltViewModel
class MainViewModel @Inject constructor(
    private val api: ApiService
) : ViewModel()

@AndroidEntryPoint
class MainActivity : AppCompatActivity()
```

**Koin пример:**
```kotlin
// Модуль
val appModule = module {
    single<ApiService> {
        Retrofit.Builder()
            .baseUrl("https://api.example.com")
            .build()
            .create(ApiService::class.java)
    }

    viewModel { MainViewModel(get()) }
}

// Инициализация
class App : Application() {
    override fun onCreate() {
        super.onCreate()
        startKoin {
            modules(appModule)
        }
    }
}

// Использование
class MainViewModel(private val api: ApiService) : ViewModel()

class MainActivity : AppCompatActivity() {
    private val viewModel: MainViewModel by viewModel()
}
```

**Когда использовать:**
- **Hilt**: Большие проекты, compile-time безопасность, команда знает Dagger
- **Koin**: Маленькие/средние проекты, быстрый старт, простота

## Answer (EN)

**Hilt** - DI framework based on Dagger with compile-time code generation.
**Koin** - lightweight service locator with runtime DSL configuration.

**Comparison:**

| Aspect | Hilt | Koin |
|--------|------|------|
| Type | Compile-time DI | Runtime service locator |
| Dependency validation | At compile time | At runtime |
| Performance | Faster at runtime | Slower startup |
| Learning curve | Steeper | Easier |
| Size | Larger (codegen) | Smaller |

**Hilt Example:**
```kotlin
// Module
@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    @Provides
    @Singleton
    fun provideApi(): ApiService = Retrofit.Builder()
        .baseUrl("https://api.example.com")
        .build()
        .create(ApiService::class.java)
}

// Usage
@HiltViewModel
class MainViewModel @Inject constructor(
    private val api: ApiService
) : ViewModel()

@AndroidEntryPoint
class MainActivity : AppCompatActivity()
```

**Koin Example:**
```kotlin
// Module
val appModule = module {
    single<ApiService> {
        Retrofit.Builder()
            .baseUrl("https://api.example.com")
            .build()
            .create(ApiService::class.java)
    }

    viewModel { MainViewModel(get()) }
}

// Initialization
class App : Application() {
    override fun onCreate() {
        super.onCreate()
        startKoin {
            modules(appModule)
        }
    }
}

// Usage
class MainViewModel(private val api: ApiService) : ViewModel()

class MainActivity : AppCompatActivity() {
    private val viewModel: MainViewModel by viewModel()
}
```

**When to Use:**
- **Hilt**: Large projects, compile-time safety, team knows Dagger
- **Koin**: Small/medium projects, quick setup, simplicity

---

## Follow-ups

- How do you test with Hilt vs Koin?
- What are Hilt scopes and how do they map to Android components?
- How does Koin handle circular dependencies?
