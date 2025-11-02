---
id: oop-001
title: "Inheritance Vs Composition / Наследование против композиции"
aliases: [Inheritance Vs Composition, Наследование против композиции]
topic: oop
subtopics: [inheritance, composition, relationships, design-patterns]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-oop
related: [c-inheritance, c-composition, q-inheritance-composition-aggregation--oop--medium, q-class-composition--oop--medium]
created: 2025-10-13
updated: 2025-10-31
tags: [oop, inheritance, composition, relationships, design-patterns, difficulty/medium]
---

# Какие Отличия Наследования От Композиции?

# Question (EN)
> What are the differences between inheritance and composition?

# Вопрос (RU)
> Какие отличия наследования от композиции?

---

## Answer (EN)

**Inheritance** is when one class **extends** another, inheriting its behavior (IS-A relationship).

**Composition** is when one object is **included in** another, with the dependency explicitly passed (HAS-A relationship).

**Composition is considered more flexible and less coupled** than inheritance.

## Key Differences

### 1. Relationship Type

**Inheritance: IS-A**
```kotlin
// Dog IS-A Animal
open class Animal {
    open fun makeSound() {
        println("Generic sound")
    }
}

class Dog : Animal() {
    override fun makeSound() {
        println("Woof!")
    }
}

val dog: Animal = Dog()  // Dog IS-A Animal
```

**Composition: HAS-A**
```kotlin
// Car HAS-A Engine
class Engine {
    fun start() {
        println("Engine started")
    }
}

class Car(private val engine: Engine) {  // Car HAS-A Engine
    fun start() {
        engine.start()
    }
}

val car = Car(Engine())
```

---

### 2. Coupling

**Inheritance: Strong Coupling**

The child class is **tightly coupled** to the parent class. Changes in the parent affect all children.

```kotlin
// - Strong coupling
open class Parent {
    open fun method1() = println("Parent method 1")
    open fun method2() = println("Parent method 2")
    open fun method3() = println("Parent method 3")
}

class Child : Parent() {
    override fun method1() = println("Child method 1")
    // Inherits method2 and method3
}

// Problem: If Parent changes, Child breaks!
// Parent adds new behavior → all children affected
// Parent changes method signature → all children must update
```

**Composition: Loose Coupling**

Objects are **loosely coupled**. Changes in composed objects have minimal impact.

```kotlin
// - Loose coupling
interface Engine {
    fun start()
}

class ElectricEngine : Engine {
    override fun start() = println("Electric engine started")
}

class GasEngine : Engine {
    override fun start() = println("Gas engine started")
}

class Car(private val engine: Engine) {  // Dependency injected
    fun start() = engine.start()
}

// Easy to swap implementations
val electricCar = Car(ElectricEngine())
val gasCar = Car(GasEngine())

// Engine changes don't affect Car (as long as interface is stable)
```

---

### 3. Flexibility

**Inheritance: Fixed at Compile Time**

The relationship is **static** - defined when you write the code.

```kotlin
// - Fixed behavior
class Warrior : Fighter() {
    // Always uses Fighter behavior
    // Cannot change at runtime
}

val warrior = Warrior()
// Warrior will always be a Fighter
```

**Composition: Flexible at Runtime**

Behavior can be **changed dynamically** at runtime.

```kotlin
// - Dynamic behavior
interface AttackStrategy {
    fun attack()
}

class SwordAttack : AttackStrategy {
    override fun attack() = println("Swing sword")
}

class MagicAttack : AttackStrategy {
    override fun attack() = println("Cast spell")
}

class Character(private var attackStrategy: AttackStrategy) {
    fun attack() = attackStrategy.attack()

    // Can change behavior at runtime!
    fun changeStrategy(newStrategy: AttackStrategy) {
        attackStrategy = newStrategy
    }
}

val character = Character(SwordAttack())
character.attack()  // "Swing sword"

character.changeStrategy(MagicAttack())
character.attack()  // "Cast spell"  - Behavior changed!
```

---

### 4. Testability

**Inheritance: Harder to Test**

Must test parent and child together. Hard to mock parent behavior.

