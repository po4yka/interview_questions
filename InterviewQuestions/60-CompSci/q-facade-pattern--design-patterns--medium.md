---
id: 20251012-1227111134
title: "Facade Pattern / Facade Паттерн"
topic: computer-science
difficulty: medium
status: draft
moc: moc-cs
related: [q-builder-pattern--design-patterns--medium, q-observer-pattern--design-patterns--medium, q-prototype-pattern--design-patterns--medium]
created: 2025-10-15
tags: [design-patterns, facade, gof-patterns, structural-patterns]
date created: Monday, October 6th 2025, 7:22:08 am
date modified: Sunday, October 26th 2025, 11:57:41 am
---

# Facade Pattern

# Question (EN)
> What is the Facade pattern? When and why should it be used?

# Вопрос (RU)
> Что такое паттерн Facade? Когда и зачем его использовать?

---

## Answer (EN)


**Facade (Фасад)** - это структурный паттерн проектирования, который предоставляет простой интерфейс к сложной системе классов, библиотеке или фреймворку. Фасад скрывает сложность системы и предоставляет клиенту простой способ взаимодействия.

### Definition


Facade pattern is a structural design pattern whose purpose is to **hide internal complexity behind a single interface that appears simple from the outside**. It provides a simplified interface to a complex subsystem.

### Problems it Solves


What problems can the Facade design pattern solve?

1. **To make a complex subsystem easier to use, a simple interface should be provided for a set of interfaces in the subsystem**
2. **The dependencies on a subsystem should be minimized**

### Key Points


Key Points of the Facade Pattern:

1. **Simplification** - Provides a simplified interface to a complex system of classes
2. **Decoupling** - Decouples the client code from the internal workings of the system
3. **Easier Maintenance** - Allows for easier maintenance, as changes in underlying subsystems don't directly affect client code

## Пример: Home Theater

```kotlin
// Subsystems
class Lights {
    fun dim() {
        println("Lights dimmed.")
    }

    fun on() {
        println("Lights turned on.")
    }
}

class Blinds {
    fun lower() {
        println("Blinds lowered.")
    }

    fun raise() {
        println("Blinds raised.")
    }
}

class Projector {
    fun turnOn() {
        println("Projector turned on.")
    }

    fun turnOff() {
        println("Projector turned off.")
    }
}

class MoviePlayer {
    fun play() {
        println("Movie started playing.")
    }

    fun stop() {
        println("Movie stopped.")
    }
}

// Facade
class HomeTheaterFacade(
    private val lights: Lights,
    private val blinds: Blinds,
    private val projector: Projector,
    private val moviePlayer: MoviePlayer
) {
    fun watchMovie() {
        println("Getting ready to watch movie...")
        lights.dim()
        blinds.lower()
        projector.turnOn()
        moviePlayer.play()
    }

    fun endMovie() {
        println("Shutting down movie theater...")
        moviePlayer.stop()
        projector.turnOff()
        blinds.raise()
        lights.on()
    }
}

fun main() {
    val homeTheater = HomeTheaterFacade(
        Lights(), Blinds(), Projector(), MoviePlayer()
    )
    homeTheater.watchMovie()
    println()
    homeTheater.endMovie()
}
```

**Output**:
```
Getting ready to watch movie...
Lights dimmed.
Blinds lowered.
Projector turned on.
Movie started playing.

Shutting down movie theater...
Movie stopped.
Projector turned off.
Blinds raised.
Lights turned on.
```

## Android Example: Retrofit Facade

