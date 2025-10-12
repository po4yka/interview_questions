---
tags:
  - inheritance
  - java
  - object-class
  - oop
  - programming-languages
difficulty: easy
status: draft
---

# От какого объекта наследуются все классы в Java?

# Question (EN)
> From which object do all classes in Java inherit?

# Вопрос (RU)
> От какого объекта наследуются все классы в Java?

---

## Answer (EN)

In Java, **all classes implicitly inherit from the Object class** if no other inheritance is explicitly specified.

**Object Class Methods:**

Every class automatically has these methods:

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

**1. toString()** - String representation

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

**2. equals()** - Object comparison

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
    return Objects.hash(name);
}
```

**4. getClass()** - Runtime class info

```java
Class<?> clazz = person.getClass();
System.out.println(clazz.getName());  // Person
```

**5. clone()** - Object copying

```java
class Person implements Cloneable {
    @Override
    protected Object clone() throws CloneNotSupportedException {
        return super.clone();
    }
}
```

**6. finalize()** - Cleanup (deprecated)

```java
@Override
protected void finalize() throws Throwable {
    // Cleanup code (deprecated in Java 9+)
}
```

**7. wait(), notify(), notifyAll()** - Thread synchronization

```java
synchronized (obj) {
    obj.wait();    // Wait for notification
    obj.notify();  // Wake one waiting thread
}
```

**All Object Methods:**

| Method | Purpose | Override? |
|--------|---------|-----------|
| toString() | String representation | - Recommended |
| equals() | Logical equality | - Often needed |
| hashCode() | Hash value | - With equals() |
| clone() | Copy object | WARNING: If Cloneable |
| getClass() | Runtime type | - Final |
| wait() | Thread wait | - Final |
| notify() | Wake thread | - Final |
| finalize() | Cleanup | WARNING: Deprecated |

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
        if (!(obj instanceof User)) return false;
        User other = (User) obj;
        return username.equals(other.username);
    }

    @Override
    public int hashCode() {
        return username.hashCode();
    }
}
```

**Summary:**

- **All Java classes** inherit from Object
- **Implicit inheritance** if not specified
- **Common methods** available to all objects
- **Override** toString(), equals(), hashCode() as needed

---

## Ответ (RU)

В Java все классы неявно наследуются от класса **Object**, если явно не указано другое наследование.

