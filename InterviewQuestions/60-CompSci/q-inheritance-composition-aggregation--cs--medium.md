---\
id: oop-002
title: "Inheritance, Composition, Aggregation / Наследование, композиция и агрегация"
aliases: [Inheritance Composition Aggregation, композиция и агрегация, Наследование]
topic: cs
subtopics: [object-oriented, relationships]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-architecture-patterns, c-computer-science]
created: 2025-10-13
updated: 2025-11-11
tags: [cs/object-oriented, cs/relationships, design-patterns, difficulty/medium]

---\
# Вопрос (RU)
> В чём различия наследования, композиции, агрегации?

# Question (EN)
> What are the differences between inheritance, composition, and aggregation?

## Ответ (RU)

**Наследование**, **композиция** и **агрегация** — распространённые способы описания связей между классами и объектами в ООП.

### 1. Наследование (отношение IS-A)

**Наследование** — механизм, при котором один класс (дочерний) получает свойства и методы другого (базового), формируя отношение **"является" (IS-A)**.

Ключевые моменты:
- Иерархия классов: базовый класс → подклассы
- Полиморфизм: объект подкласса можно использовать через тип базового класса
- Достаточно сильная связанность: дочерний класс зависит от контракта (и часто реализации) базового
- Повторное использование кода за счёт базового класса

Пример (аналогичный EN-версии):

```kotlin
// Наследование: Dog ЯВЛЯЕТСЯ Animal
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

// Использование
val dog: Animal = Dog("Buddy", "Golden Retriever")  // Полиморфизм
dog.makeSound()  // "Buddy barks: Woof!"
dog.sleep()      // "Buddy is sleeping"
```

Когда использовать наследование:
- Есть чёткое отношение IS-A (Dog IS-A Animal)
- Нужен полиморфизм по общему базовому типу
- Иерархия понятийно стабильна

Избегайте наследования, когда:
- Нет очевидного отношения IS-A
- Нужно комбинировать независимые поведения
- Иерархия становится глубокой и хрупкой

---

### 2. Композиция (отношение HAS-A, Сильная связь)

**Композиция** — отношение, при котором один объект включает другие как составные части. В модели предполагается, что части принадлежат целому и их жизненный цикл логически зависит от него.

Ключевые моменты:
- Целое "владеет" частями в предметной области
- Части трактуются как неотъемлемые элементы целого
- Относительно сильная связь: без целого части часто теряют смысл
- Хорошая инкапсуляция: внутренние детали можно скрыть
- Гибкость: поведение строится через делегирование компонентам, а не через жёсткую иерархию

Важно: в реальных языках (Kotlin, Java и др.) композиция — это намерение в дизайне; технически объекты можно передавать и переиспользовать, но по смыслу они считаются частями одного целого.

Пример (эквивалент EN):

```kotlin
// Композиция: Car ИМЕЕТ Engine (сильное владение в модели)
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

// Car состоит из Engine, Transmission, Wheels
class Car(
    val model: String,
    engineType: String,
    engineHp: Int
) {
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

// Использование
val car = Car("Tesla Model 3", "Electric", 283)
car.start()
```

Ключевая идея: компоненты моделируются как части целого и обычно создаются, управляются и уничтожаются через это целое.

---

### 3. Агрегация (отношение HAS-A, Слабая связь)

**Агрегация** — вид ассоциации, при котором объект-составляющая может существовать независимо от агрегирующего объекта. Это более слабое отношение HAS-A, без жёсткого владения.

Ключевые моменты:
- Слабая связанность
- Независимый жизненный цикл: объекты могут пережить агрегатор
- Возможность разделения: один объект может использоваться несколькими агрегаторами
- Описывает связь "имеет ссылку на" / "использует", а не полное владение

Пример (эквивалент EN):

