---id: cs-023
title: "Service Locator Pattern / Паттерн Локатор Служб"
aliases: ["Service Locator", "Локатор Служб"]
topic: cs
subtopics: [dependency-management, design-patterns, service-discovery]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-computer-science, c-dao-pattern, q-abstract-factory-pattern--cs--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [dependency-management, design-patterns, difficulty/medium, service-discovery, service-locator]
sources: ["https://martinfowler.com/articles/injection.html"]

---
# Вопрос (RU)
> Что такое паттерн `Service` Locator? Когда его использовать и как он работает?

# Question (EN)
> What is the `Service` Locator pattern? When to use it and how does it work?

---

## Ответ (RU)

**Теория `Service` Locator Pattern:**
`Service` Locator — это порождающий/структурный паттерн, инкапсулирующий логику получения зависимостей ("сервисов") через центральный реестр (service locator). Клиент запрашивает сервис по ключу/типу, а локатор возвращает зарегистрированный экземпляр. Основные компоненты: `Service` Locator, `Service` Interface, `Service` (реализация), Client. Паттерн решает задачу централизованного доступа к сервисам и выбора реализации во время выполнения, но вводит скрытые зависимости и глобальное состояние.

**Определение:**

*Теория:* `Service` Locator предоставляет абстракцию над доступом к зависимостям: центральный реестр управляет сервисами и предоставляет к ним доступ по запросу клиентов. Клиент запрашивает нужный сервис, локатор возвращает инстанс. Обратная сторона: по сравнению с явной Dependency Injection паттерн проще встроить в небольшой или legacy-код, но сложнее тестировать, ухудшает прозрачность зависимостей и потому в современном дизайне часто рассматривается как анти-паттерн.

```kotlin
// ✅ Basic Service Locator
object ServiceRegistry {
    private val services = mutableMapOf<Class<*>, Any>()

    fun <T : Any> register(serviceClass: Class<T>, service: T) {
        services[serviceClass] = service
    }

    @Suppress("UNCHECKED_CAST")
    fun <T : Any> get(serviceClass: Class<T>): T {
        return services[serviceClass] as? T
            ?: throw IllegalStateException("Service not registered: ${serviceClass.name}")
    }
}

// ✅ Service interfaces
interface AuthService {
    fun login(username: String, password: String): Boolean
}

interface DatabaseService {
    fun saveData(data: String)
}

// Пример реализаций (условно)
class AuthServiceImpl : AuthService {
    override fun login(username: String, password: String): Boolean = true
}

class DatabaseServiceImpl : DatabaseService {
    override fun saveData(data: String) { /* persist */ }
}

// ✅ Initialization
fun initializeServices() {
    ServiceRegistry.register(AuthService::class.java, AuthServiceImpl())
    ServiceRegistry.register(DatabaseService::class.java, DatabaseServiceImpl())
}

// ✅ Client usage
class UserManager {
    // Скрытые зависимости: берутся из глобального реестра
    private val authService = ServiceRegistry.get(AuthService::class.java)
    private val dbService = ServiceRegistry.get(DatabaseService::class.java)

    fun createUser(username: String, password: String) {
        if (authService.login(username, password)) {
            dbService.saveData("User: $username")
        }
    }
}
```

**Проблемы, которые решает:**

**1. Runtime `Service` Selection:**
*Теория:* Позволяет выбирать конкретные реализации сервисов во время выполнения (по типу, имени, конфигурации), не меняя код клиентов. Это упрощает подмену реализаций (например, mock vs real, разные стратегии) без перекомпиляции клиентского кода, при условии, что сами реализации доступны приложению.

**2. Avoiding DI Complexity:**
*Теория:* Для простых приложений с ограниченным набором сервисов ручной `Service` Locator может быть проще, чем внедрение полноценного DI-фреймворка. Не требует сложной конфигурации контейнера, но при этом все ещё предоставляет единый механизм получения зависимостей.

**3. Legacy Code Support:**
*Теория:* Полезен для legacy-кода, где сложно внедрить конструкторное/интерфейсное внедрение зависимостей. Локатор можно интегрировать минимальными изменениями, централизовав создание и выдачу сервисов.

