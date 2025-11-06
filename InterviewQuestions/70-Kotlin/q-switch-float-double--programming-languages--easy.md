---
id: lang-092
title: "Switch Float Double / Switch с float и double"
aliases: [Switch Float Double, Switch с float и double]
topic: programming-languages
subtopics: [language-features, switch-statement, type-system]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-hashmap-how-it-works--programming-languages--medium, q-solid-principles--software-design--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [difficulty/easy, double, float, floating-point, java, kotlin, programming-languages, switch]
---
# Работает Ли switch() С double/float?

# Вопрос (RU)
> Работает ли switch() с double/float?

---

# Question (EN)
> Does switch() work with double/float?

## Ответ (RU)

Нет, в Java switch не работает с float и double, так как они подвержены проблемам сравнения с плавающей точкой. switch работает с int, byte, short, char, enum, String, а также с их обёрточными типами.

## Answer (EN)

**No**, in Java `switch` does **not** work with `float` and `double`.

### Why Not?

**Floating-point numbers have precision issues** that make equality comparisons unreliable:

```java
double x = 0.1 + 0.2;  // Actually 0.30000000000000004
double y = 0.3;        // Actually 0.3

// These should be "equal" but aren't!
System.out.println(x == y);  // false

// This is why switch can't work with float/double
// switch (x) {
//     case 0.3:  // Which 0.3? The real one or 0.30000000000000004?
//         break;
// }
```

**Floating-point comparison is problematic:**
```java
double a = 0.1;
double b = 0.1;

// Even "identical" values may not compare equal due to rounding
double sum = 0.0;
for (int i = 0; i < 10; i++) {
    sum += 0.1;
}

System.out.println(sum);        // 0.9999999999999999
System.out.println(sum == 1.0); // false!
```

### What Types Does switch() Support?

**Java switch works with:**

```java
// - Primitive integer types
byte b = 1;
switch (b) { /* ... */ }

short s = 1;
switch (s) { /* ... */ }

int i = 1;
switch (i) { /* ... */ }

long l = 1L;
switch (l) { /* ... */ }  // WARNING: Java 7+, earlier versions don't support long

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

// - Floating-point NOT supported
// float f = 1.0f;
// switch (f) { /* ... */ }  // Compilation error!

// double d = 1.0;
// switch (d) { /* ... */ }  // Compilation error!

// - Boolean NOT supported
// boolean flag = true;
// switch (flag) { /* ... */ }  // Compilation error!
```

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

**Kotlin's `when` also doesn't directly support float/double in branches**, but you can use ranges and conditions:

```kotlin
val value = 2.5

when {
    value < 1.0 -> println("Small")
    value < 5.0 -> println("Medium")
    value >= 5.0 -> println("Large")
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

// No precision issues
int sum = 0;
for (int i = 0; i < 100; i++) {
    sum += 1;
}
System.out.println(sum == 100);  // Always true
```

### Summary

| Type | switch Support | Reason |
|------|---------------|--------|
| `byte`, `short`, `int`, `long` | - Yes | Exact equality |
| `char` | - Yes | Exact equality |
| Wrapper classes | - Yes | Auto-unboxing to primitives |
| `enum` | - Yes | Fixed set of values |
| `String` | - Yes (Java 7+) | String equality well-defined |
| `float`, `double` | - No | Floating-point precision issues |
| `boolean` | - No | Only 2 values (use if-else) |
| Objects | - No (except String, enum) | No general equality |

**Key point:** `switch` requires **exact equality matching**, which is unreliable for floating-point numbers due to rounding errors.

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-solid-principles--software-design--medium]]
-
- [[q-hashmap-how-it-works--programming-languages--medium]]
