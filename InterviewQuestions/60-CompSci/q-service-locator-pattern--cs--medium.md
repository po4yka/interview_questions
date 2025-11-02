---
id: cs-023
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
related: [q-dependency-injection-pattern--architecture-patterns--hard, q-singleton-pattern--design-patterns--medium]
created: 2025-10-15
updated: 2025-01-25
tags: [dependency-management, design-patterns, difficulty/medium, service-discovery, service-locator]
sources: [https://martinfowler.com/articles/injection.html]
date created: Monday, October 6th 2025, 7:39:28 am
date modified: Saturday, November 1st 2025, 5:43:28 pm
---

# Вопрос (RU)
> Что такое паттерн Service Locator? Когда его использовать и как он работает?

# Question (EN)
> What is the Service Locator pattern? When to use it and how does it work?

---

## Ответ (RU)

**Теория Service Locator Pattern:**
Service Locator - design pattern для encapsulating processes involved в obtaining services. Uses central registry (service locator) returns information necessary для certain tasks. Solves: runtime service selection, avoiding DI complexity, simple service discovery. Components: Service Locator, Service, Client, Service Interface.

**Определение:**

*Теория:* Service Locator - pattern для encapsulating service access с strong abstraction layer. Central registry manages services и provides access. Client requests service, locator returns instance. Trade-off: simpler than DI для small apps, но harder to test и creates hidden dependencies.

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
            ?: throw IllegalStateException("Service not registered")
    }
}

// ✅ Service interfaces
interface AuthService {
    fun login(username: String, password: String): Boolean
}

interface DatabaseService {
    fun saveData(data: String)
}

// ✅ Initialization
fun initializeServices() {
    ServiceRegistry.register(AuthService::class.java, AuthServiceImpl())
    ServiceRegistry.register(DatabaseService::class.java, DatabaseServiceImpl())
}

// ✅ Client usage
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

**Проблемы, которые решает:**

**1. Runtime Service Selection:**
*Теория:* Selecting services at runtime rather than compile-time. Allows adding code at runtime without recompiling, enables optimization through selective adding/removing. Applications can optimize themselves.

**2. Avoiding DI Complexity:**
*Theory:* For simple apps с well-defined services, Service Locator simpler than full DI framework. Avoids complexity of constructor/setter injection, factories, containers. Works well для component/service designs.

**3. Legacy Code Support:**
*Theory:* Service Locator useful для legacy code that doesn't support DI. Can integrate with existing code without major refactoring. Provides centralized service access без changing entire architecture.

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

1. **Runtime Flexibility** - add code at runtime without recompiling
2. **Optimization** - selectively add/remove items
3. **Separation** - large sections completely separated
4. **Multiple Locators** - different locators для different purposes
5. **Simplicity** - simpler than DI для structured designs

**Недостатки:**

1. **Hidden Dependencies** - runtime errors вместо compile-time
2. **Testing Difficulties** - global state makes testing harder
3. **Global State** - creates global state, harder to reason
4. **Runtime Errors** - missing services detected only at runtime
5. **Tight Coupling** - coupling to service locator itself

**Service Locator vs Dependency Injection:**

*Теория:* Key differences: dependencies visibility, error detection, testing complexity. Service Locator hides dependencies (runtime errors), Dependency Injection makes explicit (compile-time errors). Service Locator harder to test, DI easier to test.

| Aspect | Service Locator | Dependency Injection |
|--------|-----------------|---------------------|
| Dependencies | Hidden, runtime | Explicit, injected |
| Testing | Harder | Easier |
| Errors | Runtime | Compile-time (frameworks) |
| Complexity | Simple для small apps | Complex setup |
| Popularity | Less | More (industry standard) |

**Когда использовать:**

✅ **Use Service Locator when:**
- Simple application с well-defined services
- Need runtime flexibility в service selection
- Want avoid DI framework complexity
- Working с legacy code без DI support
- Need quick service discovery

❌ **Don't use Service Locator when:**
- Large, complex application (prefer DI)
- Testability is high priority
- Want compile-time dependency verification
- Following modern best practices (Google recommends DI)
- Building new application from scratch

**Android Context:**

*Теория:* In Android, Google recommends DI (Dagger/Hilt) over Service Locator. Reasons: testability (DI makes testing easier), compile-time safety, explicit dependencies, better for large apps. Service Locator considered anti-pattern by many Android developers due to hidden dependencies и global state.

