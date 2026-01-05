---
id: dp-009
title: "Facade Pattern / Паттерн фасад"
aliases: [Facade Pattern, Паттерн фасад]
topic: cs
subtopics: [abstraction, design-patterns, structural-patterns]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-architecture-patterns, c-computer-science, q-adapter-pattern--cs--medium]
created: 2023-10-15
updated: 2025-11-11
tags: [cs, difficulty/medium, facade, gof-patterns, structural-patterns]
---
# Вопрос (RU)
> Что такое паттерн Facade? Когда и зачем его использовать?

# Question (EN)
> What is the Facade pattern? When and why should it be used?

## Ответ (RU)

**Facade (Фасад)** — это структурный паттерн проектирования, который предоставляет простой интерфейс к сложной системе классов, библиотеке или фреймворку. Фасад скрывает сложность системы и предоставляет клиенту простой способ взаимодействия.

### Определение

Паттерн Facade — это структурный паттерн проектирования, целью которого является **сокрытие внутренней сложности за единым интерфейсом, который выглядит простым снаружи**. Он предоставляет упрощенный интерфейс к сложной подсистеме или набору подсистем.

### Проблемы, Которые Решает

Какие проблемы может решить паттерн проектирования Facade?

1. **Сделать сложную подсистему проще в использовании** — предоставить единый простой интерфейс к набору интерфейсов в подсистеме.
2. **Минимизировать зависимости от подсистемы** — клиентский код зависит от фасада, а не от деталей реализации.

### Ключевые Моменты

Ключевые моменты паттерна Facade:

1. **Упрощение** — предоставляет упрощенный интерфейс к сложной системе классов.
2. **Ослабление связности** — отделяет клиентский код от внутренней реализации подсистем.
3. **Облегчение поддержки** — изменения в подсистемах не требуют изменений клиентского кода при сохранении контракта фасада.

### Пример: Домашний Кинотеатр (Home Theater)

```kotlin
// Подсистемы
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

// Фасад
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

Вывод:
```text
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

### Пример: Android — Фасад Над Retrofit И Кэшем

```kotlin
// Сложные подсистемы
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

// Фасад — простой API-интерфейс
class ApiFacade(private val context: Context) {
    private val networkClient = NetworkClient()
    private val cacheManager = CacheManager(context)
    private val errorHandler = ErrorHandler()

    suspend fun getUserData(userId: String): Result<User> {
        return try {
            // Сначала кэш
            val cached = cacheManager.getFromCache("user_$userId")
            if (cached != null) {
                return Result.success(Gson().fromJson(cached, User::class.java))
            }

            // Потом сеть
            val api = networkClient.createService(ApiService::class.java)
            val user = api.getUser(userId)

            // Сохранить в кэш
            cacheManager.saveToCache("user_$userId", Gson().toJson(user))

            Result.success(user)
        } catch (e: Exception) {
            // Упрощённая обработка ошибок
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
            // Упрощённая обработка ошибок
            Result.failure(Exception(errorHandler.handleError(e)))
        }
    }
}

// Клиентский код — простой в использовании
class UserRepository(context: Context) {
    private val apiFacade = ApiFacade(context)

    suspend fun getUser(id: String) = apiFacade.getUserData(id)
    suspend fun updateUser(user: User) = apiFacade.updateUser(user)
}
```

### Пример: Kotlin — Фасад Над Базой Данных

```kotlin
// Сложные подсистемы
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
        // Сложная логика обработки (упрощено для примера)
        @Suppress("UNCHECKED_CAST")
        return rawData.map { it as T }
    }
}

// Фасад
class DatabaseFacade {
    private val connection = DatabaseConnection()
    private val queryBuilder = QueryBuilder()
    private val processor = ResultProcessor()

    fun <T> queryData(table: String, where: String, type: Class<T>): List<T> {
        connection.connect()
        val query = queryBuilder.buildSelectQuery(table, where)
        println("Executing: $query")
        val rawData = listOf<Any>() // Эмуляция результата БД
        val result = processor.processResult(rawData, type)
        connection.disconnect()
        return result
    }
}

// Пример использования
fun main() {
    val db = DatabaseFacade()
    val users = db.queryData("users", "age > 18", User::class.java)
}
```

