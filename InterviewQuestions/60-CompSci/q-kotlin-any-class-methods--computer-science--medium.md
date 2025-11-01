---
id: 20251012-12271111110
title: "Kotlin Any Class Methods / Методы класса Any в Kotlin"
aliases: []
topic: computer-science
subtopics: [operators, type-system, class-features]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-debugging-coroutines-techniques--kotlin--medium, q-retry-operators-flow--kotlin--medium, q-noncancellable-context-cleanup--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags:
  - 
  - difficulty/medium
---
# Какие в базовом классе Kotlin есть методы и что они делают?

# Question (EN)
> What methods exist in Kotlin base class and what do they do?

# Вопрос (RU)
> Какие в базовом классе Kotlin есть методы и что они делают?

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

---

## Ответ (RU)

В Kotlin все классы наследуются от `Any` и имеют **три базовых метода**:

### 1. equals(other: Any?): Boolean

Сравнивает объекты на **структурное равенство**:

```kotlin
open fun equals(other: Any?): Boolean
```

**Поведение по умолчанию**: Сравнивает ссылки (как `===`)
**Поведение в data class**: Сравнивает все свойства

```kotlin
class Person(val name: String)

val p1 = Person("John")
val p2 = Person("John")

p1.equals(p2)  // false (по умолчанию: равенство ссылок)
p1 == p2       // false (то же, что equals)

data class User(val name: String)

val u1 = User("John")
val u2 = User("John")

u1 == u2       // true (data class: равенство значений)
```

### 2. hashCode(): Int

Генерирует **хэш-код** на основе объекта:

```kotlin
open fun hashCode(): Int
```

**Поведение по умолчанию**: На основе адреса в памяти
**Поведение в data class**: На основе значений свойств

**Контракт**: Если `a.equals(b)`, то `a.hashCode() == b.hashCode()`

```kotlin
val person = Person("John")
val hash = person.hashCode()  // На основе адреса в памяти

val user = User("John")
val hash2 = user.hashCode()   // На основе значения name
```

### 3. toString(): String

Возвращает **строковое представление** объекта:

```kotlin
open fun toString(): String
```

**Поведение по умолчанию**: `ClassName@hashCode`
**Поведение в data class**: `ClassName(property1=value1, property2=value2)`

```kotlin
val person = Person("John")
println(person.toString())  // Person@1a2b3c4d

val user = User("John")
println(user.toString())    // User(name=John)
```

**Резюме:**

| Метод | По умолчанию | Data Class |
|--------|-------------|------------|
| `equals()` | Равенство ссылок | Равенство значений |
| `hashCode()` | Адрес в памяти | Хэш свойств |
| `toString()` | ClassName@hash | ClassName(props) |

**Важно**: При переопределении `equals()` вы ДОЛЖНЫ переопределить `hashCode()`!

## Related Questions

- [[q-debugging-coroutines-techniques--kotlin--medium]]
- [[q-retry-operators-flow--kotlin--medium]]
- [[q-noncancellable-context-cleanup--kotlin--medium]]
