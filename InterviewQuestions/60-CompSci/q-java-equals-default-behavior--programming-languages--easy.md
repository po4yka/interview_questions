---
tags:
  - java
  - equals
  - object-class
  - reference-equality
  - easy_kotlin
  - programming-languages
  - equality
difficulty: easy
---

# Как в оригинальном Java equals работает, что он сравнивает?

**English**: How does the original Java equals work, what does it compare?

## Answer

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
obj1.equals(obj2)  ⟷  obj1 == obj2
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

## Ответ

В оригинальном Java метод `equals` класса Object по умолчанию сравнивает **ссылки на объекты** (ссылочное равенство). Для пользовательских классов метод `equals` переопределяют, чтобы сравнивать содержимое объектов.

