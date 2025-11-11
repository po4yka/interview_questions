---
id: cs-060
title: "Singleton Pattern / Singleton Паттерн"
aliases: [Singleton Pattern, Singleton Паттерн]
topic: cs
subtopics: [design-patterns, creational-patterns, singleton]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-architecture-patterns, q-abstract-factory-pattern--cs--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [design-patterns, creational-patterns, difficulty/easy, singleton]

---

# Вопрос (RU)
> Что такое паттерн Singleton? Когда и зачем его использовать?

# Question (EN)
> What is the Singleton pattern? When and why should it be used?

---

## Ответ (RU)

### Определение

Паттерн Singleton — это порождающий паттерн проектирования, который **ограничивает создание экземпляров класса одним единственным экземпляром (или строго контролируемым числом экземпляров)** и предоставляет глобальную точку доступа к этому экземпляру.

### Проблемы, Которые Решает

Паттерн проектирования Singleton решает такие проблемы как:

1. **Как гарантировать, что класс имеет только один экземпляр?**
2. **Как обеспечить легкий доступ к единственному экземпляру класса?**
3. **Как класс может контролировать своё создание?**
4. **Как ограничить количество экземпляров класса?**

### Решение

Для создания Singleton-класса, как правило, используются:

- **Статический член**: Один раз инициализируется на уровне класса и хранит экземпляр Singleton.
- **Приватный конструктор**: Предотвращает создание экземпляров Singleton извне.
- **Статический фабричный метод**: Предоставляет глобальную точку доступа к объекту Singleton и возвращает экземпляр вызывающему коду.

### Пример: Классический (Не Потокобезопасный) Singleton

```java
public final class ClassSingleton {

    private static ClassSingleton INSTANCE;
    private String info = "Initial info class";

    private ClassSingleton() {
    }

    // Не потокобезопасен: в многопоточной среде возможно создание нескольких экземпляров
    public static ClassSingleton getInstance() {
        if (INSTANCE == null) {
            INSTANCE = new ClassSingleton();
        }
        return INSTANCE;
    }

    // getters and setters
}
```

### Пример: Потокобезопасный Singleton (`Double`-Checked Locking)

```java
public final class ThreadSafeSingleton {

    private static volatile ThreadSafeSingleton INSTANCE;

    private ThreadSafeSingleton() {
    }

    public static ThreadSafeSingleton getInstance() {
        if (INSTANCE == null) { // первая проверка (без блокировки)
            synchronized (ThreadSafeSingleton.class) {
                if (INSTANCE == null) { // вторая проверка (с блокировкой)
                    INSTANCE = new ThreadSafeSingleton();
                }
            }
        }
        return INSTANCE;
    }
}
```

### Пример Android/Kotlin: Потокобезопасный Singleton

```kotlin
// Object declaration — потокобезопасный singleton в Kotlin
object DatabaseHelper {
    private var database: SQLiteDatabase? = null

    fun getDatabase(context: Context): SQLiteDatabase {
        val appContext = context.applicationContext
        return database ?: synchronized(this) {
            database ?: SQLiteDatabase.openOrCreateDatabase(
                appContext.getDatabasePath("mydb.db"),
                null
            ).also { database = it }
        }
    }
}

// Использование
val db = DatabaseHelper.getDatabase(context)
```

### Пример Kotlin: Ленивая Инициализация

```kotlin
class NetworkManager private constructor() {

    companion object {
        @Volatile
        private var instance: NetworkManager? = null

        fun getInstance(): NetworkManager {
            return instance ?: synchronized(this) {
                instance ?: NetworkManager().also { instance = it }
            }
        }
    }

    fun makeRequest(url: String) {
        println("Making request to: $url")
    }
}

// Или используя lazy-делегат
class CacheManager private constructor() {
    companion object {
        val instance: CacheManager by lazy(LazyThreadSafetyMode.SYNCHRONIZED) {
            CacheManager()
        }
    }
}
```

### Объяснение Примера

**Пояснение**:

- **Object declaration** в Kotlin автоматически создаёт потокобезопасный singleton.
- **Companion object** с ленивой инициализацией реализует потокобезопасный singleton с double-checked locking.
- **`@Volatile`** обеспечивает видимость изменений переменной экземпляра между потоками.
- **`synchronized`** блок гарантирует, что только один поток может создать экземпляр.
- **`by lazy`** делегат (в режиме SYNCHRONIZED) предоставляет встроенную потокобезопасную ленивую инициализацию.

