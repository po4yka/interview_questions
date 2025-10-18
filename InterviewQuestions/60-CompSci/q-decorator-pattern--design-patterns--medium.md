---
id: 20251012-1227111125
title: "Decorator Pattern / Decorator Паттерн"
topic: computer-science
difficulty: medium
status: draft
moc: moc-compSci
related: [q-how-to-create-suspend-function--programming-languages--medium, q-coroutinescope-vs-supervisorscope--programming-languages--medium, q-iterator-order-guarantee--programming-languages--medium]
created: 2025-10-15
tags:
  - design-patterns
  - structural-patterns
  - decorator
  - gof-patterns
  - wrapper
---
# Decorator Pattern

# Question (EN)
> What is the Decorator pattern? When and why should it be used?

# Вопрос (RU)
> Что такое паттерн Decorator? Когда и зачем его использовать?

---

## Answer (EN)



### Definition


The Decorator Design Pattern is a structural design pattern that **allows behavior to be added to individual objects dynamically**, without affecting the behavior of other objects from the same class. It involves creating a set of decorator classes that are used to wrap concrete components.

### Problems it Solves


The decorator pattern provides a flexible alternative to subclassing for extending functionality. When using subclassing, different subclasses extend a class in different ways, but an extension is bound to the class at compile-time and can't be changed at run-time.

The decorator pattern allows responsibilities to be added (and removed from) an object dynamically at run-time by:

1. Implementing the interface of the extended (decorated) object (**`Component`**) transparently by forwarding all requests to it
2. Performing additional functionality before or after forwarding a request

### When to Use?


The Decorator Pattern works best when you need to add features to objects without changing their core structure. Use it for:

1. **Adding or removing behaviors at runtime**
2. **Enhancing legacy systems without touching their code**
3. **Avoiding an explosion of subclasses**

Don't use it if:

1. **Objects' core functionality changes often**
2. **You need to modify object internals**
3. **You already have many small, similar classes**

## Пример: Coffee Shop

```kotlin
// Main object interface
interface Coffee {
    fun cost(): Double
    fun description(): String
}

// Concrete component
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

class CaramelDecorator(coffee: Coffee) : CoffeeDecorator(coffee) {
    override fun cost() = super.cost() + 0.7
    override fun description() = super.description() + ", Caramel"
}

fun main() {
    val coffee: Coffee = SugarDecorator(MilkDecorator(BasicCoffee()))
    println("${coffee.description()} costs $${coffee.cost()}")

    val fancyCoffee: Coffee = CaramelDecorator(
        SugarDecorator(
            MilkDecorator(BasicCoffee())
        )
    )
    println("${fancyCoffee.description()} costs $${fancyCoffee.cost()}")
}
```

**Output**:
```
Basic Coffee, Milk, Sugar costs $2.7
Basic Coffee, Milk, Sugar, Caramel costs $3.4
```

## Android Example: Text Formatting

```kotlin
// Component interface
interface TextDisplay {
    fun display(): String
}

// Concrete component
class PlainText(private val text: String) : TextDisplay {
    override fun display() = text
}

// Abstract decorator
abstract class TextDecorator(
    protected val textDisplay: TextDisplay
) : TextDisplay

// Concrete decorators
class BoldDecorator(textDisplay: TextDisplay) : TextDecorator(textDisplay) {
    override fun display() = "<b>${textDisplay.display()}</b>"
}

class ItalicDecorator(textDisplay: TextDisplay) : TextDecorator(textDisplay) {
    override fun display() = "<i>${textDisplay.display()}</i>"
}

class ColorDecorator(
    textDisplay: TextDisplay,
    private val color: String
) : TextDecorator(textDisplay) {
    override fun display() = "<font color='$color'>${textDisplay.display()}</font>"
}

// Usage in Android
class TextFormatterActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val plainText = PlainText("Hello World")
        val boldText = BoldDecorator(plainText)
        val boldItalicText = ItalicDecorator(BoldDecorator(plainText))
        val coloredBoldItalic = ColorDecorator(
            ItalicDecorator(BoldDecorator(plainText)),
            "red"
        )

        textView.text = Html.fromHtml(
            coloredBoldItalic.display(),
            Html.FROM_HTML_MODE_LEGACY
        )
    }
}
```

## Kotlin Context Example: InputStream

