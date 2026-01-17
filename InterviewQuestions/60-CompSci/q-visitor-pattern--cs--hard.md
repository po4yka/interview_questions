---id: dp-001
title: "Visitor Pattern / Visitor Паттерн"
aliases: [Visitor Pattern, Visitor Паттерн]
topic: cs
subtopics: [double-dispatch, polymorphism]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-architecture-patterns, c-computer-science, c-dao-pattern]
created: 2025-10-15
updated: 2025-11-11
tags: [behavioral-patterns, design-patterns, difficulty/hard, double-dispatch, gof-patterns, visitor]

anki_cards:
- slug: dp-001-0-en
  front: |
    What is the Visitor pattern and what problem does it solve?
  back: |
    **Visitor**: Behavioral pattern adding operations to class hierarchy without modifying it.
    
    **How**: Double dispatch - element.accept(visitor) calls visitor.visit(element).
    
    **Use when**: Stable element hierarchy, varying operations.
    
    **Trade-off**: Easy to add operations, hard to add new element types.
  language: en
  difficulty: 0.5
  tags: [cs_patterns, difficulty::hard]
- slug: dp-001-0-ru
  front: |
    Что такое паттерн Посетитель и какую проблему он решает?
  back: |
    **Посетитель**: Поведенческий паттерн для добавления операций к иерархии без её изменения.
    
    **Как работает**: Двойная диспетчеризация - element.accept(visitor) вызывает visitor.visit(element).
    
    **Используйте когда**: Стабильная иерархия элементов, меняющиеся операции.
    
    **Компромисс**: Легко добавить операции, сложно добавить новые типы элементов.
  language: ru
  difficulty: 0.5
  tags: [cs_patterns, difficulty::hard]

---
# Вопрос (RU)
> Что такое паттерн Visitor? Когда и зачем его следует использовать?

# Question (EN)
> What is the Visitor pattern? When and why should it be used?

---

## Ответ (RU)

**Visitor (Посетитель)** — это поведенческий паттерн проектирования, который позволяет добавлять новые операции к группе связанных классов без изменения их структуры. Он особенно полезен, когда у вас есть стабильный набор классов, но нужно выполнять различные операции над ними.

### Определение

Паттерн проектирования Visitor (Посетитель) — это поведенческий паттерн, который **позволяет добавлять новые операции к группе связанных классов без изменения их структуры**, используя двойную диспетчеризацию. Он особенно полезен, когда у вас есть относительно стабильный набор классов-элементов, но необходимо выполнять над ними различные операции, и вы хотите расширять функциональность, добавляя новых посетителей (операции), не изменяя иерархию элементов.

### Проблемы, Которые Решает

Какие проблемы может решить паттерн проектирования Visitor?

- **Нужно иметь возможность определять новые операции для (некоторых) классов структуры объектов без изменения самих классов.**
- Требуется применять множество различных и часто слабо связанных операций к общей структуре объектов, не захламляя классы элементов этой логикой.

### Решение

Какое решение описывает паттерн проектирования Visitor?

1. **Определяется отдельный объект (посетитель)**, который реализует операции над элементами структуры объектов.
2. **Клиенты обходят структуру объектов** и вызывают на каждом элементе метод `accept(visitor)`.
3. **Объект-посетитель выполняет операцию** над элементом через перегруженные методы `visit(ElementType)` (двойная диспетчеризация).

Это позволяет создавать новые операции независимо от классов структуры объектов, добавляя новые классы-посетители.

### Мотивация Использования

1. **Разделение ответственности** — алгоритмы отделены от структуры объектов.
2. **Расширяемость по операциям** — новые операции добавляются созданием новых посетителей без изменения элементов.
3. **Улучшенная поддерживаемость** — связанное поведение централизовано в посетителях.
4. **Гибкость** — разные посетители реализуют разные поведения над одной и той же структурой.
5. **Ослабление связности** — операции меньше зависят от конкретной реализации элементов.
6. **Наилучший сценарий** — иерархия элементов относительно стабильна, а набор операций над ними меняется и растёт.

### Пример: Калькулятор Площади Фигур (Shape Area Calculator)