```kotlin
// Complex subsystems
class NetworkClient {
    private val retrofit = Retrofit.Builder()
        .baseUrl("https://api.example.com")
        .addConverterFactory(GsonConverterFactory.create())
        .build()

    fun <T> createService(serviceClass: Class<T>): T {
        return retrofit.create(serviceClass)
    }
}

class CacheManager(private val context: Context) {
    fun saveToCache(key: String, data: String) {
        context.getSharedPreferences("cache", Context.MODE_PRIVATE)
            .edit()
            .putString(key, data)
            .apply()
    }

    fun getFromCache(key: String): String? {
        return context.getSharedPreferences("cache", Context.MODE_PRIVATE)
            .getString(key, null)
    }
}

class ErrorHandler {
    fun handleError(error: Throwable): String {
        return when (error) {
            is IOException -> "Network error occurred"
            is HttpException -> "Server error: ${error.code()}"
            else -> "Unknown error occurred"
        }
    }
}

// Facade - Simple API interface
class ApiFacade(private val context: Context) {
    private val networkClient = NetworkClient()
    private val cacheManager = CacheManager(context)
    private val errorHandler = ErrorHandler()

    suspend fun getUserData(userId: String): Result<User> {
        return try {
            // Check cache first
            val cached = cacheManager.getFromCache("user_$userId")
            if (cached != null) {
                return Result.success(Gson().fromJson(cached, User::class.java))
            }

            // Fetch from network
            val api = networkClient.createService(ApiService::class.java)
            val user = api.getUser(userId)

            // Save to cache
            cacheManager.saveToCache("user_$userId", Gson().toJson(user))

            Result.success(user)
        } catch (e: Exception) {
            Result.failure(Exception(errorHandler.handleError(e)))
        }
    }

    suspend fun updateUser(user: User): Result<Unit> {
        return try {
            val api = networkClient.createService(ApiService::class.java)
            api.updateUser(user)
            cacheManager.saveToCache("user_${user.id}", Gson().toJson(user))
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(Exception(errorHandler.handleError(e)))
        }
    }
}

// Client code - simple to use!
class UserRepository(context: Context) {
    private val apiFacade = ApiFacade(context)

    suspend fun getUser(id: String) = apiFacade.getUserData(id)
    suspend fun updateUser(user: User) = apiFacade.updateUser(user)
}
```

## Kotlin Example: Database Facade

```kotlin
// Complex subsystems
class DatabaseConnection {
    fun connect() = println("Database connected")
    fun disconnect() = println("Database disconnected")
}

class QueryBuilder {
    fun buildSelectQuery(table: String, where: String) =
        "SELECT * FROM $table WHERE $where"
}

class ResultProcessor {
    fun <T> processResult(rawData: List<Any>, type: Class<T>): List<T> {
        // Complex processing logic
        return rawData.map { it as T }
    }
}

// Facade
class DatabaseFacade {
    private val connection = DatabaseConnection()
    private val queryBuilder = QueryBuilder()
    private val processor = ResultProcessor()

    fun <T> queryData(table: String, where: String, type: Class<T>): List<T> {
        connection.connect()
        val query = queryBuilder.buildSelectQuery(table, where)
        println("Executing: $query")
        val rawData = listOf<Any>() // Simulated DB result
        val result = processor.processResult(rawData, type)
        connection.disconnect()
        return result
    }
}

// Simple usage
fun main() {
    val db = DatabaseFacade()
    val users = db.queryData("users", "age > 18", User::class.java)
}
```

### Explanation


**Explanation**:

- **Subsystems** (Lights, Blinds, Projector, MoviePlayer) are complex individual components
- **Facade** (HomeTheaterFacade) provides simple methods (`watchMovie()`, `endMovie()`) that orchestrate multiple subsystems
- **Client** only interacts with the facade, not the complex subsystems
- In Android, facades simplify complex operations like network + cache + error handling

## Применение

Use Cases of Facade Pattern:

1. **Simplifying Complex External Systems** - Database connections, API calls
2. **Layering Subsystems** - Define clear boundaries between subsystems
3. **Providing Unified Interface** - Combine multiple APIs into single interface
4. **Protecting Clients from Changes** - Stable facade interface shields clients from subsystem changes

## Преимущества И Недостатки

### Pros (Преимущества)


1. **Simplified Interface** - Makes complex systems easy to use
2. **Reduced Coupling** - Clients depend on facade, not subsystems
3. **Encapsulation** - Hides implementation details
4. **Improved Maintainability** - Changes to subsystems don't affect clients
5. **Easier Testing** - Can mock the facade instead of all subsystems

### Cons (Недостатки)


1. **Increased Complexity** - Additional abstraction layer
2. **Reduced Flexibility** - May limit access to advanced features
3. **Overengineering** - Unnecessary for simple systems
4. **Potential Performance Overhead** - Extra indirection layer
5. **God Object Risk** - Facade can become too large

## Best Practices

```kotlin
// - DO: Use facade for complex subsystems
class PaymentFacade(
    private val validator: CardValidator,
    private val processor: PaymentProcessor,
    private val notifier: NotificationService
) {
    suspend fun processPayment(card: CreditCard, amount: Double): Result<String> {
        if (!validator.isValid(card)) return Result.failure(Exception("Invalid card"))
        val txId = processor.process(card, amount)
        notifier.notify("Payment successful: $txId")
        return Result.success(txId)
    }
}

// - DO: Keep facade focused
class NetworkFacade {
    suspend fun get(url: String): String { /* ... */ }
    suspend fun post(url: String, body: String): String { /* ... */ }
}

// - DO: Allow direct subsystem access when needed
class SystemFacade {
    val advancedFeatures: AdvancedSubsystem get() = subsystem
}

// - DON'T: Make facade a god object
// - DON'T: Put business logic in facade
// - DON'T: Use facade for simple systems
```

