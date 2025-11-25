---
id: lang-011
title: "Java Object Comparison / Сравнение объектов в Java"
aliases: ["Java Object Comparison", "Java Object Сравнение"]
topic: kotlin
subtopics: [equality]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-system-design
related: [c-equality, q-flow-map-operator--programming-languages--medium]
created: 2025-10-13
updated: 2025-11-11
tags: [difficulty/easy, equality, equals, hashcode, java, object-comparison, programming-languages]

date created: Tuesday, November 25th 2025, 12:55:28 pm
date modified: Tuesday, November 25th 2025, 8:53:51 pm
---

# Вопрос (RU)
> Как сравниваются объекты в Java?

# Question (EN)
> How are objects compared in Java?

## Ответ (RU)

В Java есть два основных способа сравнения объектов:

1. `==` — сравнение ссылок (идентичности объектов)
   - Оператор `==` для объектов проверяет, указывают ли две переменные на один и тот же объект в памяти.
   - Для строк (`String`) это особенно важно: литералы могут находиться в пуле строк (string pool), поэтому два одинаковых литерала могут давать `true` при `==`, но два `new `String`("...")` — `false`.

   ```java
   String str1 = new String("Hello");
   String str2 = new String("Hello");

   System.out.println(str1 == str2);  // false - разные объекты

   String str3 = "Hello";
   String str4 = "Hello";

   System.out.println(str3 == str4);  // true - один и тот же объект из пула строк
   ```

2. `.equals()` — логическое (содержательное) сравнение
   - По умолчанию `Object.equals()` сравнивает по ссылке, как `==`.
   - Многие классы (например, `String`, обёртки над примитивами, коллекции) переопределяют `.equals()` для сравнения содержимого.

   ```java
   String str1 = new String("Hello");
   String str2 = new String("Hello");

   System.out.println(str1.equals(str2));  // true - одинаковое содержимое
   ```

При переопределении `.equals()` необходимо также переопределить `.hashCode()` в соответствии с контрактом, чтобы корректно работать с коллекциями на основе хеш-таблиц (`HashMap`, `HashSet` и др.).

### Контракт equals()

Метод `.equals()` должен удовлетворять следующим свойствам:

```java
Person person = new Person("John", 30);

// 1. Рефлексивность: x.equals(x) == true
person.equals(person);  // true

// 2. Симметричность: x.equals(y) == y.equals(x)
Person p3 = new Person("John", 30);
person.equals(p3) == p3.equals(person);

// 3. Транзитивность: если x.equals(y) && y.equals(z), то x.equals(z)
Person p4 = new Person("John", 30);
if (person.equals(p3) && p3.equals(p4)) {
    person.equals(p4);  // должно быть true
}

// 4. Согласованность: повторные вызовы дают один и тот же результат
person.equals(p3);  // при неизменных объектах результат должен быть стабилен

// 5. null: x.equals(null) == false
person.equals(null);  // false
```

### Контракт hashCode()

```java
Person p1 = new Person("John", 30);
Person p2 = new Person("John", 30);

// Если equals() возвращает true, hashCode() обязан быть одинаковым
if (p1.equals(p2)) {
    assert p1.hashCode() == p2.hashCode();  // ДОЛЖНО быть true
}

// Одинаковый hashCode() не гарантирует equals() == true (возможны коллизии)
if (p1.hashCode() == p2.hashCode()) {
    // p1.equals(p2) может быть как true, так и false
}
```

### Пример Правильной Реализации equals() И hashCode()

```java
import java.util.Objects;

class Person {
    private final String name;
    private final int age;

    Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;  // та же ссылка
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

System.out.println(p1 == p2);        // false - разные объекты
System.out.println(p1.equals(p2));   // true - равны по содержимому
```

### Частые Ошибки

```java
// Ошибка: использование == для сравнения содержимого строк
String s1 = new String("test");
String s2 = new String("test");
if (s1 == s2) {  // false - разные объекты
    // не выполнится
}

// Правильно: используем equals() для сравнения содержимого
if (s1.equals(s2)) {  // true - одинаковое содержимое
    // выполнится
}

// Ошибка: логика equals() переопределена, но hashCode() не согласован
class Bad {
    private final String value;

    Bad(String value) {
        this.value = value;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (!(obj instanceof Bad)) return false;
        Bad other = (Bad) obj;
        return Objects.equals(value, other.value); // сравнение по содержимому
    }
    // Отсутствует согласованный hashCode() - ломает работу в хеш-коллекциях
}
```

### Таблица Сравнения

| Оператор    | Что сравнивает                               | Когда использовать                    | Пример               |
|-------------|----------------------------------------------|----------------------------------------|----------------------|
| `==`        | Ссылки (идентичность объекта)               | Проверка, один ли это объект           | `obj1 == obj2`      |
| `.equals()` | Реализацию в классе (обычно данные объекта) | Логическое равенство                   | `obj1.equals(obj2)` |

### Краткое Резюме

- `==` сравнивает ссылки (идентичность объекта).
- `.equals()` определяет логическое равенство; по умолчанию как `==`, но многие классы переопределяют его для сравнения содержимого.
- При переопределении `.equals()` всегда переопределяйте `.hashCode()` согласованно.
- Соблюдайте контракты `equals()`/`hashCode()` для корректной работы с коллекциями (`HashMap`, `HashSet`).

