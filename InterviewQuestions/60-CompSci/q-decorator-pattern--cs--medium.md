---
id: cs-013
title: "Decorator Pattern / Паттерн Декоратор"
aliases: ["Decorator Pattern", "Паттерн Декоратор"]
topic: cs
subtopics: [design-patterns, kotlin, structural-patterns]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-architecture-patterns, c-kotlin-features]
created: 2025-10-15
updated: 2025-11-11
tags: [decorator, design-patterns, difficulty/medium, gof-patterns, kotlin, structural-patterns, wrapper]
sources: ["https://refactoring.guru/design-patterns/decorator"]
---

# Вопрос (RU)
> Что такое паттерн Decorator? Когда и зачем его использовать?

# Question (EN)
> What is the Decorator pattern? When and why should it be used?

---

## Ответ (RU)

**Теория Decorator Pattern:**
Decorator — структурный паттерн проектирования, позволяющий динамически добавлять поведение объектам через wrapping (обёртывание). Декораторы сохраняют тот же интерфейс, что и оборачиваемый (wrapped) объект. Основная проблема: нужно добавить функциональность без взрыва количества подклассов. Решение: оборачивать объекты в декораторы, добавляющие поведение. Используется для: добавления обязанностей (responsibilities) в runtime, избежания subclass explosion, расширения (enhancement) legacy-кода без изменения исходных классов.

**Определение:**

*Теория:* Паттерн Decorator позволяет добавлять поведение к отдельным объектам динамически, не влияя на поведение других объектов того же класса. Конкретный компонент оборачивается в классы-декораторы. Это альтернатива наследованию для расширения функциональности. Поддерживает принцип открытости/закрытости (Open-Closed Principle): открыт для расширения, закрыт для изменения.

**Когда использовать:**

*Теория:* Используйте Decorator, когда нужно добавлять или удалять responsibilities в runtime. Вместо создания множества подклассов для каждой комбинации features (class explosion), создавайте декораторы и комбинируйте их динамически. Применяется для cross-cutting concerns (логирование, кэширование, шифрование), расширения legacy-кода, обёрток вокруг `InputStream`/`OutputStream`.

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

**Android / I/O Streams Example - Text Formatting:**

*Теория:* Паттерн Decorator широко используется в Java/Kotlin I/O streams (`BufferedInputStream`, `GZIPInputStream`, `InputStreamReader`). Он позволяет комбинировать разные поведения потоков динамически. В Android и backend-коде подобный подход может применяться, например, для форматирования текста, слоёв кэширования, обёрток для шифрования/сжатия.

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
    override fun display() = "<font color='${color}'>${textDisplay.display()}</font>"
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

*Теория:* Ключевое слово Kotlin `by` упрощает реализацию паттерна Decorator через делегирование. Вызовы по умолчанию делегируются оборачиваемому объекту. Переопределяйте только методы, которые нужно изменить. Это уменьшает boilerplate-код.

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

// Decorator с delegation (encrypt/decrypt реализуются отдельно)
class EncryptionDecorator(
    private val wrappee: DataSource,
    private val key: String
) : DataSource by wrappee {  // ✅ Автоматическое delegation

    override fun readData(): String {
        val encrypted = wrappee.readData()
        return decrypt(encrypted, key) // псевдокод
    }

    override fun writeData(data: String) {
        val encrypted = encrypt(data, key) // псевдокод
        wrappee.writeData(encrypted)
    }
}

