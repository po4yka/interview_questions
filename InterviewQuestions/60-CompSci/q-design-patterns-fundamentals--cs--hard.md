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
related: [c-architecture-patterns, c-clean-architecture, c-computer-science]
created: "2025-10-13"
updated: "2025-11-11"
tags: [design-patterns, difficulty/hard, gof]
sources: ["https://refactoring.guru/design-patterns"]

---
# Вопрос (RU)
> Что такое паттерны проектирования? Какие основные категории паттернов существуют и когда их использовать?

# Question (EN)
> What are design patterns? What are the main categories of patterns and when to use them?

---

## Ответ (RU)

**Теория Design Patterns:**
Design Patterns — общие, переиспользуемые решения типовых проблем в объектно-ориентированном проектировании. Gang of Four (GoF) документировали 23 фундаментальных паттерна в 1994 году. Классические GoF-паттерны делятся на 3 категории: Creational (порождающие), Structural (структурные), Behavioral (поведенческие). Паттерны обеспечивают общий словарь, проверенные решения, переиспользование кода, уменьшение связности и улучшение сопровождаемости.

**Три основные категории:**

| Категория | Назначение | Примеры |
|-----------|-----------|---------|
| **Creational** | Создание и инициализация объектов | Singleton, Factory Method, Builder |
| **Structural** | Композиция объектов и структур | Adapter, Decorator, Facade |
| **Behavioral** | Взаимодействие и распределение обязанностей | Observer, Strategy, Command |

**Creational Patterns:**

*Теория:* Порождающие паттерны управляют созданием объектов. Singleton — один глобально доступный экземпляр, Factory Method — создание через фабричные методы, Abstract Factory — создание семейств связанных объектов, Builder — пошаговое построение сложных объектов, Prototype — клонирование. Используются для управления логикой создания, избежания жёсткой связи с конкретными классами и обеспечения гибкости при создании объектов.

```kotlin
// ✅ Idiomatic Kotlin Singleton example
object DatabaseManager {
    fun getConnection(): Database = Database.create()
}

class Database {
    companion object {
        fun create(): Database = Database()
    }
}

// ✅ Factory Method example
interface NetworkRequest {
    fun execute()
}

class GetRequest : NetworkRequest {
    override fun execute() { /* handle GET */ }
}

class PostRequest : NetworkRequest {
    override fun execute() { /* handle POST */ }
}

fun createRequest(method: String): NetworkRequest = when (method) {
    "GET" -> GetRequest()
    "POST" -> PostRequest()
    else -> throw IllegalArgumentException("Unsupported method")
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

*Теория:* Структурные паттерны управляют композицией объектов в более крупные структуры. Adapter — преобразование одного интерфейса в другой, Decorator — динамическое добавление функциональности без изменения исходного класса, Facade — упрощение сложной подсистемы единым интерфейсом, Proxy — контролируемый доступ к объекту, Composite — работа с древовидными структурами как с единым объектом. Используются для работы с legacy-кодом, упрощения сложных интерфейсов, добавления обязанностей без наследования.

```kotlin
// ✅ Adapter example
interface MediaPlayer {
    fun play(file: String)
}

class VlcPlayer : MediaPlayer {
    override fun play(file: String) { /* play VLC file */ }
}

class Mp4Player {
    fun playMp4(file: String) { /* play MP4 file */ }
}

