---
'---id': lang-012
title: Java Lambda Type / Тип лямбд Java
aliases:
- Java Lambda Type
- Тип лямбд Java
topic: kotlin
subtopics:
- java
- lambda-expressions
question_kind: theory
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-aggregation
- c-app-signing
- c-backend
- c-binary-search
- c-binary-search-tree
- c-binder
- c-biometric-authentication
- c-bm25-ranking
- c-by-type
- c-cap-theorem
- c-ci-cd
- c-ci-cd-pipelines
- c-clean-code
- c-compiler-optimization
- c-compose-modifiers
- c-compose-phases
- c-compose-semantics
- c-computer-science
- c-concurrency
- c-cross-platform-development
- c-cross-platform-mobile
- c-cs
- c-data-classes
- c-data-loading
- c-debugging
- c-declarative-programming
- c-deep-linking
- c-density-independent-pixels
- c-dimension-units
- c-dp-sp-units
- c-dsl-builders
- c-dynamic-programming
- c-espresso-testing
- c-event-handling
- c-folder
- c-functional-programming
- c-gdpr-compliance
- c-gesture-detection
- c-gradle-build-cache
- c-gradle-build-system
- c-https-tls
- c-image-formats
- c-inheritance
- c-java-features
- c-jit-aot-compilation
- c-kmm
- c-kotlin
- c-lambda-expressions
- c-lazy-grid
- c-lazy-initialization
- c-level
- c-load-balancing
- c-manifest
- c-memory-optimization
- c-memory-profiler
- c-microservices
- c-multipart-form-data
- c-multithreading
- c-mutablestate
- c-networking
- c-offline-first-architecture
- c-oop
- c-oop-concepts
- c-oop-fundamentals
- c-oop-principles
- c-play-console
- c-play-feature-delivery
- c-programming-languages
- c-properties
- c-real-time-communication
- c-references
- c-scaling-strategies
- c-scoped-storage
- c-security
- c-serialization
- c-server-sent-events
- c-shader-programming
- c-snapshot-system
- c-specific
- c-strictmode
- c-system-ui
- c-test-doubles
- c-test-sharding
- c-testing-pyramid
- c-testing-strategies
- c-theming
- c-to-folder
- c-token-management
- c-touch-input
- c-turbine-testing
- c-two-pointers
- c-ui-testing
- c-ui-ux-accessibility
- c-value-classes
- c-variable
- c-weak-references
- c-windowinsets
- c-xml
created: 2025-10-13
updated: 2025-11-09
tags:
- difficulty/easy
- functional-interface
- functional-programming
- java
- lambda
- programming-languages
anki_cards:
- slug: q-java-lambda-type--kotlin--easy-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-java-lambda-type--kotlin--easy-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
# Вопрос (RU)
> Какой тип у лямбды в Java?

---

# Question (EN)
> What type does a lambda have in Java?

## Ответ (RU)

В Java лямбда-выражения не имеют собственного отдельного типа. Их тип выводится из контекста и всегда должен быть совместим с подходящим **функциональным интерфейсом** (target type), то есть интерфейсом с единственным абстрактным методом (Single Abstract Method, SAM). Такой интерфейс может также содержать статические и default-методы, но именно один абстрактный метод определяет, какому функциональному интерфейсу соответствует лямбда.

См. также: [[c-java-features]].

**Примеры встроенных функциональных интерфейсов (java.util.function):**

```java
// 1. Predicate<T> - принимает T, возвращает boolean
Predicate<String> isEmpty = s -> s.isEmpty();
boolean result = isEmpty.test("Hello");  // false

// 2. Function<T, R> - принимает T, возвращает R
Function<String, Integer> length = s -> s.length();
int len = length.apply("Hello");  // 5

// 3. Consumer<T> - принимает T, ничего не возвращает
Consumer<String> print = s -> System.out.println(s);
print.accept("Hello");  // печатает "Hello"

// 4. Supplier<T> - ничего не принимает, возвращает T
Supplier<String> supplier = () -> "Hello";
String value = supplier.get();  // "Hello"

// 5. Runnable - ничего не принимает, ничего не возвращает
Runnable task = () -> System.out.println("Running");
task.run();  // печатает "Running"
```

