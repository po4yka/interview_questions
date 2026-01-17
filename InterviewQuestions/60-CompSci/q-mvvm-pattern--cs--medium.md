---
id: cs-021
title: MVVM Pattern / Паттерн MVVM (Model-View-ViewModel)
aliases:
- MVVM Pattern
- Паттерн MVVM
topic: cs
subtopics:
- architecture-patterns
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-cs
related:
- c-architecture-patterns
- q-abstract-factory-pattern--cs--medium
- q-android-architectural-patterns--android--medium
created: 2025-10-15
updated: 2025-11-11
tags:
- android-architecture
- architecture-patterns
- data-binding
- difficulty/medium
- livedata
- mvvm
- reactive-programming
- viewmodel
sources:
- https://developer.android.com/jetpack/guide
anki_cards:
- slug: cs-021-0-en
  language: en
  anki_id: 1768455660994
  synced_at: '2026-01-15T09:43:17.038449'
- slug: cs-021-0-ru
  language: ru
  anki_id: 1768455661019
  synced_at: '2026-01-15T09:43:17.040041'
---
# Вопрос (RU)
> Что такое паттерн MVVM? Когда его использовать и как он работает?

# Question (EN)
> What is the MVVM pattern? When to use it and how does it work?

---

## Ответ (RU)

**Теория MVVM Pattern:**
MVVM (Model-`View`-`ViewModel`) — архитектурный паттерн, отделяющий разработку UI и презентационной логики от бизнес-логики и источников данных. Изначально он не привязан к конкретной платформе и может использоваться за пределами Android. В Android-контексте он помогает сделать так, чтобы `View` не зависел напрямую от конкретных моделей и источников данных. Model представляет собой абстракцию источников данных и бизнес-логики. `View` наблюдает за `ViewModel` и не содержит бизнес-логики. `ViewModel` — слой между Model и `View`, который предоставляет наблюдаемые потоки данных и команды для управления состоянием представления.

**Определение:**

*Теория:* MVVM — архитектурный паттерн, обеспечивающий разделение ответственности: UI и логика представления отделены от бизнес-логики и работы с данными. `View` не зависит от конкретной реализации модели или источников данных. Ключевая идея: `ViewModel` экспонирует состояние и события в виде наблюдаемой модели (observable state), а `View` подписывается на них. Two-way data binding может использоваться как техника интеграции `View` и `ViewModel`, но не является обязательным требованием паттерна и не всегда является рекомендуемым подходом (часто предпочтительнее однонаправленный поток данных).

```kotlin
// ✅ MVVM Structure (упрощённый пример для иллюстрации)
data class User(val id: Int, val name: String, val email: String)

class UserRepository {
    fun getUser(userId: Int): User {
        return User(userId, "John Doe", "john@example.com")
    }
}

class UserViewModel : ViewModel() {
    private val repository = UserRepository()
    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user

    private val _loading = MutableLiveData<Boolean>()
    val loading: LiveData<Boolean> = _loading

    fun loadUser(userId: Int) {
        _loading.value = true
        viewModelScope.launch {
            try {
                val userData = repository.getUser(userId)
                _user.value = userData
            } finally {
                _loading.value = false
            }
        }
    }
}

class UserActivity : AppCompatActivity() {
    private lateinit var viewModel: UserViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // setContentView(...) подразумевается

        viewModel = ViewModelProvider(this)[UserViewModel::class.java]

        viewModel.user.observe(this) { user ->
            nameTextView.text = user.name
            emailTextView.text = user.email
        }

        viewModel.loadUser(1)
    }
}
```

**Компоненты MVVM:**

**1. Model:**
*Теория:* Model — абстракция источников данных и бизнес-логики. Отвечает за сетевые вызовы, операции с базой данных, доменную логику и преобразование данных. Работает с `ViewModel` для получения и сохранения данных. `ViewModel` использует Model (репозитории, use cases и т.п.) для выполнения операций с данными.

