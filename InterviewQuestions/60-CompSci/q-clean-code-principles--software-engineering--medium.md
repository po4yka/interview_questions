---
id: 20251012-600002
title: "Clean Code Principles / Принципы чистого кода"
slug: clean-code-principles-software-engineering-medium
topic: cs
subtopics: ["computer-science", "fundamentals"]

subtopics:
  - clean-code
  - software-engineering
  - best-practices
  - code-quality
  - refactoring
status: draft
difficulty: medium
moc: moc-cs
date_created: 2025-10-12
date_updated: 2025-10-13
related_questions:
  - q-solid-principles--software-design--medium
  - q-design-patterns-types--design-patterns--medium
  - q-refactoring-techniques--software-engineering--medium
tags:
  - clean-code
  - best-practices
  - refactoring
  - code-quality
  - readable-code
---

# Clean Code Principles

## English Version

### Problem Statement

Clean code is code that is easy to understand, easy to maintain, and easy to extend. Following clean code principles improves code quality, reduces bugs, and increases development velocity. Based on Robert C. Martin's (Uncle Bob) "Clean Code" principles.

**The Question:** What are clean code principles? How do you write meaningful names, good functions, and clear comments? What are code smells and how to refactor them?

### Detailed Answer

---

### MEANINGFUL NAMES

**1. Use Intention-Revealing Names**

```kotlin
//  Bad: What does this mean?
val d: Int = 5

//  Good: Clear intent
val elapsedTimeInDays: Int = 5
val daysSinceLastUpdate: Int = 5

//  Bad: Cryptic
fun getThem(): List<IntArray> {
    val list1 = mutableListOf<IntArray>()
    for (x in theList) {
        if (x[0] == 4) {
            list1.add(x)
        }
    }
    return list1
}

//  Good: Clear purpose
fun getFlaggedCells(): List<Cell> {
    val flaggedCells = mutableListOf<Cell>()
    for (cell in gameBoard) {
        if (cell.isFlagged()) {
            flaggedCells.add(cell)
        }
    }
    return flaggedCells
}
```

**2. Avoid Disinformation**

```kotlin
//  Bad: accountList is not actually a List
val accountList: Set<Account> = setOf()

//  Good: Use accurate names
val accounts: Set<Account> = setOf()
val accountSet: Set<Account> = setOf()

//  Bad: Similar names with tiny differences
fun getActiveAccountInfo()
fun getActiveAccountData()
fun getActiveAccountRecord()  // What's the difference?

//  Good: Distinct, meaningful names
fun getActiveAccount(): Account
fun calculateAccountBalance(): Money
fun fetchAccountHistory(): List<Transaction>
```

**3. Use Pronounceable Names**

```kotlin
//  Bad: Unpronounceable
data class DtaRcrd102(
    val genymdhms: Long,  // generation date, year, month, day, hour, minute, second
    val modymdhms: Long
)

//  Good: Pronounceable
data class Customer(
    val generationTimestamp: Long,
    val modificationTimestamp: Long
)
```

**4. Use Searchable Names**

```kotlin
//  Bad: Magic numbers, hard to search
for (i in 0 until 34) {
    s += (t[i] * 4) / 5
}

//  Good: Named constants
val WORK_DAYS_PER_WEEK = 5
val NUMBER_OF_TASKS = 34

for (i in 0 until NUMBER_OF_TASKS) {
    val realTaskDays = taskEstimate[i] * WORK_DAYS_PER_WEEK
    val realTaskWeeks = realTaskDays / WORK_DAYS_PER_WEEK
    sum += realTaskWeeks
}
```

**5. Class Names = Nouns, Method Names = Verbs**

```kotlin
//  Good: Class names are nouns
class Customer
class Account
class WikiPage

//  Good: Method names are verbs
fun deletePage()
fun save()
fun calculatePayment()

//  Good: Accessors, mutators, predicates
val isActive: Boolean
    get() = status == Status.ACTIVE

fun setName(name: String)
fun getName(): String
```

---

### FUNCTIONS

**1. Small Functions**

