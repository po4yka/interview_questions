---
id: oop-003
title: "Class Composition / Композиция классов"
aliases: [Class Composition, Композиция классов]
topic: cs
subtopics: [composition, encapsulation, inheritance]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-computer-science, c-composition, q-inheritance-vs-composition--oop--medium]
created: 2025-10-13
updated: 2025-11-11
tags: [code-reuse, composition, difficulty/medium, encapsulation, inheritance, oop, relationships]
---

# Вопрос (RU)
> Что известно о композиции классов?

# Question (EN)
> What is known about class composition?

---

## Ответ (RU)
Композиция классов — один из фундаментальных принципов объектно-ориентированного программирования, который используется для моделирования отношений между объектами. В композиции один класс включает в себя объекты других классов в качестве своих полей, тем самым достигая более сложной функциональности за счет комбинирования поведения и состояний этих объектов.

### Ключевые аспекты композиции

1. **Сильная связь и владение (ownership):**
   В композиции объекты-части концептуально принадлежат объекту-целому, их жизненный цикл зависит от жизненного цикла владельца: вне контекста «целого» такие части обычно не имеют самостоятельного смысла.

   В управляемых языках (Java/Kotlin) это моделируется так, что когда объект-"контейнер" становится недостижим, связанные с ним составные объекты тоже перестают использоваться и могут быть удалены сборщиком мусора.

   ```kotlin
   class Engine(val type: String) {
       fun start() = println("Engine started")
       fun stop() = println("Engine stopped")
   }

   class Car(val model: String) {
       // Engine принадлежит Car (композиция)
       private val engine = Engine("V8")  // Создаётся вместе с Car

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
       // Когда car становится недостижим, его engine тоже недостижим —
       // в этой модели жизненный цикл Engine привязан к Car
   }
   ```

2. **Отношения часть-целое (HAS-A):**
   Композиция моделирует отношения «часть-целое», где части являются неотъемлемыми компонентами целого в рамках предметной области.

   ```kotlin
   // Целое
   class Computer(
       val brand: String
   ) {
       // Части (принадлежат Computer в данной модели)
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

   // Использование
   val computer = Computer("Gaming PC")
   computer.boot()
   // CPU, RAM, Storage, Motherboard здесь выступают частями Computer
   ```

   Примеры HAS-A:
   - `Car` HAS-A `Engine`, `Wheels`, `Transmission`
   - `House` HAS-A `Room`, `Door`, `Window`
   - `Computer` HAS-A `CPU`, `RAM`, `Storage`

3. **Повторное использование кода:**
   Композиция позволяет выносить общую функциональность в отдельные классы и переиспользовать их в разных контекстах, встраивая как поля.

   ```kotlin
   // Переиспользуемые компоненты
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

   // UserService композирует Logger, Validator, DatabaseConnection
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

   // ProductService переиспользует те же компоненты
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

4. **Альтернатива множественному наследованию:**
   В Java и Kotlin нет множественного наследования классов, поэтому композиция используется для комбинирования поведения из нескольких источников.

   ```kotlin
   class Aircraft {
       fun fly() = println("Flying")
       fun land() = println("Landing")
   }

   class Car {
       fun drive() = println("Driving")
       fun park() = println("Parking")
   }

   // FlyingCar использует композицию вместо множественного наследования
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

   **Делегирование в Kotlin** упрощает композицию:

   ```kotlin
   // Kotlin-стиль композиции через явное делегирование
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

5. **Гибкость дизайна:**
   Композиция делает архитектуру более гибкой: изменения в одном классе меньше затрагивают другие, зависимости легче подменять в тестах.

   ```kotlin
   // Легко менять способы оплаты благодаря композиции
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

   class OrderService(
       private val paymentProcessor: PaymentProcessor  // Внедрённая зависимость
   ) {
       fun placeOrder(amount: Double) {
           println("Placing order for $$amount")
           paymentProcessor.processPayment(amount)
           println("Order placed successfully")
       }
   }

   // Использование — просто меняем реализацию
   val creditCardOrder = OrderService(CreditCardProcessor())
   creditCardOrder.placeOrder(100.0)

   val paypalOrder = OrderService(PayPalProcessor())
   paypalOrder.placeOrder(200.0)
   ```

### Композиция vs Наследование

1. **Наследование (жёсткая иерархия):**
   ```kotlin
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
   ```
   Глубокие иерархии могут быть негибкими и сложными для изменения.

2. **Композиция (гибкое поведение):**
   ```kotlin
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

   class Dog(
       private val eating: EatingBehavior = EatingBehavior(),
       private val sleeping: SleepingBehavior = SleepingBehavior(),
       private val barking: BarkingBehavior = BarkingBehavior()
   ) {
       fun eat() = eating.eat()
       fun sleep() = sleeping.sleep()
       fun bark() = barking.bark()
   }

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
   Такое разбиение на поведения облегчает замену и переиспользование.