### Пояснение

- **Подсистемы** (Lights, Blinds, Projector, MoviePlayer и др.) — отдельные компоненты.
- **Фасад** (например, `HomeTheaterFacade`, `ApiFacade`, `DatabaseFacade`) предоставляет простые методы, которые оркеструют работу нескольких подсистем.
- **Клиент** взаимодействует только с фасадом, а не напрямую с каждой подсистемой.
- В Android фасады часто упрощают комбинацию сетевых запросов, кэширования и обработки ошибок.

### Применение

Use Cases паттерна Facade:

1. **Упрощение сложных внешних систем** — работа с БД, API, legacy-системами.
2. **Слоение подсистем** — формирование чётких границ между слоями (UI, domain, data).
3. **Единый унифицированный интерфейс** — объединение нескольких API/подсистем в один вход.
4. **Защита клиентов от изменений** — стабильный фасад экранирует изменения внутренних подсистем.

### Преимущества

1. **Упрощенный интерфейс** — делает сложные системы проще в использовании.
2. **Уменьшение связанности** — клиенты зависят от фасада, а не от конкретных подсистем.
3. **Инкапсуляция** — скрывает детали реализации.
4. **Улучшенная поддерживаемость** — изменения в подсистемах не влияют напрямую на клиентов.
5. **Облегчение тестирования** — можно мокировать фасад вместо всех подсистем.

### Недостатки

1. **Увеличение сложности** — дополнительный уровень абстракции.
2. **Снижение гибкости** — может ограничить доступ к продвинутым возможностям подсистем.
3. **Избыточная инженерия** — не нужен для простых систем.
4. **Потенциальные накладные расходы** — дополнительный уровень косвенности.
5. **Риск God Object** — фасад может «раздуться» и взять на себя слишком много ответственности.

### Рекомендации По Использованию (Best Practices)

```kotlin
// DO: Используйте фасад для сложных подсистем
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

// DO: Держите фасад сфокусированным
class NetworkFacade {
    suspend fun get(url: String): String { /* simplified example */ TODO("Implement HTTP GET") }
    suspend fun post(url: String, body: String): String { /* simplified example */ TODO("Implement HTTP POST") }
}

// DO: При необходимости разрешайте прямой доступ к подсистемам
class SystemFacade(private val subsystem: AdvancedSubsystem) {
    val advancedFeatures: AdvancedSubsystem get() = subsystem
}

// DON'T: Не превращайте фасад в god object
// DON'T: Не кладите сложную бизнес-логику во фасад
// DON'T: Не используйте фасад для чрезмерно простых систем
```

### Краткое Резюме (RU)

Паттерн **Facade** предоставляет упрощенный интерфейс к сложным подсистемам. Применяется, когда нужно упростить использование сложной системы, уменьшить количество зависимостей и выделить стабильный слой между клиентом и подсистемами. Частые примеры: фасад для домашнего кинотеатра, API-фасад (сеть + кэш + ошибки), фасад над базой данных.

## Answer (EN)

Facade is a structural design pattern that provides a simple interface to a complex system of classes, libraries, or frameworks. It hides complexity and exposes an easy-to-use API to clients.

### Definition

Facade pattern is a structural design pattern whose purpose is to **hide internal complexity behind a single interface that appears simple from the outside**. It provides a simplified interface to a complex subsystem.

### Problems it Solves

1. **Make a complex subsystem easier to use** — provide a single simple interface to a set of interfaces in the subsystem.
2. **Minimize dependencies on the subsystem** — client code depends on the facade instead of concrete implementation details.

### Key Points

1. **Simplification** — provides a simplified interface to a complex system of classes.
2. **Decoupling** — decouples client code from internal subsystem details.
3. **Easier Maintenance** — changes in subsystems do not require changes in client code as long as the facade contract is preserved.

### Example: Home Theater

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

