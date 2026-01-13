---
anki_cards:
- slug: q-java-all-classes-inherit-from-object--kotlin--easy-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-java-all-classes-inherit-from-object--kotlin--easy-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
---\
id: algo-070
title: "Java All Classes Inherit From Object / В Java все классы наследуются от Object"
aliases: [Java All Classes Inherit From Object, В Java все классы наследуются от Object]
topic: kotlin
subtopics: [inheritance]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-algorithms, c-computer-science]
created: 2025-10-13
updated: 2025-11-11
tags: [difficulty/easy, java, object-class, oop, programming-languages/inheritance]
---\
# Вопрос (RU)
> От какого объекта наследуются все классы в Java?

---

# Question (EN)
> From which object do all classes in Java inherit?

---

## Ответ (RU)

В Java все ссылочные типы (обычные классы) неявно наследуются от класса **Object**, если явно не указано другое наследование (кроме случая с `Object` и `enum`/`record`/`array`, которые тоже в конечном итоге связаны с `Object`). Примитивные типы не наследуются от `Object`.

Знание этого важно и для Kotlin-разработчиков: при работе на JVM корневым типом для всех классов также является `java.lang.Object` (в Kotlin он заворачивается в тип `Any`), а стандартные комментарии о `toString()`, `equals()`, `hashCode()` и других методах остаются актуальными.

См. также: [[c-kotlin]]

**Методы класса Object (основные):**

Каждый такой класс автоматически получает унаследованные методы `Object`, например:

```java
public class MyClass {
    // Автоматически наследуется от Object
}

// Эквивалентно:
public class MyClass extends Object {
    // ...
}
```

**Ключевые методы Object:**

**1. toString()** - строковое представление

```java
class Person {
    String name;

    @Override
    public String toString() {
        return "Person{name='" + name + "'}";
    }
}

Person person = new Person();
person.name = "John";
System.out.println(person.toString());  // Person{name='John'}
```

**2. equals()** - сравнение объектов

```java
@Override
public boolean equals(Object obj) {
    if (this == obj) return true;
    if (obj == null || getClass() != obj.getClass()) return false;
    Person person = (Person) obj;
    return name.equals(person.name);
}
```

**3. hashCode()** - хэш-значение

```java
@Override
public int hashCode() {
    return java.util.Objects.hash(name);
}
```

**4. getClass()** - информация о классе во время выполнения

```java
Class<?> clazz = person.getClass();
System.out.println(clazz.getName());  // Person
```

**5. clone()** - поверхностное копирование объекта

```java
class Person implements Cloneable {
    @Override
    protected Object clone() throws CloneNotSupportedException {
        return super.clone();
    }
}
```

**6. finalize()** - очистка (устарел, не использовать в новом коде)

```java
@Override
@Deprecated // finalize() устарел начиная с Java 9 и помечен к удалению
protected void finalize() throws Throwable {
    // Код очистки (для современного кода НЕ рекомендуется)
}
```

**7. wait(), notify(), notifyAll()** - синхронизация потоков

```java
synchronized (obj) {
    try {
        obj.wait();    // Ожидание уведомления (может быть прервано InterruptedException)
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
    }
    obj.notify();      // Разбудить один ожидающий поток
    obj.notifyAll();   // Разбудить все ожидающие потоки
}
```

(Также существуют перегруженные версии `wait(long)` и `wait(long, int)`. Методы `wait`, `notify`, `notifyAll` и `getClass` являются final.)

**Основные методы Object (кратко):**

| Метод         | Назначение                | Переопределять?              |
|---------------|---------------------------|------------------------------|
| toString()    | Строковое представление   | Часто рекомендуется          |
| equals()      | Логическое равенство      | Часто нужно                  |
| hashCode()    | Хэш-значение              | Всегда вместе с equals()     |
| clone()       | Копировать объект         | Только если реализуете Cloneable |
| getClass()    | Тип во время выполнения   | final, не переопределяется   |
| wait(...)     | Ожидание в мониторе       | final, не переопределяется   |
| notify()      | Разбудить один поток      | final, не переопределяется   |
| notifyAll()   | Разбудить все потоки      | final, не переопределяется   |
| finalize()    | Очистка (устарел)         | Не использовать в новом коде |

**Пример:**

```java
class User {
    private String username;

    // Автоматически наследуется от Object

    @Override
    public String toString() {
        return "User: " + username;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (!(obj instanceof User)) return false;
        User other = (User) obj;
        return java.util.Objects.equals(username, other.username);
    }

    @Override
    public int hashCode() {
        return java.util.Objects.hash(username);
    }
}
```

**Резюме:**

- Все классы-ссылочные типы в Java (кроме самого `Object`) имеют `Object` в вершине своей иерархии.
- Наследование от `Object` происходит неявно, если не указано иное.
- Общие методы `Object` доступны всем экземплярам таких классов.
- При необходимости переопределяйте `toString()`, `equals()`, `hashCode()` с соблюдением их контрактов.
- Для Kotlin на JVM важно понимать, что под капотом корнем иерархии также является `java.lang.Object` (тип `Any` компилируется к нему).

---

## Answer (EN)

