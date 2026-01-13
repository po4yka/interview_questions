---
anki_cards:
- slug: q-companion-object-initialization--kotlin--easy-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-companion-object-initialization--kotlin--easy-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
---\
id: kotlin-222
title: "Companion Object Initialization / Инициализация Companion Object"
aliases: [Companion Object Initialization, Инициализация Companion Object]
topic: kotlin
subtopics: [companion-object]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, c-kotlin-features, q-abstract-class-vs-interface--kotlin--medium]
created: 2025-10-15
updated: 2025-11-10
tags: [companion-objects, difficulty/easy, initialization, programming-languages]
---\
# Вопрос (RU)
> Когда инициализируется companion object в Kotlin?

# Question (EN)
> When is a companion object initialized in Kotlin?

## Ответ (RU)

Companion object инициализируется **при инициализации соответствующего класса** (на JVM — при инициализации сгенерированного `Companion`/класса-холдера), которая обычно происходит при первом реальном использовании его членов или других статических аспектов класса. Инициализация выполняется один раз; дальнейшие обращения используют уже инициализированный объект.

Важно: точный момент инициализации зависит от целевой платформы и правил инициализации классов (особенно на JVM). Поэтому фразу "лениво при первом использовании" стоит понимать как практическое наблюдение, а не как жесткую гарантию, отделенную от механики инициализации класса: создание экземпляра, статические вызовы или другие обращения, которые требуют инициализации класса согласно семантике платформы, могут инициализировать companion object раньше, чем первое явное обращение к его членам.

**Ключевые моменты:**
- Инициализация companion object привязана к инициализации соответствующего класса
- Обычно выглядит как "ленивая" (часто происходит при первом фактическом использовании), но не гарантируется отдельно от правил инициализации класса
- Потокобезопасна по умолчанию (инициализация выполняется один раз, даже при многопоточном доступе)
- Инициализируется только один раз за весь жизненный цикл процесса
- На JVM поведение сопоставимо со статическими блоками инициализации и правилами инициализации классов в Java

**Не гарантировано, что companion object НЕ будет инициализирован, если:**
- Просто создается экземпляр содержащего класса: в конкретной ситуации это может привести к инициализации companion object, если сгенерированный байткод/семантика платформы требуют инициализации класса
- Класс загружен: при определенных обращениях к статическим элементам/метаданным или особенностях реализации инициализация может произойти до первого явного обращения к членам companion object

(Примеры ниже иллюстрируют типичное поведение; фактический момент инициализации может отличаться в зависимости от платформы и реализации.)

### Пример Базовой Инициализации

```kotlin
class MyClass {
    companion object {
        init {
            println("Companion object initialized!")
        }
        val value = "Hello"
    }

    init {
        println("MyClass instance created!")
    }
}

fun main() {
    println("Before creating instance")
    val instance = MyClass()  // Инициализация класса (и companion) может произойти здесь в зависимости от платформы/JVM

    println("\nBefore accessing companion")
    println(MyClass.value)    // Если companion еще не инициализирован, он будет инициализирован к этому моменту

    println("\nAccessing companion again")
    println(MyClass.value)    // Повторное обращение: только "Hello" (companion уже инициализирован)
}
```

### Инициализация Companion Object С Состоянием

```kotlin
class Database {
    companion object {
        private var connectionCount = 0

        init {
            println("Initializing Database companion object...")
            connectionCount = 0
        }

        fun connect(): String {
            connectionCount++
            return "Connection #$connectionCount established"
        }

        fun getStats(): String {
            return "Total connections: $connectionCount"
        }
    }
}

fun main() {
    println("Starting application...")
    val db1 = Database()
    println("Created Database instance")

    println("\nFirst companion access:")
    println(Database.connect())

    println("\nSecond companion access:")
    println(Database.connect())

    println(Database.getStats())
}
```

### Один Companion Для Множества Экземпляров

