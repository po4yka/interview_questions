---
id: 20251012-12271111138
title: "Kotlin Java Equality Operators / Операторы равенства Kotlin и Java"
topic: computer-science
difficulty: medium
status: draft
moc: moc-kotlin
related: [q-kotlin-partition-function--programming-languages--easy, q-kotlin-null-checks-methods--programming-languages--easy, q-kotlin-non-inheritable-class--programming-languages--easy]
created: 2025-10-15
tags:
  - comparison
  - equality
  - java
  - kotlin
  - operators
  - programming-languages
---
# Чем отличаются двойное равно в Java и Kotlin?

# Question (EN)
> What is the difference between double equals in Java and Kotlin?

# Вопрос (RU)
> Чем отличаются двойное равно в Java и Kotlin?

---

## Answer (EN)


Kotlin has two equality operators: `==` for structural equality and `===` for referential equality, differing from Java's behavior.

### Structural Equality (`==`)
Compares values (calls `equals()`):
```kotlin
val a = "Hello"
val b = "Hello"
println(a == b)  // true (same content)

data class Person(val name: String)
val p1 = Person("Alice")
val p2 = Person("Alice")
println(p1 == p2)  // true (data classes auto-implement equals)
```

### Referential Equality (`===`)
Compares references (same object):
```kotlin
val a = "Hello"
val b = "Hello"
println(a === b)  // true (string pooling)

val p1 = Person("Alice")
val p2 = Person("Alice")
println(p1 === p2)  // false (different objects)

val p3 = p1
println(p1 === p3)  // true (same reference)
```

### Comparison with Java

| Operation | Kotlin | Java |
|-----------|--------|------|
| Value equality | `==` | `.equals()` |
| Reference equality | `===` | `==` |
| Null-safe comparison | `==` | Manual null check |

### Java Interop
```kotlin
// Java code
String s1 = new String("Hello");
String s2 = new String("Hello");

// In Kotlin
s1 == s2   // true (calls equals())
s1 === s2  // false (different objects)

// In Java
s1.equals(s2)  // true
s1 == s2       // false
```

### Null Safety
```kotlin
val a: String? = null
val b: String? = null

a == b   // true (both null)
a === b  // true (both null reference)

a == "text"  // false (null-safe, doesn't throw NPE)
```

### Best Practices
- Use `==` for value comparison
- Use `===` only when you need reference equality
- For collections, `==` compares contents
- Data classes provide structural equality automatically

---
---

## Ответ (RU)


Kotlin имеет два оператора равенства: `==` для структурного равенства и `===` для ссылочного равенства, отличаясь от поведения Java.

### Структурное равенство (`==`)
Сравнивает значения (вызывает `equals()`):
```kotlin
val a = "Hello"
val b = "Hello"
println(a == b)  // true (одинаковое содержимое)

data class Person(val name: String)
val p1 = Person("Alice")
val p2 = Person("Alice")
println(p1 == p2)  // true (data классы авто-реализуют equals)
```

### Ссылочное равенство (`===`)
Сравнивает ссылки (тот же объект):
```kotlin
val a = "Hello"
val b = "Hello"
println(a === b)  // true (string pooling)

val p1 = Person("Alice")
val p2 = Person("Alice")
println(p1 === p2)  // false (разные объекты)

val p3 = p1
println(p1 === p3)  // true (та же ссылка)
```

### Сравнение с Java

| Операция | Kotlin | Java |
|----------|--------|------|
| Равенство значений | `==` | `.equals()` |
| Равенство ссылок | `===` | `==` |
| Null-safe сравнение | `==` | Ручная проверка null |

### Java Interop
```kotlin
// Java код
String s1 = new String("Hello");
String s2 = new String("Hello");

// В Kotlin
s1 == s2   // true (вызывает equals())
s1 === s2  // false (разные объекты)

// В Java
s1.equals(s2)  // true
s1 == s2       // false
```

### Null безопасность
```kotlin
val a: String? = null
val b: String? = null

a == b   // true (оба null)
a === b  // true (оба null ссылка)

a == "text"  // false (null-safe, не выбрасывает NPE)
```

### Лучшие практики
- Используйте `==` для сравнения значений
- Используйте `===` только когда нужно равенство ссылок
- Для коллекций `==` сравнивает содержимое
- Data классы предоставляют структурное равенство автоматически

---

## Related Questions

- [[q-kotlin-partition-function--programming-languages--easy]]
- [[q-kotlin-null-checks-methods--programming-languages--easy]]
- [[q-kotlin-non-inheritable-class--programming-languages--easy]]

