---
id: cs-029
title: "MVP Pattern / Паттерн MVP (Model-View-Presenter)"
aliases: ["MVP Pattern", "Паттерн MVP"]
topic: cs
subtopics: [architecture-patterns, separation-of-concerns, testability]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-architecture-patterns, q-adapter-pattern--cs--medium, q-abstract-factory-pattern--cs--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [architecture-patterns, difficulty/medium, mvi, mvp, mvvm, separation-of-concerns, testability]
sources: ["https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93presenter"]

---

# Вопрос (RU)
> Что такое паттерн MVP? Когда его использовать и как он работает?

# Question (EN)
> What is the MVP pattern? When to use it and how does it work?

---

## Ответ (RU)

**Теория MVP Pattern:**
MVP (Model-`View`-Presenter) — архитектурный паттерн, улучшающий разделение ответственностей (separation of concerns) в слое представления (presentation layer). Основные цели: упростить тестирование логики представления (presentation logic), минимизировать зависимость этой логики от UI-фреймворка и отделить работу с данными от UI.

Model — слой данных и доменной логики (network, database, бизнес-правила).
`View` — слой UI (отображение данных, сообщения пользователю, делегирование пользовательских действий презентеру).
Presenter — оркестрирует взаимодействие между Model и `View`, содержит presentation logic (валидация, форматирование, выбор состояний `View`), но не доменную бизнес-логику.

**Определение:**

*Теория:* MVP — архитектурный паттерн для облегчения модульного тестирования и повышения разделения ответственностей в presentation logic. Разделяет код на 3 части: UI (`View`), presentation logic и координация (Presenter), работа с данными и доменной логикой (Model/Use Cases). `View` пассивен и не содержит бизнес-логики. Presenter можно unit-тестировать независимо от Android framework, если он не использует Android API напрямую.

```kotlin
// ✅ MVP Structure (упрощенный пример)
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

class LoginPresenter(
    private var view: LoginContract.View?,
    private val model: LoginModel
) : LoginContract.Presenter {

    override fun onLoginClicked(email: String, password: String) {
        val currentView = view ?: return
        currentView.showProgress()

        if (email.isEmpty() || password.isEmpty()) {
            currentView.hideProgress()
            currentView.showError("Fields cannot be empty")
            return
        }

        // В реальном MVP асинхронный вызов Model (callbacks/coroutines/Rx). Здесь псевдокод:
        model.login(
            email = email,
            password = password,
            onResult = { user ->
                val v = view ?: return@login
                v.hideProgress()
                if (user != null) {
                    v.showSuccess(user)
                } else {
                    v.showError("Invalid credentials")
                }
            }
        )
    }

    override fun onDestroy() {
        // Освобождаем ссылку на View, чтобы избежать утечки памяти
        view = null
    }
}

class LoginActivity : AppCompatActivity(), LoginContract.View {
    private lateinit var presenter: LoginContract.Presenter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // setContentView(...)
        presenter = LoginPresenter(this, LoginModel())

        // loginButton, emailEditText, etc. предполагаются как уже инициализированные view
        loginButton.setOnClickListener {
            presenter.onLoginClicked(
                emailEditText.text.toString(),
                passwordEditText.text.toString()
            )
        }
    }

    override fun showProgress() { progressBar.visibility = View.VISIBLE }
    override fun hideProgress() { progressBar.visibility = View.GONE }
    override fun showSuccess(user: User) {
        Toast.makeText(this, "Welcome ${user.name}", Toast.LENGTH_SHORT).show()
    }
    override fun showError(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }

    override fun onDestroy() {
        presenter.onDestroy()
        super.onDestroy()
    }
}
```

(Пример упрощён и иллюстрирует структуру контракта; детали инициализации view и асинхронности опущены.)

**Компоненты MVP:**

