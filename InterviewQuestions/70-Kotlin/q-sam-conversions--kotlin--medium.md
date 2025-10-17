---
id: 20251017-150544
title: "Sam Conversions / SAM конверсии"
topic: kotlin
difficulty: medium
status: draft
created: 2025-10-15
tags: - kotlin
  - sam
  - lambda
  - functional-interface
  - java-interop
---
# SAM (Single Abstract Method) конверсии

**English**: SAM (Single Abstract Method) conversions in Kotlin

## Answer (EN)
**SAM conversions** allow using **lambda functions** instead of class/interface objects with **one abstract method**. This makes code more concise and readable when working with Java API or functional interfaces. Instead of creating an anonymous class, you can pass a lambda.

### What is a SAM interface

**SAM** (Single Abstract Method) interface is an interface with **one** abstract method.

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

### SAM conversion in action

#### Before SAM (old approach)

```kotlin
// Anonymous class - verbose
button.setOnClickListener(object : View.OnClickListener {
    override fun onClick(v: View) {
        println("Button clicked!")
    }
})
```

#### With SAM conversion

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

### Java SAM interfaces

Kotlin automatically applies SAM conversions to **Java** interfaces:

```java
// Java интерфейс
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

// Or even shorter
val sorted = numbers.sortedWith(Comparator { a, b -> a - b })
```

### Kotlin SAM interfaces (fun interface)

Since Kotlin 1.4, SAM support for Kotlin interfaces via `fun interface`:

```kotlin
// SAM interface declaration in Kotlin
fun interface StringTransformer {
    fun transform(input: String): String
}

// Function accepting SAM interface
fun processString(input: String, transformer: StringTransformer): String {
    return transformer.transform(input)
}

// Usage with lambda
val result = processString("hello") { it.uppercase() }
println(result)  // HELLO

// Or with reference
val result2 = processString("world", String::uppercase)
println(result2)  // WORLD

// Without fun interface would have to write:
val result3 = processString("test", object : StringTransformer {
    override fun transform(input: String) = input.uppercase()
})
```

### Practical examples

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

        // - Без SAM - многословно
        button.setOnClickListener(object : View.OnClickListener {
            override fun onClick(v: View) {
                Toast.makeText(this@MainActivity, "Clicked!", Toast.LENGTH_SHORT).show()
            }
        })

        // - С SAM - кратко
        button.setOnClickListener { v ->
            Toast.makeText(this, "Clicked!", Toast.LENGTH_SHORT).show()
        }

        // - Еще короче (параметр не используется)
        button.setOnClickListener {
            Toast.makeText(this, "Clicked!", Toast.LENGTH_SHORT).show()
        }
    }
}
```

#### Пример 2: RecyclerView Adapter

```kotlin
class UserAdapter(
    private val users: List<User>,
    private val onItemClick: (User) -> Unit  // Kotlin lambda - проще SAM
) : RecyclerView.Adapter<UserAdapter.ViewHolder>() {

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val user = users[position]
        holder.bind(user)
        holder.itemView.setOnClickListener {
            onItemClick(user)  // SAM-конверсия
        }
    }

    // ...
}

// Использование
val adapter = UserAdapter(users) { user ->
    navigateToDetails(user.id)
}
```

#### Пример 3: Кастомный SAM интерфейс

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

// Можно переиспользовать валидаторы
val emailValidator = Validator<User> { it.email.contains("@") }
val validUsers = repo.findUsers(emailValidator)
```

#### Пример 4: Обработчики событий

```kotlin
fun interface EventHandler<T> {
    fun handle(event: T)
}

class EventBus {
    private val handlers = mutableMapOf<String, MutableList<EventHandler<Any>>>()

    fun <T : Any> subscribe(eventType: String, handler: EventHandler<T>) {
        handlers.getOrPut(eventType) { mutableListOf() }
            .add(handler as EventHandler<Any>)
    }

    fun <T : Any> publish(eventType: String, event: T) {
        handlers[eventType]?.forEach { it.handle(event) }
    }
}

// Использование
data class UserLoggedIn(val userId: Int, val timestamp: Long)
data class MessageReceived(val from: String, val text: String)

val eventBus = EventBus()

// SAM-конверсии для подписки
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

### SAM constructor

Can explicitly create SAM via constructor:

```kotlin
fun interface StringMapper {
    fun map(input: String): String
}

// Implicit SAM conversion
val mapper1: StringMapper = { it.uppercase() }

// Explicit SAM constructor
val mapper2 = StringMapper { it.uppercase() }

// Useful when type ambiguity
fun process(mapper: StringMapper) { }
fun process(transformer: (String) -> String) { }

