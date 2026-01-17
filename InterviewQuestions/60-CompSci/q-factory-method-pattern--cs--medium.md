---
id: dp-005
title: Factory Method Pattern / Паттерн фабричный метод
anki_cards:
- slug: dp-005-0-en
  language: en
  anki_id: 1768454535064
  synced_at: '2026-01-15T09:43:17.089318'
- slug: dp-005-0-ru
  language: ru
  anki_id: 1768454535088
  synced_at: '2026-01-15T09:43:17.090961'
aliases:
- Factory Method Pattern
- Паттерн фабричный метод
topic: cs
subtopics:
- design-patterns
- creational-patterns
- factory-method
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
- c-builder-pattern
- c-ci-cd-patterns
- c-command-pattern
- c-dao-pattern
- c-declarative-programming-patterns
- c-decorator-pattern
- c-factory-pattern
- q-abstract-factory-pattern--cs--medium
created: 2025-10-15
updated: 2025-11-11
tags:
- architecture-patterns
- creational-patterns
- difficulty/medium
- factory-method
- gof-patterns
---
# Вопрос (RU)
> Что такое паттерн Factory Method? Чем он отличается от Abstract Factory?

# Question (EN)
> What is the Factory Method pattern? How does it differ from Abstract Factory?

---

## Ответ (RU)

Паттерн Factory Method (Фабричный метод) — это порождающий паттерн проектирования, который предоставляет интерфейс для создания объектов в суперклассе, но позволяет подклассам изменять тип создаваемых объектов за счет переопределения фабричного метода.

### Определение

Паттерн Factory Method — это порождающий паттерн проектирования, который предоставляет интерфейс для создания объектов в суперклассе, но позволяет подклассам изменять тип создаваемых объектов. Обычно в базовом классе объявляется (как минимум) абстрактный или переопределяемый фабричный метод, а подклассы реализуют или переопределяют его, выбирая конкретный продукт.

### Проблемы, Которые Решает

1. Как отложить создание экземпляра объекта на подклассы? Определить фабричный метод в суперклассе и позволить подклассам решать, какой конкретный продукт создавать, переопределяя этот метод.
2. Как избежать жесткой привязки клиентского кода к конкретным классам? Клиент вызывает фабричный метод вместо прямого вызова конструктора конкретной реализации и зависит только от абстракций (интерфейсов/абстрактных классов).

Это позволяет создавать подклассы, которые могут изменить, какой класс продукта инстанцируется, не изменяя клиентский код.

### Когда Использовать

- Класс не может предсказать точные типы объектов, которые ему нужно создать.
- Класс хочет, чтобы его подклассы определяли, какие конкретные продукты создаются.
- Ответственность делегируется одному из нескольких вспомогательных подклассов, и вы хотите локализовать знание о том, какой подкласс используется, внутри этих подклассов, а не в клиентском коде.

### Пример: Обобщенная Реализация (Generic Implementation)

Шаги реализации:

1. Определить интерфейс или абстрактный класс для продуктов.
2. Определить абстрактный класс-создатель, который объявляет фабричный метод, возвращающий продукт (интерфейс/абстрактный тип).
3. Конкретные создатели переопределяют фабричный метод и создают конкретные продукты.
4. Клиенты вызывают фабричный метод (напрямую или через более высокоуровневые операции), вместо использования `new` для конкретных продуктов.

```kotlin
// Абстрактный продукт
interface Product {
    fun showProductType(): String
}

// Конкретные продукты
class ConcreteProductA : Product {
    override fun showProductType() = "Product Type A"
}

class ConcreteProductB : Product {
    override fun showProductType() = "Product Type B"
}

// Создатель с фабричным методом
abstract class Creator {
    abstract fun factoryMethod(): Product

    fun someOperation(): String {
        // Вызов фабричного метода для создания Product
        val product = factoryMethod()
        // Используем продукт
        return "Creator: Working with ${product.showProductType()}"
    }
}

// Конкретные создатели, переопределяющие фабричный метод
class ConcreteCreatorA : Creator() {
    override fun factoryMethod() = ConcreteProductA()
}

class ConcreteCreatorB : Creator() {
    override fun factoryMethod() = ConcreteProductB()
}

// Клиентский код
fun main() {
    val creatorA: Creator = ConcreteCreatorA()
    println(creatorA.someOperation())

    val creatorB: Creator = ConcreteCreatorB()
    println(creatorB.someOperation())
}
```

