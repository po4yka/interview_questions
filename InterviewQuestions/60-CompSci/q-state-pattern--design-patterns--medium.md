---
id: dp-011
title: "State Pattern / Паттерн State"
aliases: [State Pattern, State Паттерн]
topic: behavioral
subtopics: [polymorphism, state-machine]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-architecture-patterns, c-computer-science, q-abstract-factory-pattern--cs--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [behavioral, difficulty/medium, state-machine]

date created: Saturday, November 1st 2025, 1:27:09 pm
date modified: Tuesday, November 25th 2025, 8:53:53 pm
---

# Вопрос (RU)
> Что такое паттерн State? Когда и зачем его следует использовать?

# Question (EN)
> What is the State pattern? When and why should it be used?

---

## Ответ (RU)

### Определение

Паттерн State (Состояние) - это поведенческий паттерн проектирования, который **позволяет объекту изменять свое поведение при изменении внутреннего состояния**. Этот паттерн инкапсулирует различное поведение одного и того же объекта на основе его внутреннего состояния и предоставляет более чистый способ изменения поведения объекта во время выполнения за счет полиморфизма вместо длинных цепочек условных операторов.

### Проблемы, Которые Решает

Паттерн State решает две основные проблемы:

1. **Объект должен изменять свое поведение при изменении внутреннего состояния**.
2. **Поведение, специфичное для состояния, должно быть определено независимо** — добавление новых состояний не должно влиять на поведение существующих состояний.

### Почему Это Проблема?

Реализация поведения, специфичного для состояния, непосредственно в классе через условные операторы негибка, так как жестко привязывает класс ко всем возможным вариантам поведения и усложняет добавление новых состояний или изменение существующих без изменения этого класса.

### Решение

Паттерн описывает два ключевых подхода:

1. **Определить отдельные объекты состояний**, которые инкапсулируют поведение, специфичное для каждого состояния.
2. **Контекст делегирует поведение, специфичное для состояния**, своему текущему объекту состояния вместо прямой реализации через условные конструкции.

Это делает контекст независимым от конкретной реализации поведения состояний. Новые состояния добавляются путем создания новых классов состояний. Контекст может изменять свое поведение во время выполнения, переключая текущий объект состояния.

### Ключевые Особенности

1. **Инкапсуляция состояния** — каждое состояние выделено в собственный класс или вариант.
2. **Динамическое изменение поведения** — поведение объекта меняется при смене состояния за счет полиморфизма.
3. **Меньше условной логики** — длинные цепочки if-else/when заменяются делегированием состояниям (при этом переходы между состояниями могут содержать простые проверки).

### Пример: Базовый Конечный Автомат

(Код идентичен английскому примеру; изменены только комментарии.)

```kotlin
// Интерфейс состояния
interface State {
    fun handle(context: Context)
}

// Конкретные состояния
class ConcreteStateA : State {
    override fun handle(context: Context) {
        println("State A: Обработка запроса и переход в State B")
        context.setState(ConcreteStateB())
    }
}

class ConcreteStateB : State {
    override fun handle(context: Context) {
        println("State B: Обработка запроса и переход в State A")
        context.setState(ConcreteStateA())
    }
}

// Контекст
class Context {
    private var currentState: State? = null

    fun setState(state: State) {
        currentState = state
        println("Context: Состояние изменено на ${state::class.simpleName}")
    }

    fun request() {
        currentState?.handle(this) ?: println("Context: Состояние не установлено")
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

Этот пример отражает классический GoF-подход: `Context` хранит ссылку на `State` и меняет поведение, переключая объекты состояний.

### Пример Для Android: Состояния Медиаплеера

```kotlin
// Интерфейс состояния
interface PlayerState {
    fun play(player: MediaPlayer)
    fun pause(player: MediaPlayer)
    fun stop(player: MediaPlayer)
    fun getStateName(): String
}

// Конкретные состояния
class PlayingState : PlayerState {
    override fun play(player: MediaPlayer) {
        println("Уже воспроизводится")
    }

    override fun pause(player: MediaPlayer) {
        println("Пауза воспроизведения")
        player.setState(PausedState())
    }

    override fun stop(player: MediaPlayer) {
        println("Остановка воспроизведения")
        player.setState(StoppedState())
    }

    override fun getStateName() = "Playing"
}

class PausedState : PlayerState {
    override fun play(player: MediaPlayer) {
        println("Продолжение воспроизведения")
        player.setState(PlayingState())
    }

    override fun pause(player: MediaPlayer) {
        println("Уже на паузе")
    }

    override fun stop(player: MediaPlayer) {
        println("Остановка из состояния паузы")
        player.setState(StoppedState())
    }

    override fun getStateName() = "Paused"
}

