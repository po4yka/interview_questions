---
id: dp-004
title: Strategy Pattern / Strategy Паттерн
aliases:
- Strategy Pattern
- Strategy Паттерн
topic: cs
subtopics:
- behavioral-patterns
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-cs
related:
- c-architecture-patterns
- q-abstract-factory-pattern--cs--medium
created: 2025-10-15
updated: 2025-11-11
tags:
- behavioral-patterns
- design-patterns
- difficulty/medium
- gof-patterns
- policy-pattern
- strategy
anki_cards:
- slug: dp-004-0-en
  language: en
  anki_id: 1768455794444
  synced_at: '2026-01-25T13:01:16.868158'
- slug: dp-004-0-ru
  language: ru
  anki_id: 1768455794469
  synced_at: '2026-01-25T13:01:16.870042'
---
# Вопрос (RU)
> Что такое паттерн Strategy? Когда и зачем его следует использовать?

# Question (EN)
> What is the Strategy pattern? When and why should it be used?

---

## Ответ (RU)

### Определение

Паттерн проектирования **Strategy** (Стратегия) — это поведенческий паттерн, который **позволяет определить семейство алгоритмов или поведений, поместить каждый из них в отдельный класс и сделать их взаимозаменяемыми во время выполнения**. Этот паттерн полезен, когда вы хотите динамически изменять поведение класса без модификации его кода.

### Ключевые Характеристики

Паттерн Strategy обладает несколькими ключевыми характеристиками:

1. **Определяет семейство алгоритмов** - Инкапсулирует множественные алгоритмы/поведения в отдельные классы (стратегии)
2. **Инкапсулирует поведение** - Каждая стратегия инкапсулирует специфичное поведение или алгоритм
3. **Обеспечивает динамическое переключение поведения** - Клиенты могут переключаться между разными стратегиями во время выполнения
4. **Способствует взаимодействию объектов** - Контекст делегирует выполнение объекту стратегии

### Структура Паттерна

Паттерн Strategy состоит из трех основных компонентов:

1. **Strategy (Стратегия)** - Интерфейс, общий для всех поддерживаемых алгоритмов. Контекст использует этот интерфейс для вызова алгоритма, определенного конкретной стратегией.
2. **ConcreteStrategy (Конкретная стратегия)** - Реализует алгоритм, используя интерфейс Strategy. Каждая конкретная стратегия представляет собой отдельный алгоритм или вариант поведения.
3. **`Context` (Контекст)** - Хранит ссылку на объект Strategy и взаимодействует с ним исключительно через интерфейс Strategy. Контекст не знает, какую конкретную стратегию использует.

### Когда Использовать?

Паттерн Strategy может быть полезен в различных сценариях:

1. **Алгоритмы сортировки** - Различные алгоритмы сортировки инкапсулированы в стратегии
2. **Правила валидации** - Различные правила валидации как отдельные стратегии
3. **Форматирование текста** - Различные стратегии форматирования
4. **Доступ к базе данных** - Различные стратегии доступа к БД
5. **Стратегия оплаты** - Различные методы платежа как стратегии
6. **Навигационные приложения** - Разные маршруты в зависимости от способа передвижения (автомобиль, велосипед, пешком)
7. **Сжатие изображений** - Пользователи могут выбирать различные алгоритмы сжатия

### Пример: Маршруты Навигации

```kotlin
// Шаг 1: Интерфейс стратегии
interface RouteStrategy {
    fun buildRoute(start: String, destination: String): String
}

// Шаг 2: Конкретные стратегии
class DrivingStrategy : RouteStrategy {
    override fun buildRoute(start: String, destination: String): String {
        return "Driving route from $start to $destination (fastest, highways)"
    }
}

class WalkingStrategy : RouteStrategy {
    override fun buildRoute(start: String, destination: String): String {
        return "Walking route from $start to $destination (shortest, pedestrian paths)"
    }
}

class BikingStrategy : RouteStrategy {
    override fun buildRoute(start: String, destination: String): String {
        return "Biking route from $start to $destination (bike lanes, moderate distance)"
    }
}

// Шаг 3: Контекст
class Navigator(private var strategy: RouteStrategy) {
    fun setStrategy(newStrategy: RouteStrategy) {
        strategy = newStrategy
    }

    fun buildRoute(start: String, destination: String): String {
        return strategy.buildRoute(start, destination)
    }
}

// Клиентский код (пример)
fun main() {
    val navigator = Navigator(DrivingStrategy())
    println(navigator.buildRoute("Point A", "Point B"))

    navigator.setStrategy(WalkingStrategy())
    println(navigator.buildRoute("Point A", "Point B"))

    navigator.setStrategy(BikingStrategy())
    println(navigator.buildRoute("Point A", "Point B"))
}
```

