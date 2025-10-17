---
id: "20251015082237162"
title: "Java Lambda Type / Тип лямбд Java"
topic: programming-languages
difficulty: easy
status: draft
created: 2025-10-13
tags: - functional-interface
  - functional-programming
  - java
  - lambda
  - programming-languages
date_created: 2025-10-13
date_updated: 2025-10-13
moc: moc-programming-languages
related_questions: []
subtopics: ["java", "jvm", "language-features"]
---
# Какой тип у лямбды в Java?

# Question (EN)
> What type does a lambda have in Java?

# Вопрос (RU)
> Какой тип у лямбды в Java?

---

## Answer (EN)

In Java, lambda expressions have a type called **functional interface**.

**Functional Interface** is an interface that contains **only one abstract method**. This interface can also contain static and default methods, but it must have only one abstract method, which defines the type of the lambda expression.

**Built-in Functional Interfaces:**

```java
// 1. Predicate<T> - takes T, returns boolean
Predicate<String> isEmpty = s -> s.isEmpty();
boolean result = isEmpty.test("Hello");  // false

// 2. Function<T, R> - takes T, returns R
Function<String, Integer> length = s -> s.length();
int len = length.apply("Hello");  // 5

// 3. Consumer<T> - takes T, returns void
Consumer<String> print = s -> System.out.println(s);
print.accept("Hello");  // prints "Hello"

// 4. Supplier<T> - takes nothing, returns T
Supplier<String> supplier = () -> "Hello";
String value = supplier.get();  // "Hello"

// 5. Runnable - takes nothing, returns void
Runnable task = () -> System.out.println("Running");
task.run();  // prints "Running"
```

**Custom Functional Interface:**

```java
@FunctionalInterface
interface Calculator {
    int calculate(int a, int b);  // Single abstract method

    // Can have default methods
    default void log(String message) {
        System.out.println(message);
    }

    // Can have static methods
    static int add(int a, int b) {
        return a + b;
    }
}

// Lambda implementation
Calculator multiply = (a, b) -> a * b;
int result = multiply.calculate(5, 3);  // 15
```

**Key Points:**

- **@FunctionalInterface** annotation (optional but recommended)
- **Exactly one abstract method** required
- Can have **default** and **static** methods
- Lambda provides implementation of the single abstract method

**Examples:**

```java
// Comparator functional interface
List<String> names = Arrays.asList("John", "Alice", "Bob");
names.sort((a, b) -> a.compareTo(b));

// Custom functional interface
@FunctionalInterface
interface Validator {
    boolean validate(String input);
}

Validator emailValidator = email -> email.contains("@");
boolean isValid = emailValidator.validate("test@example.com");  // true
```

**Summary:**

Lambda expressions in Java have the type of a **functional interface** - an interface with exactly one abstract method that the lambda implements.

---

## Ответ (RU)

В Java лямбда-выражения имеют тип, который называется **функциональным интерфейсом**. Функциональный интерфейс — это интерфейс, который содержит только один абстрактный метод. Этот интерфейс может также содержать статические и по умолчанию (default) методы, но он должен иметь только один абстрактный метод, который определяет тип лямбда-выражения.


---

## Related Questions

### Related (Easy)
- [[q-java-equals-default-behavior--programming-languages--easy]] - Java
- [[q-java-object-comparison--programming-languages--easy]] - Java

### Advanced (Harder)
- [[q-java-access-modifiers--programming-languages--medium]] - Java
- [[q-kotlin-operator-overloading--kotlin--medium]] - Operators
- [[q-kotlin-extension-functions--kotlin--medium]] - Extensions
