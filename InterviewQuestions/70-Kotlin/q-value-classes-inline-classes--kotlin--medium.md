---
id: kotlin-235
title: "Value Classes (Inline Classes) in Kotlin / Value классы в Kotlin"
aliases: ["Value Classes", "Встраиваемые классы"]
topic: kotlin
subtopics: [inline-classes, performance, value-classes]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-data-class-detailed--kotlin--medium, q-inheritance-open-final--kotlin--medium, q-object-singleton-companion--kotlin--medium]
created: "2024-10-12"
updated: "2025-11-09"
tags: [difficulty/medium, inline-classes, kotlin, kotlin-features, performance, value-classes]
sources: ["https://kotlinlang.org/docs/inline-classes.html"]
date created: Saturday, November 1st 2025, 12:42:10 pm
date modified: Tuesday, November 25th 2025, 8:53:48 pm
---

# Вопрос (RU)
> Что такое value классы (inline классы) в Kotlin и зачем они нужны?

# Question (EN)
> What are value classes (inline classes) in Kotlin and why are they needed?

## Ответ (RU)

**Теория Value классов:**
Value классы (ранее называвшиеся inline классами) — механизм Kotlin для обёртки одного значения без существенных накладных расходов на allocation. Компилятор может представлять value класс как его базовый тип (underlying type), избегая создания дополнительного объекта в runtime, когда это безопасно. Это даёт type-safety с минимальными накладными расходами — близко к zero-cost abstractions, но не гарантируется в 100% случаев (есть сценарии boxing-а).

(В JVM-примерах используется аннотация `@JvmInline`, которая нужна для корректной генерации байткода и совместимости на JVM; в multiplatform-коде используются те же value классы, но детали реализации зависят от таргета.)

**Основные концепции:**
- **Одно underlying property**: Должен иметь ровно одно `val` или `var` property в первичном конструкторе — это underlying значение
- **Inline-представление**: Компилятор использует underlying тип представления, когда это возможно и безопасно
- **Type safety**: Обеспечивает безопасность типов поверх одинаковых базовых типов (например, `UserId` vs `OrderId` оба на `Long`)
- **Меньше allocation**: В большинстве сценариев избегает создания wrapper-объектов; при определённых использованиях происходит boxing

**Базовый синтаксис (JVM):**
```kotlin
@JvmInline
value class Password(private val value: String)

@JvmInline
value class UserId(private val id: Long)

// ✅ Использование
val password = Password("secret123")
val userId = UserId(12345L)

// ❌ Нельзя создать без значения
// val badPassword = Password() // Ошибка компиляции
```

**Type safety без лишних allocation:**
```kotlin
@JvmInline
value class Email(private val value: String) {
    init {
        require(value.contains("@")) { "Invalid email" }
    }
}

@JvmInline
value class Username(private val value: String) {
    init {
        require(value.length >= 3) { "Username too short" }
    }
}

// ✅ Различные типы, нет путаницы
fun signup(email: Email, username: Username) {
    println("Email: $email, Username: $username")
}

// ❌ Компилятор не даст перепутать типы
// signup(Username("test"), Email("test@example.com")) // Ошибка!
```

**Требования и ограничения value class:**
```kotlin
// ❌ ПЛОХО: больше одного значения в primary constructor
// value class Bad(private val a: String, private val b: String)

// ✅ underlying-свойство может быть val или var
@JvmInline
value class Good1(val value: String)

@JvmInline
value class Good2(var value: String)

// ✅ Можно объявлять дополнительные функции/свойства без backing field,
// но underlying остаётся единственным параметром primary constructor
@JvmInline
value class Distance(val meters: Int) {
    val inKm: Double get() = meters / 1000.0
}
```
Кратко об ограничениях (актуальные ключевые для собеседования):
- Нельзя иметь более одного параметра в primary constructor
- Нельзя иметь `inner` классы
- Нельзя наследоваться от других классов, только реализовывать интерфейсы; сами по себе final
- Нельзя объявлять явные backing fields, кроме underlying-свойства

**Практическое применение:**
```kotlin
@JvmInline
value class Price(val amountCents: Long) {
    fun format(): String {
        return "${'$'}${amountCents / 100.0}"
    }
}

@JvmInline
value class Minutes(val value: Int) {
    fun toSeconds(): Int = value * 60
}

// ✅ Типобезопасная работа с единицами измерения
fun calculateCost(price: Price, duration: Minutes): String {
    val total = price.amountCents * duration.value
    return "Total: ${'$'}{total / 100.0}"
}
```

**Boxing scenarios (где возможны allocation, упрощённо):**
```kotlin
@JvmInline
value class Id(val value: Int)

// ✅ В типичных простых вызовах может использоваться inlined-представление
fun processId(id: Id): Int {
    return id.value
}

// Boxing может происходить, например, когда value класс участвует в местах,
// где требуется ссылочный тип или обобщённый параметр:

interface Wrapper {
    fun getValue(): Id // Представление Id здесь зависит от контекста вызова
}

// Передача в Any (или другой тип, не знающий о value class)
fun boxId(id: Id): Any {
    return id // Здесь потребуется boxing
}

// Использование как nullable
fun nullableId(id: Id?): Id? {
    return id // Nullable value class представляется как boxed-тип
}
```