Ожидаемый вывод:
```text
Driving route from Point A to Point B (fastest, highways)
Walking route from Point A to Point B (shortest, pedestrian paths)
Biking route from Point A to Point B (bike lanes, moderate distance)
```

### Android Пример: Обработка Платежей

```kotlin
// Интерфейс стратегии оплаты (упрощенный пример)
interface PaymentStrategy {
    fun pay(amount: Double): PaymentResult
}

data class PaymentResult(val success: Boolean, val transactionId: String)

// Конкретные стратегии (заглушки)
class CreditCardStrategy(
    private val cardNumber: String,
    private val cvv: String
) : PaymentStrategy {
    override fun pay(amount: Double): PaymentResult {
        println("Processing credit card payment of $$amount")
        // TODO: Валидация карты, вызов платежного провайдера
        return PaymentResult(true, "CC-${System.currentTimeMillis()}")
    }
}

class PayPalStrategy(
    private val email: String,
    private val password: String
) : PaymentStrategy {
    override fun pay(amount: Double): PaymentResult {
        println("Processing PayPal payment of $$amount for $email")
        // TODO: Аутентификация, обработка платежа
        return PaymentResult(true, "PP-${System.currentTimeMillis()}")
    }
}

class GooglePayStrategy(
    private val accountId: String
) : PaymentStrategy {
    override fun pay(amount: Double): PaymentResult {
        println("Processing Google Pay payment of $$amount")
        // TODO: Вызов Google Pay API
        return PaymentResult(true, "GP-${System.currentTimeMillis()}")
    }
}

// Контекст
class ShoppingCart {
    private val items = mutableListOf<Pair<String, Double>>()
    private var paymentStrategy: PaymentStrategy? = null

    fun addItem(item: String, price: Double) {
        items.add(item to price)
    }

    fun setPaymentStrategy(strategy: PaymentStrategy) {
        paymentStrategy = strategy
    }

    fun checkout(): PaymentResult? {
        val total = items.sumOf { it.second }
        return paymentStrategy?.pay(total)
    }
}

// Использование (пример)
fun exampleUsage() {
    val cart = ShoppingCart()
    cart.addItem("Book", 29.99)
    cart.addItem("Pen", 5.99)

    cart.setPaymentStrategy(CreditCardStrategy("1234-5678", "123"))
    val result = cart.checkout()
    println(result)
}
```

### Kotlin Пример: Стратегия Сортировки

```kotlin
// Интерфейс стратегии сортировки
interface SortStrategy<T> {
    fun sort(list: MutableList<T>): List<T>
}

// Конкретные стратегии
class BubbleSortStrategy<T : Comparable<T>> : SortStrategy<T> {
    override fun sort(list: MutableList<T>): List<T> {
        println("Sorting using Bubble Sort")
        // Простая реализация пузырьковой сортировки (O(n^2), демонстрационная)
        for (i in 0 until list.size - 1) {
            for (j in 0 until list.size - i - 1) {
                if (list[j] > list[j + 1]) {
                    val temp = list[j]
                    list[j] = list[j + 1]
                    list[j + 1] = temp
                }
            }
        }
        return list
    }
}

class BuiltInSortStrategy<T : Comparable<T>> : SortStrategy<T> {
    override fun sort(list: MutableList<T>): List<T> {
        println("Sorting using built-in sorted() implementation")
        // Используем оптимизированную реализацию сортировки Kotlin
        return list.sorted()
    }
}

// Контекст
class Sorter<T : Comparable<T>>(private var strategy: SortStrategy<T>) {
    fun setStrategy(strategy: SortStrategy<T>) {
        this.strategy = strategy
    }

    fun sort(list: MutableList<T>) = strategy.sort(list)
}

// Использование (пример)
fun sortingExample() {
    val numbers = mutableListOf(5, 2, 8, 1, 9)

    val sorter = Sorter(BubbleSortStrategy<Int>())
    println(sorter.sort(numbers.toMutableList()))

    sorter.setStrategy(BuiltInSortStrategy())
    println(sorter.sort(numbers.toMutableList()))
}
```

