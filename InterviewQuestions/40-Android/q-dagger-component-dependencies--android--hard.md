---
id: android-465
title: Dagger Component Dependencies / Зависимости компонентов Dagger
aliases:
- Dagger Component Dependencies
- Зависимости компонентов Dagger
topic: android
subtopics:
- di-hilt
question_kind: android
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-dagger
- q-dagger-build-time-optimization--android--medium
- q-dagger-custom-scopes--android--hard
- q-dagger-framework-overview--android--hard
- q-dagger-multibinding--android--hard
- q-hilt-components-scope--android--medium
created: 2025-10-20
updated: 2025-11-11
tags:
- android/di-hilt
- difficulty/hard
anki_cards:
- slug: android-465-0-en
  language: en
  anki_id: 1768366561476
  synced_at: '2026-01-23T16:45:06.283502'
- slug: android-465-0-ru
  language: ru
  anki_id: 1768366561501
  synced_at: '2026-01-23T16:45:06.284239'
sources:
- https://dagger.dev/api/latest/dagger/Component.html
---
# Вопрос (RU)
> В чем разница между `Component` Dependencies и Subcomponents в `Dagger`? Когда использовать один подход вместо другого?

# Question (EN)
> What's the difference between `Component` Dependencies and Subcomponents in `Dagger`? When would you use one over the other?

## Ответ (RU)

`Component` Dependencies и Subcomponents — два способа композиции `Dagger`-компонентов с различными характеристиками.

## Краткая Версия
- Используйте `Component` Dependencies для модульности и явного контроля того, что экспортируется между независимыми компонентами.
- Используйте Subcomponents для иерархий, соответствующих жизненным циклам (`Activity`/`Fragment`), с общим базовым графом и удобным доступом ко всем зависимостям родителя.

## Подробная Версия
#### Ключевые Различия

| Аспект | `Component` Dependencies | Subcomponents |
|--------|-----------------------|---------------|
| **Отношение** | Has-a (агрегация): компонент зависит от другого компонента как от поставщика зависимостей | Иерархическое включение: subcomponent создается родителем и использует его граф |
| **Scope** | Имеет собственный граф; может использовать скоупы, отличные от родителя; родительский синглтон виден через явно экспортированные провайдеры | Наследует граф родителя и может добавлять свои binding'и; объекты в `@Singleton`/родительских скоупах общие, subcomponent может иметь свой более "узкий" scope |
| **Доступ** | Может использовать только зависимости, явно экспортированные родительским компонентом через методы интерфейса | Имеет доступ ко всем binding'ам родителя (с учетом scoping и видимости), без явного экспорта каждого |
| **Создание** | Строится независимо от родителя, ему передается ссылка на родительский компонент | Всегда создается через API родительского компонента (фабрика/builder) |

#### Component Dependencies

Родительский компонент явно экспортирует зависимости, которые будут доступны зависимому компоненту. Зависимый компонент имеет собственный граф и жизненный цикл; родитель не знает о его существовании.

```kotlin
// Явная изоляция графов и scope'ов
@Singleton
@Component(modules = [AppModule::class])
interface AppComponent {
    fun appDatabase(): AppDatabase  // Экспортируется явно
}

@ActivityScope
@Component(
    dependencies = [AppComponent::class],  // Зависит от AppComponent
    modules = [ActivityModule::class]
)
interface ActivityComponent {
    fun inject(activity: MainActivity)
}

// Использование
val activityComponent = DaggerActivityComponent.builder()
    .appComponent(appComponent)  // Передаем экземпляр AppComponent как зависимость
    .build()
```

Ключевые моменты:
- ActivityComponent не является "дочерним" в смысле владения: его создают независимо от жизненного цикла AppComponent, но он использует предоставленные им зависимости.
- Доступны только те зависимости AppComponent, для которых объявлены методы в его интерфейсе.

#### Subcomponents

Subcomponent создается родительским компонентом, наследует его граф зависимостей и может добавлять собственные binding'и. Не требуется явно экспортировать зависимости родителя.

