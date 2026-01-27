---
id: cs-031
title: Interpreter Pattern / Паттерн Интерпретатор
anki_cards:
- slug: cs-031-0-en
  language: en
  anki_id: 1768454535363
  synced_at: '2026-01-25T13:01:16.940655'
- slug: cs-031-0-ru
  language: ru
  anki_id: 1768454535389
  synced_at: '2026-01-25T13:01:16.942039'
aliases:
- Interpreter Pattern
- Паттерн Интерпретатор
topic: cs
subtopics:
- behavioral-patterns
- design-patterns
- language-processing
question_kind: theory
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-cs
related:
- c-architecture-patterns
- c-dao-pattern
- c-software-design-patterns
- q-abstract-factory-pattern--cs--medium
created: 2025-10-15
updated: 2025-11-11
tags:
- behavioral-patterns
- design-patterns
- difficulty/hard
- expression-evaluation
- interpreter
- language-processing
sources:
- https://refactoring.guru/design-patterns/interpreter
---
# Вопрос (RU)
> Что такое паттерн Интерпретатор? Когда его использовать и как он работает?

# Question (EN)
> What is the Interpreter pattern? When to use it and how does it work?

---

## Ответ (RU)

**Теория Interpreter Pattern:**
Interpreter — поведенческий паттерн проектирования для интерпретации предложений некоторого языка. Решает проблему: нужно формально определить простую грамматику, чтобы выражения/предложения можно было интерпретировать программно. Решение: представить элементы грамматики как набор классов, где каждый класс соответствует правилу или типу выражения. Обычно (но не обязательно по определению) поверх этого строится дерево синтаксиса (AST) для интерпретации сложных выражений.

**Определение:**

*Теория:* Паттерн Interpreter определяет представление грамматики языка в виде иерархии классов выражений и задает общий интерфейс `interpret`/`evaluate`, позволяющий интерпретировать выражения, составленные по этой грамматике. Каждое правило или терминальное/нетерминальное выражение описывается отдельным классом. Композиция таких объектов образует структуру (часто AST), которая рекурсивно вычисляется.

Важно: классическое определение предполагает, что язык достаточно простой, чтобы его грамматика могла быть напрямую отображена на иерархию классов. Построение AST и отдельный этап парсинга — распространенный, но не строго обязательный элемент реализации.

**Проблемы, которые решает:**

*Теория:*
- Когда нужно описать простой предметно-ориентированный язык (DSL) с относительно стабильной грамматикой.
- Когда повторяющиеся задачи удобно выражать в виде предложений этого языка.
- Когда нужен гибкий способ задавать и комбинировать выражения без жёсткого захардкоженного кода if/switch.

Примеры: фильтры и поисковые выражения, простые query languages, регулярные выражения (как концепт, не конкретные промышленные реализации), простые калькуляторы, конфигурационные мини-языки.

```kotlin
// ✅ Упрощённый пример: интерпретация выражений над строкой контекста
interface Expression {
    fun interpret(context: String): Boolean
}

// Terminal expression - базовое выражение
class TerminalExpression(private val data: String) : Expression {
    override fun interpret(context: String): Boolean {
        // Упрощённая логика для демонстрации идеи; в реальном языке
        // обычно используется разбор токенов/структур, а не contains.
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

    println(isMale.interpret("John"))           // true
    println(isMarriedWoman.interpret("Married Julie"))  // true
}
```

**Реальный пример: Калькулятор выражений:**

*Теория:* Interpreter может использоваться для представления и вычисления математических выражений. Классы выражений инкапсулируют операции и рекурсивно вычисляют результат. В реальной реализации поверх этого обычно добавляется парсер, который переводит входную строку в дерево выражений (AST), но здесь мы фокусируемся на стороне интерпретации.

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

