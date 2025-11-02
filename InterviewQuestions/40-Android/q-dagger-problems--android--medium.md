---
id: android-453
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
updated: 2025-10-30
tags: [android/di-hilt, android/gradle, android/testing-unit, dagger, hilt, challenges, difficulty/medium]
sources: []
date created: Thursday, October 30th 2025, 12:02:30 pm
date modified: Thursday, October 30th 2025, 12:47:30 pm
---

# Вопрос (RU)
> Какие проблемы есть у Dagger?

# Question (EN)
> What problems does Dagger have?

---

## Ответ (RU)

Dagger — мощный фреймворк внедрения зависимостей с генерацией кода на этапе компиляции, но его архитектурные особенности создают ряд существенных проблем.

### Основные Проблемы

**1. Крутая Кривая Обучения**

Dagger требует понимания множества взаимосвязанных концепций: иерархия компонентов, скоупы, различие между `@Provides` и `@Binds`, квалификаторы для разрешения конфликтов типов.

```kotlin
// ✅ Правильное использование Qualifier для разрешения конфликтов
@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class IoDispatcher

@Module
object DispatcherModule {
    @Provides
    @IoDispatcher
    fun provideIoDispatcher(): CoroutineDispatcher = Dispatchers.IO
}

// ❌ Без Qualifier — ошибка компиляции при множественных провайдерах
@Provides
fun provideDispatcher1(): CoroutineDispatcher = Dispatchers.IO

@Provides
fun provideDispatcher2(): CoroutineDispatcher = Dispatchers.Default
```

**2. Длительное Время Компиляции**

Генерация кода замедляет сборку, особенно в крупных проектах. Каждое изменение в графе зависимостей требует полной регенерации компонентов, что снижает эффективность инкрементальной компиляции и замедляет CI/CD пайплайны.

**3. Сложность Отладки**

Ошибки проявляются неочевидно. Циклические зависимости могут быть обнаружены только в рантайме, а генерированный код Dagger сложен для чтения и анализа.

```kotlin
// ❌ Циклическая зависимость — выявляется поздно
class UserRepository @Inject constructor(private val api: UserApi)
class UserApi @Inject constructor(private val repository: UserRepository)

// ❌ Отсутствующий провайдер — неясное сообщение об ошибке
@Inject constructor(private val config: AppConfig)  // Где @Provides?
```

**4. Ограниченная Гибкость**

Статическая природа Dagger затрудняет условную инъекцию — параметры недоступны на этапе компиляции.

```kotlin
// ❌ Условная логика требует обходных путей
@Module
object ConfigModule {
    @Provides
    fun provideAnalytics(isDebug: Boolean): Analytics =
        if (isDebug) DebugAnalytics() else ProdAnalytics()
}

// ✅ Используйте multibindings с @IntoMap для выбора в рантайме
@Module
interface AnalyticsModule {
    @Binds @IntoMap @StringKey("debug")
    fun bindDebug(impl: DebugAnalytics): Analytics

    @Binds @IntoMap @StringKey("prod")
    fun bindProd(impl: ProdAnalytics): Analytics
}
```

**5. Накладные Расходы**

Генерированный код увеличивает размер APK. Factory классы создаются для каждой зависимости, что добавляет накладные расходы.

**6. Сложность Тестирования**

Подмена зависимостей требует создания отдельных тестовых модулей и компонентов.

```kotlin
// ❌ Дублирование структуры для тестов
@Component(modules = [TestNetworkModule::class, TestDatabaseModule::class])
interface TestAppComponent : AppComponent

// ✅ Hilt упрощает через @TestInstallIn
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

**Hilt как эволюция:** стандартизированные компоненты, автоматическая интеграция с Android классами, упрощённое тестирование.

**Альтернативы:** Manual DI (полный контроль), Koin (runtime DI), Service Locator (простота для малых проектов).

## Answer (EN)

Dagger is a powerful compile-time dependency injection framework with code generation, but its architectural features create several significant problems.

### Main Problems

**1. Steep Learning Curve**

Dagger requires understanding many interconnected concepts: component hierarchies, scopes, differences between `@Provides` and `@Binds`, qualifiers for resolving type conflicts.

```kotlin
// ✅ Correct Qualifier usage for resolving conflicts
@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class IoDispatcher

@Module
object DispatcherModule {
    @Provides
    @IoDispatcher
    fun provideIoDispatcher(): CoroutineDispatcher = Dispatchers.IO
}

// ❌ Without Qualifier — compilation error with multiple providers
@Provides
fun provideDispatcher1(): CoroutineDispatcher = Dispatchers.IO

@Provides
fun provideDispatcher2(): CoroutineDispatcher = Dispatchers.Default
```

**2. Long Compilation Times**

Code generation slows down builds, especially in large projects. Every change in the dependency graph requires full component regeneration, reducing incremental compilation effectiveness and slowing CI/CD pipelines.

**3. Debugging Complexity**

Errors manifest non-obviously. Circular dependencies may only be detected at runtime, and generated Dagger code is difficult to read and analyze.

```kotlin
// ❌ Circular dependency — detected late
class UserRepository @Inject constructor(private val api: UserApi)
class UserApi @Inject constructor(private val repository: UserRepository)

// ❌ Missing provider — unclear error message
@Inject constructor(private val config: AppConfig)  // Where is @Provides?
```

**4. Limited Flexibility**

Dagger's static nature makes conditional injection difficult — parameters are unavailable at compile-time.

```kotlin
// ❌ Conditional logic requires workarounds
@Module
object ConfigModule {
    @Provides
    fun provideAnalytics(isDebug: Boolean): Analytics =
        if (isDebug) DebugAnalytics() else ProdAnalytics()
}

// ✅ Use multibindings with @IntoMap for runtime selection
@Module
interface AnalyticsModule {
    @Binds @IntoMap @StringKey("debug")
    fun bindDebug(impl: DebugAnalytics): Analytics

    @Binds @IntoMap @StringKey("prod")
    fun bindProd(impl: ProdAnalytics): Analytics
}
```

**5. Performance Overhead**

Generated code increases APK size. Factory classes are created for each dependency, adding overhead.

**6. Testing Complexity**

Replacing dependencies requires creating separate test modules and components.

```kotlin
// ❌ Duplicating structure for tests
@Component(modules = [TestNetworkModule::class, TestDatabaseModule::class])
interface TestAppComponent : AppComponent

// ✅ Hilt simplifies with @TestInstallIn
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

**Hilt as evolution:** standardized components, automatic Android integration, simplified testing.

**Alternatives:** Manual DI (full control), Koin (runtime DI), Service Locator (simplicity for small projects).

---

## Follow-ups

- How does Hilt specifically address Dagger's compilation time issues?
- What are the trade-offs between compile-time and runtime dependency injection?
- When should manual DI be preferred over framework-based solutions?
- How to measure and optimize Dagger's impact on build performance?
- What patterns help manage component scope complexity in large projects?

## References

- [[c-dependency-injection]]
- [[c-software-design-patterns]]
- Official Dagger documentation: https://dagger.dev/
- Hilt documentation: https://dagger.dev/hilt/

## Related Questions

### Prerequisites (Easier)
- [[q-dagger-inject-annotation--android--easy]] — Basic @Inject usage and annotation fundamentals

### Related (Same Level)
- [[q-dagger-field-injection--android--medium]] — Injection strategies and best practices
- [[q-dagger-build-time-optimization--android--medium]] — Build performance optimization techniques

### Advanced (Harder)
- [[q-dagger-framework-overview--android--hard]] — Complete framework architecture and advanced patterns
- Component vs Subcomponent design decisions and scope management
