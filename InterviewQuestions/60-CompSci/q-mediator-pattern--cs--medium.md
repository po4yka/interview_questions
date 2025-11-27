---
id: dp-006
title: "Mediator Pattern / Mediator Паттерн"
aliases: [Mediator Pattern, Mediator Паттерн]
topic: cs
subtopics: [design-patterns, behavioral, coupling-reduction]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-architecture-patterns, q-abstract-factory-pattern--cs--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [behavioral, coupling, difficulty/medium, gof-patterns, mediator]

date created: Saturday, November 1st 2025, 1:26:22 pm
date modified: Tuesday, November 25th 2025, 8:53:54 pm
---
# Вопрос (RU)
> Что такое паттерн Mediator? Когда и зачем его следует использовать?

# Question (EN)
> What is the Mediator pattern? When and why should it be used?

---

## Ответ (RU)

### Определение

Паттерн проектирования Mediator (Посредник) — это поведенческий паттерн, который **уменьшает связанность между компонентами программы, заставляя их взаимодействовать косвенно, через специальный объект-посредник**. Mediator облегчает модификацию, расширение и повторное использование отдельных компонентов, так как они больше не зависят напрямую от множества других классов.

### Проблемы, Которые Решает

Проблемы, которые решает паттерн Mediator:

1. **Следует избегать тесной связанности между набором взаимодействующих объектов.**
2. **Должна быть возможность изменять схему взаимодействия между объектами независимо от самих объектов.**

Прямое обращение объектов друг к другу и изменение состояния друг друга делает систему негибкой, так как тесно связывает объекты между собой. Тесно связанные объекты сложно реализовать, изменять, тестировать и повторно использовать.

### Решение

Решения, предлагаемые паттерном Mediator:

- Определить отдельный **объект-посредник (mediator), который инкапсулирует взаимодействие** между набором объектов.
- Объекты **делегируют своё взаимодействие объекту-посреднику** вместо прямого взаимодействия друг с другом.

Объекты взаимодействуют друг с другом косвенно через объект-посредник. Это делает их слабо связанными: они знают только о посреднике и не имеют явных зависимостей друг от друга.

### Пример: Базовый Mediator

```kotlin
// Шаг 1: Интерфейс посредника
interface Mediator {
    fun notify(sender: Colleague, event: String)
}

// Шаг 2: Конкретный посредник
class ConcreteMediator : Mediator {
    lateinit var colleague1: ColleagueA
    lateinit var colleague2: ColleagueB

    override fun notify(sender: Colleague, event: String) {
        when (event) {
            "A" -> colleague2.reactToA()
            "B" -> colleague1.reactToB()
        }
    }
}

// Базовый класс коллеги
abstract class Colleague(protected val mediator: Mediator)

class ColleagueA(mediator: Mediator) : Colleague(mediator) {
    fun doA() {
        println("ColleagueA triggers event A.")
        mediator.notify(this, "A")
    }

    fun reactToB() {
        println("ColleagueA reacts to event B.")
    }
}

class ColleagueB(mediator: Mediator) : Colleague(mediator) {
    fun doB() {
        println("ColleagueB triggers event B.")
        mediator.notify(this, "B")
    }

    fun reactToA() {
        println("ColleagueB reacts to event A.")
    }
}

// Клиентский код
fun main() {
    val mediator = ConcreteMediator()
    val colleagueA = ColleagueA(mediator)
    val colleagueB = ColleagueB(mediator)

    mediator.colleague1 = colleagueA
    mediator.colleague2 = colleagueB

    colleagueA.doA()
    colleagueB.doB()
}
```

### Android Пример: Chat Room

