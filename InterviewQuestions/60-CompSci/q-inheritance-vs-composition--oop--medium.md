---
id: oop-001
title: "Inheritance Vs Composition / Наследование против композиции"
aliases: [Inheritance Vs Composition, Наследование против композиции]
topic: cs
subtopics: [c-cs, c-architecture-patterns, c-clean-code]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-computer-science, c-architecture-patterns, q-when-inheritance-useful--cs--medium]
created: 2025-10-13
updated: 2025-11-11
tags: [cs, difficulty/medium]

---

# Вопрос (RU)
> Какие отличия наследования от композиции?

# Question (EN)
> What are the differences between inheritance and composition?

---

## Ответ (RU)

**Наследование** — это когда один класс **расширяет** другой, наследуя его поведение (отношение IS-A).

**Композиция** — это когда один объект **включён в** другой, при этом зависимость явно передаётся (отношение HAS-A).

**Композиция считается более гибкой и менее связанной** по сравнению с наследованием.

## Answer (EN)

**Inheritance** is when one class **extends** another, inheriting its behavior (IS-A relationship).

**Composition** is when one object is **included in** another, with the dependency explicitly passed (HAS-A relationship).

**Composition is considered more flexible and less coupled** than inheritance.

---

## Ключевые Отличия (RU)

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

// Примечание: если Parent меняется, потомков нужно проверять и при необходимости обновлять
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

// Изменения Engine не влияют на Car, пока интерфейс стабилен
```

### 3. Гибкость

**Наследование: Фиксировано во время компиляции**

Отношение **статично** - определено при написании кода.

```kotlin
// Фиксированное поведение
open class Fighter

