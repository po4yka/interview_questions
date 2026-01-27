---
id: android-arch-003
title: Finite State Machines for UI / Конечные автоматы для UI
aliases:
- FSM
- State Machine
- Finite State Machine
- Конечный автомат
- Машина состояний
topic: android
subtopics:
- architecture
- state-management
question_kind: android
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-mvi-architecture--android--hard
- q-mvi-pattern--architecture--hard
- q-unidirectional-data-flow--architecture--medium
created: 2026-01-23
updated: 2026-01-23
sources:
- https://developer.android.com/topic/architecture/ui-layer/stateholders
- https://statecharts.dev/
tags:
- android/architecture
- android/state-management
- difficulty/hard
- state-machine
anki_cards:
- slug: android-arch-003-0-en
  language: en
- slug: android-arch-003-0-ru
  language: ru
---
# Vopros (RU)

> Как использовать конечные автоматы (Finite State Machines) для управления состоянием UI? Приведите пример с валидацией переходов.

# Question (EN)

> How to use Finite State Machines (FSM) for UI state management? Provide an example with transition validation.

---

## Otvet (RU)

**Конечный автомат (FSM)** - модель, где система может находиться в одном из конечного числа состояний, и переходы между состояниями происходят по определенным событиям с валидацией.

### Зачем FSM для UI?

| Проблема без FSM | Решение с FSM |
|------------------|---------------|
| Невалидные состояния (`isLoading && hasError`) | Только допустимые состояния |
| Сложная логика `if/else` | Декларативные переходы |
| Баги из-за гонок событий | Валидация переходов |
| Трудно отлаживать | Визуализация и логирование |

### Базовая структура FSM

```kotlin
// Состояния - sealed class гарантирует exhaustive when
sealed interface AuthState {
    data object Idle : AuthState
    data object Loading : AuthState
    data class Authenticated(val user: User) : AuthState
    data class Error(val message: String) : AuthState
}

// События
sealed interface AuthEvent {
    data class Login(val email: String, val password: String) : AuthEvent
    data object Logout : AuthEvent
    data object Retry : AuthEvent
    data class LoginSuccess(val user: User) : AuthEvent
    data class LoginFailed(val error: String) : AuthEvent
}

// State Machine
class AuthStateMachine {
    private val _state = MutableStateFlow<AuthState>(AuthState.Idle)
    val state: StateFlow<AuthState> = _state.asStateFlow()

    fun transition(event: AuthEvent) {
        val currentState = _state.value
        val newState = reduce(currentState, event)

        if (newState != null) {
            _state.value = newState
        } else {
            // Невалидный переход - можно залогировать или выбросить исключение
            Log.w("FSM", "Invalid transition: $currentState + $event")
        }
    }

    // Reducer с валидацией переходов
    private fun reduce(state: AuthState, event: AuthEvent): AuthState? {
        return when (state) {
            is AuthState.Idle -> when (event) {
                is AuthEvent.Login -> AuthState.Loading
                else -> null  // Только Login допустим из Idle
            }

            is AuthState.Loading -> when (event) {
                is AuthEvent.LoginSuccess -> AuthState.Authenticated(event.user)
                is AuthEvent.LoginFailed -> AuthState.Error(event.error)
                else -> null  // Нельзя Login или Logout пока Loading
            }

            is AuthState.Authenticated -> when (event) {
                is AuthEvent.Logout -> AuthState.Idle
                else -> null  // Только Logout из Authenticated
            }

            is AuthState.Error -> when (event) {
                is AuthEvent.Retry -> AuthState.Loading
                is AuthEvent.Login -> AuthState.Loading
                else -> null
            }
        }
    }
}
```

### Диаграмма переходов

```text
          Login
    +----[Login]---->+
    |                |
    v                |
  Idle               |
    ^                v
    |             Loading
    |    Success/   |    \Failure
    |      /        |     \
 Logout   v         |      v
    |  Authenticated|     Error
    |       |       |       |
    +-------+       +--[Retry]-+
```

### FSM с Side Effects

