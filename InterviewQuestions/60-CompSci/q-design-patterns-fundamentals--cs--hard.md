---
id: cs-037
title: "Design Patterns Fundamentals / Фундаментальные паттерны проектирования"
aliases: ["Design Patterns Fundamentals", "Фундаментальные паттерны проектирования"]
topic: cs
subtopics: [design-patterns, gof-patterns, programming-languages]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [q-design-patterns-types--design-patterns--medium, q-factory-method-pattern--design-patterns--medium, q-singleton-pattern--design-patterns--easy]
created: "2025-10-13"
updated: 2025-01-25
tags: [android, behavioral, creational, design-patterns, difficulty/hard, gof, kotlin, structural]
sources: [https://refactoring.guru/design-patterns]
date created: Monday, October 13th 2025, 8:04:10 am
date modified: Sunday, October 26th 2025, 11:57:28 am
---

# Вопрос (RU)
> Что такое паттерны проектирования? Какие основные категории паттернов существуют и когда их использовать?

# Question (EN)
> What are design patterns? What are the main categories of patterns and when to use them?

---

## Ответ (RU)

**Теория Design Patterns:**
Design Patterns - общие, переиспользуемые решения типовых проблем в объектно-ориентированном проектировании. Gang of Four (GoF) документировали 23 фундаментальных паттерна в 1994 году. Паттерны делятся на 3 категории: Creational (порождающие), Structural (структурные), Behavioral (поведенческие). Паттерны обеспечивают common vocabulary, proven solutions, code reuse, maintainability.

**Три основные категории:**

| Категория | Назначение | Примеры |
|-----------|-----------|---------|
| **Creational** | Создание объектов | Singleton, Factory Method, Builder |
| **Structural** | Композиция объектов | Adapter, Decorator, Facade |
| **Behavioral** | Взаимодействие объектов | Observer, Strategy, Command |

**Creational Patterns:**

*Теория:* Порождающие паттерны управляют созданием объектов. Singleton - единственный instance, Factory Method - создание через методы, Abstract Factory - семейства объектов, Builder - пошаговое построение, Prototype - клонирование. Используются для: управления creation logic, избежания tight coupling с конкретными классами, обеспечения гибкости в создании объектов.

```kotlin
// ✅ Singleton example
object DatabaseManager {
    private var instance: Database? = null

    fun getInstance(): Database {
        if (instance == null) {
            synchronized(this) {
                if (instance == null) {
                    instance = Database.create()
                }
            }
        }
        return instance!!
    }
}

// ✅ Factory Method example
interface NetworkRequest {
    fun execute()
}

class GetRequest : NetworkRequest {
    override fun execute() { /* GET */ }
}

class PostRequest : NetworkRequest {
    override fun execute() { /* POST */ }
}

fun createRequest(method: String): NetworkRequest = when (method) {
    "GET" -> GetRequest()
    "POST" -> PostRequest()
    else -> throw IllegalArgumentException()
}

// ✅ Builder example
class User private constructor(val name: String, val age: Int) {
    class Builder {
    private var name: String = ""
        private var age: Int = 0

    fun name(name: String) = apply { this.name = name }
    fun age(age: Int) = apply { this.age = age }
        fun build() = User(name, age)
    }
}
```

**Structural Patterns:**

*Теория:* Структурные паттерны управляют композицией объектов в более крупные структуры. Adapter - преобразование интерфейса, Decorator - добавление функциональности, Facade - упрощение сложной системы, Proxy - контролируемый доступ, Composite - древовидные структуры. Используются для: работы с legacy code, упрощения сложных интерфейсов, добавления responsibilities без subclassing.

```kotlin
// ✅ Adapter example
interface MediaPlayer {
    fun play(file: String)
}

class VlcPlayer : MediaPlayer {
    override fun play(file: String) { /* play VLC */ }
}

class Mp4Adapter(private val player: Mp4Player) : MediaPlayer {
    override fun play(file: String) {
        player.playMp4(file)  // Adapts interface
    }
}

// ✅ Decorator example
interface Coffee {
    fun cost(): Double
}

class BasicCoffee : Coffee {
    override fun cost() = 2.0
}

class MilkDecorator(private val coffee: Coffee) : Coffee {
    override fun cost() = coffee.cost() + 0.5
}
```

**Behavioral Patterns:**

*Теория:* Поведенческие паттерны управляют взаимодействием объектов. Observer - уведомление зависимостей, Strategy - взаимозаменяемые алгоритмы, Command - инкапсуляция запросов, State - поведение на основе состояния, Template Method - скелет алгоритма. Используются для: гибкой коммуникации, расширяемости алгоритмов, undo/redo functionality, state management.

```kotlin
// ✅ Observer example
class Button {
    private val observers = mutableListOf<() -> Unit>()

    fun addObserver(observer: () -> Unit) {
        observers.add(observer)
    }

    fun click() {
        observers.forEach { it() }
    }
}

// ✅ Strategy example
interface SortStrategy {
    fun sort(list: List<Int>): List<Int>
}

class BubbleSort : SortStrategy {
    override fun sort(list: List<Int>) = /* bubble sort */
}

class QuickSort : SortStrategy {
    override fun sort(list: List<Int>) = /* quick sort */
}

class Sorter(private val strategy: SortStrategy) {
    fun sort(list: List<Int>) = strategy.sort(list)
}
```

**Когда использовать паттерны:**

✅ Когда есть proven solution для данной проблемы
✅ Когда нужна flexibility и extensibility
✅ Когда код нуждается в refactoring
✅ Когда команда использует common vocabulary

❌ Не использовать для простых случаев без необходимости
❌ Не переусложнять architecture паттернами
❌ Не применять без понимания trade-offs

**Modern Android альтернативы:**

*Теория:* Современные подходы в Android: Dependency Injection (Hilt/Dagger) вместо Singleton, StateFlow/SharedFlow вместо classic Observer, Sealed classes для State pattern, Coroutines для async patterns. Эти подходы более idiomatic для Kotlin и Android.

```kotlin
// ✅ Modern: Dependency Injection
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Singleton
    fun provideApiService(): ApiService = Retrofit.Builder()
        .baseUrl("https://api.example.com")
        .build()
        .create(ApiService::class.java)
}

// ✅ Modern: StateFlow вместо Observer
class ViewModel : ViewModel() {
    private val _state = MutableStateFlow<UiState>(UiState.Loading)
    val state: StateFlow<UiState> = _state.asStateFlow()

    fun updateState(newState: UiState) {
        _state.value = newState
    }
}

// ✅ Modern: Sealed classes для State pattern
sealed class UiState {
    object Loading : UiState()
    data class Success(val data: List<Item>) : UiState()
    data class Error(val message: String) : UiState()
}
```

**Ключевые концепции:**

1. **Common Vocabulary** - паттерны дают общий язык команде
2. **Proven Solutions** - проверенные временем решения
3. **Flexibility** - паттерны обеспечивают flexibility
4. **Maintainability** - код становится более maintainable
5. **Modern Alternatives** - использовать Kotlin/Android idiom совместимые подходы

## Answer (EN)

**Design Patterns Theory:**
Design Patterns - general, reusable solutions to typical problems in object-oriented design. Gang of Four (GoF) documented 23 fundamental patterns in 1994. Patterns divided into 3 categories: Creational, Structural, Behavioral. Patterns provide common vocabulary, proven solutions, code reuse, maintainability.

**Three Main Categories:**

| Category | Purpose | Examples |
|----------|---------|----------|
| **Creational** | Object creation | Singleton, Factory Method, Builder |
| **Structural** | Object composition | Adapter, Decorator, Facade |
| **Behavioral** | Object interaction | Observer, Strategy, Command |

**Creational Patterns:**

*Theory:* Creational patterns manage object creation. Singleton - single instance, Factory Method - creation through methods, Abstract Factory - object families, Builder - step-by-step construction, Prototype - cloning. Used for: managing creation logic, avoiding tight coupling with concrete classes, ensuring flexibility in object creation.

```kotlin
// ✅ Singleton example
object DatabaseManager {
    private var instance: Database? = null

    fun getInstance(): Database {
        if (instance == null) {
            synchronized(this) {
                if (instance == null) {
                    instance = Database.create()
                }
            }
        }
        return instance!!
    }
}

// ✅ Factory Method example
interface NetworkRequest {
    fun execute()
}

class GetRequest : NetworkRequest {
    override fun execute() { /* GET */ }
}

class PostRequest : NetworkRequest {
    override fun execute() { /* POST */ }
}

fun createRequest(method: String): NetworkRequest = when (method) {
    "GET" -> GetRequest()
    "POST" -> PostRequest()
    else -> throw IllegalArgumentException()
}

// ✅ Builder example
class User private constructor(val name: String, val age: Int) {
    class Builder {
        private var name: String = ""
        private var age: Int = 0

        fun name(name: String) = apply { this.name = name }
        fun age(age: Int) = apply { this.age = age }
        fun build() = User(name, age)
    }
}
```

**Structural Patterns:**

*Theory:* Structural patterns manage object composition into larger structures. Adapter - interface transformation, Decorator - adding functionality, Facade - simplifying complex system, Proxy - controlled access, Composite - tree structures. Used for: working with legacy code, simplifying complex interfaces, adding responsibilities without subclassing.

```kotlin
// ✅ Adapter example
interface MediaPlayer {
    fun play(file: String)
}

class VlcPlayer : MediaPlayer {
    override fun play(file: String) { /* play VLC */ }
}

class Mp4Adapter(private val player: Mp4Player) : MediaPlayer {
    override fun play(file: String) {
        player.playMp4(file)  // Adapts interface
    }
}

// ✅ Decorator example
interface Coffee {
    fun cost(): Double
}

class BasicCoffee : Coffee {
    override fun cost() = 2.0
}

class MilkDecorator(private val coffee: Coffee) : Coffee {
    override fun cost() = coffee.cost() + 0.5
}
```

**Behavioral Patterns:**

*Theory:* Behavioral patterns manage object interaction. Observer - dependency notification, Strategy - interchangeable algorithms, Command - request encapsulation, State - behavior based on state, Template Method - algorithm skeleton. Used for: flexible communication, algorithm extensibility, undo/redo functionality, state management.

```kotlin
// ✅ Observer example
class Button {
    private val observers = mutableListOf<() -> Unit>()

    fun addObserver(observer: () -> Unit) {
        observers.add(observer)
    }

    fun click() {
        observers.forEach { it() }
    }
}

// ✅ Strategy example
interface SortStrategy {
    fun sort(list: List<Int>): List<Int>
}

class BubbleSort : SortStrategy {
    override fun sort(list: List<Int>) = /* bubble sort */
}

class QuickSort : SortStrategy {
    override fun sort(list: List<Int>) = /* quick sort */
}

class Sorter(private val strategy: SortStrategy) {
    fun sort(list: List<Int>) = strategy.sort(list)
}
```

**When to Use Patterns:**

✅ When there's proven solution for given problem
✅ When need flexibility and extensibility
✅ When code needs refactoring
✅ When team uses common vocabulary

❌ Don't use for simple cases without need
❌ Don't overcomplicate architecture with patterns
❌ Don't apply without understanding trade-offs

**Modern Android Alternatives:**

*Theory:* Modern approaches in Android: Dependency Injection (Hilt/Dagger) instead of Singleton, StateFlow/SharedFlow instead of classic Observer, Sealed classes for State pattern, Coroutines for async patterns. These approaches more idiomatic for Kotlin and Android.

```kotlin
// ✅ Modern: Dependency Injection
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Singleton
    fun provideApiService(): ApiService = Retrofit.Builder()
        .baseUrl("https://api.example.com")
        .build()
        .create(ApiService::class.java)
}

// ✅ Modern: StateFlow instead of Observer
class ViewModel : ViewModel() {
    private val _state = MutableStateFlow<UiState>(UiState.Loading)
    val state: StateFlow<UiState> = _state.asStateFlow()

    fun updateState(newState: UiState) {
        _state.value = newState
    }
}

// ✅ Modern: Sealed classes for State pattern
sealed class UiState {
    object Loading : UiState()
    data class Success(val data: List<Item>) : UiState()
    data class Error(val message: String) : UiState()
}
```

**Key Concepts:**

1. **Common Vocabulary** - patterns provide common team language
2. **Proven Solutions** - time-tested solutions
3. **Flexibility** - patterns ensure flexibility
4. **Maintainability** - code becomes more maintainable
5. **Modern Alternatives** - use Kotlin/Android idiomatic approaches

---

## Follow-ups

- When should you prefer composition over inheritance?
- What are the modern alternatives to classic GoF patterns?
- How do StateFlow/SharedFlow relate to Observer pattern?

## Related Questions

### Overview
- [[q-design-patterns-types--design-patterns--medium]] - Pattern categories

### Creational Patterns
- [[q-singleton-pattern--design-patterns--easy]] - Singleton
- [[q-factory-method-pattern--design-patterns--medium]] - Factory Method
- [[q-abstract-factory-pattern--design-patterns--medium]] - Abstract Factory
- [[q-builder-pattern--design-patterns--medium]] - Builder
- [[q-prototype-pattern--design-patterns--medium]] - Prototype

### Structural Patterns
- [[q-adapter-pattern--design-patterns--medium]] - Adapter
- [[q-decorator-pattern--design-patterns--medium]] - Decorator
- [[q-facade-pattern--design-patterns--medium]] - Facade
- [[q-proxy-pattern--design-patterns--medium]] - Proxy
- [[q-composite-pattern--design-patterns--medium]] - Composite

### Behavioral Patterns
- [[q-observer-pattern--design-patterns--medium]] - Observer
- [[q-strategy-pattern--design-patterns--medium]] - Strategy
- [[q-command-pattern--design-patterns--medium]] - Command
- [[q-state-pattern--design-patterns--medium]] - State
- [[q-template-method-pattern--design-patterns--medium]] - Template Method
- [[q-iterator-pattern--design-patterns--medium]] - Iterator
- [[q-mediator-pattern--design-patterns--medium]] - Mediator
- [[q-memento-pattern--design-patterns--medium]] - Memento

### Advanced Patterns
- [[q-bridge-pattern--design-patterns--hard]] - Bridge
- [[q-visitor-pattern--design-patterns--hard]] - Visitor
- [[q-flyweight-pattern--design-patterns--hard]] - Flyweight
