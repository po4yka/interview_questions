---
id: cs-060
title: "SOLID Principles / Принципы SOLID"
aliases: [SOLID Principles, Принципы SOLID]
topic: cs
subtopics: [c-cs, c-architecture-patterns, c-clean-code]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-architecture-patterns, q-softcode-vs-hardcode--software-design--medium]
created: 2025-10-13
updated: 2025-11-11
tags: [architecture, design-principles, difficulty/medium, dip, isp, lsp, ocp, oop, solid, srp]

---

# Вопрос (RU)
> Что такое принципы SOLID?

# Question (EN)
> What are the SOLID principles?

## Ответ (RU)
Принципы SOLID — это пять основных принципов объектно-ориентированного программирования и проектирования, направленные на улучшение читаемости, масштабируемости и поддерживаемости кода, а также упрощение его тестирования и рефакторинга.

Эти принципы были сформулированы и популяризированы Робертом Мартином (Uncle Bob) и образуют акроним SOLID:

### Пять принципов SOLID (RU)

#### 1. S - Single Responsibility Principle (SRP) — Принцип единственной ответственности

Принцип: класс должен иметь только одну причину для изменения.

Смысл: у класса должна быть одна ответственность и он должен хорошо выполнять одну задачу.

##### Плохой пример: несколько ответственностей в одном классе

```kotlin
// Класс одновременно отвечает за данные пользователя, валидацию, доступ к БД,
// отправку писем и логирование — нарушение SRP
class User(
    var name: String,
    var email: String
) {
    fun validateEmail(): Boolean {
        return email.contains("@")
    }

    fun saveToDatabase() {
        val db = Database.getInstance()
        db.execute("INSERT INTO users VALUES ('$name', '$email')")
    }

    fun sendWelcomeEmail() {
        EmailService.send(email, "Welcome!")
    }

    fun logActivity() {
        Logger.log("User $name performed action")
    }
}
```

##### Хороший пример: одна ответственность на класс

```kotlin
// User — только данные пользователя
data class User(
    val id: String,
    val name: String,
    val email: String
)

// UserValidator — только валидация
class UserValidator {
    fun validateEmail(email: String): Boolean {
        return email.matches(Regex("^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+$"))
    }

    fun validateName(name: String): Boolean {
        return name.isNotBlank() && name.length >= 2
    }
}

// UserRepository — только работа с данными
class UserRepository(private val database: Database) {
    suspend fun save(user: User) {
        database.userDao().insert(user.toEntity())
    }

    suspend fun findById(id: String): User? {
        return database.userDao().findById(id)?.toDomain()
    }

    suspend fun findAll(): List<User> {
        return database.userDao().findAll().map { it.toDomain() }
    }
}

// UserNotificationService — только уведомления
class UserNotificationService(private val emailService: EmailService) {
    suspend fun sendWelcomeEmail(user: User) {
        emailService.send(
            to = user.email,
            subject = "Welcome!",
            body = "Hello ${user.name}, welcome to our app!"
        )
    }
}

// UserActivityLogger — только логирование
class UserActivityLogger(private val logger: Logger) {
    fun logUserAction(user: User, action: String) {
        logger.info("User ${user.name} (${user.id}): $action")
    }
}
```

Преимущества:
- у каждого класса одна причина для изменения;
- проще тестировать по отдельности;
- ясное разделение обязанностей.

#### 2. O - Open/Closed Principle (OCP) — Принцип открытости/закрытости

Принцип: сущности должны быть открыты для расширения, но закрыты для модификации.

Смысл: можно добавлять новый функционал без изменения уже существующего кода.

##### Плохой пример: требуется постоянно менять класс

```kotlin
// Добавление нового способа оплаты требует изменения этого класса
class PaymentProcessor {
    fun processPayment(type: String, amount: Double) {
        when (type) {
            "credit_card" -> {
                println("Processing credit card payment: $amount")
            }
            "paypal" -> {
                println("Processing PayPal payment: $amount")
            }
            "bitcoin" -> {
                println("Processing Bitcoin payment: $amount")
            }
            else -> throw IllegalArgumentException("Unknown payment type")
        }
    }
}
```

