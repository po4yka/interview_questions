---
id: lang-072
title: "Equals Hashcode Contracts / Контракты equals и hashCode"
aliases: [Equals Hashcode Contracts, Контракты equals и hashCode]
topic: kotlin
subtopics: [collections, equality, object-methods]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-equality, c-kotlin]
created: 2025-10-15
updated: 2025-11-11
tags: [collections, contracts, difficulty/medium, equality, kotlin, object-methods]
---
# Вопрос (RU)
> Расскажи о контрактах `equals` и `hashCode`

---

# Question (EN)
> Tell me about `equals` and `hashCode` contracts

## Ответ (RU)

Методы `equals()` и `hashCode()` используются для:
- логического сравнения объектов;
- корректной работы в коллекциях, основанных на хеш-таблицах (`HashSet`, `HashMap`).

### Контракт equals()

Метод `equals()` должен удовлетворять следующим свойствам:

#### 1. Рефлексивность
Объект должен быть равен сам себе:
```kotlin
data class User(val name: String)

val user = User("John")
user.equals(user)  // Должно быть true
```

#### 2. Симметричность
Если `a` равно `b`, то `b` равно `a`:
```kotlin
data class User(val name: String)

val u1 = User("John")
val u2 = User("John")

u1.equals(u2) == u2.equals(u1)  // Должно быть true
```

#### 3. Транзитивность
Если `a` равно `b` и `b` равно `c`, то `a` равно `c`:
```kotlin
data class User(val name: String)

val u1 = User("John")
val u2 = User("John")
val u3 = User("John")

// Если u1 == u2 и u2 == u3, то u1 == u3
```

#### 4. Согласованность
Повторные вызовы должны возвращать один и тот же результат, пока значимые для равенства поля не меняются:
```kotlin
class User(var name: String)

val u1 = User("John")
val u2 = User("John")

u1.equals(u2)  // true
u1.equals(u2)  // всё ещё true

u1.name = "Jane"  // изменилось поле, влияющее на равенство
u1.equals(u2)      // теперь может быть false
```

#### 5. Сравнение С Null
Для любого ненулевого объекта сравнение с `null` должно возвращать `false`:
```kotlin
data class User(val name: String)

val user = User("John")
user.equals(null)  // Должно быть false
```

### Контракт hashCode()

Метод `hashCode()` должен удовлетворять:

#### 1. Стабильность Хеша
Пока объект не меняет поля, участвующие в `equals()`, значение `hashCode()` должно оставаться тем же:
```kotlin
data class User(val name: String)

val user = User("John")
val hash1 = user.hashCode()
val hash2 = user.hashCode()

hash1 == hash2  // Должно быть true
```

#### 2. Равные Объекты → Равные hashCode
Если `a.equals(b) == true`, то `a.hashCode() == b.hashCode()` (обязательное требование):
```kotlin
class User(val name: String, val age: Int) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is User) return false
        return name == other.name && age == other.age
    }

    override fun hashCode(): Int {
        var result = name.hashCode()
        result = 31 * result + age
        return result
    }
}

val u1 = User("John", 30)
val u2 = User("John", 30)

if (u1.equals(u2)) {
    u1.hashCode() == u2.hashCode()  // Должно быть true
}
```

#### 3. Неравные Объекты Могут Иметь Одинаковый hashCode (коллизии)
`a.hashCode() == b.hashCode()` не означает `a.equals(b)`:
```kotlin
class User(val name: String, val age: Int)

val u1 = User("John", 30)
val u2 = User("Jane", 30)

// Теоретически они могут иметь одинаковый hashCode, но при этом не быть равными
```

### Примеры Реализации

Ручная реализация (обычный класс):
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
```

Data-класс (автоматическая генерация):
```kotlin
data class Person(val name: String, val age: Int)
// equals() и hashCode() генерируются автоматически
// В расчёт берутся свойства из primary constructor
```

### Почему Это Важно Для Коллекций

Хеш-коллекции (`HashSet`, `HashMap`) полагаются на корректность `equals()` и `hashCode()`:
```kotlin
data class User(val name: String, val age: Int)

val user1 = User("John", 30)
val user2 = User("John", 30)

val set = hashSetOf(user1)
set.contains(user2)  // true, т.к. equals() и hashCode() согласованы

