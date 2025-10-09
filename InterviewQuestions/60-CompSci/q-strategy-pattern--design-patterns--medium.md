---
tags:
  - design-patterns
  - behavioral-patterns
  - strategy
  - gof-patterns
  - policy-pattern
difficulty: medium
status: reviewed
---

# Strategy Pattern

**English**: What is the Strategy pattern? When and why should it be used?

## Answer

**Strategy (Стратегия)** - это поведенческий паттерн проектирования, который определяет семейство алгоритмов, инкапсулирует каждый из них и делает их взаимозаменяемыми. Стратегия позволяет изменять алгоритмы независимо от клиентов, которые ими пользуются.

### Определение

The Strategy Design Pattern is a behavioral design pattern that **allows you to define a family of algorithms or behaviors, put each of them in a separate class, and make them interchangeable at runtime**. This pattern is useful when you want to dynamically change the behavior of a class without modifying its code.

### Ключевые характеристики

This pattern exhibits several key characteristics:

1. **Defines a family of algorithms** - Encapsulates multiple algorithms/behaviors into separate classes (strategies)
2. **Encapsulates behaviors** - Each strategy encapsulates a specific behavior or algorithm
3. **Enables dynamic behavior switching** - Clients can switch between different strategies at runtime
4. **Promotes object collaboration** - Context delegates execution to a strategy object

### Когда использовать?

The Strategy Design Pattern can be useful in various scenarios:

1. **Sorting algorithms** - Different sorting algorithms encapsulated into strategies
2. **Validation rules** - Different validation rules as separate strategies
3. **Text formatting** - Different formatting strategies
4. **Database access** - Different database access strategies
5. **Payment strategy** - Different payment methods as strategies
6. **Navigation apps** - Different routes based on travel mode (driving, biking, walking)
7. **Image compression** - Users can choose different compression algorithms

## Пример: Navigation Routes

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

// Client Code
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
```
Driving route from Point A to Point B (fastest, highways)
Walking route from Point A to Point B (shortest, pedestrian paths)
Biking route from Point A to Point B (bike lanes, moderate distance)
```

## Android Example: Payment Processing

```kotlin
// Strategy interface
interface PaymentStrategy {
    fun pay(amount: Double): PaymentResult
}

data class PaymentResult(val success: Boolean, val transactionId: String)

// Concrete strategies
class CreditCardStrategy(
    private val cardNumber: String,
    private val cvv: String
) : PaymentStrategy {
    override fun pay(amount: Double): PaymentResult {
        println("Processing credit card payment of $$amount")
        // Validate card, process payment
        return PaymentResult(true, "CC-${System.currentTimeMillis()}")
    }
}

class PayPalStrategy(
    private val email: String,
    private val password: String
) : PaymentStrategy {
    override fun pay(amount: Double): PaymentResult {
        println("Processing PayPal payment of $$amount for $email")
        // Authenticate, process payment
        return PaymentResult(true, "PP-${System.currentTimeMillis()}")
    }
}

class GooglePayStrategy(
    private val accountId: String
) : PaymentStrategy {
    override fun pay(amount: Double): PaymentResult {
        println("Processing Google Pay payment of $$amount")
        // Use Google Pay API
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

// Usage
val cart = ShoppingCart()
cart.addItem("Book", 29.99)
cart.addItem("Pen", 5.99)

// User selects payment method
cart.setPaymentStrategy(CreditCardStrategy("1234-5678", "123"))
val result = cart.checkout()
```

## Kotlin Example: Sorting Strategy

```kotlin
// Strategy interface
interface SortStrategy<T> {
    fun sort(list: MutableList<T>): List<T>
}

// Concrete strategies
class BubbleSortStrategy<T : Comparable<T>> : SortStrategy<T> {
    override fun sort(list: MutableList<T>): List<T> {
        println("Sorting using Bubble Sort")
        // Bubble sort implementation
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

class QuickSortStrategy<T : Comparable<T>> : SortStrategy<T> {
    override fun sort(list: MutableList<T>): List<T> {
        println("Sorting using Quick Sort")
        return list.sorted() // Using Kotlin's optimized sort
    }
}

// Context
class Sorter<T : Comparable<T>>(private var strategy: SortStrategy<T>) {
    fun setStrategy(strategy: SortStrategy<T>) {
        this.strategy = strategy
    }

    fun sort(list: MutableList<T>) = strategy.sort(list)
}

// Usage
fun main() {
    val numbers = mutableListOf(5, 2, 8, 1, 9)

    val sorter = Sorter(BubbleSortStrategy<Int>())
    println(sorter.sort(numbers.toMutableList()))

    sorter.setStrategy(QuickSortStrategy())
    println(sorter.sort(numbers.toMutableList()))
}
```

