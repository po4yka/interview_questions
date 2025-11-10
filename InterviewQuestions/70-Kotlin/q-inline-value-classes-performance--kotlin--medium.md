---
id: kotlin-145
title: "Inline Value Classes Performance / Производительность value-классов"
aliases: [Classes, Inline, Performance, Value]
topic: kotlin
subtopics: [delegation, null-safety, object-comparison]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-expect-actual-kotlin--kotlin--medium, q-kotlin-static-variable--programming-languages--easy]
created: 2025-10-15
updated: 2025-11-09
tags: [difficulty/medium]
---
# Inline Value Classes and Performance

# Вопрос (RU)
> Как работают inline value классы? Когда следует использовать их для производительности? Каковы ограничения?

---

# Question (EN)
> How do inline value classes work? When should you use them for performance? What are the limitations?

## Ответ (RU)

**Value классы** (`value class`, ранее "inline classes") — это легковесные обертки, которые добавляют безопасность типов. В большинстве случаев компилятор может представлять их как их базовый тип (примитив или ссылочный), избегая дополнительных аллокаций по сравнению с обычными обертками.

---

### Базовый пример value-класса

```kotlin
@JvmInline
value class UserId(val value: Int)

@JvmInline
value class Email(val value: String)

fun sendEmail(userId: UserId, email: Email) {
    // Типобезопасно!
}

// На местах вызова представление обычно сводится к Int и String,
// без отдельных wrapper-объектов, когда оптимизатор может это сделать.
```

---

### Преимущество производительности (типичный случай)

Без value-класса:

```kotlin
data class UserId(val value: Int) // Обычный класс

fun process(id: UserId) {
    println(id.value)
}

// Каждый вызов обычно приводит к аллокации UserId на heap:
process(UserId(123))
```

С value-классом:

```kotlin
@JvmInline
value class UserId(val value: Int)

fun process(id: UserId) {
    println(id.value)
}

// Во многих случаях вызов компилируется так, что используется только Int без
// дополнительной обертки, но в ряде контекстов все еще возможен boxing.
process(UserId(123))
```

---

### Когда использовать (c акцентом на производительность)

Используйте value-классы, когда:

- Нужны типобезопасные примитивы / доменные типы (например, метры, секунды), чтобы избежать путаницы единиц.

```kotlin
@JvmInline
value class Meters(val value: Double)

@JvmInline
value class Seconds(val value: Double)

fun calculateSpeed(distance: Meters, time: Seconds): Double {
    return distance.value / time.value
}

// Нельзя перепутать единицы:
// calculateSpeed(Seconds(10), Meters(100)) // Ошибка компиляции
```

- Нужны обертки для API-ключей, ID, токенов, чтобы избежать случайной подстановки строк друг вместо друга.

```kotlin
@JvmInline
value class ApiKey(val value: String)

@JvmInline
value class SessionToken(val value: String)

fun authenticate(apiKey: ApiKey, token: SessionToken) {
    // Нельзя случайно передать token туда, где ожидается ApiKey
}
```

- Эти типы часто участвуют в вызовах/передаче параметров, и важно избежать лишних аллокаций.
- Не требуется идентичность объекта или сложное внутреннее состояние — достаточно представления через одно значение.

---

### Ограничения и важные нюансы

**1. Ровно одно свойство:**

```kotlin
// Корректно
@JvmInline
value class Name(val value: String)

// Некорректно: value-класс должен иметь ровно одно базовое свойство
@JvmInline
value class Person(val name: String, val age: Int)
```

**2. Нет идентичности объекта (только равенство по значению):**

```kotlin
val id1 = UserId(123)
val id2 = UserId(123)

// Сравнение по ссылке здесь не имеет смысла
// id1 === id2 // не то, что нужно
id1 == id2 // Сравнение по значению
```

**3. Boxing-сценарии (могут приводить к аллокациям):**

```kotlin
@JvmInline
value class UserId(val value: Int)

// Boxing как generic:
val list: List<UserId> = listOf(UserId(1))

// Boxing для nullable:
val nullable: UserId? = null

// Boxing при использовании как Any:
val any: Any = UserId(1)
```

