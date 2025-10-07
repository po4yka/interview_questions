---
tags:
  - design-patterns
  - structural-patterns
  - composite
  - gof-patterns
  - tree-structure
difficulty: medium
status: draft
---

# Composite Pattern

**English**: What is the Composite pattern? When and why should it be used?

## Answer

**Composite (Компоновщик)** - это структурный паттерн проектирования, который позволяет сгруппировать объекты в древовидную структуру для представления иерархии "часть-целое". Компоновщик позволяет клиентам обращаться к отдельным объектам и к группам объектов одинаково.

### Определение

The Composite Design Pattern is a structural design pattern that **lets you compose objects into tree-like structures to represent part-whole hierarchies**. It allows clients to treat individual objects and compositions of objects uniformly.

### Проблемы, которые решает

The composite design pattern solves problems like:

1. **Represent a part-whole hierarchy so that clients can treat part and whole objects uniformly**
2. **Represent a part-whole hierarchy as tree structure**
3. **Avoid having to treat `Part` and `Whole` objects separately** - This complicates client code

### Решение

Solutions the Composite design pattern describes:

- Define a unified **`Component`** interface for part (`Leaf`) objects and whole (`Composite`) objects
- Individual **`Leaf`** objects implement the Component interface directly
- **`Composite`** objects forward requests to their child components

This enables clients to work through the Component interface to treat Leaf and Composite objects uniformly. Composite objects forward requests recursively downwards the tree structure.

## Пример: Employee Hierarchy

```kotlin
// Component
interface Employee {
    fun showDetails(): String
}

// Leaf
class Developer(
    private val name: String,
    private val position: String
) : Employee {
    override fun showDetails() = "Developer: $name, Position: $position"
}

// Composite
class Manager(
    private val name: String,
    private val position: String
) : Employee {
    private val employees: MutableList<Employee> = mutableListOf()

    fun addEmployee(employee: Employee) {
        employees.add(employee)
    }

    fun removeEmployee(employee: Employee) {
        employees.remove(employee)
    }

    override fun showDetails(): String {
        val employeeDetails = employees.joinToString("\n") { "  " + it.showDetails() }
        return "Manager: $name, Position: $position\n$employeeDetails"
    }
}

fun main() {
    val dev1 = Developer("John Doe", "Frontend Developer")
    val dev2 = Developer("Jane Smith", "Backend Developer")

    val manager = Manager("Ella White", "Tech Lead")
    manager.addEmployee(dev1)
    manager.addEmployee(dev2)

    val cto = Manager("Bob Johnson", "CTO")
    cto.addEmployee(manager)

    println(cto.showDetails())
}
```

## Android Example: View Hierarchy

```kotlin
// Component interface
interface ViewComponent {
    fun draw()
    fun measure(widthSpec: Int, heightSpec: Int)
}

// Leaf - Simple view
class TextView(private val text: String) : ViewComponent {
    override fun draw() {
        println("Drawing TextView: $text")
    }

    override fun measure(widthSpec: Int, heightSpec: Int) {
        println("Measuring TextView: $text")
    }
}

class ImageView(private val imageUrl: String) : ViewComponent {
    override fun draw() {
        println("Drawing ImageView: $imageUrl")
    }

    override fun measure(widthSpec: Int, heightSpec: Int) {
        println("Measuring ImageView: $imageUrl")
    }
}

// Composite - ViewGroup
class LinearLayout(
    private val orientation: String
) : ViewComponent {
    private val children = mutableListOf<ViewComponent>()

    fun addView(view: ViewComponent) {
        children.add(view)
    }

    fun removeView(view: ViewComponent) {
        children.remove(view)
    }

    override fun draw() {
        println("Drawing LinearLayout ($orientation)")
        children.forEach { it.draw() }
    }

    override fun measure(widthSpec: Int, heightSpec: Int) {
        println("Measuring LinearLayout ($orientation)")
        children.forEach { it.measure(widthSpec, heightSpec) }
    }
}

// Usage - Building view hierarchy
fun buildUI(): ViewComponent {
    val rootLayout = LinearLayout("vertical")

    val headerLayout = LinearLayout("horizontal")
    headerLayout.addView(ImageView("logo.png"))
    headerLayout.addView(TextView("My App"))

    val contentLayout = LinearLayout("vertical")
    contentLayout.addView(TextView("Welcome"))
    contentLayout.addView(ImageView("banner.jpg"))

    rootLayout.addView(headerLayout)
    rootLayout.addView(contentLayout)

    return rootLayout
}

fun main() {
    val ui = buildUI()
    ui.measure(1080, 1920)
    ui.draw()
}
```

## Kotlin Example: File System

