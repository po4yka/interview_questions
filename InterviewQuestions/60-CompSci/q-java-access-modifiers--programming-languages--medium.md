---
tags:
  - access-modifiers
  - best-practices
  - encapsulation
  - java
  - package-private
  - private
  - programming-languages
  - protected
  - public
difficulty: medium
---

# Как лучше всего использовать модификаторы доступа в Java?

**English**: How to best use access modifiers in Java?

## Answer

Java has **four access modifiers**: `private`, package-private (no modifier), `protected`, and `public`.

**Best Practices:**

**Principle:** Use the **most restrictive** access level possible.

**1. private** - Encapsulation (MOST COMMON for fields)

Use for **all fields** to enforce encapsulation.

```java
class User {
    // ✅ Fields should ALWAYS be private
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

    // ✅ Private helper methods
    private int multiply(int x, int y) {
        return x * y;
    }

    private int add(int x, int y) {
        return x + y;
    }
}
```

**2. package-private** (no modifier) - Package Access

Use for **utility classes** within the same package.

```java
// ✅ Package-private class (no modifier)
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

**3. protected** - Inheritance Only

Use **only in abstract classes** for methods that should be overridden.

```java
// ✅ Good: protected in abstract class
abstract class Animal {
    protected abstract void makeSound();  // Subclasses must implement

    protected void breathe() {  // Subclasses can use/override
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

**❌ Avoid `protected` for fields** - breaks encapsulation:

```java
// ❌ Bad: protected fields
class Base {
    protected int value;  // Subclasses can access directly
}

class Derived extends Base {
    void modify() {
        value = 100;  // Direct access - no validation!
    }
}

// ✅ Good: private fields with protected methods
class Base {
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

Use **only for classes/methods** that are part of your public API.

```java
// ✅ Public API
public class UserService {
    public void createUser(String name) {
        validate(name);
        save(name);
    }

    // ❌ Don't make helpers public
    private void validate(String name) { }
    private void save(String name) { }
}
```

**Access Level Summary:**

| Modifier | Class | Package | Subclass | World | Use When |
|----------|-------|---------|----------|-------|----------|
| **private** | ✅ | ❌ | ❌ | ❌ | Encapsulation, helpers |
| **package-private** | ✅ | ✅ | ❌ | ❌ | Internal utilities |
| **protected** | ✅ | ✅ | ✅ | ❌ | Inheritance (methods only) |
| **public** | ✅ | ✅ | ✅ | ✅ | Public API |

**Decision Tree:**

```
Is it needed outside the class?
├─ No → private
└─ Yes
    ├─ Needed outside the package?
    │   ├─ No → package-private (no modifier)
    │   └─ Yes
    │       ├─ Only for subclasses?
    │       │   └─ Yes → protected
    │       └─ For everyone?
    │           └─ Yes → public
```

**Complete Example:**

```java
// Public API class
public class BankAccount {
    // ✅ Private fields - encapsulation
    private String accountNumber;
    private double balance;

    // ✅ Public constructor
    public BankAccount(String accountNumber) {
        this.accountNumber = accountNumber;
        this.balance = 0.0;
    }

    // ✅ Public methods - API
    public void deposit(double amount) {
        if (validateAmount(amount)) {
            balance += amount;
            logTransaction("deposit", amount);
        }
    }

    public double getBalance() {
        return balance;
    }

    // ✅ Private helpers
    private boolean validateAmount(double amount) {
        return amount > 0;
    }

    private void logTransaction(String type, double amount) {
        TransactionLogger.log(accountNumber, type, amount);
    }
}

// ✅ Package-private utility class
class TransactionLogger {
    static void log(String account, String type, double amount) {
        // Log transaction
    }
}
```

**Summary:**

- **Fields**: Almost always **private**
- **Methods**:
  - **private** if only used internally
  - **package-private** for package utilities
  - **protected** only for abstract class methods (not fields!)
  - **public** for public API
- **Principle**: **Most restrictive** access possible
- **Encapsulation**: Never expose fields directly (use getters/setters with validation)

## Ответ

В Java есть четыре модификатора доступа: `private`, package-private (без модификатора), `protected` и `public`.

**Лучшие практики:**
- **private** — для инкапсуляции данных внутри класса
- **protected** — только в abstract классах для методов (не полей!)
- **public** — для API, доступного извне
- **package-private** — для доступа внутри одного пакета

Лучше всего **ограничивать доступ** настолько, насколько это возможно.