В этих случаях value-класс фактически упаковывается, и выигрыш по памяти/GC снижается.

**4. Другие ограничения:**

- Нельзя быть `open`, `inner`, `abstract`; нет наследования от классов (только реализации интерфейсов).
- Базовое свойство фактически `val`: внутри нельзя иметь изменяемое состояние, как в обычных классах.
- Сгенерированное поведение (`equals`, `hashCode`, `toString`) должно соответствовать базовому значению.

При соблюдении этих условий value-классы дают усиленную type-safety и потенциальную выгоду по производительности без лишних аллокаций в hot-путях.

## Answer (EN)

**Value classes** (`value class`, previously called "inline classes") are lightweight wrappers that provide type safety. In many cases, the compiler represents them as their underlying type (primitive or reference), which avoids extra object allocations compared to regular wrapper classes.

---

### Basic Value Class

```kotlin
@JvmInline
value class UserId(val value: Int)

@JvmInline
value class Email(val value: String)

fun sendEmail(userId: UserId, email: Email) {
    // Type-safe!
}

// At call sites, the representation is typically just Int and String,
// not separate wrapper objects, where the optimizer can apply this.
```

---

### Performance Benefit (Typical Case)

Without a value class:

```kotlin
data class UserId(val value: Int) // Regular class

fun process(id: UserId) {
    println(id.value)
}

// Every call generally allocates a UserId instance:
process(UserId(123)) // Heap allocation
```

With a value class:

```kotlin
@JvmInline
value class UserId(val value: Int)

fun process(id: UserId) {
    println(id.value)
}

// In many cases the call can be compiled to just work with Int (no extra wrapper),
// but boxing may still occur in some contexts.
process(UserId(123))
```

---

### When to Use

- Type-safe primitives / domain-specific types:

```kotlin
@JvmInline
value class Meters(val value: Double)

@JvmInline
value class Seconds(val value: Double)

fun calculateSpeed(distance: Meters, time: Seconds): Double {
    return distance.value / time.value
}

// Cannot mix up units:
// calculateSpeed(Seconds(10), Meters(100)) // Compile-time error
```

- API keys, IDs, tokens:

```kotlin
@JvmInline
value class ApiKey(val value: String)

@JvmInline
value class SessionToken(val value: String)

fun authenticate(apiKey: ApiKey, token: SessionToken) {
    // Cannot accidentally pass token where ApiKey is expected
}
```

Use them when:
- you want stronger type safety over primitives/strings,
- you call such APIs frequently enough that avoiding wrapper allocations matters,
- you do not need object identity or complex state.

---

### Limitations

**1. Single property:**

```kotlin
// Valid
@JvmInline
value class Name(val value: String)

// Invalid: value classes must have exactly one underlying property
@JvmInline
value class Person(val name: String, val age: Int)
```

**2. No identity:**

```kotlin
val id1 = UserId(123)
val id2 = UserId(123)

// Reference identity is not meaningful here
// id1 === id2 // Not the intended comparison
id1 == id2 // Value equality
```

**3. Boxing scenarios (may allocate):**

```kotlin
@JvmInline
value class UserId(val value: Int)

// Boxed as generic:
val list: List<UserId> = listOf(UserId(1))

// Boxed when nullable:
val nullable: UserId? = null

// Boxed when used as Any:
val any: Any = UserId(1)
```

**4. Other constraints:**

- Cannot be `open`, `inner`, `abstract`; no subclassing (but may implement interfaces).
- Underlying property is effectively `val`; no mutable state like regular classes.
- Some generated methods (e.g., `equals`, `hashCode`, `toString`) are constrained by representation; behavior should match the underlying value.

---

## Дополнительные вопросы (RU)

- В чем ключевые отличия value-классов от аналогичных подходов в Java?
- Когда вы бы использовали value-классы на практике?
- Какие типичные подводные камни при их использовании?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [[c-kotlin]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## Связанные вопросы (RU)

- [[q-expect-actual-kotlin--kotlin--medium]]
- [[q-kotlin-static-variable--programming-languages--easy]]

## Related Questions

- [[q-expect-actual-kotlin--kotlin--medium]]
- [[q-kotlin-static-variable--programming-languages--easy]]
