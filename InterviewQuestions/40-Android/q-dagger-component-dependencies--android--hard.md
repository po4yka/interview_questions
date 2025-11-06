---
id: android-465
title: Dagger Component Dependencies / Зависимости компонентов Dagger
aliases: [Dagger Component Dependencies, Зависимости компонентов Dagger]
topic: android
subtopics:
  - di-hilt
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
updated: 2025-10-30
tags: [android/di-hilt, difficulty/hard]
sources:
  - https://dagger.dev/api/latest/dagger/Component.html
---

# Вопрос (RU)
> В чем разница между Component Dependencies и Subcomponents в Dagger? Когда использовать один подход вместо другого?

# Question (EN)
> What's the difference between Component Dependencies and Subcomponents in Dagger? When would you use one over the other?

## Ответ (RU)

Component Dependencies и Subcomponents — два способа композиции Dagger компонентов с различными характеристиками.

### Ключевые Различия

| Аспект | Component Dependencies | Subcomponents |
|--------|----------------------|---------------|
| **Отношение** | Has-a (агрегация) | Is-a (наследование) |
| **Изоляция scope** | Отдельные scope'ы | Общий scope с родителем |
| **Доступ** | Только экспортированные | Все зависимости родителя |
| **Создание** | Независимое | Создается родителем |

### Component Dependencies

Родитель явно экспортирует зависимости:

```kotlin
// ✅ Явная изоляция scope'ов
@Singleton
@Component(modules = [AppModule::class])
interface AppComponent {
    fun appDatabase(): AppDatabase  // ✅ Экспортируется явно
}

@ActivityScope
@Component(
    dependencies = [AppComponent::class],  // ✅ Зависит от AppComponent
    modules = [ActivityModule::class]
)
interface ActivityComponent {
    fun inject(activity: MainActivity)
}

// Использование
val activityComponent = DaggerActivityComponent.builder()
    .appComponent(appComponent)  // ✅ Передаем зависимость
    .build()
```

### Subcomponents

Автоматический доступ к зависимостям родителя:

```kotlin
// ✅ Иерархическая структура
@Singleton
@Component(modules = [AppModule::class])
interface AppComponent {
    fun activityComponentFactory(): ActivityComponent.Factory  // ✅ Фабрика subcomponent
}

@Subcomponent(modules = [ActivityModule::class])
interface ActivityComponent {
    fun inject(activity: MainActivity)
    // ❌ Не нужно явно объявлять доступ к AppComponent зависимостям

    @Subcomponent.Factory
    interface Factory {
        fun create(): ActivityComponent
    }
}

// Использование
val activityComponent = appComponent
    .activityComponentFactory()  // ✅ Создается через родителя
    .create()
```

### Когда Использовать

**Component Dependencies:**
- ✅ Модульная архитектура с изоляцией
- ✅ Независимые жизненные циклы
- ✅ Контроль экспортируемых зависимостей
- ❌ Нужен доступ ко всем зависимостям родителя

**Subcomponents:**
- ✅ Простая иерархия `Activity` → `Fragment`
- ✅ Доступ ко всем зависимостям приложения
- ✅ Feature-based модули с общим scope
- ❌ Строгая инкапсуляция модулей

### Hilt: Автоматическое Управление

[[c-hilt]] упрощает управление компонентами:

```kotlin
@AndroidEntryPoint  // ✅ Автоматическое внедрение
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository
}

@Module
@InstallIn(SingletonComponent::class)  // ✅ Автоматический scope
object AppModule {
    @Provides @Singleton
    fun provideRepository(): UserRepository = UserRepositoryImpl()
}
```

## Answer (EN)

Component Dependencies and Subcomponents are two ways to compose [[c-dagger]] components with different characteristics.

### Key Differences

| Aspect | Component Dependencies | Subcomponents |
|--------|----------------------|---------------|
| **Relationship** | Has-a (aggregation) | Is-a (inheritance) |
| **Scope Isolation** | Separate scopes | Shared scope |
| **Access** | Only exported | All parent dependencies |
| **Creation** | Independent | Created by parent |

### Component Dependencies

Parent explicitly exports dependencies:

```kotlin
// ✅ Explicit scope isolation
@Singleton
@Component(modules = [AppModule::class])
interface AppComponent {
    fun appDatabase(): AppDatabase  // ✅ Explicitly exported
}

@ActivityScope
@Component(
    dependencies = [AppComponent::class],  // ✅ Depends on AppComponent
    modules = [ActivityModule::class]
)
interface ActivityComponent {
    fun inject(activity: MainActivity)
}

// Usage
val activityComponent = DaggerActivityComponent.builder()
    .appComponent(appComponent)  // ✅ Pass dependency
    .build()
```

### Subcomponents

Automatic access to parent dependencies:

```kotlin
// ✅ Hierarchical structure
@Singleton
@Component(modules = [AppModule::class])
interface AppComponent {
    fun activityComponentFactory(): ActivityComponent.Factory  // ✅ Subcomponent factory
}

@Subcomponent(modules = [ActivityModule::class])
interface ActivityComponent {
    fun inject(activity: MainActivity)
    // ❌ No need to declare AppComponent dependencies

    @Subcomponent.Factory
    interface Factory {
        fun create(): ActivityComponent
    }
}

// Usage
val activityComponent = appComponent
    .activityComponentFactory()  // ✅ Created through parent
    .create()
```

### When to Use

**Component Dependencies:**
- ✅ Modular architecture with isolation
- ✅ Independent lifecycles
- ✅ Control exported dependencies
- ❌ Need access to all parent dependencies

**Subcomponents:**
- ✅ Simple `Activity` → `Fragment` hierarchy
- ✅ Access to all app dependencies
- ✅ Feature-based modules with shared scope
- ❌ Strict module encapsulation

### Hilt: Automatic Management

[[c-hilt]] simplifies component management:

```kotlin
@AndroidEntryPoint  // ✅ Automatic injection
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository
}

@Module
@InstallIn(SingletonComponent::class)  // ✅ Automatic scope
object AppModule {
    @Provides @Singleton
    fun provideRepository(): UserRepository = UserRepositoryImpl()
}
```

## Follow-ups

- How do you handle circular dependencies between components?
- What are the performance implications of each approach?
- How does Hilt manage component lifecycles automatically?
- When should you prefer Subcomponents over Component Dependencies?
- How do you test components with dependencies?

## References

- [[c-dagger]]
- [[c-hilt]]
- [[c-dependency-injection]]
- https://dagger.dev/api/latest/dagger/Component.html

## Related Questions

### Prerequisites
- [[q-hilt-components-scope--android--medium]] - Hilt component scopes
- [[q-dagger-build-time-optimization--android--medium]] - Dagger optimization

### Advanced
- [[q-dagger-framework-overview--android--hard]] - Complete Dagger architecture
