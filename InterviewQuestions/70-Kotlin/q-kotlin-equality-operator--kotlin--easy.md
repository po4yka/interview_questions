---
id: lang-208
title: "Kotlin Equality Operator / Оператор равенства в Kotlin"
aliases: []
topic: kotlin
subtopics: [null-safety, type-system]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-concepts--kotlin--medium, q-callback-to-coroutine-conversion--kotlin--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [difficulty/easy]

date created: Saturday, November 1st 2025, 1:26:21 pm
date modified: Tuesday, November 25th 2025, 8:53:54 pm
---
# Вопрос (RU)
> Что происходит когда делаешь ==?

# Question (EN)
> What happens when you do ==?

---

## Ответ (RU)

В Kotlin оператор `==` используется для **структурного равенства** (сравнение содержимого). Он вызывает метод `equals()` под капотом.

### Структурное Равенство (`==`)

**Сравнивает содержимое объектов:**

```kotlin
data class User(val name: String, val age: Int)

val user1 = User("John", 30)
val user2 = User("John", 30)
val user3 = User("Jane", 25)

// == вызывает метод equals()
user1 == user2  // true (одинаковое содержимое)
user1 == user3  // false (разное содержимое)

// Эквивалентно:
user1.equals(user2)  // true
```

**Что происходит на самом деле:**

```kotlin
// Когда вы пишете:
a == b

// Kotlin транслирует в:
a?.equals(b) ?: (b === null)

// Что означает:
// - Если a не null, вызвать a.equals(b)
// - Если a null, проверить является ли b тоже null
```

### Безопасность От Null

**`==` безопасен к null:**

```kotlin
val a: String? = null
val b: String? = null
val c: String? = "Hello"

a == b  // true (оба null)
a == c  // false (один null)
c == a  // false (один null)

// Нет NullPointerException!
```

**Сравнение с Java:**
```java
// Java - нужна ручная проверка на null
String a = null;
String b = "Hello";

// a.equals(b)  // NullPointerException!

// Нужно сначала проверить null
if (a != null && a.equals(b)) {
    // ...
}

// Или использовать Objects.equals()
Objects.equals(a, b);  // Безопасно
```

### Референсное Равенство (`===`)

**Для сравнения ссылок используйте `===`:**

```kotlin
val user1 = User("John", 30)
val user2 = User("John", 30)
val user3 = user1

// Структурное равенство (содержимое)
user1 == user2   // true (одинаковое содержимое)

// Референсное равенство (один объект в памяти)
user1 === user2  // false (разные объекты)
user1 === user3  // true (один и тот же объект)
```

### Таблица Сравнения

| Оператор | Назначение | Null-safe | Эквивалент |
|----------|------------|-----------|------------|
| `==` | Структурное равенство (содержимое) | Да | `a?.equals(b) ?: (b === null)` |
| `!=` | Структурное неравенство | Да | `!(a == b)` |
| `===` | Референсное равенство (один объект) | Да | Сравнение ссылок |
| `!==` | Референсное неравенство | Да | `!(a === b)` |

### Примеры

**1. Строки:**
```kotlin
val s1 = "Hello"
val s2 = "Hello"
val s3 = String(charArrayOf('H', 'e', 'l', 'l', 'o'))

s1 == s2   // true (одинаковое содержимое)
s1 === s2  // true (string pool - один объект)

s1 == s3   // true (одинаковое содержимое)
s1 === s3  // false (разные объекты)
```

**2. Data классы:**
```kotlin
data class Point(val x: Int, val y: Int)

val p1 = Point(1, 2)
val p2 = Point(1, 2)
val p3 = p1

p1 == p2   // true (data class автогенерирует equals)
p1 === p2  // false (разные экземпляры)
p1 === p3  // true (один экземпляр)
```

**3. Обычные классы:**
```kotlin
class Person(val name: String)

val person1 = Person("John")
val person2 = Person("John")

person1 == person2  // false (default equals() сравнивает ссылки)
person1 === person2 // false (разные объекты)

// Для сравнения содержимого переопределите equals()
class PersonWithEquals(val name: String) {
    override fun equals(other: Any?) =
        other is PersonWithEquals && other.name == name

    override fun hashCode() = name.hashCode()
}

val p1 = PersonWithEquals("John")
val p2 = PersonWithEquals("John")
p1 == p2  // true (custom equals проверяет содержимое)
```

