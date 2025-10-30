---
id: 20251020-200000
title: Dagger Problems / Проблемы Dagger
aliases: ["Dagger Problems", "Проблемы Dagger"]
topic: android
subtopics: [di-hilt, gradle, testing-unit]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related:
  - c-dependency-injection
  - q-dagger-build-time-optimization--android--medium
  - q-dagger-field-injection--android--medium
  - q-dagger-framework-overview--android--hard
created: 2025-10-20
updated: 2025-10-29
tags: [android/di-hilt, android/gradle, android/testing-unit, dagger, hilt, challenges, difficulty/medium]
sources: []
---

# Вопрос (RU)
> Какие проблемы есть у Dagger?

# Question (EN)
> What problems does Dagger have?

---

## Ответ (RU)

Dagger — мощный фреймворк для внедрения зависимостей, но он имеет ряд недостатков, с которыми разработчики сталкиваются в реальных проектах.

### Основные Проблемы

**1. Крутая Кривая Обучения**

Dagger требует понимания множества взаимосвязанных концепций:
- Components, Subcomponents и их иерархии
- Modules и различие между @Provides и @Binds
- Scopes и время жизни зависимостей
- Qualifiers для разрешения конфликтов типов
- Multibindings для коллекций зависимостей

```kotlin
// ✅ Правильное использование Qualifier
@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class IoDispatcher

@Module
object DispatcherModule {
    @Provides
    @IoDispatcher
    fun provideIoDispatcher(): CoroutineDispatcher = Dispatchers.IO
}

// ❌ Без Qualifier — конфликт типов
@Provides
fun provideDispatcher1(): CoroutineDispatcher = Dispatchers.IO

@Provides
fun provideDispatcher2(): CoroutineDispatcher = Dispatchers.Default
```

**2. Длительное Время Компиляции**

Генерация кода на этапе компиляции существенно замедляет сборку:

```kotlin
// Каждое изменение в графе зависимостей требует полной регенерации
@Component(modules = [
    NetworkModule::class,
    DatabaseModule::class,
    RepositoryModule::class,
    ViewModelModule::class  // Изменение здесь → полная пересборка
])
interface AppComponent
```

**Влияние:**
- Инкрементальная компиляция менее эффективна
- CI/CD пайплайны работают дольше
- Feedback loop разработчика замедляется

**3. Сложность Отладки**

Ошибки часто проявляются неочевидно:

```kotlin
// ❌ Циклическая зависимость обнаруживается только в рантайме
class UserRepository @Inject constructor(
    private val api: UserApi
)

class UserApi @Inject constructor(
    private val repository: UserRepository  // Cycle!
)

// ❌ Отсутствующий провайдер — неясная ошибка компиляции
@Inject constructor(
    private val config: AppConfig  // Где @Provides?
)
```

Генерированный код Dagger сложен для чтения, что усложняет диагностику проблем.

**4. Ограниченная Гибкость**

Статическая природа Dagger накладывает ограничения:

```kotlin
// ❌ Условная инъекция требует дополнительной работы
@Module
object ConfigModule {
    @Provides
    fun provideAnalytics(
        isDebug: Boolean  // Параметр недоступен на этапе компиляции
    ): Analytics = if (isDebug) DebugAnalytics() else ProdAnalytics()
}

// ✅ Приходится использовать @Binds с @IntoSet/Map
@Module
interface AnalyticsModule {
    @Binds
    @IntoMap
    @StringKey("debug")
    fun bindDebug(impl: DebugAnalytics): Analytics

    @Binds
    @IntoMap
    @StringKey("prod")
    fun bindProd(impl: ProdAnalytics): Analytics
}
```

**5. Накладные Расходы На Производительность**

Влияние на runtime и размер APK:

- Генерированный код увеличивает размер APK
- Factory классы создаются для каждой зависимости
- Reflection используется в некоторых случаях (assisted injection)

**6. Сложность Тестирования**

Подмена зависимостей требует дополнительной настройки:

```kotlin
// ❌ Тестовый компонент дублирует production структуру
@Component(modules = [
    TestNetworkModule::class,      // Нужны отдельные модули
    TestDatabaseModule::class,
    TestRepositoryModule::class
])
interface TestAppComponent : AppComponent

// ✅ Hilt упрощает это с @TestInstallIn
@TestInstallIn(
    components = [SingletonComponent::class],
    replaces = [NetworkModule::class]
)
@Module
object TestNetworkModule {
    @Provides
    fun provideApi(): Api = FakeApi()
}
```

### Решения

**Hilt как эволюция:**
- Стандартизированные компоненты и скоупы
- Автоматическая интеграция с Android классами
- Упрощённое тестирование

