---
id: android-215
title: "Inject Router To Presenter / Инъекция Router в Presenter"
aliases: ["Inject Router To Presenter", "Router DI", "Инъекция Router в Presenter", "Инъекция роутера"]
topic: android
subtopics: [architecture-mvi, di-hilt, di-koin]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-play-feature-delivery--android--medium, q-state-hoisting-compose--android--medium]
created: 2025-10-15
updated: 2025-10-30
tags: [android/architecture-mvi, android/di-hilt, android/di-koin, dependency-injection, difficulty/medium, navigation, router]

---

# Вопрос (RU)

> Что использовать для того, чтобы роутер инжектился напрямую в презентер?

# Question (EN)

> What to use to inject router directly into presenter?

---

## Ответ (RU)

Для внедрения роутера в презентер используйте **Dependency Injection (DI)** фреймворки. Они обеспечивают слабую связанность, упрощают тестирование и позволяют следовать SOLID-принципам.

**Основные подходы**:

1. **Hilt** — официальный Android DI, минимальный boilerplate
2. **Dagger 2** — compile-time DI, больше контроля
3. **Koin** — runtime DI, Kotlin DSL, простая настройка

### Ключевой Паттерн: Interface-Based Router

```kotlin
// ✅ Интерфейс роутера — абстрагирует навигацию
interface Router {
    fun navigateToDetails(itemId: String)
    fun navigateToSettings()
    fun navigateBack()
}
```

### Пример С Hilt (Рекомендуется)

```kotlin
// Реализация роутера
class AppRouter @Inject constructor(
    private val navController: NavController
) : Router {
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

// Модуль Hilt
@Module
@InstallIn(ActivityComponent::class)
abstract class NavigationModule {
    @Binds
    abstract fun bindRouter(impl: AppRouter): Router
}

// ✅ Презентер с конструкторной инъекцией
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

### Пример С Koin

```kotlin
// Модуль Koin
val navigationModule = module {
    scope<MainActivity> {
        scoped<Router> {
            NavigationRouter(
                findNavController = { (getSource() as MainActivity).findNavController(R.id.nav_host_fragment) }
            )
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

### Тестирование С Mock Роутером

```kotlin
class ProductPresenterTest {
    private val mockRouter = mockk<Router>(relaxed = true)
    private lateinit var presenter: ProductPresenter

    @Before
    fun setup() {
        presenter = ProductPresenter(router = mockRouter, repository = mockRepository)
    }

    @Test
    fun `when product clicked, should navigate to details`() {
        presenter.onProductClicked("123")

        verify { mockRouter.navigateToDetails("123") }
    }
}
```

### Преимущества DI Для Роутеров

1. **Слабая связанность** — презентер не зависит от NavController
2. **Легкое тестирование** — mock-роутер в unit-тестах
3. **Single Responsibility** — презентер не знает о навигации
4. **Переиспользование** — один роутер для многих презентеров
5. **Изоляция модулей** — feature модули не зависят от реализации навигации

### Best Practices

```kotlin
// ✅ GOOD: Interface + constructor injection
class Presenter @Inject constructor(private val router: Router)

// ❌ BAD: Direct NavController dependency
class Presenter @Inject constructor(private val navController: NavController)

// ✅ GOOD: Activity-scoped router
@InstallIn(ActivityComponent::class)

// ❌ BAD: Singleton router with NavController (lifecycle issues)
@InstallIn(SingletonComponent::class)
```

---

## Answer (EN)

To inject a router into a presenter, use **Dependency Injection (DI)** frameworks. They ensure loose coupling, facilitate testing, and help follow SOLID principles.

**Main Approaches**:

1. **Hilt** — official Android DI, minimal boilerplate
2. **Dagger 2** — compile-time DI, more control
3. **Koin** — runtime DI, Kotlin DSL, simple setup

### Key Pattern: Interface-Based Router

```kotlin
// ✅ Router interface — abstracts navigation logic
interface Router {
    fun navigateToDetails(itemId: String)
    fun navigateToSettings()
    fun navigateBack()
}
```

### Hilt Example (Recommended)

```kotlin
// Router implementation
class AppRouter @Inject constructor(
    private val navController: NavController
) : Router {
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

// Hilt module
@Module
@InstallIn(ActivityComponent::class)
abstract class NavigationModule {
    @Binds
    abstract fun bindRouter(impl: AppRouter): Router
}

// ✅ Presenter with constructor injection
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

### Koin Example

```kotlin
// Koin module
val navigationModule = module {
    scope<MainActivity> {
        scoped<Router> {
            NavigationRouter(
                findNavController = { (getSource() as MainActivity).findNavController(R.id.nav_host_fragment) }
            )
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

### Testing With Mock Router

```kotlin
class ProductPresenterTest {
    private val mockRouter = mockk<Router>(relaxed = true)
    private lateinit var presenter: ProductPresenter

    @Before
    fun setup() {
        presenter = ProductPresenter(router = mockRouter, repository = mockRepository)
    }

    @Test
    fun `when product clicked, should navigate to details`() {
        presenter.onProductClicked("123")

        verify { mockRouter.navigateToDetails("123") }
    }
}
```

### Benefits of DI for Routers

1. **Loose coupling** — presenter doesn't depend on NavController
2. **Easy testing** — mock router in unit tests
3. **Single Responsibility** — presenter doesn't handle navigation
4. **Reusability** — one router for multiple presenters
5. **Module isolation** — feature modules don't depend on navigation implementation

### Best Practices

```kotlin
// ✅ GOOD: Interface + constructor injection
class Presenter @Inject constructor(private val router: Router)

// ❌ BAD: Direct NavController dependency
class Presenter @Inject constructor(private val navController: NavController)

// ✅ GOOD: Activity-scoped router
@InstallIn(ActivityComponent::class)

// ❌ BAD: Singleton router with NavController (lifecycle issues)
@InstallIn(SingletonComponent::class)
```

---

## Follow-ups

1. How to handle navigation results (e.g., selecting payment method and returning result to caller)?
2. How to implement deep link routing in multi-module app with feature-based navigation?
3. What are the lifecycle implications of different DI scopes (`Activity` vs `Fragment`) for routers?
4. How to test navigation flows in integration tests without mocking the router?
5. How to migrate from `Activity`-based navigation (`Intent`) to `Fragment`-based (NavController) while keeping presenters unchanged?

## References

- [[c-dependency-injection]] — DI principles
-  — Android Navigation Component
- [[c-mvvm-pattern]] — Presenter pattern
- [Hilt Documentation](https://developer.android.com/training/dependency-injection/hilt-android)
- [Koin Documentation](https://insert-koin.io/)
- [Navigation Component Guide](https://developer.android.com/guide/navigation)

## Related Questions

### Prerequisites (Easier)
-  — DI basics
-  — DI framework comparison

### Related (Same Level)
- [[q-play-feature-delivery--android--medium]] — Feature modules with navigation
- [[q-state-hoisting-compose--android--medium]] — State management patterns

### Advanced (Harder)
-  — Deep link routing across modules
-  — Navigation with results
