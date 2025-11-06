---
id: lang-036
title: "Regular Vs Extension Method / Обычный метод против Extension метода"
aliases: [Regular Vs Extension Method, Обычный метод против Extension метода]
topic: programming-languages
subtopics: [extension-functions, functions, language-features]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-hot-vs-cold-flows--programming-languages--medium, q-reference-types-protect-from-deletion--programming-languages--easy, q-solid-principles--software-design--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [difficulty/easy, extension-functions, functions, kotlin, programming-languages, static-methods]
---
# В Чём Отличие Обычного Метода От Extension Метода В Kotlin

# Вопрос (RU)
> В чём отличие обычного метода от extension метода в Kotlin

---

# Question (EN)
> What is the difference between a regular method and an extension method in Kotlin?

## Ответ (RU)

Обычные методы (member functions) и extension-функции в Kotlin различаются как по реализации, так и по возможностям.

### Основное Различие

**Обычный метод (Member Function):**
- Определяется **внутри класса**
- Имеет прямой доступ к **приватным** членам класса
- Может быть **переопределен** в подклассах
- Изменяет байткод класса

**Extension функция:**
- Определяется **вне класса**
- Доступ только к **публичным** членам
- **Не может** быть переопределена (статическая)
- **Не изменяет** байткод класса

### Сравнительная Таблица

| Аспект | Обычный метод | Extension функция |
|--------|---------------|-------------------|
| **Расположение** | Внутри класса | Вне класса |
| **Доступ** | К приватным членам | Только к публичным |
| **Виртуальность** | Да (полиморфный) | Нет (статический) |
| **Переопределение** | Можно переопределить | Нельзя переопределить |
| **Изменяет класс** | Да | Нет |
| **Байткод** | Метод в классе | Статический метод |
| **Синтаксис вызова** | `obj.method()` | `obj.extension()` (но статический) |

### Обычный Метод (Member Function)

Определен внутри класса, имеет полный доступ:

```kotlin
class User(val name: String, private val password: String) {
    // Обычный метод (member function)
    fun validatePassword(input: String): Boolean {
        return password == input  // Доступ к private password
    }

    fun greet() {
        println("Привет, $name!")
    }

    // Доступ к приватным полям
    private fun internalMethod() {
        println("Password hash: ${password.hashCode()}")
    }

    // Может вызывать другие приватные методы
    fun process() {
        internalMethod()  // OK
    }
}

val user = User("Иван", "secret123")
user.greet()  // Вызов member функции
user.validatePassword("secret123")  // true
// user.internalMethod()  // Ошибка: private
```

**Характеристики:**
- Часть определения класса
- Доступ к private/protected членам
- Может быть переопределен в подклассах
- Виртуальная диспетчеризация (полиморфизм)
- Изменяет байткод класса

### Extension Функция

Определена вне класса, выглядит как метод но это статическая функция:

```kotlin
// Extension функция (определена вне класса)
fun User.displayInfo() {
    println("Пользователь: $name")
    // println(password)  // ОШИБКА: Нет доступа к private!
}

// Можно расширять классы, которые вы не контролируете
fun String.addQuotes(): String {
    return "\"$this\""
}

fun Int.isEven(): Boolean {
    return this % 2 == 0
}

val user = User("Иван", "secret123")
user.displayInfo()  // Выглядит как метод класса

val text = "Привет"
val quoted = text.addQuotes()  // "Привет"

println(42.isEven())  // true
println(7.isEven())   // false
```

**Характеристики:**
- Определена вне класса
- Нет доступа к private/protected членам
- Не может быть переопределена (не виртуальная)
- Статическая диспетчеризация
- НЕ изменяет байткод класса

### Как Работают Extension Функции

**Под капотом:**

```kotlin
// Kotlin extension
fun String.reverse(): String {
    return this.reversed()
}

"привет".reverse()

// Компилируется в статический метод в Java:
public static String reverse(String receiver) {
    return new StringBuilder(receiver).reverse().toString();
}

// Вызывается как:
StringExtensionsKt.reverse("привет")
```

