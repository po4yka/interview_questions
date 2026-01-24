---
id: kotlin-179
title: Sam Conversions / SAM конверсии
aliases:
- Functional Interfaces
- SAM Conversion
- Single Abstract Method
topic: kotlin
subtopics:
- java-interop
- lambdas
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-kotlin
- q-flow-exception-handling--kotlin--medium
- q-kotlin-inline-functions--kotlin--medium
created: 2025-10-15
updated: 2025-11-09
tags:
- difficulty/medium
- functional-interface
- java-interop
- kotlin
- lambda
- sam
anki_cards:
- slug: kotlin-179-0-en
  language: en
  anki_id: 1768326286055
  synced_at: '2026-01-23T17:03:51.047257'
- slug: kotlin-179-0-ru
  language: ru
  anki_id: 1768326286079
  synced_at: '2026-01-23T17:03:51.049447'
---
# Вопрос (RU)

> Что такое SAM (Single Abstract Method) конверсии в Kotlin, как они работают для Java и Kotlin интерфейсов, какие ограничения у SAM-конверсий, как использовать SAM-конструкторы и чем SAM-интерфейсы отличаются от типов функций?

# Question (EN)

> What are SAM (Single Abstract Method) conversions in Kotlin, how do they work for Java and Kotlin interfaces, what are their limitations, how are SAM constructors used, and how do SAM interfaces differ from function types?

## Ответ (RU)

**SAM (Single Abstract Method)** конверсии позволяют использовать **лямбда-функции** вместо объектов анонимных классов для интерфейсов с **одним абстрактным методом**. Это делает код короче и читабельнее, особенно при работе с Java API и функциональными интерфейсами.

### Что Такое SAM-интерфейс

**SAM-интерфейс** — это интерфейс с одним абстрактным методом.

```kotlin
// Java
interface OnClickListener {
    void onClick(View view);  // Один абстрактный метод
}

// Kotlin
fun interface OnClickListener {
    fun onClick(view: View)  // Один абстрактный метод
}
```

### SAM-конверсия На Практике

#### До SAM (старый подход)

```kotlin
// Анонимный класс — многословно
button.setOnClickListener(object : View.OnClickListener {
    override fun onClick(v: View) {
        println("Button clicked!")
    }
})
```

#### С SAM-конверсией

```kotlin
// Лямбда — короче и читабельнее
button.setOnClickListener { v ->
    println("Button clicked!")
}

// Или ещё короче (если параметр не используется)
button.setOnClickListener {
    println("Button clicked!")
}
```

### SAM Для Java-интерфейсов

Kotlin автоматически применяет SAM-конверсии к **Java** интерфейсам с одним абстрактным методом, таким как `Runnable`, `Callable`, `Comparator` и слушатели Android.

```java
// Java-интерфейсы
public interface Runnable {
    void run();
}

public interface Callable<V> {
    V call() throws Exception;
}

public interface Comparator<T> {
    int compare(T o1, T o2);
}
```

```kotlin
// Runnable
Thread {
    println("Running in thread")
}.start()

// Вместо:
Thread(object : Runnable {
    override fun run() {
        println("Running in thread")
    }
}).start()

// Callable
val executor = Executors.newSingleThreadExecutor()
val future = executor.submit<String> {
    "Result from callable"
}

// Comparator
val numbers = listOf(3, 1, 4, 1, 5, 9)
val sorted = numbers.sortedWith { a, b -> a.compareTo(b) }

// Явно через SAM-конструктор Comparator
val sorted2 = numbers.sortedWith(Comparator { a, b -> a - b })
```

### SAM Для Kotlin-интерфейсов (`fun interface`)

Для SAM-конверсии Kotlin-интерфейсов используется модификатор `fun interface` (начиная с Kotlin 1.4).

```kotlin
// SAM-интерфейс в Kotlin
fun interface StringTransformer {
    fun transform(input: String): String
}

// Функция, принимающая SAM-интерфейс
fun processString(input: String, transformer: StringTransformer): String {
    return transformer.transform(input)
}

// SAM-конверсия: использование лямбды
val result = processString("hello") { it.uppercase() }
println(result)  // HELLO

// Ссылки на функции тоже работают
val result2 = processString("world", String::uppercase)
println(result2)  // WORLD

// Без fun interface пришлось бы писать анонимный объект
val result3 = processString("test", object : StringTransformer {
    override fun transform(input: String) = input.uppercase()
})
```

