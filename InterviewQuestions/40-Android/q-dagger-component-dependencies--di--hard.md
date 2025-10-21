---
id: 20251020-200000
title: Dagger Component Dependencies / Зависимости компонентов Dagger
aliases:
  - Dagger Component Dependencies
  - Зависимости компонентов Dagger
topic: android
subtopics:
  - dependency-injection
  - architecture-patterns
question_kind: android
difficulty: hard
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - q-dagger-build-time-optimization--android--medium
  - q-dagger-framework-overview--android--hard
  - q-hilt-components-scope--android--medium
created: 2025-10-20
updated: 2025-10-20
tags:
  - android/dependency-injection
  - android/architecture-patterns
  - dagger
  - hilt
  - component-dependencies
  - subcomponents
  - difficulty/hard
source: https://dagger.dev/api/latest/dagger/Component.html
source_note: Dagger Component API documentation
---
# Вопрос (RU)
> В чем разница между Component Dependencies и Subcomponents в Dagger? Когда использовать один подход вместо другого? Как Hilt обрабатывает это?

# Question (EN)
> What's the difference between Component Dependencies and Subcomponents in Dagger? When would you use one over the other? How does Hilt handle this?

## Ответ (RU)

Component Dependencies и Subcomponents — два способа композиции Dagger компонентов с различными характеристиками и областями применения.

### Теория: Архитектурные паттерны

**Component Dependencies (Has-a relationship)**
- Агрегация компонентов через явные зависимости
- Родительский компонент должен экспортировать зависимости
- Изолированные scope'ы и жизненные циклы
- Строгая инкапсуляция зависимостей

**Subcomponents (Is-a relationship)**
- Наследование компонентов в иерархической структуре
- Автоматический доступ ко всем зависимостям родителя
- Общий scope с родительским компонентом
- Возможность переопределения bindings

### Сравнение подходов

| Аспект | Component Dependencies | Subcomponents |
|--------|----------------------|---------------|
| **Отношение** | Has-a (агрегация) | Is-a (наследование) |
| **Изоляция scope** | Отдельные scope'ы | Общий scope с родителем |
| **Доступ к зависимостям** | Только явно экспортированные | Все зависимости родителя |
| **Создание** | Независимое | Создается родителем |
| **Конфликты bindings** | Изолированы | Может переопределить родителя |

### Component Dependencies

Родительский компонент должен явно экспортировать зависимости:

```kotlin
@Singleton
@Component(modules = [AppModule::class])
interface AppComponent {
    fun appDatabase(): AppDatabase
    fun apiService(): ApiService
}

@ActivityScope
@Component(
    dependencies = [AppComponent::class],
    modules = [ActivityModule::class]
)
interface ActivityComponent {
    fun inject(activity: MainActivity)
}
```

**Использование:**
```kotlin
val appComponent = (application as MyApplication).appComponent
DaggerActivityComponent.builder()
    .appComponent(appComponent)
    .build()
    .inject(this)
```

### Subcomponents

Создается иерархическая структура с автоматическим доступом:

```kotlin
@Singleton
@Component(modules = [AppModule::class])
interface AppComponent {
    fun activityComponentFactory(): ActivityComponent.Factory
}

@Subcomponent(modules = [ActivityModule::class])
interface ActivityComponent {
    fun inject(activity: MainActivity)

    @Subcomponent.Factory
    interface Factory {
        fun create(): ActivityComponent
    }
}
```

**Использование:**
```kotlin
val activityComponent = appComponent.activityComponentFactory().create()
activityComponent.inject(this)
```

### Когда использовать

**Component Dependencies подходят для:**
- Строгой инкапсуляции зависимостей
- Независимых жизненных циклов
- Модульной архитектуры
- Когда нужен контроль над экспортируемыми зависимостями

**Subcomponents подходят для:**
- Простых иерархических структур
- Когда нужен доступ ко всем зависимостям родителя
- Feature-based архитектуры
- Когда scope должен быть общим

### Hilt подход

Hilt автоматизирует управление компонентами:

```kotlin
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository
}

@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    @Provides
    @Singleton
    fun provideRepository(): UserRepository = UserRepositoryImpl()
}
```