```kotlin
//  Bad: Too long, does too much
fun processUser(user: User) {
    // Validate email
    if (!user.email.contains("@")) {
        throw IllegalArgumentException("Invalid email")
    }

    // Check age
    if (user.age < 18) {
        throw IllegalArgumentException("User must be 18+")
    }

    // Hash password
    val hashedPassword = MessageDigest.getInstance("SHA-256")
        .digest(user.password.toByteArray())
        .joinToString("") { "%02x".format(it) }

    // Save to database
    database.execute(
        "INSERT INTO users (name, email, password, age) VALUES (?, ?, ?, ?)",
        user.name, user.email, hashedPassword, user.age
    )

    // Send welcome email
    val smtp = SMTPTransport()
    smtp.connect("smtp.example.com")
    smtp.send(user.email, "Welcome!", "Thanks for joining!")
    smtp.close()

    // Log
    logger.log("User ${user.email} registered")
}

//  Good: Small, focused functions
fun registerUser(user: User) {
    validateUser(user)
    val secureUser = securePassword(user)
    saveUser(secureUser)
    sendWelcomeEmail(user.email)
    logRegistration(user.email)
}

private fun validateUser(user: User) {
    validateEmail(user.email)
    validateAge(user.age)
}

private fun validateEmail(email: String) {
    if (!email.contains("@")) {
        throw IllegalArgumentException("Invalid email")
    }
}

private fun validateAge(age: Int) {
    if (age < 18) {
        throw IllegalArgumentException("User must be 18+")
    }
}

private fun securePassword(user: User): User {
    val hashedPassword = hashPassword(user.password)
    return user.copy(password = hashedPassword)
}

private fun hashPassword(password: String): String {
    return MessageDigest.getInstance("SHA-256")
        .digest(password.toByteArray())
        .joinToString("") { "%02x".format(it) }
}
```

**2. Do One Thing**

```kotlin
//  Bad: Function does multiple things
fun pay() {
    for (employee in employees) {
        if (employee.isPayday()) {
            val pay = employee.calculatePay()
            employee.deliverPay(pay)
        }
    }
}

//  Good: Each function does one thing
fun payEmployees() {
    employees.filter { it.isPayday() }
        .forEach { payEmployee(it) }
}

private fun payEmployee(employee: Employee) {
    val pay = calculatePay(employee)
    deliverPay(employee, pay)
}

private fun calculatePay(employee: Employee): Money {
    return Money(employee.salary / 12)
}

private fun deliverPay(employee: Employee, pay: Money) {
    employee.bankAccount.deposit(pay)
}
```

**3. Few Arguments (Prefer 0-2, Avoid 3+)**

```kotlin
//  Bad: Too many arguments
fun createUser(
    name: String,
    email: String,
    password: String,
    age: Int,
    country: String,
    phoneNumber: String,
    address: String,
    zipCode: String
) { }

//  Good: Group related data
data class UserRegistration(
    val name: String,
    val email: String,
    val password: String,
    val age: Int,
    val address: Address,
    val contact: Contact
)

data class Address(
    val country: String,
    val street: String,
    val zipCode: String
)

data class Contact(
    val phoneNumber: String,
    val email: String
)

fun createUser(registration: UserRegistration) { }

//  Good: Builder pattern for optional parameters
class UserBuilder {
    private var name: String = ""
    private var email: String = ""
    private var age: Int = 0

    fun name(name: String) = apply { this.name = name }
    fun email(email: String) = apply { this.email = email }
    fun age(age: Int) = apply { this.age = age }

    fun build() = User(name, email, age)
}

// Usage
val user = UserBuilder()
    .name("John")
    .email("john@example.com")
    .age(25)
    .build()
```

**4. No Side Effects**

```kotlin
//  Bad: Unexpected side effect
class UserValidator {
    private var session: Session? = null

    fun checkPassword(username: String, password: String): Boolean {
        val user = UserGateway.findByName(username)
        if (user != null) {
            if (user.password == password) {
                Session.initialize()  //  Unexpected side effect!
                return true
            }
        }
        return false
    }
}

//  Good: Explicit, no side effects
class UserValidator {
    fun checkPassword(username: String, password: String): Boolean {
        val user = UserGateway.findByName(username) ?: return false
        return user.password == password
    }

    fun initializeSession(user: User) {
        Session.initialize(user)
    }
}

// Usage - explicit intent
if (validator.checkPassword(username, password)) {
    validator.initializeSession(user)
}
```

