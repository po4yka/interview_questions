---
id: cs-025
title: "Composite Pattern / Паттерн Composite"
aliases: ["Composite Pattern", "Паттерн Composite"]
topic: cs
subtopics: [design-patterns, gof-patterns, structural-patterns]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-architecture-patterns, q-adapter-pattern--cs--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [composite, design-patterns, difficulty/medium, gof-patterns, structural-patterns, tree-structure]
sources: ["https://en.wikipedia.org/wiki/Composite_pattern"]

date created: Saturday, November 1st 2025, 1:24:31 pm
date modified: Tuesday, November 25th 2025, 8:53:54 pm
---

# Вопрос (RU)
> Что такое паттерн Composite? Когда и зачем его использовать?

# Question (EN)
> What is the Composite pattern? When and why should it be used?

---

## Ответ (RU)

**Теория паттерна Composite:**
Composite (Компоновщик) - структурный паттерн проектирования, который позволяет компоновать объекты в древовидные структуры для представления иерархий "часть-целое". Позволяет клиентам единообразно обрабатывать отдельные объекты (Leaf) и композиции объектов (Composite). Ключевая идея - рекурсивная композиция и общий интерфейс для всех элементов.

**Проблемы, которые решает:**

1. **Необходимость единообразной обработки** отдельных объектов и композиций
2. **Представление иерархии "часть-целое"** в виде древовидной структуры
3. **Избежание различной обработки** Leaf и Composite объектов (усложняет клиентский код)

**Решение:**

*Теория:* Определить единый интерфейс `Component` для Leaf (листья) и Composite (композиции). Leaf реализует интерфейс напрямую. Composite содержит коллекцию `Component` и делегирует запросы дочерним компонентам рекурсивно вниз по дереву.

**Структура паттерна:**

- **Component** (интерфейс) - объявляет общие операции для Leaf и Composite
- **Leaf** - конечный элемент (не имеет детей), реализует `Component`
- **Composite** - контейнер, содержит детей (Leaf или Composite), реализует `Component`, делегирует операции детям
- **Client** - работает с `Component`, не различая Leaf и Composite

**Когда использовать:**

✅ **Используйте Composite:**
- Нужно представить иерархию "часть-целое"
- Клиенты должны единообразно обрабатывать отдельные объекты и композиции
- Структура имеет древовидную форму (файловая система, UI компоненты, организационная структура)
- Нужна рекурсивная обработка структуры

**Пример 1: Файловая система:**

*Теория:* Классический пример Composite. `File` (Leaf) и `Directory` (Composite) реализуют `FileSystemComponent`. `Directory` содержит список детей и рекурсивно вычисляет размер.

```kotlin
// ✅ Component интерфейс
interface FileSystemComponent {
    fun getSize(): Long
    fun print(indent: String = "")
}

// ✅ Leaf - File
class File(
    private val name: String,
    private val size: Long
) : FileSystemComponent {
    override fun getSize() = size

    override fun print(indent: String) {
        println("$indent- $name ($size bytes)")
    }
}

// ✅ Composite - Directory
class Directory(
    private val name: String
) : FileSystemComponent {
    private val children = mutableListOf<FileSystemComponent>()

    fun add(component: FileSystemComponent) {
        children.add(component)
    }

    fun remove(component: FileSystemComponent) {
        children.remove(component)
    }

    override fun getSize(): Long {
        // Рекурсивно суммируем размеры детей
        return children.sumOf { it.getSize() }
    }

    override fun print(indent: String) {
        println("$indent+ $name/")
        children.forEach { it.print("$indent  ") }
    }
}

// ✅ Client - единообразная обработка
fun main() {
    val root = Directory("root")

    val docs = Directory("docs")
    docs.add(File("readme.txt", 1024))
    docs.add(File("guide.pdf", 5120))

    val images = Directory("images")
    images.add(File("logo.png", 2048))

    root.add(docs)
    root.add(images)
    root.add(File("config.json", 512))

    println("Total size: ${root.getSize()} bytes")
    root.print()
}
```