**1. Model:**
*Теория:* Model — слой данных и доменной логики. Отвечает за: бизнес-правила, network calls, database operations, data transformations. `View` не обращается к Model напрямую: все взаимодействие с Model организует Presenter.

```kotlin
// ✅ Model - data + domain layer (сигнатура согласована с использованием)
class LoginModel {
    fun login(
        email: String,
        password: String,
        onResult: (User?) -> Unit
    ) {
        // Реализация может быть асинхронной (например, через корутины или callbacks)
        // Здесь псевдокод:
        try {
            val response = apiService.login(email, password).execute()
            val user = if (response.isSuccessful) {
                response.body()?.also { database.userDao().save(it) }
            } else {
                null
            }
            onResult(user)
        } catch (e: Exception) {
            onResult(null)
        }
    }
}
```

**2. `View`:**
*Теория:* `View` — UI слой. Отвечает за отображение данных, приём ввода пользователя и делегирование действий презентеру. Пассивен: содержит минимум логики, не знает о том, как получать данные или реализована бизнес-логика. Реализуется в `Activity`/`Fragment`/Custom `View` и имеет ссылку на Presenter через контракт.

```kotlin
// ✅ View - passive UI (упрощенный пример)
class ProductListFragment : Fragment(), ProductContract.View {
    private lateinit var presenter: ProductContract.Presenter

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        presenter = ProductPresenter(this, ProductModel())
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
*Теория:* Presenter — посредник между Model и `View`. Отвечает за presentation logic: обработку пользовательского ввода (через вызовы из `View`), запросы к Model, выбор и установку состояний `View`. Имеет ссылки на `View` (через интерфейс) и Model. Легко тестируется, так как не зависит от Android API (если соблюдать правило отсутствия прямых Android-зависимостей).

```kotlin
// ✅ Presenter - presentation logic
class ProductPresenter(
    private var view: ProductContract.View?,
    private val model: ProductModel
) : ProductContract.Presenter {

    override fun loadProducts() {
        val currentView = view ?: return
        currentView.showProgress()
        model.getProducts(
            onSuccess = { products ->
                val v = view ?: return@getProducts
                v.hideProgress()
                v.showProducts(products)
            },
            onError = { error ->
                val v = view ?: return@getProducts
                v.hideProgress()
                v.showError(error.message ?: "Unknown error")
            }
        )
    }

    override fun onDestroy() {
        view = null
    }
}
```

**Contract Interface:**

*Теория:* Contract interface определяет границы между `View` и Presenter. Обычно содержит две вложенные интерфейсные части: `View` и Presenter. 
- `View`-интерфейс описывает методы, которые Presenter может вызывать для обновления UI. 
- Presenter-интерфейс описывает методы, которые `View` вызывает, чтобы сообщить о событиях (жизненный цикл, клики, ввод пользователя).

Это делает связи явными, уменьшает связность и упрощает тестирование.

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

// Presenter и View оба используют контракт
class UserProfilePresenter(
    private var view: UserProfileContract.View?,
    private val model: UserProfileModel
) : UserProfileContract.Presenter {
    override fun onViewCreated() { /* ... */ }
    override fun onRefreshClicked() { /* ... */ }
    override fun onEditClicked() { /* ... */ }
    override fun onDestroy() { view = null }
}

class UserProfileActivity : AppCompatActivity(), UserProfileContract.View {
    private lateinit var presenter: UserProfileContract.Presenter
    // Implementation
}
```

**Преимущества:**

1. **Separation of Concerns** — чёткое разделение между UI (`View`), presentation logic (Presenter) и данными/доменом (Model).
2. **Testability** — Presenter легко unit-тестировать отдельно от Android, при условии отсутствия прямых Android-зависимостей.
3. **Снижение зависимостей от Android в логике** — Presenter не зависит от Android UI-компонентов.
4. **Easy Maintenance** — код модульный, проще изменять и расширять.

**Недостатки:**

