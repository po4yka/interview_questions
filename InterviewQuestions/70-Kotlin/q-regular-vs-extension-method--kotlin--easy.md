---
'---id': lang-036
title: Regular Vs Extension Method / Обычный метод против Extension метода
aliases:
- Regular Vs Extension Method
- Обычный метод против Extension метода
topic: kotlin
subtopics:
- extension-functions
- functions
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
created: 2025-10-15
updated: 2025-11-11
tags:
- difficulty/easy
- extension-functions
- functions
- kotlin
- programming-languages
- static-methods
anki_cards:
- slug: q-regular-vs-extension-method--kotlin--easy-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-regular-vs-extension-method--kotlin--easy-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
# Вопрос (RU)
> В чём отличие обычного метода от extension метода в Kotlin?

---

# Question (EN)
> What is the difference between a regular method and an extension method in Kotlin?

## Ответ (RU)

Обычные методы (member functions) и extension-функции в Kotlin различаются как по реализации, так и по возможностям.

### Основное Различие

**Обычный метод (Member Function):**
- Определяется **внутри класса**
- Имеет прямой доступ к **private/protected/internal** членам в пределах области видимости
- Может быть **переопределён** в подклассах, если объявлен как `open`/`abstract` в `open`/`abstract` классе и не `final`
- Компилируется как часть байткода класса (метод внутри класса)

**Extension функция:**
- Определяется **вне класса** (или в другом контексте, например внутри класса/файла как extension)
- Имеет доступ только к тем членам, которые видимы в месте объявления extension (обычно это публичные, но также `internal`/`protected` при корректной области видимости)
- **Не может** быть переопределена как виртуальный метод базового класса (разрешается статически по типу receiver на этапе компиляции)
- Компилируется как **top-level статическая функция** (в Java-байткоде) и **не изменяет** определение исходного класса

### Сравнительная Таблица

| Аспект | Обычный метод | Extension функция |
|--------|---------------|-------------------|
| **Расположение** | Внутри класса | Вне класса (или как extension в другом контексте) |
| **Доступ** | К членам согласно модификаторам видимости (включая private внутри класса) | Только к членам, видимым в месте объявления extension (обычно не private) |
| **Виртуальность** | Может быть виртуальным (при `open`/`abstract`) | Нет (разрешается статически) |
| **Переопределение** | Можно, если не `final` | Нельзя переопределить как виртуальный метод |
| **Изменяет класс** | Является частью байткода класса | Не изменяет байткод существующего класса |
| **Байткод** | Метод внутри класса | Top-level статический метод с параметром-receiver |
| **Синтаксис вызова** | `obj.method()` | `obj.extension()` (но реализация статическая) |

### Обычный Метод (Member Function)

Определён внутри класса, имеет полный доступ к состоянию согласно модификаторам видимости:

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
- Доступ к private/protected/internal членам в рамках правил видимости
- Может быть переопределён в наследниках, если объявлен как `open`/`abstract` и не `final`
- Вызывает динамическую (виртуальную) диспетчеризацию для `open`/`override` методов (полиморфизм)

### Extension Функция

Определена вне класса, выглядит как метод, но это статическая функция с параметром-receiver:

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
- Определена вне класса или в другом контексте как extension
- Нет доступа к `private` членам класса; доступ только к тому, что видно в месте объявления
- Не может быть виртуальной: выбор реализации делается на этапе компиляции по статическому типу receiver
- Статическая диспетчеризация
- Не изменяет байткод исходного класса

### Как Работают Extension Функции

**Под капотом:**

```kotlin
// Kotlin extension
fun String.reverseCustom(): String {
    return this.reversed()
}

"привет".reverseCustom()

// Компилируется в статический метод в Java (упрощённо):
public static String reverseCustom(String receiver) {
    return new StringBuilder(receiver).reverse().toString();
}

// Вызывается как:
StringExtensionsKt.reverseCustom("привет");
```

**Ключевой момент:** Extension функция — это **синтаксический сахар** для статических методов с явным параметром-receiver.

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

**Member функции могут быть виртуальными:**

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

**Extension функции НЕ полиморфны:**

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
dog.sound()  // "Гав"

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

// Extension функции
fun Shape.describe() = "Это фигура"
fun Circle.describe() = "Это круг"

val shape: Shape = Circle(5.0)
println(shape.area())     // ~78.5 (виртуальный метод - полиморфизм)
println(shape.describe()) // "Это фигура" (extension - статический выбор по типу Shape)

