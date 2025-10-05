---
tags:
  - oop
  - composition
  - has-a
  - design-patterns
  - encapsulation
  - code-reuse
  - relationships
  - easy_kotlin
difficulty: medium
---

# Что известно о композиции классов?

**English**: What is known about class composition?

## Answer

**Class composition** is a fundamental principle of object-oriented programming used to model relationships between objects. In composition, **one class includes objects of other classes as its fields**, achieving more complex functionality through combining behaviors and properties of these objects.

## Core Aspects of Composition

### 1. Strong Coupling (Ownership)

In composition, objects used as fields are **tightly coupled** with the container class. Their **lifecycle depends on the container's lifecycle**.

**When the container is destroyed, the contained objects are also destroyed.**

```kotlin
class Engine(val type: String) {
    fun start() = println("Engine started")
    fun stop() = println("Engine stopped")
}

class Car(val model: String) {
    // Engine is owned by Car (composition)
    private val engine = Engine("V8")  // Created with Car

    fun start() {
        println("Starting $model")
        engine.start()
    }

    fun stop() {
        engine.stop()
        println("$model stopped")
    }
}

fun main() {
    val car = Car("Mustang")
    car.start()
    // When car is garbage collected, engine is also garbage collected
}
```

---

### 2. Part-Whole Relationship

Composition is often used to model **part-whole relationships**. The parts are **integral components** of the whole.

```kotlin
// Whole
class Computer(
    val brand: String
) {
    // Parts
    private val cpu = CPU("Intel i9")
    private val ram = RAM(32, "GB")
    private val storage = Storage(1, "TB SSD")
    private val motherboard = Motherboard("ASUS ROG")

    fun boot() {
        println("Booting $brand computer")
        cpu.process()
        ram.load()
        storage.read()
        motherboard.initialize()
    }

    fun shutdown() {
        println("Shutting down $brand computer")
        cpu.stop()
    }
}

class CPU(val model: String) {
    fun process() = println("CPU $model processing")
    fun stop() = println("CPU stopped")
}

class RAM(val size: Int, val unit: String) {
    fun load() = println("RAM loading $size$unit")
}

class Storage(val capacity: Int, val type: String) {
    fun read() = println("Storage reading from $capacity$type")
}

class Motherboard(val model: String) {
    fun initialize() = println("Motherboard $model initialized")
}

// Usage
val computer = Computer("Gaming PC")
computer.boot()
// CPU, RAM, Storage, Motherboard are parts of Computer
// They cannot exist without Computer
```

**Examples:**
- `Car` HAS-A `Engine`, `Wheels`, `Transmission`
- `House` HAS-A `Room`, `Door`, `Window`
- `Computer` HAS-A `CPU`, `RAM`, `Storage`

---

### 3. Code Reuse

Composition enables **code reuse** by integrating objects created for specific functions into other classes.

```kotlin
// Reusable components
class Logger {
    fun log(message: String) {
        println("[LOG] $message")
    }
}

class Validator {
    fun validateEmail(email: String): Boolean {
        return email.contains("@")
    }
}

class DatabaseConnection {
    fun save(data: String) {
        println("Saved to database: $data")
    }
}

// UserService composes Logger, Validator, Database
class UserService {
    private val logger = Logger()
    private val validator = Validator()
    private val database = DatabaseConnection()

    fun registerUser(email: String) {
        logger.log("Attempting to register user: $email")

        if (!validator.validateEmail(email)) {
            logger.log("Invalid email: $email")
            return
        }

        database.save("User: $email")
        logger.log("User registered successfully")
    }
}

// ProductService reuses same components
class ProductService {
    private val logger = Logger()
    private val database = DatabaseConnection()

    fun addProduct(name: String) {
        logger.log("Adding product: $name")
        database.save("Product: $name")
        logger.log("Product added successfully")
    }
}
```

**Benefit:** Logger, Validator, and DatabaseConnection can be reused across multiple services.

---

### 4. Avoiding Multiple Inheritance Problems

Some languages like **Java and Kotlin** don't support **multiple class inheritance** due to complexity and potential issues (diamond problem).

**Composition provides a flexible alternative** to achieve functionality from multiple sources.

