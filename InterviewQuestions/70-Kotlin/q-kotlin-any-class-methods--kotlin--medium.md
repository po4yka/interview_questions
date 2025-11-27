---
id: lang-216
title: "Kotlin Any Class Methods / Методы класса Any в Kotlin"
aliases: ["Kotlin Any methods", "Методы Any в Kotlin"]
topic: kotlin
subtopics: [classes, functions, types]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c--kotlin--medium, c-computer-science, q-debugging-coroutines-techniques--kotlin--medium]
created: 2024-10-15
updated: 2025-11-11
tags: [difficulty/medium, kotlin/classes, kotlin/functions, kotlin/types]

date created: Sunday, October 12th 2025, 12:27:48 pm
date modified: Tuesday, November 25th 2025, 8:53:54 pm
---
# Вопрос (RU)
> Какие в базовом классе Kotlin `Any` есть методы и что они делают?

# Question (EN)
> What methods exist in Kotlin base class `Any` and what do they do?

---

## Ответ (RU)

В Kotlin все неабстрактные ссылочные типы по умолчанию неявно наследуются от `Any`, который определяет ровно три открытых метода:

- `equals(other: Any?): Boolean`
- `hashCode(): Int`
- `toString(): String`

(Nullable-типы вида `Foo?` на уровне системы типов обрабатываются отдельно, но для ненулевого экземпляра используются эти же методы.)

### 1. equals(other: Any?): `Boolean`

Используется для проверки равенства оператором `==` (компилятор транслирует `==` в безопасный вызов `equals`).

```kotlin
open fun equals(other: Any?): Boolean
```

- Реализация `Any` по умолчанию (на JVM): возвращает `true` только если оба операнда ссылаются на один и тот же объект (т.е. по сути, как `===`).
- Реализация в `data class`: автоматически генерируется и сравнивает объявленные свойства (значимое равенство).

```kotlin
class Person(val name: String)

val p1 = Person("John")
val p2 = Person("John")

p1.equals(p2)  // false: разные экземпляры, реализация Any.equals по умолчанию
p1 == p2       // false: '==' вызывает equals -> всё ещё сравнение по ссылке здесь

data class User(val name: String)

val u1 = User("John")
val u2 = User("John")

u1 == u2       // true: equals в data class сравнивает 'name'
```

Замечания:
- `==` использует `equals` (c null-safe вызовом).
- `===` проверяет равенство ссылок и не может быть переопределён.

### 2. hashCode(): `Int`

Возвращает хэш-код объекта:

```kotlin
open fun hashCode(): Int
```

- Реализация `Any` по умолчанию на JVM обычно делегирует к `java.lang.Object.hashCode()`, который, как правило, основан на идентичности объекта; конкретная связь с адресом в памяти не закреплена в спецификации Kotlin.
- В `data class` хэш-код автоматически генерируется на основе свойств, участвующих в `equals`.

Ключевой контракт:
- Если `a.equals(b)` возвращает `true`, то `a.hashCode()` и `b.hashCode()` обязаны быть равны.

```kotlin
val person = Person("John")
val hash = person.hashCode()  // по умолчанию основан на идентичности объекта на JVM

val user = User("John")
val hash2 = user.hashCode()   // основан на 'name' (и других объявленных свойствах)
```

### 3. toString(): `String`

Возвращает строковое представление объекта:

```kotlin
open fun toString(): String
```

- Реализация `Any` по умолчанию на JVM делегирует к `Object.toString()`, обычно в формате `ClassName@hexHash`.
- Для `data class` генерируется удобочитаемый формат `ClassName(prop1=value1, prop2=value2, ...)`.

```kotlin
val person = Person("John")
println(person.toString())  // например, Person@1a2b3c4d (представление по умолчанию)

val user = User("John")
println(user.toString())    // User(name=John)
```

**Резюме (концептуально):**