## Дополнительные Вопросы (RU)

- Когда использовать value class vs `data class`?
- Каковы особенности производительности value классов?
- Какие boxing-сценарии стоит учитывать и по возможности избегать?

## Ссылки (RU)

- [[c-kotlin]]
- https://kotlinlang.org/docs/inline-classes.html

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-kotlin-enum-classes--kotlin--easy]] - Базовые классы

### Связанные (средняя сложность)
- [[q-data-class-detailed--kotlin--medium]] - Data классы
- [[q-inheritance-open-final--kotlin--medium]] - Наследование
- [[q-class-initialization-order--kotlin--medium]] - Порядок инициализации классов

### Продвинутое (сложнее)
- [[q-kotlin-reified-types--kotlin--hard]] - Reified типы

## Answer (EN)

**Value Class Theory:**
Value classes (previously called inline classes) are a Kotlin mechanism for wrapping a single value with minimal allocation overhead. The compiler can represent a value class as its underlying type, avoiding creating wrapper objects at runtime when safe. This provides type safety with very low overhead — close to zero-cost abstractions, though boxing can still occur in some scenarios.

(In the JVM examples below, `@JvmInline` is used to control how value classes are represented on the JVM and for Java interop; in multiplatform code you use the same `value class` construct, with backend-specific implementation details.)

**Core Concepts:**
- **Single underlying property**: Must have exactly one `val` or `var` property in the primary constructor — this is the underlying value
- **Inline-like representation**: The compiler uses the underlying type representation when possible and safe
- **Type safety**: Provides stronger type safety over identical underlying types (e.g., `UserId` vs `OrderId` over `Long`)
- **Reduced allocations**: Avoids creating wrapper objects in most common cases; boxing appears in specific usages

**Basic Syntax (JVM):**
```kotlin
@JvmInline
value class Password(private val value: String)

@JvmInline
value class UserId(private val id: Long)

// ✅ Usage
val password = Password("secret123")
val userId = UserId(12345L)

// ❌ Cannot create without value
// val badPassword = Password() // Compilation error
```

**Type Safety Without Extra Allocation:**
```kotlin
@JvmInline
value class Email(private val value: String) {
    init {
        require(value.contains("@")) { "Invalid email" }
    }
}

@JvmInline
value class Username(private val value: String) {
    init {
        require(value.length >= 3) { "Username too short" }
    }
}

// ✅ Different types, no confusion
fun signup(email: Email, username: Username) {
    println("Email: $email, Username: $username")
}

// ❌ Compiler won't let types be confused
// signup(Username("test"), Email("test@example.com")) // Error!
```

**Value Class Requirements and Constraints:**
```kotlin
// ❌ BAD: more than one value in primary constructor
// value class Bad(private val a: String, private val b: String)

// ✅ Underlying property can be val or var
@JvmInline
value class Good1(val value: String)

@JvmInline
value class Good2(var value: String)

// ✅ May declare additional members without backing fields,
// but the underlying value must be the only primary constructor parameter
@JvmInline
value class Distance(val meters: Int) {
    val inKm: Double get() = meters / 1000.0
}
```
Key constraints (essential for interviews):
- Only one parameter in the primary constructor
- No `inner` classes
- Cannot inherit from other classes; can only implement interfaces; they are effectively final
- No explicit backing fields other than the underlying property

**Practical Application:**
```kotlin
@JvmInline
value class Price(val amountCents: Long) {
    fun format(): String {
        return "${'$'}${amountCents / 100.0}"
    }
}

@JvmInline
value class Minutes(val value: Int) {
    fun toSeconds(): Int = value * 60
}

// ✅ Type-safe work with measurement units
fun calculateCost(price: Price, duration: Minutes): String {
    val total = price.amountCents * duration.value
    return "Total: ${'$'}{total / 100.0}"
}
```

**Boxing Scenarios (where allocations may occur, simplified):**
```kotlin
@JvmInline
value class Id(val value: Int)

// ✅ In many straightforward calls, the inlined representation can be used
fun processId(id: Id): Int {
    return id.value
}

// Boxing can occur when a reference type or generic context is required:

interface Wrapper {
    fun getValue(): Id // Actual representation of Id depends on call-site and backend
}

// Passed as Any (or other types unaware of the value class)
fun boxId(id: Id): Any {
    return id // Boxing required here
}

// Used as nullable
fun nullableId(id: Id?): Id? {
    return id // Nullable value classes are represented as boxed types
}
```

## Follow-ups

- When to use value class vs `data class`?
- Performance implications of value classes?
- Boxing scenarios to be aware of and avoid where possible?

## References

- [[c-kotlin]]
- https://kotlinlang.org/docs/inline-classes.html

## Related Questions

### Prerequisites (Easier)
- [[q-kotlin-enum-classes--kotlin--easy]] - Basic classes

### Related (Medium)
- [[q-data-class-detailed--kotlin--medium]] - Data classes
- [[q-inheritance-open-final--kotlin--medium]] - Inheritance
- [[q-class-initialization-order--kotlin--medium]] - Class initialization

### Advanced (Harder)
- [[q-kotlin-reified-types--kotlin--hard]] - Reified types