### Android-пример

Композиция широко используется в Android для разделения ответственности и переиспользования компонентов, например в паттерне Repository.

```kotlin
class UserRepository(
    private val remoteDataSource: UserRemoteDataSource,
    private val localDataSource: UserLocalDataSource,
    private val cache: UserCache
) {
    suspend fun getUser(id: String): User? {
        cache.get(id)?.let { return it }

        localDataSource.getUser(id)?.let {
            cache.put(id, it)
            return it
        }

        val user = remoteDataSource.fetchUser(id)
        user?.let {
            localDataSource.saveUser(it)
            cache.put(id, it)
        }

        return user
    }
}

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

class UserActivity : AppCompatActivity() {
    // В реальном приложении UserRepository передаётся через DI или фабрику
    private val viewModel: UserViewModel by viewModels {
        object : ViewModelProvider.Factory {
            override fun <T : ViewModel> create(modelClass: Class<T>): T {
                val repo = UserRepository(
                    UserRemoteDataSource(),
                    UserLocalDataSource(),
                    UserCache()
                )
                @Suppress("UNCHECKED_CAST")
                return UserViewModel(repo) as T
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        viewModel.user.observe(this) { user ->
            // Обновление UI
        }

        viewModel.loadUser("user_123")
    }
}
```

### Рекомендуемые практики (DO)

1. **Отдавайте предпочтение композиции перед наследованием:**
   ```kotlin
   // Правильно: композиция
   class Car(private val engine: Engine)

   // Неправильно: Car IS-NOT-A Engine
   class Car : Engine()
   ```

2. **Используйте внедрение зависимостей:**
   ```kotlin
   class UserService(
       private val repository: UserRepository,
       private val logger: Logger
   )
   ```

3. **Программируйте против интерфейсов:**
   ```kotlin
   class OrderService(
       private val paymentProcessor: PaymentProcessor
   )
   ```

4. **Делайте компоненты узкоспециализированными:**
   ```kotlin
   class UserValidator  // Только валидация
   class UserRepository // Только доступ к данным
   class UserService    // Оркестрация операций
   ```

### Антипаттерны (DON'T)

1. **Не создавайте "бог-объекты":**
   ```kotlin
   // ПЛОХО: слишком много ответственностей и зависимостей
   class UserManager(
       private val validator: Validator,
       private val repository: Repository,
       private val emailService: EmailService,
       private val smsService: SmsService,
       private val analytics: Analytics,
       private val logger: Logger,
       // ... ещё десятки зависимостей
   )
   ```

2. **Не используйте наследование там, где лучше композиция:**
   ```kotlin
   // ПЛОХО: Car IS-NOT-A Engine
   class Car : Engine()

   // ХОРОШО: Car HAS-A Engine
   class Car(private val engine: Engine)
   ```

### Итоги

Композиция классов:
- выражает включение объектов одних классов в другие как части целого;
- задаёт сильную связь и зависимость жизненного цикла частей от целого;
- моделирует отношения часть-целое (HAS-A);
- облегчает повторное использование кода и замену реализаций;
- помогает избежать проблем множественного наследования;
- повышает гибкость, тестируемость и поддерживаемость системы.

Практическое правило: в большинстве случаев предпочитайте композицию наследованию, применяя наследование там, где действительно выполняется отношение IS-A и нужен полиморфизм по иерархии типов.

---

## Answer (EN)

Class composition is a fundamental principle of object-oriented programming used to model relationships between objects. In composition, one class includes objects of other classes as its fields, achieving more complex functionality by combining the behaviors and state of these objects.

## Core Aspects of Composition

### 1. Strong Coupling (Ownership)

In composition, objects used as fields are tightly coupled with the container class at the domain-model level. Their lifecycle is intended to depend on the container's lifecycle: they conceptually do not make sense without the owning object.