**5. Command Query Separation**

```kotlin
//  Bad: Function does both query and command
fun set(attribute: String, value: String): Boolean {
    if (attributeExists(attribute)) {
        setAttribute(attribute, value)
        return true
    }
    return false
}

// Usage is confusing
if (set("username", "bob")) { }  // Does this check or set?

//  Good: Separate query from command
fun attributeExists(attribute: String): Boolean {
    return attributes.containsKey(attribute)
}

fun setAttribute(attribute: String, value: String) {
    attributes[attribute] = value
}

// Usage is clear
if (attributeExists("username")) {
    setAttribute("username", "bob")
}
```

---

### COMMENTS

**1. Explain Why, Not What**

```kotlin
//  Bad: Comments explain what code does
// Check if user is adult
if (user.age >= 18) {
    // Allow access
    grantAccess()
}

//  Good: Code is self-explanatory
if (user.isAdult()) {
    grantAccess()
}

//  Good: Comment explains WHY
// We use 18 as the legal age because our primary market is the US
// and most states require 18+ for our service
private const val LEGAL_AGE = 18

fun User.isAdult() = age >= LEGAL_AGE
```

**2. Avoid Redundant Comments**

```kotlin
//  Bad: Redundant comments
// The name of the user
val userName: String

// The user's email address
val userEmail: String

// Returns the user's age
fun getUserAge(): Int

//  Good: Self-documenting code
val userName: String
val userEmail: String
fun getUserAge(): Int
```

**3. Use Comments for TODO, FIXME, WARNING**

```kotlin
//  Good: Important markers
// TODO: Add input validation for email format
// FIXME: This occasionally returns null even when user exists
// WARNING: Don't call this from UI thread - it blocks

// TODO: [JIRA-123] Implement proper error handling
fun processPayment(amount: Money) {
    // Current implementation is temporary
    // See design doc: https://docs.example.com/payments
}
```

**4. Don't Comment Out Code - Delete It**

```kotlin
//  Bad: Commented out code
fun calculateTax(income: Double): Double {
    // val oldTax = income * 0.15
    // return oldTax + 100
    return income * 0.20
}

//  Good: Delete it (version control remembers)
fun calculateTax(income: Double): Double {
    return income * 0.20
}
```

---

### CODE FORMATTING

**1. Vertical Formatting**

```kotlin
//  Good: Related concepts close together
class User(
    val id: String,
    val name: String,
    val email: String
) {
    // Group related methods
    fun getName() = name
    fun getEmail() = email

    // Separate group with blank line
    fun updateProfile(newName: String, newEmail: String) {
        // Implementation
    }

    fun deleteAccount() {
        // Implementation
    }
}

//  Good: Vertical ordering (high-level to low-level)
class OrderProcessor {
    fun processOrder(order: Order) {  // Public, high-level
        validateOrder(order)
        calculateTotal(order)
        chargePayment(order)
        sendConfirmation(order)
    }

    private fun validateOrder(order: Order) {  // Private, detail
        // Validation logic
    }

    private fun calculateTotal(order: Order) {
        // Calculation logic
    }

    private fun chargePayment(order: Order) {
        // Payment logic
    }

    private fun sendConfirmation(order: Order) {
        // Email logic
    }
}
```

**2. Horizontal Formatting**

```kotlin
//  Good: Max 80-120 characters per line
// Use line breaks for long expressions

//  Bad: Too long
fun registerUser(name: String, email: String, password: String, age: Int, country: String, phoneNumber: String) { }

//  Good: Break into multiple lines
fun registerUser(
    name: String,
    email: String,
    password: String,
    age: Int,
    country: String,
    phoneNumber: String
) { }

//  Good: Align related expressions
val name     = user.getName()
val email    = user.getEmail()
val age      = user.getAge()
val country  = user.getCountry()
```

---

### ERROR HANDLING

**1. Use Exceptions, Not Error Codes**

```kotlin
//  Bad: Error codes
fun deleteFile(fileName: String): Int {
    if (!fileExists(fileName)) {
        return -1  // Error code
    }
    // Delete file
    return 0  // Success
}

// Usage is cluttered
val result = deleteFile("data.txt")
if (result == -1) {
    // Handle error
}

//  Good: Exceptions
fun deleteFile(fileName: String) {
    if (!fileExists(fileName)) {
        throw FileNotFoundException(fileName)
    }
    // Delete file
}

// Usage is cleaner
try {
    deleteFile("data.txt")
} catch (e: FileNotFoundException) {
    // Handle error
}
```