```kotlin
// Интерфейс посредника чата
interface ChatMediator {
    fun sendMessage(message: String, user: User)
    fun addUser(user: User)
}

// Конкретный посредник
class ChatRoom : ChatMediator {
    private val users = mutableListOf<User>()

    override fun addUser(user: User) {
        users.add(user)
        println("${user.name} joined the chat")
    }

    override fun sendMessage(message: String, sender: User) {
        users.filter { it != sender }.forEach { user ->
            user.receive(message, sender)
        }
    }
}

// Коллега
class User(
    private val mediator: ChatMediator,
    val name: String
) {
    fun send(message: String) {
        println("$name sends: $message")
        mediator.sendMessage(message, this)
    }

    fun receive(message: String, sender: User) {
        println("$name received from ${sender.name}: $message")
    }
}

// Использование
fun main() {
    val chatRoom = ChatRoom()

    val alice = User(chatRoom, "Alice")
    val bob = User(chatRoom, "Bob")
    val charlie = User(chatRoom, "Charlie")

    chatRoom.addUser(alice)
    chatRoom.addUser(bob)
    chatRoom.addUser(charlie)

    alice.send("Hello everyone!")
    bob.send("Hi Alice!")
}
```

(Пользователи общаются только через ChatRoom, который централизует маршрутизацию сообщений — классический пример Mediator-подхода.)

### Kotlin Пример: Mediator Для UI-формы

```kotlin
// UI-компоненты (Colleagues)
class Button(private val text: String) {
    var onClick: (() -> Unit)? = null

    fun click() {
        println("Button '$text' clicked")
        onClick?.invoke()
    }
}

class TextField {
    var text: String = ""
        set(value) {
            field = value
            onTextChanged?.invoke(value)
        }

    var onTextChanged: ((String) -> Unit)? = null
}

class Label {
    var text: String = ""
        set(value) {
            field = value
            println("Label updated: $value")
        }
}

// Mediator
class FormMediator {
    private val submitButton = Button("Submit")
    private val cancelButton = Button("Cancel")
    private val nameField = TextField()
    private val statusLabel = Label()

    init {
        submitButton.onClick = { handleSubmit() }
        cancelButton.onClick = { handleCancel() }
        nameField.onTextChanged = { handleNameChange(it) }
    }

    private fun handleSubmit() {
        if (nameField.text.isNotBlank()) {
            statusLabel.text = "Form submitted with name: ${nameField.text}"
        } else {
            statusLabel.text = "Error: Name is required"
        }
    }

    private fun handleCancel() {
        nameField.text = ""
        statusLabel.text = "Form cancelled"
    }

    private fun handleNameChange(text: String) {
        statusLabel.text = if (text.isNotBlank()) {
            "Ready to submit"
        } else {
            "Please enter your name"
        }
    }

    fun simulateUserActions() {
        nameField.text = "John"
        submitButton.click()

        cancelButton.click()
    }
}

fun main() {
    val form = FormMediator()
    form.simulateUserActions()
}
```

(Иллюстрирует централизованное управление взаимодействиями между UI-компонентами.)

### Пример: `ViewModel` Как Mediator-подобный Компонент В Android

```kotlin
// ViewModel здесь играет роль посредника между UI и уровнями данных.
class OrderViewModel(
    private val productRepository: ProductRepository,
    private val cartRepository: CartRepository,
    private val paymentService: PaymentService
) : ViewModel() {

    private val _orderState = MutableStateFlow<OrderState>(OrderState.Idle)
    val orderState: StateFlow<OrderState> = _orderState.asStateFlow()

    fun addToCart(productId: String) {
        viewModelScope.launch {
            val product = productRepository.getProduct(productId)
            cartRepository.addItem(product)
            updateCartTotal()
        }
    }

    fun checkout() {
        viewModelScope.launch {
            _orderState.value = OrderState.Processing
            val cartItems = cartRepository.getItems()
            val total = cartRepository.getTotal()

            try {
                val result = paymentService.processPayment(total)
                if (result.success) {
                    cartRepository.clear()
                    _orderState.value = OrderState.Success(result.orderId)
                } else {
                    _orderState.value = OrderState.Error("Payment failed")
                }
            } catch (e: Exception) {
                _orderState.value = OrderState.Error(e.message ?: "Unknown error")
            }
        }
    }

    private fun updateCartTotal() {
        val total = cartRepository.getTotal()
        _orderState.value = OrderState.CartUpdated(total)
    }
}

sealed class OrderState {
    object Idle : OrderState()
    object Processing : OrderState()
    data class CartUpdated(val total: Double) : OrderState()
    data class Success(val orderId: String) : OrderState()
    data class Error(val message: String) : OrderState()
}
```