**Альтернативы:**
- [[c-dependency-injection|Manual DI]] — полный контроль без магии
- Koin — легковесная runtime DI библиотека
- Service Locator — простой паттерн для небольших проектов

## Answer (EN)

Dagger is a powerful dependency injection framework, but it has several drawbacks that developers encounter in real-world projects.

### Main Problems

**1. Steep Learning Curve**

Dagger requires understanding many interconnected concepts:
- Components, Subcomponents and their hierarchies
- Modules and the difference between @Provides and @Binds
- Scopes and dependency lifecycles
- Qualifiers for resolving type conflicts
- Multibindings for dependency collections

```kotlin
// ✅ Correct Qualifier usage
@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class IoDispatcher

@Module
object DispatcherModule {
    @Provides
    @IoDispatcher
    fun provideIoDispatcher(): CoroutineDispatcher = Dispatchers.IO
}

// ❌ Without Qualifier — type conflict
@Provides
fun provideDispatcher1(): CoroutineDispatcher = Dispatchers.IO

@Provides
fun provideDispatcher2(): CoroutineDispatcher = Dispatchers.Default
```

**2. Long Compilation Times**

Code generation at compile-time significantly slows down builds:

```kotlin
// Every change in dependency graph requires full regeneration
@Component(modules = [
    NetworkModule::class,
    DatabaseModule::class,
    RepositoryModule::class,
    ViewModelModule::class  // Change here → full rebuild
])
interface AppComponent
```

**Impact:**
- Incremental compilation is less effective
- CI/CD pipelines take longer
- Developer feedback loop slows down

**3. Debugging Complexity**

Errors often manifest in non-obvious ways:

```kotlin
// ❌ Circular dependency detected only at runtime
class UserRepository @Inject constructor(
    private val api: UserApi
)

class UserApi @Inject constructor(
    private val repository: UserRepository  // Cycle!
)

// ❌ Missing provider — unclear compilation error
@Inject constructor(
    private val config: AppConfig  // Where is @Provides?
)
```

Generated Dagger code is difficult to read, complicating problem diagnosis.

**4. Limited Flexibility**

Dagger's static nature imposes constraints:

```kotlin
// ❌ Conditional injection requires extra work
@Module
object ConfigModule {
    @Provides
    fun provideAnalytics(
        isDebug: Boolean  // Parameter unavailable at compile-time
    ): Analytics = if (isDebug) DebugAnalytics() else ProdAnalytics()
}

// ✅ Must use @Binds with @IntoSet/Map
@Module
interface AnalyticsModule {
    @Binds
    @IntoMap
    @StringKey("debug")
    fun bindDebug(impl: DebugAnalytics): Analytics

    @Binds
    @IntoMap
    @StringKey("prod")
    fun bindProd(impl: ProdAnalytics): Analytics
}
```

**5. Performance Overhead**

Impact on runtime and APK size:

- Generated code increases APK size
- Factory classes created for each dependency
- Reflection used in some cases (assisted injection)

**6. Testing Complexity**

Replacing dependencies requires additional setup:

```kotlin
// ❌ Test component duplicates production structure
@Component(modules = [
    TestNetworkModule::class,      // Need separate modules
    TestDatabaseModule::class,
    TestRepositoryModule::class
])
interface TestAppComponent : AppComponent

// ✅ Hilt simplifies this with @TestInstallIn
@TestInstallIn(
    components = [SingletonComponent::class],
    replaces = [NetworkModule::class]
)
@Module
object TestNetworkModule {
    @Provides
    fun provideApi(): Api = FakeApi()
}
```

### Solutions

**Hilt as evolution:**
- Standardized components and scopes
- Automatic integration with Android classes
- Simplified testing

**Alternatives:**
- [[c-dependency-injection|Manual DI]] — full control without magic
- Koin — lightweight runtime DI library
- Service Locator — simple pattern for small projects

---

## Follow-ups

- How does Hilt address the main Dagger problems?
- What are the trade-offs between compile-time and runtime DI?
- When should you choose manual DI over Dagger?
- How to optimize Dagger build times in large projects?
- What testing strategies work best with Dagger components?

## References

- [[c-dependency-injection]]
- [[c-software-design-patterns]]
- Official Dagger documentation: https://dagger.dev/
- Hilt documentation: https://dagger.dev/hilt/

## Related Questions

### Prerequisites (Easier)
- [[q-dagger-inject-annotation--android--easy]] — Basic @Inject usage
- Understanding dependency injection patterns

### Related (Same Level)
- [[q-dagger-field-injection--android--medium]] — Injection strategies
- [[q-dagger-build-time-optimization--android--medium]] — Build performance

### Advanced (Harder)
- [[q-dagger-framework-overview--android--hard]] — Complete framework architecture
- Component vs Subcomponent design decisions