```kotlin
// Шаг 1: Интерфейс элемента и конкретные элементы
interface Shape {
    fun accept(visitor: ShapeVisitor)
}

class Circle(val radius: Double) : Shape {
    override fun accept(visitor: ShapeVisitor) {
        visitor.visit(this)
    }
}

class Square(val side: Double) : Shape {
    override fun accept(visitor: ShapeVisitor) {
        visitor.visit(this)
    }
}

class Triangle(val base: Double, val height: Double) : Shape {
    override fun accept(visitor: ShapeVisitor) {
        visitor.visit(this)
    }
}

// Шаг 2: Интерфейс посетителя и конкретные посетители
interface ShapeVisitor {
    fun visit(circle: Circle)
    fun visit(square: Square)
    fun visit(triangle: Triangle)
}

class AreaVisitor : ShapeVisitor {
    private var totalArea = 0.0

    override fun visit(circle: Circle) {
        val area = Math.PI * circle.radius * circle.radius
        println("Area of Circle: $area")
        totalArea += area
    }

    override fun visit(square: Square) {
        val area = square.side * square.side
        println("Area of Square: $area")
        totalArea += area
    }

    override fun visit(triangle: Triangle) {
        val area = 0.5 * triangle.base * triangle.height
        println("Area of Triangle: $area")
        totalArea += area
    }

    fun getTotalArea() = totalArea
}

class PerimeterVisitor : ShapeVisitor {
    override fun visit(circle: Circle) {
        val perimeter = 2 * Math.PI * circle.radius
        println("Perimeter of Circle: $perimeter")
    }

    override fun visit(square: Square) {
        val perimeter = 4 * square.side
        println("Perimeter of Square: $perimeter")
    }

    override fun visit(triangle: Triangle) {
        println("Perimeter of Triangle: (cannot calculate without all sides)")
    }
}

// Клиентский код
fun main() {
    val shapes: List<Shape> = listOf(
        Circle(5.0),
        Square(4.0),
        Triangle(3.0, 6.0)
    )

    val areaVisitor = AreaVisitor()
    val perimeterVisitor = PerimeterVisitor()

    println("Calculating areas:")
    shapes.forEach { it.accept(areaVisitor) }
    println("Total area: ${areaVisitor.getTotalArea()}")

    println("\nCalculating perimeters:")
    shapes.forEach { it.accept(perimeterVisitor) }
}
```

### Android Пример: Иерархия `View`

```kotlin
// Интерфейс элемента
interface ViewElement {
    fun accept(visitor: ViewVisitor)
}

// Конкретные элементы
class ButtonElement(val text: String, val enabled: Boolean) : ViewElement {
    override fun accept(visitor: ViewVisitor) = visitor.visitButton(this)
}

class TextViewElement(val text: String, val textSize: Float) : ViewElement {
    override fun accept(visitor: ViewVisitor) = visitor.visitTextView(this)
}

class ImageViewElement(val imageUrl: String, val width: Int, val height: Int) : ViewElement {
    override fun accept(visitor: ViewVisitor) = visitor.visitImageView(this)
}

// Интерфейс посетителя
interface ViewVisitor {
    fun visitButton(button: ButtonElement)
    fun visitTextView(textView: TextViewElement)
    fun visitImageView(imageView: ImageViewElement)
}

// Конкретные посетители
class ValidationVisitor : ViewVisitor {
    private val errors = mutableListOf<String>()

    override fun visitButton(button: ButtonElement) {
        if (button.text.isBlank()) {
            errors.add("Button has empty text")
        }
    }

    override fun visitTextView(textView: TextViewElement) {
        if (textView.textSize < 12f) {
            errors.add("TextView text size is too small: ${textView.textSize}")
        }
    }

    override fun visitImageView(imageView: ImageViewElement) {
        if (imageView.width > 1000 || imageView.height > 1000) {
            errors.add("ImageView dimensions are too large: ${imageView.width}x${imageView.height}")
        }
    }

    fun getErrors() = errors
}

class RenderVisitor : ViewVisitor {
    private val renderCommands = mutableListOf<String>()

    override fun visitButton(button: ButtonElement) {
        renderCommands.add("Render button: '${button.text}' (enabled: ${button.enabled})")
    }

    override fun visitTextView(textView: TextViewElement) {
        renderCommands.add("Render text: '${textView.text}' (size: ${textView.textSize})")
    }

    override fun visitImageView(imageView: ImageViewElement) {
        renderCommands.add("Render image: ${imageView.imageUrl} (${imageView.width}x${imageView.height})")
    }

    fun getRenderCommands() = renderCommands
}

// Использование
fun main() {
    val views = listOf(
        ButtonElement("Submit", true),
        TextViewElement("Welcome", 14f),
        ImageViewElement("banner.jpg", 800, 600)
    )

    val validationVisitor = ValidationVisitor()
    views.forEach { it.accept(validationVisitor) }
    println("Validation errors: ${validationVisitor.getErrors()}")

    val renderVisitor = RenderVisitor()
    views.forEach { it.accept(renderVisitor) }
    renderVisitor.getRenderCommands().forEach { println(it) }
}
```