1. **Presenter Expansion (God Object)** — при неправильном дизайне Presenter может разрастись и нарушить Single Responsibility.
2. **Overhead для Small Apps** — избыточная структуризация для очень простых приложений.
3. **Interface Complexity** — большое количество контрактов и интерфейсов может усложнять код.
4. **Memory Leaks Risk** — необходимо вовремя обнулять ссылку на `View` в Presenter (detachView/onDestroy), особенно при длительных операциях.

**Когда использовать:**

*Теория:* Используйте MVP когда: важна высокая тестируемость presentation logic, есть относительно сложная логика взаимодействия с данными и состояниями UI, команда следует принципам чистой архитектуры, и нужно минимизировать зависимость логики от Android framework. Избегайте MVP там, где структура добавляет лишнюю сложность: очень простые приложения, быстрые прототипы, команды, не знакомые с паттерном.

✅ **Use MVP when:**
- Нужна высокая testability слоя представления
- Есть сложная логика взаимодействия UI с данными
- Следуете clean architecture principles
- Хотите отделить presentation logic от Android API

❌ **Don't use MVP when:**
- Очень простые приложения (over-engineering)
- Прототипы (лишний оверхед)
- Команда не знакома с паттерном и не готова его поддерживать

**MVP vs MVVM vs MVI:**

*Теория:* 
- MVP: пассивный `View`, Presenter управляет состоянием `View` и вызывает Model. Хорошо контролируется поток данных, Presenter легко мокать и тестировать.
- MVVM: `ViewModel` экспонирует данные/состояния (`LiveData`/`StateFlow` и т.п.), `View` подписывается на изменения. Двусторонний data binding возможен, но не обязателен.
- MVI: однонаправленный поток данных, намерения (intents), редьюсер и иммутабельное состояние.

Все три могут обеспечивать высокую тестируемость при корректной реализации. MVP не является "лучшим" по умолчанию; выбор зависит от требований к управлению состоянием, используемого инструментария и предпочтений/опыта команды.

**Ключевые концепции:**

1. **Contract Interface** — явно определяет интерфейсы `View` и Presenter.
2. **Passive `View`** — `View` отвечает только за отображение и делегирование событий, без бизнес-логики.
3. **Testability** — Presenter можно тестировать отдельно от Android.
4. **Separation of Concerns** — чёткие границы между UI, presentation logic и Model.
5. **Минимизация Android-зависимостей в Presenter** — Presenter не использует Android API напрямую, что упрощает тестирование.

---

## Answer (EN)

**MVP Pattern Theory:**
MVP (Model-`View`-Presenter) is an architectural pattern that improves separation of concerns in the presentation layer. Its main goals are: make presentation logic easier to test, minimize its dependency on the UI framework, and separate data handling from UI.

Model: data and domain layer (network, database, business rules).
`View`: UI layer (renders data, shows messages, delegates user actions to the presenter).
Presenter: orchestrates communication between Model and `View`, holds presentation logic (validation, formatting, choosing `View` states), but not core domain business logic.

**Definition:**

*Theory:* MVP is an architectural pattern for facilitating automated unit testing and improving separation of concerns in the presentation layer. It splits code into three parts: UI (`View`), presentation/coordination logic (Presenter), and data/domain logic (Model/Use Cases). The `View` is passive and contains no business logic. The Presenter can be unit tested independently from the Android framework as long as it avoids direct Android API usage.

