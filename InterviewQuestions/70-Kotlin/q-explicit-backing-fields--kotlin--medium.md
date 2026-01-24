---
anki_cards:
- slug: q-explicit-backing-fields--kotlin--medium-0-en
  language: en
  anki_id: 1769173395409
  synced_at: '2026-01-23T17:03:50.991040'
- slug: q-explicit-backing-fields--kotlin--medium-0-ru
  language: ru
  anki_id: 1769173395435
  synced_at: '2026-01-23T17:03:50.993669'
---
# Вопрос (RU)
> Объясните явные backing fields в Kotlin. Как они помогают с инкапсуляцией?

# Question (EN)
> Explain explicit backing fields in Kotlin. How do they help with encapsulation?

## Ответ (RU)

**Экспериментальная фича с Kotlin 2.0, развивается в 2.3**

**Explicit backing fields** позволяют объявить backing field свойства с другим типом, чем само свойство. Это улучшает инкапсуляцию без необходимости создавать отдельное приватное свойство.

---

### Синтаксис

```kotlin
class Counter {
    val count: Int
        field = 0  // backing field с явным типом
        get() = field

    fun increment() {
        field++  // прямой доступ к backing field
    }
}
```

---

### Проблема без explicit backing fields

**Типичный паттерн с MutableStateFlow:**

```kotlin
class ViewModel {
    // Нужно два свойства для разных типов
    private val _state = MutableStateFlow(0)
    val state: StateFlow<Int> = _state.asStateFlow()

    fun update(value: Int) {
        _state.value = value
    }
}
```

**Проблемы:**
- Дублирование (два свойства для одного состояния)
- Возможность ошибки (забыть обновить публичное свойство)
- Загромождение кода

---

### Решение с explicit backing fields

```kotlin
class ViewModel {
    val state: StateFlow<Int>
        field = MutableStateFlow(0)  // приватный MutableStateFlow
        get() = field.asStateFlow()

    fun update(value: Int) {
        field.value = value  // доступ к mutable версии
    }
}
```

---

### Практические примеры

**Неизменяемая коллекция снаружи:**

```kotlin
class Repository {
    val items: List<Item>
        field = mutableListOf()
        get() = field.toList()  // копия для безопасности

    fun addItem(item: Item) {
        field.add(item)
    }

    fun removeItem(item: Item) {
        field.remove(item)
    }
}
```

**Ленивая инициализация с доступом:**

```kotlin
class Service {
    val connection: Connection
        field: Connection? = null
        get() = field ?: createConnection().also { field = it }

    private fun createConnection(): Connection {
        return Connection()
    }
}
```

**Валидация при записи:**

```kotlin
class User {
    var email: String
        field = ""
        get() = field
        set(value) {
            require(value.contains("@")) { "Invalid email" }
            field = value
        }
}
```

---

### StateFlow паттерн (главный use case)

```kotlin
// До: два свойства
class OldViewModel {
    private val _uiState = MutableStateFlow(UiState.Initial)
    val uiState: StateFlow<UiState> = _uiState

    fun load() {
        _uiState.value = UiState.Loading
    }
}

// После: одно свойство
class NewViewModel {
    val uiState: StateFlow<UiState>
        field = MutableStateFlow(UiState.Initial)
        get() = field

    fun load() {
        field.value = UiState.Loading
    }
}
```

---

### Типобезопасность

```kotlin
class Container {
    val items: List<String>
        field: MutableList<String> = mutableListOf()
        get() = field  // автоматическое приведение к List

    fun add(item: String) {
        field.add(item)  // field имеет тип MutableList
    }

    // Снаружи:
    // val container = Container()
    // container.items.add("x")  // Compile error: List не имеет add
}
```

---

### Включение функции

```kotlin
// build.gradle.kts
kotlin {
    compilerOptions {
        freeCompilerArgs.add("-Xexplicit-backing-fields")
    }
}
```

---

### Ограничения

- Только для свойств с backing field (не для делегированных)
- Тип field должен быть совместим с типом свойства
- Пока экспериментальная фича

```kotlin
// Работает: MutableList -> List
val list: List<Int>
    field: MutableList<Int> = mutableListOf()

// Работает: MutableStateFlow -> StateFlow
val flow: StateFlow<Int>
    field: MutableStateFlow<Int> = MutableStateFlow(0)

// НЕ работает: несовместимые типы
// val value: String
//     field: Int = 0  // Compile error
```

---

### Сравнение подходов