val map = hashMapOf(user1 to "data")
map[user2]  // Вернёт "data"
```

При нарушении контракта возможны «пропавшие» элементы, дубли и некорректная работа `contains`, `get` и других операций:
```kotlin
class BadUser(val name: String) {
    // Переопределён только equals, но не hashCode — НАРУШЕНИЕ КОНТРАКТА
    // HashSet/HashMap используют hashCode() для выбора бакета и equals() для сравнения внутри бакета
    override fun equals(other: Any?) = other is BadUser && name == other.name
}

val u1 = BadUser("John")
val u2 = BadUser("John")

u1.equals(u2)                 // true
u1.hashCode() == u2.hashCode()  // не гарантируется

val set = hashSetOf(u1)
set.contains(u2)  // Может вернуть false из-за разных hashCode()
```

### Рекомендации По Реализации

1. Всегда переопределяйте `equals()` и `hashCode()` вместе, когда определяете логическое равенство.
```kotlin
override fun equals(other: Any?): Boolean = ...
override fun hashCode(): Int = ...
```

2. Используйте один и тот же набор полей в `equals()` и `hashCode()`:
```kotlin
class User(val id: Int, val name: String) {
    override fun equals(other: Any?): Boolean {
        if (other !is User) return false
        return id == other.id  // Равенство только по id
    }

    override fun hashCode(): Int = id.hashCode()  // То же поле, что и в equals
}
```

3. По возможности предпочитайте `data class` — для них корректные `equals()` и `hashCode()` генерируются автоматически (для свойств primary constructor).

4. Для ручных реализаций используйте стабильную комбинацию хешей полей (часто умножение на 31, как в примерах выше). На JVM также можно использовать `java.util.Objects.hash(...)`, но в идиоматичном Kotlin обычно достаточно `data class` или явных комбинаций.

### Summary (RU)

- equals():
  - Рефлексивность: `a.equals(a) == true`.
  - Симметричность: `a.equals(b) == b.equals(a)`.
  - Транзитивность: `a == b` и `b == c` ⇒ `a == c`.
  - Согласованность: результат стабилен при неизменных значимых полях.
  - Сравнение с `null`: всегда `false`.
- hashCode():
  - Стабильность: один и тот же объект → тот же `hashCode` при неизменных значимых полях.
  - Из равенства следует равенство хешей: `a == b` ⇒ `hash(a) == hash(b)` (обязательное правило).
  - Обратное не требуется: одинаковый `hashCode` не гарантирует равенство объектов.

---

## Answer (EN)

The `equals()` and `hashCode()` methods are used for:
- logical object comparison;
- correct behavior in hash-based collections (`HashSet`, `HashMap`).

### equals() Contract

The `equals()` method must satisfy these properties:

#### 1. Reflexivity
An object must equal itself:
```kotlin
data class User(val name: String)

val user = User("John")
user.equals(user)  // Must be true
```

#### 2. Symmetry
If a equals b, then b equals a:
```kotlin
data class User(val name: String)

val u1 = User("John")
val u2 = User("John")

u1.equals(u2) == u2.equals(u1)  // Must be true
```

#### 3. Transitivity
If a equals b and b equals c, then a equals c:
```kotlin
data class User(val name: String)

val u1 = User("John")
val u2 = User("John")
val u3 = User("John")

// If u1 == u2 and u2 == u3, then u1 == u3
```

#### 4. Consistency
Multiple invocations return the same result as long as equality-significant fields do not change:
```kotlin
class User(var name: String)

val u1 = User("John")
val u2 = User("John")

u1.equals(u2)  // true
u1.equals(u2)  // still true

u1.name = "Jane"  // equality-significant field changed
u1.equals(u2)      // now may be false
```

#### 5. Null Comparison
Comparison with null always returns false for non-null references:
```kotlin
data class User(val name: String)

val user = User("John")
user.equals(null)  // Must be false
```

### hashCode() Contract

The `hashCode()` method must satisfy:

#### 1. Consistent Hash
If the object does not change its equality-significant fields, the hash code stays the same:
```kotlin
data class User(val name: String)

val user = User("John")
val hash1 = user.hashCode()
val hash2 = user.hashCode()