##### Хороший пример: открыто для расширения

```kotlin
// Абстракция способа оплаты
interface PaymentMethod {
    fun processPayment(amount: Double)
}

class CreditCardPayment : PaymentMethod {
    override fun processPayment(amount: Double) {
        println("Processing credit card payment: $amount")
    }
}

class PayPalPayment : PaymentMethod {
    override fun processPayment(amount: Double) {
        println("Processing PayPal payment: $amount")
    }
}

class BitcoinPayment : PaymentMethod {
    override fun processPayment(amount: Double) {
        println("Processing Bitcoin payment: $amount")
    }
}

class PaymentProcessor {
    fun processPayment(paymentMethod: PaymentMethod, amount: Double) {
        paymentMethod.processPayment(amount)
    }
}
```

Преимущества:
- добавление новых реализаций без изменения существующего кода;
- стабильность и предсказуемость поведения.

#### 3. L - Liskov Substitution Principle (LSP) — Принцип подстановки Барбары Лисков

Принцип: подтипы должны быть взаимозаменяемы с базовыми типами.

Смысл: если `B` наследуется от `A`, то `B` можно использовать везде, где ожидается `A`, без нарушения корректности.

##### Плохой пример: нарушение LSP

```kotlin
open class Bird {
    open fun fly() {
        println("Flying...")
    }
}

class Sparrow : Bird() {
    override fun fly() {
        println("Sparrow flying")
    }
}

// Penguin нарушает ожидания базового типа
class Penguin : Bird() {
    override fun fly() {
        throw UnsupportedOperationException("Penguins can't fly!")
    }
}

fun makeBirdFly(bird: Bird) {
    bird.fly() // с Penguin приведет к исключению
}
```

##### Хороший пример: корректная иерархия

```kotlin
abstract class Bird {
    abstract fun move()
}

interface Flyable {
    fun fly()
}

class Sparrow : Bird(), Flyable {
    override fun move() {
        fly()
    }

    override fun fly() {
        println("Sparrow flying")
    }
}

class Penguin : Bird() {
    override fun move() {
        swim()
    }

    fun swim() {
        println("Penguin swimming")
    }
}

fun makeBirdMove(bird: Bird) {
    bird.move()
}

fun makeFlyableFly(flyable: Flyable) {
    flyable.fly()
}
```

Преимущества:
- предсказуемый полиморфизм;
- отсутствие неожиданных ошибок времени выполнения.

#### 4. I - Interface Segregation Principle (ISP) — Принцип разделения интерфейса

Принцип: клиенты не должны зависеть от интерфейсов, которые они не используют.

Смысл: лучше много маленьких специализированных интерфейсов, чем один «толстый».

##### Плохой пример: «жирный» интерфейс

```kotlin
interface Worker {
    fun work()
    fun eat()
    fun sleep()
    fun getSalary()
    fun attendMeeting()
}

class Robot : Worker {
    override fun work() {
        println("Robot working")
    }

    override fun eat() {
        throw UnsupportedOperationException("Robots don't eat")
    }

    override fun sleep() {
        throw UnsupportedOperationException("Robots don't sleep")
    }

    override fun getSalary() {
        throw UnsupportedOperationException("Robots don't get salary")
    }

    override fun attendMeeting() {
        throw UnsupportedOperationException("Robots don't attend meetings")
    }
}
```

##### Хороший пример: разделенные интерфейсы

```kotlin
interface Workable {
    fun work()
}

interface Eatable {
    fun eat()
}

interface Sleepable {
    fun sleep()
}

interface Payable {
    fun getSalary()
}

interface MeetingAttendee {
    fun attendMeeting()
}

class Human : Workable, Eatable, Sleepable, Payable, MeetingAttendee {
    override fun work() { println("Human working") }
    override fun eat() { println("Human eating") }
    override fun sleep() { println("Human sleeping") }
    override fun getSalary() { println("Human receiving salary") }
    override fun attendMeeting() { println("Human attending meeting") }
}

class Robot : Workable {
    override fun work() { println("Robot working") }
}

class Manager : Workable, Eatable, Sleepable, Payable, MeetingAttendee {
    override fun work() { println("Manager managing") }
    override fun eat() { println("Manager eating") }
    override fun sleep() { println("Manager sleeping") }
    override fun getSalary() { println("Manager receiving salary") }
    override fun attendMeeting() { println("Manager leading meeting") }
}
```