Output:
```text
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

### Android Example: Retrofit Facade

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
            // Simplified error handling for example purposes.
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
            // Simplified error handling for example purposes.
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

### Kotlin Example: Database Facade

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
        // Complex processing logic (simplified for example)
        @Suppress("UNCHECKED_CAST")
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

// Simple usage (example only)
fun main() {
    val db = DatabaseFacade()
    val users = db.queryData("users", "age > 18", User::class.java)
}
```

### Explanation

- **Subsystems** (Lights, Blinds, Projector, MoviePlayer, etc.) are individual components.
- **Facade** (e.g., `HomeTheaterFacade`, `ApiFacade`, `DatabaseFacade`) provides simple methods that orchestrate multiple subsystems.
- **Client** interacts only with the facade, not with each subsystem directly.
- In Android, facades often simplify combinations of network calls, caching, and error handling.

### Use Cases of Facade Pattern

1. **Simplifying Complex External Systems** — database connections, API calls, legacy systems.
2. **Layering Subsystems** — defining clear boundaries between layers (UI, domain, data).
3. **Providing Unified Interface** — combining multiple APIs/subsystems into a single entry point.
4. **Protecting Clients from Changes** — stable facade interface shields clients from subsystem changes.

### Pros

1. **Simplified Interface** — makes complex systems easier to use.
2. **Reduced Coupling** — clients depend on the facade instead of subsystems.
3. **Encapsulation** — hides implementation details.
4. **Improved Maintainability** — subsystem changes do not directly affect clients.
5. **Easier Testing** — you can mock the facade instead of all subsystems.

### Cons

1. **Increased Complexity** — adds an extra abstraction layer.
2. **Reduced Flexibility** — may limit access to advanced subsystem features.
3. **Overengineering Risk** — unnecessary for simple systems.
4. **Potential Performance Overhead** — extra indirection.
5. **God Object Risk** — facade may grow too large.

### Best Practices

```kotlin
// DO: Use facade for complex subsystems
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

// DO: Keep facade focused
class NetworkFacade {
    suspend fun get(url: String): String { /* simplified example */ TODO("Implement HTTP GET") }
    suspend fun post(url: String, body: String): String { /* simplified example */ TODO("Implement HTTP POST") }
}

// DO: Allow direct subsystem access when needed
class SystemFacade(private val subsystem: AdvancedSubsystem) {
    val advancedFeatures: AdvancedSubsystem get() = subsystem
}

// DON'T: Make facade a god object
// DON'T: Put complex business logic in facade
// DON'T: Use facade for simple systems
```

### Summary (EN)

Facade is a structural pattern that provides a simplified interface to complex subsystems.
Use it when:
- a complex subsystem needs a simple entry point,
- you want to reduce coupling between clients and implementation details,
- you introduce a stable layer between modules.

Common examples: home theater system, API facade (network + cache + error handling), database facade.

## Дополнительные Вопросы (RU)

- Чем паттерн Facade отличается от паттернов Adapter и Proxy?
- Когда использование Facade может стать вредным (например, god object, чрезмерное сокрытие деталей)?
- Как бы вы применили Facade в слоистой архитектуре реального проекта?

## Follow-ups

- How does Facade differ from Adapter and Proxy patterns?
- When can using a Facade become harmful (e.g., god object, hiding too much)?
- How would you apply Facade in a layered architecture for a real project?

## Ссылки (RU)

- [[c-architecture-patterns]]
- [[c-computer-science]]
- [[q-adapter-pattern--cs--medium]]

## Related Questions

- [[q-adapter-pattern--cs--medium]]

## References

- [Facade Design Pattern](https://howtodoinjava.com/design-patterns/structural/facade-design-pattern/)
- [Facade pattern](https://en.wikipedia.org/wiki/Facade_pattern)
- [Facade](https://refactoring.guru/design-patterns/facade)
- [Facade Method Design Pattern](https://www.geeksforgeeks.org/facade-design-pattern-introduction/)
- [Facade Design Pattern in Android](https://medium.com/@naimish-trivedi/facade-design-pattern-in-android-3eb959df5478)
- [Facade Design Pattern in Kotlin](https://www.javaguides.net/2023/10/facade-design-pattern-in-kotlin.html)

---
*Source: Kirchhoff Android Interview Questions*