| Подход | Код | Инкапсуляция |
|--------|-----|--------------|
| Два свойства | `_state` + `state` | Хорошая, но громоздко |
| Одно mutable | `var state` | Плохая (можно изменить снаружи) |
| Explicit backing field | `val state` + `field` | Хорошая и чисто |

---

## Answer (EN)

**Experimental since Kotlin 2.0, evolving in 2.3**

**Explicit backing fields** allow declaring a property's backing field with a different type than the property itself. This improves encapsulation without needing a separate private property.

---

### Syntax

```kotlin
class Counter {
    val count: Int
        field = 0  // backing field with explicit type
        get() = field

    fun increment() {
        field++  // direct access to backing field
    }
}
```

---

### Problem Without Explicit Backing Fields

**Typical MutableStateFlow pattern:**

```kotlin
class ViewModel {
    // Need two properties for different types
    private val _state = MutableStateFlow(0)
    val state: StateFlow<Int> = _state.asStateFlow()

    fun update(value: Int) {
        _state.value = value
    }
}
```

**Problems:**
- Duplication (two properties for one state)
- Error-prone (forgetting to update public property)
- Code clutter

---

### Solution with Explicit Backing Fields

```kotlin
class ViewModel {
    val state: StateFlow<Int>
        field = MutableStateFlow(0)  // private MutableStateFlow
        get() = field.asStateFlow()

    fun update(value: Int) {
        field.value = value  // access mutable version
    }
}
```

---

### Practical Examples

**Immutable Collection Externally:**

```kotlin
class Repository {
    val items: List<Item>
        field = mutableListOf()
        get() = field.toList()  // copy for safety

    fun addItem(item: Item) {
        field.add(item)
    }

    fun removeItem(item: Item) {
        field.remove(item)
    }
}
```

**Lazy Initialization with Access:**

```kotlin
class Service {
    val connection: Connection
        field: Connection? = null
        get() = field ?: createConnection().also { field = it }

    private fun createConnection(): Connection {
        return Connection()
    }
}
```

**Validation on Write:**

```kotlin
class User {
    var email: String
        field = ""
        get() = field
        set(value) {
            require(value.contains("@")) { "Invalid email" }
            field = value
        }
}
```

---

### StateFlow Pattern (Main Use Case)

```kotlin
// Before: two properties
class OldViewModel {
    private val _uiState = MutableStateFlow(UiState.Initial)
    val uiState: StateFlow<UiState> = _uiState

    fun load() {
        _uiState.value = UiState.Loading
    }
}

// After: one property
class NewViewModel {
    val uiState: StateFlow<UiState>
        field = MutableStateFlow(UiState.Initial)
        get() = field

    fun load() {
        field.value = UiState.Loading
    }
}
```

---

### Type Safety

```kotlin
class Container {
    val items: List<String>
        field: MutableList<String> = mutableListOf()
        get() = field  // automatic cast to List

    fun add(item: String) {
        field.add(item)  // field has type MutableList
    }

    // From outside:
    // val container = Container()
    // container.items.add("x")  // Compile error: List has no add
}
```

---

### Enabling the Feature

```kotlin
// build.gradle.kts
kotlin {
    compilerOptions {
        freeCompilerArgs.add("-Xexplicit-backing-fields")
    }
}
```

---

### Limitations

- Only for properties with backing field (not delegated)
- Field type must be compatible with property type
- Still an experimental feature

```kotlin
// Works: MutableList -> List
val list: List<Int>
    field: MutableList<Int> = mutableListOf()

// Works: MutableStateFlow -> StateFlow
val flow: StateFlow<Int>
    field: MutableStateFlow<Int> = MutableStateFlow(0)

// Does NOT work: incompatible types
// val value: String
//     field: Int = 0  // Compile error
```

---

### Approach Comparison

| Approach | Code | Encapsulation |
|----------|------|---------------|
| Two properties | `_state` + `state` | Good but verbose |
| Single mutable | `var state` | Poor (modifiable externally) |
| Explicit backing field | `val state` + `field` | Good and clean |

---

## Follow-ups

- When will explicit backing fields become stable?
- Can you use explicit backing fields with delegated properties?
- How does this interact with Kotlin/JS and Kotlin/Native?

## Related Questions

- [[q-kotlin-properties--kotlin--easy]]
- [[q-stateflow-purpose--kotlin--medium]]

## References

- https://github.com/Kotlin/KEEP/blob/master/proposals/explicit-backing-fields.md
- https://kotlinlang.org/docs/properties.html