**Пример 2: UI компоненты (Android `View` Hierarchy):**

*Теория:* Система Android `View` является примером использования идей Composite: `View` (Leaf) и `ViewGroup` (Composite) реализуют общий контракт отображения/измерения. `ViewGroup` содержит детей и рекурсивно вызывает measure/draw. Ниже упрощенный пример, иллюстрирующий структуру, а не реальное API.

```kotlin
// ✅ Component интерфейс
interface ViewComponent {
    fun draw()
    fun measure(widthSpec: Int, heightSpec: Int)
}

// ✅ Leaf - TextView
class TextView(private val text: String) : ViewComponent {
    override fun draw() {
        println("Drawing TextView: $text")
    }

    override fun measure(widthSpec: Int, heightSpec: Int) {
        println("Measuring TextView: $text")
    }
}

// ✅ Composite - LinearLayout (упрощенный пример)
class LinearLayout(
    private val orientation: String
) : ViewComponent {
    private val children = mutableListOf<ViewComponent>()

    fun addView(view: ViewComponent) {
        children.add(view)
    }

    override fun draw() {
        println("Drawing LinearLayout ($orientation)")
        children.forEach { it.draw() }  // Рекурсивно
    }

    override fun measure(widthSpec: Int, heightSpec: Int) {
        println("Measuring LinearLayout ($orientation)")
        children.forEach { it.measure(widthSpec, heightSpec) }  // Рекурсивно
    }
}

// ✅ Client - строим иерархию
fun buildUI(): ViewComponent {
    val root = LinearLayout("vertical")

    val header = LinearLayout("horizontal")
    header.addView(TextView("Logo"))
    header.addView(TextView("Title"))

    root.addView(header)
    root.addView(TextView("Content"))

    return root
}
```

**Пример 3: Организационная структура:**

*Теория:* Сотрудники (`Developer` - Leaf) и менеджеры (`Manager` - Composite). `Manager` содержит подчинённых и рекурсивно показывает детали.

```kotlin
// ✅ Component интерфейс
interface Employee {
    fun showDetails(): String
    fun getSalary(): Double
}

// ✅ Leaf - Developer
class Developer(
    private val name: String,
    private val salary: Double
) : Employee {
    override fun showDetails() = "Developer: $name"
    override fun getSalary() = salary
}

// ✅ Composite - Manager
class Manager(
    private val name: String,
    private val salary: Double
) : Employee {
    private val team = mutableListOf<Employee>()

    fun addEmployee(employee: Employee) {
        team.add(employee)
    }

    override fun showDetails(): String {
        val teamDetails = team.joinToString("\n") { "  ${it.showDetails()}" }
        return "Manager: $name\n$teamDetails"
    }

    override fun getSalary(): Double {
        // Рекурсивно суммируем зарплаты команды
        return salary + team.sumOf { it.getSalary() }
    }
}
```

**Преимущества:**

1. **Единообразная обработка** - клиент не различает Leaf и Composite
2. **Упрощение клиентского кода** - нет необходимости проверять тип
3. **Open/Closed Principle** - легко добавлять новые типы компонентов
4. **Рекурсивная композиция** - можно строить сложные структуры
5. **Гибкость** - легко добавлять/удалять компоненты в runtime

**Недостатки:**

1. **Сложность ограничений** - трудно ограничить типы компонентов в Composite
2. **Overhead** - дополнительные объекты для простых структур
3. **Нарушение Interface Segregation** - при "прозрачном" интерфейсе Leaf может иметь методы управления детьми (`add`/`remove`), которые ему не нужны

**Связанные паттерны:**

- **Iterator** - для обхода Composite структуры
- **Visitor** - для операций над Composite структурой
- **Decorator** - похожая рекурсивная структура, но другая цель
- **Chain of Responsibility** - может использовать Composite для организации цепочки

**Ключевые моменты:**

