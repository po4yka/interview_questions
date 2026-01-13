---
---
---\
id: kotlin-020
title: "Infix Functions / Инфиксные функции"
aliases: ["Infix Functions", "Инфиксные функции"]

# Classification
topic: kotlin
subtopics: [functions, infix]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: "https://github.com/Kirchhoff-/Android-Interview-Questions"
source_note: Kirchhoff Android Interview Questions repository - Kotlin Batch 2

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-kotlin, q-kotlin-dsl-creation--kotlin--hard, q-kotlin-extension-functions--kotlin--medium, q-kotlin-operator-overloading--kotlin--medium]

# Timestamps
created: 2025-10-05
updated: 2025-11-09

tags: [difficulty/medium, functions, infix, kotlin, operators, syntax]
---\
# Вопрос (RU)
> Что такое инфиксные функции в Kotlin?

# Question (EN)
> What are infix functions in Kotlin?

## Ответ (RU)

Инфиксные функции позволяют вызывать функции без точки и скобок между приёмником и единственным аргументом, что делает код похожим на естественный язык. См. также [[c-kotlin]].

### Требования

Должны удовлетворять ВСЕМ из них:
- Должна быть **функцией-членом** или **функцией-расширением**
- Должна иметь ровно **один параметр**
- Параметр **не должен принимать переменное количество аргументов** (нет `vararg`)
- Параметр **не должен иметь значения по умолчанию**

### Синтаксис

```kotlin
infix fun Int.shl(x: Int): Int { /*...*/ }

// Вызов с инфиксной нотацией
1 shl 2

// То же что и обычный вызов
1.shl(2)
```

### Частые Примеры

#### 1. Создание Пар С `to`

```kotlin
val pair1 = 1 to "apple"   // Инфиксный вызов
val pair2 = 1.to("apple")  // Обычный вызов
```

#### 2. Побитовые Операции

```kotlin
val color = 0x123456
val red = (color and 0xff0000) shr 16
val green = (color and 0x00ff00) shr 8
val blue = color and 0x0000ff
```

#### 3. Булевы / Битовые Операции С Инфиксными Функциями

```kotlin
if ((targetUser.isEnabled and !targetUser.isBlocked) or currentUser.isAdmin) {
    // Действие
}
```

Здесь используются инфиксные функции `and` и `or` (как функции для `Boolean`/`Int`), а не логические операторы `&&` и `||`.

#### 4. Сопоставление Строк (regex)

```kotlin
val matches = "Hello, World" matches "^Hello".toRegex()  // Инфиксный вызов
```

### Важные Правила

#### Вызовы Внутри Класса

```kotlin
class MyStringCollection {
    private val list = mutableListOf<String>()

    infix fun add(s: String) { list.add(s) }

    fun build() {
        this add "abc"   // Корректно: инфиксный вызов с явным this
        add("abc")       // Корректно: обычный вызов
        add "abc"        // Корректно: инфиксный вызов без явного this
    }
}
```

Инфиксный вызов требует явного приёмника только когда без него возникает неоднозначность.

#### Приоритет Операций

Инфиксные вызовы имеют **меньший приоритет**, чем:
- Арифметические операторы (`+`, `-`, `*`, `/`, `%`)
- Приведения типов (`as`, `as?`)
- Оператор диапазона `..`

```kotlin
1 shl 2 + 3      // То же, что 1 shl (2 + 3)
0 until n * 2    // То же, что 0 until (n * 2)
```

Инфиксные вызовы имеют **больший приоритет**, чем:
- Логические операторы (`&&`, `||`)
- Проверки `is` и `in`

```kotlin
a && b xor c   // То же, что a && (b xor c)
a xor b in c   // То же, что (a xor b) in c
```

### Пользовательские Инфиксные Функции

