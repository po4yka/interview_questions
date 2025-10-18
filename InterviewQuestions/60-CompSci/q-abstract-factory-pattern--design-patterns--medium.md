---
id: 20251012-1227111112
title: "Abstract Factory Pattern / Abstract Factory Паттерн"
topic: computer-science
difficulty: medium
status: draft
moc: moc-cs
related: [q-throw-vs-throws--programming-languages--easy, q-clean-code-principles--software-engineering--medium, q-coroutine-dispatchers--programming-languages--medium]
created: 2025-10-15
tags:
  - design-patterns
  - creational-patterns
  - abstract-factory
  - factory
  - gof-patterns
---
# Abstract Factory Pattern

# Question (EN)
> What is the Abstract Factory pattern? When and why should it be used?

# Вопрос (RU)
> Что такое паттерн Abstract Factory? Когда и зачем его использовать?

---

## Answer (EN)


**Abstract Factory (Абстрактная фабрика)** - это порождающий паттерн проектирования, целью которого является предоставление единого интерфейса для создания семейств связанных объектов с одной темой, но без раскрытия конкретной реализации.

### Definition


The Abstract Factory is a software design pattern whose goal is to provide a **single interface to create families of objects with the same theme** but without exposing the concrete implementation.

### Problems it Solves


It may be used to solve problems such as:

1. **How can an application be independent of how its objects are created?**
2. **How can a class be independent of how the objects that it requires are created?**
3. **How can families of related or dependent objects be created?**

### Why is this a problem?


Creating objects directly within the class that requires the objects is inflexible:
- Doing so **commits the class to particular objects**
- Makes it impossible to change the instantiation later without changing the class
- Prevents the class from being reusable if other objects are required
- Makes the class difficult to test because real objects cannot be replaced with mock objects

### Solution


The pattern describes how to solve such problems:

1. **Encapsulate object creation** in a separate (factory) object by defining and implementing an interface for creating objects
2. **Delegate object creation** to a factory object instead of creating objects directly

This makes a class **independent of how its objects are created**. A class may be configured with a factory object, which it uses to create objects, and the factory object can be exchanged at runtime.

### When to Use?


**When to Use Abstract Factory Pattern**?

- The **client is independent** of how we create and compose the objects in the system
- The system consists of **multiple families of objects**, and these families are designed to be used together
- We need a **run-time value to construct a particular dependency**

## Пример: UI Themes

Implementation Steps:

1. Define abstract product interfaces for different types of UI components (e.g., Button, Window)
2. Define concrete product classes for each product type and theme
3. Define an abstract factory interface that declares creation methods for each product type
4. Implement concrete factories for each theme that produce theme-specific UI components

```kotlin
// Abstract product interfaces
interface Button {
    fun display(): String
}

interface Window {
    fun display(): String
}

// Concrete products for Light theme
class LightButton : Button {
    override fun display() = "Displaying Light Theme Button"
}

class LightWindow : Window {
    override fun display() = "Displaying Light Theme Window"
}

// Concrete products for Dark theme
class DarkButton : Button {
    override fun display() = "Displaying Dark Theme Button"
}

class DarkWindow : Window {
    override fun display() = "Displaying Dark Theme Window"
}

// Abstract Factory
interface GUIFactory {
    fun createButton(): Button
    fun createWindow(): Window
}

// Concrete factories
class LightThemeFactory : GUIFactory {
    override fun createButton() = LightButton()
    override fun createWindow() = LightWindow()
}

class DarkThemeFactory : GUIFactory {
    override fun createButton() = DarkButton()
    override fun createWindow() = DarkWindow()
}

// Client code
fun main() {
    // Client code using the Abstract Factory
    val lightFactory: GUIFactory = LightThemeFactory()
    val lightButton: Button = lightFactory.createButton()
    println(lightButton.display())
    val lightWindow: Window = lightFactory.createWindow()
    println(lightWindow.display())

    val darkFactory: GUIFactory = DarkThemeFactory()
    val darkButton: Button = darkFactory.createButton()
    println(darkButton.display())
    val darkWindow: Window = darkFactory.createWindow()
    println(darkWindow.display())
}
```

**Output**:
```
Displaying Light Theme Button
Displaying Light Theme Window
Displaying Dark Theme Button
Displaying Dark Theme Window
```

### Example Explanation


**Explanation**:

- `Button` and `Window` are **abstract product interfaces** representing UI components
- `LightButton`, `LightWindow`, `DarkButton`, and `DarkWindow` are **concrete implementations** of these products, tailored for specific themes
- `GUIFactory` is the **Abstract Factory interface** which declares methods for creating products
- `LightThemeFactory` and `DarkThemeFactory` are **concrete factories** that instantiate theme-specific UI components
- The **client code** (`main` function) uses an abstract factory to create UI components, ensuring they match the chosen theme

## Android Example: Database

```kotlin
// Abstract products
interface Database {
    fun query(sql: String): List<String>
}

interface Cache {
    fun get(key: String): String?
    fun put(key: String, value: String)
}

// SQLite implementations
class SQLiteDatabase : Database {
    override fun query(sql: String): List<String> {
        println("Executing SQLite query: $sql")
        return listOf("Result from SQLite")
    }
}

class SQLiteCache : Cache {
    private val cache = mutableMapOf<String, String>()

    override fun get(key: String) = cache[key]

    override fun put(key: String, value: String) {
        cache[key] = value
    }
}

// Room implementations
class RoomDatabase : Database {
    override fun query(sql: String): List<String> {
        println("Executing Room query: $sql")
        return listOf("Result from Room")
    }
}

class RoomCache : Cache {
    private val cache = mutableMapOf<String, String>()

    override fun get(key: String) = cache[key]

    override fun put(key: String, value: String) {
        cache[key] = value
    }
}

// Abstract Factory
interface DataStorageFactory {
    fun createDatabase(): Database
    fun createCache(): Cache
}

// Concrete Factories
class SQLiteFactory : DataStorageFactory {
    override fun createDatabase() = SQLiteDatabase()
    override fun createCache() = SQLiteCache()
}

class RoomFactory : DataStorageFactory {
    override fun createDatabase() = RoomDatabase()
    override fun createCache() = RoomCache()
}

// Client
class DataManager(factory: DataStorageFactory) {
    private val database = factory.createDatabase()
    private val cache = factory.createCache()

    fun fetchData(query: String): List<String> {
        val cacheKey = "query_$query"
        cache.get(cacheKey)?.let {
            return listOf(it)
        }

        val results = database.query(query)
        cache.put(cacheKey, results.first())
        return results
    }
}
```

## Преимущества и недостатки

### Pros (Преимущества)


1. **Ensures compatibility** - Created objects are compatible and belong to the same family
2. **Promotes decoupling** - Makes it easier to introduce new families of objects without modifying existing code
3. **Enforces consistency** - Enforces a consistent interface for creating objects, enhancing maintainability and readability
4. **Isolation** - Isolates concrete classes from the client
5. **Easy to exchange product families** - Because the factory creates all objects from one family, it's easy to swap families

### Cons (Недостатки)


1. **Can lead to many classes** - Can lead to a large number of concrete classes if there are many families of objects
2. **Complexity** - Can be overly complex for simple systems
3. **Rigidity** - Supporting new kinds of products requires extending the factory interface, which involves changing the AbstractFactory class and all of its subclasses

## UML Diagram

```

  Client         

          uses
         

 AbstractFactory 
 + createProductA
 + createProductB

         
         
                           
   
ConcreteFactory1   ConcreteFactory2
   
                         
        creates           creates
                         
   
ProductA1        ProductA2     
   
```

## Best Practices

```kotlin
// - DO: Use when you need families of related objects
interface UIFactory {
    fun createButton(): Button
    fun createCheckbox(): Checkbox
    fun createTextfield(): TextField
}

// - DO: Make factories interchangeable
fun createUI(factory: UIFactory) {
    val button = factory.createButton()
    val checkbox = factory.createCheckbox()
    // UI components are guaranteed to be compatible
}

// - DON'T: Use for single product creation
// Use Factory Method instead

// - DON'T: Create factories with unrelated products
// Products should be from the same "family"
```

**English**: **Abstract Factory** is a creational design pattern that provides an interface for creating families of related objects without specifying their concrete classes. **Problem**: Direct object creation makes code inflexible and tightly coupled. **Solution**: Encapsulate object creation in separate factory objects. **Use when**: (1) System should be independent of object creation, (2) Multiple families of related objects need to be created together, (3) Need runtime dependency construction. **Pros**: ensures compatibility, promotes decoupling, enforces consistency. **Cons**: many classes for multiple families, complexity for simple systems. **Example**: UI themes (Light/Dark), database implementations (SQLite/Room).

## Links