**Ключевой момент:** Extension функция это **синтаксический сахар** для статических методов!

### Доступ К Членам Класса

```kotlin
class User(val name: String, private val age: Int) {
    // Обычный метод - доступ к private
    fun isAdult(): Boolean {
        return age >= 18  // OK - доступ к private age
    }

    fun getInfo(): String {
        return "$name, $age лет"  // OK
    }
}

// Extension - нет доступа к private
fun User.printAge() {
    println(name)  // OK (публичное)
    // println(age)  // ОШИБКА: age приватное!
}

fun User.canVote(): Boolean {
    // return age >= 18  // ОШИБКА: нет доступа к age
    return isAdult()  // Можно вызвать публичный метод
}
```

### Полиморфизм

**Member функции виртуальные:**

```kotlin
open class Animal {
    open fun sound() = "Какой-то звук"
}

class Dog : Animal() {
    override fun sound() = "Гав"  // Переопределение
}

class Cat : Animal() {
    override fun sound() = "Мяу"
}

val animal: Animal = Dog()
animal.sound()  // "Гав" (полиморфный вызов)

val cat: Animal = Cat()
cat.sound()  // "Мяу"
```

**Extension функции НЕ виртуальные:**

```kotlin
open class Animal
class Dog : Animal()
class Cat : Animal()

fun Animal.sound() = "Какой-то звук"
fun Dog.sound() = "Гав"
fun Cat.sound() = "Мяу"

val animal: Animal = Dog()
animal.sound()  // "Какой-то звук" (НЕ "Гав"!)
// Разрешается на основе объявленного типа (Animal), а не реального (Dog)

val dog: Dog = Dog()
dog.sound()  // "Гав" (теперь тип Dog)

// Extension функции не полиморфны!
```

**Практический пример:**

```kotlin
open class Shape {
    open fun area(): Double = 0.0
}

class Circle(val radius: Double) : Shape() {
    override fun area(): Double = Math.PI * radius * radius
}

// Extension функция
fun Shape.describe() = "Это фигура"
fun Circle.describe() = "Это круг"

val shape: Shape = Circle(5.0)
println(shape.area())     // ~78.5 (виртуальный метод - полиморфизм)
println(shape.describe()) // "Это фигура" (extension - статический)

val circle: Circle = Circle(5.0)
println(circle.describe()) // "Это круг" (тип Circle)
```

### Member Имеет Приоритет

Если существуют и member, и extension с одним именем, **вызывается member**:

```kotlin
class MyClass {
    fun foo() {
        println("Member функция")
    }
}

fun MyClass.foo() {  // Extension с тем же именем
    println("Extension функция")
}

MyClass().foo()  // Выводит: "Member функция" (не "Extension функция")
```

**Почему:**
- Member функция часть класса
- Extension функция просто удобный синтаксис
- Приоритет всегда у настоящего member

### Когда Использовать

**Обычные методы когда:**
- Нужен доступ к приватному состоянию
- Требуется полиморфизм/переопределение
- Это основной функционал класса
- Вы контролируете класс

**Extension функции когда:**
- Расширение классов, которыми вы не владеете (String, List, etc.)
- Утилитные функции, не требующие приватного доступа
- Сохранение фокуса класса (разделение concern)
- Создание DSL

### Практические Примеры

**Обычные методы (core functionality):**
```kotlin
class BankAccount(private var balance: Double) {
    // Основные операции требуют приватного доступа
    fun deposit(amount: Double) {
        if (amount > 0) {
            balance += amount
        }
    }

    fun withdraw(amount: Double): Boolean {
        return if (balance >= amount) {
            balance -= amount
            true
        } else {
            false
        }
    }

    fun getBalance(): Double {
        return balance  // Контролируемый доступ
    }

    private fun logTransaction(type: String, amount: Double) {
        println("$type: $amount, новый баланс: $balance")
    }
}
```

