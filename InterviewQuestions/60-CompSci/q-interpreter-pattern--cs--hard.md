---
id: cs-031
title: "Interpreter Pattern / Паттерн Интерпретатор"
aliases: ["Interpreter Pattern", "Паттерн Интерпретатор"]
topic: cs
subtopics: [behavioral-patterns, design-patterns, expression-evaluation, language-processing]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: []
created: 2025-10-15
updated: 2025-01-25
tags: [behavioral-patterns, design-patterns, difficulty/hard, expression-evaluation, interpreter, language-processing]
sources: [https://refactoring.guru/design-patterns/interpreter]
---

# Вопрос (RU)
> Что такое паттерн Интерпретатор? Когда его использовать и как он работает?

# Question (EN)
> What is the Interpreter pattern? When to use it and how does it work?

---

## Ответ (RU)

**Теория Interpreter Pattern:**
Interpreter - behavioral design pattern для интерпретации языка или выражения. Решает проблему: нужно определить grammar для простого языка, чтобы предложения могли быть интерпретированы. Решение: представлять grammar как набор classes, где каждый class - правило в grammar. Позволяет строить Abstract Syntax Tree (AST) для интерпретации сложных expressions.

**Определение:**

*Теория:* Interpreter pattern определяет способ интерпретации и evaluation language grammar или expressions. Представляет grammar как set of classes, где каждый class представляет rule или expression в grammar. Позволяет compose hierarchically для интерпретации complex expressions. Создаёт AST (Abstract Syntax Tree) для representation.

**Проблемы, которые решает:**

*Теория:* Когда нужно определить grammar для простого языка (Domain Specific Language). Когда есть часто возникающие problems, которые можно represent как sentences в simple language. Когда нужно flexible способ specify different expressions без hard-coding их в classes. Примеры: search expressions, query languages, regular expressions, calculators.

```kotlin
// ✅ Базовый пример: Expression интерпретация
interface Expression {
    fun interpret(context: String): Boolean
}

// Terminal expression - базовое выражение
class TerminalExpression(private val data: String) : Expression {
    override fun interpret(context: String): Boolean {
        return context.contains(data)
    }
}

// Non-terminal expressions - составные выражения
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

// Использование
fun main() {
    val isMale = OrExpression(
        TerminalExpression("John"),
        TerminalExpression("Robert")
    )

    val isMarriedWoman = AndExpression(
        TerminalExpression("Julie"),
        TerminalExpression("Married")
    )

    println(isMale.interpret("John"))  // true
    println(isMarriedWoman.interpret("Married Julie"))  // true
}
```

**Реальный пример: Калькулятор выражений:**

*Теория:* Interpreter используется для parsing и evaluation математических выражений. Строится AST для представления expression structure. Expression classes интерпретируют свои части и combine результаты. Позволяет динамически parse и evaluate expressions во время runtime.

```kotlin
// ✅ Калькулятор выражений
abstract class Expression {
    abstract fun evaluate(): Int
}

class NumberExpression(private val value: Int) : Expression() {
    override fun evaluate() = value
}

class AddExpression(
    private val left: Expression,
    private val right: Expression
) : Expression() {
    override fun evaluate() = left.evaluate() + right.evaluate()
}

class MultiplyExpression(
    private val left: Expression,
    private val right: Expression
) : Expression() {
    override fun evaluate() = left.evaluate() * right.evaluate()
}

// Использование: "3 + 4 * 5"
val expression = AddExpression(
    NumberExpression(3),
    MultiplyExpression(NumberExpression(4), NumberExpression(5))
)
println(expression.evaluate())  // 23
```

**Когда использовать:**

*Теория:* Используйте Interpreter когда: нужно evaluate серию expressions, following некоторую grammar; работаете с complex expressions, которые можно разбить на smaller components; язык relatively simple но нужен structured approach. Не используйте для: very large grammars (performance issues), simple cases (over-engineering), frequently changing grammars (maintenance burden).

✅ **Use Interpreter when:**
- Нужно evaluate expressions, following grammar
- Complex expressions можно разбить на smaller parts
- Относительно simple grammar
- Нужна flexibility в expressions

❌ **Don't use Interpreter when:**
- Very large grammar (performance issues)
- Simple cases (over-engineering)
- Frequently changing grammar (maintenance burden)
- Нужна высокая performance для large expression trees

**Реализация:**

*Теория:* Шаги реализации: 1. Define abstract Expression, declares interpret operation. 2. Для каждого rule в grammar, create concrete Expression class. 3. Client создаёт instances этих classes для interpret specific expressions. AST строится compositionally из Expression objects.

**Преимущества:**

1. **Extensibility** - легко добавлять новые expressions без изменения existing code
2. **Maintainability** - expression logic разделена на individual components
3. **Readability** - код более understandable с well-named classes
4. **Separation of Concerns** - parsing отделён от evaluation

**Недостатки:**

1. **Complexity** - может introduce unnecessary complexity для simple scenarios
2. **Performance** - recursive nature может lead к performance issues для large trees
3. **Grammar Changes** - изменения в grammar требуют changes во многих classes
4. **Not for Large Grammars** - не лучший choice для very large grammars

**Ключевые концепции:**

1. **Abstract Syntax Tree** - AST для representation
2. **Terminal vs Non-terminal** - базовые vs составные expressions
3. **Recursive Evaluation** - expressions evaluate рекурсивно
4. **Grammar as Classes** - grammar represented как classes
5. **Compositional Structure** - expressions composed hierarchically

## Answer (EN)

**Interpreter Pattern Theory:**
Interpreter - behavioral design pattern for interpreting language or expressions. Solves problem: need to define grammar for simple language so sentences can be interpreted. Solution: represent grammar as set of classes, where each class is rule in grammar. Allows building Abstract Syntax Tree (AST) for interpreting complex expressions.

**Definition:**

*Theory:* Interpreter pattern defines way to interpret and evaluate language grammar or expressions. Represents grammar as set of classes, where each class represents rule or expression in grammar. Allows composing hierarchically for interpreting complex expressions. Creates AST (Abstract Syntax Tree) for representation.

**Problems Solved:**

*Theory:* When need to define grammar for simple language (Domain Specific Language). When have frequently occurring problems that can be represented as sentences in simple language. When need flexible way to specify different expressions without hard-coding them in classes. Examples: search expressions, query languages, regular expressions, calculators.

```kotlin
// ✅ Basic example: Expression interpretation
interface Expression {
    fun interpret(context: String): Boolean
}

// Terminal expression - basic expression
class TerminalExpression(private val data: String) : Expression {
    override fun interpret(context: String): Boolean {
        return context.contains(data)
    }
}

// Non-terminal expressions - composite expressions
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

// Usage
fun main() {
    val isMale = OrExpression(
        TerminalExpression("John"),
        TerminalExpression("Robert")
    )

    val isMarriedWoman = AndExpression(
        TerminalExpression("Julie"),
        TerminalExpression("Married")
    )

    println(isMale.interpret("John"))  // true
    println(isMarriedWoman.interpret("Married Julie"))  // true
}
```

**Real Example: Expression Calculator:**

*Theory:* Interpreter used for parsing and evaluating mathematical expressions. Builds AST for representing expression structure. Expression classes interpret their parts and combine results. Allows dynamically parsing and evaluating expressions at runtime.

```kotlin
// ✅ Expression calculator
abstract class Expression {
    abstract fun evaluate(): Int
}

class NumberExpression(private val value: Int) : Expression() {
    override fun evaluate() = value
}

class AddExpression(
    private val left: Expression,
    private val right: Expression
) : Expression() {
    override fun evaluate() = left.evaluate() + right.evaluate()
}

class MultiplyExpression(
    private val left: Expression,
    private val right: Expression
) : Expression() {
    override fun evaluate() = left.evaluate() * right.evaluate()
}

// Usage: "3 + 4 * 5"
val expression = AddExpression(
    NumberExpression(3),
    MultiplyExpression(NumberExpression(4), NumberExpression(5))
)
println(expression.evaluate())  // 23
```

**When to Use:**

*Theory:* Use Interpreter when: need to evaluate series of expressions following some grammar; dealing with complex expressions that can be broken into smaller components; language relatively simple but needs structured approach. Don't use for: very large grammars (performance issues), simple cases (over-engineering), frequently changing grammars (maintenance burden).

✅ **Use Interpreter when:**
- Need to evaluate expressions following grammar
- Complex expressions can be broken into smaller parts
- Relatively simple grammar
- Need flexibility in expressions

❌ **Don't use Interpreter when:**
- Very large grammar (performance issues)
- Simple cases (over-engineering)
- Frequently changing grammar (maintenance burden)
- Need high performance for large expression trees

**Implementation:**

*Theory:* Implementation steps: 1. Define abstract Expression, declares interpret operation. 2. For each rule in grammar, create concrete Expression class. 3. Client creates instances of these classes to interpret specific expressions. AST built compositionally from Expression objects.

**Advantages:**

1. **Extensibility** - easy to add new expressions without changing existing code
2. **Maintainability** - expression logic separated into individual components
3. **Readability** - code more understandable with well-named classes
4. **Separation of Concerns** - parsing separated from evaluation

**Disadvantages:**

1. **Complexity** - may introduce unnecessary complexity for simple scenarios
2. **Performance** - recursive nature may lead to performance issues for large trees
3. **Grammar Changes** - grammar changes require changes in many classes
4. **Not for Large Grammars** - not best choice for very large grammars

**Key Concepts:**

1. **Abstract Syntax Tree** - AST for representation
2. **Terminal vs Non-terminal** - basic vs composite expressions
3. **Recursive Evaluation** - expressions evaluate recursively
4. **Grammar as Classes** - grammar represented as classes
5. **Compositional Structure** - expressions composed hierarchically

---

## Follow-ups

- How does Interpreter pattern relate to Composite pattern?
- What is the difference between Interpreter and Visitor pattern?
- When would you use a parser generator instead of Interpreter?

## Related Questions

### Prerequisites (Easier)
- Basic design patterns concepts
- Tree structures understanding

### Related (Same Level)
- [[q-composite-pattern--design-patterns--medium]] - Composite pattern (similar structure)
- [[q-visitor-pattern--design-patterns--hard]] - Visitor pattern (alternative approach)

### Advanced (Hardder)
- [[q-flyweight-pattern--design-patterns--hard]] - Optimization techniques
- Parser generators vs Interpreter pattern