- [Abstract Factory Pattern in Kotlin](https://www.baeldung.com/kotlin/abstract-factory-pattern)
- [Abstract factory pattern](https://en.wikipedia.org/wiki/Abstract_factory_pattern)
- [Abstract Factory Design Pattern in Kotlin](https://www.javaguides.net/2023/10/abstract-factory-design-pattern-in-kotlin.html)

## Further Reading

- [Abstract Factory Design Pattern](https://sourcemaking.com/design_patterns/abstract_factory)
- [Abstract Factory](https://refactoring.guru/design-patterns/abstract-factory)

---
*Source: Kirchhoff Android Interview Questions*


## Ответ (RU)

### Определение

Abstract Factory — это паттерн проектирования, целью которого является предоставление **единого интерфейса для создания семейств связанных объектов с одной темой**, но без раскрытия конкретной реализации.

### Проблемы, которые решает

Паттерн может использоваться для решения таких проблем как:

1. **Как сделать приложение независимым от способа создания его объектов?**
2. **Как сделать класс независимым от способа создания требуемых объектов?**
3. **Как создавать семейства связанных или зависимых объектов?**

### Почему это проблема?

Создание объектов напрямую внутри класса, которому эти объекты нужны, негибко:
- Это **привязывает класс к конкретным объектам**
- Делает невозможным изменение создания экземпляров позже без изменения класса
- Препятствует повторному использованию класса, если требуются другие объекты
- Затрудняет тестирование класса, так как реальные объекты нельзя заменить mock-объектами

### Решение

Паттерн описывает, как решить такие проблемы:

1. **Инкапсулировать создание объектов** в отдельном (фабричном) объекте путем определения и реализации интерфейса для создания объектов
2. **Делегировать создание объектов** фабричному объекту вместо создания объектов напрямую

Это делает класс **независимым от способа создания его объектов**. Класс может быть сконфигурирован фабричным объектом, который он использует для создания объектов, и фабричный объект может быть заменен во время выполнения.

### Когда использовать?

**Когда использовать паттерн Abstract Factory?**

- **Клиент независим** от того, как мы создаем и компонуем объекты в системе
- Система состоит из **нескольких семейств объектов**, и эти семейства спроектированы для совместного использования
- Нам нужно **значение времени выполнения для создания конкретной зависимости**

### Объяснение примера

**Объяснение**:

- `Button` и `Window` — это **интерфейсы абстрактных продуктов**, представляющие компоненты UI
- `LightButton`, `LightWindow`, `DarkButton` и `DarkWindow` — это **конкретные реализации** этих продуктов, адаптированные для конкретных тем
- `GUIFactory` — это **интерфейс Abstract Factory**, который объявляет методы для создания продуктов
- `LightThemeFactory` и `DarkThemeFactory` — это **конкретные фабрики**, которые создают компоненты UI для конкретных тем
- **Клиентский код** (функция `main`) использует абстрактную фабрику для создания компонентов UI, гарантируя их соответствие выбранной теме

### Pros (Преимущества)

1. **Обеспечивает совместимость** - Созданные объекты совместимы и принадлежат одному семейству
2. **Способствует слабой связанности** - Упрощает внедрение новых семейств объектов без изменения существующего кода
3. **Обеспечивает согласованность** - Обеспечивает согласованный интерфейс для создания объектов, улучшая поддерживаемость и читаемость
4. **Изоляция** - Изолирует конкретные классы от клиента
5. **Легко заменять семейства продуктов** - Поскольку фабрика создает все объекты из одного семейства, легко заменять семейства

### Cons (Недостатки)

1. **Может привести к множеству классов** - Может привести к большому количеству конкретных классов, если существует много семейств объектов
2. **Сложность** - Может быть излишне сложным для простых систем
3. **Жесткость** - Поддержка новых видов продуктов требует расширения интерфейса фабрики, что включает изменение класса AbstractFactory и всех его подклассов


---

## Related Questions

### Hub
- [[q-design-patterns-types--design-patterns--medium]] - Design pattern categories overview

### Creational Patterns
- [[q-factory-method-pattern--design-patterns--medium]] - Factory Method pattern
- [[q-builder-pattern--design-patterns--medium]] - Builder pattern
- [[q-prototype-pattern--design-patterns--medium]] - Prototype pattern

### Structural Patterns
- [[q-adapter-pattern--design-patterns--medium]] - Adapter pattern

### Behavioral Patterns
- [[q-strategy-pattern--design-patterns--medium]] - Strategy pattern