```kotlin
// ✅ Service Locator в legacy code
class LegacyActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // ✅ Registry provides services
        val authService = ServiceRegistry.get(AuthService::class.java)
        val database = ServiceRegistry.get(DatabaseService::class.java)

        // Legacy code continues using services
    }
}
```

**Преимущества:**

1. **Централизованный доступ** — единая точка регистрации и получения сервисов.
2. **Гибкость выбора реализаций во время выполнения** — можно подменять реализации без изменения клиентского кода.
3. **Инкапсуляция создания сервисов** — скрывает детали создания и жизненного цикла за локатором.
4. **Упрощённая интеграция с legacy** — позволяет постепенно выносить создание зависимостей из разбросанного кода.

**Недостатки:**

1. **Скрытые зависимости** — класс использует `Service` Locator внутри, зависимости не видны в API (конструкторах/интерфейсах).
2. **Глобальное состояние** — локатор часто реализуется как синглтон с изменяемым состоянием, что усложняет понимание и сопровождение.
3. **Сложность тестирования** — требуется настраивать глобальный реестр или мокать его; легко получить неочевидное взаимодействие тестов.
4. **Ошибки только во время выполнения** — отсутствие регистрации или конфликтные регистрации обнаруживаются в рантайме.
5. **Жёсткая связность с локатором** — клиенты зависят от конкретного механизма поиска сервисов.

**`Service` Locator vs Dependency Injection:**

*Теория:* Ключевые различия: явность зависимостей, точка контроля и типы ошибок.
- В `Service` Locator зависимости скрыты внутри реализации: класс сам "тянет" их из локатора.
- В Dependency Injection зависимости явны: передаются через конструктор/поля/методы, обычно настраиваются в одном месте.
- SL чаще приводит к рантайм-ошибкам (нет регистрации), сложнее для модульного тестирования.
- DI облегчает тестирование (можно передать моки) и позволяет ловить часть ошибок конфигурации раньше (на уровне компиляции или старта приложения, особенно с compile-time DI).

| Aspect | `Service` Locator | Dependency Injection |
|--------|-----------------|---------------------|
| Dependencies | Hidden (pulled from locator) | Explicit (pushed/injected) |
| Testing | Harder (глобальное состояние, требуется настройка локатора) | Easier (моки/стабы передаются явно) |
| Errors | В основном runtime (нет/неверная регистрация) | Могут выявляться раньше (compile-time или на старте, в зависимости от фреймворка), но тоже возможны runtime |
| Complexity | Простая реализация для небольших проектов | Выше порог входа, особенно с DI-фреймворками |
| Modern practice | Часто рассматривается как анти-паттерн | Де-факто стандарт для масштабируемых систем |

**Когда использовать:**

✅ **Использовать `Service` Locator можно, если:**
- Приложение небольшое, набор сервисов невелик и стабилен.
- Нужна ограниченная гибкость выбора реализаций во время выполнения без внедрения DI-фреймворка.
- Требуется быстро централизовать создание зависимостей в legacy-коде.
- Команда осознаёт минусы скрытых зависимостей и глобального состояния.

❌ **Не использовать (или избегать), если:**
- Система крупная и развивающаяся (предпочтительнее DI).
- Тестируемость и прозрачность зависимостей — приоритет.
- Нужна как можно более строгая проверка зависимостей (compile-time / детерминированная конфигурация).
- Следуете современным практикам чистой архитектуры.
- Проект создаётся с нуля, и нет ограничений, мешающих использовать DI.

**Android `Context`:**

*Теория:* В Android Google и сообщество рекомендуют DI (Dagger/Hilt/Koin и т.п.) вместо `Service` Locator. Причины: лучшая тестируемость, явные зависимости во `ViewModel`/`Activity`/`Fragment`, compile-time-поддержка (в случае Dagger/Hilt), предсказуемость жизненного цикла. `Service` Locator во многих Android-кодовых базах рассматривается как анти-паттерн из-за скрытых зависимостей и глобального состояния.