```kotlin
// Агрегация: Department ИМЕЕТ Employee (слабое владение)
class Employee(
    val id: String,
    val name: String,
    val position: String
) {
    fun work() {
        println("$name is working as $position")
    }
}

// Department хранит ссылки на Employee, но не владеет их существованием
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

// Использование
val alice = Employee("E001", "Alice", "Developer")
val bob = Employee("E002", "Bob", "Designer")

val engineeringDept = Department("Engineering")
engineeringDept.addEmployee(alice)
engineeringDept.addEmployee(bob)

engineeringDept.work()

// Employee может существовать без Department
bob.work()

// Employee может перейти в другой отдел
val designDept = Department("Design")
engineeringDept.removeEmployee(bob)
designDept.addEmployee(bob)
```

Ключевая идея: сотрудники существуют независимо от отдела; уничтожение отдела не уничтожает сотрудников.

---

### Сравнение (эквивалент таблицы)

- Наследование:
  - Отношение: IS-A
  - Связанность: сильная (иерархия типов)
  - Жизненный цикл: общий тип, зависимость от базового класса
  - Полиморфизм: да
  - Пример: Dog IS-A Animal
- Композиция:
  - Отношение: HAS-A (часть-целое, сильная связь)
  - Связанность: от сильной до умеренной
  - Жизненный цикл: части концептуально зависят от целого
  - Полиморфизм: не встроен
  - Пример: Car HAS-A Engine
- Агрегация:
  - Отношение: HAS-A (слабая связь)
  - Связанность: слабая
  - Жизненный цикл: объекты независимы, могут разделяться
  - Полиморфизм: не встроен
  - Пример: Department HAS-A Employee

---

### Визуальное Представление

Наследование:
```text
Animal (parent)
   ↑
   |
   Dog (child)
   Cat (child)
   Bird (child)
```

Композиция (Car владеет Engine):
```text
Car
  Engine       (part of Car)
  Transmission (part of Car)
  Wheels       (part of Car)
```

Агрегация (Department использует Employee):
```text
Department
  Employee (independent)
  Employee (independent)
  Employee (independent)
```

---

### Примеры Для Android

#### Наследование

```kotlin
// Базовый класс для UI-компонентов
abstract class UIComponent(val id: String) {
    abstract fun render()

    open fun onClick() {
        println("$id clicked")
    }
}

// Button ЯВЛЯЕТСЯ UIComponent
class Button(id: String, val text: String) : UIComponent(id) {
    override fun render() {
        println("Rendering button: $text")
    }
}

// TextView ЯВЛЯЕТСЯ UIComponent
class TextView(id: String, val content: String) : UIComponent(id) {
    override fun render() {
        println("Rendering text: $content")
    }
}
```

#### Композиция

```kotlin
// Activity использует ViewModel (композиция на уровне дизайна)
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

class UserActivity : AppCompatActivity() {
    // ViewModel привязан к жизненному циклу Activity как ViewModelStoreOwner
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Используем viewModel здесь
    }
}
```

#### Агрегация

```kotlin
// Fragment ИМЕЕТ Adapter (агрегация: адаптер может переиспользоваться)
class UserListFragment : Fragment() {

    private var _binding: FragmentUserListBinding? = null
    private val binding get() = _binding!!

    // Адаптер — отдельный объект, который теоретически можно разделять
    private var adapter: UserAdapter? = null

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentUserListBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        if (adapter == null) {
            adapter = UserAdapter()
        }

        binding.recyclerView.adapter = adapter
    }

    override fun onDestroyView() {
        super.onDestroyView()
        binding.recyclerView.adapter = null
        _binding = null
        // Судьба adapter зависит от того, хотим ли мы его переиспользовать
    }
}
```

Этот пример показывает, что `Fragment` может ссылаться на адаптер, не "владея" его жизненным циклом: адаптер может существовать и использоваться отдельно.

---

### Когда Что Использовать (RU)

Используйте наследование, когда:
- Есть чёткое и устойчивое отношение IS-A
- Нужен полиморфизм по базовому типу
- Общая функциональность естественно живёт в базовом классе

Используйте композицию, когда:
- Нужно отношение HAS-A / "часть-целое"
- Компоненты являются частями одного целого
- Важно инкапсулировать детали и легко менять реализацию

Используйте агрегацию, когда:
- Нужна связь HAS-A без владения
- Объекты существуют независимо и могут разделяться
- Требуется более слабая связанность между объектами

Общая рекомендация: по возможности предпочитайте композицию и агрегацию глубокому наследованию.