```kotlin
// Полная реализация с side effects
@HiltViewModel
class AuthViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {

    private val stateMachine = AuthStateMachine()
    val state = stateMachine.state

    private val _sideEffects = Channel<AuthSideEffect>(Channel.BUFFERED)
    val sideEffects = _sideEffects.receiveAsFlow()

    fun onEvent(event: AuthEvent) {
        val previousState = state.value

        // 1. Выполняем переход
        stateMachine.transition(event)

        // 2. Side effects на основе перехода
        handleSideEffect(previousState, event, state.value)
    }

    private fun handleSideEffect(
        previousState: AuthState,
        event: AuthEvent,
        newState: AuthState
    ) {
        viewModelScope.launch {
            // Side effect: переход в Loading -> запускаем login
            if (previousState is AuthState.Idle && newState is AuthState.Loading) {
                when (event) {
                    is AuthEvent.Login -> performLogin(event.email, event.password)
                    else -> Unit
                }
            }

            // Side effect: переход Error -> Loading (Retry)
            if (previousState is AuthState.Error && newState is AuthState.Loading) {
                // Повторяем последний login (нужно хранить credentials)
            }

            // Side effect: успешный вход
            if (newState is AuthState.Authenticated) {
                _sideEffects.send(AuthSideEffect.NavigateToHome)
            }
        }
    }

    private suspend fun performLogin(email: String, password: String) {
        authRepository.login(email, password)
            .onSuccess { user ->
                onEvent(AuthEvent.LoginSuccess(user))
            }
            .onFailure { error ->
                onEvent(AuthEvent.LoginFailed(error.message ?: "Unknown error"))
            }
    }
}

sealed interface AuthSideEffect {
    data object NavigateToHome : AuthSideEffect
    data class ShowError(val message: String) : AuthSideEffect
}
```

### Иерархические состояния (Hierarchical FSM)

Для сложных UI используйте вложенные состояния:

```kotlin
// Иерархическое состояние с подсостояниями
sealed interface OrderState {
    // Верхний уровень
    data object Draft : OrderState

    // Состояние с подсостояниями
    sealed interface Checkout : OrderState {
        data object EnteringAddress : Checkout
        data object SelectingPayment : Checkout
        data object Confirming : Checkout
    }

    sealed interface Processing : OrderState {
        data object PaymentPending : Processing
        data object PaymentProcessing : Processing
        data class PaymentFailed(val reason: String) : Processing
    }

    data class Completed(val orderId: String) : OrderState
    data class Cancelled(val reason: String) : OrderState
}

// Переходы с учетом иерархии
class OrderStateMachine {
    fun reduce(state: OrderState, event: OrderEvent): OrderState? {
        return when (state) {
            is OrderState.Draft -> when (event) {
                is OrderEvent.StartCheckout -> OrderState.Checkout.EnteringAddress
                else -> null
            }

            is OrderState.Checkout.EnteringAddress -> when (event) {
                is OrderEvent.AddressEntered -> OrderState.Checkout.SelectingPayment
                is OrderEvent.Cancel -> OrderState.Cancelled("User cancelled")
                else -> null
            }

            is OrderState.Checkout.SelectingPayment -> when (event) {
                is OrderEvent.PaymentSelected -> OrderState.Checkout.Confirming
                is OrderEvent.Back -> OrderState.Checkout.EnteringAddress
                is OrderEvent.Cancel -> OrderState.Cancelled("User cancelled")
                else -> null
            }

            is OrderState.Checkout.Confirming -> when (event) {
                is OrderEvent.Confirm -> OrderState.Processing.PaymentPending
                is OrderEvent.Back -> OrderState.Checkout.SelectingPayment
                is OrderEvent.Cancel -> OrderState.Cancelled("User cancelled")
                else -> null
            }

            is OrderState.Processing.PaymentPending -> when (event) {
                is OrderEvent.PaymentStarted -> OrderState.Processing.PaymentProcessing
                is OrderEvent.PaymentFailed -> OrderState.Processing.PaymentFailed(event.reason)
                else -> null
            }

            is OrderState.Processing.PaymentProcessing -> when (event) {
                is OrderEvent.PaymentSucceeded -> OrderState.Completed(event.orderId)
                is OrderEvent.PaymentFailed -> OrderState.Processing.PaymentFailed(event.reason)
                else -> null
            }

            is OrderState.Processing.PaymentFailed -> when (event) {
                is OrderEvent.Retry -> OrderState.Processing.PaymentPending
                is OrderEvent.Cancel -> OrderState.Cancelled("Payment failed")
                else -> null
            }

            is OrderState.Completed,
            is OrderState.Cancelled -> null // Терминальные состояния
        }
    }
}
```

### Типобезопасные переходы с Kotlin