// Использование: выражение "3 + 4 * 5"
fun main() {
    val expression: Expression = AddExpression(
        NumberExpression(3),
        MultiplyExpression(NumberExpression(4), NumberExpression(5))
    )
    println(expression.evaluate())  // 23
}
```

Здесь дерево выражений создаётся вручную для краткости; в полном решении для Interpreter-подхода обычно есть шаг парсинга входной строки в такую структуру.

**Когда использовать:**

*Теория:* Используйте Interpreter, когда:
- нужно интерпретировать множество выражений по фиксированной и относительно простой грамматике;
- сложные выражения естественно раскладываются на композицию меньших выражений;
- требуется расширяемость за счёт добавления новых типов выражений;
- язык не настолько сложен, чтобы оправдывать использование полноценных парсер-генераторов.

Не используйте, когда:
- грамматика очень большая или сложная (слишком много классов, проблемы с поддержкой и производительностью);
- задача тривиальна и не требует введения отдельного языка (оверинжиниринг);
- грамматика часто меняется (дорого обновлять множество классов);
- критична высокая производительность на очень больших деревьях выражений.

✅ **Используйте Interpreter, когда:**
- Нужно `evaluate`/`interpret` выражения по формальной, но простой грамматике
- Сложные выражения можно разбить на меньшие части и представить объектами
- Грамматика относительно простая и стабильная
- Нужна гибкость в определении и комбинировании новых выражений

❌ **Не используйте Interpreter, когда:**
- Очень большая или сложная грамматика (проблемы с производительностью и сопровождением)
- Слишком простой кейс (over-engineering)
- Часто меняющаяся грамматика (дорогое сопровождение)
- Нужна очень высокая производительность для больших деревьев выражений

**Реализация:**

*Теория:* Основные шаги:
1. Определить общий интерфейс/абстрактный класс `Expression` с операцией `interpret`/`evaluate`.
2. Для каждого правила грамматики создать конкретный класс выражения (Terminal / Non-terminal).
3. Клиент строит выражения (обычно дерево) из этих объектов и вызывает `interpret`/`evaluate` на корне.
4. (Часто) Добавить парсер, который превращает текстовый ввод в структуру `Expression`.

**Преимущества:**

1. **Extensibility** — легко добавлять новые типы выражений за счёт новых классов
2. **Maintainability** — логика разных конструкций языка разделена по отдельным классам
3. **Readability** — структура языка явно отражена в коде
4. **Separation of Concerns** — грамматика и операции интерпретации инкапсулированы; парсинг может быть отделён отдельным слоем

**Недостатки:**

1. **Complexity** — множество мелких классов усложняют код для простых задач
2. **Performance** — рекурсивная интерпретация и большое количество объектов могут быть неэффективны
3. **Grammar Changes** — изменения грамматики требуют модификаций многих классов
4. **Not for Large Grammars** — плохо масштабируется для больших и сложных языков

**Ключевые концепции:**

1. **Abstract Syntax Tree** — часто используется для представления выражений, но не является строго обязательным
2. **Terminal vs Non-terminal** — базовые (листья) и составные выражения
3. **Recursive Evaluation** — вычисление/интерпретация выполняется рекурсивно по структуре выражений
4. **Grammar as Classes** — грамматика представлена иерархией классов
5. **Compositional Structure** — выражения композиционно собираются в более сложные конструкции

## Answer (EN)

**Interpreter Pattern Theory:**
Interpreter is a behavioral design pattern for interpreting sentences in a language. It addresses the problem of defining a simple grammar so that expressions can be interpreted programmatically. The solution is to represent elements of the grammar as a set of classes, where each class corresponds to a rule or expression type. Typically (but not strictly required) an Abstract Syntax Tree (AST) is built from these objects to interpret complex expressions.

**Definition:**

*Theory:* The Interpreter pattern defines a representation of a language's grammar using a hierarchy of expression classes and specifies a common `interpret`/`evaluate` operation to interpret expressions built according to this grammar. Each rule or terminal/non-terminal expression is modeled as a separate class. Composing these objects forms a structure (often an AST) that is evaluated recursively.

Note: In the classic GoF formulation the language is assumed to be simple enough that the grammar can be mapped directly to the class hierarchy. Building an AST and having a separate parsing phase is a common implementation approach, but not mandated by the pattern definition.

**Problems Solved:**

*Theory:*
- When you need to define a simple domain-specific language (DSL) with a relatively stable grammar.
- When recurring problems can be expressed as sentences in such a language.
- When you need a flexible way to specify and combine expressions instead of hard-coding logic with if/switch chains.

Examples: search filters, simple query languages, regular-expression-like mini-languages (conceptually), calculators, small configuration languages.

```kotlin
// ✅ Simplified example: expression interpretation over string context
interface Expression {
    fun interpret(context: String): Boolean
}

