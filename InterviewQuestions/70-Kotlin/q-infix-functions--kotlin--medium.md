---
id: 20251005-235012
title: "Infix Functions / Инфиксные функции"
aliases: []

# Classification
topic: kotlin
subtopics: [infix, functions, syntax, operators]
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
related: [q-kotlin-operator-overloading--kotlin--medium, q-kotlin-extension-functions--kotlin--medium, q-kotlin-dsl-creation--kotlin--hard]

# Timestamps
created: 2025-10-05
updated: 2025-10-18

tags: [kotlin, infix, functions, syntax, operators, difficulty/medium]
---
# Question (EN)
> What are infix functions in Kotlin?
# Вопрос (RU)
> Что такое инфиксные функции в Kotlin?

---

## Answer (EN)

Infix functions can be called without using the period and brackets, resulting in code that looks more like natural language.

### Requirements

Must satisfy ALL of these:
- Must be **member function** or **extension function**
- Must have exactly **one parameter**
- Parameter must **not accept variable number of arguments** (no `vararg`)
- Parameter must have **no default value**

### Syntax

```kotlin
infix fun Int.shl(x: Int): Int { ... }

// Calling with infix notation
1 shl 2

// Same as regular call
1.shl(2)
```

### Common Examples

#### 1. Creating Pairs with `to`

```kotlin
val pair = 1 to "apple"  // Infix
val pair = 1.to("apple")  // Regular
```

#### 2. Bitwise Operations

```kotlin
val color = 0x123456
val red = (color and 0xff0000) shr 16  // Infix
val green = (color and 0x00ff00) shr 8
val blue = (color and 0x0000ff) shr 0
```

#### 3. Boolean Operations

```kotlin
if ((targetUser.isEnabled and !targetUser.isBlocked) or currentUser.admin) {
    // Do something
}
```

#### 4. String Matching

```kotlin
"Hello, World" matches "^Hello".toRegex()  // Infix
```

### Important Rules

#### Must use `this` explicitly

```kotlin
class MyStringCollection {
    infix fun add(s: String) { /*...*/ }

    fun build() {
        this add "abc"   // - Correct
        add("abc")       // - Correct
        // add "abc"     // - Incorrect: receiver must be specified
    }
}
```

#### Precedence Rules

Infix calls have **lower precedence** than:
- Arithmetic operators (+, -, *, /, %)
- Type casts
- `rangeTo` operator (..)

```kotlin
1 shl 2 + 3  // Same as: 1 shl (2 + 3)
0 until n * 2  // Same as: 0 until (n * 2)
```

Infix calls have **higher precedence** than:
- Boolean operators (&&, ||)
- `is` and `in` checks

```kotlin
a && b xor c  // Same as: a && (b xor c)
a xor b in c  // Same as: (a xor b) in c
```

### Custom Infix Functions

```kotlin
data class Point(val x: Double, val y: Double)

infix fun Point.distanceTo(other: Point): Double {
    val dx = this.x - other.x
    val dy = this.y - other.y
    return Math.sqrt(dx * dx + dy * dy)
}

// Usage
val p1 = Point(0.0, 0.0)
val p2 = Point(3.0, 4.0)
val distance = p1 distanceTo p2  // 5.0
```

**English Summary**: Infix functions allow calling functions without dots and parentheses for more readable code. Must be member/extension functions with exactly one parameter. Common examples: `to` for pairs, bitwise operators (`and`, `or`, `shl`), `matches` for regex. Have specific precedence rules relative to other operators.

## Ответ (RU)

Инфиксные функции можно вызывать без точки и скобок, что делает код похожим на естественный язык.

### Требования

Должны удовлетворять ВСЕМ из них:
- Должна быть **функцией-членом** или **функцией-расширением**
- Должна иметь ровно **один параметр**
- Параметр **не должен принимать переменное количество аргументов** (нет `vararg`)
- Параметр должен **не иметь значения по умолчанию**

### Синтаксис

```kotlin
infix fun Int.shl(x: Int): Int { ... }

// Вызов с инфиксной нотацией
1 shl 2

// То же что и обычный вызов
1.shl(2)
```

### Частые примеры

#### 1. Создание пар с `to`

```kotlin
val pair = 1 to "apple"  // Инфиксный
val pair = 1.to("apple")  // Обычный
```

#### 2. Побитовые операции

```kotlin
val color = 0x123456
val red = (color and 0xff0000) shr 16
```

#### 3. Булевы операции

```kotlin
if ((targetUser.isEnabled and !targetUser.isBlocked) or currentUser.admin) {
    // Действие
}
```

**Краткое содержание**: Инфиксные функции позволяют вызывать функции без точек и скобок для более читаемого кода. Должны быть функциями-членами/расширениями с ровно одним параметром. Частые примеры: `to` для пар, побитовые операторы, `matches` для regex. Имеют специфические правила приоритета.

---

## References
- [Functions - Kotlin Documentation](https://kotlinlang.org/docs/reference/functions.html)

## Related Questions

### Prerequisites (Easier)
- [[q-equality-operators-kotlin--kotlin--easy]] - Equality
### Related (Medium)
- [[q-kotlin-extension-functions--kotlin--medium]] - Extensions
- [[q-instant-search-flow-operators--kotlin--medium]] - Flow
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-kotlin-operator-overloading--kotlin--medium]] - Operators
### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flow-operators-deep-dive--kotlin--hard]] - Flow