class Mp4Adapter(private val player: Mp4Player) : MediaPlayer {
    override fun play(file: String) {
        player.playMp4(file) // адаптация интерфейса
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

*Теория:* Поведенческие паттерны управляют взаимодействием объектов и распределением обязанностей. Observer — оповещение подписчиков об изменении состояния субъекта, Strategy — взаимозаменяемые алгоритмы под единым интерфейсом, Command — инкапсуляция запроса как объекта, State — изменение поведения в зависимости от текущего состояния, Template Method — задание «скелета» алгоритма с переопределяемыми шагами. Используются для гибкой коммуникации, расширяемости алгоритмов, реализации undo/redo и управления состоянием.

```kotlin
// ✅ Simplified Observer-style example
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
    override fun sort(list: List<Int>): List<Int> = list.sorted() // placeholder
}

class QuickSort : SortStrategy {
    override fun sort(list: List<Int>): List<Int> = list.sorted() // placeholder
}

class Sorter(private val strategy: SortStrategy) {
    fun sort(list: List<Int>): List<Int> = strategy.sort(list)
}
```

**Когда использовать паттерны:**

✅ Когда есть хорошо известное, проверенное решение для данной проблемы
✅ Когда нужна гибкость и расширяемость без жёсткой связности
✅ Когда код требует рефакторинга для улучшения структуры
✅ Когда команда опирается на общий словарь архитектурных решений

❌ Не использовать для тривиальных случаев без необходимости
❌ Не переусложнять архитектуру паттернами
❌ Не применять без понимания trade-offs и контекста

**Современные Android/Kotlin-подходы:**

*Теория:* Современные подходы на Android и в Kotlin: Dependency Injection (Hilt/Dagger) вместо ручного Singleton для зависимостей, `StateFlow`/`SharedFlow` вместо самописного Observer, sealed-классы для выражения состояний (частично решают задачи State/Result-паттернов), корутины для асинхронных задач. Эти подходы более идиоматичны для Kotlin и Android, но концептуально опираются на те же идеи, что и классические паттерны.

```kotlin
// ✅ Modern: Dependency Injection (пример DI контейнера вместо ручного Singleton)
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

interface ApiService

// ✅ Modern: StateFlow вместо самописного Observer
class SampleViewModel : ViewModel() {
    private val _state = MutableStateFlow<UiState>(UiState.Loading)
    val state: StateFlow<UiState> = _state.asStateFlow()

    fun updateState(newState: UiState) {
        _state.value = newState
    }
}

// ✅ Modern: Sealed classes для представления состояний UI
sealed class UiState {
    object Loading : UiState()
    data class Success(val data: List<Item>) : UiState()
    data class Error(val message: String) : UiState()
}

class Item
```

**Ключевые концепции:**

1. **Common Vocabulary** — паттерны дают общий язык команде.
2. **Proven Solutions** — проверенные временем решения повторяющихся задач.
3. **Flexibility & Decoupling** — снижение связности и повышение гибкости.
4. **Maintainability** — код становится проще расширять и сопровождать.
5. **Modern Alternatives** — использовать идиоматичные для Kotlin/Android подходы, сохраняя понимание базовых паттернов.

## Answer (EN)

**Design Patterns Theory:**
Design patterns are general, reusable solutions to typical problems in object-oriented design. The Gang of Four (GoF) documented 23 fundamental patterns in 1994. The classic GoF patterns are grouped into 3 categories: Creational, Structural, and Behavioral. Patterns provide a common vocabulary, proven solutions, code reuse, reduced coupling, and improved maintainability.

**Three Main Categories:**

| Category | Purpose | Examples |
|----------|---------|----------|
| **Creational** | Object creation and initialization | Singleton, Factory Method, Builder |
| **Structural** | Object and structure composition | Adapter, Decorator, Facade |
| **Behavioral** | Object interaction and responsibility distribution | Observer, Strategy, Command |

**Creational Patterns:**

*Theory:* Creational patterns manage object creation. Singleton — a single globally accessible instance, Factory Method — creation via factory methods, Abstract Factory — families of related objects, Builder — step-by-step construction of complex objects, Prototype — cloning. Used for managing creation logic, avoiding tight coupling to concrete classes, and ensuring flexibility in object creation.

```kotlin
// ✅ Idiomatic Kotlin Singleton example
object DatabaseManager {
    fun getConnection(): Database = Database.create()
}

class Database {
    companion object {
        fun create(): Database = Database()
    }
}

// ✅ Factory Method example
interface NetworkRequest {
    fun execute()
}

class GetRequest : NetworkRequest {
    override fun execute() { /* handle GET */ }
}

class PostRequest : NetworkRequest {
    override fun execute() { /* handle POST */ }
}

fun createRequest(method: String): NetworkRequest = when (method) {
    "GET" -> GetRequest()
    "POST" -> PostRequest()
    else -> throw IllegalArgumentException("Unsupported method")
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

*Theory:* Structural patterns manage object composition into larger structures. Adapter — converting one interface to another, Decorator — dynamically adding functionality without modifying the original class, Facade — providing a simplified interface to a complex subsystem, Proxy — controlled access to an object, Composite — treating tree structures uniformly. Used for working with legacy code, simplifying complex interfaces, and adding responsibilities without subclassing.

```kotlin
// ✅ Adapter example
interface MediaPlayer {
    fun play(file: String)
}

class VlcPlayer : MediaPlayer {
    override fun play(file: String) { /* play VLC file */ }
}

class Mp4Player {
    fun playMp4(file: String) { /* play MP4 file */ }
}

class Mp4Adapter(private val player: Mp4Player) : MediaPlayer {
    override fun play(file: String) {
        player.playMp4(file) // adapts interface
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

*Theory:* Behavioral patterns manage object interaction and responsibility distribution. Observer — notifying subscribers about subject state changes, Strategy — interchangeable algorithms under a common interface, Command — encapsulating a request as an object, State — changing behavior based on current state, Template Method — defining the skeleton of an algorithm with overridable steps. Used for flexible communication, algorithm extensibility, undo/redo functionality, and state management.

```kotlin
// ✅ Simplified Observer-style example
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
    override fun sort(list: List<Int>): List<Int> = list.sorted() // placeholder
}

class QuickSort : SortStrategy {
    override fun sort(list: List<Int>): List<Int> = list.sorted() // placeholder
}

class Sorter(private val strategy: SortStrategy) {
    fun sort(list: List<Int>): List<Int> = strategy.sort(list)
}
```

**When to Use Patterns:**

✅ When there is a well-known, proven solution for the given problem
✅ When flexibility and extensibility are needed without tight coupling
✅ When code needs refactoring to improve structure
✅ When the team relies on a shared vocabulary of architectural solutions

❌ Don't use for trivial cases without need
❌ Don't overcomplicate architecture with patterns
❌ Don't apply without understanding trade-offs and context

**Modern Android/Kotlin Approaches:**

*Theory:* Modern approaches in Android and Kotlin: Dependency Injection (Hilt/Dagger) instead of manual singletons for dependencies, `StateFlow`/`SharedFlow` instead of ad-hoc Observer implementations, sealed classes for representing states (partially covering State/Result-like patterns), coroutines for async patterns. These approaches are more idiomatic for Kotlin and Android, while conceptually building on the same underlying design principles.

```kotlin
// ✅ Modern: Dependency Injection (use DI container instead of manual Singleton)
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

interface ApiService

// ✅ Modern: StateFlow instead of custom Observer
class SampleViewModel : ViewModel() {
    private val _state = MutableStateFlow<UiState>(UiState.Loading)
    val state: StateFlow<UiState> = _state.asStateFlow()

    fun updateState(newState: UiState) {
        _state.value = newState
    }
}

// ✅ Modern: Sealed classes for UI state representation
sealed class UiState {
    object Loading : UiState()
    data class Success(val data: List<Item>) : UiState()
    data class Error(val message: String) : UiState()
}

class Item
```

**Key Concepts:**

1. **Common Vocabulary** — patterns provide a shared language for the team.
2. **Proven Solutions** — time-tested solutions to recurring problems.
3. **Flexibility & Decoupling** — reduced coupling and increased flexibility.
4. **Maintainability** — code becomes easier to extend and maintain.
5. **Modern Alternatives** — use idiomatic Kotlin/Android approaches while understanding core pattern concepts.

---

## Дополнительные Вопросы (RU)

- Когда следует предпочесть композицию наследованию?
- Каковы современные альтернативы классическим GoF-паттернам?
- Как `StateFlow`/`SharedFlow` соотносятся с паттерном Observer?

## Follow-ups

- When should you prefer composition over inheritance?
- What are the modern alternatives to classic GoF patterns?
- How do `StateFlow`/`SharedFlow` relate to the Observer pattern?

## Связанные Вопросы (RU)

### Обзор
- [[q-design-patterns-types--cs--medium]] — Категории паттернов

### Порождающие Паттерны
- [[q-singleton-pattern--cs--easy]] — Singleton

### Поведенческие Паттерны
- [[q-strategy-pattern--cs--medium]] — Strategy
- [[q-state-pattern--cs--medium]] — State
- [[q-template-method-pattern--cs--medium]] — Template Method

## Related Questions

### Overview
- [[q-design-patterns-types--cs--medium]] - Pattern categories

### Creational Patterns
- [[q-singleton-pattern--cs--easy]] - Singleton

### Behavioral Patterns
- [[q-strategy-pattern--cs--medium]] - Strategy
- [[q-state-pattern--cs--medium]] - State
- [[q-template-method-pattern--cs--medium]] - Template Method

## References

- [[c-architecture-patterns]]
- [[c-clean-architecture]]
- [[c-computer-science]]
- "https://refactoring.guru/design-patterns"
