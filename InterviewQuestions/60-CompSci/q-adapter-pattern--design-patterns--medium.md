---
tags:
  - design-patterns
  - structural-patterns
  - adapter
  - gof-patterns
  - wrapper
difficulty: medium
status: reviewed
---

# Adapter Pattern

**English**: What is the Adapter pattern? When and why should it be used?

## Answer

**Adapter (Адаптер)** - это структурный паттерн проектирования, который позволяет объектам с несовместимыми интерфейсами работать вместе. Он действует как мост между двумя классами с разными интерфейсами.

### Определение

The adapter pattern is a structural design pattern that **permits two somewhat incompatible interfaces to work together**. It acts as a bridge between two classes with different interfaces, allowing them to work together seamlessly.

### Проблемы, которые решает

The adapter design pattern solves problems like:

1. **How can a class be reused that does not have an interface that a client requires?**
2. **How can classes that have incompatible interfaces work together?**
3. **How can an alternative interface be provided for a class?**

### Почему это проблема?

Often an (already existing) class cannot be reused only because its interface does not conform to the interface clients require.

### Решение

The adapter design pattern describes how to solve such problems:

- Define a separate **`adapter`** class that converts the (incompatible) interface of a class (**`adaptee`**) into another interface (**`target`**) clients require
- Work through an **`adapter`** to work with (reuse) classes that do not have the required interface

The key idea is to work through a separate adapter that adapts the interface of an (already existing) class without changing it. Clients don't know whether they work with a target class directly or through an adapter.

## Ключевые характеристики

Key Characteristics:

1. **Interface Conversion** - Converts the interface of a class into another interface clients expect
2. **Reusability** - Promotes code reusability by allowing different classes to work together without modifying their code
3. **Flexibility** - Makes it easy to introduce new types of data sources or components

## Пример: Basic Adapter

```kotlin
// Target interface
interface ThreePinSocket {
    fun acceptThreePinPlug()
}

// Adaptee
class TwoPinPlug {
    fun insertTwoPinPlug() {
        println("Two-pin plug inserted!")
    }
}

// Adapter
class PlugAdapter(private val plug: TwoPinPlug) : ThreePinSocket {
    override fun acceptThreePinPlug() {
        plug.insertTwoPinPlug()
        println("Adapter made it compatible with three-pin socket!")
    }
}

fun main() {
    val twoPinPlug = TwoPinPlug()
    val adapter = PlugAdapter(twoPinPlug)
    adapter.acceptThreePinPlug()
}
```

**Output**:
```
Two-pin plug inserted!
Adapter made it compatible with three-pin socket!
```

## Android Example: RecyclerView Adapter

```kotlin
// Data model
data class User(val id: Int, val name: String, val email: String)

// ViewHolder
class UserViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
    private val nameTextView: TextView = itemView.findViewById(R.id.nameTextView)
    private val emailTextView: TextView = itemView.findViewById(R.id.emailTextView)

    fun bind(user: User) {
        nameTextView.text = user.name
        emailTextView.text = user.email
    }
}

// Adapter - bridges between data and RecyclerView
class UserAdapter(private val users: List<User>) :
    RecyclerView.Adapter<UserViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): UserViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_user, parent, false)
        return UserViewHolder(view)
    }

    override fun onBindViewHolder(holder: UserViewHolder, position: Int) {
        holder.bind(users[position])
    }

    override fun getItemCount() = users.size
}

// Usage
val users = listOf(
    User(1, "John Doe", "john@example.com"),
    User(2, "Jane Smith", "jane@example.com")
)
recyclerView.adapter = UserAdapter(users)
```

## Kotlin Example: Legacy System Integration

```kotlin
// Legacy payment system (Adaptee)
class LegacyPaymentSystem {
    fun processOldPayment(amount: Double, cardNumber: String): Boolean {
        println("Processing payment of $$amount with card $cardNumber")
        return true
    }
}

// Modern payment interface (Target)
interface ModernPaymentProcessor {
    fun processPayment(paymentRequest: PaymentRequest): PaymentResult
}

data class PaymentRequest(val amount: Double, val cardInfo: CardInfo)
data class CardInfo(val number: String, val cvv: String)
data class PaymentResult(val success: Boolean, val transactionId: String)

// Adapter
class PaymentAdapter(
    private val legacySystem: LegacyPaymentSystem
) : ModernPaymentProcessor {

    override fun processPayment(paymentRequest: PaymentRequest): PaymentResult {
        val success = legacySystem.processOldPayment(
            paymentRequest.amount,
            paymentRequest.cardInfo.number
        )

        return PaymentResult(
            success = success,
            transactionId = generateTransactionId()
        )
    }

    private fun generateTransactionId() = "TXN-${System.currentTimeMillis()}"
}

// Client code
fun main() {
    val legacySystem = LegacyPaymentSystem()
    val modernProcessor: ModernPaymentProcessor = PaymentAdapter(legacySystem)

    val request = PaymentRequest(
        amount = 100.0,
        cardInfo = CardInfo("1234-5678-9012-3456", "123")
    )

    val result = modernProcessor.processPayment(request)
    println("Payment result: ${result.success}, ID: ${result.transactionId}")
}
```