1. **Рекурсия** - Composite рекурсивно делегирует операции детям
2. **Единообразие** - клиент работает через `Component` интерфейс
3. **Древовидная структура** - естественная модель для иерархий
4. **Прозрачность vs Безопасность** - "прозрачный" интерфейс делает Leaf и Composite неотличимыми для клиента (удобнее, но может нарушать ISP), "безопасный" интерфейс выносит операции управления детьми только в Composite (строже типобезопасность, но клиенту сложнее)

---

## Answer (EN)

**Composite Pattern Theory:**
Composite is a structural design pattern that allows composing objects into tree-like structures to represent part-whole hierarchies. It allows clients to treat individual objects (`Leaf`) and compositions of objects (`Composite`) uniformly. Key idea: recursive composition and a common interface for all elements.

**Problems it Solves:**

1. **Need for uniform treatment** of individual objects and compositions
2. **Representing part-whole hierarchy** as tree structure
3. **Avoiding different treatment** of `Leaf` and `Composite` objects (which complicates client code)

**Solution:**

*Theory:* Define a unified `Component` interface for `Leaf` and `Composite`. `Leaf` implements the interface directly. `Composite` contains a collection of `Component` and delegates requests to its children recursively down the tree.

**Pattern Structure:**

- **Component** (interface) - declares common operations for `Leaf` and `Composite`
- **Leaf** - leaf element (no children), implements `Component`
- **Composite** - container, holds children (`Leaf` or `Composite`), implements `Component`, delegates operations to children
- **Client** - works with `Component` without distinguishing `Leaf` and `Composite`

**When to Use:**

✅ **Use Composite when:**
- You need to represent part-whole hierarchy
- Clients should treat individual objects and compositions uniformly
- The structure is naturally tree-like (file system, UI components, organizational structure)
- You need recursive processing of the structure

**Example 1: File System:**

*Theory:* Classic Composite example. `File` (Leaf) and `Directory` (Composite) implement `FileSystemComponent`. `Directory` holds child components and recursively calculates size.

```kotlin
// ✅ Component interface
interface FileSystemComponent {
    fun getSize(): Long
    fun print(indent: String = "")
}

// ✅ Leaf - File
class File(
    private val name: String,
    private val size: Long
) : FileSystemComponent {
    override fun getSize() = size

    override fun print(indent: String) {
        println("$indent- $name ($size bytes)")
    }
}

// ✅ Composite - Directory
class Directory(
    private val name: String
) : FileSystemComponent {
    private val children = mutableListOf<FileSystemComponent>()

    fun add(component: FileSystemComponent) {
        children.add(component)
    }

    fun remove(component: FileSystemComponent) {
        children.remove(component)
    }

    override fun getSize(): Long {
        // Recursively sum children sizes
        return children.sumOf { it.getSize() }
    }

    override fun print(indent: String) {
        println("$indent+ $name/")
        children.forEach { it.print("$indent  ") }
    }
}

// ✅ Client - uniform treatment
fun main() {
    val root = Directory("root")

    val docs = Directory("docs")
    docs.add(File("readme.txt", 1024))
    docs.add(File("guide.pdf", 5120))

    val images = Directory("images")
    images.add(File("logo.png", 2048))

    root.add(docs)
    root.add(images)
    root.add(File("config.json", 512))

    println("Total size: ${root.getSize()} bytes")
    root.print()
}
```

**Example 2: UI Components (Android `View` Hierarchy):**

*Theory:* The Android `View` system is an example of applying Composite ideas: `View` (Leaf) and `ViewGroup` (Composite) share common rendering/measurement contracts. `ViewGroup` holds children and calls measure/draw recursively. The simplified example below illustrates the structure, not the exact Android APIs.

