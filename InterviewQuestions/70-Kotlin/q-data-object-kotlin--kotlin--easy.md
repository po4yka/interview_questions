---
anki_cards:
- slug: q-data-object-kotlin--kotlin--easy-0-en
  language: en
  anki_id: 1769173428060
  synced_at: '2026-01-23T17:03:51.690526'
- slug: q-data-object-kotlin--kotlin--easy-0-ru
  language: ru
  anki_id: 1769173428084
  synced_at: '2026-01-23T17:03:51.691414'
---
# Вопрос (RU)
> Что такое data object в Kotlin? Чем он отличается от обычного object и data class?

# Question (EN)
> What is a data object in Kotlin? How does it differ from a regular object and data class?

## Ответ (RU)

**Введено в Kotlin 1.9, стабильно**

**Data object** - это объект с автоматически генерируемыми методами `toString()`, `equals()` и `hashCode()`. Полезен для синглтонов в sealed-иерархиях, где нужно читаемое строковое представление.

---

### Синтаксис

```kotlin
data object MySingleton {
    val property = "value"
}
```

---

### Сравнение: object vs data class vs data object

| Характеристика | `object` | `data class` | `data object` |
|---------------|----------|--------------|---------------|
| Экземпляров | 1 (синглтон) | Много | 1 (синглтон) |
| `toString()` | `ClassName@hash` | `ClassName(props)` | `ClassName` |
| `equals()` | По ссылке | По свойствам | По ссылке |
| `hashCode()` | Стандартный | По свойствам | Константный |
| `copy()` | Нет | Да | Нет |
| `componentN()` | Нет | Да | Нет |
| Свойства в конструкторе | Нет | Да | Нет |

---

### Примеры

**Обычный object:**

```kotlin
object RegularObject {
    val name = "Regular"
}

println(RegularObject)  // RegularObject@1a2b3c4d
```

**Data object:**

```kotlin
data object DataSingleton {
    val name = "Data"
}

println(DataSingleton)  // DataSingleton
```

---

### Основное применение: Sealed классы

```kotlin
sealed interface Result<out T> {
    data class Success<T>(val data: T) : Result<T>
    data class Error(val message: String) : Result<Nothing>
    data object Loading : Result<Nothing>
    data object Empty : Result<Nothing>
}

fun displayResult(result: Result<String>) {
    when (result) {
        is Result.Success -> println("Data: ${result.data}")
        is Result.Error -> println("Error: ${result.message}")
        Result.Loading -> println("Loading...")  // чистый toString()
        Result.Empty -> println("No data")
    }
}

// Логирование
val result: Result<String> = Result.Loading
println("Current state: $result")  // Current state: Loading
```

---

### Сравнение с обычным object

**До data object:**

```kotlin
sealed interface State {
    object Idle : State
}

println(State.Idle)  // State$Idle@7a5d012c (нечитаемо)
```

**С data object:**

```kotlin
sealed interface State {
    data object Idle : State
}

println(State.Idle)  // Idle (читаемо)
```

---

### Генерируемые методы

```kotlin
data object AppConfig {
    val version = "1.0"
}

// toString() - возвращает имя класса
println(AppConfig.toString())  // AppConfig

// equals() - сравнение по ссылке (синглтон)
println(AppConfig == AppConfig)  // true
println(AppConfig.equals(AppConfig))  // true

// hashCode() - константное значение
println(AppConfig.hashCode())  // всегда одинаковый
```

---

### Практические примеры

**Состояния UI:**

```kotlin
sealed interface UiState<out T> {
    data object Initial : UiState<Nothing>
    data object Loading : UiState<Nothing>
    data class Content<T>(val data: T) : UiState<T>
    data class Error(val exception: Throwable) : UiState<Nothing>
}

class ViewModel {
    private val _state = MutableStateFlow<UiState<List<Item>>>(UiState.Initial)
    val state: StateFlow<UiState<List<Item>>> = _state

    fun load() {
        _state.value = UiState.Loading
        // ...
    }
}
```

**Команды и события:**

```kotlin
sealed interface Command {
    data object Refresh : Command
    data object Clear : Command
    data class Search(val query: String) : Command
}

fun handleCommand(command: Command) {
    println("Handling: $command")
    // Handling: Refresh  (читаемо, без хеша)
}
```

**Конфигурации:**

```kotlin
sealed interface Environment {
    data object Development : Environment {
        val apiUrl = "https://dev.api.com"
        val debug = true
    }
    data object Production : Environment {
        val apiUrl = "https://api.com"
        val debug = false
    }
}
```

---

### Ограничения

