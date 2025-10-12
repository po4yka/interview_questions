---
tags:
  - design-patterns
  - behavioral-patterns
  - mediator
  - gof-patterns
  - coupling
difficulty: medium
status: draft
---

# Mediator Pattern

# Question (EN)
> What is the Mediator pattern? When and why should it be used?

# Вопрос (RU)
> Что такое паттерн Mediator? Когда и зачем его следует использовать?

---

## Answer (EN)


**Mediator (Посредник)** - это поведенческий паттерн проектирования, который уменьшает связанность множества классов между собой, благодаря перемещению этих связей в один класс-посредник.

### Definition


Mediator is a behavioral design pattern that **reduces coupling between components of a program by making them communicate indirectly, through a special mediator object**. The Mediator makes it easy to modify, extend and reuse individual components because they're no longer dependent on dozens of other classes.

### Problems it Solves


Problems that the mediator design pattern can solve:

1. **Tight coupling between a set of interacting objects should be avoided**
2. **It should be possible to change the interaction between a set of objects independently**

Defining a set of interacting objects by accessing and updating each other directly is inflexible because it tightly couples the objects to each other. Tightly coupled objects are hard to implement, change, test, and reuse.

### Solution


Solutions described by the mediator design pattern:

- Define a separate **(mediator) object that encapsulates the interaction** between a set of objects
- Objects **delegate their interaction to a mediator object** instead of interacting with each other directly

The objects interact with each other indirectly through a mediator object. This makes the objects loosely coupled. They only refer to and know about their mediator object and have no explicit knowledge of each other.

## Пример: Basic Mediator

```kotlin
// Step 1: Define the Mediator interface
interface Mediator {
    fun notify(sender: Colleague, event: String)
}

// Step 2: Create concrete mediator class
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

// Base colleague class
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

// Client Code
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

**Output**:
```
ColleagueA triggers event A.
ColleagueB reacts to event A.
ColleagueB triggers event B.
ColleagueA reacts to event B.
```

## Android Example: Chat Room

```kotlin
// Mediator interface
interface ChatMediator {
    fun sendMessage(message: String, user: User)
    fun addUser(user: User)
}

// Concrete Mediator
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

// Colleague
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

// Usage
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

## Kotlin Example: UI Form Mediator

```kotlin
// UI Components (Colleagues)
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

## Android ViewModel Mediator Example

```kotlin
// Mediator - ViewModel coordinates between components
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


**Explanation**:

- **Mediator** interface defines contract for communication
- **Concrete mediator** implements coordination logic
- **Colleagues** communicate only through mediator, not directly
- **Reduces dependencies** - Each colleague only knows about mediator
- **Android**: Chat applications, form validation, ViewModel coordinating repositories

## Real World Examples

Real-world example of mediator pattern:

1. **Traffic control room at airports** - Flights communicate with tower, not each other
2. **Chat application** - Messages go through central hub, not peer-to-peer
3. **UI frameworks** - Event dispatchers coordinate component interactions

## Преимущества и недостатки

### Pros (Преимущества)


1. **Reduced coupling** - Components don't depend on each other
2. **Centralized control** - All interactions in one place
3. **Reusability** - Components can be reused independently
4. **Easier maintenance** - Changes to interactions don't affect components
5. **Single Responsibility** - Communication logic separated from components

### Cons (Недостатки)


1. **God object** - Mediator can become too complex
2. **Single point of failure** - Mediator failure affects all communication
3. **Maintenance complexity** - Adding features may require mediator changes

## Best Practices

```kotlin
// - DO: Use for complex component interactions
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

// - DO: Keep mediator focused
interface NotificationMediator {
    fun notify(event: String, data: Any)
}

// - DO: Use with Observer pattern
class EventBus : Mediator {
    private val subscribers = mutableMapOf<String, MutableList<(Any) -> Unit>>()

    fun subscribe(event: String, handler: (Any) -> Unit) {
        subscribers.getOrPut(event) { mutableListOf() }.add(handler)
    }

    fun publish(event: String, data: Any) {
        subscribers[event]?.forEach { it(data) }
    }
}

// - DON'T: Put business logic in mediator
// - DON'T: Make mediator know about all component details
// - DON'T: Use for simple component interactions
```