### Объяснение

- **Интерфейс Mediator** определяет контракт для коммуникации.
- **Конкретный посредник** реализует координирующую логику.
- **Коллеги (Colleagues)** общаются только через посредника, а не напрямую.
- **Уменьшение зависимостей**: каждый коллега знает только о посреднике.
- **Android**: чат-приложения, валидация форм, `ViewModel` (координирующий/mediator-подобный компонент) между UI и репозиториями.
- **Важно отличать Mediator от Pub-Sub**: универсальный `EventBus` концептуально ближе к паттерну Publisher-Subscriber, чем к классическому GoF Mediator, хотя оба могут использоваться для маршрутизации событий.

### Реальные Примеры

1. **Диспетчерская вышка в аэропорту** — самолёты общаются с вышкой, а не напрямую друг с другом.
2. **Чат-приложение** — сообщения проходят через центральный сервер/узел, а не peer-to-peer.
3. **UI-фреймворки** — диспетчеры событий и контроллеры координируют взаимодействие компонентов.

### Преимущества

1. **Уменьшенная связанность** — компоненты не зависят напрямую друг от друга.
2. **Централизованный контроль** — логика взаимодействий сосредоточена в одном месте.
3. **Переиспользуемость** — компоненты можно повторно использовать независимо.
4. **Упрощённое сопровождение** — изменения во взаимодействиях не требуют модификации всех компонентов.
5. **Принцип единственной ответственности** — логика коммуникации отделена от бизнес-логики компонентов.

### Недостатки

1. **Риск God Object** — посредник может разрастись и стать слишком сложным.
2. **Единая точка отказа** — проблемы в посреднике влияют на всю коммуникацию.
3. **Сложность сопровождения** — добавление новых сценариев взаимодействия может требовать частых изменений посредника.

### Когда Использовать

Используйте паттерн Mediator, когда:

1. **Сложная коммуникация между компонентами** — множество компонентов взаимодействуют сложным образом.
2. **Нужна слабая связанность** — компоненты не должны знать детали друг о друге.
3. **Нужен централизованный контроль** — взаимодействия удобно контролировать через одну точку.
4. **Нужна переиспользуемость компонентов** — компоненты должны быть максимально независимыми.

### Примеры В Android

- **`ViewModel`** — координирует взаимодействие между UI и слоями данных (ведёт себя как посредник, хотя формально не является реализацией GoF Mediator).
- **Централизованные диспетчеры событий / шины событий** — единая точка маршрутизации событий (но классический `EventBus` ближе к Publisher-Subscriber, чем к GoF Mediator; важно различать эти концепты).
- **Чат-приложения** — центральная комната/сервер координирует сообщения между пользователями.
- **Валидация форм** — объект-посредник координирует логику валидации и реакций между полями формы и UI.

### Best Practices (Рекомендации)

