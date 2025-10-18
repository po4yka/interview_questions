---
id: 20251012-600004
title: "OOP Principles Deep Dive / Глубокое погружение в принципы ООП"
topic: cs
difficulty: medium
status: draft
created: 2025-10-12
tags:
  - oop
  - encapsulation
  - inheritance
  - polymorphism
  - abstraction
  - composition
moc: moc-cs
related: [q-garbage-collector-roots--programming-languages--medium, q-concurrency-fundamentals--computer-science--hard, q-template-method-pattern--design-patterns--medium]
  - q-solid-principles--software-design--medium
  - q-clean-code-principles--software-engineering--medium
  - q-design-patterns-types--design-patterns--medium
subtopics:
  - oop
  - object-oriented-programming
  - encapsulation
  - inheritance
  - polymorphism
  - abstraction
---
# OOP Principles Deep Dive

## English Version

### Problem Statement

Object-Oriented Programming (OOP) is a paradigm based on objects containing data and behavior. The four pillars of OOP—Encapsulation, Inheritance, Polymorphism, and Abstraction—provide structure for building maintainable, reusable code.

**The Question:** What are the four pillars of OOP? How do encapsulation, inheritance, polymorphism, and abstraction work? When to use composition over inheritance? What are common OOP pitfalls?

### Detailed Answer

---

### THE FOUR PILLARS OF OOP

```
1. ENCAPSULATION
   - Bundle data and methods
   - Hide internal details
   - Control access (private/public)

2. INHERITANCE
   - Create new classes from existing
   - "IS-A" relationship
   - Code reuse

3. POLYMORPHISM
   - Many forms
   - Same interface, different implementations
   - Method overriding/overloading

4. ABSTRACTION
   - Hide complexity
   - Show only essential features
   - Interfaces and abstract classes
```

---

### 1. ENCAPSULATION

**Definition: Bundle data and methods that operate on that data**

```kotlin
//  Bad: No encapsulation
class BankAccountBad {
    var balance: Double = 0.0  // Direct access

    fun deposit(amount: Double) {
        balance += amount
    }
}

// Problem:
val account = BankAccountBad()
account.balance = -1000.0  //  Can set invalid state!

//  Good: Encapsulation with validation
class BankAccount(initialBalance: Double) {
    private var _balance: Double = initialBalance  // Private
        set(value) {
            require(value >= 0) { "Balance cannot be negative" }
            field = value
        }

    val balance: Double  // Read-only public access
        get() = _balance

    fun deposit(amount: Double) {
        require(amount > 0) { "Deposit amount must be positive" }
        _balance += amount
    }

    fun withdraw(amount: Double): Boolean {
        if (amount <= 0) return false
        if (amount > _balance) return false

        _balance -= amount
        return true
    }
}

// Usage:
val account = BankAccount(1000.0)
// account._balance = -100.0  //  Compilation error
account.deposit(500.0)  //  Controlled access
println(account.balance)  //  Read-only
```

**Benefits of Encapsulation:**
```
 Control access to data
 Validate state changes
 Hide implementation details
 Easy to change internals without affecting users
 Maintain invariants
```

**Android Example:**
```kotlin
// ViewModel with encapsulation
class UserViewModel : ViewModel() {
    // Private mutable state
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)

    // Public immutable state
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    // Private mutable list
    private val _users = MutableLiveData<List<User>>()

    // Public immutable list
    val users: LiveData<List<User>> = _users

    // Controlled modification
    fun loadUsers() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            try {
                val users = repository.getUsers()
                _users.value = users
                _uiState.value = UiState.Success
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message)
            }
        }
    }
}
```

---

### 2. INHERITANCE

**Definition: Create new class from existing class**