- Нельзя объявлять свойства в первичном конструкторе (его нет)
- Нет `copy()` (синглтон, копировать некуда)
- Нет `componentN()` (нет свойств конструктора)

```kotlin
// Ошибка: у data object нет первичного конструктора
// data object Invalid(val x: Int)  // Compile error
```

---

## Answer (EN)

**Introduced in Kotlin 1.9, stable**

**Data object** is an object with automatically generated `toString()`, `equals()`, and `hashCode()` methods. Useful for singletons in sealed hierarchies where readable string representation is needed.

---

### Syntax

```kotlin
data object MySingleton {
    val property = "value"
}
```

---

### Comparison: object vs data class vs data object

| Feature | `object` | `data class` | `data object` |
|---------|----------|--------------|---------------|
| Instances | 1 (singleton) | Many | 1 (singleton) |
| `toString()` | `ClassName@hash` | `ClassName(props)` | `ClassName` |
| `equals()` | By reference | By properties | By reference |
| `hashCode()` | Standard | By properties | Constant |
| `copy()` | No | Yes | No |
| `componentN()` | No | Yes | No |
| Constructor properties | No | Yes | No |

---

### Examples

**Regular object:**

```kotlin
object RegularObject {
    val name = "Regular"
}

println(RegularObject)  // RegularObject@1a2b3c4d
```

**Data object:**

```kotlin
data object DataSingleton {
    val name = "Data"
}

println(DataSingleton)  // DataSingleton
```

---

### Primary Use Case: Sealed Classes

```kotlin
sealed interface Result<out T> {
    data class Success<T>(val data: T) : Result<T>
    data class Error(val message: String) : Result<Nothing>
    data object Loading : Result<Nothing>
    data object Empty : Result<Nothing>
}

fun displayResult(result: Result<String>) {
    when (result) {
        is Result.Success -> println("Data: ${result.data}")
        is Result.Error -> println("Error: ${result.message}")
        Result.Loading -> println("Loading...")  // clean toString()
        Result.Empty -> println("No data")
    }
}

// Logging
val result: Result<String> = Result.Loading
println("Current state: $result")  // Current state: Loading
```

---

### Comparison with Regular Object

**Before data object:**

```kotlin
sealed interface State {
    object Idle : State
}

println(State.Idle)  // State$Idle@7a5d012c (unreadable)
```

**With data object:**

```kotlin
sealed interface State {
    data object Idle : State
}

println(State.Idle)  // Idle (readable)
```

---

### Generated Methods

```kotlin
data object AppConfig {
    val version = "1.0"
}

// toString() - returns class name
println(AppConfig.toString())  // AppConfig

// equals() - reference comparison (singleton)
println(AppConfig == AppConfig)  // true
println(AppConfig.equals(AppConfig))  // true

// hashCode() - constant value
println(AppConfig.hashCode())  // always the same
```

---

### Practical Examples

**UI States:**

```kotlin
sealed interface UiState<out T> {
    data object Initial : UiState<Nothing>
    data object Loading : UiState<Nothing>
    data class Content<T>(val data: T) : UiState<T>
    data class Error(val exception: Throwable) : UiState<Nothing>
}

class ViewModel {
    private val _state = MutableStateFlow<UiState<List<Item>>>(UiState.Initial)
    val state: StateFlow<UiState<List<Item>>> = _state

    fun load() {
        _state.value = UiState.Loading
        // ...
    }
}
```

**Commands and Events:**

```kotlin
sealed interface Command {
    data object Refresh : Command
    data object Clear : Command
    data class Search(val query: String) : Command
}

fun handleCommand(command: Command) {
    println("Handling: $command")
    // Handling: Refresh  (readable, no hash)
}
```

**Configurations:**

```kotlin
sealed interface Environment {
    data object Development : Environment {
        val apiUrl = "https://dev.api.com"
        val debug = true
    }
    data object Production : Environment {
        val apiUrl = "https://api.com"
        val debug = false
    }
}
```

---

### Limitations

- Cannot declare properties in primary constructor (there is none)
- No `copy()` (singleton, nothing to copy)
- No `componentN()` (no constructor properties)

```kotlin
// Error: data object has no primary constructor
// data object Invalid(val x: Int)  // Compile error
```

---

## Follow-ups

- When should you prefer data object over sealed class with object?
- Can data object have companion objects?
- How does data object interact with serialization?

## Related Questions

- [[q-sealed-classes--kotlin--medium]]
- [[q-object-companion-object--kotlin--medium]]
- [[q-describe-data-sealed-classes--kotlin--medium]]

## References

- https://kotlinlang.org/docs/object-declarations.html#data-objects
- https://kotlinlang.org/docs/sealed-classes.html