```kotlin
// DO: Используйте Mediator для сложных взаимодействий между компонентами
class OrderFlowMediator(
    private val ui: UI,
    private val validator: Validator,
    private val repository: Repository
) {
    fun handleCheckout(items: List<Item>) {
        if (validator.validate(items)) {
            repository.save(items)
            ui.showSuccess()
        } else {
            ui.showError()
        }
    }
}

// DO: Держите посредник сфокусированным
interface NotificationMediator {
    fun notify(event: String, data: Any)
}

// DO: При необходимости комбинируйте Mediator-подход с Observer/Publish-Subscribe.
// Но помните: универсальный EventBus концептуально ближе к Pub-Sub, чем к GoF Mediator.
class EventBus {
    private val subscribers = mutableMapOf<String, MutableList<(Any) -> Unit>>()

    fun subscribe(event: String, handler: (Any) -> Unit) {
        subscribers.getOrPut(event) { mutableListOf() }.add(handler)
    }

    fun publish(event: String, data: Any) {
        subscribers[event]?.forEach { it(data) }
    }
}

// DON'T: Не помещайте всю бизнес-логику в посредник.
// DON'T: Не делайте посредник знающим все детали всех компонентов.
// DON'T: Не используйте Mediator для очень простых взаимодействий.
```

---

## Answer (EN)

Mediator is a behavioral design pattern that reduces coupling between multiple classes/components by moving their interaction logic into a separate mediator object.

### Definition

Mediator is a behavioral design pattern that **reduces coupling between components of a program by making them communicate indirectly, through a special mediator object**. The Mediator makes it easier to modify, extend, and reuse individual components because they're no longer directly dependent on many other classes.

### Problems it Solves

1. **Tight coupling between a set of interacting objects should be avoided.**
2. **It should be possible to change the interaction between a set of objects independently of the objects themselves.**

Direct interaction between objects tightly couples them, which makes the system hard to change, test, and reuse.

### Solution

- Define a separate **mediator object that encapsulates the interaction** between a set of objects.
- Objects **delegate their interaction to a mediator object** instead of interacting with each other directly.

Objects interact indirectly via the mediator, which keeps them loosely coupled.

### Example: Basic Mediator

```kotlin
interface Mediator {
    fun notify(sender: Colleague, event: String)
}

class ConcreteMediator : Mediator {
    lateinit var colleague1: ColleagueA
    lateinit var colleague2: ColleagueB

    override fun notify(sender: Colleague, event: String) {
        when (event) {
            "A" -> colleague2.reactToA()
            "B" -> colleague1.reactToB()
        }
    }
}

abstract class Colleague(protected val mediator: Mediator)

class ColleagueA(mediator: Mediator) : Colleague(mediator) {
    fun doA() {
        println("ColleagueA triggers event A.")
        mediator.notify(this, "A")
    }

    fun reactToB() {
        println("ColleagueA reacts to event B.")
    }
}

class ColleagueB(mediator: Mediator) : Colleague(mediator) {
    fun doB() {
        println("ColleagueB triggers event B.")
        mediator.notify(this, "B")
    }

    fun reactToA() {
        println("ColleagueB reacts to event A.")
    }
}

fun main() {
    val mediator = ConcreteMediator()
    val colleagueA = ColleagueA(mediator)
    val colleagueB = ColleagueB(mediator)

    mediator.colleague1 = colleagueA
    mediator.colleague2 = colleagueB

    colleagueA.doA()
    colleagueB.doB()
}
```

### Android Example: Chat Room

```kotlin
interface ChatMediator {
    fun sendMessage(message: String, user: User)
    fun addUser(user: User)
}

class ChatRoom : ChatMediator {
    private val users = mutableListOf<User>()

    override fun addUser(user: User) {
        users.add(user)
        println("${user.name} joined the chat")
    }

    override fun sendMessage(message: String, sender: User) {
        users.filter { it != sender }.forEach { user ->
            user.receive(message, sender)
        }
    }
}

class User(
    private val mediator: ChatMediator,
    val name: String
) {
    fun send(message: String) {
        println("$name sends: $message")
        mediator.sendMessage(message, this)
    }

    fun receive(message: String, sender: User) {
        println("$name received from ${sender.name}: $message")
    }
}

fun main() {
    val chatRoom = ChatRoom()

    val alice = User(chatRoom, "Alice")
    val bob = User(chatRoom, "Bob")
    val charlie = User(chatRoom, "Charlie")

    chatRoom.addUser(alice)
    chatRoom.addUser(bob)
    chatRoom.addUser(charlie)

    alice.send("Hello everyone!")
    bob.send("Hi Alice!")
}
```