class StoppedState : PlayerState {
    override fun play(player: MediaPlayer) {
        println("Старт воспроизведения")
        player.setState(PlayingState())
    }

    override fun pause(player: MediaPlayer) {
        println("Нельзя поставить на паузу — плеер остановлен")
    }

    override fun stop(player: MediaPlayer) {
        println("Уже остановлен")
    }

    override fun getStateName() = "Stopped"
}

// Контекст — медиаплеер
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

fun main() {
    val player = MediaPlayer()
    player.play()   // Stopped -> Playing
    player.pause()  // Playing -> Paused
    player.play()   // Paused -> Playing
    player.stop()   // Playing -> Stopped
}
```

Этот пример соответствует паттерну State: `MediaPlayer` (контекст) делегирует поведение текущему `PlayerState`.

### Пример `ViewModel`: UI-состояния

Здесь используется `sealed class` для моделирования UI-состояний. Это ближе к конечному автомату/ADT, но решает ту же задачу: поведение и отображение зависят от состояния.

```kotlin
// Состояния UI
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
```

### Kotlin-пример: Обработка Заказа

Тот же подход с `sealed class`, как в английском примере:

```kotlin
sealed class OrderState {
    abstract fun processNext(order: Order)
    abstract fun cancel(order: Order)

    object Pending : OrderState() {
        override fun processNext(order: Order) {
            println("Обработка платежа...")
            order.setState(Processing)
        }

        override fun cancel(order: Order) {
            println("Заказ отменен")
            order.setState(Cancelled)
        }
    }

    object Processing : OrderState() {
        override fun processNext(order: Order) {
            println("Отправка заказа...")
            order.setState(Shipped)
        }

        override fun cancel(order: Order) {
            println("Нельзя отменить — уже в обработке")
        }
    }

    object Shipped : OrderState() {
        override fun processNext(order: Order) {
            println("Заказ доставлен")
            order.setState(Delivered)
        }

        override fun cancel(order: Order) {
            println("Нельзя отменить — уже отправлен")
        }
    }

    object Delivered : OrderState() {
        override fun processNext(order: Order) {
            println("Заказ завершен — действий нет")
        }

        override fun cancel(order: Order) {
            println("Нельзя отменить — уже доставлен")
        }
    }

    object Cancelled : OrderState() {
        override fun processNext(order: Order) {
            println("Отмененный заказ — действий нет")
        }

        override fun cancel(order: Order) {
            println("Уже отменен")
        }
    }
}

class Order(private var state: OrderState = OrderState.Pending) {
    fun setState(newState: OrderState) {
        state = newState
        println("Состояние заказа: ${state::class.simpleName}")
    }