```kotlin
// ✅ Component interface
interface ViewComponent {
    fun draw()
    fun measure(widthSpec: Int, heightSpec: Int)
}

// ✅ Leaf - TextView
class TextView(private val text: String) : ViewComponent {
    override fun draw() {
        println("Drawing TextView: $text")
    }

    override fun measure(widthSpec: Int, heightSpec: Int) {
        println("Measuring TextView: $text")
    }
}

// ✅ Composite - LinearLayout (simplified example)
class LinearLayout(
    private val orientation: String
) : ViewComponent {
    private val children = mutableListOf<ViewComponent>()

    fun addView(view: ViewComponent) {
        children.add(view)
    }

    override fun draw() {
        println("Drawing LinearLayout ($orientation)")
        children.forEach { it.draw() }  // Recursively
    }

    override fun measure(widthSpec: Int, heightSpec: Int) {
        println("Measuring LinearLayout ($orientation)")
        children.forEach { it.measure(widthSpec, heightSpec) }  // Recursively
    }
}

// ✅ Client - build hierarchy
fun buildUI(): ViewComponent {
    val root = LinearLayout("vertical")

    val header = LinearLayout("horizontal")
    header.addView(TextView("Logo"))
    header.addView(TextView("Title"))

    root.addView(header)
    root.addView(TextView("Content"))

    return root
}
```

**Example 3: Organizational Structure:**

*Theory:* Employees (`Developer` - Leaf) and managers (`Manager` - Composite). `Manager` contains subordinates and recursively shows details.

```kotlin
// ✅ Component interface
interface Employee {
    fun showDetails(): String
    fun getSalary(): Double
}

// ✅ Leaf - Developer
class Developer(
    private val name: String,
    private val salary: Double
) : Employee {
    override fun showDetails() = "Developer: $name"
    override fun getSalary() = salary
}

// ✅ Composite - Manager
class Manager(
    private val name: String,
    private val salary: Double
) : Employee {
    private val team = mutableListOf<Employee>()

    fun addEmployee(employee: Employee) {
        team.add(employee)
    }

    override fun showDetails(): String {
        val teamDetails = team.joinToString("\n") { "  ${it.showDetails()}" }
        return "Manager: $name\n$teamDetails"
    }

    override fun getSalary(): Double {
        // Recursively sum team salaries
        return salary + team.sumOf { it.getSalary() }
    }
}
```

**Advantages:**

1. **Uniform treatment** - client doesn't distinguish `Leaf` and `Composite`
2. **Simplified client code** - no need for type checks
3. **Open/Closed Principle** - easy to add new component types
4. **Recursive composition** - can build complex structures
5. **Flexibility** - easy to add/remove components at runtime

**Disadvantages:**

1. **Constraint complexity** - hard to restrict which component types `Composite` can contain
2. **Overhead** - additional objects/abstraction for simple structures
3. **Interface Segregation violation** - with a "transparent" interface, `Leaf` may expose child-management methods (`add`/`remove`) it does not need

**Related Patterns:**

- **Iterator** - for traversing Composite structures
- **Visitor** - for operations on Composite structures
- **Decorator** - similar recursive structure, but different intent
- **Chain of Responsibility** - can be combined with Composite to organize chains

**Key Points:**

1. **Recursion** - Composite recursively delegates operations to children
2. **Uniformity** - client works through the `Component` interface
3. **Tree structure** - natural model for hierarchical data
4. **Transparency vs Safety** - "transparent" interface makes `Leaf` and `Composite` indistinguishable to clients (easier to use, may hurt ISP); "safe" interface exposes child-management only on `Composite` (better type safety, but less uniform)

---

## Дополнительные Вопросы (RU)

- В чем разница между паттернами Composite и Decorator?
- Как реализовать обход дерева в паттерне Composite?
- В чем суть компромисса между прозрачностью и безопасностью интерфейса в Composite?

## Follow-ups

- What is the difference between Composite and Decorator patterns?
- How do you implement tree traversal in Composite pattern?
- What is the transparency vs safety trade-off?

## Связанные Вопросы / Предпосылки (RU)

### Базовые Знания (проще)
- Базовые знания ООП и рекурсии

## Related Questions

### Prerequisites (Easier)
- Basic OOP and recursion concepts

## References

- [[c-architecture-patterns]]
- [[q-adapter-pattern--cs--medium]]