In managed languages (like Java/Kotlin), this is modeled so that when the container is no longer reachable, its composed objects also become unreachable and can be garbage-collected together.

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
    // When 'car' becomes unreachable, its 'engine' becomes unreachable as well
    // (conceptually: Engine's lifecycle is bound to Car in this design)
}
```

---

### 2. Part-Whole Relationship

Composition is often used to model part-whole relationships. The parts are integral components of the whole within the modeled domain.

```kotlin
// Whole
class Computer(
    val brand: String
) {
    // Parts (owned by Computer in this model)
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
// CPU, RAM, Storage, Motherboard are modeled as parts of Computer in this design
```

Examples:
- `Car` HAS-A `Engine`, `Wheels`, `Transmission`
- `House` HAS-A `Room`, `Door`, `Window`
- `Computer` HAS-A `CPU`, `RAM`, `Storage`

---

### 3. Code Reuse

Composition enables code reuse by integrating objects created for specific functions into other classes.

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

Benefit: Logger, Validator, and DatabaseConnection can be reused across multiple services.

---

### 4. Avoiding Multiple Inheritance Problems

Some languages like Java and Kotlin don't support multiple class inheritance due to complexity and potential issues (diamond problem).

Composition provides a flexible alternative to achieve functionality from multiple sources.

```kotlin
// - BAD: Can't inherit from multiple classes in Kotlin
// class FlyingCar : Car, Aircraft { }  // Compilation error!

// - GOOD: Use composition
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

Kotlin Delegation makes this even easier:

```kotlin
// - BETTER: Kotlin-style composition via explicit delegation
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

Composition provides greater flexibility in software design because changes in one class have less impact on classes that use its objects.

```kotlin
// - Composition: Easy to swap payment methods
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

Benefit: Can change PaymentProcessor implementation without modifying OrderService.

---

## Composition Vs Inheritance

### Inheritance Example

```kotlin
// - Inheritance: Rigid hierarchy
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

// Problem: Deep hierarchies can be rigid and harder to change
```

### Composition Example

```kotlin
// - Composition: Flexible behavior
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
    // In a real app, provide UserRepository via DI or a factory
    private val viewModel: UserViewModel by viewModels {
        object : ViewModelProvider.Factory {
            override fun <T : ViewModel> create(modelClass: Class<T>): T {
                val repo = UserRepository(
                    UserRemoteDataSource(),
                    UserLocalDataSource(),
                    UserCache()
                )
                @Suppress("UNCHECKED_CAST")
                return UserViewModel(repo) as T
            }
        }
    }

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

### - DO

1. Favor composition over inheritance:
   ```kotlin
   // - Composition
   class Car(private val engine: Engine)

   // - Inheritance (incorrect modeling)
   class Car : Engine()  // Car IS-NOT-A Engine!
   ```

2. Use dependency injection:
   ```kotlin
   class UserService(
       private val repository: UserRepository,  // Injected
       private val logger: Logger               // Injected
   )
   ```

3. Program to interfaces:
   ```kotlin
   class OrderService(
       private val paymentProcessor: PaymentProcessor  // Interface
   )
   ```

4. Keep components focused:
   ```kotlin
   class UserValidator  // Only validates
   class UserRepository  // Only persists data
   class UserService    // Orchestrates
   ```

---

### - DON'T

1. Don't create god objects:
   ```kotlin
   // - BAD: Too many responsibilities
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

2. Don't use inheritance when composition fits better:
   ```kotlin
   // - BAD: Car IS-NOT-A Engine
   class Car : Engine()

   // - GOOD: Car HAS-A Engine
   class Car(private val engine: Engine)
   ```

---

## Summary

Class Composition:
- One class contains objects of other classes as fields
- Strong coupling - lifecycle dependency at the model level
- Part-whole relationship - components are integral parts
- Code reuse - reusable components
- Avoids multiple inheritance - flexible alternative
- Design flexibility - easy to change and test

Key benefits:
- Flexibility - easy to swap implementations
- Testability - easy to mock components
- Maintainability - changes localized
- Reusability - components can be reused

Best practice: Favor composition over inheritance for more flexible and maintainable code.

---

## Related Questions
- How does composition relate to [[c-composition]] and other object relationships?
- When would inheritance be preferable despite the benefits of composition?
- How would you refactor an inheritance-heavy hierarchy to use composition instead?
- How does composition help with adhering to SOLID principles?
- How is composition applied in designing services in layered or hexagonal architectures?

## References
- [[c-computer-science]]
- [[c-composition]]