Обычный `interface` с одним методом в Kotlin не становится SAM-совместимым для Kotlin-лямбд без `fun interface`.

### Практические Примеры

#### Пример 1: Android OnClickListener

```kotlin
// Java-интерфейс из Android SDK
// public interface OnClickListener {
//     void onClick(View v);
// }

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val button = findViewById<Button>(R.id.myButton)

        // Без SAM — многословно
        button.setOnClickListener(object : View.OnClickListener {
            override fun onClick(v: View) {
                Toast.makeText(this@MainActivity, "Clicked!", Toast.LENGTH_SHORT).show()
            }
        })

        // С SAM — короче
        button.setOnClickListener { v ->
            Toast.makeText(this, "Clicked!", Toast.LENGTH_SHORT).show()
        }

        // Параметр не используется
        button.setOnClickListener {
            Toast.makeText(this, "Clicked!", Toast.LENGTH_SHORT).show()
        }
    }
}
```

#### Пример 2: RecyclerView Adapter (лямбда Как коллбек)

```kotlin
class UserAdapter(
    private val users: List<User>,
    private val onItemClick: (User) -> Unit  // Тип функции (не SAM), но используется с лямбдой
) : RecyclerView.Adapter<UserAdapter.ViewHolder>() {

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val user = users[position]
        holder.bind(user)
        holder.itemView.setOnClickListener {
            onItemClick(user)
        }
    }

    // ...
}

// Использование
val adapter = UserAdapter(users) { user ->
    navigateToDetails(user.id)
}
```

#### Пример 3: Кастомный SAM-интерфейс Validator

```kotlin
// Валидатор данных
fun interface Validator<T> {
    fun validate(value: T): Boolean
}

data class User(val name: String, val email: String, val age: Int)

class UserRepository {
    fun findUsers(validator: Validator<User>): List<User> {
        val allUsers = getAllUsers()
        return allUsers.filter { validator.validate(it) }
    }
}

// Использование
val repo = UserRepository()

// SAM-конверсия: лямбда вместо объекта
val adults = repo.findUsers { user -> user.age >= 18 }

val withValidEmail = repo.findUsers { user ->
    user.email.contains("@") && user.email.contains(".")
}

// Переиспользуем валидаторы
val emailValidator = Validator<User> { it.email.contains("@") }
val validUsers = repo.findUsers(emailValidator)
```

#### Пример 4: Обработчики Событий (EventBus)

```kotlin
fun interface EventHandler<T> {
    fun handle(event: T)
}

class EventBus {
    private val handlers = mutableMapOf<String, MutableList<EventHandler<Any>>>()

    fun <T : Any> subscribe(eventType: String, handler: EventHandler<T>) {
        @Suppress("UNCHECKED_CAST")
        handlers.getOrPut(eventType) { mutableListOf() }
            .add(handler as EventHandler<Any>)  // небезопасное приведение, полагаемся на корректное использование
    }

    fun <T : Any> publish(eventType: String, event: T) {
        handlers[eventType]?.forEach { handler ->
            @Suppress("UNCHECKED_CAST")
            (handler as EventHandler<T>).handle(event)
        }
    }
}

// Использование (предполагается, что типы согласованы)
data class UserLoggedIn(val userId: Int, val timestamp: Long)
data class MessageReceived(val from: String, val text: String)

val eventBus = EventBus()

eventBus.subscribe("user.login") { event: UserLoggedIn ->
    println("User ${event.userId} logged in at ${event.timestamp}")
}

eventBus.subscribe("message.received") { event: MessageReceived ->
    println("Message from ${event.from}: ${event.text}")
}

// Публикация
eventBus.publish("user.login", UserLoggedIn(123, System.currentTimeMillis()))
eventBus.publish("message.received", MessageReceived("Alice", "Hello!"))
```

### SAM-конструктор

SAM-инстанс можно создать явно через синтаксис конструктора SAM-интерфейса. Это полезно при неоднозначности перегрузок.

```kotlin
fun interface StringMapper {
    fun map(input: String): String
}

// Неявная SAM-конверсия
val mapper1: StringMapper = { it.uppercase() }

// Явный SAM-конструктор
val mapper2 = StringMapper { it.uppercase() }

// Пример разрешения перегрузок
fun process(mapper: StringMapper) { }
fun process(transformer: (String) -> String) { }

// Явно выбираем перегрузку с SAM-интерфейсом
process(StringMapper { it.uppercase() })
```

