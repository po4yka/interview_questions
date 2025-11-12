---
id: lang-068
title: "Extensions Concept / Концепция расширений"
aliases: [Extensions Concept, Концепция расширений]
topic: kotlin
subtopics: [extensions, functions, kotlin]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin-features, c-kotlin, q-extension-properties--programming-languages--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [difficulty/easy, extension-functions, extensions, kotlin]
---
# Вопрос (RU)
> Что такое Extensions?

---

# Question (EN)
> What are Extensions?

## Ответ (RU)

**Extensions** в Kotlin позволяют добавлять новую функциональность к уже существующим классам, не изменяя их исходный код и не используя наследование. Это включает extension functions и extension properties. Расширения компилируются в статические функции (в сгенерированном классе вида `FileNameKt`), разрешаются статически (не полиморфно, выбор основан на статическом типе выражения, а не на runtime-типе) и не имеют доступа к приватным и protected-членам расширяемого типа.

### Extension Functions (Функции-расширения)

**Добавление функций к существующим типам:**

```kotlin
// Расширяем класс String новой функцией
fun String.addExclamation(): String {
    return this + "!"
}

// Использование
val greeting = "Hello"
println(greeting.addExclamation())  // "Hello!"

// Можно вызывать непосредственно на литерале
println("Kotlin".addExclamation())  // "Kotlin!"
```

### Extension Properties (Свойства-расширения)

**Добавление свойств к существующим типам:**

```kotlin
// Добавляем свойство к Int
val Int.isEven: Boolean
    get() = this % 2 == 0

// Использование
println(4.isEven)   // true
println(5.isEven)   // false
```

### Real-World Examples (Практические примеры)

**1. Утилиты для строк (упрощённый пример):**
```kotlin
fun String.isEmailValid(): Boolean {
    // Простейшая проверка, не предназначена для реальной валидации email
    return this.contains("@") && this.contains(".")
}

val email = "user@example.com"
if (email.isEmailValid()) {
    println("Valid email")
}
```

**2. Утилиты для коллекций:**
```kotlin
fun <T> List<T>.secondOrNull(): T? {
    return if (this.size >= 2) this[1] else null
}

val list = listOf(1, 2, 3)
println(list.secondOrNull())  // 2
```

**3. Расширения `Context` в Android:**
```kotlin
fun Context.showToast(message: String) {
    Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
}

// Использование в Activity
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        showToast("Welcome!")  // Extension на Context, доступен внутри Activity
    }
}
```

### How Extensions Work (Как работают расширения)

```kotlin
// Kotlin-расширение
fun String.reverse(): String {
    return this.reversed()
}

// Концептуальный эквивалент на Java: статический метод в file-class
public static String reverse(String receiver) {
    return new StringBuilder(receiver).reverse().toString();
}

// Фактический вызов из Java зависит от имени файла, например:
// StringExtensionsKt.reverse("hello")
```

Ключевые моменты:
- Класс фактически не модифицируется
- В байткоде это статические функции в сгенерированном классе-файле
- `this` указывает на объект-получатель
- Разрешаются статически (не полиморфно, зависит от статического типа)

### Benefits (Преимущества)

**1. Без наследования:**
```kotlin
// Невозможно модифицировать класс String или унаследоваться от него для добавления поведения
// Но можно добавить функциональность через extension
fun String.isPalindrome() = this == this.reversed()
```

**2. Чистый API:**
```kotlin
// Было: утилитный класс
StringUtils.capitalize(text)

// Стало: extension (пример иллюстративный)
fun String.capitalizeFirstChar(): String =
    replaceFirstChar { if (it.isLowerCase()) it.titlecase() else it.toString() }

val text = "kotlin"
println(text.capitalizeFirstChar())
```

**3. Контроль области видимости:**
```kotlin
// Можно объявлять функции-расширения с разной видимостью
internal fun String.internalExt() = this.length

class MyClass {
    // Приватная функция с получателем String, используемая только внутри MyClass
    private fun String.myExtension() = this.uppercase()
}
```

### Nullable Receiver Extensions (Расширения для nullable-типов)

```kotlin
fun String?.orDefault(default: String = ""): String {
    return this ?: default
}

val text: String? = null
println(text.orDefault("N/A"))  // "N/A"

val text2: String? = "Hello"
println(text2.orDefault("N/A"))  // "Hello"
```

### Member Vs Extension (Метод-член vs функция-расширение)

```kotlin
class MyClass {
    fun foo() {
        println("Member")
    }
}

fun MyClass.foo() {  // Extension
    println("Extension")
}

MyClass().foo()  // Выведет: "Member"
```

Методы-члены всегда имеют приоритет над функциями-расширениями с той же сигнатурой.

### Common Use Cases (Типичные случаи использования)

**1. Расширения для `View` в Android:**
```kotlin
fun View.visible() {
    visibility = View.VISIBLE
}

fun View.gone() {
    visibility = View.GONE
}

// Использование
textView.visible()
progressBar.gone()
```

**2. Преобразование типов:**
```kotlin
fun String.toIntOrDefault(default: Int = 0): Int {
    return this.toIntOrNull() ?: default
}

val number = "123".toIntOrDefault()  // 123
val invalid = "abc".toIntOrDefault() // 0
```

**3. Валидация (упрощённый пример):**
```kotlin
fun String.isValidPassword(): Boolean {
    return this.length >= 8 &&
           this.any { it.isDigit() } &&
           this.any { it.isUpperCase() }
}
```

### Limitations (Ограничения)

Extensions не позволяют:
- Доступ к private или protected-членам класса
- Переопределять методы-члены
- Быть виртуальными/полиморфными (разрешение всегда статическое)
- Изменять структуру класса (добавлять реальные поля и т.п.)