```kotlin
class Counter(val instanceId: Int) {
    companion object {
        var instanceCount = 0
            private set

        private val creationTime = System.currentTimeMillis()

        init {
            println("Companion object initialized at $creationTime")
        }

        fun getInstanceCount() = instanceCount
        fun getCreationTime() = creationTime
    }

    init {
        instanceCount++
        println("Instance #$instanceId created (total: $instanceCount)")
    }
}

fun main() {
    println("Creating first instance:")
    val c1 = Counter(1)

    println("\nCreating second instance:")
    val c2 = Counter(2)

    println("\nCreating third instance:")
    val c3 = Counter(3)

    println("\nTotal instances: ${Counter.getInstanceCount()}")
}
```

### Ленивая Семантика И Дорогостоящая Инициализация

```kotlin
class ExpensiveResource {
    companion object {
        init {
            println("Loading expensive resources...")
            Thread.sleep(1000)
            println("Resources loaded!")
        }

        fun doSomething() {
            println("Doing something with resources")
        }
    }

    init {
        println("ExpensiveResource instance created")
    }
}

fun main() {
    println("Application started")

    println("\nCreating instances...")
    val r1 = ExpensiveResource()
    val r2 = ExpensiveResource()

    println("\nNow accessing companion for first time...")
    ExpensiveResource.doSomething()

    println("\nAccessing companion again...")
    ExpensiveResource.doSomething()
}
```

### Порядок Инициализации При Наследовании

```kotlin
open class Base {
    companion object {
        init {
            println("Base companion initialized")
        }

        val baseValue = "Base"
    }

    init {
        println("Base instance created")
    }
}

class Derived : Base() {
    companion object {
        init {
            println("Derived companion initialized")
        }

        val derivedValue = "Derived"
    }

    init {
        println("Derived instance created")
    }
}

fun main() {
    println("Creating Derived instance:")
    val d = Derived()

    println("\nAccessing Base companion:")
    println(Base.baseValue)

    println("\nAccessing Derived companion:")
    println(Derived.derivedValue)
}
```

### Компаньон Как Фабрика (ленивая Инициализация фабрики)

```kotlin
class User private constructor(val id: Int, val name: String) {
    companion object {
        private val users = mutableMapOf<Int, User>()
        private var nextId = 1

        init {
            println("User companion object initialized")
            println("User factory ready")
        }

        fun create(name: String): User {
            val user = User(nextId++, name)
            users[user.id] = user
            return user
        }

        fun getById(id: Int): User? = users[id]

        fun getAllUsers(): List<User> = users.values.toList()
    }
}

fun main() {
    println("Application started")

    println("\nCreating first user:")
    val user1 = User.create("Alice")

    println("User created: ${user1.name} (ID: ${user1.id})")

    val user2 = User.create("Bob")
    println("User created: ${user2.name} (ID: ${user2.id})")

    println("\nAll users: ${User.getAllUsers().map { it.name }}")
}
```

### Потокобезопасная Инициализация

```kotlin
class ThreadSafeExample {
    companion object {
        private var initializationThread: String? = null

        init {
            initializationThread = Thread.currentThread().name
            println("Initialized by thread: $initializationThread")
        }

        fun getInitThread() = initializationThread
    }
}

fun main() {
    val threads = List(10) { index ->
        Thread {
            println("Thread $index accessing companion")
            ThreadSafeExample.getInitThread()
        }
    }

    threads.forEach { it.start() }
    threads.forEach { it.join() }

    println("\nInitialized by: ${ThreadSafeExample.getInitThread()}")
}
```

### Избежание Преждевременной Инициализации (иллюстрация Возможной проблемы)

```kotlin
class ConfigManager {
    companion object {
        init {
            println("Loading configuration from file...")
            Thread.sleep(500)
            println("Configuration loaded!")
        }

        private val config = mapOf(
            "api_url" to "https://api.example.com",
            "timeout" to "30",
            "debug" to "true"
        )

        fun get(key: String): String? = config[key]
    }
}

fun main() {
    println("App starting...")

    println("Doing some work...")
    repeat(3) { i ->
        println("  Step ${i + 1}")
        Thread.sleep(200)
    }

    println("\nNeed configuration now:")
    val apiUrl = ConfigManager.get("api_url")
    println("API URL: $apiUrl")
}
```

