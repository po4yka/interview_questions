---
id: 20251020-200000
title: Dagger Build Time Optimization / Оптимизация времени сборки Dagger
aliases:
- Dagger Build Time Optimization
- Оптимизация времени сборки Dagger
topic: android
subtopics:
- di-hilt
- gradle
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- q-android-build-optimization--android--medium
- q-dependency-injection-basics--android--medium
- q-hilt-android--android--medium
created: 2025-10-20
updated: 2025-10-20
tags:
- android/di-hilt
- android/gradle
- difficulty/medium
source: https://dagger.dev/hilt/
source_note: Hilt documentation
---
# Вопрос (RU)
> Как минимизировать влияние Dagger на время сборки?

# Question (EN)
> How to minimize Dagger's impact on build time?

## Ответ (RU)

Минимизация влияния Dagger на время сборки требует комплексного подхода, включающего оптимизацию архитектуры, конфигурации и инструментов сборки.

Связано с концепциями [[c-dependency-injection]], [[c-gradle-optimization]] и [[c-annotation-processing]].

### Теория: Источники замедления сборки

**Annotation Processing Overhead**
- Dagger генерирует код на этапе компиляции
- Каждый `@Provides` метод создает провайдер
- Каждый компонент генерирует фабрику
- Большое количество зависимостей увеличивает граф

**Incremental Build Impact**
- Изменения в одном модуле могут перекомпилировать весь граф зависимостей
- Отсутствие инкрементальности в kapt
- Неоптимальная модульная структура

### Ключевые стратегии оптимизации

**1. Миграция на Hilt**
Hilt автоматизирует создание компонентов и упрощает архитектуру:

```kotlin
// Вместо ручного создания компонентов
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository
}
```

**2. Модульная архитектура**
Разделение на логические модули уменьшает область перекомпиляции:

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Singleton
    fun provideRetrofit(): Retrofit { /* ... */ }
}
```

**3. Использование @Binds**
`@Binds` генерирует меньше кода чем `@Provides`:

```kotlin
@Module
abstract class RepositoryModule {
    @Binds
    @Singleton
    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository
}
```

**4. Оптимизация Scopes**
Минимизация Singleton зависимостей:

```kotlin
@Module
@InstallIn(ActivityComponent::class)
object ActivityModule {
    @Provides
    @ActivityScoped
    fun provideAdapter(): MyAdapter = MyAdapter()
}
```

### Конфигурация сборки

**Gradle настройки:**
```properties
# gradle.properties
org.gradle.parallel=true
org.gradle.caching=true
kapt.incremental.apt=true
kapt.use.worker.api=true
```

**Kapt оптимизации:**
```gradle
kapt {
    useBuildCache = true
    correctErrorTypes = true
    arguments {
        arg("dagger.gradle.incremental", "enabled")
    }
}
```

### Производительность

**Типичные улучшения:**
- Время сборки: -50-70%
- Kapt задачи: -60-80%
- Генерируемый код: -40-60%

**Мониторинг:**
- Build Analyzer в Android Studio
- Gradle Build Scan
- Профилирование kapt/ksp задач

## Answer (EN)

Minimizing Dagger's impact on build time requires a comprehensive approach including architecture optimization, build configuration, and tooling improvements.

Related to concepts [[c-dependency-injection]], [[c-gradle-optimization]], and [[c-annotation-processing]].

### Theory: Sources of Build Slowdown

**Annotation Processing Overhead**
- Dagger generates code during compilation
- Each `@Provides` method creates a provider
- Each component generates a factory
- Large dependency graphs increase complexity

**Incremental Build Impact**
- Changes in one module can recompile the entire dependency graph
- Lack of incrementality in kapt
- Suboptimal modular structure

### Key Optimization Strategies

**1. Migration to Hilt**
Hilt automates component creation and simplifies architecture:

```kotlin
// Instead of manual component creation
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository
}
```

**2. Modular Architecture**
Logical module separation reduces recompilation scope:

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Singleton
    fun provideRetrofit(): Retrofit { /* ... */ }
}
```

**3. Using @Binds**
`@Binds` generates less code than `@Provides`:

```kotlin
@Module
abstract class RepositoryModule {
    @Binds
    @Singleton
    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository
}
```

**4. Scope Optimization**
Minimizing Singleton dependencies:

```kotlin
@Module
@InstallIn(ActivityComponent::class)
object ActivityModule {
    @Provides
    @ActivityScoped
    fun provideAdapter(): MyAdapter = MyAdapter()
}
```

### Build Configuration

**Gradle settings:**
```properties
# gradle.properties
org.gradle.parallel=true
org.gradle.caching=true
kapt.incremental.apt=true
kapt.use.worker.api=true
```

**Kapt optimizations:**
```gradle
kapt {
    useBuildCache = true
    correctErrorTypes = true
    arguments {
        arg("dagger.gradle.incremental", "enabled")
    }
}
```

### Performance

**Typical improvements:**
- Build time: -50-70%
- Kapt tasks: -60-80%
- Generated code: -40-60%

**Monitoring:**
- Build Analyzer in Android Studio
- Gradle Build Scan
- Profiling kapt/ksp tasks

## Follow-ups

- How does Dagger's annotation processing compare to Koin's runtime DI in terms of build time?
- What are the trade-offs between using @Binds vs @Provides for performance?
- How can you profile and measure Dagger's impact on your specific build times?

## References

- [Hilt Documentation](https://dagger.dev/hilt/)
- [Android Hilt Guide](https://developer.android.com/training/dependency-injection/hilt-android)

## Related Questions

### Prerequisites (Easier)
- [[q-android-project-parts--android--easy]]

### Related (Same Level)
- [[q-android-build-optimization--android--medium]]
- [[q-gradle-build-system--android--medium]]

### Advanced (Harder)
- [[q-dagger-framework-overview--android--hard]]
