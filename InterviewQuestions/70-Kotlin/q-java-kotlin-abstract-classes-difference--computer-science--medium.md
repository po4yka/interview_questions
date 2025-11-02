---
id: cs-001
title: "Java Kotlin Abstract Classes Difference"
aliases: []
topic: computer-science
subtopics: [access-modifiers, class-features, type-system]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-inline-function-limitations--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [difficulty/medium]
date created: Sunday, October 12th 2025, 12:27:47 pm
date modified: Saturday, November 1st 2025, 5:43:22 pm
---

# Какое Главное Отличие Между Java И Kotlin Касательно Абстрактных Классов, Методов?

# Question (EN)
> What are the main differences between Java and Kotlin regarding abstract classes and methods?

# Вопрос (RU)
> Какое главное отличие между Java и Kotlin касательно абстрактных классов, методов?

---

## Answer (EN)

Both **Java** and **Kotlin** support concepts of abstract classes and methods, but there are certain differences in approaches and capabilities related to these concepts in each language.

## Key Differences

### 1. Syntax and Usage

**Java:**
- Uses `abstract` keyword for abstract classes and methods
- Abstract methods cannot have implementation in abstract class
- Must explicitly declare constructors

**Kotlin:**
- Also uses `abstract` keyword
- **Main difference:** Kotlin supports **abstract properties** (not just methods)
- Constructors are more concise with primary constructor syntax

**Java Example:**

```java
// Java abstract class
public abstract class Animal {
    private String name;

    // Constructor
    public Animal(String name) {
        this.name = name;
    }

    // Abstract method - no implementation
    public abstract void makeSound();

    // Concrete method - has implementation
    public void sleep() {
        System.out.println(name + " is sleeping");
    }

    // Getters/setters needed
    public String getName() {
        return name;
    }
}

// Implementation
public class Dog extends Animal {
    public Dog(String name) {
        super(name);
    }

    @Override
    public void makeSound() {
        System.out.println("Woof!");
    }
}
```

**Kotlin Example:**

```kotlin
// Kotlin abstract class
abstract class Animal(val name: String) {  // Primary constructor

    // Abstract method
    abstract fun makeSound()

    // Abstract property (Kotlin-specific!)
    abstract val category: String

    // Concrete method
    fun sleep() {
        println("$name is sleeping")
    }
}

// Implementation
class Dog(name: String) : Animal(name) {
    override fun makeSound() {
        println("Woof!")
    }

    override val category = "Mammal"  // Implement abstract property
}
```

---

### 2. Abstract Properties (Kotlin-Specific)

**Kotlin allows abstract properties**, which Java doesn't directly support.

**Kotlin:**

```kotlin
abstract class Vehicle {
    // Abstract property
    abstract val maxSpeed: Int
    abstract var fuelLevel: Double

    // Computed property
    val canDrive: Boolean
        get() = fuelLevel > 0
}

class Car : Vehicle() {
    override val maxSpeed = 200
    override var fuelLevel = 50.0
}
```

**Java equivalent (using methods):**

```java
public abstract class Vehicle {
    // No abstract properties - use abstract methods
    public abstract int getMaxSpeed();
    public abstract double getFuelLevel();
    public abstract void setFuelLevel(double level);

    public boolean canDrive() {
        return getFuelLevel() > 0;
    }
}

public class Car extends Vehicle {
    private int maxSpeed = 200;
    private double fuelLevel = 50.0;

    @Override
    public int getMaxSpeed() {
        return maxSpeed;
    }

    @Override
    public double getFuelLevel() {
        return fuelLevel;
    }

    @Override
    public void setFuelLevel(double level) {
        this.fuelLevel = level;
    }
}
```

---

### 3. Interfaces with Default Implementation

**Java:**
- Interfaces can have default methods (since Java 8)
- Classes can implement multiple interfaces

**Kotlin:**
- Interfaces can have **default implementations** (like Java 8+)
- Class can implement multiple interfaces
- **More flexible** - interfaces can have properties with custom getters

**Java Interface:**

```java
public interface Drawable {
    // Abstract method
    void draw();

    // Default implementation (Java 8+)
    default void display() {
        System.out.println("Displaying drawable");
        draw();
    }
}

public class Circle implements Drawable {
    @Override
    public void draw() {
        System.out.println("Drawing circle");
    }
}
```

**Kotlin Interface:**

```kotlin
interface Drawable {
    // Abstract method
    fun draw()

    // Property with custom getter
    val type: String
        get() = "Generic Drawable"

    // Default implementation
    fun display() {
        println("Displaying $type")
        draw()
    }
}

class Circle : Drawable {
    override fun draw() {
        println("Drawing circle")
    }

    override val type = "Circle"
}
```

---

### 4. Multiple Interface Implementation

**Both Java and Kotlin** allow implementing multiple interfaces, but Kotlin's syntax is more concise.

**Java:**

```java
public interface Flyable {
    void fly();
}

public interface Swimmable {
    void swim();
}

public class Duck extends Animal implements Flyable, Swimmable {
    public Duck(String name) {
        super(name);
    }

    @Override
    public void makeSound() {
        System.out.println("Quack!");
    }

    @Override
    public void fly() {
        System.out.println("Flying");
    }

    @Override
    public void swim() {
        System.out.println("Swimming");
    }
}
```

**Kotlin:**

```kotlin
interface Flyable {
    fun fly()
}

interface Swimmable {
    fun swim()
}

class Duck(name: String) : Animal(name), Flyable, Swimmable {
    override fun makeSound() {
        println("Quack!")
    }

    override fun fly() {
        println("Flying")
    }

    override fun swim() {
        println("Swimming")
    }
}
```

