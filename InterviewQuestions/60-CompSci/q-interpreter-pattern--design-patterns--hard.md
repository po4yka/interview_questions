---
id: 20251012-1227111150
title: Interpreter Pattern
topic: design-patterns
difficulty: hard
status: draft
moc: moc-cs
created: 2025-10-15
tags: []
related: [q-coroutinescope-vs-supervisorscope--programming-languages--medium, q-what-is-coroutinescope--programming-languages--medium, q-data-sealed-classes-why--programming-languages--medium]
  - composite-pattern
  - visitor-pattern
subtopics:
  - behavioral-patterns
  - language-processing
  - expression-evaluation
---
# Interpreter Pattern / Паттерн Интерпретатор

# Question (EN)
> What is the Interpreter pattern?

# Вопрос (RU)
> Что такое паттерн Интерпретатор?

---

## Answer (EN)


### Definition
The Interpreter design pattern is a behavioral design pattern that defines a way to interpret and evaluate language grammar or expressions. It provides a mechanism to evaluate sentences in a language by representing their grammar as a set of classes. Each class represents a rule or expression in the grammar, and the pattern allows these classes to be composed hierarchically to interpret complex expressions.

### Problems It Solves
What problems can the Interpreter design pattern solve?
- A grammar for a simple language should be defined
- So that sentences in the language can be interpreted

When a problem occurs very often, it could be considered to represent it as a sentence in a simple language (Domain Specific Languages) so that an interpreter can solve the problem by interpreting the sentence.

For example, when many different or complex search expressions must be specified. Implementing (hard-wiring) them directly into a class is inflexible because it commits the class to particular expressions and makes it impossible to specify new expressions or change existing ones independently from (without having to change) the class.

### Solution
What solution does the Interpreter design pattern describe?
- Define a grammar for a simple language by defining an `Expression` class hierarchy and implementing an `interpret()` operation
- Represent a sentence in the language by an abstract syntax tree (AST) made up of `Expression` instances
- Interpret a sentence by calling `interpret()` on the AST

### When to Use
The Interpreter pattern comes in handy when:
- We need to evaluate a series of expressions that follow some grammar or rules
- We're dealing with complex expressions that can be broken down into smaller components
- The language we're working with is relatively simple but needs a structured approach

### Implementation Steps
1. Define an abstract expression that declares an interpret operation
2. For every rule in the grammar, create a concrete expression class
3. The client creates instances of these concrete expression classes to interpret the specific expressions

### Example in Kotlin

```kotlin
// Step 1: Define the Abstract Expression
interface Expression {
    fun interpret(context: String): Boolean
}

// Step 2: Concrete Expressions
class TerminalExpression(private val data: String) : Expression {
    override fun interpret(context: String): Boolean {
        return context.contains(data)
    }
}

class OrExpression(
    private val expr1: Expression,
    private val expr2: Expression
) : Expression {
    override fun interpret(context: String): Boolean {
        return expr1.interpret(context) || expr2.interpret(context)
    }
}

class AndExpression(
    private val expr1: Expression,
    private val expr2: Expression
) : Expression {
    override fun interpret(context: String): Boolean {
        return expr1.interpret(context) && expr2.interpret(context)
    }
}

// Client code to interpret expressions
fun getMaleExpression(): Expression {
    val john = TerminalExpression("John")
    val robert = TerminalExpression("Robert")
    return OrExpression(john, robert)
}

fun getMarriedWomanExpression(): Expression {
    val julie = TerminalExpression("Julie")
    val married = TerminalExpression("Married")
    return AndExpression(julie, married)
}

fun main() {
    val isMale = getMaleExpression()
    val isMarriedWoman = getMarriedWomanExpression()

    println("John is male? ${isMale.interpret("John")}")
    println("Julie is a married woman? ${isMarriedWoman.interpret("Married Julie")}")
}
```

**Output:**
```
John is male? true
Julie is a married woman? true
```

**Explanation:**
- We define an `Expression` interface with the `interpret` method
- `TerminalExpression`, `OrExpression`, and `AndExpression` are concrete implementations that interpret specific expressions
- In the client code, we build up a more complex expression by combining the simple terminal expressions. For instance, the `getMarriedWomanExpression` checks if a woman is named "Julie" and is "Married"

### Advantages
- **Extensibility**. It's easy to add more expressions or operators without affecting the existing code
- **Maintainability**. The expression logic is separated into individual components, making the code cleaner and easier to maintain
- **Readability**. With the use of well-named classes (like AddExpression, NumberExpression), the code becomes more understandable and easier to extend

### Disadvantages
- **Complexity**. For simple scenarios, the Interpreter pattern might introduce unnecessary complexity. If the problem doesn't require a structured approach, a simpler solution might be more appropriate
- **Performance**. In cases with large and complex expression trees, the recursive nature of the Interpreter pattern could lead to performance issues. It might not be the best choice for very large grammars

---



## Ответ (RU)

### Определение
Паттерн проектирования Интерпретатор - это поведенческий паттерн проектирования, который определяет способ интерпретации и оценки грамматики или выражений языка. Он предоставляет механизм для оценки предложений на языке путем представления их грамматики в виде набора классов. Каждый класс представляет правило или выражение в грамматике, и паттерн позволяет этим классам быть скомпонованными иерархически для интерпретации сложных выражений.

### Решаемые Проблемы
Какие проблемы решает паттерн Интерпретатор?
- Должна быть определена грамматика для простого языка
- Чтобы предложения на языке могли быть интерпретированы

