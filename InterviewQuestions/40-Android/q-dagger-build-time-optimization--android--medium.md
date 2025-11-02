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
  - q-android-build-optimization--android--medium
  - q-kapt-ksp-migration--android--medium
  - q-dagger-framework-overview--android--hard
created: 2025-10-20
updated: 2025-01-27
tags: [android/di-hilt, android/gradle, difficulty/medium]
sources:
  - https://dagger.dev/hilt/
date created: Monday, October 27th 2025, 3:27:45 pm
date modified: Thursday, October 30th 2025, 11:51:12 am
---

# Вопрос (RU)
> Как минимизировать влияние Dagger на время сборки?

# Question (EN)
> How to minimize Dagger's impact on build time?

## Ответ (RU)

Dagger генерирует код через annotation processing (kapt/ksp), что замедляет инкрементальные сборки. Ключевые стратегии оптимизации: миграция на Hilt, модуляризация, правильное использование scopes и переход на KSP.

Связано с концепциями [[c-dependency-injection]], [[c-gradle]].

### Основные Источники Замедления

**Annotation Processing**
- Каждый `@Provides` генерирует Provider класс
- Компоненты создают фабрики и DaggerComponent классы
- Большой граф зависимостей умножает объём генерируемого кода

**Проблемы Инкрементальности**
- KAPT не поддерживает полную инкрементальную компиляцию
- Изменение в одном модуле триггерит перекомпиляцию зависимых графов
- Неправильная модульная структура усугубляет проблему

### Практические Стратегии

**1. Hilt вместо Dagger**
```kotlin
// ✅ Минимум boilerplate, оптимизированная генерация
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository
}
```

**2. Предпочитайте @Binds над @Provides**
```kotlin
@Module
abstract class DataModule {
    @Binds  // ✅ Легковесная делегация без лишних классов
    abstract fun bindRepo(impl: RepoImpl): Repository
}
```

**3. Миграция на KSP**
KSP быстрее KAPT в 2-4 раза для annotation processing. Hilt поддерживает KSP начиная с определённой версии.

**4. Gradle Конфигурация**
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

Используйте Android Studio Build Analyzer или `./gradlew build --scan` для профилирования kapt/ksp задач. Типичные улучшения: снижение времени annotation processing на 50-70%.

## Answer (EN)

Dagger generates code via annotation processing (kapt/ksp), which slows down incremental builds. Key optimization strategies: migrate to Hilt, modularize properly, use appropriate scopes, and switch to KSP.

Related to concepts [[c-dependency-injection]], [[c-gradle]].

### Core Build Slowdowns

**Annotation Processing**
- Each `@Provides` generates a Provider class
- Components create factories and DaggerComponent classes
- Large dependency graphs multiply generated code volume

**Incrementality Issues**
- KAPT doesn't support full incremental compilation
- Changes in one module trigger recompilation of dependent graphs
- Poor modular structure compounds the problem

### Practical Strategies

**1. Hilt Over Dagger**
```kotlin
// ✅ Minimal boilerplate, optimized generation
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository
}
```

**2. Prefer @Binds Over @Provides**
```kotlin
@Module
abstract class DataModule {
    @Binds  // ✅ Lightweight delegation without extra classes
    abstract fun bindRepo(impl: RepoImpl): Repository
}
```

**3. Migrate to KSP**
KSP is 2-4x faster than KAPT for annotation processing. Hilt supports KSP starting from certain versions.

**4. Gradle Configuration**
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

Use Android Studio Build Analyzer or `./gradlew build --scan` to profile kapt/ksp tasks. Typical improvements: 50-70% reduction in annotation processing time.

## Follow-ups

- What is the specific performance difference between KAPT and KSP for Dagger/Hilt?
- When should you avoid using Singleton scope for build time optimization?
- How does modularization impact Dagger's code generation?

## References

- https://dagger.dev/hilt/
- https://developer.android.com/training/dependency-injection/hilt-android

## Related Questions

### Prerequisites (Easier)
- [[q-android-project-parts--android--easy]]

### Related (Same Level)
- [[q-android-build-optimization--android--medium]]
- [[q-gradle-build-system--android--medium]]

### Advanced (Harder)
- [[q-dagger-framework-overview--android--hard]]