### Kotlin Example: UI Form Mediator

```kotlin
class Button(private val text: String) {
    var onClick: (() -> Unit)? = null

    fun click() {
        println("Button '$text' clicked")
        onClick?.invoke()
    }
}

class TextField {
    var text: String = ""
        set(value) {
            field = value
            onTextChanged?.invoke(value)
        }

    var onTextChanged: ((String) -> Unit)? = null
}

class Label {
    var text: String = ""
        set(value) {
            field = value
            println("Label updated: $value")
        }
}

class FormMediator {
    private val submitButton = Button("Submit")
    private val cancelButton = Button("Cancel")
    private val nameField = TextField()
    private val statusLabel = Label()

    init {
        submitButton.onClick = { handleSubmit() }
        cancelButton.onClick = { handleCancel() }
        nameField.onTextChanged = { handleNameChange(it) }
    }

    private fun handleSubmit() {
        if (nameField.text.isNotBlank()) {
            statusLabel.text = "Form submitted with name: ${nameField.text}"
        } else {
            statusLabel.text = "Error: Name is required"
        }
    }

    private fun handleCancel() {
        nameField.text = ""
        statusLabel.text = "Form cancelled"
    }

    private fun handleNameChange(text: String) {
        statusLabel.text = if (text.isNotBlank()) {
            "Ready to submit"
        } else {
            "Please enter your name"
        }
    }

    fun simulateUserActions() {
        nameField.text = "John"
        submitButton.click()

        cancelButton.click()
    }
}

fun main() {
    val form = FormMediator()
    form.simulateUserActions()
}
```

### Android `ViewModel` Mediator Example

```kotlin
class OrderViewModel(
    private val productRepository: ProductRepository,
    private val cartRepository: CartRepository,
    private val paymentService: PaymentService
) : ViewModel() {

    private val _orderState = MutableStateFlow<OrderState>(OrderState.Idle)
    val orderState: StateFlow<OrderState> = _orderState.asStateFlow()

    fun addToCart(productId: String) {
        viewModelScope.launch {
            val product = productRepository.getProduct(productId)
            cartRepository.addItem(product)
            updateCartTotal()
        }
    }

    fun checkout() {
        viewModelScope.launch {
            _orderState.value = OrderState.Processing
            val cartItems = cartRepository.getItems()
            val total = cartRepository.getTotal()

            try {
                val result = paymentService.processPayment(total)
                if (result.success) {
                    cartRepository.clear()
                    _orderState.value = OrderState.Success(result.orderId)
                } else {
                    _orderState.value = OrderState.Error("Payment failed")
                }
            } catch (e: Exception) {
                _orderState.value = OrderState.Error(e.message ?: "Unknown error")
            }
        }
    }

    private fun updateCartTotal() {
        val total = cartRepository.getTotal()
        _orderState.value = OrderState.CartUpdated(total)
    }
}

sealed class OrderState {
    object Idle : OrderState()
    object Processing : OrderState()
    data class CartUpdated(val total: Double) : OrderState()
    data class Success(val orderId: String) : OrderState()
    data class Error(val message: String) : OrderState()
}
```

### Explanation

- Mediator interface defines the contract for communication.
- Concrete mediator implements coordination logic.
- Colleagues communicate only through the mediator.
- Reduces dependencies: each colleague knows only about the mediator.
- Android: chat applications, form validation, `ViewModel` (mediator-like coordinator) between UI and repositories.
- Important distinction: a generic `EventBus` or message bus is conceptually closer to Publisher-Subscriber than to the classic GoF Mediator, even though both centralize event routing.

### Real World Examples

1. Traffic control tower at airports.
2. Chat applications with a central hub/server.
3. UI frameworks where dispatchers/controllers coordinate components.

### Pros