### Kotlin Пример: Интерпретатор Выражений (Expression Evaluator)

```kotlin
// Элементы — типы выражений
sealed class Expression {
    abstract fun accept(visitor: ExpressionVisitor): Double
}

data class Number(val value: Double) : Expression() {
    override fun accept(visitor: ExpressionVisitor) = visitor.visitNumber(this)
}

data class Addition(val left: Expression, val right: Expression) : Expression() {
    override fun accept(visitor: ExpressionVisitor) = visitor.visitAddition(this)
}

data class Multiplication(val left: Expression, val right: Expression) : Expression() {
    override fun accept(visitor: ExpressionVisitor) = visitor.visitMultiplication(this)
}

// Интерфейс посетителя для вычисления
interface ExpressionVisitor {
    fun visitNumber(number: Number): Double
    fun visitAddition(addition: Addition): Double
    fun visitMultiplication(multiplication: Multiplication): Double
}

// Конкретный посетитель — вычислитель
class EvaluatorVisitor : ExpressionVisitor {
    override fun visitNumber(number: Number) = number.value

    override fun visitAddition(addition: Addition): Double {
        val left = addition.left.accept(this)
        val right = addition.right.accept(this)
        return left + right
    }

    override fun visitMultiplication(multiplication: Multiplication): Double {
        val left = multiplication.left.accept(this)
        val right = multiplication.right.accept(this)
        return left * right
    }
}

// Альтернативный посетитель — печать выражений
interface ExpressionPrinterVisitor {
    fun visitNumber(number: Number): String
    fun visitAddition(addition: Addition): String
    fun visitMultiplication(multiplication: Multiplication): String
}

class PrinterVisitor : ExpressionPrinterVisitor {
    override fun visitNumber(number: Number): String = number.value.toString()

    override fun visitAddition(addition: Addition): String {
        val left = addition.left.accept(EvaluatorVisitor())
        val right = addition.right.accept(EvaluatorVisitor())
        // В реальном принтере мы бы рекурсивно строили строку через вызовы посетителя.
        return "(${left} + ${right})"
    }

    override fun visitMultiplication(multiplication: Multiplication): String {
        val left = multiplication.left.accept(EvaluatorVisitor())
        val right = multiplication.right.accept(EvaluatorVisitor())
        // Упрощено для иллюстрации.
        return "(${left} * ${right})"
    }
}

// Использование
fun main() {
    // (2 + 3) * 4
    val expr = Multiplication(
        Addition(Number(2.0), Number(3.0)),
        Number(4.0)
    )

    val evaluator = EvaluatorVisitor()
    val result = expr.accept(evaluator)
    println("Result: $result")

    // Пример использования отдельного посетителя-принтера отличался бы сигнатурами.
}
```

### Объяснение

- Интерфейс `Element` содержит метод `accept(visitor)`.
- Конкретные элементы внутри `accept` передают себя в соответствующий метод `visit` посетителя.
- Интерфейс `Visitor` определяет метод `visit` для каждого типа элемента.
- Конкретные посетители реализуют операции для каждого типа элемента.
- Двойная диспетчеризация — выбор операции зависит и от типа посетителя, и от фактического типа элемента.
- Для Android: подход применим для обхода и проверки иерархий `View`, валидации, рендеринга, сериализации при стабильной структуре и меняющихся операциях.