```kotlin
data class Point(val x: Double, val y: Double)

infix fun Point.distanceTo(other: Point): Double {
    val dx = this.x - other.x
    val dy = this.y - other.y
    return Math.sqrt(dx * dx + dy * dy)
}

// Использование
val p1 = Point(0.0, 0.0)
val p2 = Point(3.0, 4.0)
val distance = p1 distanceTo p2  // 5.0
```

**Краткое содержание**: Инфиксные функции позволяют вызывать функции без точки и скобок для более читаемого кода. Должны быть функциями-членами/расширениями с ровно одним параметром без `vararg` и значения по умолчанию. Частые примеры: `to` для пар, побитовые операторы (`and`, `or`, `shl`), `matches` для regex. Имеют специфические правила приоритета относительно других операторов.

## Answer (EN)

Infix functions allow calling functions without dots and parentheses between the receiver and the single argument, resulting in code that looks more like natural language.

### Requirements

Must satisfy ALL of these:
- Must be a **member function** or an **extension function**
- Must have exactly **one parameter**
- Parameter must **not accept a variable number of arguments** (no `vararg`)
- Parameter must **not have a default value**

### Syntax

```kotlin
infix fun Int.shl(x: Int): Int { /*...*/ }

// Calling with infix notation
1 shl 2

// Same as regular call
1.shl(2)
```

### Common Examples

#### 1. Creating Pairs with `to`

```kotlin
val pair1 = 1 to "apple"   // Infix call
val pair2 = 1.to("apple")  // Regular call
```

#### 2. Bitwise Operations

```kotlin
val color = 0x123456
val red = (color and 0xff0000) shr 16
val green = (color and 0x00ff00) shr 8
val blue = color and 0x0000ff
```

#### 3. Boolean / Bitwise Operations Using Infix Functions

```kotlin
if ((targetUser.isEnabled and !targetUser.isBlocked) or currentUser.isAdmin) {
    // Do something
}
```

Here `and` and `or` are infix functions (on `Boolean`/`Int`), not the short-circuit operators `&&` and `||`.

#### 4. String Matching

```kotlin
val matches = "Hello, World" matches "^Hello".toRegex()  // Infix call
```

### Important Rules

#### Calls Inside a Class

```kotlin
class MyStringCollection {
    private val list = mutableListOf<String>()

    infix fun add(s: String) { list.add(s) }

    fun build() {
        this add "abc"   // Correct: infix call with explicit this
        add("abc")       // Correct: regular call
        add "abc"        // Correct: infix call without explicit this
    }
}
```

An infix call requires an explicit receiver only when omitting it would make the call ambiguous.

#### Precedence Rules

Infix calls have **lower precedence** than:
- Arithmetic operators (`+`, `-`, `*`, `/`, `%`)
- Type casts (`as`, `as?`)
- `rangeTo` operator (`..`)

```kotlin
1 shl 2 + 3      // Same as: 1 shl (2 + 3)
0 until n * 2    // Same as: 0 until (n * 2)
```

Infix calls have **higher precedence** than:
- `Boolean` operators (`&&`, `||`)
- `is` and `in` checks

```kotlin
a && b xor c   // Same as: a && (b xor c)
a xor b in c   // Same as: (a xor b) in c
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

**English Summary**: Infix functions allow calling functions without dots and parentheses for more readable code. They must be member/extension functions with exactly one parameter, without `vararg` or a default value. Common examples: `to` for pairs, bitwise operators (`and`, `or`, `shl`), `matches` for regex. They have specific precedence rules relative to other operators.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [Functions - Kotlin Documentation](https://kotlinlang.org/docs/reference/functions.html)

## Related Questions

### Prerequisites (Easier)
- [[q-equality-operators-kotlin--kotlin--easy]] - Equality
### Related (Medium)
- [[q-kotlin-extension-functions--kotlin--medium]] - Extensions
- [[q-instant-search-flow-operators--kotlin--medium]] - `Flow`
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-kotlin-operator-overloading--kotlin--medium]] - Operators
### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flow-operators-deep-dive--kotlin--hard]] - `Flow`