val circle: Circle = Circle(5.0)
println(circle.describe()) // "Это круг" (тип Circle)
```

### Member Имеет Приоритет

Если существуют и member, и extension с одним именем и сигнатурой, **вызывается member**:

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
- Member функция — часть класса
- Extension функция — просто удобный синтаксис (top-level функция)
- Приоритет всегда у настоящего member

### Когда Использовать

**Обычные методы когда:**
- Нужен доступ к приватному состоянию
- Требуется полиморфизм/переопределение
- Это основной функционал класса
- Вы контролируете класс

**Extension функции когда:**
- Расширение классов, которыми вы не владеете (`String`, `List`, etc.)
- Утилитные функции, не требующие приватного доступа
- Сохранение фокуса класса (разделение ответственности)
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
println(email.isValidEmail())  // true (упрощённая проверка)

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

// После: extensions (пример)
text.trim().uppercase() // стандартные extension

// Пользовательские extension
fun String.addPrefix(prefix: String): String = "$prefix$this"

// Fluent API
text
    .trim()
    .lowercase()
    .let { it.addPrefix("> ") }
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

// Или ограничение файлом
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

fun <T> List<T>.shuffleCopy(): List<T> = this.shuffled()
```

### Extension И DSL / Receiver Типы

Extensions всегда имеют receiver type. В сочетании с function types with receiver они активно используются для построения DSL:

```kotlin
// Простейший extension
fun String.addPrefix(prefix: String): String {
    return "$prefix$this"
}

class HtmlBuilder {
    private val content = StringBuilder()

    // Extension на String внутри HtmlBuilder
    fun String.unaryPlus() {
        content.append(this)
    }

    // Функция с receiver HtmlBuilder для DSL
    fun tag(name: String, init: HtmlBuilder.() -> Unit): String {
        val builder = HtmlBuilder()
        builder.init()
        return "<$name>${builder.content}</$name>"
    }
}

// Использование DSL-подхода
val html = HtmlBuilder().tag("div") {
    +"Hello "  // вызывает String.unaryPlus()
    +"World"
}
```

### Тестирование

```kotlin
// Обычный метод - требует mock/stub зависимостей
class UserService(private val repository: UserRepository) {
    fun findUser(id: Int): User? {
        return repository.findById(id)
    }
}

// Extension - чистая функция, легко тестировать
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

// 1. Нет доступа к private-членам
fun MyClass.cantAccessPrivate() {
    // println(value)      // ОШИБКА!
    // privateMethod()     // ОШИБКА!
}

// 2. Нельзя переопределить как виртуальный метод
open class Base
class Derived : Base()

fun Base.method() = "Base"
// Никакое объявление в Derived не "override"-ит эту extension для Base

// 3. Нельзя добавить состояние к существующему классу
fun String.addCounter() {
    // var counter = 0  // Только локальная переменная, не поле экземпляра
}
```

### Интероперабельность С Java

**Вызов из Java:**

```java
// Kotlin extension:
// public fun String.reverseCustom(): String

// Java вызов:
String reversed = StringExtensionsKt.reverseCustom("hello");
// Для Java это обычный статический метод, а не член String
```

### Nullable Receiver

Extensions могут работать с nullable типами:

```kotlin
// Extension для nullable типа
fun String?.isNullOrEmptySafe(): Boolean {
    return this == null || this.isEmpty()
}

val text: String? = null
println(text.isNullOrEmptySafe())  // true - без NPE

// Extension для non-null
fun String.capitalizeFirst(): String {
    return this.replaceFirstChar { it.uppercase() }
}

// val result = text.capitalizeFirst()  // ОШИБКА: text nullable
```

### Резюме

**Extension функция:**
- Выглядит как добавленная к классу
- На самом деле top-level статическая функция с параметром-receiver
- Предоставляет синтаксический сахар
- Не изменяет байткод существующего класса
- Нет доступа к private-членам класса
- Разрешается статически, не виртуальна

**Обычный метод:**
- Реальный член класса
- Имеет доступ к приватному состоянию
- Может быть виртуальным/полиморфным (`open`/`override`)
- Может быть переопределён
- Компилируется как часть байткода класса

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
class User(val name: String, private val password: String) {
    fun authenticate(input: String): Boolean {
        return password == input  // Нужен private доступ
    }
}

// Вспомогательный функционал - extension (использует только публичный API)
fun User.toJson(): String {
    return """{"name": "${this.name}"}"""
}
```

## Answer (EN)

### Main Difference

Regular (member) functions are real methods declared inside a class, participate in visibility rules and polymorphism, and have access to the class internals. Extension functions are top-level static functions with receiver syntax that:
- Do not change the original class
- Are resolved statically by the declared receiver type
- Cannot access private members

### Regular Method (Member Function)

Defined inside the class, has direct access to members according to visibility modifiers:

```kotlin
class User(val name: String, private val password: String) {
    // Regular method (member function)
    fun validatePassword(input: String): Boolean {
        return password == input  // Can access private password
    }

    fun greet() {
        println("Hello, $name!")
    }