**2. Extract Try/Catch Blocks**

```kotlin
//  Bad: Try/catch mixed with logic
fun processUser(user: User) {
    try {
        val data = database.query("SELECT * FROM users WHERE id = ${user.id}")
        if (data != null) {
            user.name = data.name
            user.email = data.email
            logger.log("User processed")
        }
    } catch (e: SQLException) {
        logger.error("Database error", e)
    }
}

//  Good: Separate error handling from logic
fun processUser(user: User) {
    try {
        updateUserFromDatabase(user)
    } catch (e: SQLException) {
        handleDatabaseError(e)
    }
}

private fun updateUserFromDatabase(user: User) {
    val data = database.findUserById(user.id)
    user.updateFrom(data)
    logger.log("User processed")
}

private fun handleDatabaseError(e: SQLException) {
    logger.error("Database error", e)
}
```

**3. Don't Return Null**

```kotlin
//  Bad: Returning null
fun getUser(id: String): User? {
    return database.findById(id)
}

// Caller must check null
val user = getUser("123")
if (user != null) {
    // Use user
}

//  Better: Return Result or throw exception
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val exception: Exception) : Result<Nothing>()
}

fun getUser(id: String): Result<User> {
    return try {
        val user = database.findById(id)
            ?: return Result.Error(UserNotFoundException(id))
        Result.Success(user)
    } catch (e: Exception) {
        Result.Error(e)
    }
}

//  Best: Use Kotlin's Result type
fun getUser(id: String): kotlin.Result<User> {
    return runCatching {
        database.findById(id) ?: throw UserNotFoundException(id)
    }
}
```

---

### CODE SMELLS

**1. Duplicated Code**

```kotlin
//  Bad: Duplicated logic
fun getUserByEmail(email: String): User? {
    val connection = DriverManager.getConnection(DB_URL)
    val statement = connection.prepareStatement("SELECT * FROM users WHERE email = ?")
    statement.setString(1, email)
    val result = statement.executeQuery()
    // Parse result...
    connection.close()
    return user
}

fun getUserById(id: String): User? {
    val connection = DriverManager.getConnection(DB_URL)
    val statement = connection.prepareStatement("SELECT * FROM users WHERE id = ?")
    statement.setString(1, id)
    val result = statement.executeQuery()
    // Parse result...
    connection.close()
    return user
}

//  Good: Extract common logic
private fun executeQuery(sql: String, vararg params: Any): ResultSet {
    val connection = DriverManager.getConnection(DB_URL)
    val statement = connection.prepareStatement(sql)
    params.forEachIndexed { index, param ->
        statement.setObject(index + 1, param)
    }
    return statement.executeQuery()
}

fun getUserByEmail(email: String): User? {
    val result = executeQuery("SELECT * FROM users WHERE email = ?", email)
    return parseUser(result)
}

fun getUserById(id: String): User? {
    val result = executeQuery("SELECT * FROM users WHERE id = ?", id)
    return parseUser(result)
}
```

**2. Long Methods**

```kotlin
//  Bad: Method too long (100+ lines)
fun processOrder(order: Order) {
    // 20 lines of validation
    // 30 lines of calculation
    // 25 lines of database operations
    // 15 lines of email sending
    // 10 lines of logging
}

//  Good: Extract to small methods
fun processOrder(order: Order) {
    validateOrder(order)
    calculateOrderTotal(order)
    saveOrderToDatabase(order)
    sendOrderConfirmation(order)
    logOrderProcessing(order)
}
```

**3. Large Classes**

