---
id: lang-010
title: "Java Equals Default Behavior / Поведение equals по умолчанию в Java"
aliases: [Java Equals Default Behavior, Поведение equals по умолчанию в Java]
topic: kotlin
subtopics: [equality, java, object-methods]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-equality, c-java-features]
created: 2025-10-13
updated: 2025-11-09
tags: [difficulty/easy, equality, java, object-methods, programming-languages, reference-equality]
---
# Вопрос (RU)
> Как по умолчанию работает метод equals() из java.lang.Object в Java, что именно он сравнивает?

---

# Question (EN)
> How does the default equals() method from java.lang.Object work in Java, what does it compare?

## Ответ (RU)

По умолчанию реализация `equals()` в классе `Object` сравнивает **ссылки на объекты** (ссылочное равенство), то есть проверяет, указывают ли обе переменные на один и тот же объект в памяти.

Фактически для классов, которые не переопределяют `equals()`, результат `obj1.equals(obj2)` будет таким же, как и у `obj1 == obj2`:

```java
// Реализация в классе Object
public boolean equals(Object obj) {
    return (this == obj); // сравнение ссылок
}
```

Пример поведения по умолчанию:

```java
class Person {
    private String name;

    public Person(String name) {
        this.name = name;
    }

    // equals() не переопределён — используется Object.equals()
}

Person p1 = new Person("John");
Person p2 = new Person("John");
Person p3 = p1;

System.out.println(p1.equals(p2));  // false — разные объекты
System.out.println(p1.equals(p3));  // true — одна и та же ссылка
System.out.println(p1 == p2);       // false
System.out.println(p1 == p3);       // true
```

```java
// Для классов, которые НЕ переопределяют equals():
boolean r1 = obj1.equals(obj2);   // вызывает Object.equals -> (this == obj)
boolean r2 = (obj1 == obj2);      // прямое сравнение ссылок
// r1 и r2 дадут одинаковый результат
```

Для сравнения **содержимого** (полей) в пользовательских классах нужно переопределять `equals()` (и вместе с ним обязательно `hashCode()`), чтобы соблюдать контракт `equals`/`hashCode`.

Пример корректного переопределения:

```java
class Person {
    private String name;

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true; // 1. быстрая проверка ссылки
        if (obj == null || getClass() != obj.getClass())
            return false;              // 2. null или другой тип

        Person person = (Person) obj;  // 3. сравнение содержимого
        return Objects.equals(name, person.name);
    }

    @Override
    public int hashCode() {
        return Objects.hash(name);
    }
}
```

Примеры стандартных классов:

- `String` переопределяет `equals()` и сравнивает содержимое:

```java
String s1 = new String("Hello");
String s2 = new String("Hello");

s1 == s2;        // false — разные объекты
s1.equals(s2);   // true — сравнение содержимого
```

- `ArrayList` также переопределяет `equals()` и сравнивает элементы по порядку:

```java
List<String> list1 = new ArrayList<>(Arrays.asList("a", "b"));
List<String> list2 = new ArrayList<>(Arrays.asList("a", "b"));

list1 == list2;        // false — разные объекты
list1.equals(list2);   // true — одинаковое содержимое
```

- Пользовательский класс без переопределения `equals()` использует сравнение ссылок:

```java
class Box {
    int value;
}

Box box1 = new Box();
Box box2 = new Box();
box1.value = 10;
box2.value = 10;

box1.equals(box2);  // false — Object.equals(), сравнение ссылок
box1 == box2;       // false — разные ссылки
```

Сводка:

- По умолчанию `equals()` в `Object` сравнивает **ссылки**, как `==`.
- Для сравнения содержимого нужно переопределять `equals()`.
- При переопределении `equals()` необходимо также переопределить `hashCode()`.
- Стандартные классы, такие как `String` и `ArrayList`, переопределяют `equals()` для сравнения содержимого.

---

## Answer (EN)

In Java, the default implementation of the `equals()` method in the `Object` class compares **object references** (reference equality), i.e. it checks whether both references point to the same object in memory.

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

**Default equals() is effectively the same as `==` for classes that don't override it:**

```java
// For classes that do NOT override equals():
boolean r1 = obj1.equals(obj2);   // uses Object.equals -> (this == obj)
boolean r2 = (obj1 == obj2);      // direct reference comparison
// r1 and r2 will produce the same result
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

**`String`** (overrides equals):

```java
String s1 = new String("Hello");
String s2 = new String("Hello");

s1 == s2;        // false - different objects
s1.equals(s2);   // true - String overrides equals() to compare content
```

**`ArrayList`** (overrides equals):

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

- **Default `equals()`** in `Object` compares **references** (like `==`)
- For **content comparison**, override `equals()` in your class
- When overriding `equals()`, **always override `hashCode()`** too
- Built-in classes like `String`, `ArrayList` override `equals()` for content comparison

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия этого поведения от Kotlin?
- Когда на практике достаточно поведения `Object.equals()` по умолчанию?
- Каковы типичные ошибки при переопределении `equals()` и `hashCode()`?

## Follow-ups

- What are the key differences between this and Kotlin?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [[c-equality]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

### Простые (Easy)
- [[q-java-object-comparison--kotlin--easy]] - Java
-  - Java

### Продвинутые (Harder)
- [[q-java-access-modifiers--kotlin--medium]] - Java
- [[q-kotlin-operator-overloading--kotlin--medium]] - Операторы
- [[q-kotlin-extension-functions--kotlin--medium]] - Расширения

## Related Questions

### Related (Easy)
- [[q-java-object-comparison--kotlin--easy]] - Java
-  - Java

### Advanced (Harder)
- [[q-java-access-modifiers--kotlin--medium]] - Java
- [[q-kotlin-operator-overloading--kotlin--medium]] - Operators
- [[q-kotlin-extension-functions--kotlin--medium]] - Extensions