    private fun internalMethod() {
        println("Password hash: ${password.hashCode()}")
    }

    fun process() {
        internalMethod()  // OK
    }
}

val user = User("John", "secret123")
user.greet()  // Calls member function
user.validatePassword("secret123")  // true
```

**Characteristics:**
- Part of the class definition
- Can access `private`/`protected`/`internal` members (within visibility rules)
- Can be overridden in subclasses if declared `open`/`abstract` in an `open`/`abstract` class and not `final`
- Uses virtual dispatch for `open`/`override` methods (polymorphism)
- Compiled as a regular method in the class bytecode

### Extension Function

Defined outside the class (or in another scope) and looks like a member, but compiles to a static function with a receiver parameter:

```kotlin
// Extension function (defined outside class)
fun User.displayInfo() {
    println("User: $name")
    // println(password)  // ERROR: Cannot access private!
}

// Can extend classes you don't own
fun String.addQuotes(): String {
    return "\"$this\""
}

fun Int.isEven(): Boolean {
    return this % 2 == 0
}

val user = User("John", "secret123")
user.displayInfo()  // Looks like member call

val text = "Hello"
val quoted = text.addQuotes()  // "Hello"

println(42.isEven())  // true
println(7.isEven())   // false
```

**Characteristics:**
- Declared outside the target class or inside another scope
- Can only access members visible where the extension is declared (no `private` access)
- Resolved statically based on the declared receiver type (not virtual)
- Does not modify the original class bytecode
- Compiled as a top-level static method with the receiver as the first parameter

### How Extension Functions Work (Under the Hood)

```kotlin
// Kotlin extension
fun String.reverseCustom(): String {
    return this.reversed()
}

"hello".reverseCustom()

// Compiles to static method in Java (simplified):
public static String reverseCustom(String receiver) {
    return new StringBuilder(receiver).reverse().toString();
}

// Called as:
StringExtensionsKt.reverseCustom("hello");
```

Key point: an extension function is syntactic sugar for a static method with an explicit receiver parameter.

### Access to Class Members

```kotlin
class User(val name: String, private val age: Int) {
    // Regular method - can access private
    fun isAdult(): Boolean {
        return age >= 18
    }

    fun getInfo(): String {
        return "$name, $age years"
    }
}

// Extension - cannot access private
fun User.printAge() {
    println(name)  // OK (public)
    // println(age)  // ERROR: age is private!
}

fun User.canVote(): Boolean {
    // return age >= 18  // ERROR: cannot access age
    return isAdult()    // Use public API instead
}
```

### Polymorphism

Member functions can be virtual:

```kotlin
open class Animal {
    open fun sound() = "Some sound"
}

class Dog : Animal() {
    override fun sound() = "Woof"
}

class Cat : Animal() {
    override fun sound() = "Meow"
}

val animal: Animal = Dog()
animal.sound()  // "Woof" (polymorphic call)

val cat: Animal = Cat()
cat.sound()  // "Meow"
```

Extension functions are NOT virtual:

```kotlin
open class Animal
class Dog : Animal()
class Cat : Animal()

fun Animal.sound() = "Some sound"
fun Dog.sound() = "Woof"
fun Cat.sound() = "Meow"

val animal: Animal = Dog()
animal.sound()  // "Some sound" (NOT "Woof"!)
// Resolved by declared type (Animal), not runtime type (Dog)

val dog: Dog = Dog()
dog.sound()  // "Woof"
```

More detailed example mirroring shapes:

```kotlin
open class Shape {
    open fun area(): Double = 0.0
}

class Circle(val radius: Double) : Shape() {
    override fun area(): Double = Math.PI * radius * radius
}

fun Shape.describe() = "This is a shape"
fun Circle.describe() = "This is a circle"

val shape: Shape = Circle(5.0)
println(shape.area())     // ~78.5 (virtual call)
println(shape.describe()) // "This is a shape" (extension resolved statically)

val circle: Circle = Circle(5.0)
println(circle.describe()) // "This is a circle"
```

### Member Takes Precedence

If both a member and an extension with the same signature exist, the member is called:

```kotlin
class MyClass {
    fun foo() {
        println("Member")
    }
}

fun MyClass.foo() {  // Extension with same name
    println("Extension")
}

MyClass().foo()  // Prints: "Member"
```

Because the member is a real part of the class, it always wins over an extension with the same signature.

### When to Use What

Use regular methods when:
- You need access to private/internal state
- You need polymorphism/overriding
- Implementing core behavior of the class
- You own/control the class

Use extension functions when:
- Extending classes you do not own (`String`, `List`, framework types)
- Adding utility helpers that rely only on the public API
- Keeping classes focused (separation of concerns)
- Building DSL-style APIs

### Practical Examples

Regular methods (core functionality):

```kotlin
class BankAccount(private var balance: Double) {
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
        return balance
    }

    private fun logTransaction(type: String, amount: Double) {
        println("$type: $amount, new balance: $balance")
    }
}
```

Extension functions (utilities):

```kotlin
// Extending String
fun String.isValidEmail(): Boolean {
    return this.contains("@") && this.contains(".")
}