```kotlin
// Base class
open class Animal(val name: String) {
    open fun makeSound() {
        println("$name makes a sound")
    }

    fun sleep() {
        println("$name is sleeping")
    }
}

// Derived classes
class Dog(name: String) : Animal(name) {
    override fun makeSound() {
        println("$name barks: Woof!")
    }

    fun fetch() {
        println("$name fetches the ball")
    }
}

class Cat(name: String) : Animal(name) {
    override fun makeSound() {
        println("$name meows: Meow!")
    }

    fun climb() {
        println("$name climbs the tree")
    }
}

// Usage:
val dog = Dog("Rex")
dog.makeSound()  // Rex barks: Woof!
dog.sleep()      // Rex is sleeping (inherited)
dog.fetch()      // Rex fetches the ball (specific to Dog)

val cat = Cat("Whiskers")
cat.makeSound()  // Whiskers meows: Meow!
cat.sleep()      // Whiskers is sleeping (inherited)
cat.climb()      // Whiskers climbs the tree (specific to Cat)
```

**Inheritance Types:**

**1. Single Inheritance:**
```kotlin
open class Vehicle
class Car : Vehicle()  // Car inherits from Vehicle
```

**2. Multi-level Inheritance:**
```kotlin
open class Vehicle
open class Car : Vehicle()
class SportsCar : Car()  // SportsCar → Car → Vehicle
```

**3. Hierarchical Inheritance:**
```kotlin
open class Vehicle
class Car : Vehicle()
class Bike : Vehicle()
class Truck : Vehicle()  // Multiple classes inherit from Vehicle
```

**Android Example:**
```kotlin
// Android Activity hierarchy
abstract class BaseActivity : AppCompatActivity() {
    protected lateinit var analytics: Analytics

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        analytics = Analytics.getInstance()
        setupToolbar()
    }

    protected open fun setupToolbar() {
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
    }

    override fun onStart() {
        super.onStart()
        analytics.trackScreenView(this::class.simpleName ?: "Unknown")
    }
}

class MainActivity : BaseActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        // MainActivity specific logic
    }

    override fun setupToolbar() {
        super.setupToolbar()
        // MainActivity specific toolbar customization
        supportActionBar?.setTitle("Home")
    }
}

class ProfileActivity : BaseActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_profile)
        // ProfileActivity specific logic
    }
}
```

---

### 3. POLYMORPHISM

**Definition: Same interface, different implementations**

**A. Method Overriding (Runtime Polymorphism)**

```kotlin
open class Shape {
    open fun area(): Double {
        return 0.0
    }

    open fun draw() {
        println("Drawing shape")
    }
}

class Circle(val radius: Double) : Shape() {
    override fun area(): Double {
        return Math.PI * radius * radius
    }

    override fun draw() {
        println("Drawing circle with radius $radius")
    }
}

class Rectangle(val width: Double, val height: Double) : Shape() {
    override fun area(): Double {
        return width * height
    }

    override fun draw() {
        println("Drawing rectangle ${width}x${height}")
    }
}

// Polymorphism in action:
fun printShapeInfo(shape: Shape) {  // Accepts any Shape
    shape.draw()
    println("Area: ${shape.area()}")
}

// Usage:
val shapes: List<Shape> = listOf(
    Circle(5.0),
    Rectangle(4.0, 6.0),
    Circle(3.0)
)

shapes.forEach { shape ->
    printShapeInfo(shape)  // Different behavior for each type
}

// Output:
// Drawing circle with radius 5.0
// Area: 78.53981633974483
// Drawing rectangle 4.0x6.0
// Area: 24.0
// Drawing circle with radius 3.0
// Area: 28.274333882308138
```

**B. Method Overloading (Compile-time Polymorphism)**

```kotlin
class Calculator {
    // Same name, different parameters
    fun add(a: Int, b: Int): Int {
        return a + b
    }

    fun add(a: Double, b: Double): Double {
        return a + b
    }

    fun add(a: Int, b: Int, c: Int): Int {
        return a + b + c
    }

    fun add(numbers: List<Int>): Int {
        return numbers.sum()
    }
}

// Usage:
val calc = Calculator()
println(calc.add(1, 2))              // Calls Int version → 3
println(calc.add(1.5, 2.5))          // Calls Double version → 4.0
println(calc.add(1, 2, 3))           // Calls 3-parameter version → 6
println(calc.add(listOf(1, 2, 3, 4))) // Calls List version → 10
```