```kotlin
// ❌ BAD: Can't inherit from multiple classes in Kotlin
// class FlyingCar : Car, Aircraft { }  // Compilation error!

// ✅ GOOD: Use composition
class Aircraft {
    fun fly() = println("Flying")
    fun land() = println("Landing")
}

class Car {
    fun drive() = println("Driving")
    fun park() = println("Parking")
}

// FlyingCar uses composition instead of multiple inheritance
class FlyingCar {
    private val carCapabilities = Car()
    private val aircraftCapabilities = Aircraft()

    fun drive() = carCapabilities.drive()
    fun park() = carCapabilities.park()
    fun fly() = aircraftCapabilities.fly()
    fun land() = aircraftCapabilities.land()

    fun transform() {
        park()
        println("Transforming...")
        fly()
    }
}

fun main() {
    val flyingCar = FlyingCar()
    flyingCar.drive()
    flyingCar.transform()
    flyingCar.land()
}
```

**Kotlin Delegation** makes this even easier:

```kotlin
// ✅ BETTER: Kotlin delegation
class FlyingCar(
    private val carCapabilities: Car = Car(),
    private val aircraftCapabilities: Aircraft = Aircraft()
) {
    fun drive() = carCapabilities.drive()
    fun park() = carCapabilities.park()
    fun fly() = aircraftCapabilities.fly()
    fun land() = aircraftCapabilities.land()
}
```

---

### 5. Flexibility in Design

Composition provides **greater flexibility** in software design because **changes in one class have less impact** on classes that use its objects.

```kotlin
// ✅ Composition: Easy to swap payment methods
interface PaymentProcessor {
    fun processPayment(amount: Double)
}

class CreditCardProcessor : PaymentProcessor {
    override fun processPayment(amount: Double) {
        println("Processing $amount via Credit Card")
    }
}

class PayPalProcessor : PaymentProcessor {
    override fun processPayment(amount: Double) {
        println("Processing $amount via PayPal")
    }
}

class BitcoinProcessor : PaymentProcessor {
    override fun processPayment(amount: Double) {
        println("Processing $amount via Bitcoin")
    }
}

// OrderService uses composition
class OrderService(
    private val paymentProcessor: PaymentProcessor  // Injected dependency
) {
    fun placeOrder(amount: Double) {
        println("Placing order for $$amount")
        paymentProcessor.processPayment(amount)
        println("Order placed successfully")
    }
}

// Usage - easy to swap payment methods
val creditCardOrder = OrderService(CreditCardProcessor())
creditCardOrder.placeOrder(100.0)

val paypalOrder = OrderService(PayPalProcessor())
paypalOrder.placeOrder(200.0)

// No changes to OrderService needed!
```

**Benefit:** Can change PaymentProcessor implementation without modifying OrderService.

---

## Composition vs Inheritance

### Inheritance Example

```kotlin
// ❌ Inheritance: Rigid hierarchy
open class Animal {
    open fun eat() = println("Eating")
    open fun sleep() = println("Sleeping")
}

class Dog : Animal() {
    override fun eat() = println("Dog eating")
    fun bark() = println("Woof!")
}

class Cat : Animal() {
    override fun eat() = println("Cat eating")
    fun meow() = println("Meow!")
}

// Problem: Hard to change behavior, deep hierarchies
```

### Composition Example

```kotlin
// ✅ Composition: Flexible behavior
class EatingBehavior {
    fun eat() = println("Eating")
}

class SleepingBehavior {
    fun sleep() = println("Sleeping")
}

class BarkingBehavior {
    fun bark() = println("Woof!")
}

class MeowingBehavior {
    fun meow() = println("Meow!")
}

// Compose behaviors
class Dog(
    private val eating: EatingBehavior = EatingBehavior(),
    private val sleeping: SleepingBehavior = SleepingBehavior(),
    private val barking: BarkingBehavior = BarkingBehavior()
) {
    fun eat() = eating.eat()
    fun sleep() = sleeping.sleep()
    fun bark() = barking.bark()
}

// Easy to swap behaviors at runtime
class Cat(
    private val eating: EatingBehavior = EatingBehavior(),
    private val sleeping: SleepingBehavior = SleepingBehavior(),
    private val meowing: MeowingBehavior = MeowingBehavior()
) {
    fun eat() = eating.eat()
    fun sleep() = sleeping.sleep()
    fun meow() = meowing.meow()
}
```

---

## Android Example