### Объяснение примера

**Explanation**:

- **`RouteStrategy`** defines a contract that all strategies (algorithms) must follow
- **Concrete strategies** (`DrivingStrategy`, `WalkingStrategy`) encapsulate specific algorithms
- **`Navigator`** (context class) maintains a reference to a strategy object and can switch between strategies
- Client can easily switch between different strategies without changing the context implementation
- **Android**: Payment processing, image filters, data validation, network retry strategies

## Преимущества и недостатки

### Pros (Преимущества)

1. **Eliminates conditional logic** - Reduces complex if-else or when statements
2. **Enhances flexibility** - Easy to add/modify algorithms without affecting client code
3. **Promotes reusability** - Each algorithm is standalone and reusable
4. **Improves maintainability** - Encapsulating algorithms separately makes code easier to maintain
5. **Open/Closed Principle** - Open for extension, closed for modification
6. **Runtime flexibility** - Can switch strategies at runtime

### Cons (Недостатки)

1. **Increased number of classes** - Each algorithm requires a separate class
2. **Complexity** - Can introduce complexity with numerous strategies
3. **Overhead** - May introduce overhead when simple conditional would suffice
4. **Client awareness** - Clients must be aware of different strategies
5. **Strategy selection logic** - Need to implement strategy selection logic

## Best Practices

```kotlin
// - DO: Use when you have multiple algorithms for same task
interface CompressionStrategy {
    fun compress(data: ByteArray): ByteArray
}

class ZipCompression : CompressionStrategy {
    override fun compress(data: ByteArray) = /* ZIP compression */ data
}

class GzipCompression : CompressionStrategy {
    override fun compress(data: ByteArray) = /* GZIP compression */ data
}

// - DO: Use with dependency injection
class ImageProcessor @Inject constructor(
    private val compressionStrategy: CompressionStrategy
) {
    fun processImage(image: ByteArray) = compressionStrategy.compress(image)
}

// - DO: Combine with Factory pattern
object StrategyFactory {
    fun getPaymentStrategy(type: PaymentType): PaymentStrategy {
        return when (type) {
            PaymentType.CREDIT_CARD -> CreditCardStrategy()
            PaymentType.PAYPAL -> PayPalStrategy()
            PaymentType.GOOGLE_PAY -> GooglePayStrategy()
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

**English**: **Strategy** is a behavioral design pattern that defines a family of interchangeable algorithms and allows selecting them at runtime. **Problem**: Need different algorithms for same task, want to avoid complex conditionals. **Solution**: Encapsulate each algorithm in separate strategy class, make them interchangeable. **Use when**: (1) Multiple algorithms for same task, (2) Need runtime algorithm switching, (3) Want to eliminate conditional logic. **Android**: Payment methods, navigation routes, image compression, sorting algorithms. **Pros**: eliminates conditionals, flexible, reusable, maintainable. **Cons**: many classes, complexity with numerous strategies. **Examples**: payment processing, route planning, sorting, compression, validation.

## Links

- [Strategy Design Pattern](https://www.geeksforgeeks.org/system-design/strategy-pattern-set-1/)
- [A Beginner's Guide to the Strategy Design Pattern](https://www.freecodecamp.org/news/a-beginners-guide-to-the-strategy-design-pattern/)
- [Strategy Design Pattern in Kotlin](https://www.javaguides.net/2023/10/strategy-design-pattern-in-kotlin.html)
- [Understanding the Strategy Pattern in Android Development](https://blog.evanemran.info/understanding-the-strategy-pattern-in-android-development)

## Further Reading

- [Strategy Design Pattern](https://sourcemaking.com/design_patterns/strategy)
- [Strategy](https://refactoring.guru/design-patterns/strategy)
- [Strategy Pattern in Kotlin](https://swiderski.tech/kotlin-strategy-pattern/)

---
*Source: Kirchhoff Android Interview Questions*
