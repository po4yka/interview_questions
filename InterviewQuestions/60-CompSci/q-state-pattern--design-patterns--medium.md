---
id: 20251012-1227111182
title: "State Pattern / State Паттерн"
topic: computer-science
difficulty: medium
status: draft
moc: moc-cs
related: [q-bridge-pattern--design-patterns--hard, q-hot-vs-cold-flows--programming-languages--medium, q-sharedflow-vs-stateflow--programming-languages--easy]
created: 2025-10-15
tags:
  - design-patterns
  - behavioral-patterns
  - state
  - gof-patterns
  - state-machine
---
# State Pattern

# Question (EN)
> What is the State pattern? When and why should it be used?

# Вопрос (RU)
> Что такое паттерн State? Когда и зачем его следует использовать?

---

## Answer (EN)


**State (Состояние)** - это поведенческий паттерн проектирования, который позволяет объекту изменять своё поведение в зависимости от внутреннего состояния. При этом создается впечатление, что изменился класс объекта.

### Definition


The state pattern is a behavioral software design pattern that **allows an object to alter its behavior when its internal state changes**. This pattern encapsulates varying behavior for the same object based on its internal state, providing a cleaner way for an object to change its behavior at runtime without resorting to conditional statements.

### Problems it Solves


The state pattern is set to solve two main problems:

1. **An object should change its behavior when its internal state changes**
2. **State-specific behavior should be defined independently** - Adding new states should not affect the behavior of existing states

### Why is this a problem?


Implementing state-specific behavior directly within a class is inflexible because it commits the class to a particular behavior and makes it impossible to add a new state or change the behavior of an existing state later without changing the class.

### Solution


The pattern describes two solutions:

1. **Define separate (state) objects** that encapsulate state-specific behavior for each state
2. **A class delegates state-specific behavior** to its current state object instead of implementing it directly

This makes a class independent of how state-specific behavior is implemented. New states can be added by defining new state classes. A class can change its behavior at run-time by changing its current state object.

## Ключевые особенности

Key Features:

1. **State Encapsulation** - Each state is encapsulated in its own class
2. **Behavioral Changes** - Behavior changes dynamically as object's state changes
3. **No Conditionals** - Eliminates long if-else or when chains by using polymorphism

## Пример: Basic State Machine

```kotlin
// State Interface
interface State {
    fun handle(context: Context)
}

// Concrete States
class ConcreteStateA : State {
    override fun handle(context: Context) {
        println("State A: Handling request and transitioning to State B")
        context.setState(ConcreteStateB())
    }
}

class ConcreteStateB : State {
    override fun handle(context: Context) {
        println("State B: Handling request and transitioning to State A")
        context.setState(ConcreteStateA())
    }
}

// Context
class Context {
    private var currentState: State? = null

    fun setState(state: State) {
        currentState = state
        println("Context: State changed to ${state::class.simpleName}")
    }

    fun request() {
        currentState?.handle(this) ?: println("Context: No state is set")
    }
}

fun main() {
    val context = Context()
    context.setState(ConcreteStateA())
    context.request() // State A -> State B
    context.request() // State B -> State A
    context.request() // State A -> State B
}
```

**Output**:
```
Context: State changed to ConcreteStateA
State A: Handling request and transitioning to State B
Context: State changed to ConcreteStateB
State B: Handling request and transitioning to State A
Context: State changed to ConcreteStateA
State A: Handling request and transitioning to State B
Context: State changed to ConcreteStateB
```

## Android Example: Media Player States

```kotlin
// State interface
interface PlayerState {
    fun play(player: MediaPlayer)
    fun pause(player: MediaPlayer)
    fun stop(player: MediaPlayer)
    fun getStateName(): String
}

// Concrete states
class PlayingState : PlayerState {
    override fun play(player: MediaPlayer) {
        println("Already playing")
    }

    override fun pause(player: MediaPlayer) {
        println("Pausing playback")
        player.setState(PausedState())
    }

    override fun stop(player: MediaPlayer) {
        println("Stopping playback")
        player.setState(StoppedState())
    }

    override fun getStateName() = "Playing"
}

class PausedState : PlayerState {
    override fun play(player: MediaPlayer) {
        println("Resuming playback")
        player.setState(PlayingState())
    }

    override fun pause(player: MediaPlayer) {
        println("Already paused")
    }

    override fun stop(player: MediaPlayer) {
        println("Stopping from pause")
        player.setState(StoppedState())
    }

    override fun getStateName() = "Paused"
}

class StoppedState : PlayerState {
    override fun play(player: MediaPlayer) {
        println("Starting playback")
        player.setState(PlayingState())
    }

    override fun pause(player: MediaPlayer) {
        println("Cannot pause - player is stopped")
    }

    override fun stop(player: MediaPlayer) {
        println("Already stopped")
    }

    override fun getStateName() = "Stopped"
}

// Context - Media Player
class MediaPlayer {
    private var state: PlayerState = StoppedState()

    fun setState(newState: PlayerState) {
        state = newState
        println("State changed to: ${state.getStateName()}")
    }

    fun play() = state.play(this)
    fun pause() = state.pause(this)
    fun stop() = state.stop(this)
    fun getCurrentState() = state.getStateName()
}

// Usage
fun main() {
    val player = MediaPlayer()
    player.play()   // Stopped -> Playing
    player.pause()  // Playing -> Paused
    player.play()   // Paused -> Playing
    player.stop()   // Playing -> Stopped
}
```