### Объяснение примера

**Explanation**:

- **`ThreePinSocket`** is the target interface that our client expects
- **`TwoPinPlug`** is the adaptee – the existing functionality we want to adapt
- **`PlugAdapter`** is the adapter class that implements the target interface and wraps the adaptee
- In Android, **RecyclerView.Adapter** is a classic example - it adapts data to ViewHolder items
- The **payment adapter** shows how to integrate legacy systems with modern interfaces

## Применение в Android

Adapter Pattern in Android:

1. **RecyclerView Adapters** - Convert data into ViewHolder items for efficient display
2. **ListView Adapters** - Adapt data for ListView and GridView components
3. **ViewPager Adapters** - Adapt pages for ViewPager to display fragments or views
4. **Database Adapters** - Adapt between different database systems or APIs

## Преимущества и недостатки

### Pros (Преимущества)

1. **Code reusability** - Reuse existing code without modifying it
2. **Single Responsibility** - Separates interface conversion from business logic
3. **Flexibility** - Can easily switch adapters to support different interfaces
4. **Open/Closed Principle** - Can introduce new adapters without changing existing code
5. **Decoupling** - Decouples client from specific implementations

### Cons (Недостатки)

1. **Increased complexity** - Adds extra layer of abstraction
2. **Performance overhead** - Additional indirection may impact performance slightly
3. **Maintenance challenges** - Multiple adapters can become cumbersome
4. **Over-engineering risk** - May be unnecessary for trivial changes
5. **Limited scope** - Can only translate two interfaces at a time

## Best Practices

```kotlin
// ✅ DO: Use adapter for incompatible interfaces
interface NewAPI {
    fun fetchData(): Flow<Data>
}

class OldAPIAdapter(private val oldAPI: OldAPI) : NewAPI {
    override fun fetchData() = flow {
        val result = oldAPI.getData() // Old blocking call
        emit(result.toNewFormat())
    }
}

// ✅ DO: Keep adapters simple and focused
class SimpleAdapter(private val adaptee: Adaptee) : Target {
    override fun request() = adaptee.specificRequest()
}

// ✅ DO: Use for database migration
class RoomToRealmAdapter(private val realmDB: Realm) : AppDatabase {
    override fun getUsers() = realmDB.where<User>().findAll()
        .map { it.toRoomEntity() }
}

// ❌ DON'T: Use adapter for single method translation
// Use extension functions instead

// ❌ DON'T: Create adapters with unrelated functionality
// Keep adapters focused on interface translation
```

**English**: **Adapter** is a structural design pattern that allows incompatible interfaces to work together by acting as a bridge. **Problem**: Existing class cannot be reused because its interface doesn't match client requirements. **Solution**: Create adapter class that converts adaptee's interface to target interface. **Use when**: (1) Want to reuse existing class with incompatible interface, (2) Integrating legacy systems, (3) Need to work with multiple incompatible interfaces. **Android**: RecyclerView.Adapter, ViewPager adapters. **Pros**: code reusability, flexibility, decoupling. **Cons**: increased complexity, performance overhead. **Examples**: RecyclerView adapter, legacy system integration, database adapters.

## Links

- [The Adapter Pattern in Kotlin](https://www.baeldung.com/kotlin/adapter-pattern)
- [Adapter pattern](https://en.wikipedia.org/wiki/Adapter_pattern)
- [Understanding the Adapter Pattern in Android Development](https://blog.evanemran.info/understanding-the-adapter-pattern-in-android-development)
- [Adapter Design Pattern in Kotlin](https://www.javaguides.net/2023/10/adapter-design-pattern-in-kotlin.html)

## Further Reading

- [Adapter](https://refactoring.guru/design-patterns/adapter)
- [Adapter Design Pattern](https://sourcemaking.com/design_patterns/adapter)
- [Adapter Software Pattern Kotlin Examples](https://softwarepatterns.com/kotlin/adapter-software-pattern-kotlin-example)

---
*Source: Kirchhoff Android Interview Questions*