```kotlin
// ✅ Model - data abstraction
class UserRepository(
    private val apiService: ApiService,
    private val database: UserDatabase
) {
    suspend fun getUser(userId: Int): User {
        // Try cache first
        val cached = database.userDao().getUserById(userId)
        if (cached != null) return cached

        // Fetch from network
        val response = apiService.getUser(userId)
        database.userDao().insert(response)
        return response
    }
}
```

**2. `View`:**
*Теория:* `View` — слой UI. Уведомляет `ViewModel` о действиях пользователя и наблюдает за её состоянием для обновления интерфейса. Не содержит бизнес-логики. Синхронизируется с `ViewModel` через observable-объекты. Должен оставаться максимально «тонким» и сфокусированным на отображении.

```kotlin
// ✅ View - наблюдает за ViewModel
class ProductListFragment : Fragment() {
    private val viewModel: ProductListViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Observe state
        viewModel.products.observe(viewLifecycleOwner) { products ->
            adapter.submitList(products)
        }

        viewModel.loading.observe(viewLifecycleOwner) { isLoading ->
            progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
        }

        // User interactions
        swipeRefreshLayout.setOnRefreshListener {
            viewModel.refresh()
        }
    }
}
```

**3. `ViewModel`:**
*Теория:* `ViewModel` экспонирует наблюдаемые данные и события, релевантные `View`. Выступает как посредник между Model и `View`. Не содержит ссылок на `View`. Инкапсулирует презентационную логику. В Android `ViewModel` переживает конфигурационные изменения и обычно использует такие механизмы, как `LiveData` или `StateFlow`, для реактивного обновления UI.

```kotlin
// ✅ ViewModel - presentation logic
class ProductListViewModel(private val repository: ProductRepository) : ViewModel() {
    private val _products = MutableLiveData<List<Product>>()
    val products: LiveData<List<Product>> = _products

    private val _loading = MutableLiveData<Boolean>()
    val loading: LiveData<Boolean> = _loading

    init {
        loadProducts()
    }

    fun loadProducts() {
        _loading.value = true
        viewModelScope.launch {
            try {
                val result = repository.getProducts()
                _products.value = result
            } catch (e: Exception) {
                // Обработка ошибки (например, отдельное состояние для ошибок)
            } finally {
                _loading.value = false
            }
        }
    }

    fun refresh() {
        loadProducts()
    }
}
```

**Ключевые принципы:**

**1. Two-Way Data Binding:**
*Теория:* Может использоваться двусторонний data binding между `View` и `ViewModel`, при котором свойства `ViewModel` синхронизируются с `View`: изменения во `View` обновляют `ViewModel`, а изменения в `ViewModel` — `View`. Однако двусторонний data binding — это опциональный механизм (зависит от фреймворка/инструментов) и в Android не является обязательной частью MVVM; часто рекомендуется однонаправленный data flow для упрощения отладки и предсказуемости.

```kotlin
// ✅ Data Binding Example (XML) - иллюстрация возможности two-way binding
// activity_user.xml
<layout xmlns:android="...">
    <data>
        <variable name="viewModel" type="com.example.UserViewModel"/>
    </data>

    <EditText
        android:text="@={viewModel.email}"/>
</layout>
```

**2. `Observable` Pattern:**
*Теория:* `ViewModel` экспонирует наблюдаемые данные (например, `LiveData`, `StateFlow`). `View` подписывается на них и реагирует на изменения. `ViewModel` не знает о конкретных подписчиках. Несколько `View` могут подписываться на один и тот же источник данных, что обеспечивает слабую связанность.

**3. `Lifecycle` Awareness (в Android):**
*Теория:* В Android `ViewModel` привязан к lifecycle owner (`Activity`, `Fragment`) и переживает конфигурационные изменения (например, поворот экрана). `LiveData` отслеживает состояние жизненного цикла и автоматически прекращает доставку обновлений, когда владелец уничтожен. Это платформенные особенности реализации MVVM в Android.

**4. No `View` Reference:**
*Теория:* `ViewModel` не должен иметь прямой ссылки на `View` или Android UI-классы. Он только предоставляет состояние и события, а `View` самостоятельно подписывается и обновляет UI. Это повышает тестируемость и уменьшает риск утечек памяти.

**Преимущества:**

