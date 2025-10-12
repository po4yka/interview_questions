---
tags:
  - design-patterns
  - creational-patterns
  - factory-method
  - factory
  - gof-patterns
difficulty: medium
status: draft
---

# Factory Method Pattern

# Question (EN)
> What is the Factory Method pattern? How does it differ from Abstract Factory?

# Вопрос (RU)
> Что такое паттерн Factory Method? Чем он отличается от Abstract Factory?

---

## Answer (EN)


**Factory Method (Фабричный метод)** - это порождающий паттерн проектирования, который предоставляет интерфейс для создания объектов в суперклассе, но позволяет подклассам изменять тип создаваемых объектов.

### Definition


The Factory Method pattern is a creational design pattern that provides an interface for creating objects in a superclass but allows subclasses to alter the type of objects that will be created. It defines a method for creating objects, which subclasses can then override to change the type of objects that will be created.

### Problems it Solves


The factory method design pattern solves problems such as:

1. **How can an object's subclasses redefine its subsequent and distinct implementation?** The pattern involves creation of a factory method within the superclass that defers the object's creation to a subclass's factory method
2. **How can an object's instantiation be deferred to a subclass?** Create an object by calling a factory method instead of directly calling a constructor

This enables the creation of subclasses that can change the way in which an object is created (for example, by redefining which class to instantiate).

### When to Use?


**When to use Factory Method Design Pattern?**

- A class **cannot predict the type** of objects it needs to create
- A class wants its **subclasses to specify** the objects it creates
- Classes **delegate responsibility** to one of multiple helper subclasses, and you aim to keep the information about which helper subclass is the delegate within a specific scope or location

## Пример: Generic Implementation

Implementation Steps:

1. Define an interface or abstract class with a factory method
2. Concrete classes will implement or override this factory method to produce objects
3. Clients will call the factory method instead of directly using the `new` keyword

```kotlin
// Abstract product
interface Product {
    fun showProductType(): String
}

// Concrete products
class ConcreteProductA : Product {
    override fun showProductType() = "Product Type A"
}

class ConcreteProductB : Product {
    override fun showProductType() = "Product Type B"
}

// Creator class with the factory method
abstract class Creator {
    abstract fun factoryMethod(): Product

    fun someOperation(): String {
        // Call the factory method to create a Product object
        val product = factoryMethod()
        // Now use the product
        return "Creator: Working with ${product.showProductType()}"
    }
}

// Concrete creators that override the factory method
class ConcreteCreatorA : Creator() {
    override fun factoryMethod() = ConcreteProductA()
}

class ConcreteCreatorB : Creator() {
    override fun factoryMethod() = ConcreteProductB()
}

// Client code
fun main() {
    val creatorA: Creator = ConcreteCreatorA()
    println(creatorA.someOperation())

    val creatorB: Creator = ConcreteCreatorB()
    println(creatorB.someOperation())
}
```

**Output**:
```
Creator: Working with Product Type A
Creator: Working with Product Type B
```

### Explanation


**Explanation**:

- `Product` is an interface representing the **abstract product**
- `ConcreteProductA` and `ConcreteProductB` are **concrete implementations** of the `Product`
- `Creator` is an abstract class with an **abstract `factoryMethod`** which returns an object of type `Product`
- `ConcreteCreatorA` and `ConcreteCreatorB` are **subclasses of Creator** that override the `factoryMethod` to produce `ConcreteProductA` and `ConcreteProductB` respectively
- In the client code (`main` function), instead of directly instantiating the product, we use the concrete creators' `factoryMethod` to get the product

## Android Example: Dialog Factory

```kotlin
// Product interface
interface Dialog {
    fun show()
    fun dismiss()
}

// Concrete products
class AlertDialog : Dialog {
    override fun show() {
        println("Showing Alert Dialog")
    }

    override fun dismiss() {
        println("Dismissing Alert Dialog")
    }
}

class BottomSheetDialog : Dialog {
    override fun show() {
        println("Showing Bottom Sheet Dialog")
    }

    override fun dismiss() {
        println("Dismissing Bottom Sheet Dialog")
    }
}

class FullScreenDialog : Dialog {
    override fun show() {
        println("Showing Full Screen Dialog")
    }

    override fun dismiss() {
        println("Dismissing Full Screen Dialog")
    }
}

// Creator
abstract class DialogFactory {
    // Factory method
    abstract fun createDialog(): Dialog

    // Template method using factory method
    fun showDialog() {
        val dialog = createDialog()
        dialog.show()
        // Additional common logic
        println("Dialog is now visible")
    }
}

// Concrete creators
class AlertDialogFactory : DialogFactory() {
    override fun createDialog() = AlertDialog()
}

class BottomSheetDialogFactory : DialogFactory() {
    override fun createDialog() = BottomSheetDialog()
}

class FullScreenDialogFactory : DialogFactory() {
    override fun createDialog() = FullScreenDialog()
}

// Usage
fun main() {
    val factory: DialogFactory = when (userPreference) {
        "alert" -> AlertDialogFactory()
        "bottomSheet" -> BottomSheetDialogFactory()
        else -> FullScreenDialogFactory()
    }

    factory.showDialog()
}
```

## Factory Method vs Abstract Factory

| Aspect | Factory Method | Abstract Factory |
|--------|----------------|------------------|
| **Purpose** | Create one product | Create families of related products |
| **Structure** | Single method | Multiple methods |
| **Abstraction level** | Method level | Class level |
| **Complexity** | Simpler | More complex |
| **Use case** | One type of object with variants | Multiple related types of objects |

### Example Comparison

