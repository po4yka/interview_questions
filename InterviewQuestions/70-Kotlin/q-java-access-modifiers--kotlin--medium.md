---
id: lang-013
title: "Java Access Modifiers / Модификаторы доступа Java"
aliases: [Java Access Modifiers, Модификаторы доступа Java]
topic: kotlin
subtopics: [java, oop]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-architecture-patterns
related: [c-architecture-patterns, q-interface-vs-abstract-class--programming-languages--medium]
created: 2025-10-13
updated: 2025-11-11
tags: [access-modifiers, difficulty/medium, encapsulation, java, oop, programming-languages]
date created: Tuesday, November 25th 2025, 12:55:28 pm
date modified: Tuesday, November 25th 2025, 8:53:51 pm
---
# Вопрос (RU)
> Как лучше всего использовать модификаторы доступа в Java?

# Question (EN)
> How to best use access modifiers in Java?

## Ответ (RU)

В Java есть четыре уровня доступа: `private`, package-private (без модификатора), `protected` и `public`.

**Принцип:** использовать **максимально строгий** уровень доступа, который всё ещё позволяет нужное использование.

### 1. `private` — Инкапсуляция (наиболее Часто Для полей)

Используйте для **почти всех полей** и для вспомогательных методов, которые не нужны извне класса.

```java
class User {
    // Поля должны быть private для сохранения инкапсуляции
    private String username;
    private String password;
    private int age;

    // Публичные методы для контролируемого доступа
    public String getUsername() {
        return username;
    }

    public void setAge(int age) {
        if (age > 0 && age < 150) {  // Валидация
            this.age = age;
        }
    }
}
```

```java
class Calculator {
    public int calculate(int a, int b) {
        return add(multiply(a, 2), b);
    }

    // Приватные вспомогательные методы
    private int multiply(int x, int y) {
        return x * y;
    }

    private int add(int x, int y) {
        return x + y;
    }
}
```

### 2. Package-private (без модификатора) — Доступ Внутри Пакета

Используется для **классов и членов**, предназначенных только для использования внутри одного пакета.

```java
// Класс с доступом по умолчанию (package-private)
class DatabaseHelper {
    // Доступен только внутри того же пакета
    void connect() { }
    void disconnect() { }
}

// Публичный API-класс
public class UserRepository {
    private DatabaseHelper dbHelper = new DatabaseHelper();

    public void save(User user) {
        dbHelper.connect();
        // Сохранение пользователя
        dbHelper.disconnect();
    }
}
```

### 3. `protected` — Наследование + Доступ Внутри Пакета

Применяйте, когда член:
- должен быть доступен наследникам (в том числе в других пакетаx), и
- может быть доступен другим классам того же пакета.

Типичный случай: базовые/абстрактные классы с методами для переопределения или использования наследниками.

```java
// Пример: protected в абстрактном базовом классе
abstract class Animal {
    protected abstract void makeSound();  // Наследники обязаны реализовать

    protected void breathe() {  // Доступно наследникам и классам в пакете
        System.out.println("Breathing...");
    }
}

class Dog extends Animal {
    @Override
    protected void makeSound() {
        System.out.println("Woof!");
    }
}
```

Избегайте `protected` для изменяемых полей, так как это ослабляет инкапсуляцию:

```java
// Плохо: защищённое поле
class Base {
    protected int value;  // Прямой доступ из наследников и классов пакета
}

class Derived extends Base {
    void modify() {
        value = 100;  // Нет валидации
    }
}

// Лучше: private поле + protected аксессоры
class Base2 {
    private int value;

    protected int getValue() {
        return value;
    }

    protected void setValue(int value) {
        if (value >= 0) {  // Валидация
            this.value = value;
        }
    }
}
```

### 4. `public` — Публичный API

Используйте **только** для классов и методов, которые являются частью публичного API и должны вызываться из других пакетов/модулей.

```java
// Публичный API
public class UserService {
    public void createUser(String name) {
        validate(name);
        save(name);
    }

    // Вспомогательные методы не должны быть public
    private void validate(String name) { }
    private void save(String name) { }
}
```

### Сводка Уровней Доступа