hash1 == hash2  // Must be true
```

#### 2. Equal Objects Have Equal Hash Codes
If `a.equals(b)`, then `a.hashCode() == b.hashCode()` (must hold):
```kotlin
class User(val name: String, val age: Int) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is User) return false
        return name == other.name && age == other.age
    }

    override fun hashCode(): Int {
        var result = name.hashCode()
        result = 31 * result + age
        return result
    }
}

val u1 = User("John", 30)
val u2 = User("John", 30)

if (u1.equals(u2)) {
    u1.hashCode() == u2.hashCode()  // Must be true
}
```

#### 3. Unequal Objects May Have Equal Hash Codes (Collision)
`a.hashCode() == b.hashCode()` does not imply `a.equals(b)`:
```kotlin
class User(val name: String, val age: Int)

val u1 = User("John", 30)
val u2 = User("Jane", 30)

// These can legally have the same hash code even if not equal
```

### Implementation Examples

Manual implementation (non-data class):
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
```

Data class (automatic):
```kotlin
data class Person(val name: String, val age: Int)
// equals() and hashCode() are generated automatically
// Only properties in the primary constructor are used
```

### Why This Matters for Collections

Hash-based collections rely on these contracts:
```kotlin
data class User(val name: String, val age: Int)

val user1 = User("John", 30)
val user2 = User("John", 30)

// HashSet uses hashCode() and equals()
val set = hashSetOf(user1)
set.contains(user2)  // true (because equals() and hashCode() are consistent)

// HashMap uses hashCode() for bucket, equals() for exact match
val map = hashMapOf(user1 to "data")
map[user2]  // Returns "data" (because user1 == user2)
```

Without proper implementation:
```kotlin
class BadUser(val name: String) {
    // Only overrides equals, not hashCode - VIOLATION OF CONTRACT
    // HashSet/HashMap use hashCode() to pick a bucket and equals() to compare within a bucket
    override fun equals(other: Any?) = other is BadUser && name == other.name
}

val u1 = BadUser("John")
val u2 = BadUser("John")

u1.equals(u2)          // true
u1.hashCode() == u2.hashCode()  // not guaranteed, may be false

val set = hashSetOf(u1)
set.contains(u2)  // May be false due to different hashCode() values
```

### Implementation Tips

1. Always override both together when defining logical equality:
```kotlin
override fun equals(other: Any?): Boolean = ...
override fun hashCode(): Int = ...
```

2. Use the same set of properties in both equals() and hashCode():
```kotlin
class User(val id: Int, val name: String) {
    override fun equals(other: Any?): Boolean {
        if (other !is User) return false
        return id == other.id  // Equality based only on id
    }

    override fun hashCode(): Int = id.hashCode()  // Same property as in equals
}
```

3. Prefer data classes when applicable:
```kotlin
data class User(val name: String, val age: Int)
// Correct equals() and hashCode() are generated for constructor properties
```

4. Use a stable hash code combination for manual implementations:
```kotlin
override fun hashCode(): Int {
    var result = property1.hashCode()
    result = 31 * result + property2.hashCode()
    result = 31 * result + property3.hashCode()
    return result
}

// On JVM you can also use java.util.Objects.hash(...),
// but idiomatic Kotlin often relies on data classes or custom combinations.
```

### Summary (EN)

- equals():
  - Reflexivity: `a.equals(a) == true`.
  - Symmetry: `a.equals(b) == b.equals(a)`.
  - Transitivity: `a == b` and `b == c` ⇒ `a == c`.
  - Consistency: stable result while significant fields do not change.
  - Null comparison: always `false`.
- hashCode():
  - Consistency: same object → same hash code while significant fields unchanged.
  - Equality implies hash equality: `a == b` ⇒ `hash(a) == hash(b)` (must hold).
  - Hash equality does not imply object equality.

---

## Дополнительные Вопросы (RU)

- В чём ключевые отличия контрактов в контексте Java и Kotlin?
- Где на практике особенно важно корректно реализовывать `equals()` и `hashCode()`?
- Какие типичные ошибки при переопределении этих методов?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- Официальная документация Kotlin: https://kotlinlang.org/docs/home.html
- [[c-kotlin]]
- [[c-equality]]

## References

- Kotlin Documentation: https://kotlinlang.org/docs/home.html
- [[c-kotlin]]
- [[c-equality]]

## Связанные Вопросы (RU)

- [[q-equals-hashcode-purpose--kotlin--hard]]

## Related Questions

- [[q-equals-hashcode-purpose--kotlin--hard]]
