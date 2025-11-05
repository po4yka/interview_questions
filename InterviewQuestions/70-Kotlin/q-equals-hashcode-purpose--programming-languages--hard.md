---
id: lang-083
title: "Equals Hashcode Purpose / Назначение equals и hashCode"
aliases: [Equals Hashcode Purpose, Назначение equals и hashCode]
topic: programming-languages
subtopics: [collections, equality, object-methods]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-equality, q-equals-hashcode-contracts--programming-languages--medium, q-java-equals-default-behavior--programming-languages--easy]
created: 2025-10-15
updated: 2025-10-31
tags: [collections, contracts, difficulty/hard, equality, object-methods, programming-languages]
date created: Friday, October 31st 2025, 6:29:51 pm
date modified: Saturday, November 1st 2025, 5:43:26 pm
---
# Why Are Equals and Hashcode Methods Needed?

# Вопрос (RU)
> Зачем нужны методы equals и hashcode в Kotlin и Java?

---

# Question (EN)
> Why are equals and hashcode methods needed in Kotlin and Java?

## Ответ (RU)
Методы equals() и hashCode() играют центральную роль в сравнении объектов и управлении ими в коллекциях. Метод equals(Object obj) определяет равенство объектов по содержимому вместо сравнения ссылок. Метод hashCode() возвращает хеш-код объекта для использования в хеш-таблицах. Соблюдение контракта между equals() и hashCode() критически важно для правильной работы коллекций, основанных на хеш-таблицах.

## Answer (EN)

The `equals()` and `hashCode()` methods play a central role in object comparison and management in collections:

**equals(Object obj) method:**
- Defines object equality based on content rather than reference comparison
- Allows logical comparison of objects instead of just memory address comparison
- Used by collections like `ArrayList`, `HashSet`, and `HashMap` to determine if objects are equal

**hashCode() method:**
- Returns an integer hash code for the object
- Used by hash-based collections like `HashMap`, `HashSet`, and `Hashtable`
- Provides efficient lookup in hash-table data structures
- Must be consistent with `equals()` to ensure correct collection behavior

**The contract between equals() and hashCode():**
Maintaining the contract between these methods is critically important for proper functioning of hash-based collections:

1. If two objects are equal according to `equals()`, they must return the same `hashCode()`
2. If two objects return the same `hashCode()`, they are not necessarily equal (hash collision)
3. If `equals()` is overridden, `hashCode()` must also be overridden
4. The hash code should remain constant if the object hasn't changed

### Code Examples

**Manual implementation:**
```kotlin
class Person(val name: String, val age: Int) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is Person) return false

        return name == other.name && age == other.age
    }

    override fun hashCode(): Int {
        var result = name.hashCode()
        result = 31 * result + age
        return result
    }
}

// Usage
fun main() {
    val person1 = Person("Alice", 30)
    val person2 = Person("Alice", 30)
    val person3 = Person("Bob", 25)

    println(person1 == person2)  // true (content equality)
    println(person1 === person2) // false (different references)
    println(person1.hashCode() == person2.hashCode())  // true

    // Works correctly in collections
    val set = hashSetOf(person1, person2, person3)
    println(set.size)  // 2 (person1 and person2 are considered equal)

    val map = hashMapOf(person1 to "Developer", person3 to "Designer")
    println(map[person2])  // "Developer" (finds using person2 as key)
}
```

**Using data class (automatic generation):**
```kotlin
data class Person(val name: String, val age: Int)

fun main() {
    val person1 = Person("Alice", 30)
    val person2 = Person("Alice", 30)

    println(person1 == person2)  // true
    println(person1.hashCode() == person2.hashCode())  // true

    // Automatically works correctly in all collections
    val set = hashSetOf(person1, person2)
    println(set.size)  // 1
}
```

**Problems without proper hashCode implementation:**
```kotlin
class BadPerson(val name: String, val age: Int) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is BadPerson) return false
        return name == other.name && age == other.age
    }
    // Missing hashCode() override!
}

fun main() {
    val person1 = BadPerson("Alice", 30)
    val person2 = BadPerson("Alice", 30)

    println(person1 == person2)  // true

    // HashMap won't work correctly!
    val map = hashMapOf(person1 to "Developer")
    println(map[person2])  // null! (should be "Developer")

    // HashSet won't work correctly!
    val set = hashSetOf(person1, person2)
    println(set.size)  // 2! (should be 1)
}
```

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-detect-unused-object--programming-languages--easy]]
- [[q-java-object-comparison--programming-languages--easy]]
-
