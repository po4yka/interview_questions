---
id: 20251012-1227111195
title: Access Modifiers in Kotlin / Модификаторы доступа в Kotlin
aliases: []

# Classification
topic: kotlin
subtopics: [access-modifiers, visibility, encapsulation, oop]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: ""
source_note: ""

# Workflow & relations
status: draft
moc: moc-kotlin
related: []

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [kotlin, access-modifiers, visibility, encapsulation, oop, difficulty/medium]
---
# Question (EN)
> What are access modifiers in Kotlin and how do they differ from Java?

## Answer (EN)
Access modifiers are keywords that define who can see and use a class, variable, or method. They help encapsulate data and protect code from improper use.

**Kotlin access modifiers:**

1. **private** - visible only within the same file or class
2. **protected** - visible in class and its subclasses
3. **internal** - visible within the same module
4. **public** - visible everywhere (default)

### Code Examples

**All access modifiers:**

```kotlin
class AccessModifierDemo {
    // Public by default - accessible anywhere
    val publicProperty = "Public"

    // Private - only within this class
    private val privateProperty = "Private"

    // Protected - within class and subclasses
    protected val protectedProperty = "Protected"

    // Internal - within the same module
    internal val internalProperty = "Internal"

    fun demonstrateAccess() {
        println(publicProperty)     // OK
        println(privateProperty)    // OK
        println(protectedProperty)  // OK
        println(internalProperty)   // OK
    }
}

class Subclass : AccessModifierDemo() {
    fun accessParent() {
        println(publicProperty)      // OK
        // println(privateProperty)  // ERROR - not visible
        println(protectedProperty)   // OK - in subclass
        println(internalProperty)    // OK - same module
    }
}

fun main() {
    val demo = AccessModifierDemo()

    println(demo.publicProperty)     // OK
    // println(demo.privateProperty) // ERROR - not visible
    // println(demo.protectedProperty) // ERROR - not visible
    println(demo.internalProperty)   // OK - same module
}
```

**private modifier:**

```kotlin
class BankAccount(private val accountNumber: String) {
    private var balance: Double = 0.0

    private fun validateAmount(amount: Double): Boolean {
        return amount > 0
    }

    fun deposit(amount: Double) {
        if (validateAmount(amount)) {  // Can call private method
            balance += amount
            println("Deposited: $$amount, Balance: $$balance")
        }
    }

    fun withdraw(amount: Double): Boolean {
        return if (validateAmount(amount) && balance >= amount) {
            balance -= amount
            println("Withdrawn: $$amount, Balance: $$balance")
            true
        } else {
            println("Insufficient funds")
            false
        }
    }

    fun getBalance(): Double = balance  // Public accessor
}

fun main() {
    val account = BankAccount("12345")

    account.deposit(1000.0)
    account.withdraw(500.0)
    println("Current balance: $${account.getBalance()}")

    // Cannot access private members:
    // println(account.accountNumber)  // ERROR
    // println(account.balance)  // ERROR
    // account.validateAmount(100.0)  // ERROR
}
```

**protected modifier:**

```kotlin
open class Animal(protected val name: String) {
    protected fun makeSound() {
        println("$name makes a sound")
    }

    protected open fun eat() {
        println("$name is eating")
    }

    fun publicMethod() {
        makeSound()  // OK - within same class
        eat()        // OK - within same class
    }
}

class Dog(name: String) : Animal(name) {
    fun bark() {
        makeSound()  // OK - in subclass
        eat()        // OK - in subclass
        println("$name barks: Woof!")  // OK - protected property
    }

    override fun eat() {
        println("$name eats dog food")
    }
}

fun main() {
    val dog = Dog("Buddy")

    dog.bark()        // OK
    dog.publicMethod()  // OK

    // Cannot access protected members:
    // dog.makeSound()  // ERROR
    // dog.eat()  // ERROR
    // println(dog.name)  // ERROR
}
```

**internal modifier:**

```kotlin
// File: Module.kt
internal class InternalClass {
    internal val data = "Internal data"

    internal fun process() {
        println("Processing...")
    }
}

class PublicClass {
    internal val internalProp = "Internal property"

    fun publicMethod() {
        println("Public method")
    }

    internal fun internalMethod() {
        println("Internal method")
    }
}

// In same module - all OK
fun sameModuleFunction() {
    val obj = InternalClass()  // OK
    obj.process()              // OK

    val pub = PublicClass()
    pub.publicMethod()        // OK
    pub.internalMethod()      // OK
    println(pub.internalProp) // OK
}

// In different module - some would fail
// fun differentModuleFunction() {
//     val obj = InternalClass()  // ERROR - not visible
//     val pub = PublicClass()    // OK
//     pub.internalMethod()       // ERROR - not visible
//     println(pub.internalProp)  // ERROR - not visible
// }
```

**Top-level declarations:**