```kotlin
// Type-safe transitions с inline functions
class TypeSafeStateMachine<S : Any, E : Any>(
    initialState: S,
    private val transitions: TransitionTable<S, E>
) {
    private val _state = MutableStateFlow(initialState)
    val state: StateFlow<S> = _state.asStateFlow()

    fun transition(event: E): Boolean {
        val currentState = _state.value
        val newState = transitions.getNextState(currentState, event)

        return if (newState != null) {
            _state.value = newState
            true
        } else {
            false
        }
    }
}

class TransitionTable<S : Any, E : Any> {
    private val transitions = mutableMapOf<Pair<KClass<out S>, KClass<out E>>, (S, E) -> S?>()

    inline fun <reified FROM : S, reified ON : E> on(
        noinline action: (FROM, ON) -> S?
    ) {
        @Suppress("UNCHECKED_CAST")
        transitions[FROM::class to ON::class] = action as (S, E) -> S?
    }

    fun getNextState(state: S, event: E): S? {
        val key = state::class to event::class
        val transition = transitions[key] ?: return null
        return transition(state, event)
    }
}

// Использование
val transitions = TransitionTable<AuthState, AuthEvent>().apply {
    on<AuthState.Idle, AuthEvent.Login> { _, _ ->
        AuthState.Loading
    }

    on<AuthState.Loading, AuthEvent.LoginSuccess> { _, event ->
        AuthState.Authenticated(event.user)
    }

    on<AuthState.Loading, AuthEvent.LoginFailed> { _, event ->
        AuthState.Error(event.error)
    }

    on<AuthState.Authenticated, AuthEvent.Logout> { _, _ ->
        AuthState.Idle
    }

    on<AuthState.Error, AuthEvent.Retry> { _, _ ->
        AuthState.Loading
    }
}

val stateMachine = TypeSafeStateMachine(
    initialState = AuthState.Idle,
    transitions = transitions
)
```

### Guards (условия перехода)

```kotlin
// Переходы с условиями
sealed interface FormState {
    data class Editing(val data: FormData, val errors: List<ValidationError>) : FormState
    data object Submitting : FormState
    data class Submitted(val result: SubmitResult) : FormState
}

class FormStateMachine {
    fun reduce(state: FormState, event: FormEvent): FormState? {
        return when (state) {
            is FormState.Editing -> when (event) {
                is FormEvent.Submit -> {
                    // Guard: можно submit только если нет ошибок
                    if (state.errors.isEmpty()) {
                        FormState.Submitting
                    } else {
                        null // Переход запрещен
                    }
                }
                is FormEvent.UpdateField -> {
                    val newData = state.data.update(event.field, event.value)
                    val newErrors = validate(newData)
                    FormState.Editing(newData, newErrors)
                }
                else -> null
            }
            // ...
            else -> null
        }
    }
}
```

### Тестирование FSM

```kotlin
class AuthStateMachineTest {

    private lateinit var stateMachine: AuthStateMachine

    @Before
    fun setup() {
        stateMachine = AuthStateMachine()
    }

    @Test
    fun `initial state is Idle`() {
        assertEquals(AuthState.Idle, stateMachine.state.value)
    }

    @Test
    fun `Login from Idle transitions to Loading`() {
        stateMachine.transition(AuthEvent.Login("test@test.com", "password"))

        assertEquals(AuthState.Loading, stateMachine.state.value)
    }

    @Test
    fun `LoginSuccess from Loading transitions to Authenticated`() {
        val user = User("1", "Test")

        stateMachine.transition(AuthEvent.Login("test@test.com", "password"))
        stateMachine.transition(AuthEvent.LoginSuccess(user))

        assertEquals(AuthState.Authenticated(user), stateMachine.state.value)
    }

    @Test
    fun `Logout from Idle is invalid and state remains unchanged`() {
        stateMachine.transition(AuthEvent.Logout)

        assertEquals(AuthState.Idle, stateMachine.state.value)
    }

    @Test
    fun `Cannot Login while Loading`() {
        stateMachine.transition(AuthEvent.Login("test@test.com", "password"))
        stateMachine.transition(AuthEvent.Login("other@test.com", "pass"))

        assertEquals(AuthState.Loading, stateMachine.state.value)
    }

    @Test
    fun `full login flow`() {
        val user = User("1", "Test")

        // Idle -> Loading
        assertTrue(stateMachine.transition(AuthEvent.Login("test@test.com", "password")))
        assertEquals(AuthState.Loading, stateMachine.state.value)

        // Loading -> Authenticated
        assertTrue(stateMachine.transition(AuthEvent.LoginSuccess(user)))
        assertEquals(AuthState.Authenticated(user), stateMachine.state.value)

        // Authenticated -> Idle
        assertTrue(stateMachine.transition(AuthEvent.Logout))
        assertEquals(AuthState.Idle, stateMachine.state.value)
    }
}
```

---

## Answer (EN)

**Finite State Machine (FSM)** is a model where a system can be in one of a finite number of states, and transitions between states occur on specific events with validation.

### Why FSM for UI?

| Problem without FSM | Solution with FSM |
|---------------------|-------------------|
| Invalid states (`isLoading && hasError`) | Only valid states |
| Complex `if/else` logic | Declarative transitions |
| Bugs from race conditions | Transition validation |
| Hard to debug | Visualization and logging |