**Пользовательский функциональный интерфейс:**

```java
@FunctionalInterface
interface Calculator {
    int calculate(int a, int b);  // Единственный абстрактный метод

    // Можно иметь default-методы
    default void log(String message) {
        System.out.println(message);
    }

    // Можно иметь static-методы
    static int add(int a, int b) {
        return a + b;
    }
}

// Реализация через лямбду
Calculator multiply = (a, b) -> a * b;
int result = multiply.calculate(5, 3);  // 15
```

**Ключевые моменты:**

- Лямбда всегда приводится к типу **функционального интерфейса** (target type).
- Аннотация `@FunctionalInterface` не обязательна, но рекомендуется.
- Должен быть ровно один абстрактный метод.
- Могут быть default- и static-методы.
- Лямбда предоставляет реализацию этого единственного абстрактного метода.

**Примеры:**

```java
// Comparator как функциональный интерфейс
List<String> names = Arrays.asList("John", "Alice", "Bob");
names.sort((a, b) -> a.compareTo(b));

// Пользовательский функциональный интерфейс
@FunctionalInterface
interface Validator {
    boolean validate(String input);
}

Validator emailValidator = email -> email.contains("@");
boolean isValid = emailValidator.validate("test@example.com");  // true
```

**Итого:**

Лямбда-выражения в Java имеют тип целевого функционального интерфейса — интерфейса с ровно одним абстрактным методом, который эта лямбда реализует.

---

## Answer (EN)

In Java, lambda expressions do not have a standalone intrinsic type. Their type is inferred from the context and must be compatible with a target **functional interface**, i.e., an interface with a single abstract method (Single Abstract Method, SAM). Such an interface may also contain static and default methods, but the single abstract method determines which functional interface the lambda can be assigned to.

See also: [[c-java-features]].

**Built-in Functional Interfaces (java.util.function):**

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

- A lambda is always typed as a compatible **functional interface** (target type).
- The `@FunctionalInterface` annotation is optional but recommended.
- Exactly one abstract method is required.
- May have default and static methods.
- The lambda provides the implementation of that single abstract method.

**Examples:**

```java
// Comparator as a functional interface
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

Lambda expressions in Java have the type of a target functional interface — an interface with exactly one abstract method that the lambda implements.

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия между лямбдами Java и анонимными классами?
- Когда на практике стоит использовать лямбды?
- Каковы распространенные ошибки при работе с функциональными интерфейсами и лямбдами в Java?

## Follow-ups

- What are the key differences between Java lambdas and anonymous classes?
- When would you use a lambda in practice?
- What are common pitfalls when working with functional interfaces and lambdas in Java?

## Ссылки (RU)

- Официальная документация Java по лямбдам и функциональным интерфейсам

## References

- Official Java documentation for lambda expressions and functional interfaces

## Связанные Вопросы (RU)

### Связанные (Простые)
- [[q-java-equals-default-behavior--kotlin--easy]] - Java
- [[q-java-object-comparison--kotlin--easy]] - Java

### Продвинутые (Сложнее)
- [[q-java-access-modifiers--kotlin--medium]] - Java
- [[q-kotlin-operator-overloading--kotlin--medium]] - Операторы
- [[q-kotlin-extension-functions--kotlin--medium]] - Расширения

## Related Questions

### Related (Easy)
- [[q-java-equals-default-behavior--kotlin--easy]] - Java
- [[q-java-object-comparison--kotlin--easy]] - Java

### Advanced (Harder)
- [[q-java-access-modifiers--kotlin--medium]] - Java
- [[q-kotlin-operator-overloading--kotlin--medium]] - Operators
- [[q-kotlin-extension-functions--kotlin--medium]] - Extensions