**Android Example:**
```kotlin
// Polymorphism with ViewHolder pattern
abstract class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
    abstract fun bind(item: Any)
}

class TextViewHolder(itemView: View) : ViewHolder(itemView) {
    private val textView: TextView = itemView.findViewById(R.id.textView)

    override fun bind(item: Any) {
        if (item is String) {
            textView.text = item
        }
    }
}

class ImageViewHolder(itemView: View) : ViewHolder(itemView) {
    private val imageView: ImageView = itemView.findViewById(R.id.imageView)

    override fun bind(item: Any) {
        if (item is ImageData) {
            imageView.load(item.url)
        }
    }
}

class MyAdapter(private val items: List<Any>) : RecyclerView.Adapter<ViewHolder>() {
    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(items[position])  // Polymorphic call
    }

    override fun getItemViewType(position: Int): Int {
        return when (items[position]) {
            is String -> TYPE_TEXT
            is ImageData -> TYPE_IMAGE
            else -> TYPE_UNKNOWN
        }
    }

    // ...
}
```

---

### 4. ABSTRACTION

**Definition: Hide complexity, show only essential features**

**A. Abstract Classes**

```kotlin
abstract class Employee(val name: String, val id: String) {
    // Abstract method (must be implemented)
    abstract fun calculateSalary(): Double

    // Abstract property
    abstract val department: String

    // Concrete method (optional to override)
    open fun clockIn() {
        println("$name clocked in at ${System.currentTimeMillis()}")
    }

    // Concrete method (cannot override - not open)
    fun getId(): String = id
}

class FullTimeEmployee(
    name: String,
    id: String,
    private val annualSalary: Double
) : Employee(name, id) {
    override val department: String = "Engineering"

    override fun calculateSalary(): Double {
        return annualSalary / 12  // Monthly salary
    }
}

class Contractor(
    name: String,
    id: String,
    private val hourlyRate: Double,
    private val hoursWorked: Double
) : Employee(name, id) {
    override val department: String = "Contract"

    override fun calculateSalary(): Double {
        return hourlyRate * hoursWorked
    }

    override fun clockIn() {
        super.clockIn()
        println("$name is a contractor")
    }
}

// Usage:
val employees: List<Employee> = listOf(
    FullTimeEmployee("Alice", "FT001", 120000.0),
    Contractor("Bob", "CT001", 50.0, 160.0)
)

employees.forEach { employee ->
    employee.clockIn()
    println("${employee.name} salary: $${employee.calculateSalary()}")
}
```

**B. Interfaces**

```kotlin
interface Drawable {
    fun draw()
    fun erase() {  // Default implementation
        println("Erasing...")
    }
}

interface Clickable {
    fun onClick()
    fun onDoubleClick() {
        println("Double clicked")  // Default implementation
    }
}

// Class can implement multiple interfaces
class Button : Drawable, Clickable {
    override fun draw() {
        println("Drawing button")
    }

    override fun onClick() {
        println("Button clicked")
    }

    // Uses default implementation of erase() and onDoubleClick()
}

// Usage:
val button = Button()
button.draw()
button.onClick()
button.erase()
button.onDoubleClick()
```

**Interface vs Abstract Class:**
```
Interface:
 Multiple inheritance
 No state (properties must be abstract)
 All methods abstract (unless default impl)
 Use for "CAN-DO" relationships

Abstract Class:
 Single inheritance only
 Can have state (properties with values)
 Can mix abstract and concrete methods
 Use for "IS-A" relationships with shared code

Example:
interface Flyable {  // CAN-DO
    fun fly()
}

abstract class Bird {  // IS-A
    abstract fun makeSound()
    fun eat() { }  // Common to all birds
}

class Sparrow : Bird(), Flyable {
    override fun makeSound() { }
    override fun fly() { }
}
```

