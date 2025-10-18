---
id: 20251012-1227111128
title: "Equals Hashcode Contracts / Контракты equals и hashCode"
topic: computer-science
difficulty: medium
status: draft
moc: moc-compSci
related: [q-what-is-garbage-in-gc--programming-languages--easy, q-composite-pattern--design-patterns--medium, q-flyweight-pattern--design-patterns--hard]
created: 2025-10-15
tags:
  - collections
  - contract
  - equals
  - hashcode
  - kotlin
  - object-methods
  - programming-languages
---
# Расскажи о контрактах equals и hashCode

# Question (EN)
> Tell me about equals and hashCode contracts

# Вопрос (RU)
> Расскажи о контрактах equals и hashCode

---

## Answer (EN)

The `equals()` and `hashCode()` methods are used for **comparing objects** and their **correct operation in collections** (Set, Map).

### equals() Contract

The `equals()` method must satisfy these properties:

#### 1. Reflexivity
An object must equal itself:
```kotlin
a.equals(a) == true

val user = User("John")
user.equals(user)  // Must be true
```

#### 2. Symmetry
If a equals b, then b equals a:
```kotlin
a.equals(b) == b.equals(a)

val u1 = User("John")
val u2 = User("John")
u1.equals(u2) == u2.equals(u1)  // Must be true
```

#### 3. Transitivity
If a equals b and b equals c, then a equals c:
```kotlin
if (a.equals(b) && b.equals(c)) {
    a.equals(c) == true
}

val u1 = User("John")
val u2 = User("John")
val u3 = User("John")
// If u1 == u2 and u2 == u3, then u1 == u3
```

#### 4. Consistency
Multiple invocations return same result if objects don't change:
```kotlin
val u1 = User("John")
val u2 = User("John")

u1.equals(u2)  // true
u1.equals(u2)  // still true
u1.equals(u2)  // still true

// Unless object is modified
u1.name = "Jane"
u1.equals(u2)  // now false
```

#### 5. Null Comparison
Comparison with null always returns false:
```kotlin
a.equals(null) == false

val user = User("John")
user.equals(null)  // Must be false
```

### hashCode() Contract

The `hashCode()` method must satisfy:

#### 1. Consistent Hash
If object doesn't change, hash code stays the same:
```kotlin
val user = User("John")
val hash1 = user.hashCode()
val hash2 = user.hashCode()
hash1 == hash2  // Must be true
```

#### 2. Equal Objects Have Equal Hash Codes
**Most important**: If `a.equals(b)`, then `a.hashCode() == b.hashCode()`
```kotlin
val u1 = User("John", 30)
val u2 = User("John", 30)

if (u1.equals(u2)) {
    u1.hashCode() == u2.hashCode()  // Must be true!
}
```

#### 3. Unequal Objects May Have Equal Hash Codes (Collision)
**Not required, but allowed**: `a.hashCode() == b.hashCode()` does not imply `a.equals(b)`
```kotlin
// These can have same hash code even if not equal
val u1 = User("John", 30)
val u2 = User("Jane", 30)

u1.hashCode() == u2.hashCode()  // Allowed (hash collision)
u1.equals(u2)  // false
```

### Implementation Examples

**Manual implementation:**
```kotlin
data class Person(val name: String, val age: Int) {
    // equals() - compare all properties
    override fun equals(other: Any?): Boolean {
        if (this === other) return true  // Reflexivity
        if (other !is Person) return false  // Type check

        // Compare properties
        return name == other.name && age == other.age
    }

    // hashCode() - combine property hash codes
    override fun hashCode(): Int {
        var result = name.hashCode()
        result = 31 * result + age
        return result
    }
}
```

**Data class (automatic):**
```kotlin
data class Person(val name: String, val age: Int)
// equals() and hashCode() generated automatically
// Only considers properties in primary constructor
```

### Why This Matters for Collections

**HashSet/HashMap rely on these contracts:**
```kotlin
data class User(val name: String, val age: Int)

val user1 = User("John", 30)
val user2 = User("John", 30)

// HashSet uses hashCode() and equals()
val set = hashSetOf(user1)
set.contains(user2)  // true (because equals() returns true)

// HashMap uses hashCode() for bucket, equals() for exact match
val map = hashMapOf(user1 to "data")
map[user2]  // Returns "data" (because user1.equals(user2))
```

**Without proper implementation:**
```kotlin
class BadUser(val name: String) {
    // Only overrides equals, not hashCode - WRONG!
    override fun equals(other: Any?) = other is BadUser && name == other.name
}

val u1 = BadUser("John")
val u2 = BadUser("John")

u1.equals(u2)  // true
u1.hashCode() == u2.hashCode()  // false - VIOLATES CONTRACT!

// Breaks HashMap/HashSet
val set = hashSetOf(u1)
set.contains(u2)  // false (because hash codes differ!)
```

### Implementation Tips

**1. Always override both together:**
```kotlin
// - Wrong: Only equals
override fun equals(other: Any?) = ...

// - Correct: Both equals and hashCode
override fun equals(other: Any?) = ...
override fun hashCode() = ...
```

**2. Use same properties in both:**
```kotlin
data class User(val id: Int, val name: String) {
    override fun equals(other: Any?): Boolean {
        if (other !is User) return false
        return id == other.id  // Only compare id
    }

    override fun hashCode(): Int {
        return id.hashCode()  // Only use id (same as equals)
    }
}
```

**3. Use data classes when possible:**
```kotlin
// Automatic, correct implementation
data class User(val name: String, val age: Int)
```

**4. Good hash code formula:**
```kotlin
override fun hashCode(): Int {
    var result = property1.hashCode()
    result = 31 * result + property2.hashCode()
    result = 31 * result + property3.hashCode()
    return result
}

// Or use Objects.hash() in Java/Kotlin
override fun hashCode() = Objects.hash(property1, property2, property3)
```

### Summary Table

| Contract | Rule | Example |
|----------|------|---------|
| **equals()** | | |
| Reflexivity | `a.equals(a) == true` | Object equals itself |
| Symmetry | `a.equals(b) == b.equals(a)` | Bidirectional equality |
| Transitivity | `a==b && b==c => a==c` | Transitive equality |
| Consistency | Repeated calls same result | Unless object changes |
| Null safety | `a.equals(null) == false` | Never equal to null |
| **hashCode()** | | |
| Consistency | Same object → same hash | Unless object changes |
| Equality → hash | `a==b => hash(a)==hash(b)` | **Must satisfy** |
| Hash → equality | `hash(a)==hash(b) !=> a==b` | **Not required** |

---

## Ответ (RU)

Методы equals() и hashCode() используются для сравнения объектов и их корректной работы в коллекциях (Set, Map). Контракт `equals()` должен: Рефлексивность: a.equals(a) → true (объект равен самому себе). Симметричность: a.equals(b) == b.equals(a). Транзитивность: если a == b и b == c, то a == c. Согласованность: если a == b, то a.equals(b) всегда возвращает одно и же, пока объект не изменится. Сравнение с null всегда даёт false: a.equals(null) == false. Контракт hashCode(): если a.equals(b) то a.hashCode() == b.hashCode().

## Related Questions

- [[q-what-is-garbage-in-gc--programming-languages--easy]]
- [[q-composite-pattern--design-patterns--medium]]
- [[q-flyweight-pattern--design-patterns--hard]]
