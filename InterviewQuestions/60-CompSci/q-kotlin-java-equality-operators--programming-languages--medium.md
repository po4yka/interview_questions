---
tags:
  - comparison
  - equality
  - java
  - kotlin
  - operators
  - programming-languages
difficulty: medium
---

# Чем отличаются двойное равно в Java и Kotlin?

**English**: What is the difference between double equals in Java and Kotlin?

## Answer

In Java and Kotlin, `==` has different semantics:

### Java

- `==` checks **reference equality** (same object in memory)
- `.equals()` checks **structural equality** (same values)

```java
String a = new String("hello");
String b = new String("hello");

a == b           // false (different references)
a.equals(b)      // true (same values)
```

### Kotlin

- `==` checks **structural equality** (calls `.equals()` under the hood)
- `===` checks **reference equality** (same object in memory)

```kotlin
val a = "hello"
val b = "hello"

a == b           // true (structural equality)
a === b          // true (string interning)

val c = StringBuilder("hello").toString()
a == c           // true (same values)
a === c          // false (different objects)
```

**Comparison table:**

| Purpose | Java | Kotlin |
|---------|------|--------|
| Reference equality | `==` | `===` |
| Structural equality | `.equals()` | `==` |
| Null-safe comparison | Manual null checks | Built-in (`==` handles null) |

**Key difference**: Kotlin's `==` is null-safe - `null == null` is true!

## Ответ

В Java оператор == проверяет, указывают ли две переменные на один и тот же объект в памяти. Для сравнения значений строк используется метод equals(). В Kotlin оператор == сравнивает значения объектов аналогично методу equals() в Java, а для сравнения ссылок используется оператор ===.