```kotlin
// ❌ Service Locator (Android anti-pattern)
class MyViewModel {
    private val repository = ServiceRegistry.get(Repository::class.java)
    // Hidden dependency, hard to test
}

// ✅ Dependency Injection (Recommended)
class MyViewModel @Inject constructor(
    private val repository: Repository
) {
    // Explicit dependencies, easy to test
}
```

## Answer (EN)

**`Service` Locator Pattern Theory:**
The `Service` Locator is a creational/structural pattern that encapsulates how application components obtain their dependencies ("services") via a central registry (the service locator). Clients request services by key/type, and the locator returns registered instances. Core components: `Service` Locator, `Service` Interface, `Service` implementation, Client. It provides centralized access and runtime selection of implementations, but introduces hidden dependencies and global state.

**Definition:**

*Theory:* `Service` Locator provides an abstraction over service access: a central registry manages services and provides them to clients on request. The client asks for what it needs; the locator returns an instance. Trade-off: it can be simpler than introducing a full DI framework for small or legacy systems, but it makes dependencies implicit, complicates testing, and is therefore often considered an anti-pattern in modern design.

```kotlin
// ✅ Basic Service Locator
object ServiceRegistry {
    private val services = mutableMapOf<Class<*>, Any>()

    fun <T : Any> register(serviceClass: Class<T>, service: T) {
        services[serviceClass] = service
    }

    @Suppress("UNCHECKED_CAST")
    fun <T : Any> get(serviceClass: Class<T>): T {
        return services[serviceClass] as? T
            ?: throw IllegalStateException("Service not registered: ${serviceClass.name}")
    }
}

// ✅ Service interfaces
interface AuthService {
    fun login(username: String, password: String): Boolean
}

interface DatabaseService {
    fun saveData(data: String)
}

// Example implementations (simplified)
class AuthServiceImpl : AuthService {
    override fun login(username: String, password: String): Boolean = true
}

class DatabaseServiceImpl : DatabaseService {
    override fun saveData(data: String) { /* persist */ }
}

// ✅ Initialization
fun initializeServices() {
    ServiceRegistry.register(AuthService::class.java, AuthServiceImpl())
    ServiceRegistry.register(DatabaseService::class.java, DatabaseServiceImpl())
}

// ✅ Client usage
class UserManager {
    // Hidden dependencies: pulled from global registry
    private val authService = ServiceRegistry.get(AuthService::class.java)
    private val dbService = ServiceRegistry.get(DatabaseService::class.java)

    fun createUser(username: String, password: String) {
        if (authService.login(username, password)) {
            dbService.saveData("User: $username")
        }
    }
}
```

**Problems Solved:**

**1. Runtime `Service` Selection:**
*Theory:* Allows choosing specific service implementations at runtime (by type/name/configuration) without changing client code. This makes it easier to swap implementations (e.g., mock vs real, different strategies), as long as those implementations are available to the application.

**2. Avoiding DI Complexity:**
*Theory:* For small applications with a limited, stable set of services, a hand-rolled `Service` Locator can be simpler than adopting a full DI framework. It avoids complex container configuration while still centralizing how services are obtained.

**3. Legacy Code Support:**
*Theory:* Useful in legacy codebases where introducing constructor-based or interface-based DI is difficult. A locator can be integrated with minimal code changes, centralizing service creation and lookup.

```kotlin
// ✅ Service Locator in legacy code
class LegacyActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // ✅ Registry provides services
        val authService = ServiceRegistry.get(AuthService::class.java)
        val database = ServiceRegistry.get(DatabaseService::class.java)

        // Legacy code continues using services
    }
}
```

**Advantages:**

1. **Centralized access** - single place to register and retrieve services.
2. **Runtime implementation flexibility** - implementations can be swapped without changing client code.
3. **Encapsulation of creation** - hides construction and lifecycle details behind the locator.
4. **Legacy integration** - makes it easier to gradually centralize dependency creation.

**Disadvantages:**

