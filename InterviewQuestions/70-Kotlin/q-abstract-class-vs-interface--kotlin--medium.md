---
id: 20251005-235006
title: "Abstract Class vs Interface / Абстрактный класс vs интерфейс"
aliases: ["Abstract Class vs Interface", "Абстрактный класс vs интерфейс"]
topic: kotlin
subtopics: [classes, inheritance]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
source: https://kotlinlang.org/docs/interfaces.html
source_note: Official Kotlin documentation on interfaces
status: draft
moc: moc-kotlin
related:
    [
        q-kotlin-contracts-smart-casts--kotlin--hard,
        q-kotlin-init-block--kotlin--easy,
        q-kotlin-generic-function-syntax--programming-languages--easy,
    ]
created: 2025-10-05
updated: 2025-10-05
tags: [kotlin, abstract-class, interface, oop, inheritance, difficulty/medium]
---
# Вопрос (RU)

> В чем разница между абстрактным классом и интерфейсом в Kotlin?

# Question (EN)

> What is the difference between abstract class and interface in Kotlin?

---

## Ответ (RU)

### Интерфейс

Интерфейс — это blueprint класса, который описывает методы, которые класс обязуется реализовать. **Не может хранить состояние** (не может иметь инициализированные свойства), но может содержать реализации методов по умолчанию.

```kotlin
interface Clickable {
    fun click()  // Абстрактный метод
    fun showOff() = println("I'm clickable!")  // Реализация по умолчанию
}
```

### Абстрактный класс

Абстрактный класс **может хранить состояние** (может иметь инициализированные свойства). Это частично определенный класс, где методы и свойства должны быть реализованы подклассами.

```kotlin
abstract class Animated {
    abstract fun animate()  // Должен быть реализован

    open fun stopAnimating() {  // Может быть переопределен
        println("Stopped animating")
    }

    fun animateTwice() {  // Конкретный метод
        animate()
        animate()
    }
}
```

### Ключевые отличия

| Функция                  | Абстрактный класс                                   | Интерфейс                                                 |
| ------------------------ | --------------------------------------------------- | --------------------------------------------------------- |
| **Состояние**            | Может иметь свойства с backing fields               | Может иметь свойства, но без backing fields (Kotlin 1.0+) |
| **Наследование**         | Только одиночное                                    | Множественная реализация                                  |
| **Конструкторы**         | Имеет конструкторы с параметрами                    | Нет конструкторов                                         |
| **Реализация**           | Может предоставить реализацию интерфейса            | Не может предоставить реализацию абстрактного класса      |
| **Расширяет**            | Может расширить один класс + реализовать интерфейсы | Может расширить несколько интерфейсов                     |
| **Модификаторы доступа** | public, protected, private, internal                | public по умолчанию, private доступен (Kotlin 1.4+)       |
| **Свойства**             | Может иметь изменяемое состояние с backing fields   | Только абстрактные свойства или свойства с custom getters |

### Важные особенности Kotlin

**Свойства в интерфейсах:**

```kotlin
interface Named {
    val name: String  // Абстрактное свойство
    val displayName: String
        get() = "User: $name"  // Свойство с custom getter (без backing field)
}

class Person(override val name: String) : Named
// Person("Alice").displayName => "User: Alice"
```

**Интерфейс не может иметь состояние:**

```kotlin
interface Counter {
    var count: Int  // Должно быть переопределено в реализации
}

class MyCounter : Counter {
    override var count: Int = 0  // Реализация с backing field
}
```

**Абстрактный класс с состоянием:**

```kotlin
abstract class Repository {
    private val cache = mutableMapOf<String, Any>()  // Состояние с backing field

    protected fun getCached(key: String): Any? = cache[key]
    protected fun putCached(key: String, value: Any) {
        cache[key] = value
    }

    abstract fun fetch(id: String): Any
}
```

**Множественные интерфейсы vs Абстрактный класс:**

```kotlin
// - Можно реализовать несколько интерфейсов
interface Serializable
interface Comparable<T>
interface Cloneable

class Data : Serializable, Comparable<Data>, Cloneable {
    override fun compareTo(other: Data): Int = 0
    override fun clone(): Any = this
}

// - Можно наследовать только один абстрактный класс
abstract class BaseViewModel
abstract class BaseRepository
// class MyClass : BaseViewModel(), BaseRepository()  // Не скомпилируется
```

### Примеры из Android

**Интерфейс для коллбэков:**

```kotlin
interface OnItemClickListener {
    fun onItemClick(position: Int)
    fun onItemLongClick(position: Int): Boolean = false  // Реализация по умолчанию
}

class MyAdapter : RecyclerView.Adapter<ViewHolder>() {
    var listener: OnItemClickListener? = null
    // ...
}
```

**Абстрактный класс для общего состояния:**

```kotlin
abstract class BaseViewModel : ViewModel() {
    protected val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    protected val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()

    abstract fun loadData()
}

class UserViewModel : BaseViewModel() {
    override fun loadData() {
        _isLoading.value = true
        // Загрузка данных пользователя
        _isLoading.value = false
    }
}
```

### Когда использовать что

**Абстрактный класс:**

-   Делить код между **тесно связанными классами**
-   Классы имеют **много общих методов или полей**
-   Нужны **модификаторы доступа** кроме public (protected, private)
-   Нужно **хранить состояние** (backing fields)

**Интерфейс:**

-   **Несвязанные классы** будут его реализовывать
-   Хотите указать **поведение** не заботясь кто реализует
-   Нужно **множественное наследование типа**
-   Определяете только **контракт** без состояния

