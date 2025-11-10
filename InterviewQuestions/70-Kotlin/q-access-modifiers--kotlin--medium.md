---
id: kotlin-045
title: Access Modifiers in Kotlin / Модификаторы доступа в Kotlin
aliases: [Access Modifiers in Kotlin, Модификаторы доступа в Kotlin]
topic: kotlin
subtopics: [access-modifiers, encapsulation, visibility]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
source: ""
source_note: ""
status: draft
moc: moc-kotlin
related: [c-kotlin, q-kotlin-visibility-modifiers--kotlin--easy]
created: 2025-10-06
updated: 2025-11-10
tags: [access-modifiers, difficulty/medium, encapsulation, kotlin, oop, visibility]
---
# Вопрос (RU)
> Что такое модификаторы доступа в Kotlin и чем они отличаются от Java?

# Question (EN)
> What are access modifiers in Kotlin and how do they differ from Java?

## Ответ (RU)

Модификаторы доступа — это ключевые слова, которые определяют, кто может видеть и использовать класс, переменную или метод. Они помогают инкапсулировать данные и защищать код от неправильного использования.

См. также: [[c-kotlin]]

**Модификаторы доступа в Kotlin:**

1. **private** — виден только внутри того же файла или класса / объекта.
2. **protected** — виден внутри класса и его подклассов (и не даёт видимости на уровне пакета).
3. **internal** — виден внутри того же модуля.
4. **public** — виден везде (по умолчанию).

**Ключевые отличия от Java:**
- В Kotlin **public** по умолчанию (в Java по умолчанию — package-private).
- **internal** модификатор есть только в Kotlin (видимость на уровне модуля).
- **protected** члены не видны в пакете (в Java видны в том же пакете).
- На верхнем уровне нельзя использовать **protected**.

### Примеры кода (RU)

Все приведённые ниже примеры кода идентичны английской версии; комментарии и пояснения адаптированы на русском.

**Все модификаторы доступа:**

```kotlin
class AccessModifierDemo {
    // Public по умолчанию — доступно откуда угодно
    val publicProperty = "Public"

    // Private — только внутри этого класса
    private val privateProperty = "Private"

    // Protected — внутри класса и его подклассов
    protected val protectedProperty = "Protected"

    // Internal — внутри одного модуля
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
        println(publicProperty)       // OK
        // println(privateProperty)  // ОШИБКА — не видно
        println(protectedProperty)    // OK — в подклассе
        println(internalProperty)     // OK — тот же модуль
    }
}

fun main() {
    val demo = AccessModifierDemo()

    println(demo.publicProperty)       // OK
    // println(demo.privateProperty)   // ОШИБКА — не видно
    // println(demo.protectedProperty) // ОШИБКА — не видно
    println(demo.internalProperty)     // OK — в том же модуле
}
```

**Модификатор private:**

```kotlin
class BankAccount(private val accountNumber: String) {
    private var balance: Double = 0.0

    private fun validateAmount(amount: Double): Boolean {
        return amount > 0
    }

    fun deposit(amount: Double) {
        if (validateAmount(amount)) {  // Можно вызвать private-метод
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

    fun getBalance(): Double = balance  // Публичный геттер
}

fun main() {
    val account = BankAccount("12345")

    account.deposit(1000.0)
    account.withdraw(500.0)
    println("Current balance: $${account.getBalance()}")

    // Нельзя обращаться к private-членам:
    // println(account.accountNumber)  // ОШИБКА
    // println(account.balance)        // ОШИБКА
    // account.validateAmount(100.0)  // ОШИБКА
}
```

**Модификатор protected:**

```kotlin
open class Animal(protected val name: String) {
    protected fun makeSound() {
        println("$name makes a sound")
    }

    protected open fun eat() {
        println("$name is eating")
    }

    fun publicMethod() {
        makeSound()  // OK — внутри того же класса
        eat()        // OK — внутри того же класса
    }
}

class Dog(name: String) : Animal(name) {
    fun bark() {
        makeSound()  // OK — в подклассе
        eat()        // OK — в подклассе
        println("$name barks: Woof!")  // OK — protected-свойство
    }

    override fun eat() {
        println("$name eats dog food")
    }
}

fun main() {
    val dog = Dog("Buddy")

    dog.bark()          // OK
    dog.publicMethod()  // OK

    // Нельзя вызывать protected-сущности снаружи:
    // dog.makeSound()  // ОШИБКА
    // dog.eat()        // ОШИБКА
    // println(dog.name)  // ОШИБКА
}
```

**Модификатор internal:**

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

// В том же модуле — всё OK
fun sameModuleFunction() {
    val obj = InternalClass()  // OK
    obj.process()              // OK

    val pub = PublicClass()
    pub.publicMethod()         // OK
    pub.internalMethod()       // OK
    println(pub.internalProp)  // OK
}

// В другом модуле некоторые обращения будут недоступны
// fun differentModuleFunction() {
//     val obj = InternalClass()  // ОШИБКА — не видно
//     val pub = PublicClass()    // OK
//     pub.internalMethod()       // ОШИБКА — не видно
//     println(pub.internalProp)  // ОШИБКА — не видно
// }
```

**Верхнеуровневые объявления:**

```kotlin
// File: TopLevel.kt

// Public по умолчанию — видна везде
fun publicFunction() = "Public"

// Private для файла — доступна только в этом файле
private fun privateFunction() = "Private"

// Internal — доступна в рамках модуля
internal fun internalFunction() = "Internal"

// Protected для верхнеуровневых объявлений запрещён
// protected fun protectedFunction() = "Protected"  // ОШИБКА

private const val PRIVATE_CONSTANT = "Secret"
const val PUBLIC_CONSTANT = "Public constant"
internal const val INTERNAL_CONSTANT = "Internal constant"

