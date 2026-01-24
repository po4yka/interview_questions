---
anki_cards:
- slug: q-context-sensitive-resolution--kotlin--medium-0-en
  language: en
  anki_id: 1769173424959
  synced_at: '2026-01-23T17:03:51.653136'
- slug: q-context-sensitive-resolution--kotlin--medium-0-ru
  language: ru
  anki_id: 1769173424984
  synced_at: '2026-01-23T17:03:51.653969'
---
# Вопрос (RU)
> Объясните context-sensitive resolution в Kotlin. Как это упрощает код с enum и sealed классами?

# Question (EN)
> Explain context-sensitive resolution in Kotlin. How does it simplify code with enums and sealed classes?

## Ответ (RU)

**Preview с Kotlin 2.2**

**Context-sensitive resolution** позволяет опускать имя типа при обращении к членам enum, sealed class или объектам-компаньонам, когда компилятор может однозначно определить тип из контекста.

---

### Синтаксис

```kotlin
enum class Color { RED, GREEN, BLUE }

// До: полное имя
val color: Color = Color.RED

// После: имя типа опускается
val color: Color = .RED
```

---

### Enums

**До context-sensitive resolution:**

```kotlin
enum class State { IDLE, LOADING, SUCCESS, ERROR }

fun updateState(state: State) { ... }

// Нужно повторять имя enum
updateState(State.LOADING)
when (currentState) {
    State.IDLE -> ...
    State.LOADING -> ...
    State.SUCCESS -> ...
    State.ERROR -> ...
}
```

**С context-sensitive resolution:**

```kotlin
// Компилятор знает ожидаемый тип
updateState(.LOADING)

when (currentState) {
    .IDLE -> handleIdle()
    .LOADING -> showProgress()
    .SUCCESS -> showData()
    .ERROR -> showError()
}
```

---

### Sealed classes

```kotlin
sealed interface UiState {
    data object Loading : UiState
    data class Success(val data: String) : UiState
    data class Error(val message: String) : UiState
}

// До
val state: UiState = UiState.Loading

// После
val state: UiState = .Loading

// В when
fun render(state: UiState) = when (state) {
    .Loading -> showLoader()
    is .Success -> showData(state.data)
    is .Error -> showError(state.message)
}
```

---

### Companion objects

```kotlin
class Factory {
    companion object {
        fun create(): Factory = Factory()
        val DEFAULT = Factory()
    }
}

// До
val factory = Factory.Companion.create()
val default = Factory.DEFAULT

// После
val factory: Factory = .create()
val default: Factory = .DEFAULT
```

---

### Практические примеры

**UI State Machine:**

```kotlin
sealed interface ViewState {
    data object Initial : ViewState
    data object Loading : ViewState
    data class Content(val items: List<Item>) : ViewState
    data class Error(val e: Throwable) : ViewState
}

class ViewModel {
    private val _state = MutableStateFlow<ViewState>(.Initial)

    fun load() {
        _state.value = .Loading
        viewModelScope.launch {
            try {
                val items = repository.getItems()
                _state.value = .Content(items)
            } catch (e: Exception) {
                _state.value = .Error(e)
            }
        }
    }
}
```

**Builder pattern:**

```kotlin
enum class Alignment { START, CENTER, END }
enum class Size { SMALL, MEDIUM, LARGE }

class ButtonStyle(
    val alignment: Alignment,
    val size: Size
)

// Чище без повторения имен
val style = ButtonStyle(
    alignment = .CENTER,
    size = .LARGE
)
```

**When expressions:**

```kotlin
enum class HttpMethod { GET, POST, PUT, DELETE }

fun handleRequest(method: HttpMethod) = when (method) {
    .GET -> fetchData()
    .POST -> createResource()
    .PUT -> updateResource()
    .DELETE -> deleteResource()
}
```

---

### Где работает

| Контекст | Пример |
|----------|--------|
| Объявление переменной | `val x: Color = .RED` |
| Параметры функции | `paint(.RED)` |
| Return statement | `return .SUCCESS` |
| When branches | `when (x) { .A -> ... }` |
| Коллекции | `listOf(.A, .B)` |

---

### Где НЕ работает

```kotlin
// Нет контекста типа - не работает
val x = .RED  // Error: не понятно какой enum

// Перегрузка функций - неоднозначно
fun process(c: Color) { ... }
fun process(s: State) { ... }
process(.RED)  // Error: неоднозначный вызов
```

---

### @all мета-аннотация

Kotlin 2.2 также вводит `@all` для применения аннотаций ко всем целям:

```kotlin
// Применяется к property, field, getter, setter
@all:Deprecated("Use newProperty")
var oldProperty: String = ""
```

---

### Включение функции

```kotlin
// build.gradle.kts
kotlin {
    compilerOptions {
        freeCompilerArgs.add("-Xcontext-sensitive-resolution")
    }
}
```

---

### Сравнение с другими языками