### Типичное Применение

Распространённые случаи использования:

- Паттерны **abstract factory, factory method, builder и prototype** могут использовать singleton в своей реализации.
- **Facade-объекты** часто являются singleton, так как требуется только один facade-объект.
- **State-объекты** иногда реализуются как singleton.
- **Подключения к базам данных, сетевые менеджеры, менеджеры конфигурации** (с учётом корректного жизненного цикла) в Android.
- **Репозитории уровня приложения, средства аналитики, утилиты логирования**.

### Преимущества

1. **Контролируемый доступ** - Обеспечивает контролируемый доступ к единственному экземпляру.
2. **Сокращение дублирования** - Позволяет не создавать множество одинаковых тяжёлых объектов, когда достаточно одного.
3. **Глобальная точка доступа** - Лёгкий доступ из любого места приложения.
4. **Ленивая инициализация** - Экземпляр может быть создан при первой необходимости.
5. **Потенциальная потокобезопасность** - Может быть реализован безопасным для многопоточности образом.

### Недостатки

1. **Глобальное состояние** - Создаёт глобальное состояние, что усложняет понимание поведения системы и тестирование.
2. **Скрытые зависимости** - Классы, использующие singleton, получают зависимости неявно, а не через явное внедрение.
3. **Нарушение Single Responsibility** - Класс управляет и своей жизнью, и бизнес-логикой.
4. **Сложность тестирования** - Трудно мокировать и сбрасывать состояние в unit-тестах.
5. **Проблемы с конкурентностью** - Требуется аккуратная синхронизация в многопоточных средах.
6. **Нарушение Dependency Inversion** - Стимулирует жёсткую связь с конкретной реализацией.
7. **Время жизни и память** - Долго живущие singleton-объекты могут удерживать ресурсы дольше, чем требуется.

### Лучшие Практики

```kotlin
// DO: Используйте object declaration для простых singleton без внешнего жизненного цикла
object AppConfig {
    var apiKey: String = ""
    var baseUrl: String = ""
}

// DO: Используйте ленивую инициализацию для дорогих объектов
class ImageCache private constructor(context: Context) {
    companion object {
        @Volatile private var instance: ImageCache? = null

        fun getInstance(context: Context): ImageCache {
            val appContext = context.applicationContext
            return instance ?: synchronized(this) {
                instance ?: ImageCache(appContext)
                    .also { instance = it }
            }
        }
    }
}

// DO: Отдавайте предпочтение Dependency Injection вместо singleton, когда это возможно (тестируемость, слабое зацепление)
class MyRepository(private val api: ApiService) // Внедрён, не singleton

// DON'T: Не используйте singleton для объектов с разными жизненными циклами (экран, запрос и т.п.)
// DON'T: Не храните прямые ссылки на Activity/Context в singleton (утечки памяти!)
```

Singleton — это порождающий паттерн проектирования, который гарантирует, что класс имеет только один экземпляр (или контролируемое число экземпляров) и предоставляет глобальную точку доступа к нему. **Проблема**: Нужно гарантировать существование только одного экземпляра и обеспечить к нему удобный доступ. **Решение**: Приватный конструктор, статический экземпляр и статический фабричный метод с корректной синхронизацией. **Использовать когда**: (1) Нужен ровно один (или фиксированно ограниченный) экземпляр, (2) Экземпляр должен быть глобально доступен, (3) Требуется ленивая инициализация или контролируемый жизненный цикл. **Kotlin**: Используйте `object` declaration или companion object с ленивой инициализацией. **Плюсы**: контролируемый доступ, уменьшение дублирования, глобальный доступ. **Минусы**: глобальное состояние, скрытые зависимости, сложность тестирования, риск проблем с ресурсами и жизненным циклом. **Примеры**: Database helper (c application context), network manager, конфигурация, analytics tracker.

---

## Answer (EN)

Singleton is a creational design pattern that ensures a class has only one instance (or a strictly limited number of instances) and provides a global point of access to that instance.

### Definition

Singleton pattern is a software design pattern that **restricts the instantiation of a class to one "single" instance**. This is useful when exactly one object is needed to coordinate actions across the system. The term comes from the mathematical concept of a singleton.