### Ограничения SAM-конверсий

**1. Только для интерфейсов с одним абстрактным методом**

```kotlin
// Не SAM — два абстрактных метода
interface MultiMethod {
    fun method1()
    fun method2()
}

// SAM-конверсия не сработает
val obj = MultiMethod { /* ... */ }  // ОШИБКА

// SAM — один абстрактный метод
fun interface SingleMethod {
    fun method()
}

val obj2 = SingleMethod { /* ... */ }  // OK
```

**2. Методы по умолчанию не считаются абстрактными**

```kotlin
// SAM — только один АБСТРАКТНЫЙ метод
fun interface Processor {
    fun process(input: String): String

    // Метод по умолчанию не влияет на SAM-свойство
    fun log(message: String) {
        println(message)
    }
}

val processor = Processor { it.uppercase() }  // OK
```

**3. Kotlin-интерфейсы требуют `fun interface` для SAM-конверсии**

```kotlin
// Обычный Kotlin-интерфейс — не рассматривается как SAM для Kotlin-лямбд
interface Transformer {
    fun transform(input: String): String
}

val t1 = Transformer { it.uppercase() }  // ОШИБКА

// fun interface — SAM-конверсия работает
fun interface TransformerFun {
    fun transform(input: String): String
}

val t2 = TransformerFun { it.uppercase() }  // OK
```

**4. Java-интерфейсы поддерживаются автоматически**

```kotlin
// Java-интерфейс (например, Runnable)
// interface Runnable { void run(); }

// SAM-конверсия работает без `fun interface`
val runnable = Runnable { println("Running") }  // OK
```

### Сравнение С Высшими Функциями (function types)

```kotlin
// Подход 1: SAM-интерфейс
fun interface ClickHandler {
    fun onClick()
}

fun setHandler(handler: ClickHandler) {
    handler.onClick()
}

setHandler { println("Clicked") }

// Подход 2: Тип функции (higher-order function)
fun setHandlerFn(handler: () -> Unit) {
    handler()
}

setHandlerFn { println("Clicked") }
```

Когда выбирать SAM-интерфейс:
- Для interop с Java (`Runnable`, `OnClickListener`, `Executor` и т.п.).
- Когда нужен именованный функциональный тип с чёткой семантикой.
- Когда предполагаются несколько реализаций и/или вы хотите документировать контракт как интерфейс.

Когда выбирать тип функции `(T) -> R`:
- Для чистого Kotlin-кода без требований Java interop.
- Когда важна простота сигнатур и минимум обёрток.

SAM-конструкторы (`Runnable { ... }`, `Comparator { ... }`, `StringMapper { ... }`) помогают явно указать использование функционального интерфейса и разрешить неоднозначность перегрузок.

## Answer (EN)

**SAM (Single Abstract Method) conversions** allow using **lambda functions** instead of anonymous class/interface objects for interfaces with **one abstract method**. This makes code more concise and readable, especially when working with Java APIs or functional interfaces.

### What is a SAM Interface

A **SAM interface** is an interface with exactly one abstract method.

```kotlin
// Java
interface OnClickListener {
    void onClick(View view);  // One abstract method
}

// Kotlin
fun interface OnClickListener {
    fun onClick(view: View)  // One abstract method
}
```

### SAM Conversion in Action

#### Before SAM (old approach)

```kotlin
// Anonymous class - verbose
button.setOnClickListener(object : View.OnClickListener {
    override fun onClick(v: View) {
        println("Button clicked!")
    }
})
```

#### With SAM Conversion

```kotlin
// Lambda - concise and readable
button.setOnClickListener { v ->
    println("Button clicked!")
}

// Or even shorter (if parameter not used)
button.setOnClickListener {
    println("Button clicked!")
}
```

### Java SAM Interfaces

Kotlin automatically applies SAM conversions to **Java** interfaces that have a single abstract method:

```java
// Java interfaces
public interface Runnable {
    void run();
}

public interface Callable<V> {
    V call() throws Exception;
}

public interface Comparator<T> {
    int compare(T o1, T o2);
}
```