### Пояснение К Примерам

- **`RouteStrategy`** определяет контракт, которому должны следовать все стратегии (алгоритмы)
- **Конкретные стратегии** (`DrivingStrategy`, `WalkingStrategy` и др.) инкапсулируют отдельные алгоритмы
- **`Navigator`** (контекст) хранит ссылку на стратегию и может переключаться между ними
- Паттерн полезен, когда необходимо легко переключаться между различными алгоритмами без изменения контекста
- В Android: стратегии оплаты, фильтры изображений, валидация данных, стратегии повтора сетевых запросов, различные подходы к навигации

### Pros (Преимущества)

1. **Устраняет условную логику** - Уменьшает сложные конструкции if-else или when
2. **Повышает гибкость** - Легко добавлять/изменять алгоритмы без влияния на клиентский код
3. **Способствует повторному использованию** - Каждый алгоритм является самостоятельным и переиспользуемым
4. **Улучшает поддерживаемость** - Инкапсуляция алгоритмов отдельно делает код легче в поддержке
5. **Принцип открытости/закрытости** - Открыт для расширения, закрыт для модификации
6. **Гибкость во время выполнения** - Можно переключать стратегии во время выполнения

### Cons (Недостатки)

1. **Увеличение количества классов** - Каждый алгоритм требует отдельного класса (если не используются функции/лямбды)
2. **Сложность** - Может привнести сложность при большом количестве стратегий
3. **Накладные расходы** - Может создать излишние накладные расходы, когда достаточно простого условного оператора
4. **Осведомленность клиента** - Клиенты должны знать о различных стратегиях
5. **Логика выбора стратегии** - Необходимо реализовать логику выбора стратегии

### Лучшие Практики

```kotlin
// DO: Используйте, когда есть несколько алгоритмов для одной задачи
interface CompressionStrategy {
    fun compress(data: ByteArray): ByteArray
}

class ZipCompression : CompressionStrategy {
    override fun compress(data: ByteArray) = /* TODO: ZIP compression */ data
}

class GzipCompression : CompressionStrategy {
    override fun compress(data: ByteArray) = /* TODO: GZIP compression */ data
}

// DO: Используйте с dependency injection
class ImageProcessor @Inject constructor(
    private val compressionStrategy: CompressionStrategy
) {
    fun processImage(image: ByteArray) = compressionStrategy.compress(image)
}

// DO: Комбинируйте с Factory паттерном (демонстрационный пример)
object StrategyFactory {
    fun getPaymentStrategy(
        type: PaymentType,
        cardNumber: String? = null,
        cvv: String? = null,
        email: String? = null,
        password: String? = null,
        accountId: String? = null
    ): PaymentStrategy {
        return when (type) {
            PaymentType.CREDIT_CARD -> CreditCardStrategy(cardNumber ?: "", cvv ?: "")
            PaymentType.PAYPAL -> PayPalStrategy(email ?: "", password ?: "")
            PaymentType.GOOGLE_PAY -> GooglePayStrategy(accountId ?: "")
        }
    }
}

// DO: Используйте функциональный стиль в Kotlin
class Processor(private var strategy: (String) -> String) {
    fun process(data: String) = strategy(data)
}

val uppercase: (String) -> String = { it.uppercase() }
val lowercase: (String) -> String = { it.lowercase() }

val processor = Processor(uppercase)
processor.process("Hello") // "HELLO"

// DON'T: Используйте Strategy для одного алгоритма, который не меняется
// DON'T: Создавайте стратегии для тривиальных операций
// DON'T: Смешивайте бизнес-логику с логикой выбора стратегии
```

