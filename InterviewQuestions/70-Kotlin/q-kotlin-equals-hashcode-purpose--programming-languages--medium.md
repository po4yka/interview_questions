---
id: lang-087
title: "Kotlin Equals Hashcode Purpose / Назначение equals и hashCode в Kotlin"
aliases: [Kotlin Equals Hashcode Purpose, Назначение equals и hashCode в Kotlin]
topic: programming-languages
subtopics: [collections, null-safety, type-system]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-launch-vs-async--kotlin--easy, q-semaphore-rate-limiting--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [collections, difficulty/medium, equals, hashcode, object-comparison, programming-languages]
date created: Friday, October 31st 2025, 6:28:52 pm
date modified: Saturday, November 1st 2025, 5:43:25 pm
---
# Зачем Нужны Методы Equals И Hashcode?

# Вопрос (RU)
> Зачем нужны методы equals и hashcode?

---

# Question (EN)
> Why do we need equals and hashCode methods?

## Ответ (RU)

Методы `equals()` и `hashCode()` играют центральную роль в сравнении объектов и управлении ими в коллекциях.

**equals()** определяет равенство объектов по содержимому вместо сравнения ссылок.

**hashCode()** возвращает хеш-код объекта для использования в хеш-таблицах.

Соблюдение контракта между `equals()` и `hashCode()` критически важно для правильной работы коллекций, основанных на хеш-таблицах.

## Answer (EN)

Methods `equals()` and `hashCode()` play a **central role** in comparing objects and managing them in collections.

**equals(Object obj)** - Defines object equality by content instead of reference comparison.

**hashCode()** - Returns object hash code for use in hash tables.

**Adhering to the contract** between `equals()` and `hashCode()` is **critically important** for correct operation of hash-based collections.

**Why equals() is needed:**

```kotlin
data class Person(val name: String, val age: Int)

val person1 = Person("John", 30)
val person2 = Person("John", 30)

// Without equals: reference comparison
// person1 == person2  // false (different objects)

// With equals: content comparison
person1 == person2  // true (same content)
```

**Why hashCode() is needed:**

```kotlin
val set = HashSet<Person>()
set.add(Person("Alice", 25))

// Hash code determines bucket in hash table
val contains = set.contains(Person("Alice", 25))
// Without hashCode: false (different hash)
// With hashCode: true (same hash for equal objects)
```

**Contract between equals() and hashCode():**

```kotlin
// Rule 1: If equals() returns true, hashCode() MUST return same value
if (obj1 == obj2) {
    obj1.hashCode() == obj2.hashCode()  // MUST be true
}

// Rule 2: If hashCode() is same, equals() MAY be true or false
if (obj1.hashCode() == obj2.hashCode()) {
    obj1 == obj2  // May be true or false (collision)
}
```

**Using in Collections:**

```kotlin
// HashMap relies on hashCode() + equals()
val map = HashMap<Person, String>()
map[Person("John", 30)] = "Engineer"

// Lookup uses:
// 1. hashCode() to find bucket
// 2. equals() to find exact key
val job = map[Person("John", 30)]  // "Engineer"
```

**Data Class Auto-generates Both:**

```kotlin
data class User(val id: Int, val name: String)

val user1 = User(1, "Alice")
val user2 = User(1, "Alice")

user1 == user2  // true - equals() auto-generated
user1.hashCode() == user2.hashCode()  // true - hashCode() auto-generated
```

**Manual Implementation:**

```kotlin
class Book(val isbn: String, val title: String) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is Book) return false
        return isbn == other.isbn  // Compare by ISBN only
    }

    override fun hashCode(): Int {
        return isbn.hashCode()  // Hash by ISBN only
    }
}
```

**Hash-based Collections:**

| Collection | Uses hashCode() | Uses equals() |
|------------|-----------------|---------------|
| HashSet | - Yes | - Yes |
| HashMap | - Yes | - Yes |
| LinkedHashSet | - Yes | - Yes |
| ArrayList | - No | - Yes (for contains) |
| TreeSet | - No | - No (uses Comparable) |

**Summary:**

- **equals()**: Compares objects by **content**, not reference
- **hashCode()**: Returns **hash value** for hash table storage
- **Contract**: If `equals()` is true, `hashCode()` **must** be equal
- **Critical for**: HashSet, HashMap, LinkedHashSet
- **data class**: Auto-generates both methods

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-semaphore-rate-limiting--kotlin--medium]]
- [[q-launch-vs-async--kotlin--easy]]
-
