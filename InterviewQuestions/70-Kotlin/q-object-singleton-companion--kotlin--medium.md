---
id: kotlin-234
title: "Object, Companion Object, and Singleton Pattern / object, companion object и паттерн Singleton"
aliases: ["Object Singleton Companion", "Объект Singleton Companion"]
topic: kotlin
subtopics: [companion-object, object-keyword, singleton-pattern]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-class-initialization-order--kotlin--medium, q-inheritance-open-final--kotlin--medium, q-inner-nested-classes--kotlin--medium]
created: 2025-10-12
updated: 2025-11-09
tags: [companion-object, difficulty/medium, kotlin, kotlin-features, object-keyword, singleton-pattern]
sources: ["https://kotlinlang.org/docs/object-declarations.html"]
---

# Вопрос (RU)
> Как работают object, companion object и паттерн singleton в Kotlin?

# Question (EN)
> How do object, companion object, and singleton pattern work in Kotlin?

---

## Ответ (RU)

**Теория object и companion object:**
В Kotlin ключевое слово `object` объявляет singleton — единственный экземпляр, который создаётся и инициализируется при первом обращении к этому объекту (инициализация гарантированно потокобезопасна). `companion object` — это специальный `object` внутри класса, доступ к которому идёт через имя класса. Они используются для реализации singleton-паттерна, утилитных функций, factory-методов и псевдо-"статических" членов. См. также [[c-kotlin]].

**Основные концепции:**
- **object**: Объявляет singleton-объект (единственный экземпляр типа)
- **companion object**: Объект внутри класса, доступный через имя класса
- **Инициализация при первом использовании**: Инициализируется при первом обращении к объекту
- **Потокобезопасная инициализация**: Создание экземпляра `object` / `companion object` потокобезопасно, но внутреннее изменяемое состояние не становится автоматически потокобезопасным

**Object Singleton:**
```kotlin
// ✅ object объявляет singleton
object DatabaseManager {
    private val connection = "Connected"

    fun connect() {
        println(connection)
    }

    fun disconnect() {
        println("Disconnected")
    }
}

// Usage: обращение как к единственному экземпляру
DatabaseManager.connect() // Connected
DatabaseManager.disconnect() // Disconnected

// ❌ нельзя создать новый экземпляр
// val db = DatabaseManager() // Ошибка!
```

**Companion Object:**
```kotlin
class MyClass {
    private val instanceData = "Instance data"

    // ✅ companion object доступен через имя класса
    companion object {
        private const val CONSTANT = "Constant value"

        fun factory(): MyClass {
            return MyClass()
        }
    }
}

// Usage
val instance = MyClass.factory() // Доступ через имя класса
```

**Companion с интерфейсами:**
```kotlin
interface Factory {
    fun create(): Any
}

class User {
    companion object : Factory {
        override fun create() = User()
    }
}

// ✅ Можно вызывать User.create(), т.к. companion реализует Factory
val user = User.create()
```

**Практическое применение:**
```kotlin
// ✅ Singleton для настроек (общая точка доступа к состоянию)
object SettingsManager {
    private var theme: String = "light"

    fun setTheme(theme: String) {
        this.theme = theme
    }

    fun getTheme(): String = theme
}

// ✅ Factory-методы в companion
class User private constructor(val name: String) {
    companion object {
        fun create(name: String): User {
            return User(name)
        }

        fun createAdmin(): User {
            return User("Admin")
        }
    }
}
```

**Избегание проблем singleton:**
```kotlin
// ❌ ПЛОХО: Глобальное изменяемое состояние, усложняет тестирование и потокобезопасность
object GlobalState {
    var counter = 0
}

// ✅ ЛУЧШЕ: Инкапсулированное состояние и контролируемый доступ
// (но при работе из нескольких потоков всё равно требуется забота о потокобезопасности)
object Logger {
    private val logs = mutableListOf<String>()

    fun log(message: String) {
        logs.add(message)
    }

    fun getLogs(): List<String> = logs.toList()
}
```

---

## Answer (EN)

**Object and Companion Object Theory:**
In Kotlin, the `object` keyword declares a singleton — a single instance that is created and initialized upon its first use (the initialization itself is guaranteed to be thread-safe). A `companion object` is a special `object` inside a class, accessible through the class name. They are used for implementing the singleton pattern, utility functions, factory methods, and pseudo-"static" members. See also [[c-kotlin]].

**Core Concepts:**
- **object**: Declares a singleton object (a single instance of that type)
- **companion object**: Object inside a class, accessible through the class name
- **Initialization on first use**: Initialized when first referenced
- **Thread-safe initialization**: Creation of `object` / `companion object` is thread-safe, but mutable state inside is not automatically thread-safe

**Object Singleton:**
```kotlin
// ✅ object creates a singleton
object DatabaseManager {
    private val connection = "Connected"

    fun connect() {
        println(connection)
    }

    fun disconnect() {
        println("Disconnected")
    }
}

// Usage: access as single instance
DatabaseManager.connect() // Connected
DatabaseManager.disconnect() // Disconnected

// ❌ cannot create a new instance
// val db = DatabaseManager() // Error!
```

**Companion Object:**
```kotlin
class MyClass {
    private val instanceData = "Instance data"

    // ✅ companion object accessible through class name
    companion object {
        private const val CONSTANT = "Constant value"

        fun factory(): MyClass {
            return MyClass()
        }
    }
}

// Usage
val instance = MyClass.factory() // Access through class name
```

**Companion with Interfaces:**
```kotlin
interface Factory {
    fun create(): Any
}

class User {
    companion object : Factory {
        override fun create() = User()
    }
}

// ✅ You can call User.create(), since the companion implements Factory
val user = User.create()
```

**Practical Application:**
```kotlin
// ✅ Singleton for settings (shared state access point)
object SettingsManager {
    private var theme: String = "light"

    fun setTheme(theme: String) {
        this.theme = theme
    }

    fun getTheme(): String = theme
}

// ✅ Factory methods in companion
class User private constructor(val name: String) {
    companion object {
        fun create(name: String): User {
            return User(name)
        }

        fun createAdmin(): User {
            return User("Admin")
        }
    }
}
```

**Avoiding Singleton Problems:**
```kotlin
// ❌ BAD: Global mutable state, hard to test and reason about
object GlobalState {
    var counter = 0
}

// ✅ BETTER: Encapsulated state with controlled access
// (but you still must handle thread-safety if accessed from multiple threads)
object Logger {
    private val logs = mutableListOf<String>()

    fun log(message: String) {
        logs.add(message)
    }

    fun getLogs(): List<String> = logs.toList()
}
```

## Follow-ups

- When to use `object` vs class with private constructor?
- How to test code with `object` singletons?
- Performance implications of initialization on first use?

## References

- https://kotlinlang.org/docs/object-declarations.html

## Related Questions

### Prerequisites (Easier)
- [[q-kotlin-enum-classes--kotlin--easy]] - Basic classes

### Related (Medium)
- [[q-class-initialization-order--kotlin--medium]] - Class initialization
- [[q-inheritance-open-final--kotlin--medium]] - Inheritance
- [[q-inner-nested-classes--kotlin--medium]] - Inner/Nested classes

### Advanced (Harder)
- [[q-delegation-by-keyword--kotlin--medium]] - Class delegation
