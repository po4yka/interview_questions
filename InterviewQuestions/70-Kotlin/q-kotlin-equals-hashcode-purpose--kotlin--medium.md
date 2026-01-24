---
id: lang-087
title: Kotlin Equals Hashcode Purpose / Назначение equals и hashCode в Kotlin
aliases:
- Kotlin Equals Hashcode Purpose
- Назначение equals и hashCode в Kotlin
topic: kotlin
subtopics:
- collections
- equality
- hash-tables
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-equality
- c-kotlin
- q-launch-vs-async--kotlin--easy
- q-semaphore-rate-limiting--kotlin--medium
created: 2025-10-15
updated: 2025-11-10
tags:
- collections
- difficulty/medium
- equals
- hashcode
- kotlin
- object-comparison
anki_cards:
- slug: lang-087-0-en
  language: en
  anki_id: 1768326293732
  synced_at: '2026-01-23T17:03:51.610011'
- slug: lang-087-0-ru
  language: ru
  anki_id: 1768326293756
  synced_at: '2026-01-23T17:03:51.610845'
---
# Вопрос (RU)
> Зачем нужны методы equals и hashCode?

---

# Question (EN)
> Why do we need equals and hashCode methods?

## Ответ (RU)

Методы `equals()` и `hashCode()` в Kotlin определяют, как объекты сравниваются между собой и как они ведут себя в коллекциях, особенно в хеш-коллекциях. Корректное соблюдение контракта между этими методами критически важно для предсказуемой и корректной работы таких структур.

**Зачем нужен equals():**

- Определяет логическое (структурное) равенство по содержимому, а не только сравнение по ссылке.
- Оператор `==` в Kotlin делегирует вызов методу `equals()`, поэтому переопределение `equals()` напрямую влияет на поведение `==`. Для обычных классов, не переопределяющих `equals()`, используется реализация `Any.equals()`, которая по умолчанию сравнивает ссылки.
- Используется методами коллекций (`contains`, `indexOf` и т.п.) для проверки логического равенства.

**Зачем нужен hashCode():**

- Возвращает целочисленный хеш-код, который используется для размещения объекта в хеш-таблицах (`HashSet`, `HashMap` и т.п.).
- Позволяет эффективно находить элементы в хеш-структурах.

**Контракт между equals() и hashCode():**

```kotlin
// Правило 1: если equals() возвращает true, hashCode() ОБЯЗАН возвращать одно и то же значение.
if (obj1 == obj2) {
    obj1.hashCode() == obj2.hashCode()  // Должно быть true
}

// Правило 2: одинаковый hashCode() не гарантирует equals() == true (возможны коллизии).
if (obj1.hashCode() == obj2.hashCode()) {
    obj1 == obj2  // Может быть true или false
}
```

Если контракт нарушен, хеш-коллекции работают некорректно (поиск, вставка, `contains` и т.д.). Это критично для таких структур, как `HashSet`, `HashMap`, `LinkedHashSet`.

**Использование в коллекциях:**

```kotlin
data class Person(val name: String, val age: Int)

val person1 = Person("John", 30)
val person2 = Person("John", 30)

// Для обычных классов без переопределения equals() реализация Any.equals() по умолчанию
// выполняет сравнение по ссылке, поэтому `==` ведет себя как сравнение ссылок.
// Для data class Kotlin генерирует equals() по свойствам, поэтому `==` сравнивает содержимое.
person1 == person2  // true: одинаковое содержимое
```

```kotlin
val set = HashSet<Person>()
set.add(Person("Alice", 25))

// hashCode() определяет корзину в хеш-таблице, equals() — фактическое совпадение элемента.
// Для data class hashCode() генерируется согласованно с equals().
val contains = set.contains(Person("Alice", 25))
// contains == true при согласованных equals() и hashCode().
```

```kotlin
// `HashMap` полагается на hashCode() + equals()
val map = HashMap<Person, String>()
map[Person("John", 30)] = "Engineer"

// Поиск ключа:
// 1. hashCode() для выбора корзины
// 2. equals() для точного совпадения ключа
val job = map[Person("John", 30)]  // "Engineer"
```

**Data class: авто-генерация equals() и hashCode():**

```kotlin
data class User(val id: Int, val name: String)

val user1 = User(1, "Alice")
val user2 = User(1, "Alice")

user1 == user2  // true — equals() по свойствам
user1.hashCode() == user2.hashCode()  // true — согласованный hashCode()
```

**Ручная реализация (обычный класс):**

```kotlin
class Book(val isbn: String, val title: String) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is Book) return false
        return isbn == other.isbn  // Сравнение только по ISBN
    }

    override fun hashCode(): Int {
        return isbn.hashCode()  // Хеш только по ISBN, согласован с equals()
    }
}
```

**Поведение различных коллекций (обзор):**

- `HashSet` — использует `hashCode()` для разбиения по корзинам и `equals()` для проверки равенства элементов.
- `HashMap` — использует `hashCode()` для ключей и `equals()` для сравнения ключей внутри корзины.
- `LinkedHashSet` — как `HashSet`, плюс запоминает порядок вставки.
- `ArrayList` — не использует `hashCode()`, поиск (`contains`, `indexOf`) идёт по `equals()` линейным проходом.
- `TreeSet` — не использует `hashCode()`, полагается на `Comparable`/`Comparator`: порядок и "равенство" определяются результатом `compare()`.

**Итог:**