```kotlin
// File: TopLevel.kt

// Public by default - visible everywhere
fun publicFunction() = "Public"

// Private to file - only visible in this file
private fun privateFunction() = "Private"

// Internal - visible in same module
internal fun internalFunction() = "Internal"

// Protected NOT allowed for top-level declarations
// protected fun protectedFunction() = "Protected"  // ERROR

private const val PRIVATE_CONSTANT = "Secret"
const val PUBLIC_CONSTANT = "Public constant"
internal const val INTERNAL_CONSTANT = "Internal constant"

fun demonstrateTopLevel() {
    println(publicFunction())    // OK
    println(privateFunction())   // OK - same file
    println(internalFunction())  // OK - same module
}
```

**Constructor access modifiers:**

```kotlin
// Private primary constructor
class Singleton private constructor() {
    companion object {
        private var instance: Singleton? = null

        fun getInstance(): Singleton {
            return instance ?: synchronized(this) {
                instance ?: Singleton().also { instance = it }
            }
        }
    }
}

// Protected constructor
open class ProtectedConstructor protected constructor(val value: Int) {
    companion object {
        fun create(value: Int) = ProtectedConstructor(value)
    }
}

class SubProtected(value: Int) : ProtectedConstructor(value)

// Internal constructor
class InternalConstructor internal constructor(val data: String) {
    companion object {
        fun createPublic() = InternalConstructor("public data")
    }
}

fun main() {
    // val singleton1 = Singleton()  // ERROR - private constructor
    val singleton = Singleton.getInstance()  // OK

    // val protected = ProtectedConstructor(10)  // ERROR
    val protected = ProtectedConstructor.create(10)  // OK
    val sub = SubProtected(20)  // OK - in subclass

    // Internal constructor visible in same module
    val internal = InternalConstructor("test")  // OK in same module
}
```

**Setter visibility:**

```kotlin
class Person {
    // Public getter, private setter
    var name: String = ""
        private set

    // Public getter, protected setter
    var age: Int = 0
        protected set

    // Public getter, internal setter
    var email: String = ""
        internal set

    fun changeName(newName: String) {
        name = newName  // OK - within class
    }
}

class Employee : Person() {
    fun celebrateBirthday() {
        age++  // OK - protected setter in subclass
    }
}

fun main() {
    val person = Person()

    // Getters are public
    println(person.name)
    println(person.age)
    println(person.email)

    // Setters have restricted access
    // person.name = "Alice"  // ERROR - private setter
    // person.age = 30  // ERROR - protected setter
    person.email = "alice@example.com"  // OK - internal setter in same module

    person.changeName("Alice")  // OK - public method
    println(person.name)
}
```

**Real-world example:**

```kotlin
class UserRepository private constructor() {
    private val users = mutableListOf<User>()

    companion object {
        @Volatile
        private var instance: UserRepository? = null

        fun getInstance(): UserRepository {
            return instance ?: synchronized(this) {
                instance ?: UserRepository().also { instance = it }
            }
        }
    }

    fun addUser(user: User) {
        validateUser(user)
        users.add(user)
    }

    fun getUsers(): List<User> = users.toList()

    private fun validateUser(user: User) {
        require(user.name.isNotBlank()) { "Name cannot be blank" }
        require(user.email.contains("@")) { "Invalid email" }
    }

    internal fun clearAll() {
        users.clear()
    }
}

data class User(
    val id: Int,
    val name: String,
    internal val email: String  // Internal property
)

fun main() {
    val repo = UserRepository.getInstance()

    repo.addUser(User(1, "Alice", "alice@example.com"))
    repo.addUser(User(2, "Bob", "bob@example.com"))

    println("Users: ${repo.getUsers()}")

    // repo.clearAll()  // OK - internal, same module
    // repo.validateUser(User(3, "Charlie", "charlie@example.com"))  // ERROR - private
}
```

---

# Вопрос (RU)
> Что такое модификаторы доступа в Kotlin и чем они отличаются от Java?

## Ответ (RU)

Модификаторы доступа — это ключевые слова, которые определяют, кто может видеть и использовать класс, переменную или метод. Они помогают инкапсулировать данные и защищать код от неправильного использования.

**Модификаторы доступа в Kotlin:**

1. **private** - виден только внутри того же файла или класса
2. **protected** - виден в классе и его подклассах
3. **internal** - виден внутри того же модуля
4. **public** - виден везде (по умолчанию)

**Ключевые отличия от Java:**
- В Kotlin **public по умолчанию** (в Java package-private)
- **internal** модификатор есть только в Kotlin (видимость на уровне модуля)
- **protected** члены не видны в пакете (в Java видны)
- На верхнем уровне нельзя использовать **protected**

Все примеры кода из английской версии применимы и к русской версии.

---

## Related Questions

### Prerequisites (Easier)
- [[q-kotlin-visibility-modifiers--kotlin--easy]] - Visibility
### Related (Medium)
- [[q-visibility-modifiers-kotlin--kotlin--medium]] - Classes
- [[q-value-classes-inline-classes--kotlin--medium]] - Classes
- [[q-delegation-by-keyword--kotlin--medium]] - Classes
- [[q-class-initialization-order--kotlin--medium]] - Classes