(В этом примере тяжелая инициализация по-прежнему происходит при инициализации класса/companion object; код иллюстрирует, как такая инициализация может сработать раньше или позже в зависимости от того, когда класс будет инициализирован, и показывает потенциальную проблему, а не решение.)

## Answer (EN)

A companion object is initialized **when its containing class (or the generated `Companion`/holder class) is initialized**, which typically happens around the first real use of its members or other static aspects of the class. Initialization happens once; all subsequent accesses use the already initialized instance.

Important: The exact timing depends on the target platform and class initialization rules (notably on the JVM). The common "initialized on first use" description is a useful intuition, but not a strict, platform-independent guarantee decoupled from class initialization. Creating instances, calling certain methods, or other accesses that, per platform semantics, require class initialization may trigger the companion object initialization earlier than the first explicit access to its members.

**Key points:**
- Companion object initialization is tied to initialization of the corresponding class
- Often appears "lazy" (commonly near first actual use), but this is not a separate hard guarantee from the class initialization rules
- `Thread`-safe by default (initialization happens only once, even with concurrent access)
- Initialized only once for the process lifetime
- On the JVM, behavior aligns with Java's class initialization and static initializer semantics

**Not guaranteed to avoid initialization when:**
- Merely creating an instance of the containing class: in specific cases this can cause class (and thus companion) initialization, depending on generated bytecode and platform rules
- The class is loaded: certain metadata or static accesses/optimizations may cause initialization before the first explicit companion member use

(The examples below illustrate typical behavior; actual timing may vary by platform and implementation.)

### Code Examples

#### Basic Initialization Timing

```kotlin
class MyClass {
    companion object {
        init {
            println("Companion object initialized!")
        }

        val value = "Hello"
    }

    init {
        println("MyClass instance created!")
    }
}

fun main() {
    println("Before creating instance")
    val instance = MyClass()  // On JVM/platforms, class (and companion) initialization may occur here depending on semantics

    println("\nBefore accessing companion")
    println(MyClass.value)    // If not yet initialized, companion will be initialized by this point

    println("\nAccessing companion again")
    println(MyClass.value)
}
```

#### Companion Object Initialization with State

```kotlin
class Database {
    companion object {
        private var connectionCount = 0

        init {
            println("Initializing Database companion object...")
            connectionCount = 0
        }

        fun connect(): String {
            connectionCount++
            return "Connection #$connectionCount established"
        }

        fun getStats(): String {
            return "Total connections: $connectionCount"
        }
    }
}

fun main() {
    println("Starting application...")
    val db1 = Database()
    println("Created Database instance")

    println("\nFirst companion access:")
    println(Database.connect())

    println("\nSecond companion access:")
    println(Database.connect())

    println(Database.getStats())
}
```

#### One Companion for Many Instances

```kotlin
class Counter(val instanceId: Int) {
    companion object {
        var instanceCount = 0
            private set

        private val creationTime = System.currentTimeMillis()

        init {
            println("Companion object initialized at $creationTime")
        }

        fun getInstanceCount() = instanceCount
        fun getCreationTime() = creationTime
    }

    init {
        instanceCount++
        println("Instance #$instanceId created (total: $instanceCount)")
    }
}

fun main() {
    println("Creating first instance:")
    val c1 = Counter(1)

    println("\nCreating second instance:")
    val c2 = Counter(2)

    println("\nCreating third instance:")
    val c3 = Counter(3)

    println("\nTotal instances: ${Counter.getInstanceCount()}")
}
```

#### Lazy-like Semantics and Expensive Initialization

```kotlin
class ExpensiveResource {
    companion object {
        init {
            println("Loading expensive resources...")
            Thread.sleep(1000)
            println("Resources loaded!")
        }

        fun doSomething() {
            println("Doing something with resources")
        }
    }

    init {
        println("ExpensiveResource instance created")
    }
}

fun main() {
    println("Application started")

    println("\nCreating instances...")
    val r1 = ExpensiveResource()
    val r2 = ExpensiveResource()

    println("\nNow accessing companion for first time...")
    ExpensiveResource.doSomething()

    println("\nAccessing companion again...")
    ExpensiveResource.doSomething()
}
```

