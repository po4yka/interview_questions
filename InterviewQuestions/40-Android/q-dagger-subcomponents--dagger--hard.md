---
id: android-dagger-003
title: Dagger Subcomponents and Component Dependencies / Subcomponents и Component
  Dependencies в Dagger
aliases:
- Dagger Subcomponents
- Component Dependencies
- Subcomponents
topic: android
subtopics:
- dagger
- di-dagger
question_kind: theory
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-dependency-injection
- q-dagger-component-module--dagger--medium
- q-dagger-scopes-custom--dagger--hard
created: 2026-01-23
updated: 2026-01-23
tags:
- android/di-dagger
- dependency-injection
- difficulty/hard
- dagger
- subcomponent
- component-dependencies
anki_cards:
- slug: android-dagger-003-0-en
  language: en
- slug: android-dagger-003-0-ru
  language: ru
---
# Вопрос (RU)
> В чём разница между Subcomponents и Component Dependencies в Dagger?

# Question (EN)
> What is the difference between Subcomponents and Component Dependencies in Dagger?

---

## Ответ (RU)

Dagger предоставляет два механизма для организации иерархии компонентов: **Subcomponents** и **Component Dependencies**. Оба позволяют создавать компоненты с разными жизненными циклами, но работают по-разному.

### Subcomponents - Дочерние Компоненты

Subcomponent имеет полный доступ ко всему графу родительского компонента. Родитель "владеет" subcomponent.

```kotlin
// Родительский компонент
@Singleton
@Component(modules = [AppModule::class, NetworkModule::class])
interface AppComponent {

    // Фабрика для создания subcomponent
    fun activityComponent(): ActivityComponent.Factory

    // Или через Builder
    fun activityComponentBuilder(): ActivityComponent.Builder
}

// Subcomponent - дочерний компонент
@ActivityScope
@Subcomponent(modules = [ActivityModule::class])
interface ActivityComponent {

    fun inject(activity: MainActivity)
    fun inject(activity: ProfileActivity)

    // Вложенный subcomponent
    fun fragmentComponent(): FragmentComponent.Factory

    @Subcomponent.Factory
    interface Factory {
        fun create(@BindsInstance activity: Activity): ActivityComponent
    }

    @Subcomponent.Builder
    interface Builder {
        @BindsInstance
        fun activity(activity: Activity): Builder
        fun build(): ActivityComponent
    }
}

// Вложенный subcomponent
@FragmentScope
@Subcomponent(modules = [FragmentModule::class])
interface FragmentComponent {

    fun inject(fragment: HomeFragment)

    @Subcomponent.Factory
    interface Factory {
        fun create(@BindsInstance fragment: Fragment): FragmentComponent
    }
}
```

### Регистрация Subcomponent в Родителе

```kotlin
@Module(subcomponents = [ActivityComponent::class])
abstract class AppModule {
    // ...
}

@Module(subcomponents = [FragmentComponent::class])
class ActivityModule {
    // ...
}
```

### Использование Subcomponents

```kotlin
class MainActivity : AppCompatActivity() {

    @Inject lateinit var presenter: MainPresenter

    lateinit var activityComponent: ActivityComponent

    override fun onCreate(savedInstanceState: Bundle?) {
        // Создаём subcomponent из родительского
        activityComponent = (application as MyApp)
            .appComponent
            .activityComponent()
            .create(this)

        activityComponent.inject(this)
        super.onCreate(savedInstanceState)
    }
}

class HomeFragment : Fragment() {

    @Inject lateinit var viewModel: HomeViewModel

    override fun onAttach(context: Context) {
        super.onAttach(context)
        // Создаём fragment subcomponent из activity component
        (requireActivity() as MainActivity)
            .activityComponent
            .fragmentComponent()
            .create(this)
            .inject(this)
    }
}
```

### Component Dependencies - Независимые Компоненты

Component Dependencies - это связь между независимыми компонентами. Зависимый компонент получает доступ только к явно экспортированным зависимостям.

```kotlin
// Родительский компонент - явно экспортирует зависимости
@Singleton
@Component(modules = [AppModule::class, NetworkModule::class])
interface AppComponent {

    // Только эти зависимости доступны дочернему компоненту
    fun retrofit(): Retrofit
    fun okHttpClient(): OkHttpClient
    fun application(): Application

    // НЕ экспортировано - недоступно через dependencies
    // UserRepository не будет виден
}

// Зависимый компонент - использует dependencies
@FeatureScope
@Component(
    dependencies = [AppComponent::class],
    modules = [FeatureModule::class]
)
interface FeatureComponent {

    fun inject(activity: FeatureActivity)

    @Component.Factory
    interface Factory {
        fun create(
            appComponent: AppComponent,
            @BindsInstance userId: String
        ): FeatureComponent
    }
}
```

### Использование Component Dependencies

```kotlin
class FeatureActivity : AppCompatActivity() {

    @Inject lateinit var featurePresenter: FeaturePresenter

    override fun onCreate(savedInstanceState: Bundle?) {
        val appComponent = (application as MyApp).appComponent

        DaggerFeatureComponent.factory()
            .create(
                appComponent = appComponent,
                userId = intent.getStringExtra("USER_ID") ?: ""
            )
            .inject(this)

        super.onCreate(savedInstanceState)
    }
}
```