1. Поддерживаемость — предсказуемая структура, проще развивать и рефакторить.
2. Расширяемость — можно относительно изолированно заменять или добавлять функциональность.
3. Тестируемость — презентационная и бизнес-логика отделены от UI, проще писать unit-тесты.
4. Чёткие контракты — `ViewModel` предоставляет явный интерфейс состояния и событий для `View`.
5. Поддержка жизненного цикла (в Android) — `ViewModel` помогает корректно переживать конфигурационные изменения.

**Недостатки:**

1. Overkill для простых экранов — избыточная сложность для очень простого UI.
2. Сложность проектирования — требуется аккуратный дизайн `ViewModel` и состояний для сложных сценариев.
3. Debugging сложных биндингов — особенно с активным two-way binding.
4. Избыточное состояние — неправильное управление состоянием во `ViewModel` может приводить к перерасходу памяти.

**Когда использовать:**

*Теория:* Используйте MVVM, когда требуется чёткое разделение ответственности, реактивные обновления UI, сложное управление состоянием, переиспользуемость и тестируемость логики, а также когда вы следуете современным рекомендациям (например, Android Jetpack). Для очень простых экранов или быстрых прототипов MVVM может быть излишним.

✅ Использовать MVVM когда:
- Современные Android-приложения с Jetpack-компонентами.
- Нужны реактивные обновления UI.
- Сложное состояние и несколько источников данных.
- Важны тестируемость и переживание конфигурационных изменений.

❌ Необязательно использовать MVVM когда:
- Очень простой UI (может быть over-engineering).
- Быстрые прототипы, где избыточна дополнительная структура.

**MVVM и Android Jetpack:**

*Теория:* В Android MVVM часто реализуется с помощью Jetpack-компонентов: `ViewModel` (lifecycle-aware holder для state), `LiveData` или `Flow`/`StateFlow` (наблюдаемые источники данных), Data Binding/`View` Binding (декларативное связывание или удобная работа с `View`), Repository (абстракция источников данных). Эти инструменты поддерживают, но не определяют сам паттерн MVVM.

**Ключевые концепции:**

1. `Observable` State — `ViewModel` экспонирует состояние, за которым наблюдает `View`.
2. Separation of Concerns — чёткое разделение UI, презентационной и бизнес-логики.
3. Отсутствие зависимости `ViewModel` от `View`.
4. (Опционально) Two-Way Binding — может применяться, но не обязателен.
5. `Lifecycle` Awareness в Android — реализация MVVM учитывает жизненный цикл компонентов.

---

## Answer (EN)

**MVVM Pattern Theory:**
MVVM (Model-`View`-`ViewModel`) is an architectural pattern that separates UI and presentation logic from business logic and data sources. It is platform-agnostic and can be used beyond Android. In the Android context, it helps ensure that the `View` does not directly depend on specific models or data sources. The Model represents abstractions of data sources and business logic. The `View` observes the `ViewModel` and does not contain business logic. The `ViewModel` is an intermediate layer between Model and `View` exposing observable data streams and commands for managing view state.

**Definition:**

*Theory:* MVVM is an architectural pattern enforcing separation of concerns: UI and presentation logic are decoupled from business logic and data access. The `View` is independent from concrete model or data source implementations. The key idea is that the `ViewModel` exposes state and events as observable models, and the `View` subscribes to them. Two-way data binding can be used as an integration technique between `View` and `ViewModel`, but it is not a mandatory characteristic of MVVM and is not always recommended; one-way data flow is often preferred for clarity and debuggability.

```kotlin
// ✅ MVVM Structure (simplified example for illustration)
data class User(val id: Int, val name: String, val email: String)

class UserRepository {
    fun getUser(userId: Int): User {
        return User(userId, "John Doe", "john@example.com")
    }
}

class UserViewModel : ViewModel() {
    private val repository = UserRepository()
    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user

    private val _loading = MutableLiveData<Boolean>()
    val loading: LiveData<Boolean> = _loading

    fun loadUser(userId: Int) {
        _loading.value = true
        viewModelScope.launch {
            try {
                val userData = repository.getUser(userId)
                _user.value = userData
            } finally {
                _loading.value = false
            }
        }
    }
}

class UserActivity : AppCompatActivity() {
    private lateinit var viewModel: UserViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // setContentView(...) is implied

        viewModel = ViewModelProvider(this)[UserViewModel::class.java]

        viewModel.user.observe(this) { user ->
            nameTextView.text = user.name
            emailTextView.text = user.email
        }

        viewModel.loadUser(1)
    }
}
```