### Когда Использовать

1. Нужно добавлять новые операции к объектам, не изменяя их классы.
2. Структура содержит множество несвязанных операций — собирать их в одном классе нецелесообразно.
3. Иерархия элементов относительно стабильна, но операции над ними будут меняться и расширяться.

### Преимущества

1. Разделение ответственности — операции отделены от классов элементов.
2. Легко добавлять новые операции — создание новых классов-посетителей без изменения иерархии элементов.
3. Централизованная логика — связанное поведение сгруппировано в посетителях.
4. Упрощённое сопровождение — изменяется посетитель, а не все классы элементов.
5. Типобезопасность — методы посетителя специфичны для конкретных типов.
6. Принцип открытости/закрытости — новые операции добавляются без модификации классов элементов.

### Недостатки

1. Дополнительная сложность — больше классов и механика двойной диспетчеризации.
2. Сложность добавления новых типов элементов — требует изменения всех существующих посетителей.
3. Тесная связанность по типам — посетители должны знать полный набор типов элементов.
4. Увеличение количества классов — может загромождать кодовую базу.
5. Плохо подходит при частых изменениях структуры — часто меняющаяся иерархия элементов делает Visitor тяжёлым в сопровождении.

### Лучшие Практики (RU)

```kotlin
// - РЕКОМЕНДУЕТСЯ: использовать для стабильной структуры объектов с меняющимися операциями
interface DocumentElement {
    fun accept(visitor: DocumentVisitor)
}

interface DocumentVisitor {
    fun visitParagraph(para: Paragraph)
    fun visitImage(img: Image)
    fun visitTable(table: Table)
}

// Разные операции над одной и той же структурой
class WordCountVisitor : DocumentVisitor { /* ... */ }
class SpellCheckVisitor : DocumentVisitor { /* ... */ }
class ExportVisitor : DocumentVisitor { /* ... */ }

// - РЕКОМЕНДУЕТСЯ: использовать с Composite-паттерном
interface FileSystemNode {
    fun accept(visitor: FileSystemVisitor)
}

interface FileSystemVisitor {
    fun visitFile(file: File)
    fun visitDirectory(dir: Directory)
}

// - РЕКОМЕНДУЕТСЯ: предоставлять базовые реализации
abstract class BaseVisitor : ShapeVisitor {
    override fun visit(circle: Circle) {}
    override fun visit(square: Square) {}
    override fun visit(triangle: Triangle) {}
}

class SpecificVisitor : BaseVisitor() {
    override fun visit(circle: Circle) {
        // Обрабатываем только Circle
    }
}

// - НЕ РЕКОМЕНДУЕТСЯ: использовать, когда структура объектов часто меняется
// - НЕ РЕКОМЕНДУЕТСЯ: для простых операций
// - НЕ РЕКОМЕНДУЕТСЯ: использовать посетителей для скрытых изменений инвариантов элементов
```

### Краткое Резюме (RU)

Паттерн Visitor позволяет добавлять новые операции к стабильной структуре объектов без изменения самих классов элементов, опираясь на двойную диспетчеризацию. Используется, когда:
- у вас стабильная иерархия элементов и много разных операций над ними;
- важны разделение ответственности и соответствие принципу открытости/закрытости.

Плюсы: удобное добавление операций, централизованная логика, типобезопасность.
Минусы: сложно добавлять новые типы элементов, повышенная сложность и связность.

---

## Answer (EN)

Visitor is a behavioral design pattern that lets you add new operations to a group of related classes without changing their structure. It is especially useful when you have a stable set of element classes but need to perform different operations over them.

### Definition

The Visitor design pattern is a behavioral pattern that **allows you to add new operations to a group of related classes without modifying their structures** via double dispatch. It is particularly useful when you have a relatively stable set of element classes but need to perform various operations on them, making it easy to extend functionality by adding new visitors (operations) without altering the existing element hierarchy.

### Problems it Solves

- **It should be possible to define a new operation for (some) classes of an object structure without changing the classes.**
- You want to apply many distinct, often unrelated operations over a common object structure without polluting element classes with all these behaviors.

### Solution