```kotlin
//  Bad: God class doing everything
class OrderManager {
    fun createOrder() { }
    fun validateOrder() { }
    fun calculateTax() { }
    fun calculateShipping() { }
    fun processPayment() { }
    fun chargeCard() { }
    fun checkInventory() { }
    fun updateInventory() { }
    fun sendEmail() { }
    fun generateInvoice() { }
    fun printReceipt() { }
    fun logTransaction() { }
}

//  Good: Single Responsibility Principle
class OrderService {
    private val validator = OrderValidator()
    private val calculator = PriceCalculator()
    private val paymentProcessor = PaymentProcessor()
    private val inventoryManager = InventoryManager()
    private val notificationService = NotificationService()

    fun processOrder(order: Order) {
        validator.validate(order)
        val total = calculator.calculateTotal(order)
        paymentProcessor.process(order, total)
        inventoryManager.updateInventory(order)
        notificationService.sendConfirmation(order)
    }
}
```

**4. Feature Envy**

```kotlin
//  Bad: Method uses another class's data extensively
class Order {
    lateinit var customer: Customer

    fun calculateDiscount(): Double {
        var discount = 0.0
        if (customer.yearsAsMember > 5) {
            discount += 0.10
        }
        if (customer.totalPurchases > 1000) {
            discount += 0.05
        }
        if (customer.isPremium) {
            discount += 0.15
        }
        return discount
    }
}

//  Good: Move method to the class it uses
class Customer {
    var yearsAsMember: Int = 0
    var totalPurchases: Double = 0.0
    var isPremium: Boolean = false

    fun getDiscount(): Double {
        var discount = 0.0
        if (yearsAsMember > 5) discount += 0.10
        if (totalPurchases > 1000) discount += 0.05
        if (isPremium) discount += 0.15
        return discount
    }
}

class Order {
    lateinit var customer: Customer

    fun calculateDiscount(): Double {
        return customer.getDiscount()
    }
}
```

---

### KEY TAKEAWAYS

1. **Meaningful names** - intention-revealing, pronounceable, searchable
2. **Small functions** - do one thing, few arguments (<3)
3. **Comments** - explain why, not what; avoid redundant comments
4. **Formatting** - consistent vertical/horizontal spacing
5. **Error handling** - use exceptions, not error codes
6. **DRY** - Don't Repeat Yourself
7. **Single Responsibility** - each class/function does one thing
8. **No side effects** - functions should be predictable
9. **Command-Query Separation** - separate queries from commands
10. **Code smells** - duplicated code, long methods, god classes

---

## Russian Version

### Постановка задачи

Чистый код - код, который легко понять, легко поддерживать и легко расширять. Следование принципам чистого кода улучшает качество кода, сокращает баги и увеличивает скорость разработки. Основано на принципах "Clean Code" Robert C. Martin (Uncle Bob).

**Вопрос:** Каковы принципы чистого кода? Как писать осмысленные имена, хорошие функции и понятные комментарии? Что такое code smells и как их рефакторить?

### Ключевые выводы

1. **Осмысленные имена** - раскрывающие намерение, произносимые, искомые
2. **Маленькие функции** - делают одно, мало аргументов (<3)
3. **Комментарии** - объясняют почему, не что; избегайте избыточных комментариев
4. **Форматирование** - консистентные вертикальные/горизонтальные отступы
5. **Обработка ошибок** - используйте exceptions, не error codes
6. **DRY** - Don't Repeat Yourself (не повторяйтесь)
7. **Single Responsibility** - каждый класс/функция делает одно
8. **Без побочных эффектов** - функции должны быть предсказуемыми
9. **Command-Query Separation** - разделяйте запросы от команд
10. **Code smells** - дублированный код, длинные методы, god классы

## Follow-ups

1. What is the Boy Scout Rule in clean code?
2. How do you measure code quality?
3. What are code metrics (cyclomatic complexity, coupling, cohesion)?
4. How do you refactor legacy code safely?
5. What is technical debt and how to manage it?
6. What are YAGNI and KISS principles?
7. How do you write self-documenting code?
8. What is the difference between comments and documentation?
9. How do you handle code reviews effectively?
10. What are the benefits of pair programming for code quality?

---

## Related Questions

### Prerequisites (Easier)
- [[q-xml-acronym--programming-languages--easy]] - Computer Science
- [[q-data-structures-overview--algorithms--easy]] - Data Structures

### Related (Medium)
- [[q-oop-principles-deep-dive--computer-science--medium]] - Computer Science
- [[q-default-vs-io-dispatcher--programming-languages--medium]] - Computer Science

### Advanced (Harder)
- [[q-os-fundamentals-concepts--computer-science--hard]] - Computer Science