Преимущества:
- классы реализуют только нужные методы;
- меньше пустых или фиктивных реализаций;
- лучшее разделение ролей.

#### 5. D - Dependency Inversion Principle (DIP) — Принцип инверсии зависимостей

Принцип:
- высокоуровневые модули не должны зависеть от низкоуровневых, оба должны зависеть от абстракций;
- абстракции не должны зависеть от деталей, детали должны зависеть от абстракций.

Смысл: зависеть от интерфейсов, а не от конкретных реализаций; использовать внедрение зависимостей.

##### Плохой пример: зависимость от конкретной реализации

```kotlin
class MySQLDatabase {
    fun save(data: String) {
        println("Saving to MySQL: $data")
    }

    fun fetch(id: String): String {
        return "Data from MySQL"
    }
}

class UserService {
    private val database = MySQLDatabase() // тесная связь

    fun saveUser(user: String) {
        database.save(user)
    }

    fun getUser(id: String): String {
        return database.fetch(id)
    }
}
```

##### Хороший пример: зависимость от абстракции

```kotlin
interface Database {
    fun save(data: String)
    fun fetch(id: String): String
}

class MySQLDatabase : Database {
    override fun save(data: String) {
        println("Saving to MySQL: $data")
    }

    override fun fetch(id: String): String {
        return "Data from MySQL: $id"
    }
}

class PostgreSQLDatabase : Database {
    override fun save(data: String) {
        println("Saving to PostgreSQL: $data")
    }

    override fun fetch(id: String): String {
        return "Data from PostgreSQL: $id"
    }
}

class MongoDBDatabase : Database {
    override fun save(data: String) {
        println("Saving to MongoDB: $data")
    }

    override fun fetch(id: String): String {
        return "Data from MongoDB: $id"
    }
}

class UserService(private val database: Database) {
    fun saveUser(user: String) {
        database.save(user)
    }

    fun getUser(id: String): String {
        return database.fetch(id)
    }
}
```

Преимущества:
- слабое зацепление;
- легкая подмена реализаций (в том числе в тестах);
- более гибкая архитектура.

### Краткое резюме SOLID (RU)

| Принцип                        | Буква | Ключевая идея                                   | Польза                              |
|--------------------------------|-------|-------------------------------------------------|-------------------------------------|
| Single Responsibility          | S     | Один класс — одна ответственность              | Понятность и поддерживаемость       |
| Open/Closed                    | O     | Открыт для расширения, закрыт для модификации  | Добавление фич без ломки старого    |
| Liskov Substitution            | L     | Подтипы заменяют базовый тип без сюрпризов     | Корректный полиморфизм              |
| Interface Segregation          | I     | Много маленьких интерфейсов лучше одного большого | Нет лишних зависимостей         |
| Dependency Inversion           | D     | Зависимость от абстракций, а не реализаций     | Гибкость и тестируемость            |

### Пример для Android: Полное SOLID-приложение (RU)