### Сравнительная Таблица

| Критерий | Subcomponent | Component Dependencies |
|----------|--------------|----------------------|
| Доступ к графу | Полный | Только экспортированные |
| Связь | Тесная (parent owns child) | Слабая (независимые) |
| Объявление | `@Subcomponent` | `dependencies = [...]` |
| Инкапсуляция | Слабая | Сильная |
| Модульность | Низкая | Высокая |
| Многомодульные проекты | Менее удобно | Предпочтительно |
| Создание | Через родителя | Независимо |

### Когда Что Использовать

**Subcomponents - когда:**
- Tight coupling между компонентами нормален
- Нужен доступ ко всем зависимостям родителя
- Простая иерархия App -> Activity -> Fragment
- Монолитное приложение

**Component Dependencies - когда:**
- Нужна строгая инкапсуляция
- Многомодульный проект (feature modules)
- Компоненты логически независимы
- Хотите контролировать API между модулями

### Пример Многомодульного Проекта

```kotlin
// :core модуль
@Singleton
@Component(modules = [CoreModule::class])
interface CoreComponent {
    // Экспортируем только нужное
    fun retrofit(): Retrofit
    fun analytics(): Analytics
    fun userSession(): UserSession
}

// :feature-profile модуль
@FeatureScope
@Component(
    dependencies = [CoreComponent::class],
    modules = [ProfileModule::class]
)
interface ProfileComponent {
    fun inject(activity: ProfileActivity)

    @Component.Factory
    interface Factory {
        fun create(coreComponent: CoreComponent): ProfileComponent
    }
}

// :feature-settings модуль
@FeatureScope
@Component(
    dependencies = [CoreComponent::class],
    modules = [SettingsModule::class]
)
interface SettingsComponent {
    fun inject(activity: SettingsActivity)

    @Component.Factory
    interface Factory {
        fun create(coreComponent: CoreComponent): SettingsComponent
    }
}
```

### Комбинирование Подходов

```kotlin
// AppComponent использует component dependencies для core
// но subcomponents для внутренней иерархии

@Singleton
@Component(
    dependencies = [CoreComponent::class],
    modules = [AppModule::class]
)
interface AppComponent {

    // Subcomponent для тесно связанных компонентов
    fun mainActivityComponent(): MainActivityComponent.Factory

    // Provision для feature modules с component dependencies
    fun retrofit(): Retrofit
    fun userSession(): UserSession
}
```

---

## Answer (EN)

Dagger provides two mechanisms for organizing component hierarchy: **Subcomponents** and **Component Dependencies**. Both allow creating components with different lifecycles but work differently.

### Subcomponents - Child Components

Subcomponent has full access to the parent component's entire graph. Parent "owns" the subcomponent.

```kotlin
// Parent component
@Singleton
@Component(modules = [AppModule::class, NetworkModule::class])
interface AppComponent {

    // Factory to create subcomponent
    fun activityComponent(): ActivityComponent.Factory

    // Or via Builder
    fun activityComponentBuilder(): ActivityComponent.Builder
}

// Subcomponent - child component
@ActivityScope
@Subcomponent(modules = [ActivityModule::class])
interface ActivityComponent {

    fun inject(activity: MainActivity)
    fun inject(activity: ProfileActivity)

    // Nested subcomponent
    fun fragmentComponent(): FragmentComponent.Factory

    @Subcomponent.Factory
    interface Factory {
        fun create(@BindsInstance activity: Activity): ActivityComponent
    }

    @Subcomponent.Builder
    interface Builder {
        @BindsInstance
        fun activity(activity: Activity): Builder
        fun build(): ActivityComponent
    }
}

// Nested subcomponent
@FragmentScope
@Subcomponent(modules = [FragmentModule::class])
interface FragmentComponent {

    fun inject(fragment: HomeFragment)

    @Subcomponent.Factory
    interface Factory {
        fun create(@BindsInstance fragment: Fragment): FragmentComponent
    }
}
```

### Registering Subcomponent in Parent

```kotlin
@Module(subcomponents = [ActivityComponent::class])
abstract class AppModule {
    // ...
}

@Module(subcomponents = [FragmentComponent::class])
class ActivityModule {
    // ...
}
```

### Using Subcomponents

```kotlin
class MainActivity : AppCompatActivity() {

    @Inject lateinit var presenter: MainPresenter

    lateinit var activityComponent: ActivityComponent

    override fun onCreate(savedInstanceState: Bundle?) {
        // Create subcomponent from parent
        activityComponent = (application as MyApp)
            .appComponent
            .activityComponent()
            .create(this)

        activityComponent.inject(this)
        super.onCreate(savedInstanceState)
    }
}

class HomeFragment : Fragment() {

    @Inject lateinit var viewModel: HomeViewModel

    override fun onAttach(context: Context) {
        super.onAttach(context)
        // Create fragment subcomponent from activity component
        (requireActivity() as MainActivity)
            .activityComponent
            .fragmentComponent()
            .create(this)
            .inject(this)
    }
}
```