```kotlin
// Factory Method - creates one type of object
abstract class ButtonFactory {
    abstract fun createButton(): Button
}

// Abstract Factory - creates family of objects
interface UIFactory {
    fun createButton(): Button
    fun createCheckbox(): Checkbox
    fun createTextField(): TextField
}
```

## Преимущества и недостатки

### Pros (Преимущества)


1. **Separates creation logic from client code** - Improving flexibility
2. **New product types can be added easily** - Open/Closed Principle
3. **Simplifies unit testing** - By allowing mock class creation
4. **Centralizes object creation logic** - Across the application
5. **Hides specific product classes from clients** - Reducing dependency

### Cons (Недостатки)


1. **Adds more classes and interfaces** - Which can complicate maintenance
2. **Slight performance impacts** - Due to polymorphism
3. **Clients need knowledge of specific subclasses** - To instantiate creators
4. **May lead to unnecessary complexity** - If applied too broadly

## Kotlin Companion Object Alternative

```kotlin
// Kotlin-style factory using companion object
sealed class PaymentMethod {
    data class CreditCard(val number: String) : PaymentMethod()
    data class PayPal(val email: String) : PaymentMethod()
    data class Crypto(val wallet: String) : PaymentMethod()

    companion object {
        fun create(type: String, value: String): PaymentMethod {
            return when (type) {
                "card" -> CreditCard(value)
                "paypal" -> PayPal(value)
                "crypto" -> Crypto(value)
                else -> throw IllegalArgumentException("Unknown payment type")
            }
        }
    }
}

// Usage
val payment = PaymentMethod.create("card", "1234-5678-9012-3456")
```

## Best Practices

```kotlin
// - DO: Use for creating different variants of same type
abstract class TransportFactory {
    abstract fun createTransport(): Transport
}

// - DO: Combine with Template Method
abstract class Creator {
    fun operation() {
        val product = factoryMethod()
        // Use product
    }

    abstract fun factoryMethod(): Product
}

// - DO: Use sealed classes in Kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()

    companion object {
        fun <T> success(data: T) = Success(data)
        fun error(message: String) = Error(message)
    }
}

// - DON'T: Use for creating families of objects
// Use Abstract Factory instead

// - DON'T: Overcomplicate simple object creation
// Direct instantiation is fine for simple cases
```

**English**: **Factory Method** is a creational design pattern that defines an interface for creating objects in a superclass, allowing subclasses to alter the type of created objects. **Problem**: Class cannot predict object types it needs to create. Direct constructor calls are inflexible. **Solution**: Define factory method in superclass, defer object creation to subclasses. **Use when**: (1) Class can't predict object types, (2) Want subclasses to specify objects, (3) Delegate responsibility to helper subclasses. **Pros**: separates creation logic, easy to add new types, simplifies testing, centralizes logic. **Cons**: more classes, slight performance impact, unnecessary complexity if overused. **vs Abstract Factory**: Factory Method creates one product type, Abstract Factory creates families of related products.

## Links

- [Factory method pattern](https://en.wikipedia.org/wiki/Factory_method_pattern)
- [Factory Method Design Pattern in Java](https://www.geeksforgeeks.org/java/factory-method-design-pattern-in-java/)
- [Factory Method Design Pattern in Kotlin](https://www.javaguides.net/2023/10/factory-method-design-pattern-in-kotlin.html)

## Further Reading

- [Factory Method Design Pattern](https://sourcemaking.com/design_patterns/factory_method)
- [Factory Method](https://refactoring.guru/design-patterns/factory-method)

---
*Source: Kirchhoff Android Interview Questions*


## Ответ (RU)

### Определение


The Factory Method pattern is a creational design pattern that provides an interface for creating objects in a superclass but allows subclasses to alter the type of objects that will be created. It defines a method for creating objects, which subclasses can then override to change the type of objects that will be created.

### Проблемы, которые решает


The factory method design pattern solves problems such as:

1. **How can an object's subclasses redefine its subsequent and distinct implementation?** The pattern involves creation of a factory method within the superclass that defers the object's creation to a subclass's factory method
2. **How can an object's instantiation be deferred to a subclass?** Create an object by calling a factory method instead of directly calling a constructor

This enables the creation of subclasses that can change the way in which an object is created (for example, by redefining which class to instantiate).

### Когда использовать?


**When to use Factory Method Design Pattern?**

- A class **cannot predict the type** of objects it needs to create
- A class wants its **subclasses to specify** the objects it creates
- Classes **delegate responsibility** to one of multiple helper subclasses, and you aim to keep the information about which helper subclass is the delegate within a specific scope or location

### Объяснение


**Explanation**:

- `Product` is an interface representing the **abstract product**
- `ConcreteProductA` and `ConcreteProductB` are **concrete implementations** of the `Product`
- `Creator` is an abstract class with an **abstract `factoryMethod`** which returns an object of type `Product`
- `ConcreteCreatorA` and `ConcreteCreatorB` are **subclasses of Creator** that override the `factoryMethod` to produce `ConcreteProductA` and `ConcreteProductB` respectively
- In the client code (`main` function), instead of directly instantiating the product, we use the concrete creators' `factoryMethod` to get the product

### Pros (Преимущества)


1. **Separates creation logic from client code** - Improving flexibility
2. **New product types can be added easily** - Open/Closed Principle
3. **Simplifies unit testing** - By allowing mock class creation
4. **Centralizes object creation logic** - Across the application
5. **Hides specific product classes from clients** - Reducing dependency

### Cons (Недостатки)


1. **Adds more classes and interfaces** - Which can complicate maintenance
2. **Slight performance impacts** - Due to polymorphism
3. **Clients need knowledge of specific subclasses** - To instantiate creators
4. **May lead to unnecessary complexity** - If applied too broadly
