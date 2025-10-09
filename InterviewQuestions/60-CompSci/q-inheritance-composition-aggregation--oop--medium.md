---
tags:
  - aggregation
  - composition
  - design-patterns
  - has-a
  - inheritance
  - is-a
  - oop
  - relationships
difficulty: medium
status: reviewed
---

# В чём различия наследования, композиции, агрегации?

**English**: What are the differences between inheritance, composition, and aggregation?

## Answer

**Inheritance**, **Composition**, and **Aggregation** are three fundamental relationships in object-oriented programming for modeling connections between classes.

## 1. Inheritance (IS-A Relationship)

**Inheritance** is a mechanism where one class inherits properties and methods from another class, establishing an **"is-a" relationship**.

### Key Characteristics

- **Class hierarchy** - parent-child relationship
- **Polymorphism** - subclasses can be used as parent type
- **Strong coupling** - child class depends on parent implementation
- **Code reuse** - inherit behavior from parent

### Example

```kotlin
// - Inheritance: Dog IS-A Animal
open class Animal(val name: String) {
    open fun makeSound() {
        println("Some generic animal sound")
    }

    fun sleep() {
        println("$name is sleeping")
    }
}

class Dog(name: String, val breed: String) : Animal(name) {
    override fun makeSound() {
        println("$name barks: Woof!")
    }

    fun fetch() {
        println("$name is fetching the ball")
    }
}

class Cat(name: String) : Animal(name) {
    override fun makeSound() {
        println("$name meows: Meow!")
    }
}

// Usage
val dog: Animal = Dog("Buddy", "Golden Retriever")  // Polymorphism
dog.makeSound()  // "Buddy barks: Woof!"
dog.sleep()      // "Buddy is sleeping"
```

### When to Use Inheritance

- **Use inheritance when:**
- Clear **"is-a" relationship** exists (Dog IS-A Animal)
- Shared behavior across related classes
- Need polymorphism (treat Dog as Animal)
- Hierarchy is stable and unlikely to change

- **Avoid inheritance when:**
- No clear "is-a" relationship
- Need to combine multiple behaviors
- Hierarchy becomes too deep or complex

---

## 2. Composition (HAS-A Relationship, Strong)

**Composition** is when one class contains objects of other classes as fields, **owning them completely**. The contained objects' **lifecycle depends on the container**.

### Key Characteristics

- **Ownership** - container owns the components
- **Lifecycle dependency** - components destroyed with container
- **Strong coupling** - components are part of the whole
- **Encapsulation** - components hidden from outside
- **Flexibility** - easy to change composition at runtime

### Example

```kotlin
// - Composition: Car HAS-A Engine (strong ownership)
class Engine(val type: String, val horsepower: Int) {
    fun start() {
        println("Engine $type started")
    }

    fun stop() {
        println("Engine stopped")
    }
}

class Transmission(val type: String) {
    fun shiftGear(gear: Int) {
        println("Shifted to gear $gear")
    }
}

class Wheels(val count: Int, val size: Int) {
    fun rotate() {
        println("$count wheels rotating")
    }
}

// Composition: Car owns Engine, Transmission, Wheels
class Car(
    val model: String,
    engineType: String,
    engineHp: Int
) {
    // Components created inside Car
    private val engine = Engine(engineType, engineHp)
    private val transmission = Transmission("Automatic")
    private val wheels = Wheels(4, 18)

    fun start() {
        println("Starting $model")
        engine.start()
        transmission.shiftGear(1)
        wheels.rotate()
    }

    fun stop() {
        engine.stop()
        println("$model stopped")
    }
}

// Usage
val car = Car("Tesla Model 3", "Electric", 283)
car.start()
// When car is destroyed, engine, transmission, wheels are also destroyed
```

**Key point:** Engine, Transmission, Wheels **cannot exist without Car**. When Car is destroyed, all components are destroyed.

---

## 3. Aggregation (HAS-A Relationship, Weak)

**Aggregation** is a special case of composition where objects **can exist independently** of their container. It represents a **weak "has-a" relationship**.

### Key Characteristics

- **Weak coupling** - components independent of container
- **Shared lifecycle** - components can outlive container
- **Flexibility** - components can be shared or replaced
- **Association** - represents a relationship, not ownership

### Example

```kotlin
// - Aggregation: Department HAS-A Employee (weak ownership)
class Employee(
    val id: String,
    val name: String,
    val position: String
) {
    fun work() {
        println("$name is working as $position")
    }
}

// Aggregation: Department uses Employees, but doesn't own them
class Department(
    val name: String,
    val employees: MutableList<Employee> = mutableListOf()
) {
    fun addEmployee(employee: Employee) {
        employees.add(employee)
        println("${employee.name} joined $name department")
    }

    fun removeEmployee(employee: Employee) {
        employees.remove(employee)
        println("${employee.name} left $name department")
    }

    fun work() {
        println("$name department working:")
        employees.forEach { it.work() }
    }
}

// Usage
val alice = Employee("E001", "Alice", "Developer")
val bob = Employee("E002", "Bob", "Designer")

val engineeringDept = Department("Engineering")
engineeringDept.addEmployee(alice)
engineeringDept.addEmployee(bob)

engineeringDept.work()

// Employee can exist without Department
bob.work()  // Bob still exists

// Employee can move to different department
val designDept = Department("Design")
engineeringDept.removeEmployee(bob)
designDept.addEmployee(bob)

// Department destroyed, employees still exist
```

**Key point:** Employees **exist independently** of Department. Destroying Department doesn't destroy Employees.

---

## Comparison Table

