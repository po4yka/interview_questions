---
id: kotlin-021
title: "Type Aliases in Kotlin / Псевдонимы типов в Kotlin"
aliases: ["Type Aliases in Kotlin, Псевдонимы типов в Kotlin"]

# Classification
topic: kotlin
subtopics: [dsl, readability, type-aliases]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/Kirchhoff-/Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository - Kotlin Batch 2

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-inline-classes-value-classes--kotlin--medium, q-kotlin-generics--kotlin--hard, q-kotlin-type-system--kotlin--medium]

# Timestamps
created: 2025-10-05
updated: 2025-10-18

tags: [difficulty/medium, dsl, kotlin, readability, type-aliases, types]
---
# Вопрос (RU)
> Что такое псевдонимы типов (type aliases) в Kotlin и когда их использовать?

---

# Question (EN)
> What are type aliases in Kotlin and when should you use them?
## Ответ (RU)

Псевдонимы типов (type aliases) предоставляют альтернативные имена для существующих типов. Если имя типа слишком длинное, можно ввести другое, более короткое имя и использовать его.

### Базовый Синтаксис

```kotlin
typealias NodeSet = Set<Network.Node>
typealias FileTable<K> = MutableMap<K, MutableList<File>>
```

### Частые Случаи Использования

#### 1. Сокращение Длинных Обобщенных Типов

```kotlin
// До
val userCache: MutableMap<String, MutableList<User>> = mutableMapOf()

// После
typealias UserCache = MutableMap<String, MutableList<User>>
val userCache: UserCache = mutableMapOf()
```

#### 2. Псевдонимы Функциональных Типов

```kotlin
typealias MyHandler = (Int, String, Any) -> Unit
typealias Predicate<T> = (T) -> Boolean
typealias ClickListener = (View) -> Unit
```

#### 3. Семантические Имена Типов

```kotlin
typealias UserId = String
typealias ProductId = Int
typealias Email = String

fun fetchUserProfile(userId: UserId): UserProfile {
    // Понятнее чем просто String
}
```

### Важно: Псевдонимы Не Создают Новые Типы

Псевдонимы типов **не являются новыми типами** - они эквивалентны соответствующим базовым типам. Компилятор всегда разворачивает их в исходный тип.

```kotlin
typealias Predicate<T> = (T) -> Boolean

fun foo(p: Predicate<Int>) = p(42)

fun main() {
    // Можно передать обычный функциональный тип
    val f: (Int) -> Boolean = { it > 0 }
    println(foo(f)) // Работает!

    // Можно передать псевдоним типа
    val p: Predicate<Int> = { it > 0 }
    println(listOf(1, -2).filter(p)) // Работает!
}
```

### Почему Использовать Псевдонимы Типов?

1. **Улучшенная читаемость** - Делает код понятнее с осмысленными именами
2. **Абстракция и инкапсуляция** - Может абстрагировать детали реализации
3. **Переиспользуемость кода** - Последовательный способ представления концепций
4. **Создание DSL** - Помогает создавать предметно-ориентированные языки

### Ограничения Псевдонимов Типов

1. **Не создают новые типы** - Это просто альтернативные имена
2. **Нет усиленной типобезопасности** - Любая строка может быть присвоена `typealias Email = String`
3. **Одинаковое восприятие компилятором** - Компилятор интерпретирует их как исходные типы

```kotlin
// Пример ограничения
typealias Email = String
typealias PhoneNumber = String

val email: Email = "user@example.com"
val phone: PhoneNumber = email  // - Компилируется! Нет типобезопасности

// Для реальной типобезопасности используйте value классы:
@JvmInline
value class Email(val value: String)
@JvmInline
value class PhoneNumber(val value: String)

val email2 = Email("user@example.com")
val phone2: PhoneNumber = email2  // - Ошибка компиляции! Реальная типобезопасность
```

**Краткое содержание**: Псевдонимы типов предоставляют альтернативные имена для существующих типов, улучшая читаемость кода без создания новых типов. Полезны для сокращения длинных обобщенных типов, именования функциональных типов и создания DSL. Однако не обеспечивают типобезопасность - для этого используйте value классы.

---

## Answer (EN)

Type aliases provide alternative names for existing types. If the type name is too long, you can introduce a different shorter name and use the new one instead.

### Basic Syntax

```kotlin
typealias NodeSet = Set<Network.Node>
typealias FileTable<K> = MutableMap<K, MutableList<File>>
```

### Common Use Cases

#### 1. Shortening Long Generic Types

```kotlin
// Before
val userCache: MutableMap<String, MutableList<User>> = mutableMapOf()

// After
typealias UserCache = MutableMap<String, MutableList<User>>
val userCache: UserCache = mutableMapOf()
```