---



## Ответ (RU)

### Определение


Mediator is a behavioral design pattern that **reduces coupling between components of a program by making them communicate indirectly, through a special mediator object**. The Mediator makes it easy to modify, extend and reuse individual components because they're no longer dependent on dozens of other classes.

### Проблемы, которые решает


Problems that the mediator design pattern can solve:

1. **Tight coupling between a set of interacting objects should be avoided**
2. **It should be possible to change the interaction between a set of objects independently**

Defining a set of interacting objects by accessing and updating each other directly is inflexible because it tightly couples the objects to each other. Tightly coupled objects are hard to implement, change, test, and reuse.

### Решение


Solutions described by the mediator design pattern:

- Define a separate **(mediator) object that encapsulates the interaction** between a set of objects
- Objects **delegate their interaction to a mediator object** instead of interacting with each other directly

The objects interact with each other indirectly through a mediator object. This makes the objects loosely coupled. They only refer to and know about their mediator object and have no explicit knowledge of each other.

### Объяснение


**Explanation**:

- **Mediator** interface defines contract for communication
- **Concrete mediator** implements coordination logic
- **Colleagues** communicate only through mediator, not directly
- **Reduces dependencies** - Each colleague only knows about mediator
- **Android**: Chat applications, form validation, ViewModel coordinating repositories

### Pros (Преимущества)


1. **Reduced coupling** - Components don't depend on each other
2. **Centralized control** - All interactions in one place
3. **Reusability** - Components can be reused independently
4. **Easier maintenance** - Changes to interactions don't affect components
5. **Single Responsibility** - Communication logic separated from components

### Cons (Недостатки)


1. **God object** - Mediator can become too complex
2. **Single point of failure** - Mediator failure affects all communication
3. **Maintenance complexity** - Adding features may require mediator changes


**Mediator (Посредник)** - это поведенческий паттерн проектирования, который уменьшает связанность множества классов между собой, благодаря перемещению этих связей в один класс-посредник. **Проблема**: Тесная связанность между взаимодействующими объектами. **Решение**: Создать объект-посредник, который инкапсулирует взаимодействия, объекты общаются через него. **Использовать когда**: (1) Сложная коммуникация между компонентами, (2) Нужна слабая связанность, (3) Необходим централизованный контроль. **Android**: Чат-приложения, валидация форм, ViewModel координирующий репозитории. **Плюсы**: уменьшенная связанность, централизованный контроль, переиспользуемость. **Минусы**: риск god object, единая точка отказа. **Примеры**: Чат-комната, валидация UI-форм, управление воздушным движением, event bus.

## Links

- [Mediator pattern](https://en.wikipedia.org/wiki/Mediator_pattern)
- [Mediator Design Pattern](https://howtodoinjava.com/design-patterns/behavioral/mediator-pattern/)
- [Mediator Design Pattern in Kotlin](https://www.javaguides.net/2023/10/mediator-design-pattern-in-kotlin.html)
- [Mediator Pattern in Kotlin](https://www.baeldung.com/kotlin/mediator)

## Further Reading

- [Mediator](https://refactoring.guru/design-patterns/mediator)
- [Mediator Software Pattern Kotlin Examples](https://softwarepatterns.com/kotlin/mediator-software-pattern-kotlin-example)

---
*Source: Kirchhoff Android Interview Questions*


---

## Related Questions

### Hub
- [[q-design-patterns-types--design-patterns--medium]] - Design pattern categories overview

### Behavioral Patterns
- [[q-strategy-pattern--design-patterns--medium]] - Strategy pattern
- [[q-observer-pattern--design-patterns--medium]] - Observer pattern
- [[q-command-pattern--design-patterns--medium]] - Command pattern
- [[q-template-method-pattern--design-patterns--medium]] - Template Method pattern
- [[q-iterator-pattern--design-patterns--medium]] - Iterator pattern

### Creational Patterns
- [[q-factory-method-pattern--design-patterns--medium]] - Factory Method pattern

### Structural Patterns
- [[q-adapter-pattern--design-patterns--medium]] - Adapter pattern

