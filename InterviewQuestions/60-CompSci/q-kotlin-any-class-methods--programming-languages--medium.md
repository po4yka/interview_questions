---
id: 20251003141114
title: Any class methods in Kotlin / Методы класса Any в Kotlin
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, type-system, object-methods]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/1045
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-type-system
  - c-object-methods

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, any, equals, hashcode, tostring, object-methods, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What methods exist in Kotlin base class and what do they do

# Вопрос (RU)
> Какие в базовом классе Kotlin есть методы и что они делают

---

## Answer (EN)

In Kotlin, all classes inherit from `Any` and have **three base methods**:

### 1. equals(other: Any?): Boolean

Compares objects for **structural equality**:

```kotlin
open fun equals(other: Any?): Boolean
```

**Default behavior**: Compares references (same as `===`)
**Data class behavior**: Compares all properties

```kotlin
class Person(val name: String)

val p1 = Person("John")
val p2 = Person("John")

p1.equals(p2)  // false (default: reference equality)
p1 == p2       // false (same as equals)

data class User(val name: String)

val u1 = User("John")
val u2 = User("John")

u1 == u2       // true (data class: value equality)
```

### 2. hashCode(): Int

Generates **hash code** based on object:

```kotlin
open fun hashCode(): Int
```

**Default behavior**: Based on memory address
**Data class behavior**: Based on property values

**Contract**: If `a.equals(b)` then `a.hashCode() == b.hashCode()`

```kotlin
val person = Person("John")
val hash = person.hashCode()  // Based on memory address

val user = User("John")
val hash2 = user.hashCode()   // Based on name value
```

### 3. toString(): String

Returns **string representation** of object:

```kotlin
open fun toString(): String
```

**Default behavior**: `ClassName@hashCode`
**Data class behavior**: `ClassName(property1=value1, property2=value2)`

```kotlin
val person = Person("John")
println(person.toString())  // Person@1a2b3c4d

val user = User("John")
println(user.toString())    // User(name=John)
```

**Summary:**

| Method | Default | Data Class |
|--------|---------|------------|
| `equals()` | Reference equality | Value equality |
| `hashCode()` | Memory address | Property hash |
| `toString()` | ClassName@hash | ClassName(props) |

**Important**: When overriding `equals()`, you MUST override `hashCode()`!

## Ответ (RU)

В Kotlin все классы наследуются от Any и имеют три базовых метода: equals(), hashCode() и toString()...

---

## Follow-ups
- What is the equals/hashCode contract?
- How do data classes implement these methods?
- When should you override these methods?

## References
- [[c-kotlin-type-system]]
- [[c-object-methods]]
- [[moc-kotlin]]

## Related Questions
- [[q-equals-hashcode-rules--programming-languages--medium]]
- [[q-kotlin-any-inheritance--programming-languages--easy]]