```kotlin
// Доменный слой — сущность пользователя
data class User(
    val id: String,
    val name: String,
    val email: String
)

// DIP: абстракция репозитория пользователя
interface UserRepository {
    suspend fun save(user: User)
    suspend fun findById(id: String): User?
    suspend fun findAll(): List<User>
}

// Реализация на Room
class RoomUserRepository(
    private val userDao: UserDao
) : UserRepository {
    override suspend fun save(user: User) {
        userDao.insert(user.toEntity())
    }

    override suspend fun findById(id: String): User? {
        return userDao.findById(id)?.toDomain()
    }

    override suspend fun findAll(): List<User> {
        return userDao.findAll().map { it.toDomain() }
    }
}

// OCP: правила валидации расширяем без изменения интерфейса
interface ValidationRule<T> {
    fun validate(value: T): Boolean
    fun errorMessage(): String
}

class EmailValidationRule : ValidationRule<String> {
    override fun validate(value: String): Boolean {
        return value.matches(Regex("^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+$"))
    }

    override fun errorMessage() = "Invalid email format"
}

class NameValidationRule : ValidationRule<String> {
    override fun validate(value: String): Boolean {
        return value.isNotBlank() && value.length >= 2
    }

    override fun errorMessage() = "Name must be at least 2 characters"
}

class UserValidator {
    private val emailRule = EmailValidationRule()
    private val nameRule = NameValidationRule()

    fun validate(user: User): List<String> {
        val errors = mutableListOf<String>()

        if (!emailRule.validate(user.email)) {
            errors.add(emailRule.errorMessage())
        }

        if (!nameRule.validate(user.name)) {
            errors.add(nameRule.errorMessage())
        }

        return errors
    }
}

// ISP: разделяем чтение и запись при необходимости
interface UserReader {
    suspend fun findById(id: String): User?
    suspend fun findAll(): List<User>
}

interface UserWriter {
    suspend fun save(user: User)
    suspend fun delete(id: String)
}

interface ReadOnlyUserRepository : UserReader
interface WriteOnlyUserRepository : UserWriter

// Сервис уведомлений
class UserNotificationService(private val emailService: EmailService) {
    suspend fun sendWelcomeEmail(user: User) {
        emailService.send(
            to = user.email,
            subject = "Welcome!",
            body = "Hello ${user.name}, welcome to our app!"
        )
    }
}

// Use case: создание пользователя (SRP + DIP)
class CreateUserUseCase(
    private val repository: UserRepository,
    private val validator: UserValidator,
    private val notificationService: UserNotificationService
) {
    suspend operator fun invoke(name: String, email: String): Result<User> {
        val user = User(
            id = UUID.randomUUID().toString(),
            name = name,
            email = email
        )

        val errors = validator.validate(user)
        if (errors.isNotEmpty()) {
            return Result.failure(ValidationException(errors))
        }

        repository.save(user)
        notificationService.sendWelcomeEmail(user)
        return Result.success(user)
    }
}

class GetUsersUseCase(
    private val repository: UserRepository
) {
    suspend operator fun invoke(): List<User> = repository.findAll()
}

// ViewModel — использует абстракции и DI
class UserViewModel(
    private val createUserUseCase: CreateUserUseCase,
    private val getUsersUseCase: GetUsersUseCase
) : ViewModel() {

    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()

    fun createUser(name: String, email: String) {
        viewModelScope.launch {
            createUserUseCase(name, email)
                .onSuccess { user ->
                    _users.value = _users.value + user
                }
                .onFailure {
                    // обработка ошибок
                }
        }
    }

    fun loadUsers() {
        viewModelScope.launch {
            _users.value = getUsersUseCase()
        }
    }
}
```

### Преимущества SOLID (RU)

1. Улучшенная поддерживаемость: изменения локализованы и предсказуемы.
2. Масштабируемость: проще добавлять новые функции и варианты поведения.
3. Тестируемость: зависимости абстрагированы, классы изолированы.
4. Читаемость: структура кода отражает обязанности.
5. Гибкость: легче адаптироваться к новым требованиям.
6. Снижение связности: компоненты слабо связаны.
7. Повторное использование: модули можно применять в разных контекстах.

### Дополнительные вопросы (RU)

- Как принципы SOLID связаны с Clean Architecture на практике?
- Приведите пример, когда чрезмерное применение SOLID приводит к оверинжинирингу.
- Как вы бы рефакторили "God object" с помощью SOLID?

### Связанные вопросы (RU)

- Как принципы SOLID связаны с Clean Architecture на практике?
- Приведите пример, когда чрезмерное применение SOLID приводит к оверинжинирингу.
- Как вы бы рефакторили "God object" с помощью SOLID?