- `equals(other: Any?)`:
  - Реализация Any по умолчанию: по идентичности (один и тот же экземпляр).
  - Data class / переопределения: по значению, как определено реализацией.
- `hashCode()`: обязан быть согласован с `equals`; в data class строится из свойств, участвующих в равенстве.
- `toString()`: техническое представление по умолчанию; в data class — читаемое представление со свойствами.

Важно:
- При переопределении `equals()` необходимо переопределить и `hashCode()` для соблюдения контракта.

## Answer (EN)

In Kotlin, all non-nullable classes implicitly inherit from `Any`, which defines exactly three open methods:

- `equals(other: Any?): Boolean`
- `hashCode(): Int`
- `toString(): String`

(Nullable types like `Foo?` are represented differently at the type system level but still rely on these methods when the underlying instance is non-null.)

### 1. equals(other: Any?): `Boolean`

Used for equality checks via the `==` operator (which the compiler translates to a safe call to `equals`).

```kotlin
open fun equals(other: Any?): Boolean
```

- Default `Any` implementation on JVM: returns `true` only if both references point to the same instance (reference equality), i.e. behaves like `===`.
- `data class` implementation: auto-generated to compare declared properties for value-based equality.

```kotlin
class Person(val name: String)

val p1 = Person("John")
val p2 = Person("John")

p1.equals(p2)  // false: different instances, default Any.equals
p1 == p2       // false: '==' calls equals -> still reference-based here

data class User(val name: String)

val u1 = User("John")
val u2 = User("John")

u1 == u2       // true: data class equals compares 'name'
```

Note:
- `==` uses `equals` (with a null-safe call).
- `===` checks reference equality and is not overridable.

### 2. hashCode(): `Int`

Returns a hash code for the object:

```kotlin
open fun hashCode(): Int
```

- Default `Any` implementation on JVM: typically delegates to `java.lang.Object.hashCode()`, which is usually based on the object's identity; the exact numeric relation to memory address is not part of the Kotlin language specification.
- `data class` implementation: auto-generated from the properties used in `equals`.

Key contract:
- If `a.equals(b)` is `true`, then `a.hashCode()` must be equal to `b.hashCode()`.

```kotlin
val person = Person("John")
val hash = person.hashCode()  // identity-based in default implementation on JVM

val user = User("John")
val hash2 = user.hashCode()   // based on 'name' (and other declared properties, if any)
```

### 3. toString(): `String`

Returns a string representation of the object:

```kotlin
open fun toString(): String
```

- Default `Any` implementation on JVM: delegates to `Object.toString()`, typically formatted as `ClassName@hexHash`.
- `data class` implementation: auto-generated as `ClassName(prop1=value1, prop2=value2, ...)`.

```kotlin
val person = Person("John")
println(person.toString())  // e.g. Person@1a2b3c4d (default representation)

val user = User("John")
println(user.toString())    // User(name=John)
```

**Summary (conceptual):**

- `equals(other: Any?)`:
  - Default Any: identity-based (same instance).
  - Data classes / overrides: value-based as defined by implementation.
- `hashCode()`: must be consistent with `equals`; data classes derive it from properties used in equality.
- `toString()`: default technical representation; data classes provide a readable representation with properties.

Important:
- When you override `equals()`, you MUST also override `hashCode()` to preserve the contract.

## Related Questions

- [[q-abstract-class-vs-interface--kotlin--medium]]
- [[q-access-modifiers--kotlin--medium]]
- [[q-abstract-class-purpose--cs--medium]]

## Follow-ups

- How do `==` and `===` differ in Kotlin, and how do they relate to `equals`?
- Why must `hashCode()` be overridden together with `equals()`?
- How are `Any` methods represented and used on different Kotlin targets (JVM/JS/Native)?

## References

- [[c--kotlin--medium]]
- [[c-computer-science]]
- Official Kotlin docs: "Classes and Inheritance" and "Equality" sections