Вывод:

```text
Creator: Working with Product Type A
Creator: Working with Product Type B
```

Объяснение:

- `Product` — интерфейс абстрактного продукта.
- `ConcreteProductA` и `ConcreteProductB` — конкретные реализации `Product`.
- `Creator` — абстрактный класс с абстрактным методом `factoryMethod`, который возвращает `Product`.
- `ConcreteCreatorA` и `ConcreteCreatorB` — подклассы `Creator`, переопределяющие `factoryMethod` для создания соответствующих продуктов.
- Клиент вызывает операции создателя, которые используют `factoryMethod`, вместо прямого создания конкретных продуктов.

### Android-пример: Фабрика Диалогов (Dialog Factory)

(Упрощенный пример, имена пересекаются с Android-классами, но поведение здесь условное.)

```kotlin
// Интерфейс продукта
interface Dialog {
    fun show()
    fun dismiss()
}

// Конкретные продукты (иллюстративно)
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

// Создатель
abstract class DialogFactory {
    // Фабричный метод
    abstract fun createDialog(): Dialog

    // Шаблонный метод, использующий фабричный метод
    fun showDialog() {
        val dialog = createDialog()
        dialog.show()
        // Общая дополнительная логика
        println("Dialog is now visible")
    }
}

// Конкретные фабрики
class AlertDialogFactory : DialogFactory() {
    override fun createDialog() = AlertDialog()
}

class BottomSheetDialogFactory : DialogFactory() {
    override fun createDialog() = BottomSheetDialog()
}

class FullScreenDialogFactory : DialogFactory() {
    override fun createDialog() = FullScreenDialog()
}

// Использование (пример)
fun main() {
    val userPreference = "alert"

    val factory: DialogFactory = when (userPreference) {
        "alert" -> AlertDialogFactory()
        "bottomSheet" -> BottomSheetDialogFactory()
        else -> FullScreenDialogFactory()
    }

    factory.showDialog()
}
```

Здесь выбор конкретного диалога инкапсулирован в соответствующих фабриках, а клиент работает через абстракцию `DialogFactory` и `Dialog`.

### Factory Method Vs Abstract Factory

- Factory Method фокусируется на создании одного вида продукта через переопределяемый метод в иерархии создателей.
- Abstract Factory предоставляет интерфейс для создания семейств связанных продуктов (несколько методов для разных типов продуктов), гарантируя согласованность между ними.

Пример сравнения:

```kotlin
// Factory Method — иерархия создателей для одного абстрактного продукта
abstract class ButtonFactory {
    abstract fun createButton(): Button
}

// Abstract Factory — фабрика для семейства связанных компонентов UI
interface UIFactory {
    fun createButton(): Button
    fun createCheckbox(): Checkbox
    fun createTextField(): TextField
}
```

### Плюсы И Минусы

Плюсы:

1. Отделяет логику создания объектов от клиентского кода.
2. Облегчает добавление новых типов продуктов (следование принципу открытости/закрытости).
3. Упрощает тестирование за счет возможности подменять создателей/продукты.
4. Централизует логику создания.
5. Скрывает конкретные классы продуктов от клиентов, снижая связность.

Минусы:

1. Увеличивает количество классов и интерфейсов.
2. Добавляет дополнительный уровень косвенности.
3. Клиент или конфигурация все равно должны выбрать конкретного создателя.
4. Может вносить избыточную сложность при чрезмерном использовании.

### Kotlin: Вариант С Companion Object (Simple Factory)

Ниже пример простой фабрики с использованием `companion object` (это не классический GoF Factory Method, а simple factory, но идея централизации создания похожа):

```kotlin
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

// Использование
val payment = PaymentMethod.create("card", "1234-5678-9012-3456")
```