```kotlin
// The Java I/O library uses decorator pattern extensively
fun readCompressedFile(filename: String): String {
    val fileInputStream = FileInputStream(filename)
    val bufferedStream = BufferedInputStream(fileInputStream)
    val gzipStream = GZIPInputStream(bufferedStream)
    val reader = InputStreamReader(gzipStream)

    return reader.readText()
}

// Kotlin delegation provides syntactic sugar for decoration
interface DataSource {
    fun readData(): String
    fun writeData(data: String)
}

class FileDataSource(private val filename: String) : DataSource {
    override fun readData() = File(filename).readText()
    override fun writeData(data: String) = File(filename).writeText(data)
}

// Decorator using delegation
class EncryptionDecorator(
    private val wrappee: DataSource,
    private val key: String
) : DataSource by wrappee {

    override fun readData(): String {
        val encrypted = wrappee.readData()
        return decrypt(encrypted, key)
    }

    override fun writeData(data: String) {
        val encrypted = encrypt(data, key)
        wrappee.writeData(encrypted)
    }

    private fun encrypt(data: String, key: String) = /* encryption */ data
    private fun decrypt(data: String, key: String) = /* decryption */ data
}

class CompressionDecorator(
    private val wrappee: DataSource
) : DataSource by wrappee {

    override fun readData() = decompress(wrappee.readData())
    override fun writeData(data: String) = wrappee.writeData(compress(data))

    private fun compress(data: String) = /* compression */ data
    private fun decompress(data: String) = /* decompression */ data
}
```

### Example Explanation


**Explanation**:

- **`Coffee`** is the main object interface, defining methods to get cost and description
- **`BasicCoffee`** is a concrete component that implements the Coffee interface
- **`CoffeeDecorator`** is an abstract decorator that implements Coffee and wraps another Coffee object
- **Concrete decorators** (`MilkDecorator`, `SugarDecorator`) add their respective features
- **Kotlin delegation** (`by` keyword) simplifies decorator implementation
- **Android**: Text formatting, input streams, caching layers use decorators

## Преимущества и недостатки

### Pros (Преимущества)


1. **Open-Closed Principle** - Can add functionality without modifying existing code
2. **Flexibility** - Add/remove responsibilities at runtime
3. **Reusable code** - Decorators are reusable components
4. **Composition over inheritance** - Avoids deep class hierarchies
5. **Single Responsibility** - Each decorator handles one specific feature
6. **Dynamic behavior** - Can apply or remove decorators at runtime

### Cons (Недостатки)


1. **Complexity** - Nesting decorators can make code hard to understand
2. **Many small classes** - Can lead to proliferation of classes
3. **Order matters** - Decorator order affects final behavior
4. **Debugging difficulty** - Stack traces become deeper
5. **Instantiation complexity** - Creating heavily decorated objects is verbose

## Best Practices

```kotlin
// - DO: Use for adding cross-cutting concerns
class LoggingDecorator(private val service: ApiService) : ApiService by service {
    override fun fetchData() {
        Log.d("API", "Fetching data...")
        val result = service.fetchData()
        Log.d("API", "Data fetched: $result")
        return result
    }
}

// - DO: Chain decorators for multiple behaviors
val decoratedService = CachingDecorator(
    LoggingDecorator(
        RealApiService()
    )
)

// - DO: Use Kotlin delegation for cleaner code
class RetryDecorator(
    private val service: NetworkService
) : NetworkService by service {
    override suspend fun request() = retry(3) { service.request() }
}

// - DO: Keep decorators focused on single responsibility
class MetricsDecorator(service: Service) : ServiceDecorator(service) {
    override fun execute() {
        val start = System.currentTimeMillis()
        super.execute()
        val duration = System.currentTimeMillis() - start
        MetricsLogger.log("Duration: $duration ms")
    }
}

// - DON'T: Use for fundamentally different behaviors
// - DON'T: Create overly complex decoration chains
// - DON'T: Modify core object state in decorators
```

**English**: **Decorator** is a structural design pattern that dynamically adds behaviors to objects by wrapping them in decorator objects. **Problem**: Need to add functionality without modifying existing classes or creating many subclasses. **Solution**: Wrap objects in decorators that add behavior while maintaining the same interface. **Use when**: (1) Need to add responsibilities at runtime, (2) Want to avoid subclass explosion, (3) Enhancing legacy code. **Kotlin**: Use delegation (`by` keyword) for cleaner decorators. **Pros**: runtime flexibility, composition over inheritance, Open-Closed Principle. **Cons**: many small classes, order matters, complexity. **Examples**: Java I/O streams, text formatting, caching layers, logging wrappers.