fun demonstrateTopLevel() {
    println(publicFunction())    // OK
    println(privateFunction())   // OK — тот же файл
    println(internalFunction())  // OK — тот же модуль
}
```

**Модификаторы конструкторов:**

```kotlin
// Private-первичный конструктор
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

// Protected-конструктор — доступен наследникам
open class ProtectedConstructor protected constructor(val value: Int) {
    companion object {
        fun create(value: Int) = ProtectedConstructor(value)
    }
}

class SubProtected(value: Int) : ProtectedConstructor(value)

// Internal-конструктор
class InternalConstructor internal constructor(val data: String) {
    companion object {
        fun createPublic() = InternalConstructor("public data")
    }
}

fun main() {
    // val singleton1 = Singleton()  // ОШИБКА — private-конструктор
    val singleton = Singleton.getInstance()  // OK

    // val protected = ProtectedConstructor(10)  // ОШИБКА — нельзя вызвать protected-конструктор снаружи
    val protected = ProtectedConstructor.create(10)  // OK
    val sub = SubProtected(20)  // OK — подкласс может вызвать protected-конструктор

    // Internal-конструктор доступен в том же модуле
    val internal = InternalConstructor("test")  // OK в том же модуле
}
```

**Видимость сеттеров:**

```kotlin
class Person {
    // Публичный геттер, private-сеттер (менять может только класс)
    var name: String = ""
        private set

    // Публичный геттер, protected-сеттер (менять могут класс и наследники)
    var age: Int = 0
        protected set

    // Публичный геттер, internal-сеттер (менять может только модуль)
    var email: String = ""
        internal set

    fun changeName(newName: String) {
        name = newName  // OK — внутри класса
    }
}

class Employee : Person() {
    fun celebrateBirthday() {
        age++  // OK — protected-сеттер в подклассе
    }
}

fun main() {
    val person = Person()

    // Геттеры публичны
    println(person.name)
    println(person.age)
    println(person.email)

    // Сеттеры с ограниченным доступом
    // person.name = "Alice"      // ОШИБКА — private-сеттер
    // person.age = 30             // ОШИБКА — protected-сеттер
    person.email = "alice@example.com"  // OK — internal-сеттер в том же модуле

    person.changeName("Alice")  // OK — через публичный метод
    println(person.name)
}
```

**Практический пример:**

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
    internal val email: String  // Internal-свойство — видно внутри модуля
)

fun main() {
    val repo = UserRepository.getInstance()

    repo.addUser(User(1, "Alice", "alice@example.com"))
    repo.addUser(User(2, "Bob", "bob@example.com"))

    println("Users: ${repo.getUsers()}")

    // repo.clearAll()  // OK — internal, тот же модуль
    // repo.validateUser(User(3, "Charlie", "charlie@example.com"))  // ОШИБКА — private
}
```

---

## Answer (EN)
Access modifiers are keywords that define who can see and use a class, variable, or method. They help encapsulate data and protect code from improper use.

See also: [[c-kotlin]]

**Kotlin access modifiers:**

1. **private** - visible only within the same file or class/object
2. **protected** - visible in the class and its subclasses (and does NOT grant package-level visibility)
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

    dog.bark()          // OK
    dog.publicMethod()  // OK

    // Cannot access protected members from outside:
    // dog.makeSound()  // ERROR
    // dog.eat()        // ERROR
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

// Protected constructor - accessible to subclasses
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

    // val protected = ProtectedConstructor(10)  // ERROR - cannot call protected constructor from outside
    val protected = ProtectedConstructor.create(10)  // OK
    val sub = SubProtected(20)  // OK - subclass can call protected constructor

    // Internal constructor visible in same module
    val internal = InternalConstructor("test")  // OK in same module
}
```

**Setter visibility:**

```kotlin
class Person {
    // Public getter, private setter (only this class can modify)
    var name: String = ""
        private set

    // Public getter, protected setter (only this class and subclasses can modify)
    var age: Int = 0
        protected set

    // Public getter, internal setter (only same module can modify)
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
    // person.age = 30         // ERROR - protected setter
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
    internal val email: String  // Internal property - visible within module
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

## Дополнительные вопросы (RU)

- Как работает модификатор `internal` при разделении проекта на несколько модулей?
- Что происходит при переопределении `protected`-члена в Kotlin?
- Можно ли ослаблять или усиливать модификатор доступа при переопределении метода?

## Follow-ups

- How does `internal` modifier work across different modules?
- What happens when you override a protected member in Kotlin?
- Can you change access modifier when overriding a member?

## Ссылки (RU)

- [Kotlin Visibility Modifiers](https://kotlinlang.org/docs/visibility-modifiers.html) — официальная документация Kotlin

## References

- [Kotlin Visibility Modifiers](https://kotlinlang.org/docs/visibility-modifiers.html) - Official Kotlin documentation

## Связанные вопросы (RU)

### Предпосылки (проще)
- [[q-kotlin-visibility-modifiers--kotlin--easy]] - Видимость

### Связанные (средний уровень)
- [[q-visibility-modifiers-kotlin--kotlin--medium]] - Классы
- [[q-value-classes-inline-classes--kotlin--medium]] - Классы
- [[q-delegation-by-keyword--kotlin--medium]] - Классы
- [[q-class-initialization-order--kotlin--medium]] - Классы

## Related Questions

### Prerequisites (Easier)
- [[q-kotlin-visibility-modifiers--kotlin--easy]] - Visibility

### Related (Medium)
- [[q-visibility-modifiers-kotlin--kotlin--medium]] - Classes
- [[q-value-classes-inline-classes--kotlin--medium]] - Classes
- [[q-delegation-by-keyword--kotlin--medium]] - Classes
- [[q-class-initialization-order--kotlin--medium]] - Classes