**4. Коллекции:**
```kotlin
val list1 = listOf(1, 2, 3)
val list2 = listOf(1, 2, 3)
val list3 = list1

list1 == list2   // true (одинаковое содержимое)
list1 === list2  // false (разные объекты списков)
list1 === list3  // true (одна ссылка)
```

### Kotlin Vs Java

**Kotlin:**
```kotlin
val a = "Hello"
val b = "Hello"

// Структурное равенство (сравнивает содержимое)
a == b  // true

// Референсное равенство (сравнивает ссылки)
a === b  // true (string pool)
```

**Java:**
```java
String a = "Hello";
String b = "Hello";

// Равенство ссылок (сравнивает ссылки!)
a == b  // true (string pool)

// Структурное равенство (сравнивает содержимое)
a.equals(b)  // true

// Для объектов
Person p1 = new Person("John");
Person p2 = new Person("John");

p1 == p2;       // false (разные объекты)
p1.equals(p2);  // зависит от реализации equals()
```

### Custom equals() / Кастомная Реализация equals()

```kotlin
class User(val id: Int, val name: String) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true  // тот же объект
        if (other !is User) return false  // проверка типа

        // сравнение свойств
        return id == other.id && name == other.name
    }

    override fun hashCode(): Int {
        var result = id.hashCode()
        result = 31 * result + name.hashCode()
        return result
    }
}

val user1 = User(1, "John")
val user2 = User(1, "John")

user1 == user2  // true (custom equals сравнивает id и name)
```

### Распространенные Ошибки

**1. Забыть переопределить equals():**
```kotlin
class Person(val name: String)  // Нет переопределения equals()

val p1 = Person("John")
val p2 = Person("John")

p1 == p2  // false! (использует default equals(), который сравнивает ссылки)

// Решение: используйте data class или переопределите equals()
```

**2. Переопределить equals() без hashCode():**
```kotlin
class Bad(val value: Int) {
    override fun equals(other: Any?) =
        other is Bad && other.value == value
    // Отсутствует hashCode()! Нарушает контракт!
}

val set = hashSetOf(Bad(1))
set.contains(Bad(1))  // Может быть false! HashSet сломан!
```

**3. Использовать === когда имеется в виду ==:**
```kotlin
val s1 = String(charArrayOf('H', 'i'))
val s2 = String(charArrayOf('H', 'i'))

s1 === s2  // false (разные объекты)
s1 == s2   // true (одинаковое содержимое)
```

### Резюме

**Оператор `==` в Kotlin:**
- Вызывает метод `equals()`
- Сравнивает **содержимое** объектов (структурное равенство)
- Безопасен к null по дизайну
- Отличается от Java `==` (который сравнивает ссылки)

**Для сравнения ссылок:**
- Используйте `===` (референсное равенство)
- Проверяет, указывают ли две переменные на один объект

**Ключевое различие от Java: **
- Kotlin `==` соответствует Java `.equals()`
- Kotlin `===` соответствует Java `==`

### Практические Примеры Использования

**Пример 1: Сравнение data классов**
```kotlin
data class User(val id: Int, val name: String, val email: String)

val user1 = User(1, "Иван", "ivan@example.com")
val user2 = User(1, "Иван", "ivan@example.com")
val user3 = user1

println(user1 == user2)  // true - все поля одинаковы
println(user1 === user2) // false - разные объекты в памяти
println(user1 === user3) // true - один и тот же объект
```

**Пример 2: Обычные классы требуют переопределения equals()**
```kotlin
class Person2(val name: String, val age: Int)

val personA = Person2("Анна", 25)
val personB = Person2("Анна", 25)

println(personA == personB)  // false - сравнение ссылок

class PersonWithEquals2(val name: String, val age: Int) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is PersonWithEquals2) return false
        return name == other.name && age == other.age
    }

    override fun hashCode(): Int {
        var result = name.hashCode()
        result = 31 * result + age
        return result
    }
}

val pa = PersonWithEquals2("Анна", 25)
val pb = PersonWithEquals2("Анна", 25)
println(pa == pb)  // true
```