class Warrior : Fighter() {
    // Всегда использует Fighter как базовый тип
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
    override fun attack() = println("Произнесение заклинания")
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
character.attack()  // "Произнесение заклинания" - поведение изменилось!
```

### 4. Тестируемость

**Наследование: Сложнее тестировать**

Нужно учитывать поведение родителя и потомка вместе. Сложнее подменять поведение родителя.

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

// При прямом использовании требуется реальная база данных
// или дополнительные уровни абстракции/переопределения
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

Большинство языков (Java, Kotlin) не поддерживают множественное наследование реализации.

```kotlin
// Множественное наследование классов не разрешено в Kotlin/Java
class FlyingCar : Car(), Airplane {  // Airplane должен быть интерфейсом
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

---

## Key Differences (EN)

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

// Problem: If Parent changes, Child can break.
// Parent adds or changes behavior/signatures → all children must be reviewed/updated
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

### 3. Flexibility

**Inheritance: Fixed at Compile Time**

The relationship is **static** - defined when you write the code.

```kotlin
// - Fixed behavior
open class Fighter

class Warrior : Fighter() {
    // Always uses Fighter as base type
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

// Testing UserService directly hits the real database
// unless you introduce additional indirection/overrides
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

### 5. Multiple Behaviors

**Inheritance: Can't Inherit from Multiple Classes**

Most languages (Java, Kotlin) don't support multiple inheritance of implementation.

```kotlin
// - Multiple class inheritance not allowed in Kotlin/Java
class FlyingCar : Car(), Airplane {  // In Kotlin, Airplane must be an interface
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

## Таблица Сравнения (RU)

| Аспект | Наследование | Композиция |
|--------|-------------|------------|
| **Отношение** | IS-A (ЯВЛЯЕТСЯ) | HAS-A (ИМЕЕТ) |
| **Связанность** | Сильная (тесная) | Слабая (свободная) |
| **Гибкость** | Фиксирована при компиляции | Гибкая во время выполнения |
| **Тестируемость** | Часто сложнее | Проще (через внедрение) |
| **Множественное поведение** | Ограничено (нет множественного наследования классов) | Неограниченно |
| **Зависимость** | Неявная (встроенная) | Явная (внедрённая) |
| **Переиспользование** | От родителя к потомкам | Компоненты переиспользуются везде |
| **Сложность** | Может приводить к глубоким иерархиям | Обычно более плоский дизайн |

---

## Comparison Table (EN)

| Aspect | Inheritance | Composition |
|--------|------------|-------------|
| **Relationship** | IS-A | HAS-A |
| **Coupling** | Strong (tight) | Weak (loose) |
| **Flexibility** | Fixed at compile time | Flexible at runtime |
| **Testability** | Often harder | Easier (via injection) |
| **Multiple behaviors** | Limited (no multiple class inheritance in many languages) | Unlimited |
| **Dependency** | Implicit (built-in) | Explicit (injected) |
| **Reusability** | Parent → Children | Components reused anywhere |
| **Complexity** | Can lead to deep hierarchies | Typically flatter design |

---

## Примеры (RU)

### Пример Наследования

```kotlin
// Наследование
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

// Замечания:
// - Car и Motorcycle зависят от дизайна Vehicle
// - Глубокие или неверные иерархии усложняют переиспользование и сопровождение
```

### Пример Композиции

```kotlin
// Композиция
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

// Преимущества:
// - Слабая связанность
// - Легко менять реализации двигателей и колёс
// - Легко тестировать с mock-объектами
// - Поведение (Engine, Wheels) можно переиспользовать в других типах
```

---

## Examples (EN)

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

// Considerations:
// - Car and Motorcycle depend on Vehicle's design
// - Deep or incorrect hierarchies can make reuse and maintenance harder
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
// - Easy to swap engines
// - Easy to test with mocks
// - Behaviors (Engine, Wheels) can be shared by other types
```

---

## Android Example (RU)

### Подход с Наследованием (традиционный)

```kotlin
// Наследование: тесная связанность
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

// Замечания:
// - Все Activity зависят от BaseActivity
// - Изменения в BaseActivity затрагивают все наследники
// - Сложнее варьировать поведение для отдельных экранов
```

### Подход с Композицией (современный)

```kotlin
// Композиция: слабая связанность через внедрение зависимостей
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

class UserActivity : AppCompatActivity() {
    private val logger: Logger by lazy { AndroidLogger("UserActivity") }
    private val errorHandler: ErrorHandler by lazy { ToastErrorHandler(this) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        logger.log("UserActivity created")
    }
}

// Преимущества:
// - Нет жёсткой привязки к базовому классу для кросс-секционных задач
// - Легко подменять реализации (Logger, ErrorHandler)
// - Легко тестировать с mock-объектами
// - Разные Activity могут использовать разные реализации
```

---

## Android Example (EN)

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

// Considerations:
// - All activities depend on BaseActivity
// - Changing BaseActivity affects all subclasses
// - Harder to vary logging per-screen
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
// - No tight coupling to a base class for cross-cutting concerns
// - Easy to swap implementations (Logger, ErrorHandler)
// - Easy to test with mocks
// - Different activities can use different implementations
```

---

## Когда Использовать Каждый (RU)

### Используйте Наследование (когда это хорошо)

- Чёткое отношение **IS-A (ЯВЛЯЕТСЯ)**
- Нужен **полиморфизм** (обрабатывать Dog как Animal)
- **Расширение фреймворка/библиотеки** (`Activity`, `Fragment`)
- **Стабильная иерархия**, которая редко меняется

```kotlin
// Хорошее использование наследования
class MainActivity : AppCompatActivity() {
    // MainActivity ЯВЛЯЕТСЯ AppCompatActivity
}
```

### Используйте Композицию (когда это хорошо)

- Отношение **HAS-A (ИМЕЕТ)**
- Нужна **гибкость**
- Важно обеспечить **слабую связанность**
- Важна **тестируемость**
- Нужно комбинировать **множественное поведение**

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

---

## When to Use Each (EN)

### Use Inheritance (Good)

- Clear **IS-A** relationship
- Need **polymorphism** (treat Dog as Animal)
- **Framework/library extension** (`Activity`, `Fragment`)
- **Stable hierarchy** (won't change often)

```kotlin
// - Good use of inheritance
class MainActivity : AppCompatActivity() {
    // MainActivity IS-A AppCompatActivity
}
```

### Use Composition (Good)

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

## Лучшая Практика: Предпочитайте Композицию Наследованию (RU)

```kotlin
// Избегайте: Наследование для переиспользования кода
open class Logger {
    open fun log(message: String) {
        println(message)
    }
}

class UserService : Logger() {
    fun createUser(name: String) {
        log("Создание пользователя: $name")  // Наследует log()
    }
}

// Предпочитайте: Композицию с внедрением зависимостей
interface Logger2 {
    fun log(message: String)
}

class ConsoleLogger : Logger2 {
    override fun log(message: String) {
        println(message)
    }
}

class UserService2(private val logger: Logger2) {
    fun createUser(name: String) {
        logger.log("Создание пользователя: $name")  // Композиция logger
    }
}
```

**Почему композиция лучше во многих случаях:**
1. **Слабая связанность** - UserService2 не зависит от конкретной реализации Logger2
2. **Гибкость** - Можно легко заменить Logger2 (ConsoleLogger, FileLogger и т.д.)
3. **Тестируемость** - Можно внедрить MockLogger для тестирования
4. **Явная зависимость** - Logger2 явно передаётся, не скрыт в наследовании

---

## Best Practice: Favor Composition Over Inheritance (EN)

```kotlin
// - Avoid: Inheritance for code reuse
open class Logger {
    open fun log(message: String) {
        println(message)
    }
}

class UserService : Logger() {
    fun createUser(name: String) {
        log("Creating user: $name")  // Inheriting log()
    }
}

// - Prefer: Composition with dependency injection
interface Logger2 {
    fun log(message: String)
}

class ConsoleLogger : Logger2 {
    override fun log(message: String) {
        println(message)
    }
}

class UserService2(private val logger: Logger2) {
    fun createUser(name: String) {
        logger.log("Creating user: $name")  // Composing logger
    }
}
```

**Why composition is better in many cases:**
1. **Loose coupling** - UserService2 doesn't depend on a specific Logger2 implementation
2. **Flexibility** - Can swap Logger2 easily (ConsoleLogger, FileLogger, etc.)
3. **Testability** - Can inject MockLogger for testing
4. **Clear dependency** - Logger2 is explicitly passed, not hidden in inheritance

---

## Резюме (RU)

**Наследование:**
- Один класс **расширяет** другой (IS-A)
- **Более сильная связанность**, фиксировано при компиляции
- Может быть **сложнее тестировать**, гибкость ограничена при неправильном применении
- Используйте для **расширения фреймворка** и **чётких иерархий**

**Композиция:**
- Один объект **содержит** другой (HAS-A)
- **Более слабая связанность**, гибкость во время выполнения
- **Легко тестировать**, зависимости явные
- Используйте в **большинстве случаев**, особенно когда нужна гибкость

**Золотое правило:** "Предпочитайте композицию наследованию", если нет веских причин делать иначе.

Композиция считается **более гибкой и менее связанной**, чем наследование, что делает её предпочтительным выбором для многих сценариев проектирования.

---

## Summary (EN)

**Inheritance:**
- One class **extends** another (IS-A)
- **Stronger coupling**, fixed at compile time
- May be **harder to test**, limited flexibility if overused
- Use for **framework extension** and **clear hierarchies**

**Composition:**
- One object **contains** another (HAS-A)
- **Looser coupling**, flexible at runtime
- **Easy to test**, explicit dependencies
- Use for **most cases**, especially when you need flexibility

**Golden Rule:** "Favor composition over inheritance" when in doubt.

Composition is considered **more flexible and less coupled** than inheritance, making it the preferred choice for many design scenarios.

---

## Дополнительные вопросы (RU)

### Предпосылки (проще)
- [[q-java-all-classes-inherit-from-object--programming-languages--easy]]
- [[q-kotlin-enum-classes--kotlin--easy]]

### Связанные (средний уровень)
- [[q-when-inheritance-useful--cs--medium]]
- [[q-inheritance-composition-aggregation--oop--medium]]
- [[q-class-composition--oop--medium]]
- [[q-java-marker-interfaces--programming-languages--medium]]

---

## Follow-ups

### Prerequisites (Easier)
- [[q-java-all-classes-inherit-from-object--programming-languages--easy]]
- [[q-kotlin-enum-classes--kotlin--easy]]

### Related (Medium)
- [[q-when-inheritance-useful--cs--medium]]
- [[q-inheritance-composition-aggregation--oop--medium]]
- [[q-class-composition--oop--medium]]
- [[q-java-marker-interfaces--programming-languages--medium]]

---

## Related Questions

- [[q-when-inheritance-useful--cs--medium]]
- [[q-inheritance-composition-aggregation--oop--medium]]
- [[q-class-composition--oop--medium]]

---

## References

- [[c-computer-science]]
- [[c-architecture-patterns]]