**Extension функции (utilities):**
```kotlin
// Расширение String (не владеем этим классом)
fun String.isValidEmail(): Boolean {
    return this.contains("@") && this.contains(".")
}

// Расширение Context (Android)
fun Context.showToast(message: String, duration: Int = Toast.LENGTH_SHORT) {
    Toast.makeText(this, message, duration).show()
}

// Расширение List
fun <T> List<T>.secondOrNull(): T? {
    return if (this.size >= 2) this[1] else null
}

// Использование
val email = "test@example.com"
println(email.isValidEmail())  // true

val numbers = listOf(1, 2, 3)
println(numbers.secondOrNull())  // 2
```

### Преимущества Extension Функций

**1. Не требуют изменения класса:**
```kotlin
// Нельзя изменить класс String, но можем добавить функционал
fun String.camelToSnakeCase(): String {
    return this.replace(Regex("([a-z])([A-Z])"), "$1_$2").lowercase()
}

"camelCase".camelToSnakeCase()  // "camel_case"

fun String.isPalindrome(): Boolean {
    return this == this.reversed()
}

"radar".isPalindrome()  // true
```

**2. Более чистый API:**
```kotlin
// До: статические утилиты
StringUtils.capitalize(text)
StringUtils.reverse(text)
MathUtils.square(number)

// После: extensions
text.capitalize()
text.reverse()
number.square()

// Fluent API
text
    .trim()
    .lowercase()
    .capitalize()
    .addQuotes()
```

**3. Контроль области видимости:**
```kotlin
// Extension только в определенном контексте
class HtmlBuilder {
    fun String.wrapInTag(tag: String): String {
        return "<$tag>$this</$tag>"
        // Доступно только внутри HtmlBuilder
    }

    fun build(): String {
        return "Hello".wrapInTag("h1")  // OK
    }
}

// "World".wrapInTag("p")  // ОШИБКА: не видна снаружи

// Или в файле
private fun String.internalHelper() {
    // Видна только в этом файле
}
```

**4. Групповая организация:**
```kotlin
// Файл StringExtensions.kt
fun String.truncate(maxLength: Int): String =
    if (this.length > maxLength) "${this.take(maxLength)}..." else this

fun String.words(): List<String> = this.split(" ")

fun String.removeWhitespace(): String = this.replace("\\s".toRegex(), "")

// Файл CollectionExtensions.kt
fun <T> List<T>.middle(): T? =
    if (this.isNotEmpty()) this[this.size / 2] else null

fun <T> List<T>.shuffle(): List<T> = this.shuffled()
```

### Receiver Типы

Extensions могут иметь receiver type (this):

```kotlin
// Regular extension
fun String.addPrefix(prefix: String): String {
    return "$prefix$this"
}

// Extension с receiver типом (для DSL)
class HtmlBuilder {
    private val content = StringBuilder()

    fun String.unaryPlus() {
        content.append(this)
    }

    fun tag(name: String, init: HtmlBuilder.() -> Unit): String {
        val builder = HtmlBuilder()
        builder.init()
        return "<$name>${builder.content}</$name>"
    }
}

// Использование
val html = HtmlBuilder().tag("div") {
    +"Hello "  // String.unaryPlus()
    +"World"
}
```

### Тестирование

```kotlin
// Обычный метод - требует mock/stub
class UserService(private val repository: UserRepository) {
    fun findUser(id: Int): User? {
        return repository.findById(id)
    }
}

// Extension - легко тестировать
fun String.toSlug(): String {
    return this.lowercase()
        .replace(" ", "-")
        .replace(Regex("[^a-z0-9-]"), "")
}

@Test
fun testToSlug() {
    assertEquals("hello-world", "Hello World!".toSlug())
}
```

### Ограничения Extension Функций