---

## Answer (EN)

Java provides two main ways to compare objects:

1. Reference Comparison (`==`) - Compares object identity
   - The `==` operator compares references: it checks whether two variables refer to the same object.
   - For `String`, this is important: literals may be stored in the string pool, so two identical literals may yield `true` with `==`, while two `new `String`("...")` instances yield `false`.

   ```java
   String str1 = new String("Hello");
   String str2 = new String("Hello");

   System.out.println(str1 == str2);  // false - different objects

   String str3 = "Hello";
   String str4 = "Hello";

   System.out.println(str3 == str4);  // true - same interned String instance (string pool)
   ```

2. `.equals()` - Logical (content) equality
   - By default, `Object.equals()` behaves like `==` (compares references).
   - Many classes (e.g., `String`, wrappers, collections) override `.equals()` to compare contents.

   ```java
   String str1 = new String("Hello");
   String str2 = new String("Hello");

   System.out.println(str1.equals(str2));  // true - same content
   ```

When you override `.equals()`, you must also override `.hashCode()` to preserve their contract, especially for hash-based collections (`HashMap`, `HashSet`, etc.).

### equals() Contract

The `.equals()` method must satisfy these properties:

```java
Person person = new Person("John", 30);

// 1. Reflexive: x.equals(x) == true
person.equals(person);  // true

// 2. Symmetric: x.equals(y) == y.equals(x)
Person p3 = new Person("John", 30);
person.equals(p3) == p3.equals(person);

// 3. Transitive: if x.equals(y) && y.equals(z), then x.equals(z)
Person p4 = new Person("John", 30);
if (person.equals(p3) && p3.equals(p4)) {
    person.equals(p4);  // must be true
}

// 4. Consistent: multiple calls return same result
person.equals(p3);  // result must remain stable if objects do not change

// 5. null: x.equals(null) == false
person.equals(null);  // false
```

### hashCode() Contract

```java
Person p1 = new Person("John", 30);
Person p2 = new Person("John", 30);

// If equals() returns true, hashCode() must be equal
if (p1.equals(p2)) {
    assert p1.hashCode() == p2.hashCode();  // MUST be true
}

// Equal hashCode() does not guarantee equals() == true (collisions possible)
if (p1.hashCode() == p2.hashCode()) {
    // p1.equals(p2) may be either true or false
}
```

### Example of Correct equals() and hashCode() Implementation

```java
import java.util.Objects;

class Person {
    private final String name;
    private final int age;

    Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;  // same reference
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

### Common Mistakes

```java
// Wrong: Using == for String content comparison
String s1 = new String("test");
String s2 = new String("test");
if (s1 == s2) {  // false - different objects
    // Won't execute
}

// Correct: Using equals() for String content comparison
if (s1.equals(s2)) {  // true - same content
    // Will execute
}

// Wrong: equals() defines logical equality, but hashCode() is not consistent
class Bad {
    private final String value;

    Bad(String value) {
        this.value = value;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (!(obj instanceof Bad)) return false;
        Bad other = (Bad) obj;
        return Objects.equals(value, other.value); // content-based equality
    }
    // Missing consistent hashCode() override - breaks behavior in hash-based collections
}
```

### Comparison Table

| Operator    | Compares                                   | Use Case                    | Example               |
|-------------|--------------------------------------------|-----------------------------|-----------------------|
| `==`        | References (object identity)               | Identity check              | `obj1 == obj2`       |
| `.equals()` | As implemented by the class (usually data) | Logical equality check      | `obj1.equals(obj2)` |

### Summary

- `==` compares references (object identity).
- `.equals()` defines logical equality; by default it's identity, but many classes override it to compare content.
- When overriding `.equals()`, always override `.hashCode()` consistently.
- Follow the `equals()`/`hashCode()` contracts for correct behavior with collections like `HashMap` and `HashSet`.

---

## Дополнительные Вопросы (RU)

- В чем различия между `==`/`.equals()` в Java и `==`/`===` в Kotlin?
- Когда на практике стоит использовать проверку идентичности, а когда логического равенства?
- Какие распространенные ошибки возникают при переопределении `equals()` и `hashCode()`?

## Follow-ups

- What are the key differences between Java `==`/`equals()` and Kotlin `==`/`===`?
- When would you use identity vs logical equality in practice?
- What are common pitfalls to avoid when overriding equals() and hashCode()?

## Ссылки (RU)

- [[c-equality]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-equality]]

## Связанные Вопросы (RU)

### Простые (Easy)
- [[q-java-equals-default-behavior--programming-languages--easy]] - Java
- [[q-java-lambda-type--programming-languages--easy]] - Java

### Продвинутые (Сложнее)
- [[q-java-access-modifiers--programming-languages--medium]] - Java
- [[q-kotlin-operator-overloading--kotlin--medium]] - Операторы
- [[q-kotlin-extension-functions--kotlin--medium]] - Расширения

## Related Questions

### Related (Easy)
- [[q-java-equals-default-behavior--programming-languages--easy]] - Java
- [[q-java-lambda-type--programming-languages--easy]] - Java

### Advanced (Harder)
- [[q-java-access-modifiers--programming-languages--medium]] - Java
- [[q-kotlin-operator-overloading--kotlin--medium]] - Operators
- [[q-kotlin-extension-functions--kotlin--medium]] - Extensions