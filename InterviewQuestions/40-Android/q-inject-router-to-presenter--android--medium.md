---\
id: android-215
title: "Inject Router To Presenter / Инъекция Router в Presenter"
aliases: ["Inject Router To Presenter", "Router DI", "Инъекция Router в Presenter", "Инъекция роутера"]
topic: android
subtopics: [architecture-mvvm, di-hilt, ui-navigation]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-dependency-injection, q-play-feature-delivery--android--medium, q-state-hoisting-compose--android--medium]
created: 2025-10-15
updated: 2025-11-10
tags: [android/architecture-mvvm, android/di-hilt, android/ui-navigation, dependency-injection, difficulty/medium, navigation, router]

---\
# Вопрос (RU)

> Что использовать для того, чтобы роутер инжектился напрямую в презентер?

# Question (EN)

> What to use to inject router directly into presenter?

---

## Ответ (RU)

Для внедрения роутера в презентер используйте **Dependency Injection (DI)** фреймворки. Они обеспечивают слабую связанность, упрощают тестирование и позволяют лучше следовать SOLID-принципам.

Важно: под "прямой инъекцией" подразумевается инъекция абстракции `Router` в конструктор презентера, а не прямой инъекции `NavController` или `Fragment`.

**Основные подходы**:

1. **`Hilt`** — официальный Android DI, минимальный boilerplate
2. **`Dagger` 2** — compile-time DI, больше контроля
3. **`Koin`** — runtime DI, Kotlin DSL, простая настройка

### Ключевой Паттерн: Router Через Интерфейс

```kotlin
// ✅ Интерфейс роутера — абстрагирует детали реализации навигации
interface Router {
    fun navigateToDetails(itemId: String)
    fun navigateToSettings()
    fun navigateBack()
}
```

### Пример С Hilt (Рекомендуется)

Важно: `NavController` привязан к `NavHostFragment` и обычно не инжектится напрямую как долгоживущая зависимость на уровне `ActivityComponent`/`SingletonComponent`. Вместо этого инжектируйте абстракцию `Router` в презентер, а `Router` реализуйте так, чтобы он получал актуальный `NavController` через переданные зависимости, события или коллбеки, не нарушая жизненный цикл.

Один из безопасных вариантов — `Router`, которому UI-слой (Fragment/Activity) передает навигационные события/handler, либо который оперирует навигационными событиями (например, `LiveData` / `Flow`) вместо прямого хранения `NavController`.

```kotlin
// Реализация роутера, завязанная на NavController через переданный navControllerProvider
class AppRouter @Inject constructor(
    private val navControllerProvider: () -> NavController
) : Router {

    private val navController: NavController
        get() = navControllerProvider()

    override fun navigateToDetails(itemId: String) {
        navController.navigate("details/$itemId")
    }

    override fun navigateToSettings() {
        navController.navigate("settings")
    }

    override fun navigateBack() {
        navController.popBackStack()
    }
}

// Модуль Hilt — биндим интерфейс на реализацию
@Module
@InstallIn(ActivityComponent::class)
abstract class NavigationModule {
    @Binds
    abstract fun bindRouter(impl: AppRouter): Router
}

// В Activity/Fragment вы можете предоставить navControllerProvider,
// замыкающийся на актуальный NavController текущего NavHostFragment.
// Конкретная реализация зависит от структуры навигации приложения.

// ✅ Презентер с конструкторной инъекцией Router
class ProductListPresenter @Inject constructor(
    private val router: Router,
    private val repository: ProductRepository
) {
    fun onProductClicked(productId: String) {
        router.navigateToDetails(productId)
    }
}

// Fragment
@AndroidEntryPoint
class ProductListFragment : Fragment() {
    @Inject lateinit var presenter: ProductListPresenter
}
```

Этот пример демонстрирует идею: презентер получает `Router` по интерфейсу, а конкретная реализация `Router` знает, как работать с навигацией. Важно спроектировать `Router` так, чтобы он не держал долгоживущих ссылок на `NavController` или `Fragment` и уважал scope компонентов `Hilt`.

### Пример С Koin

```kotlin
// Модуль Koin
val navigationModule = module {
    // Router с областью жизни Activity или конкретного навигационного контейнера
    scope<MainActivity> {
        scoped<Router> { (navController: NavController) ->
            AppRouter(navControllerProvider = { navController })
        }
    }
}

val presenterModule = module {
    scope<ProductListFragment> {
        scoped { ProductListPresenter(router = get(), repository = get()) }
    }
}

// Fragment
class ProductListFragment : Fragment() {
    private val navController by lazy { findNavController() }

    private val presenter: ProductListPresenter by scopedInject(parameters = {
        parametersOf(navController)
    })
}
```