**Нельзя:**
```kotlin
class MyClass(private val value: Int) {
    private fun privateMethod() {}
}

// 1. Нет доступа к private
fun MyClass.cantAccessPrivate() {
    // println(value)  // ОШИБКА!
    // privateMethod()  // ОШИБКА!
}

// 2. Нельзя переопределить
open class Base
class Derived : Base()

fun Base.method() = "Base"
// Derived не может "override" это

// 3. Нельзя иметь состояние
fun String.addCounter() {
    // var counter = 0  // Можно, но это локальная переменная
    // Нельзя добавить поле в String
}
```

### Интероперабельность С Java

**Вызов из Java:**
```java
// Kotlin extension:
// fun String.reverse(): String

// Java вызов:
String reversed = StringExtensionsKt.reverse("hello");

// Не выглядит как метод в Java
```

### Nullable Receiver

Extensions могут работать с nullable типами:

```kotlin
// Extension для nullable типа
fun String?.isNullOrEmpty(): Boolean {
    return this == null || this.isEmpty()
}

val text: String? = null
println(text.isNullOrEmpty())  // true - не crash!

// Обычная extension для non-null
fun String.capitalize(): String {
    return this.replaceFirstChar { it.uppercase() }
}

// val result = text.capitalize()  // ОШИБКА: text nullable
```

### Резюме

**Extension функция:**
- Выглядит как добавленная к классу
- На самом деле статическая функция
- Предоставляет синтаксический сахар
- Не изменяет байткод класса
- Нет доступа к приватным членам
- Не виртуальная/не полиморфная

**Обычный метод:**
- Реальный член класса
- Доступ к приватному состоянию
- Виртуальный/полиморфный
- Может быть переопределен
- Часть байткода класса

**Выбор между ними:**

| Требование | Используйте |
|------------|-------------|
| Доступ к private | Member |
| Полиморфизм | Member |
| Расширение чужого класса | Extension |
| Утилитные функции | Extension |
| Основная логика класса | Member |
| DSL | Extension |

**Практический совет:**
```kotlin
// Основной функционал - member
class User(private val password: String) {
    fun authenticate(input: String): Boolean {
        return password == input  // Нужен private доступ
    }
}

// Вспомогательный функционал - extension
fun User.toJson(): String {
    // Использует только публичный API
    return """{"name": "$name"}"""
}
```

## Answer (EN)

### Regular Method (Member Function)

**Defined inside class**, has direct access to private members:

```kotlin
class User(val name: String, private val password: String) {
    // Regular method (member function)
    fun validatePassword(input: String): Boolean {
        return password == input  // Can access private password
    }

    fun greet() {
        println("Hello, $name!")
    }
}

val user = User("John", "secret123")
user.greet()  // Calls member function
user.validatePassword("secret123")  // true
```

**Characteristics:**
- Part of class definition
- Can access private/protected members
- Can be overridden in subclasses
- Dispatched virtually (polymorphic)
- Modifies class bytecode

### Extension Function

**Defined outside class**, looks like member but is actually static:

```kotlin
// Extension function (defined outside class)
fun User.displayInfo() {
    println("User: $name")
    // println(password)  // ERROR: Cannot access private members!
}

// Can extend classes you don't own
fun String.addQuotes(): String {
    return "\"$this\""
}

val user = User("John", "secret123")
user.displayInfo()  // Looks like member call

val text = "Hello"
val quoted = text.addQuotes()  // "Hello"
```

**Characteristics:**
- Defined outside class
- Cannot access private/protected members
- Cannot be overridden (not virtual)
- Resolved statically
- Does NOT modify class bytecode

### How Extension Functions Work

**Under the hood:**

```kotlin
// Kotlin extension
fun String.reverse(): String {
    return this.reversed()
}

"hello".reverse()

// Compiles to static method in Java:
public static String reverse(String receiver) {
    return new StringBuilder(receiver).reverse().toString();
}

// Called as:
StringExtensionsKt.reverse("hello")
```

**Key point:** Extension is **syntactic sugar** for static method calls!

### Comparison