1. **Define a separate (visitor) object** that implements an operation to be performed on elements of an object structure.
2. **Clients traverse the object structure** and call a dispatching operation `accept(visitor)` on each element.
3. **The visitor object then performs the operation** on the element via an overloaded `visit(ElementType)` method (double dispatch).

This makes it possible to create new operations independently from the classes of an object structure by adding new visitor objects.

### Motivation for Use

1. **Separation of Concerns** - Separates algorithms from the object structure.
2. **Extensibility for Operations** - Define new operations just by adding new visitors, without changing element classes.
3. **Improved Maintainability** - Centralizes related behavior in visitors.
4. **Enhanced Flexibility** - Different visitors implement different behaviors over the same structure.
5. **Decoupling** - Decouples operations from element implementations.
6. **Best fit scenario** - The set of element types is stable, but the set of operations over them is expected to change or grow.

## Example: Shape Area Calculator

```kotlin
// Step 1: Element Interface and Concrete Elements
interface Shape {
    fun accept(visitor: ShapeVisitor)
}

class Circle(val radius: Double) : Shape {
    override fun accept(visitor: ShapeVisitor) {
        visitor.visit(this)
    }
}

class Square(val side: Double) : Shape {
    override fun accept(visitor: ShapeVisitor) {
        visitor.visit(this)
    }
}

class Triangle(val base: Double, val height: Double) : Shape {
    override fun accept(visitor: ShapeVisitor) {
        visitor.visit(this)
    }
}

// Step 2: Visitor Interface and Concrete Visitors
interface ShapeVisitor {
    fun visit(circle: Circle)
    fun visit(square: Square)
    fun visit(triangle: Triangle)
}

class AreaVisitor : ShapeVisitor {
    private var totalArea = 0.0

    override fun visit(circle: Circle) {
        val area = Math.PI * circle.radius * circle.radius
        println("Area of Circle: $area")
        totalArea += area
    }

    override fun visit(square: Square) {
        val area = square.side * square.side
        println("Area of Square: $area")
        totalArea += area
    }

    override fun visit(triangle: Triangle) {
        val area = 0.5 * triangle.base * triangle.height
        println("Area of Triangle: $area")
        totalArea += area
    }

    fun getTotalArea() = totalArea
}

class PerimeterVisitor : ShapeVisitor {
    override fun visit(circle: Circle) {
        val perimeter = 2 * Math.PI * circle.radius
        println("Perimeter of Circle: $perimeter")
    }

    override fun visit(square: Square) {
        val perimeter = 4 * square.side
        println("Perimeter of Square: $perimeter")
    }

    override fun visit(triangle: Triangle) {
        println("Perimeter of Triangle: (cannot calculate without all sides)")
    }
}

// Client Code
fun main() {
    val shapes: List<Shape> = listOf(
        Circle(5.0),
        Square(4.0),
        Triangle(3.0, 6.0)
    )

    val areaVisitor = AreaVisitor()
    val perimeterVisitor = PerimeterVisitor()

    println("Calculating areas:")
    shapes.forEach { it.accept(areaVisitor) }
    println("Total area: ${areaVisitor.getTotalArea()}")

    println("\nCalculating perimeters:")
    shapes.forEach { it.accept(perimeterVisitor) }
}
```

## Android Example: `View` Hierarchy

