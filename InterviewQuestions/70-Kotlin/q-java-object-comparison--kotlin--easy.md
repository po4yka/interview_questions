---
anki_cards:
- slug: q-java-object-comparison--kotlin--easy-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-java-object-comparison--kotlin--easy-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
## Answer (EN)

Java provides two main ways to compare objects:

1. Reference Comparison (`==`) - Compares object identity
   - The `==` operator compares references: it checks whether two variables refer to the same object.
   - For `String`, this is important: literals may be stored in the string pool, so two identical literals may yield `true` with `==`, while two `new ``String``("...")` instances yield `false`.

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
- [[q-java-equals-default-behavior--kotlin--easy]] - Java
-  - Java

### Продвинутые (Сложнее)
- [[q-java-access-modifiers--kotlin--medium]] - Java
- [[q-kotlin-operator-overloading--kotlin--medium]] - Операторы
- [[q-kotlin-extension-functions--kotlin--medium]] - Расширения

## Related Questions

### Related (Easy)
- [[q-java-equals-default-behavior--kotlin--easy]] - Java
-  - Java

### Advanced (Harder)
- [[q-java-access-modifiers--kotlin--medium]] - Java
- [[q-kotlin-operator-overloading--kotlin--medium]] - Operators
- [[q-kotlin-extension-functions--kotlin--medium]] - Extensions