| Язык | Синтаксис |
|------|-----------|
| Swift | `.red` (всегда) |
| Kotlin | `.RED` (preview) |
| Java | `Color.RED` (всегда) |
| C# | `Color.Red` (всегда) |

---

## Answer (EN)

**Preview since Kotlin 2.2**

**Context-sensitive resolution** allows omitting the type name when accessing enum members, sealed class subtypes, or companion object members when the compiler can unambiguously determine the type from context.

---

### Syntax

```kotlin
enum class Color { RED, GREEN, BLUE }

// Before: full name
val color: Color = Color.RED

// After: type name omitted
val color: Color = .RED
```

---

### Enums

**Before context-sensitive resolution:**

```kotlin
enum class State { IDLE, LOADING, SUCCESS, ERROR }

fun updateState(state: State) { ... }

// Need to repeat enum name
updateState(State.LOADING)
when (currentState) {
    State.IDLE -> ...
    State.LOADING -> ...
    State.SUCCESS -> ...
    State.ERROR -> ...
}
```

**With context-sensitive resolution:**

```kotlin
// Compiler knows expected type
updateState(.LOADING)

when (currentState) {
    .IDLE -> handleIdle()
    .LOADING -> showProgress()
    .SUCCESS -> showData()
    .ERROR -> showError()
}
```

---

### Sealed Classes

```kotlin
sealed interface UiState {
    data object Loading : UiState
    data class Success(val data: String) : UiState
    data class Error(val message: String) : UiState
}

// Before
val state: UiState = UiState.Loading

// After
val state: UiState = .Loading

// In when
fun render(state: UiState) = when (state) {
    .Loading -> showLoader()
    is .Success -> showData(state.data)
    is .Error -> showError(state.message)
}
```

---

### Companion Objects

```kotlin
class Factory {
    companion object {
        fun create(): Factory = Factory()
        val DEFAULT = Factory()
    }
}

// Before
val factory = Factory.Companion.create()
val default = Factory.DEFAULT

// After
val factory: Factory = .create()
val default: Factory = .DEFAULT
```

---

### Practical Examples

**UI State Machine:**

```kotlin
sealed interface ViewState {
    data object Initial : ViewState
    data object Loading : ViewState
    data class Content(val items: List<Item>) : ViewState
    data class Error(val e: Throwable) : ViewState
}

class ViewModel {
    private val _state = MutableStateFlow<ViewState>(.Initial)

    fun load() {
        _state.value = .Loading
        viewModelScope.launch {
            try {
                val items = repository.getItems()
                _state.value = .Content(items)
            } catch (e: Exception) {
                _state.value = .Error(e)
            }
        }
    }
}
```

**Builder Pattern:**

```kotlin
enum class Alignment { START, CENTER, END }
enum class Size { SMALL, MEDIUM, LARGE }

class ButtonStyle(
    val alignment: Alignment,
    val size: Size
)

// Cleaner without repeating names
val style = ButtonStyle(
    alignment = .CENTER,
    size = .LARGE
)
```

**When Expressions:**

```kotlin
enum class HttpMethod { GET, POST, PUT, DELETE }

fun handleRequest(method: HttpMethod) = when (method) {
    .GET -> fetchData()
    .POST -> createResource()
    .PUT -> updateResource()
    .DELETE -> deleteResource()
}
```

---

### Where It Works

| Context | Example |
|---------|---------|
| Variable declaration | `val x: Color = .RED` |
| Function parameters | `paint(.RED)` |
| Return statement | `return .SUCCESS` |
| When branches | `when (x) { .A -> ... }` |
| Collections | `listOf(.A, .B)` |

---

### Where It Doesn't Work

```kotlin
// No type context - doesn't work
val x = .RED  // Error: unknown enum

// Function overloading - ambiguous
fun process(c: Color) { ... }
fun process(s: State) { ... }
process(.RED)  // Error: ambiguous call
```

---

### @all Meta-Annotation

Kotlin 2.2 also introduces `@all` for applying annotations to all targets:

```kotlin
// Applied to property, field, getter, setter
@all:Deprecated("Use newProperty")
var oldProperty: String = ""
```

---

### Enabling the Feature

```kotlin
// build.gradle.kts
kotlin {
    compilerOptions {
        freeCompilerArgs.add("-Xcontext-sensitive-resolution")
    }
}
```

---

### Comparison with Other Languages

| Language | Syntax |
|----------|--------|
| Swift | `.red` (always) |
| Kotlin | `.RED` (preview) |
| Java | `Color.RED` (always) |
| C# | `Color.Red` (always) |

---

## Follow-ups

- How does context-sensitive resolution interact with IDE autocompletion?
- Can this cause confusion with property access?
- When will this become stable?

## Related Questions

- [[q-sealed-classes--kotlin--medium]]
- [[q-sealed-vs-enum-classes--kotlin--medium]]

## References

- https://kotlinlang.org/docs/whatsnew22.html
- https://github.com/Kotlin/KEEP/issues/384