## Links

- [Decorator Design Pattern](https://www.geeksforgeeks.org/decorator-pattern/)
- [Decorator pattern](https://en.wikipedia.org/wiki/Decorator_pattern)
- [Decorator Pattern Explained: Basics to Advanced](https://daily.dev/blog/decorator-pattern-explained-basics-to-advanced)
- [Decorator Design Pattern in Kotlin](https://www.javaguides.net/2023/10/decorator-design-pattern-in-kotlin.html)

## Further Reading

- [Decorator Design Pattern](https://sourcemaking.com/design_patterns/decorator)
- [Decorator](https://refactoring.guru/design-patterns/decorator)
- [Decorator Pattern in Kotlin](https://swiderski.tech/kotlin-decorator-pattern/)

---
*Source: Kirchhoff Android Interview Questions*


## Ответ (RU)

### Определение

Паттерн проектирования Decorator — это структурный паттерн проектирования, который **позволяет динамически добавлять поведение отдельным объектам**, не влияя на поведение других объектов того же класса. Он включает создание набора классов-декораторов, которые используются для обёртывания конкретных компонентов.

### Проблемы, которые решает

Паттерн декоратор предоставляет гибкую альтернативу подклассам для расширения функциональности. При использовании подклассов разные подклассы расширяют класс разными способами, но расширение привязано к классу во время компиляции и не может быть изменено во время выполнения.

Паттерн декоратор позволяет динамически добавлять (и удалять) обязанности объекту во время выполнения следующим образом:

1. Прозрачная реализация интерфейса расширяемого (декорируемого) объекта (**`Component`**) путём перенаправления всех запросов к нему
2. Выполнение дополнительной функциональности до или после перенаправления запроса

### Когда использовать?

Паттерн Decorator работает лучше всего, когда нужно добавить возможности объектам без изменения их основной структуры. Используйте его для:

1. **Добавления или удаления поведений во время выполнения**
2. **Улучшения устаревших систем без изменения их кода**
3. **Избежания взрыва подклассов**

Не используйте его, если:

1. **Основная функциональность объектов часто меняется**
2. **Необходимо изменять внутреннее устройство объекта**
3. **У вас уже есть много мелких, похожих классов**

### Объяснение примера

**Объяснение**:

- **`Coffee`** — это основной интерфейс объекта, определяющий методы для получения стоимости и описания
- **`BasicCoffee`** — это конкретный компонент, который реализует интерфейс Coffee
- **`CoffeeDecorator`** — это абстрактный декоратор, который реализует Coffee и оборачивает другой объект Coffee
- **Конкретные декораторы** (`MilkDecorator`, `SugarDecorator`) добавляют свои соответствующие возможности
- **Делегирование Kotlin** (ключевое слово `by`) упрощает реализацию декоратора
- **Android**: форматирование текста, потоки ввода, кэширующие слои используют декораторы

### Pros (Преимущества)

1. **Принцип открытости/закрытости** — можно добавлять функциональность без изменения существующего кода
2. **Гибкость** — добавлять/удалять обязанности во время выполнения
3. **Переиспользуемый код** — декораторы являются переиспользуемыми компонентами
4. **Композиция вместо наследования** — избегает глубоких иерархий классов
5. **Единственная ответственность** — каждый декоратор обрабатывает одну конкретную возможность
6. **Динамическое поведение** — можно применять или удалять декораторы во время выполнения

### Cons (Недостатки)

1. **Сложность** — вложенность декораторов может затруднить понимание кода
2. **Много маленьких классов** — может привести к разрастанию классов
3. **Порядок важен** — порядок декораторов влияет на конечное поведение
4. **Сложность отладки** — трассировки стека становятся глубже
5. **Сложность создания экземпляров** — создание сильно декорированных объектов многословно


---

## Related Questions

### Hub
- [[q-design-patterns-types--design-patterns--medium]] - Design pattern categories overview

### Structural Patterns
- [[q-adapter-pattern--design-patterns--medium]] - Adapter pattern
- [[q-facade-pattern--design-patterns--medium]] - Facade pattern
- [[q-proxy-pattern--design-patterns--medium]] - Proxy pattern
- [[q-composite-pattern--design-patterns--medium]] - Composite pattern

### Creational Patterns
- [[q-factory-method-pattern--design-patterns--medium]] - Factory Method pattern

### Behavioral Patterns
- [[q-strategy-pattern--design-patterns--medium]] - Strategy pattern