```kotlin
// - Hard to test
open class DatabaseService {
    open fun save(data: String) {
        // Real database call
        connectToDatabase()
        executeQuery("INSERT INTO table VALUES ($data)")
    }
}

class UserService : DatabaseService() {
    fun createUser(name: String) {
        save(name)  // Calls real database!
    }
}

// Testing UserService requires real database
// Hard to mock save() method
```

**Composition: Easy to Test**

Can easily inject mocks/fakes.

```kotlin
// - Easy to test
interface DatabaseService {
    fun save(data: String)
}

class RealDatabaseService : DatabaseService {
    override fun save(data: String) {
        // Real database call
    }
}

class UserService(private val database: DatabaseService) {
    fun createUser(name: String) {
        database.save(name)
    }
}

// Testing - inject mock
class MockDatabaseService : DatabaseService {
    override fun save(data: String) {
        println("Mock: saved $data")
    }
}

val userService = UserService(MockDatabaseService())
userService.createUser("Alice")  // Uses mock, no real database!
```

---

### 5. Multiple Behaviors

**Inheritance: Can't Inherit from Multiple Classes**

Most languages (Java, Kotlin) don't support multiple inheritance.

```kotlin
// - Multiple inheritance not allowed
class FlyingCar : Car, Airplane {  // Compilation error!
    // ...
}
```

**Composition: Can Compose Multiple Objects**

Can easily combine behaviors from multiple sources.

```kotlin
// - Multiple composition
class FlyingCar(
    private val carEngine: CarEngine,
    private val wings: Wings,
    private val propeller: Propeller
) {
    fun drive() = carEngine.start()
    fun fly() {
        wings.extend()
        propeller.spin()
    }
}
```

---

## Comparison Table

| Aspect | Inheritance | Composition |
|--------|------------|-------------|
| **Relationship** | IS-A | HAS-A |
| **Coupling** | Strong (tight) | Weak (loose) |
| **Flexibility** | Fixed at compile time | Flexible at runtime |
| **Testability** | Hard to mock | Easy to mock |
| **Multiple behaviors** | Limited (single inheritance) | Unlimited |
| **Dependency** | Implicit (built-in) | Explicit (injected) |
| **Reusability** | Parent → Children | Components reused anywhere |
| **Complexity** | Can lead to deep hierarchies | Flat, simple design |

---

## Examples

### Inheritance Example

```kotlin
// Inheritance
abstract class Vehicle(val brand: String) {
    abstract fun start()

    fun stop() {
        println("$brand vehicle stopped")
    }
}

class Car(brand: String) : Vehicle(brand) {
    override fun start() {
        println("$brand car started")
    }
}

class Motorcycle(brand: String) : Vehicle(brand) {
    override fun start() {
        println("$brand motorcycle started")
    }
}

// Problems:
// - Car and Motorcycle tightly coupled to Vehicle
// - Can't share behaviors between Car and Boat (Boat is not a Vehicle)
// - Hard to test in isolation
```

### Composition Example

```kotlin
// Composition
interface Engine {
    fun start()
}

interface Wheels {
    fun rotate()
}

class V8Engine : Engine {
    override fun start() = println("V8 engine started")
}

class ElectricEngine : Engine {
    override fun start() = println("Electric engine started")
}

class FourWheels : Wheels {
    override fun rotate() = println("4 wheels rotating")
}

class Car(
    private val engine: Engine,
    private val wheels: Wheels
) {
    fun drive() {
        engine.start()
        wheels.rotate()
    }
}

// Benefits:
// - Loose coupling
// - Easy to swap engines: Car(V8Engine(), ...) or Car(ElectricEngine(), ...)
// - Easy to test with mocks
// - Behaviors can be shared (Boat can also have Engine)
```

---

## Android Example

### Inheritance Approach (Traditional)

```kotlin
// - Inheritance: Tightly coupled
abstract class BaseActivity : AppCompatActivity() {
    protected val logger = Logger()

    protected fun showError(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }

    protected fun logEvent(event: String) {
        logger.log(event)
    }
}

class UserActivity : BaseActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        logEvent("UserActivity created")
    }
}

class ProductActivity : BaseActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        logEvent("ProductActivity created")
    }
}

// Problems:
// - All activities inherit from BaseActivity
// - Hard to change logging mechanism
// - Can't test activities without BaseActivity
// - Can't use different loggers for different activities
```