```kotlin
// ✅ MVP Structure (simplified example)
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

class LoginPresenter(
    private var view: LoginContract.View?,
    private val model: LoginModel
) : LoginContract.Presenter {

    override fun onLoginClicked(email: String, password: String) {
        val currentView = view ?: return
        currentView.showProgress()

        if (email.isEmpty() || password.isEmpty()) {
            currentView.hideProgress()
            currentView.showError("Fields cannot be empty")
            return
        }

        // In real MVP this should be async (callbacks/coroutines/Rx). Pseudocode for brevity:
        model.login(
            email = email,
            password = password,
            onResult = { user ->
                val v = view ?: return@login
                v.hideProgress()
                if (user != null) {
                    v.showSuccess(user)
                } else {
                    v.showError("Invalid credentials")
                }
            }
        )
    }

    override fun onDestroy() {
        // Clear View reference to avoid memory leaks
        view = null
    }
}

class LoginActivity : AppCompatActivity(), LoginContract.View {
    private lateinit var presenter: LoginContract.Presenter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // setContentView(...)
        presenter = LoginPresenter(this, LoginModel())

        // loginButton, emailEditText, etc. are assumed to be initialized views
        loginButton.setOnClickListener {
            presenter.onLoginClicked(
                emailEditText.text.toString(),
                passwordEditText.text.toString()
            )
        }
    }

    override fun showProgress() { progressBar.visibility = View.VISIBLE }
    override fun hideProgress() { progressBar.visibility = View.GONE }
    override fun showSuccess(user: User) {
        Toast.makeText(this, "Welcome ${user.name}", Toast.LENGTH_SHORT).show()
    }
    override fun showError(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }

    override fun onDestroy() {
        presenter.onDestroy()
        super.onDestroy()
    }
}
```

(Simplified example to illustrate the contract structure; view initialization and async details are omitted.)

**MVP Components:**

**1. Model:**
*Theory:* Model is the data and domain layer. Responsible for business rules, network calls, database operations, and data transformations. The `View` does not talk to the Model directly; all interaction with Model is coordinated by the Presenter.

```kotlin
// ✅ Model - data + domain layer (signature aligned with usage)
class LoginModel {
    fun login(
        email: String,
        password: String,
        onResult: (User?) -> Unit
    ) {
        // Implementation can be async (coroutines/callbacks/etc.). Pseudocode:
        try {
            val response = apiService.login(email, password).execute()
            val user = if (response.isSuccessful) {
                response.body()?.also { database.userDao().save(it) }
            } else {
                null
            }
            onResult(user)
        } catch (e: Exception) {
            onResult(null)
        }
    }
}
```

**2. `View`:**
*Theory:* `View` is the UI layer. Responsible for rendering data, handling user input events, and delegating these events to the Presenter. It is passive: contains minimal logic and does not know how data is loaded or business rules are implemented. Typically implemented by `Activity`/`Fragment`/Custom `View` and holds a reference to the Presenter via contract.

```kotlin
// ✅ View - passive UI (simplified example)
class ProductListFragment : Fragment(), ProductContract.View {
    private lateinit var presenter: ProductContract.Presenter

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        presenter = ProductPresenter(this, ProductModel())
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
*Theory:* Presenter is the mediator between Model and `View`. Responsible for presentation logic: processing user input (via calls from the `View`), requesting data from Model, and updating the `View` state. Holds references to `View` (via interface) and Model. It is easily testable because it does not depend on Android APIs when implemented correctly.

```kotlin
// ✅ Presenter - presentation logic
class ProductPresenter(
    private var view: ProductContract.View?,
    private val model: ProductModel
) : ProductContract.Presenter {

    override fun loadProducts() {
        val currentView = view ?: return
        currentView.showProgress()
        model.getProducts(
            onSuccess = { products ->
                val v = view ?: return@getProducts
                v.hideProgress()
                v.showProducts(products)
            },
            onError = { error ->
                val v = view ?: return@getProducts
                v.hideProgress()
                v.showError(error.message ?: "Unknown error")
            }
        )
    }

    override fun onDestroy() {
        view = null
    }
}
```

**Contract Interface:**

*Theory:* A contract interface defines the relationship between `View` and Presenter. It usually contains two inner interfaces: `View` and Presenter.
- `View` interface: methods that Presenter can call to update the UI.
- Presenter interface: methods that `View` calls to notify about lifecycle events and user actions.

This makes responsibilities explicit, reduces coupling, and improves testability.

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

// Presenter and View both use the Contract
class UserProfilePresenter(
    private var view: UserProfileContract.View?,
    private val model: UserProfileModel
) : UserProfileContract.Presenter {
    override fun onViewCreated() { /* ... */ }
    override fun onRefreshClicked() { /* ... */ }
    override fun onEditClicked() { /* ... */ }
    override fun onDestroy() { view = null }
}

class UserProfileActivity : AppCompatActivity(), UserProfileContract.View {
    private lateinit var presenter: UserProfileContract.Presenter
    // Implementation
}
```