### Problems it Solves

The singleton design pattern solves problems like:

1. **How can it be ensured that a class has only one instance?**
2. **How can the sole instance of a class be accessed easily?**
3. **How can a class control its instantiation?**
4. **How can the number of instances of a class be restricted?**

### Solution

To create the singleton class, we typically use:

- **Static member**: Holds the singleton instance and is initialized once for the class loader.
- **Private constructor**: Prevents instantiation of the Singleton class from outside the class.
- **Static factory method**: Provides the global point of access to the Singleton object and returns the instance to the caller.

### Example: Classic (Non-Thread-Safe) Singleton

```java
public final class ClassSingleton {

    private static ClassSingleton INSTANCE;
    private String info = "Initial info class";

    private ClassSingleton() {
    }

    // Not thread-safe: multiple instances may be created in a multithreaded context
    public static ClassSingleton getInstance() {
        if (INSTANCE == null) {
            INSTANCE = new ClassSingleton();
        }
        return INSTANCE;
    }

    // getters and setters
}
```

### Example: Thread-Safe Singleton (`Double`-Checked Locking)

```java
public final class ThreadSafeSingleton {

    private static volatile ThreadSafeSingleton INSTANCE;

    private ThreadSafeSingleton() {
    }

    public static ThreadSafeSingleton getInstance() {
        if (INSTANCE == null) { // first check (no locking)
            synchronized (ThreadSafeSingleton.class) {
                if (INSTANCE == null) { // second check (with locking)
                    INSTANCE = new ThreadSafeSingleton();
                }
            }
        }
        return INSTANCE;
    }
}
```

### Android/Kotlin Example: Thread-Safe Singleton

```kotlin
// Object declaration - thread-safe singleton in Kotlin
object DatabaseHelper {
    private var database: SQLiteDatabase? = null

    fun getDatabase(context: Context): SQLiteDatabase {
        val appContext = context.applicationContext
        return database ?: synchronized(this) {
            database ?: SQLiteDatabase.openOrCreateDatabase(
                appContext.getDatabasePath("mydb.db"),
                null
            ).also { database = it }
        }
    }
}

// Usage
val db = DatabaseHelper.getDatabase(context)
```

### Kotlin Example: Lazy Initialization

```kotlin
class NetworkManager private constructor() {

    companion object {
        @Volatile
        private var instance: NetworkManager? = null

        fun getInstance(): NetworkManager {
            return instance ?: synchronized(this) {
                instance ?: NetworkManager().also { instance = it }
            }
        }
    }

    fun makeRequest(url: String) {
        println("Making request to: $url")
    }
}

// Or using lazy delegate
class CacheManager private constructor() {
    companion object {
        val instance: CacheManager by lazy(LazyThreadSafetyMode.SYNCHRONIZED) {
            CacheManager()
        }
    }
}
```

### Example Explanation

**Explanation**:

- **Object declaration** in Kotlin automatically creates a thread-safe singleton.
- **Companion object** with lazy initialization provides a thread-safe singleton with double-checked locking.
- **`@Volatile`** ensures visibility of changes to the instance variable across threads.
- **`synchronized`** block ensures only one thread can create the instance at a time.
- **`by lazy`** delegate provides built-in (configurable) thread-safe lazy initialization when using SYNCHRONIZED mode.

### Typical Use Cases

Common uses:

- The **abstract factory, factory method, builder, and prototype** patterns can use singletons in their implementation.
- **Facade objects** are often singletons because only one facade object is required.
- **State objects** are sometimes implemented as singletons.
- **Database connections, network managers, configuration managers** (carefully, with proper lifecycle) in Android.
- **`Application`-wide repositories, analytics trackers, logging utilities**.

### Pros and Cons

#### Pros

1. **Controlled access** - Provides controlled access to the sole instance.
2. **Potential reduction of duplication** - Avoids creating multiple identical heavy objects when only one is needed.
3. **Global access point** - Easy access from anywhere in the application.
4. **Lazy initialization** - Instance can be created when first needed.
5. **Thread safety** - Can be implemented to be thread-safe.

#### Cons