Здесь логика создания сосредоточена в одном месте и скрывает детали конкретных подтипов, но в отличие от классического Factory Method не использует наследование создателя и переопределение фабричного метода.

### Best Practices (Лучшие практики)

```kotlin
// DO: использовать для создания разных вариантов одного абстрактного продукта
abstract class TransportFactory {
    abstract fun createTransport(): Transport
}

// DO: комбинировать с Template Method
abstract class Creator {
    fun operation() {
        val product = factoryMethod()
        // Используем product
    }

    abstract fun factoryMethod(): Product
}

// DO: использовать sealed-классы там, где иерархия продуктов замкнута
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()

    companion object {
        fun <T> success(data: T) = Success(data)
        fun error(message: String) = Error(message)
    }
}

// DON'T: использовать Factory Method, когда нужно создавать целые семейства несвязанных продуктов —
//        для этого лучше подходит Abstract Factory.

// DON'T: чрезмерно усложнять простой процесс создания объектов —
//        прямой конструктор вполне допустим в простых случаях.
```

### Кратко

Factory Method — порождающий паттерн, который определяет интерфейс для создания объектов в суперклассе и позволяет подклассам изменять тип создаваемых объектов. Применяется, когда сложно заранее знать конкретные типы или нужно избавиться от зависимости клиентского кода от конкретных классов. Отличается от Abstract Factory тем, что работает с одной иерархией продукта (метод), а Abstract Factory создает семейства связанных продуктов. Плюсы: отделение создания от использования, простое добавление новых типов, скрытие конкретных классов, снижение связности. Минусы: больше классов, дополнительная косвенность, риск избыточной сложности при неверном применении.

---

## Answer (EN)

Factory Method is a creational design pattern that provides an interface for creating objects in a superclass but allows subclasses to alter the type of objects that will be created by overriding a factory method.

### Definition

The Factory Method pattern is a creational design pattern that provides an interface for creating objects in a superclass but allows subclasses to alter the type of objects that will be created. It defines an abstract or overridable factory method for creating objects, which subclasses implement or override to decide which concrete product to instantiate.

### Problems it Solves

1. How can a class defer instantiation to its subclasses? Define a factory method in the superclass and let subclasses decide which concrete product to create by overriding this method.
2. How to avoid hard-coding concrete classes in client code? Clients call the factory method instead of `new` on specific implementations, depending only on abstractions (interfaces/abstract classes).

This enables creation of subclasses that can change which product class is instantiated without modifying client code.

### When to Use

- A class cannot predict the exact types of objects it needs to create.
- A class wants its subclasses to specify the concrete products it creates.
- Classes delegate responsibility to one of multiple helper subclasses, and you want the knowledge of which helper is used to be localized inside those subclasses instead of client code.

### Example: Generic Implementation

Implementation steps:

1. Define an interface or abstract class for products.
2. Define an abstract creator class that declares a factory method returning the product interface/abstract type.
3. Concrete creator subclasses override this factory method to produce concrete products.
4. Clients call the creator's factory method (directly or via higher-level operations) instead of using `new` for concrete products.

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

Output:

```text
Creator: Working with Product Type A
Creator: Working with Product Type B
```

Explanation:

- `Product` is an interface representing the abstract product.
- `ConcreteProductA` and `ConcreteProductB` are concrete implementations of `Product`.
- `Creator` is an abstract class with an abstract `factoryMethod` which returns an object of type `Product`.
- `ConcreteCreatorA` and `ConcreteCreatorB` are subclasses of `Creator` that override the `factoryMethod` to produce `ConcreteProductA` and `ConcreteProductB` respectively.
- In the client code, instead of directly instantiating concrete products, we use the concrete creators' `factoryMethod` (via `someOperation`) to get the product.

### Android Example: Dialog Factory

(Illustrative example using dialog-like classes; names overlap with Android classes but behavior here is simplified.)

```kotlin
// Product interface
interface Dialog {
    fun show()
    fun dismiss()
}

// Concrete products (illustrative, not android.app.AlertDialog etc.)
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

// Usage (pseudo-code; userPreference assumed to be defined)
fun main() {
    val userPreference = "alert" // example value

    val factory: DialogFactory = when (userPreference) {
        "alert" -> AlertDialogFactory()
        "bottomSheet" -> BottomSheetDialogFactory()
        else -> FullScreenDialogFactory()
    }

    factory.showDialog()
}
```

