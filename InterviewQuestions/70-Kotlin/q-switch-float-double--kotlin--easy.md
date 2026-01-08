---\
id: lang-092
title: "Switch Float Double / Switch float double"
aliases: [Switch float double, Switch Float Double]
topic: kotlin
subtopics: [language-features, switch-statement, type-system]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-kotlin-type-system-features--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [difficulty/easy]
---\
# Вопрос (RU)

> Работает ли switch() с double/float?

# Question (EN)

> Does switch() work with double/float?

---

## Ответ (RU)

Нет, в Java switch не работает с float и double. Для классического switch-выражения разрешены только целочисленные типы:

- byte, short, char, int;
- соответствующие классы-обёртки (`Byte`, `Short`, Character, Integer) с auto-unboxing;
- enum;
- `String` (Java 7+).

long, float, double, boolean не поддерживаются в switch-выражениях: это определено спецификацией языка, где требуется точное совпадение значений, что проблематично для floating-point чисел. long и boolean также не поддерживаются в классическом switch.

## Answer (EN)

**No**, in Java `switch` does **not** work with `float` and `double`.

This is defined by the language: for the classic `switch` statement, Java only allows integral types (`byte`, `short`, `char`, `int`), their wrappers, `enum`, and `String` as selector types. `long`, `float`, `double`, `boolean`, and arbitrary reference types are not permitted.

Precision and comparison concerns with floating-point numbers are one of the practical reasons why using them for `case` labels (which require exact equality) is undesirable, but the restriction itself is a compile-time type rule.

### Why Floating-Point is Problematic for Exact Matching

**Floating-point numbers have precision characteristics** that can make equality comparisons surprising:

```java
double x = 0.1 + 0.2;  // 0.30000000000000004
double y = 0.3;        // 0.3

System.out.println(x == y);  // false
```

```java
double a = 0.1;

double sum = 0.0;
for (int i = 0; i < 10; i++) {
    sum += a;
}

System.out.println(sum);        // 0.9999999999999999
System.out.println(sum == 1.0); // false
```

Since `switch` requires exact matches of the selector value to `case` labels, such behavior would be error-prone for many real-world floating-point use cases.

### What Types Does switch() Support?

In standard Java (up to current versions), `switch` supports:

```java
// - Primitive integral types
byte b = 1;
switch (b) { /* ... */ }

short s = 1;
switch (s) { /* ... */ }

int i = 1;
switch (i) { /* ... */ }

char c = 'A';
switch (c) { /* ... */ }

// - Wrapper types (auto-unboxing)
Integer num = 1;
switch (num) { /* ... */ }

// - Enum types
enum Day { MONDAY, TUESDAY }
Day day = Day.MONDAY;
switch (day) { /* ... */ }

// - String (Java 7+)
String text = "hello";
switch (text) { /* ... */ }

// - NOT supported:
// long, float, double, boolean, arbitrary objects (except String and enum)
// All of the following are compilation errors:

// long l = 1L;
// switch (l) { /* ... */ }

// float f = 1.0f;
// switch (f) { /* ... */ }

// double d = 1.0;
// switch (d) { /* ... */ }

// boolean flag = true;
// switch (flag) { /* ... */ }
```

(Note: newer Java versions also add pattern matching to `switch`, but that is out of scope for this question.)

### Alternatives for Floating-Point

**1. Use if-else with range checks:**

```java
double value = 2.5;

if (value < 1.0) {
    System.out.println("Small");
} else if (value < 5.0) {
    System.out.println("Medium");
} else {
    System.out.println("Large");
}
```

**2. Convert to int (if appropriate):**

```java
double temperature = 25.7;
int tempCategory = (int) (temperature / 10);  // 2

switch (tempCategory) {
    case 0: System.out.println("Cold (0-9)"); break;
    case 1: System.out.println("Cool (10-19)"); break;
    case 2: System.out.println("Warm (20-29)"); break;
    case 3: System.out.println("Hot (30+)"); break;
    default: System.out.println("Out of range");
}
```

**3. Use epsilon comparison in if-else:**

```java
double value = 0.3;
final double EPSILON = 0.0001;

if (Math.abs(value - 0.3) < EPSILON) {
    System.out.println("About 0.3");
} else if (Math.abs(value - 0.5) < EPSILON) {
    System.out.println("About 0.5");
} else {
    System.out.println("Something else");
}
```

### Kotlin when with Floating-Point

In Kotlin, `when` is more flexible than Java's `switch`:

- You can use `when` with any type as the subject.
- You can match on constant values, ranges, conditions, etc.

That includes `Float`/`Double` constants:

```kotlin
val value: Double = 2.5

when (value) {
    0.1 -> println("Exactly 0.1")
    0.2 -> println("Exactly 0.2")
    else -> println("Something else")
}
```

But the same caveats about floating-point equality still apply: matching on exact binary floating-point values can be fragile, so in practice you often prefer ranges or epsilon checks:

```kotlin
when {
    value < 1.0 -> println("Small")
    value < 5.0 -> println("Medium")
    else -> println("Large")
}

// Or with ranges
when (value) {
    in 0.0..1.0 -> println("Range 0-1")
    in 1.0..5.0 -> println("Range 1-5")
    else -> println("Above 5")
}
```

### Why Switch on Integers is Safe

**Integer equality is exact:**

```java
int x = 5;
int y = 5;
System.out.println(x == y);  // Always true

int sum = 0;
for (int i = 0; i < 100; i++) {
    sum += 1;
}
System.out.println(sum == 100);  // Always true
```

This exactness makes integral types suitable for the constant-equality semantics required by `switch`.

### Summary

| Type                   | switch Support           | Reason                                                    |
| ---------------------- | ------------------------ | --------------------------------------------------------- |
| `byte`, `short`, `int` | Yes                      | Exact equality, allowed by spec                           |
| `char`                 | Yes                      | Exact equality, allowed by spec                           |
| Wrapper classes        | Yes                      | Auto-unboxing to primitives                               |
| `enum`                 | Yes                      | Fixed set of values                                       |
| `String`               | Yes (Java 7+)            | Well-defined equality, optimized by compiler              |
| `float`, `double`      | No                       | Not allowed by spec; exact-match semantics poorly suit FP |
| `long`                 | No                       | Not allowed by spec for classic switch                    |
| `boolean`              | No                       | Not allowed by spec (use if-else)                         |
| Other Objects          | No (except `String`, enum) | Not allowed by classic switch                             |

**Key point:** Java's classic `switch` requires exact equality on a restricted set of types; `float`/`double` are not permitted, and using them for exact matches is generally unsafe due to their representation.

---

## Follow-ups

- How does Kotlin's `when` differ from Java's `switch` in terms of supported types and patterns?
- When would you use exact matches vs ranges/epsilon comparisons for numeric values?
- What are common pitfalls when comparing floating-point numbers in Java/Kotlin?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-solid-principles--cs--medium]]
-
- [[q-hashmap-how-it-works--kotlin--medium]]