// Terminal expression - basic expression
class TerminalExpression(private val data: String) : Expression {
    override fun interpret(context: String): Boolean {
        // Simplified logic for demonstration; real interpreters
        // typically operate on tokens/structured input, not raw contains.
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

    println(isMale.interpret("John"))            // true
    println(isMarriedWoman.interpret("Married Julie"))  // true
}
```

**Real Example: Expression Calculator:**

*Theory:* Interpreter can be used to represent and evaluate mathematical expressions. Expression classes encapsulate operations and recursively compute results. In a full implementation, a parser would convert an input string into an expression tree (AST); here, we focus on the interpretation side and construct the tree manually for clarity.

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

// Usage: expression "3 + 4 * 5"
fun main() {
    val expression: Expression = AddExpression(
        NumberExpression(3),
        MultiplyExpression(NumberExpression(4), NumberExpression(5))
    )
    println(expression.evaluate())  // 23
}
```

Here the expression tree is created manually for brevity; a typical Interpreter-based calculator would also include a parsing step that builds this structure from input.

**When to Use:**

*Theory:* Use Interpreter when:
- You need to evaluate/interpret many expressions defined by a fixed, relatively simple grammar.
- Complex expressions can be naturally decomposed into smaller expression objects.
- You require extensibility by introducing new expression types.
- The language is simple enough that a class-per-rule approach is feasible.

Don't use it when:
- The grammar is very large or complex (too many classes, poor scalability).
- The problem is simple and doesn't justify introducing a language (over-engineering).
- The grammar changes frequently (high maintenance cost).
- You need very high performance on large expression trees.

✅ **Use Interpreter when:**
- Need to evaluate/interpret expressions following a simple, well-defined grammar
- Complex expressions can be broken down and represented as composable objects
- Grammar is relatively simple and stable
- Need flexibility in defining and combining expressions

❌ **Don't use Interpreter when:**
- Very large or complex grammar (performance/maintainability issues)
- Trivial use cases (over-engineering)
- Frequently changing grammar (maintenance burden)
- Need high performance for huge expression trees

**Implementation:**

*Theory:* Implementation steps:
1. Define an `Expression` interface/abstract class declaring `interpret`/`evaluate`.
2. For each grammar rule, create a concrete `Expression` class (Terminal / Non-terminal).
3. Let the client build expressions (typically a tree) from these objects and call `interpret`/`evaluate` on the root.
4. (Often) Add a parser that converts textual input into `Expression` objects.

**Advantages:**

1. **Extensibility** - easy to add new expression types by adding new classes
2. **Maintainability** - logic for different language constructs is separated into individual classes
3. **Readability** - language structure is explicit in the code
4. **Separation of Concerns** - grammar and interpretation logic are encapsulated; parsing can be handled separately

**Disadvantages:**

1. **Complexity** - many small classes can overcomplicate simple scenarios
2. **Performance** - recursive evaluation and many objects can be inefficient for large trees
3. **Grammar Changes** - changes in grammar may require updating many classes
4. **Not for Large Grammars** - does not scale well for industrial-strength languages

**Key Concepts:**

1. **Abstract Syntax Tree** - commonly used to represent expressions, though not strictly required
2. **Terminal vs Non-terminal** - basic (leaf) vs composite expressions
3. **Recursive Evaluation** - expressions evaluated recursively via the structure
4. **Grammar as Classes** - grammar represented as a class hierarchy
5. **Compositional Structure** - expressions composed hierarchically into complex constructs

---

## Дополнительные Вопросы (RU)

- Как паттерн Interpreter соотносится с паттерном Composite (см. также [[c-architecture-patterns]])?
- В чем разница между паттернами Interpreter и Visitor?
- В каких случаях стоит использовать генератор парсеров вместо паттерна Interpreter?

## Follow-ups

- How does Interpreter pattern relate to Composite pattern (see also [[c-architecture-patterns]])?
- What is the difference between Interpreter and Visitor pattern?
- When would you use a parser generator instead of Interpreter?

## Связанные Вопросы (RU)

### Предпосылки (проще)
- Базовые знания паттернов проектирования
- Понимание деревьев

### Связанные (того Же уровня)
- Паттерн Composite (похожая структура)
- Паттерн Visitor (альтернативный подход)

### Продвинутые (сложнее)
- Паттерн Flyweight (оптимизационные техники)
- Генераторы парсеров vs паттерн Interpreter

## Related Questions

### Prerequisites (Easier)
- Basic design patterns concepts
- Tree structures understanding

### Related (Same Level)
- Composite pattern (similar structure)
- Visitor pattern (alternative approach)

### Advanced (Harder)
- Flyweight pattern (optimization techniques)
- Parser generators vs Interpreter pattern

## Ссылки (RU)

- [[c-architecture-patterns]]
- [[c-software-design-patterns]]
- "Design Patterns: Elements of Reusable Object-Oriented Software" (Gamma и др.)
- [Refactoring Guru — Interpreter Pattern](https://refactoring.guru/design-patterns/interpreter)

## References

- [[c-architecture-patterns]]
- [[c-software-design-patterns]]
- "Design Patterns: Elements of Reusable Object-Oriented Software" (Gamma et al.)
- [Refactoring Guru — Interpreter Pattern](https://refactoring.guru/design-patterns/interpreter)