**Hilt автоматически:**
- Создает компоненты по scope'ам
- Управляет зависимостями между компонентами
- Обрабатывает жизненные циклы
- Предотвращает циклические зависимости

### Лучшие практики

**Для Component Dependencies:**
- Экспортируйте только необходимые зависимости
- Используйте интерфейсы для абстракции
- Избегайте глубоких иерархий

**Для Subcomponents:**
- Ограничивайте глубину иерархии
- Используйте @Subcomponent.Builder для гибкости
- Избегайте переопределения bindings без необходимости

## Answer (EN)

Component Dependencies and Subcomponents are two ways to compose Dagger components with different characteristics and use cases.

### Theory: Architectural Patterns

**Component Dependencies (Has-a relationship)**
- Component aggregation through explicit dependencies
- Parent component must export dependencies
- Isolated scopes and lifecycles
- Strict dependency encapsulation

**Subcomponents (Is-a relationship)**
- Component inheritance in hierarchical structure
- Automatic access to all parent dependencies
- Shared scope with parent component
- Ability to override bindings

### Approach Comparison

| Aspect | Component Dependencies | Subcomponents |
|--------|----------------------|---------------|
| **Relationship** | Has-a (aggregation) | Is-a (inheritance) |
| **Scope Isolation** | Separate scopes | Shared scope with parent |
| **Dependency Access** | Only explicitly exported | All parent dependencies |
| **Creation** | Independent | Created by parent |
| **Binding Conflicts** | Isolated | Can override parent |

### Component Dependencies

Parent component must explicitly export dependencies:

```kotlin
@Singleton
@Component(modules = [AppModule::class])
interface AppComponent {
    fun appDatabase(): AppDatabase
    fun apiService(): ApiService
}

@ActivityScope
@Component(
    dependencies = [AppComponent::class],
    modules = [ActivityModule::class]
)
interface ActivityComponent {
    fun inject(activity: MainActivity)
}
```

**Usage:**
```kotlin
val appComponent = (application as MyApplication).appComponent
DaggerActivityComponent.builder()
    .appComponent(appComponent)
    .build()
    .inject(this)
```

### Subcomponents

Creates hierarchical structure with automatic access:

```kotlin
@Singleton
@Component(modules = [AppModule::class])
interface AppComponent {
    fun activityComponentFactory(): ActivityComponent.Factory
}

@Subcomponent(modules = [ActivityModule::class])
interface ActivityComponent {
    fun inject(activity: MainActivity)

    @Subcomponent.Factory
    interface Factory {
        fun create(): ActivityComponent
    }
}
```

**Usage:**
```kotlin
val activityComponent = appComponent.activityComponentFactory().create()
activityComponent.inject(this)
```

### When to Use

**Component Dependencies are suitable for:**
- Strict dependency encapsulation
- Independent lifecycles
- Modular architecture
- When control over exported dependencies is needed

**Subcomponents are suitable for:**
- Simple hierarchical structures
- When access to all parent dependencies is needed
- Feature-based architecture
- When scope should be shared

### Hilt Approach

Hilt automates component management:

```kotlin
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository
}

@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    @Provides
    @Singleton
    fun provideRepository(): UserRepository = UserRepositoryImpl()
}
```

**Hilt automatically:**
- Creates components by scopes
- Manages dependencies between components
- Handles lifecycles
- Prevents circular dependencies

### Best Practices

**For Component Dependencies:**
- Export only necessary dependencies
- Use interfaces for abstraction
- Avoid deep hierarchies

**For Subcomponents:**
- Limit hierarchy depth
- Use @Subcomponent.Builder for flexibility
- Avoid unnecessary binding overrides

## Follow-ups

- How do you handle circular dependencies between components?
- What are the performance implications of each approach?
- How does Hilt's automatic component management work internally?

## References

- [Dagger Component API](https://dagger.dev/api/latest/dagger/Component.html)
- [Hilt Component Hierarchy](https://dagger.dev/hilt/components.html)

## Related Questions

### Prerequisites (Easier)
- [[q-dagger-build-time-optimization--android--medium]]

### Related (Same Level)
- [[q-hilt-components-scope--android--medium]]

### Advanced (Harder)
- [[q-dagger-framework-overview--android--hard]]