**Пример 3: Безопасность от null**
```kotlin
val s1: String? = null
val s2: String? = null
val s3: String? = "Привет"
val s4: String? = "Привет"

println(s1 == s2)  // true
println(s1 == s3)  // false
println(s3 == s4)  // true
```

**Пример 4: Коллекции и равенство**
```kotlin
val listA = listOf(1, 2, 3)
val listB = listOf(1, 2, 3)
val listC = mutableListOf(1, 2, 3)

println(listA == listB)  // true
println(listA == listC)  // true
println(listA === listB) // false
println(listA === listC) // false
```

**Пример 5: Сравнение в when выражении**
```kotlin
fun processCommand(command: String) {
    when (command) {
        "start" -> println("Запуск")
        "stop" -> println("Остановка")
        "pause" -> println("Пауза")
        else -> println("Неизвестная команда")
    }
}
```

**Пример 6: Проверка типа с is и сравнение**
```kotlin
fun processValue(value: Any) {
    when {
        value is String && value == "special" ->
            println("Специальная строка")
        value is Int && value > 100 ->
            println("Большое число")
        value is List<*> && value.isEmpty() ->
            println("Пустой список")
        else -> println("Другое значение")
    }
}
```

**Пример 7: Кастомная реализация equals для сложной логики**
```kotlin
data class Product(val id: Int, val name: String, val price: Double, val metadata: Map<String, String>) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is Product) return false
        return id == other.id &&
               name == other.name &&
               price == other.price
    }

    override fun hashCode(): Int {
        var result = id
        result = 31 * result + name.hashCode()
        result = 31 * result + price.hashCode()
        return result
    }
}
```

**Пример 8: Сравнение в Collections**
```kotlin
data class Student(val id: Int, val name: String)

val students = listOf(
    Student(1, "Иван"),
    Student(2, "Мария"),
    Student(3, "Петр")
)

val searchStudent = Student(2, "Мария")

println(students.contains(searchStudent))  // true
println(students.indexOf(searchStudent))   // 1
```

**Пример 9: Сравнение с nullable типами**
```kotlin
fun compareNullable(a: String?, b: String?) {
    when {
        a == null && b == null -> println("Оба null")
        a == null -> println("Только a null")
        b == null -> println("Только b null")
        a == b -> println("Равны: $a")
        else -> println("Разные: $a vs $b")
    }
}
```

**Пример 10: Проверка identity в кэше**
```kotlin
class Cache<K, V> {
    private val cache = mutableMapOf<K, V>()

    fun put(key: K, value: V) {
        cache[key] = value
    }

    fun get(key: K): V? = cache[key]

    fun isSameInstance(key: K, value: V): Boolean {
        val cached = cache[key]
        return cached === value
    }

    fun hasEqualValue(key: K, value: V): Boolean {
        val cached = cache[key]
        return cached == value
    }
}
```

### Важные Замечания

1. Data классы автоматически генерируют `equals()` и `hashCode()`.
2. Обычные классы требуют ручного переопределения `equals()` и `hashCode()`.
3. `==` всегда null-safe.
4. `===` полезен, когда важно сравнить именно ссылки.
5. Коллекции используют `equals()` для поиска и сравнения элементов.
6. Контракт: если `equals()` говорит, что объекты равны, их `hashCode()` должен совпадать.

### Таблица Quick Reference

| Сценарий | Оператор | Пример |
|----------|----------|--------|
| Сравнение значений | `==` | `"hello" == "hello"` → true |
| Проверка null | `==` | `null == null` → true |
| Сравнение ссылок | `===` | `obj1 === obj2` |
| Неравенство значений | `!=` | `5 != 3` → true |
| Неравенство ссылок | `!==` | `obj1 !== obj2` |
| В коллекциях | `contains()` | Использует `==` |
| В when | `when(x)` | Использует `==` |

---

## Answer (EN)

In Kotlin, the `==` operator is used for structural equality (comparing contents). It calls the `equals()` method under the hood.

### Structural Equality (`==`)

```kotlin
data class User(val name: String, val age: Int)

val user1 = User("John", 30)
val user2 = User("John", 30)
val user3 = User("Jane", 25)

// == calls equals() method
user1 == user2  // true (same content)
user1 == user3  // false (different content)

// Equivalent to:
user1.equals(user2)  // true
```

When you write `a == b`, Kotlin translates it to:

```kotlin
a?.equals(b) ?: (b === null)
```

- If `a` is not null, it calls `a.equals(b)`.
- If `a` is null, it checks whether `b` is also null.

### Null Safety

```kotlin
val a: String? = null
val b: String? = null
val c: String? = "Hello"

a == b  // true (both null)
a == c  // false (one is null)
c == a  // false (one is null)
```

No `NullPointerException` is thrown when using `==`.

In Java:

```java
String a = null;
String b = "Hello";

// a.equals(b);  // NullPointerException!

if (a != null && a.equals(b)) {
    // ...
}

Objects.equals(a, b);  // Safe
```

### Referential Equality (`===`)

Use `===` to compare references (identity):

```kotlin
val user1 = User("John", 30)
val user2 = User("John", 30)
val user3 = user1

user1 == user2   // true (same contents)
user1 === user2  // false (different objects)
user1 === user3  // true (same object)
```

### Comparison Table

| Operator | Purpose | Null-safe | Equivalent |
|----------|---------|-----------|------------|
| `==` | Structural equality (contents) | Yes | `a?.equals(b) ?: (b === null)` |
| `!=` | Structural inequality | Yes | `!(a == b)` |
| `===` | Referential equality (same object) | Yes | compare references |
| `!==` | Referential inequality | Yes | `!(a === b)` |

### Examples

1. Strings

```kotlin
val s1 = "Hello"
val s2 = "Hello"
val s3 = String(charArrayOf('H', 'e', 'l', 'l', 'o'))

s1 == s2   // true (same content)
s1 === s2  // true (may be same instance due to pooling)

s1 == s3   // true (same content)
s1 === s3  // false (different objects)
```

1. Data classes

```kotlin
data class Point(val x: Int, val y: Int)

val p1 = Point(1, 2)
val p2 = Point(1, 2)
val p3 = p1

p1 == p2   // true (auto-generated equals compares properties)
p1 === p2  // false (different instances)
p1 === p3  // true (same instance)
```

1. Regular classes

```kotlin
class Person(val name: String)

val person1 = Person("John")
val person2 = Person("John")

person1 == person2  // false (default equals compares references)
person1 === person2 // false (different objects)

class PersonWithEquals(val name: String) {
    override fun equals(other: Any?) =
        other is PersonWithEquals && other.name == name

    override fun hashCode() = name.hashCode()
}

val p1 = PersonWithEquals("John")
val p2 = PersonWithEquals("John")

p1 == p2  // true (custom equals checks content)
```

1. Collections

```kotlin
val list1 = listOf(1, 2, 3)
val list2 = listOf(1, 2, 3)
val list3 = list1

list1 == list2   // true (same contents)
list1 === list2  // false (different instances)
list1 === list3  // true (same reference)
```

### Kotlin Vs Java Mapping

- In Kotlin, `==` corresponds to Java `.equals()` (content/structural equality).
- In Kotlin, `===` corresponds to Java `==` (reference equality).

### Custom equals() Implementation

```kotlin
class User(val id: Int, val name: String) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is User) return false
        return id == other.id && name == other.name
    }

    override fun hashCode(): Int {
        var result = id.hashCode()
        result = 31 * result + name.hashCode()
        return result
    }
}

val userA = User(1, "John")
val userB = User(1, "John")

userA == userB  // true
```

### Common Pitfalls

1. Forgetting to override `equals()` (and `hashCode()`) in regular classes when logical equality is needed.
2. Overriding `equals()` without a consistent `hashCode()` breaks collections like `HashSet` and `HashMap`.
3. Using `===` when you intend to compare values; use `==` for structural equality.

### Practical Usage Examples

1. Comparing data classes

```kotlin
data class User(val id: Int, val name: String, val email: String)

val u1 = User(1, "John", "john@example.com")
val u2 = User(1, "John", "john@example.com")
val u3 = u1

u1 == u2   // true (all properties equal)
u1 === u2  // false (different instances)
u1 === u3  // true (same instance)
```

1. Regular classes require equals()

```kotlin
class Person2(val name: String, val age: Int)

val a = Person2("Anna", 25)
val b = Person2("Anna", 25)

a == b    // false (reference-based)
```

1. Null-safety with `==`

