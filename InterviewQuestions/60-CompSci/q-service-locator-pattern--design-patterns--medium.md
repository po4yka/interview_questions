---
id: 20251012-1227111177
title: Service Locator Pattern
topic: design-patterns
difficulty: medium
status: draft
created: 2025-10-15
tags: []
related:   - dependency-injection
  - singleton-pattern
  - factory-pattern
subtopics:   - structural-patterns
  - dependency-management
  - service-discovery
---
# Service Locator Pattern / Паттерн Локатор Служб

# Question (EN)
> What is the Service Locator pattern? When and why should it be used?

# Вопрос (RU)
> Что такое паттерн Service Locator? Когда и зачем его следует использовать?

---

## Answer (EN)


### Definition
The **Service Locator pattern** is a design pattern used to encapsulate the processes involved in obtaining a service with a strong abstraction layer. This pattern uses a central registry known as the "service locator", which on request returns the information necessary to perform a certain task. Proponents of the pattern say the approach simplifies component-based applications where all dependencies are cleanly listed at the beginning of the whole application design, consequently making traditional dependency injection a more complex way of connecting objects.

### Key Components
- **Service Locator**: Central registry that manages and provides access to services
- **Service**: The actual functionality or object that needs to be accessed
- **Client**: The code that requests services from the Service Locator
- **Service Interface**: Defines the contract that services must implement

### How It Works
1. Services are registered with the Service Locator during application initialization
2. When a client needs a service, it requests it from the Service Locator
3. The Service Locator returns the requested service instance
4. The client uses the service to perform operations

### Example in Kotlin

```kotlin
// Services
class Service1 {
    fun action() {
        println("Action from Service 1")
    }
}

class Service2 {
    fun action() {
        println("Action from Service 2")
    }
}

// Service Locator Interface
interface ServiceLocator {
    val service1: Service1
    val service2: Service2
}

// Service Locator Implementation
class ServiceLocatorImpl : ServiceLocator {
    override val service1: Service1 by lazy { Service1() }
    override val service2: Service2 by lazy { Service2() }
}

// Client class that uses services
class ServiceComposition(serviceLocator: ServiceLocator) {
    private val service1 = serviceLocator.service1
    private val service2 = serviceLocator.service2

    fun serviceInteraction() {
        service1.action()
        service2.action()
    }
}

// Example usage
class ServiceLocatorExample {
    fun example() {
        val serviceLocator: ServiceLocator = ServiceLocatorImpl()
        val serviceComposition = ServiceComposition(serviceLocator)

        serviceComposition.serviceInteraction()
    }
}
```

**Output:**
```
Action from Service 1
Action from Service 2
```

### More Complex Example

```kotlin
// Generic Service Locator
object ServiceRegistry {
    private val services = mutableMapOf<Class<*>, Any>()

    fun <T : Any> register(serviceClass: Class<T>, service: T) {
        services[serviceClass] = service
    }

    @Suppress("UNCHECKED_CAST")
    fun <T : Any> get(serviceClass: Class<T>): T {
        return services[serviceClass] as? T
            ?: throw IllegalStateException("Service ${serviceClass.simpleName} not registered")
    }
}

// Service interfaces
interface AuthService {
    fun login(username: String, password: String): Boolean
}

interface DatabaseService {
    fun saveData(data: String)
}

// Service implementations
class AuthServiceImpl : AuthService {
    override fun login(username: String, password: String): Boolean {
        println("Authenticating user: $username")
        return true
    }
}

class DatabaseServiceImpl : DatabaseService {
    override fun saveData(data: String) {
        println("Saving data: $data")
    }
}

// Application initialization
fun initializeServices() {
    ServiceRegistry.register(AuthService::class.java, AuthServiceImpl())
    ServiceRegistry.register(DatabaseService::class.java, DatabaseServiceImpl())
}

// Client usage
class UserManager {
    private val authService = ServiceRegistry.get(AuthService::class.java)
    private val dbService = ServiceRegistry.get(DatabaseService::class.java)

    fun createUser(username: String, password: String) {
        if (authService.login(username, password)) {
            dbService.saveData("User: $username")
        }
    }
}
```

### Advantages
- **Runtime Flexibility**: The service locator can act as a simple run-time linker. This allows code to be added at run-time without re-compiling the application, and in some cases without having to even restart it
- **Optimization**: Applications can optimize themselves at run-time by selectively adding and removing items from the service locator
- **Separation**: Large sections of a library or application can be completely separated. The only link between them becomes the registry
- **Multiple Locators**: An application may use multiple structured service locators purposed for particular functionality/testing. Service locator does not mandate one single static class per process
- **Simplicity**: The solution may be simpler with service locator (vs. dependency injection) in applications with well-structured component/service design