**Advantages:**

1. **Separation of Concerns** – clear separation between UI (`View`), presentation logic (Presenter), and data/domain (Model).
2. **Testability** – Presenter is easily unit testable without Android framework dependencies when designed properly.
3. **Reduced Android Dependency in Logic** – Presenter does not depend on Android UI components.
4. **Easy Maintenance** – modular code that is easier to change and extend.

**Disadvantages:**

1. **Presenter Expansion (God Object)** – Presenter can grow too large if responsibilities are not controlled.
2. **Overhead for Small Apps** – may be unnecessary for very simple applications.
3. **Interface Complexity** – many contracts/interfaces can increase complexity.
4. **Memory Leaks Risk** – must properly clear `View` references in Presenter (detach onDestroy, etc.), especially for long-running operations.

**When to Use:**

*Theory:* Use MVP when you need high testability of presentation logic, have non-trivial UI/data interaction, follow clean architecture principles, and want to minimize coupling between presentation logic and Android framework. Avoid MVP when it introduces unnecessary complexity: very small apps, quick prototypes, or when the team is not ready to maintain the pattern.

✅ **Use MVP when:**
- High presentation-layer testability is required
- Complex UI-to-data interaction
- Following clean architecture principles
- Need to decouple presentation logic from Android APIs

❌ **Don't use MVP when:**
- Very simple apps (over-engineering)
- Prototypes (unnecessary overhead)
- Team is not familiar with the pattern and cannot support it

**MVP vs MVVM vs MVI:**

*Theory:*
- MVP: passive `View`, Presenter drives `View` and talks to Model. Explicit coordination; good testability.
- MVVM: `ViewModel` exposes observable state (`LiveData`/`StateFlow`/etc.), `View` observes it. Two-way binding is possible but not mandatory.
- MVI: unidirectional data flow with intents, reducers, and immutable state.

All three can be highly testable if implemented correctly. MVP is not inherently "the best" for testability; the choice depends on state management needs, tooling, and team preferences.

**Key Concepts:**

1. **Contract Interface** – defines `View` and Presenter interfaces.
2. **Passive `View`** – `View` only renders and forwards events, no business logic.
3. **Testability** – Presenter can be tested in isolation.
4. **Separation of Concerns** – clear boundaries between UI, presentation logic, and Model.
5. **Minimized Android Dependency in Presenter** – Presenter avoids direct Android APIs, improving testability.

---

## Дополнительные вопросы (RU)

- Как паттерн MVP обеспечивает тестируемость?
- В чём разница между MVP и MVVM?
- Как предотвращать утечки памяти в Presenter при использовании MVP?

## Связанные вопросы (RU)

### Предварительные (проще)
- Базовые концепции архитектуры Android и разделения ответственностей

### Связанные (такой же уровень)
- Вопрос о паттерне MVVM (MVVM pattern)
- Вопрос о паттерне MVI (MVI pattern)

### Продвинутые (сложнее)
- Вопрос о Clean Architecture
- Продвинутые реализации MVP
- Стратегии тестирования MVP

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
- MVVM pattern
- MVI pattern

### Advanced (Harder)
- Clean Architecture
- Advanced MVP implementations
- Testing strategies for MVP

---

## References

- [[c-architecture-patterns]]
- "Model–view–presenter" on Wikipedia: https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93presenter
