---
id: kotlin-195
title: "Equals Hashcode Purpose / Назначение equals и hashCode"
aliases: [Equals, Hashcode, Object Comparison]
topic: kotlin
subtopics: [collections, equality, object-comparison]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-kotlin-map-flatmap--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [difficulty/medium, equality, hashmap, kotlin, object-comparison]
date created: Friday, October 31st 2025, 6:29:04 pm
date modified: Tuesday, November 25th 2025, 8:53:52 pm
---
# Вопрос (RU)
> Зачем нужны методы equals() и hashCode() в Kotlin/Java?

# Question (EN)
> Why are equals() and hashCode() methods needed in Kotlin/Java?

## Ответ (RU)

Методы `equals()` и `hashCode()` играют центральную роль в сравнении объектов и управлении ими в коллекциях. См. также [[c-kotlin]] и [[c-equality]].

### equals(Object obj)

Определяет равенство объектов по содержимому вместо сравнения ссылок.

В Kotlin оператор `==` вызывает метод `equals()` (структурное равенство), а оператор `===` сравнивает ссылки (референсное равенство). Поэтому, если вы не переопределяете `equals()` (как в обычном классе), используется реализация из `Any`, которая сравнивает ссылки.

**Без переопределения equals()**:

```kotlin
class User(val name: String, val age: Int)

val user1 = User("Alice", 30)
val user2 = User("Alice", 30)

println(user1 == user2)  // false (используется Any.equals -> сравнение ссылок)
println(user1 === user2) // false (разные ссылки)
```

**С переопределением equals()** (автоматически в data class):

```kotlin
data class User(val name: String, val age: Int)

val user1 = User("Alice", 30)
val user2 = User("Alice", 30)

println(user1 == user2)  // true (equals() сгенерирован по свойствам)
println(user1 === user2) // false (разные ссылки)
```

### hashCode()

Возвращает хеш-код объекта для использования в хеш-таблицах (`HashMap`, `HashSet` и т.д.). Важно, чтобы реализация `hashCode()` была согласована с `equals()`.

**Пример использования в `HashMap`**:

```kotlin
data class User(val name: String, val age: Int)

val users = HashMap<User, String>()
users[User("Alice", 30)] = "Engineer"

// Поиск работает, потому что hashCode() и equals() согласованы:
// равные объекты имеют одинаковый hashCode()
println(users[User("Alice", 30)])  // "Engineer"
```

### Контракт Между equals() И hashCode()

**Критически важно соблюдать**:

1. Если `a.equals(b)` возвращает `true`, то `a.hashCode()` должен равняться `b.hashCode()`.
2. Если `a.equals(b)` возвращает `false`, то `a.hashCode()` может быть одинаковым или разным (коллизии допустимы).
3. При корректной реализации, если `a.hashCode() != b.hashCode()`, то `a.equals(b)` обязан возвращать `false` (равные объекты не могут иметь разные хеши).

```kotlin
val user1 = User("Alice", 30)
val user2 = User("Alice", 30)

if (user1 == user2) {
    // hashCode() должен быть одинаковым
    assert(user1.hashCode() == user2.hashCode())
}
```

### Проблемы При Нарушении Контракта

**Неправильная реализация** (пример, аналогичный EN-версии, с одним полем):

```kotlin
class BrokenUser(val name: String) {
    override fun equals(other: Any?): Boolean {
        if (other !is BrokenUser) return false
        return name == other.name
    }

    // НЕ переопределён hashCode()!
}

val map = HashMap<BrokenUser, String>()
val user1 = BrokenUser("Alice")
map[user1] = "Engineer"

val user2 = BrokenUser("Alice")
println(map[user2])  // null ← ОШИБКА! Не найдётся, хотя user1 == user2
```

**Правильная реализация**:

```kotlin
class CorrectUser(val name: String, val age: Int) {
    override fun equals(other: Any?): Boolean {
        if (other !is CorrectUser) return false
        return name == other.name && age == other.age
    }

    override fun hashCode(): Int {
        var result = name.hashCode()
        result = 31 * result + age
        return result
    }
}

// Или просто используйте data class:
// equals() и hashCode() генерируются автоматически по свойствам
// первичного конструктора.
data class User(val name: String, val age: Int)
```

### Использование В Коллекциях

