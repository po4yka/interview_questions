---
id: lang-011
title: "Java Object Comparison / Java Object Сравнение"
aliases: [Java Object Comparison, Java Object Сравнение]
topic: programming-languages
subtopics: [java, object-model, equality]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-programming-languages
related: [q-coroutinescope-vs-supervisorscope--programming-languages--medium, q-flow-map-operator--programming-languages--medium, q-observer-pattern--design-patterns--medium]
created: 2025-10-13
updated: 2025-10-31
tags: [equality, equals, hashcode, java, object-comparison, programming-languages, difficulty/easy]
date created: Saturday, October 4th 2025, 3:02:36 pm
date modified: Sunday, October 26th 2025, 12:08:04 pm
---

# Как Сравниваются Объекты В Java?

# Question (EN)
> How are objects compared in Java?

# Вопрос (RU)
> Как сравниваются объекты в Java?

---

## Answer (EN)

Java provides **two ways** to compare objects:

**1. Reference Comparison (`==`)** - Compares memory addresses

By default, `==` compares **references** (memory addresses).

```java
String str1 = new String("Hello");
String str2 = new String("Hello");

System.out.println(str1 == str2);  // false - different objects in memory

String str3 = "Hello";
String str4 = "Hello";

System.out.println(str3 == str4);  // true - same object in string pool
```

**2. Logical Comparison (`.equals()`)** - Compares content

The `.equals()` method compares **logical content**.

```java
String str1 = new String("Hello");
String str2 = new String("Hello");

System.out.println(str1.equals(str2));  // true - same content
```

**Overriding equals() and hashCode():**

When overriding `.equals()`, you should **also override `.hashCode()`**.

```java
class Person {
    private String name;
    private int age;

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;  // Same reference
        if (obj == null || getClass() != obj.getClass()) return false;

        Person person = (Person) obj;
        return age == person.age &&
               Objects.equals(name, person.name);
    }

    @Override
    public int hashCode() {
        return Objects.hash(name, age);
    }
}

Person p1 = new Person("John", 30);
Person p2 = new Person("John", 30);

System.out.println(p1 == p2);        // false - different objects
System.out.println(p1.equals(p2));   // true - same content
```

**equals() Contract:**

Must satisfy these properties:

```java
// 1. Reflexive: x.equals(x) == true
person.equals(person);  // true

// 2. Symmetric: x.equals(y) == y.equals(x)
p1.equals(p2) == p2.equals(p1);

// 3. Transitive: if x.equals(y) && y.equals(z), then x.equals(z)
if (p1.equals(p2) && p2.equals(p3)) {
    p1.equals(p3);  // must be true
}

// 4. Consistent: multiple calls return same result
p1.equals(p2);  // always same result

// 5. null: x.equals(null) == false
person.equals(null);  // false
```

**hashCode() Contract:**

```java
// If equals() is true, hashCode() must be equal
if (p1.equals(p2)) {
    p1.hashCode() == p2.hashCode();  // MUST be true
}

// If hashCode() is equal, equals() MAY be true or false
if (p1.hashCode() == p2.hashCode()) {
    p1.equals(p2);  // could be true or false (hash collision)
}
```

**Common Mistakes:**

```java
// - Wrong: Using == for String comparison
String s1 = new String("test");
String s2 = new String("test");
if (s1 == s2) {  // false - different objects
    // Won't execute
}

// - Correct: Using equals() for String comparison
if (s1.equals(s2)) {  // true - same content
    // Will execute
}

// - Wrong: Overriding equals() without hashCode()
class Bad {
    @Override
    public boolean equals(Object obj) {
        // ...
    }
    // Missing hashCode() override!
}
```

**Comparison Table:**

| Operator | Compares | Use Case | Example |
|----------|----------|----------|---------|
| `==` | References (addresses) | Identity check | `obj1 == obj2` |
| `.equals()` | Logical content | Equality check | `obj1.equals(obj2)` |

**Summary:**

- **`==`** compares **references** (memory addresses)
- **`.equals()`** compares **logical content**
- When overriding `.equals()`, **always override `.hashCode()`**
- Follow the equals/hashCode **contract** for correct behavior

---

## Ответ (RU)

По умолчанию через `==` — сравнение ссылок (адресов). Через `.equals()` — логическое сравнение содержимого. При переопределении `.equals()` рекомендуется также переопределить `.hashCode()`.


---

## Related Questions

### Related (Easy)
- [[q-java-equals-default-behavior--programming-languages--easy]] - Java
- [[q-java-lambda-type--programming-languages--easy]] - Java

### Advanced (Harder)
- [[q-java-access-modifiers--programming-languages--medium]] - Java
- [[q-kotlin-operator-overloading--kotlin--medium]] - Operators
- [[q-kotlin-extension-functions--kotlin--medium]] - Extensions