```kotlin
// Usage in Kotlin with SAM conversions

// Runnable
Thread {
    println("Running in thread")
}.start()

// Instead of:
Thread(object : Runnable {
    override fun run() {
        println("Running in thread")
    }
}).start()

// Callable
val executor = Executors.newSingleThreadExecutor()
val future = executor.submit<String> {
    "Result from callable"
}

// Comparator
val numbers = listOf(3, 1, 4, 1, 5, 9)
val sorted = numbers.sortedWith { a, b -> a.compareTo(b) }

// Or explicitly via a Comparator SAM constructor
val sorted2 = numbers.sortedWith(Comparator { a, b -> a - b })
```

### Kotlin SAM Interfaces (fun interface)

Since Kotlin 1.4, SAM conversion is also supported for Kotlin interfaces marked with `fun interface`.

```kotlin
// SAM interface declaration in Kotlin
fun interface StringTransformer {
    fun transform(input: String): String
}

// Function accepting SAM interface
fun processString(input: String, transformer: StringTransformer): String {
    return transformer.transform(input)
}

// Usage with lambda (SAM conversion applies)
val result = processString("hello") { it.uppercase() }
println(result)  // HELLO

// Or with function reference
val result2 = processString("world", String::uppercase)
println(result2)  // WORLD

// Without fun interface you would have to write:
val result3 = processString("test", object : StringTransformer {
    override fun transform(input: String) = input.uppercase()
})
```

### Practical Examples

#### Example 1: Android OnClickListener

```kotlin
// Java interface from Android SDK
// public interface OnClickListener {
//     void onClick(View v);
// }

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val button = findViewById<Button>(R.id.myButton)

        // Without SAM - verbose
        button.setOnClickListener(object : View.OnClickListener {
            override fun onClick(v: View) {
                Toast.makeText(this@MainActivity, "Clicked!", Toast.LENGTH_SHORT).show()
            }
        })

        // With SAM - concise
        button.setOnClickListener { v ->
            Toast.makeText(this, "Clicked!", Toast.LENGTH_SHORT).show()
        }

        // Even shorter (parameter not used)
        button.setOnClickListener {
            Toast.makeText(this, "Clicked!", Toast.LENGTH_SHORT).show()
        }
    }
}
```

#### Example 2: RecyclerView Adapter

```kotlin
class UserAdapter(
    private val users: List<User>,
    private val onItemClick: (User) -> Unit  // Kotlin function type, not SAM, but used with a lambda
) : RecyclerView.Adapter<UserAdapter.ViewHolder>() {

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val user = users[position]
        holder.bind(user)
        holder.itemView.setOnClickListener {
            onItemClick(user)  // uses the provided lambda
        }
    }

    // ...
}

// Usage
val adapter = UserAdapter(users) { user ->
    navigateToDetails(user.id)
}
```

#### Example 3: Custom SAM Interface (Validator)

```kotlin
// Data validator
fun interface Validator<T> {
    fun validate(value: T): Boolean
}

data class User(val name: String, val email: String, val age: Int)

class UserRepository {
    fun findUsers(validator: Validator<User>): List<User> {
        val allUsers = getAllUsers()
        return allUsers.filter { validator.validate(it) }
    }
}

// Usage
val repo = UserRepository()

// SAM conversion: lambda instead of an object
val adults = repo.findUsers { user -> user.age >= 18 }

val withValidEmail = repo.findUsers { user ->
    user.email.contains("@") && user.email.contains(".")
}

// You can reuse validators
val emailValidator = Validator<User> { it.email.contains("@") }
val validUsers = repo.findUsers(emailValidator)
```

#### Example 4: Event Handlers (EventBus)

```kotlin
fun interface EventHandler<T> {
    fun handle(event: T)
}

class EventBus {
    private val handlers = mutableMapOf<String, MutableList<EventHandler<Any>>>()

    fun <T : Any> subscribe(eventType: String, handler: EventHandler<T>) {
        @Suppress("UNCHECKED_CAST")
        handlers.getOrPut(eventType) { mutableListOf() }
            .add(handler as EventHandler<Any>)  // unsafe cast, relies on consistent usage
    }

    fun <T : Any> publish(eventType: String, event: T) {
        handlers[eventType]?.forEach { handler ->
            // unchecked cast at call site; simplified for example purposes
            @Suppress("UNCHECKED_CAST")
            (handler as EventHandler<T>).handle(event)
        }
    }
}

// Usage (assumes consistent event types; otherwise may cause ClassCastException)
data class UserLoggedIn(val userId: Int, val timestamp: Long)
data class MessageReceived(val from: String, val text: String)

val eventBus = EventBus()

// SAM conversions for subscription
eventBus.subscribe("user.login") { event: UserLoggedIn ->
    println("User ${event.userId} logged in at ${event.timestamp}")
}

eventBus.subscribe("message.received") { event: MessageReceived ->
    println("Message from ${event.from}: ${event.text}")
}

// Publishing
eventBus.publish("user.login", UserLoggedIn(123, System.currentTimeMillis()))
eventBus.publish("message.received", MessageReceived("Alice", "Hello!"))
```