```kotlin
// Иерархическая структура
@Singleton
@Component(modules = [AppModule::class])
interface AppComponent {
    fun activityComponentFactory(): ActivityComponent.Factory  // Фабрика subcomponent
}

@Subcomponent(modules = [ActivityModule::class])
interface ActivityComponent {
    fun inject(activity: MainActivity)
    // Не нужно явно объявлять доступ к зависимостям AppComponent

    @Subcomponent.Factory
    interface Factory {
        fun create(): ActivityComponent
    }
}

// Использование
val activityComponent = appComponent
    .activityComponentFactory()  // Создается через родителя
    .create()
```

Ключевые моменты:
- Subcomponent живет не дольше родительского компонента.
- Имеет доступ ко всем binding'ам родителя (например, `@Singleton`-объекты), плюс своим binding'ам.
- Может вводить более узкий scope (например, `@ActivityScope`) поверх родительского (например, `@Singleton`).

#### Когда Использовать

`Component` Dependencies:
- Модульная архитектура с четкой изоляцией: каждый модуль имеет свой компонент.
- Независимые жизненные циклы компонент (компонент можно пересоздавать/менять, имея только ссылку на зависимости).
- Точный контроль экспортируемых зависимостей между модулями.
- Менее удобно, когда нужна видимость многих binding'ов родителя (надо явно экспортировать).

Subcomponents:
- Естественная иерархия `Activity` → `Fragment` → Child (соответствие жизненным циклам).
- Удобный доступ ко всем зависимостям родителя без ручного экспорта.
- Подходят, когда фича логически вложена в приложение и разделяет общий базовый граф (`@Singleton`).
- Менее строгая модульная изоляция.

#### Hilt: Автоматическое Управление

[[c-hilt]] упрощает управление компонентами, автоматически создавая и связывая иерархии компонентов (по сути, subcomponents/entry points), привязанные к жизненным циклам Android.

```kotlin
@AndroidEntryPoint  // Автоматическое внедрение
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository
}

@Module
@InstallIn(SingletonComponent::class)  // Привязка к компоненту приложения
object AppModule {
    @Provides
    @Singleton
    fun provideRepository(): UserRepository = UserRepositoryImpl()
}
```

## Answer (EN)

`Component` Dependencies and Subcomponents are two ways to compose [[c-dagger]] components with different characteristics.

## Short Version
- Use `Component` Dependencies for modularization and explicit control over what is exposed between independent components.
- Use Subcomponents for lifecycle-aligned hierarchies (`Activity`/`Fragment`) with a shared base graph and convenient access to all parent bindings.

## Detailed Version
#### Key Differences

| Aspect | `Component` Dependencies | Subcomponents |
|--------|-----------------------|---------------|
| **Relationship** | Has-a (aggregation): a component depends on another component as a provider of dependencies | Hierarchical inclusion: subcomponent is created by the parent and uses its graph |
| **Scope** | Has its own graph; may define scopes independent from the parent; parent singletons are visible only via explicitly exported provision methods | Inherits the parent's object graph and can add its own bindings; parent-scoped objects (e.g. `@Singleton`) are shared; subcomponent can define narrower scopes |
| **Access** | Can use only dependencies explicitly exported by the parent component via interface methods | Has access to all parent's bindings (subject to scoping/visibility), without explicit export of each |
| **Creation** | Built independently; an instance of the parent component is passed in as a dependency | Always created through the parent component's API (factory/builder) |

#### Component Dependencies

The parent component explicitly exports the dependencies that will be available to the dependent component. The dependent component has its own graph and lifecycle; the parent is unaware of it.

```kotlin
// Explicit graph and scope isolation
@Singleton
@Component(modules = [AppModule::class])
interface AppComponent {
    fun appDatabase(): AppDatabase  // Explicitly exported
}

@ActivityScope
@Component(
    dependencies = [AppComponent::class],  // Depends on AppComponent
    modules = [ActivityModule::class]
)
interface ActivityComponent {
    fun inject(activity: MainActivity)
}

// Usage
val activityComponent = DaggerActivityComponent.builder()
    .appComponent(appComponent)  // Pass AppComponent instance as dependency
    .build()
```