```kotlin
// ❌ Service Locator (Android anti-pattern)
class MyViewModel {
    private val repository = ServiceLocator.get(Repository::class.java)
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

**Service Locator Pattern Theory:**
Service Locator - design pattern for encapsulating processes involved in obtaining services. Uses central registry (service locator) that returns information necessary for certain tasks. Solves: runtime service selection, avoiding DI complexity, simple service discovery. Components: Service Locator, Service, Client, Service Interface.

**Definition:**

*Theory:* Service Locator - pattern for encapsulating service access with strong abstraction layer. Central registry manages services and provides access. Client requests service, locator returns instance. Trade-off: simpler than DI for small apps, but harder to test and creates hidden dependencies.

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
            ?: throw IllegalStateException("Service not registered")
    }
}

// ✅ Service interfaces
interface AuthService {
    fun login(username: String, password: String): Boolean
}

interface DatabaseService {
    fun saveData(data: String)
}

// ✅ Initialization
fun initializeServices() {
    ServiceRegistry.register(AuthService::class.java, AuthServiceImpl())
    ServiceRegistry.register(DatabaseService::class.java, DatabaseServiceImpl())
}

// ✅ Client usage
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

**Problems Solved:**

**1. Runtime Service Selection:**
*Theory:* Selecting services at runtime rather than compile-time. Allows adding code at runtime without recompiling, enables optimization through selective adding/removing. Applications can optimize themselves.

**2. Avoiding DI Complexity:**
*Theory:* For simple apps with well-defined services, Service Locator simpler than full DI framework. Avoids complexity of constructor/setter injection, factories, containers. Works well for component/service designs.

**3. Legacy Code Support:**
*Theory:* Service Locator useful for legacy code that doesn't support DI. Can integrate with existing code without major refactoring. Provides centralized service access without changing entire architecture.

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

1. **Runtime Flexibility** - add code at runtime without recompiling
2. **Optimization** - selectively add/remove items
3. **Separation** - large sections completely separated
4. **Multiple Locators** - different locators for different purposes
5. **Simplicity** - simpler than DI for structured designs

**Disadvantages:**

1. **Hidden Dependencies** - runtime errors instead of compile-time
2. **Testing Difficulties** - global state makes testing harder
3. **Global State** - creates global state, harder to reason
4. **Runtime Errors** - missing services detected only at runtime
5. **Tight Coupling** - coupling to service locator itself

**Service Locator vs Dependency Injection:**

*Theory:* Key differences: dependencies visibility, error detection, testing complexity. Service Locator hides dependencies (runtime errors), Dependency Injection makes explicit (compile-time errors). Service Locator harder to test, DI easier to test.

| Aspect | Service Locator | Dependency Injection |
|--------|-----------------|---------------------|
| Dependencies | Hidden, runtime | Explicit, injected |
| Testing | Harder | Easier |
| Errors | Runtime | Compile-time (frameworks) |
| Complexity | Simple for small apps | Complex setup |
| Popularity | Less | More (industry standard) |

**When to Use:**

✅ **Use Service Locator when:**
- Simple application with well-defined services
- Need runtime flexibility in service selection
- Want to avoid DI framework complexity
- Working with legacy code without DI support
- Need quick service discovery

❌ **Don't use Service Locator when:**
- Large, complex application (prefer DI)
- Testability is high priority
- Want compile-time dependency verification
- Following modern best practices (Google recommends DI)
- Building new application from scratch

**Android Context:**

*Theory:* In Android, Google recommends DI (Dagger/Hilt) over Service Locator. Reasons: testability (DI makes testing easier), compile-time safety, explicit dependencies, better for large apps. Service Locator considered anti-pattern by many Android developers due to hidden dependencies and global state.

```kotlin
// ❌ Service Locator (Android anti-pattern)
class MyViewModel {
    private val repository = ServiceLocator.get(Repository::class.java)
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

## Follow-ups

- What is the difference between Service Locator and Dependency Injection?
- Why is Service Locator considered an anti-pattern in modern Android development?
- How to refactor from Service Locator to Dependency Injection?

## Related Questions

### Prerequisites (Easier)
- Basic design patterns concepts
- Understanding of dependency management

### Related (Same Level)
- [[q-dependency-injection-pattern--architecture-patterns--hard]] - Dependency Injection
- [[q-singleton-pattern--design-patterns--medium]] - Singleton pattern
- [[q-factory-method-pattern--design-patterns--medium]] - Factory Method pattern

### Advanced (Harder)
- Advanced DI patterns
- DI frameworks comparison
- Refactoring patterns