1. **Global state** - Creates global state which can make reasoning about the system and testing difficult.
2. **Hidden dependencies** - Classes using singleton have hidden dependencies instead of explicit injection.
3. **Violates Single Responsibility** - Controls both its own creation and business logic.
4. **Difficult to test** - Hard to mock and reset in unit tests.
5. **Concurrency issues** - Requires careful synchronization in multithreaded environments.
6. **Violates Dependency Inversion** - Encourages tight coupling to a concrete implementation.
7. **Lifetime and memory** - Long-lived singletons can accidentally retain resources longer than needed.

### Best Practices

```kotlin
// DO: Use object declaration for simple singletons without external lifecycle
object AppConfig {
    var apiKey: String = ""
    var baseUrl: String = ""
}

// DO: Use lazy initialization for expensive objects
class ImageCache private constructor(context: Context) {
    companion object {
        @Volatile private var instance: ImageCache? = null

        fun getInstance(context: Context): ImageCache {
            val appContext = context.applicationContext
            return instance ?: synchronized(this) {
                instance ?: ImageCache(appContext)
                    .also { instance = it }
            }
        }
    }
}

// DO: Prefer Dependency Injection over singletons for better testability and decoupling
class MyRepository(private val api: ApiService) // Injected, not a singleton

// DON'T: Use singleton for objects that should have different lifecycles (e.g., per-screen, per-request)
// DON'T: Store Activity/Context references directly in singletons (memory leaks!)
```

Singleton is a creational design pattern that ensures a class has only one instance (or a strictly limited number of instances) and provides global access to it. **Problem**: Need to ensure only one instance exists and provide easy access. **Solution**: Private constructor, static instance, and static factory method with appropriate thread safety. **Use when**: (1) Exactly one instance is needed, (2) Instance must be accessible globally, (3) Lazy initialization or controlled lifecycle is desired. **Kotlin**: Use `object` declaration or companion object with lazy initialization. **Pros**: controlled access, reduced duplication when a single instance is sufficient, global access. **Cons**: global state, hidden dependencies, difficult to test, potential resource/lifecycle issues. **Examples**: Database helper (using application context), network manager, configuration, analytics tracker.

---

## Дополнительные вопросы (RU)

- Как вы бы рефакторили дизайн, основанный на `Singleton`, чтобы использовать Dependency Injection?
- Когда использование `Singleton` оправдано, несмотря на его недостатки?
- Чем `Singleton` отличается от простой глобальной переменной с точки зрения инкапсуляции и жизненного цикла?

## Follow-ups

- How would you refactor a `Singleton`-based design to use Dependency Injection instead?
- When is it acceptable to use `Singleton` despite its drawbacks?
- How does `Singleton` differ from a simple global variable in terms of encapsulation and lifecycle?

## Связанные вопросы (RU)

- [[q-abstract-factory-pattern--cs--medium]]

## Related Questions

- [[q-abstract-factory-pattern--cs--medium]]

## Ссылки (RU)

- [[c-architecture-patterns]]
- [Singleton pattern](https://en.wikipedia.org/wiki/Singleton_pattern)
- [Java Singleton Design Pattern Best Practices](https://www.journaldev.com/1377/java-singleton-design-pattern-best-practices-examples)
- [Singleton Class in Java](https://www.geeksforgeeks.org/singleton-class-java/)
- [Singleton Design Pattern in Java](https://www.javatpoint.com/singleton-design-pattern-in-java)
- [Java Singleton Design Pattern](https://www.baeldung.com/java-singleton)
- [Singleton](https://sourcemaking.com/design_patterns/singleton)
- [Singleton Pattern in Kotlin](https://www.baeldung.com/kotlin/singleton-classes)

## References

- [[c-architecture-patterns]]
- [Singleton pattern](https://en.wikipedia.org/wiki/Singleton_pattern)
- [Java Singleton Design Pattern Best Practices](https://www.journaldev.com/1377/java-singleton-design-pattern-best-practices-examples)
- [Singleton Class in Java](https://www.geeksforgeeks.org/singleton-class-java/)
- [Singleton Design Pattern in Java](https://www.javatpoint.com/singleton-design-pattern-in-java)
- [Java Singleton Design Pattern](https://www.baeldung.com/java-singleton)
- [Singleton](https://sourcemaking.com/design_patterns/singleton)
- [Singleton Pattern in Kotlin](https://www.baeldung.com/kotlin/singleton-classes)

---
*Source: Kirchhoff Android Interview Questions*