    fun processNext() = state.processNext(this)
    fun cancel() = state.cancel(this)
}
```

### Объяснение (итог)

- **Интерфейс/абстракция состояния** задает контракт.
- **Конкретные состояния** реализуют различающееся поведение.
- **Контекст** хранит текущее состояние и делегирует ему вызовы.
- **Переходы между состояниями** могут быть реализованы внутри состояний или контекста.
- Классический GoF-подход опирается на полиморфные объекты-состояния.
- В Kotlin/Android также распространен подход с `sealed class` + `when`/`StateFlow` для моделирования конечных автоматов; он структурно отличается от классического GoF State, но решает ту же задачу: "поведение зависит от состояния".

### Применение (реальные примеры)

1. **ТВ-приставка** — кнопки пульта работают по-разному в состояниях ON/OFF.
2. **Состояния потока/потока выполнения** — жизненный цикл потоков.
3. **Обработка заказа** — Pending → Processing → Shipped → Delivered.
4. **Медиаплееры** — Playing, Paused, Stopped.

### Когда Использовать

Используйте State, когда:

- Поведение объекта существенно зависит от его состояния.
- Есть несколько состояний с разным поведением.
- Хотите избежать разрастания условных операторов и "божественных" классов.

### Лучшие Практики

- Ясно определяйте возможные состояния и допустимые переходы.
- Держите логику, специфичную для состояния, внутри соответствующего состояния.
- Для Kotlin/Android UI удобно использовать `sealed class` + потоки (`StateFlow`) для реактивных обновлений.
- Не применяйте тяжеловесную реализацию State там, где достаточно простого булева флага.

### Дополнительные Вопросы (RU)

- Как вы бы отрефакторили сложную цепочку `when`/`if` в дизайн на основе State?
- Сравните классический паттерн State (GoF) с моделированием на основе `sealed class` + `when` в Kotlin.
- Когда паттерн State является избыточным и какие более простые альтернативы вы бы использовали?

### Ссылки (RU)

- [[c-architecture-patterns]]
- [[c-computer-science]]
- [State pattern](https://en.wikipedia.org/wiki/State_pattern)
- [State Design Pattern in Kotlin](https://medium.com/softaai-blogs/gain-clarity-on-the-state-design-pattern-in-kotlin-a-step-by-step-guide-4f768db2cc03)
- [State Design Pattern](https://howtodoinjava.com/design-patterns/behavioral/state-design-pattern/)
- [State Design Pattern](https://sourcemaking.com/design_patterns/state)
- [State pattern for changing internal processes](https://blog.devgenius.io/state-pattern-for-changing-internal-processes-kotlin-72bd4ef92b2e)

---

## Answer (EN)

State is a behavioral design pattern that allows an object to change its behavior when its internal state changes. It encapsulates varying behavior into separate state types instead of hard-coding all branches in one "god" class.

### Definition

The State pattern is a behavioral software design pattern that **allows an object to alter its behavior when its internal state changes**. This pattern encapsulates varying behavior for the same object based on its internal state, providing a cleaner way for an object to change its behavior at runtime by using polymorphism instead of long conditional statements.

### Problems it Solves

1. An object should change its behavior when its internal state changes.
2. State-specific behavior should be defined independently so that adding new states does not break existing behavior.

### Why is This a Problem?

Implementing state-specific behavior directly within a class via conditionals is inflexible because it tightly couples the class to all possible behaviors and makes it hard to add a new state or change existing behavior later without modifying that class.

### Solution

1. Define separate state objects that encapsulate state-specific behavior.
2. A context class delegates state-specific behavior to its current state object instead of implementing it directly with conditionals.

New states can be added by defining new state classes; behavior changes at runtime by switching the current state object.

### Key Features

1. State encapsulation in dedicated types.
2. Dynamic behavior changes via polymorphism.
3. Reduced conditional complexity.

### Example: Basic State Machine

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

This is the classic GoF State implementation: `Context` holds a `State` and behavior changes by switching state objects.

### Android Example: Media Player States

```kotlin
interface PlayerState {
    fun play(player: MediaPlayer)
    fun pause(player: MediaPlayer)
    fun stop(player: MediaPlayer)
    fun getStateName(): String
}

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
```

The `MediaPlayer` context delegates to the current `PlayerState`.

### Android `ViewModel` Example: UI States

This example uses a sealed class and flows; conceptually close to an FSM and used heavily in Kotlin/Android.

```kotlin
sealed class UiState {
    object Loading : UiState()
    data class Success(val data: List<String>) : UiState()
    data class Error(val message: String) : UiState()
    object Empty : UiState()
}

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
```

### Kotlin Example: Order Processing

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
            println("Order complete - no further actions")
        }

        override fun cancel(order: Order) {
            println("Cannot cancel - already delivered")
        }
    }

    object Cancelled : OrderState() {
        override fun processNext(order: Order) {
            println("Cancelled order - no actions")
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

- State abstraction defines the interface.
- Concrete states implement per-state behavior.
- `Context` holds current state and delegates.
- Transitions may live in states or in context.
- Classic GoF State uses polymorphic state objects.
- Sealed-class based approaches (e.g., `sealed class` + `when`/`StateFlow`) are structurally different from classic GoF State but solve the same core concern: behavior depends on state.

### Real World Examples

1. TV box power states.
2. Thread lifecycle states.
3. Order workflow.
4. Media player states.

### When to Use

Use State when:

- Object behavior depends on state.
- There are multiple states with different behavior.
- You want to avoid huge conditional blocks.

### Best Practices

- Model clear states and transitions.
- Keep state-specific logic inside state implementations.
- In Kotlin, sealed classes + `when` + `StateFlow` are great for UI and FSM-like logic.
- Do not overuse the pattern for trivial flags.

## Related Questions

- How would you refactor a complex `when`/`if` chain into a State-based design?
- Compare the classic GoF State pattern with sealed class + `when` modeling in Kotlin.
- When is the State pattern overkill, and what simpler alternatives would you use?

### Links

- [State pattern](https://en.wikipedia.org/wiki/State_pattern)
- [State Design Pattern in Kotlin](https://medium.com/softaai-blogs/gain-clarity-on-the-state-design-pattern-in-kotlin-a-step-by-step-guide-4f768db2cc03)
- [State Design Pattern](https://howtodoinjava.com/design-patterns/behavioral/state-design-pattern/)

### Further Reading

- [State Design Pattern](https://sourcemaking.com/design_patterns/state)
- [State pattern for changing internal processes](https://blog.devgenius.io/state-pattern-for-changing-internal-processes-kotlin-72bd4ef92b2e)

### References

- [[c-architecture-patterns]]
- [[c-computer-science]]
- [State pattern](https://en.wikipedia.org/wiki/State_pattern)