1. **Hidden dependencies** - classes pull dependencies from the locator; not visible in constructors/APIs.
2. **Global state** - often implemented as a mutable singleton, which complicates reasoning about behavior.
3. **Testing difficulties** - tests must configure/override global registry; can lead to brittle tests.
4. **Runtime errors** - missing or misconfigured registrations are discovered only at runtime.
5. **Tight coupling to locator** - clients depend directly on the locator mechanism.

**`Service` Locator vs Dependency Injection:**

*Theory:* Key differences concern dependency visibility, control, and error detection.
- With a `Service` Locator, dependencies are pulled implicitly; configuration errors tend to show up at runtime.
- With Dependency Injection, dependencies are explicit and supplied from the outside; this improves readability and testability.
- DI (especially compile-time checked frameworks) can surface some configuration errors earlier (compile time or application startup), while SL typically cannot.

| Aspect | `Service` Locator | Dependency Injection |
|--------|-----------------|---------------------|
| Dependencies | Hidden (pulled from locator) | Explicit (pushed/injected) |
| Testing | Harder (global state, special setup) | Easier (mocks/stubs passed explicitly) |
| Errors | Mostly runtime (missing/wrong registration) | Often caught earlier (compile/startup with frameworks), though runtime issues still possible |
| Complexity | Simple to implement for small apps | Higher setup/learning cost, esp. with frameworks |
| Modern practice | Often treated as an anti-pattern | Industry standard for scalable systems |

**When to Use:**

✅ **Use `Service` Locator when:**
- The application is small with a limited, stable set of services.
- You need modest runtime flexibility in implementation choice without adopting a DI framework.
- You are working with legacy code where introducing full DI is not yet feasible.
- The team is aware of the trade-offs (hidden dependencies, global state).

❌ **Avoid `Service` Locator when:**
- Building large, complex, or long-lived applications (prefer DI).
- Testability, maintainability, and explicit design are priorities.
- You want strong guarantees about dependency wiring (compile-time/startup validation).
- Following modern best practices such as Clean Architecture.
- Starting a new project without constraints against DI.

**Android `Context`:**

*Theory:* In Android development, Google and the community recommend Dependency Injection (e.g., Dagger/Hilt/Koin) over a `Service` Locator. Reasons: better testability, explicit dependencies in ViewModels/Activities/Fragments, compile-time support in some frameworks, and more predictable lifecycles. `Service` Locator is widely viewed as an anti-pattern in Android codebases because of hidden dependencies and reliance on global mutable state.

```kotlin
// ❌ Service Locator (Android anti-pattern)
class MyViewModel {
    private val repository = ServiceRegistry.get(Repository::class.java)
    // Hidden dependency, hard to test
}

// ✅ Dependency Injection (Recommended)
class MyViewModel @Inject constructor(
    private val repository: Repository
) {
    // Explicit dependencies, easy to test
}
```

---

## Продолжение / Дополнительные Вопросы (RU)

- В чем разница между `Service` Locator и Dependency Injection?
- Почему `Service` Locator считается анти-паттерном в современной Android-разработке?
- Как рефакторить код с `Service` Locator на Dependency Injection?

## Follow-ups

- What is the difference between `Service` Locator and Dependency Injection?
- Why is `Service` Locator considered an anti-pattern in modern Android development?
- How to refactor from `Service` Locator to Dependency Injection?

## Связанные Вопросы (RU)

### Предпосылки (проще)
- Базовые концепции шаблонов проектирования
- Понимание управления зависимостями

### Связанные (тот Же уровень)
- [[q-abstract-factory-pattern--cs--medium]] — Паттерн Abstract Factory

### Продвинутые (сложнее)
- Продвинутые подходы к DI
- Сравнение DI-фреймворков
- Паттерны рефакторинга зависимостей

## Related Questions

### Prerequisites (Easier)
- Basic design patterns concepts
- Understanding of dependency management

### Related (Same Level)
- [[q-abstract-factory-pattern--cs--medium]] - Abstract Factory pattern

### Advanced (Harder)
- Advanced DI patterns
- DI frameworks comparison
- Refactoring patterns

## References

- [[c-computer-science]]
- "Inversion of Control Containers and the Dependency Injection pattern" — Martin Fowler (https://martinfowler.com/articles/injection.html)