1. Reduced coupling.
2. Centralized control.
3. Reusability of independent components.
4. Easier maintenance of interaction logic.
5. Clear separation of responsibilities.

### Cons

1. Risk of a "god object" mediator.
2. Single point of failure.
3. Mediator can become complex as interactions grow.

### When to Use

Use the Mediator pattern when:

1. You have complex communication between multiple components.
2. You need loose coupling between components.
3. You want centralized control over interactions.
4. You want reusable, independent components.

### Android Examples

- `ViewModel` coordinating interactions between UI and data layers (acts as a mediator-like component, though not a strict GoF Mediator).
- Centralized event dispatchers / event buses where a dedicated coordinator routes events (while a generic `EventBus` is closer to Pub-Sub, specific mediators that know participants and interaction rules align more with Mediator semantics).
- Chat applications where a central room/server coordinates messages between users.
- Form validation flows where a mediator object coordinates validation and reactions between form fields and UI state.

### Best Practices

```kotlin
// DO: Use for complex component interactions
class OrderFlowMediator(
    private val ui: UI,
    private val validator: Validator,
    private val repository: Repository
) {
    fun handleCheckout(items: List<Item>) {
        if (validator.validate(items)) {
            repository.save(items)
            ui.showSuccess()
        } else {
            ui.showError()
        }
    }
}

// DO: Keep mediator focused
interface NotificationMediator {
    fun notify(event: String, data: Any)
}

// DO: Combine Mediator-style coordination with Observer/Publish-Subscribe when appropriate.
// Note: a generic EventBus is conceptually closer to Pub-Sub than classic GoF Mediator.
class EventBus {
    private val subscribers = mutableMapOf<String, MutableList<(Any) -> Unit>>()

    fun subscribe(event: String, handler: (Any) -> Unit) {
        subscribers.getOrPut(event) { mutableListOf() }.add(handler)
    }

    fun publish(event: String, data: Any) {
        subscribers[event]?.forEach { it(data) }
    }
}

// DON'T: Put all business logic into the mediator.
// DON'T: Make the mediator aware of every detail of every component.
// DON'T: Use a mediator for trivial interactions.
```

---

## Дополнительные Вопросы (RU)

- Чем Mediator отличается от Observer и Publisher-Subscriber на концептуальном и реализационном уровнях?
- В каких случаях вы предпочтёте Mediator вместо использования DI и интерфейсов между компонентами?
- Как избежать превращения посредника в "god object" в крупной системе?

## Follow-ups

- How does the Mediator pattern differ from the Observer and Publish-Subscribe patterns conceptually and in implementation?
- When would you prefer Mediator over simply using dependency injection and interfaces between components?
- How can you prevent the mediator from turning into a god object in a large system?

## Ссылки (RU)

- [Mediator pattern](https://en.wikipedia.org/wiki/Mediator_pattern)
- [Mediator Design Pattern](https://howtodoinjava.com/design-patterns/behavioral/mediator-pattern/)
- [Mediator Design Pattern in Kotlin](https://www.javaguides.net/2023/10/mediator-design-pattern-in-kotlin.html)
- [Mediator Pattern in Kotlin](https://www.baeldung.com/kotlin/mediator)
- [Mediator on Refactoring.Guru](https://refactoring.guru/design-patterns/mediator)
- [[c-architecture-patterns]]

## References

- [Mediator pattern](https://en.wikipedia.org/wiki/Mediator_pattern)
- [Mediator Design Pattern](https://howtodoinjava.com/design-patterns/behavioral/mediator-pattern/)
- [Mediator Design Pattern in Kotlin](https://www.javaguides.net/2023/10/mediator-design-pattern-in-kotlin.html)
- [Mediator Pattern in Kotlin](https://www.baeldung.com/kotlin/mediator)
- [Mediator on Refactoring.Guru](https://refactoring.guru/design-patterns/mediator)
- [[c-architecture-patterns]]