```kotlin
val s1: String? = null
val s2: String? = null
val s3: String? = "Hi"

s1 == s2   // true
s1 == s3   // false
s3 == "Hi" // true
```

1. Collections and equality

```kotlin
val listA = listOf(1, 2, 3)
val listB = listOf(1, 2, 3)
val listC = listA

listA == listB   // true
listA === listB  // false
listA === listC  // true
```

1. Use in when expressions

```kotlin
fun handle(command: String) {
    when (command) {
        "start" -> println("Start")
        "stop" -> println("Stop")
        else -> println("Unknown")
    }
}
```

1. Type checks combined with equality

```kotlin
fun inspect(value: Any) {
    when {
        value is String && value == "ok" -> println("OK string")
        value is Int && value > 0 -> println("Positive int")
        else -> println("Something else")
    }
}
```

1. Custom equals for domain-specific logic

```kotlin
data class Product(val id: Int, val name: String, val price: Double, val metadata: Map<String, String>) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is Product) return false
        return id == other.id &&
               name == other.name &&
               price == other.price
    }

    override fun hashCode(): Int {
        var result = id
        result = 31 * result + name.hashCode()
        result = 31 * result + price.hashCode()
        return result
    }
}
```

1. Collections use `==`

```kotlin
data class Student(val id: Int, val name: String)

val students = listOf(
    Student(1, "Ivan"),
    Student(2, "Maria")
)

val search = Student(2, "Maria")

students.contains(search)  // true (uses == / equals)
```

1. Nullable comparisons helper

```kotlin
fun compareNullable(a: String?, b: String?) {
    when {
        a == null && b == null -> println("Both null")
        a == null -> println("Only a is null")
        b == null -> println("Only b is null")
        a == b -> println("Equal: $a")
        else -> println("Different: $a vs $b")
    }
}
```

1. Identity check in cache

```kotlin
class Cache<K, V> {
    private val cache = mutableMapOf<K, V>()

    fun put(key: K, value: V) {
        cache[key] = value
    }

    fun get(key: K): V? = cache[key]

    fun isSameInstance(key: K, value: V): Boolean {
        val cached = cache[key]
        return cached === value
    }

    fun hasEqualValue(key: K, value: V): Boolean {
        val cached = cache[key]
        return cached == value
    }
}
```

### Important Notes

1. Data classes auto-generate `equals()` and `hashCode()` based on primary constructor properties.
2. Regular classes need manual `equals()` and `hashCode()` when logical equality is required.
3. `==` is always null-safe in Kotlin.
4. `===` is useful when you truly care about object identity.
5. Collections (`Set`, `Map`, `List` operations) rely on `equals()` (and `hashCode()` for hash-based collections).
6. Collections use `equals()` (and thus `==`) for operations like `contains()` and lookups in sets/maps.

### Quick Reference Table

| Scenario | Operator | Example |
|----------|----------|---------|
| Compare values | `==` | `"hello" == "hello"` → true |
| Check nulls | `==` | `null == null` → true |
| Compare references | `===` | `obj1 === obj2` |
| Value inequality | `!=` | `5 != 3` → true |
| Reference inequality | `!==` | `obj1 !== obj2` |
| Collections | `==` / `equals()` | `list1 == list2` compares contents; `contains()` uses `==` |
| when expressions | `==` | `when(x) { "a" -> ... }` uses `==` |

---

## Дополнительные Вопросы (RU)

- Как работает равенство для чисел с плавающей точкой в Kotlin?
- Каковы потенциальные подводные камни при переопределении `equals()` и `hashCode()`?
- Как ведет себя равенство для изменяемых коллекций?

## Follow-ups

- How does equality work for floating-point numbers in Kotlin?
- What are potential pitfalls when overriding `equals()` and `hashCode()`?
- How does equality behave for mutable collections?

## Ссылки (RU)

- [[c-concepts--kotlin--medium]]
- Официальная документация Kotlin: "Equality in Kotlin" (https://kotlinlang.org/docs/equality.html)

## References

- [[c-concepts--kotlin--medium]]
- Official Kotlin docs: "Equality in Kotlin" (https://kotlinlang.org/docs/equality.html)

## Связанные Вопросы (RU)

- [[q-callback-to-coroutine-conversion--kotlin--medium]]

## Related Questions

- [[q-callback-to-coroutine-conversion--kotlin--medium]]