### Basic FSM Structure

```kotlin
// States - sealed class guarantees exhaustive when
sealed interface AuthState {
    data object Idle : AuthState
    data object Loading : AuthState
    data class Authenticated(val user: User) : AuthState
    data class Error(val message: String) : AuthState
}

// Events
sealed interface AuthEvent {
    data class Login(val email: String, val password: String) : AuthEvent
    data object Logout : AuthEvent
    data object Retry : AuthEvent
    data class LoginSuccess(val user: User) : AuthEvent
    data class LoginFailed(val error: String) : AuthEvent
}

// State Machine with transition validation
class AuthStateMachine {
    private val _state = MutableStateFlow<AuthState>(AuthState.Idle)
    val state: StateFlow<AuthState> = _state.asStateFlow()

    fun transition(event: AuthEvent): Boolean {
        val currentState = _state.value
        val newState = reduce(currentState, event)

        return if (newState != null) {
            _state.value = newState
            true
        } else {
            Log.w("FSM", "Invalid transition: $currentState + $event")
            false
        }
    }

    // Reducer with transition validation
    private fun reduce(state: AuthState, event: AuthEvent): AuthState? {
        return when (state) {
            is AuthState.Idle -> when (event) {
                is AuthEvent.Login -> AuthState.Loading
                else -> null  // Only Login allowed from Idle
            }

            is AuthState.Loading -> when (event) {
                is AuthEvent.LoginSuccess -> AuthState.Authenticated(event.user)
                is AuthEvent.LoginFailed -> AuthState.Error(event.error)
                else -> null  // Cannot Login or Logout while Loading
            }

            is AuthState.Authenticated -> when (event) {
                is AuthEvent.Logout -> AuthState.Idle
                else -> null  // Only Logout from Authenticated
            }

            is AuthState.Error -> when (event) {
                is AuthEvent.Retry -> AuthState.Loading
                is AuthEvent.Login -> AuthState.Loading
                else -> null
            }
        }
    }
}
```

### Transition Diagram

```text
          Login
    +----[Login]---->+
    |                |
    v                |
  Idle               |
    ^                v
    |             Loading
    |    Success/   |    \Failure
    |      /        |     \
 Logout   v         |      v
    |  Authenticated|     Error
    |       |       |       |
    +-------+       +--[Retry]-+
```

### Hierarchical States

```kotlin
// Hierarchical state with substates
sealed interface OrderState {
    data object Draft : OrderState

    sealed interface Checkout : OrderState {
        data object EnteringAddress : Checkout
        data object SelectingPayment : Checkout
        data object Confirming : Checkout
    }

    sealed interface Processing : OrderState {
        data object PaymentPending : Processing
        data object PaymentProcessing : Processing
        data class PaymentFailed(val reason: String) : Processing
    }

    data class Completed(val orderId: String) : OrderState
    data class Cancelled(val reason: String) : OrderState
}
```

### Guards (Transition Conditions)

```kotlin
// Transitions with guards
fun reduce(state: FormState, event: FormEvent): FormState? {
    return when (state) {
        is FormState.Editing -> when (event) {
            is FormEvent.Submit -> {
                // Guard: can only submit if no errors
                if (state.errors.isEmpty()) {
                    FormState.Submitting
                } else {
                    null // Transition not allowed
                }
            }
            // ...
        }
        else -> null
    }
}
```

### Testing FSM

```kotlin
@Test
fun `Cannot Login while Loading`() {
    stateMachine.transition(AuthEvent.Login("test@test.com", "password"))
    val result = stateMachine.transition(AuthEvent.Login("other@test.com", "pass"))

    assertFalse(result)
    assertEquals(AuthState.Loading, stateMachine.state.value)
}
```

---

## Follow-ups

- How do you handle async operations in FSM transitions?
- When should you use FSM vs simple sealed class state?
- How do you visualize and debug complex state machines?
- What are statecharts and how do they extend FSM?

## References

- https://statecharts.dev/
- https://developer.android.com/topic/architecture/ui-layer/stateholders

## Related Questions

### Prerequisites

- [[q-mvi-architecture--android--hard]] - MVI basics
- [[q-unidirectional-data-flow--architecture--medium]] - UDF principles

### Related

- [[q-mvi-pattern--architecture--hard]] - MVI components
- [[q-sealed-classes-state-management--android--medium]] - Sealed classes for state

### Advanced

- [[q-orbit-mvi--architecture--medium]] - Orbit MVI
- [[q-circuit-framework--architecture--medium]] - Circuit by Slack