### SAM Constructor

You can explicitly create a SAM instance via its constructor syntax:

```kotlin
fun interface StringMapper {
    fun map(input: String): String
}

// Implicit SAM conversion
val mapper1: StringMapper = { it.uppercase() }

// Explicit SAM constructor
val mapper2 = StringMapper { it.uppercase() }

// Useful when there is type ambiguity
fun process(mapper: StringMapper) { }
fun process(transformer: (String) -> String) { }

// Disambiguate which overload to call
process(StringMapper { it.uppercase() })  // uses SAM overload
```

### SAM Conversion Limitations

1. Only for interfaces with one abstract method.

```kotlin
// Not SAM - two abstract methods
interface MultiMethod {
    fun method1()
    fun method2()
}

// SAM conversion does NOT work
val obj = MultiMethod { /* ... */ }  // ERROR

// SAM - one abstract method
fun interface SingleMethod {
    fun method()
}

val obj2 = SingleMethod { /* ... */ }  // OK
```

1. Default methods do not count as abstract.

```kotlin
// SAM - only one ABSTRACT method
fun interface Processor {
    fun process(input: String): String

    // Default method does not count as abstract
    fun log(message: String) {
        println(message)
    }
}

val processor = Processor { it.uppercase() }  // OK
```

1. Kotlin interfaces require `fun interface` for SAM conversion.

```kotlin
// Regular Kotlin interface - NOT treated as SAM for Kotlin SAM conversion
interface Transformer {
    fun transform(input: String): String
}

val t1 = Transformer { it.uppercase() }  // ERROR

// fun interface - SAM conversion works
fun interface TransformerFun {
    fun transform(input: String): String
}

val t2 = TransformerFun { it.uppercase() }  // OK
```

1. Java interfaces are supported automatically.

```kotlin
// Java interface (from library)
// interface Runnable { void run(); }

// SAM conversion works without fun interface
val runnable = Runnable { println("Running") }  // OK
```

### Comparison with Higher-Order Functions

```kotlin
// Approach 1: SAM interface
fun interface ClickHandler {
    fun onClick()
}

fun setHandler(handler: ClickHandler) {
    handler.onClick()
}

setHandler { println("Clicked") }

// Approach 2: Higher-order function (function type)
fun setHandlerFn(handler: () -> Unit) {
    handler()
}

setHandlerFn { println("Clicked") }
```

When to use SAM:
- Interoperating with Java and existing functional interfaces (`Runnable`, `OnClickListener`, `Executor`, etc.).
- When you want a named functional type with clear semantics.
- When you plan to have multiple implementations of the interface.

When to use function types `(T) -> R`:
- In pure Kotlin code without specific Java interop requirements.
- When you prefer simpler signatures and minimal wrappers.

SAM constructors like `Runnable { ... }`, `Comparator { ... }`, `StringMapper { ... }` help disambiguate overloads and explicitly select the functional interface overload.

## Дополнительные Вопросы (RU)

- В чем ключевые отличия SAM-конверсий Kotlin от Java-подхода?
- Когда вы бы использовали SAM-конверсии на практике?
- Какие типичные ошибки и подводные камни при использовании SAM-конверсий?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [[c-kotlin]]
- "Kotlin Documentation" — https://kotlinlang.org/docs/home.html

## References

- https://kotlinlang.org/docs/home.html

## Связанные Вопросы (RU)

- [[q-flow-exception-handling--kotlin--medium]]
- [[q-kotlin-inline-functions--kotlin--medium]]
- [[q-object-companion-object--kotlin--medium]]

## Related Questions

- [[q-flow-exception-handling--kotlin--medium]]
- [[q-kotlin-inline-functions--kotlin--medium]]
- [[q-object-companion-object--kotlin--medium]]
