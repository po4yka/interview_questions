---
id: 20251012-1227111166
title: "MVP Pattern / Паттерн MVP (Model-View-Presenter)"
aliases: ["MVP Pattern", "Паттерн MVP"]
topic: cs
subtopics: [android-architecture, architecture-patterns, separation-of-concerns, testability]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [q-clean-architecture--architecture-patterns--hard, q-mvi-pattern--architecture-patterns--hard, q-mvvm-pattern--architecture-patterns--medium]
created: 2025-10-15
updated: 2025-01-25
tags: [android-architecture, difficulty/medium, mvi, mvp, mvvm, separation-of-concerns, testability]
sources: [https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93presenter]
date created: Monday, October 6th 2025, 7:37:30 am
date modified: Sunday, October 26th 2025, 12:46:55 pm
---

# Вопрос (RU)
> Что такое паттерн MVP? Когда его использовать и как он работает?

# Question (EN)
> What is the MVP pattern? When to use it and how does it work?

---

## Ответ (RU)

**Теория MVP Pattern:**
MVP (Model-View-Presenter) - архитектурный паттерн для separation of concerns в presentation logic. Решает проблему: тестирование UI logic и business logic. Model - data layer (business logic, network, database). View - UI layer (отображение data, notifications о user actions). Presenter - логика UI и управление state View.

**Определение:**

*Теория:* MVP - архитектурный паттерн для facilitating automated unit testing и improving separation of concerns в presentation logic. Разделяет code на 3 части: business logic (Presenter), UI (View), data interaction (Model). View passive, не содержит business logic. Presenter может быть unit tested независимо от Android framework.

```kotlin
// ✅ MVP Structure
interface LoginContract {
    interface View {
        fun showProgress()
        fun hideProgress()
        fun showSuccess(user: User)
        fun showError(message: String)
    }

    interface Presenter {
        fun onLoginClicked(email: String, password: String)
        fun onDestroy()
    }
}

class LoginPresenter(private val view: LoginContract.View) : LoginContract.Presenter {
    private val model = LoginModel()

    override fun onLoginClicked(email: String, password: String) {
        view.showProgress()

        if (email.isEmpty() || password.isEmpty()) {
            view.hideProgress()
            view.showError("Fields cannot be empty")
            return
        }

        val user = model.login(email, password)
        view.hideProgress()

        if (user != null) {
            view.showSuccess(user)
        } else {
            view.showError("Invalid credentials")
        }
    }

    override fun onDestroy() { /* Cleanup */ }
}

class LoginActivity : AppCompatActivity(), LoginContract.View {
    private lateinit var presenter: LoginContract.Presenter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        presenter = LoginPresenter(this)

        loginButton.setOnClickListener {
            presenter.onLoginClicked(
                emailEditText.text.toString(),
                passwordEditText.text.toString()
            )
        }
    }

    override fun showProgress() = progressBar.visibility = View.VISIBLE
    override fun hideProgress() = progressBar.visibility = View.GONE
    override fun showSuccess(user: User) = Toast.makeText(this, "Welcome ${user.name}", Toast.LENGTH_SHORT).show()
    override fun showError(message: String) = Toast.makeText(this, message, Toast.LENGTH_SHORT).show()

    override fun onDestroy() {
        presenter.onDestroy()
        super.onDestroy()
    }
}
```

**Компоненты MVP:**

**1. Model:**
*Теория:* Model - data layer. Отвечает за: business logic, network calls, database operations, data transformations. Представляет domain logic и data structures. View не имеет direct access к Model. Все interactions через Presenter.

```kotlin
// ✅ Model - data layer
class LoginModel {
    suspend fun login(email: String, password: String): User? {
        return try {
            val response = apiService.login(email, password)
            if (response.isSuccessful) {
                database.userDao().save(response.body())
                response.body()
            } else null
        } catch (e: Exception) {
            null
        }
    }
}
```