| Модификатор      | Тот же класс | Тот же пакет | Подкласс (другой пакет) | Везде | Типичное применение                     |
|------------------|-------------|-------------|--------------------------|-------|-----------------------------------------|
| private          | Да          | Нет         | Нет                      | Нет   | Инкапсуляция, хелперы                   |
| package-private  | Да          | Да          | Нет (если другой пакет)  | Нет   | Внутренние/пакетные утилиты             |
| protected        | Да          | Да          | Да                       | Нет   | Наследование + доступ в пределах пакета |
| public           | Да          | Да          | Да                       | Да    | Публичный/стабильный API                |

### Решающее Правило (Decision Tree)

```text
Нужно ли вне класса?
 Нет → private
 Да
     Нужно ли вне пакета?
        Нет → package-private (нет модификатора)
        Да
            Только для наследников?
               Да → protected
               Нет → public
```

### Полный Пример

```java
// Публичный API-класс
public class BankAccount {
    // Private поля — инкапсуляция
    private String accountNumber;
    private double balance;

    // Публичный конструктор
    public BankAccount(String accountNumber) {
        this.accountNumber = accountNumber;
        this.balance = 0.0;
    }

    // Публичные методы — API
    public void deposit(double amount) {
        if (validateAmount(amount)) {
            balance += amount;
            logTransaction("deposit", amount);
        }
    }

    public double getBalance() {
        return balance;
    }

    // Приватные вспомогательные методы
    private boolean validateAmount(double amount) {
        return amount > 0;
    }

    private void logTransaction(String type, double amount) {
        TransactionLogger.log(accountNumber, type, amount);
    }
}

// Package-private утилитный класс
class TransactionLogger {
    static void log(String account, String type, double amount) {
        // Логирование транзакции
    }
}
```

### Краткая Сводка

- **Поля**: почти всегда `private`.
- **Методы**:
  - `private` — если используется только внутри класса.
  - package-private — для утилит и коллабораторов внутри пакета.
  - `protected` — когда явно проектируете API для наследников (и принимаете доступ внутри пакета).
  - `public` — только для стабильного внешнего API.
- **Принцип**: выбирать **максимально ограничивающий** уровень доступа, который всё ещё позволяет требуемое использование.
- **Инкапсуляция**: не раскрывать изменяемые поля напрямую; использовать методы (геттеры/сеттеры или API, основанный на поведении).

Также см. [[c-architecture-patterns]] для контекста проектирования API и инкапсуляции.

## Answer (EN)

Java has four access levels: `private`, package-private (no modifier), `protected`, and `public`.

**Best Practices:**

**Principle:** Use the **most restrictive** access level possible.

**1. private** - Encapsulation (MOST COMMON for fields)

Use for **almost all fields** to enforce encapsulation.

```java
class User {
    // Fields should be private to preserve encapsulation
    private String username;
    private String password;
    private int age;

    // Public methods for controlled access
    public String getUsername() {
        return username;
    }

    public void setAge(int age) {
        if (age > 0 && age < 150) {  // Validation
            this.age = age;
        }
    }
}
```

Use for **helper methods** not needed outside the class.

```java
class Calculator {
    public int calculate(int a, int b) {
        return add(multiply(a, 2), b);
    }

    // Private helper methods
    private int multiply(int x, int y) {
        return x * y;
    }

    private int add(int x, int y) {
        return x + y;
    }
}
```

**2. package-private** (no modifier) - Package Access

Use for **utility classes and members** intended only for use within the same package.

```java
// Package-private class (no modifier)
class DatabaseHelper {
    // Only accessible within the same package
    void connect() { }
    void disconnect() { }
}

// Public API class
public class UserRepository {
    private DatabaseHelper dbHelper = new DatabaseHelper();

    public void save(User user) {
        dbHelper.connect();
        // Save user
        dbHelper.disconnect();
    }
}
```

**3. protected** - Inheritance + Package Visibility

Use when a member:
- should be accessible to subclasses (even in other packages), and
- can also be accessible to other classes in the same package.

Typical use: in base/abstract classes for methods intended to be used or overridden by subclasses.

```java
// Example: protected in abstract base class
abstract class Animal {
    protected abstract void makeSound();  // Subclasses must implement

    protected void breathe() {  // Subclasses and same-package classes can use/override
        System.out.println("Breathing...");
    }
}

class Dog extends Animal {
    @Override
    protected void makeSound() {
        System.out.println("Woof!");
    }
}
```

Avoid `protected` for mutable fields when possible — it weakens encapsulation:

```java
// Bad: protected field
class Base {
    protected int value;  // Subclasses and same-package classes can access directly
}

class Derived extends Base {
    void modify() {
        value = 100;  // Direct access - no validation
    }
}

// Better: private field with protected accessors
class Base2 {
    private int value;

    protected int getValue() {
        return value;
    }

    protected void setValue(int value) {
        if (value >= 0) {  // Validation
            this.value = value;
        }
    }
}
```

**4. public** - Public API

Use **only for classes/methods** that are part of your public API and are intended to be used from other packages/modules.

```java
// Public API
public class UserService {
    public void createUser(String name) {
        validate(name);
        save(name);
    }

    // Don't make helpers public
    private void validate(String name) { }
    private void save(String name) { }
}
```

**Access Level Summary:**

| Modifier         | Same Class | Same Package | Subclass (other pkg) | Everywhere | Typical Use                     |
|-----------------|------------|--------------|----------------------|-----------|---------------------------------|
| private         | Yes        | No           | No                   | No        | Encapsulation, helpers          |
| package-private | Yes        | Yes          | No (if other pkg)    | No        | Internal/package utilities      |
| protected       | Yes        | Yes          | Yes                  | No        | Inheritance + package access    |
| public          | Yes        | Yes          | Yes                  | Yes       | Public/stable API               |

**Decision Tree:**

```text
Is it needed outside the class?
 No → private
 Yes
     Needed outside the package?
        No → package-private (no modifier)
        Yes
            Only for subclasses?
               Yes → protected
               No  → public
```

**Complete Example:**

```java
// Public API class
public class BankAccount {
    // Private fields - encapsulation
    private String accountNumber;
    private double balance;

    // Public constructor
    public BankAccount(String accountNumber) {
        this.accountNumber = accountNumber;
        this.balance = 0.0;
    }

    // Public methods - API
    public void deposit(double amount) {
        if (validateAmount(amount)) {
            balance += amount;
            logTransaction("deposit", amount);
        }
    }

    public double getBalance() {
        return balance;
    }

    // Private helpers
    private boolean validateAmount(double amount) {
        return amount > 0;
    }

    private void logTransaction(String type, double amount) {
        TransactionLogger.log(accountNumber, type, amount);
    }
}

// Package-private utility class
class TransactionLogger {
    static void log(String account, String type, double amount) {
        // Log transaction
    }
}
```

**Summary:**

- **Fields**: Almost always **private**.
- **Methods**:
  - `private` if only used internally.
  - package-private for package-only utilities and collaborators.
  - `protected` when explicitly designing for inheritance (and accepting same-package visibility).
  - `public` for stable, documented, external API.
- **Principle**: Choose the **most restrictive** access level that still supports required usage.
- **Encapsulation**: Avoid exposing mutable fields directly; prefer methods (getters/setters, behavior-rich APIs).

Also see [[c-architecture-patterns]] for API and encapsulation design context.

## Дополнительные Вопросы (RU)

- Чем модификаторы доступа в Java отличаются от модификаторов видимости в Kotlin в аналогичных сценариях?
- В каких случаях вы выберете `protected` vs package-private vs `public` в реальном проекте?
- Каковы типичные ошибки при использовании модификаторов (например, чрезмерное использование `public`/`protected`, утечка внутренних деталей между пакетами)?

## Follow-ups

- How do Java access modifiers differ from Kotlin visibility modifiers in similar scenarios?
- When would you choose `protected` vs package-private vs `public` in a real codebase?
- What are common pitfalls to avoid (e.g., overusing `public`/`protected`, leaking internals across packages)?

## Ссылки (RU)

- [Java Language Specification - 6.6. Access Control](https://docs.oracle.com/javase/specs/)

## References

- [Java Language Specification - 6.6. Access Control](https://docs.oracle.com/javase/specs/)

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-java-equals-default-behavior--kotlin--easy]] - Java
- [[q-java-object-comparison--kotlin--easy]] - Java
- [[c-variable--programming-languages--easy]] - Java

### Связанные (средний уровень)
- [[q-kotlin-operator-overloading--kotlin--medium]] - Операторы
- [[q-kotlin-extension-functions--kotlin--medium]] - Расширения

## Related Questions

### Prerequisites (Easier)
- [[q-java-equals-default-behavior--kotlin--easy]] - Java
- [[q-java-object-comparison--kotlin--easy]] - Java
- [[c-variable--programming-languages--easy]] - Java

### Related (Medium)
- [[q-kotlin-operator-overloading--kotlin--medium]] - Operators
- [[q-kotlin-extension-functions--kotlin--medium]] - Extensions
