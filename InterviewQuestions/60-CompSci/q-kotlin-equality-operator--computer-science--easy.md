---
id: cs-009
title: "Kotlin Equality Operator / Оператор равенства в Kotlin"
aliases: []
topic: computer-science
subtopics: [access-modifiers, null-safety, type-system]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-kotlin-any-unit-nothing--programming-languages--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [difficulty/easy]
---

# Что Происходит Когда Делаешь ==?

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

### Kotlin Vs Java

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
```

### Распространенные Ошибки

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

### Практические Примеры Использования

**Пример 1: Сравнение data классов**
```kotlin
data class User(val id: Int, val name: String, val email: String)

val user1 = User(1, "Иван", "ivan@example.com")
val user2 = User(1, "Иван", "ivan@example.com")
val user3 = user1

// Структурное равенство - сравнивает все поля
println(user1 == user2)  // true - все поля одинаковы
println(user1 === user2) // false - разные объекты в памяти
println(user1 === user3) // true - один и тот же объект

// Data класс автоматически генерирует equals()
// который сравнивает все свойства из primary constructor
```

**Пример 2: Обычные классы требуют переопределения equals()**
```kotlin
// БЕЗ переопределения equals()
class Person(val name: String, val age: Int)

val person1 = Person("Анна", 25)
val person2 = Person("Анна", 25)

println(person1 == person2)  // false - использует default equals() (сравнение ссылок)
println(person1 === person2) // false - разные объекты

// С переопределением equals()
class PersonWithEquals(val name: String, val age: Int) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is PersonWithEquals) return false
        return name == other.name && age == other.age
    }

    override fun hashCode(): Int {
        var result = name.hashCode()
        result = 31 * result + age
        return result
    }
}

val p1 = PersonWithEquals("Анна", 25)
val p2 = PersonWithEquals("Анна", 25)

println(p1 == p2)  // true - custom equals сравнивает name и age
println(p1 === p2) // false - все еще разные объекты
```

**Пример 3: Безопасность от null**
```kotlin
val s1: String? = null
val s2: String? = null
val s3: String? = "Привет"
val s4: String? = "Привет"

// == безопасен к null
println(s1 == s2)  // true - оба null
println(s1 == s3)  // false - один null, другой нет
println(s3 == s4)  // true - одинаковое содержимое

// В Java это вызвало бы NullPointerException:
// s1.equals(s2)  // NPE!
```

**Пример 4: Коллекции и равенство**
```kotlin
val list1 = listOf(1, 2, 3)
val list2 = listOf(1, 2, 3)
val list3 = mutableListOf(1, 2, 3)

// Структурное равенство - сравнивает содержимое
println(list1 == list2)  // true - одинаковое содержимое
println(list1 == list3)  // true - содержимое одинаково

// Референсное равенство - сравнивает объекты
println(list1 === list2) // false - разные объекты
println(list1 === list3) // false - разные объекты

// Работает с map, set и т.д.
val map1 = mapOf("a" to 1, "b" to 2)
val map2 = mapOf("a" to 1, "b" to 2)
println(map1 == map2)   // true
println(map1 === map2)  // false
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
    // when использует == (структурное равенство)
}

// Сравнение объектов
sealed class State
object Loading : State()
object Success : State()
data class Error(val message: String) : State()

fun handleState(state: State) {
    when (state) {
        is Loading -> println("Загрузка...")
        is Success -> println("Успешно")
        is Error -> println("Ошибка: ${state.message}")
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

// Использование
processValue("special")     // Специальная строка
processValue(150)           // Большое число
processValue(emptyList<Int>()) // Пустой список
```

**Пример 7: Кастомная реализация equals для сложной логики**
```kotlin
data class Product(
    val id: Int,
    val name: String,
    val price: Double,
    val metadata: Map<String, String>
) {
    // Переопределяем equals для игнорирования metadata
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is Product) return false

        // Сравниваем только id, name, price (игнорируем metadata)
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

val product1 = Product(1, "Ноутбук", 1000.0, mapOf("color" to "black"))
val product2 = Product(1, "Ноутбук", 1000.0, mapOf("color" to "white"))

println(product1 == product2)  // true - metadata игнорируется
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

// contains использует == (equals)
println(students.contains(searchStudent))  // true

// indexOf также использует ==
println(students.indexOf(searchStudent))   // 1

// remove в MutableList использует ==
val mutableStudents = students.toMutableList()
mutableStudents.remove(searchStudent)      // Удалит студента с id=2
println(mutableStudents.size)              // 2

// Set использует equals и hashCode
val studentSet = setOf(
    Student(1, "Иван"),
    Student(2, "Мария"),
    Student(1, "Иван")  // Дубликат - не будет добавлен
)
println(studentSet.size)  // 2
```

**Пример 9: Сравнение с nullable типами**
```kotlin
fun compareNullable(a: String?, b: String?) {
    // Безопасное сравнение
    when {
        a == null && b == null -> println("Оба null")
        a == null -> println("Только a null")
        b == null -> println("Только b null")
        a == b -> println("Равны: $a")
        else -> println("Разные: $a vs $b")
    }
}

compareNullable(null, null)         // Оба null
compareNullable("test", null)       // Только b null
compareNullable("test", "test")     // Равны: test
compareNullable("test", "other")    // Разные: test vs other
```

**Пример 10: Проверка identity в кэше**
```kotlin
class Cache<K, V> {
    private val cache = mutableMapOf<K, V>()

    fun put(key: K, value: V) {
        cache[key] = value
    }

    fun get(key: K): V? = cache[key]

    // Проверка что значение то же самое (не копия)
    fun isSameInstance(key: K, value: V): Boolean {
        val cached = cache[key]
        return cached === value  // Референсное сравнение
    }

    // Проверка что содержимое одинаково
    fun hasEqualValue(key: K, value: V): Boolean {
        val cached = cache[key]
        return cached == value  // Структурное сравнение
    }
}

// Использование
val cache = Cache<String, List<Int>>()
val list1 = listOf(1, 2, 3)
val list2 = listOf(1, 2, 3)

cache.put("data", list1)

println(cache.isSameInstance("data", list1))  // true - тот же объект
println(cache.isSameInstance("data", list2))  // false - другой объект
println(cache.hasEqualValue("data", list2))   // true - одинаковое содержимое
```

### Важные Замечания

1. **Data классы автоматически генерируют equals()** - сравнивают все свойства из primary constructor
2. **Обычные классы требуют ручного переопределения** equals() и hashCode()
3. **== всегда null-safe** - не нужны дополнительные проверки
4. **=== полезен для оптимизации** - быстрая проверка identity перед дорогим equals()
5. **Collections используют equals()** - важно правильно реализовать для корректной работы Set, Map
6. **hashCode() должен соответствовать equals()** - если equals() говорит что объекты равны, hashCode() должен быть одинаковым

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

## Related Questions

- [[q-kotlin-any-unit-nothing--programming-languages--medium]]
- [[q-callback-to-coroutine-conversion--kotlin--medium]]
- [[q-inheritance-open-final--kotlin--medium]]