```kotlin
// Repository pattern using composition
class UserRepository(
    private val remoteDataSource: UserRemoteDataSource,
    private val localDataSource: UserLocalDataSource,
    private val cache: UserCache
) {
    suspend fun getUser(id: String): User? {
        // Try cache first
        cache.get(id)?.let { return it }

        // Try local database
        localDataSource.getUser(id)?.let {
            cache.put(id, it)
            return it
        }

        // Fetch from remote
        val user = remoteDataSource.fetchUser(id)
        user?.let {
            localDataSource.saveUser(it)
            cache.put(id, it)
        }

        return user
    }
}

// ViewModel composes Repository
class UserViewModel(
    private val userRepository: UserRepository
) : ViewModel() {

    private val _user = MutableLiveData<User?>()
    val user: LiveData<User?> = _user

    fun loadUser(id: String) {
        viewModelScope.launch {
            _user.value = userRepository.getUser(id)
        }
    }
}

// Activity composes ViewModel
class UserActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        viewModel.user.observe(this) { user ->
            // Update UI
        }

        viewModel.loadUser("user_123")
    }
}
```

---

## Best Practices

### ✅ DO

1. **Favor composition over inheritance:**
   ```kotlin
   // ✅ Composition
   class Car(private val engine: Engine)

   // ❌ Inheritance
   class Car : Engine()  // Car IS-NOT-A Engine!
   ```

2. **Use dependency injection:**
   ```kotlin
   class UserService(
       private val repository: UserRepository,  // Injected
       private val logger: Logger               // Injected
   )
   ```

3. **Program to interfaces:**
   ```kotlin
   class OrderService(
       private val paymentProcessor: PaymentProcessor  // Interface
   )
   ```

4. **Keep components focused:**
   ```kotlin
   class UserValidator  // Only validates
   class UserRepository  // Only persists data
   class UserService    // Orchestrates
   ```

---

### ❌ DON'T

1. **Don't create god objects:**
   ```kotlin
   // ❌ BAD: Too many responsibilities
   class UserManager(
       private val validator: Validator,
       private val repository: Repository,
       private val emailService: EmailService,
       private val smsService: SmsService,
       private val analytics: Analytics,
       private val logger: Logger,
       // ... 20 more dependencies
   )
   ```

2. **Don't use inheritance when composition fits better:**
   ```kotlin
   // ❌ BAD: Car IS-NOT-A Engine
   class Car : Engine()

   // ✅ GOOD: Car HAS-A Engine
   class Car(private val engine: Engine)
   ```

---

## Summary

**Class Composition:**
- One class contains objects of other classes as fields
- **Strong coupling** - lifecycle dependency
- **Part-whole relationship** - components are integral parts
- **Code reuse** - reusable components
- **Avoids multiple inheritance** - flexible alternative
- **Design flexibility** - easy to change and test

**Key benefits:**
- **Flexibility** - easy to swap implementations
- **Testability** - easy to mock components
- **Maintainability** - changes localized
- **Reusability** - components can be reused

**Best practice:** **Favor composition over inheritance** for more flexible and maintainable code.

---

## Ответ

Композиция классов — это один из фундаментальных принципов объектно-ориентированного программирования, который используется для моделирования отношений между объектами. В контексте композиции один класс включает в себя один или несколько объектов других классов в качестве своих полей, тем самым достигая более сложной функциональности через комбинирование поведений и свойств этих объектов.

**Основные аспекты:**

1. **Сильная связь**: В композиции объекты классов, которые используются как поля, тесно связаны с классом-контейнером. Это означает, что их жизненный цикл зависит от жизненного цикла контейнера.

2. **Отношения часть-целое**: Композиция часто используется для моделирования отношений часть-целое. Например, класс Автомобиль может включать в себя объекты классов Колесо, Двигатель и Салон.

3. **Повторное использование кода**: Композиция позволяет повторно использовать код, поскольку объекты классов, созданные для определённых функций, могут быть легко интегрированы в другие классы.

4. **Избежание проблем множественного наследования**: Композиция предоставляет альтернативный и более гибкий способ объединения функциональности из нескольких источников.

5. **Гибкость в дизайне**: Использование композиции предоставляет большую гибкость в проектировании программного обеспечения, так как изменения в одном классе меньше влияют на классы, которые используют его объекты.