In Java, all reference types (regular classes) implicitly inherit from the **Object** class if no other superclass is explicitly specified (except for `Object` itself and special cases like `enum`/`record`/arrays, which are also ultimately related to `Object`). Primitive types do not inherit from `Object`.

This is also relevant for Kotlin developers targeting the JVM: the root of the hierarchy at the bytecode level is still `java.lang.Object` (Kotlin's `Any` maps to it), so the usual considerations around `toString()`, `equals()`, `hashCode()`, and other methods remain applicable.

See also: [[c-kotlin]]

**Object Class Methods (core):**

Every such class automatically has the methods inherited from `Object`, for example:

```java
public class MyClass {
    // Automatically inherits from Object
}

// Equivalent to:
public class MyClass extends Object {
    // ...
}
```

**Key Object Methods:**

**1. toString()** - `String` representation

```java
class Person {
    String name;

    @Override
    public String toString() {
        return "Person{name='" + name + "'}";
    }
}

Person person = new Person();
person.name = "John";
System.out.println(person.toString());  // Person{name='John'}
```

**2. equals()** - Object comparison (logical equality)

```java
@Override
public boolean equals(Object obj) {
    if (this == obj) return true;
    if (obj == null || getClass() != obj.getClass()) return false;
    Person person = (Person) obj;
    return name.equals(person.name);
}
```

**3. hashCode()** - Hash value

```java
@Override
public int hashCode() {
    return java.util.Objects.hash(name);
}
```

`equals()` and `hashCode()` must follow their contracts, especially when objects are used in hash-based collections.

**4. getClass()** - Runtime class info

```java
Class<?> clazz = person.getClass();
System.out.println(clazz.getName());  // Person
```

**5. clone()** - Shallow object copying

```java
class Person implements Cloneable {
    @Override
    protected Object clone() throws CloneNotSupportedException {
        return super.clone();
    }
}
```

**6. finalize()** - Cleanup (deprecated, avoid in new code)

```java
@Override
@Deprecated // finalize() is deprecated since Java 9 and marked for removal
protected void finalize() throws Throwable {
    // Cleanup code (NOT recommended in modern code)
}
```

**7. wait(), notify(), notifyAll()** - `Thread` synchronization

```java
synchronized (obj) {
    try {
        obj.wait();    // Wait for notification (may throw InterruptedException)
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
    }
    obj.notify();      // Wake one waiting thread
    obj.notifyAll();   // Wake all waiting threads
}
```

(There are also overloaded versions `wait(long)` and `wait(long, int)`. Methods `wait`, `notify`, `notifyAll`, and `getClass` are final.)

**Main Object Methods (short list):**

| Method        | Purpose                   | Override?                     |
|---------------|---------------------------|-------------------------------|
| toString()    | `String` representation   | Often recommended             |
| equals()      | Logical equality          | Often needed                  |
| hashCode()    | Hash value                | Always with equals()          |
| clone()       | Copy object               | Only if implementing Cloneable|
| getClass()    | Runtime type              | final, not overridable        |
| wait(...)     | Monitor wait              | final, not overridable        |
| notify()      | Wake one thread           | final, not overridable        |
| notifyAll()   | Wake all threads          | final, not overridable        |
| finalize()    | Cleanup (deprecated)      | Avoid in new code             |

**Example:**

```java
class User {
    private String username;

    // Automatically inherits from Object

    @Override
    public String toString() {
        return "User: " + username;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (!(obj instanceof User)) return false;
        User other = (User) obj;
        return java.util.Objects.equals(username, other.username);
    }

    @Override
    public int hashCode() {
        return java.util.Objects.hash(username);
    }
}
```

**Summary:**

- All Java reference-type classes (except `Object` itself) have `Object` at the top of their hierarchy.
- Inheritance from `Object` is implicit if no other superclass is specified.
- Common `Object` methods are available to all such instances.
- Override `toString()`, `equals()`, and `hashCode()` when needed and respect their contracts.
- For Kotlin on the JVM, it is important to remember that the underlying root is still `java.lang.Object` (Kotlin's `Any` compiles to it).

---

## Дополнительные Вопросы (RU)

- Как эта единая корневая иерархия `Object` сравнивается с языками, где нет единого универсального базового класса?
- В каких практических ситуациях вы будете переопределять `equals()`, `hashCode()` и `toString()`?
- Каковы типичные ошибки при переопределении `equals()` и `hashCode()`?

## Follow-ups

- How does this root `Object` hierarchy compare to languages without a single universal base class?
- When would you override equals(), hashCode(), and toString() in practice?
- What are common pitfalls when overriding equals() and hashCode()?

## Ссылки (RU)

- Официальная документация Java SE для `java.lang.Object`
- [[c-kotlin]]

## References

- Official Java SE API documentation for `java.lang.Object`
- [[c-kotlin]]

## Related Questions

### Related (Easy)
- [[q-kotlin-enum-classes--kotlin--easy]] - Enums

### Advanced (Harder)
- [[q-java-marker-interfaces--kotlin--medium]] - Inheritance
- [[q-when-inheritance-useful--cs--medium]] - Inheritance
- [[q-inheritance-vs-composition--cs--medium]] - Inheritance