```kotlin
// Component
interface FileSystemComponent {
    fun getSize(): Long
    fun print(indent: String = "")
}

// Leaf - File
class File(
    private val name: String,
    private val size: Long
) : FileSystemComponent {
    override fun getSize() = size

    override fun print(indent: String) {
        println("$indent📄 $name ($size bytes)")
    }
}

// Composite - Directory
class Directory(private val name: String) : FileSystemComponent {
    private val contents = mutableListOf<FileSystemComponent>()

    fun add(component: FileSystemComponent) {
        contents.add(component)
    }

    fun remove(component: FileSystemComponent) {
        contents.remove(component)
    }

    override fun getSize(): Long = contents.sumOf { it.getSize() }

    override fun print(indent: String) {
        println("$indent📁 $name/")
        contents.forEach { it.print("$indent  ") }
    }
}

// Usage
fun main() {
    val root = Directory("root")

    val docs = Directory("documents")
    docs.add(File("resume.pdf", 1024))
    docs.add(File("cover_letter.docx", 512))

    val photos = Directory("photos")
    photos.add(File("vacation.jpg", 2048))
    photos.add(File("family.png", 1536))

    root.add(docs)
    root.add(photos)
    root.add(File("readme.txt", 256))

    root.print()
    println("\nTotal size: ${root.getSize()} bytes")
}
```

### Объяснение

**Explanation**:

- **`Employee`/`ViewComponent`** is the component interface providing uniform methods
- **`Developer`/`TextView`** is a leaf that implements the interface directly
- **`Manager`/`LinearLayout`** is a composite containing list of components
- Composite forwards operations to children, aggregating results
- **Android**: View hierarchy (ViewGroup/View), menu structures, drawable layers

## Когда использовать?

When to use:

1. **Tree-like structures** - Natural hierarchies where objects compose other objects (file systems, UI components, organizational structures)
2. **Recursive structures** - Objects made up of smaller objects of same type
3. **Simplifying client code** - Want to treat individual and composite objects uniformly
4. **Part-whole hierarchies** - Need to represent part-whole relationships

## Преимущества и недостатки

### Pros (Преимущества)

1. **Flexibility** - Easy to add new component types
2. **Simplified client code** - Treat individual and composite objects the same
3. **Improved scalability** - Build complex hierarchies easily
4. **Reduced coupling** - Clients don't know if working with leaf or composite
5. **Open/Closed Principle** - Add new components without changing existing code

### Cons (Недостатки)

1. **Increased complexity** - More complex for simple cases
2. **Performance overhead** - Extra layers of abstraction
3. **Limited functionality** - Best for similar objects in hierarchy
4. **Overly general** - Component interface may be too general

## Best Practices

```kotlin
// ✅ DO: Use for tree structures
interface UIComponent {
    fun render(): String
    fun onClick()
}

class Button(private val text: String) : UIComponent {
    override fun render() = "<button>$text</button>"
    override fun onClick() = println("Button clicked: $text")
}

class Panel : UIComponent {
    private val children = mutableListOf<UIComponent>()
    fun add(component: UIComponent) { children.add(component) }

    override fun render() = children.joinToString("") { it.render() }
    override fun onClick() { children.forEach { it.onClick() } }
}

// ✅ DO: Use with Iterator pattern for traversal
class CompositeIterator(root: FileSystemComponent) : Iterator<FileSystemComponent> {
    // Implementation
}

// ✅ DO: Consider using sealed classes in Kotlin
sealed class MenuItem {
    abstract val title: String

    data class Item(override val title: String, val action: () -> Unit) : MenuItem()
    data class SubMenu(override val title: String, val items: List<MenuItem>) : MenuItem()
}

// ❌ DON'T: Use for fundamentally different types
// ❌ DON'T: Make all operations mandatory in component interface
// ❌ DON'T: Allow adding leafs to leafs
```

**English**: **Composite** is a structural pattern that composes objects into tree structures to represent part-whole hierarchies, allowing uniform treatment of individual and composite objects. **Problem**: Need to represent tree structures and treat parts/wholes uniformly. **Solution**: Define component interface, implement with leaves (individual) and composites (containers). **Use when**: (1) Tree structures, (2) Part-whole hierarchies, (3) Want uniform treatment. **Android**: View hierarchy, menu structures, drawable layers. **Pros**: flexibility, simplified client code, scalability. **Cons**: complexity, performance overhead. **Examples**: View hierarchy, file system, organizational chart, menu structures.

## Links

- [Composite Design Pattern in Java](https://www.geeksforgeeks.org/composite-design-pattern-in-java/)
- [Composite pattern](https://en.wikipedia.org/wiki/Composite_pattern)
- [Composite Design Pattern in Kotlin](https://www.javaguides.net/2023/10/composite-design-pattern-in-kotlin.html)

## Further Reading

- [Composite Design Pattern](https://sourcemaking.com/design_patterns/composite)
- [Composite](https://refactoring.guru/design-patterns/composite)

---
*Source: Kirchhoff Android Interview Questions*
