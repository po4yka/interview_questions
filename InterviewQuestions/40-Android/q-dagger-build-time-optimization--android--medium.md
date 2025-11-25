---
id: android-439
title: Dagger Build Time Optimization / Оптимизация времени сборки Dagger
aliases: [Dagger Build Time Optimization, Оптимизация времени сборки Dagger]
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
status: draft
moc: moc-android
related:
  - c-dependency-injection
  - c-gradle
  - q-android-build-optimization--android--medium
  - q-build-optimization-gradle--android--medium
  - q-dagger-framework-overview--android--hard
  - q-dagger-problems--android--medium
  - q-kapt-ksp-migration--android--medium
created: 2025-10-20
updated: 2025-11-10
tags: [android/di-hilt, android/gradle, difficulty/medium]
sources:
  - "https://dagger.dev/hilt/"
date created: Saturday, November 1st 2025, 12:46:47 pm
date modified: Tuesday, November 25th 2025, 8:54:01 pm
---

# Вопрос (RU)
> Как минимизировать влияние Dagger на время сборки?

# Question (EN)
> How to minimize Dagger's impact on build time?

## Ответ (RU)

Dagger генерирует код через annotation processing (kapt/ksp), что замедляет инкрементальные сборки. Ключевые стратегии оптимизации: миграция на Hilt (там, где это уместно), модуляризация, аккуратное использование scopes (не раздувать Singleton-граф), и переход на KSP вместо KAPT.

Связано с концепциями [[c-dependency-injection]], [[c-gradle]].

### Основные Источники Замедления

**Annotation Processing**
- Каждый `@Provides` и связанный с ним тип добавляют элементы в сгенерированные фабрики и компоненты (больше методов/классов, больше работы генератора)
- Компоненты создают фабрики и реализации компонентов (например, `DaggerAppComponent`)
- Большой и сильно связанный граф зависимостей увеличивает объём генерируемого кода и время обработки

**Проблемы Инкрементальности**
- KAPT не поддерживает полностью инкрементальную компиляцию для всех кейсов
- Изменение в одном модуле может триггерить перекомпиляцию зависимых графов
- Неправильная модульная структура и чрезмерное количество биндов в одном компоненте усугубляют проблему

### Практические Стратегии

**1. Hilt вместо ручного Dagger, где возможно**
```kotlin
// ✅ Минимум boilerplate, оптимизированная генерация
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository
}
```

**2. Предпочитайте @Binds над @Provides для интерфейсных зависимостей**
```kotlin
@Module
abstract class DataModule {
    @Binds  // ✅ Легковесная делегация без лишней логики
    abstract fun bindRepo(impl: RepoImpl): Repository
}
```

**3. Миграция на KSP**
KSP обычно быстрее KAPT для annotation processing и лучше поддерживает инкрементальность. Hilt поддерживает KSP начиная с соответствующих версий плагина и библиотек; при миграции нужно проверить совместимость версий AGP/Dagger/Hilt.

**4. Корректная работа со scope и графами**
- Не складывайте весь граф в один `@Singleton`-компонент; выносите фичи в отдельные компоненты/модули
- Локализуйте зависимости по модулям так, чтобы изменения в фиче не пересобирали весь граф приложения

**5. Gradle Конфигурация**
```properties
# gradle.properties
kapt.incremental.apt=true
kapt.use.worker.api=true
org.gradle.caching=true
```

```kotlin
// build.gradle.kts
kapt {
    arguments {
        arg("dagger.gradle.incremental", "enabled")
    }
}
```

### Измерение Эффекта

Используйте Android Studio Build Analyzer или `./gradlew build --scan` для профилирования kapt/ksp задач. Типичные наблюдаемые улучшения при миграции на KSP и оптимизации графа могут составлять десятки процентов сокращения времени annotation processing, но конкретные цифры зависят от проекта.

## Answer (EN)

Dagger generates code via annotation processing (kapt/ksp), which can slow down incremental builds. Key optimization strategies: migrate to Hilt where appropriate, design proper modularization, use scopes carefully (avoid an oversized Singleton graph), and switch from KAPT to KSP.

Related to concepts [[c-dependency-injection]], [[c-gradle]].

### Core Build Slowdowns

**Annotation Processing**
- Each `@Provides` and its types contribute entries to generated factories and components (more methods/classes => more work for the processor)
- Components produce factory classes and component implementations (e.g., `DaggerAppComponent`)
- Large, tightly coupled dependency graphs increase generated code volume and processing time

**Incrementality Issues**
- KAPT does not provide fully incremental compilation for all scenarios
- A change in one module can trigger recompilation of dependent graphs
- Poor modularization and too many bindings in a single component worsen the impact

### Practical Strategies

**1. Hilt Over Manual Dagger Where It Fits**
```kotlin
// ✅ Minimal boilerplate, optimized generation
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository
}
```

**2. Prefer @Binds Over @Provides for Interface Bindings**
```kotlin
@Module
abstract class DataModule {
    @Binds  // ✅ Lightweight delegation without extra logic
    abstract fun bindRepo(impl: RepoImpl): Repository
}
```

**3. Migrate to KSP**
KSP is typically faster than KAPT for annotation processing and offers better incremental behavior. Hilt supports KSP starting from compatible versions of the Hilt Gradle plugin and libraries; verify AGP/Dagger/Hilt versions when migrating.

**4. Scope and Graph Design**
- Avoid putting everything into a single `@Singleton` component; split features into dedicated components/modules
- Localize dependencies per module so that feature changes do not force regeneration of the entire application graph

**5. Gradle Configuration**
```properties
# gradle.properties
kapt.incremental.apt=true
kapt.use.worker.api=true
org.gradle.caching=true
```

```kotlin
// build.gradle.kts
kapt {
    arguments {
        arg("dagger.gradle.incremental", "enabled")
    }
}
```

### Measuring Impact

Use Android Studio Build Analyzer or `./gradlew build --scan` to profile kapt/ksp tasks. In real projects, migration to KSP and better graph/modular design often yields noticeable reductions (e.g., tens of percent) in annotation processing time, but exact numbers are project-specific.

## Дополнительные Вопросы (RU)

- Какова конкретная разница в производительности между KAPT и KSP для Dagger/Hilt?
- В каких случаях не стоит использовать Singleton scope с точки зрения оптимизации времени сборки?
- Как модуляризация влияет на генерацию кода Dagger?

## Follow-ups

- What is the specific performance difference between KAPT and KSP for Dagger/Hilt?
- When should you avoid using Singleton scope for build time optimization?
- How does modularization impact Dagger's code generation?

## Ссылки (RU)

- [[c-dependency-injection]]
- [[c-gradle]]
- "https://dagger.dev/hilt/"
- "https://developer.android.com/training/dependency-injection/hilt-android"

## References

- [[c-dependency-injection]]
- [[c-gradle]]
- https://dagger.dev/hilt/
- https://developer.android.com/training/dependency-injection/hilt-android

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-android-project-parts--android--easy]]

### Связанные (средний уровень)
- [[q-android-build-optimization--android--medium]]

### Продвинутые (сложнее)
- [[q-dagger-framework-overview--android--hard]]

## Related Questions

### Prerequisites (Easier)
- [[q-android-project-parts--android--easy]]

### Related (Same Level)
- [[q-android-build-optimization--android--medium]]

### Advanced (Harder)
- [[q-dagger-framework-overview--android--hard]]