- `equals()` определяет логическое равенство объектов по содержимому.
- `hashCode()` даёт хеш для эффективной работы хеш-структур.
- Если `equals()` возвращает `true`, `hashCode()` обязан быть одинаковым.
- Особенно важно для `HashSet`, `HashMap`, `LinkedHashSet` и других хеш-коллекций.
- В `data class` оба метода автоматически генерируются на основе свойств первичного конструктора.

## Answer (EN)

Methods `equals()` and `hashCode()` in Kotlin define how objects are compared and how they behave in collections, especially hash-based ones. Correctly following their contract is critical for predictable behavior.

**Why equals() is needed:**

- Defines logical (structural) equality by content instead of just reference comparison.
- The `==` operator in Kotlin delegates to `equals()`, so overriding `equals()` directly affects `==`. For ordinary classes that do not override `equals()`, the default `Any.equals()` implementation performs reference comparison.
- Used by collection methods like `contains`, `indexOf`, etc., for logical equality checks.

**Why hashCode() is needed:**

- Returns an integer hash code used to place objects into hash tables (`HashSet`, `HashMap`, etc.).
- Enables efficient lookup in hash-based data structures.

**Contract between equals() and hashCode():**

```kotlin
// Rule 1: If equals() returns true, hashCode() MUST return the same value.
if (obj1 == obj2) {
    obj1.hashCode() == obj2.hashCode()  // MUST be true
}

// Rule 2: If hashCode() is the same, equals() MAY be true or false (hash collision).
if (obj1.hashCode() == obj2.hashCode()) {
    obj1 == obj2  // May be true or false
}
```

If this contract is violated, hash-based collections (lookup, insert, `contains`, etc.) behave incorrectly.

**Using in collections (Person example):**

```kotlin
data class Person(val name: String, val age: Int)

val person1 = Person("John", 30)
val person2 = Person("John", 30)

// For ordinary classes without overriding equals(), the default Any.equals()
// implementation does reference comparison, so `==` behaves as reference equality.
// For data classes, Kotlin auto-generates equals() to compare properties, so `==` checks content.
person1 == person2  // true: same content
```

**Using in collections (`HashSet` example):**

```kotlin
val set = HashSet<Person>()
set.add(Person("Alice", 25))

// Hash code determines the bucket in the hash table; equals() checks actual element equality.
// For data classes, hashCode() is auto-generated consistently with equals().
val contains = set.contains(Person("Alice", 25))
// contains == true, because equals() and hashCode() are consistent.
```

**Using in collections (`HashMap` example):**

```kotlin
// `HashMap` relies on hashCode() + equals()
val map = HashMap<Person, String>()
map[Person("John", 30)] = "Engineer"

// Lookup uses:
// 1. hashCode() to find bucket
// 2. equals() to find the exact key
val job = map[Person("John", 30)]  // "Engineer"
```

**Data class auto-generates both:**

```kotlin
data class User(val id: Int, val name: String)

val user1 = User(1, "Alice")
val user2 = User(1, "Alice")

user1 == user2  // true - equals() auto-generated based on properties
user1.hashCode() == user2.hashCode()  // true - hashCode() auto-generated consistently
```

**Manual implementation (non-data class):**

```kotlin
class Book(val isbn: String, val title: String) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is Book) return false
        return isbn == other.isbn  // Compare by ISBN only
    }

    override fun hashCode(): Int {
        return isbn.hashCode()  // Hash by ISBN only, consistent with equals()
    }
}
```

**Hash-based and other collections (behavior overview):**

- `HashSet` — uses `hashCode()` for bucketing and `equals()` to check element equality.
- `HashMap` — uses `hashCode()` for keys and `equals()` to compare keys within the bucket.
- `LinkedHashSet` — same as `HashSet`, plus preserves insertion order.
- `ArrayList` — does not use `hashCode()`; `contains`/`indexOf` perform a linear search using `equals()`.
- `TreeSet` — does not use `hashCode()`; relies on `Comparable`/`Comparator`: ordering and "equality" are defined via `compare()`.

**Summary:**

- `equals()` defines how to compare objects by content (logical equality).
- `hashCode()` provides a hash value for efficient use in hash-based collections.
- Contract: if `equals()` is true, `hashCode()` must be equal.
- Critical for: `HashSet`, `HashMap`, `LinkedHashSet` and similar.
- `data class` automatically generates consistent `equals()` and `hashCode()` based on primary constructor properties.

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия контракта `equals()/hashCode()` в Kotlin по сравнению с Java?
- В каких практических сценариях особенно важно корректно переопределять эти методы?
- Какие типичные ошибки при реализации `equals()` и `hashCode()` приводят к багам в коллекциях?

## Follow-ups

- What are the key differences between the `equals()/hashCode()` contract in Kotlin and Java?
- In which practical scenarios is it especially important to override these methods correctly?
- What typical mistakes in implementing `equals()` and `hashCode()` lead to bugs in collections?

## Ссылки (RU)

- Официальная документация Kotlin: "https://kotlinlang.org/docs/home.html"
- См. также: [[c-kotlin]], [[c-equality]]

## References

- Kotlin Documentation: "https://kotlinlang.org/docs/home.html"
- See also: [[c-kotlin]], [[c-equality]]

## Связанные Вопросы (RU)

- [[q-semaphore-rate-limiting--kotlin--medium]]
- [[q-launch-vs-async--kotlin--easy]]

## Related Questions

- [[q-semaphore-rate-limiting--kotlin--medium]]
- [[q-launch-vs-async--kotlin--easy]]