Когда проблема возникает очень часто, можно рассмотреть возможность представления ее в виде предложения на простом языке (предметно-ориентированных языках), чтобы интерпретатор мог решить проблему, интерпретируя предложение.

Например, когда нужно указать много различных или сложных поисковых выражений. Реализация (жесткое кодирование) их непосредственно в классе негибка, потому что это привязывает класс к конкретным выражениям и делает невозможным указание новых выражений или изменение существующих независимо от (без необходимости изменения) класса.

### Решение
Какое решение описывает паттерн Интерпретатор?
- Определить грамматику для простого языка путем определения иерархии классов `Expression` и реализации операции `interpret()`
- Представить предложение на языке в виде абстрактного синтаксического дерева (AST), состоящего из экземпляров `Expression`
- Интерпретировать предложение путем вызова `interpret()` на AST

### Когда Использовать
Паттерн Интерпретатор пригодится, когда:
- Нам нужно оценить серию выражений, которые следуют некоторой грамматике или правилам
- Мы имеем дело со сложными выражениями, которые можно разбить на более мелкие компоненты
- Язык, с которым мы работаем, относительно прост, но требует структурированного подхода

### Шаги Реализации
1. Определить абстрактное выражение, которое объявляет операцию интерпретации
2. Для каждого правила в грамматике создать класс конкретного выражения
3. Клиент создает экземпляры этих классов конкретных выражений для интерпретации конкретных выражений

### Пример на Kotlin

```kotlin
// Шаг 1: Определить абстрактное выражение
interface Expression {
    fun interpret(context: String): Boolean
}

// Шаг 2: Конкретные выражения
class TerminalExpression(private val data: String) : Expression {
    override fun interpret(context: String): Boolean {
        return context.contains(data)
    }
}

class OrExpression(
    private val expr1: Expression,
    private val expr2: Expression
) : Expression {
    override fun interpret(context: String): Boolean {
        return expr1.interpret(context) || expr2.interpret(context)
    }
}

class AndExpression(
    private val expr1: Expression,
    private val expr2: Expression
) : Expression {
    override fun interpret(context: String): Boolean {
        return expr1.interpret(context) && expr2.interpret(context)
    }
}

// Клиентский код для интерпретации выражений
fun getMaleExpression(): Expression {
    val john = TerminalExpression("John")
    val robert = TerminalExpression("Robert")
    return OrExpression(john, robert)
}

fun getMarriedWomanExpression(): Expression {
    val julie = TerminalExpression("Julie")
    val married = TerminalExpression("Married")
    return AndExpression(julie, married)
}

fun main() {
    val isMale = getMaleExpression()
    val isMarriedWoman = getMarriedWomanExpression()

    println("John is male? ${isMale.interpret("John")}")
    println("Julie is a married woman? ${isMarriedWoman.interpret("Married Julie")}")
}
```

**Вывод:**
```
John is male? true
Julie is a married woman? true
```

**Объяснение:**
- Мы определяем интерфейс `Expression` с методом `interpret`
- `TerminalExpression`, `OrExpression` и `AndExpression` - это конкретные реализации, которые интерпретируют конкретные выражения
- В клиентском коде мы строим более сложное выражение путем комбинирования простых терминальных выражений. Например, `getMarriedWomanExpression` проверяет, названа ли женщина "Julie" и является ли она "Married"

### Преимущества
- **Расширяемость**. Легко добавлять больше выражений или операторов без влияния на существующий код
- **Поддерживаемость**. Логика выражений разделена на отдельные компоненты, что делает код чище и проще в поддержке
- **Читаемость**. С использованием хорошо названных классов (таких как AddExpression, NumberExpression) код становится более понятным и легче расширяемым

### Недостатки
- **Сложность**. Для простых сценариев паттерн Интерпретатор может внести ненужную сложность. Если проблема не требует структурированного подхода, более простое решение может быть более подходящим
- **Производительность**. В случаях с большими и сложными деревьями выражений рекурсивная природа паттерна Интерпретатор может привести к проблемам с производительностью. Это может быть не лучшим выбором для очень больших грамматик

---

## References
- [Interpreter Design Pattern in Java - GeeksforGeeks](https://www.geeksforgeeks.org/java/interpreter-design-pattern-in-java/)
- [Interpreter pattern - Wikipedia](https://en.wikipedia.org/wiki/Interpreter_pattern)
- [Understanding the Interpreter Design Pattern in Kotlin - Medium](https://medium.com/softaai-blogs/understanding-the-interpreter-design-pattern-in-kotlin-a-comprehensive-guide-28b8dba98bb9)
- [Interpreter Design Pattern in Kotlin](https://www.javaguides.net/2023/10/interpreter-design-pattern-in-kotlin.html)
- [Interpreter Design Pattern - SourceMaking](https://sourcemaking.com/design_patterns/interpreter)

---

**Source:** Kirchhoff-Android-Interview-Questions
**Attribution:** Content adapted from the Kirchhoff repository


---

## Related Questions

### Hub
- [[q-design-patterns-types--design-patterns--medium]] - Design pattern categories overview

### Advanced Patterns
- [[q-bridge-pattern--design-patterns--hard]] - Bridge pattern
- [[q-visitor-pattern--design-patterns--hard]] - Visitor pattern
- [[q-flyweight-pattern--design-patterns--hard]] - Flyweight pattern

