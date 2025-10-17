---
id: "20251015082237179"
title: "Kotlin Equality Operator / Оператор равенства в Kotlin"
topic: computer-science
difficulty: easy
status: draft
created: 2025-10-15
tags: - equality
  - equals
  - kotlin
  - operators
  - programming-languages
  - referential-equality
  - structural-equality
---
# Что происходит когда делаешь ==?

# Question (EN)
> What happens when you do ==?

# Вопрос (RU)
> Что происходит когда делаешь ==?

---

## Answer (EN)

In Kotlin, the `==` operator is used for **structural equality** (comparing contents). It calls the `equals()` method under the hood.

### Structural Equality (`==`)

**Compares object contents:**

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

**What actually happens:**

```kotlin
// When you write:
a == b

// Kotlin translates to:
a?.equals(b) ?: (b === null)

// Which means:
// - If a is not null, call a.equals(b)
// - If a is null, check if b is also null
```

### Null Safety

**`==` is null-safe:**

```kotlin
val a: String? = null
val b: String? = null
val c: String? = "Hello"

a == b  // true (both null)
a == c  // false (one is null)
c == a  // false (one is null)

// No NullPointerException!
```

**Compare to Java:**
```java
// Java - manual null check needed
String a = null;
String b = "Hello";

// a.equals(b)  // NullPointerException!

// Must check null first
if (a != null && a.equals(b)) {
    // ...
}

// Or use Objects.equals()
Objects.equals(a, b);  // Safe
```

### Referential Equality (`===`)

**For reference comparison, use `===`:**

```kotlin
val user1 = User("John", 30)
val user2 = User("John", 30)
val user3 = user1

// Structural equality (contents)
user1 == user2   // true (same contents)

// Referential equality (same object in memory)
user1 === user2  // false (different objects)
user1 === user3  // true (same object)
```

### Comparison Table

| Operator | Purpose | Null-safe | Equivalent |
|----------|---------|-----------|------------|
| `==` | Structural equality (contents) | Yes | `a?.equals(b) ?: (b === null)` |
| `!=` | Structural inequality | Yes | `!(a == b)` |
| `===` | Referential equality (same object) | Yes | Compare references |
| `!==` | Referential inequality | Yes | `!(a === b)` |

### Examples

**1. Strings:**
```kotlin
val s1 = "Hello"
val s2 = "Hello"
val s3 = String(charArrayOf('H', 'e', 'l', 'l', 'o'))

s1 == s2   // true (same content)
s1 === s2  // true (string pool - same object)

s1 == s3   // true (same content)
s1 === s3  // false (different objects)
```

**2. Data classes:**
```kotlin
data class Point(val x: Int, val y: Int)

val p1 = Point(1, 2)
val p2 = Point(1, 2)
val p3 = p1

p1 == p2   // true (data class auto-generates equals)
p1 === p2  // false (different instances)
p1 === p3  // true (same instance)
```

**3. Regular classes:**
```kotlin
class Person(val name: String)

val person1 = Person("John")
val person2 = Person("John")

person1 == person2  // false (default equals() compares references)
person1 === person2 // false (different objects)

// To get content comparison, override equals()
class PersonWithEquals(val name: String) {
    override fun equals(other: Any?) =
        other is PersonWithEquals && other.name == name

    override fun hashCode() = name.hashCode()
}

val p1 = PersonWithEquals("John")
val p2 = PersonWithEquals("John")
p1 == p2  // true (custom equals checks content)
```

**4. Collections:**
```kotlin
val list1 = listOf(1, 2, 3)
val list2 = listOf(1, 2, 3)
val list3 = list1

list1 == list2   // true (same contents)
list1 === list2  // false (different list objects)
list1 === list3  // true (same reference)
```

### Kotlin vs Java

**Kotlin:**
```kotlin
val a = "Hello"
val b = "Hello"

// Structural equality (compares contents)
a == b  // true

// Referential equality (compares references)
a === b  // true (string pool)
```

**Java:**
```java
String a = "Hello";
String b = "Hello";

// Reference equality (compares references!)
a == b  // true (string pool)

// Structural equality (compares contents)
a.equals(b)  // true

// For objects
Person p1 = new Person("John");
Person p2 = new Person("John");

p1 == p2       // false (different objects)
p1.equals(p2)  // Depends on equals() implementation
```

### Custom equals() Implementation

```kotlin
class User(val id: Int, val name: String) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true  // Same object
        if (other !is User) return false  // Type check

        // Compare properties
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

user1 == user2  // true (custom equals compares id and name)
```

### Common Pitfalls

**1. Forgetting to override equals():**
```kotlin
class Person(val name: String)  // No equals() override

val p1 = Person("John")
val p2 = Person("John")

p1 == p2  // false! (uses default equals() which compares references)

// Solution: use data class or override equals()
```

**2. Overriding equals() without hashCode():**
```kotlin
class Bad(val value: Int) {
    override fun equals(other: Any?) =
        other is Bad && other.value == value
    // Missing hashCode()! Violates contract!
}

val set = hashSetOf(Bad(1))
set.contains(Bad(1))  // May be false! HashSet broken!
```

**3. Using === when you mean ==:**
```kotlin
val s1 = String(charArrayOf('H', 'i'))
val s2 = String(charArrayOf('H', 'i'))

s1 === s2  // false (different objects)
s1 == s2   // true (same content) 
```

### Summary

**`==` operator in Kotlin:**
- Calls `equals()` method
- Compares object **contents** (structural equality)
- Null-safe by design
- Different from Java's `==` (which compares references)

**For reference comparison:**
- Use `===` (referential equality)
- Checks if two variables point to same object

---

## Ответ (RU)

В Kotlin оператор `==` используется для **структурного равенства** (сравнение содержимого). Он вызывает метод `equals()` под капотом.

### Структурное равенство (`==`)

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

### Безопасность от null

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

### Референсное равенство (`===`)

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

### Таблица сравнения

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

### Kotlin vs Java

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
```

### Распространенные ошибки

**1. Забыть переопределить equals():**
```kotlin
class Person(val name: String)  // Нет переопределения equals()

val p1 = Person("John")
val p2 = Person("John")

p1 == p2  // false! (использует default equals() который сравнивает ссылки)

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
- Проверяет указывают ли две переменные на один объект

**Ключевое различие от Java:**
- Kotlin `==` = Java `.equals()`
- Kotlin `===` = Java `==`