## Android ViewModel Example: UI States

```kotlin
// State sealed class
sealed class UiState {
    object Loading : UiState()
    data class Success(val data: List<String>) : UiState()
    data class Error(val message: String) : UiState()
    object Empty : UiState()
}

// ViewModel
class DataViewModel(
    private val repository: DataRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadData() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading

            try {
                val data = repository.fetchData()
                _uiState.value = if (data.isEmpty()) {
                    UiState.Empty
                } else {
                    UiState.Success(data)
                }
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }

    fun retry() = loadData()
}

// Fragment/Activity
class DataFragment : Fragment() {
    private val viewModel: DataViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                when (state) {
                    is UiState.Loading -> showLoading()
                    is UiState.Success -> showData(state.data)
                    is UiState.Error -> showError(state.message)
                    is UiState.Empty -> showEmpty()
                }
            }
        }
    }

    private fun showLoading() { /* Show progress */ }
    private fun showData(data: List<String>) { /* Display data */ }
    private fun showError(message: String) { /* Show error */ }
    private fun showEmpty() { /* Show empty state */ }
}
```

## Kotlin Example: Order Processing

```kotlin
sealed class OrderState {
    abstract fun processNext(order: Order)
    abstract fun cancel(order: Order)

    object Pending : OrderState() {
        override fun processNext(order: Order) {
            println("Processing payment...")
            order.setState(Processing)
        }

        override fun cancel(order: Order) {
            println("Order cancelled")
            order.setState(Cancelled)
        }
    }

    object Processing : OrderState() {
        override fun processNext(order: Order) {
            println("Shipping order...")
            order.setState(Shipped)
        }

        override fun cancel(order: Order) {
            println("Cannot cancel - already processing")
        }
    }

    object Shipped : OrderState() {
        override fun processNext(order: Order) {
            println("Order delivered")
            order.setState(Delivered)
        }

        override fun cancel(order: Order) {
            println("Cannot cancel - already shipped")
        }
    }

    object Delivered : OrderState() {
        override fun processNext(order: Order) {
            println("Order complete - no further action")
        }

        override fun cancel(order: Order) {
            println("Cannot cancel - already delivered")
        }
    }

    object Cancelled : OrderState() {
        override fun processNext(order: Order) {
            println("Cancelled order - no action")
        }

        override fun cancel(order: Order) {
            println("Already cancelled")
        }
    }
}

class Order(private var state: OrderState = OrderState.Pending) {
    fun setState(newState: OrderState) {
        state = newState
        println("Order state: ${state::class.simpleName}")
    }

    fun processNext() = state.processNext(this)
    fun cancel() = state.cancel(this)
}
```

### Explanation


**Explanation**:

- **State interface** defines methods for handling state-specific behavior
- **Concrete states** implement specific behavior for each state
- **Context** maintains reference to current state and delegates behavior
- **State transitions** happen within state classes themselves
- **Android**: UI states with sealed classes, media player states, order processing

## Применение

Real World Examples:

1. **TV box** - Different states (ON/OFF) respond differently to remote buttons
2. **Thread states** - Java thread lifecycle states
3. **Order processing** - Pending → Processing → Shipped → Delivered
4. **Media players** - Playing, Paused, Stopped states

## Преимущества и недостатки

### Pros (Преимущества)


1. **Single Responsibility** - Each state is in separate class
2. **Open/Closed Principle** - Easy to add new states
3. **Eliminates conditionals** - No complex if-else chains
4. **Cleaner code** - State-specific behavior is localized
5. **Easy to understand** - Clear state transitions

### Cons (Недостатки)


1. **Overkill for simple states** - Too complex for few states
2. **Many classes** - Each state needs a class
3. **State coupling** - States need to know about each other
4. **Complexity** - Can be hard to track state transitions

## Best Practices