```kotlin
// Element interface
interface ViewElement {
    fun accept(visitor: ViewVisitor)
}

// Concrete elements
class ButtonElement(val text: String, val enabled: Boolean) : ViewElement {
    override fun accept(visitor: ViewVisitor) = visitor.visitButton(this)
}

class TextViewElement(val text: String, val textSize: Float) : ViewElement {
    override fun accept(visitor: ViewVisitor) = visitor.visitTextView(this)
}

class ImageViewElement(val imageUrl: String, val width: Int, val height: Int) : ViewElement {
    override fun accept(visitor: ViewVisitor) = visitor.visitImageView(this)
}

// Visitor interface
interface ViewVisitor {
    fun visitButton(button: ButtonElement)
    fun visitTextView(textView: TextViewElement)
    fun visitImageView(imageView: ImageViewElement)
}

// Concrete visitors
class ValidationVisitor : ViewVisitor {
    private val errors = mutableListOf<String>()

    override fun visitButton(button: ButtonElement) {
        if (button.text.isBlank()) {
            errors.add("Button has empty text")
        }
    }

    override fun visitTextView(textView: TextViewElement) {
        if (textView.textSize < 12f) {
            errors.add("TextView text size is too small: ${textView.textSize}")
        }
    }

    override fun visitImageView(imageView: ImageViewElement) {
        if (imageView.width > 1000 || imageView.height > 1000) {
            errors.add("ImageView dimensions are too large: ${imageView.width}x${imageView.height}")
        }
    }

    fun getErrors() = errors
}

class RenderVisitor : ViewVisitor {
    private val renderCommands = mutableListOf<String>()

    override fun visitButton(button: ButtonElement) {
        renderCommands.add("Render button: '${button.text}' (enabled: ${button.enabled})")
    }

    override fun visitTextView(textView: TextViewElement) {
        renderCommands.add("Render text: '${textView.text}' (size: ${textView.textSize})")
    }

    override fun visitImageView(imageView: ImageViewElement) {
        renderCommands.add("Render image: ${imageView.imageUrl} (${imageView.width}x${imageView.height})")
    }

    fun getRenderCommands() = renderCommands
}

// Usage
fun main() {
    val views = listOf(
        ButtonElement("Submit", true),
        TextViewElement("Welcome", 14f),
        ImageViewElement("banner.jpg", 800, 600)
    )

    val validationVisitor = ValidationVisitor()
    views.forEach { it.accept(validationVisitor) }
    println("Validation errors: ${validationVisitor.getErrors()}")

    val renderVisitor = RenderVisitor()
    views.forEach { it.accept(renderVisitor) }
    renderVisitor.getRenderCommands().forEach { println(it) }
}
```

## Kotlin Example: Expression Evaluator

```kotlin
// Elements - Expression types
sealed class Expression {
    abstract fun accept(visitor: ExpressionVisitor): Double
}

data class Number(val value: Double) : Expression() {
    override fun accept(visitor: ExpressionVisitor) = visitor.visitNumber(this)
}

data class Addition(val left: Expression, val right: Expression) : Expression() {
    override fun accept(visitor: ExpressionVisitor) = visitor.visitAddition(this)
}

data class Multiplication(val left: Expression, val right: Expression) : Expression() {
    override fun accept(visitor: ExpressionVisitor) = visitor.visitMultiplication(this)
}

// Visitor interface focused on evaluation
interface ExpressionVisitor {
    fun visitNumber(number: Number): Double
    fun visitAddition(addition: Addition): Double
    fun visitMultiplication(multiplication: Multiplication): Double
}

// Concrete visitor - Evaluator
class EvaluatorVisitor : ExpressionVisitor {
    override fun visitNumber(number: Number) = number.value

    override fun visitAddition(addition: Addition): Double {
        val left = addition.left.accept(this)
        val right = addition.right.accept(this)
        return left + right
    }

    override fun visitMultiplication(multiplication: Multiplication): Double {
        val left = multiplication.left.accept(this)
        val right = multiplication.right.accept(this)
        return left * right
    }
}

// Alternative concrete visitor - Pretty printer
interface ExpressionPrinterVisitor {
    fun visitNumber(number: Number): String
    fun visitAddition(addition: Addition): String
    fun visitMultiplication(multiplication: Multiplication): String
}

class PrinterVisitor : ExpressionPrinterVisitor {
    override fun visitNumber(number: Number): String = number.value.toString()

    override fun visitAddition(addition: Addition): String {
        val left = addition.left.accept(EvaluatorVisitor())
        val right = addition.right.accept(EvaluatorVisitor())
        // In a real printer, we would recursively build a String via visitor calls.
        return "(${left} + ${right})"
    }

    override fun visitMultiplication(multiplication: Multiplication): String {
        val left = multiplication.left.accept(EvaluatorVisitor())
        val right = multiplication.right.accept(EvaluatorVisitor())
        // Simplified for illustration.
        return "(${left} * ${right})"
    }
}

// Usage
fun main() {
    // (2 + 3) * 4
    val expr = Multiplication(
        Addition(Number(2.0), Number(3.0)),
        Number(4.0)
    )

    val evaluator = EvaluatorVisitor()
    val result = expr.accept(evaluator)
    println("Result: $result")

    // Example of using a separate printer interface/visitor would differ in signature.
}
```