### Краткое Резюме (RU)

Strategy — поведенческий паттерн, который определяет семейство взаимозаменяемых алгоритмов и позволяет выбирать их во время выполнения. Применяется, когда нужно поддерживать разные алгоритмы для одной задачи, избежать разрастания условных операторов и упростить расширение системы за счет инкапсуляции алгоритмов в отдельные стратегии.

## Answer (EN)

### Definition

The Strategy Design Pattern is a behavioral design pattern that **allows you to define a family of algorithms or behaviors, put each of them in a separate class, and make them interchangeable at runtime**. This pattern is useful when you want to dynamically change the behavior of a class without modifying its code.

### Key Characteristics

This pattern exhibits several key characteristics:

1. **Defines a family of algorithms** - Encapsulates multiple algorithms/behaviors into separate classes (strategies)
2. **Encapsulates behaviors** - Each strategy encapsulates a specific behavior or algorithm
3. **Enables dynamic behavior switching** - Clients can switch between different strategies at runtime
4. **Promotes object collaboration** - `Context` delegates execution to a strategy object

### Structure

The Strategy pattern has three main participants:

1. **Strategy** - An interface common to all supported algorithms. The `Context` uses this interface to call the algorithm defined by a concrete strategy.
2. **ConcreteStrategy** - Implements a specific algorithm using the Strategy interface. Each concrete strategy represents a distinct behavior.
3. **`Context`** - Maintains a reference to a Strategy object and interacts with it exclusively through the Strategy interface. The `Context` is decoupled from concrete strategy implementations.

### When to Use?

The Strategy Design Pattern can be useful in various scenarios:

1. **Sorting algorithms** - Different sorting algorithms encapsulated into strategies
2. **Validation rules** - Different validation rules as separate strategies
3. **Text formatting** - Different formatting strategies
4. **`Database` access** - Different database access strategies
5. **Payment strategy** - Different payment methods as strategies
6. **Navigation apps** - Different routes based on travel mode (driving, biking, walking)
7. **Image compression** - Users can choose different compression algorithms

### Example: Navigation Routes

```kotlin
// Step 1: Strategy Interface
interface RouteStrategy {
    fun buildRoute(start: String, destination: String): String
}

// Step 2: Concrete Strategies
class DrivingStrategy : RouteStrategy {
    override fun buildRoute(start: String, destination: String): String {
        return "Driving route from $start to $destination (fastest, highways)"
    }
}

class WalkingStrategy : RouteStrategy {
    override fun buildRoute(start: String, destination: String): String {
        return "Walking route from $start to $destination (shortest, pedestrian paths)"
    }
}

class BikingStrategy : RouteStrategy {
    override fun buildRoute(start: String, destination: String): String {
        return "Biking route from $start to $destination (bike lanes, moderate distance)"
    }
}

// Step 3: Context Class
class Navigator(private var strategy: RouteStrategy) {
    fun setStrategy(newStrategy: RouteStrategy) {
        strategy = newStrategy
    }

    fun buildRoute(start: String, destination: String): String {
        return strategy.buildRoute(start, destination)
    }
}

// Client Code (illustrative)
fun main() {
    val navigator = Navigator(DrivingStrategy())
    println(navigator.buildRoute("Point A", "Point B"))

    navigator.setStrategy(WalkingStrategy())
    println(navigator.buildRoute("Point A", "Point B"))

    navigator.setStrategy(BikingStrategy())
    println(navigator.buildRoute("Point A", "Point B"))
}
```

**Output**:
```text
Driving route from Point A to Point B (fastest, highways)
Walking route from Point A to Point B (shortest, pedestrian paths)
Biking route from Point A to Point B (bike lanes, moderate distance)
```

### Android Example: Payment Processing