### Disadvantages
- **Hidden Dependencies**: The registry hides the class' dependencies, causing run-time errors instead of compile-time errors when dependencies are missing (similar to using dependency injection)
- **Testing Difficulties**: The registry makes code harder to test, since all tests need to interact with the same global service locator class to set the fake dependencies of a class under test
- **Global State**: Creates a global state that can make the application harder to reason about
- **Runtime Errors**: Missing services are only detected at runtime, not compile time
- **Tight Coupling**: Can create tight coupling to the service locator itself

### Service Locator vs Dependency Injection
| Aspect | Service Locator | Dependency Injection |
|--------|----------------|---------------------|
| Dependencies | Hidden, requested at runtime | Explicit, injected from outside |
| Testing | Harder to test | Easier to test |
| Error Detection | Runtime | Compile-time (with frameworks) |
| Complexity | Simpler for small apps | More complex setup |
| Popularity | Less popular | More popular |

### When to Use
Use the Service Locator pattern when:
- You have a simple application with well-defined services
- You need runtime flexibility in service selection
- You want to avoid the complexity of a full DI framework
- You're working with legacy code that doesn't support DI

### When NOT to Use
Avoid the Service Locator pattern when:
- You're building a large, complex application (prefer DI)
- Testability is a high priority
- You want compile-time dependency verification
- You're following modern Android development best practices (Google recommends DI)

---



## Ответ (RU)

### Определение
**Паттерн Локатор Служб** - это паттерн проектирования, используемый для инкапсуляции процессов, связанных с получением службы с сильным уровнем абстракции. Этот паттерн использует центральный реестр, известный как "локатор служб", который по запросу возвращает информацию, необходимую для выполнения определенной задачи. Сторонники паттерна говорят, что подход упрощает компонентные приложения, где все зависимости четко перечислены в начале всего дизайна приложения, следовательно, делая традиционное внедрение зависимостей более сложным способом соединения объектов.

### Ключевые Компоненты
- **Service Locator (Локатор Служб)**: Центральный реестр, который управляет и предоставляет доступ к службам
- **Service (Служба)**: Фактическая функциональность или объект, к которому нужно получить доступ
- **Client (Клиент)**: Код, который запрашивает службы у Локатора Служб
- **Service Interface (Интерфейс Службы)**: Определяет контракт, который должны реализовывать службы

### Как Это Работает
1. Службы регистрируются в Локаторе Служб во время инициализации приложения
2. Когда клиенту нужна служба, он запрашивает ее у Локатора Служб
3. Локатор Служб возвращает запрошенный экземпляр службы
4. Клиент использует службу для выполнения операций

### Пример на Kotlin

```kotlin
// Службы
class Service1 {
    fun action() {
        println("Action from Service 1")
    }
}

class Service2 {
    fun action() {
        println("Action from Service 2")
    }
}

// Интерфейс Локатора Служб
interface ServiceLocator {
    val service1: Service1
    val service2: Service2
}

// Реализация Локатора Служб
class ServiceLocatorImpl : ServiceLocator {
    override val service1: Service1 by lazy { Service1() }
    override val service2: Service2 by lazy { Service2() }
}

// Класс клиента, использующий службы
class ServiceComposition(serviceLocator: ServiceLocator) {
    private val service1 = serviceLocator.service1
    private val service2 = serviceLocator.service2

    fun serviceInteraction() {
        service1.action()
        service2.action()
    }
}

// Пример использования
class ServiceLocatorExample {
    fun example() {
        val serviceLocator: ServiceLocator = ServiceLocatorImpl()
        val serviceComposition = ServiceComposition(serviceLocator)

        serviceComposition.serviceInteraction()
    }
}
```

**Вывод:**
```
Action from Service 1
Action from Service 2
```

### Более Сложный Пример