Здесь ключевая идея сохраняется: презентер получает `Router` по интерфейсу, а детали получения `NavController` инкапсулируются в реализации роутера и согласованы с областью жизни (scope). Можно выбрать и другие варианты (например, события навигации), главное — не передавать во внутренние слои долгоживущие ссылки на UI.

### Тестирование С Mock Router

```kotlin
class ProductListPresenterTest {
    private val mockRouter = mockk<Router>(relaxed = true)
    private val mockRepository = mockk<ProductRepository>()
    private lateinit var presenter: ProductListPresenter

    @Before
    fun setup() {
        presenter = ProductListPresenter(router = mockRouter, repository = mockRepository)
    }

    @Test
    fun `when product clicked, should navigate to details`() {
        presenter.onProductClicked("123")

        verify { mockRouter.navigateToDetails("123") }
    }
}
```

### Преимущества DI Для Роутеров

1. **Слабая связанность** — презентер зависит только от интерфейса `Router`, а не от `NavController`
2. **Легкое тестирование** — можно подменить роутер на mock/stub в unit-тестах
3. **Разделение ответственностей** — презентационная логика не знает деталей реализации навигации
4. **Переиспользование** — один `Router` (или набор интерфейсов) для многих презентеров
5. **Изоляция модулей** — feature-модули зависят от абстракций навигации, а не от конкретного стека

### Best Practices

```kotlin
// ✅ GOOD: интерфейс + конструкторная инъекция
class Presenter @Inject constructor(private val router: Router)

// ❌ BAD: прямая зависимость от NavController в презентере
class Presenter @Inject constructor(private val navController: NavController)

// ✅ GOOD: Router, живущий не дольше Activity/host компонента
@InstallIn(ActivityComponent::class)

// ❌ BAD: Singleton Router, держащий NavController (проблемы с жизненным циклом)
@InstallIn(SingletonComponent::class)
```

---

## Answer (EN)

To inject a router into a presenter, use **Dependency Injection (DI)** frameworks. They ensure loose coupling, make testing easier, and help better adhere to SOLID principles.

Importantly, "direct injection" here should mean injecting a `Router` abstraction into the presenter's constructor, not injecting `NavController` or `Fragment` directly.

**Main approaches**:

1. **`Hilt`** — official Android DI, minimal boilerplate
2. **`Dagger` 2** — compile-time DI, more control
3. **`Koin`** — runtime DI, Kotlin DSL, simple setup

### Key Pattern: Interface-Based Router

```kotlin
// ✅ Router interface — abstracts navigation implementation details
interface Router {
    fun navigateToDetails(itemId: String)
    fun navigateToSettings()
    fun navigateBack()
}
```

### Hilt Example (Recommended)

Important: `NavController` is tied to a `NavHostFragment` and usually should not be injected as a long-lived dependency at `ActivityComponent`/`SingletonComponent` level. Instead, inject a `Router` abstraction into the presenter and implement the `Router` so that it obtains and uses the current `NavController` via provided dependencies, callbacks or navigation events without breaking lifecycle constraints.

One safe option is to have a `Router` that receives a `navControllerProvider` from the UI layer or operates on navigation events (e.g., `LiveData`/`Flow`) rather than storing a `NavController` reference directly inside the presenter.

```kotlin
// Router implementation that uses NavController via a provider
class AppRouter @Inject constructor(
    private val navControllerProvider: () -> NavController
) : Router {

    private val navController: NavController
        get() = navControllerProvider()

    override fun navigateToDetails(itemId: String) {
        navController.navigate("details/$itemId")
    }

    override fun navigateToSettings() {
        navController.navigate("settings")
    }

    override fun navigateBack() {
        navController.popBackStack()
    }
}

// Hilt module — bind interface to implementation
@Module
@InstallIn(ActivityComponent::class)
abstract class NavigationModule {
    @Binds
    abstract fun bindRouter(impl: AppRouter): Router
}

// In Activity/Fragment, you can provide a navControllerProvider
// that captures the current NavController of your NavHostFragment.
// Concrete wiring depends on your app's navigation setup.

// ✅ Presenter with constructor-injected Router
class ProductListPresenter @Inject constructor(
    private val router: Router,
    private val repository: ProductRepository
) {
    fun onProductClicked(productId: String) {
        router.navigateToDetails(productId)
    }
}

// Fragment
@AndroidEntryPoint
class ProductListFragment : Fragment() {
    @Inject lateinit var presenter: ProductListPresenter
}
```

This example illustrates the idea: the presenter depends only on the `Router` interface; the `Router` implementation encapsulates NavController/host details and is scoped properly so that it does not hold invalid or leaking references.

### Koin Example