**2. View:**
*Теория:* View - UI layer. Отвечает за: displaying data, user input handling, UI updates. View passive - не содержит business logic. Реализуется в Activity/Fragment. Имеет reference к Presenter через interface (Contract). Уведомляет Presenter о user actions.

```kotlin
// ✅ View - passive UI
class ProductListFragment : Fragment(), ProductContract.View {
    private lateinit var presenter: ProductContract.Presenter

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        presenter = ProductPresenter(this)
        presenter.loadProducts()
    }

    override fun showProducts(products: List<Product>) {
        adapter.submitList(products)
    }

    override fun showError(message: String) {
        Snackbar.make(requireView(), message, Snackbar.LENGTH_SHORT).show()
    }
}
```

**3. Presenter:**
*Теория:* Presenter - mediator между Model и View. Отвечает за: business logic для UI, управление View state, validation input, координация Model и View. Имеет references к View (через interface) и Model. Testable без Android framework.

```kotlin
// ✅ Presenter - business logic
class ProductPresenter(private val view: ProductContract.View) : ProductContract.Presenter {
    private val model = ProductModel()

    override fun loadProducts() {
        view.showProgress()
        model.getProducts(
            onSuccess = { products ->
                view.hideProgress()
                view.showProducts(products)
            },
            onError = { error ->
                view.hideProgress()
                view.showError(error.message)
            }
        )
    }
}
```

**Contract Interface:**

*Теория:* Contract interface определяет relationship между View и Presenter. Содержит 2 inner interfaces: View и Presenter. View interface - methods для Presenter для updates UI. Presenter interface - methods для View для user actions. Делает code более readable и testable.

```kotlin
// ✅ Contract interface
interface UserProfileContract {
    interface View {
        fun showUserInfo(user: User)
        fun showLoading()
        fun hideLoading()
        fun showError(message: String)
    }

    interface Presenter {
        fun onViewCreated()
        fun onRefreshClicked()
        fun onEditClicked()
        fun onDestroy()
    }
}

// Presenter и View оба reference Contract
class UserProfilePresenter(
    private val view: UserProfileContract.View,
    private val model: UserProfileModel
) : UserProfileContract.Presenter {
    // Implementation
}

class UserProfileActivity : AppCompatActivity(), UserProfileContract.View {
    private lateinit var presenter: UserProfileContract.Presenter
    // Implementation
}
```

**Преимущества:**

1. **Separation of Concerns** - clear separation между UI, business logic, data
2. **Testability** - Presenter unit testable без Android framework
3. **No Android Framework Dependency** - Presenter не зависит от Android
4. **Easy Maintenance** - code modular и easy to maintain
5. **No Conceptual Relationship** - нет tight coupling с Android components

**Недостатки:**

1. **Presenter Expansion** - может стать huge all-knowing class если не следовать Single Responsibility
2. **Overhead для Small Apps** - излишен для простых приложений
3. **Interface Complexity** - много interfaces может быть overwhelming
4. **Memory Leaks** - нужно правильно manage Presenter lifecycle

**Когда использовать:**

*Теория:* Используйте MVP когда: нужна высокая testability, complex business logic, teams following clean architecture, UI logic должен быть separated от Android framework. Не используйте для: simple apps (over-engineering), prototypes (unnecessary overhead).

✅ **Use MVP when:**
- Высокая testability нужна
- Complex business logic
- Clean architecture principles
- UI logic нужно separate от Android framework

❌ **Don't use MVP when:**
- Simple apps (over-engineering)
- Prototypes (unnecessary overhead)
- Team не familiar с pattern

**MVP vs MVVM vs MVI:**

*Теория:* MVP - View passive, Presenter contains UI logic. MVVM - View binding к ViewModel, Two-way binding, LiveData/StateFlow. MVI - unidirectional flow, Intent-based, immutable state. MVP - best для testability, MVVM - best для two-way binding, MVI - best для strict state management.

**Ключевые концепции:**

