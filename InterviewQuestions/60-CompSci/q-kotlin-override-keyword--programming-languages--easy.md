---
tags:
  - abstract
  - inheritance
  - keywords
  - kotlin
  - open
  - override
  - polymorphism
  - programming-languages
difficulty: easy
status: draft
---

# Какое ключевое слово используется для определения метода, который должен быть переопределен в подклассе?

# Question (EN)
> Which keyword is used to define a method that must be overridden in a subclass?

# Вопрос (RU)
> Какое ключевое слово используется для определения метода, который должен быть переопределен в подклассе?

---

## Answer (EN)

In Kotlin, the **`override` keyword** is used to override a method from a parent class. However, to make a method overridable, the parent class method must be marked with **`open`**.

**For abstract methods (must be overridden):**
```kotlin
abstract class Animal {
    abstract fun makeSound()  // Must be overridden
}

class Dog : Animal() {
    override fun makeSound() {
        println("Woof!")
    }
}
```

**For open methods (can be overridden):**
```kotlin
open class Vehicle {
    open fun start() {  // Can be overridden (but not required)
        println("Vehicle starting")
    }
}

class Car : Vehicle() {
    override fun start() {  // override keyword required
        println("Car starting")
    }
}
```

**Key points:**
- Use `abstract` to declare a method that **must** be overridden
- Use `open` to declare a method that **can** be overridden
- Use `override` in the subclass to override the method
- Unlike Java, Kotlin requires explicit `override` keyword (prevents accidental overrides)

**Preventing further overrides:**
```kotlin
open class Base {
    open fun foo() {}
}

class Derived : Base() {
    final override fun foo() {}  // Cannot be overridden further
}
```

**Comparison with Java:**
- Java: `@Override` is optional (annotation)
- Kotlin: `override` is mandatory (keyword)
- Kotlin requires parent methods to be `open` or `abstract`

---

## Ответ (RU)

В Kotlin ключевое слово `override` используется для переопределения метода из родительского класса. Однако, чтобы метод можно было переопределить, метод родительского класса должен быть помечен как `open` или `abstract`.

