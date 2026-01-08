---id: kotlin-145
title: "Inline Value Classes Performance / Производительность value-классов"
aliases: [Classes, Inline, Performance, Value]
topic: kotlin
subtopics: [object-comparison]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, c-value-classes, q-expect-actual-kotlin--kotlin--medium]
created: 2024-10-15
updated: 2025-11-11
tags: [difficulty/medium]
---
# Вопрос (RU)
> Как работают inline value классы? Когда следует использовать их для производительности? Каковы ограничения?

---

# Question (EN)
> How do inline value classes work? When should you use them for performance? What are the limitations?

## Ответ (RU)

**Value классы** (`value class`, ранее "inline classes") — это легковесные обертки, которые добавляют безопасность типов. В большинстве случаев компилятор может представлять их как их базовый тип (примитив или ссылочный), избегая дополнительных аллокаций по сравнению с обычными обертками, когда это возможно. Однако это оптимизация реализации, а не жесткая гарантия для всех контекстов: на производительность нужно смотреть эмпирически.

---

### Базовый Пример Value-класса

```kotlin
@JvmInline
value class UserId(val value: Int)

@JvmInline
value class Email(val value: String)

fun sendEmail(userId: UserId, email: Email) {
    // Типобезопасно!
}

// На местах вызова представление обычно может сводиться к Int и String
// без отдельных wrapper-объектов, когда backend/JIT может это оптимизировать.
```

---

### Преимущество Производительности (типичный случай)

Без value-класса:

```kotlin
data class UserId(val value: Int) // Обычный класс

fun process(id: UserId) {
    println(id.value)
}

// Каждый вызов обычно приводит к созданию экземпляра UserId в heap:
process(UserId(123))
```

С value-классом:

```kotlin
@JvmInline
value class UserId(val value: Int)

fun process(id: UserId) {
    println(id.value)
}

// Во многих случаях вызов может быть скомпилирован так, что используется только Int без
// дополнительной обертки. Но в ряде контекстов (generics, nullable, Any и др.)
// все еще возможен boxing и аллокации.
process(UserId(123))
```

---

### Когда Использовать (c Акцентом На производительность)

Используйте value-классы в первую очередь для:

- Типобезопасных примитивов / доменных типов (например, метры, секунды), чтобы избежать путаницы единиц.

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

- Оберток для API-ключей, ID, токенов, чтобы избежать случайной подстановки строк друг вместо друга.

```kotlin
@JvmInline
value class ApiKey(val value: String)

@JvmInline
value class SessionToken(val value: String)

fun authenticate(apiKey: ApiKey, token: SessionToken) {
    // Нельзя случайно передать token туда, где ожидается ApiKey
}
```

- Сценариев, где такие типы часто участвуют в вызовах/передаче параметров, и важно уменьшить количество лишних аллокаций.
- Ситуаций, где не требуется идентичность объекта или сложное внутреннее состояние — достаточно представления через одно значение.

При этом на выигрыш по памяти/GC стоит рассчитывать как на потенциальную оптимизацию: он зависит от конкретных контекстов и целевой платформы.

---

### Ограничения И Важные Нюансы

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
id1 == id2 // Сравнение по значению, через базовое свойство
```

**3. Boxing-сценарии (могут приводить к аллокациям):**

```kotlin
@JvmInline
value class UserId(val value: Int)

// Boxing как generic:
val list: List<UserId> = listOf(UserId(1))

// Boxing для nullable: для отличия null от значения используется представление-обертка
val nullable: UserId? = null

// Boxing при использовании как Any:
val any: Any = UserId(1)
```

В этих случаях value-класс фактически упаковывается, и выигрыш по памяти/GC снижается.

**4. Другие ограничения:**

- Нельзя быть `open`, `inner`, `abstract`; нет наследования от классов (только реализации интерфейсов).
- Базовое свойство фактически `val`: внутри нельзя иметь изменяемое состояние, как в обычных классах.
- Семантика `equals`, `hashCode`, `toString` определяется через базовое значение и должна рассматриваться как value-based.

При соблюдении этих условий value-классы дают усиленную type-safety и потенциальную выгоду по производительности без лишних аллокаций в hot-путях, но использовать их стоит прежде всего ради четких доменных типов.

## Answer (EN)

**Value classes** (`value class`, previously called "inline classes") are lightweight wrappers that provide type safety. In many cases, the compiler can represent them as their underlying type (primitive or reference), which avoids extra object allocations compared to regular wrapper classes when possible. However, this is an implementation optimization, not an unconditional guarantee in all contexts; you should validate performance empirically.

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

// At call sites, the representation can often be just Int and String,
// not separate wrapper objects, where the backend/JIT can optimize it.
```

---

### Performance Benefit (Typical Case)

Without a value class:

```kotlin
data class UserId(val value: Int) // Regular class

fun process(id: UserId) {
    println(id.value)
}

// Each call typically allocates a UserId instance on the heap:
process(UserId(123))
```

With a value class:

```kotlin
@JvmInline
value class UserId(val value: Int)

fun process(id: UserId) {
    println(id.value)
}

// In many cases, the call can be compiled to just work with Int (no extra wrapper),
// but boxing and allocations may still occur in certain contexts
// (generics, nullable, Any, reflection, etc.).
process(UserId(123))
```

---

### When to Use

Primarily use value classes for:

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
- such types appear frequently in call sites and you want to reduce wrapper allocations,
- you do not need object identity or complex mutable state.

Treat performance benefits as potential optimizations, not as a strict ABI-level guarantee.

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

**2. No identity (value-based semantics):**

```kotlin
val id1 = UserId(123)
val id2 = UserId(123)

// Reference identity is not meaningful here
// id1 === id2 // Not the intended comparison
id1 == id2 // Value equality via the underlying property
```

**3. Boxing scenarios (may allocate):**

```kotlin
@JvmInline
value class UserId(val value: Int)

// Boxed when used as a generic type argument:
val list: List<UserId> = listOf(UserId(1))

// Boxed when nullable: needs a wrapper representation to distinguish null from values
val nullable: UserId? = null

// Boxed when used as Any:
val any: Any = UserId(1)
```

In these scenarios, the value class is actually boxed, so memory/GC savings are reduced.

**4. Other constraints:**

- Cannot be `open`, `inner`, or `abstract`; no subclassing (they may implement interfaces).
- The underlying property is effectively `val`; you cannot keep additional mutable state like in regular classes.
- The semantics of `equals`, `hashCode`, and `toString` are defined in terms of the underlying value and should be treated as value-based.

When used within these constraints, value classes provide stronger type safety and can offer performance benefits (fewer allocations, smaller representations) on hot paths, but they should be introduced primarily for clearer domain modeling.

## Дополнительные Вопросы (RU)

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

## Связанные Вопросы (RU)

- [[q-expect-actual-kotlin--kotlin--medium]]
## Related Questions

- [[q-expect-actual-kotlin--kotlin--medium]]