```kotlin
class MyClass {
    private val secret = "hidden"
}

fun MyClass.tryAccess() {
    // println(secret)  // Ошибка: нет доступа к private-члену
}
```

---

## Answer (EN)

**Extensions** in Kotlin allow you to **add new functionality to existing classes** without modifying their source code or using inheritance. This includes both extension functions and extension properties. Extensions are compiled to static functions (in a generated `FileNameKt` class), are resolved statically (not polymorphically; resolution is based on the static type of the expression, not its runtime type), and cannot access private or protected members of the extended type.

### Extension Functions

**Add functions to existing types:**

```kotlin
// Extend `String` class with new function
fun String.addExclamation(): String {
    return this + "!"
}

// Usage
val greeting = "Hello"
println(greeting.addExclamation())  // "Hello!"

// Can also use directly
println("Kotlin".addExclamation())  // "Kotlin!"
```

### Extension Properties

**Add properties to existing types:**

```kotlin
// Add property to Int
val Int.isEven: Boolean
    get() = this % 2 == 0

// Usage
println(4.isEven)   // true
println(5.isEven)   // false
```

### Real-World Examples

**1. String utilities (simplified):**
```kotlin
fun String.isEmailValid(): Boolean {
    // Simple check, not intended for production-grade validation
    return this.contains("@") && this.contains(".")
}

val email = "user@example.com"
if (email.isEmailValid()) {
    println("Valid email")
}
```

**2. Collection utilities:**
```kotlin
fun <T> List<T>.secondOrNull(): T? {
    return if (this.size >= 2) this[1] else null
}

val list = listOf(1, 2, 3)
println(list.secondOrNull())  // 2
```

**3. `Context` extensions (Android):**
```kotlin
fun Context.showToast(message: String) {
    Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
}

// Usage in Activity
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        showToast("Welcome!")  // Extension on Context, available inside Activity
    }
}
```

### How Extensions Work

**Under the hood:**
```kotlin
// Kotlin extension
fun String.reverse(): String {
    return this.reversed()
}

// Conceptual Java equivalent: compiled as a static method in a file-class
public static String reverse(String receiver) {
    return new StringBuilder(receiver).reverse().toString();
}

// Actual usage from Java depends on file name, e.g. StringExtensionsKt.reverse("hello")
```

**Key points:**
- Not actually modifying the class
- Compiled as static functions in a generated file-class (e.g. `FileNameKt`)
- `this` refers to the receiver object
- Resolved statically (not polymorphic; based on static type)

### Benefits

**1. No inheritance needed:**
```kotlin
// Can't modify `String` class or inherit from it
// But can add functionality via extension
fun String.isPalindrome() = this == this.reversed()
```

**2. Clean API:**
```kotlin
// Before: utility class
StringUtils.capitalize(text)

// After: extension (illustrative example)
fun String.capitalizeFirstChar(): String =
    replaceFirstChar { if (it.isLowerCase()) it.titlecase() else it.toString() }

val text = "kotlin"
println(text.capitalizeFirstChar())
```

**3. Scope control:**
```kotlin
// Extensions can be declared with different visibilities
internal fun String.internalExt() = this.length

class MyClass {
    // Private function with String receiver, used only inside MyClass
    private fun String.myExtension() = this.uppercase()
}
```

### Nullable Receiver Extensions

**Can extend nullable types:**

```kotlin
fun String?.orDefault(default: String = ""): String {
    return this ?: default
}

val text: String? = null
println(text.orDefault("N/A"))  // "N/A"

val text2: String? = "Hello"
println(text2.orDefault("N/A"))  // "Hello"
```

### Member Vs Extension

**Member functions take precedence:**

```kotlin
class MyClass {
    fun foo() {
        println("Member")
    }
}

fun MyClass.foo() {  // Extension
    println("Extension")
}

MyClass().foo()  // Prints: "Member"
```

### Common Use Cases

**1. Android `View` extensions:**
```kotlin
fun View.visible() {
    visibility = View.VISIBLE
}

fun View.gone() {
    visibility = View.GONE
}

// Usage
textView.visible()
progressBar.gone()
```

**2. Type conversions:**
```kotlin
fun String.toIntOrDefault(default: Int = 0): Int {
    return this.toIntOrNull() ?: default
}

val number = "123".toIntOrDefault()  // 123
val invalid = "abc".toIntOrDefault() // 0
```

**3. Validation (simplified):**
```kotlin
fun String.isValidPassword(): Boolean {
    return this.length >= 8 &&
           this.any { it.isDigit() } &&
           this.any { it.isUpperCase() }
}
```

### Limitations

**Extensions cannot:**
- Access private or protected members of the class
- Override member functions
- Be virtual/polymorphic (resolution is always static)
- Change class structure

```kotlin
class MyClass {
    private val secret = "hidden"
}

fun MyClass.tryAccess() {
    // println(secret)  // Error: Cannot access private member
}
```

---

## Дополнительные вопросы (RU)

- В чем ключевые отличия extensions от аналогичных возможностей в Java?
- Когда имеет смысл использовать extensions на практике?
- Какие распространенные ошибки при использовании extensions?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [[c-kotlin]]
- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [[c-kotlin]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные вопросы (RU)

- [[q-inheritance-composition-aggregation--oop--medium]]
- [[q-sealed-classes-limitations--programming-languages--medium]]
- [[q-reference-types-criteria--programming-languages--medium]]

## Related Questions

- [[q-inheritance-composition-aggregation--oop--medium]]
- [[q-sealed-classes-limitations--programming-languages--medium]]
- [[q-reference-types-criteria--programming-languages--medium]]