class CompressionDecorator(private val wrappee: DataSource) : DataSource by wrappee {
    override fun readData() = decompress(wrappee.readData()) // псевдокод
    override fun writeData(data: String) = wrappee.writeData(compress(data)) // псевдокод
}
```

**Проблемы, решаемые Decorator:**

*Теория:* Основная проблема — subclass explosion. Если нужно добавить N независимых фич к объекту, создание подклассов для каждой комбинации даёт до 2^N подклассов. Decorator позволяет комбинировать фичи динамически в runtime. Также помогает избавиться от жёстких иерархий, жёсткого compile-time связывания и статической композиции.

**Преимущества:**

1. **Open-Closed Principle** — добавление функциональности без изменения существующего кода компонентов
2. **Runtime Flexibility** — можно добавлять/удалять декораторы в runtime (где это позволяет дизайн)
3. **Composition over Inheritance** — избегает глубоких иерархий наследования
4. **Single Responsibility** — каждый декоратор добавляет одну чёткую фичу
5. **Reusable Decorators** — можно комбинировать в разном порядке для разных сценариев

**Недостатки:**

1. **Сложность структуры** — вложенные декораторы трудно отслеживать
2. **Много мелких классов** — увеличивается количество классов
3. **Порядок важен** — порядок декораторов влияет на поведение
4. **Debugging сложнее** — глубокие цепочки обёрток усложняют отладку
5. **Verbose instantiation** — создание цепочек декораторов может выглядеть громоздко

**Когда использовать:**

✅ Добавление responsibilities в runtime
✅ Избежание subclass explosion
✅ Расширение legacy-кода без модификации исходных классов
✅ Реализация cross-cutting concerns (логирование, кэширование и т.п.)

❌ Когда core-функциональность часто радикально меняется (лучше пересмотреть дизайн, а не наращивать декораторы)
❌ Когда сложные состояния и инварианты делают цепочки декораторов трудными для понимания и сопровождения
❌ Когда уже есть перегруженная иерархия множества мелких похожих классов — декораторы могут усложнить её ещё больше

**Ключевые концепции:**

1. **Wrapping** — декоратор оборачивает компонент
2. **Same Interface** — декоратор и компонент реализуют один и тот же интерфейс (или общий абстрактный тип)
3. **Dynamic Composition** — комбинации формируются в runtime
4. **Transparent Behavior** — запросы делегируются базовому компоненту, добавляя/изменяя поведение по пути
5. **Chain of Decorators** — можно составлять цепочки из нескольких декораторов

---

## Answer (EN)

**Decorator Pattern Theory:**
The Decorator is a structural design pattern that allows adding behavior to objects dynamically via wrapping. Decorators keep the same interface as the wrapped object. The core problem: you need to add functionality without causing a subclass explosion. The solution: wrap objects in decorators that add behavior. It is used for adding responsibilities at runtime, avoiding subclass explosion, and enhancing legacy code without modifying existing classes.

**Definition:**

*Theory:* The Decorator pattern allows adding behavior to individual objects dynamically without affecting other objects of the same class. A concrete component is wrapped in decorator classes. It is an alternative to subclassing for extending functionality. It supports the Open-Closed Principle: open for extension, closed for modification.

**When to Use:**

*Theory:* Use Decorator when you need to add or remove responsibilities at runtime. Instead of creating many subclasses for every feature combination (class explosion), create decorators and compose them dynamically. Common uses: cross-cutting concerns (logging, caching, encryption), enhancing legacy code, and wrappers around `InputStream`/`OutputStream`.

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

**Android / I/O Streams Example - Text Formatting:**

*Theory:* The Decorator pattern is widely used in Java/Kotlin I/O streams (`BufferedInputStream`, `GZIPInputStream`, `InputStreamReader`). It allows combining different stream behaviors dynamically. In Android and general application code, a similar approach can be used for text formatting, caching layers, and encryption/compression wrappers.

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
    override fun display() = "<font color='${color}'>${textDisplay.display()}</font>"
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

*Theory:* The Kotlin `by` keyword simplifies implementing the Decorator pattern using delegation. Calls are automatically delegated to the wrapped object. You override only the methods you want to change, which reduces boilerplate.

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

// Decorator with delegation (encrypt/decrypt implemented elsewhere)
class EncryptionDecorator(
    private val wrappee: DataSource,
    private val key: String
) : DataSource by wrappee {  // ✅ Automatic delegation

    override fun readData(): String {
        val encrypted = wrappee.readData()
        return decrypt(encrypted, key) // pseudo-code
    }

    override fun writeData(data: String) {
        val encrypted = encrypt(data, key) // pseudo-code
        wrappee.writeData(encrypted)
    }
}

class CompressionDecorator(private val wrappee: DataSource) : DataSource by wrappee {
    override fun readData() = decompress(wrappee.readData()) // pseudo-code
    override fun writeData(data: String) = wrappee.writeData(compress(data)) // pseudo-code
}
```

**Problems Solved by Decorator:**

*Theory:* The main problem is subclass explosion. If you need to add N independent features to an object, creating subclasses for each combination can lead to up to 2^N subclasses. The Decorator allows combining features dynamically at runtime. It also helps avoid rigid class hierarchies, compile-time-only binding, and purely static composition.

**Advantages:**

1. **Open-Closed Principle** — adds functionality without modifying existing component code
2. **Runtime Flexibility** — can add/remove decorators at runtime (when the design allows it)
3. **Composition over Inheritance** — avoids deep inheritance hierarchies
4. **Single Responsibility** — each decorator adds one clearly defined feature
5. **Reusable Decorators** — can be combined in different orders for different use cases

**Disadvantages:**

1. **Structural Complexity** — nested decorators can be hard to follow
2. **Many Small Classes** — increases the number of classes
3. **Order Matters** — decorator order can affect behavior
4. **Harder Debugging** — deep wrapping chains make debugging more difficult
5. **Verbose Instantiation** — constructing decorator chains can be verbose

**When to Use:**

✅ Adding responsibilities at runtime
✅ Avoiding subclass explosion
✅ Enhancing legacy code without modifying original classes
✅ Implementing cross-cutting concerns (logging, caching, etc.)

❌ When core functionality is frequently and fundamentally changing (better to revisit the design instead of stacking decorators)
❌ When complex shared state and invariants make decorator chains hard to reason about and maintain
❌ When you already have an overloaded hierarchy of many similar small classes — decorators may complicate it further

**Key Concepts:**

1. **Wrapping** — decorator wraps the component
2. **Same Interface** — decorator and component share the same interface (or abstract type)
3. **Dynamic Composition** — combinations are formed at runtime
4. **Transparent Behavior** — requests are forwarded to the component, adding/modifying behavior along the way
5. **Chain of Decorators** — multiple decorators can be combined into a chain

---

## Дополнительные вопросы (RU)

- Как паттерн Decorator соотносится с паттерном Adapter?
- Можно ли удалять декораторы в runtime?
- В чем разница между Decorator и Proxy?

## Follow-ups

- How does Decorator pattern relate to Adapter pattern?
- Can you remove decorators at runtime?
- What's the difference between Decorator and Proxy pattern?

## Связанные вопросы (RU)

### Предпосылки (проще)
- Базовые знания объектно-ориентированного программирования
- Понимание интерфейсов

### Связанные (тот же уровень)
- [[q-adapter-pattern--cs--medium]] — паттерн Adapter

### Продвинутые (сложнее)
- Комбинирование нескольких паттернов проектирования
- Продвинутые реализации Decorator
- Влияние паттерна Decorator на производительность

## Related Questions

### Prerequisites (Easier)
- Basic object-oriented programming
- Interface concepts

### Related (Same Level)
- [[q-adapter-pattern--cs--medium]] - Adapter pattern

### Advanced (Harder)
- Combining multiple design patterns
- Advanced Decorator implementations
- Performance implications of Decorator

## Ссылки (RU)

- [[c-architecture-patterns]]
- [[c-kotlin-features]]

## References

- [[c-architecture-patterns]]
- [[c-kotlin-features]]