**Android Example:**
```kotlin
// Repository interface (abstraction)
interface UserRepository {
    suspend fun getUser(id: String): User?
    suspend fun saveUser(user: User)
    suspend fun deleteUser(id: String)
}

// Local implementation
class LocalUserRepository(
    private val database: AppDatabase
) : UserRepository {
    override suspend fun getUser(id: String): User? {
        return database.userDao().getUser(id)
    }

    override suspend fun saveUser(user: User) {
        database.userDao().insert(user)
    }

    override suspend fun deleteUser(id: String) {
        database.userDao().delete(id)
    }
}

// Remote implementation
class RemoteUserRepository(
    private val apiService: ApiService
) : UserRepository {
    override suspend fun getUser(id: String): User? {
        return apiService.getUser(id)
    }

    override suspend fun saveUser(user: User) {
        apiService.createUser(user)
    }

    override suspend fun deleteUser(id: String) {
        apiService.deleteUser(id)
    }
}

// ViewModel depends on abstraction, not concrete implementation
class UserViewModel(
    private val repository: UserRepository  // Abstraction
) : ViewModel() {
    fun loadUser(id: String) {
        viewModelScope.launch {
            val user = repository.getUser(id)
            // Update UI
        }
    }
}

// Dependency injection decides which implementation
@Module
class RepositoryModule {
    @Provides
    fun provideUserRepository(
        localRepo: LocalUserRepository,
        remoteRepo: RemoteUserRepository
    ): UserRepository {
        // Return based on configuration
        return if (isOfflineMode) localRepo else remoteRepo
    }
}
```

---

### COMPOSITION OVER INHERITANCE

**Prefer composition to inheritance for better flexibility**

```kotlin
//  Inheritance approach (rigid)
open class Vehicle {
    open fun start() { println("Starting vehicle") }
}

class Car : Vehicle() {
    override fun start() {
        println("Starting car engine")
    }

    fun drive() { println("Driving car") }
}

class ElectricCar : Car() {  // Problem: ElectricCar is forced to inherit Car
    override fun start() {
        println("Starting electric motor")  // Different from car
    }

    // What if ElectricCar needs different behavior?
    // Inheritance hierarchy becomes complex
}

//  Composition approach (flexible)
interface Engine {
    fun start()
}

class GasEngine : Engine {
    override fun start() {
        println("Starting gas engine")
    }
}

class ElectricMotor : Engine {
    override fun start() {
        println("Starting electric motor")
    }
}

class FlexibleCar(private val engine: Engine) {  // Composition
    fun start() {
        engine.start()
    }

    fun drive() {
        println("Driving car")
    }
}

// Usage:
val gasCar = FlexibleCar(GasEngine())
gasCar.start()  // Starting gas engine

val electricCar = FlexibleCar(ElectricMotor())
electricCar.start()  // Starting electric motor

// Easy to add new engine types without changing Car
class HybridEngine : Engine {
    override fun start() {
        println("Starting hybrid engine")
    }
}

val hybridCar = FlexibleCar(HybridEngine())
```

**Real Android Example:**
```kotlin
//  Inheritance (rigid)
abstract class BaseFragment : Fragment() {
    abstract fun setupUI()
    abstract fun loadData()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        setupUI()
        loadData()
    }
}

// Problem: All fragments forced to inherit BaseFragment
// Hard to reuse setupUI or loadData independently

//  Composition (flexible)
interface UISetup {
    fun setupUI(fragment: Fragment)
}

interface DataLoader {
    fun loadData(fragment: Fragment)
}

class StandardUISetup : UISetup {
    override fun setupUI(fragment: Fragment) {
        // Standard UI setup
    }
}

class CustomUISetup : UISetup {
    override fun setupUI(fragment: Fragment) {
        // Custom UI setup
    }
}

class NetworkDataLoader : DataLoader {
    override fun loadData(fragment: Fragment) {
        // Load from network
    }
}

class MyFragment : Fragment() {
    private val uiSetup: UISetup = StandardUISetup()
    private val dataLoader: DataLoader = NetworkDataLoader()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        uiSetup.setupUI(this)
        dataLoader.loadData(this)
    }
}

// Easy to mix and match behaviors
class AnotherFragment : Fragment() {
    private val uiSetup: UISetup = CustomUISetup()  // Different UI
    private val dataLoader: DataLoader = NetworkDataLoader()  // Same data

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        uiSetup.setupUI(this)
        dataLoader.loadData(this)
    }
}
```

---

### COMMON OOP PITFALLS