---

## Answer (EN)

**Inheritance**, **Composition**, and **Aggregation** are three common ways in object-oriented programming to model relationships between classes.

## 1. Inheritance (IS-A Relationship)

**Inheritance** is a mechanism where one class inherits properties and methods from another class, establishing an **"is-a" relationship**.

### Key Characteristics

- **Class hierarchy** - parent-child relationship
- **Polymorphism** - subclasses can be used as parent type
- **Strong coupling** - child class depends on parent abstraction and often its implementation
- **Code reuse** - inherit behavior from parent

### Example

```kotlin
// Inheritance: Dog IS-A Animal
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

- Use inheritance when:
  - Clear **"is-a" relationship** exists (Dog IS-A Animal)
  - Shared behavior across closely related classes
  - Need polymorphism (treat Dog as Animal)
  - Hierarchy is conceptually stable and unlikely to change drastically

- Avoid inheritance when:
  - No clear "is-a" relationship
  - Need to combine multiple orthogonal behaviors
  - Hierarchy becomes too deep or complex

---

## 2. Composition (HAS-A Relationship, Strong)

**Composition** is when one class contains objects of other classes as fields, in a way that models strong ownership: the contained objects' **lifecycle is intended to depend on the container** in the domain model.

### Key Characteristics

- **Ownership in the model** - container conceptually owns the components
- **`Lifecycle` dependency (conceptual)** - components are treated as parts; if the whole is removed, its parts usually do not make sense independently
- **Strong relationship** - components are integral to the whole
- **Encapsulation** - components can be hidden from outside
- **Flexibility** - behavior built by delegating to components rather than inheriting

Note: In typical OO languages (including Kotlin), composition is a design concept: technically, nothing prevents reusing component instances elsewhere, but the intent is that they belong to one whole.

### Example

```kotlin
// Composition: Car HAS-A Engine (strong ownership in the model)
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

// Car is composed of Engine, Transmission, Wheels
class Car(
    val model: String,
    engineType: String,
    engineHp: Int
) {
    // Here we create and encapsulate components inside Car
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
```

**Key point:** In composition, the components are modeled as parts of a whole; they are typically created, managed, and disposed of through that whole, rather than being shared arbitrarily.

---

## 3. Aggregation (HAS-A Relationship, Weak)

**Aggregation** is a form of association where objects **can exist independently** of the container. It represents a **weaker "has-a" relationship** and typically no strong ownership.

### Key Characteristics

- **Weak coupling** - components independent of container
- **Independent lifecycle** - components can outlive container
- **Can be shared** - same object may be referenced by multiple containers
- **Represents a relationship, not ownership**

### Example

```kotlin
// Aggregation: Department HAS-A Employee (weak ownership)
class Employee(
    val id: String,
    val name: String,
    val position: String
) {
    fun work() {
        println("$name is working as $position")
    }
}

// Department references Employees, but does not own their existence
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

// Employee can exist without any Department
bob.work()

// Employee can move to different department
val designDept = Department("Design")
engineeringDept.removeEmployee(bob)
designDept.addEmployee(bob)

// If Department is destroyed, employees still conceptually exist
```

**Key point:** Employees exist independently of Department. Destroying Department (in the model) doesn't destroy Employees.

---

## Comparison Table

| Aspect | Inheritance | Composition | Aggregation |
|--------|-------------|-------------|-------------|
| **Relationship** | IS-A | HAS-A (strong, part-of) | HAS-A (weak) |
| **Coupling** | Strong | Strong to moderate | Weak |
| **`Lifecycle` (conceptual)** | Shared type hierarchy | Parts depend on whole | Independent |
| **Flexibility** | Lower (hierarchy-bound) | High | High |
| **Code reuse** | Through parent | Through components | Shared objects |
| **Polymorphism** | Yes (via base type) | Not inherent | Not inherent |
| **Example** | Dog IS-A Animal | Car HAS-A Engine | Department HAS-A Employee |
| **Destruction (conceptual)** | N/A (language-specific) | Parts usually not meaningful alone | Aggregated objects survive |

---

## Visual Representation

### Inheritance
```text
Animal (parent)
   ↑
   |
   Dog (child)
   Cat (child)
   Bird (child)
```

### Composition (Car Owns Engine)
```text
Car
  Engine       (part of Car)
  Transmission (part of Car)
  Wheels       (part of Car)
```

### Aggregation (Department Uses Employees)
```text
Department
  Employee (independent)
  Employee (independent)
  Employee (independent)
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
// Activity uses a ViewModel (composition at design level)
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

class UserActivity : AppCompatActivity() {
    // ViewModel is scoped to this Activity as ViewModelStoreOwner.
    // It survives configuration changes and is cleared when the Activity is finished.
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Use viewModel here
    }
}
```

### Aggregation Example

```kotlin
// Fragment HAS-A Adapter (aggregation-like: adapter can be shared/reused)
class UserListFragment : Fragment() {