```kotlin
data class User(val name: String, val age: Int)

// HashSet использует hashCode() и equals() для определения уникальности
val users = hashSetOf<User>()
users.add(User("Alice", 30))
users.add(User("Alice", 30))  // Не добавится (дубликат)
println(users.size)  // 1

// HashMap использует hashCode() для индексации и equals() для проверки ключей
val userRoles = hashMapOf<User, String>()
userRoles[User("Alice", 30)] = "Engineer"
println(userRoles[User("Alice", 30)])  // "Engineer"
```

## Answer (EN)

`equals()` and `hashCode()` are fundamental for object equality and correct behavior in collections. See also [[c-kotlin]] and [[c-equality]].

### equals(Object obj)

Defines equality by content instead of by reference.

In Kotlin, `==` calls `.equals()` (structural equality), and `===` checks reference equality. If you do not override `equals()` in your class, the implementation from `Any` is used, which is reference-based.

**Without overriding equals()**:

```kotlin
class User(val name: String, val age: Int)

val user1 = User("Alice", 30)
val user2 = User("Alice", 30)

println(user1 == user2)  // false (Any.equals -> reference comparison)
println(user1 === user2) // false (different references)
```

**With overridden equals()** (automatically in a data class):

```kotlin
data class User(val name: String, val age: Int)

val user1 = User("Alice", 30)
val user2 = User("Alice", 30)

println(user1 == user2)  // true (equals() generated from properties)
println(user1 === user2) // false (different references)
```

### hashCode()

Returns a hash code used in hash-based collections (`HashMap`, `HashSet`, etc.). It must be consistent with `equals()`.

**Example usage in `HashMap`**:

```kotlin
data class User(val name: String, val age: Int)

val users = HashMap<User, String>()
users[User("Alice", 30)] = "Engineer"

// Lookup works because hashCode() and equals() are consistent:
// equal objects have the same hashCode()
println(users[User("Alice", 30)])  // "Engineer"
```

### Key Contract

1. If `a.equals(b)` is `true`, then `a.hashCode()` must be equal to `b.hashCode()`.
2. If `a.equals(b)` is `false`, their hash codes may be the same or different (collisions are allowed).
3. With a correct implementation, if `a.hashCode() != b.hashCode()`, then `a.equals(b)` must be `false` (equal objects cannot have different hash codes).

```kotlin
val user1 = User("Alice", 30)
val user2 = User("Alice", 30)

if (user1 == user2) {
    // hashCode() must be the same
    assert(user1.hashCode() == user2.hashCode())
}
```

Violating these rules breaks the behavior of hash-based collections.

### Problems when the Contract is Violated

**Broken implementation**:

```kotlin
class User(val name: String) {
    override fun equals(other: Any?) = (other as? User)?.name == name
    // Missing hashCode()! HashMap/HashSet lookups may fail.
}

val map = hashMapOf<User, String>()
map[User("Alice")] = "Engineer"
println(map[User("Alice")])  // null - broken
```

**Correct implementation / idiomatic Kotlin**:

```kotlin
// Manual implementation
class CorrectUser(val name: String, val age: Int) {
    override fun equals(other: Any?): Boolean {
        if (other !is CorrectUser) return false
        return name == other.name && age == other.age
    }

    override fun hashCode(): Int {
        var result = name.hashCode()
        result = 31 * result + age
        return result
    }
}

// Idiomatic: use a data class.
// equals() and hashCode() are generated automatically
// based on primary constructor properties.
data class User(val name: String, val age: Int)
```

### Usage in Collections

```kotlin
data class User(val name: String, val age: Int)

// HashSet uses hashCode() and equals() to determine uniqueness
val users = hashSetOf<User>()
users.add(User("Alice", 30))
users.add(User("Alice", 30))  // Duplicate; will not be added
println(users.size)  // 1

// HashMap uses hashCode() for indexing and equals() to compare keys
val userRoles = hashMapOf<User, String>()
userRoles[User("Alice", 30)] = "Engineer"
println(userRoles[User("Alice", 30)])  // "Engineer"
```

---

## Дополнительные Вопросы (RU)

- В чём ключевые отличия контракта equals()/hashCode() в Kotlin и Java?
- Когда на практике необходимо явно переопределять эти методы?
- Какие распространённые ошибки при реализации equals()/hashCode()?

## Follow-ups

- What are the key differences between the contract in Kotlin and Java?
- When do you need to explicitly override these methods in practice?
- What are common mistakes in implementing equals()/hashCode()?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-kotlin-sealed-classes-purpose--kotlin--medium]]
- [[q-kotlin-map-flatmap--kotlin--medium]]

## Related Questions

- [[q-kotlin-sealed-classes-purpose--kotlin--medium]]
- [[q-kotlin-map-flatmap--kotlin--medium]]
