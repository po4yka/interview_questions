---
id: "20251025-110310"
title: "Software Design Patterns / Паттерны Проектирования"
aliases: ["Design Patterns", "Software Patterns", "Архитектурные Паттерны", "Паттерны Проектирования"]
summary: "Reusable solutions to common software design problems"
topic: "cs"
subtopics: ["architecture", "design-patterns", "software-engineering"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-cs"
related: []
created: "2025-10-25"
updated: "2025-10-25"
tags: ["architecture", "concept", "design-patterns", "difficulty/medium", "software-engineering"]
---

# Software Design Patterns / Паттерны Проектирования

## Summary (EN)

Design patterns are reusable, proven solutions to common problems that occur in software design. They represent best practices evolved over time and provide a shared vocabulary for developers to communicate design decisions. Patterns are not finished code but templates for how to solve problems in various contexts.

## Краткое Описание (RU)

Паттерны проектирования - это переиспользуемые, проверенные решения общих проблем, возникающих при проектировании программного обеспечения. Они представляют лучшие практики, развившиеся со временем, и обеспечивают общий словарь для разработчиков при обсуждении архитектурных решений. Паттерны - это не готовый код, а шаблоны решения проблем в различных контекстах.

## Key Points (EN)

- **Creational Patterns**: Control object creation mechanisms (Singleton, Factory, Builder)
- **Structural Patterns**: Compose objects and classes into larger structures (Adapter, Decorator, Facade)
- **Behavioral Patterns**: Define communication between objects (Observer, Strategy, Command)
- **Architectural Patterns**: High-level organization of software systems (MVC, MVVM, MVI)
- **Language-agnostic**: Applicable across different programming languages and platforms
- **Not silver bullets**: Must be applied appropriately based on context

## Ключевые Моменты (RU)

- **Порождающие паттерны**: Управляют механизмами создания объектов (Singleton, Factory, Builder)
- **Структурные паттерны**: Компонуют объекты и классы в более крупные структуры (Adapter, Decorator, Facade)
- **Поведенческие паттерны**: Определяют взаимодействие между объектами (Observer, Strategy, Command)
- **Архитектурные паттерны**: Высокоуровневая организация программных систем (MVC, MVVM, MVI)
- **Независимость от языка**: Применимы в различных языках программирования и платформах
- **Не панацея**: Должны применяться соответственно контексту

## Common Patterns in Android Development

### Creational Patterns

**Singleton**
```kotlin
object DatabaseHelper {
    private var instance: Database? = null

    fun getInstance(): Database {
        return instance ?: synchronized(this) {
            instance ?: Database().also { instance = it }
        }
    }
}
```

**Factory**
```kotlin
interface ViewModelFactory {
    fun create(): ViewModel
}

class UserViewModelFactory(private val repository: UserRepository) : ViewModelFactory {
    override fun create(): ViewModel = UserViewModel(repository)
}
```

**Builder**
```kotlin
class NetworkRequest private constructor(
    val url: String,
    val method: String,
    val headers: Map<String, String>,
    val body: String?
) {
    class Builder {
        private var url: String = ""
        private var method: String = "GET"
        private var headers: MutableMap<String, String> = mutableMapOf()
        private var body: String? = null

        fun url(url: String) = apply { this.url = url }
        fun method(method: String) = apply { this.method = method }
        fun header(key: String, value: String) = apply { headers[key] = value }
        fun body(body: String) = apply { this.body = body }

        fun build() = NetworkRequest(url, method, headers, body)
    }
}
```

### Structural Patterns

**Adapter**
```kotlin
// Adapts legacy API to new interface
class LegacyUserAdapter(private val legacyUser: LegacyUser) : User {
    override fun getName() = legacyUser.fullName
    override fun getEmail() = legacyUser.emailAddress
}
```

**Decorator**
```kotlin
// Adds functionality to existing objects
class LoggingRepository(private val repository: Repository) : Repository {
    override fun getData(): Data {
        Log.d("Repository", "Fetching data")
        return repository.getData().also {
            Log.d("Repository", "Data fetched: $it")
        }
    }
}
```

### Behavioral Patterns

**Observer**
```kotlin
// Used extensively in LiveData, Flow
class DataSource {
    private val observers = mutableListOf<(String) -> Unit>()

    fun observe(observer: (String) -> Unit) {
        observers.add(observer)
    }

    fun notifyObservers(data: String) {
        observers.forEach { it(data) }
    }
}
```

**Strategy**
```kotlin
interface SortStrategy {
    fun sort(items: List<Int>): List<Int>
}

class QuickSort : SortStrategy {
    override fun sort(items: List<Int>) = items.sorted()
}

class BubbleSort : SortStrategy {
    override fun sort(items: List<Int>): List<Int> {
        // Bubble sort implementation
        return items
    }
}

class Sorter(private val strategy: SortStrategy) {
    fun execute(items: List<Int>) = strategy.sort(items)
}
```

### Architectural Patterns

**MVVM (Model-View-ViewModel)**
```kotlin
// Model
data class User(val id: Int, val name: String)

// ViewModel
class UserViewModel(private val repository: UserRepository) : ViewModel() {
    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user

    fun loadUser(id: Int) {
        viewModelScope.launch {
            _user.value = repository.getUser(id)
        }
    }
}

// View (Activity/Fragment)
class UserFragment : Fragment() {
    private val viewModel: UserViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewModel.user.observe(viewLifecycleOwner) { user ->
            // Update UI
        }
    }
}
```

## Use Cases

### When to Use

- **Complex object creation**: Use Factory or Builder patterns
- **Single instance needed**: Use Singleton pattern
- **Incompatible interfaces**: Use Adapter pattern
- **Dynamic behavior changes**: Use Strategy pattern
- **Event-driven systems**: Use Observer pattern
- **UI architecture**: Use MVVM, MVI, or Clean Architecture patterns
- **Code reusability**: Apply DRY principle with appropriate patterns

### When to Avoid

- **Simple problems**: Don't over-engineer with patterns when simple code suffices
- **Performance-critical code**: Some patterns add overhead
- **Learning phase**: Don't force patterns without understanding the problem
- **Team unfamiliarity**: Ensure team understands patterns being used

## Trade-offs

**Pros**:
- **Proven solutions**: Battle-tested approaches to common problems
- **Common vocabulary**: Easier communication between developers
- **Code maintainability**: Well-structured, easier to modify
- **Best practices**: Encapsulate industry knowledge
- **Flexibility**: Many patterns promote loose coupling
- **Documentation**: Self-documenting code structure

**Cons**:
- **Complexity**: Can over-complicate simple solutions
- **Learning curve**: Requires understanding of multiple patterns
- **Performance overhead**: Some patterns add abstraction layers
- **Misapplication**: Using wrong pattern can create more problems
- **Dogmatism**: Forcing patterns where not needed
- **Initial development time**: Takes longer to implement than ad-hoc solutions

## Pattern Categories

### Gang of Four (GoF) Patterns

**Creational** (5 patterns):
- Singleton
- Factory Method
- Abstract Factory
- Builder
- Prototype

**Structural** (7 patterns):
- Adapter
- Bridge
- Composite
- Decorator
- Facade
- Flyweight
- Proxy

**Behavioral** (11 patterns):
- Chain of Responsibility
- Command
- Interpreter
- Iterator
- Mediator
- Memento
- Observer
- State
- Strategy
- Template Method
- Visitor

### Modern Android Patterns

- **MVVM**: Model-View-ViewModel architecture
- **MVI**: Model-View-Intent architecture
- **Repository Pattern**: Data access abstraction
- **Dependency Injection**: Inversion of control
- **Clean Architecture**: Layered architecture with dependency rule

## Best Practices

1. **Understand the problem first**: Don't apply patterns blindly
2. **Start simple**: Add patterns only when needed
3. **Know multiple patterns**: Choose the most appropriate one
4. **Combine patterns**: Many patterns work well together
5. **Consider context**: Same problem may need different patterns in different contexts
6. **Refactor to patterns**: Let patterns emerge from code evolution
7. **Document pattern usage**: Help future maintainers understand design decisions

## Related Concepts

- [[c-dependency-injection]]
- [[c-lifecycle]]
- [[c-coroutines]]
- [[c-hilt]]
- [[c-dagger]]

## References

- "Design Patterns: Elements of Reusable Object-Oriented Software" by Gang of Four
- "Head First Design Patterns" by Freeman & Freeman
- [Refactoring Guru - Design Patterns](https://refactoring.guru/design-patterns)
- [Android Architecture Components Guide](https://developer.android.com/topic/architecture)
- [Kotlin Design Patterns](https://kotlinlang.org/docs/kotlin-tips.html)