### Ссылки (RU)

- [[c-architecture-patterns]]

---

## Answer (EN)
SOLID is an acronym for five fundamental principles of object-oriented programming and design that improve code readability, scalability, maintainability, and simplify testing and refactoring.

These principles were formulated and popularized by Robert C. Martin (Uncle Bob).

### The Five SOLID Principles

#### 1. S - Single Responsibility Principle (SRP)

Principle: A class should have only one reason to change.

Meaning: Each class should have one responsibility and do one thing well.

##### BAD: Multiple Responsibilities

```kotlin
// - Class handles both user data AND persistence
class User(
    var name: String,
    var email: String
) {
    fun validateEmail(): Boolean {
        return email.contains("@")
    }

    // - Database logic in User class
    fun saveToDatabase() {
        val db = Database.getInstance()
        db.execute("INSERT INTO users VALUES ('$name', '$email')")
    }

    // - Email sending logic in User class
    fun sendWelcomeEmail() {
        EmailService.send(email, "Welcome!")
    }

    // - Logging in User class
    fun logActivity() {
        Logger.log("User $name performed action")
    }
}
```

##### GOOD: Single Responsibility

```kotlin
// - User class - only user data
data class User(
    val id: String,
    val name: String,
    val email: String
)

// - UserValidator - only validation
class UserValidator {
    fun validateEmail(email: String): Boolean {
        // Simplified example regex for demonstration purposes
        return email.matches(Regex("^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+$"))
    }

    fun validateName(name: String): Boolean {
        return name.isNotBlank() && name.length >= 2
    }
}

// - UserRepository - only data persistence
class UserRepository(private val database: Database) {
    suspend fun save(user: User) {
        database.userDao().insert(user.toEntity())
    }

    suspend fun findById(id: String): User? {
        return database.userDao().findById(id)?.toDomain()
    }

    suspend fun findAll(): List<User> {
        return database.userDao().findAll().map { it.toDomain() }
    }
}

// - UserNotificationService - only notifications
class UserNotificationService(private val emailService: EmailService) {
    suspend fun sendWelcomeEmail(user: User) {
        emailService.send(
            to = user.email,
            subject = "Welcome!",
            body = "Hello ${user.name}, welcome to our app!"
        )
    }
}

// - UserActivityLogger - only logging
class UserActivityLogger(private val logger: Logger) {
    fun logUserAction(user: User, action: String) {
        logger.info("User ${user.name} (${user.id}): $action")
    }
}
```

Benefits:
- Each class has one reason to change
- Easy to test in isolation
- Clear separation of concerns

---

#### 2. O - Open/Closed Principle (OCP)

Principle: Software entities should be open for extension but closed for modification.

Meaning: You should be able to add new functionality without changing existing code.

##### BAD: Modification Required

```kotlin
// - Adding new payment method requires modifying this class
class PaymentProcessor {
    fun processPayment(type: String, amount: Double) {
        when (type) {
            "credit_card" -> {
                println("Processing credit card payment: $amount")
            }
            "paypal" -> {
                println("Processing PayPal payment: $amount")
            }
            // - To add Bitcoin, must modify this class!
            "bitcoin" -> {
                println("Processing Bitcoin payment: $amount")
            }
            else -> throw IllegalArgumentException("Unknown payment type")
        }
    }
}
```

##### GOOD: Open for Extension

```kotlin
// - Abstract interface - closed for modification
interface PaymentMethod {
    fun processPayment(amount: Double)
}

// - Concrete implementations - extend functionality
class CreditCardPayment : PaymentMethod {
    override fun processPayment(amount: Double) {
        println("Processing credit card payment: $amount")
        // Credit card logic
    }
}

class PayPalPayment : PaymentMethod {
    override fun processPayment(amount: Double) {
        println("Processing PayPal payment: $amount")
        // PayPal logic
    }
}

// - Adding Bitcoin doesn't modify existing code
class BitcoinPayment : PaymentMethod {
    override fun processPayment(amount: Double) {
        println("Processing Bitcoin payment: $amount")
        // Bitcoin logic
    }
}

// - PaymentProcessor uses abstraction
class PaymentProcessor {
    fun processPayment(paymentMethod: PaymentMethod, amount: Double) {
        paymentMethod.processPayment(amount)
    }
}

// Usage
val processor = PaymentProcessor()
processor.processPayment(CreditCardPayment(), 100.0)
processor.processPayment(BitcoinPayment(), 50.0)
```

