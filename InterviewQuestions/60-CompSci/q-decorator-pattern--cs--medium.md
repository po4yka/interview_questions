---
id: cs-013
title: "Decorator Pattern / Паттерн Декоратор"
aliases: ["Decorator Pattern", "Паттерн Декоратор"]
topic: cs
subtopics: [design-patterns, kotlin, programming-languages, structural-patterns]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [q-composite-pattern--design-patterns--medium, q-facade-pattern--design-patterns--medium, q-proxy-pattern--design-patterns--medium]
created: 2025-10-15
updated: 2025-01-25
tags: [decorator, design-patterns, difficulty/medium, gof-patterns, kotlin, structural-patterns, wrapper]
sources: [https://refactoring.guru/design-patterns/decorator]
date created: Monday, October 6th 2025, 7:20:34 am
date modified: Sunday, October 26th 2025, 11:50:32 am
---

# Вопрос (RU)
> Что такое паттерн Decorator? Когда и зачем его использовать?

# Question (EN)
> What is the Decorator pattern? When and why should it be used?

---

## Ответ (RU)

**Теория Decorator Pattern:**
Decorator - структурный паттерн проектирования, позволяющий динамически добавлять поведение объектам через wrapping. Сохраняет тот же интерфейс, что и wrapped объект. Проблема: нужно добавить функциональность без subclass explosion. Решение: wrap объекты в decorators, добавляющие поведение. Используется для: добавления responsibilities в runtime, избежания subclass explosion, enhancement legacy code.

**Определение:**

*Теория:* Decorator pattern позволяет добавлять behavior к индивидуальным объектам динамически, не влияя на поведение других объектов того же класса. Wraps concrete component в decorator classes. Альтернатива subclassing для расширения функциональности. Поддерживает Open-Closed Principle - открыт для extension, закрыт для modification.

**Когда использовать:**

*Теория:* Используйте Decorator когда нужно добавлять или удалять responsibilities в runtime. Вместо создания множества подклассов для каждого комбинации features (class explosion), создаёте decorators и комбинируете их динамически. Используется для cross-cutting concerns (logging, caching, encryption), legacy code enhancement, InputStream/OutputStream wrappers.

```kotlin
// ✅ Coffee Shop Example
interface Coffee {
    fun cost(): Double
    fun description(): String
}

class BasicCoffee : Coffee {
    override fun cost() = 2.0
    override fun description() = "Basic Coffee"
}

// Abstract decorator
abstract class CoffeeDecorator(private val coffee: Coffee) : Coffee {
    override fun cost() = coffee.cost()
    override fun description() = coffee.description()
}

// Concrete decorators
class MilkDecorator(coffee: Coffee) : CoffeeDecorator(coffee) {
    override fun cost() = super.cost() + 0.5
    override fun description() = super.description() + ", Milk"
}

class SugarDecorator(coffee: Coffee) : CoffeeDecorator(coffee) {
    override fun cost() = super.cost() + 0.2
    override fun description() = super.description() + ", Sugar"
}

// Usage
val coffee = SugarDecorator(MilkDecorator(BasicCoffee()))
println("${coffee.description()} costs $${coffee.cost()}")
// Output: Basic Coffee, Milk, Sugar costs $2.7
```

**Android Example - Text Formatting:**

*Теория:* Decorator pattern широко используется в Java/Kotlin I/O streams (BufferedInputStream, GZIPInputStream, InputStreamReader). Позволяет комбинировать разные stream behaviors динамически. В Android используется для text formatting, caching layers, encryption/compression wrappers.

```kotlin
// ✅ Text Display Decorator
interface TextDisplay {
    fun display(): String
}

class PlainText(private val text: String) : TextDisplay {
    override fun display() = text
}

abstract class TextDecorator(protected val textDisplay: TextDisplay) : TextDisplay

class BoldDecorator(textDisplay: TextDisplay) : TextDecorator(textDisplay) {
    override fun display() = "<b>${textDisplay.display()}</b>"
}

class ItalicDecorator(textDisplay: TextDisplay) : TextDecorator(textDisplay) {
    override fun display() = "<i>${textDisplay.display()}</i>"
}

class ColorDecorator(textDisplay: TextDisplay, private val color: String) : TextDecorator(textDisplay) {
    override fun display() = "<font color='$color'>${textDisplay.display()}</font>"
}

// Usage
val coloredBoldItalic = ColorDecorator(
    ItalicDecorator(BoldDecorator(PlainText("Hello"))),
    "red"
)
println(coloredBoldItalic.display())
// Output: <font color='red'><i><b>Hello</b></i></font>
```

**Kotlin Delegation для Decorator:**

*Теория:* Kotlin `by` keyword упрощает реализацию decorator pattern через delegation. Автоматически делегирует вызовы к wrapped объекту. Переопределяйте только методы, которые нужно modify. Уменьшает boilerplate code для стандартных методов.

```kotlin
// ✅ Kotlin Delegation
interface DataSource {
    fun readData(): String
    fun writeData(data: String)
}

class FileDataSource(private val filename: String) : DataSource {
    override fun readData() = File(filename).readText()
    override fun writeData(data: String) = File(filename).writeText(data)
}

// Decorator с delegation
class EncryptionDecorator(
    private val wrappee: DataSource,
    private val key: String
) : DataSource by wrappee {  // ✅ Автоматическое delegation

    override fun readData(): String {
        val encrypted = wrappee.readData()
        return decrypt(encrypted, key)
    }

    override fun writeData(data: String) {
        val encrypted = encrypt(data, key)
        wrappee.writeData(encrypted)
    }
}

class CompressionDecorator(private val wrappee: DataSource) : DataSource by wrappee {
    override fun readData() = decompress(wrappee.readData())
    override fun writeData(data: String) = wrappee.writeData(compress(data))
}
```

**Проблемы, решаемые Decorator:**

*Теория:* Основная проблема - subclass explosion. Если нужно добавлять N features к объекту, создание подклассов для каждой комбинации даёт 2^N подклассов. Decorator позволяет комбинировать features динамически в runtime. Решает проблемы: rigid class hierarchies, compile-time binding, static composition.

**Преимущества:**

1. **Open-Closed Principle** - добавляет функциональность без изменения кода
2. **Runtime Flexibility** - можно добавлять/удалять decorators в runtime
3. **Composition over Inheritance** - избегает глубоких иерархий
4. **Single Responsibility** - каждый decorator добавляет одну фичу
5. **Reusable Decorators** - можно комбинировать в любом порядке

**Недостатки:**

1. **Комплексность** - вложенные decorators трудно понять
2. **Маленькие классы** - много маленьких decorator классов
3. **Порядок важен** - порядок decorators влияет на поведение
4. **Debugging сложнее** - deep stack traces
5. **Verbose instantiation** - создание decorated объекта громоздкое

**Когда использовать:**

✅ Добавление responsibilities в runtime
✅ Избежание subclass explosion
✅ Enhancement legacy code без модификации
✅ Cross-cutting concerns (logging, caching)

❌ Когда core functionality часто меняется
❌ Когда нужно изменять internal state
❌ Когда уже есть много похожих маленьких классов

**Ключевые концепции:**

1. **Wrapping** - decorator wraps component
2. **Same Interface** - decorator и component - тот же интерфейс
3. **Dynamic Composition** - комбинации в runtime
4. **Transparent Behavior** - forwarding requests к component
5. **Chain of Decorators** - можно комбинировать decorators

## Answer (EN)

**Decorator Pattern Theory:**
Decorator - structural design pattern allowing dynamic behavior addition to objects through wrapping. Maintains same interface as wrapped object. Problem: need to add functionality without subclass explosion. Solution: wrap objects in decorators adding behavior. Used for: adding responsibilities at runtime, avoiding subclass explosion, enhancing legacy code.

**Definition:**

*Theory:* Decorator pattern allows adding behavior to individual objects dynamically, without affecting other objects from same class. Wraps concrete component in decorator classes. Alternative to subclassing for extending functionality. Supports Open-Closed Principle - open for extension, closed for modification.

**When to Use:**

*Theory:* Use Decorator when need to add or remove responsibilities at runtime. Instead of creating many subclasses for each combination of features (class explosion), create decorators and combine them dynamically. Used for cross-cutting concerns (logging, caching, encryption), legacy code enhancement, InputStream/OutputStream wrappers.

```kotlin
// ✅ Coffee Shop Example
interface Coffee {
    fun cost(): Double
    fun description(): String
}

class BasicCoffee : Coffee {
    override fun cost() = 2.0
    override fun description() = "Basic Coffee"
}

// Abstract decorator
abstract class CoffeeDecorator(private val coffee: Coffee) : Coffee {
    override fun cost() = coffee.cost()
    override fun description() = coffee.description()
}

// Concrete decorators
class MilkDecorator(coffee: Coffee) : CoffeeDecorator(coffee) {
    override fun cost() = super.cost() + 0.5
    override fun description() = super.description() + ", Milk"
}

class SugarDecorator(coffee: Coffee) : CoffeeDecorator(coffee) {
    override fun cost() = super.cost() + 0.2
    override fun description() = super.description() + ", Sugar"
}

// Usage
val coffee = SugarDecorator(MilkDecorator(BasicCoffee()))
println("${coffee.description()} costs $${coffee.cost()}")
// Output: Basic Coffee, Milk, Sugar costs $2.7
```

**Android Example - Text Formatting:**

*Theory:* Decorator pattern widely used in Java/Kotlin I/O streams (BufferedInputStream, GZIPInputStream, InputStreamReader). Allows combining different stream behaviors dynamically. In Android used for text formatting, caching layers, encryption/compression wrappers.

```kotlin
// ✅ Text Display Decorator
interface TextDisplay {
    fun display(): String
}

class PlainText(private val text: String) : TextDisplay {
    override fun display() = text
}

abstract class TextDecorator(protected val textDisplay: TextDisplay) : TextDisplay

class BoldDecorator(textDisplay: TextDisplay) : TextDecorator(textDisplay) {
    override fun display() = "<b>${textDisplay.display()}</b>"
}

class ItalicDecorator(textDisplay: TextDisplay) : TextDecorator(textDisplay) {
    override fun display() = "<i>${textDisplay.display()}</i>"
}

class ColorDecorator(textDisplay: TextDisplay, private val color: String) : TextDecorator(textDisplay) {
    override fun display() = "<font color='$color'>${textDisplay.display()}</font>"
}

// Usage
val coloredBoldItalic = ColorDecorator(
    ItalicDecorator(BoldDecorator(PlainText("Hello"))),
    "red"
)
println(coloredBoldItalic.display())
// Output: <font color='red'><i><b>Hello</b></i></font>
```

**Kotlin Delegation for Decorator:**

*Theory:* Kotlin `by` keyword simplifies decorator pattern implementation through delegation. Automatically delegates calls to wrapped object. Override only methods that need modification. Reduces boilerplate for standard methods.

```kotlin
// ✅ Kotlin Delegation
interface DataSource {
    fun readData(): String
    fun writeData(data: String)
}

class FileDataSource(private val filename: String) : DataSource {
    override fun readData() = File(filename).readText()
    override fun writeData(data: String) = File(filename).writeText(data)
}

// Decorator with delegation
class EncryptionDecorator(
    private val wrappee: DataSource,
    private val key: String
) : DataSource by wrappee {  // ✅ Automatic delegation

    override fun readData(): String {
        val encrypted = wrappee.readData()
        return decrypt(encrypted, key)
    }

    override fun writeData(data: String) {
        val encrypted = encrypt(data, key)
        wrappee.writeData(encrypted)
    }
}

class CompressionDecorator(private val wrappee: DataSource) : DataSource by wrappee {
    override fun readData() = decompress(wrappee.readData())
    override fun writeData(data: String) = wrappee.writeData(compress(data))
}
```

**Problems Solved by Decorator:**

*Theory:* Main problem - subclass explosion. If need to add N features to object, creating subclasses for each combination gives 2^N subclasses. Decorator allows combining features dynamically at runtime. Solves problems: rigid class hierarchies, compile-time binding, static composition.

**Advantages:**

1. **Open-Closed Principle** - adds functionality without modifying code
2. **Runtime Flexibility** - can add/remove decorators at runtime
3. **Composition over Inheritance** - avoids deep hierarchies
4. **Single Responsibility** - each decorator adds one feature
5. **Reusable Decorators** - can combine in any order

**Disadvantages:**

1. **Complexity** - nested decorators hard to understand
2. **Small Classes** - many small decorator classes
3. **Order Matters** - decorator order affects behavior
4. **Debugging Harder** - deep stack traces
5. **Verbose Instantiation** - creating decorated object is verbose

**When to Use:**

✅ Adding responsibilities at runtime
✅ Avoiding subclass explosion
✅ Enhancing legacy code without modification
✅ Cross-cutting concerns (logging, caching)

❌ When core functionality changes frequently
❌ When need to modify internal state
❌ When already have many similar small classes

**Key Concepts:**

1. **Wrapping** - decorator wraps component
2. **Same Interface** - decorator and component have same interface
3. **Dynamic Composition** - combinations at runtime
4. **Transparent Behavior** - forwarding requests to component
5. **Chain of Decorators** - can combine decorators

---

## Follow-ups

- How does Decorator pattern relate to Adapter pattern?
- Can you remove decorators at runtime?
- What's the difference between Decorator and Proxy pattern?

## Related Questions

### Prerequisites (Easier)
- Basic object-oriented programming
- Interface concepts

### Related (Same Level)
- [[q-facade-pattern--design-patterns--medium]] - Facade pattern
- [[q-proxy-pattern--design-patterns--medium]] - Proxy pattern
- [[q-composite-pattern--design-patterns--medium]] - Composite pattern

### Advanced (Harder)
- Combining multiple design patterns
- Advanced Decorator implementations
- Performance implications of Decorator