```kotlin
// Универсальный Локатор Служб
object ServiceRegistry {
    private val services = mutableMapOf<Class<*>, Any>()

    fun <T : Any> register(serviceClass: Class<T>, service: T) {
        services[serviceClass] = service
    }

    @Suppress("UNCHECKED_CAST")
    fun <T : Any> get(serviceClass: Class<T>): T {
        return services[serviceClass] as? T
            ?: throw IllegalStateException("Service ${serviceClass.simpleName} not registered")
    }
}

// Интерфейсы служб
interface AuthService {
    fun login(username: String, password: String): Boolean
}

interface DatabaseService {
    fun saveData(data: String)
}

// Реализации служб
class AuthServiceImpl : AuthService {
    override fun login(username: String, password: String): Boolean {
        println("Аутентификация пользователя: $username")
        return true
    }
}

class DatabaseServiceImpl : DatabaseService {
    override fun saveData(data: String) {
        println("Сохранение данных: $data")
    }
}

// Инициализация приложения
fun initializeServices() {
    ServiceRegistry.register(AuthService::class.java, AuthServiceImpl())
    ServiceRegistry.register(DatabaseService::class.java, DatabaseServiceImpl())
}

// Использование клиентом
class UserManager {
    private val authService = ServiceRegistry.get(AuthService::class.java)
    private val dbService = ServiceRegistry.get(DatabaseService::class.java)

    fun createUser(username: String, password: String) {
        if (authService.login(username, password)) {
            dbService.saveData("User: $username")
        }
    }
}
```

### Преимущества
- **Гибкость во время выполнения**: Локатор служб может действовать как простой компоновщик времени выполнения. Это позволяет добавлять код во время выполнения без перекомпиляции приложения, а в некоторых случаях даже без его перезапуска
- **Оптимизация**: Приложения могут оптимизировать себя во время выполнения, выборочно добавляя и удаляя элементы из локатора служб
- **Разделение**: Большие разделы библиотеки или приложения могут быть полностью разделены. Единственной связью между ними становится реестр
- **Множественные локаторы**: Приложение может использовать несколько структурированных локаторов служб для конкретной функциональности/тестирования. Локатор служб не требует одного статического класса на процесс
- **Простота**: Решение может быть проще с локатором служб (в сравнении с внедрением зависимостей) в приложениях с хорошо структурированным дизайном компонентов/служб

### Недостатки
- **Скрытые зависимости**: Реестр скрывает зависимости класса, вызывая ошибки времени выполнения вместо ошибок времени компиляции, когда зависимости отсутствуют (аналогично использованию внедрения зависимостей)
- **Трудности тестирования**: Реестр усложняет тестирование кода, поскольку всем тестам необходимо взаимодействовать с одним и тем же глобальным классом локатора служб для установки фиктивных зависимостей тестируемого класса
- **Глобальное состояние**: Создает глобальное состояние, которое может затруднить рассуждение о приложении
- **Ошибки во время выполнения**: Отсутствующие службы обнаруживаются только во время выполнения, а не во время компиляции
- **Тесная связанность**: Может создать тесную связанность с самим локатором служб

### Локатор Служб vs Внедрение Зависимостей
| Аспект | Локатор Служб | Внедрение Зависимостей |
|--------|----------------|------------------------|
| Зависимости | Скрыты, запрашиваются во время выполнения | Явные, внедряются извне |
| Тестирование | Сложнее тестировать | Легче тестировать |
| Обнаружение ошибок | Время выполнения | Время компиляции (с фреймворками) |
| Сложность | Проще для малых приложений | Более сложная настройка |
| Популярность | Менее популярен | Более популярен |

### Когда Использовать
Используйте паттерн Локатор Служб, когда:
- У вас простое приложение с четко определенными службами
- Вам нужна гибкость времени выполнения в выборе служб
- Вы хотите избежать сложности полноценного DI-фреймворка
- Вы работаете с устаревшим кодом, который не поддерживает DI

### Когда НЕ Использовать
Избегайте паттерна Локатор Служб, когда:
- Вы создаете большое, сложное приложение (предпочтите DI)
- Тестируемость является высоким приоритетом
- Вы хотите проверку зависимостей во время компиляции
- Вы следуете современным лучшим практикам разработки Android (Google рекомендует DI)

---

## References
- [Service locator pattern - Wikipedia](https://en.wikipedia.org/wiki/Service_locator_pattern)
- [Service Locator pattern in Android - Medium](https://medium.com/inloopx/service-locator-pattern-in-android-af3830924c69)
- [Inversion of Control Containers and the Dependency Injection pattern - Martin Fowler](https://martinfowler.com/articles/injection.html)
- [Why service locator is so unpopular - ProAndroidDev](https://proandroiddev.com/why-service-locator-is-so-unpopular-bbe8678be72c)

---

**Source:** Kirchhoff-Android-Interview-Questions
**Attribution:** Content adapted from the Kirchhoff repository


---

## Related Questions

### Hub
- [[q-design-patterns-types--design-patterns--medium]] - Design pattern categories overview