#### Initialization order with Inheritance

```kotlin
open class Base {
    companion object {
        init {
            println("Base companion initialized")
        }

        val baseValue = "Base"
    }

    init {
        println("Base instance created")
    }
}

class Derived : Base() {
    companion object {
        init {
            println("Derived companion initialized")
        }

        val derivedValue = "Derived"
    }

    init {
        println("Derived instance created")
    }
}

fun main() {
    println("Creating Derived instance:")
    val d = Derived()

    println("\nAccessing Base companion:")
    println(Base.baseValue)

    println("\nAccessing Derived companion:")
    println(Derived.derivedValue)
}
```

#### Companion as Factory (lazy Initialization of factory)

```kotlin
class User private constructor(val id: Int, val name: String) {
    companion object {
        private val users = mutableMapOf<Int, User>()
        private var nextId = 1

        init {
            println("User companion object initialized")
            println("User factory ready")
        }

        fun create(name: String): User {
            val user = User(nextId++, name)
            users[user.id] = user
            return user
        }

        fun getById(id: Int): User? = users[id]

        fun getAllUsers(): List<User> = users.values.toList()
    }
}

fun main() {
    println("Application started")

    println("\nCreating first user:")
    val user1 = User.create("Alice")

    println("User created: ${user1.name} (ID: ${user1.id})")

    val user2 = User.create("Bob")
    println("User created: ${user2.name} (ID: ${user2.id})")

    println("\nAll users: ${User.getAllUsers().map { it.name }}")
}
```

#### Thread-safe Initialization

```kotlin
class ThreadSafeExample {
    companion object {
        private var initializationThread: String? = null

        init {
            initializationThread = Thread.currentThread().name
            println("Initialized by thread: $initializationThread")
        }

        fun getInitThread() = initializationThread
    }
}

fun main() {
    val threads = List(10) { index ->
        Thread {
            println("Thread $index accessing companion")
            ThreadSafeExample.getInitThread()
        }
    }

    threads.forEach { it.start() }
    threads.forEach { it.join() }

    println("\nInitialized by: ${ThreadSafeExample.getInitThread()}")
}
```

#### Avoiding Premature Initialization (illustrating a Potential issue)

```kotlin
class ConfigManager {
    companion object {
        init {
            println("Loading configuration from file...")
            Thread.sleep(500)
            println("Configuration loaded!")
        }

        private val config = mapOf(
            "api_url" to "https://api.example.com",
            "timeout" to "30",
            "debug" to "true"
        )

        fun get(key: String): String? = config[key]
    }
}

fun main() {
    println("App starting...")

    println("Doing some work...")
    repeat(3) { i ->
        println("  Step ${i + 1}")
        Thread.sleep(200)
    }

    println("\nNeed configuration now:")
    val apiUrl = ConfigManager.get("api_url")
    println("API URL: $apiUrl")
}
```

(In this example, heavy work still runs during class/companion initialization; it illustrates how such initialization may happen earlier or later depending on when the class is initialized, highlighting a potential pitfall rather than a solution.)

## Дополнительные Вопросы (RU)

- В чем ключевые отличия поведения companion object по сравнению со `static` в Java?
- Когда на практике стоит опираться на кажущуюся "ленивую" инициализацию companion object и как учитывать правила инициализации класса?
- Какие типичные ошибки связаны с тяжелой инициализацией в companion object с учетом того, что она может выполниться раньше, чем ожидается, и как их избегать?

## Follow-ups (EN)

- What are the key differences between companion object behavior and `static` in Java?
- When would you rely on the apparent "initialized on first use" semantics in practice, and how should you factor in class initialization rules?
- What common pitfalls are associated with heavy initialization in a companion object, given that it may run earlier than expected, and how can they be avoided?

## Ссылки (RU)

- [[c-kotlin]]
- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References (EN)

- [[c-kotlin]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-abstract-class-vs-interface--kotlin--medium]]

## Related Questions (EN)

- [[q-abstract-class-vs-interface--kotlin--medium]]