// Extending Context (Android)
fun Context.showToast(message: String, duration: Int = Toast.LENGTH_SHORT) {
    Toast.makeText(this, message, duration).show()
}

// Extending List
fun <T> List<T>.secondOrNull(): T? {
    return if (this.size >= 2) this[1] else null
}
```

### Benefits of Extension Functions

1. No class modification:

```kotlin
fun String.camelToSnakeCase(): String {
    return this.replace(Regex("([a-z])([A-Z])"), "$1_$2").lowercase()
}

"camelCase".camelToSnakeCase()  // "camel_case"

fun String.isPalindrome(): Boolean {
    return this == this.reversed()
}

"radar".isPalindrome()  // true
```

1. Cleaner API:

```kotlin
// Before: static utilities
StringUtils.capitalize(text)
StringUtils.reverse(text)

// After: extensions / stdlib-style
text.trim().uppercase()

fun String.addPrefix(prefix: String): String = "$prefix$this"
```

1. Scope control:

```kotlin
class HtmlBuilder {
    fun String.wrapInTag(tag: String): String {
        return "<$tag>$this</$tag>"
    }

    fun build(): String {
        return "Hello".wrapInTag("h1")
    }
}

private fun String.internalHelper() {
    // Visible only in this file
}
```

1. Grouped organization:

```kotlin
// StringExtensions.kt
fun String.truncate(maxLength: Int): String =
    if (this.length > maxLength) "${this.take(maxLength)}..." else this

fun String.words(): List<String> = this.split(" ")

fun String.removeWhitespace(): String = this.replace("\\s".toRegex(), "")

// CollectionExtensions.kt
fun <T> List<T>.middle(): T? =
    if (this.isNotEmpty()) this[this.size / 2] else null

fun <T> List<T>.shuffleCopy(): List<T> = this.shuffled()
```

### Extensions and DSL / Receiver Types

Extensions use a receiver type; together with function types with receiver they are powerful for building DSLs:

```kotlin
fun String.addPrefix(prefix: String): String {
    return "$prefix$this"
}

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

val html = HtmlBuilder().tag("div") {
    +"Hello "
    +"World"
}
```

### Testing

```kotlin
class UserService(private val repository: UserRepository) {
    fun findUser(id: Int): User? {
        return repository.findById(id)
    }
}

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

### Limitations of Extension Functions

You cannot:

```kotlin
class MyClass(private val value: Int) {
    private fun privateMethod() {}
}

fun MyClass.cantAccessPrivate() {
    // println(value)      // ERROR
    // privateMethod()     // ERROR
}

open class Base
class Derived : Base()

fun Base.method() = "Base"
// No extension on Derived can override this for Base

fun String.addCounter() {
    // Only local vars, cannot add real state to String
}
```

### Interoperability with Java

```java
// Kotlin extension:
// public fun String.reverseCustom(): String

// From Java:
String reversed = StringExtensionsKt.reverseCustom("hello");
// It's just a static method for Java callers
```

### Nullable Receiver

```kotlin
fun String?.isNullOrEmptySafe(): Boolean {
    return this == null || this.isEmpty()
}

val text: String? = null
println(text.isNullOrEmptySafe())  // true

fun String.capitalizeFirst(): String {
    return this.replaceFirstChar { it.uppercase() }
}

// text.capitalizeFirst() // ERROR: text is nullable
```

### Summary

Extension function:
- Syntactic sugar over a top-level static function with receiver
- Does not change the class
- Cannot access private members
- Resolved statically, not polymorphic

Regular method:
- Real class member in bytecode
- Has access to private/internal state
- Supports virtual dispatch and overriding when `open`/`override`

Choose:
- Member for core behavior, encapsulation, and polymorphism
- Extension for utilities, DSLs, and extending existing APIs without modifying them

## Дополнительные Вопросы (RU)

- В чём ключевые отличия этого подхода от Java?
- Когда бы вы использовали extension функции на практике?
- Каковы типичные ошибки и подводные камни при использовании extension функций?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Kotlin Документация](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## Связанные Вопросы (RU)

- [[q-reference-types-protect-from-deletion--kotlin--easy]]
- [[q-solid-principles--cs--medium]]
- [[q-hot-vs-cold-flows--kotlin--medium]]

## Related Questions

- [[q-reference-types-protect-from-deletion--kotlin--easy]]
- [[q-solid-principles--cs--medium]]
- [[q-hot-vs-cold-flows--kotlin--medium]]