Benefits:
- Add new payment methods without changing PaymentProcessor
- Existing code remains stable
- Easier to maintain and test

---

#### 3. L - Liskov Substitution Principle (LSP)

Principle: Subtypes must be substitutable for their base types.

Meaning: If class `B` extends class `A`, you should be able to replace `A` with `B` without breaking the program.

##### BAD: Violates LSP

```kotlin
open class Bird {
    open fun fly() {
        println("Flying...")
    }
}

class Sparrow : Bird() {
    override fun fly() {
        println("Sparrow flying")
    }
}

// - Penguin can't fly, violates LSP!
class Penguin : Bird() {
    override fun fly() {
        throw UnsupportedOperationException("Penguins can't fly!")
    }
}

// - This code breaks with Penguin
fun makeBirdFly(bird: Bird) {
    bird.fly()  // Throws exception if bird is Penguin!
}

makeBirdFly(Sparrow())
makeBirdFly(Penguin())
```

##### GOOD: Follows LSP

```kotlin
// - Base abstraction without fly
abstract class Bird {
    abstract fun move()
}

// - Separate interface for flying birds
interface Flyable {
    fun fly()
}

class Sparrow : Bird(), Flyable {
    override fun move() {
        fly()
    }

    override fun fly() {
        println("Sparrow flying")
    }
}

class Penguin : Bird() {
    override fun move() {
        swim()
    }

    fun swim() {
        println("Penguin swimming")
    }
}

// - Functions work with appropriate abstractions
fun makeBirdMove(bird: Bird) {
    bird.move()
}

fun makeFlyableFly(flyable: Flyable) {
    flyable.fly()
}

makeBirdMove(Sparrow())
makeBirdMove(Penguin())
makeFlyableFly(Sparrow())
```

Benefits:
- Subtypes behave consistently
- No unexpected runtime errors
- Polymorphism works correctly

---

#### 4. I - Interface Segregation Principle (ISP)

Principle: Clients should not be forced to depend on interfaces they don't use.

Meaning: Many small, specific interfaces are better than one large, general interface.

##### BAD: Fat Interface

```kotlin
// - Large interface with many responsibilities
interface Worker {
    fun work()
    fun eat()
    fun sleep()
    fun getSalary()
    fun attendMeeting()
}

// - Robot doesn't eat or sleep!
class Robot : Worker {
    override fun work() {
        println("Robot working")
    }

    override fun eat() {
        // - Robots don't eat!
        throw UnsupportedOperationException("Robots don't eat")
    }

    override fun sleep() {
        // - Robots don't sleep!
        throw UnsupportedOperationException("Robots don't sleep")
    }

    override fun getSalary() {
        // - Robots don't get paid!
        throw UnsupportedOperationException("Robots don't get salary")
    }

    override fun attendMeeting() {
        // - Robots don't attend meetings!
        throw UnsupportedOperationException("Robots don't attend meetings")
    }
}
```

##### GOOD: Segregated Interfaces

```kotlin
// - Small, focused interfaces
interface Workable {
    fun work()
}

interface Eatable {
    fun eat()
}

interface Sleepable {
    fun sleep()
}

interface Payable {
    fun getSalary()
}

interface MeetingAttendee {
    fun attendMeeting()
}

// - Human implements all interfaces
class Human : Workable, Eatable, Sleepable, Payable, MeetingAttendee {
    override fun work() {
        println("Human working")
    }

    override fun eat() {
        println("Human eating")
    }

    override fun sleep() {
        println("Human sleeping")
    }

    override fun getSalary() {
        println("Human receiving salary")
    }

    override fun attendMeeting() {
        println("Human attending meeting")
    }
}

// - Robot only implements relevant interfaces
class Robot : Workable {
    override fun work() {
        println("Robot working")
    }
}

// - Manager has different interface combination
class Manager : Workable, Eatable, Sleepable, Payable, MeetingAttendee {
    override fun work() {
        println("Manager managing")
    }

    override fun eat() {
        println("Manager eating")
    }

    override fun sleep() {
        println("Manager sleeping")
    }

    override fun getSalary() {
        println("Manager receiving salary")
    }

    override fun attendMeeting() {
        println("Manager leading meeting")
    }
}
```

