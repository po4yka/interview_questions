---
id: lang-083
title: Equals Hashcode Purpose / Назначение equals и hashCode
aliases:
- Equals Hashcode Purpose
- Назначение equals и hashCode
topic: kotlin
subtopics:
- collections
- equality
- object-methods
question_kind: theory
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-equality
created: 2025-10-15
updated: 2025-11-10
tags:
- collections
- contracts
- difficulty/hard
- equality
- kotlin
- object-methods
anki_cards:
- slug: lang-083-0-en
  language: en
  anki_id: 1768326285856
  synced_at: '2026-01-23T17:03:51.031941'
- slug: lang-083-0-ru
  language: ru
  anki_id: 1768326285882
  synced_at: '2026-01-23T17:03:51.034245'
---
# Вопрос (RU)
> Зачем нужны методы `equals()` и `hashCode()` в Kotlin и Java?

# Question (EN)
> Why are `equals()` and `hashCode()` methods needed in Kotlin and Java?

## Ответ (RU)
Методы `equals()` и `hashCode()` играют ключевую роль в сравнении объектов и работе коллекций.

`equals(Object other)`:
- Определяет логическое равенство объектов по их содержимому, а не только по ссылкам.
- Используется коллекциями (например, `List` при `contains`, `remove`, `indexOf`, а также `Set` и `Map`) для определения, считаются ли два объекта равными.

`hashCode()`:
- Возвращает целочисленный хеш-код объекта.
- Используется хеш-коллекциями (такими как `HashMap`, `HashSet`, `Hashtable`) для эффективного размещения и поиска элементов.

Критично важно соблюдать контракт между `equals()` и `hashCode()`:
1. Если два объекта равны с точки зрения `equals()`, они обязаны возвращать одинаковый `hashCode()`.
2. Обратное неверно: одинаковый `hashCode()` не гарантирует равенство (возможны коллизии).
3. Если переопределяется `equals()`, почти всегда необходимо переопределить и `hashCode()` таким образом, чтобы оба метода были согласованы.
4. Значение `hashCode()` должно оставаться постоянным в рамках одного запуска программы, пока остаются неизменными значения полей, участвующих в `equals()`/`hashCode()`. Изменение таких полей для объекта, находящегося в хеш-коллекции, приводит к некорректной работе операций поиска и удаления.

### Примеры Кода (RU)

Ручная реализация:
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

// Пример использования
fun main() {
    val person1 = Person("Alice", 30)
    val person2 = Person("Alice", 30)
    val person3 = Person("Bob", 25)

    println(person1 == person2)  // true (логическое равенство по содержимому)
    println(person1 === person2) // false (разные ссылки)
    println(person1.hashCode() == person2.hashCode())  // true

    // Корректная работа в коллекциях
    val set = hashSetOf(person1, person2, person3)
    println(set.size)  // 2 (person1 и person2 считаются равными)

    val map = hashMapOf(person1 to "Developer", person3 to "Designer")
    println(map[person2])  // "Developer" (поиск по ключу person2)
}
```

Использование data class (автоматическая генерация):
```kotlin
data class Person(val name: String, val age: Int)

fun main() {
    val person1 = Person("Alice", 30)
    val person2 = Person("Alice", 30)

    println(person1 == person2)  // true
    println(person1.hashCode() == person2.hashCode())  // true

    // Автоматически корректная работа в хеш-коллекциях
    val set = hashSetOf(person1, person2)
    println(set.size)  // 1
}
```

Проблемы без корректной реализации `hashCode`:
```kotlin
class BadPerson(val name: String, val age: Int) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is BadPerson) return false
        return name == other.name && age == other.age
    }
    // Нет переопределения hashCode()!
}

fun main() {
    val person1 = BadPerson("Alice", 30)
    val person2 = BadPerson("Alice", 30)

    println(person1 == person2)  // true

    val map = hashMapOf(person1 to "Developer")
    println(map[person2])  // null (поиск ломается, так как hashCode не согласован с equals)

    val set = hashSetOf(person1, person2)
    println(set.size)  // 2 (объекты хранятся отдельно, несмотря на equals() == true)
}
```

Эти примеры показывают, почему согласованная реализация `equals()` и `hashCode()` критична для корректной и эффективной работы хеш-коллекций.

## Answer (EN)

The `equals()` and `hashCode()` methods play a central role in object comparison and how objects behave in collections.

`equals(Object other)` method:
- Defines logical equality of objects based on their content rather than just reference identity.
- Used by many collections (e.g., `List` for `contains`, `remove`, `indexOf`, and also `Set` and `Map`) to decide whether two elements or keys/values are considered equal.

`hashCode()` method:
- Returns an integer hash code for the object.
- Used by hash-based collections like `HashMap`, `HashSet`, and `Hashtable` to place and look up elements efficiently.

The contract between `equals()` and `hashCode()` is critically important for correct behavior of hash-based collections:

1. If two objects are equal according to `equals()`, they must return the same `hashCode()`.
2. If two objects have the same `hashCode()`, they are not necessarily equal (hash collisions are possible).
3. If `equals()` is overridden, `hashCode()` must also be overridden in a way that is consistent with it.
4. The hash code must remain consistent within a single execution of the program as long as the fields used in `equals()`/`hashCode()` remain unchanged. Mutating those fields while the object is used as a key in a hash-based collection can break lookups and removals.

### Code Examples (EN)

Manual implementation:
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

Using data class (automatic generation):
```kotlin
data class Person(val name: String, val age: Int)

fun main() {
    val person1 = Person("Alice", 30)
    val person2 = Person("Alice", 30)

    println(person1 == person2)  // true
    println(person1.hashCode() == person2.hashCode())  // true

    // Automatically works correctly in hash-based collections
    val set = hashSetOf(person1, person2)
    println(set.size)  // 1
}
```

Problems without proper `hashCode` implementation:
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

    val map = hashMapOf(person1 to "Developer")
    println(map[person2])  // null (lookup fails because hashCode is not consistent with equals)

    val set = hashSetOf(person1, person2)
    println(set.size)  // 2 (both instances stored separately despite equals() returning true)
}
```

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия реализации и использования `equals()`/`hashCode()` в Kotlin и Java?
- Когда на практике важно правильно переопределять эти методы и учитывать контракт `equals()`/`hashCode()`?
- Какие распространенные ошибки связаны с нарушением контракта `equals()`/`hashCode()` при работе с коллекциями?

## Follow-ups

- What are the key differences in how `equals()`/`hashCode()` are implemented and used in Kotlin vs Java?
- When is it important in practice to correctly override these methods and respect the `equals()`/`hashCode()` contract?
- What common mistakes occur when violating the `equals()`/`hashCode()` contract when working with collections?

## Ссылки (RU)

- [[c-equality]]
- [Документация Kotlin]("https://kotlinlang.org/docs/home.html")

## References

- [[c-equality]]
- [Kotlin Documentation]("https://kotlinlang.org/docs/home.html")

## Связанные Вопросы (RU)

- [[q-detect-unused-object--kotlin--easy]]
- [[q-java-object-comparison--kotlin--easy]]

## Related Questions

- [[q-detect-unused-object--kotlin--easy]]
- [[q-java-object-comparison--kotlin--easy]]