```kotlin
// Koin module
val navigationModule = module {
    // Router scoped to Activity or specific navigation host
    scope<MainActivity> {
        scoped<Router> { (navController: NavController) ->
            AppRouter(navControllerProvider = { navController })
        }
    }
}

val presenterModule = module {
    scope<ProductListFragment> {
        scoped { ProductListPresenter(router = get(), repository = get()) }
    }
}

// Fragment
class ProductListFragment : Fragment() {
    private val navController by lazy { findNavController() }

    private val presenter: ProductListPresenter by scopedInject(parameters = {
        parametersOf(navController)
    })
}
```

Again, the key idea: the presenter depends on an interface-based `Router`, and the router implementation (with proper scoping) knows how to reach the `NavController` or other navigation primitives. Other variants (like emitting navigation events) are also valid as long as you avoid leaking UI components into long-lived layers.

### Testing With Mock Router

```kotlin
class ProductListPresenterTest {
    private val mockRouter = mockk<Router>(relaxed = true)
    private val mockRepository = mockk<ProductRepository>()
    private lateinit var presenter: ProductListPresenter

    @Before
    fun setup() {
        presenter = ProductListPresenter(router = mockRouter, repository = mockRepository)
    }

    @Test
    fun `when product clicked, should navigate to details`() {
        presenter.onProductClicked("123")

        verify { mockRouter.navigateToDetails("123") }
    }
}
```

### Benefits of DI for Routers

1. **Loose coupling** — presenter depends only on `Router` interface, not `NavController`
2. **Easy testing** — router can be mocked/stubbed in unit tests
3. **Separation of concerns** — presentation logic is decoupled from navigation implementation details
4. **Reusability** — one `Router` (or a set of interfaces) can be reused across multiple presenters
5. **`Module` isolation** — feature modules depend on navigation abstractions instead of a concrete navigation stack

### Best Practices

```kotlin
// ✅ GOOD: Interface + constructor injection
class Presenter @Inject constructor(private val router: Router)

// ❌ BAD: Direct NavController dependency inside presenter
class Presenter @Inject constructor(private val navController: NavController)

// ✅ GOOD: Router scoped no longer than Activity/host component
@InstallIn(ActivityComponent::class)

// ❌ BAD: Singleton Router holding NavController (lifecycle issues)
@InstallIn(SingletonComponent::class)
```

---

## Дополнительные Вопросы (RU)

1. Как обрабатывать результаты навигации (например, выбор способа оплаты и возврат результата вызывающему экрану), сохраняя презентер независимым от конкретных навигационных API?
2. Как спроектировать абстракцию `Router`, которая одинаково хорошо работает и с навигацией на базе `Activity`, и с навигацией на базе `Fragment`?
3. Как правильно задавать области жизни (scope) для `Router` в мульти-модульных проектах, чтобы избежать утечек `NavController` или ссылок на `Activity`?
4. Как сочетать абстракции `Router` с `ViewModel`/MVI, представляя навигацию как события состояния?
5. Как тестировать навигационные сценарии end-to-end при использовании интерфейса `Router` (например, с помощью Espresso или Robolectric)?

## Follow-ups

1. How to handle navigation results (e.g., selecting payment method and returning result to caller) while keeping the presenter unaware of concrete navigation APIs?
2. How to design a router abstraction that works consistently across both `Activity`-based and `Fragment`-based navigation?
3. How to scope routers correctly in multi-module projects to avoid leaking `NavController` or `Activity` references?
4. How to combine `Router` abstractions with `ViewModel`/MVI state to model navigation as events?
5. How to test navigation flows end-to-end when using a router interface (e.g., with Espresso or Robolectric)?

## Ссылки (RU)

- [[c-dependency-injection]] — Принципы DI
- [Hilt Documentation](https://developer.android.com/training/dependency-injection/hilt-android)
- [Koin Documentation](https://insert-koin.io/)
- [Navigation `Component` Guide](https://developer.android.com/guide/navigation)

## References

- [[c-dependency-injection]] — DI principles
- [Hilt Documentation](https://developer.android.com/training/dependency-injection/hilt-android)
- [Koin Documentation](https://insert-koin.io/)
- [Navigation `Component` Guide](https://developer.android.com/guide/navigation)

## Связанные Вопросы (RU)

### База (Проще)
- [[q-play-feature-delivery--android--medium]] — Фиче-модули и навигация

### Похожие (Тот Же уровень)
- [[q-state-hoisting-compose--android--medium]] — Паттерны управления состоянием

### Продвинутые (Сложнее)
- [[q-android-modularization--android--medium]] — Навигация и границы модулей

## Related Questions

### Prerequisites (Easier)
- [[q-play-feature-delivery--android--medium]] — Feature modules with navigation

### Related (Same Level)
- [[q-state-hoisting-compose--android--medium]] — State management patterns

### Advanced (Harder)
- [[q-android-modularization--android--medium]] — Navigation and module boundaries