### Component Dependencies - Independent Components

Component Dependencies create a relationship between independent components. Dependent component only accesses explicitly exported dependencies.

```kotlin
// Parent component - explicitly exports dependencies
@Singleton
@Component(modules = [AppModule::class, NetworkModule::class])
interface AppComponent {

    // Only these dependencies available to dependent component
    fun retrofit(): Retrofit
    fun okHttpClient(): OkHttpClient
    fun application(): Application

    // NOT exported - not available through dependencies
    // UserRepository won't be visible
}

// Dependent component - uses dependencies
@FeatureScope
@Component(
    dependencies = [AppComponent::class],
    modules = [FeatureModule::class]
)
interface FeatureComponent {

    fun inject(activity: FeatureActivity)

    @Component.Factory
    interface Factory {
        fun create(
            appComponent: AppComponent,
            @BindsInstance userId: String
        ): FeatureComponent
    }
}
```

### Using Component Dependencies

```kotlin
class FeatureActivity : AppCompatActivity() {

    @Inject lateinit var featurePresenter: FeaturePresenter

    override fun onCreate(savedInstanceState: Bundle?) {
        val appComponent = (application as MyApp).appComponent

        DaggerFeatureComponent.factory()
            .create(
                appComponent = appComponent,
                userId = intent.getStringExtra("USER_ID") ?: ""
            )
            .inject(this)

        super.onCreate(savedInstanceState)
    }
}
```

### Comparison Table

| Criterion | Subcomponent | Component Dependencies |
|-----------|--------------|----------------------|
| Graph access | Full | Only exported |
| Coupling | Tight (parent owns child) | Loose (independent) |
| Declaration | `@Subcomponent` | `dependencies = [...]` |
| Encapsulation | Weak | Strong |
| Modularity | Low | High |
| Multi-module projects | Less convenient | Preferred |
| Creation | Through parent | Independent |

### When to Use What

**Subcomponents - when:**
- Tight coupling between components is acceptable
- Need access to all parent dependencies
- Simple hierarchy App -> Activity -> Fragment
- Monolithic application

**Component Dependencies - when:**
- Need strict encapsulation
- Multi-module project (feature modules)
- Components are logically independent
- Want to control API between modules

### Multi-Module Project Example

```kotlin
// :core module
@Singleton
@Component(modules = [CoreModule::class])
interface CoreComponent {
    // Export only what's needed
    fun retrofit(): Retrofit
    fun analytics(): Analytics
    fun userSession(): UserSession
}

// :feature-profile module
@FeatureScope
@Component(
    dependencies = [CoreComponent::class],
    modules = [ProfileModule::class]
)
interface ProfileComponent {
    fun inject(activity: ProfileActivity)

    @Component.Factory
    interface Factory {
        fun create(coreComponent: CoreComponent): ProfileComponent
    }
}

// :feature-settings module
@FeatureScope
@Component(
    dependencies = [CoreComponent::class],
    modules = [SettingsModule::class]
)
interface SettingsComponent {
    fun inject(activity: SettingsActivity)

    @Component.Factory
    interface Factory {
        fun create(coreComponent: CoreComponent): SettingsComponent
    }
}
```

### Combining Approaches

```kotlin
// AppComponent uses component dependencies for core
// but subcomponents for internal hierarchy

@Singleton
@Component(
    dependencies = [CoreComponent::class],
    modules = [AppModule::class]
)
interface AppComponent {

    // Subcomponent for tightly coupled components
    fun mainActivityComponent(): MainActivityComponent.Factory

    // Provision for feature modules with component dependencies
    fun retrofit(): Retrofit
    fun userSession(): UserSession
}
```

---

## Дополнительные Вопросы (RU)

- Как scopes влияют на subcomponents и component dependencies?
- Можно ли иметь несколько родителей через component dependencies?
- Как организовать DI в многомодульном Gradle проекте?

## Follow-ups

- How do scopes affect subcomponents and component dependencies?
- Can you have multiple parents through component dependencies?
- How do you organize DI in a multi-module Gradle project?

## Ссылки (RU)

- [Dagger Subcomponents](https://dagger.dev/dev-guide/subcomponents.html)
- [Component Dependencies](https://dagger.dev/dev-guide/component-dependencies.html)

## References

- [Dagger Subcomponents](https://dagger.dev/dev-guide/subcomponents.html)
- [Component Dependencies](https://dagger.dev/dev-guide/component-dependencies.html)

## Связанные Вопросы (RU)

### Medium
- [[q-dagger-component-module--dagger--medium]]
- [[q-dagger-component-builder--dagger--medium]]

### Hard
- [[q-dagger-scopes-custom--dagger--hard]]
- [[q-dagger-multibindings--dagger--hard]]

## Related Questions

### Medium
- [[q-dagger-component-module--dagger--medium]]
- [[q-dagger-component-builder--dagger--medium]]

### Hard
- [[q-dagger-scopes-custom--dagger--hard]]
- [[q-dagger-multibindings--dagger--hard]]