#### 2. Function Type Aliases

```kotlin
typealias MyHandler = (Int, String, Any) -> Unit
typealias Predicate<T> = (T) -> Boolean
typealias ClickListener = (View) -> Unit

// Usage
fun setOnClickListener(listener: ClickListener) {
    // ...
}
```

#### 3. Inner and Nested Classes

```kotlin
class A {
    inner class Inner
}

class B {
    inner class Inner
}

typealias AInner = A.Inner
typealias BInner = B.Inner
```

### Important: Type Aliases Don't Create New Types

Type aliases are **not new types** - they are equivalent to the corresponding underlying types. The compiler always expands them to the original type.

```kotlin
typealias Predicate<T> = (T) -> Boolean

fun foo(p: Predicate<Int>) = p(42)

fun main() {
    // Can pass regular function type
    val f: (Int) -> Boolean = { it > 0 }
    println(foo(f)) // Works! Prints "true"

    // Can pass type alias
    val p: Predicate<Int> = { it > 0 }
    println(listOf(1, -2).filter(p)) // Works! Prints "[1]"
}
```

### Why Use Type Aliases?

1. **Improved Readability** - Makes code more understandable by giving meaningful names to complex types
2. **Abstraction and Encapsulation** - Can abstract implementation details
3. **Code Reusability** - Provides consistent way to represent concepts
4. **DSL Creation** - Helps create domain-specific languages

### Examples

#### Example 1: Enhancing Function Signatures

```kotlin
// Without type alias
fun distance(p1: Pair<Double, Double>, p2: Pair<Double, Double>): Double {
    val dx = p1.first - p2.first
    val dy = p1.second - p2.second
    return Math.sqrt(dx * dx + dy * dy)
}

// With type alias - more descriptive
typealias Point = Pair<Double, Double>

fun distance(p1: Point, p2: Point): Double {
    val dx = p1.first - p2.first
    val dy = p1.second - p2.second
    return Math.sqrt(dx * dx + dy * dy)
}

// Usage is clearer
val p1: Point = 3.0 to 4.0
val p2: Point = 6.0 to 8.0
val dist = distance(p1, p2)
```

#### Example 2: Creating DSL-like Syntax

```kotlin
typealias Tag = StringBuilder.() -> Unit

fun html(block: Tag): String {
    val sb = StringBuilder()
    sb.append("<html>")
    sb.block()
    sb.append("</html>")
    return sb.toString()
}

fun Tag.head(block: Tag) {
    append("<head>")
    block()
    append("</head>")
}

fun Tag.body(block: Tag) {
    append("<body>")
    block()
    append("</body>")
}

fun Tag.p(content: String) {
    append("<p>$content</p>")
}

// Usage
val page = html {
    head {
        p("Type Aliases in Kotlin")
    }
    body {
        p("Learn about type aliases.")
    }
}
```

#### Example 3: Semantic Type Names

```kotlin
typealias UserId = String
typealias ProductId = Int
typealias Email = String

fun fetchUserProfile(userId: UserId): UserProfile {
    // More clear than just using String
}

fun validateEmail(email: Email): Boolean {
    // Intent is clearer than using String
}
```

### Limitations of Type Aliases

1. **Don't Create New Types** - They're just alternative names for existing types
2. **No Enhanced Type Safety** - Any string can be assigned to `typealias Email = String`
3. **Same Compiler Perception** - Compiler treats them as their original types

```kotlin
// Example of limitation
typealias Email = String
typealias PhoneNumber = String

val email: Email = "user@example.com"
val phone: PhoneNumber = email  // - Compiles! No type safety

// If you need real type safety, use value classes:
@JvmInline
value class Email(val value: String)
@JvmInline
value class PhoneNumber(val value: String)

val email2 = Email("user@example.com")
val phone2: PhoneNumber = email2  // - Compilation error! Real type safety
```

### Best Practices

1. **Use for readability** - When type names are too long or cryptic
2. **Use for domain modeling** - `UserId`, `ProductId`, etc.
3. **Use for function types** - Makes callback signatures clearer
4. **Don't overuse** - Only when it genuinely improves code clarity
5. **Consider value classes** - If you need actual type safety, use value classes instead

**English Summary**: Type aliases provide alternative names for existing types, improving code readability without creating new types. They're useful for shortening long generic types, naming function types, and creating DSLs. However, they don't provide type safety - for that, use value classes. The compiler always expands type aliases to their underlying types.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [Type Aliases - Kotlin Documentation](https://kotlinlang.org/docs/type-aliases.html)
- [All About Type Aliases](https://typealias.com/guides/all-about-type-aliases/)

## Related Questions
- [[q-kotlin-generics--kotlin--hard]]
- [[q-kotlin-sam-interfaces--kotlin--medium]]