### Composition Approach (Modern)

```kotlin
// - Composition: Loose coupling with dependency injection
interface Logger {
    fun log(message: String)
}

interface ErrorHandler {
    fun showError(message: String)
}

class AndroidLogger(private val tag: String) : Logger {
    override fun log(message: String) {
        Log.d(tag, message)
    }
}

class ToastErrorHandler(private val context: Context) : ErrorHandler {
    override fun showError(message: String) {
        Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
    }
}

// Inject dependencies
class UserActivity : AppCompatActivity() {
    private val logger: Logger by lazy { AndroidLogger("UserActivity") }
    private val errorHandler: ErrorHandler by lazy { ToastErrorHandler(this) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        logger.log("UserActivity created")
    }
}

// Benefits:
// - No base class coupling
// - Easy to swap implementations (Logger, ErrorHandler)
// - Easy to test with mocks
// - Different activities can use different implementations
```

---

## When to Use Each

### Use Inheritance GOOD

- Clear **IS-A** relationship
- Need **polymorphism** (treat Dog as Animal)
- **Framework/library extension** (Activity, Fragment)
- **Stable hierarchy** (won't change often)

```kotlin
// - Good use of inheritance
class MainActivity : AppCompatActivity() {
    // MainActivity IS-A AppCompatActivity
}
```

### Use Composition GOOD

- **HAS-A** relationship
- Need **flexibility**
- Want **loose coupling**
- Need **testability**
- Combining **multiple behaviors**

```kotlin
// - Good use of composition
class OrderService(
    private val paymentProcessor: PaymentProcessor,
    private val emailService: EmailService,
    private val logger: Logger
) {
    // OrderService HAS-A PaymentProcessor, EmailService, Logger
}
```

---

## Best Practice: Favor Composition Over Inheritance

```kotlin
// - Avoid: Inheritance for code reuse
class UserService : Logger() {
    fun createUser(name: String) {
        log("Creating user: $name")  // Inheriting log()
    }
}

// - Prefer: Composition with dependency injection
class UserService(private val logger: Logger) {
    fun createUser(name: String) {
        logger.log("Creating user: $name")  // Composing logger
    }
}
```

**Why composition is better:**
1. **Loose coupling** - UserService doesn't depend on Logger implementation
2. **Flexibility** - Can swap Logger easily (ConsoleLogger, FileLogger, etc.)
3. **Testability** - Can inject MockLogger for testing
4. **Clear dependency** - Logger is explicitly passed, not hidden in inheritance

---

## Summary

**Inheritance:**
- One class **extends** another (IS-A)
- **Strong coupling**, fixed at compile time
- **Hard to test**, limited flexibility
- Use for **framework extension** and **clear hierarchies**

**Composition:**
- One object **contains** another (HAS-A)
- **Loose coupling**, flexible at runtime
- **Easy to test**, explicit dependencies
- Use for **most cases**, especially when need flexibility

**Golden Rule:** **"Favor composition over inheritance"**

Composition is considered **more flexible and less coupled** than inheritance, making it the preferred choice for most design scenarios.

---

## Ответ (RU)

**Наследование** — это когда один класс **расширяет** другой, наследуя его поведение (отношение IS-A).

**Композиция** — это когда один объект **включён в** другой, при этом зависимость явно передаётся (отношение HAS-A).

**Композиция считается более гибкой и менее связанной** по сравнению с наследованием.

## Ключевые Отличия

### 1. Тип Отношения

**Наследование: IS-A (ЯВЛЯЕТСЯ)**
```kotlin
// Dog ЯВЛЯЕТСЯ Animal
open class Animal {
    open fun makeSound() {
        println("Общий звук")
    }
}

class Dog : Animal() {
    override fun makeSound() {
        println("Гав!")
    }
}

val dog: Animal = Dog()  // Dog ЯВЛЯЕТСЯ Animal
```

**Композиция: HAS-A (ИМЕЕТ)**
```kotlin
// Car ИМЕЕТ Engine
class Engine {
    fun start() {
        println("Двигатель запущен")
    }
}

class Car(private val engine: Engine) {  // Car ИМЕЕТ Engine
    fun start() {
        engine.start()
    }
}

val car = Car(Engine())
```

### 2. Связанность

**Наследование: Сильная связанность**

Дочерний класс **тесно связан** с родительским классом. Изменения в родителе влияют на всех потомков.

```kotlin
// Сильная связанность
open class Parent {
    open fun method1() = println("Родительский метод 1")
    open fun method2() = println("Родительский метод 2")
    open fun method3() = println("Родительский метод 3")
}

class Child : Parent() {
    override fun method1() = println("Дочерний метод 1")
    // Наследует method2 и method3
}

// Проблема: Если Parent изменится, Child сломается!
// Parent добавляет новое поведение → все потомки затронуты
// Parent изменяет сигнатуру метода → все потомки должны обновиться
```

**Композиция: Слабая связанность**

Объекты **слабо связаны**. Изменения в компонуемых объектах имеют минимальное влияние.

```kotlin
// Слабая связанность
interface Engine {
    fun start()
}

class ElectricEngine : Engine {
    override fun start() = println("Электрический двигатель запущен")
}

class GasEngine : Engine {
    override fun start() = println("Бензиновый двигатель запущен")
}

class Car(private val engine: Engine) {  // Зависимость внедрена
    fun start() = engine.start()
}

// Легко менять реализации
val electricCar = Car(ElectricEngine())
val gasCar = Car(GasEngine())

// Изменения Engine не влияют на Car (пока интерфейс стабилен)
```

### 3. Гибкость

**Наследование: Фиксировано во время компиляции**

Отношение **статично** - определено при написании кода.

```kotlin
// Фиксированное поведение
class Warrior : Fighter() {
    // Всегда использует поведение Fighter
    // Нельзя изменить во время выполнения
}

val warrior = Warrior()
// Warrior всегда будет Fighter
```

**Композиция: Гибко во время выполнения**

Поведение может быть **изменено динамически** во время выполнения.

```kotlin
// Динамическое поведение
interface AttackStrategy {
    fun attack()
}

class SwordAttack : AttackStrategy {
    override fun attack() = println("Замах мечом")
}

class MagicAttack : AttackStrategy {
    override fun attack() = println("Произношение заклинания")
}

class Character(private var attackStrategy: AttackStrategy) {
    fun attack() = attackStrategy.attack()

    // Можно изменить поведение во время выполнения!
    fun changeStrategy(newStrategy: AttackStrategy) {
        attackStrategy = newStrategy
    }
}

val character = Character(SwordAttack())
character.attack()  // "Замах мечом"

character.changeStrategy(MagicAttack())
character.attack()  // "Произношение заклинания" - Поведение изменилось!
```

### 4. Тестируемость

**Наследование: Сложнее тестировать**

Нужно тестировать родителя и потомка вместе. Сложно подменять поведение родителя.

```kotlin
// Сложно тестировать
open class DatabaseService {
    open fun save(data: String) {
        // Реальный вызов базы данных
        connectToDatabase()
        executeQuery("INSERT INTO table VALUES ($data)")
    }
}

class UserService : DatabaseService() {
    fun createUser(name: String) {
        save(name)  // Вызывает реальную базу данных!
    }
}

// Тестирование UserService требует реальной базы данных
// Сложно подменить метод save()
```

**Композиция: Легко тестировать**

Можно легко внедрять mock/fake объекты.

```kotlin
// Легко тестировать
interface DatabaseService {
    fun save(data: String)
}

class RealDatabaseService : DatabaseService {
    override fun save(data: String) {
        // Реальный вызов базы данных
    }
}

class UserService(private val database: DatabaseService) {
    fun createUser(name: String) {
        database.save(name)
    }
}

// Тестирование - внедрить mock
class MockDatabaseService : DatabaseService {
    override fun save(data: String) {
        println("Mock: сохранено $data")
    }
}

val userService = UserService(MockDatabaseService())
userService.createUser("Alice")  // Использует mock, реальной базы не нужно!
```

### 5. Множественное Поведение

**Наследование: Нельзя наследоваться от нескольких классов**

Большинство языков (Java, Kotlin) не поддерживают множественное наследование.

```kotlin
// Множественное наследование не разрешено
class FlyingCar : Car, Airplane {  // Ошибка компиляции!
    // ...
}
```

**Композиция: Можно компоновать несколько объектов**

Можно легко комбинировать поведение из нескольких источников.

```kotlin
// Множественная композиция
class FlyingCar(
    private val carEngine: CarEngine,
    private val wings: Wings,
    private val propeller: Propeller
) {
    fun drive() = carEngine.start()
    fun fly() {
        wings.extend()
        propeller.spin()
    }
}
```

## Таблица Сравнения

| Аспект | Наследование | Композиция |
|--------|-------------|------------|
| **Отношение** | IS-A (ЯВЛЯЕТСЯ) | HAS-A (ИМЕЕТ) |
| **Связанность** | Сильная (тесная) | Слабая (свободная) |
| **Гибкость** | Фиксирована при компиляции | Гибкая во время выполнения |
| **Тестируемость** | Сложно подменять | Легко подменять |
| **Множественное поведение** | Ограничено (одиночное наследование) | Неограниченно |
| **Зависимость** | Неявная (встроенная) | Явная (внедрённая) |
| **Переиспользование** | Родитель → Потомки | Компоненты переиспользуются везде |
| **Сложность** | Может привести к глубоким иерархиям | Плоский, простой дизайн |

### Когда Использовать Каждый

**Используйте Наследование:**
- Чёткое отношение **IS-A (ЯВЛЯЕТСЯ)**
- Нужен **полиморфизм** (обрабатывать Dog как Animal)
- **Расширение фреймворка/библиотеки** (Activity, Fragment)
- **Стабильная иерархия** (не будет часто меняться)

```kotlin
// Хорошее использование наследования
class MainActivity : AppCompatActivity() {
    // MainActivity ЯВЛЯЕТСЯ AppCompatActivity
}
```

**Используйте Композицию:**
- Отношение **HAS-A (ИМЕЕТ)**
- Нужна **гибкость**
- Требуется **слабая связанность**
- Нужна **тестируемость**
- Комбинирование **множественного поведения**

```kotlin
// Хорошее использование композиции
class OrderService(
    private val paymentProcessor: PaymentProcessor,
    private val emailService: EmailService,
    private val logger: Logger
) {
    // OrderService ИМЕЕТ PaymentProcessor, EmailService, Logger
}
```

## Лучшая Практика: Предпочитайте Композицию Наследованию

```kotlin
// Избегайте: Наследование для переиспользования кода
class UserService : Logger() {
    fun createUser(name: String) {
        log("Создание пользователя: $name")  // Наследование log()
    }
}

// Предпочитайте: Композицию с внедрением зависимостей
class UserService(private val logger: Logger) {
    fun createUser(name: String) {
        logger.log("Создание пользователя: $name")  // Композиция logger
    }
}
```

**Почему композиция лучше:**
1. **Слабая связанность** - UserService не зависит от реализации Logger
2. **Гибкость** - Можно легко заменить Logger (ConsoleLogger, FileLogger и т.д.)
3. **Тестируемость** - Можно внедрить MockLogger для тестирования
4. **Явная зависимость** - Logger явно передаётся, не скрыт в наследовании

## Резюме

**Наследование:**
- Один класс **расширяет** другой (IS-A)
- **Сильная связанность**, фиксировано при компиляции
- **Сложно тестировать**, ограниченная гибкость
- Используйте для **расширения фреймворка** и **чётких иерархий**

**Композиция:**
- Один объект **содержит** другой (HAS-A)
- **Слабая связанность**, гибко во время выполнения
- **Легко тестировать**, явные зависимости
- Используйте для **большинства случаев**, особенно когда нужна гибкость

**Золотое правило:** **"Предпочитайте композицию наследованию"**

Композиция считается **более гибкой и менее связанной** чем наследование, что делает её предпочтительным выбором для большинства сценариев проектирования.


---

## Related Questions

### Prerequisites (Easier)
- [[q-java-all-classes-inherit-from-object--programming-languages--easy]] - Inheritance
- [[q-kotlin-enum-classes--kotlin--easy]] - Enums

### Related (Medium)
- [[q-when-inheritance-useful--oop--medium]] - Inheritance
- [[q-inheritance-composition-aggregation--oop--medium]] - Inheritance
- [[q-class-composition--oop--medium]] - Inheritance
- [[q-java-marker-interfaces--programming-languages--medium]] - Inheritance