Benefits:
- Classes only implement what they need
- No forced empty implementations
- Better separation of concerns

---

#### 5. D - Dependency Inversion Principle (DIP)

Principle:
- High-level modules should not depend on low-level modules. Both should depend on abstractions.
- Abstractions should not depend on details. Details should depend on abstractions.

Meaning: Depend on interfaces, not concrete implementations.

##### BAD: Direct Dependency on Implementation

```kotlin
// - Concrete implementation
class MySQLDatabase {
    fun save(data: String) {
        println("Saving to MySQL: $data")
    }

    fun fetch(id: String): String {
        return "Data from MySQL"
    }
}

// - UserService depends directly on MySQLDatabase
class UserService {
    private val database = MySQLDatabase()  // - Tightly coupled!

    fun saveUser(user: String) {
        database.save(user)
    }

    fun getUser(id: String): String {
        return database.fetch(id)
    }
}
```

##### GOOD: Dependency on Abstraction

```kotlin
// - Abstract interface
interface Database {
    fun save(data: String)
    fun fetch(id: String): String
}

// - Concrete implementations
class MySQLDatabase : Database {
    override fun save(data: String) {
        println("Saving to MySQL: $data")
    }

    override fun fetch(id: String): String {
        return "Data from MySQL: $id"
    }
}

class PostgreSQLDatabase : Database {
    override fun save(data: String) {
        println("Saving to PostgreSQL: $data")
    }

    override fun fetch(id: String): String {
        return "Data from PostgreSQL: $id"
    }
}

class MongoDBDatabase : Database {
    override fun save(data: String) {
        println("Saving to MongoDB: $data")
    }

    override fun fetch(id: String): String {
        return "Data from MongoDB: $id"
    }
}

// - UserService depends on abstraction via dependency injection
class UserService(private val database: Database) {
    fun saveUser(user: String) {
        database.save(user)
    }

    fun getUser(id: String): String {
        return database.fetch(id)
    }
}

// Usage - can easily switch implementations
val mysqlService = UserService(MySQLDatabase())
val postgresService = UserService(PostgreSQLDatabase())
val mongoService = UserService(MongoDBDatabase())

// - Easy to test with mock
class MockDatabase : Database {
    override fun save(data: String) {
        // Mock implementation
    }

    override fun fetch(id: String): String {
        return "Mock data"
    }
}

val testService = UserService(MockDatabase())
```

Benefits:
- Easy to swap implementations
- Testable with mocks
- Loose coupling
- Follows dependency injection pattern

---

## SOLID Summary

| Principle             | Acronym | Key Idea                                  | Benefit                             |
|-----------------------|---------|-------------------------------------------|-------------------------------------|
| Single Responsibility | S       | One class, one responsibility             | Easy to understand and maintain     |
| Open/Closed           | O       | Open for extension, closed for modification | Add features without breaking code |
| Liskov Substitution   | L       | Subtypes must be substitutable            | Polymorphism works correctly        |
| Interface Segregation | I       | Many small interfaces > one large         | No forced implementations           |
| Dependency Inversion  | D       | Depend on abstractions, not implementations | Flexible, testable code          |

---

## Android Example: Complete SOLID `Application`

