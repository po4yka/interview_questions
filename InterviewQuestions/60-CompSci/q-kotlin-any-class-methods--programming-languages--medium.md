---
tags:
  - kotlin
  - any
  - equals
  - hashcode
  - tostring
  - object-methods
  - easy_kotlin
  - programming-languages
  - type-system
difficulty: medium
---

# Какие в базовом классе Kotlin есть методы и что они делают?

**English**: What methods exist in Kotlin base class and what do they do?

## Answer

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

## Ответ

В Kotlin все классы наследуются от Any и имеют три базовых метода: equals(), hashCode() и toString()...