**English**: **Facade** is a structural pattern that provides a simplified interface to complex subsystems. **Problem**: Complex system is hard to use. **Solution**: Create facade that wraps subsystems and provides simple methods. **Use when**: (1) Complex subsystem needs simple interface, (2) Want to reduce dependencies, (3) Layering system. **Android**: Network + cache + error handling, database operations. **Pros**: simplification, decoupling, easier maintenance. **Cons**: added complexity, reduced flexibility. **Examples**: Home theater system, API facade, database facade.

## Links

- [Facade Design Pattern](https://howtodoinjava.com/design-patterns/structural/facade-design-pattern/)
- [Facade pattern](https://en.wikipedia.org/wiki/Facade_pattern)
- [Facade Design Pattern in Android](https://medium.com/@naimish-trivedi/facade-design-pattern-in-android-3eb959df5478)
- [Facade Design Pattern in Kotlin](https://www.javaguides.net/2023/10/facade-design-pattern-in-kotlin.html)

## Further Reading

- [Facade](https://refactoring.guru/design-patterns/facade)
- [Facade Method Design Pattern](https://www.geeksforgeeks.org/facade-design-pattern-introduction/)

---
*Source: Kirchhoff Android Interview Questions*


## Ответ (RU)

### Определение

Паттерн Facade — это структурный паттерн проектирования, целью которого является **сокрытие внутренней сложности за единым интерфейсом, который выглядит простым снаружи**. Он предоставляет упрощенный интерфейс к сложной подсистеме.

### Проблемы, Которые Решает

Какие проблемы может решить паттерн проектирования Facade?

1. **Чтобы сделать сложную подсистему проще в использовании, должен быть предоставлен простой интерфейс для набора интерфейсов в подсистеме**
2. **Зависимости от подсистемы должны быть минимизированы**

### Ключевые Моменты

Ключевые моменты паттерна Facade:

1. **Упрощение** - предоставляет упрощенный интерфейс к сложной системе классов
2. **Разделение ответственности** - отделяет клиентский код от внутренней работы системы
3. **Облегчение поддержки** - позволяет проще поддерживать код, так как изменения в базовых подсистемах не влияют напрямую на клиентский код

### Объяснение

**Пояснение**:

- **Подсистемы (Subsystems)** (Lights, Blinds, Projector, MoviePlayer) — это сложные отдельные компоненты
- **Фасад (Facade)** (HomeTheaterFacade) предоставляет простые методы (`watchMovie()`, `endMovie()`), которые оркеструют множество подсистем
- **Клиент (Client)** взаимодействует только с фасадом, а не со сложными подсистемами
- В Android фасады упрощают сложные операции, такие как сеть + кэш + обработка ошибок

### Преимущества

1. **Упрощенный интерфейс** - делает сложные системы простыми в использовании
2. **Уменьшение связанности** - клиенты зависят от фасада, а не от подсистем
3. **Инкапсуляция** - скрывает детали реализации
4. **Улучшенная поддерживаемость** - изменения в подсистемах не влияют на клиентов
5. **Облегчение тестирования** - можно мокировать фасад вместо всех подсистем

### Недостатки

1. **Увеличение сложности** - дополнительный уровень абстракции
2. **Уменьшение гибкости** - может ограничить доступ к продвинутым возможностям
3. **Избыточная инженерия** - не нужен для простых систем
4. **Потенциальные накладные расходы производительности** - дополнительный уровень косвенности
5. **Риск God Object** - фасад может стать слишком большим


---

## Related Questions

### Hub
- [[q-design-patterns-types--design-patterns--medium]] - Design pattern categories overview

### Structural Patterns
- [[q-adapter-pattern--design-patterns--medium]] - Adapter pattern
- [[q-decorator-pattern--design-patterns--medium]] - Decorator pattern
- [[q-proxy-pattern--design-patterns--medium]] - Proxy pattern
- [[q-composite-pattern--design-patterns--medium]] - Composite pattern

### Creational Patterns
- [[q-factory-method-pattern--design-patterns--medium]] - Factory Method pattern

### Behavioral Patterns
- [[q-strategy-pattern--design-patterns--medium]] - Strategy pattern