| Aspect | Inheritance | Composition | Aggregation |
|--------|-------------|-------------|-------------|
| **Relationship** | IS-A | HAS-A (strong) | HAS-A (weak) |
| **Coupling** | Strong | Strong | Weak |
| **Lifecycle** | Shared hierarchy | Dependent | Independent |
| **Flexibility** | Low | High | High |
| **Code reuse** | Parent code | Component code | Shared objects |
| **Polymorphism** | Yes | No | No |
| **Example** | Dog IS-A Animal | Car HAS-A Engine | Department HAS-A Employee |
| **When destroyed** | Child exists independently | Components destroyed | Components survive |

---

## Visual Representation

### Inheritance
```
Animal (parent)
   ↑
   |
   ├── Dog (child)
   ├── Cat (child)
   └── Bird (child)
```

### Composition (Car owns Engine)
```
Car
 ├── Engine     (owned, dies with Car)
 ├── Transmission (owned, dies with Car)
 └── Wheels     (owned, dies with Car)
```

### Aggregation (Department uses Employees)
```
Department
 ├── Employee (independent, survives)
 ├── Employee (independent, survives)
 └── Employee (independent, survives)
```

---

## Android Examples

### Inheritance Example

```kotlin
// Base class for all UI components
abstract class UIComponent(val id: String) {
    abstract fun render()

    open fun onClick() {
        println("$id clicked")
    }
}

// Button IS-A UIComponent
class Button(id: String, val text: String) : UIComponent(id) {
    override fun render() {
        println("Rendering button: $text")
    }
}

// TextView IS-A UIComponent
class TextView(id: String, val content: String) : UIComponent(id) {
    override fun render() {
        println("Rendering text: $content")
    }
}
```

### Composition Example

```kotlin
// Activity HAS-A ViewModel (composition)
class UserViewModel(private val repository: UserRepository) : ViewModel() {
    private val _users = MutableLiveData<List<User>>()
    val users: LiveData<List<User>> = _users

    init {
        loadUsers()
    }

    private fun loadUsers() {
        viewModelScope.launch {
            _users.value = repository.getUsers()
        }
    }
}

// Activity owns ViewModel (created and destroyed together)
class UserActivity : AppCompatActivity() {
    // Composition: ViewModel created for this Activity
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // ViewModel lifecycle tied to Activity
    }
}
```

### Aggregation Example

```kotlin
// Fragment HAS-A Adapter (aggregation)
class UserListFragment : Fragment() {

    // Aggregation: Adapter can exist independently
    private var adapter: UserAdapter? = null

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Create or reuse adapter
        adapter = UserAdapter()

        binding.recyclerView.adapter = adapter
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // Adapter can be reused elsewhere
        binding.recyclerView.adapter = null
        // Don't set adapter = null, might be reused
    }
}
```

---

## Best Practices

### Favor Composition Over Inheritance

**Why?**
- More flexible
- Easier to test
- Avoids deep hierarchies
- Reduces coupling

```kotlin
// - BAD: Deep inheritance hierarchy
open class Animal { ... }
open class Mammal : Animal() { ... }
open class Carnivore : Mammal() { ... }
open class Feline : Carnivore() { ... }
class Cat : Feline() { ... }  // 5 levels deep!

// - GOOD: Composition
class Cat(
    private val mobility: Mobility,
    private val diet: Diet,
    private val habitat: Habitat
) {
    fun move() = mobility.move()
    fun eat() = diet.eat()
    fun live() = habitat.getLivingSpace()
}
```

### Use Aggregation for Shared Resources

```kotlin
// - Aggregation: Multiple activities can share same database
class DatabaseManager private constructor() {
    companion object {
        val instance: DatabaseManager by lazy { DatabaseManager() }
    }
}

class UserActivity : AppCompatActivity() {
    private val database = DatabaseManager.instance  // Aggregation
}

class ProductActivity : AppCompatActivity() {
    private val database = DatabaseManager.instance  // Same instance
}
```

---

## When to Use Each

### Use Inheritance When:
- Clear "is-a" relationship exists
- Need polymorphism
- Stable hierarchy (unlikely to change)
- Shared behavior across similar classes

### Use Composition When:
- Need "has-a" relationship
- Components are parts of a whole
- Lifecycle is dependent
- Want strong encapsulation
- Need flexibility to change components

### Use Aggregation When:
- Need "has-a" relationship
- Components exist independently
- Lifecycle is independent
- Want to share objects
- Weak coupling is desired

---

## Summary

**Inheritance:**
- **IS-A** relationship
- Strong coupling, class hierarchy
- Polymorphism support
- Use when clear parent-child relationship exists

**Composition:**
- **HAS-A** relationship (strong ownership)
- Components' lifecycle depends on container
- High encapsulation
- Use when building complex objects from parts

**Aggregation:**
- **HAS-A** relationship (weak ownership)
- Components exist independently
- Weak coupling, flexible
- Use when objects can be shared or reused

**Best practice:** Favor **composition over inheritance** for flexibility and maintainability.

---

## Ответ

**Наследование** — это механизм в объектно-ориентированном программировании, позволяющий одному классу наследовать свойства и методы другого класса. Основные черты: иерархия классов, полиморфизм и связанность.

**Композиция** — метод моделирования отношений, при котором один класс содержит другие классы, инкапсулируя их в один объект. Основные черты: собственность и жизненный цикл, независимость компонентов могут быть полностью скрыты от внешнего мира, обеспечивая уровень инкапсуляции и гибкость.

**Агрегация** — специальный случай композиции, где объекты могут существовать независимо от своего контейнера. Основные черты: слабая связь и гибкость.

Выбор между наследованием, композицией и агрегацией зависит от конкретной задачи и требуемой гибкости архитектуры программного обеспечения. Как правило, рекомендуется использовать композицию или агрегацию для большей гибкости и меньшей связанности компонентов, в то время как наследование лучше подходит для случаев, когда чётко определена иерархическая модель с общим поведением.