    private var _binding: FragmentUserListBinding? = null
    private val binding get() = _binding!!

    // Adapter is a separate object that could, in principle, be reused
    private var adapter: UserAdapter? = null

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentUserListBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        if (adapter == null) {
            adapter = UserAdapter()
        }

        binding.recyclerView.adapter = adapter
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // Break references from RecyclerView to avoid leaks
        binding.recyclerView.adapter = null
        _binding = null
        // Whether adapter itself is kept or discarded depends on reuse needs.
    }
}
```

This example illustrates that the `Fragment` can reference an `Adapter` without owning its existence; the `Adapter` could be managed or shared elsewhere.

---

## Best Practices

### Favor Composition Over Inheritance

Reasons:
- More flexible (behaviors composed, not locked into hierarchies)
- Often easier to test
- Avoids deep, rigid hierarchies
- Reduces tight coupling to base classes

```kotlin
// BAD: Deep inheritance hierarchy
open class Animal { /* ... */ }
open class Mammal : Animal() { /* ... */ }
open class Carnivore : Mammal() { /* ... */ }
open class Feline : Carnivore() { /* ... */ }
class Cat : Feline() { /* ... */ }  // 5 levels deep!

// GOOD: Composition
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
// Aggregation: Multiple activities can share the same database manager
class DatabaseManager private constructor() {
    companion object {
        val instance: DatabaseManager by lazy { DatabaseManager() }
    }
}

class UserActivity : AppCompatActivity() {
    private val database = DatabaseManager.instance
}

class ProductActivity : AppCompatActivity() {
    private val database = DatabaseManager.instance
}
```

Here, activities hold references to a shared object whose lifecycle is independent of any single activity.

---

## When to Use Each

### Use Inheritance When:
- Clear "is-a" relationship exists
- Need polymorphism over a common base type
- Hierarchy is stable
- Behavior is naturally shared across similar classes

### Use Composition When:
- Need a "has-a" / "part-of" relationship
- Components are parts of a whole
- Want strong encapsulation and delegation
- Need flexibility to change components or behavior without changing type hierarchy

### Use Aggregation When:
- Need a "has-a" relationship without ownership
- Components exist independently and can be shared
- Lifecycles are independent
- Want weaker coupling between collaborator objects

---

## Summary

**Inheritance:**
- **IS-A** relationship
- Strong coupling via hierarchy
- Supports polymorphism
- Use when clear parent-child relationship exists

**Composition:**
- **HAS-A** relationship with strong, part-of semantics
- Components managed and exposed via the whole
- Encourages encapsulation and flexibility

**Aggregation:**
- **HAS-A** relationship with weak ownership
- Components exist independently and may be shared
- Suitable for shared services/resources and loose coupling

Best practice: Prefer composition (and aggregation) over inheritance where possible for flexibility and maintainability.

---

## Related Questions

- [[q-inheritance-vs-composition--cs--medium]]

---

## Follow-ups

- How does "composition over inheritance" relate to SOLID principles?
- How would you refactor a deep inheritance hierarchy into composition in a real codebase?
- How do these relationships manifest differently in languages with multiple inheritance vs interfaces-only inheritance?

## References

- [[c-computer-science]]
- [[c-architecture-patterns]]
- Gang of Four, "Design Patterns" (composition over inheritance)