```kotlin
// Strategy interface (illustrative, not production-ready Android payment code)
interface PaymentStrategy {
    fun pay(amount: Double): PaymentResult
}

data class PaymentResult(val success: Boolean, val transactionId: String)

// Concrete strategies (illustrative stubs)
class CreditCardStrategy(
    private val cardNumber: String,
    private val cvv: String
) : PaymentStrategy {
    override fun pay(amount: Double): PaymentResult {
        println("Processing credit card payment of $$amount")
        // TODO: Validate card, process payment via provider
        return PaymentResult(true, "CC-${System.currentTimeMillis()}")
    }
}

class PayPalStrategy(
    private val email: String,
    private val password: String
) : PaymentStrategy {
    override fun pay(amount: Double): PaymentResult {
        println("Processing PayPal payment of $$amount for $email")
        // TODO: Authenticate, process payment
        return PaymentResult(true, "PP-${System.currentTimeMillis()}")
    }
}

class GooglePayStrategy(
    private val accountId: String
) : PaymentStrategy {
    override fun pay(amount: Double): PaymentResult {
        println("Processing Google Pay payment of $$amount")
        // TODO: Use Google Pay API
        return PaymentResult(true, "GP-${System.currentTimeMillis()}")
    }
}

// Context
class ShoppingCart {
    private val items = mutableListOf<Pair<String, Double>>()
    private var paymentStrategy: PaymentStrategy? = null

    fun addItem(item: String, price: Double) {
        items.add(item to price)
    }

    fun setPaymentStrategy(strategy: PaymentStrategy) {
        paymentStrategy = strategy
    }

    fun checkout(): PaymentResult? {
        val total = items.sumOf { it.second }
        return paymentStrategy?.pay(total)
    }
}

// Usage (illustrative)
fun exampleUsage() {
    val cart = ShoppingCart()
    cart.addItem("Book", 29.99)
    cart.addItem("Pen", 5.99)

    // User selects payment method
    cart.setPaymentStrategy(CreditCardStrategy("1234-5678", "123"))
    val result = cart.checkout()
    println(result)
}
```

### Kotlin Example: Sorting Strategy

```kotlin
// Strategy interface
interface SortStrategy<T> {
    fun sort(list: MutableList<T>): List<T>
}

// Concrete strategies
class BubbleSortStrategy<T : Comparable<T>> : SortStrategy<T> {
    override fun sort(list: MutableList<T>): List<T> {
        println("Sorting using Bubble Sort")
        // Simple Bubble sort implementation (O(n^2), illustrative)
        for (i in 0 until list.size - 1) {
            for (j in 0 until list.size - i - 1) {
                if (list[j] > list[j + 1]) {
                    val temp = list[j]
                    list[j] = list[j + 1]
                    list[j + 1] = temp
                }
            }
        }
        return list
    }
}

class BuiltInSortStrategy<T : Comparable<T>> : SortStrategy<T> {
    override fun sort(list: MutableList<T>): List<T> {
        println("Sorting using built-in sorted() implementation")
        // Use Kotlin's optimized sort implementation as an alternative algorithm
        return list.sorted()
    }
}

// Context
class Sorter<T : Comparable<T>>(private var strategy: SortStrategy<T>) {
    fun setStrategy(strategy: SortStrategy<T>) {
        this.strategy = strategy
    }

    fun sort(list: MutableList<T>) = strategy.sort(list)
}

// Usage (illustrative)
fun sortingExample() {
    val numbers = mutableListOf(5, 2, 8, 1, 9)

    val sorter = Sorter(BubbleSortStrategy<Int>())
    println(sorter.sort(numbers.toMutableList()))

    sorter.setStrategy(BuiltInSortStrategy())
    println(sorter.sort(numbers.toMutableList()))
}
```

### Example Explanation

- **`RouteStrategy`** defines a contract that all strategies (algorithms) must follow
- **Concrete strategies** (`DrivingStrategy`, `WalkingStrategy`, etc.) encapsulate specific algorithms
- **`Navigator`** (context class) maintains a reference to a strategy object and can switch between strategies
- Client can easily switch between different strategies without changing the context implementation
- **Android**: Payment processing, image filters, data validation, network retry strategies

