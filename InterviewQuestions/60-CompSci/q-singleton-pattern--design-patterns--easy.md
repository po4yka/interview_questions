---
id: design-patterns-006
title: "Singleton Pattern / Singleton Паттерн"
aliases: [Singleton Pattern, Singleton Паттерн]
topic: design-patterns
subtopics: [creational-patterns, global-access, instantiation]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-design-patterns
related: [q-abstract-factory-pattern--design-patterns--medium, q-builder-pattern--design-patterns--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [creational-patterns, design-patterns, difficulty/easy, gof-patterns, singleton]
date created: Monday, October 6th 2025, 7:18:19 am
date modified: Saturday, November 1st 2025, 5:43:29 pm
---

# Singleton Pattern

# Question (EN)
> What is the Singleton pattern? When and why should it be used?

# Вопрос (RU)
> Что такое паттерн Singleton? Когда и зачем его использовать?

---

## Answer (EN)


**Singleton (Одиночка)** - это порождающий паттерн проектирования, который гарантирует, что класс имеет только один экземпляр, и предоставляет глобальную точку доступа к этому экземпляру.

### Definition


Singleton pattern is a software design pattern that **restricts the instantiation of a class to one "single" instance**. This is useful when exactly one object is needed to coordinate actions across the system. The term comes from the mathematical concept of a singleton.

### Problems it Solves


The singleton design pattern solves problems like:

1. **How can it be ensured that a class has only one instance?**
2. **How can the sole instance of a class be accessed easily?**
3. **How can a class control its instantiation?**
4. **How can the number of instances of a class be restricted?**

### Solution


To create the singleton class, we need to have:

- **Static member**: It gets memory only once because of static, it contains the instance of the Singleton class
- **Private constructor**: It will prevent to instantiate the Singleton class from outside the class
- **Static factory method**: This provides the global point of access to the Singleton object and returns the instance to the caller

## Пример: Classic Singleton

```java
public final class ClassSingleton {

    private static ClassSingleton INSTANCE;
    private String info = "Initial info class";

    private ClassSingleton() {
    }

    public static ClassSingleton getInstance() {
        if(INSTANCE == null) {
            INSTANCE = new ClassSingleton();
        }

        return INSTANCE;
    }

    // getters and setters
}
```

## Android/Kotlin Example: Thread-Safe Singleton

```kotlin
// Object declaration - thread-safe singleton in Kotlin
object DatabaseHelper {
    private var database: SQLiteDatabase? = null

    fun getDatabase(context: Context): SQLiteDatabase {
        return database ?: synchronized(this) {
            database ?: SQLiteDatabase.openOrCreateDatabase(
                context.getDatabasePath("mydb.db"),
                null
            ).also { database = it }
        }
    }
}

// Usage
val db = DatabaseHelper.getDatabase(context)
```

## Kotlin Example: Lazy Initialization

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

- **Object declaration** in Kotlin automatically creates a thread-safe singleton
- **Companion object** with lazy initialization provides thread-safe singleton with double-checked locking
- **`@Volatile`** ensures visibility of changes to the instance variable across threads
- **`synchronized`** block ensures only one thread can create the instance
- **`by lazy`** delegate provides built-in thread-safe lazy initialization

## Типичные Применения

Common uses:

- The **abstract factory, factory method, builder, and prototype** patterns can use singletons in their implementation
- **Facade objects** are often singletons because only one facade object is required
- **State objects** are often singletons
- **Database connections, network managers, configuration managers** in Android
- **Application-wide repositories, analytics trackers, logging utilities**

## Преимущества И Недостатки

### Pros (Преимущества)


1. **Controlled access** - Provides controlled access to the sole instance
2. **Memory efficiency** - Saves memory as only one instance exists
3. **Global access point** - Easy access from anywhere in the application
4. **Lazy initialization** - Instance can be created when first needed
5. **Thread safety** - Can be implemented to be thread-safe

### Cons (Недостатки)


1. **Global state** - Creates global state which can make testing difficult
2. **Hidden dependencies** - Classes using singleton have hidden dependencies
3. **Violates Single Responsibility** - Controls both its own creation and business logic
4. **Difficult to test** - Hard to mock in unit tests
5. **Concurrency issues** - Requires careful synchronization in multithreaded environments
6. **Violates Dependency Inversion** - Tight coupling to concrete implementation

## Best Practices

```kotlin
// - DO: Use object declaration for simple singletons
object AppConfig {
    var apiKey: String = ""
    var baseUrl: String = ""
}

// - DO: Use lazy initialization for expensive objects
class ImageCache private constructor(context: Context) {
    companion object {
        @Volatile private var instance: ImageCache? = null

        fun getInstance(context: Context): ImageCache {
            return instance ?: synchronized(this) {
                instance ?: ImageCache(context.applicationContext)
                    .also { instance = it }
            }
        }
    }
}

// - DO: Use Dependency Injection instead when possible
class MyRepository(private val api: ApiService) // Injected, not singleton

// - DON'T: Use singleton for objects that should have different lifecycles
// - DON'T: Store Activity/Context references in singletons (memory leaks!)
```

**English**: **Singleton** is a creational design pattern that ensures a class has only one instance and provides global access to it. **Problem**: Need to ensure only one instance exists and provide easy access. **Solution**: Private constructor, static instance, and static factory method. **Use when**: (1) Exactly one instance is needed, (2) Instance must be accessible globally, (3) Lazy initialization is desired. **Kotlin**: Use `object` declaration or companion object with lazy initialization. **Pros**: controlled access, memory efficient, global access. **Cons**: global state, hidden dependencies, difficult to test. **Examples**: Database helper, network manager, configuration, analytics tracker.

---



## Ответ (RU)

### Определение

Паттерн Singleton — это паттерн проектирования, который **ограничивает создание экземпляров класса одним единственным экземпляром**. Это полезно, когда требуется ровно один объект для координации действий в системе. Термин происходит от математической концепции одноэлементного множества.

### Проблемы, Которые Решает

Паттерн проектирования Singleton решает такие проблемы как:

1. **Как гарантировать, что класс имеет только один экземпляр?**
2. **Как обеспечить легкий доступ к единственному экземпляру класса?**
3. **Как класс может контролировать своё создание?**
4. **Как ограничить количество экземпляров класса?**

### Решение

Для создания singleton класса необходимо иметь:

- **Статический член**: Получает память только один раз из-за static, содержит экземпляр Singleton класса
- **Приватный конструктор**: Предотвращает создание экземпляров Singleton класса извне
- **Статический фабричный метод**: Предоставляет глобальную точку доступа к объекту Singleton и возвращает экземпляр вызывающему коду

### Пример: Классический Singleton

```java
public final class ClassSingleton {

    private static ClassSingleton INSTANCE;
    private String info = "Initial info class";

    private ClassSingleton() {
    }

    public static ClassSingleton getInstance() {
        if(INSTANCE == null) {
            INSTANCE = new ClassSingleton();
        }

        return INSTANCE;
    }

    // getters and setters
}
```

### Пример Android/Kotlin: Потокобезопасный Singleton

```kotlin
// Object declaration - потокобезопасный singleton в Kotlin
object DatabaseHelper {
    private var database: SQLiteDatabase? = null

    fun getDatabase(context: Context): SQLiteDatabase {
        return database ?: synchronized(this) {
            database ?: SQLiteDatabase.openOrCreateDatabase(
                context.getDatabasePath("mydb.db"),
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

// Или используя lazy делегат
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

- **Object declaration** в Kotlin автоматически создает потокобезопасный singleton
- **Companion object** с ленивой инициализацией обеспечивает потокобезопасный singleton с двойной проверкой блокировки
- **`@Volatile`** обеспечивает видимость изменений переменной экземпляра между потоками
- **`synchronized`** блок гарантирует, что только один поток может создать экземпляр
- **`by lazy`** делегат предоставляет встроенную потокобезопасную ленивую инициализацию

### Типичное Применение

Распространенное использование:

- Паттерны **abstract factory, factory method, builder и prototype** могут использовать singleton в своей реализации
- **Facade объекты** часто являются singleton, так как требуется только один facade объект
- **State объекты** часто являются singleton
- **Подключения к базам данных, network менеджеры, configuration менеджеры** в Android
- **Репозитории уровня приложения, analytics trackers, утилиты логирования**

### Преимущества

1. **Контролируемый доступ** - Обеспечивает контролируемый доступ к единственному экземпляру
2. **Эффективность памяти** - Экономит память, так как существует только один экземпляр
3. **Глобальная точка доступа** - Легкий доступ из любого места приложения
4. **Ленивая инициализация** - Экземпляр может быть создан при первой необходимости
5. **Потокобезопасность** - Может быть реализован потокобезопасным способом

### Недостатки

1. **Глобальное состояние** - Создает глобальное состояние, что может усложнить тестирование
2. **Скрытые зависимости** - Классы, использующие singleton, имеют скрытые зависимости
3. **Нарушает Single Responsibility** - Контролирует как своё создание, так и бизнес-логику
4. **Сложность тестирования** - Трудно мокировать в unit тестах
5. **Проблемы с конкурентностью** - Требует тщательной синхронизации в многопоточных средах
6. **Нарушает Dependency Inversion** - Жесткая связь с конкретной реализацией

### Лучшие Практики

```kotlin
// DO: Используйте object declaration для простых singleton
object AppConfig {
    var apiKey: String = ""
    var baseUrl: String = ""
}

// DO: Используйте ленивую инициализацию для дорогих объектов
class ImageCache private constructor(context: Context) {
    companion object {
        @Volatile private var instance: ImageCache? = null

        fun getInstance(context: Context): ImageCache {
            return instance ?: synchronized(this) {
                instance ?: ImageCache(context.applicationContext)
                    .also { instance = it }
            }
        }
    }
}

// DO: Используйте Dependency Injection вместо singleton когда возможно
class MyRepository(private val api: ApiService) // Внедрён, не singleton

// DON'T: Не используйте singleton для объектов с разными жизненными циклами
// DON'T: Не храните ссылки на Activity/Context в singleton (утечки памяти!)
```

Singleton — это порождающий паттерн проектирования, который гарантирует, что класс имеет только один экземпляр, и предоставляет глобальную точку доступа к этому экземпляру. **Проблема**: Необходимо гарантировать существование только одного экземпляра и обеспечить легкий доступ. **Решение**: Приватный конструктор, статический экземпляр и статический фабричный метод. **Использовать когда**: (1) Нужен ровно один экземпляр, (2) Экземпляр должен быть глобально доступен, (3) Желательна ленивая инициализация. **Kotlin**: Используйте `object` declaration или companion object с ленивой инициализацией. **Плюсы**: контролируемый доступ, эффективность памяти, глобальный доступ. **Минусы**: глобальное состояние, скрытые зависимости, сложность тестирования. **Примеры**: Database helper, network manager, конфигурация, analytics tracker.

---

## Links

- [Singleton pattern](https://en.wikipedia.org/wiki/Singleton_pattern)
- [Java Singleton Design Pattern Best Practices](https://www.journaldev.com/1377/java-singleton-design-pattern-best-practices-examples)
- [Singleton Class in Java](https://www.geeksforgeeks.org/singleton-class-java/)
- [Singleton Design Pattern in Java](https://www.javatpoint.com/singleton-design-pattern-in-java)

## Further Reading

- [Java Singleton Design Pattern](https://www.baeldung.com/java-singleton)
- [Singleton](https://sourcemaking.com/design_patterns/singleton)
- [Singleton Pattern in Kotlin](https://www.baeldung.com/kotlin/singleton-classes)

---
*Source: Kirchhoff Android Interview Questions*


---

## Related Questions

### Hub
- [[q-design-patterns-types--design-patterns--medium]] - Design pattern categories overview

### Creational Patterns
- [[q-factory-method-pattern--design-patterns--medium]] - Factory Method pattern
- [[q-abstract-factory-pattern--design-patterns--medium]] - Abstract Factory pattern
- [[q-builder-pattern--design-patterns--medium]] - Builder pattern