1. **Contract Interface** - определяет View и Presenter interfaces
2. **Passive View** - View только displays, не содержит logic
3. **Testability** - Presenter unit testable
4. **Separation of Concerns** - clear boundaries между layers
5. **No Android Dependency** - Presenter не зависит от Android

## Answer (EN)

**MVP Pattern Theory:**
MVP (Model-View-Presenter) - architecture pattern for separation of concerns in presentation logic. Solves problem: testing UI logic and business logic. Model - data layer (business logic, network, database). View - UI layer (displays data, notifies about user actions). Presenter - UI logic and manages View state.

**Definition:**

*Theory:* MVP - architecture pattern for facilitating automated unit testing and improving separation of concerns in presentation logic. Separates code into 3 parts: business logic (Presenter), UI (View), data interaction (Model). View passive, doesn't contain business logic. Presenter can be unit tested independently from Android framework.

```kotlin
// ✅ MVP Structure
interface LoginContract {
    interface View {
        fun showProgress()
        fun hideProgress()
        fun showSuccess(user: User)
        fun showError(message: String)
    }

    interface Presenter {
        fun onLoginClicked(email: String, password: String)
        fun onDestroy()
    }
}

class LoginPresenter(private val view: LoginContract.View) : LoginContract.Presenter {
    private val model = LoginModel()

    override fun onLoginClicked(email: String, password: String) {
        view.showProgress()

        if (email.isEmpty() || password.isEmpty()) {
            view.hideProgress()
            view.showError("Fields cannot be empty")
            return
        }

        val user = model.login(email, password)
        view.hideProgress()

        if (user != null) {
            view.showSuccess(user)
        } else {
            view.showError("Invalid credentials")
        }
    }

    override fun onDestroy() { /* Cleanup */ }
}

class LoginActivity : AppCompatActivity(), LoginContract.View {
    private lateinit var presenter: LoginContract.Presenter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        presenter = LoginPresenter(this)

        loginButton.setOnClickListener {
            presenter.onLoginClicked(
                emailEditText.text.toString(),
                passwordEditText.text.toString()
            )
        }
    }

    override fun showProgress() = progressBar.visibility = View.VISIBLE
    override fun hideProgress() = progressBar.visibility = View.GONE
    override fun showSuccess(user: User) = Toast.makeText(this, "Welcome ${user.name}", Toast.LENGTH_SHORT).show()
    override fun showError(message: String) = Toast.makeText(this, message, Toast.LENGTH_SHORT).show()

    override fun onDestroy() {
        presenter.onDestroy()
        super.onDestroy()
    }
}
```

**MVP Components:**

**1. Model:**
*Theory:* Model - data layer. Responsible for: business logic, network calls, database operations, data transformations. Represents domain logic and data structures. View has no direct access to Model. All interactions through Presenter.

```kotlin
// ✅ Model - data layer
class LoginModel {
    suspend fun login(email: String, password: String): User? {
        return try {
            val response = apiService.login(email, password)
            if (response.isSuccessful) {
                database.userDao().save(response.body())
                response.body()
            } else null
        } catch (e: Exception) {
            null
        }
    }
}
```

**2. View:**
*Theory:* View - UI layer. Responsible for: displaying data, user input handling, UI updates. View passive - doesn't contain business logic. Implemented in Activity/Fragment. Has reference to Presenter through interface (Contract). Notifies Presenter about user actions.

```kotlin
// ✅ View - passive UI
class ProductListFragment : Fragment(), ProductContract.View {
    private lateinit var presenter: ProductContract.Presenter

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        presenter = ProductPresenter(this)
        presenter.loadProducts()
    }

    override fun showProducts(products: List<Product>) {
        adapter.submitList(products)
    }

    override fun showError(message: String) {
        Snackbar.make(requireView(), message, Snackbar.LENGTH_SHORT).show()
    }
}
```

**3. Presenter:**
*Theory:* Presenter - mediator between Model and View. Responsible for: business logic for UI, manages View state, validates input, coordinates Model and View. Has references to View (through interface) and Model. Testable without Android framework.