```kotlin
// - DO: Use sealed classes in Kotlin
sealed class ConnectionState {
    object Disconnected : ConnectionState()
    object Connecting : ConnectionState()
    object Connected : ConnectionState()
    data class Failed(val error: String) : ConnectionState()
}

// - DO: Use with StateFlow for reactive updates
class ConnectionManager {
    private val _state = MutableStateFlow<ConnectionState>(ConnectionState.Disconnected)
    val state: StateFlow<ConnectionState> = _state.asStateFlow()

    fun connect() {
        when (_state.value) {
            is ConnectionState.Disconnected -> {
                _state.value = ConnectionState.Connecting
                // Connect logic
            }
            else -> println("Invalid state for connect")
        }
    }
}

// - DO: Define clear state transitions
interface State {
    fun nextState(): State?
}

// - DON'T: Use for simple boolean flags
// - DON'T: Make states mutable
// - DON'T: Put business logic in context
```

**English**: **State** is a behavioral pattern that allows an object to change its behavior when internal state changes. **Problem**: Complex conditionals for state-specific behavior. **Solution**: Encapsulate each state in separate class, delegate behavior to current state. **Use when**: (1) Object behavior depends on state, (2) Many states with different behaviors, (3) Want to avoid complex conditionals. **Android**: UI states with sealed classes, media player, network connection states. **Pros**: eliminates conditionals, easy to add states, cleaner code. **Cons**: many classes, complexity for simple states. **Examples**: Media player, order processing, connection states, UI states.

## Links

- [State pattern](https://en.wikipedia.org/wiki/State_pattern)
- [State Design Pattern in Kotlin](https://medium.com/softaai-blogs/gain-clarity-on-the-state-design-pattern-in-kotlin-a-step-by-step-guide-4f768db2cc03)
- [State Design Pattern](https://howtodoinjava.com/design-patterns/behavioral/state-design-pattern/)

## Further Reading

- [State Design Pattern](https://sourcemaking.com/design_patterns/state)
- [State pattern for changing internal processes](https://blog.devgenius.io/state-pattern-for-changing-internal-processes-kotlin-72bd4ef92b2e)

---
*Source: Kirchhoff Android Interview Questions*


## Ответ (RU)

### Определение

Паттерн State (Состояние) - это поведенческий паттерн проектирования, который **позволяет объекту изменять свое поведение при изменении внутреннего состояния**. Этот паттерн инкапсулирует различное поведение одного и того же объекта на основе его внутреннего состояния, предоставляя более чистый способ изменения поведения объекта во время выполнения без использования условных операторов.

### Проблемы, которые решает

Паттерн State решает две основные проблемы:

1. **Объект должен изменять свое поведение при изменении внутреннего состояния**
2. **Поведение, специфичное для состояния, должно быть определено независимо** - Добавление новых состояний не должно влиять на поведение существующих состояний

### Почему это проблема?

Реализация поведения, специфичного для состояния, непосредственно в классе негибка, поскольку привязывает класс к конкретному поведению и делает невозможным добавление нового состояния или изменение поведения существующего состояния позже без изменения класса.

### Решение

Паттерн описывает два решения:

1. **Определить отдельные объекты состояний**, которые инкапсулируют поведение, специфичное для каждого состояния
2. **Класс делегирует поведение, специфичное для состояния**, своему текущему объекту состояния вместо прямой реализации

Это делает класс независимым от того, как реализовано поведение, специфичное для состояния. Новые состояния могут быть добавлены путем определения новых классов состояний. Класс может изменять свое поведение во время выполнения, изменяя свой текущий объект состояния.

### Объяснение

**Пояснение**:

- **Интерфейс State** определяет методы для обработки поведения, специфичного для состояния
- **Конкретные состояния** реализуют специфичное поведение для каждого состояния
- **Context (Контекст)** поддерживает ссылку на текущее состояние и делегирует поведение
- **Переходы между состояниями** происходят внутри самих классов состояний
- **Android**: UI состояния с sealed классами, состояния медиа-плеера, обработка заказов

### Pros (Преимущества)

1. **Единственная ответственность** - Каждое состояние в отдельном классе
2. **Принцип открытости/закрытости** - Легко добавлять новые состояния
3. **Устраняет условные операторы** - Нет сложных цепочек if-else
4. **Чище код** - Поведение, специфичное для состояния, локализовано
5. **Легко понять** - Четкие переходы между состояниями

### Cons (Недостатки)

1. **Избыточность для простых состояний** - Слишком сложно для нескольких состояний
2. **Много классов** - Каждое состояние требует класс
3. **Связанность состояний** - Состояния должны знать друг о друге
4. **Сложность** - Может быть трудно отслеживать переходы между состояниями


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

