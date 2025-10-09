---
tags:
  - design-patterns
  - behavioral-patterns
  - visitor
  - gof-patterns
  - double-dispatch
difficulty: hard
status: reviewed
---

# Visitor Pattern

**English**: What is the Visitor pattern? When and why should it be used?

## Answer

**Visitor (Посетитель)** - это поведенческий паттерн проектирования, который позволяет добавлять новые операции к группе связанных классов без изменения их структуры. Он особенно полезен, когда у вас есть стабильный набор классов, но нужно выполнять различные операции над ними.

### Определение

The Visitor design pattern is a behavioral pattern that **allows you to add new operations to a group of related classes without modifying their structures**. It is particularly useful when you have a stable set of classes but need to perform various operations on them, making it easy to extend functionality without altering the existing codebase.

### Проблемы, которые решает

What problems can the Visitor design pattern solve?

- **It should be possible to define a new operation for (some) classes of an object structure without changing the classes**

### Решение

What solution does the Visitor design pattern describe?

1. **Define a separate (visitor) object** that implements an operation to be performed on elements of an object structure
2. **Clients traverse the object structure** and call a dispatching operation `accept(visitor)` on an element
3. **The visitor object then performs the operation** on the element ("visits the element")

This makes it possible to create new operations independently from the classes of an object structure by adding new visitor objects.

### Мотивация использования

Motivation for Using the Visitor Pattern:

1. **Separation of Concerns** - Separates algorithm from object structure
2. **Extensibility** - Define new operations without changing element classes
3. **Improved Maintainability** - Centralizes related behavior in visitor
4. **Enhanced Flexibility** - Define operations without modifying element classes
5. **Decoupling** - Decouples operations from object structure

## Пример: Shape Area Calculator

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

## Android Example: View Hierarchy

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

// Visitor interface
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

// Concrete visitor - String formatter
class PrinterVisitor : ExpressionVisitor {
    override fun visitNumber(number: Number) = number.value

    override fun visitAddition(addition: Addition): Double {
        val left = addition.left.accept(this)
        val right = addition.right.accept(this)
        println("($left + $right)")
        return left + right
    }

    override fun visitMultiplication(multiplication: Multiplication): Double {
        val left = multiplication.left.accept(this)
        val right = multiplication.right.accept(this)
        println("($left * $right)")
        return left * right
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

    val printer = PrinterVisitor()
    expr.accept(printer)
}
```

### Объяснение

**Explanation**:

- **Element** interface has `accept(visitor)` method
- **Concrete elements** pass themselves to visitor's visit method
- **Visitor** interface has visit method for each element type
- **Concrete visitors** implement operations for each element
- **Double dispatch** - operation depends on both visitor and element type
- **Android**: View traversal, validation, rendering, serialization

## Когда использовать?

When to use:

1. **Need to add operations to objects** without modifying their classes
2. **Structure contains many unrelated operations** - Grouping them in same class isn't feasible
3. **Classes defining objects aren't likely to change** - But want to define new operations on them

## Преимущества и недостатки

### Pros (Преимущества)

1. **Separation of Concerns** - Operations separated from objects
2. **Easy to Add New Features** - Create new visitor classes
3. **Centralized Logic** - All operations in one place
4. **Easier Maintenance** - Update visitor, not all object classes
5. **Type Safety** - Each visitor method is type-specific
6. **Open/Closed Principle** - Add operations without modifying elements

### Cons (Недостатки)

1. **Added Complexity** - Extra classes and double dispatch
2. **Challenging to Add New Objects** - Requires changes to all visitors
3. **Tight Coupling** - Visitors need to know all element types
4. **More Classes** - Can clutter codebase
5. **Not Ideal for Frequent Changes** - Adding element types is difficult

## Best Practices

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

class FileSystemVisitor {
    fun visitFile(file: File) { /* ... */ }
    fun visitDirectory(dir: Directory) { /* ... */ }
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
// - DON'T: Modify element state in visitors
```

**English**: **Visitor** is a behavioral pattern that allows adding new operations to object structure without modifying classes. **Problem**: Need to perform various operations on stable object structure. **Solution**: Define visitor with operation methods for each element type, elements accept visitors and dispatch to appropriate method. **Use when**: (1) Need to add operations without modifying classes, (2) Many unrelated operations, (3) Object structure stable but operations change. **Android**: View traversal, validation, serialization, rendering. **Pros**: separation of concerns, easy to add operations, centralized logic. **Cons**: hard to add new element types, complexity. **Examples**: Shape calculations, document processing, expression evaluation, view validation.

## Links

- [Visitor design pattern](https://www.geeksforgeeks.org/system-design/visitor-design-pattern/)
- [Visitor pattern](https://en.wikipedia.org/wiki/Visitor_pattern)
- [Visitor Design Pattern in Kotlin](https://www.javaguides.net/2023/10/visitor-design-pattern-in-kotlin.html)

## Further Reading

- [Visitor Design Pattern](https://sourcemaking.com/design_patterns/visitor)
- [Visitor](https://refactoring.guru/design-patterns/visitor)
- [Visitor Software Pattern Kotlin Examples](https://softwarepatterns.com/kotlin/visitor-software-pattern-kotlin-example)

---
*Source: Kirchhoff Android Interview Questions*