### Explanation

- `Element` interface has `accept(visitor)` method.
- Concrete elements pass themselves to the corresponding `visit` method of the visitor.
- `Visitor` interface defines `visit` methods for each element type.
- Concrete visitors implement operations for each element type.
- `Double` dispatch - operation depends on both visitor type and element runtime type.
- Android: applicable for view traversal, validation, serialization, rendering when the hierarchy is stable and operations evolve.

### When to Use

1. Need to add operations to objects without modifying their classes.
2. Structure contains many unrelated operations - grouping them in the same class is undesirable.
3. Element hierarchy is relatively stable, but operations over them are expected to evolve.

### Pros

1. Separation of Concerns - Operations are separated from element classes.
2. Easy to Add New Features - Create new visitor classes (new operations) without changing elements.
3. Centralized Logic - Related operations grouped in visitors.
4. Easier Maintenance - Update visitor implementations instead of all element classes.
5. Type Safety - Each visitor method is type-specific.
6. Open/Closed Principle - Add operations without modifying element classes.

### Cons

1. Added Complexity - Extra classes and double dispatch mechanics.
2. Hard to Add New Element Types - Requires changes to all existing visitors.
3. Tight Coupling - Visitors must know all element types.
4. More Classes - Can clutter the codebase.
5. Not Ideal for Frequently Changing Structures - Visitor becomes expensive to maintain.

### Best Practices

```kotlin
// - DO: Use for stable object structure with changing operations
interface DocumentElement {
    fun accept(visitor: DocumentVisitor)
}

interface DocumentVisitor {
    fun visitParagraph(para: Paragraph)
    fun visitImage(img: Image)
    fun visitTable(table: Table)
}

// Different operations on same structure
class WordCountVisitor : DocumentVisitor { /* ... */ }
class SpellCheckVisitor : DocumentVisitor { /* ... */ }
class ExportVisitor : DocumentVisitor { /* ... */ }

// - DO: Use with composite pattern
interface FileSystemNode {
    fun accept(visitor: FileSystemVisitor)
}

interface FileSystemVisitor {
    fun visitFile(file: File)
    fun visitDirectory(dir: Directory)
}

// - DO: Provide default implementations
abstract class BaseVisitor : ShapeVisitor {
    override fun visit(circle: Circle) {}
    override fun visit(square: Square) {}
    override fun visit(triangle: Triangle) {}
}

class SpecificVisitor : BaseVisitor() {
    override fun visit(circle: Circle) {
        // Only handle circles
    }
}

// - DON'T: Use when object structure changes frequently
// - DON'T: Use for simple operations
// - DON'T: Rely on visitors to mutate core invariants of elements in surprising ways
```

### Short Summary (EN)

Visitor is a behavioral pattern that allows adding new operations to an object structure without modifying element classes, using double dispatch.
Use it when:
- you have a stable element hierarchy with many different operations;
- you want clear separation of concerns and adherence to the Open/Closed Principle.

Pros: convenient addition of operations, centralized logic, type safety.
Cons: hard to add new element types, extra complexity and coupling.

---

## Follow-ups

- How does the Visitor pattern compare to using pattern matching or `when` expressions over sealed classes in Kotlin?
- In which scenarios would you prefer strategy or command patterns instead of visitor?
- How would you adapt Visitor when your element hierarchy changes more frequently?

## References

- [[c-architecture-patterns]]
- [[c-computer-science]]
- [Visitor design pattern](https://www.geeksforgeeks.org/system-design/visitor-design-pattern/)
- [Visitor pattern](https://en.wikipedia.org/wiki/Visitor_pattern)
- [Visitor Design Pattern in Kotlin](https://www.javaguides.net/2023/10/visitor-design-pattern-in-kotlin.html)
- [Visitor Design Pattern](https://sourcemaking.com/design-patterns/visitor)
- [Visitor](https://refactoring.guru/design-patterns/visitor)
- [Visitor Software Pattern Kotlin Examples](https://softwarepatterns.com/kotlin/visitor-software-pattern-kotlin-example)

---
*Source: Kirchhoff Android Interview Questions*