**MVVM Components:**

**1. Model:**
*Theory:* The Model is an abstraction over data sources and business logic. It is responsible for network calls, database operations, domain logic, and data transformations. It collaborates with the `ViewModel` for fetching and persisting data. The `ViewModel` uses Model components (repositories, use cases, etc.) to perform data operations.

```kotlin
// ✅ Model - data abstraction
class UserRepository(
    private val apiService: ApiService,
    private val database: UserDatabase
) {
    suspend fun getUser(userId: Int): User {
        // Try cache first
        val cached = database.userDao().getUserById(userId)
        if (cached != null) return cached

        // Fetch from network
        val response = apiService.getUser(userId)
        database.userDao().insert(response)
        return response
    }
}
```

**2. `View`:**
*Theory:* The `View` is the UI layer. It notifies the `ViewModel` about user actions and observes its state to update the UI. It should not contain business logic. It keeps in sync with the `ViewModel` via observable objects. It should remain thin and focused on rendering.

```kotlin
// ✅ View - observes ViewModel
class ProductListFragment : Fragment() {
    private val viewModel: ProductListViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Observe state
        viewModel.products.observe(viewLifecycleOwner) { products ->
            adapter.submitList(products)
        }

        viewModel.loading.observe(viewLifecycleOwner) { isLoading ->
            progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
        }

        // User interactions
        swipeRefreshLayout.setOnRefreshListener {
            viewModel.refresh()
        }
    }
}
```

**3. `ViewModel`:**
*Theory:* The `ViewModel` exposes observable data and events relevant to the `View`. It acts as an intermediary between Model and `View`. It should not hold references to `View` or Android UI classes. It encapsulates presentation logic. In Android, `ViewModel` survives configuration changes and typically uses `LiveData` or `StateFlow` to drive reactive UI updates.

```kotlin
// ✅ ViewModel - presentation logic
class ProductListViewModel(private val repository: ProductRepository) : ViewModel() {
    private val _products = MutableLiveData<List<Product>>()
    val products: LiveData<List<Product>> = _products

    private val _loading = MutableLiveData<Boolean>()
    val loading: LiveData<Boolean> = _loading

    init {
        loadProducts()
    }

    fun loadProducts() {
        _loading.value = true
        viewModelScope.launch {
            try {
                val result = repository.getProducts()
                _products.value = result
            } catch (e: Exception) {
                // Handle error (e.g., expose separate error state)
            } finally {
                _loading.value = false
            }
        }
    }

    fun refresh() {
        loadProducts()
    }
}
```

**Key Principles:**

**1. Two-Way Data Binding:**
*Theory:* Two-way data binding can be used between the `View` and `ViewModel` so that `ViewModel` properties and `View` widgets stay in sync: changes in the `View` update the `ViewModel` and vice versa. However, two-way binding is an optional mechanism provided by certain frameworks/tooling and is not a strict requirement of MVVM. In Android, one-way data flow from `ViewModel` to `View` is often preferred for better predictability.

```kotlin
// ✅ Data Binding Example (XML) - demonstrates optional two-way binding
// activity_user.xml
<layout xmlns:android="...">
    <data>
        <variable name="viewModel" type="com.example.UserViewModel"/>
    </data>

    <EditText
        android:text="@={viewModel.email}"/>
</layout>
```

**2. `Observable` Pattern:**
*Theory:* The `ViewModel` exposes observable data (e.g., `LiveData`, `StateFlow`). The `View` subscribes to these observables and reacts to changes. The `ViewModel` is unaware of specific `View` subscribers. Multiple Views can observe the same data source, supporting a decoupled architecture.