```kotlin
// ✅ Presenter - business logic
class ProductPresenter(private val view: ProductContract.View) : ProductContract.Presenter {
    private val model = ProductModel()

    override fun loadProducts() {
        view.showProgress()
        model.getProducts(
            onSuccess = { products ->
                view.hideProgress()
                view.showProducts(products)
            },
            onError = { error ->
                view.hideProgress()
                view.showError(error.message)
            }
        )
    }
}
```

**Contract Interface:**

*Theory:* Contract interface defines relationship between View and Presenter. Contains 2 inner interfaces: View and Presenter. View interface - methods for Presenter to update UI. Presenter interface - methods for View for user actions. Makes code more readable and testable.

```kotlin
// ✅ Contract interface
interface UserProfileContract {
    interface View {
        fun showUserInfo(user: User)
        fun showLoading()
        fun hideLoading()
        fun showError(message: String)
    }

    interface Presenter {
        fun onViewCreated()
        fun onRefreshClicked()
        fun onEditClicked()
        fun onDestroy()
    }
}

// Presenter and View both reference Contract
class UserProfilePresenter(
    private val view: UserProfileContract.View,
    private val model: UserProfileModel
) : UserProfileContract.Presenter {
    // Implementation
}

class UserProfileActivity : AppCompatActivity(), UserProfileContract.View {
    private lateinit var presenter: UserProfileContract.Presenter
    // Implementation
}
```

**Advantages:**

1. **Separation of Concerns** - clear separation between UI, business logic, data
2. **Testability** - Presenter unit testable without Android framework
3. **No Android Framework Dependency** - Presenter doesn't depend on Android
4. **Easy Maintenance** - code modular and easy to maintain
5. **No Conceptual Relationship** - no tight coupling with Android components

**Disadvantages:**

1. **Presenter Expansion** - may become huge all-knowing class if not following Single Responsibility
2. **Overhead for Small Apps** - unnecessary for simple applications
3. **Interface Complexity** - many interfaces can be overwhelming
4. **Memory Leaks** - need to properly manage Presenter lifecycle

**When to Use:**

*Theory:* Use MVP when: need high testability, complex business logic, teams following clean architecture, UI logic needs to be separated from Android framework. Don't use for: simple apps (over-engineering), prototypes (unnecessary overhead).

✅ **Use MVP when:**
- High testability needed
- Complex business logic
- Clean architecture principles
- UI logic needs separation from Android framework

❌ **Don't use MVP when:**
- Simple apps (over-engineering)
- Prototypes (unnecessary overhead)
- Team not familiar with pattern

**MVP vs MVVM vs MVI:**

*Theory:* MVP - View passive, Presenter contains UI logic. MVVM - View binding to ViewModel, two-way binding, LiveData/StateFlow. MVI - unidirectional flow, intent-based, immutable state. MVP - best for testability, MVVM - best for two-way binding, MVI - best for strict state management.

**Key Concepts:**

1. **Contract Interface** - defines View and Presenter interfaces
2. **Passive View** - View only displays, doesn't contain logic
3. **Testability** - Presenter unit testable
4. **Separation of Concerns** - clear boundaries between layers
5. **No Android Dependency** - Presenter doesn't depend on Android

---

## Follow-ups

- How does MVP pattern ensure testability?
- What is the difference between MVP and MVVM?
- How do you prevent memory leaks in MVP Presenter?

## Related Questions

### Prerequisites (Easier)
- Basic Android architecture concepts
- Understanding of separation of concerns

### Related (Same Level)
- [[q-mvvm-pattern--architecture-patterns--medium]] - MVVM pattern
- [[q-mvi-pattern--architecture-patterns--hard]] - MVI pattern

### Advanced (Harder)
- [[q-clean-architecture--architecture-patterns--hard]] - Clean Architecture
- Advanced MVP implementations
- Testing strategies for MVP