**1. God Objects**
```kotlin
//  Bad: Class does everything
class UserManager {
    fun createUser() { }
    fun deleteUser() { }
    fun validateUser() { }
    fun authenticateUser() { }
    fun sendEmail() { }
    fun logActivity() { }
    fun generateReport() { }
    fun processPayment() { }
    // ... 50 more methods
}

//  Good: Single Responsibility
class UserService {
    fun createUser() { }
    fun deleteUser() { }
}

class UserValidator {
    fun validate(user: User): Boolean { }
}

class AuthenticationService {
    fun authenticate(credentials: Credentials): Boolean { }
}

class EmailService {
    fun sendEmail(to: String, subject: String, body: String) { }
}
```

**2. Deep Inheritance Hierarchies**
```kotlin
//  Bad: Too deep
open class A
open class B : A()
open class C : B()
open class D : C()
open class E : D()  // Too deep, hard to understand

//  Good: Shallow, use composition
interface Behavior1
interface Behavior2
interface Behavior3

class MyClass : Behavior1, Behavior2, Behavior3
```

**3. Leaky Abstractions**
```kotlin
//  Bad: Abstraction leaks implementation details
interface DataStore {
    fun save(data: String)
    fun getSQLConnection(): Connection  //  Leaks SQL implementation!
}

//  Good: Pure abstraction
interface DataStore {
    fun save(data: String)
    fun load(): String
}
```

---

### KEY TAKEAWAYS

1. **Encapsulation** - bundle data + methods, control access
2. **Inheritance** - IS-A relationship, code reuse
3. **Polymorphism** - same interface, different implementations
4. **Abstraction** - hide complexity, show essentials
5. **Composition > Inheritance** - more flexible
6. **Interfaces** for multiple inheritance, CAN-DO relationships
7. **Abstract classes** for IS-A with shared code
8. **Avoid deep inheritance** - prefer shallow hierarchies
9. **Single Responsibility** - each class does one thing
10. **Program to interfaces** - depend on abstractions

---

## Russian Version

### Постановка задачи

Объектно-ориентированное программирование (ООП) - парадигма, основанная на объектах, содержащих данные и поведение. Четыре столпа ООП—Инкапсуляция, Наследование, Полиморфизм и Абстракция—обеспечивают структуру для создания поддерживаемого, переиспользуемого кода.

**Вопрос:** Каковы четыре столпа ООП? Как работают инкапсуляция, наследование, полиморфизм и абстракция? Когда использовать композицию вместо наследования? Какие распространённые ошибки ООП?

### Ключевые выводы

1. **Инкапсуляция** - связывание данных + методов, контроль доступа
2. **Наследование** - отношение IS-A, переиспользование кода
3. **Полиморфизм** - одинаковый интерфейс, разные реализации
4. **Абстракция** - скрытие сложности, показ сущностей
5. **Композиция > Наследование** - более гибкая
6. **Интерфейсы** для множественного наследования, отношения CAN-DO
7. **Абстрактные классы** для IS-A с общим кодом
8. **Избегайте глубокого наследования** - предпочитайте плоские иерархии
9. **Single Responsibility** - каждый класс делает одно
10. **Программируйте к интерфейсам** - зависьте от абстракций

## Follow-ups

1. What is the Liskov Substitution Principle?
2. How does Kotlin's delegation work (by keyword)?
3. What are mixins and how do they relate to OOP?
4. What is the difference between association, aggregation, and composition?
5. How do you handle the diamond problem in multiple inheritance?
6. What are the benefits of immutability in OOP?
7. How does OOP relate to functional programming?
8. What are data classes and when to use them?
9. How do you design for testability in OOP?
10. What is dependency inversion and how does it improve OOP design?

---

## Related Questions

### Prerequisites (Easier)
- [[q-xml-acronym--programming-languages--easy]] - Computer Science
- [[q-data-structures-overview--algorithms--easy]] - Data Structures

### Related (Medium)
- [[q-clean-code-principles--software-engineering--medium]] - Computer Science
- [[q-default-vs-io-dispatcher--programming-languages--medium]] - Computer Science

### Advanced (Harder)
- [[q-os-fundamentals-concepts--computer-science--hard]] - Computer Science