### Pros and Cons

#### Pros

1. **Eliminates conditional logic** - Reduces complex if-else or when statements
2. **Enhances flexibility** - Easy to add/modify algorithms without affecting client code
3. **Promotes reusability** - Each algorithm is standalone and reusable
4. **Improves maintainability** - Encapsulating algorithms separately makes code easier to maintain
5. **Open/Closed Principle** - Open for extension, closed for modification
6. **Runtime flexibility** - Can switch strategies at runtime

#### Cons

1. **Increased number of classes** - Each algorithm typically requires a separate class (unless using functions/lambdas)
2. **Complexity** - Can introduce complexity with numerous strategies
3. **Overhead** - May introduce overhead when a simple conditional would suffice
4. **Client awareness** - Clients must be aware of different strategies
5. **Strategy selection logic** - Need to implement strategy selection logic

### Best Practices

```kotlin
// - DO: Use when you have multiple algorithms for same task
interface CompressionStrategy {
    fun compress(data: ByteArray): ByteArray
}

class ZipCompression : CompressionStrategy {
    override fun compress(data: ByteArray) = /* TODO: ZIP compression */ data
}

class GzipCompression : CompressionStrategy {
    override fun compress(data: ByteArray) = /* TODO: GZIP compression */ data
}

// - DO: Use with dependency injection
class ImageProcessor @Inject constructor(
    private val compressionStrategy: CompressionStrategy
) {
    fun processImage(image: ByteArray) = compressionStrategy.compress(image)
}

// - DO: Combine with Factory pattern (illustrative only)
// PaymentType and concrete strategy constructors should be defined consistently
// with your actual PaymentStrategy implementations.
object StrategyFactory {
    fun getPaymentStrategy(type: PaymentType, cardNumber: String? = null, cvv: String? = null, email: String? = null, password: String? = null, accountId: String? = null): PaymentStrategy {
        return when (type) {
            PaymentType.CREDIT_CARD -> CreditCardStrategy(cardNumber ?: "", cvv ?: "")
            PaymentType.PAYPAL -> PayPalStrategy(email ?: "", password ?: "")
            PaymentType.GOOGLE_PAY -> GooglePayStrategy(accountId ?: "")
        }
    }
}

// - DO: Use functional programming in Kotlin
class Processor(private var strategy: (String) -> String) {
    fun process(data: String) = strategy(data)
}

val uppercase: (String) -> String = { it.uppercase() }
val lowercase: (String) -> String = { it.lowercase() }

val processor = Processor(uppercase)
processor.process("Hello") // "HELLO"

// - DON'T: Use for single algorithm that never changes
// - DON'T: Create strategies for trivial operations
// - DON'T: Mix business logic in strategy selection
```

### Concise Summary (EN)

Strategy is a behavioral design pattern that defines a family of interchangeable algorithms and allows selecting them at runtime. Use it when you have multiple algorithms for the same task, want to avoid complex conditionals, and prefer extending the system with new algorithms without modifying existing code.

## Дополнительные Вопросы (RU)

- Как реализовать выбор стратегии (например, через фабрику или конфигурацию), не смешивая бизнес-логику с клиентским кодом?
- Когда использование Strategy является избыточным по сравнению с простыми условными операторами?
- Как тестировать различные стратегии изолированно?

## Follow-ups

- How would you implement strategy selection (e.g., via factory or configuration) without leaking business logic into client code?
- When is Strategy overkill compared to simple conditionals?
- How would you test different strategies in isolation?

## Related Questions

- [[q-abstract-factory-pattern--cs--medium]]

## References

- [[c-architecture-patterns]]
- [Strategy Design Pattern]("https://sourcemaking.com/design_patterns/strategy")
- [Strategy]("https://refactoring.guru/design-patterns/strategy")
- [Understanding the Strategy Pattern in Android Development]("https://blog.evanemran.info/understanding-the-strategy-pattern-in-android-development")
- [Strategy Pattern in Kotlin]("https://swiderski.tech/kotlin-strategy-pattern/")