**Краткое содержание**: В Kotlin абстрактные классы могут иметь свойства с backing fields и конструкторы, поддерживают одиночное наследование. Интерфейсы могут иметь свойства с custom getters (без backing fields) и поддерживают множественную реализацию. С Kotlin 1.4 интерфейсы могут иметь private члены. Используйте абстрактные классы для тесно связанных классов с общим состоянием и поведением. Используйте интерфейсы для контрактов, множественного наследования или когда нужно определить только поведение без состояния.

## Answer (EN)

### Interface

An interface is a blueprint of a class that describes methods a class agrees to implement. **Cannot hold state** (cannot have initialized properties), but can contain default method implementations.

```kotlin
interface Clickable {
    fun click()  // Abstract method
    fun showOff() = println("I'm clickable!")  // Default implementation
}
```

### Abstract Class

An abstract class **can hold state** (can have initialized properties). It's a partially defined class where methods and properties must be implemented by subclasses.

```kotlin
abstract class Animated {
    abstract fun animate()  // Must be implemented

    open fun stopAnimating() {  // Can be overridden
        println("Stopped animating")
    }

    fun animateTwice() {  // Concrete method
        animate()
        animate()
    }
}
```

### Key Differences

| Feature              | Abstract Class                               | Interface                                                           |
| -------------------- | -------------------------------------------- | ------------------------------------------------------------------- |
| **State**            | Can have properties with backing fields      | Can have properties but no backing fields (Kotlin 1.0+)             |
| **Inheritance**      | Single inheritance only                      | Multiple implementation                                             |
| **Constructors**     | Has constructors with parameters             | No constructors                                                     |
| **Implementation**   | Can provide interface implementation         | Cannot provide abstract class implementation                        |
| **Extends**          | Can extend one class + implement interfaces  | Can extend multiple interfaces                                      |
| **Access modifiers** | Can use public, protected, private, internal | Members are public by default, can be private (Kotlin 1.4+)         |
| **Properties**       | Can have mutable state with backing fields   | Can only have abstract properties or properties with custom getters |

### Important Kotlin-Specific Details

**Interface Properties (Kotlin):**

```kotlin
interface Named {
    val name: String  // Abstract property
    val displayName: String
        get() = "User: $name"  // Property with custom getter (no backing field)
}

class Person(override val name: String) : Named
// Person("Alice").displayName => "User: Alice"
```

**Interface with State-Like Behavior:**

```kotlin
interface Counter {
    var count: Int  // Must be overridden in implementation
}

class MyCounter : Counter {
    override var count: Int = 0  // Implementation with backing field
}
```

**Abstract Class with State:**

```kotlin
abstract class Repository {
    private val cache = mutableMapOf<String, Any>()  // State with backing field

    protected fun getCached(key: String): Any? = cache[key]
    protected fun putCached(key: String, value: Any) {
        cache[key] = value
    }

    abstract fun fetch(id: String): Any
}
```

**Multiple Interfaces vs Abstract Class:**

```kotlin
// - Can implement multiple interfaces
interface Serializable
interface Comparable<T>
interface Cloneable

class Data : Serializable, Comparable<Data>, Cloneable {
    override fun compareTo(other: Data): Int = 0
    override fun clone(): Any = this
}

// - Can only extend one abstract class
abstract class BaseViewModel
abstract class BaseRepository
// class MyClass : BaseViewModel(), BaseRepository()  // Won't compile
```

### Real Android Examples

**Interface for callbacks:**

```kotlin
interface OnItemClickListener {
    fun onItemClick(position: Int)
    fun onItemLongClick(position: Int): Boolean = false  // Default
}

class MyAdapter : RecyclerView.Adapter<ViewHolder>() {
    var listener: OnItemClickListener? = null
    // ...
}
```

**Abstract class for shared state:**

```kotlin
abstract class BaseViewModel : ViewModel() {
    protected val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    protected val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()

    abstract fun loadData()
}

class UserViewModel : BaseViewModel() {
    override fun loadData() {
        _isLoading.value = true
        // Load user data
        _isLoading.value = false
    }
}
```

### When to Use Abstract Class

-   Share code among **closely related classes**
-   Classes have **many common methods or fields**
-   Need **access modifiers** other than public (protected, private)
-   Want to define **non-static, non-final** fields

```kotlin
abstract class Animal(val name: String) {
    protected var age: Int = 0  // State

    abstract fun makeSound()  // Must implement

    fun sleep() {  // Common behavior
        println("$name is sleeping")
    }
}

class Dog(name: String) : Animal(name) {
    override fun makeSound() {
        println("Woof!")
    }
}
```

### When to Use Interface

-   **Unrelated classes** would implement it
-   Want to specify **behavior** without caring who implements it
-   Need **multiple inheritance of type**

```kotlin
interface Comparable<T> {
    fun compareTo(other: T): Int
}

interface Cloneable {
    fun clone(): Any
}

// Any class can implement these
class User : Comparable<User>, Cloneable {
    override fun compareTo(other: User): Int = /* ... */
    override fun clone(): Any = /* ... */
}
```

**Summary**: In Kotlin, abstract classes can have properties with backing fields and constructors, supporting single inheritance. Interfaces can have properties with custom getters (no backing fields) and support multiple implementation. Since Kotlin 1.4, interfaces can have private members. Use abstract classes for closely related classes sharing state and behavior. Use interfaces for contracts, multiple inheritance, or when you only need to define behavior without state.

---

## Follow-ups

-   How do sealed classes differ from abstract classes and interfaces?
-   What are the performance implications of using interfaces vs abstract classes?
-   How do you handle diamond problem with multiple interface inheritance?
-   When should you use composition over inheritance with interfaces?
