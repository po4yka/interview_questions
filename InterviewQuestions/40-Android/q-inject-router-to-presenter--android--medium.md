---
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

---

# Вопрос (RU)

> Что использовать для того, чтобы роутер инжектился напрямую в презентер?

# Question (EN)

> What to use to inject router directly into presenter?

---

## Ответ (RU)

Для внедрения роутера в презентер используйте **Dependency Injection (DI)** фреймворки. Они обеспечивают слабую связанность, упрощают тестирование и позволяют лучше следовать SOLID-принципам.

**Основные подходы**:

1. **Hilt** — официальный Android DI, минимальный boilerplate
2. **Dagger 2** — compile-time DI, больше контроля
3. **Koin** — runtime DI, Kotlin DSL, простая настройка

### Ключевой паттерн: Router через интерфейс

```kotlin
// ✅ Интерфейс роутера — абстрагирует детали реализации навигации
interface Router {
    fun navigateToDetails(itemId: String)
    fun navigateToSettings()
    fun navigateBack()
}
```

### Пример с Hilt (Рекомендуется)

Важно: `NavController` привязан к `NavHostFragment` и обычно не инжектится напрямую как зависимость на уровне `ActivityComponent`/`SingletonComponent`. Вместо этого инжектируйте абстракцию `Router`, а внутри реализации получайте `NavController` из актуального `Fragment`/`View` (или передавайте его в методах), чтобы избежать проблем с жизненным циклом.

```kotlin
// Реализация роутера, завязанная на NavController
class AppRouter @Inject constructor() : Router {

    // Получение NavController должно быть безопасно по жизненному циклу,
    // например, через слабую ссылку на Activity/Fragment или через callback.
    private fun navController(fragment: Fragment): NavController =
        fragment.findNavController()

    override fun navigateToDetails(itemId: String) {
        // пример: навигация должна выполняться с актуального fragment/navController
        // navController(currentFragment).navigate("details/$itemId")
    }

    override fun navigateToSettings() {
        // navController(currentFragment).navigate("settings")
    }

    override fun navigateBack() {
        // navController(currentFragment).popBackStack()
    }
}

// Модуль Hilt — биндим интерфейс на реализацию без нарушения жизненного цикла
@Module
@InstallIn(ActivityComponent::class)
abstract class NavigationModule {
    @Binds
    abstract fun bindRouter(impl: AppRouter): Router
}

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

Этот пример демонстрирует идею: презентер получает `Router` по интерфейсу, а конкретная реализация `Router` знает, как работать с `NavController`/`Activity`/`Fragment`. Важно спроектировать `Router` так, чтобы он не держал долгоживущих ссылок на `NavController`.

### Пример с Koin

```kotlin
// Модуль Koin
val navigationModule = module {
    // Router с областью жизни Activity или конкретного навигационного контейнера
    scope<MainActivity> {
        scoped<Router> {
            // Реализация должна безопасно получать NavController,
            // например, через activity.findNavController(...)
            AppRouter()
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
    private val presenter: ProductListPresenter by inject()
}
```

Здесь также ключевая идея: презентер получает `Router` по интерфейсу, а детали получения `NavController` инкапсулируются в реализации роутера и должны быть согласованы с областью жизни (scope).

### Тестирование с mock Router

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

### Преимущества DI для роутеров

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

**Main approaches**:

1. **Hilt** — official Android DI, minimal boilerplate
2. **Dagger 2** — compile-time DI, more control
3. **Koin** — runtime DI, Kotlin DSL, simple setup

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

Important: `NavController` is tied to a `NavHostFragment` and usually should not be injected as a long-lived dependency at `ActivityComponent`/`SingletonComponent` level. Instead, inject a `Router` abstraction into the presenter and let the router implementation deal with obtaining/using the current `NavController` safely.

```kotlin
// Router implementation that works with NavController
class AppRouter @Inject constructor() : Router {

    // NavController access must respect the lifecycle,
    // e.g., via a weak reference to Activity/Fragment or a callback.
    private fun navController(fragment: Fragment): NavController =
        fragment.findNavController()

    override fun navigateToDetails(itemId: String) {
        // Example: perform navigation using the current fragment/navController
        // navController(currentFragment).navigate("details/$itemId")
    }

    override fun navigateToSettings() {
        // navController(currentFragment).navigate("settings")
    }

    override fun navigateBack() {
        // navController(currentFragment).popBackStack()
    }
}

// Hilt module — bind interface to implementation without breaking lifecycle constraints
@Module
@InstallIn(ActivityComponent::class)
abstract class NavigationModule {
    @Binds
    abstract fun bindRouter(impl: AppRouter): Router
}

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

This example illustrates the idea: the presenter depends only on the `Router` interface, and the `Router` implementation encapsulates the `NavController`/host component details. It is crucial to design the router so it does not hold long-lived references to a specific `NavController` instance.

### Koin Example

```kotlin
// Koin module
val navigationModule = module {
    // Router scoped to Activity or specific navigation host
    scope<MainActivity> {
        scoped<Router> {
            // Implementation must obtain NavController safely,
            // for example via activity.findNavController(...)
            AppRouter()
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
    private val presenter: ProductListPresenter by inject()
}
```

Again, the key idea: the presenter gets an interface-based `Router`, and the router implementation (with proper scoping) handles how to reach the `NavController` or other navigation primitives.

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
5. **Module isolation** — feature modules depend on navigation abstractions instead of concrete navigation stack

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

## Дополнительные вопросы (RU)

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
- [Hilt Documentation]("https://developer.android.com/training/dependency-injection/hilt-android")
- [Koin Documentation]("https://insert-koin.io/")
- [Navigation Component Guide]("https://developer.android.com/guide/navigation")

## References

- [[c-dependency-injection]] — DI principles
- [Hilt Documentation]("https://developer.android.com/training/dependency-injection/hilt-android")
- [Koin Documentation]("https://insert-koin.io/")
- [Navigation Component Guide]("https://developer.android.com/guide/navigation")

## Связанные вопросы (RU)

### База (Проще)
- [[q-play-feature-delivery--android--medium]] — Фиче-модули и навигация

### Похожие (Тот же уровень)
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