### Factory Method Vs Abstract Factory

| Aspect | Factory Method | Abstract Factory |
|--------|----------------|------------------|
| Purpose | Provide an interface for creating a product; each concrete creator decides which variant to instantiate | Provide an interface for creating families of related products without specifying their concrete classes |
| Structure | Typically one factory method per creator hierarchy | Interface/class with multiple factory methods for different product types |
| Abstraction level | Method level (focus on a single product abstraction per hierarchy) | Class level (focus on a set of related products) |
| Complexity | Simpler | More complex |
| Use case | Vary the concrete class of one product abstraction | Create multiple related products that must be used together |

Example comparison:

```kotlin
// Factory Method - creator hierarchy for one product abstraction
abstract class ButtonFactory {
    abstract fun createButton(): Button
}

// Abstract Factory - creates a family of related UI components
interface UIFactory {
    fun createButton(): Button
    fun createCheckbox(): Checkbox
    fun createTextField(): TextField
}
```

### Pros and Cons

Pros:

1. Separates creation logic from client code.
2. New product types can be added easily (Open/Closed Principle).
3. Simplifies unit testing by allowing different creator/product implementations.
4. Centralizes object creation logic.
5. Hides specific product classes from clients, reducing coupling.

Cons:

1. Adds more classes and interfaces.
2. Introduces an extra indirection layer.
3. Clients/configuration still need to choose concrete creators.
4. May lead to unnecessary complexity if overused.

### Kotlin Companion Object Alternative

```kotlin
// Kotlin-style static factory using companion object (Simple Factory, not classic GoF Factory Method)
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

This shows a Kotlin-idiomatic simple factory approach: the creation logic is centralized in one place. Unlike the classic Factory Method pattern, it does not rely on subclassing a creator and overriding a factory method.

### Best Practices

```kotlin
// DO: Use for creating different variants of the same product abstraction
abstract class TransportFactory {
    abstract fun createTransport(): Transport
}

// DO: Combine with Template Method
abstract class Creator {
    fun operation() {
        val product = factoryMethod()
        // Use product
    }

    abstract fun factoryMethod(): Product
}

// DO: Use sealed classes in Kotlin where appropriate for closed hierarchies
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()

    companion object {
        fun <T> success(data: T) = Success(data)
        fun error(message: String) = Error(message)
    }
}

// DON'T: Use Factory Method when you need to create whole families of unrelated products.
//        Use Abstract Factory instead.

// DON'T: Overcomplicate simple object creation.
//        Direct instantiation is fine for straightforward cases.
```

### Summary

Factory Method is a creational design pattern that defines an interface for creating objects in a superclass, allowing subclasses to alter the type of created objects by overriding a factory method. Problem: class cannot predict object types or you want to avoid coupling to concrete classes. Solution: define a factory method in the superclass and delegate creation to subclasses. Use when a class can't predict concrete types, when subclasses should decide which products to create, or when delegating responsibility to helper subclasses. Pros: separates creation logic, easy to add new types, simplifies testing, centralizes logic, hides concrete classes. Cons: more classes, extra indirection, unnecessary complexity if overused. Vs Abstract Factory: Factory Method focuses on one product abstraction via an overridable method; Abstract Factory creates families of related products via multiple factory methods.

---

## Follow-ups

- How would you refactor existing code that directly instantiates classes to use Factory Method?
- When would you still prefer simple constructors or a simple factory over Factory Method?
- How would you combine Factory Method with Dependency Injection in a real project?

## Related Questions

- [[q-abstract-factory-pattern--cs--medium]]

## References

- [[c-architecture-patterns]]
- [Factory method pattern](https://en.wikipedia.org/wiki/Factory_method_pattern)
- [Factory Method Design Pattern](https://sourcemaking.com/design_patterns/factory_method)
- [Factory Method](https://refactoring.guru/design-patterns/factory-method)