| Aspect | Regular Method | Extension Function |
|--------|---------------|-------------------|
| **Location** | Inside class | Outside class |
| **Access** | Private members | Public members only |
| **Virtual** | Yes (polymorphic) | No (static) |
| **Override** | Can override | Cannot override |
| **Modifies class** | Yes | No |
| **Bytecode** | Method in class | Static method |
| **Syntax** | `obj.method()` | `obj.extension()` (but static) |

### Access to Members

```kotlin
class User(val name: String, private val age: Int) {
    // Regular method - can access private
    fun isAdult(): Boolean {
        return age >= 18  // OK
    }
}

// Extension - cannot access private
fun User.printAge() {
    println(name)  // OK (public)
    // println(age)  // ERROR: age is private!
}
```

### Polymorphism

**Member functions are virtual:**

```kotlin
open class Animal {
    open fun sound() = "Some sound"
}

class Dog : Animal() {
    override fun sound() = "Woof"  // Override
}

val animal: Animal = Dog()
animal.sound()  // "Woof" (polymorphic call)
```

**Extension functions are NOT virtual:**

```kotlin
open class Animal

class Dog : Animal()

fun Animal.sound() = "Some sound"
fun Dog.sound() = "Woof"

val animal: Animal = Dog()
animal.sound()  // "Some sound" (NOT "Woof"!)
// Resolved based on declared type (Animal), not actual type (Dog)
```

### Member Takes Precedence

**If both exist, member wins:**

```kotlin
class MyClass {
    fun foo() {
        println("Member")
    }
}

fun MyClass.foo() {  // Extension with same name
    println("Extension")
}

MyClass().foo()  // Prints: "Member" (not "Extension")
```

### Use Cases

**Regular methods when:**
- Need access to private state
- Want polymorphism/overriding
- Core functionality of the class
- You control the class

**Extension functions when:**
- Extending classes you don't own (String, List, etc.)
- Utility functions that don't need private access
- Keeping class focused (separate concerns)
- Creating DSLs

### Real-World Examples

**Regular methods (core functionality):**
```kotlin
class BankAccount(private var balance: Double) {
    // Core operations need private access
    fun deposit(amount: Double) {
        balance += amount
    }

    fun withdraw(amount: Double): Boolean {
        return if (balance >= amount) {
            balance -= amount
            true
        } else {
            false
        }
    }
}
```

**Extension functions (utilities):**
```kotlin
// Extending String (don't own this class)
fun String.isValidEmail(): Boolean {
    return this.contains("@") && this.contains(".")
}

// Extending Context (Android)
fun Context.showToast(message: String) {
    Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
}

// Extending List
fun <T> List<T>.secondOrNull(): T? {
    return if (this.size >= 2) this[1] else null
}
```

### Benefits of Extensions

**1. No class modification:**
```kotlin
// Can't modify String class, but can add functionality
fun String.camelToSnakeCase(): String {
    return this.replace(Regex("([a-z])([A-Z])"), "$1_$2").lowercase()
}

"camelCase".camelToSnakeCase()  // "camel_case"
```

**2. Cleaner API:**
```kotlin
// Before: static utility
StringUtils.capitalize(text)
StringUtils.reverse(text)

// After: extensions
text.capitalize()
text.reverse()
```

**3. Scope control:**
```kotlin
// Extension only available in specific context
class Config {
    fun String.parseConfig(): Map<String, String> {
        // Only available inside Config class
    }
}
```

### Summary

**Extension function:**
- Looks like it's added to the class
- Actually a static function
- Provides syntactic sugar
- Doesn't modify class bytecode
- Cannot access private members
- Not virtual/polymorphic

**Regular method:**
- Actual member of class
- Can access private state
- Virtual/polymorphic
- Can be overridden
- Part of class bytecode

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-reference-types-protect-from-deletion--programming-languages--easy]]
- [[q-solid-principles--software-design--medium]]
- [[q-hot-vs-cold-flows--programming-languages--medium]]