**3. `Lifecycle` Awareness (in Android):**
*Theory:* In Android, `ViewModel` instances are scoped to a lifecycle owner (`Activity`, `Fragment`) and survive configuration changes (e.g., rotation). `LiveData` is lifecycle-aware and automatically stops sending updates when the owner is destroyed. These are Android-specific implementation details supporting MVVM.

**4. No `View` Reference:**
*Theory:* The `ViewModel` should not hold a direct reference to the `View` or UI toolkit classes. It only exposes observable state and events; the `View` subscribes and updates itself. This improves testability and avoids memory leaks.

**Advantages:**

1. Maintainability — clear structure and separation of concerns simplify evolution and refactoring.
2. Extensibility — features can be added or modified with limited impact on other layers.
3. Testability — business and presentation logic are decoupled from UI, enabling easier unit testing.
4. Clear Contracts — `ViewModel` exposes an explicit state/events interface to the `View`.
5. `Lifecycle` Support (Android) — `ViewModel` helps survive configuration changes.

**Disadvantages:**

1. Overkill for simple UIs — introduces unnecessary complexity for very simple screens.
2. Design challenges — designing good ViewModels and state models can be non-trivial.
3. Debugging complexity — especially when heavily using complex or two-way bindings.
4. State/memory overhead — poorly managed `ViewModel` state can lead to memory overhead.

**When to Use:**

*Theory:* Use MVVM when you need clear separation of concerns, reactive UI updates, complex state management, reuse and testability of logic, and when following modern architecture guidelines (e.g., with Android Jetpack). It might be unnecessary for very simple UIs or throwaway prototypes.

✅ Use MVVM when:
- Building modern Android apps with Jetpack components.
- You need reactive UI updates.
- You have complex state and multiple data sources.
- Testability and configuration change survival matter.

❌ Not strictly necessary when:
- The UI is very simple (risk of over-engineering).
- Rapid prototypes where extra structure is not justified.

**MVVM and Android Jetpack:**

*Theory:* In Android, MVVM is commonly implemented using Jetpack components: `ViewModel` (lifecycle-aware state holder), `LiveData` or `Flow`/`StateFlow` (observable data streams), Data Binding or `View` Binding (declarative binding / safer view access), and the Repository pattern (data source abstraction). These support but do not define the MVVM pattern itself.

**Key Concepts:**

1. `Observable` State — `ViewModel` exposes state observed by the `View`.
2. Separation of Concerns — clear boundaries between UI, presentation, and business logic.
3. No `View` Dependency — `ViewModel` does not depend on `View`.
4. (Optional) Two-Way Binding — may be used, but not required.
5. `Lifecycle` Awareness in Android — using Android tools that respect lifecycle.

---

## Дополнительные Вопросы (RU)

- В чем разница между `LiveData` и `StateFlow`?
- Как `ViewModel` переживает конфигурационные изменения?
- Когда следует использовать двусторонний data binding, а когда однонаправленный?

## Follow-ups

- What is the difference between `LiveData` and `StateFlow`?
- How does `ViewModel` survive configuration changes?
- When should you use two-way data binding vs one-way?

## Связанные Вопросы (RU)

### Предпосылки (проще)
- Базовые архитектурные концепции Android
- Понимание `LiveData` и `ViewModel`

### Связанные (средний уровень)
- Сравнение архитектурных паттернов MVVM, MVP и MVI

### Продвинутые (сложнее)
- Применение Clean Architecture вместе с MVVM
- Продвинутые паттерны MVVM
- Сравнение `StateFlow` и `LiveData`

## Related Questions

### Prerequisites (Easier)
- Basic Android architecture concepts
- Understanding of `LiveData` and `ViewModel`

### Related (Same Level)
- MVVM vs MVP vs MVI architectural patterns

### Advanced (Harder)
- Applying Clean Architecture with MVVM
- Advanced MVVM patterns
- `StateFlow` vs `LiveData` comparison

## Ссылки (RU)

- [[c-architecture-patterns]]
- [Официальное руководство по архитектуре Android](https://developer.android.com/jetpack/guide)

## References

- [[c-architecture-patterns]]
- [Android official architecture guidance](https://developer.android.com/jetpack/guide)
