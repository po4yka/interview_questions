---
id: lang-010
title: "Java Equals Default Behavior / Поведение equals по умолчанию в Java"
aliases: [Java Equals Default Behavior, Поведение equals по умолчанию в Java]
topic: programming-languages
subtopics: [equality, java, object-methods]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-equality, c-java-features, q-equals-hashcode-contracts--programming-languages--medium]
created: 2025-10-13
updated: 2025-10-31
tags: [difficulty/easy, equality, java, object-methods, programming-languages, reference-equality]
date created: Friday, October 31st 2025, 6:32:22 pm
date modified: Saturday, November 1st 2025, 5:43:25 pm
---
# Как В Оригинальном Java Equals Работает, Что Он Сравнивает?

# Вопрос (RU)
> Как в оригинальном Java equals работает, что он сравнивает?

---

# Question (EN)
> How does the original Java equals work, what does it compare?

## Ответ (RU)

В оригинальном Java метод `equals` класса Object по умолчанию сравнивает **ссылки на объекты** (ссылочное равенство). Для пользовательских классов метод `equals` переопределяют, чтобы сравнивать содержимое объектов.


---

## Answer (EN)

In the original Java `Object` class, the **`equals()` method by default compares object references** (reference equality).

**Default Implementation:**

```java
// Object class implementation
public boolean equals(Object obj) {
    return (this == obj);  // Reference comparison
}
```

**Behavior:**

```java
class Person {
    private String name;

    public Person(String name) {
        this.name = name;
    }

    // NOT overriding equals() - uses Object's default
}

Person p1 = new Person("John");
Person p2 = new Person("John");
Person p3 = p1;

System.out.println(p1.equals(p2));  // false - different objects
System.out.println(p1.equals(p3));  // true - same reference
System.out.println(p1 == p2);       // false - different references
System.out.println(p1 == p3);       // true - same reference
```

**Default equals() is equivalent to `==`:**

```java
// These are identical for default equals():
obj1.equals(obj2)    obj1 == obj2
```

**Overriding equals() for Content Comparison:**

For custom classes, override `equals()` to compare **content** instead of references.

```java
class Person {
    private String name;

    @Override
    public boolean equals(Object obj) {
        // 1. Same reference?
        if (this == obj) return true;

        // 2. Null or different class?
        if (obj == null || getClass() != obj.getClass())
            return false;

        // 3. Compare content
        Person person = (Person) obj;
        return Objects.equals(name, person.name);
    }

    @Override
    public int hashCode() {
        return Objects.hash(name);
    }
}

Person p1 = new Person("John");
Person p2 = new Person("John");

System.out.println(p1.equals(p2));  // true - same content
System.out.println(p1 == p2);       // false - different references
```

**Examples with Built-in Classes:**

**String** (overrides equals):

```java
String s1 = new String("Hello");
String s2 = new String("Hello");

s1 == s2;        // false - different objects
s1.equals(s2);   // true - String overrides equals() to compare content
```

**ArrayList** (overrides equals):

```java
List<String> list1 = new ArrayList<>(Arrays.asList("a", "b"));
List<String> list2 = new ArrayList<>(Arrays.asList("a", "b"));

list1 == list2;        // false - different objects
list1.equals(list2);   // true - ArrayList overrides equals()
```

**Custom class without override:**

```java
class Box {
    int value;
}

Box box1 = new Box();
Box box2 = new Box();
box1.value = 10;
box2.value = 10;

box1.equals(box2);  // false - uses Object.equals() (reference comparison)
box1 == box2;       // false - different references
```

**Comparison:**

| Scenario | Default equals() | Overridden equals() |
|----------|------------------|---------------------|
| Same object | true | true |
| Different objects, same content | false | true (if implemented) |
| Different objects, different content | false | false |
| Comparison basis | Reference | Content |

**Summary:**

- **Default `equals()`** in Object class compares **references** (like `==`)
- For **content comparison**, override `equals()` in your class
- When overriding `equals()`, **always override `hashCode()`** too
- Built-in classes like String, ArrayList override `equals()` for content comparison

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

### Related (Easy)
- [[q-java-object-comparison--programming-languages--easy]] - Java
- [[q-java-lambda-type--programming-languages--easy]] - Java

### Advanced (Harder)
- [[q-java-access-modifiers--programming-languages--medium]] - Java
- [[q-kotlin-operator-overloading--kotlin--medium]] - Operators
- [[q-kotlin-extension-functions--kotlin--medium]] - Extensions