Key points:
- ActivityComponent is not "owned" by AppComponent; it is constructed separately while using its exported dependencies.
- Only dependencies exposed via methods on AppComponent are visible to ActivityComponent.

#### Subcomponents

A Subcomponent is created by its parent, inherits its dependency graph, and can add its own bindings. Parent dependencies do not need to be explicitly exported.

```kotlin
// Hierarchical structure
@Singleton
@Component(modules = [AppModule::class])
interface AppComponent {
    fun activityComponentFactory(): ActivityComponent.Factory  // Subcomponent factory
}

@Subcomponent(modules = [ActivityModule::class])
interface ActivityComponent {
    fun inject(activity: MainActivity)
    // No need to declare AppComponent dependencies explicitly

    @Subcomponent.Factory
    interface Factory {
        fun create(): ActivityComponent
    }
}

// Usage
val activityComponent = appComponent
    .activityComponentFactory()  // Created through parent
    .create()
```

Key points:
- Subcomponent cannot outlive its parent component.
- It has access to all parent's bindings (e.g. `@Singleton` instances), plus its own.
- It can use a narrower scope (e.g. `@ActivityScope`) layered on top of the parent's scope (e.g. `@Singleton`).

#### When to Use

`Component` Dependencies:
- Modular architecture with clear boundaries: each module owns its component.
- Independent component lifecycles (you can recreate/replace dependent components while holding only references to required dependencies).
- Fine-grained control over which dependencies are exposed between modules.
- Less convenient when you need access to many of the parent's bindings (must export them explicitly).

Subcomponents:
- Natural fit for `Activity` → `Fragment` → Child hierarchies matching lifecycles.
- Easy access to all parent-provided dependencies without manual export.
- Good when a feature is logically nested within the app and shares the app's base graph (e.g. `@Singleton`).
- Weaker module encapsulation: boundaries between graphs are less explicit.

#### Hilt: Automatic Management

[[c-hilt]] simplifies component management by generating and wiring a hierarchy of components (effectively using subcomponents/entry points) tied to Android lifecycles.

```kotlin
@AndroidEntryPoint  // Automatic injection
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository
}

@Module
@InstallIn(SingletonComponent::class)  // Bound to the application-level component
object AppModule {
    @Provides
    @Singleton
    fun provideRepository(): UserRepository = UserRepositoryImpl()
}
```

## Дополнительные Вопросы (RU)

- Как обрабатывать циклические зависимости между компонентами?
- Каковы производительные последствия каждого подхода?
- Как `Hilt` автоматически управляет жизненными циклами компонентов?
- Когда следует предпочесть Subcomponents вместо `Component` Dependencies?
- Как тестировать компоненты с зависимостями?

## Follow-ups

- How do you handle circular dependencies between components?
- What are the performance implications of each approach?
- How does `Hilt` manage component lifecycles automatically?
- When should you prefer Subcomponents over `Component` Dependencies?
- How do you test components with dependencies?

## Ссылки (RU)

- [[c-dagger]]
- [[c-hilt]]
- [[c-dependency-injection]]
- https://dagger.dev/api/latest/dagger/Component.html

## References

- [[c-dagger]]
- [[c-hilt]]
- [[c-dependency-injection]]
- https://dagger.dev/api/latest/dagger/Component.html

## Связанные Вопросы (RU)

### Предпосылки
- [[q-hilt-components-scope--android--medium]] - Scope'ы компонентов `Hilt`
- [[q-dagger-build-time-optimization--android--medium]] - Оптимизация `Dagger`

### Продвинутое
- [[q-dagger-framework-overview--android--hard]] - Архитектура `Dagger`

## Related Questions

### Prerequisites
- [[q-hilt-components-scope--android--medium]] - `Hilt` component scopes
- [[q-dagger-build-time-optimization--android--medium]] - `Dagger` optimization

### Advanced
- [[q-dagger-framework-overview--android--hard]] - Complete `Dagger` architecture