// Нужно уточнить, какую перегрузку вызываем
process(StringMapper { it.uppercase() })  // SAM
```

### Ограничения SAM-конверсий

**1. Только для интерфейсов с одним абстрактным методом**

```kotlin
// - НЕ SAM - два метода
interface MultiMethod {
    fun method1()
    fun method2()
}

// - Не работает SAM-конверсия
val obj = MultiMethod { ... }  // ERROR

// - SAM - один метод
fun interface SingleMethod {
    fun method()
}

val obj = SingleMethod { ... }  // OK
```

**2. Дефолтные методы не считаются абстрактными**

```kotlin
// - SAM - только один АБСТРАКТНЫЙ метод
fun interface Processor {
    fun process(input: String): String

    // Дефолтный метод не считается
    fun log(message: String) {
        println(message)
    }
}

val processor = Processor { it.uppercase() }  // OK
```

**3. Kotlin интерфейсы требуют `fun interface`**

```kotlin
// - Обычный Kotlin интерфейс - НЕТ SAM
interface Transformer {
    fun transform(input: String): String
}

val t = Transformer { it.uppercase() }  // ERROR

// - fun interface - SAM работает
fun interface Transformer {
    fun transform(input: String): String
}

val t = Transformer { it.uppercase() }  // OK
```

**4. Java интерфейсы работают автоматически**

```kotlin
// Java интерфейс (из библиотеки)
// interface Runnable { void run(); }

// - SAM работает без fun
val runnable = Runnable { println("Running") }  // OK
```

### Сравнение с высшими функциями

```kotlin
// Подход 1: SAM интерфейс
fun interface ClickHandler {
    fun onClick()
}

fun setHandler(handler: ClickHandler) {
    handler.onClick()
}

setHandler { println("Clicked") }

// Подход 2: Высшая функция (function type)
fun setHandler(handler: () -> Unit) {
    handler()
}

setHandler { println("Clicked") }
```

**Когда использовать SAM:**
- Совместимость с Java
- Нужна типобезопасность на уровне интерфейса
- Планируется несколько реализаций

**Когда использовать function type:**
- Чистый Kotlin код
- Нужна простота
- Не требуется Java interop

### Best Practices

**1. Используйте `fun interface` для Kotlin SAM**

```kotlin
// - ПРАВИЛЬНО
fun interface Mapper<T, R> {
    fun map(input: T): R
}

val stringToInt = Mapper<String, Int> { it.length }
```

**2. SAM для Java interop**

```kotlin
// - ПРАВИЛЬНО - работа с Java API
executor.submit {
    doWork()
}

button.setOnClickListener {
    handleClick()
}
```

**3. Function types для чистого Kotlin**

```kotlin
// - ПРАВИЛЬНО - чистый Kotlin
fun processItems(items: List<String>, transform: (String) -> String) {
    items.forEach { println(transform(it)) }
}

processItems(list) { it.uppercase() }
```

**English**: **SAM (Single Abstract Method)** conversions allow using **lambda functions** instead of anonymous class objects for interfaces with **one abstract method**. Works automatically with **Java** interfaces (Runnable, Comparator, OnClickListener). For **Kotlin** interfaces, requires `fun interface` modifier. Example: `button.setOnClickListener { }` instead of `object : OnClickListener { override fun onClick(...) }`. Use SAM for Java interop and type safety. Use function types `(T) -> R` for pure Kotlin code. SAM constructor explicitly creates instance: `Runnable { code }`. Only works with single abstract method - default methods don't count.

## Ответ (RU)

**SAM (Single Abstract Method)** конверсии позволяют использовать **лямбда-функции** вместо объектов анонимных классов для интерфейсов с **одним абстрактным методом**.

### Как работает

Вместо создания анонимного класса можно передать лямбду:

```kotlin
// Без SAM - многословно
button.setOnClickListener(object : View.OnClickListener {
    override fun onClick(v: View) { }
})

// С SAM - кратко
button.setOnClickListener { v -> }
```

### Для Java интерфейсов

Работает автоматически для Java интерфейсов (Runnable, Comparator, OnClickListener)

### Для Kotlin интерфейсов

Требует модификатор `fun interface`:

```kotlin
fun interface StringTransformer {
    fun transform(input: String): String
}

// Использование
val result = processString("hello") { it.uppercase() }
```

### Когда использовать

- **SAM**: для Java interop и типобезопасности
- **Function types** `(T) -> R`: для чистого Kotlin кода

SAM конструктор явно создает экземпляр: `Runnable { code }`. Работает только с одним абстрактным методом - default методы не считаются.