---

### 5. Default Access Modifiers

**Java:**
- If not specified, default is **package-private**
- Must explicitly use `public` for public access

**Kotlin:**
- If not specified, default is **public**
- More concise - no need to write `public` everywhere

**Java:**

```java
// Package-private (default)
abstract class InternalClass {
    abstract void method();
}

// Must explicitly declare public
public abstract class PublicClass {
    public abstract void method();
}
```

**Kotlin:**

```kotlin
// Public by default
abstract class PublicClass {
    abstract fun method()
}

// Explicitly internal (module-level)
internal abstract class InternalClass {
    abstract fun method()
}
```

---

### 6. Constructor Parameters

**Kotlin** has more concise syntax with **primary constructors**.

**Java:**

```java
public abstract class Person {
    private String name;
    private int age;

    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    public abstract void introduce();

    // Getters needed
    public String getName() {
        return name;
    }

    public int getAge() {
        return age;
    }
}
```

**Kotlin:**

```kotlin
abstract class Person(
    val name: String,
    val age: Int
) {
    abstract fun introduce()
}

// Usage
class Student(name: String, age: Int, val grade: Int) : Person(name, age) {
    override fun introduce() {
        println("I'm $name, $age years old, grade $grade")
    }
}
```

---

### 7. Interface Diamond Problem Resolution

**Both languages** handle the diamond problem, but with different syntax.

**Java:**

```java
interface A {
    default void method() {
        System.out.println("A");
    }
}

interface B {
    default void method() {
        System.out.println("B");
    }
}

class C implements A, B {
    @Override
    public void method() {
        // Must resolve conflict
        A.super.method();  // Call specific interface method
    }
}
```

**Kotlin:**

```kotlin
interface A {
    fun method() {
        println("A")
    }
}

interface B {
    fun method() {
        println("B")
    }
}

class C : A, B {
    override fun method() {
        super<A>.method()  // Call specific interface method
        super<B>.method()
    }
}
```

---

## Comparison Table

| Feature | Java | Kotlin |
|---------|------|--------|
| **Abstract methods** | Yes | Yes |
| **Abstract properties** | - No (use methods) | - Yes |
| **Interface default methods** | Yes (Java 8+) | Yes |
| **Interface properties** | - No | - Yes (with getters) |
| **Primary constructor** | - No | - Yes |
| **Default visibility** | Package-private | Public |
| **Multiple inheritance** | - No (classes) <br> - Yes (interfaces) | - No (classes) <br> - Yes (interfaces) |
| **Syntax verbosity** | More verbose | More concise |

---

## Complete Example Comparison

### Java Version

```java
public abstract class Shape {
    private String color;

    public Shape(String color) {
        this.color = color;
    }

    // Abstract method
    public abstract double calculateArea();

    // Concrete method
    public void printInfo() {
        System.out.println("Shape color: " + color);
        System.out.println("Area: " + calculateArea());
    }

    public String getColor() {
        return color;
    }
}

public class Circle extends Shape {
    private double radius;

    public Circle(String color, double radius) {
        super(color);
        this.radius = radius;
    }

    @Override
    public double calculateArea() {
        return Math.PI * radius * radius;
    }
}
```

### Kotlin Version

```kotlin
abstract class Shape(val color: String) {
    // Abstract method
    abstract fun calculateArea(): Double

    // Abstract property
    abstract val shapeType: String

    // Concrete method
    fun printInfo() {
        println("$shapeType - Color: $color")
        println("Area: ${calculateArea()}")
    }
}

class Circle(color: String, val radius: Double) : Shape(color) {
    override fun calculateArea() = Math.PI * radius * radius

    override val shapeType = "Circle"
}
```

---

## Summary

**Main differences between Java and Kotlin abstract classes:**

1. **Abstract Properties** - Kotlin supports them, Java doesn't
2. **Syntax** - Kotlin is more concise with primary constructors
3. **Default Visibility** - Kotlin is public by default, Java is package-private
4. **Interfaces** - Both support default methods, but Kotlin also supports properties in interfaces
5. **Inheritance** - Both only allow single class inheritance, multiple interface implementation
6. **Flexibility** - Kotlin provides more flexibility with properties and concise syntax

**When to use:**
- **Abstract classes** - when you need to share code and state
- **Interfaces** - when you need multiple inheritance of type

**Best practice:** Prefer interfaces with default implementations over abstract classes when you don't need to share state.

---

## Ответ (RU)

Java и Kotlin оба поддерживают концепции абстрактных классов и методов, но существуют определенные различия в подходах и возможностях, связанных с этими концепциями в каждом из языков. Рассмотрим ключевые отличия: 1. Синтаксис и использование - Java использует ключевое слово abstract для объявления абстрактных классов и методов. Абстрактные методы не могут иметь реализации в абстрактном классе. - Kotlin также использует ключевое слово abstract для объявления абстрактных классов и методов. Основное отличие в том, что Kotlin поддерживает свойства которые могут быть абстрактными. 2. Наследование и реализация - Java не поддерживает множественное наследование классов поэтому классы могут наследовать только один абстрактный класс. - Kotlin вводит понятие интерфейсов которые могут содержать реализацию по умолчанию и класс может реализовывать несколько интерфейсов. Это предоставляет большую гибкость по сравнению с Java. 3. Модификаторы доступа по умолчанию - В Java, если он не указан по умолчанию он имеет уровень доступа package-private. - В Kotlin, если он не указан по умолчанию он является public.

## Related Questions

-
- [[q-inline-function-limitations--kotlin--medium]]
-