```kotlin
// Domain layer - business entities
data class User(
    val id: String,
    val name: String,
    val email: String
)

// S - Single Responsibility
// Each class has one job

// Data layer abstraction (D - Dependency Inversion)
interface UserRepository {
    suspend fun save(user: User)
    suspend fun findById(id: String): User?
    suspend fun findAll(): List<User>
}

// Concrete implementation
class RoomUserRepository(
    private val userDao: UserDao
) : UserRepository {
    override suspend fun save(user: User) {
        userDao.insert(user.toEntity())
    }

    override suspend fun findById(id: String): User? {
        return userDao.findById(id)?.toDomain()
    }

    override suspend fun findAll(): List<User> {
        return userDao.findAll().map { it.toDomain() }
    }
}

// O - Open/Closed
// Can add validation rules without modifying validator
interface ValidationRule<T> {
    fun validate(value: T): Boolean
    fun errorMessage(): String
}

class EmailValidationRule : ValidationRule<String> {
    override fun validate(value: String): Boolean {
        // Simplified example regex for demonstration purposes
        return value.matches(Regex("^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+$"))
    }

    override fun errorMessage() = "Invalid email format"
}

class NameValidationRule : ValidationRule<String> {
    override fun validate(value: String): Boolean {
        return value.isNotBlank() && value.length >= 2
    }

    override fun errorMessage() = "Name must be at least 2 characters"
}

class UserValidator {
    private val emailRule = EmailValidationRule()
    private val nameRule = NameValidationRule()

    fun validate(user: User): List<String> {
        val errors = mutableListOf<String>()

        if (!emailRule.validate(user.email)) {
            errors.add(emailRule.errorMessage())
        }

        if (!nameRule.validate(user.name)) {
            errors.add(nameRule.errorMessage())
        }

        return errors
    }
}

// I - Interface Segregation
// Separate interfaces for different responsibilities
interface UserReader {
    suspend fun findById(id: String): User?
    suspend fun findAll(): List<User>
}

interface UserWriter {
    suspend fun save(user: User)
    suspend fun delete(id: String)
}

// Example split repository if needed
interface ReadOnlyUserRepository : UserReader
interface WriteOnlyUserRepository : UserWriter

// Use case / business logic
class CreateUserUseCase(
    private val repository: UserRepository,
    private val validator: UserValidator,
    private val notificationService: UserNotificationService
) {
    suspend operator fun invoke(name: String, email: String): Result<User> {
        val user = User(
            id = UUID.randomUUID().toString(),
            name = name,
            email = email
        )

        // Validate
        val errors = validator.validate(user)
        if (errors.isNotEmpty()) {
            return Result.failure(ValidationException(errors))
        }

        // Save
        repository.save(user)

        // Notify
        notificationService.sendWelcomeEmail(user)

        return Result.success(user)
    }
}

class GetUsersUseCase(
    private val repository: UserRepository
) {
    suspend operator fun invoke(): List<User> = repository.findAll()
}

// ViewModel (presentation layer)
class UserViewModel(
    private val createUserUseCase: CreateUserUseCase,
    private val getUsersUseCase: GetUsersUseCase
) : ViewModel() {

    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()

    fun createUser(name: String, email: String) {
        viewModelScope.launch {
            createUserUseCase(name, email)
                .onSuccess { user ->
                    // Update UI
                    _users.value = _users.value + user
                }
                .onFailure {
                    // Handle error
                }
        }
    }

    fun loadUsers() {
        viewModelScope.launch {
            _users.value = getUsersUseCase()
        }
    }
}
```

---

## Benefits of SOLID

1. Maintainability: Easy to update and modify code.
2. Scalability: Easy to add new features.
3. Testability: Easy to write unit tests.
4. Readability: Code is clear and well-organized.
5. Flexibility: Easy to adapt to changing requirements.
6. Reduced coupling: Components are independent.
7. Reusability: Code can be reused in different contexts.

---

## Follow-ups

- How do SOLID principles relate to Clean Architecture in practice?
- Show an example where over-applying SOLID leads to over-engineering.
- How would you refactor an existing "God object" using SOLID?

## Related Questions

- How do SOLID principles relate to Clean Architecture in practice?
- Show an example where over-applying SOLID leads to over-engineering.
- How would you refactor an existing "God object" using SOLID?

## References

- [[c-architecture-patterns]]
